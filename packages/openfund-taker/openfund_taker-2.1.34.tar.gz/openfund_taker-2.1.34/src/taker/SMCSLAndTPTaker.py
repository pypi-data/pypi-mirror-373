from typing import override
import pandas as pd

from taker.TrailingSLTaker import TrailingSLTaker

class SMCSLAndTPTaker(TrailingSLTaker):
    def __init__(self,g_config, platform_config, feishu_webhook=None, monitor_interval=4,logger=None):
        super().__init__(g_config, platform_config, feishu_webhook, monitor_interval,logger)
        self.global_symbol_take_profit_flag = {} # 记录每个symbol是否设置全局止盈标志
        self.global_symbol_take_profit_price = {} # 记录每个symbol的止盈价格
        self.htf_liquidities = {}
        self.all_TP_SL_ratio = float(platform_config.get("all_TP_SL_ratio",1.5)) #The profit-loss ratio 盈亏比
        self.open_trail_profit = bool(platform_config.get("open_trail_profit",True)) # 开仓是否设置止盈
       
    @override  
    def check_reverse_position(self,symbol,position,pair_config):
        """
        检查是否有反向持仓
        """
        self.logger.debug(f"{symbol}: 检查LTF-Struceture是否市价清仓。")
        # 根据LTF的Struceture识别
        
 
     
    def build_struct(self, df, prd=20, check_bounds=True, global_extremum=False) :
        
        """_summary_
            构建SMC结构，参考 Tradingview Smart Money Concepts Probability (Expo)@Openfund
        """
        data = df.copy()
        data['Up'] = None
        data['Dn'] = None
        data['iUp'] = None
        data['iDn'] = None
        data['pos'] = 0
        data['pattern'] = None

        # 初始化 Up 和 Dn 的第一个值
        data.at[0, 'Up'] = data.at[0, 'high']
        data.at[0, 'Dn'] = data.at[0, 'low']
        

        for index in range(1, len(data)):
      
            data.at[index, 'Up'] = max(data.at[index - 1, 'Up'], data.at[index, 'high'])
            data.at[index, 'Dn'] = min(data.at[index - 1, 'Dn'], data.at[index, 'low'])
            data.at[index, 'pos'] = data.at[index - 1, 'pos']
            data.at[index, 'iUp'] = data.at[max(0,index - 1), 'iUp'] if data.at[max(0,index - 1), 'iUp'] is not None else index
            data.at[index, 'iDn'] = data.at[max(0,index - 1), 'iDn'] if data.at[max(0,index - 1), 'iDn'] is not None else index

            # 寻找枢轴高点和低点
            pvtHi = self.is_pivot_high(data, index, prd, check_bounds)
            pvtLo = self.is_pivot_low(data, index, prd, check_bounds)

            if pvtHi:
                data.at[index, 'Up'] = data.at[index, 'high']
                data.at[index, 'iUp'] = index
            if pvtLo:
                data.at[index, 'Dn'] = data.at[index, 'low']
                data.at[index, 'iDn'] = index
            # 寻找Bullish结构
            if data.at[index, 'Up'] > data.at[index - 1, 'Up']:
                data.at[index, 'iUp'] = index # TODO
                if data.at[index - 1, 'pos'] <= 0:
                    # data.at[index, 'pattern'] = 'CHoCH (Bullish)'
                    data.at[index, 'pattern'] = 'Bullish_CHoCH'
                    data.at[index, 'pos'] = 1
                elif data.at[index - 1, 'pos'] == 1 \
                        and data.at[index - 1, 'Up'] == data.at[max(0,index - prd), 'Up']:               
                    data.at[index, 'pattern'] = 'Bullish_SMS'
                    data.at[index, 'pos'] = 2
                    
                elif data.at[index - 1, 'pos'] > 1 \
                        and data.at[index - 1, 'Up'] == data.at[max(0,index - prd), 'Up']:                
                    data.at[index, 'pattern'] = 'Bullish_BMS'
                    data.at[index, 'pos'] = data.at[index - 1, 'pos'] + 1
                    
            elif global_extremum and data.at[index, 'Up'] < data.at[index - 1, 'Up']:
                data.at[index, 'iUp'] = data.at[index - 1, 'iUp']
        
            # # 寻找Bearish结构
            if data.at[index, 'Dn'] < data.at[index - 1, 'Dn']:
                data.at[index, 'iDn'] = index # TODO
                if data.at[index - 1, 'pos'] >= 0:
                
                    data.at[index, 'pattern'] = 'Bearish_CHoCH'
                    data.at[index, 'pos'] = -1
                elif data.at[index - 1, 'pos'] == -1  \
                        and data.at[index - 1, 'Dn'] == data.at[max(0,index - prd), 'Dn']:
                    data.at[index, 'pattern'] = 'Bearish_SMS'
                    data.at[index, 'pos'] = -2
                elif data.at[index - 1, 'pos'] < -1  \
                        and data.at[index - 1, 'Dn'] == data.at[max(0,index - prd), 'Dn']:
                    data.at[index, 'pattern'] = 'Bearish_BMS'
                    data.at[index, 'pos'] = data.at[index - 1, 'pos'] - 1
                    
            elif global_extremum and data.at[index, 'Dn'] > data.at[index - 1, 'Dn']:
                data.at[index, 'iDn'] = data.at[index - 1, 'iDn']
                
        return data
            
    def detect_struct(self, data, prd=20, check_valid_range=True, struct_key=None, check_bounds=True, global_extremum=False) -> dict:
        """_summary_    
            识别智能资金结构
        
        :param data: 包含 'high' 和 'low' 列的 DataFrame
        :param prd: 结构周期
        :param s1: 结构响应布尔值
        :param resp: 响应周期
        :return: 包含结构识别结果的 DataFrame
        """

        data = self.build_struct(data, prd, check_bounds, global_extremum)
               
        
        # 获取最后一个结构和位置
        last_struct = {
            "struct": None,
            "index": -1,
            "pivot_high": None,
            "pivot_high_index": -1,
            "pivot_low": None,
            "pivot_low_index": -1,
            "side": None
            
        }
        
        pivot_high_index = last_struct["pivot_high_index"] = int(data["iUp"].iloc[-1])
        pivot_low_index = last_struct["pivot_low_index"] = int(data["iDn"].iloc[-1])
        
        last_struct["pivot_high"] = float(data.loc[last_struct["pivot_high_index"], 'high'])
        last_struct["pivot_low"] = float(data.loc[last_struct["pivot_low_index"], 'low'])
        
        for i in range(len(data)-1, -1, -1):
            if check_valid_range:
                # 检查是否在pivot_high_index和pivot_low_index之间的有效范围内
                if data.at[i, 'iUp'] != -1 and data.at[i, 'iDn'] != -1:
                    # pivot_high_index = data.at[i, 'iUp'] 
                    # pivot_low_index = data.at[i, 'iDn']
                    if i < min(pivot_high_index, pivot_low_index) or i > max(pivot_high_index, pivot_low_index):
                        continue
            
            if data.at[i, 'pattern'] is not None:
                if struct_key is not None and struct_key not in data.at[i, 'pattern']:
                    continue
                last_struct["struct"] = data.at[i, 'pattern']
                last_struct["index"] = i
               
                break
        
        if last_struct['struct'] is not None :
            # 找到最后一个结构的枢轴高点和低点，如果当前是孤立点，则取前一个孤立点
            # 判断交易方向
            if 'Bearish' in last_struct["struct"]:
                last_struct["side"] = 'sell'
            else :
                last_struct["side"] = 'buy'
        else:
            last_struct['struct'] = 'None'
            last_struct["index"] = -1

            
        return last_struct
 
    def is_pivot_high(self, data, index, period, check_bounds=False):
        """
        判断当前索引处是否为枢轴高点
        :param data: 包含 'high' 列的 DataFrame
        :param index: 当前索引
        :param period: 前后比较的周期数
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
        :return: 是否为枢轴低点
        """
        if check_bounds and (index < period or index >= len(data) - period):
            return False
        current_low = data.at[index, 'low']
        prev_lows = data['low'].iloc[max(0,index - period):index]
        next_lows = data['low'].iloc[index :min(len(data),index + period + 1)]
        return all(current_low <= prev_lows) and all(current_low <= next_lows)

              
    def set_sl_by_profit(self, symbol, position, profit, pair_config, kLines=None):
        
        """
        根据利润设置止损价
        Args:
            symbol: 交易对
            position: 仓位信息
            profit: 利润
            pair_config: 交易对配置
            kLines: K线数据
        """

        total_profit = profit      

        current_tier = '无'
        # 各档止盈逻辑
        # 确定当前盈利档位
        if self.open_trail_profit and total_profit >= self.second_trail_profit_threshold:
            current_tier = "高档"
     
        elif self.open_trail_profit and total_profit>= self.first_trail_profit_threshold:
            current_tier = "中档"
         
        elif self.open_trail_profit and total_profit >= self.low_trail_profit_threshold:
            current_tier = "低档"
         
        # 根据不同档位设置止损价格,没有单独为交易对设置，用全局参数代替
        tier_config = {
            "低档": {
                "stop_loss_pct": float(pair_config.get('low_trail_stop_loss_pct',self.low_trail_stop_loss_pct)),
                         
            },
            "中档": {
                "stop_loss_pct": float(pair_config.get('trail_stop_loss_pct',self.trail_stop_loss_pct)),
            
            },
            "高档": {
                "stop_loss_pct": float(pair_config.get('higher_trail_stop_loss_pct',self.higher_trail_stop_loss_pct)),

            }
        }
        self.logger.info(
                f"{symbol} 档位[{current_tier}]: 盈利: {total_profit:.2f}%")

        if current_tier in tier_config:
            config = tier_config[current_tier]  

                 

            # 计算回撤止损价格
            sl_price = self.calculate_stop_loss_price(
                symbol=symbol, 
                position=position,
                stop_loss_pct=config['stop_loss_pct']
            )
            
            # 检查价格是否变化
            latest_sl_price = self.exchange.safe_float(self.global_symbol_stop_loss_price, symbol, 0.0)
            if sl_price == latest_sl_price:
                self.logger.debug(f"{symbol}: 回撤止损价格{latest_sl_price}未变化，不设置")
                return
            
            # 根据持仓方向判断是否需要更新止损价格
            should_update = False
            if position['side'] == 'long':
                # 多仓时,新止损价需高于当前止损价
                should_update = sl_price >= latest_sl_price
                if not should_update:
                    self.logger.debug(f"{symbol}: 多仓回撤止损价格{sl_price}低于当前止损价格{latest_sl_price}，不更新")
                else:
                    self.logger.debug(f"{symbol}: 多仓回撤止损价格{sl_price}高于当前止损价格{latest_sl_price}，更新")
            else:
                # 空仓时,新止损价需低于当前止损价
                should_update = sl_price <= latest_sl_price
                if not should_update:
                    self.logger.debug(f"{symbol}: 空仓回撤止损价格{sl_price}高于当前止损价格{latest_sl_price}，不更新")
                else:
                    self.logger.debug(f"{symbol}: 空仓回撤止损价格{sl_price}低于当前止损价格{latest_sl_price}，更新")
            
            if not should_update:
                return  
            
            self.cancel_all_algo_orders(symbol=symbol, attachType='SL')
                
            # 移动止损保护
            if_success =  self.set_stop_loss(symbol=symbol, position=position, stop_loss_price=sl_price)
            
            if if_success:
                # 更新回撤止损价格
         
                self.global_symbol_stop_loss_price[symbol] = sl_price
                self.global_symbol_stop_loss_flag[symbol] = True
                cur_highest_total_profit = self.highest_total_profit.get(symbol, 0.0) 
                
                # 发送通知
                msg = (f"{symbol}: 盈利达到【{current_tier}】阈值，最高总盈利: {cur_highest_total_profit:.2f}%,"
                      f"当前盈利回撤到: {total_profit:.2f}%，市场价格:{position['markPrice']},"
                      f"设置回撤止损位: {sl_price:.9f}")
                self.logger.info(msg)
                self.send_feishu_notification(msg)
                
        else:

            # 默认全局止损            
            if_success = self.set_global_stop_loss(symbol=symbol, position=position, pair_config=pair_config ,kLines = kLines)
            if if_success:
                # 更新回撤止损价格 
                self.global_symbol_take_profit_flag[symbol] = False
        
    def find_liquidity(self, symbol, data, liquidity_type="BSL") -> pd.DataFrame:
        """
        寻找流动性，根据side判断是做多还是做空，做多则寻找iUp，做空则寻找iDn
        Args:
            symbol (str): 交易对
            data (pd.DataFrame): 数据
            liquidity_type (str): 流动性类型，'BSL' 或 'BSL'
            
        """
        df = data.copy()
        
        is_buy = liquidity_type == 'BSL'
        col_prefix = 'iDn' if is_buy else 'iUp'
        
        return df[df.index == df[col_prefix]].sort_index(ascending=False)
    
    def detect_liquidity_for_TP(self, symbol, data, side , market_price) -> pd.DataFrame:
        """
        TP校对流动性，用市场价格校验流动性是否有效,做多则流动性在市场价格之上，做空流动性要在市场价格之下。
        Args:
            symbol (str): 交易对
            side (str): 交易方向，'long' 或 'short'
            df_liquidities (pd.DataFrame): 流动性数据
            market_price (float): 当前市场价格
            
        """
        is_buy = side == 'long'
        col_prefix = 'iUp' if is_buy else 'iDn'
        price_col = 'Up' if is_buy else 'Dn'
        
        # 设置TP,long寻找SSL,short寻找BSL
        liquidity_type = 'SSL' if is_buy else 'BSL'
        
        df_liquidities = self.find_liquidity(symbol, data, liquidity_type=liquidity_type)

        df_valid_liquidities = df_liquidities.copy()     
                 
        result_indices = []
        current_price = float('-inf') if is_buy else float('inf')
        current_i = float('inf') 
        
        # 遍历并筛选符合条件的记录
        for idx, row in df_valid_liquidities.iterrows():
            if is_buy:
                if  row[price_col] > current_price and row[price_col] > market_price and row[col_prefix] < current_i:
                    result_indices.append(idx)
                    current_price = row[price_col]
                    current_i = row[col_prefix]
            else:
                if  row[price_col] < current_price and row[price_col] < market_price and row[col_prefix] < current_i:
                    result_indices.append(idx)
                    current_price = row[price_col]
                    current_i = row[col_prefix]
                    
        return df_valid_liquidities.loc[result_indices].sort_index(ascending=False)
    
    def detect_liquidity_for_SL(self, symbol, data, side, market_price) -> pd.DataFrame:
        """
        SL校对流动性，用市场价格校验流动性是否有效,做多则流动性在市场价格之下，做空流动性要在市场价格之上。
        Args:
            symbol (str): 交易对
            side (str): 交易方向，'long' 或'short'
            df_liquidities (pd.DataFrame): 流动性数据
            market_price (float): 当前市场价格

        """
        is_buy = side == 'long'
        col_prefix = 'iDn' if is_buy else 'iUp'
        price_col = 'Dn' if is_buy else 'Up'
        # 设置SL,long寻找BSL,short寻找SSL
        liquidity_type = 'BSL' if is_buy else 'SSL'
        
        df_liquidities = self.find_liquidity(symbol, data, liquidity_type=liquidity_type)

        df_valid_liquidities = df_liquidities.copy()     
        df_valid_liquidities['was_swept'] = None  
        df_valid_liquidities['took_out'] = None   
        
        result_indices = []
        current_price = float('inf') if is_buy else float('-inf')
        current_i = float('inf') 
        took_out_status = False
        
        # 遍历并筛选符合条件的记录，找到扫过流动性的
        for idx, row in df_valid_liquidities.iterrows():
            if not is_buy:
                if row[price_col] > market_price:
                    if  row[price_col] > current_price and row[col_prefix] < current_i:
                        result_indices.append(idx)
                        
                        if current_i != float('inf')  and  not df_valid_liquidities.at[current_i, 'took_out'] :
                            df_valid_liquidities.at[idx, 'took_out'] = True
                            
                        current_price = row[price_col]
                        current_i = row[col_prefix]
                        
                    else:
                        df_valid_liquidities.at[idx, 'was_swept'] = True
               
            else:
                if row[price_col] < market_price:
                    if  row[price_col] < current_price and row[col_prefix] < current_i:
                        result_indices.append(idx)
                        
                        if current_i != float('inf')  and  not df_valid_liquidities.at[current_i, 'took_out'] :
                            df_valid_liquidities.at[idx, 'took_out'] = True
                        current_price = row[price_col]
                        current_i = row[col_prefix]
                    else:
                        df_valid_liquidities.at[idx, 'was_swept'] = True
                        
        # 过滤出took_out为True的记录
        took_out_df = df_valid_liquidities.loc[result_indices]
        took_out_df = took_out_df[took_out_df['took_out'] == True]
        return took_out_df.sort_index(ascending=False)
        
    def calculate_tp_price_by_liquidity(self, symbol, position, df_liquidities, stop_loss_pct=2, tp_sl_ratio=1.5, offset=1) -> float:
        """_summary_
        计算止盈价格，根据流动性，做多则止盈价格在流动性之上，做空则止盈价格在流动性之下。
        Args:
            symbol (_type_): _description_
            position (_type_): _description_
            df_liquidities (_type_): _description_
            stop_loss_pct (int, optional): _description_. Defaults to 2.
            tp_sl_ratio (float, optional): _description_. Defaults to 1.5.
            offset (int, optional): _description_. Defaults to 1.

        Returns:
            float: _description_
        """        
        
        tp_price = 0.0
        # market_price = float(position['markPrice'])
        
        is_buy = position['side'] == 'long'
        price_col = 'Up' if is_buy else 'Dn'
        
        # sl_price = self.global_symbol_stop_loss_price.get(symbol, float(position['markPrice']))
        entry_price = float(position['entryPrice'])
        sl_price =  self.calculate_sl_price_by_pct(symbol, position, stop_loss_pct)
        threshold = 0.0
        if is_buy and sl_price > 0 :
            threshold = float(self.round_price_to_tick(symbol, (entry_price - sl_price ) * tp_sl_ratio + entry_price))
        elif not is_buy and sl_price > 0:
            threshold = float(self.round_price_to_tick(symbol, entry_price - (sl_price - entry_price ) * tp_sl_ratio))
         

        # 过滤有效的流动性价格
        valid_mask = df_liquidities[price_col] > threshold if is_buy else df_liquidities[price_col] < threshold
        df_valid_liquidities = df_liquidities[valid_mask]
        self.logger.debug(f"{symbol} : threshold={threshold} sl_price={sl_price} 有效的流动=\n {df_valid_liquidities[['timestamp','Up','Dn']]}")
        # 获取止盈价格
        tp_price = df_valid_liquidities.iloc[0][price_col] if len(df_valid_liquidities) > 0 else threshold
        if is_buy:
            tp_price = max(tp_price, threshold)
        else:
            tp_price = min(tp_price, threshold)
        tick_size = self.get_tick_size(symbol)
        
        # 计算止盈价格 , 做多则止盈价格在流动性之下tick_size，做空则止盈价格在流动性之上tick_size。
        if is_buy:
            tp_price = tp_price - offset * tick_size
        else:   
            tp_price = tp_price + offset * tick_size
            
        
        return tp_price
    
    @override
    def close_all_cache(self):
        super().close_all_cache()
        self.htf_liquidities.clear()
        self.global_symbol_take_profit_flag.clear()
        self.global_symbol_take_profit_price.clear()


    @override
    def reset_all_cache(self, symbol):
        super().reset_all_cache(symbol)
        self.htf_liquidities[symbol] = None
        self.global_symbol_take_profit_flag[symbol] = False
        self.global_symbol_take_profit_price[symbol] = None
           
    def set_tp_by_structure(self, symbol, position, pair_config, htf_Klines=None):
        """
        根据结构设置止盈
        """
        # 如果已经触发过全局止盈，则跳过 
        if self.global_symbol_take_profit_flag.get(symbol, False):            
            self.logger.info(f"{symbol} : 已经设置过全局止盈 tp_price={self.global_symbol_take_profit_price[symbol]}")
            return

        smc_strategy = pair_config.get('smc_strategy',{})
        htf = str(smc_strategy.get('HTF','15m')) 
        htf_prd = int(smc_strategy.get('HTF_swing_points_length',3))    
         
        # 寻找HTF的流动性，作为止盈位置    
        if htf_Klines is None:
            htf_Klines = self.get_historical_klines(symbol=symbol, bar=htf)
        htf_df = self.format_klines(htf_Klines)   
        htf_df_with_struct = self.build_struct(df=htf_df,prd=htf_prd)  

        # 寻找流动性
        htf_liquidity = self.htf_liquidities.get(symbol,None)
        if htf_liquidity is None:
            htf_liquidity = self.detect_liquidity_for_TP(symbol, htf_df_with_struct, position['side'], position['markPrice'])
            self.htf_liquidities[symbol] = htf_liquidity
        
        if len(htf_liquidity) <= 0:
            self.logger.info(f"{symbol} : 没有找到流动性，不设置止盈")
            return
       
        tp_price = self.calculate_tp_price_by_liquidity(symbol, position, htf_liquidity, self.stop_loss_pct, self.all_TP_SL_ratio)
        
        self.cancel_all_algo_orders(symbol=symbol, attachType='TP')
        
        if self.set_take_profit(symbol, position, tp_price):
            self.global_symbol_take_profit_flag[symbol] = True
            self.global_symbol_take_profit_price[symbol] = tp_price
            self.logger.info(f"{symbol} : [{position['side']}] 设置全局止盈价={tp_price}")
    
 
    def check_total_profit(self, symbol, position):
        """
        检查当前总盈利
        """
        pair_config = self.get_pair_config(symbol)  
        total_profit = self.calculate_average_profit(symbol, position)     
        cur_highest_total_profit = self.highest_total_profit.get(symbol, 0.0)    
        if total_profit > cur_highest_total_profit:            
            self.highest_total_profit[symbol] = total_profit
        profit_key = "盈利" if total_profit > 0.0 else "亏损"
        msg = f"{symbol} : {profit_key}={total_profit:.2f}% 方向={position['side']} 开仓={position['entryPrice']:.6f} 市价={position['markPrice']:.6f}"
        self.logger.info(msg)
        self.send_feishu_notification(msg)    
        
        # self.cancel_all_algo_orders(symbol=symbol) 
        
        smc_strategy = pair_config.get('smc_strategy',{})
        htf = str(smc_strategy.get('HTF','15m'))    
        htf_Klines = self.get_historical_klines(symbol=symbol, bar=htf)
          

        # 1. 根据总盈利设置止损
        self.set_sl_by_profit(symbol=symbol, position=position, profit=total_profit, pair_config=pair_config, kLines=htf_Klines)
        
        # 2. 根据结构设置止盈
        self.set_tp_by_structure(symbol=symbol, position=position, pair_config=pair_config, htf_Klines=htf_Klines)
        
        
        return
     