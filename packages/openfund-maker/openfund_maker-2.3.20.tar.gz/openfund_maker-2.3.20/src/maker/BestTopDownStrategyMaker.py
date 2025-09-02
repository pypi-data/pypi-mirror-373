# -*- coding: utf-8 -*-
import traceback
import pandas as pd

from typing import override
from cachetools import TTLCache
from core.smc.TF import TF
from maker.StrategyMaker import StrategyMaker

class BestTopDownStrategyMaker(StrategyMaker):
    def __init__(self, config, platform_config, common_config, logger=None, exchangeKey='okx'):
        super().__init__(config, platform_config, common_config, logger, exchangeKey)
        self.htf_last_struct = {} # 缓存HTF的最后一个结构
        self.logger = logger
        cache_ttl = common_config.get('cache_ttl', 60)
        # 跳过步骤

        self.htf_cache = TTLCache(maxsize=100, ttl=int(cache_ttl*60))
        self.atf_cache = TTLCache(maxsize=100, ttl=int(cache_ttl*60))
        
        
    @override
    def reset_all_cache(self, symbol):
        """
        重置所有缓存
        """
        super().reset_all_cache(symbol)    
        self.htf_last_struct.pop(symbol, None) 
        self.clear_cache_historical_klines_df(symbol)
        self.htf_cache.pop(symbol, None)
        self.atf_cache.pop(symbol, None)
   
        
    @override
    def process_pair(self,symbol,pair_config):
        self.logger.info("-" * 60)
        """_summary_
        HTF (Daily & 4H)
            1.1. Price's Current Trend 市场趋势
            1.2. Who's In Control 供需控制
            1.3. Key Support & Resistance Levels 关键位置
        ATF (1H & 30 Min & 15 Min)
            2.1. Market Condition
            2.2. PD Arrays
            2.3. Liquidity Areas
        ETF (5 Min & 1 Min)
            1. Reversal Signs
            2. PD Arrays
            3. Place Order 

        """
        try:
            # 是否有持仓，有持仓不进行下单
            if self.fetch_position(symbol=symbol) :
                self.reset_all_cache(symbol)
                self.logger.info(f"{symbol} : 有持仓合约，不进行下单。")          
                return           
            precision = self.get_precision_length(symbol)
            
            top_down_strategy = pair_config.get('top_down_strategy',{})

            """
            获取策略配置
            """
            htf = str(pair_config.get('HTF','4h'))  
            atf = str(pair_config.get('ATF','15m'))
            etf = str(pair_config.get('ETF', '1m')) 
            open_body_break = bool(pair_config.get('open_body_break', True))
            range_of_the_ob = float(pair_config.get('range_of_the_ob', 0.6))

            self.logger.info(f"{symbol} : TopDownSMC策略 {htf}|{atf}|{etf} open_body_break={open_body_break} range_of_the_ob={range_of_the_ob}\n")
            market_price = self.get_market_price(symbol=symbol)
            
            """
            step 1 : Higher Time Frame Analysis
            """
            step = "1"
     
            htf_cache_key = f"{symbol}_{htf}"
            if htf_cache_key not in self.htf_cache:
                # 初始化HTF趋势相关变量
                htf_side, htf_struct, htf_trend = None, None, None
                # HTF 缓存，减小流量损耗            
                htf_df = self.get_historical_klines_df_by_cache(symbol=symbol, tf=htf)
               
                htf_struct =self.build_struct(symbol=symbol, data=htf_df, is_struct_body_break=open_body_break)
        
                htf_latest_struct = self.get_latest_struct(symbol=symbol, data=htf_struct, is_struct_body_break=open_body_break)
                htf_trend = htf_latest_struct[self.STRUCT_DIRECTION_COL]
                htf_side = self.BUY_SIDE if htf_trend == self.BULLISH_TREND else self.SELL_SIDE
                    
                # 1.1. Price's Current Trend 市场趋势（HTF）
                step = "1.1"
                self.logger.info(f"{symbol} : {step}. HTF {htf} Price's Current Trend is {htf_trend}。")
                # 1.2. Who's In Control 供需控制，Bullish 或者 Bearish ｜ Choch 或者 BOS
                step = "1.2"
                self.logger.info(f"{symbol} : {step}. HTF {htf} struct is {htf_latest_struct[self.STRUCT_COL]}。")

                # 1.3. HTF Key Support & Resistance Levels 支撑或阻力关键位置(HTF 看上下的供需区位置）
                step = "1.3"
                htf_OBs_df = self.find_OBs(symbol=symbol,struct=htf_struct,is_struct_body_break=open_body_break,atr_multiplier=range_of_the_ob)
                # self.logger.debug(f"{symbol} : {step}. HTF {htf} 找到OBs\n "
                #     f"{htf_OBs_df[[self.TIMESTAMP_COL,self.OB_HIGH_COL,self.OB_LOW_COL,self.OB_MID_COL,self.OB_DIRECTION_COL]]}。")
                
                htf_support_resistance = self.get_support_resistance_from_OBs(symbol=symbol, obs_struct=htf_OBs_df)
                if htf_support_resistance is None:
                    self.logger.debug(f"{symbol} : {step}. HTF {htf} 未找到支撑位和阻力位。")
                    return
                htf_support_price = htf_support_resistance.get(self.SUPPORT_PRICE_KEY)
                htf_support_timestamp = htf_support_resistance.get(self.SUPPORT_TIMESTAMP_KEY)
                htf_resistance_price = htf_support_resistance.get(self.RESISTANCE_PRICE_KEY)
                htf_resistance_timestamp = htf_support_resistance.get(self.RESISTANCE_TIMESTAMP_KEY)
                htf_support_OB = htf_support_resistance.get(self.SUPPORT_OB_KEY)
                htf_resistance_OB = htf_support_resistance.get(self.RESISTANCE_OB_KEY)
                        
                self.logger.info(f"{symbol} : {step}. HTF {htf}, Key Support Mid ={htf_support_price:.{precision}f}({htf_support_timestamp}) & Key Resistance Mid={htf_resistance_price:.{precision}f}({htf_resistance_timestamp}) ")
                #1.4. 检查关键支撑位和阻力位之间是否有利润空间。
                step = "1.4"
                # 计算支撑位和阻力位之间的利润空间百分比
                htf_profit_percent = abs((htf_resistance_price - htf_support_price) / htf_support_price * 100)
                min_profit_percent = top_down_strategy.get('min_profit_percent', 4) # 默认最小利润空间为0.5%

                if htf_profit_percent < min_profit_percent:
                    self.logger.info(f"{symbol} : {step}. HTF {htf} 支撑位中线={htf_support_price:.{precision}f} 与阻力位中线={htf_resistance_price:.{precision}f} 之间利润空间{htf_profit_percent:.2f}% < {min_profit_percent}%，等待...")
                    return
                else:
                    self.logger.info(f"{symbol} : {step}. HTF {htf} 支撑位中线={htf_support_price:.{precision}f} 与阻力位中线={htf_resistance_price:.{precision}f} 之间利润空间{htf_profit_percent:.2f}% >= {min_profit_percent}%")
                                
                # 1.5. 检查当前价格是否在关键支撑位和阻力位，支撑位可以做多，阻力位可以做空。
                step = "1.5"
                htf_support_OB_top = None
                if htf_support_OB :
                    htf_support_OB_top = htf_support_OB.get(self.OB_HIGH_COL)
                htf_resistance_OB_bottom = None    
                if htf_resistance_OB :
                    htf_resistance_OB_bottom = htf_resistance_OB.get(self.OB_LOW_COL)
                
                # 检查支撑位做多条件
                down_support_status = False
                if htf_support_OB_top is not None:
                    if market_price <= htf_support_OB_top:
                        down_support_status = True
                        # 价格进入支撑OB，可以开始做多
                        if htf_side != self.BUY_SIDE: 
                            htf_side = self.BUY_SIDE         
                        self.logger.info(f"{symbol} : {step}. HTF {htf} 当前价格{market_price:.{precision}f} <= HTF_OB_SUPPORT_TOP({htf_support_OB_top:.{precision}f}), 开始做多{htf_side}。")
                    else:
                        self.logger.info(f"{symbol} : {step}. HTF {htf} 当前价格{market_price:.{precision}f} > HTF_OB_SUPPORT_TOP({htf_support_OB_top:.{precision}f}), 等待趋势反转。")
                else:
                    self.logger.info(f"{symbol} : {step}. HTF {htf} 未找到HTF_OB_SUPPORT_TOP。")
                
                # 检查阻力位做空条件
                up_resistance_status = False
                if htf_resistance_OB_bottom is not None:
                    if market_price >= htf_resistance_OB_bottom:
                        up_resistance_status = True
                        # 价格进入阻力OB，可以开始做空
                        if htf_side != self.SELL_SIDE: 
                            htf_side = self.SELL_SIDE         
                        self.logger.info(f"{symbol} : {step}. HTF {htf} 当前价格{market_price:.{precision}f} >= HTF_OB_RESISTANCE_BOTTOM({htf_resistance_OB_bottom:.{precision}f}), 开始做空{htf_side}。")
                    else:
                        self.logger.info(f"{symbol} : {step}. HTF {htf} 当前价格{market_price:.{precision}f} < HTF_OB_RESISTANCE_BOTTOM({htf_resistance_OB_bottom:.{precision}f}), 等待趋势反转。")
                else:
                    self.logger.info(f"{symbol} : {step}. HTF {htf} 未找到HTF_OB_RESISTANCE_BOTTOM。")
            
                step = "1.6"
                # 构建 HTF 缓存
                tf_HTF = TF(TF.HTF, htf, htf_side, htf_trend)
                tf_HTF.resistance_price = htf_resistance_price
                tf_HTF.support_price = htf_support_price
                tf_HTF.struct = htf_latest_struct
                tf_HTF.resistance_timestamp = htf_resistance_timestamp
                tf_HTF.support_timestamp = htf_support_timestamp
                tf_HTF.up_resistance_status = up_resistance_status
                tf_HTF.down_support_status = down_support_status

                self.htf_cache[htf_cache_key] = tf_HTF
                self.logger.info(f"{symbol} : {step}. HTF {htf} 构建 {htf_cache_key} 缓存成功 \n{tf_HTF}。")
            
            atf_cache_key = f"{symbol}_{atf}"
            if atf_cache_key not in self.atf_cache:
                """
                step 2 : Analysis Time Frames
                """
                # 2. ATF Step 
                # 2.1 Market Condition 市场状况（ATF 看上下的供需区位置）
                htf_resistance_timestamp = self.htf_cache[htf_cache_key].resistance_timestamp
                htf_support_timestamp = self.htf_cache[htf_cache_key].support_timestamp
                htf_side = self.htf_cache[htf_cache_key].side

                atf_side, atf_struct, atf_trend = None, None, None
                # 获取ATF的开始时间戳:取HTF支撑和阻力时间的较小值,并减去一个ATF周期,格式化为标准时间字符串
                min_htf_timestamp = min(htf_resistance_timestamp, htf_support_timestamp)
                atf_start_timestamp = (pd.Timestamp(min_htf_timestamp) - pd.Timedelta(atf)).strftime('%Y-%m-%d %H:%M:%S+08:00')
                atf_df = self.get_historical_klines_df(symbol=symbol, tf=atf, after = atf_start_timestamp)
                atf_struct =self.build_struct(symbol=symbol, data=atf_df, is_struct_body_break=open_body_break)            
                # 获取最新的市场结构,如果为空则返回None
                atf_latest_struct = self.get_latest_struct(symbol=symbol, data=atf_struct)
                if atf_latest_struct is None:
                    self.logger.info(f"{symbol} : {step}. ATF {atf} 未形成结构，等待... ")
                    return
                atf_trend = atf_latest_struct[self.STRUCT_DIRECTION_COL]
                atf_side = self.BUY_SIDE if atf_trend == self.BULLISH_TREND else self.SELL_SIDE
                # 2.1. Price's Current Trend 市场趋势（HTF ）
                step = "2.1"
                self.logger.info(f"{symbol} : {step}. ATF {atf} Price's Current Trend is {atf_trend}。")
                # 2.2. Who's In Control 供需控制，Bullish 或者 Bearish ｜ Choch 或者 BOS
                step = "2.2"
                self.logger.info(f"{symbol} : {step}. ATF {atf} struct is {atf_latest_struct[self.STRUCT_COL]}。")
                # 2.3. 检查关键支撑位和阻力位之间是否有利润空间。
                step = "2.3"
                atf_OBs_df = self.find_OBs(symbol=symbol,struct=atf_struct)
                atf_support_OB = self.get_latest_OB(symbol=symbol,data=atf_OBs_df,trend=self.BULLISH_TREND)
                if atf_support_OB :
                    atf_support_price = atf_support_OB.get(self.OB_MID_COL)
                    atf_support_timestamp = atf_support_OB.get(self.TIMESTAMP_COL)
                else:
                    atf_support_price = atf_struct.at[atf_struct.index[-1], self.STRUCT_LOW_COL]
                    atf_support_timestamp = atf_struct.at[htf_struct.index[-1], self.TIMESTAMP_COL]
            
                atf_resistance_OB = self.get_latest_OB(symbol=symbol,data=atf_OBs_df,trend=self.BEARISH_TREND)
                if atf_resistance_OB :
                    atf_resistance_price = atf_resistance_OB.get(self.OB_MID_COL)
                    atf_resistance_timestamp = atf_resistance_OB.get(self.TIMESTAMP_COL)
                else:
                    atf_resistance_price = atf_struct.at[atf_struct.index[-1], self.STRUCT_HIGH_COL]
                    atf_resistance_timestamp = atf_struct.at[atf_struct.index[-1], self.TIMESTAMP_COL]
                    
                self.logger.info(f"{symbol} : {step}.1 ATF {atf}, Key Support={atf_support_price:.{precision}f} "
                                f"& Key Resistance={atf_resistance_price:.{precision}f} ")
                
                open_check_atf_profit_room = top_down_strategy.get('open_check_atf_profit_room', True)
                if open_check_atf_profit_room :
                    # 计算支撑位和阻力位之间的利润空间百分比
                    atf_profit_percent = abs((atf_resistance_price - atf_support_price) / atf_support_price * 100)
                    if atf_profit_percent < min_profit_percent :
                        self.logger.info(f"{symbol} : {step}.2 ATF {atf} 支撑位={atf_support_price:.{precision}f} 与阻力位={atf_resistance_price:.{precision}f} "
                            f"之间利润空间{atf_profit_percent:.2f}% < {min_profit_percent}%，等待...")
                        return
                    else:
                        self.logger.info(f"{symbol} : {step}.2 ATF {atf} 支撑位={atf_support_price:.{precision}f} 与阻力位={atf_resistance_price:.{precision}f} "
                            f"之间利润空间{atf_profit_percent:.2f}% >= {min_profit_percent}%，允许下单...")
                    
                
                
                # 2.4. ATF 方向要和 HTF方向一致
                step = "2.4"
        
                if htf_side != atf_side:
                    self.logger.info(f"{symbol} : {step}. ATF {atf} is {atf_side} 与 HTF {htf} is {htf_side} 不一致，等待...")
                    return
                else:
                    self.logger.info(f"{symbol} : {step}. ATF {atf} is {atf_side} 与 HTF {htf} is {htf_side} 一致。")

                #2.5. 反转结构CHOCH， check Liquidity Areas ，检查当前结构是否是流动性摄取。
                step = "2.5"
                # if "CHOCH" in atf_struct[self.STRUCT_COL] or "BOS" in atf_struct[self.STRUCT_COL]:
                # 2.5.1. Equal Lows & Equal Highs
                if top_down_strategy.get('open_check_liquidity_areas', True):
                    end_idx = atf_latest_struct[self.STRUCT_HIGH_INDEX_COL] if atf_side == self.BUY_SIDE else atf_latest_struct[self.STRUCT_LOW_INDEX_COL]
                    last_EQ = self.find_EQH_EQL(symbol=symbol, data=atf_df, trend=atf_trend, end_idx=end_idx, pair_config=pair_config)
                    if last_EQ and last_EQ[self.HAS_EQ_KEY]:
                        price_eq = last_EQ[self.EQUAL_HIGH_COL] if atf_side == self.BUY_SIDE else last_EQ[self.EQUAL_LOW_COL]
                        self.logger.info(f"{symbol} : {step}.1 ATF {atf} {atf_side} find EQ {price_eq}")
                        # 检查是否Liquidity Sweeps
                        if (atf_side == self.BUY_SIDE and atf_latest_struct[self.STRUCT_HIGH_COL] > price_eq) \
                            or (atf_side == self.SELL_SIDE and atf_latest_struct[self.STRUCT_LOW_COL] < price_eq):
                    
                            atf_side = self.SELL_SIDE if atf_side == self.BUY_SIDE else self.BUY_SIDE
                            self.logger.info(f"{symbol} : {step}.1 ATF {atf} Liquidity Sweeps , Reverse the ATF {atf} {atf_side} side。")
                        else:
                            self.logger.info(f"{symbol} : {step}.1 ATF {atf} is not found Liquidity Sweeps .")                
                    else:    
                        self.logger.info(f"{symbol} : {step}.1 ATF {atf} is not found EQ .") 
            
                # FIXME 2.5.2. Dynamic Trendlines and Channels
                if top_down_strategy.get('open_check_dynamic_trendlines_and_channels', True):
                    atf_pre_struct = atf_struct[atf_struct[self.STRUCT_DIRECTION_COL].notna()].iloc[-2]  # 看前一个结构是否为动态趋势           
                    atf_start_index = min(atf_pre_struct[self.STRUCT_LOW_INDEX_COL] ,atf_pre_struct[self.STRUCT_HIGH_INDEX_COL])
                    atf_end_index = max(atf_latest_struct[self.STRUCT_LOW_INDEX_COL] ,atf_latest_struct[self.STRUCT_HIGH_INDEX_COL]) 

                    is_dynamic_trendlines = self.identify_dynamic_trendlines(symbol=symbol, data=atf_struct, trend=atf_trend, start_idx=atf_start_index, end_idx=atf_end_index)
                    if is_dynamic_trendlines :
                        self.logger.info(f"{symbol} : {step}.2 ATF {atf} {atf_trend} find Dynamic Trendlines .")
                    else:
                        self.logger.info(f"{symbol} : {step}.2 ATF {atf} {atf_trend} not find Dynamic Trendlines .")


                # 2.6. 在HTF供需区范围，找ATF的PDArray，FVG和OB，供需区，计算监测下单区域范围。
                step = "2.6"
                atf_pdArrays_df = self.find_PDArrays(symbol=symbol,struct=atf_struct,side=atf_side)
                
                # 不同的结构，不同位置，如果是Choch则等待价格进入PDArray，如果是BOS则等待价格进入折价区
                # 划分 折价(discount)区和溢价(premium)区
                atf_struct_high = atf_latest_struct[self.STRUCT_HIGH_COL]
                atf_struct_low = atf_latest_struct[self.STRUCT_LOW_COL]            
                atf_struct_mid = atf_latest_struct[self.STRUCT_MID_COL]
                
                if "CHOCH" in atf_struct[self.STRUCT_COL]:
                    # 找PDArray,Bullish 则PDArray的mid要小于 atf_struct_mid，Bearish 则PDArray的mid要大于 atf_struct_mid
                    # atf_discount_mid = (atf_struct_mid + atf_struct_high) / 2  if atf_trend == self.BEARISH_TREND else (atf_struct_mid + atf_struct_low) / 2
                    # mask = atf_pdArrays_df[self.PD_MID_COL] >= atf_struct_mid if atf_side == self.BUY_SIDE else atf_pdArrays_df[self.PD_MID_COL] <= atf_struct_mid
                    # atf_pdArrays_df = atf_pdArrays_df[mask]
                    # if len(atf_pdArrays_df) == 0:
                    #     self.logger.info(f"{symbol} : {step}.1. ATF {atf} 未找到PDArray，不下单")
                    #     return
                    # else:
                    #     # 找到最新的PDArray              
                    #     atf_vaild_pdArray = atf_pdArrays_df.iloc[-1]
                    #     self.logger.info(f"{symbol} : {step}.1. ATF {atf} 找到PDArray\n"
                    #         f"{atf_vaild_pdArray[[self.TIMESTAMP_COL,self.PD_TYPE_COL,self.PD_HIGH_COL,self.PD_LOW_COL,self.PD_MID_COL]]}。")
                    self.logger.debug(f"{symbol} : {step}.1. ATF {atf} CHOCH 结构，不下单")
                    return

                
                
                #SMS
                elif "SMS" in atf_struct[self.STRUCT_COL]:
                    # mask = atf_pdArrays_df[self.PD_MID_COL] >= atf_struct_mid if atf_side == self.BUY_SIDE else atf_pdArrays_df[self.PD_MID_COL] <= atf_struct_mid
                    mask = atf_pdArrays_df[self.PD_HIGH_COL] <= atf_struct_mid if atf_side == self.BUY_SIDE else atf_pdArrays_df[self.PD_LOW_COL] >= atf_struct_mid
                    atf_pdArrays_df = atf_pdArrays_df[mask]
                    if len(atf_pdArrays_df) == 0:
                        self.logger.info(f"{symbol} : {step}.1. ATF {atf} 在{atf_struct_mid:.{precision}f}未找到PDArray，不下单.\n mask={mask}")
                        return
                    else:
                        # 找到最新的PDArray              
                        atf_vaild_pdArray = atf_pdArrays_df.iloc[-1]
                        self.logger.info(f"{symbol} : {step}.1. ATF {atf} 找到PDArray\n"
                            f"{atf_vaild_pdArray[[self.TIMESTAMP_COL,self.PD_TYPE_COL,self.PD_HIGH_COL,self.PD_LOW_COL,self.PD_MID_COL]]}。")
                

                #BOS   
                else:
                    # atf_premium_mid = (atf_struct_mid + atf_struct_low) / 2  if atf_side == self.BUY_SIDE else (atf_struct_mid + atf_struct_high) / 2
                    # mask = atf_pdArrays_df[self.PD_HIGH_COL] >= atf_premium_mid if atf_side == self.BUY_SIDE else atf_pdArrays_df[self.PD_LOW_COL] <= atf_premium_mid
                    # atf_pdArrays_df = atf_pdArrays_df[mask]
                    # if len(atf_pdArrays_df) == 0:
                    #     self.logger.info(f"{symbol} : {step}.1. ATF {atf} ,在{atf_premium_mid:.{precision}f}未找到PDArray，不下单")
                    #     return
                    # else:
                    #     # 找到最新的PDArray              
                    #     atf_vaild_pdArray = atf_pdArrays_df.iloc[-1]
                    #     self.logger.info(f"{symbol} : {step}.1. ATF {atf} 找到PDArray\n"
                    #         f"{atf_vaild_pdArray[[self.TIMESTAMP_COL,self.PD_TYPE_COL,self.PD_HIGH_COL,self.PD_LOW_COL,self.PD_MID_COL]]}")
                    self.logger.debug(f"{symbol} : {step}.1. ATF {atf} BOS 结构，不下单")
                    return
                
                
                
                step = "2.7"

                # 2.7. 等待价格进入 PDArray
        
                if not (market_price <= atf_vaild_pdArray[self.PD_HIGH_COL] and market_price >= atf_vaild_pdArray[self.PD_LOW_COL]):
                    self.logger.info(f"{symbol} : {step}. ATF {atf} market_price={market_price:.{precision}f} 未达到PDArray范围。"
                                    f"PD_HIGH={atf_vaild_pdArray[self.PD_HIGH_COL]:.{precision}f} "
                                    f"PD_LOW={atf_vaild_pdArray[self.PD_LOW_COL]:.{precision}f} ")

                    return 
                else:
                    self.logger.info(f"{symbol} : {step}. ATF {atf} market_price={market_price:.{precision}f} 已到达PDArray范围。"
                                    f"PD_HIGH={atf_vaild_pdArray[self.PD_HIGH_COL]:.{precision}f} "
                                    f"PD_MID={atf_vaild_pdArray[self.PD_MID_COL]:.{precision}f} ")
                    
                #
                step = "2.8"
                tf_ATF = TF(TF.ATF, atf, atf_side, atf_trend)
                tf_ATF.resistance_price = atf_resistance_price
                tf_ATF.resistance_timestamp = atf_resistance_timestamp
                tf_ATF.support_price = atf_support_price
                tf_ATF.support_timestamp = atf_support_timestamp
                tf_ATF.struct = atf_latest_struct
                tf_ATF.pdArrays = atf_vaild_pdArray
                self.atf_cache[atf_cache_key] = tf_ATF
            
            # 3. ETF Step 
            step = "3.1"
            etf_side, etf_struct, etf_trend = None, None, None
            etf_df = self.get_historical_klines_df(symbol=symbol, tf=etf)                   
            etf_struct =self.build_struct(symbol=symbol, data=etf_df, is_struct_body_break=open_body_break)            
            etf_latest_struct = self.get_latest_struct(symbol=symbol, data=etf_struct)

            # 初始化ETF趋势相关变量
            if etf_latest_struct is None:
                self.logger.info(f"{symbol} : {step}. ETF {etf} 未形成结构，等待... ")
                return
            etf_trend = etf_latest_struct[self.STRUCT_DIRECTION_COL]            
            etf_side = self.BUY_SIDE if etf_trend == self.BULLISH_TREND else self.SELL_SIDE

            # 3.1. Price's Current Trend 市场趋势（ETF ）
            step = "3.1"
            self.logger.info(f"{symbol} : {step}. ETF {etf} Price's Current Trend is {etf_trend}。")
            # 3.2. Who's In Control 供需控制，Bullish 或者 Bearish ｜ Choch 或者 BOS
            step = "3.2"
            self.logger.info(f"{symbol} : {step}. ETF {etf} struct is {etf_latest_struct[self.STRUCT_COL]}。")
            

            # 3.3 Reversal Signs 反转信号
            step = "3.3" 

            # 看是否在HTF的支撑和阻力位，是则直接下单
            placing_order = False

            order_side = self.atf_cache[atf_cache_key].side
            # 如果HTF中 _up_resistance_status
            tf_HTF = self.htf_cache[htf_cache_key]
            if tf_HTF.up_resistance_status:
                order_side = self.SELL_SIDE 
                placing_order = True
            elif tf_HTF.down_support_status:
                order_side = self.BUY_SIDE
                placing_order = True

            if order_side != etf_side:
                self.logger.info(f"{symbol} : {step}. ETF {etf} 市场结构{etf_latest_struct[self.STRUCT_COL]}未反转,等待...")
                return
            else:
                self.logger.info(f"{symbol} : {step}. ETF {etf} 市场结构{etf_latest_struct[self.STRUCT_COL]}已反转。")


            # TODO "CHOCH"|"BOS" 的PDArray 入场位置不一样

            # 3.4 找 PD Arrays 价格区间（ETF 看上下的供需区位置）
            step = "3.4"
            if not placing_order:
              
                etf_pdArrays_df = self.find_PDArrays(symbol=symbol,struct=etf_struct,side=etf_side)
                # 划分 折价(discount)区和溢价(premium)区
                etf_struct_high = etf_latest_struct[self.STRUCT_HIGH_COL]
                etf_struct_low = etf_latest_struct[self.STRUCT_LOW_COL]            
                etf_struct_mid = etf_latest_struct[self.STRUCT_MID_COL]
                mask = etf_pdArrays_df[self.PD_MID_COL] >= etf_struct_mid if etf_side == self.SELL_SIDE else etf_pdArrays_df[self.PD_MID_COL] <= etf_struct_mid
                etf_pdArrays_df = etf_pdArrays_df[mask]
                if len(etf_pdArrays_df) == 0:
                    self.logger.info(f"{symbol} : {step}.1. ETF {etf} 未找到PDArray，不下单")
                    return
                else:
                    # 找到最新的PDArray              
                    etf_vaild_pdArray = etf_pdArrays_df.iloc[-1]
                    self.logger.info(f"{symbol} : {step}.1. ETF {etf} 找到PDArray.\n"
                                    f"{etf_vaild_pdArray[[self.TIMESTAMP_COL,self.PD_TYPE_COL,self.PD_HIGH_COL,self.PD_LOW_COL,self.PD_MID_COL]]}。")
                
        
                if not (market_price <= etf_vaild_pdArray[self.PD_HIGH_COL] and market_price >= etf_vaild_pdArray[self.PD_LOW_COL]):
                    self.logger.info(f"{symbol} : {step}.2. ETF {etf} market_price={market_price:.{precision}f} 未达到PDArray范围。"
                                    f"PD_HIGH={etf_vaild_pdArray[self.PD_HIGH_COL]:.{precision}f} "
                                    f"PD_LOW={etf_vaild_pdArray[self.PD_LOW_COL]:.{precision}f}")

                    return 
                else:
                    self.logger.info(f"{symbol} : {step}.2. ETF {etf} market_price={market_price:.{precision}f} 已到达PDArray范围。"
                                    f"PD_HIGH={etf_vaild_pdArray[self.PD_HIGH_COL]:.{precision}f} "
                                    f"PD_LOW={etf_vaild_pdArray[self.PD_LOW_COL]:.{precision}f}")    

            # 3.5 Place Order 下单
            step = "3.5"
            
            if not placing_order:
                order_price = self.toDecimal(etf_vaild_pdArray[self.PD_MID_COL])  
            else:
                order_price = self.toDecimal(market_price)
                self.logger.info(f"{symbol} : {step}. ETF {etf}, placing_order 用市场价格 {order_price:.{precision}f} 直接下单。")
            
            latest_order_price = self.toDecimal(self.place_order_prices.get(symbol,0))
            if order_price == latest_order_price:
                self.logger.info(f"{symbol} : {step}. ETF {etf}, 下单价格 {order_price:.{precision}} 未变化，不进行下单。")
                return
            
            self.cancel_all_orders(symbol=symbol) 
            self.place_order(symbol=symbol, price=order_price, side=etf_side, pair_config=pair_config)
            self.place_order_prices[symbol] = order_price # 记录下单价格,过滤重复下单
            self.logger.info(f"{symbol} : {step}. ETF {etf}, {etf_side} 价格={order_price:.{precision}f}")


        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            # 记录错误信息和堆栈跟踪
            self.logger.error(f"{error_message}\n{traceback.format_exc()}")
            traceback.print_exc()
            self.send_feishu_notification(symbol, error_message)
        except KeyboardInterrupt:
            self.logger.info("程序收到中断信号，开始退出...")
        finally:
            self.logger.info("=" * 60 + "\n")
            
  
            

        
