import logging
import yaml
from logging.handlers import TimedRotatingFileHandler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

from maker.WickReversalStrategyMaker import WickReversalStrategyMaker
from maker.ThreeLineStrategyMaker import ThreeLineStrategyMaker
from maker.MACDStrategyMaker import MACDStrategyMaker
from maker.SMCStrategyMaker import SMCStrategyMaker
from maker.BestFVGStrategyMaker import BestFVGStrategyMaker

def build_logger(log_config) -> logging.Logger:
        # 配置日志

        log_file = log_config["file"] 
        logger = logging.getLogger(__name__)
        logger.setLevel(log_config["level"])

        file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7, encoding='utf-8')
        file_handler.suffix = "%Y-%m-%d"
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
def read_config_file(file_path):
    try:
        # 打开 YAML 文件
        with open(file_path, 'r', encoding='utf-8') as file:
            # 使用 yaml.safe_load 方法解析 YAML 文件内容
            data = yaml.safe_load(file)
            return data
    except FileNotFoundError:
        raise Exception(f"文件 {file_path} 未找到。")
    except yaml.YAMLError as e:
        raise Exception(f"解析 {file_path} 文件时出错: {e}")
    
def run_bot(bot, logger):
    try:

        bot.monitor_klines()
    except Exception as e:
        logger.error(f"执行任务时发生错误: {str(e)}", exc_info=True)

def main():   
    import importlib.metadata
    version = importlib.metadata.version("openfund-maker")
    
    maker_config_path = 'maker_config.yaml'
    config_data = read_config_file(maker_config_path)
        
    platform_config = config_data['okx']
    feishu_webhook_url = config_data['feishu_webhook']
    logger = build_logger(config_data["Logger"])
    package_name = __package__ or "maker"

    
    maker = config_data.get('actived_maker', 'MACDStrategyMaker')
    
    
    # 根据配置动态创建策略实例
    strategy_class = globals()[maker]
    bot = strategy_class(config_data, platform_config, feishu_webhook=feishu_webhook_url, logger=logger)
    
    logger.info(f" ++ {package_name}.{maker}:{version} is doing...")
    
    # 获取计划配置
    schedule_config = config_data.get('schedule', {})
    if schedule_config.get('enabled', False):
        scheduler = BlockingScheduler()
        
        # 设置每5分钟执行一次的任务，从整点开始
        monitor_interval = int(schedule_config.get('monitor_interval', 4)) 
        
        # 计算下一个整点分钟
        now = datetime.now()
        # 将当前时间的秒和微秒设置为0
        next_run = now.replace(second=58, microsecond=0)
        # 计算下一个周期的开始时间
        current_minute = next_run.minute
        # 向上取整到下一个周期时间点, 然后再减去2Units,比如秒就是58秒执行。
        next_interval = ((current_minute // monitor_interval) + 1) * monitor_interval -1
        # 如果下一个周期时间点超过60分钟，需要调整为下一个小时的对应分钟数
        if next_interval >= 60:
            next_interval = next_interval % 60
            next_run = next_run.replace(hour=next_run.hour + 1)
        next_run = next_run.replace(minute=next_interval)
        
        scheduler.add_job(
            run_bot,
            IntervalTrigger(minutes=monitor_interval),
            args=[bot, logger],
            next_run_time=next_run  # 从下一个周期整点开始
        )
        
        try:
            logger.info(f"启动定时任务调度器，从 {next_run} 开始每{monitor_interval}分钟执行一次...")
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("程序收到中断信号，正在退出...")
            scheduler.shutdown()
    else:
        # 如果未启用计划，直接运行
        run_bot(bot, logger)

if __name__ == "__main__":
    main()
