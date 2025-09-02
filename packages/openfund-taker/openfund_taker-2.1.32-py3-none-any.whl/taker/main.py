import logging
import yaml
from logging.handlers import TimedRotatingFileHandler

from taker.TrailingSLTaker import TrailingSLTaker
from taker.TrailingSLAndTPTaker import TrailingSLAndTPTaker
from taker.ThreeLineTradingTaker import ThreeLineTradingTaker
from taker.SMCSLAndTPTaker import SMCSLAndTPTaker

def build_logger(log_config) -> logging.Logger:
            # 配置日志
        # log_file = "log/okx_MultiAssetNewTradingBot.log"
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


def main():
    import importlib.metadata
    version = importlib.metadata.version("openfund-taker")
    
    # openfund_config_path = 'config.json'
    openfund_config_path = 'taker_config.yaml'
    config_data = read_config_file(openfund_config_path)
    
    
    # with open(openfund_config_path, 'r') as f:
    #     config_data = json.load(f)
        
    platform_config = config_data['okx']
    feishu_webhook_url = config_data['feishu_webhook']
    monitor_interval = config_data.get("monitor_interval", 60)  # 默认值为60秒
    logger = build_logger(config_data["Logger"])
    package_name = __package__ or "taker" 
    
    taker = config_data.get('actived_taker', 'SMCSLAndTPTaker')
        
    # 根据配置动态创建策略实例
    strategy_class = globals()[taker]
    bot = strategy_class(config_data, platform_config, feishu_webhook=feishu_webhook_url, monitor_interval=monitor_interval,logger=logger)
    logger.info(f" ++ {package_name}.{taker}:{version} is doing...")

    bot.monitor_total_profit()
    # bot = ThreeLineTradingBot(platform_config, feishu_webhook=feishu_webhook_url, monitor_interval=monitor_interval)
    # bot.monitor_klines()

if __name__ == "__main__":
    main()
