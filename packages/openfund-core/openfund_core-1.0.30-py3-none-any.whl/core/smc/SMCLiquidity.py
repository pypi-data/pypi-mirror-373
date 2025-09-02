import logging
from decimal import Decimal
from core.smc.SMCStruct import SMCStruct


class SMCLiquidity(SMCStruct):
    EQUAL_HIGH_COL = "equal_high"
    EQUAL_LOW_COL = "equal_low"
    LIQU_HIGH_COL = "liqu_high"
    LIQU_LOW_COL = "liqu_low"
    EQUAL_HIGH_INDEX_KEY = "equal_high_index"
    EQUAL_LOW_INDEX_KEY = "equal_low_index"
    HAS_EQ_KEY = "has_EQ"
    LIQU_HIGH_DIFF_COL = "liqu_high_diff"
    LIQU_LOW_DIFF_COL = "liqu_low_diff"


    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        
    def _identify_liquidity_pivots(self, data, pivot_length=1):
        """
        识别流动性的高点和低点
        """

        df = data.copy()
        
        # 识别高点
        df[self.LIQU_HIGH_COL] = Decimal(0.0)
        for i in range(pivot_length, len(df) - pivot_length):
            if df[self.HIGH_COL].iloc[i] == max(df[self.HIGH_COL].iloc[i-pivot_length:i+pivot_length+1]):
                df.loc[df.index[i], self.LIQU_HIGH_COL] = df[self.HIGH_COL].iloc[i]        
        # 识别低点
        df[self.LIQU_LOW_COL] = Decimal(0.0)
        for i in range(pivot_length, len(df) - pivot_length):

            if df[self.LOW_COL].iloc[i] == min(df[self.LOW_COL].iloc[i-pivot_length:i+pivot_length+1]):
                df.loc[df.index[i], self.LIQU_LOW_COL] = df[self.LOW_COL].iloc[i]

        return df
        
    def find_EQH_EQL(self, data, trend, end_idx=-1, atr_offset=0.1) -> dict:
        """_summary_
        识别等高等低流动性
        Args:
            data (_type_): _description_
            trend (_type_): _description_
            end_idx (int, optional): _description_. Defaults to -1.
            atr_offset (float, optional): _description_. Defaults to 0.1.

        Returns:
            dict: _description_
        """
        
        df = data.copy() if end_idx == -1 else data.copy().iloc[:end_idx+1]

        check_columns = [self.LIQU_HIGH_COL, self.LIQU_LOW_COL]

        try:
            self.check_columns(df, check_columns) 
        except ValueError as e:
            # self.logger.warning(f"DataFrame must contain columns {check_columns} : {str(e)}")
            df = self._identify_liquidity_pivots(df)
            
        df = df[(df[self.LIQU_HIGH_COL] > 0) | (df[self.LIQU_LOW_COL] > 0)]
        # 初始化结果列
        df[self.EQUAL_HIGH_COL] = 0
        df[self.EQUAL_LOW_COL] = 0 
        df[self.ATR_COL] = self.calculate_atr(df)
        # 跟踪前一个高点和低点
        previous_high = None
        previous_high_index = None
        previous_high_pos = -1
        previous_low = None
        previous_low_index = None  
        previous_low_pos = -1   
        for i in range(len(df)-1, -1, -1):

            offset = self.toDecimal(df[self.ATR_COL].iloc[i] * atr_offset)

            if trend == self.BULLISH_TREND:
                current_high = df[self.LIQU_HIGH_COL].iloc[i]
                if current_high == 0:
                    continue
        
                if previous_high is None:
                    previous_high = current_high
                    previous_high_index = df.index[i]
                    previous_high_pos = i
                    continue
                
                max_val = max(current_high, previous_high)
                min_val = min(current_high, previous_high)
                
                
                if abs(max_val - min_val) <= offset: # EQH|EQL
            
                    df.loc[df.index[i], self.EQUAL_HIGH_COL] = previous_high_index
                    df.loc[df.index[previous_high_pos], self.EQUAL_HIGH_COL] = previous_high_index
                        
                else:
                    # 倒序遍历，等高线被高点破坏，则更新等高点位置
                    if current_high > previous_high:
                        previous_high = current_high
                        previous_high_index = df.index[i]
                        previous_high_pos = i



            else:
                current_low = df[self.LIQU_LOW_COL].iloc[i]
                if current_low == 0:
                    continue
        
                # current_low = df[self.EQUAL_LOW_COL].iloc[i]
                if previous_low is None:
                    previous_low = current_low
                    previous_low_index = df.index[i]
                    previous_low_pos = i
                    continue
                
                max_val = max(current_low, previous_low)
                min_val = min(current_low, previous_low)
                
                

                
                if abs(max_val - min_val) <= offset: # EQH|EQL
            
                    df.loc[df.index[i], self.EQUAL_LOW_COL] = previous_low_index
                    df.loc[df.index[previous_low_pos], self.EQUAL_LOW_COL] = previous_low_index
                        
                else:
                    # 倒序遍历，等高线被高点破坏，则更新等高点位置
                    if current_low < previous_low:
                        previous_low = current_low
                        previous_low_index = df.index[i]
                        previous_low_pos = i
                
        # 筛选有效结构且在prd范围内的数据
        last_EQ = {

        }
        if trend == self.BULLISH_TREND :
            mask = df[self.EQUAL_HIGH_COL] > 0
            valid_EQH_df = df[ mask ]
            if not valid_EQH_df.empty:
                last_EQ[self.HAS_EQ_KEY] = True
                last_EQ[self.EQUAL_HIGH_COL] = valid_EQH_df.iloc[-1][self.LIQU_HIGH_COL]
                last_EQ[self.EQUAL_HIGH_INDEX_KEY] = valid_EQH_df.iloc[-1][self.EQUAL_HIGH_COL]
        else:
            mask = df[self.EQUAL_LOW_COL] > 0
            valid_EQL_df = df[ mask ]
            if not valid_EQL_df.empty:
                last_EQ[self.HAS_EQ_KEY] = True
                last_EQ[self.EQUAL_LOW_COL] = valid_EQL_df.iloc[-1][self.LIQU_LOW_COL]
                last_EQ[self.EQUAL_LOW_INDEX_KEY] = valid_EQL_df.iloc[-1][self.EQUAL_LOW_COL]

        return last_EQ
               
    def identify_dynamic_trendlines(self, data, trend, start_idx=-1, end_idx=-1, ratio=0.8) -> tuple:
        """
        识别动态趋势线或隧道
        Args:
            data (pd.DataFrame): _description_

        Returns:
            pd.DataFrame: _description_
        """          

        df = data.copy() if start_idx == -1 or end_idx == -1 else data.copy().iloc[start_idx-1:end_idx+2] #考虑poivt值，前后各增加一个

        check_columns = [self.LIQU_HIGH_COL]

        try:
            self.check_columns(df, check_columns) 
        except ValueError as e:
            self.logger.warning(f"DataFrame must contain columns {check_columns} : {str(e)}")
            df = self._identify_liquidity_pivots(df)
        diff_ratio = 0.0
        if trend == self.BEARISH_TREND:
            # 判断Bearish趋势是高点不断升高,
            liqu_bear_df = df[df[self.LIQU_HIGH_COL] > 0]
            liqu_bear_df[self.LIQU_HIGH_DIFF_COL] = liqu_bear_df[self.LIQU_HIGH_COL].diff()
            # self.logger.info(f"dynamic_trendlines:\n {liqu_bear_df[[self.TIMESTAMP_COL,self.LIQU_HIGH_COL,self.LIQU_HIGH_DIFF_COL]]}")
            diff_ratio = self.toDecimal(liqu_bear_df[self.LIQU_HIGH_DIFF_COL].dropna().lt(0).mean(),2)
            if diff_ratio >= ratio:
               return diff_ratio,True
        else:
            # Bullish趋势是低点不断降低
            liqu_bullish_df = df[df[self.LIQU_LOW_COL] > 0]
            liqu_bullish_df[self.LIQU_LOW_DIFF_COL] = liqu_bullish_df[self.LIQU_LOW_COL].diff()
            # self.logger.info(f"dynamic_trendlines:\n {liqu_bullish_df[[self.TIMESTAMP_COL,self.LIQU_LOW_COL,self.LIQU_LOW_DIFF_COL]]}")
            diff_ratio = self.toDecimal(liqu_bullish_df[self.LIQU_LOW_DIFF_COL].dropna().gt(0).mean(),2)
            if diff_ratio >= ratio:
               return diff_ratio,True

        return diff_ratio,False


        

