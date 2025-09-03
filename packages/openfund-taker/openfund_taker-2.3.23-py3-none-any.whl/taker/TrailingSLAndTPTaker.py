
from decimal import Decimal
from typing import override
from taker.TrailingSLTaker import TrailingSLTaker
'''
自动设置移动止损单
'''
class TrailingSLAndTPTaker(TrailingSLTaker):
    def __init__(self,g_config, platform_config, common_config, feishu_webhook=None, monitor_interval=4,logger=None):
        super().__init__(g_config, platform_config, common_config, feishu_webhook, monitor_interval,logger)
        self.global_symbol_take_profit_flag = {} # 记录每个symbol是否设置全局止盈标志
        self.global_symbol_take_profit_price = {} # 记录每个symbol的止盈价格
        # self.all_TP_SL_ratio = float(platform_config.get("all_TP_SL_ratio",1.5)) #The profit-loss ratio 盈亏比
        
        self.all_take_profit_pct = self.stop_loss_pct *  self.all_TP_SL_ratio
   
    def set_stop_loss_take_profit(self, symbol, position, stop_loss_price:Decimal=None, take_profit_price:Decimal=None) -> bool:
        if not stop_loss_price and not take_profit_price:
            self.logger.warning(f"{symbol}: No stop loss price or take profit price provided for {symbol}")
            return False   
        if not position:
            self.logger.warning(f"{symbol}: No position found for {symbol}")
            return False
        
        # 取消所有策略订单
        if_success = self.cancel_all_algo_orders(symbol=symbol)
        
        if if_success:
            self.global_symbol_stop_loss_price[symbol] = None
            self.global_symbol_stop_loss_flag[symbol] = False
            return
        
        if_stop_loss_success ,if_take_profit_success  = True , True     
        
        if stop_loss_price :
            if_stop_loss_success = self.set_stop_loss(symbol=symbol, position=position, stop_loss_price=stop_loss_price)
        if take_profit_price :
            if_take_profit_success = self.set_take_profit(symbol=symbol, position=position, take_profit_price=take_profit_price)
            
        is_successful =  if_stop_loss_success and if_take_profit_success
        
        order_take_profit_price = take_profit_price
        if take_profit_price is None:
            order_take_profit_price = self.calculate_take_profile_price(symbol, position, self.all_take_profit_pct)
            is_successful = self.set_take_profit(symbol, position, order_take_profit_price)    
        
        return is_successful
    
    @override
    def close_all_cache(self):
        super().close_all_cache()
        self.global_symbol_take_profit_flag.clear()
        self.global_symbol_take_profit_price.clear()
    @override    
    def reset_all_cache(self, symbol):
        self.reset_highest_profit_and_tier(symbol)
        self.reset_take_profie(symbol)
        self.global_symbol_take_profit_flag[symbol] = False
        self.global_symbol_take_profit_price[symbol] = None