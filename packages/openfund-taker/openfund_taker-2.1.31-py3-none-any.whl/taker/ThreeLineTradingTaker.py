# -*- coding: utf-8 -*-
import ccxt
import time
import logging
import requests
from logging.handlers import TimedRotatingFileHandler


class ThreeLineTradingTaker:
    def __init__(self, config, feishu_webhook=None, monitor_interval=60):
        self.stop_loss_pct = config["all_stop_loss_pct"]  # 全局止损百分比
        
        self.feishu_webhook = feishu_webhook
        self.monitor_interval = monitor_interval  # 监控循环时间是分仓监控的3倍
        self.global_symbol_stop_loss_flag = {} # 记录每个symbol是否设置全局止损
        
        
        # 配置交易所
        self.exchange = ccxt.okx({
            'apiKey': config["apiKey"],
            'secret': config["secret"],
            'password': config["password"],
            'timeout': 3000,
            'rateLimit': 50,
            'options': {'defaultType': 'future'},
            'proxies': {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'},
        })
        
        # 配置日志
        log_file = "log/okx_ThreeLineTradingBot.log"
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8')
        file_handler.suffix = "%Y-%m-%d"
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        self.logger = logger
        self.position_mode = self.get_position_mode()  # 获取持仓模式

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
                if response.status_code == 200:
                    self.logger.info("飞书通知发送成功")
                else:
                    self.logger.error("飞书通知发送失败，状态码: %s", response.status_code)
            except Exception as e:
                self.logger.error("发送飞书通知时出现异常: %s", str(e))
    # 获取当前持仓
    def fetch_positions(self):
        try:
            positions = self.exchange.fetch_positions()
            return positions
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return []
    # 获取当前委托
    def fetch_open_orders(self,symbol,params={}):
        try:
            orders = self.exchange.fetch_open_orders(symbol=symbol,params=params)
            return orders
        except Exception as e:
            self.logger.error(f"Error fetching open orders: {e}")
            return []
    # 放弃当前委托
    def cancel_all_algo_orders(self,symbol):
        
        params = {
            "ordType": "conditional",
        }
        orders = self.fetch_open_orders(symbol=symbol,params=params)
        # 如果没有委托订单则直接返回
        if not orders:
            self.global_symbol_stop_loss_flag.clear()
            self.logger.debug(f"{symbol} 未设置策略订单列表。")
            return
     
        algo_ids = [order['info']['algoId'] for order in orders if 'info' in order and 'algoId' in order['info']]
        try:
            params = {
                "algoId": algo_ids,
                "trigger": 'trigger'
            }
            rs = self.exchange.cancel_orders(ids=algo_ids, symbol=symbol, params=params)
            self.global_symbol_stop_loss_flag.clear()
            # self.logger.debug(f"Order {algo_ids} cancelled:{rs}")
        except Exception as e:
            self.logger.error(f"Error cancelling order {algo_ids}: {e}")

    # 平仓
    def close_all_positions(self):
        positions = self.fetch_positions()
        for position in positions:
            symbol = position['symbol']
            amount = abs(float(position['contracts']))
            side = position['side']
            td_mode = position['marginMode']
            if amount > 0:
                try:
                    self.logger.debug(f"Preparing to close position for {symbol}, side: {side}, amount: {amount}")

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
                        'autoCxl': 'true'
              
                    }
                    # 发送平仓请求并获取返回值
                    order = self.exchange.close_position(
                        symbol=symbol,
                        side=orderSide,
                        params=params
                    )
                    time.sleep(0.1)  # 短暂延迟后再试
                    self.global_symbol_stop_loss_flag.clear()
                    self.logger.info(f"Close position response for {symbol}: {order}")
                    self.send_feishu_notification(f"平仓订单完全成交 -{symbol} side: {side}")
                    '''
                    # 检查平仓结果
                    if order['status'] == 'closed':
                        # 订单完全成交
                        filled_amount = float(order['filled'])
                        average_price = float(order['average'])
                        self.logger.info(f"平仓订单完全成交 -{symbol} side: {side}, 成交数量: {filled_amount}, 平均成交价: {average_price}")
                        self.send_feishu_notification(f"平仓订单完全成交 -{symbol} side: {side}, 成交数量: {filled_amount}, 平均成交价: {average_price}")
                    elif order['status'] == 'canceled':
                        # 订单被取消
                        self.logger.warning(f"平仓订单被取消 -{symbol} side: {side}, 取消原因: {order['info']['msg']}")
                        self.send_feishu_notification(f"平仓订单被取消 -{symbol} side: {side}, 取消原因: {order['info']['msg']}")

                    elif order['status'] == 'expired':
                        # 订单过期
                        self.logger.warning(f"平仓订单已过期 -{symbol} side: {side}, 过期原因: {order['info']['msg']}")
                        self.send_feishu_notification(f"平仓订单已过期 -{symbol} side: {side}, 过期原因: {order['info']['msg']}")
                    else:
                        # 其他状态
                        self.logger.info(f"平仓订单当前状态: -{symbol} side: {side}, 其他原因: {order['status']}")
                        self.send_feishu_notification(f"平仓订单当前状态: -{symbol} side: {side}, 其他原因: {order['status']}")
                    '''
                except Exception as e:
                    self.logger.error(f"Error closing position for {symbol}: {e}")
                    self.send_feishu_notification(f"Error closing position for {symbol}: {e}")
    # 计算平均利润
    def calculate_average_profit(self):
        positions = self.fetch_positions()
        total_profit_pct = 0.0
        num_positions = 0

        for position in positions:
            symbol = position['symbol']
            entry_price = float(position['entryPrice'])
            current_price = float(position['markPrice'])
            side = position['side']

            # 计算单个仓位的浮动盈利百分比
            if side == 'long':
                profit_pct = (current_price - entry_price) / entry_price * 100
            elif side == 'short':
                profit_pct = (entry_price - current_price) / entry_price * 100
            else:
                continue

            # 累加总盈利百分比
            total_profit_pct += profit_pct
            num_positions += 1

            # 记录单个仓位的盈利情况
            self.logger.info(f"仓位 {symbol}，方向: {side}，开仓价格: {entry_price}，当前价格: {current_price}，"
                             f"浮动盈亏: {profit_pct:.2f}%")

        # 计算平均浮动盈利百分比
        average_profit_pct = total_profit_pct / num_positions if num_positions > 0 else 0
        return average_profit_pct
    
    def round_price_to_tick(self,symbol, price):
        tick_size = float(self.exchange.market(symbol)['info']['tickSz'])
        # 计算 tick_size 的小数位数
        tick_decimals = len(f"{tick_size:.10f}".rstrip('0').split('.')[1]) if '.' in f"{tick_size:.10f}" else 0

        # 调整价格为 tick_size 的整数倍
        adjusted_price = round(price / tick_size) * tick_size
        return f"{adjusted_price:.{tick_decimals}f}"   
    
    def set_stop_loss_take_profit(self, symbol, position, stop_loss_price=None, take_profit_price=None):
        self.cancel_all_algo_orders(symbol=symbol)
        tick_size = float(self.exchange.market(symbol)['info']['tickSz'])
        stop_params = {}
            
        if not position:
            self.logger.warn(f"No position found for {symbol}")
            return
            
        amount = abs(float(position['contracts']))
        
        if amount <= 0:
            self.logger.warn(f"amount is 0 for {symbol}")
            return
        adjusted_price = self.round_price_to_tick(symbol, stop_loss_price)
            
        # 设置止损单 ccxt 只支持单向（conditional）不支持双向下单（oco、conditional）
        if stop_loss_price:
 
            
            side = 'short' 
            if position['side'] == side: # 和持仓反向相反下单
                side ='long'
                
            orderSide = 'buy' if side == 'long' else 'sell'
            
            stop_params = {
                # 'slTriggerPx':adjusted_price + tick_size if orderSide == 'sell' else adjusted_price - tick_size, # 触发价格比订单价格要提前，让订单触发
                # 'slOrdPx':adjusted_price,
                'slTriggerPx':adjusted_price , 
                'slOrdPx':'-1', # 委托价格为-1时，执行市价止损
                'slTriggerPxType':'mark',
                'tdMode':position['marginMode'],
                'sz': str(amount),
                'cxlOnClosePos': True,
                'reduceOnly':True
            }   
            self.exchange.create_order(
                symbol=symbol,
                type='conditional',
                side=orderSide,
                amount=amount,
                params=stop_params
            )
            self.logger.debug(f"+++ Stop loss order set for {symbol} at {stop_loss_price}")
          
    # 修改策略交易    
    def edit_order(self,symbol, position, stop_loss_price=None, take_profit_price=None):
        '''
        策略交易
        POST /api/v5/trade/order-algo
        type 订单类型
        conditional：单向止盈止损
        oco：双向止盈止损

        chase: 追逐限价委托，仅适用于交割和永续
        trigger：计划委托
        move_order_stop：移动止盈止损
        twap：时间加权委托
        '''
        # 构建修改订单的参数
        params = {
            "algoId": position['info']['closeOrderAlgo'][0]['algoId'],
            "tdMode": position['marginMode'],  # 交易模式，如现金模式
            "side": position['side'],
            "ordType": "conditional",
            "closeFraction": "1", # 全仓
            # 止盈止损参数
            "tpTriggerPx": str(take_profit_price), # 止盈触发价格
            "tpOrdPx": str(take_profit_price), # 止盈委托价格
            "tpTriggerPxType":'last',  # 触发价格类型
            # "slTriggerPx": str(stop_loss_price),
            # "slOrdPx": str(stop_loss_price), # 止损
            # "slTriggerPxType":'mark',
            "cxlOnClosePos":True, # 平仓时取消订单
            "reduceOnly":True # 仅平仓
        }
        self.logger.info(f"algoId: {position['info']['closeOrderAlgo'][0]['algoId']}")
        
        try:
            # 修改订单,止盈止损
            modified_order = self.exchange.edit_order(
                id=position['info']['closeOrderAlgo'][0]['algoId'],
                symbol=symbol,
                type="conditional",
                side=position['side'],
                # amount=str(position['contracts']),
                # price=new_price,
                params=params
            )
            print('订单修改成功:', modified_order)        
        except KeyboardInterrupt:
            self.logger.info("程序收到中断信号，开始退出...")
        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            self.logger.error(error_message)
            self.send_feishu_notification(error_message)
            
    def set_global_stop_loss(self, symbol, position, side, stop_loss_algo):
        """设置全局止损
        
        Args:
            symbol: 交易对
            position: 持仓信息
            side: 持仓方向
            stop_loss_algo: 止损算法信息
        """
        # 如果已经触发过全局止损并且有止损单，则跳过
        if self.global_symbol_stop_loss_flag.get(symbol, False) and stop_loss_algo:
            return
            
        # 根据持仓方向计算止损价格
        if side == 'long':
            stop_loss_price = position['entryPrice'] * (1 - self.stop_loss_pct/100)
        elif side == 'short': 
            stop_loss_price = position['entryPrice'] * (1 + self.stop_loss_pct/100)
            
        try:
            # 设置止损单
            self.set_stop_loss_take_profit(
                symbol=symbol,
                position=position,
                stop_loss_price=stop_loss_price
            )
            self.logger.debug(f"{symbol} - {side} 设置全局止损价: {stop_loss_price}")
            
            # 设置全局止损标志
            self.global_symbol_stop_loss_flag[symbol] = True
                
        except Exception as e:
            error_msg = f"{symbol} - 设置止损时发生错误: {str(e)}"
            self.logger.error(error_msg)
            self.send_feishu_notification(error_msg)         
    
    
    def monitor_klines(self):
        self.logger.info("启动主循环，开始监控K线...")
        
        try:
            while True:
                positions = self.fetch_positions()
                # 检查是否有仓位
                if not positions:
                    # self.logger.debug("没有持仓，等待下一次检查...")
                    time.sleep(1)
                    continue

                total_profit = self.calculate_average_profit()
                if total_profit > 0.0 :
                    self.logger.info(f"当前总盈利: {total_profit:.2f}%")
                    self.send_feishu_notification(f"当前总盈利: {total_profit:.2f}%")
         
 
                
                for position in positions:
                    symbol = position['symbol']
                    current_price = float(position['markPrice'])
                    side = position['side']
                    ctime = position['timestamp']
                    stop_loss_algo = position['info']['closeOrderAlgo']
                    # 计算当前时间与开仓时间的差值（毫秒转换为分钟）TODO 目前是写死的分钟
                    time_diff = (time.time() * 1000 - ctime) / (1000 * 60)
                    # 如果持仓时间不足3分钟，全局止损
                    if time_diff < 3 :
                        # 调用设置全局止损函数
                        self.set_global_stop_loss(symbol, position, side, stop_loss_algo)
                        continue

                    # 三根k线之后开始进行三线移动止盈
                    else:
                        '''
                        取当前K线的前三根K线中最高/低的值作为止盈位。
                        '''    
                        # 获取 K 线数据
                        ohlcv = self.exchange.fetch_ohlcv(symbol, '1m')
                        # 确保有足够的 K 线数据
                        if len(ohlcv) >= 4:
                            # 取当前 K 线的前三根 K 线
                            previous_three_candles = ohlcv[-4:-1]
                            # 提取每根 K 线的最高价
                            
                            high_prices = [candle[2] for candle in previous_three_candles]
                            # 提取每根 K 线的最低价
                            low_prices = [candle[3] for candle in previous_three_candles]
                            # 找出最大值
                            max_high = max(high_prices)
                            # 找出最小值
                            min_low = min(low_prices)
                            self.logger.debug(f"当前K线的前三根K线 最高价: {max_high}, 最低价: {min_low}")
                        else:
                            self.logger.info("K 线数据不足，无法计算。")
                            continue

                        # 多头持仓
                        if side == 'long':
                            stop_loss_price = min_low
                            # 设置三根K线的最低价为止损
                            self.logger.debug(f"{symbol} 多头持仓, 前三根K线最低价 {min_low}设置为止盈线。")
                        # 空头持仓
                        elif side == 'short':
                            # 设置三根K线的最高价为止损
                            stop_loss_price = max_high
                            self.logger.debug(f"{symbol} 空头持仓, 前三根K线最高价 {max_high}设置为止盈线。")
                            
                        try:
                            # TODO 止损价格上下浮动一个单位    
                            self.set_stop_loss_take_profit(
                                symbol=symbol,
                                position=position,
                                stop_loss_price=stop_loss_price)
                            self.logger.debug(f"{symbol} - 设置止损价格: {stop_loss_price}")
                        except Exception as e:
                            self.set_global_stop_loss(symbol, position, side, stop_loss_algo)
                            error_msg = f"{symbol} - 设置止损时发生错误: {str(e)}"
                            self.logger.error(error_msg)
                            self.send_feishu_notification(error_msg)
                            continue
                        
                            
                time.sleep(self.monitor_interval)

        except KeyboardInterrupt:
            self.logger.info("程序收到中断信号，开始退出...")
        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            self.logger.error(error_message)
            self.send_feishu_notification(error_message)

