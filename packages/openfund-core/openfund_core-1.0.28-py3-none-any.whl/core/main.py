import logging
from pyfiglet import Figlet

def main():   

    # import importlib.metadata
    # package_name = __package__ or "openfund-core"
    # version = importlib.metadata.version("openfund-core")

    # 创建日志记录器并设置输出到屏幕
    logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    # # 设置日志级别为INFO
    logger.setLevel(logging.INFO)
    
    f = Figlet(font="standard")  # 字体可选（如 "block", "bubble"）
    logger.info(f"\n{f.renderText("OpenFund Core")}")
    


if __name__ == "__main__":
    main()
