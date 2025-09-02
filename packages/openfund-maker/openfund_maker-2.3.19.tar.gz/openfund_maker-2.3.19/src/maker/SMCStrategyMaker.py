# -*- coding: utf-8 -*-
import traceback
import pandas as pd
from decimal import Decimal


from maker.ThreeLineStrategyMaker import ThreeLineStrategyMaker

class SMCStrategyMaker(ThreeLineStrategyMaker):
    def __init__(self, config, platform_config, common_config, feishu_webhook=None,logger=None):
        super().__init__(config, platform_config, common_config, feishu_webhook, logger)

        self.place_order_prices = {} # 记录每个symbol的挂单价格
        
    def place_order(self,symbol, price:Decimal, side,pair_config):
        """_summary_
            下单
        Args:
            symbol (_type_): _description_
            price (_type_): _description_
            amount_usdt (_type_): _description_
            side (_type_): _description_
            order_type (_type_): _description_
        """
        long_amount_usdt = pair_config.get('long_amount_usdt', 5)
        short_amount_usdt = pair_config.get('short_amount_usdt', 5) 
        order_amount_usdt = 5
        # order_type='optimal_limit_ioc'

        if side == 'sell' :
            self.logger.debug(f"{symbol} : 触发做空下单条件。")
            order_amount_usdt = short_amount_usdt
        elif side == 'buy' :
            self.logger.debug(f"{symbol} : 触发做多下单条件。")
            order_amount_usdt = long_amount_usdt
        super().place_order(symbol=symbol, price=price, amount_usdt=order_amount_usdt, side=side)
        
    def format_klines(self,klines) -> pd.DataFrame:
       
        """_summary_
            格式化K线数据
        Args:
            klines (_type_): _description_
        """
        klines_df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']) 
        # 转换时间戳为日期时间
        klines_df['timestamp'] = pd.to_datetime(klines_df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
        # klines_df['timestamp'] = pd.to_datetime(klines_df['timestamp'], unit='ms')
        # klines_df['timestamp'] = klines_df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
        
        return klines_df
    
    def find_OB_boxes(self, data, side, threshold, pivot_index, symbol=None, pair_config=None) -> list:
        """_summary_
            识别OB
        Args:
            data (_type_): _description_
            symbol (_type_): _description_
      
        """
        df = data.copy().iloc[pivot_index:]
        # 首先计算实体的高点和低点，即开盘价和收盘价中的较大值和较小值
        df['body_high'] = df[['open', 'close']].max(axis=1)
        df['body_low'] = df[['open', 'close']].min(axis=1)
        
        # 初始化OB的高点和低点列为空
        df['OB_high'] = None
        df['OB_low'] = None
        
        # 使用布尔索引一次性更新OB_high
        # df.loc[df['iUp'] == df.index, 'OB_high'] = df.loc[df['iUp'] == df.index, 'high']
        # df.loc[df['iUp'] == df.index, 'OB_low'] = df['body_low'].shift(1).fillna(df['body_low'])              
        
        # df.loc[df['iDn'] == df.index, 'OB_low'] = df.loc[df['iDn'] == df.index, 'low']
        # df.loc[df['iDn'] == df.index, 'OB_high'] = df['body_high'].shift(1).fillna(df['body_high'])
        
        # print(df[['timestamp', 'pattern','high','low','Dn','iDn','Up','iUp','body_high','body_low']])
        
        OB_boxes = []
        # 根据交易方向构建OB盒子，OB区规则孤立高点+实体低点 孤立低点+实体高点
        if side == 'buy':
            # 买入方向的OB盒子构建
            OB_boxes = [
                {
                    'index': idx,
                    'top': self.toDecimal(df.loc[idx, 'low']),  # OB低点为当前K线的最低点
                    'bot': self.toDecimal(df.loc[idx - 1 if idx > df.index[0] else idx, 'body_high']) # OB高点为前一根K线的实体高点
                }
                for idx in df.index 
                # 判断条件：是第一根K线（极值点）或当前下降趋势大于前一个，且前一根K线实体高点小于阈值
                if (idx == df.index[0] or (df.loc[idx, 'Dn'] > df.loc[idx - 1, 'Dn'])) 
                and df.loc[idx - 1 if idx > df.index[0] else idx, 'body_high'] <= threshold
            ]
        else:
            # 卖出方向的OB盒子构建
            OB_boxes = [
                {
                    'index': idx,
                    'top': self.toDecimal(df.loc[idx, 'high']),  # OB高点为当前K线的最高点
                    'bot': self.toDecimal(df.loc[idx - 1 if idx > df.index[0] else idx, 'body_low'])  # OB低点为前一根K线的实体低点
                }
                for idx in df.index
                # 判断条件：是第一根K线（极值点）或当前上升趋势小于前一个，且前一根K线实体低点大于阈值
                if (idx == df.index[0] or (df.loc[idx, 'Up'] < df.loc[idx - 1, 'Up']))
                and df.loc[idx - 1 if idx > df.index[0] else idx, 'body_low'] >= threshold
            ]

        return OB_boxes
        
        
    def find_fvg_boxes(self, data, side, threshold:Decimal, check_balanced=True, pivot_index=0, symbol=None, pair_config=None) -> list:
        """_summary_
            寻找公允价值缺口
        Args:
            data (_type_): K线数据
            side (_type_): 交易方向 'buy'|'sell'
            threshold (_type_): 阈值价格，通常为溢价和折价区的CE
            check_balanced (bool): 是否检查FVG是否被平衡过,默认为True
            pivot_index (int): 枢轴点索引,默认为0
            symbol (_type_): 交易对名称
            pair_config (_type_): 交易对配置
        Returns:
            list: FVG盒子列表,每个盒子包含以下字段:
                # index: FVG出现的K线位置索引
                # top: FVG的上边界价格,对应K线的最高价或最低价
                # bot: FVG的下边界价格,对应K线的最高价或最低价
        """
        # bug2.2.5_1，未到折价区，计算FVG需要前一根K线
        # df = data.copy().iloc[pivot_index:]
        df = data.copy().iloc[max(0,pivot_index-1):] 
   
        fvg_boxes = []
        if side == 'buy' :
            
            # 处理看涨公允价值缺口
            df.loc[:, 'is_bullish_fvg'] = df['high'].shift(3) < df['low'].shift(1)
            bullish_df = df[df['is_bullish_fvg']].copy()
            valid_indices = bullish_df.index[
                (bullish_df.index - 1).isin(df.index) & 
                (bullish_df.index - 2).isin(df.index) & 
                (bullish_df.index - 3).isin(df.index)
            ]                  
  
            fvg_boxes = [
                {
                    'index': idx - 2, # FVG的索引
                    'top': min(self.toDecimal(df.loc[idx - 1, 'low']),threshold),  # FVG高点为右1K线的最低点
                    'bot': self.toDecimal(df.loc[idx - 3, 'high'])  # FVG低点为左1K线的最高点
                }
                # [df.loc[idx - 1, 'low'], df.loc[idx - 3, 'high'], idx - 2]
                for idx in valid_indices 
                if df.loc[idx - 3, 'high'] <= threshold and
                (not check_balanced or all((df.loc[idx:, 'low'] > df.loc[idx - 3, 'high'])))   # check_balanced = true 检查FVG是否被平衡过
            ]


        else :
            # 处理看跌公允价值缺口
            df.loc[:, 'is_bearish_fvg'] = df['low'].shift(3) > df['high'].shift(1)
            
            bearish_df = df[df['is_bearish_fvg']].copy()
            valid_indices = bearish_df.index[
                (bearish_df.index - 1).isin(df.index) & 
                (bearish_df.index - 2).isin(df.index) & 
                (bearish_df.index - 3).isin(df.index)
            ]
            
 
            fvg_boxes = [
                {
                    'index': idx - 2, # FVG的索引
                    'top': self.toDecimal(df.loc[idx - 3, 'low']),  # FVG高点为右1K线的最高点
                    'bot': max(self.toDecimal(df.loc[idx - 1, 'high']),threshold)  # FVG低点为左1K线的最低点
                }
                
                for idx in valid_indices 
                if df.loc[idx - 3, 'low'] >= threshold and
                (not check_balanced or all((df.loc[idx:, 'high'] < df.loc[idx - 3, 'low'])))  # check_balanced = true 检查FVG是否被平衡过
            ]
      

        return fvg_boxes

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
      
            # data.at[index, 'Up'] = max(data.at[index - 1, 'Up'], data.at[index, 'high'])
            # data.at[index, 'Dn'] = min(data.at[index - 1, 'Dn'], data.at[index, 'low'])
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
            识别SMC结构，参考 Tradingview Smart Money Concepts Probability (Expo)@Openfund
 
        Args:
            data (df): df格式的K线数据
            prd (int): 计算Swing Points的bar数量
            struct_key (str): 结构类型，如 'CHoCH'|'SMS'|'BMS'
            check_valid_range (bool): 结构类型在 pivot_high_index 和 pivot_low_index 之间为有效范围内，默认为False
            check_bounds (bool): 计算Swing Points是否检查边界，默认为True
            global_extremum (bool): 是否使用全局极值点，默认为False
            s1 (bool): 结构响应布尔值
            resp (int): 响应周期
        Returns:
            dict: 包含结构识别结果的字典,包含以下字段:
                "struct": 结构类型,如 'Bullish_CHoCH'|'Bullish_SMS'|'Bullish_BMS'|'Bearish_CHoCH'|'Bearish_SMS'|'Bearish_BMS'
                "index": 结构出现的位置索引
                "pivot_high": 枢轴高点价格
                "pivot_high_index": 枢轴高点索引
                "pivot_low": 枢轴低点价格
                "pivot_low_index": 枢轴低点索引
                "side": 交易方向,'buy'或'sell'
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
        
        last_struct["pivot_high"] = self.toDecimal(data.loc[last_struct["pivot_high_index"], 'high'])
        last_struct["pivot_low"] = self.toDecimal(data.loc[last_struct["pivot_low_index"], 'low'])
        
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
    
    # def round_price(self,symbol, price: Decimal) -> Decimal:
    #     return super().round_price_to_tick(symbol, price)
    
    def calculate_ce(self, symbol, pivot_high:Decimal , pivot_low:Decimal) -> Decimal:
        ce = (pivot_high + pivot_low) / 2
        return self.round_price_to_tick(symbol, ce)
    
    def reset_all_cache(self, symbol):
        """_summary_
            重置所有缓存数据
        """
        if symbol in self.place_order_prices:            
            self.place_order_prices.pop(symbol)
    
    def process_pair(self,symbol,pair_config):
        self.logger.info("-" * 60)
        """_summary_
            1. HTF 判断struct趋势（SMS和BMS）
            2. HTF 获取最新的两个极值点，设置折价区和溢价区
            3. CTF 在折价区获取FVG和OB的位置
            4. CTF 下单
            5. 
        """
        try:
            # 检查是否有持仓，有持仓不进行下单
            if self.check_position(symbol=symbol) :
                self.logger.info(f"{symbol} : 有持仓合约，不进行下单。")  
                if symbol in self.place_order_prices:  
                    self.reset_all_cache(symbol)
                    
                return           
           
            
            smc_strategy = pair_config.get('smc_strategy',{})

            # 获取历史K线，HTF和CTF
            htf = str(smc_strategy.get('HTF','15m'))            
            htf_Klines = self.get_historical_klines(symbol=symbol, bar=htf)
            htf_df = self.format_klines(htf_Klines)
                       
            ctf = str(pair_config.get('CHF', '5m')) 
            ctf_kLines = self.get_historical_klines(symbol=symbol, bar=ctf)
            ctf_df = self.format_klines(ctf_kLines)
            
            enable_FVG = smc_strategy.get('enable_FVG',True) # 是否启用FVG
            enable_OB = smc_strategy.get('enable_OB',True) # 是否启用OB
            self.logger.debug(f"{symbol} : SMC策略 {ctf}|{htf} enable_FVG={enable_FVG} enable_OB={enable_OB} ...")
   
            side = 'none'
            # 1. HTF 判断struct趋势（CHoCH\SMS\BMS） ,HTF struct 看趋势，CTF 看FVG和OB的位置    
            swing_points_length = smc_strategy.get('swing_points_length',10)    
            htf_last_struct = self.detect_struct(htf_df,prd=swing_points_length)
            htf_last_struct_label = htf_last_struct["struct"]
            precision = self.get_precision_length(symbol)
         
            if htf_last_struct_label is None:
                self.logger.debug(f"{symbol} : {htf} 未形成 struct,不下单。{htf_last_struct}。")
                return
            
            # ctf_last_struct = self.detect_struct(ctf_df)
            # ctf_last_struct_label = ctf_last_struct["struct"]
            
            # if ctf_last_struct_label is None:
            #     self.logger.debug(f"{symbol} :{ctf} 未形成 struct,不下单。{ctf_last_struct}。")
            #     return

            side = htf_last_struct["side"]
            # self.logger.debug(f"{symbol} : {htf} 趋势={htf_last_struct_label}-{side}: \n{htf_last_struct}")

            
            # 2. HTF 获取最新的两个极值点，设置折价(discount)区和溢价(premium)区
            pivot_high = self.toDecimal(htf_last_struct["pivot_high"])
            pivot_low = self.toDecimal(htf_last_struct["pivot_low"])            
            mid_line = self.calculate_ce(symbol,pivot_high,pivot_low)
       
            # 计算溢价和折价区
            premium_box = {
                'top': pivot_high,
                'bot': mid_line,
                'ce': self.calculate_ce(symbol,pivot_high,mid_line)
            }
            discount_box = {
                'top': mid_line,
                'bot': pivot_low,
                'ce': self.calculate_ce(symbol,mid_line,pivot_low)
            }
            
            self.logger.debug(f"{symbol} : {htf} 趋势={htf_last_struct_label}: \n" \
                f"pivot_high={pivot_high:.{precision}} pivot_low={pivot_low:.{precision}} mid_line={mid_line:.{precision}}\n" \
                f"溢价区={premium_box}\n" 
                f"折价区={discount_box}")
                
            # 3. 根据HTF结构来分析下单位置和止盈位置 
            threshold = self.toDecimal(0.0)   
            order_side = side
            # 获取当前市场价格
            market_price = self.toDecimal(ctf_df['close'].iloc[-1])

            if 'CHoCH' in htf_last_struct_label:
                """
                ChoCh 结构。
                Bearish趋势 如果价格，
                1.在溢价区上半区，可以考虑顺当前趋势，做空。
                2.在折价区下半区，则考虑回收流动性，做多。
                3.溢价区下半区和折价区上半区，不做单。
                
                Bullish趋势 如果价格，
                1.在折价区下半区，可以考虑顺当前趋势，做多。
                2.在溢价区上半区，则考虑回收流动性的，做空。
                3.溢价区下半区和折价区上半区，不做单。
                
                """
                # 溢价区上半区做空
                if market_price >= premium_box['ce'] and side == 'sell':
                    threshold = premium_box['ce']
                # 折价区下半区做多    
                elif market_price <= discount_box['ce'] and side == 'buy':
                    threshold = discount_box['ce']
                # 折价区下半区回收流动性做空  # TODO 要考虑是否有孤立点
                # elif market_price <= discount_box['ce'] and side == 'sell':
                #     threshold = discount_box['ce'] 
                #     order_side = 'buy'
                # # 溢价区上半区回收流动性做多
                # elif market_price >= premium_box['ce'] and side == 'buy':
                #     threshold = premium_box['ce']
                #     order_side = 'sell'
   
            
            elif 'SMS' in htf_last_struct_label or 'BMS' in htf_last_struct_label:
                """
                SMS/BMS 结构。
                Bullish趋势 如果价格，
                1.在折价区可以下单，不区分上下半区
                
                Bearish趋势 如果价格，
                1.在溢价区可以下单，不区分上下半区
                
                """
                # Bearish趋势 如果价格在溢价区可以下单
                # if market_price >= mid_line and side == 'sell':
                #     threshold = mid_line
                # # Bullish趋势 如果价格在折价区可以下单    
                # elif market_price <= mid_line and side == 'buy':
                #     threshold = mid_line
                threshold = mid_line
   
    
    
            if threshold == 0.0:
                self.logger.debug(f"{symbol} : 价格{market_price:.{precision}}不在目标区域，不下单。")
                # 取消所有未成交订单
                self.cancel_all_orders(symbol=symbol) 
                return
        
                
            # 4. 在CTF折价区获取FVG的位置       
            order_price = self.toDecimal(0.0)                
           
            if enable_FVG and order_price == 0.0:               
                
                all_tf = ['1m', '3m', '5m', '15m', '30m', '1H', '2H', '4H']
                # 获取当前时间周期之前的所有时间周期
                ctf_index = all_tf.index(ctf)
                ltf_tfs = all_tf[:ctf_index + 1]
                
                # 遍历所有LTF时间周期，获取FVG 
                for tf in ltf_tfs[::-1]:
                    tf_Klines = self.get_historical_klines(symbol=symbol, bar=tf)
                    tf_df = self.format_klines(tf_Klines)
                          
                    fvg_boxes = self.find_fvg_boxes(tf_df,side=order_side,threshold=threshold)
                    if len(fvg_boxes) > 0:
                        self.logger.debug(f"{symbol} : 方向={order_side}, {tf} FVG={fvg_boxes}")
                        break
                    else:
                        self.logger.debug(f"{symbol} : 方向={order_side}, {tf} 未找到 FVG")
                
                
              
                if len(fvg_boxes) != 0 and order_price == 0.0:
                    last_fvg_box = fvg_boxes[-1]
                    ce_price = self.calculate_ce(symbol,last_fvg_box['top'],last_fvg_box['bot'])
                    self.logger.info(f"{symbol} : 方向={order_side}, FVG_ce={ce_price:.{precision}} FVG={last_fvg_box} ")
                    order_price = ce_price 
            
            # 4. 找OB位置，OB规则孤立高点+实体低点 孤立低点+实体高点
    
            if enable_OB and order_price == 0.0: # OB 优先级低于 FVG, order_price有价格时，不再计算OB
                
                ctf_last_struct = self.detect_struct(ctf_df,prd=swing_points_length)
                # 找到最近的一个极值点的位置
                if order_side == 'buy':
                    pivot_index = ctf_last_struct["pivot_low_index"]
                else:
                    pivot_index = ctf_last_struct["pivot_high_index"]
                # TODO 不同级别的pivot_index 需要优化计算
                OB_boxes = self.find_OB_boxes(ctf_df,side=side,threshold=threshold,pivot_index=pivot_index)
                
                if len(OB_boxes) != 0 :                
                    last_OB_box = OB_boxes[-1]
                    ce_price = self.calculate_ce(symbol,last_OB_box['top'],last_OB_box['bot'])
                    self.logger.info(f"{symbol} : 方向={order_side}, OB_ce={ce_price:.{precision}} , OB={last_OB_box} ")
                    order_price = ce_price 
                
            if order_price == 0.0:
                self.logger.warning(f"！！！{symbol} : 未找到 FVG和OB")
                self.cancel_all_orders(symbol=symbol) 
                return  

            latest_order_price = self.place_order_prices.get(symbol,0.0)
            if order_price == latest_order_price:
                self.logger.debug(f"{symbol} : 下单价格 {order_price:.{precision}} 未变化，不进行下单。")
                return
        
              
            # 下单    
            self.cancel_all_orders(symbol=symbol) 
            self.place_order(symbol=symbol, price=order_price, side=order_side, pair_config=pair_config)
            self.place_order_prices[symbol] = order_price # 记录下单价格,过滤重复下单
            self.logger.debug(f"{symbol} : {side}, 下单价格 {order_price:.{precision}}")
            
            
        except KeyboardInterrupt:
            self.logger.info("程序收到中断信号，开始退出...")
        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            self.logger.error(error_message,exc_info=True)
            traceback.print_exc()
            self.send_feishu_notification(error_message)
        finally:
            self.logger.info("=" * 60)

        
