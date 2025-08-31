# -*- coding: utf-8 -*-
import time
import ccxt

import requests
import pandas as pd


from concurrent.futures import ThreadPoolExecutor, as_completed


class WickReversalStrategyMaker:
    def __init__(self, config, platform_config, feishu_webhook=None , logger=None):

        self.g_config = config
        self.feishu_webhook = feishu_webhook
        self.monitor_interval = self.g_config.get("monitor_interval", 4)  # 默认值为60秒  # 监控循环时间是分仓监控的3倍
        self.trading_pairs_config = self.g_config.get('tradingPairs', {})
        self.highest_total_profit = 0  # 记录最高总盈利
        self.leverage_value = self.g_config.get('leverage', 2)
        self.is_demo_trading = self.g_config.get('is_demo_trading', 1)  # live trading: 0, demo trading: 1
        # self.instrument_info_dict = {}

        # 配置交易所
        self.exchange = ccxt.okx({
            'apiKey': platform_config["apiKey"],
            'secret': platform_config["secret"],
            'password': platform_config["password"],
            'timeout': 3000,
            'rateLimit': 50,
            'options': {'defaultType': 'future'},
            'proxies': {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'},
        })
        
        self.position_mode = self.get_position_mode()  # 获取持仓模式
        import importlib.metadata
        self.logger = logger
        version = importlib.metadata.version("openfund-wick-reversal")
        self.logger.info(f" ++ openfund-wick-reversal:{version} is doing...")

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
    # 获取K线收盘价格            
    def get_close_price(self,symbol):
        '''
        bar = 
        时间粒度，默认值1m
        如 [1m/3m/5m/15m/30m/1H/2H/4H]
        香港时间开盘价k线：[6H/12H/1D/2D/3D/1W/1M/3M]
        UTC时间开盘价k线：[/6Hutc/12Hutc/1Dutc/2Dutc/3Dutc/1Wutc/1Mutc/3Mutc]
        '''
        # response = market_api.get_candlesticks(instId=instId,bar='1m')
        klines = self.exchange.fetch_ohlcv(symbol, timeframe='1m',limit=3)
        if klines:
            # close_price = response['data'][0][4]
            # 获取前一个K线 close price
            close_price = klines[-1][4]
            return float(close_price)
        else:
            raise ValueError("Unexpected response structure or missing 'c' value")


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

    def round_price_to_tick(self,price, tick_size):
        # 计算 tick_size 的小数位数
        tick_decimals = len(f"{tick_size:.10f}".rstrip('0').split('.')[1]) if '.' in f"{tick_size:.10f}" else 0

        # 调整价格为 tick_size 的整数倍
        adjusted_price = round(price / tick_size) * tick_size
        return f"{adjusted_price:.{tick_decimals}f}"

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
    
    def alculate_sma_pandas(self,data,period):
        """
        使用 pandas 计算 SMA
        :param 收盘价列表
        :param period: SMA 周期
        :return: SMA 值
        """
        import pandas as pd
        df = pd.Series(data)
        sma = df.rolling(window=period).mean()
        return sma.iloc[-1]  # 返回最后一个 SMA 值
        
        
    def calculate_ema_pandas(self,data, period):
        """
        使用 pandas 计算 EMA
        :param 收盘价列表
        :param period: EMA 周期
        :return: EMA 值
        """
       
        df = pd.Series(data)
        ema = df.ewm(span=period, adjust=False).mean()
        return ema.iloc[-1]  # 返回最后一个 EMA 值


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
    
    def cancel_all_orders(self,symbol):
        try:
            # 获取所有未完成订单
            params = {
                # 'instId': instId
            }
            open_orders = self.exchange.fetch_open_orders(symbol=symbol,params=params)
            
            # 取消每个订单
            for order in open_orders:
                self.exchange.cancel_order(order['id'], symbol,params=params)
                
            self.logger.info(f"{symbol}挂单取消成功.")
        except Exception as e:
            self.logger.error(f"取消订单失败: {str(e)}")

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
            self.logger.debug(f"Successfully set leverage to {leverage}x for {symbol}")
        except Exception as e:
            self.logger.error(f"Error setting leverage: {e}")
    # 
    def check_position(self,symbol) -> bool:
        """
        检查指定交易对是否有持仓
        
        Args:
            symbol: 交易对ID
            
        Returns:
            bool: 是否有持仓
        """
        try:
            position = self.exchange.fetch_position(symbol=symbol)
            if position and position['contracts']> 0:
                self.logger.debug(f"{symbol} 有持仓合约数: {position}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"检查持仓失败 {symbol}: {str(e)}")
            return False


    def place_order(self,symbol, price, amount_usdt, side):
        if self.check_position(symbol=symbol) :
            self.logger.info(f"{symbol} 有持仓合约，不进行下单。")
            return 
        
        markets = self.exchange.load_markets()
        if symbol not in markets:
            self.logger.error(f"Instrument {symbol} not found in markets")
            return
        market = markets[symbol]
        # 获取价格精度
        price_precision = market['precision']['price']
        adjusted_price = self.round_price_to_tick(price, price_precision)

        # okx api
        # if instId not in self.instrument_info_dict:
        #   tick_size = float(self.instrument_info_dict[instId]['tickSz'])
        #   adjusted_price = self.round_price_to_tick(price, tick_size)

        # response = public_api.convert_contract_coin(type='1', instId=instId, sz=str(amount_usdt), px=str(adjusted_price), unit='usdt', opType='open')
        
        # 使用ccxt进行单位换算：将USDT金额转换为合约张数
        contract_amount = self.exchange.amount_to_precision(symbol, amount_usdt / float(adjusted_price))
        # contract_amount = 30
        # if float(contract_amount) > 0:
        if amount_usdt > 0:
            if side == 'buy':
                pos_side = 'long' 
            else:
                pos_side = 'short'   
            # 设置杠杆 
            self.set_leverage(symbol=symbol, leverage=self.leverage_value, mgnMode='isolated',posSide=pos_side)  
            params = {
                
                "tdMode": 'isolated',
                "side": side,
                "ordType": 'limit',
                "sz": contract_amount,
                "px": str(adjusted_price)
            } 
            
            # 模拟盘(demo_trading)需要 posSide
            if self.is_demo_trading == 1 :
                params["posSide"] = pos_side
                
            self.logger.debug(f"---- Order placed params: {params}")
            try:
                # 使用ccxt创建订单
                order_result = self.exchange.create_order(
                    symbol=symbol,
                    type='limit',
                    side=side,
                    amount=amount_usdt,
                    price=float(adjusted_price),
                    params=params
                )
                self.logger.debug(f"Order placed: {order_result}")
            except Exception as e:
                self.logger.error(f"Failed to place order: {e}")
        else:
            self.logger.warn(f"{symbol} 金额转换为合约张数失败！")
            self.send_feishu_notification(f"{symbol} 金额转换为合约张数失败！")
        self.logger.info(f"------------------ {symbol} Order placed done! ------------------")   
        
    # 接针挂单业务逻辑
    def process_pair(self,symbol,pair_config):
        try:
            klines = self.get_historical_klines(symbol=symbol)
            # 提取收盘价数据用于计算 EMA
            # 从K线数据中提取收盘价，按时间顺序排列（新数据在后）
            close_prices = [float(kline[4]) for kline in klines]
    

            # 计算 EMA
            ema_length = pair_config.get('ema', 240)
            
            # 如果ema值为0 不区分方向，不挂单
            if ema_length == 0:
                is_bullish_trend = True
                is_bearish_trend = True
            else:
                ema = self.calculate_ema_pandas(close_prices, period=ema_length)
                # 判断趋势：多头趋势或空头趋势
                is_bullish_trend = close_prices[-1] > ema  # 收盘价在 EMA 之上
                is_bearish_trend = close_prices[-1] < ema  # 收盘价在 EMA 之下
                self.logger.info(f"{symbol} EMA: {ema:.6f}, 当前价格: {close_prices[-1]:.6f}, 多头趋势: {is_bullish_trend}, 空头趋势: {is_bearish_trend}")
            # 接针挂单逻辑
            wick_reversal_strategy = pair_config.get('wick_reversal_strategy', {})
            use_market_price = wick_reversal_strategy.get('use_market_price', 1)
            if use_market_price == 1 :
                base_price = self.get_mark_price(symbol=symbol) #最新价格
            else :
                base_price = klines[-1][4] # 替换成上周期的收盘价格
            # 计算 ATR
            atr = self.calculate_atr(klines)
            # 当前价格/ATR比值
            price_atr_ratio = (base_price / atr) / 100
            self.logger.info(f"{symbol} ATR: {atr:.3f}, 当前价格/ATR比值: {price_atr_ratio:.3f}")
            # 平均振幅
            average_amplitude = self.calculate_average_amplitude(klines)
            self.logger.info(f"{symbol} 平均振幅: {average_amplitude:.2f}%")

            # 接针的挂单距离，默认计算逻辑是atr/close 跟 振幅ma的区间求最小值 *系数，如果周期小这样其实大部分时候都是采用的振幅，
            value_multiplier = wick_reversal_strategy.get('value_multiplier', 2)
            '''
                接针的挂单距离，默认计算逻辑是atr/close 跟 振幅ma的区间求最小值 *系数，如果周期小这样其实大部分时候都是采用的振幅，
                其实可以多试试其他方案，比如改成atr/close 跟 振幅ma的平均值，这样的话atr权重实际会更大，大部分行情还是atr反应更直接。
            '''
            # selected_value = (average_amplitude + price_atr_ratio)/2 * value_multiplier
            
            selected_value = min(average_amplitude, price_atr_ratio) * value_multiplier
            amplitude_limit = float(wick_reversal_strategy.get('amplitude_limit', 0.8))
            selected_value = max(selected_value, amplitude_limit)
            self.logger.info(f"{symbol} selected_value: {selected_value} ")


            long_price_factor = 1 - selected_value / 100
            short_price_factor = 1 + selected_value / 100

            long_amount_usdt = pair_config.get('long_amount_usdt', 5)
            short_amount_usdt = pair_config.get('short_amount_usdt', 5)

            target_price_long = base_price * long_price_factor
            target_price_short = base_price * short_price_factor

            self.logger.info(f"{symbol} base_price: {base_price} Long target price: {target_price_long:.6f}, Short target price: {target_price_short:.6f}")

            self.cancel_all_orders(symbol=symbol)

            # 判断趋势后决定是否挂单
            if is_bullish_trend:
                self.logger.info(f"{symbol} 当前为多头趋势，允许挂多单")
                # send_feishu_notification(f"{instId} place_order:+buy+,目标价格:{target_price_long},交易USDT:{long_amount_usdt} ")
                self.place_order(symbol, target_price_long, long_amount_usdt, 'buy')
            else:
                self.logger.info(f"{symbol} 当前非多头趋势，跳过多单挂单")

            if is_bearish_trend:
                self.logger.info(f"{symbol} 当前为空头趋势，允许挂空单")
                # send_feishu_notification(f"{instId} place_order:-sell-,目标价格:{target_price_short},交易USDT:{short_amount_usdt} ")
                self.place_order(symbol, target_price_short, short_amount_usdt, 'sell')
            else:
                self.logger.info(f"{symbol} 当前非空头趋势，跳过空单挂单")

        except Exception as e:
            error_message = f'Error processing {symbol}: {e}'
            self.logger.error(error_message)
            self.send_feishu_notification(error_message)
            
    def monitor_klines(self):
        symbols = list(self.trading_pairs_config.keys())  # 获取所有币对的ID
        batch_size = 5  # 每批处理的数量
        while True:
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                with ThreadPoolExecutor(max_workers=batch_size) as executor:
                    futures = [executor.submit(self.process_pair, symbol,self.trading_pairs_config[symbol]) for symbol in batch]
                    for future in as_completed(futures):
                        future.result()  # Raise any exceptions caught during execution

            time.sleep(self.monitor_interval)