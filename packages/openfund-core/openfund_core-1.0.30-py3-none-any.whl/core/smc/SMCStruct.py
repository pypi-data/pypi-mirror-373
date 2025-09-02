import logging
import operator
from core.utils.OPTools import OPTools
from core.smc.SMCBase import SMCBase


class SMCStruct(SMCBase):
    BULLISH_TREND = 'Bullish'
    BEARISH_TREND = 'Bearish'
    STRUCT_COL = "struct"
    STRUCT_HIGH_COL = "struct_high"
    STRUCT_LOW_COL = "struct_low"
    STRUCT_MID_COL = "struct_mid"
    STRUCT_HIGH_INDEX_COL = "struct_high_index"
    STRUCT_LOW_INDEX_COL = "struct_low_index"
    STRUCT_DIRECTION_COL = "struct_direction"
    HIGH_START_COL = "high_start"
    LOW_START_COL = "low_start"
    DIRECTION_COL = "direction"

    def __init__(self):  
        super().__init__()
        self.logger = logging.getLogger(__name__)
      
   
    def build_struct(self, data, tf=None, is_struct_body_break=True):
        """处理价格结构,识别高低点突破和结构方向
        
        Args:
            data: 数据框
            tf: 时间周期
            window: 寻找结构极值的窗口大小
            is_struct_body_break: 是否使用收盘价判断突破
            
        Returns:
            处理后的数据框,包含结构相关列
        """
        # 复制数据并去掉最后一条记录，因为最后一条记录不是完成状态的K线
        # 根据时间周期处理数据框
        df = data.copy()
        if tf == '1m':
            df = df.iloc[:-1]  # 1分钟周期去掉最后一条未完成的K线
            
            
        check_columns = [self.HIGH_COL, self.LOW_COL, self.CLOSE_COL]
        self.check_columns(df, check_columns)
        
        # 初始化结构相关列
        # 定义结构相关的列名
        struct_columns = [self.STRUCT_COL, self.STRUCT_HIGH_COL, self.STRUCT_LOW_COL, 
                         self.STRUCT_HIGH_INDEX_COL, self.STRUCT_LOW_INDEX_COL, self.STRUCT_DIRECTION_COL, self.DIRECTION_COL]
        
        # 初始化结构相关列的默认值
        default_values = {
            self.STRUCT_COL: None,  # 结构类型列初始化为None
            self.STRUCT_HIGH_COL: self.toDecimal('0.0'),  # 结构高点价格初始化为0
            self.STRUCT_LOW_COL: self.toDecimal('0.0'),  # 结构低点价格初始化为0
            self.STRUCT_HIGH_INDEX_COL: 0,  # 结构高点索引初始化为0 
            self.STRUCT_LOW_INDEX_COL: 0,  # 结构低点索引初始化为0
            self.STRUCT_DIRECTION_COL: None,  # 结构方向初始化为0
            self.DIRECTION_COL: 0  # 结构方向初始化为0
        }
        
        # 为每个结构列赋默认值
        for col in struct_columns:
            df[col] = default_values[col]
            
        # 初始化结构变量
        structure = {
            self.HIGH_COL: df[self.HIGH_COL].iloc[0],
            self.LOW_COL: df[self.LOW_COL].iloc[0],
            self.HIGH_START_COL: -1,
            self.LOW_START_COL: -1,
            self.DIRECTION_COL: 0
        }

        # 确定突破判断列
        break_price_col = self.CLOSE_COL if is_struct_body_break else self.HIGH_COL
        break_price_col_low = self.CLOSE_COL if is_struct_body_break else self.LOW_COL
        structLabelNo = 0

        for i in range(1, len(df)):
            curr_prices = {
                self.HIGH_COL: self.toDecimal(df[break_price_col].iloc[i]),
                self.LOW_COL: self.toDecimal(df[break_price_col_low].iloc[i])
            }
            
            # # 获取前3根K线价格
            # prev_prices = {
            #     self.HIGH_COL: df[break_price_col].iloc[i-3:i].values,
            #     self.LOW_COL: df[break_price_col_low].iloc[i-3:i].values
            # }

            # 判断结构突破
            is_high_broken = self._check_structure_break(
                curr_price=curr_prices[self.HIGH_COL],
                struct_price=structure[self.HIGH_COL],
                df = df,
                struct_start = structure[self.HIGH_START_COL],
                mode=self.HIGH_COL
            )

 
            is_low_broken = self._check_structure_break(
                curr_price=curr_prices[self.LOW_COL],
                struct_price=structure[self.LOW_COL],
                df = df,
                struct_start = structure[self.LOW_START_COL],
                mode=self.LOW_COL
            )
  
            # 处理低点突破
            if is_low_broken:
                extreme_idx = self._get_structure_extreme_bar(
                    df, i, 
                    struct_index=structure[self.LOW_START_COL],
                    mode=self.HIGH_COL
                )
                
                if extreme_idx != 0:
                    struct_type = 'SMS' if structure[self.DIRECTION_COL] == 1 else 'CHOCH'
                     # 使用字典优化结构类型判断逻辑
                    if struct_type == 'CHOCH':
                        structLabelNo = 0
                    else:  # struct_type == 'SMS'
                        if structLabelNo == 0:
                            structLabelNo = 1
                        elif structLabelNo == 1:
                            struct_type = 'BOS'
                    structure = self._handle_structure_break(
                        df, i, structure,
                        break_type=self.LOW_COL,
                        struct_type=struct_type,
                        extreme_idx=extreme_idx
                    )
                else:
                    is_low_broken = False

            # 处理高点突破    
            if is_high_broken :
                extreme_idx = self._get_structure_extreme_bar(
                    df, i,
                    struct_index=structure[self.HIGH_START_COL],
                    mode=self.LOW_COL
                )
                
                if extreme_idx != 0:
                    # 根据方向判断结构类型
                    struct_type = 'SMS' if structure[self.DIRECTION_COL] == 2 else 'CHOCH'
                    
                    # 使用字典优化结构类型判断逻辑
                    if struct_type == 'CHOCH':
                        structLabelNo = 0
                    else:  # struct_type == 'SMS'
                        if structLabelNo == 0:
                            structLabelNo = 1
                        elif structLabelNo == 1:
                            struct_type = 'BOS'

                    structure = self._handle_structure_break(
                        df, i, structure, 
                        break_type=self.HIGH_COL,
                        struct_type=struct_type,
                        extreme_idx=extreme_idx
                    )
                else:
                    is_high_broken = False

            # 如果没有突破发生，更新当前结构
            if not any([is_low_broken, is_high_broken]):
                structure = self._update_current_structure(
                    df, i, structure,
                    is_struct_body_break=is_struct_body_break
                )
            
            # 更新数据框结构列
            self._update_structure_columns(df, i, structure)

        return df

    def _get_structure_extreme_bar(self, df, bar_index,  struct_index, mode='high'):
        """
        获取结构最高点或最低点
        :param df: DataFrame数据
        :param bar_index: 当前K线索引
        :param struct_index: 结构开始索引
        :param mode: high 寻找最高点,low 寻找最低点
        :return: 结构极值点的索引
        """
        df = df.copy()
        window_start = max(0, struct_index)
        
        window = df.iloc[window_start : bar_index + 1]
 
        
        # 获取窗口内的极值点索引
        if mode == self.HIGH_COL:
            # extremeBar = window[self.HIGH_COL].argmax() 
            extremeBar = window[self.HIGH_COL].idxmax() 
            price_col = self.HIGH_COL
            comp_func = lambda x, y: x > y
        else:
            # extremeBar = window[self.LOW_COL].argmin() 
            extremeBar = window[self.LOW_COL].idxmin() 
            price_col = self.LOW_COL
            comp_func = lambda x, y: x < y

        # 初始化记录点
        pivot = 0
        # 从后向前遍历寻找结构极值点
        # for i in range(lookback - 1, -1, -1):
        for idx in range(bar_index, struct_index, -1):
            # 计算当前位置的索引
            # idx = bar_index - i
            if idx < 2:
                continue
                
            price_prev = df[price_col].iloc[idx - 1]
            price_prev2 = df[price_col].iloc[idx - 2]
            price_curr = df[price_col].iloc[idx]
            
            # 记录满足条件的点位
            if (comp_func(price_prev, price_prev2) and
                not comp_func(price_curr, price_prev) 
                and idx - 1 >= extremeBar
                ):
                if pivot == 0:
                    pivot = idx - 1
                    continue
                else:                   
                    # 比较当前点位与之前记录的极值点的价格,因为在区间内有多个极致点，需要比较
                    if comp_func(df[price_col].iloc[idx-1], df[price_col].iloc[pivot]):
                        pivot = idx - 1
                
        return pivot

    def _check_structure_break(self, curr_price, struct_price, df, struct_start, mode='high'):
        """检查结构是否突破"""
        comp = operator.gt if mode == self.HIGH_COL else operator.lt
        # reverse_comp = operator.le if mode == self.HIGH_COL else operator.ge
        
        # basic_break = (
        #     comp(curr_price, struct_price) and
        #     all(reverse_comp(p, struct_price) for p in prev_prices) and
        #     all(i-j > struct_start for j in range(1,4))
        # )
        
        direction_break = comp(curr_price, struct_price)


        # 判断 是否是
        extreme_idx = self._get_structure_extreme_bar(
            df, bar_index=struct_start+1,
            struct_index=struct_start,
            mode=mode
        )

        is_extreme = extreme_idx != 0
        
        return direction_break and is_extreme

    def _handle_structure_break(self, df, i, structure, break_type, struct_type, extreme_idx ):
        """处理结构突破"""
        is_high_break = break_type == self.HIGH_COL

        # 更新结构信息
        new_structure = structure.copy()
        new_structure[self.DIRECTION_COL] = 2 if is_high_break else 1
        
        if is_high_break:
            new_structure.update({
                self.LOW_COL: self.toDecimal(df[self.LOW_COL].iloc[extreme_idx]),
                self.HIGH_COL: self.toDecimal(df[self.HIGH_COL].iloc[i]),
                self.LOW_START_COL: extreme_idx,
                self.HIGH_START_COL: i
            })
        else:
            new_structure.update({
                self.HIGH_COL: self.toDecimal(df[self.HIGH_COL].iloc[extreme_idx]),
                self.LOW_COL: self.toDecimal(df[self.LOW_COL].iloc[i]),
                self.HIGH_START_COL: extreme_idx,
                self.LOW_START_COL: i
            })
            
        # 更新DataFrame结构信息
        # df.at[i, self.STRUCT_DIRECTION_COL] = new_structure[self.DIRECTION_COL] 

        df.at[i, self.STRUCT_DIRECTION_COL] = self.BULLISH_TREND if is_high_break else self.BEARISH_TREND
        df.at[i, self.STRUCT_COL] = f"{self.BULLISH_TREND if is_high_break else self.BEARISH_TREND}_{struct_type}"
        
        return new_structure

    def _update_current_structure(self, df, i, structure, is_struct_body_break):
        """更新当前结构"""
        new_structure = structure.copy()
        
        # 检查是否需要更新高点
        if (structure[self.DIRECTION_COL] in (2,0)) and self.toDecimal(df.at[i,self.HIGH_COL]) > structure[self.HIGH_COL]:
            # if not (is_struct_body_break and all(i-j > structure[self.HIGH_START_COL] for j in range(1,4))):
            new_structure[self.HIGH_COL] = df.at[i,self.HIGH_COL]
            new_structure[self.HIGH_START_COL] = i
                
        # 检查是否需要更新低点
        elif (structure[self.DIRECTION_COL] in (1,0)) and self.toDecimal(df.at[i,self.LOW_COL]) < structure[self.LOW_COL]:
            # if not (is_struct_body_break and all(i-j > structure[self.LOW_START_COL] for j in range(1,4))):
            new_structure[self.LOW_COL] = df.at[i,self.LOW_COL]
            new_structure[self.LOW_START_COL] = i
                
        return new_structure

    def _update_structure_columns(self, df, i, structure):
        """更新数据框中的结构列"""
        df.at[i, self.STRUCT_HIGH_COL] = self.toDecimal(structure[self.HIGH_COL])
        df.at[i, self.STRUCT_LOW_COL] = self.toDecimal(structure[self.LOW_COL] )
        df.at[i, self.STRUCT_HIGH_INDEX_COL] = structure[self.HIGH_START_COL]
        df.at[i, self.STRUCT_LOW_INDEX_COL] = structure[self.LOW_START_COL]
        df.at[i, self.DIRECTION_COL] = structure[self.DIRECTION_COL]

    def get_latest_struct(self, df, is_struct_body_break=True):
        """
        获取最新的结构
        """
        check_columns = [self.STRUCT_COL]
        # if not self.check_columns(df, check_columns):
        try :
            self.check_columns(df, check_columns)
        except ValueError as e:
            df = self.build_struct(df, is_struct_body_break=is_struct_body_break)
 
        data = df.copy()
       
        # 筛选有效结构且在prd范围内的数据
        last_struct = None
        mask = data[self.STRUCT_COL].notna()
        valid_structs = data[ mask ]
        if not valid_structs.empty:
            # 获取最近的结构
            last_struct = valid_structs.iloc[-1]
            return {
                self.STRUCT_COL: last_struct[self.STRUCT_COL],
                self.STRUCT_HIGH_COL: last_struct[self.STRUCT_HIGH_COL],
                self.STRUCT_LOW_COL: last_struct[self.STRUCT_LOW_COL], 
                self.STRUCT_MID_COL: (last_struct[self.STRUCT_HIGH_COL] + last_struct[self.STRUCT_LOW_COL]) / 2,
                self.STRUCT_HIGH_INDEX_COL: last_struct[self.STRUCT_HIGH_INDEX_COL],
                self.STRUCT_LOW_INDEX_COL: last_struct[self.STRUCT_LOW_INDEX_COL],
                self.STRUCT_DIRECTION_COL: last_struct[self.STRUCT_DIRECTION_COL]
            }

        return last_struct

