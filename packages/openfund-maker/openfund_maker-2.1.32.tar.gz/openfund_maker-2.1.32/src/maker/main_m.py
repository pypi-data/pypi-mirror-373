import time
import json
import logging
import requests
import pandas as pd

import okx.PublicData as PublicData
import okx.Trade as Trade
import okx.MarketData as MarketData
import okx.Account as Account

from concurrent.futures import ThreadPoolExecutor, as_completed
from logging.handlers import TimedRotatingFileHandler

# import app.okx_buou.Trade_api as TradeAPI
# import app.okx_buou.Public_api as PublicAPI
# import app.okx_buou.Market_api as MarketAPI
# import app.okx_buou.Account_api as AccountAPI

import os
openfund_config_path = os.getenv('wick_reversal_config_path','config_okx.json')
# 读取配置文件
with open(openfund_config_path, 'r') as f:
    config = json.load(f)

# 提取配置
okx_config = config['okx']
trading_pairs_config = config.get('tradingPairs', {})
monitor_interval = config.get('monitor_interval', 60)  # 默认60秒
feishu_webhook = config.get('feishu_webhook', '')
leverage_value = config.get('leverage', 10)
api_key = okx_config["apiKey"]
secret_key = okx_config["secret"]
passphrase = okx_config["password"]
flag = "0"  # live trading: 0, demo trading: 1

public_api = PublicData.PublicAPI(api_key, secret_key, passphrase, False, flag)
trade_api = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
market_api = MarketData.MarketAPI(api_key, secret_key, passphrase, False, flag)
account_api = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
# trade_api = TradeAPI.TradeAPI(okx_config["apiKey"], okx_config["secret"], okx_config["password"], False, flag)
# market_api = MarketAPI.MarketAPI(okx_config["apiKey"], okx_config["secret"], okx_config["password"], False, flag)
# public_api = PublicAPI.PublicAPI(okx_config["apiKey"], okx_config["secret"], okx_config["password"], False, flag)
# account_api = AccountAPI.AccountAPI(okx_config["apiKey"], okx_config["secret"], okx_config["password"], False, flag)

