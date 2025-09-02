import requests
from decimal import Decimal

class OPTools:
    
    @staticmethod
    def toDecimal(value, precision:int=None):
        """将数值转换为Decimal类型
        
        Args:
            value: 需要转换的数值
            precision: 精度,如果不指定则保持原始精度
        
        Returns:
            Decimal: 转换后的Decimal对象 
        """
        if precision is None:
            return Decimal(str(value))
        return Decimal(f"{value:.{precision}f}")
    
    @staticmethod
    def send_feishu_notification(webhook, message):
        if webhook:
            headers = {'Content-Type': 'application/json'}
            data = {"msg_type": "text", "content": {"text": message}}
            response = requests.post(webhook, headers=headers, json=data)
            if response.status_code != 200:
                # self.logger.debug("飞书通知发送成功")
                raise Exception(f"飞书通知发送失败: {response.text} {webhook}")

