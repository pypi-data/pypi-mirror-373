class ModelValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class ModelValidationErrorMessage:
    @staticmethod
    def resample_and_fillna_error():
        return (
            "\n==============================\n"
            "Remove resample operations (.sum(), .std., .mean()) and use replace(np.nan, False) instead of fillna(False).\n\n"
            "- Resample operations have forward-looking issues; implement them directly.\n"
            "- fillna(False) is inefficient; replace(np.nan, False) is recommended.\n"
            "==============================\n"
        )

    @staticmethod
    def invalid_cm_loading_error():
        return (
            "\n==============================\n"
            "Invalid CM loading detected.\n\n"
            "Please use 'Base[Alpha|Portfolio|Fund|FlexibleFund].get_cm' or 'self.get_cm' for correct CM loading.\n"
            "==============================\n"
        )

    @staticmethod
    def nickname_dot_error():
        return (
            "\n==============================\n"
            "Nickname should not contain '.'.\n\n"
            "==============================\n"
        )

    @staticmethod
    def identity_space_error():
        return (
            "\n==============================\n"
            "Identity name should not contain space.\n\n"
            "==============================\n"
        )

    @staticmethod
    def index_out_of_range_error(start_date, end_date, test_idx, expected_idx):
        return (
            f"\n==============================\n"
            f"Index out of range error.\n\n"
            f"An index out of range issue was detected while executing "
            f"get({start_date}, {end_date})\n"
            f"expected indices : {expected_idx[0].date()}~{expected_idx[-1].date()}\n"
            f"test indices : {test_idx[0].date()}~{test_idx[-1].date()}\n"
            "The test index range must not exceed the expected index range.\n"
            "Recommendation: Please use loc[str(start): str(end)] in the get method.\n"
            "==============================\n"
        )

    @staticmethod
    def index_mismatch_error(
        expected_idx, missing_expected_indices, unexpected_indices
    ):
        return (
            f"\n==============================\n"
            f"Index mismatch detected.\n\n"
            "Recommend using 'df.reindex' with finter.calendar to align the index.\n"
            f"periods : {expected_idx[0].date()}~{expected_idx[-1].date()}\n"
            f"missing expected indices: {missing_expected_indices}\n"
            f"unexpected indices: {unexpected_indices}\n"
            "Please check the index of the output position.\n"
            f"==============================\n"
        )

    @staticmethod
    def all_nan_error():
        return (
            "\n==============================\n"
            "All NaN detected.\n\n"
            "Please check the output position.\n"
            "If you intended all cash, please fillna(0).\n"
            "==============================\n"
        )

    @staticmethod
    def exceed_max_position_error(max_size):
        return (
            f"\n==============================\n"
            f"Exceed max position size.\n\n"
            "Position size should be less than 1e8.\n"
            f"Your max position size: {max_size}\n"
            "==============================\n"
        )

    @staticmethod
    def start_end_dependency_error(orig, variation, name, compare_error):
        def format_index(idx):
            import pandas as pd

            start = (
                int(idx[0].strftime("%Y%m%d"))
                if idx[0].time() == pd.Timestamp("00:00:00").time()
                else idx[0]
            )
            end = (
                int(idx[-1].strftime("%Y%m%d"))
                if idx[-1].time() == pd.Timestamp("00:00:00").time()
                else idx[-1]
            )
            return start, end

        orig_start, orig_end = format_index(orig.index)
        var_start, var_end = format_index(variation.index)

        return (
            f"\n==============================\n"
            f"There is a {name} dependency detected, indicating a mismatch between the original and variation positions.\n\n"
            f"Original Position (start, end):\n"
            f"  ({orig_start}, {orig_end})\n\n"
            f"Variation Position (start, end):\n"
            f"  ({var_start}, {var_end})\n\n"
            f"{compare_error}\n\n"
            "This mismatch can lead to incorrect model behavior or inaccurate results. Please ensure that the positions are aligned correctly.\n"
            "==============================\n"
        )

    @staticmethod
    def duration_error(duration_secs, limit_secs):
        return (
            f"\n==============================\n"
            f"Your model took too long to run.\n\n"
            f"Duration: {duration_secs} seconds\n"
            f"Limit: {limit_secs} seconds\n"
            "==============================\n"
        )
