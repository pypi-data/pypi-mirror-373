import logging
import time
import ccxt
import pandas as pd


from decimal import Decimal
from core.utils.OPTools import OPTools
from core.account.AccountBalance import AccountBalance 

from ccxt.base.exchange import ConstructorArgs


class Exchange:
    BUY_SIDE = 'buy'
    SELL_SIDE = 'sell'
    LONG_KEY = 'long'
    SHORT_KEY = 'short'
    SIDE_KEY = 'side'
    SYMBOL_KEY = 'symbol'
    ENTRY_PRICE_KEY = 'entryPrice'
    MARK_PRICE_KEY = 'markPrice'
    CONTRACTS_KEY = 'contracts'
    def __init__(self, config:ConstructorArgs, exchangeKey:str = "okx",) :
        # 配置交易所
        self.exchange = getattr(ccxt, exchangeKey)(config)
        self.logger = logging.getLogger(__name__)

    def getMarket(self, symbol:str):
        # 配置交易对
        self.exchange.load_markets()
        
        return self.exchange.market(symbol)
  
    def get_position_mode(self) -> str:
    
        try:
            # 假设获取账户持仓模式的 API
            response = self.exchange.private_get_account_config()
            data = response.get('data', [])
            if data and isinstance(data, list):
                # 取列表的第一个元素（假设它是一个字典），然后获取 'posMode'
                position_mode = data[0].get('posMode', 'single')  # 默认值为单向
                
                return position_mode
            else:
               
                return 'single'  # 返回默认值
        except Exception as e:        
            error_message = f"Error fetching position mode: {e}"
            self.logger.error(error_message)        
            raise Exception(error_message)  
        
    def get_tick_size(self,symbol) -> Decimal:     
        
        market = self.getMarket(symbol)
        if market and 'precision' in market and 'price' in market['precision']:            
            return OPTools.toDecimal(market['precision']['price'])
        else:
            raise ValueError(f"{symbol}: 无法从市场数据中获取价格精度")

    def amount_to_precision(self,symbol, contract_size):
        return self.exchange.amount_to_precision(symbol, contract_size)
       
    def set_leverage(self,symbol, leverage, mgnMode='isolated',posSide=None):
        try:
            # 设置杠杆
            params = {
                # 'instId': instId,
                'leverage': leverage,
                'marginMode': mgnMode
            }
            if posSide:
                params['side'] = posSide
                
            self.exchange.set_leverage(leverage, symbol=symbol, params=params)
            self.logger.info(f"{symbol} Successfully set leverage to {leverage}x")
        except Exception as e:
            error_message = f"{symbol} Error setting leverage: {e}"
            self.logger.error(error_message)        
            raise Exception(error_message)  
    # 获取价格精度
    def get_precision_length(self,symbol) -> int:
        tick_size = self.get_tick_size(symbol)
        return len(f"{tick_size:.15f}".rstrip('0').split('.')[1]) if '.' in f"{tick_size:.15f}" else 0

    def format_price(self, symbol, price:Decimal) -> str:
        precision = self.get_precision_length(symbol)
        return f"{price:.{precision}f}"
    
    def convert_contract(self, symbol, amount, price:Decimal, direction='cost_to_contract'):
        """
        进行合约与币的转换
        :param symbol: 交易对符号，如 'BTC/USDT:USDT'
        :param amount: 输入的数量，可以是合约数量或币的数量
        :param direction: 转换方向，'amount_to_contract' 表示从数量转换为合约，'cost_to_contract' 表示从金额转换为合约
        :return: 转换后的数量
        """

        # 获取合约规模
        market_contractSize = OPTools.toDecimal(self.getMarket(symbol)['contractSize'])
        amount = OPTools.toDecimal(amount)
        if direction == 'amount_to_contract':
            contract_size = amount / market_contractSize
        elif direction == 'cost_to_contract':
            contract_size = amount / price / market_contractSize
        else:
            raise Exception(f"{symbol} : {direction} 是无效的转换方向，请输入 'amount_to_contract' 或 'cost_to_contract'。")
        
        return self.amount_to_precision(symbol, contract_size)
    
    def close_position(self, symbol, position, params={}) -> dict:

        amount = abs(float(position['contracts']))

        if amount <= 0:
            self.logger.warning(f"{symbol}: position contracts must be greater than 0")
            return
            
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            
            try:
                side = position[self.SIDE_KEY]
                self.logger.debug(f"{symbol}: Preparing to close position, side= {side}, amount={amount}")
                position_mode = self.get_position_mode()  # 获取持仓模式
                if position_mode == 'long_short_mode':
                    # 在双向持仓模式下，指定平仓方向
                    # pos_side = 'long' if side == 'long' else 'short'
                    pos_side = side
                else:
                    # 在单向模式下，不指定方向
                    pos_side = 'net'
                orderSide = 'buy' if side == 'long' else 'sell'                
                
                td_mode = position['marginMode']
                params = {                    
                    'mgnMode': td_mode,
                    'posSide': pos_side,
                    # 当市价全平时，平仓单是否需要自动撤销,默认为false. false：不自动撤单 true：自动撤单
                    'autoCxl': 'true',
                    **params
            
                }

                # 发送平仓请求并获取返回值
                order = self.exchange.close_position(
                    symbol=symbol,
                    side=orderSide,
                    params=params
                )
                
                self.logger.info(f"{symbol} Close position response : {order}")
                return order
            
            except Exception as e:
                
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"{symbol} Error closing position : {str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)                
                else:
                    self.logger.warning(f"{symbol} 平仓失败，正在进行第{retry_count}次重试: {str(e)}")
                    time.sleep(0.1)  # 重试前等待0.1秒
                        
    def cancel_all_orders(self, symbol):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 获取所有未完成订单
                params = {
                    # 'instId': instId
                }
                open_orders = self.exchange.fetch_open_orders(symbol=symbol, params=params)
                
                # 批量取消所有订单
                if open_orders:
                    order_ids = [order['id'] for order in open_orders]
                    self.exchange.cancel_orders(order_ids, symbol, params=params)
                    
                    self.logger.debug(f"{symbol}: {order_ids} 挂单取消成功.")
                else:
                    self.logger.debug(f"{symbol}: 无挂单.")
                return True
                
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"{symbol} 取消挂单失败(重试{retry_count}次): {str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)                
                else:
                    self.logger.warning(f"{symbol} 取消挂单失败，正在进行第{retry_count}次重试: {str(e)}")
                    time.sleep(0.1)  # 重试前等待0.1秒

    def cancel_all_algo_orders(self, symbol, attachType=None) -> bool:
        """_summary_

        Args:
            symbol (_type_): _description_
            attachType (_type_, optional): "TP"|"SL". Defaults to None.
        """
        
        params = {
            "ordType": "conditional",
        }
        try:
            orders = self.fetch_open_orders(symbol=symbol,params=params)
        except Exception as e:
            error_message = f"!!{symbol} : Error fetching open orders: {e}"
            self.logger.error(error_message)
            raise Exception(error_message)
       
        
        if len(orders) == 0:           
            self.logger.debug(f"{symbol} 未设置策略订单列表。")
            return True
     
        algo_ids = []
        if attachType and attachType == 'SL':
            algo_ids = [order['id'] for order in orders if order['stopLossPrice'] and order['stopLossPrice'] > 0.0 ]
        elif attachType and attachType == 'TP':
            algo_ids = [order['id'] for order in orders if order['takeProfitPrice'] and order['takeProfitPrice'] > 0.0]
        else :
            algo_ids = [order['id'] for order in orders ]
            
        if len(algo_ids) == 0 :         
            self.logger.debug(f"{symbol} 未设置策略订单列表。")
            return True
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                params = {
                    "algoId": algo_ids,
                    "trigger": 'trigger'
                }
                rs = self.exchange.cancel_orders(ids=algo_ids, symbol=symbol, params=params)
                
                return len(rs) > 0
       
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"!!{symbol} : Error cancelling order {algo_ids}: {e}"
                    self.logger.error(error_message)
                    raise Exception(error_message) 
                   
                self.logger.warning(f"{symbol} : Error cancelling order {algo_ids}: {str(e)}")
                time.sleep(0.1)  # 重试前等待0.1秒 
    
    def place_algo_orders(self, symbol, position, price: Decimal, order_type, sl_or_tp='SL', params={}) -> bool:
        """
        下单
        Args:
            symbol: 交易对
            position: 仓位
            price: 下单价格
            order_type: 订单类型
        """
        # 计算下单数量
        amount = abs(position[self.CONTRACTS_KEY])
    
        if amount <= 0:
            self.logger.warning(f"{symbol}: amount is 0 for {symbol}")
            return

        # 止损单逻辑 
        adjusted_price = self.format_price(symbol, price)
        
        # 默认市价止损，委托价格为-1时，执行市价止损。
        sl_params = {
            **params,
            'slTriggerPx':adjusted_price , 
            'slOrdPx':'-1', # 委托价格为-1时，执行市价止损
            # 'slOrdPx' : adjusted_price,
            'slTriggerPxType':'last',
            'tdMode':position['marginMode'],
            'sz': str(amount),        
            'cxlOnClosePos': True,
            'reduceOnly':True,            
        }
        
        tp_params = {  
            **params,
            'tpTriggerPx':adjusted_price,
            'tpOrdPx' : adjusted_price,
            'tpOrdKind': 'condition',
            'tpTriggerPxType':'last',            
            'tdMode':position['marginMode'],
            'sz': str(amount),          
            'cxlOnClosePos': True,
            'reduceOnly':True
        }
        
        order_params = sl_params if sl_or_tp == 'SL' else tp_params
        # order_params.update(params)
        
        if order_type == 'limit' and sl_or_tp =='SL':
            order_params['slOrdPx'] = adjusted_price
        
        orderSide = self.BUY_SIDE if position[self.SIDE_KEY] == self.SHORT_KEY else self.SELL_SIDE # 和持仓反向相反下单
        
        order = {
            'symbol': symbol,
            'side': orderSide,
            'type': order_type,
            'amount': amount,
            'price': adjusted_price,
            'params': order_params
        }
        
        max_retries = 3
        retry_count = 0
        self.logger.info(f"{symbol} : Pre Algo Order placed:  {order} ")
        while retry_count < max_retries:
            try:
                # 创建订单
                order_result = self.exchange.create_order(**order)
                self.logger.info(f"{symbol} : --------- ++ Algo Order placed done. --------")
                return True
                
            except (ccxt.NetworkError, ccxt.ExchangeError, Exception) as e:
                retry_count += 1
                error_type = "网络" if isinstance(e, ccxt.NetworkError) else "交易所" if isinstance(e, ccxt.ExchangeError) else "未知"
                self.logger.warning(f"{symbol} : 设置止盈止损单时发生{error_type}错误,正在进行第{retry_count}次重试: {str(e)}")
                
                if retry_count == max_retries:
                    error_message = f"!! {symbol}: 设置止盈止损单失败(重试{max_retries}次): {str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)
                    
                time.sleep(0.1)
        
    def place_order(self, symbol, price: Decimal, amount_usdt, side, leverage=20, order_type='limit', params={}) -> bool: 
        """
        下单
        Args:
            symbol: 交易对
            price: 下单价格
            amount_usdt: 下单金额
            side: 下单方向
            order_type: 订单类型
        """       
        # 格式化价格
        adjusted_price = self.format_price(symbol, price)

        # 20250828 下单金额可以通过账户余额进行动态设置
        if amount_usdt <= 0:
            # self.logger.warning(f"{symbol}: amount_usdt must be greater than 0")
            # return
            accountBalance = self.fetch_balance()
            balance_free = accountBalance.free
            if balance_free <= 0:
                self.logger.warning(f"{symbol}: account balance is 0.")
                return False

            amount_usdt = balance_free * leverage / 2
            self.logger.info(f"{symbol}: amount_usdt = {amount_usdt}")
            self.logger.info(f"{symbol}: calculate amount_usdt by account balance. free={balance_free} leverage={leverage} amount_usdt = {amount_usdt} ")


    
        pos_side = self.LONG_KEY if side == self.BUY_SIDE else self.SHORT_KEY

        # 设置杠杆 
        self.set_leverage(symbol=symbol, leverage=leverage, mgnMode='isolated',posSide=pos_side)  
        # 20250220 SWAP类型计算合约数量 
        contract_size = self.convert_contract(symbol=symbol, price = OPTools.toDecimal(adjusted_price) ,amount=amount_usdt)

        if OPTools.toDecimal(contract_size) <= 0:
            self.logger.warning(f"{symbol}: contract_size is 0 by {amount_usdt}")
            return False

        order_params = {
            **params,
            "tdMode": 'isolated',
            "side": side,
            "ordType": order_type,
            "sz": contract_size,
            "px": adjusted_price
        } 
        
        # # 模拟盘(demo_trading)需要 posSide
        # if self.is_demo_trading == 1 :
        #     params["posSide"] = pos_side
            
        order = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'amount': contract_size,
            'price': adjusted_price,
            'params': order_params
        }
        
        max_retries = 3
        retry_count = 0

        self.logger.info(f"{symbol} : Pre Order placed:  {order} ")
        
        while retry_count < max_retries:
            try:
                # 使用ccxt创建订单
                order_result = self.exchange.create_order(**order)
                self.logger.info(f"{symbol} : --------- ++ Order placed done. --------")  
                return True
            except (ccxt.NetworkError, ccxt.ExchangeError, Exception) as e:
                retry_count += 1
                error_type = "网络" if isinstance(e, ccxt.NetworkError) else "交易所" if isinstance(e, ccxt.ExchangeError) else "未知"
                self.logger.warning(f"{symbol} : 下单时发生{error_type}错误,正在进行第{retry_count}次重试: {str(e)}")
                if retry_count == max_retries:
                    error_message = f"!! {symbol}: 下单时重试{max_retries}次后仍未成功：{str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)
                time.sleep(1)
      
    def fetch_position(self, symbol):
        """_summary_

        Args:
            symbol (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                position = self.exchange.fetch_position(symbol=symbol)
                if position :
                    # self.logger.debug(f"{symbol} 有持仓合约数: {position['contracts']}")
                    return position
                return None
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"!!{symbol} 获取持仓失败(重试{retry_count}次): {str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)
                   
                self.logger.warning(f"{symbol} 检查持仓失败，正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)  # 重试前等待0.1秒
    
    def fetch_positions(self):
        """_summary_
        Returns:
            _type_: _description_
        """
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                positions = self.exchange.fetch_positions()
                return positions
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"!! 获取持仓列表失败(重试{retry_count}次): {str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)

                self.logger.warning(f"获取持仓列表失败，正在进行第{retry_count}次重试: {str(e)}")
                time.sleep(0.1)  # 重试前等待0.1秒
    
    def fetch_open_orders(self,symbol,params={}):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                orders = self.exchange.fetch_open_orders(symbol=symbol,params=params)
                return orders
            
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"{symbol} : fetching open orders(retry {retry_count} times): {str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)
                   
                self.logger.warning(f"{symbol} : Error fetching open orders: {str(e)}")
                time.sleep(0.1)  # 重试前等待0.1秒     
    
    def get_market_price(self, symbol) -> Decimal:
        """
        获取最新价格
        Args:
            symbol: 交易对
        """
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                if ticker and 'last' in ticker:
                    return OPTools.toDecimal(ticker['last'])
                else:
                    raise Exception(f"{symbol} : Unexpected response structure or missing 'last' price")
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"{symbol} 获取最新价格失败(重试{retry_count}次): {str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)
            
    def get_historical_klines(self, symbol, bar='15m', limit=300, after:str=None, params={}):
        """
        获取历史K线数据
        Args:
            symbol: 交易对
            bar: K线周期
            limit: 数据条数
            after: 之后时间，格式为 "2025-05-21 23:00:00+08:00"
        """
           
        params = {
            **params,
            # 'instId': instId,
        }
        since = None
        if after:
            since = self.exchange.parse8601(after)
            limit = None
            if since:
                params['paginate'] = True
            
        klines = self.exchange.fetch_ohlcv(symbol, timeframe=bar,since=since, limit=limit, params=params)
        # if 'data' in response and len(response['data']) > 0:
        if klines :
            # return response['data']
            return klines
        else:
            raise Exception(f"{symbol} : Unexpected response structure or missing candlestick data")
        
    def get_historical_klines_df(self, symbol, bar='15m', limit=300, after:str=None, params={}) -> pd.DataFrame:
        klines = self.get_historical_klines(symbol, bar=bar, limit=limit, after=after, params=params)
        return self.format_klines(klines)

    def format_klines(self, klines) -> pd.DataFrame:       
        """_summary_
            格式化K线数据
        Args:
            klines (_type_): _description_
        """
        klines_df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']) 
        # 转换时间戳为日期时间
        klines_df['timestamp'] = pd.to_datetime(klines_df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
  
        return klines_df

    def fetch_balance(self, currency:str="USDT", marketType:str="futures", params={}) -> AccountBalance:
        """_summary_
        Args:
            currency (str, optional): _description_. Defaults to "USDT".
            marketType (str, optional): _description_. Defaults to "futures".
            params (dict, optional): _description_. Defaults to {}.
        Returns:
            AccountBalance: _description_
        """
        max_retries = 3
        retry_count = 0

        params = {
            **params,
            'type': marketType,
            'ccy': currency
                
            }

        while retry_count < max_retries:
            try:
                ccxt_balance = self.exchange.fetch_balance(params)
                balance = AccountBalance.build_from_ccxt(ccxt_balance, currency)
                return balance
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_message = f"!! 获取{marketType} {currency}余额失败(重试{retry_count}次): {str(e)}"
                    self.logger.error(error_message)
                    raise Exception(error_message)