log_file = "log/okx.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8')
file_handler.suffix = "%Y-%m-%d"
formatter = logging.Formatter('%(asctime)s - %(name)s -%(lineno)d - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

instrument_info_dict = {}

def fetch_and_store_all_instruments(instType='SWAP'):
    try:
        logger.info(f"Fetching all instruments for type: {instType}")

        response = public_api.get_instruments(instType=instType)
        # response = public_api.get_instruments(instType=instType)
        # logger.debug(f"data: {response['data']}")
        if 'data' in response and len(response['data']) > 0:
            instrument_info_dict.clear()
            for instrument in response['data']:
                instId = instrument['instId']
                instrument_info_dict[instId] = instrument
                # logger.debug(f"Stored instrument: {instId}")
        else:
            raise ValueError("Unexpected response structure or no instrument data available")
    except Exception as e:
        logger.error(f"Error fetching instruments: {e}")
        raise

def send_feishu_notification(message):
    if feishu_webhook:
        headers = {'Content-Type': 'application/json'}
        data = {"msg_type": "text", "content": {"text": message}}
        response = requests.post(feishu_webhook, headers=headers, json=data)
        if response.status_code == 200:
            logger.debug("飞书通知发送成功")
        else:
            logger.error(f"飞书通知发送失败: {response.text}")
            
def get_close_price(instId):
    '''
    bar = 
    时间粒度，默认值1m
    如 [1m/3m/5m/15m/30m/1H/2H/4H]
    香港时间开盘价k线：[6H/12H/1D/2D/3D/1W/1M/3M]
    UTC时间开盘价k线：[/6Hutc/12Hutc/1Dutc/2Dutc/3Dutc/1Wutc/1Mutc/3Mutc]
    '''
    response = market_api.get_candlesticks(instId=instId,bar='1m')
    if 'data' in response and len(response['data']) > 0:
        close_price = response['data'][0][4]
        return float(close_price)
    else:
        raise ValueError("Unexpected response structure or missing 'c' value")


def get_mark_price(instId):
    response = market_api.get_ticker(instId)
    if 'data' in response and len(response['data']) > 0:
        last_price = response['data'][0]['last']
        return float(last_price)
    else:
        raise ValueError("Unexpected response structure or missing 'last' key")

def round_price_to_tick(price, tick_size):
    # 计算 tick_size 的小数位数
    tick_decimals = len(f"{tick_size:.10f}".rstrip('0').split('.')[1]) if '.' in f"{tick_size:.10f}" else 0

    # 调整价格为 tick_size 的整数倍
    adjusted_price = round(price / tick_size) * tick_size
    return f"{adjusted_price:.{tick_decimals}f}"

def get_historical_klines(instId, bar='1m', limit=241):
    response = market_api.get_candlesticks(instId, bar=bar, limit=limit)
    if 'data' in response and len(response['data']) > 0:
        return response['data']
    else:
        raise ValueError("Unexpected response structure or missing candlestick data")

def calculate_atr(klines, period=60):
    trs = []
    for i in range(1, len(klines)):
        high = float(klines[i][2])
        low = float(klines[i][3])
        prev_close = float(klines[i-1][4])
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    atr = sum(trs[-period:]) / period
    return atr

def calculate_ema_pandas(data, period):
    """
    使用 pandas 计算 EMA
    :param 收盘价列表
    :param period: EMA 周期
    :return: EMA 值
    """
    df = pd.Series(data)
    ema = df.ewm(span=period, adjust=False).mean()
    return ema.iloc[-1]  # 返回最后一个 EMA 值


def calculate_average_amplitude(klines, period=60):
    amplitudes = []
    for i in range(len(klines) - period, len(klines)):
        high = float(klines[i][2])
        low = float(klines[i][3])
        close = float(klines[i][4])
        amplitude = ((high - low) / close) * 100
        amplitudes.append(amplitude)
    average_amplitude = sum(amplitudes) / len(amplitudes)
    return average_amplitude

def cancel_all_orders(instId):
    open_orders = trade_api.get_order_list(instId=instId, state='live')
    order_ids = [order['ordId'] for order in open_orders['data']]
    for ord_id in order_ids:
        trade_api.cancel_order(instId=instId, ordId=ord_id)
    logger.info(f"{instId}挂单取消成功.")

def set_leverage(instId, leverage, mgnMode='isolated',posSide=None):
    try:
        body = {
            "instId": instId,
            "lever": str(leverage),
            "mgnMode": mgnMode
        }
        # 模拟盘需要控制 posSide
        if flag =='1' and mgnMode == 'isolated' and posSide:
            body["posSide"] = posSide
        logger.debug(f"Leverage set parameter is:{body}")    
        response = account_api.set_leverage(**body)
        if response['code'] == '0':
            logger.debug(f"Leverage set to {leverage}x for {instId} with mgnMode: {mgnMode}")
        else:
            logger.error(f"Failed to set leverage: {response['msg']}")
    except Exception as e:
        logger.error(f"Error setting leverage: {e}")

def place_order(instId, price, amount_usdt, side):
    if instId not in instrument_info_dict:
        logger.error(f"Instrument {instId} not found in instrument info dictionary")
        return
    tick_size = float(instrument_info_dict[instId]['tickSz'])
    adjusted_price = round_price_to_tick(price, tick_size)
    # response = public_api.convert_contract_coin(type='1', instId=instId, sz=str(amount_usdt), px=str(adjusted_price), unit='usdt', opType='open')
    
    # https://www.okx.com/docs-v5/zh/#public-data-rest-api-unit-convert
    '''
    type 转换类型
        1：币转张
        2：张转币
        默认为1
    '''

    response = public_api.get_convert_contract_coin(type='1', instId=instId, sz=str(amount_usdt), px=str(adjusted_price), unit='usdt')
    if response['code'] == '0':
        sz = response['data'][0]['sz']
        if float(sz) > 0:

            if side == 'buy':
                pos_side = 'long' 
            else:
                pos_side = 'short'
                
            set_leverage(instId=instId, leverage=leverage_value, mgnMode='isolated',posSide=pos_side)
            
            
            params = {
                "instId": instId,
                "tdMode": 'isolated',
                "side": side,
                "ordType": 'limit',
                "sz": sz,
                "px": str(adjusted_price)
            } 
            # 模拟盘需要控制 posSide
            if flag == 1 :
                params["posSide"] = pos_side
            
            logger.info(f"Order placed params: {params}")
            order_result = trade_api.place_order(
                **params
                # instId=instId,
                # #tdMode='isolated',
                # tdMode='cross',# 保证金模式：isolated：逐仓 ；cross：全仓
                # side=side, # 订单方向 buy：买， sell：卖
                # posSide=pos_side, #持仓方向 在开平仓模式下必填，且仅可选择 long 或 short。 仅适用交割、永续。
                # ordType='limit',
                # sz=sz,
                # px=str(adjusted_price)
            )
            logger.debug(f"Order placed: {order_result}")
        else:
            logger.info(f"{instId}计算出的合约张数太小，无法下单。")
    else:
        logger.info(f"{instId}转换失败: {response['msg']}")
        send_feishu_notification(f"{instId}转换失败: {response['msg']}")
    logger.info(f"------------------ {instId} Order placed done! ------------------")   
def check_position(instId, instType='SWAP') -> bool:
    """
    检查指定交易对是否有持仓
    
    Args:
        instType: 交易对类型 SPOT、SWAP、FUTURES
        instId: 交易对ID
        
    Returns:
        bool: 是否有持仓
    """
    try:
        
        positions = account_api.get_positions(instType=instType)
        if positions and 'data' in positions and len(positions['data']) > 0:
            logger.debug(f"{instId} 有持仓，{positions['data']}")
            return True
        return False
    except Exception as e:
        logger.error(f"检查持仓失败 {instId}: {str(e)}")
        return False


# 处理交易对
def process_pair(instId, pair_config):
    if check_position(instId,instType='SWAP'):
        logger.info(f"{instId} 有持仓，不下单!")
        return 
    try:
        use_market_price = pair_config.get('use_market_price', 1)
        if use_market_price == 1 :
            mark_price = get_mark_price(instId)
        else :
            mark_price = get_close_price(instId) # 替换成上周期的收盘价格
        klines = get_historical_klines(instId)

        # 提取收盘价数据用于计算 EMA
        close_prices = [float(kline[4]) for kline in klines[::-1]]  # K线中的收盘价，顺序要新的在最后

        # 计算 EMA
        ema_value = pair_config.get('ema', 240)
        # 如果ema值为0 不区分方向，两头都挂单
        if ema_value == 0:
            is_bullish_trend = True
            is_bearish_trend = True
        else:
            ema60 = calculate_ema_pandas(close_prices, period=ema_value)
            logger.info(f"{instId} EMA60: {ema60:.6f}, 当前价格: {mark_price:.6f}")
            # 判断趋势：多头趋势或空头趋势
            is_bullish_trend = close_prices[-1] > ema60  # 收盘价在 EMA60 之上
            is_bearish_trend = close_prices[-1] < ema60  # 收盘价在 EMA60 之下

        # 计算 ATR
        atr = calculate_atr(klines)
        # 当前价格/ATR比值
        price_atr_ratio = (mark_price / atr) / 100
        logger.info(f"{instId} ATR: {atr:.3f}, 当前价格/ATR比值: {price_atr_ratio:.3f}")
        # 平均振幅
        average_amplitude = calculate_average_amplitude(klines)
        logger.info(f"{instId} 平均振幅: {average_amplitude:.2f}%")

        value_multiplier = pair_config.get('value_multiplier', 2)
        '''
            接针的挂单距离，默认计算逻辑是atr/close 跟 振幅ma的区间求最小值 *系数，如果周期小这样其实大部分时候都是采用的振幅，
            其实可以多试试其他方案，比如改成atr/close 跟 振幅ma的平均值，这样的话atr权重实际会更大，大部分行情还是atr反应更直接。
        '''
        # selected_value = (average_amplitude + price_atr_ratio)/2 * value_multiplier
        
        selected_value = min(average_amplitude, price_atr_ratio) * value_multiplier
        amplitude_limit = float(pair_config.get('amplitude_limit', 0.8))
        selected_value = max(selected_value, amplitude_limit)
        logger.info(f"{instId} selected_value: {selected_value} ")


        long_price_factor = 1 - selected_value / 100
        short_price_factor = 1 + selected_value / 100

        long_amount_usdt = pair_config.get('long_amount_usdt', 5)
        short_amount_usdt = pair_config.get('short_amount_usdt', 5)

        target_price_long = mark_price * long_price_factor
        target_price_short = mark_price * short_price_factor

        logger.info(f"{instId} mark_price: {mark_price} Long target price: {target_price_long:.6f}, Short target price: {target_price_short:.6f}")

        cancel_all_orders(instId)

        # 判断趋势后决定是否挂单
        if is_bullish_trend:
            logger.info(f"{instId} 当前为多头趋势，允许挂多单")
            # send_feishu_notification(f"{instId} place_order:+buy+,目标价格:{target_price_long},交易USDT:{long_amount_usdt} ")
            place_order(instId, target_price_long, long_amount_usdt, 'buy')
        else:
            logger.info(f"{instId} 当前非多头趋势，跳过多单挂单")

        if is_bearish_trend:
            logger.info(f"{instId} 当前为空头趋势，允许挂空单")
            # send_feishu_notification(f"{instId} place_order:-sell-,目标价格:{target_price_short},交易USDT:{short_amount_usdt} ")
            place_order(instId, target_price_short, short_amount_usdt, 'sell')
        else:
            logger.info(f"{instId} 当前非空头趋势，跳过空单挂单")

    except Exception as e:
        error_message = f'Error processing {instId}: {e}'
        logger.error(error_message)
        send_feishu_notification(error_message)

def main():
    import importlib.metadata

    version = importlib.metadata.version("openfund-wick-reversal")
    logger.info(f" ++ openfund-wick-reversal:{version} is doing...")
    logger.info(f" ++ api_key : {api_key}")
    fetch_and_store_all_instruments()
    inst_ids = list(trading_pairs_config.keys())  # 获取所有币对的ID
    batch_size = 5  # 每批处理的数量

    while True:
        for i in range(0, len(inst_ids), batch_size):
            batch = inst_ids[i:i + batch_size]
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = [executor.submit(process_pair, instId, trading_pairs_config[instId]) for instId in batch]
                for future in as_completed(futures):
                    future.result()  # Raise any exceptions caught during execution

        time.sleep(monitor_interval)

if __name__ == '__main__':
    main()
