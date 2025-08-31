import logging
import logging.config
import yaml
import importlib
import importlib.metadata
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from pyfiglet import Figlet
from typing import Dict, Any

def read_config_file(file_path: str) -> Dict[str, Any]:
    """读取并解析YAML配置文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 {file_path} 未找到。")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"解析 {file_path} 文件时出错: {e}")

def run_bot(bot: Any, logger: logging.Logger) -> None:
    """执行机器人监控任务"""
    try:
        bot.monitor_klines()
    except Exception as e:
        logger.error(f"执行任务时发生错误: {str(e)}", exc_info=True)

def calculate_next_run_time(current_time: datetime, interval: int) -> datetime:
    """计算下一次运行时间"""
    next_run = current_time.replace(second=58, microsecond=0)
    current_minute = next_run.minute
    next_interval = ((current_minute // interval) + 1) * interval - 1
    
    if next_interval >= 60:
        next_interval %= 60
        next_run = next_run.replace(hour=next_run.hour + 1)
    
    return next_run.replace(minute=next_interval)

def setup_scheduler(bot: Any, logger: logging.Logger, interval: int) -> None:
    """设置并启动调度器"""
    scheduler = BlockingScheduler()
    next_run = calculate_next_run_time(datetime.now(), interval)
    
    scheduler.add_job(
        run_bot,
        IntervalTrigger(minutes=interval),
        args=[bot, logger],
        next_run_time=next_run
    )
    
    try:
        logger.info(f"启动定时任务调度器，从 {next_run} 开始每{interval}分钟执行一次...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("程序收到中断信号，正在退出...")
        scheduler.shutdown()
def create_strategy_instance(maker_name: str, configs: Dict[str, Any], logger: logging.Logger, exchangeKey:str):
    """创建策略实例"""
    module = importlib.import_module(f"maker.{maker_name}")
    strategy_class = getattr(module, maker_name)
    return strategy_class(
        configs, 
        configs['platform'][exchangeKey],
        configs['common'],
        logger=logger,
        exchangeKey=exchangeKey
    )
def main():
    # 获取包信息
    version = importlib.metadata.version("openfund-maker")
    package_name = __package__ or "openfund-maker"
    
    # 读取配置
    maker_config_path = 'maker_config.yaml'
    config_data = read_config_file(maker_config_path)
    
    # 设置日志
    logging.config.dictConfig(config_data["Logger"])
    logger = logging.getLogger("openfund-maker")
    
    # 显示启动标题
    f = Figlet(font="standard")
    logger.info(f"\n{f.renderText('OpenFund Maker')}")
    
    # 获取配置信息
    common_config = config_data['common']
    maker_name = common_config.get('actived_maker', 'StrategyMaker')
    logger.info(f" ++ {package_name}.{maker_name}:{version} is doing...")
    exchangeKey = common_config.get("exchange_key", "okx")
    # 创建并运行策略实例
    bot = create_strategy_instance(maker_name, config_data, logger, exchangeKey)

    # 处理调度
    schedule_config = common_config.get('schedule', {})
    if schedule_config.get('enabled', False):
        monitor_interval = int(schedule_config.get('monitor_interval', 4))
        setup_scheduler(bot, logger, monitor_interval)
    else:
        run_bot(bot, logger)

if __name__ == "__main__":
    main()
