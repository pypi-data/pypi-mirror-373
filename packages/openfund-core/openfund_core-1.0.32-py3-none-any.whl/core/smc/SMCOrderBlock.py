import logging
from token import OP
import pandas as pd

from core.smc.SMCStruct import SMCStruct


class SMCOrderBlock(SMCStruct):
    OB_HIGH_COL = "ob_high"
    OB_LOW_COL = "ob_low"
    OB_MID_COL = "ob_mid"
    OB_VOLUME_COL = "ob_volume"
    OB_DIRECTION_COL = "ob_direction"  # 1: 向上突破, 2: 向下突破
    # OB_START_INDEX_COL = "ob_start_index"
    # OB_START_TS_COL = "ob_start_ts"
    OB_ATR = "ob_atr"
    OB_IS_COMBINED = "ob_is_combined"
    OB_WAS_CROSSED = "ob_was_crossed"

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def find_OBs(
        self,
        struct: pd.DataFrame,
        side=None,
        start_index: int = -1,
        is_valid: bool = True,
        if_combine: bool = True,
        is_struct_body_break: bool = True,
        atr_multiplier: float = 0.6,
    ) -> pd.DataFrame:
        """_summary_

        Args:
            symbol (_type_): _description_
            data (pd.DataFrame): _description_
            side (_type_): _description_ 如果是None, 则返回所有OB boxes（包括bullish和bearish）
            start_index (int): _description_ 开始的位置
            is_valid (bool): _description_ 找到有效的OB，没有被crossed
            if_combine (bool): _description_ 是否合并OB
        Returns:
            list: _description_
        """

        df = struct.copy() if start_index == -1 else struct.copy().iloc[start_index:]
        if self.OB_DIRECTION_COL not in df.columns:
            df = self.build_struct_for_ob(df, is_struct_body_break, atr_multiplier)

        # 获取有效的OB数据
        ob_df = df[df[self.OB_DIRECTION_COL].notna()]

        # 根据side过滤并生成OB
        if side is not None:
            direction = "Bullish" if side == self.BUY_SIDE else "Bearish"
            ob_df = ob_df[ob_df[self.OB_DIRECTION_COL] == direction]

        # 检查OB是否被平衡过
        ob_df = ob_df.copy() 
        ob_df.loc[:, self.OB_WAS_CROSSED] = ob_df.apply(
            lambda row: any(
                df.loc[row.name + 1 :, self.LOW_COL] <= row[self.OB_LOW_COL]
            )
            if row[self.OB_DIRECTION_COL] == "Bullish"
            else any(df.loc[row.name + 1 :, self.HIGH_COL] >= row[self.OB_HIGH_COL]),
            axis=1,
        )
        if is_valid :
            ob_df = ob_df[~ob_df[self.OB_WAS_CROSSED]]      

        if if_combine:
            # 合并OB
            ob_df = self._combineOB(ob_df)
            
        # 过滤掉已经被合并的OB
        ob_df = ob_df[ob_df[self.OB_IS_COMBINED] != 1]

        return ob_df

    def build_struct_for_ob(
        self, df, is_struct_body_break=True, atr_multiplier=0.6
    ):
        """
        构建结构并检测Order Block

        Args:
            df: 数据框
            window: 寻找结构极值的窗口大小
            is_struct_body_break: 是否使用收盘价判断突破
            ob_length: 搜索Order Block的回溯长度
            atr_multiplier: ATR倍数阈值

        Returns:
            处理后的数据框,包含结构和Order Block相关列
        """
  

        check_columns = [self.HIGH_COL, self.LOW_COL, self.CLOSE_COL]
        self.check_columns(df, check_columns)
        
        check_struct_columns = [self.STRUCT_COL]
       
        try:
             self.check_columns(df, check_struct_columns)
        except ValueError as e:
                 # 首先构建基础结构
            df = self.build_struct(df, is_struct_body_break=is_struct_body_break)           

        # 初始化OB相关列
        ob_columns = [
            self.OB_HIGH_COL,
            self.OB_LOW_COL,
            self.OB_MID_COL,
            self.OB_VOLUME_COL,
            self.OB_DIRECTION_COL,
            # self.OB_START_INDEX_COL,
            # self.OB_START_TS_COL,
            self.OB_ATR,
        ]
        for col in ob_columns:
            df[col] = None

        # 计算ATR用于阈值判断
        df[self.ATR_COL] = self._calculate_atr(df)

        # 检测Order Block
        for i in range(1, len(df)):
            # 检查是否为结构高点突破
            if df.at[i, self.STRUCT_COL] and "Bullish" in df.at[i, self.STRUCT_COL]:
                self._find_ob(df, i, atr_multiplier)

            # 检查是否为结构低点突破
            elif df.at[i, self.STRUCT_COL] and "Bearish" in df.at[i, self.STRUCT_COL]:
                self._find_ob(df, i, atr_multiplier, is_bullish=False)

        return df

    def _combineOB(self, df_OBs, combine_atr_muiltiplier=0.2):
        """
        合并OB
        """

        df_ob = df_OBs.copy()
        # 初始化 OB_IS_COMBINED 列为 0
        df_ob[self.OB_IS_COMBINED] = 0

        combine_atr_muiltiplier = self.toDecimal(combine_atr_muiltiplier)
        # 遍历所有OB，检查是否需要合并
        for i in range(len(df_ob)):
            # 如果当前OB已被合并，跳过
            if df_ob.iloc[i][self.OB_IS_COMBINED] == 1:
                continue

            current_direction = df_ob.iloc[i][self.OB_DIRECTION_COL]
            current_mid = df_ob.iloc[i][self.OB_MID_COL]
            current_atr = df_ob.iloc[i][self.OB_ATR]

            # 检查后续的OB
            for j in range(i + 1, len(df_ob)):
                # 如果后续OB已被合并，跳过
                if df_ob.iloc[j][self.OB_IS_COMBINED] == 1:
                    continue

                # 如果方向相同且中间价差值小于阈值，标记为已合并
                if (
                    df_ob.iloc[j][self.OB_DIRECTION_COL] == current_direction
                    and abs(df_ob.iloc[j][self.OB_MID_COL] - current_mid)
                    < current_atr * combine_atr_muiltiplier
                ):
                    df_ob.iloc[i, df_ob.columns.get_loc(self.OB_IS_COMBINED)] = 1
                    break
        # 遍历所有的OB

        return df_ob

    def _calculate_atr(self, df, period=200, multiplier=2):
        return super().calculate_atr(df, period, multiplier)

    def _find_ob(self, df, i, atr_multiplier, is_bullish=True):
        """寻找Order Block
        Args:
            df: 数据框
            i: 当前索引
            atr_multiplier: ATR乘数
            is_bullish: 是否为看涨OB,True为看涨,False为看跌
        """
        # 根据方向获取相应的结构索引和价格，OB是取结构开始的最高价或最低价的K线
        if is_bullish:
            index = df.loc[i, self.STRUCT_LOW_INDEX_COL]
            extreme_price = df.loc[i, self.STRUCT_LOW_COL]

            # Oper_func = min
            src = self.toDecimal(df.loc[index, self.HIGH_COL])
            direction = "Bullish"

        else:
            index = df.loc[i, self.STRUCT_HIGH_INDEX_COL]
            extreme_price = df.loc[i, self.STRUCT_HIGH_COL]
            # Oper_func = max
            src = self.toDecimal(df.loc[index, self.LOW_COL])
            direction = "Bearish"

        # 计算累积成交量
        vol = df.loc[index:i, self.VOLUME_COL].sum()

        # 应用ATR阈值，如果OB的范围小于ATR(=20)的60%（20*0.6=12），则把OB可扩展到ATR(=20)范围。
        precision = self.get_precision_length(extreme_price)
        atr = self.toDecimal(df.loc[i, self.ATR_COL])
        atr_multiplier = self.toDecimal(atr_multiplier)
        if is_bullish:
            # 计算当前区间大小
            current_range = src - extreme_price
            target_range = atr
            if current_range < atr * atr_multiplier:
                # 如果区间过小，将区间扩展到目标大小，并在中心点两侧平均分配
                extend_amount = (target_range - current_range) / 2
                src += extend_amount
                extreme_price -= extend_amount

            high, low = (
                self.toDecimal(src, precision),
                self.toDecimal(extreme_price, precision),
            )
        else:
            # 计算当前区间大小
            current_range = extreme_price - src
            target_range = atr
            if current_range < atr * atr_multiplier:
                # 如果区间过小，将区间扩展到目标大小，并在中心点两侧平均分配
                extend_amount = (target_range - current_range) / 2
                src -= extend_amount
                extreme_price += extend_amount

            high, low = (
                self.toDecimal(extreme_price, precision),
                self.toDecimal(src, precision),
            )

        # 计算中间值
        mid = (high + low) / 2

        # 更新OB信息到DataFrame
        df.at[index, self.OB_HIGH_COL] = self.toDecimal(high)
        df.at[index, self.OB_LOW_COL] = self.toDecimal(low)
        df.at[index, self.OB_MID_COL] = self.toDecimal(mid)
        df.at[index, self.OB_VOLUME_COL] = vol
        df.at[index, self.OB_DIRECTION_COL] = direction
        # df.at[i, self.OB_START_INDEX_COL] = index
        # df.at[i, self.OB_START_TS_COL] = df.loc[index, self.TIMESTAMP_COL]
        df.at[index, self.OB_ATR] = atr

    def get_latest_OB(self, data, trend, start_index=-1):
        """
        获取最新的Order Block

        Args:
            df: 数据框
            trend: 趋势，"Bullish" 或 "Bearish"

        Returns:
            最新的Order Block信息或None
        """
        # 获取prd范围内的数据
        df = (
            data.copy()
            if start_index == -1
            else data.copy().iloc[start_index :]
        )

        # 检查数据中是否包含必要的列
        check_columns = [self.OB_DIRECTION_COL]
        self.check_columns(df, check_columns)

        # 筛选有效OB且在prd范围内的数据
        mask = df[self.OB_DIRECTION_COL] == trend
        valid_obs = df[mask]

        if not valid_obs.empty:
            # 获取最近的OB
            last_ob = valid_obs.iloc[-1]
            return {
                self.TIMESTAMP_COL: last_ob[self.TIMESTAMP_COL],
                self.OB_HIGH_COL: last_ob[self.OB_HIGH_COL],
                self.OB_LOW_COL: last_ob[self.OB_LOW_COL],
                self.OB_MID_COL: last_ob[self.OB_MID_COL],
                self.OB_VOLUME_COL: last_ob[self.OB_VOLUME_COL],
                self.OB_DIRECTION_COL: last_ob[self.OB_DIRECTION_COL],
                self.OB_ATR: last_ob[self.OB_ATR],
                self.OB_WAS_CROSSED: last_ob[self.OB_WAS_CROSSED],
            }

        return None
