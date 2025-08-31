import logging
import pandas as pd

from core.smc.SMCStruct import SMCStruct


class SMCFVG(SMCStruct):
    FVG_TOP = "fvg_top"
    FVG_BOT = "fvg_bot"
    FVG_MID = "fvg_mid"
    FVG_SIDE = "fvg_side"
    FVG_WAS_BALANCED = "fvg_was_balanced"

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def find_FVGs(
        self, struct: pd.DataFrame, side, check_balanced=True, start_index=-1
    ) -> pd.DataFrame:
        """_summary_
            寻找公允价值缺口
        Args:
            data (pd.DataFrame): K线数据
            side (_type_): 交易方向 'buy'|'sell'
            threshold (_type_): 阈值价格，通常为溢价和折价区的CE
            check_balanced (bool): 是否检查FVG是否被平衡过,默认为True
            start_index (int): 开始查找索引的起点,默认为-1

        Returns:
            pd.DataFrame: _description_

        """
        # bug2.2.5_1，未到折价区，计算FVG需要前一根K线
        # df = data.copy().iloc[pivot_index:]
        df = (
            struct.copy()
            if start_index == -1
            else struct.copy().iloc[max(0, start_index - 1) :]
        )

        # 检查数据中是否包含必要的列
        check_columns = [self.HIGH_COL, self.LOW_COL]
        self.check_columns(df, check_columns)

        # 处理公允价值缺口
        # 使用向量化操作替代apply，提高性能
        if side == self.BUY_SIDE:
            condition = df[self.HIGH_COL].shift(1) < df[self.LOW_COL].shift(-1)
            side_value = self.BULLISH_TREND
            price_top = df[self.LOW_COL].shift(-1)
            price_bot = df[self.HIGH_COL].shift(1)
        else:
            condition = df[self.LOW_COL].shift(1) > df[self.HIGH_COL].shift(-1)
            side_value = self.BEARISH_TREND
            price_top = df[self.LOW_COL].shift(1)
            price_bot = df[self.HIGH_COL].shift(-1)

        df.loc[:, self.FVG_SIDE] = pd.Series(
            [side_value if x else None for x in condition], index=df.index
        )
        
        df.loc[:, self.FVG_TOP] = price_top.where(condition, 0)
        df.loc[:, self.FVG_BOT] = price_bot.where(condition, 0)
        
        df.loc[:, self.FVG_TOP] = price_top.where(condition, 0).apply(
            lambda x: self.toDecimal(x) if pd.notnull(x) else None
        )
        df.loc[:, self.FVG_BOT] = price_bot.where(condition, 0).apply(
            lambda x: self.toDecimal(x) if pd.notnull(x) else None
        )
    
        df.loc[:, self.FVG_MID] = (df[self.FVG_TOP] + df[self.FVG_BOT]) / 2

        fvg_df = df[
            df[self.FVG_SIDE] == self.BULLISH_TREND
            if side == self.BUY_SIDE
            else df[self.FVG_SIDE] == self.BEARISH_TREND
        ]
        fvg_df = fvg_df.copy()
        if check_balanced:
            # 检查FVG是否被平衡过
            fvg_df.loc[:, self.FVG_WAS_BALANCED] = fvg_df.apply(
                lambda row: any(df.loc[row.name + 2 :, self.LOW_COL] <= row[self.FVG_BOT])
                if side == self.BUY_SIDE
                else any(
                    df.loc[row.name + 2 :, self.HIGH_COL] >= row[self.FVG_TOP]
                ),  
                axis=1,
            )

            fvg_df = fvg_df[~fvg_df[self.FVG_WAS_BALANCED]]

        return fvg_df

