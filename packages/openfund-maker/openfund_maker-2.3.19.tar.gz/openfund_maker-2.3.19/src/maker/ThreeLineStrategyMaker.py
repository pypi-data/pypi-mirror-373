# -*- coding: utf-8 -*-
import time
import ccxt
import traceback
import requests
import pandas as pd
from decimal import Decimal

from concurrent.futures import ThreadPoolExecutor, as_completed



class ThreeLineStrategyMaker:
    def __init__(self, config, platform_config, common_config, feishu_webhook=None,logger=None):

        self.g_config = config
        self.feishu_webhook = feishu_webhook
        self.common_config = common_config
        self.strategy_config = self.g_config.get('strategy', {})
      
        self.trading_pairs_config = self.g_config.get('tradingPairs', {})
        
        self.leverage_value = self.strategy_config.get('leverage', 20)
        self.is_demo_trading = self.common_config.get('is_demo_trading', 1)  # live trading: 0, demo trading: 1
        
        self.highest_total_profit = 0  # 记录最高总盈利
        # self.instrument_info_dict = {}
        self.cross_directions = {} # 持仓期间，存储每个交易对的交叉方向 
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

        self.logger = logger
        self.position_mode = self.get_position_mode()  # 获取持仓模式

    def format_price(self, symbol, price:Decimal) -> str:
        precision = self.get_precision_length(symbol)
        return f"{price:.{precision}f}"

    @staticmethod
    def toDecimal(value):
        return Decimal(str(value))


    def getMarket(self,symbol):
        self.exchange.load_markets()
        return self.exchange.market(symbol)
    
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
    
    def convert_contract(self, symbol, amount, price:Decimal, direction='cost_to_contract'):
        """
        进行合约与币的转换
        :param symbol: 交易对符号，如 'BTC/USDT:USDT'
        :param amount: 输入的数量，可以是合约数量或币的数量
        :param direction: 转换方向，'amount_to_contract' 表示从数量转换为合约，'cost_to_contract' 表示从金额转换为合约
        :return: 转换后的数量
        """

        # 获取合约规模
        market_contractSize = self.toDecimal(self.getMarket(symbol)['contractSize'])
        amount = self.toDecimal(amount)
        if direction == 'amount_to_contract':
            contract_size = amount / market_contractSize
        elif direction == 'cost_to_contract':
            contract_size = amount / price / market_contractSize
        else:
            raise Exception(f"{symbol}:{direction} 是无效的转换方向，请输入 'amount_to_contract' 或 'cost_to_contract'。")
        
        return self.exchange.amount_to_precision(symbol, contract_size)
   
    
    # 获取价格精度
    def get_precision_length(self,symbol) -> int:
        tick_size = self.get_tick_size(symbol)
        return len(f"{tick_size:.15f}".rstrip('0').split('.')[1]) if '.' in f"{tick_size:.15f}" else 0

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
    
    def fetch_and_store_all_instruments(self,instType='SWAP'):
        try:
            self.logger.info(f"Fetching all instruments for type: {instType}")
            # 获取当前交易对
            instruments = self.exchange.fetch_markets_by_type(type=instType)
            if instruments:
                # self.instrument_info_dict.clear()
                for instrument in instruments:
                    # instId = instrument['info']['instId']
                    symbol = instrument['symbol']
                    # self.instrument_info_dict[symbol] = instrument['info']
        except Exception as e:
            self.logger.error(f"Error fetching instruments: {e}")
            raise

    def send_feishu_notification(self,message):
        if self.feishu_webhook:
            headers = {'Content-Type': 'application/json'}
            data = {"msg_type": "text", "content": {"text": message}}
            response = requests.post(self.feishu_webhook, headers=headers, json=data)
            if response.status_code == 200:
                self.logger.debug("飞书通知发送成功")
            else:
                self.logger.error(f"飞书通知发送失败: {response.text}")

    def get_mark_price(self,symbol):
        # response = market_api.get_ticker(instId)
        ticker = self.exchange.fetch_ticker(symbol)
        # if 'data' in response and len(response['data']) > 0:
        if ticker :
            # last_price = response['data'][0]['last']
            last_price = ticker['last']
            return float(last_price)
        else:
            raise ValueError("Unexpected response structure or missing 'last' key")

    def round_price_to_tick(self, symbol, price: Decimal) -> Decimal:
        tick_size = self.get_tick_size(symbol)
        # 计算 tick_size 的小数位数
        tick_decimals = self.get_precision_length(symbol) 
        # 调整价格为 tick_size 的整数倍
        adjusted_price = round(price / tick_size) * tick_size
        return self.toDecimal(f"{adjusted_price:.{tick_decimals}f}")

    def get_historical_klines(self,symbol, bar='1m', limit=241):
        # response = market_api.get_candlesticks(instId, bar=bar, limit=limit)
        params = {
            # 'instId': instId,
        }
        klines = self.exchange.fetch_ohlcv(symbol, timeframe=bar,limit=limit,params=params)
        # if 'data' in response and len(response['data']) > 0:
        if klines :
            # return response['data']
            return klines
        else:
            raise ValueError("Unexpected response structure or missing candlestick data")

    def calculate_atr(self,klines, period=60):
        trs = []
        for i in range(1, len(klines)):
            high = float(klines[i][2])
            low = float(klines[i][3])
            prev_close = float(klines[i-1][4])
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            trs.append(tr)
        atr = sum(trs[-period:]) / period
        return atr
    
    def calculate_sma_pandas(self,symbol, klines, period) -> pd.Series:
        """
        使用 pandas 计算 SMA
        :param KLines K线
        :param period: SMA 周期
        :return: SMA 值
        """
       
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        sma = df['close'].rolling(window=period).mean()
        return sma 
               
    def calculate_ema_pandas(self,symbol, klines, period) -> pd.Series:
        """
        使用 pandas 计算 EMA
        :param KLines K线
        :param period: EMA 周期
        :return: EMA 值
        """
      
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # 计算EMA
        ema = df['close'].ewm(span=period, adjust=False).mean()
        return ema 

    def calculate_average_amplitude(self,klines, period=60):
        amplitudes = []
        for i in range(len(klines) - period, len(klines)):
            high = float(klines[i][2])
            low = float(klines[i][3])
            close = float(klines[i][4])
            amplitude = ((high - low) / close) * 100
            amplitudes.append(amplitude)
        average_amplitude = sum(amplitudes) / len(amplitudes)
        return average_amplitude

    def calculate_range_diff(self,prices:pd.Series) -> float:
        """
        计算价格列表中最后一个价格与第一个价格的差值。
        Args:
            prices: 价格列表。
        Returns:
            diff: 计算最高价列的最大值与最小值的差值
。
        """
        if prices.empty:
            return None
        # 将价格列表转换为pandas Series格式
  
        diff = prices.max() - prices.min()
        
        return diff
    
    def calculate_place_order_price(self, symbol,side,base_price:Decimal, amplitude_limit: float, offset=1) -> Decimal:
        """
        计算开仓价格
        Args:
            symbol: 交易对
            side: 开仓方向
            base_price: 开盘价格
            amplitude_limit: 振幅限制
            offset: 偏移量
        Returns:
            place_order_price: 开仓价格
        """
        tick_size = self.get_tick_size(symbol)
        precision= self.get_precision_length(symbol)
        place_order_price = None
        # 计算止盈价格，用市场价格（取持仓期间历史最高）减去开仓价格的利润，再乘以不同阶段的止盈百分比。
      
        if side == 'buy':
            place_order_price = base_price * (1- self.toDecimal(amplitude_limit)/100) - offset * tick_size
        else:
            place_order_price = base_price * (1 + self.toDecimal(amplitude_limit)/100) + offset * tick_size
        self.logger.debug(f"++++ {symbol} 下单价格: {place_order_price:.{precision}f} 方向 {side} 基准价格{base_price:.{precision}} 振幅限制 {amplitude_limit} ")
        return self.round_price_to_tick(place_order_price,tick_size)
     
    # 定义根据均线斜率判断 K 线方向的函数： 0 空 1 多 -1 平
    def judge_k_line_direction(self, symbol, ema: pd.Series, klines, period=3) -> int:
        """
        判断K线方向
        Args:
            symbol: 交易对
            pair_config: 配置参数
            ema: EMA数据
        Returns:
            int: -1:平, 0:空, 1:多
        """

        
        # precision= self.get_precision_length(symbol)

        ema_diff = ema.diff().tail(period)
 
        direction = None
        if ema_diff.iloc[-1] < 0:
            # 下降趋势
            direction = 0 
        elif ema_diff.iloc[-1] > 0 :
            # 上升趋势
            direction = 1
        else:
            # 震荡趋势
            direction = -1 
        self.logger.debug(f"{symbol}: K线极差={ema_diff.map('{:.9f}'.format).values}  ,K线方向={direction}")
        return direction
    
    def judge_ema_direction(self, symbol, ema: pd.Series, period=3) -> int:
        """
        判断EMA方向
        Args:
            symbol: 交易对
            pair_config: 配置参数
            ema: EMA数据
        Returns:
            int: -1:平, 0:空, 1:多
        """
        
        precision= self.get_precision_length(symbol)

        ema_4_diff = ema.round(precision).diff().tail(period)
 
        direction = None
        if all(ema_4_diff <= 0) and any(ema_4_diff < 0) :
            # 下降趋势
            direction = 0 
        elif all(ema_4_diff >= 0) and any(ema_4_diff > 0) :
            # 上升趋势
            direction = 1
        # 都是 (0 0 0) 或 (+ 0 -) 这两种情况认为都是震荡
        else: 
            # 震荡趋势
            direction = -1 
        self.logger.debug(f"{symbol}: EMA极差={ema_4_diff.map('{:.4f}'.format).values}  ,EMA方向={direction}")
        return direction    
  
    def judge_cross_direction(self,fastklines,slowklines) :
        # 创建DataFrame,去掉最新的，最新的不稳定。
        df = pd.DataFrame({
            'fast': fastklines.iloc[:-1],
            'slow': slowklines.iloc[:-1]
        })
        
        # 判断金叉和死叉
        df['golden_cross'] = (df['fast'] > df['slow']) & (df['fast'].shift(1) < df['slow'].shift(1))
        df['death_cross'] = (df['fast'] < df['slow']) & (df['fast'].shift(1) > df['slow'].shift(1))
        
        # 从后往前找最近的交叉点
        last_golden = df['golden_cross'].iloc[::-1].idxmax() if df['golden_cross'].any() else None
        last_death = df['death_cross'].iloc[::-1].idxmax() if df['death_cross'].any() else None
        
        # 判断最近的交叉类型
        if last_golden is None and last_death is None:
            return {
                'cross': -1,  # 无交叉
                'index': None
            }
        
        # 如果金叉更近或只有金叉
        if last_golden is not None and (last_death is None or last_golden > last_death):
            return {
                'cross': 1,  # 金叉
                'index': last_golden
            }
        # 如果死叉更近或只有死叉
        else:
            return {
                'cross': 0,  # 死叉
                'index': last_death
            }
        
    def judge_ma_apex(self,symbol,cross_index, fastklines,slowklines,period=3) -> bool:

        precision= self.get_precision_length(symbol)
        
        # 获取交叉点的索引,从交叉点之后进行判断
        index = 0
        if cross_index is not None:
            index = cross_index
            
        df = pd.DataFrame({
            'ema': fastklines,
            'sma': slowklines
        })
        # 快线和慢线的差值
        # 将ema和sma转换为tick_size精度
        # df['diff'] = df['ema'].apply(lambda x: float(self.round_price_to_tick(x, tick_size))) - df['sma'].apply(lambda x: float(self.round_price_to_tick(x, tick_size)))
        df['diff'] = df['ema'].tail(period*2).round(precision)-df['sma'].tail(period*2).round(precision)
        df['ema_diff'] = df['ema'] - df['ema'].shift(1)
        df['sma_diff'] = df['sma'] - df['sma'].shift(1)
        # 计算斜率，【正】表示两线距离扩张，【负】表示两线距离收缩
        df['slope'] = df['diff'].abs().diff().round(4)
        
        self.logger.debug(f"{symbol}: ma apex slopes = \n" 
                f"{df[['ema','ema_diff','sma','sma_diff','diff','slope']].iloc[-1-period:-1]}  ")
        # 筛选出索引大于等于特定索引值的 slope 列元素
        filtered_slope = df['slope'][df.index >= index]

        # 两条线的距离是扩张状态还是收缩状态 true 是收缩 flase 是扩张
        is_expanding_or_contracting = all(filtered_slope.tail(period) <= 0 ) and \
            any(filtered_slope.tail(period) < 0)
            
        return is_expanding_or_contracting 
    
    def judge_range_diff(self,symbol,prices:pd.Series,limit = 1,period=3) -> bool:
        """
        计算价格列表中最后一个价格与第一个价格的差值。
        Args:
            prices: 价格列表。
        Returns:
            diff: 计算最高价列的最大值与最小值的差值
        """
        # limit = int(pair_config.get('ema_range_limit', 1))
        # period = int(pair_config.get('ema_range_period', 3))
        tick_size = self.get_tick_size(symbol)
        if prices.empty:
            return None     
  
        diff = prices.tail(period).max() - prices.tail(period).min()   
        self.logger.debug(f"{symbol}: 最高价列的最大值与最小值的差值 = {diff:.9f}")     
        return abs(diff) <= tick_size * limit       
      
    def set_leverage(self,symbol, leverage, mgnMode='isolated',posSide=None):
        try:
            # 设置杠杆
            params = {
                # 'instId': instId,
                'leverage': leverage,
                'marginMode': mgnMode
            }
            if posSide:
                params['side'] = posSide
                
            self.exchange.set_leverage(leverage, symbol=symbol, params=params)
            self.logger.debug(f"{symbol} Successfully set leverage to {leverage}x")
        except Exception as e:
            self.logger.error(f"{symbol} Error setting leverage: {e}")
    # 
    def check_position(self, symbol) -> bool:
        """
        检查指定交易对是否有持仓，失败时最多重试3次
        
        Args:
            symbol: 交易对ID
            
        Returns:
            bool: 是否有持仓
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                position = self.exchange.fetch_position(symbol=symbol)
                if position and position['contracts'] > 0:
                    self.logger.debug(f"{symbol} 有持仓合约数: {position['contracts']}")
                    return True
                return False
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    self.logger.warning(f"{symbol} 检查持仓失败(重试{retry_count}次): {str(e)}")
                    return True
                self.logger.warning(f"{symbol} 检查持仓失败，正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)  # 重试前等待0.1秒

    def place_order(self, symbol, price: Decimal, amount_usdt, side, order_type='limit'): 
        """
        下单
        Args:
            symbol: 交易对
            price: 下单价格
            amount_usdt: 下单金额
            side: 下单方向
            order_type: 订单类型
        """       
        # 格式化价格
        adjusted_price = self.format_price(symbol, price)

        if amount_usdt > 0:
            if side == 'buy':
                pos_side = 'long' 
            else:
                pos_side = 'short'   
            # 设置杠杆 
            self.set_leverage(symbol=symbol, leverage=self.leverage_value, mgnMode='isolated',posSide=pos_side)  
            # 20250220 SWAP类型计算合约数量 
            contract_size = self.convert_contract(symbol=symbol, price = self.toDecimal(adjusted_price) ,amount=amount_usdt)
    
            params = {
                
                "tdMode": 'isolated',
                "side": side,
                "ordType": order_type,
                "sz": contract_size,
                "px": adjusted_price
            } 
            
            # 模拟盘(demo_trading)需要 posSide
            if self.is_demo_trading == 1 :
                params["posSide"] = pos_side
                
            # self.logger.debug(f"---- Order placed params: {params}")
            try:
                order = {
                    'symbol': symbol,
                    'side': side,
                    'type': 'limit',
                    'amount': contract_size,
                    'price': adjusted_price,
                    'params': params
                }
                # 使用ccxt创建订单
                self.logger.debug(f"Pre Order placed:  {order} ")
                order_result = self.exchange.create_order(
                    **order
                    # symbol=symbol,
                    # type='limit',
                    # side=side,
                    # amount=amount_usdt,
                    # price=float(adjusted_price),
                    # params=params
                )
                # self.logger.debug(f"{symbol} ++ Order placed rs :  {order_result}")
            except Exception as e:
                error_message = f"{symbol} Failed to place order: {e}"
                self.logger.error(error_message)
                self.send_feishu_notification(error_message)
        self.logger.info(f"--------- ++ {symbol} Order placed done! --------")         
  
    def cancel_all_orders(self, symbol):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 获取所有未完成订单
                params = {
                    # 'instId': instId
                }
                open_orders = self.exchange.fetch_open_orders(symbol=symbol, params=params)
                
                # 批量取消所有订单
                if open_orders:
                    order_ids = [order['id'] for order in open_orders]
                    self.exchange.cancel_orders(order_ids, symbol, params=params)
                    
                    self.logger.info(f"{symbol}: {order_ids} 挂单取消成功.")
                else:
                    self.logger.info(f"{symbol}: 无挂单.")
                return True
                
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"{symbol} 取消挂单失败(重试{retry_count}次): {str(e)}"
                    self.logger.error(error_message)
                    self.send_feishu_notification(error_message)
                    return False
                self.logger.warning(f"{symbol} 取消挂单失败，正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)  # 重试前等待0.1秒

    def process_pair(self,symbol,pair_config):
        self.logger.info("=" * 60)
        # 检查是否有持仓，有持仓不进行下单
        if self.check_position(symbol=symbol) :
            self.logger.info(f"{symbol} 有持仓合约，不进行下单。")
            self.logger.info("-" * 60)  
            return 
        # 取消之前的挂单
        self.cancel_all_orders(symbol=symbol)  
        three_line_strategy = pair_config.get('three_line_strategy',{})
        klines_period = str(pair_config.get('klines_period', '1m'))   
        try:
            klines = self.get_historical_klines(symbol=symbol,bar=klines_period)
            # 提取收盘价数据用于计算 EMA
            # 从K线数据中提取收盘价，按时间顺序排列（新数据在后）
            # close_prices = [float(kline[4]) for kline in klines]
            is_bullish_trend = False
            is_bearish_trend = False

            # 计算 快线EMA & 慢线SMA
            ema_length = pair_config.get('ema', 15)
            sma_length = pair_config.get('sma', 50)
            
            # 增加 金叉死叉 方向确认的 20250209
            fastk = self.calculate_ema_pandas(symbol=symbol, klines=klines, period=ema_length)
            slowk = self.calculate_sma_pandas(symbol=symbol, klines=klines, period=sma_length)

            cross_direction = self.judge_cross_direction(fastklines=fastk,slowklines=slowk)
            # 更新交叉状态
            if cross_direction['cross'] != -1 :  #本次不一定有交叉
                self.cross_directions[symbol] = cross_direction
            
            # 最新交叉方向
            last_cross_direction = self.exchange.safe_dict(self.cross_directions,symbol,None)
            cross_index = self.exchange.safe_dict(last_cross_direction,'index',None)
                
            # 判断趋势：多头趋势或空头趋势
            ema_range_period = int(three_line_strategy.get('ema_range_period', 3))
            direction = self.judge_k_line_direction(symbol=symbol,ema=fastk,klines=klines,period=ema_range_period) 
            if direction == 1:
                is_bullish_trend = True     
            elif direction == 0:
                is_bearish_trend = True
     
            # 结合金叉死叉判断是否是周期顶部和底部
            ema_direction = self.judge_ema_direction(symbol=symbol,ema=fastk,period=ema_range_period)
            is_apex = self.judge_ma_apex(symbol=symbol,cross_index=cross_index, fastklines=fastk,slowklines=slowk,period=ema_range_period)
            
            # ema_range_limit = int(pair_config.get('ema_range_limit', 1))
            # if_inner_range = self.judge_range_diff(symbol=symbol, prices=fastk,limit=ema_range_limit, period=ema_range_period)
            
            # 金叉死叉逻辑
            if last_cross_direction and last_cross_direction['cross'] == 1 : # 金叉
                # 强校验下单条件
                # if is_apex or ema_direction == -1 or if_inner_range:
                #     self.logger.debug(f"{symbol} 强校验 - 金叉:{last_cross_direction}，两线收缩={is_apex} ,ema_平={ema_direction}，均线振幅={if_inner_range} ,不开单！！")
                # 弱校验下单条件
                if is_apex or ema_direction == -1: 
                    self.logger.debug(f"{symbol} :金叉={last_cross_direction['cross']}，两线收缩={is_apex} ,快线方向(平:-1)={ema_direction}，不挂单！！")
                    is_bullish_trend = False
                    is_bearish_trend = False
                else :
                    self.logger.debug(f"{symbol} :金叉={last_cross_direction['cross']}，两线收缩={is_apex} ,快线方向(平:-1)={ema_direction}, 清理空单，挂多单！！")
                    is_bearish_trend = False 
                    
            elif last_cross_direction and last_cross_direction['cross'] == 0 : # 死叉

                # 强校验下单条件
                # if is_apex or ema_direction == -1 or if_inner_range :
                #     self.logger.debug(f"{symbol} 强校验 - 死叉:{last_cross_direction}，两线收缩={is_apex} ,ema_平={ema_direction}，均线振幅={if_inner_range} ,不开单！！")
                # 弱校验下单条件
                if is_apex or ema_direction == -1:
                    self.logger.debug(f"{symbol} :死叉={last_cross_direction['cross']}，两线收缩={is_apex} ,快线方向(平:-1)={ema_direction}，不挂单！！")
                    is_bearish_trend = False
                    is_bullish_trend = False 
                else :
                    self.logger.debug(f"{symbol} :死叉={last_cross_direction['cross']}，两线收缩={is_apex} ,快线方向(平:-1)={ema_direction}，清理多单，挂空单！！")
                    is_bullish_trend = False      
                    
            else:
                self.logger.warning(f"{symbol} :当前没有金叉死叉,以K线趋势为准。")
                   
            
            if  (not is_bullish_trend and not is_bearish_trend) :
                self.logger.info(f"{symbol} :当前是震荡趋势(平),不挂单!! 死叉={last_cross_direction['cross']}，两线收缩={is_apex} ,快线方向(平:-1)={ema_direction}")
                return  

            '''
            取当前K线的前三根K线中最高/低的值作为止盈位。
            20250210 增加开单价格约束,下单时,三线如果价格振幅小(如0.32%内),那去找到0.32%外的那根。 振幅 amplitude_limit
            '''    
            
            # 取当前 K 线的前三根 K 线
      
            df_3 = pd.DataFrame(klines[-4:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            low_prices = df_3['low']
            high_prices = df_3['high']
            max_high = self.toDecimal(high_prices.max())
            min_low = self.toDecimal(low_prices.min())
      
            # 计算当前 振幅是否超过amplitude_limit
            long_amount_usdt = pair_config.get('long_amount_usdt', 5)
            short_amount_usdt = pair_config.get('short_amount_usdt', 5)     
            

            amplitude_limit = three_line_strategy.get('amplitude_limit', 0.32)
            
            self.logger.debug(f"{symbol} 当前K线的前三根K线 最高价: {max_high}, 最低价: {min_low}")    
            
                            
            '''
            挂单线都是三线中最高/低，如果打到下单线说明趋势反转，所以应该挂和反方向的单，
            
            '''
            # 取最新K线的收盘价格
            close_price = klines[-1][4]
            self.logger.debug(f"-- {symbol} 最新K线 {klines[-1]}")
            
            # FIXME calculate_range_diff 去掉
            if is_bullish_trend:
                diff = self.calculate_range_diff(prices=low_prices)
                cur_amplitude_limit =  diff / close_price * 100 
                self.logger.info(f"{symbol} 当前为上升（多）趋势，允许挂多单，振幅{cur_amplitude_limit:.3f} hight/low {low_prices.max()}/{low_prices.min()} ++")
                # 振幅大于限制，直接下单,否则，根据振幅计算下单价格
                if  cur_amplitude_limit >= amplitude_limit:
                    self.place_order(symbol, min_low, long_amount_usdt, 'buy')
                else:
                    entry_price = self.calculate_place_order_price(symbol,side='buy',base_price=min_low, amplitude_limit=amplitude_limit,offset=0)
                    self.place_order(symbol, entry_price ,long_amount_usdt, 'buy')
                   

            if is_bearish_trend:
                diff = self.calculate_range_diff(prices=high_prices)
                cur_amplitude_limit =  diff / close_price * 100 
                self.logger.info(f"{symbol} 当前为下降（空）趋势，允许挂空单，振幅{cur_amplitude_limit:.3f} hight/low {high_prices.max()}/{high_prices.min()}--")
                if cur_amplitude_limit >= amplitude_limit:
                    self.place_order(symbol, max_high, short_amount_usdt, 'sell')
                else:
                    entry_price = self.calculate_place_order_price(symbol,side='sell',base_price=max_high, amplitude_limit=amplitude_limit,offset=0)
                    self.place_order(symbol, entry_price ,long_amount_usdt, 'sell')  

        except KeyboardInterrupt:
            self.logger.info("程序收到中断信号，开始退出...")
        except Exception as e:
            error_message = f"程序异常退出: {str(e)}"
            self.logger.error(error_message,exc_info=True)
            traceback.print_exc()
            self.send_feishu_notification(error_message)
            
        self.logger.info("-" * 60)  
        
    def get_pair_config(self,symbol):
        # 获取交易对特定配置,如果没有则使用全局策略配置
        pair_config = self.trading_pairs_config.get(symbol, {})
        
        # 使用字典推导式合并配置,trading_pairs_config优先级高于strategy_config
        pair_config = {
            **self.strategy_config,  # 基础配置
            **pair_config  # 交易对特定配置会覆盖基础配置
        }
        return pair_config
    
    
    def monitor_klines(self):
        symbols = list(self.trading_pairs_config.keys())  # 获取所有币对的ID
        batch_size = 5  # 每批处理的数量
        # while True:

        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = [executor.submit(self.process_pair, symbol,self.get_pair_config(symbol)) for symbol in batch]
                for future in as_completed(futures):
                    future.result()  # Raise any exceptions caught during execution
