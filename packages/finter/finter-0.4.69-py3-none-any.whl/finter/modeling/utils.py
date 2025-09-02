import numpy as np
import pandas as pd
from typing_extensions import Literal


def daily2period(
    data: pd.DataFrame, period: Literal["W", "M", "Q"], keep_index=False
) -> pd.DataFrame:
    tmp = data.index[-2:-1].append(data.index[0:-1])
    mask = data.index.to_period(period) != tmp.to_period(period)
    if keep_index:
        ffill_dates = 90
        if period == "W":
            ffill_dates = 7
        elif period == "M":
            ffill_dates = 30
        return data[mask].fillna(0).reindex(data.index).ffill(limit=ffill_dates)
    return data[mask]


def get_rebalancing_mask(
    data: pd.DataFrame, period: Literal["W", "M", "Q", "Y"]
) -> pd.Index:
    tmp = data.index[-2:-1].append(data.index[0:-1])
    mask = data.index.to_period(period) != tmp.to_period(period)
    return data.index[mask]


class DataFrameFilter:
    @staticmethod
    def data_to_str(df):
        df_str = df.astype(str)
        na_mask = df.isna()
        processed_df = df_str.apply(lambda x: x.str.split(".").str[0])
        processed_df[na_mask] = np.nan
        return processed_df

    @staticmethod
    def reindex_df(filter_df, target_df):
        return filter_df.reindex(target_df.index).ffill(limit=30)

    @staticmethod
    def match_common_column(filter_df, target_df, slice_length=None):
        col_mapping = {}
        for target_col in target_df.columns:
            if slice_length is None:
                sliced_col = target_col
            else:
                sliced_col = target_col[:slice_length]

            if sliced_col in filter_df.columns:
                if sliced_col not in col_mapping:
                    col_mapping[sliced_col] = []
                col_mapping[sliced_col].append(target_col)

        dfs_to_concat = []

        for sliced_col, target_cols in col_mapping.items():
            for target_col in target_cols:
                temp_df = pd.DataFrame(
                    filter_df[sliced_col].values,
                    index=filter_df.index,
                    columns=[target_col],
                )
                dfs_to_concat.append(temp_df)

        if dfs_to_concat:
            return pd.concat(dfs_to_concat, axis=1)
        else:
            return pd.DataFrame(index=filter_df.index)

    @staticmethod
    def compare_column_length(filter_df, target_df):
        filter_df_col_length = (
            len(filter_df.columns[0]) if len(filter_df.columns) > 0 else 0
        )
        target_df_col_length = (
            len(target_df.columns[0]) if len(target_df.columns) > 0 else 0
        )
        return filter_df_col_length == target_df_col_length

    @staticmethod
    def slice_masking(slice_filter_df, value, mode="include"):
        pattern_mask = pd.DataFrame(
            False, index=slice_filter_df.index, columns=slice_filter_df.columns
        )

        for col in slice_filter_df.columns:
            valid_cells = slice_filter_df[col].notna()
            if valid_cells.any():
                sliced_values = (
                    slice_filter_df.loc[valid_cells, col].astype(str).str[: len(value)]
                )
                matches = sliced_values == value

                if matches.any():
                    pattern_mask.loc[matches.index[matches], col] = True

        result_mask = pd.DataFrame(
            np.nan, index=slice_filter_df.index, columns=slice_filter_df.columns
        )
        if mode == "include":
            result_mask[pattern_mask] = 1
        else:  # exclude
            not_matched = ~pattern_mask & slice_filter_df.notna()
            result_mask[not_matched] = 1

        return result_mask

    @staticmethod
    def identical_masking(df, value, mode="include"):
        mask = df.astype(str) == value
        mask_df = pd.DataFrame(np.nan, index=df.index, columns=df.columns)

        if mode == "include":
            mask_df[mask] = 1
        else:
            orig_not_na = df.notna()
            mask_df[orig_not_na & ~mask] = 1

        return mask_df

    @staticmethod
    def match_column_reindex(result_mask, filter_df, target_df, slice_length=None):
        if not DataFrameFilter.compare_column_length(filter_df, target_df):
            matched_mask = DataFrameFilter.match_common_column(
                result_mask, target_df, slice_length
            )
            final_mask = DataFrameFilter.reindex_df(matched_mask, target_df)
        else:
            final_mask = DataFrameFilter.reindex_df(result_mask, target_df)

        return final_mask

    @classmethod
    def by_boolean(
        cls, boolean_df, target_df, tobe_masked, mode="include", slice_length=None
    ):
        target = target_df.copy()
        boolean = boolean_df.copy()

        boolean_str = cls.data_to_str(boolean)

        result_mask = pd.DataFrame(
            np.nan, index=boolean_str.index, columns=boolean_str.columns
        )

        for value in tobe_masked:
            temp_masked = cls.identical_masking(boolean_str, value, mode)
            result_mask = result_mask.combine_first(temp_masked)

        final_mask = cls.match_column_reindex(
            result_mask, boolean_df, target_df, slice_length
        )

        return final_mask * target

    @classmethod
    def by_gics(cls, gics_df, target_df, tobe_masked, mode="include", slice_length=6):
        target = target_df.copy()
        gics = gics_df.copy()

        result_mask = pd.DataFrame(np.nan, index=gics.index, columns=gics.columns)

        for value in tobe_masked:
            temp_mask = cls.slice_masking(gics, value, mode)
            result_mask = result_mask.combine_first(temp_mask)

        final_mask = cls.match_column_reindex(
            result_mask, gics_df, target_df, slice_length
        )

        return final_mask * target
