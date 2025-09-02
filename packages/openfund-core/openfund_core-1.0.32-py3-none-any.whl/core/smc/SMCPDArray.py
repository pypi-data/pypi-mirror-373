import logging
import pandas as pd

from core.smc.SMCFVG import SMCFVG
from core.smc.SMCOrderBlock import SMCOrderBlock

class SMCPDArray(SMCFVG,SMCOrderBlock):
    PD_HIGH_COL = "pd_high"
    PD_LOW_COL = "pd_low"
    PD_MID_COL = "pd_mid"
    PD_TYPE_COL = "pd_type"
    PD_WAS_BALANCED_COL = "pd_was_balanced"

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def find_PDArrays(
        self, struct: pd.DataFrame, side, start_index=-1, balanced=False, is_struct_body_break=False
    ) -> pd.DataFrame:
        """_summary_
            寻找PDArrays,包括Fair Value Gap (FVG)|Order Block (OB)|Breaker Block(BB)|Mitigation Block(BB) 
        Args:
            data (pd.DataFrame): K线数据
            side (_type_): 交易方向 'buy'|'sell'
            start_index (int): 开始查找索引的起点,默认为-1
            balanced (bool): PD是否有效,默认为False。PD被crossed过,则是无效PD

        Returns:
            pd.DataFrame: _description_

        """
       
        df = (
            struct.copy()
            if start_index == -1
            else struct.copy().iloc[max(0, start_index - 1) :]
        )

        df_FVGs = self.find_FVGs(df, side, start_index)

        if not balanced:
            df_FVGs = df_FVGs[~df_FVGs[self.FVG_WAS_BALANCED]]
        # self.logger.info(f"fvgs:\n{df_FVGs[['timestamp', self.FVG_SIDE, self.FVG_TOP, self.FVG_BOT, self.FVG_WAS_BALANCED]]}")

        is_valid = not balanced
        df_OBs = self.find_OBs(struct=df, side=side, start_index=start_index, is_valid=is_valid, is_struct_body_break=is_struct_body_break)
        # self.logger.info("find_OBs:\n %s", df_OBs)
        
        # 使用更简洁的方式重命名和合并时间戳列
        timestamp_mapping = {self.TIMESTAMP_COL: ['ts_OBs', 'ts_FVGs']}
        df_OBs = df_OBs.rename(columns={self.TIMESTAMP_COL: timestamp_mapping[self.TIMESTAMP_COL][0]})
        df_FVGs = df_FVGs.rename(columns={self.TIMESTAMP_COL: timestamp_mapping[self.TIMESTAMP_COL][1]})

        # 使用更高效的方式合并数据框
        df_PDArrays = pd.concat(
            [df_OBs, df_FVGs], 
            axis=1,
            join='outer'
        ).sort_index()

        # 使用更清晰的方式合并时间戳列
        df_PDArrays[self.TIMESTAMP_COL] = df_PDArrays[timestamp_mapping[self.TIMESTAMP_COL][0]].fillna(
            df_PDArrays[timestamp_mapping[self.TIMESTAMP_COL][1]]
        )

        df_PDArrays[self.PD_WAS_BALANCED_COL] = df_PDArrays[[self.OB_WAS_CROSSED, self.FVG_WAS_BALANCED]].apply(
            lambda x: x.iloc[0] if pd.notna(x.iloc[0]) else x.iloc[1], axis=1)

        df_PDArrays[self.PD_TYPE_COL] = df_PDArrays[[self.FVG_SIDE, self.OB_DIRECTION_COL]].apply(
            lambda x: 'FVG-OB' if pd.notna(x.iloc[0]) and pd.notna(x.iloc[1]) else 'FVG' if pd.notna(x.iloc[0]) else 'OB', axis=1
        )
     
        # 将数值转换为decimal类型以避免float运算错误
        df_PDArrays.loc[:, self.PD_HIGH_COL] = df_PDArrays[[self.FVG_TOP, self.OB_HIGH_COL]].max(axis=1)
        df_PDArrays.loc[:, self.PD_LOW_COL] = df_PDArrays[[self.FVG_BOT, self.OB_LOW_COL]].min(axis=1)
        df_PDArrays.loc[:, self.PD_MID_COL] = (df_PDArrays[self.PD_HIGH_COL] + df_PDArrays[self.PD_LOW_COL]) / 2
               

        # 根据balanced参数过滤PDArrays,返回符合条件的数据
      
        return df_PDArrays[df_PDArrays[self.PD_WAS_BALANCED_COL] == balanced]


    def get_latest_PDArray(self, df_PDArrays: pd.DataFrame, side, start_index=-1, balanced=False, mask=None, is_struct_body_break=False) -> dict:
        """_summary_
            过滤PDArrays,只保留指定方向的PDArrays
        Args:
            df_PDArrays (pd.DataFrame): _description_
            mask (str): _description_

        Returns:
            pd.DataFrame: _description_
        """   

        # 检查数据中是否包含必要的列
        df = df_PDArrays.copy()
        check_columns = [self.STRUCT_COL]
        try:
            self.check_columns(df, check_columns)
        except ValueError as e:
            df = self.build_struct(df,is_struct_body_break=is_struct_body_break)


        check_columns = [self.PD_TYPE_COL]
        try:
            self.check_columns(df, check_columns)
        except ValueError as e:
            df = self.find_PDArrays(df, side, start_index, balanced, is_struct_body_break=is_struct_body_break)
        
        if mask is not None:
            df = df[mask]
            
        if len(df) == 0:
            self.logger.info("未找到PDArray.")
            return None
        else:
            self.logger.debug(f"PDArray:\n{df[[self.TIMESTAMP_COL, self.PD_TYPE_COL, self.PD_HIGH_COL, self.PD_LOW_COL, self.PD_MID_COL,self.PD_WAS_BALANCED_COL,self.OB_WAS_CROSSED,self.FVG_WAS_BALANCED]]}")
            last_pd = df.iloc[-1]
            return {
                self.TIMESTAMP_COL: last_pd[self.TIMESTAMP_COL],
                self.PD_TYPE_COL: last_pd[self.PD_TYPE_COL],
                self.PD_HIGH_COL: last_pd[self.PD_HIGH_COL],
                self.PD_LOW_COL: last_pd[self.PD_LOW_COL],
                self.PD_MID_COL: last_pd[self.PD_MID_COL],
                self.PD_WAS_BALANCED_COL: last_pd[self.PD_WAS_BALANCED_COL],
            }
