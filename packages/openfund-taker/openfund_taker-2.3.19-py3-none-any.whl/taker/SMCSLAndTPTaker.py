from typing import override
from ccxt.base import precise
import pandas as pd
from decimal import Decimal


from taker.TrailingSLTaker import TrailingSLTaker

class SMCSLAndTPTaker(TrailingSLTaker):
    def __init__(self,g_config, platform_config, common_config=None, feishu_webhook=None, monitor_interval=4,logger=None):
        super().__init__(g_config, platform_config, common_config, feishu_webhook, monitor_interval,logger)
        self.global_symbol_take_profit_flag = {} # 记录每个symbol是否设置全局止盈标志
        self.global_symbol_take_profit_price = {} # 记录每个symbol的止盈价格
        self.htf_liquidities_TP = {}
        self.htf_liquidities_SL = {}
        # self.all_TP_SL_ratio = float(platform_config.get("all_TP_SL_ratio",1.5)) #The profit-loss ratio 盈亏比
        # self.open_trail_profit = bool(platform_config.get("open_trail_profit",True)) # 开仓是否设置止盈
       
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
      
            prev_up = self.toDecimal(data.at[index - 1, 'Up'])
            curr_high = self.toDecimal(data.at[index, 'high'])
            prev_dn = self.toDecimal(data.at[index - 1, 'Dn'])
            curr_low = self.toDecimal(data.at[index, 'low'])
            
            data.at[index, 'Up'] = max(prev_up, curr_high)
            data.at[index, 'Dn'] = min(prev_dn, curr_low)
            data.at[index, 'pos'] = data.at[index - 1, 'pos']
            data.at[index, 'iUp'] = data.at[max(0,index - 1), 'iUp'] if data.at[max(0,index - 1), 'iUp'] is not None else index
            data.at[index, 'iDn'] = data.at[max(0,index - 1), 'iDn'] if data.at[max(0,index - 1), 'iDn'] is not None else index

            # 寻找枢轴高点和低点
            pvtHi = self.is_pivot_high(data, index, prd, check_bounds)
            pvtLo = self.is_pivot_low(data, index, prd, check_bounds)

            if pvtHi:
                data.at[index, 'Up'] = self.toDecimal(data.at[index, 'high'])
                data.at[index, 'iUp'] = index
            if pvtLo:
                data.at[index, 'Dn'] = self.toDecimal(data.at[index, 'low'])
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
                data.at[index, 'iDn'] = index 
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
        next_highs = data['high'].iloc[index+1 :min(len(data),index + period )+1]
        return all(current_high >= prev_highs) and all(current_high > next_highs)

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
        next_lows = data['low'].iloc[index+1 :min(len(data),index + period)+1]
        return all(current_low <= prev_lows) and all(current_low < next_lows)

              
    def set_sl_by_profit(self, symbol, position, profit, pair_config, kLines=None):
        
        """
        根据扫过的流动性移动止损
        Args:
            symbol: 交易对
            position: 仓位信息
            profit: 利润
            pair_config: 交易对配置
            kLines: K线数据
        """


        
        if self.open_trail_profit and self.global_symbol_stop_loss_flag.get(symbol,False):
            
            smc_strategy = pair_config.get('smc_strategy',{})
            htf = str(smc_strategy.get('HTF','15m')) 
            htf_prd = int(smc_strategy.get('HTF_swing_points_length',3))           
            ltf = str(smc_strategy.get('LTF','1m'))
            ltf_prd = int(smc_strategy.get('LTF_swing_points_length',3))
           
            
            ctf = ltf
            ctf_prd = ltf_prd
            # ctf_Klines = kLines
            
            # 寻找LTF的流动性，作为移动止损位置
            ctf_Klines = self.get_historical_klines(symbol=symbol, bar=ctf)
            ctf_df = self.format_klines(ctf_Klines)
            ctf_df_with_struct = self.build_struct(df=ctf_df,prd=ctf_prd)
            # self.logger.debug(f"{symbol} : {ctf} ctf_df_with_struct\n{ctf_df_with_struct}")

            marketPrice = self.toDecimal(position['markPrice'])


            # 寻找流动性
            htf_liquidity_SL = self.htf_liquidities_SL.get(symbol,None)
            if htf_liquidity_SL is None:
                htf_liquidity_SL = self.detect_liquidity_for_SL(symbol, ctf_df_with_struct, position['side'], marketPrice)
                self.htf_liquidities_SL[symbol] = htf_liquidity_SL
            
            if len(htf_liquidity_SL) == 0:
                self.logger.info(f"{symbol} : {ctf} 没有找到扫荡的流动性，不重设止损")
                return
        
            sl_price = self.calculate_trailing_sl_price_by_liquidity(symbol, position, htf_liquidity_SL, self.stop_loss_pct)
       
            
            # 检查价格是否变化
            latest_sl_price = self.global_symbol_stop_loss_price.get(symbol,0.0)
            side = position['side']
            if sl_price == latest_sl_price:
                self.logger.debug(f"{symbol}: 移动止损价格{latest_sl_price}未变化，不设置")
                return
            elif (side == 'long' and sl_price < latest_sl_price) or (side == 'short' and sl_price > latest_sl_price):
                self.logger.debug(f"{symbol}: [{side}] 新移动止损价格{sl_price} 不能替换 {latest_sl_price}，不设置")                
                return
                
            
            self.cancel_all_algo_orders(symbol=symbol, attachType='SL')
                
            # 移动止损保护
            if_success =  self.set_stop_loss(symbol=symbol, position=position, stop_loss_price=sl_price)
            
            if if_success:
                # 更新回撤止损价格
         
                self.global_symbol_stop_loss_price[symbol] = sl_price
                self.global_symbol_stop_loss_flag[symbol] = True
                # cur_highest_total_profit = self.highest_total_profit.get(symbol, 0.0) 
                
                # 发送通知
                # msg = (f"{symbol}: 盈利达到【{current_tier}】阈值，最高总盈利: {cur_highest_total_profit:.2f}%,"
                #       f"当前盈利回撤到: {total_profit:.2f}%，市场价格:{position['markPrice']},"
                #       f"设置回撤止损位: {sl_price:.9f}")
                msg = (f"{symbol}: {ctf}移动止损，找到扫荡的流动性位置，设置止损: {sl_price:.9f}")
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
    
    def detect_liquidity_for_TP(self, symbol, data, side , market_price: Decimal) -> pd.DataFrame:
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
    
    def detect_liquidity_for_SL(self, symbol, data, side, market_price:Decimal) -> pd.DataFrame:
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
        df = data.copy()  
        

        # 初始化新列

        df['pivot_price'] = pd.NA
        df['is_extreme'] = False

        # 1. 根据pos值分组（连续相同pos为一个区间）

        groups = df['pos'].gt(0).ne(df['pos'].gt(0).shift()).cumsum()

        # 2. 对每个pos区间处理
        for group_id, group_data in df.groupby(groups):
            pos_val = group_data['pos'].iloc[0]
            
            if pos_val > 0:
                # 找high最大值及其第一次出现的位置
                max_high = group_data['high'].max()
                max_idx = group_data['high'].idxmax()
                df.at[max_idx, 'pivot_price'] = max_high
                df.at[max_idx, 'is_extreme'] = True
                
            elif pos_val < 0:
                # 找low最小值及其第一次出现的位置
                min_low = group_data['low'].min()
                min_idx = group_data['low'].idxmin()
                df.at[min_idx, 'pivot_price'] = min_low
                df.at[min_idx, 'is_extreme'] = True


        # self.logger.debug(f"{df[['timestamp', 'pattern','high','low','pivot_price','is_extreme']]}")
        
        struct_siginfo = "Bullish" if is_buy else "Bearish"

        # 3. 筛选CHoCH后符合条件的行
        result_indices = []
        # 倒序遍历数据
        found_choch = False
        for idx in reversed(df.index):
           
            # 检查是否有新的pattern
            current_pattern = df.at[idx, 'pattern']
            
            
            # 如果找到对应的CHoCH结构
            if current_pattern and f"{struct_siginfo}_CHoCH" == current_pattern:
                found_choch = True
                continue
   
            # 在找到CHoCH结构后,记录极值点
            if found_choch and df.at[idx, 'is_extreme']:
                result_indices.append(idx)
                found_choch = False
                
        self.logger.debug(f"result_indices = {result_indices}")
        took_out_df = df.loc[result_indices].copy()
        valid_mast = took_out_df['pivot_price'] < market_price if is_buy else took_out_df['pivot_price'] > market_price
        took_out_df = took_out_df[valid_mast]
        return took_out_df.sort_index(ascending=False)
    
   
    def calculate_trailing_sl_price_by_liquidity(self, symbol, position, df_liquidities, stop_loss_pct=2, offset=1) -> Decimal:
        """
        计算回撤止损价格，根据流动性，做多则回撤止损价格在流动性之下，做空则回撤止损价格在流动性之上。
        Args:
            symbol (str): 交易对
            position (dict): 仓位信息
            df_liquidities (pd.DataFrame): 流动性数据
            stop_loss_pct (int, optional): 回撤百分比. Defaults to 2.
            offset (int, optional): 偏移量. Defaults to 1.
        Returns:
            Decimal: 回撤止损价格
        """
        sl_price =  self.calculate_sl_price_by_pct(symbol, position, stop_loss_pct)
        precision = self.get_precision_length(symbol)

               
        is_buy = position['side'] == 'long'
        price_col = 'Dn' if is_buy else 'Up'
        self.logger.debug(f"{symbol} : SL side={position['side']} sl_price={sl_price:.{precision}} \n SL的扫荡流动性=\n {df_liquidities[['timestamp',price_col, 'is_extreme']]}")
        
        # valid_mask = df_liquidities[price_col] > sl_price if is_buy else df_liquidities[price_col] < sl_price
        # df_valid_liquidities = df_liquidities[valid_mask]
        # 获取止损价格
        # trailing_sl = df_valid_liquidities.iloc[0][price_col] if len(df_valid_liquidities) > 0 else sl_price
        trailing_sl = self.toDecimal(df_liquidities[price_col].max() if is_buy else df_liquidities[price_col].min())
                
        # 计算移动止损价格 , 做多则止损价格在流动性之下tick_size，做空则止损价格在流动性之上tick_size。
        tick_size = self.get_tick_size(symbol)
        if is_buy:
            trailing_sl = trailing_sl - offset * tick_size
        else:   
            trailing_sl = trailing_sl + offset * tick_size
            
        return self.round_price_to_tick(symbol, trailing_sl)
    
    def calculate_tp_price_by_liquidity(self, symbol, position, df_liquidities, stop_loss_pct=2, tp_sl_ratio=1.5, offset=1) -> Decimal:
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
            Decimal: _description_
        """        
        
        tp_price = Decimal('0.0')
        # market_price = float(position['markPrice'])
        
        is_buy = position['side'] == 'long'
        price_col = 'Up' if is_buy else 'Dn'
        
        # sl_price = self.global_symbol_stop_loss_price.get(symbol, float(position['markPrice']))
        # 获取开仓价格和止损价格
        entry_price = self.toDecimal(position['entryPrice'])
        sl_price = self.calculate_sl_price_by_pct(symbol, position, stop_loss_pct)
        
        # 计算止盈阈值
        threshold = Decimal('0.0')
        if sl_price <= 0:
            return threshold
            
     
        # 计算开仓价格和止损价格的差值
        price_diff = abs(entry_price - sl_price)
        
        # 根据方向计算止盈阈值
        target_price = entry_price + price_diff * self.toDecimal(tp_sl_ratio) if is_buy else entry_price - price_diff * self.toDecimal(tp_sl_ratio)
        threshold = self.round_price_to_tick(symbol, target_price)

        precision = self.get_precision_length(symbol)
         
        # 根据方向过滤有效的流动性价格
        df_liquidities[price_col] = df_liquidities[price_col].apply(self.toDecimal)
        valid_mask = df_liquidities[price_col] > threshold if is_buy else df_liquidities[price_col] < threshold
        df_valid_liquidities = df_liquidities[valid_mask]
        
        self.logger.debug(f"{symbol} : TP threshold={threshold:.{precision}} sl_price={sl_price:.{precision}} 有效的流动=\n {df_valid_liquidities[['timestamp','Up','Dn']]}")
        
        # 获取止盈价格并确保其满足方向要求
        tp_price = df_valid_liquidities.iloc[0][price_col] if len(df_valid_liquidities) > 0 else threshold
        tp_price = self.toDecimal(max(tp_price, threshold) if is_buy else min(tp_price, threshold))
        tick_size = self.get_tick_size(symbol)
        
        # 计算止盈价格 , 做多则止盈价格在流动性之下tick_size，做空则止盈价格在流动性之上tick_size。
        if is_buy:
            tp_price = tp_price - offset * tick_size
        else:   
            tp_price = tp_price + offset * tick_size
            
        
        return self.round_price_to_tick(symbol, tp_price)
    
    @override
    def close_all_cache(self):
        super().close_all_cache()
        self.htf_liquidities_TP.clear()
        self.htf_liquidities_SL.clear()
        self.global_symbol_take_profit_flag.clear()
        self.global_symbol_take_profit_price.clear()


    @override
    def reset_all_cache(self, symbol):
        super().reset_all_cache(symbol)
        self.htf_liquidities_TP[symbol] = None
        self.htf_liquidities_SL[symbol] = None
        self.global_symbol_take_profit_flag[symbol] = False
        self.global_symbol_take_profit_price[symbol] = None
           
    def set_tp_by_structure(self, symbol, position, pair_config, htf_Klines=None):
        """
        根据结构设置止盈
        """

        presision = self.get_precision_length(symbol)
       
        # 如果已经触发过全局止盈，则跳过 
        if self.global_symbol_take_profit_flag.get(symbol, False):            
            self.logger.info(f"{symbol} : 已经设置过全局止盈 tp_price={self.global_symbol_take_profit_price[symbol]:.{presision}}")
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
        htf_liquidity = self.htf_liquidities_TP.get(symbol,None)
        if htf_liquidity is None:
            htf_liquidity = self.detect_liquidity_for_TP(symbol, htf_df_with_struct, position['side'], self.toDecimal(position['markPrice']))
            self.htf_liquidities_TP[symbol] = htf_liquidity
        
        if len(htf_liquidity) <= 0:
            self.logger.info(f"{symbol} : 没有找到流动性，不设置止盈")
            return
       
        tp_price = self.calculate_tp_price_by_liquidity(symbol, position, htf_liquidity, self.stop_loss_pct, self.all_TP_SL_ratio)
        
        self.cancel_all_algo_orders(symbol=symbol, attachType='TP')
        
        if self.set_take_profit(symbol, position, tp_price):
            self.global_symbol_take_profit_flag[symbol] = True
            self.global_symbol_take_profit_price[symbol] = tp_price
            self.logger.info(f"{symbol} : [{position['side']}] 设置全局止盈价={tp_price:.{presision}}")
    
 
    def check_total_profit(self, symbol, position):
        """
        检查当前总盈利
        """
        pair_config = self.get_pair_config(symbol)  
        total_profit = self.calculate_average_profit(symbol, position)     
        cur_highest_total_profit = self.highest_total_profit.get(symbol, 0.0)    
        if total_profit > cur_highest_total_profit:            
            self.highest_total_profit[symbol] = total_profit
        
        precision = self.get_precision_length(symbol)
        entryPrice = self.toDecimal(position['entryPrice'])
        marketPrice = self.toDecimal(position['markPrice'])
        msg = f"{symbol} : 盈利={total_profit:.2f}% 方向={position['side']} 开仓={entryPrice:.{precision}f} 市价={marketPrice:.{precision}f}"
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
     