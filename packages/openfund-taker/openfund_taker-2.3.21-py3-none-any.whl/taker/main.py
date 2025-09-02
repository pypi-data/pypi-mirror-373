import logging
import logging.config
import yaml
import importlib
import importlib.metadata
from pathlib import Path
from typing import Dict, Any
from pyfiglet import Figlet

def read_config_file(file_path: str) -> Dict[str, Any]:
    """读取并解析YAML配置文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"文件 {file_path} 未找到。")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"解析 {file_path} 文件时出错: {e}")

def initialize_logger(config: Dict[str, Any]) -> logging.Logger:
    """初始化日志配置并返回logger实例"""
    logging.config.dictConfig(config["Logger"])
    return logging.getLogger("openfund-taker")

def create_strategy_instance(taker_name: str, configs: Dict[str, Any], logger: logging.Logger, exchangeKey:str):
    """创建策略实例"""
    module = importlib.import_module(f"taker.{taker_name}")
    strategy_class = getattr(module, taker_name)
    return strategy_class(
        configs, 
        configs['platform'][exchangeKey],
        configs['common'],
        logger=logger
    )

def main():
    # 获取版本信息和包名
    version = importlib.metadata.version("openfund-taker")
    package_name = __package__ or "taker"

    # 读取配置文件
    config_path = Path('taker_config.yaml')
    config_data = read_config_file(config_path)
    
    # 获取配置参数
    common_config = config_data['common']
    taker_name = common_config.get('actived_taker', 'StrategyTaker')

    # 初始化日志
    logger = initialize_logger(config_data)
    
    # 显示启动信息
    f = Figlet(font="standard")
    logger.info(f"\n{f.renderText('OpenFund Taker')}")
    logger.info(f" ++ {package_name}.{taker_name}:{version} is doing...")
    exchangeKey = common_config.get("exchange_key", "okx")
    # 创建并运行策略实例
    bot = create_strategy_instance(taker_name, config_data, logger, exchangeKey)
    bot.monitor_total_profit()

if __name__ == "__main__":
    main()
