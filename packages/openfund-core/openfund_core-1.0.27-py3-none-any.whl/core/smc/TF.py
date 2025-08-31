from core.utils.OPTools import OPTools


class TF:
    HTF = 'HTF'
    ATF = 'ATF'
    ETF = 'ETF'

    """技术形态(Technical Formation)类"""
    
    def __init__(self, type: str, tf_value: int, side: str, trend: str):
        """
        初始化技术形态对象
        
        Args:
            type: TF类型 HTF|ATF|ETF
            value: TF值 4h/1h/15m/5m/1m
            side: 方向 buy|sell
            trend: 趋势 Bullish|Bearish
        """
        self._type = type
        self._side = side 
        self._trend = trend
        self._tf_value = tf_value
        # 最新的SMC结构
        self._struct = None
        # 价格支撑和阻力位
        self._resistance_price = None
        self._support_price = None
        self._resistance_timestamp = None
        self._support_timestamp = None
        
        # 价格数组
        self._pdArrays = None


        self._up_resistance_status = False
        self._down_support_status = False
        

    
    @property
    def type(self):
        return self._type
        
    @property
    def side(self):
        return self._side
        
    @property
    def trend(self):
        return self._trend
        
    @property
    def tf_value(self):
        return self._tf_value

        # 价格支撑和阻力位状态
    @property
    def up_resistance_status(self):
        return self._up_resistance_status
        
    @up_resistance_status.setter 
    def up_resistance_status(self, value):
        self._up_resistance_status = value
        
    @property
    def down_support_status(self):
        return self._down_support_status
        
    @down_support_status.setter
    def down_support_status(self, value):
        self._down_support_status = value
    
    @property
    def resistance_price(self):
        return self._resistance_price
        
    @resistance_price.setter 
    def resistance_price(self, value):
        self._resistance_price = value
        
    @property
    def support_price(self):
        return self._support_price
        
    @support_price.setter
    def support_price(self, value):
        self._support_price = value

    @property
    def resistance_timestamp(self):
        return self._resistance_timestamp
        
    @resistance_timestamp.setter
    def resistance_timestamp(self, value):
        self._resistance_timestamp = value

    @property
    def support_timestamp(self):
        return self._support_timestamp
        
    @support_timestamp.setter
    def support_timestamp(self, value):
        self._support_timestamp = value
        
    @property
    def struct(self):
        return self._struct
        
    @struct.setter
    def struct(self, value):
        self._struct = value
        
    @property
    def pdArrays(self):
        return self._pdArrays
        
    @pdArrays.setter
    def pdArrays(self, value):
        self._pdArrays = value


        
    def __str__(self):
        return f"{self._type} {self._side} {self._tf_value} {self._trend}"
