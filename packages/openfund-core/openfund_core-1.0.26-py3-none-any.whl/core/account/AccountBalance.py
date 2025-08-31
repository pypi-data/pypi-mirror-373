from decimal import Decimal


class AccountBalance:
    """账户余额类"""
    def __init__(self, currency:str, free: Decimal, used: Decimal, total: Decimal):
        """
        初始化余额对象
        
        Args:
            currency: 币种
            free: 可用余额
            used: 冻结余额
            total: 总余额
        """
        self._currency = currency
        self._free = free
        self._used = used 
        self._total = total
        
        
    @property
    def currency(self):
        return self._currency
    
    @property
    def free(self):
        return self._free

        
    @property
    def used(self):
        return self._used   
        
    @property
    def total(self):
        return self._total
        
    def __str__(self):
        return f"{self._free} {self._used} {self._total}"

    @classmethod
    def build_from_ccxt(cls, ccxt_balance, currency:str = 'USDT'):
        """
        从ccxt获取余额信息
        
        Args:
            ccxt_balance: ccxt余额信息
        """
        # 从ccxt余额信息中获取指定币种的余额数据
      
        free = Decimal(str(ccxt_balance[currency]['free']))
        used = Decimal(str(ccxt_balance[currency]['used']))
        total = Decimal(str(ccxt_balance[currency]['total']))
        return cls(currency, free, used, total)
