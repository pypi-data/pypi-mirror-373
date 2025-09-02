from re import A
from typing import override

from cachetools import TTLCache
from core.smc.TF import TF
from taker.StrategyTaker import StrategyTaker

class BestTopDownStrategyTaker(StrategyTaker):
    """
    最佳顶底策略
    """
    def __init__(self, g_config,  platform_config, common_config, logger=None, exchangeKey='okx') -> None:
        super().__init__(g_config=g_config,  platform_config=platform_config, common_config=common_config, logger=logger, exchangeKey=exchangeKey)
        self.has_init_SL_TPs = {}
        self.entering_channel_tps = {} # 进入止盈监控

        cache_ttl = common_config.get('cache_ttl', 60)

        self.htf_cache = TTLCache(maxsize=100, ttl=int(cache_ttl*60))
        self.atf_cache = TTLCache(maxsize=100, ttl=int(cache_ttl*60))
        
    @override
    def reset_SL_TP(self, symbol=None, attachType='BOTH'):
        super().reset_SL_TP(symbol, attachType)
        if not symbol :
            self.has_init_SL_TPs.clear()
            self.entering_channel_tps.clear()
                  
        elif attachType==self.BOTH_KEY and symbol in self.has_init_SL_TPs:
            del self.has_init_SL_TPs[symbol]
            del self.entering_channel_tps[symbol]

    def init_SL_TP(self, symbol: str, position, tfs: dict, strategy: dict) -> bool:
        """
        设置首次止盈止损
        """
        open_body_break = strategy.get('open_body_break', True)
        
        precision = self.get_precision_length(symbol)
        # htf = tfs[self.HTF_KEY]
        
        atf = tfs[self.ATF_KEY]
        
        # 1.1  ATF Key Support & Resistance Levels 支撑或阻力关键位置(ATF 看上下的供需区位置）
        atf_df = self.get_historical_klines_df(symbol=symbol, tf=atf)
        atf_struct =self.build_struct(symbol=symbol, data=atf_df, is_struct_body_break=open_body_break)
        atf_OBs_df = self.find_OBs(symbol=symbol,struct=atf_struct)
        pos_side = position[self.SIDE_KEY]
        side = self.SELL_SIDE if pos_side == self.SHORT_KEY else self.BUY_SIDE 
        
        entering_trigger_price = 0.0 # 进入止盈监控的触发价格
    
        atf_support_OB = self.get_latest_OB(symbol=symbol,data=atf_OBs_df,trend=self.BULLISH_TREND)
        if atf_support_OB :
            atf_support_price = atf_support_OB.get(self.OB_MID_COL)
            if pos_side == self.SHORT_KEY:
                entering_trigger_price = atf_support_OB.get(self.OB_LOW_COL)
        else:
            atf_support_price = atf_struct.at[atf_struct.index[-1], self.STRUCT_LOW_COL]
    
        atf_resistance_OB = self.get_latest_OB(symbol=symbol,data=atf_OBs_df,trend=self.BEARISH_TREND)
        
        if atf_resistance_OB :
            atf_resistance_price = atf_resistance_OB.get(self.OB_MID_COL)
            if pos_side == self.LONG_KEY:
                entering_trigger_price = atf_resistance_OB.get(self.OB_HIGH_COL)
        else:
            atf_resistance_price = atf_struct.at[atf_struct.index[-1], self.STRUCT_HIGH_COL]
            
        self.logger.info(f"{symbol} : ATF {atf}, Key Support={atf_support_price:.{precision}f} "
                         f"& Key Resistance={atf_resistance_price:.{precision}f} ")
        
        etf = tfs[self.ETF_KEY]
        etf_df = self.get_historical_klines_df_by_cache(symbol=symbol, tf=etf)
        # etf_struct =self.build_struct(symbol=symbol, data=etf_df)
        etf_latest_struct = self.get_latest_struct(symbol=symbol, data=etf_df)
        

        tick_size = self.get_tick_size(symbol)
        offset = strategy.get('offset',1) # 价格偏移量， 1 代表 1 tick ， 0.000001 代表 1 p
        price_offset = offset * tick_size
        
        if side == self.BUY_SIDE:
            # sl_price = self.toDecimal(atf_support_price) - self.toDecimal(price_offset)
            # 20250610 止损价格设置ETF的结构的最低价格
            sl_price = self.toDecimal(etf_latest_struct[self.STRUCT_LOW_COL]) - self.toDecimal(price_offset)
            tp_price = self.toDecimal(atf_resistance_price) + self.toDecimal(price_offset)
        else:
            # sl_price = self.toDecimal(atf_resistance_price) + self.toDecimal(price_offset)
            # 20250610 止损价格设置ETF的结构的最高价格
            sl_price = self.toDecimal(etf_latest_struct[self.STRUCT_HIGH_COL]) + self.toDecimal(price_offset)
            tp_price = self.toDecimal(atf_support_price) - self.toDecimal(price_offset)

        self.cancel_all_algo_orders(symbol=symbol, attachType=self.SL_KEY)
        self.set_stop_loss(symbol=symbol, position=position, sl_price=sl_price)
        self.cancel_all_algo_orders(symbol=symbol, attachType=self.TP_KEY)
        self.set_take_profit(symbol=symbol, position=position, tp_price=tp_price)
        
        if entering_trigger_price > 0:
            self.entering_channel_tps[symbol] = entering_trigger_price
        return True

    def check_TP(self, symbol: str, position, tfs, strategy: dict) -> bool:
        """
        监控TP，在ETF下Bullish进入BOT或Bearish进入TOP开始监测反转结构止盈
        """
        if_pass = False
        open_body_break = strategy.get('open_body_break', True)
        
        if symbol not in self.entering_channel_tps:
            return if_pass

        entering_trigger_price = self.entering_channel_tps[symbol]
        marker_price = position[self.MARK_PRICE_KEY]
        mask = marker_price >= entering_trigger_price if position[self.SIDE_KEY] == self.LONG_KEY else marker_price <= entering_trigger_price
        
        if not mask:
            return if_pass
        
        precision = self.get_precision_length(symbol)
        self.logger.info(f"{symbol} : 进入止盈监控，当前价格{marker_price:.{precision}f}，触发价格{entering_trigger_price:.{precision}f}")
        
        # 1.2  检查反转结构
        etf = tfs[self.ETF_KEY]
        etf_side, etf_struct, etf_trend = None, None, None
        etf_df = self.get_historical_klines_df(symbol=symbol, tf=etf)                   
        etf_struct =self.build_struct(symbol=symbol, data=etf_df, is_struct_body_break=open_body_break)            
        etf_latest_struct = self.get_latest_struct(symbol=symbol, data=etf_struct)

        etf_trend = etf_latest_struct[self.STRUCT_DIRECTION_COL]  
            
        setp = "1.2.1"
        self.logger.info(f"{symbol} : {setp}. ETF {etf} Price's Current Trend is {etf_trend}。")
        # 3.2. Who's In Control 供需控制，Bullish 或者 Bearish ｜ Choch 或者 BOS
        setp = "1.2.2"
        self.logger.info(f"{symbol} : {setp}. ETF {etf} struct is {etf_latest_struct[self.STRUCT_COL]}。")
        setp = "1.2.3"
        pos_trend = self.BULLISH_TREND if position[self.SIDE_KEY] == self.LONG_KEY else self.BEARISH_TREND
        
        if pos_trend != etf_trend:
        
            self.logger.info(f"{symbol} : {setp}. ETF {etf} 市场结构{etf_latest_struct[self.STRUCT_COL]}未反转,等待...")
            return if_pass
        else:
            self.logger.info(f"{symbol} : {setp}. ETF {etf} 市场结构{etf_latest_struct[self.STRUCT_COL]}已反转。")
            if_pass = True

         
        return if_pass
    
    def trailing_SL(self, symbol: str, position, tfs, strategy: dict) :
        """
        移动止损
        :param symbol: 交易对
        :param position: 仓位
        :param tfs: 时间周期
        :param strategy: 策略配置
        :return:    
        """

        open_body_break = strategy.get('open_body_break', True)

        precision = self.get_precision_length(symbol)
        tf = tfs[self.ETF_KEY]
        position_side = position[self.SIDE_KEY]
        market_price = position[self.MARK_PRICE_KEY]
        
        # 获取ATF K线数据
        tf_df = self.get_historical_klines_df_by_cache(symbol=symbol, tf=tf)
        
        # 获取最新的PDArray
        tf_struct = self.build_struct(symbol=symbol, data=tf_df, is_struct_body_break=open_body_break)
        pdArray_side = self.BUY_SIDE if position_side == self.SELL_SIDE else self.SELL_SIDE
        tf_PDArrays_df = self.find_PDArrays(symbol=symbol, struct=tf_struct, side=pdArray_side, balanced=True)
        self.logger.info(f"{symbol} : TF {tf} 最新被平衡过的PDArray = {tf_PDArrays_df}")
        mask = tf_PDArrays_df[self.PD_HIGH_COL] < market_price if position_side == self.BUY_SIDE else tf_PDArrays_df[self.PD_LOW_COL] > market_price
        
        tf_PDArrays_df = tf_PDArrays_df[mask]
        # tf_latest_crossed_PD = self.get_latest_PDArray(symbol=symbol, data=tf_PDArrays_df, side=pdArray_side)
        if len(tf_PDArrays_df) < 2:
            self.logger.info(f"{symbol} : TF {tf} 未找到被平衡过的次新PDArray，等待。")
            return

        tf_sub_new_crossed_pd = {
                self.TIMESTAMP_COL: tf_PDArrays_df.iloc[-2][self.TIMESTAMP_COL],
                self.PD_TYPE_COL: tf_PDArrays_df.iloc[-2][self.PD_TYPE_COL],
                self.PD_HIGH_COL: tf_PDArrays_df.iloc[-2][self.PD_HIGH_COL],
                self.PD_LOW_COL: tf_PDArrays_df.iloc[-2][self.PD_LOW_COL],
                self.PD_MID_COL: tf_PDArrays_df.iloc[-2][self.PD_MID_COL],
                self.PD_WAS_BALANCED_COL: tf_PDArrays_df.iloc[-2][self.PD_WAS_BALANCED_COL],
            }
        # 用次新PDArray赋值给最新PDArray
        tf_latest_crossed_PD = tf_sub_new_crossed_pd
        # if atf_latest_crossed_PD is None:
        #     self.logger.info(f"{symbol} : ATF {atf}  未找到最新被平衡过的PDArray。")
        #     return


        # 根据方向找到对应的ce价格    
        pos_side = position[self.SIDE_KEY]
        tick_size = self.get_tick_size(symbol)
        offset = strategy.get('offset', 1)
        price_offset = offset * tick_size        
       
        latest_sl_price = self.get_stop_loss_price(symbol)
        if pos_side == self.LONG_KEY:
            # 多头找下方PDArray的ce
            sl_price = tf_latest_crossed_PD[self.PD_MID_COL] - self.toDecimal(price_offset)
            mask = sl_price > 0 and sl_price < position[self.MARK_PRICE_KEY] and (latest_sl_price is None or sl_price > latest_sl_price)
        else:
            # 空头找上方PDArray的ce  
            sl_price = tf_latest_crossed_PD[self.PD_MID_COL] + self.toDecimal(price_offset)
            mask = sl_price > 0 and sl_price > position[self.MARK_PRICE_KEY] and (latest_sl_price is None or sl_price < latest_sl_price)


        if mask:
            
            self.logger.info(f"{symbol} : TF {tf} {pos_side} 重置SL价格 = {sl_price:.{precision}f}")
            self.cancel_all_algo_orders(symbol=symbol, attachType=self.SL_KEY)
            self.set_stop_loss(symbol=symbol, position=position, sl_price=sl_price)
        else:
            # FIX BUG 06262110
            # self.logger.debug(f"{symbol} : ATF {atf} {pos_side} 未重置SL。SL价格 = {sl_price:.{precision}f} "
            #     f"最新价格 = {position[self.MARK_PRICE_KEY]:.{precision}f} last_sl={latest_sl_price:.{precision}f}")
            latest_sl_price_display = f"{latest_sl_price:.{precision}f}" if latest_sl_price is not None else "未设置"
            log_message = (f"{symbol} : 最新价格 = {position[self.MARK_PRICE_KEY]:.{precision}f} "
                           f"last_sl={latest_sl_price_display} ，find sl_price={sl_price:.{precision}f} 不满足条件。")
            self.logger.debug(log_message)
    @override
    def process_pair(self, symbol: str, position, pair_config: dict) -> None:
        """
        处理单个交易对
        """
        
        precision = self.get_precision_length(symbol)
        
        top_down_strategy = pair_config.get('top_down_strategy',{})

        """
        获取策略配置
        """
              
        tfs = {
            self.HTF_KEY: str(pair_config.get(self.HTF_KEY,'4h')) ,
            self.ATF_KEY: str(pair_config.get(self.ATF_KEY,'15m')),
            self.ETF_KEY: str(pair_config.get(self.ETF_KEY, '1m')),
        }
        
        htf = tfs[self.HTF_KEY]
        atf = tfs[self.ATF_KEY]
        etf = tfs[self.ETF_KEY]

  
        
        self.logger.info(f"{symbol} : TopDownSMC策略 {htf}|{atf}|{etf} \n")
        
        # 1.1 初始化止盈止损
        if symbol not in self.has_init_SL_TPs:      
            has_pass = self.init_SL_TP(symbol, position, tfs, top_down_strategy)
            
            if has_pass:
                self.has_init_SL_TPs[symbol] = True
                self.logger.debug(f"{symbol} : 初始化止盈止损成功。 {has_pass}。")
            else:
                self.logger.info(f"{symbol} : 初始化止盈止损失败。 {has_pass}。")
        
        # 1.2 移动止损     
        open_trailing_SL = top_down_strategy.get('open_trailing_SL', False)
        if open_trailing_SL:
            self.logger.debug(f"{symbol} : 开启移动止损...")
            self.trailing_SL(symbol, position, tfs, top_down_strategy)  
     
        # 1.3 监测止盈
        open_check_TP = top_down_strategy.get('open_check_TP', True)
        if open_check_TP:
            if not self.check_TP(symbol, position, tfs, top_down_strategy):  
                self.logger.debug(f"{symbol} : 未触发止盈监控，等待...")       
            else:
                order = self.close_position(symbol, position)
                if order:
                    self.logger.info(f"{symbol} : 已触发止盈监控，市价{position[self.MARK_PRICE_KEY]:.{precision}f}平仓。")

