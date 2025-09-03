# -*- coding: utf-8 -*-
import ccxt
import time
import requests
import traceback
import pandas as pd
# import talib as ta
from decimal import Decimal

'''
自动设置移动止损单
'''
class TrailingSLTaker:
    def __init__(self, g_config, platform_config, common_config=None, feishu_webhook=None, monitor_interval=4,logger=None):
        self.g_config = g_config

        if not common_config:
            self.common_config = self.g_config.get('common', {})
        else:
            self.common_config = common_config

        self.feishu_webhook = feishu_webhook
        self.monitor_interval = monitor_interval  # 监控循环时间是分仓监控的3倍
        self.logger = logger

        proxies = {
            "http": self.common_config.get('proxy', "http://localhost:7890"),
            "https": self.common_config.get('proxy', "http://localhost:7890")
        }
        
        # 配置交易所
        self.exchange = ccxt.okx({
            'apiKey': platform_config["apiKey"],
            'secret': platform_config["secret"],
            'password': platform_config["password"],
            'timeout': 3000,
            'rateLimit': 50,
            'options': {'defaultType': 'future'},
            'proxies': proxies
        })

        self.strategy_config = self.g_config.get('strategy', {})     
        self.trading_pairs_config = self.g_config.get('tradingPairs', {})       
        
        # base
    
        self.stop_loss_pct = float(self.strategy_config.get("all_stop_loss_pct",2))  # 全局止损百分比
        self.all_TP_SL_ratio = float(self.strategy_config.get("all_TP_SL_ratio",2))  
        self.leverage = int(self.strategy_config.get("leverage",1)) 

        # trailing_strategy
        self.trailing_strategy_config = self.strategy_config.get('trailing_strategy', {})


        # 设置利润触发规则      
        self.open_trail_profit = self.trailing_strategy_config.get("open_trail_profit",False)# 是否开启追踪利润
        self.low_trail_profit_threshold = self.trailing_strategy_config["all_low_trail_profit_threshold"]# 第一档
        self.first_trail_profit_threshold = self.trailing_strategy_config["all_first_trail_profit_threshold"]# 第二档
        self.second_trail_profit_threshold = self.trailing_strategy_config["all_second_trail_profit_threshold"]# 第三档
        # 设置SL 推损规则
        self.low_trail_stop_loss_pct = self.trailing_strategy_config["all_low_trail_stop_loss_pct"] # 第一档
        self.trail_stop_loss_pct = self.trailing_strategy_config["all_trail_stop_loss_pct"]# 第二档
        self.higher_trail_stop_loss_pct = self.trailing_strategy_config["all_higher_trail_stop_loss_pct"]# 第三档        
        # 设置TP 止盈规则
        self.open_trail_tp = self.trailing_strategy_config.get("open_trail_tp",False)# 是否开启追踪止盈
        self.low_trail_tp_pct = self.trailing_strategy_config["all_low_trail_tp_pct"]# 第一档
        self.trail_tp_pct = self.trailing_strategy_config["all_trail_tp_pct"]# 第二档
        self.higher_trail_tp_pct = self.trailing_strategy_config["all_higher_trail_tp_pct"]# 第三档
                
        self.highest_total_profit = {}  # 记录最高总盈利        
        self.positions_entry_price = {} # 记录每个symbol的开仓价格                
        self.global_symbol_stop_loss_flag = {} # 记录每个symbol是否设置全局止损
        self.global_symbol_stop_loss_price = {} # 记录每个symbol的止损价格
        
        # 保留在止盈挂单中最高最低两个价格，计算止盈价格。
        self.max_market_price = {}
        self.min_market_price = {}        
        self.cross_directions = {} # 持仓期间，存储每个交易对的交叉方向 

        self.position_mode = self.get_position_mode()  # 获取持仓模式
    
    def get_pair_config(self,symbol):
        # 获取交易对特定配置,如果没有则使用全局策略配置
        pair_config = self.trading_pairs_config.get(symbol, {})
        
        # 使用字典推导式合并配置,trading_pairs_config优先级高于strategy_config
        pair_config = {
            **self.strategy_config,  # 基础配置
            **pair_config  # 交易对特定配置会覆盖基础配置
        }
        return pair_config

    def format_price(self, symbol, price:Decimal) -> str:
        precision = self.get_precision_length(symbol)
        return f"{price:.{precision}f}"

    @staticmethod
    def toDecimal(value):
        return Decimal(str(value))

    # 获取市场信息
    def getMarket(self,symbol):
        self.exchange.load_markets()
        return self.exchange.market(symbol)
    # 获取tick_size
    def get_tick_size(self,symbol) -> Decimal:
      
        try:
            market = self.getMarket(symbol)
            if market and 'precision' in market and 'price' in market['precision']:
                
                return self.toDecimal(market['precision']['price'])
            else:
                # self.logger.error(f"{symbol}: 无法从市场数据中获取价格精度")
                # return self.toDecimal("0.00001")  # 返回默认精度
                raise ValueError(f"{symbol}: 无法从市场数据中获取价格精度")
        except Exception as e:
            self.logger.error(f"{symbol}: 获取市场价格精度时发生错误: {str(e)}")
            self.send_feishu_notification(f"{symbol}: 获取市场价格精度时发生错误: {str(e)}")

    # 获取价格精度
    def get_precision_length(self,symbol) -> int:
        tick_size = self.get_tick_size(symbol)
        return len(f"{tick_size:.15f}".rstrip('0').split('.')[1]) if '.' in f"{tick_size:.15f}" else 0
    # 获取当前持仓模式
    def get_position_mode(self):
        try:
            # 假设获取账户持仓模式的 API
            response = self.exchange.private_get_account_config()
            data = response.get('data', [])
            if data and isinstance(data, list):
                # 取列表的第一个元素（假设它是一个字典），然后获取 'posMode'
                position_mode = data[0].get('posMode', 'single')  # 默认值为单向
                self.logger.info(f"当前持仓模式: {position_mode}")
                return position_mode
            else:
                self.logger.error("无法检测持仓模式: 'data' 字段为空或格式不正确")
                return 'single'  # 返回默认值
        except Exception as e:
            self.logger.error(f"无法检测持仓模式: {e}")
            return None

    def send_feishu_notification(self, message):
        if self.feishu_webhook:
            try:
                headers = {'Content-Type': 'application/json'}
                payload = {"msg_type": "text", "content": {"text": message}}
                response = requests.post(self.feishu_webhook, json=payload, headers=headers)
                # if response.status_code == 200:
                #     self.logger.debug("飞书通知发送成功")
                # else:
                #     self.logger.warn("飞书通知发送失败，状态码: %s", response.status_code)
            except Exception as e:
                self.logger.error("发送飞书通知时出现异常: %s", str(e))

    def fetch_positions(self):     
        return self.exchange.fetch_positions()
  
    # 获取当前委托
    def fetch_open_orders(self,symbol,params={}):
        try:
            orders = self.exchange.fetch_open_orders(symbol=symbol,params=params)
            return orders
        except Exception as e:
            self.logger.error(f"Error fetching open orders: {e}")
            return []

    # 获取历史K线，不包含最新的一条
    def get_historical_klines_except_last(self,symbol, bar='1m', limit=241):
  
        klines = self.get_historical_klines(symbol, bar=bar, limit=limit)
        return klines[:-1]


    def get_historical_klines(self,symbol, bar='1m', limit=241):
        
        params = {
            # 'instId': instId,
        }
        klines = self.exchange.fetch_ohlcv(symbol, timeframe=bar,limit=limit,params=params)
        
        if klines :
            
            return klines
        else:
            raise ValueError("Unexpected response structure or missing candlestick data")

    def format_klines(self,klines) -> pd.DataFrame:
       
        """_summary_
            格式化K线数据
        Args:
            klines (_type_): _description_
        """
        klines_df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']) 
        # 转换时间戳为日期时间
        klines_df['timestamp'] = pd.to_datetime(klines_df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
        
        return klines_df

    def is_pivot_high(self, data, index, period, check_bounds=False):
        """
        判断当前索引处是否为枢轴高点
        :param data: 包含 'high' 列的 DataFrame
        :param index: 当前索引
        :param period: 前后比较的周期数
        :param check_bounds: 是否检查边界
        :return: 是否为枢轴高点
        """
        if check_bounds and (index < period or index >= len(data) - period):
            return False
        current_high = data.at[index, 'high']
        prev_highs = data['high'].iloc[max(0,index - period):index]
        next_highs = data['high'].iloc[index :min(len(data),index + period + 1)]
        return all(current_high >= prev_highs) and all(current_high >= next_highs)


    def is_pivot_low(self, data, index, period, check_bounds=False):
        """
        判断当前索引处是否为枢轴低点
        :param data: 包含 'low' 列的 DataFrame
        :param index: 当前索引
        :param period: 前后比较的周期数
        :param check_bounds: 是否检查边界
        :return: 是否为枢轴低点
        """
        if check_bounds and (index < period or index >= len(data) - period):
            return False
        current_low = data.at[index, 'low']
        prev_lows = data['low'].iloc[max(0,index - period):index]
        next_lows = data['low'].iloc[index :min(len(data),index + period + 1)]
        return all(current_low <= prev_lows) and all(current_low <= next_lows)


    def get_last_solated_point(self,symbol,position, kLines ,prd=20):
        # 将K线数据转换为DataFrame格式    
        df = self.format_klines(kLines)

        # 根据position方向寻找孤立点
        side = position['side']
        window = prd  # 设置窗口大小，用于判断局部最值
        isolated_points = []
        for i in range(len(df)-1, -1, -1):

            if side == 'short':
                # 找最近的孤立高点
                if self.is_pivot_high(df, i, window):
                # 获取最近的孤立高点
                    isolated_points.append(df.iloc[i])
                    break
                
            else:
                # 找最近的孤立低点 
                if self.is_pivot_low(df, i, window):
                    isolated_points.append(df.iloc[i])
                    break

        return isolated_points


    def judge_correct_postion_side(self, symbol, pair_config, klines=None) -> str:

        '''
        零轴之上的macd与signal形成金叉
        零轴之下的死叉
        零轴之上的死叉-金叉-死叉
        零轴之下的金叉-死叉-金叉
        '''

        order_side = 'none'
        if 'macd_strategy' not in pair_config :
            return  order_side
        
        macd = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # 将时间戳转换为日期时间格式
        macd['timestamp'] = pd.to_datetime(macd['timestamp'], unit='ms').dt.strftime('%m-%d %H:%M')
            
        # 使用 TA-Lib 计算 MACD
        # macd[['macd', 'signal', 'hist']] = pd.DataFrame(ta.MACD(macd['close'], fastperiod=12, slowperiod=26, signalperiod=9)).T
        # 计算EMA12和EMA26
        exp1 = macd['close'].ewm(span=12, adjust=False).mean()
        exp2 = macd['close'].ewm(span=26, adjust=False).mean()
        # 计算MACD线
        macd['macd'] = exp1 - exp2
        # 计算信号线
        macd['signal'] = macd['macd'].ewm(span=9, adjust=False).mean()
        # 计算柱状图
        macd['hist'] = macd['macd'] - macd['signal']
        # self.logger.debug(f"{symbol} : MACD Values = \n {macd.tail(5)}")
        
        
        # 计算最近三个交叉点
        last_up_crosses = []
        last_down_crosses = []
        other_crosses = []
        all_cross = []
        
        # 从最新K开始往前遍历
        for i in range(len(macd)-1, 2, -1):
            # 检查是否发生死叉（MACD从上方穿过Signal）
            if (macd.iloc[i-1]['macd'] <= macd.iloc[i-1]['signal'] and                 
                macd.iloc[i]['macd'] > macd.iloc[i]['signal'] 
                ):
                all_cross.append(('golden', i))
                
                # 判断如果都在零轴之上加入last_up_crosses , 判断如果都在零轴之下加入last_down_crosses
                if macd.iloc[i]['macd'] > 0 and macd.iloc[i]['signal'] > 0 :
                    last_up_crosses.append(('golden', i))
                elif macd.iloc[i]['macd'] < 0 and macd.iloc[i]['signal'] < 0 :
                    last_down_crosses.append(('golden', i))
                else:
                    other_crosses.append(('golden', i))
   
            # 检查是否发生死叉（MACD从上方穿过Signal）
            elif macd.iloc[i-1]['macd'] >= macd.iloc[i-1]['signal'] and macd.iloc[i]['macd'] < macd.iloc[i]['signal']:
                all_cross.append(('death', i))
                # 判断如果都在零轴之上加入last_up_crosses , 判断如果都在零轴之下加入last_down_crosses
                if macd.iloc[i]['macd'] > 0 and macd.iloc[i]['signal'] > 0 :
                    last_up_crosses.append(('death', i))
                elif macd.iloc[i]['macd'] < 0 and macd.iloc[i]['signal'] < 0 :
                    last_down_crosses.append(('death', i))
                else:
                    other_crosses.append(('golden', i))
            # 只保留最后三个交叉点
            if len(last_up_crosses) == 3 or len(last_down_crosses) == 3:
                break
            
        self.logger.debug(f"{symbol} : \n- 所有cross {all_cross} \n- 零轴之上cross {last_up_crosses} \n- 零轴之下cross {last_down_crosses} \n- 其他corss {other_crosses}。")
        
        # valid_klines = pair_config['macd_strategy'].get('valid_klines', 5)
        # 如果最新的交叉是金叉，且又是零轴上方的金叉
        if len(last_up_crosses) > 0 and all_cross[0][0] == 'golden' and all_cross[0][1] == last_up_crosses[0][1] :
            order_side =  'long'
            self.logger.debug(f"{symbol} : 零轴之上的macd与signal形成金叉{all_cross[0]} 。") 
            
        # 如果最新的交叉是死叉，且又是零轴下方的死叉
        elif len(last_down_crosses) > 0 and all_cross[0][0] == 'death' and all_cross[0][1] == last_down_crosses[0][1] :
            order_side ='short'
            self.logger.debug(f"{symbol} : 零轴之下的macd与signal形成死叉{all_cross[0]} 。")
        # 分析交叉点模式，要满足连续的三个交叉都是零上
        elif len(last_up_crosses) == 3 and len(all_cross) == 3:
      
           # 零轴之上的死叉-金叉-死叉模式
            if (last_up_crosses[0][0] == 'death' and 
                last_up_crosses[1][0] == 'golden' and 
                last_up_crosses[2][0] == 'death' 
                ):
                order_side = 'short'
                self.logger.debug(f"{symbol} : 零轴之上的死叉-金叉-死叉模式 {order_side}。")
            
        elif len(last_down_crosses) == 3 and len(all_cross) == 3:
            # 零轴之下的金叉-死叉-金叉模式
            if (last_down_crosses[0][0] == 'golden' and 
                  last_down_crosses[1][0] == 'death' and 
                  last_down_crosses[2][0] == 'golden' 
                  ):
                order_side = 'long'
                self.logger.debug(f"{symbol} : 零轴之下的金叉-死叉-金叉模式 {order_side}。")

        return order_side

    def is_profitable(self, symbol ,position) -> bool:
        # 判断是否进入浮赢阶段
        if position['side'] == 'long':
            # 多单判断持仓价格是否小于止损价格
            return position['entryPrice'] < self.global_symbol_stop_loss_price.get(symbol,0.0)
        else:
            # 空单判断持仓价格是否大于止损价格
            return position['entryPrice'] > self.global_symbol_stop_loss_price.get(symbol,0.0)

    def check_reverse_position(self,symbol,position,pair_config):
        if 'entryPrice' not in position or self.is_profitable(symbol,position):
            self.logger.debug(f"{symbol} : 方向={position['side']} 经进入浮赢阶段，不校验全局止损位置，止损价={self.global_symbol_stop_loss_price} ,开仓价={position['entryPrice']}。")
            return 
            
        side = position['side']
        try:

            klines_period = str(pair_config.get('CHF', '1m'))
            klines = self.get_historical_klines_except_last(symbol=symbol,bar=klines_period)

            self.logger.debug(f"开始监控 {symbol} : klines {klines_period} - {len(klines)}")
            
            correct_side = self.judge_correct_postion_side(symbol=symbol, pair_config=pair_config, klines=klines)
            
            order_stop_loss_pct = None
            # 方向不一致 尽快平仓
            if correct_side != 'none' and correct_side != side :
                self.logger.info(f"{symbol}: 持仓方向={side} 与 正确方向={correct_side} 相反 , 减少止损。")
                order_stop_loss_pct = self.stop_loss_pct / 2
                self.logger.info(f"{symbol} 全局止损阈值-修正后= {self.stop_loss_pct:.2f} -> {order_stop_loss_pct:.2f}%")
            else :
                order_stop_loss_pct = self.stop_loss_pct
                self.logger.info(f"{symbol}: 持仓方向={side} 与 正确方向={correct_side} 相同 , 恢复正常。") 

            # 根据情况 重新修正止损         
            self.global_symbol_stop_loss_flag[symbol] = False  
           
            self.set_global_stop_loss(symbol=symbol,position=position, pair_config=pair_config, stop_loss_pct=order_stop_loss_pct)

                
        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            self.logger.warning(error_message,exc_info=True)
            traceback.print_exc()
            self.send_feishu_notification(error_message)
    
    def calculate_sma_pandas(self,symbol,kLines,period):
        """
        使用 pandas 计算 SMA
        :param KLines K线
        :param period: SMA 周期
        :return: SMA 值
        """
 
        df = pd.DataFrame(kLines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        sma = df['close'].rolling(window=period).mean()
        return sma 
            
    def calculate_ema_pandas(self,symbol,kLines, period):
        """
        使用 pandas 计算 EMA
        :param KLines K线
        :param period: EMA 周期
        :return: EMA 值
        """

        df = pd.DataFrame(kLines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # 计算EMA
        ema = df['close'].ewm(span=period, adjust=False).mean()
        return ema 
    
   # 计算平均利润
    def calculate_average_profit(self,symbol,position):
  
        total_profit_pct = Decimal('0')
        num_positions = 0

        entry_price = self.toDecimal(position['entryPrice'])
        current_price = self.toDecimal(position['markPrice'])
        side = position['side']

        # 计算单个仓位的浮动盈利百分比
        if side not in ['long', 'short']:
            return
            
        # 使用三元运算符简化计算逻辑
        profit_pct = ((current_price - entry_price) if side == 'long' else (entry_price - current_price)) / entry_price * 100

        # 累加总盈利百分比
        total_profit_pct += profit_pct
        num_positions += 1
        # 记录单个仓位的盈利情况
        precision = self.get_precision_length(symbol)
        self.logger.info(f"仓位 {symbol}，方向: {side}，开仓价格: {entry_price:.{precision}}，当前价格: {current_price:.{precision}}，"
                            f"浮动盈亏: {profit_pct:.2f}%")

        # 计算平均浮动盈利百分比
        average_profit_pct = total_profit_pct / num_positions if num_positions > 0 else 0
        return average_profit_pct

    def reset_highest_profit_and_tier(self,symbol=None):
        """重置最高总盈利和当前档位状态"""
        if not symbol:
            self.highest_total_profit.clear()
        else :
            self.highest_total_profit[symbol] = 0.0

        # self.logger.debug("已重置最高总盈利")
  
    def reset_take_profie(self,symbol=None):
        if not symbol:
            self.global_symbol_stop_loss_price.clear()
            self.global_symbol_stop_loss_flag.clear()
            # 保留在止盈挂单中最高最低两个价格，计算止盈价格。
            self.max_market_price.clear()
            self.min_market_price.clear() 
            self.cross_directions.clear()
            
        else :
            self.global_symbol_stop_loss_price[symbol] = 0.0
            self.global_symbol_stop_loss_flag[symbol] = False
            # 保留在止盈挂单中最高最低两个价格，计算止盈价格。
            self.max_market_price[symbol] = 0.0
            self.min_market_price[symbol] = float('inf')  # 初始化为浮点数最大值
            self.cross_directions[symbol] = None
       
    def round_price_to_tick(self, symbol, price:Decimal) -> Decimal:
        tick_size = self.get_tick_size(symbol)
        # 计算 tick_size 的小数位数
        tick_decimals = self.get_precision_length(symbol) 
        # 调整价格为 tick_size 的整数倍
        adjusted_price = round(price / tick_size) * tick_size
        return self.toDecimal(f"{adjusted_price:.{tick_decimals}f}")
        # return self.toDecimal(self.exchange.price_to_precision(symbol, price))
    
    def cancel_all_algo_orders(self, symbol, attachType=None) -> bool:
        """_summary_

        Args:
            symbol (_type_): _description_
            attachType (_type_, optional): "TP"|"SL". Defaults to None.
        """
        
        params = {
            "ordType": "conditional",
        }
        orders = self.fetch_open_orders(symbol=symbol,params=params)
        # 如果没有委托订单则直接返回
        if len(orders) == 0:           
            self.global_symbol_stop_loss_flag[symbol] = False
            self.logger.debug(f"{symbol} 未设置策略订单列表。")
            return
     
        # algo_ids = [order['info']['algoId'] for order in orders if 'info' in order and 'algoId' in order['info']]
        algo_ids = []
        if attachType and attachType == 'SL':
            algo_ids = [order['id'] for order in orders if order['stopLossPrice'] and order['stopLossPrice'] > 0.0 ]
        elif attachType and attachType == 'TP':
            algo_ids = [order['id'] for order in orders if order['takeProfitPrice'] and order['takeProfitPrice'] > 0.0]
        else :
            algo_ids = [order['id'] for order in orders ]
            
        if len(algo_ids) == 0 :         
            self.logger.debug(f"{symbol} 未设置策略订单列表。")
            return
        
        try:
            params = {
                "algoId": algo_ids,
                "trigger": 'trigger'
            }
            rs = self.exchange.cancel_orders(ids=algo_ids, symbol=symbol, params=params)
            
            return len(rs) > 0
            # self.global_symbol_stop_loss_flag[symbol] = False
            # self.logger.debug(f"Order {algo_ids} cancelled:{rs}")
        except Exception as e:
            self.logger.error(f"{symbol} Error cancelling order {algo_ids}: {e}")
      
    def set_stop_loss_take_profit(self, symbol, position, stop_loss_price:Decimal=None,take_profit_price:Decimal=None) -> bool:
        if not stop_loss_price :
            self.logger.warning(f"{symbol}: No stop loss price or take profit price provided for {symbol}")
            return False   
        if not position:
            self.logger.warning(f"{symbol}: No position found for {symbol}")
            return False
        
   
        if self.cancel_all_algo_orders(symbol=symbol, attachType='SL'):
            self.global_symbol_stop_loss_flag[symbol] = False
            return

        return self.set_stop_loss(symbol=symbol, position=position, stop_loss_price=stop_loss_price) 
    

          
    def set_take_profit(self, symbol, position, take_profit_price:Decimal=None) -> bool:

        # 计算下单数量
        amount = abs(self.toDecimal(position['contracts']))
    
        if amount <= 0:
            self.logger.warning(f"{symbol}: amount is 0 for {symbol}")
            return

        
       # 止损单逻辑 
        adjusted_price = self.format_price(symbol, take_profit_price)
         
        tp_params = {
   
            
            'tpTriggerPx':adjusted_price,
            'tpOrdPx' : adjusted_price,
            'tpOrdKind': 'condition',
            'tpTriggerPxType':'last',
            
            'tdMode':position['marginMode'],
            'sz': str(amount),
            # 'closeFraction': '1',
            'cxlOnClosePos': True,
            'reduceOnly':True
        }
        
        side = 'short' 
        if position['side'] == side: # 和持仓反向相反下单
            side ='long'
            
        orderSide = 'buy' if side == 'long' else 'sell'
    
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:

                self.logger.debug(f"{symbol}: {orderSide} - TP at {adjusted_price} Starting....  ")
                
                self.exchange.create_order(
                    symbol=symbol,
                    type='optimal_limit_ioc',
  
                    price=adjusted_price,
                    side=orderSide,
                    amount=amount,
                    params=tp_params
                )
          
                self.logger.info(f"{symbol}: TP at {adjusted_price} Done.")
                break
                
               
            except ccxt.NetworkError as e:
                # 处理网络相关错误
                retry_count += 1
                self.logger.warning(f"!! 设置止盈单时发生网络错误,正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)  # 重试前等待1秒
                continue
            except ccxt.ExchangeError as e:
                # 处理交易所API相关错误
                retry_count += 1
                self.logger.warning(f"!! 设置止盈单时发生交易所错误,正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)
                continue
            except Exception as e:
                # 处理其他未预期的错误
                retry_count += 1
                self.logger.warning(f"!! 设置止盈单时发生未知错误,正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)
                continue
            
        if retry_count >= max_retries:
            # 重试次数用完仍未成功设置止损单
            self.logger.warning(f"!! {symbol} 设置止盈单时重试次数用完仍未成功设置成功。 ")
            return False
        return True 
        

            
    def set_stop_loss(self, symbol, position, stop_loss_price:Decimal=None , ord_type='conditional') -> bool:
        """
        设置止盈单
        :param symbol: 交易对
        :param position: 持仓信息
        :param stop_loss_price: 止损价格
        :param ord_type: 订单类型 ord_type: 'conditional'|'market'|'limit'
        :return: 是否成功设置止盈单
        """
        # 计算下单数量
        amount = abs(self.toDecimal(position['contracts']))
    
        if amount <= 0:
            self.logger.warning(f"{symbol}: amount is 0 for {symbol}")
            return

        # 止损单逻辑 
        adjusted_price = self.format_price(symbol, stop_loss_price)
        
        # 默认市价止损，委托价格为-1时，执行市价止损。
        sl_params = {
            'slTriggerPx':adjusted_price , 
            'slOrdPx':'-1', # 委托价格为-1时，执行市价止损
            # 'slOrdPx' : adjusted_price,
            'slTriggerPxType':'last',
            'tdMode':position['marginMode'],
            'sz': str(amount),
            # 'closeFraction': '1',
            'cxlOnClosePos': True,
            'reduceOnly':True
        }
        if ord_type == 'limit':
            sl_params['slOrdPx'] = adjusted_price
        
        side = 'long' if position['side'] == 'short' else 'short' # 和持仓反向相反下单
        orderSide = 'buy' if side == 'long' else 'sell'
    
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:

                self.logger.debug(f"{symbol}: {orderSide} - Pre SL at {adjusted_price} Starting....  ")
                
                self.exchange.create_order(
                    symbol=symbol,
                    # type='optimal_limit_ioc',
                    type=ord_type,
                    # type='limit',
                    price=adjusted_price,
                    side=orderSide,
                    amount=amount,
                    params=sl_params
                )
                self.logger.info(f"{symbol}: SL at {adjusted_price} Done.")
                
                break               
               
            except ccxt.NetworkError as e:
                # 处理网络相关错误
                retry_count += 1
                self.logger.warning(f"!! 设置止损单时发生网络错误,正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)  # 重试前等待1秒
                continue
            except ccxt.ExchangeError as e:
                # 处理交易所API相关错误
                retry_count += 1
                self.logger.warning(f"!! 设置止损单时发生交易所错误,正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)
                continue
            except Exception as e:
                # 处理其他未预期的错误
                retry_count += 1
                self.logger.warning(f"!! 设置止损单时发生未知错误,正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)
                continue
            
        if retry_count >= max_retries:
            # 重试次数用完仍未成功设置止损单
            self.logger.warning(f"!! {symbol} 设置止损单时重试次数用完仍未成功设置成功。 ")
            return False
        
        return True


    def calculate_sl_price_by_pct(self, symbol, position, sl_pct) -> Decimal:
        # 根据持仓方向计算止损价格
        side = position['side']
        
        # 使用decimal进行精确计算
        sl_pct_decimal = self.toDecimal(sl_pct) / 100
        entry_price_decimal = self.toDecimal(position['entryPrice'])
        
        if side == 'long':
            # 多仓止损价 = 开仓价 * (1 - 止损百分比)
            sl_price = entry_price_decimal * (1 - sl_pct_decimal)
        elif side == 'short':
            # 空仓止损价 = 开仓价 * (1 + 止损百分比) 
            sl_price = entry_price_decimal * (1 + sl_pct_decimal)
        else:
            raise ValueError(f"无效的持仓方向: {side}")
            
        # 将止损价格四舍五入到合法的价格精度
        sl_order_price = self.round_price_to_tick(symbol, sl_price)
        
        return sl_order_price
            
    def set_global_stop_loss(self, symbol, position, pair_config , stop_loss_pct=None, kLines=None) -> bool:
        """设置全局止损
        
        Args:
            symbol: 交易对
            position: 持仓信息
            pair_config: 交易对配置
            
        """
        global_sl_price = self.global_symbol_stop_loss_price.get(symbol, 0.0)
        # 如果已经触发过全局止损并且有止损单，则跳过
        self.logger.debug(f"{symbol} : 是否设置过全局止损 {self.global_symbol_stop_loss_flag.get(symbol, False)} global_sl_price={self.format_price(symbol, global_sl_price)}")  
        if self.global_symbol_stop_loss_flag.get(symbol, False):
            return
      
             
        if stop_loss_pct is None :
            stop_loss_pct = self.stop_loss_pct  
             
        # 根据持仓方向计算止损价格
        side = position['side']       
            
        sl_order_price = self.calculate_sl_price_by_pct(symbol, position, stop_loss_pct)

        precision = self.get_precision_length(symbol)
        # 验证止损价格是否合理20250312
        mark_price = self.toDecimal(position['markPrice'])
        # 验证止损价格是否合理,如果止损价格已经触发则直接平仓
        if (side == 'long' and sl_order_price >= mark_price) or \
           (side == 'short' and sl_order_price <= mark_price):
            self.close_all_positions(symbol, position)
            direction = "多头" if side == "long" else "空头"
            self.logger.warning(f"{symbol}: !! {direction}止损价格= {sl_order_price:.{precision}} {'大于等于' if side=='long' else '小于等于'}市场价格= {mark_price:.{precision}}，触发止损")
            return
                
        # 250228 没有指定止损回撤阈值stop_loss_pct...
        open_swing_point = pair_config.get('open_swing_point', False)
        if open_swing_point :
            if kLines is None :
                klines_period = str(pair_config.get('CHF', '1m'))
                kLines = self.get_historical_klines(symbol=symbol,bar=klines_period)               
       
            swing_points_length = pair_config.get('swing_points_length', 20)
            isolated_points = self.get_last_solated_point(symbol ,position , kLines,prd=swing_points_length)  
            # self.logger.debug(f"--------00 {isolated_points[0]['high']}" )
            if len(isolated_points) > 0 :
                # 获取最近的孤立点
                last_isolated_point = isolated_points[0]
                
                # 将孤立点价格转换为Decimal类型
                isolated_high = self.toDecimal(last_isolated_point['high'])
                isolated_low = self.toDecimal(last_isolated_point['low'])
                
                # 根据持仓方向设置止损价格
                sl_order_price = (
                    min(isolated_low, sl_order_price) if side == 'long'
                    else max(isolated_high, sl_order_price)
                )
                
                # 记录日志
                self.logger.debug(
                    f"{symbol} : {side} 止损价={sl_order_price:.{precision}} \n"
                    f"孤立点高点={isolated_high:.{precision}} \n"
                    f"孤立点低点={isolated_low:.{precision}}"
                )

        
        last_sl_price= self.global_symbol_stop_loss_price.get(symbol,0.0)  
        if last_sl_price != 0.0 and last_sl_price == sl_order_price:
            self.global_symbol_stop_loss_flag[symbol] = True
            self.logger.debug(f"{symbol} : [{side}] 全局止损价没变化, {last_sl_price:.{precision}} = {sl_order_price:.{precision}}")
            
            return 
            
        try:
            # 设置止损单
            if_success = self.set_stop_loss_take_profit(
                symbol=symbol,
                position=position,
                stop_loss_price=sl_order_price
                # take_profit_price=tp_order_price
            )
            if if_success:
                # 设置全局止损标志
                self.logger.info(f"{symbol} : [{side}] 设置全局止损价={sl_order_price:.{precision}}")
                self.global_symbol_stop_loss_flag[symbol] = True
                self.global_symbol_stop_loss_price[symbol] = sl_order_price
                
            return if_success
                
        except Exception as e:
            error_msg = f"{symbol} : 设置止损时发生错误, {str(e)}"
            self.logger.error(error_msg)
            traceback.print_exc()
            self.send_feishu_notification(error_msg)  
    
    def calculate_take_profile_price(self, symbol: str, position: dict, take_profile_pct: float, offset: int = 1) -> Decimal:
        """计算止盈价格
        Args:
            symbol: 交易对
            position: 持仓信息
            take_profile_pct: 止盈百分比
            offset: 价格偏移量
        Returns:
            Decimal: 止盈价格
        """
        # 获取最小价格变动单位和开仓价格
        tick_size = self.get_tick_size(symbol)
        
        # 获取开仓价格并转换为Decimal类型
        entry_price = self.toDecimal(position['entryPrice'])
        
        # 获取持仓方向
        side = position['side']

        # 将止盈百分比转换为小数形式的Decimal
        take_profile_pct = self.toDecimal(take_profile_pct) / 100
        
        # 计算价格偏移量
        price_offset = offset * tick_size
        
        # 根据持仓方向计算基础止盈价格
        # 多仓: 开仓价 * (1 + 止盈率)
        # 空仓: 开仓价 * (1 - 止盈率) 
        base_price = entry_price * (
            1 + take_profile_pct if side == 'long' 
            else 1 - take_profile_pct
        )
        
        # 应用偏移量调整最终止盈价格
        # 多仓: 基础价格 - 偏移量
        # 空仓: 基础价格 + 偏移量
        take_profile_price = (
            base_price - price_offset if side == 'long' 
            else base_price + price_offset
        )

        # 按照价格精度四舍五入并返回
        return self.round_price_to_tick(symbol, take_profile_price)
    
    # 计算回撤止盈价格
    def calculate_stop_loss_price(self, symbol, position, stop_loss_pct, offset=1) -> Decimal:
        tick_size = self.get_tick_size(symbol)
        market_price = self.toDecimal(position['markPrice'])
        entry_price = self.toDecimal(position['entryPrice'])
        side = position['side']
        # base_price = abs(market_price-entry_price) * (1-stop_loss_pct)
        # 计算止盈价格，用市场价格（取持仓期间历史最高）减去开仓价格的利润，再乘以不同阶段的止盈百分比。
        latest_stop_loss_price = self.toDecimal(self.global_symbol_stop_loss_price.get(symbol,None))
        # 多头仓位止损价计算
        if side == 'long':
            # 获取并更新最高价
            last_max_market_price = self.toDecimal(self.max_market_price.get(symbol, 0.0))
            self.max_market_price[symbol] = max(market_price, last_max_market_price)
            
            # 计算基准价格和止损价格
            price_diff = abs(self.max_market_price[symbol] - entry_price)
            base_price = price_diff * self.toDecimal(1 - stop_loss_pct) 
            stop_loss_price = entry_price + base_price - offset * tick_size
            
            # 如果已有止损价,取较高值
            if latest_stop_loss_price:
                stop_loss_price = max(stop_loss_price, latest_stop_loss_price)

        # 空头仓位止损价计算
        elif side == 'short':
            # 获取并更新最低价
            last_min_market_price = self.toDecimal(self.min_market_price.get(symbol, float('inf')))
            self.min_market_price[symbol] = min(market_price, last_min_market_price)
            
            # 计算基准价格和止损价格
            price_diff = abs(self.min_market_price[symbol] - entry_price)
            base_price = price_diff * self.toDecimal(1 - stop_loss_pct)
            stop_loss_price = entry_price - base_price + offset * tick_size
            
            # 如果已有止损价,取较低值
            if latest_stop_loss_price:
                stop_loss_price = min(stop_loss_price, latest_stop_loss_price)
                
        return self.round_price_to_tick(symbol,stop_loss_price)
    
    # 市价仓位平仓    
    def close_all_positions(self,symbol,position):

        amount = abs(float(position['contracts']))
        side = position['side']
        td_mode = position['marginMode']
        if amount > 0:
            try:
                self.logger.info(f"{symbol}: Preparing to close position for {symbol}, side: {side}, amount: {amount}")

                if self.position_mode == 'long_short_mode':
                    # 在双向持仓模式下，指定平仓方向
                    pos_side = 'long' if side == 'long' else 'short'
                else:
                    # 在单向模式下，不指定方向
                    pos_side = 'net'
                orderSide = 'buy' if side == 'long' else 'sell'
                
                
                params = {
                    
                    'mgnMode': td_mode,
                    'posSide': pos_side,
                    # 当市价全平时，平仓单是否需要自动撤销,默认为false. false：不自动撤单 true：自动撤单
                    'autoCxl': 'true'
            
                }

                # 发送平仓请求并获取返回值
                order = self.exchange.close_position(
                    symbol=symbol,
                    side=orderSide,
                    params=params
                )
                time.sleep(0.1)  # 短暂延迟后再试
                self.reset_take_profie(symbol)
                self.logger.info(f"{symbol} Close position response for {symbol}: {order}")
                self.send_feishu_notification(f"{symbol} 平仓订单完全成交 -{symbol} side: {side}")

            except Exception as e:
                self.logger.error(f"{symbol} Error closing position for {symbol}: {e}")
                self.send_feishu_notification(f"{symbol} Error closing position for {symbol}: {e}")             

    def check_stop_loss_trigger(self, symbol: str, position: dict) -> bool:
            """
            检查是否触发止损条件
            Args:
                symbol: 交易对
                position: 持仓信息
            Returns:
                bool: 是否需要平仓
            """
            latest_stop_loss_price = self.exchange.safe_float(self.global_symbol_stop_loss_price, symbol, 0.0)
            if latest_stop_loss_price == 0.0:
                self.logger.warning(f"{symbol}: 未设置止损价格，执行平仓")
                return True
                
            mark_price = position['markPrice']
            side = position['side']
            
            sl_price = float(self.round_price_to_tick(symbol=symbol,price=latest_stop_loss_price))
            
            if side == 'long' and mark_price < sl_price:
                self.logger.warning(f"{'*'*60}\n[非正常关闭]: {symbol} 方向 {side} - 市场价格 {mark_price} 低于止盈 {latest_stop_loss_price}，触发全局止盈\n{'*'*60}")
                return True
            elif side == 'short' and mark_price > sl_price:
                self.logger.warning(f"{'*'*60}\n[非正常关闭]: {symbol} 方向 {side} - 市场价格 {mark_price} 高于止盈价 {latest_stop_loss_price}，触发全局止盈\n{'*'*60}")
                return True
                
            return False
    
    def check_position(self, symbol, position):
        # 清理趋势相反的仓位
        # pair_config = self.trading_pairs_config.get(symbol, {})
        pair_config = self.get_pair_config(symbol)
        self.check_reverse_position(symbol=symbol, position=position, pair_config=pair_config)
        
        # 检查止损是否触发止盈
        # if self.check_stop_loss_trigger(symbol, position):
        #     self.close_all_positions(symbol=symbol, position=position)
        #     return
        
    
    def check_total_profit(self, symbol, position):
        """
        检查当前总盈利
        """
    
        total_profit = self.calculate_average_profit(symbol, position)

        # 获取开仓价和市价,转为Decimal类型提高精度
        entry_price = self.toDecimal(position['entryPrice'])
        mark_price = self.toDecimal(position['markPrice'])
        precision = self.get_precision_length(symbol)
        
        # 格式化消息,使用f-string提高可读性
        msg = (f"{symbol}: 盈利={total_profit:.2f}% "
               f"开仓={entry_price:.{precision}f} "
               f"市价={mark_price:.{precision}f}")
        self.logger.info(msg)
        self.send_feishu_notification(msg)
            
        cur_highest_total_profit = self.highest_total_profit.get(symbol, 0.0)    
        
        if total_profit > cur_highest_total_profit:
            cur_highest_total_profit = total_profit
            self.highest_total_profit[symbol] = total_profit
            
        current_tier = '无'   
        # 确定当前盈利档位
        if cur_highest_total_profit >= self.second_trail_profit_threshold:
            current_tier = "高档"
     
        elif cur_highest_total_profit>= self.first_trail_profit_threshold:
            current_tier = "中档"
         
        elif cur_highest_total_profit >= self.low_trail_profit_threshold:
            current_tier = "低档"
            
            
        if total_profit > 0.0 :
            self.logger.info(
                f"{symbol} 档位[{current_tier}]: 盈利: {total_profit:.2f}%，最高盈利: {cur_highest_total_profit:.2f}%")
                
        '''
        第一档:低档保护止盈:当盈利达到0.3%触发,要么到第二档,要么回到0.2%止盈
        第二档:盈利达到1%触发,记录最高价,最高价的80%是止盈位
        第三档:盈利达到3%触发,记录最高价,最高价的75%是止盈位
        
        '''
        # 各档止盈逻辑
        pair_config = self.get_pair_config(symbol)   
        # 根据不同档位设置止损价格,没有单独为交易对设置，用全局参数代替
        tier_config = {
            "低档": {
                "stop_loss_pct": float(pair_config.get('low_trail_stop_loss_pct',self.low_trail_stop_loss_pct)),
                "trail_tp_pct": float(pair_config.get('low_trail_tp_pct',self.low_trail_tp_pct))                
            },
            "中档": {
                "stop_loss_pct": float(pair_config.get('trail_stop_loss_pct',self.trail_stop_loss_pct)),
                "trail_tp_pct": float(pair_config.get('trail_tp_pct',self.trail_tp_pct))
            },
            "高档": {
                "stop_loss_pct": float(pair_config.get('higher_trail_stop_loss_pct',self.higher_trail_stop_loss_pct)),
                "trail_tp_pct": float(pair_config.get('higher_trail_tp_pct',self.higher_trail_tp_pct))
            }
        }

        if current_tier in tier_config:
            config = tier_config[current_tier]
            
            # 是否追踪止盈
            if self.open_trail_tp and total_profit < cur_highest_total_profit:
                cur_trail_tp_pct = round((1-total_profit/cur_highest_total_profit), 3)
                trail_tp_pct = float(config['trail_tp_pct'])
                if cur_trail_tp_pct >= trail_tp_pct:
                    self.close_all_positions(symbol=symbol, position=position)
                    msg = f"{symbol}: 盈利【{current_tier}】保护止盈={trail_tp_pct*100}%，价格回撤 -{cur_trail_tp_pct*100}%: 利润={total_profit:.2f}%，执行止盈平仓"
                    self.logger.info(msg)
                    self.send_feishu_notification(msg)
                    return

            # 记录日志
            self.logger.debug(f"{symbol}: 回撤止盈阈值: {config['stop_loss_pct']*100}%")
            
            # 计算回撤止损价格
            sl_price = self.calculate_stop_loss_price(
                symbol=symbol, 
                position=position,
                stop_loss_pct=config['stop_loss_pct']
            )
            
            # 检查价格是否变化
            latest_sl_price = self.toDecimal(self.global_symbol_stop_loss_price.get(symbol, 0.0))
            if sl_price == latest_sl_price:
                self.logger.debug(f"{symbol}: 回撤止损价格{latest_sl_price:.{precision}}未变化，不设置")
                return
                
            # 设置止损
            if_success = self.set_stop_loss(symbol, position, stop_loss_price=sl_price)
            
            if if_success:
                # 更新回撤止损价格
         
                self.global_symbol_stop_loss_price[symbol] = sl_price
                self.global_symbol_stop_loss_flag[symbol] = True
                
                # 发送通知
                msg = (f"{symbol}: 盈利达到【{current_tier}】阈值，最高总盈利: {cur_highest_total_profit:.2f}%,"
                      f"当前盈利回撤到: {total_profit:.2f}%，市场价格:{mark_price:.{precision}},"
                      f"设置回撤止损位: {sl_price:.{precision}}")
                self.logger.info(msg)
                self.send_feishu_notification(msg)
                
        else:

            # 默认全局止损
           
            self.set_global_stop_loss(symbol, position, pair_config)
            self.logger.info(f"{symbol}: 全局止损阈值: {self.stop_loss_pct:.2f}%")
            
        return
    
    def close_all_cache(self):
        self.reset_highest_profit_and_tier()
        self.reset_take_profie()
        self.positions_entry_price= {}
    
    def reset_all_cache(self, symbol):
        self.reset_highest_profit_and_tier(symbol)
        self.reset_take_profie(symbol)
        
    def monitor_total_profit(self):
        self.logger.info("启动主循环，开始监控总盈利...")

        while True:
            try:
                positions = self.fetch_positions()
        
            except Exception as e:
                self.logger.warning(f"获取仓位信息时发生错误: {e}")
                time.sleep(1)
                continue
            
            try:
                # 检查是否有仓位
                if len(positions) == 0:
                    # self.logger.debug("没有持仓，等待下一次检查...")
                    self.close_all_cache()
                    time.sleep(1)
                    continue
                
                self.logger.info("+" * 60)
                # 检查仓位总规模变化
                # current_position_size = sum(abs(float(position['contracts'])) for position in self.fetch_positions())
                # if current_position_size > previous_position_size:
                #     self.send_feishu_notification(f"检测到仓位变化操作，重置最高盈利和档位状态")
                #     self.logger.info("检测到新增仓位操作，重置最高盈利和档位状态")
                #     self.reset_highest_profit_and_tier()
                #     previous_position_size = current_position_size
                #     time.sleep(0.1)
                #     continue  # 跳过本次循环

                for position in positions:
                    symbol = position['symbol']
                    cur_entry_price = self.toDecimal(position['entryPrice'])
                   
                    if symbol in self.positions_entry_price and cur_entry_price != self.positions_entry_price[symbol]:
                        # 新开仓
                        self.reset_all_cache(symbol)
                    
                    if symbol not in self.positions_entry_price:
                        self.positions_entry_price[symbol] = cur_entry_price
                        precision = self.get_precision_length(symbol)
                        msg = f"{symbol} : ## 重新开仓。 入场方向={position['side']} 入场价格={cur_entry_price:.{precision}} ##"
                        self.logger.info(msg)
                        self.send_feishu_notification(msg)
                        
                    self.check_total_profit(symbol, position)
                    time.sleep(0.1) 
                    # 检查仓位和挂单是否有问题
                    self.check_position(symbol, position)

                self.logger.info("-" * 60)
                time.sleep(self.monitor_interval)

            except Exception as e:
                # print(e)
                error_message = f"程序异常退出: {str(e)}"
                traceback.print_exc()
                self.logger.error(error_message)
                self.send_feishu_notification(error_message)
                self.logger.info("-" * 60)
                continue
            except KeyboardInterrupt:
                self.logger.info("程序收到中断信号，开始退出...")
                break

