# -*- coding: utf-8 -*-
import traceback
from typing import override


from maker.SMCStrategyMaker import SMCStrategyMaker

class BestFVGStrategyMaker(SMCStrategyMaker):
    def __init__(self, config, platform_config, common_config, feishu_webhook=None,logger=None):
        super().__init__(config, platform_config, common_config, feishu_webhook, logger)
  

        self.htf_last_CHoCH = {} #记录HTF的CHoCH struct
        
    def check_price_in_fvg(self, df, side, fvg, struct_index=None):
        """
        检查最大或最小价格是否在FVG范围内
        Args:
            df: DataFrame, 包含价格数据的DataFrame            
            side: str, 方向 'buy' or 'sell'
            fvg: Dic, FVG
            struct_index: int, 从哪个index开始检查，默认None
        Returns:
            bool: 是否在FVG范围内
        """
        if fvg is None:
            return False
        
        data = df.copy()

        fvg_top = fvg["top"]
        fvg_bot = fvg["bot"]
        fvg_index = fvg["index"]
        
        # bug2.2.5_1，未等到折价区FVG就开单
        # if struct_index is not None:
        #     data = data.iloc[struct_index:]
        '''
            FixMe: bug2.2.5_1 20230502 
            检查价格是否在FVG范围内,bar_index，跳过FVG相关的三根K线，从FVG下一根的K线开始检查
            并且满足bar_index要从struct_index之后，struct_index和FVG_index 不一定哪个大，取最晚的index。
        '''
        start_index = max(struct_index,fvg_index+2) # 
      
        if fvg_index is not None:
            data = data.iloc[min(len(data),start_index):].copy()
        
        
        # 检查价格是否在FVG范围内,bar_index 从struct_index
        if side == 'buy':
            # 多头趋势检查最低价是否进入FVG区域
            min_price = min(data['low'])
            return min_price <= fvg_top
        else:
            # 空头趋势检查最高价是否进入FVG区域
            max_price = max(data['high'])
            return fvg_bot <= max_price 

    @override
    def reset_all_cache(self, symbol):
        """
        重置所有缓存
        """
        super().reset_all_cache(symbol)
        if symbol in self.htf_last_CHoCH:
            self.htf_last_CHoCH.pop(symbol)
    
    def process_pair(self,symbol,pair_config):
        self.logger.info("=" * 60)
        """_summary_
            1. HTF 判断struct趋势
            2. HTF 获取最新的两个极值点，设置折价区和溢价区
            3. HTF 在折价区找FVG，监控价格是否进入FVG
            
            4. LTF 判断struct趋势是否有CHoCH
            5. LTF 寻找FVG，下单
        """
        try:
            # 检查是否有持仓，有持仓不进行下单
            if self.check_position(symbol=symbol) :
                self.reset_all_cache(symbol)
                self.logger.info(f"{symbol} : 有持仓合约，不进行下单。")          
                return           
           
            
            smc_strategy = pair_config.get('smc_strategy',{})

            """
            获取策略配置
            """
            htf = str(smc_strategy.get('HTF','15m'))  
            ltf = str(smc_strategy.get('LTF', '1m'))           
            htf_prd = int(smc_strategy.get('HTF_swing_points_length',15))
            ltf_prd = int(smc_strategy.get('LTF_swing_points_length',3))
            htf_entry_struct = str(smc_strategy.get('HTF_entry_struct','CHoCH'))
            ltf_entry_struct = str(smc_strategy.get('LTF_entry_struct','CHoCH'))
            enable_FVG = bool(smc_strategy.get('enable_FVG',True)) # 是否启用FVG
            enable_OB = bool(smc_strategy.get('enable_OB',True))# 是否启用OB
            self.logger.info(f"{symbol} : BestFVGSMC策略 {ltf}|{htf} \nenable_FVG={enable_FVG} enable_OB={enable_OB} \nHTF_swing_points_length={htf_prd} LTF_swing_points_length={ltf_prd}")
            
            htf_Klines = self.get_historical_klines(symbol=symbol, bar=htf)
            htf_df = self.format_klines(htf_Klines)         
            precision = self.get_precision_length(symbol)
   
            # 初始化HTF趋势相关变量
            htf_side, valid_htf_struct = None, None
            htf_struct = {"struct": "None"}
            # 获取上一个周期的CHoCH结构
            htf_last_CHoCH = self.htf_last_CHoCH.get(symbol,None)
            # 获取最新的CHoCH结构
            htf_struct = self.detect_struct(htf_df, prd=htf_prd) # HTF结构要严谨，prd周期要长一些
        
            # 处理最新结构未形成的情况，使用上一个周期的结构
            if htf_struct["struct"] == "None":
                if htf_last_CHoCH:
                                  
                    valid_htf_struct = htf_last_CHoCH
                    self.logger.debug(f"{symbol} : {htf} 使用之前 {htf_entry_struct} struct。{valid_htf_struct['struct']} prd={htf_prd}。")
                else:
                    self.logger.debug(f"{symbol} : {htf} 未形成有效的 {htf_entry_struct} struct,不下单。")
                    return
            else:
                valid_htf_struct = htf_struct
                self.logger.debug(f"{symbol} : {htf} 形成新的struct。{valid_htf_struct['struct']} prd={htf_prd}。")
            
            # 检查是否已形成有效的结构
            htf_struct_label = valid_htf_struct["struct"]
            htf_side = valid_htf_struct["side"] 
            
            # 20250417 优化: 最新的HTF_entry_struct结构要满足，才能下单。
            if  htf_entry_struct not in htf_struct_label :
                # 如果是反转结构判断一下方向是否一致，不一致重置缓存。
                if "CHoCH" in htf_struct_label and htf_last_CHoCH and htf_last_CHoCH["side"] != htf_side:
                    self.htf_last_CHoCH[symbol] = {}
                    
                self.logger.debug(f"{symbol} : {htf} is {htf_struct_label}, 未形成有效的 {htf_entry_struct} struct,不下单。")
                return
             
    
            # 1. HTF 判断struct趋势（CHoCH\SMS\BMS） ,HTF struct 看趋势，CTF 看FVG和OB的位置    
            htf_pivot_high = valid_htf_struct["pivot_high"]
            htf_pivot_low = valid_htf_struct["pivot_low"]            
            htf_mid_line = self.calculate_ce(symbol,htf_pivot_high,htf_pivot_low)
            
            # 2. HTF 获取最新的两个极值点，设置折价(discount)区和溢价(premium)区  
            # 计算溢价和折价区
            premium_box = {
                'top': htf_pivot_high,
                'bot': htf_mid_line,
                'ce': self.calculate_ce(symbol,htf_pivot_high,htf_mid_line)
            }
            discount_box = {
                'top': htf_mid_line,
                'bot': htf_pivot_low,
                'ce': self.calculate_ce(symbol,htf_mid_line,htf_pivot_low)
            }
            
            self.logger.info(f"{symbol} : {htf} 趋势={htf_struct_label} 匹配 {htf_entry_struct} struct")
            self.logger.debug(f"{symbol} : {htf}\npivot_high={htf_pivot_high:.{precision}} pivot_low={htf_pivot_low:.{precision}} mid_line={htf_mid_line:.{precision}}\n溢价区={premium_box}\n折价区={discount_box}")

            # 3. find HTF FVG           
            
            pivot_index = valid_htf_struct["pivot_low_index"] if htf_side == "buy" else valid_htf_struct["pivot_high_index"]       
            # TODO 优化: 缓存FVG，不用每次都计算，且被平衡
            htf_fvg_boxes = self.find_fvg_boxes(htf_df,side=htf_side,threshold=htf_mid_line,check_balanced=False,pivot_index=pivot_index)
            if len(htf_fvg_boxes) == 0:
                self.logger.debug(f"{symbol} : HTF={htf} 方向={htf_side}, 未找到 FVG")
                return 
            self.logger.debug(f"{symbol} : HTF_fvg_box={htf_fvg_boxes[-1]}")
            
            # 判断是否进入最近的FVG     
            if_tap_into_fvg = self.check_price_in_fvg(htf_df,htf_side,htf_fvg_boxes[-1],valid_htf_struct["index"])
            if not if_tap_into_fvg:
                self.logger.debug(f"{symbol} : 价格[未进入] HTF_FVG区域，不进行下单")
                return
            else:
                self.logger.debug(f"{symbol} : 价格[进入] HTF_FVG区域，开始下单。\n fvgbox={htf_fvg_boxes[-1]}")

            # 4. LTF 判断struct趋势是否有CHoCH
  
  
            ltf_kLines = self.get_historical_klines(symbol=symbol, bar=ltf)
            ltf_df = self.format_klines(ltf_kLines)            
         
            ltf_struct = self.detect_struct(ltf_df,prd=ltf_prd)
            ltf_struct_label = ltf_struct["struct"]
            ltf_struct_side = ltf_struct["side"]
            ltf_last_pivot_high = ltf_struct["pivot_high"]
            ltf_last_pivot_low = ltf_struct["pivot_low"]
            ltf_last_mid_line = self.calculate_ce(symbol,ltf_last_pivot_high,ltf_last_pivot_low)
            
            # 计算溢价和折价区
            ltf_premium_box = {
                'top': ltf_last_pivot_high,
                'bot': ltf_last_mid_line,
                'ce': self.calculate_ce(symbol,ltf_last_pivot_high,ltf_last_mid_line)
            }
            ltf_discount_box = {
                'top': ltf_last_mid_line,
                'bot': ltf_last_pivot_low,
                'ce': self.calculate_ce(symbol,ltf_last_mid_line,ltf_last_pivot_low)
            }
            
            self.logger.info(f"{symbol} : {ltf} 趋势={ltf_struct_label} struct={ltf_struct}")
            self.logger.debug(f"{symbol} : {ltf} \npivot_high={ltf_last_pivot_high} pivot_low={ltf_last_pivot_low:.{precision}} mid_line={ltf_last_mid_line:.{precision}}\n溢价区={ltf_premium_box}\n折价区={ltf_discount_box}")


            # 5. LTF 寻找FVG，下单
       
            if ltf_struct_label == "None" or htf_side != ltf_struct_side :
                self.logger.debug(f"{symbol} : {htf} {htf_struct_label} VS {ltf} {ltf_struct_label} 趋势不一致{htf_side}|{ltf_struct_side}，不进行下单")
                return 
            
            threshold = 0.0
            # 如果LTF结构是BMS，趋势强，FVG的范围不要求，只要能接上就行，如果结构是CHoCH或SMS，趋势弱，则取折价区或溢价区的FVG
            if 'BMS' in ltf_struct_label:
                threshold = ltf_last_pivot_high if ltf_struct_side == "buy" else ltf_last_pivot_low
            else:
                threshold = self.calculate_ce(symbol,ltf_last_pivot_high,ltf_last_pivot_low)
            
            pivot_index = ltf_struct["pivot_low_index"] if ltf_struct_side == "buy" else ltf_struct["pivot_high_index"]
                      
            ltf_fvg_boxes = self.find_fvg_boxes(ltf_df,side=ltf_struct_side,threshold=threshold,pivot_index=pivot_index)
    
            if len(ltf_fvg_boxes) == 0:
                self.logger.debug(f"{symbol} : LTF={ltf} 趋势={ltf_struct_label}, 未找到 FVG")
                return
            
            self.logger.debug(f"{symbol} : LTF_fvg_box={ltf_fvg_boxes[-1]}")
        
                
            # 4. LTF 寻找FVG，下单      
            order_price = self.toDecimal(ltf_fvg_boxes[-1]["top"] if ltf_struct_side == "buy" else ltf_fvg_boxes[-1]["bot"] )                     

            latest_order_price = self.toDecimal(self.place_order_prices.get(symbol,0))
            if order_price == latest_order_price:
                self.logger.debug(f"{symbol} : 下单价格 {order_price:.{precision}} 未变化，不进行下单。")
                return
        
              
            # 下单    
            self.cancel_all_orders(symbol=symbol) 
            self.place_order(symbol=symbol, price=order_price, side=ltf_struct_side, pair_config=pair_config)
            self.place_order_prices[symbol] = order_price # 记录下单价格,过滤重复下单
            self.logger.debug(f"{symbol} : {ltf_struct_side}, 下单价格 {order_price:.{precision}}")
            
            
        except KeyboardInterrupt:
            self.logger.info("程序收到中断信号，开始退出...")
        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            self.logger.error(error_message,exc_info=True)
            traceback.print_exc()
            self.send_feishu_notification(error_message)
        finally:
            self.logger.info("-" * 60)

        
