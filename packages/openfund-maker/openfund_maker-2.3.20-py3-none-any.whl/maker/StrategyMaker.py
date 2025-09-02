# -*- coding: utf-8 -*-
from functools import lru_cache
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.utils.OPTools import OPTools
from core.Exchange import Exchange

# 导入SMC相关模块
from core.smc import (
    SMCBase,
    SMCPDArray,
    SMCStruct, 
    SMCOrderBlock,
    SMCFVG,
    SMCLiquidity
)

class StrategyMaker():
    BUY_SIDE = 'buy'
    SELL_SIDE = 'sell'
    BULLISH_TREND = 'Bullish'
    BEARISH_TREND = 'Bearish'

    HIGH_COL = SMCBase.SMCBase.HIGH_COL
    LOW_COL = SMCBase.SMCBase.LOW_COL
    CLOSE_COL = SMCBase.SMCBase.CLOSE_COL
    OPEN_COL = SMCBase.SMCBase.OPEN_COL
    TIMESTAMP_COL = SMCBase.SMCBase.TIMESTAMP_COL
    VOLUME_COL = SMCBase.SMCBase.VOLUME_COL
    
    STRUCT_COL = SMCStruct.SMCStruct.STRUCT_COL
    STRUCT_HIGH_COL = SMCStruct.SMCStruct.STRUCT_HIGH_COL
    STRUCT_LOW_COL = SMCStruct.SMCStruct.STRUCT_LOW_COL 
    STRUCT_MID_COL = SMCStruct.SMCStruct.STRUCT_MID_COL
    STRUCT_HIGH_INDEX_COL = SMCStruct.SMCStruct.STRUCT_HIGH_INDEX_COL
    STRUCT_LOW_INDEX_COL = SMCStruct.SMCStruct.STRUCT_LOW_INDEX_COL
    STRUCT_DIRECTION_COL = SMCStruct.SMCStruct.STRUCT_DIRECTION_COL
    HIGH_START_COL = SMCStruct.SMCStruct.HIGH_START_COL
    LOW_START_COL = SMCStruct.SMCStruct.LOW_START_COL
    
    OB_HIGH_COL = SMCOrderBlock.SMCOrderBlock.OB_HIGH_COL
    OB_LOW_COL = SMCOrderBlock.SMCOrderBlock.OB_LOW_COL
    OB_MID_COL = SMCOrderBlock.SMCOrderBlock.OB_MID_COL
    OB_VOLUME_COL = SMCOrderBlock.SMCOrderBlock.OB_VOLUME_COL
    OB_DIRECTION_COL = SMCOrderBlock.SMCOrderBlock.OB_DIRECTION_COL
    OB_ATR = SMCOrderBlock.SMCOrderBlock.OB_ATR
    OB_IS_COMBINED = SMCOrderBlock.SMCOrderBlock.OB_IS_COMBINED
    OB_WAS_CROSSED = SMCOrderBlock.SMCOrderBlock.OB_WAS_CROSSED
    
    PD_HIGH_COL = SMCPDArray.SMCPDArray.PD_HIGH_COL
    PD_LOW_COL = SMCPDArray.SMCPDArray.PD_LOW_COL
    PD_MID_COL = SMCPDArray.SMCPDArray.PD_MID_COL 
    PD_TYPE_COL = SMCPDArray.SMCPDArray.PD_TYPE_COL

    LIQU_HIGH_COL = SMCLiquidity.SMCLiquidity.LIQU_HIGH_COL
    LIQU_LOW_COL = SMCLiquidity.SMCLiquidity.LIQU_LOW_COL
    EQUAL_HIGH_COL = SMCLiquidity.SMCLiquidity.EQUAL_HIGH_COL
    EQUAL_LOW_COL = SMCLiquidity.SMCLiquidity.EQUAL_LOW_COL
    EQH_INDEX_KEY = SMCLiquidity.SMCLiquidity.EQUAL_HIGH_INDEX_KEY
    EQL_INDEX_KEY = SMCLiquidity.SMCLiquidity.EQUAL_LOW_INDEX_KEY
    HAS_EQ_KEY = SMCLiquidity.SMCLiquidity.HAS_EQ_KEY

    SUPPORT_PRICE_KEY = "support_price"
    RESISTANCE_PRICE_KEY = "resistance_price"
    SUPPORT_TIMESTAMP_KEY = "support_timestamp"
    RESISTANCE_TIMESTAMP_KEY = "resistance_timestamp"
    SUPPORT_OB_KEY = "support_OB"
    RESISTANCE_OB_KEY = "resistance_OB"
    
    def __init__(self, config,  platform_config, common_config, feishu_webhook=None, logger=None ,exchangeKey='okx'):
        """_summary_
            初始化
        Args:
            config (_type_): _description_
            platform_config (_type_): _description_
            common_config (_type_): _description_
            feishu_webhook (_type_, optional): _description_. Defaults to None.
            logger (_type_, optional): _description_. Defaults to None.
        """
        self.logger = logger
        self.g_config = config
        
        self.common_config = common_config
        self.feishu_webhook = self.common_config.get('feishu_webhook',"")
      
        self.strategy_config = self.g_config.get('strategy', {})
        self.trading_pairs_config = self.g_config.get('tradingPairs', {})
        
        self.leverage_value = self.strategy_config.get('leverage', 20)
        self.is_demo_trading = self.common_config.get('is_demo_trading', 1)  # live trading: 0, demo trading: 1
        proxies = {
            "http": self.common_config.get('proxy', "http://localhost:7890"),
            "https": self.common_config.get('proxy', "http://localhost:7890")
        }
        try:
            self.exchange = Exchange({
                'apiKey': platform_config["apiKey"],
                'secret': platform_config["secret"],
                'password': platform_config["password"],
                'timeout': 3000,
                'rateLimit': 50,
                'options': {'defaultType': 'future'},
                'proxies': proxies
            }, exchangeKey)
        except Exception as e:
            self.logger.error(f"连接交易所失败: {e}")
            raise Exception(f"连接交易所失败: {e}")
        
        self.smcPDArray = SMCPDArray.SMCPDArray()
        self.smcStruct = SMCStruct.SMCStruct()
        self.smcOB = SMCOrderBlock.SMCOrderBlock()
        self.smcFVG = SMCFVG.SMCFVG()
        self.smcLiqu = SMCLiquidity.SMCLiquidity()
        
        self.interval_map = {
            '1d': 24 * 60 * 60 ,  # 1天
            '4h': 4 * 60 * 60 ,   # 4小时
            '1h': 60 * 60 ,        # 1小时
            '30m': 30 * 60 ,       # 30分钟
            '15m': 15 * 60 ,       # 15分钟
            '5m': 5 * 60 ,         # 5分钟
        }
        
        self.place_order_prices = {} # 记录每个symbol的挂单价格
        self.cache_time = {}  # 记录缓存时间的字典

    
    def toDecimal(self, price):
        """_summary_
            将价格转换为Decimal类型
        Args:
            price (_type_): _description_
        Returns:
            _type_: _description_
        """
        return OPTools.toDecimal(price)
        
    def get_pair_config(self,symbol):
        # 获取交易对特定配置,如果没有则使用全局策略配置
        pair_config = self.trading_pairs_config.get(symbol, {})
        
        # 使用字典推导式合并配置,trading_pairs_config优先级高于strategy_config
        pair_config = {
            **self.strategy_config,  # 基础配置
            **pair_config  # 交易对特定配置会覆盖基础配置
        }
        return pair_config
        
    
    def send_feishu_notification(self, symbol, message):
        if self.feishu_webhook:
            try:
                OPTools.send_feishu_notification(self.feishu_webhook,message)
            except Exception as e:
                self.logger.warning(f"{symbol} 发送飞书消息失败: {e}")

    def get_precision_length(self, symbol):
        """_summary_
            获取价格的精度长度
        Args:
            price (_type_): _description_
        Returns:
            _type_: _description_
        """
        tick_size = self.exchange.get_tick_size(symbol)
        return self.smcStruct.get_precision_length(tick_size)
    
    def get_market_price(self, symbol):
        """_summary_
            获取最新成交价
        Args:
            symbol (_type_): _description_
        Returns:
            _type_: _description_
        """
        return self.exchange.get_market_price(symbol)
    
    def place_order(self, symbol, price:Decimal, side,  pair_config, leverage:int=0, order_type='limit'):
        """_summary_
            下单
        Args:
            symbol (_type_): _description_
            price (_type_): _description_
            amount_usdt (_type_): _description_
            side (_type_): _description_
            order_type (_type_): _description_
        """
        # 获取做多和做空的下单金额配置
        long_amount_usdt = pair_config.get('long_amount_usdt', 5)
        short_amount_usdt = pair_config.get('short_amount_usdt', 5)
        
        # 设置杠杆倍数
        leverage = leverage or self.leverage_value
        
        # 根据交易方向设置下单金额
        order_amount_usdt = short_amount_usdt if side == self.SELL_SIDE else long_amount_usdt
        
        # 记录下单日志
        direction = self.BULLISH_TREND if side == self.BUY_SIDE else self.BEARISH_TREND
        self.logger.info(f"{symbol} : 触发{direction}下单条件. 下单价格: {price}")
        
        # 执行下单
        try :
            self.exchange.place_order(
                symbol=symbol,
                price=price,
                amount_usdt=order_amount_usdt,
                side=side,
                leverage=leverage,
                order_type=order_type
            )
        except Exception as e:
            error_message = f"{symbol} 下单失败: {e}"
            self.logger.error(error_message)
            self.send_feishu_notification(symbol, error_message)
      
    def cancel_all_orders(self, symbol):
        """_summary_
            取消所有挂单
        Args:
            symbol (_type_): _description_
        """
        try:
            self.exchange.cancel_all_orders(symbol=symbol)
        except Exception as e:
            error_message = f"{symbol} 取消所有挂单失败: {e}"
            self.logger.error(error_message)
            self.send_feishu_notification(symbol, error_message)
            
    def get_historical_klines(self, symbol, tf='15m'):
        """_summary_
            获取历史K线数据
        Args:
            symbol (_type_): _description_
            bar (_type_, optional): _description_. Defaults to '15m'.
        Returns:
            _type_: _description_
        """
        return self.exchange.get_historical_klines(symbol=symbol, bar=tf)
    
    @lru_cache(maxsize=32)  # 缓存最近32个不同的请求
    def _get_cache_historical_klines_df(self, symbol, tf):
        """被缓存的获取K线数据的方法"""
        return self.get_historical_klines_df(symbol, tf)
    
    def clear_cache_historical_klines_df(self, symbol=None):
        """
        清除指定交易对和时间周期的缓存
        
        参数:
            symbol (str, optional): 交易对符号，如为None则清除所有缓存
            tf (str, optional): 时间周期，如为None则清除所有缓存
        """
        if symbol is None:
            # 清除所有缓存
            self._get_cache_historical_klines_df.cache_clear()
            self.cache_time.clear()
            # print("已清除所有K线数据缓存")
        else:
            # 删除所有包含cache_key的缓存
            keys_to_delete = [k for k in self.cache_time.keys() if symbol in k]
            if keys_to_delete:
                for k in keys_to_delete:
                    del self.cache_time[k]
                # 由于lru_cache无法单独清除特定键，这里只能清除所有缓存
                self._get_cache_historical_klines_df.cache_clear()
      
    def get_historical_klines_df_by_cache(self, symbol, tf='15m'):
        """_summary_
            获取历史K线数据
        Args:
            symbol (_type_): _description_
            bar (_type_, optional): _description_. Defaults to '15m'.
        Returns:
            _type_: _description_
        """
        # cache_key = (symbol, tf)
        cache_valid_second = self.interval_map.get(tf, 4 * 60 * 60)  # 默认缓存时间为60分钟
        cache_key = (symbol, tf)
        
        # 检查缓存是否存在且未过期
        current_time = datetime.now()
        if cache_key in self.cache_time:
            # 计算缓存时间与当前时间的差值(秒)
            cache_age = (current_time - self.cache_time[cache_key]).total_seconds()
            if cache_age <= cache_valid_second:
                # 缓存有效，直接返回
                # print(f"使用缓存数据: {symbol} {tf} (缓存时间: {cache_age:.2f} 分钟前)")
                return self._get_cache_historical_klines_df(symbol, tf)
            else:
                # 缓存过期，清除缓存
                self.logger.debug(f"{symbol} : 缓存已过期: {symbol} {tf} (缓存时间: {cache_age:.2f} 秒前)")
                self._get_cache_historical_klines_df.cache_clear()
        
        # 获取新数据并更新缓存时间
        self.logger.debug(f"{symbol} : 重新获取新数据: {symbol} {tf}")
        self.cache_time[cache_key] = current_time
        return self._get_cache_historical_klines_df(symbol, tf)
   
    def get_historical_klines_df(self, symbol, tf='15m', after:str=None):
        """_summary_
            获取历史K线数据
        Args:
            symbol (_type_): _description_
            bar (_type_, optional): _description_. Defaults to '15m'.
        Returns:
            _type_: _description_
        """
        return self.exchange.get_historical_klines_df(symbol=symbol, bar=tf, after=after)
    
    def format_klines(self, klines) -> pd.DataFrame:
       
        """_summary_
            格式化K线数据
        Args:
            klines (_type_): _description_
        Returns:
            _type_: _description_
        """
        
        return self.exchange.format_klines(klines)
    
    def find_PDArrays(self, symbol, struct, side=None, start_index=-1, pair_config=None) -> pd.DataFrame:
        """_summary_
            寻找PDArray
        Args:
            symbol (_type_): _description_
            data (_type_): _description_
            side (_type_): _description_
            start_index (_type_): _description_ 
            is_valid (bool, optional): _description_. Defaults to True.
            pair_config (_type_): _description_
        Returns:
            _type_: _description_
        """
        return self.smcPDArray.find_PDArrays(struct=struct, side=side, start_index=start_index)  
    
    def find_OBs(self, symbol, struct, side=None, start_index=-1, is_valid=True, is_struct_body_break=True,atr_multiplier=0.6, pair_config=None ) -> pd.DataFrame:
        """_summary_
            识别OB
        Args:
            symbol (_type_): _description_
            data (_type_): _description_
            side (_type_): _description_
            start_index (_type_): _description_
            is_valid (bool, optional): _description_. Defaults to True.
            pair_config (_type_): _description_
        Returns:
            _type_: _description_
        """

        return self.smcOB.find_OBs(struct=struct, side=side, start_index=start_index, is_valid=is_valid, is_struct_body_break=is_struct_body_break,atr_multiplier=atr_multiplier)
    
    def get_latest_OB(self, symbol, data, trend, start_index=-1) -> dict:
        """_summary_
            获取最新的Order Block
        Args:
            symbol (_type_): _description_
            data (_type_): _description_
            trend (_type_): _description_
            start_index (_type_): _description_
        Returns:
            _type_: _description_
        """

        return self.smcOB.get_latest_OB(data=data, trend=trend, start_index=start_index)
               
    def find_FVGs(self, symbol, data, side, check_balanced=True, start_index=-1, pair_config=None) -> pd.DataFrame:
        """_summary_
            寻找公允价值缺口
        Args:
            symbol (_type_): _description_
            data (_type_): _description_
            side (_type_): _description_
            check_balanced (bool, optional): _description_. Defaults to True.
            start_index (_type_): _description_
            pair_config (_type_): _description_
        Returns:
            _type_: _description_
        """
            

        return self.smcFVG.find_FVGs(data, side, check_balanced, start_index)

    def find_EQH_EQL(self, symbol, data, trend, end_idx=-1, atr_offset=0.1, pair_config=None) -> dict:
        """_summary_
            寻找等值高点和等值低点
        Args:
            symbol (_type_): _description_
            data (_type_): _description_
            trend (_type_): _description_
            end_idx (int, optional): _description_. Defaults to -1.
            atr_offset (float, optional): _description_. Defaults to 0.1.
        Returns:
            _type_: _description_
        """
        return self.smcLiqu.find_EQH_EQL(data, trend, end_idx=end_idx, atr_offset=atr_offset)

    def identify_dynamic_trendlines(self, symbol, data, trend, start_idx=-1, end_idx=-1, ratio=0.8) -> bool:
        """_summary_
            识别动态趋势线
        Args:
            symbol (_type_): _description_
            data (_type_): _description_
            trend (_type_): _description_
            start_idx (int, optional): _description_. Defaults to -1.
            end_idx (int, optional): _description_. Defaults to -1.
            ratio (float, optional): _description_. Defaults to 0.5.
        Returns:
            _type_: _description_
        """
        return self.smcLiqu.identify_dynamic_trendlines(data, trend, start_idx, end_idx, ratio)

    def build_struct(self, symbol, data, tf=None, is_struct_body_break=True) -> pd.DataFrame:
        
        """_summary_
            构建SMC结构，参考 Tradingview OP@SMC Structures and FVG
        Args:
            symbol (_type_): _description_
            data (_type_): _description_
        Returns:
            _type_: _description_    
        """
        
                
        return self.smcStruct.build_struct(data, tf=None, is_struct_body_break=is_struct_body_break)
        
    def get_latest_struct(self, symbol, data, is_struct_body_break=True) -> dict:
        """_summary_
            获取最后一个SMC结构
        Args:
            symbol (_type_): _description_
            data (_type_): _description_
        Returns:
            _type_: _description_
        """
        return self.smcStruct.get_latest_struct(data, is_struct_body_break=is_struct_body_break)
    
    def reset_all_cache(self, symbol):
        """_summary_
            重置所有缓存数据
        """
        if symbol in self.place_order_prices:            
            self.place_order_prices.pop(symbol)
        self.clear_cache_historical_klines_df(symbol)
        
    def fetch_position(self, symbol) -> bool:
        """
        检查指定交易对是否有持仓，失败时最多重试3次
        
        Args:
            symbol: 交易对ID
            
        Returns:
            bool: 是否有持仓
        """
        try:
            position = self.exchange.fetch_position(symbol=symbol)
            return position['contracts'] > 0
        except Exception as e:
            error_message = f"{symbol} 检查持仓失败: {e}"
            self.logger.error(error_message)            
            self.send_feishu_notification(symbol,error_message)
            return True

    def  get_support_resistance(self, symbol, data_struct) -> dict:
        """_summary_
            获取支持位和阻力位
        Args:
            symbol (_type_): _description_
            data_struct (_type_): _description_
        Returns:
            dict: _description_
        """
    def get_support_resistance_from_OBs(self, symbol, obs_struct) -> dict:
        '''
        获取支持位和阻力位
        Args:
            symbol (str): _description_
            data_struct (pd.DataFrame): _description_
            is_struct_body_break (bool, optional): _description_. Defaults to True.

        Returns:
            dict: _description_
        '''
        OBs_df = obs_struct.copy()

        if OBs_df is None or len(OBs_df) == 0:
            # self.logger.debug(f"{symbol} : {step}. HTF {htf} 未找到OB。")
            return None
        else:
            # self.logger.debug(f"{symbol} : {step}. HTF {htf} 找到OB。")
        
            support_OB = self.get_latest_OB(symbol=symbol,data=OBs_df,trend=self.BULLISH_TREND)
            if support_OB :
                support_price = support_OB.get(self.OB_MID_COL)
                support_timestamp = support_OB.get(self.TIMESTAMP_COL)
            else:
                support_price = OBs_df.at[OBs_df.index[-1], self.STRUCT_LOW_COL]
                support_timestamp = OBs_df.at[OBs_df.index[-1], self.TIMESTAMP_COL]
        
            resistance_OB = self.get_latest_OB(symbol=symbol,data=OBs_df,trend=self.BEARISH_TREND)
            if resistance_OB :
                resistance_price = resistance_OB.get(self.OB_MID_COL)
                resistance_timestamp = resistance_OB.get(self.TIMESTAMP_COL)
            else:
                resistance_price = OBs_df.at[OBs_df.index[-1], self.STRUCT_HIGH_COL]
                resistance_timestamp = OBs_df.at[OBs_df.index[-1], self.TIMESTAMP_COL]
                
                
            return {
                self.SUPPORT_PRICE_KEY: support_price,
                self.SUPPORT_TIMESTAMP_KEY: support_timestamp,
                self.RESISTANCE_PRICE_KEY: resistance_price,
                self.RESISTANCE_TIMESTAMP_KEY: resistance_timestamp,
                self.SUPPORT_OB_KEY: support_OB,
                self.RESISTANCE_OB_KEY: resistance_OB,
            }
        

    @abstractmethod
    def process_pair(self, symbol, pair_config):
        """
        处理单个交易对的策略逻辑
        
        Args:
            symbol: 交易对名称
            pair_config: 交易对配置信息
            
        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("必须在子类中实现process_pair方法")   
    
    def monitor_klines(self):
        symbols = list(self.trading_pairs_config.keys())  # 获取所有币对的ID
        batch_size = 10  # 每批处理的数量
        # while True:

        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = [executor.submit(self.process_pair, symbol,self.get_pair_config(symbol)) for symbol in batch]
                for future in as_completed(futures):
                    future.result()  # Raise any exceptions caught during execution
