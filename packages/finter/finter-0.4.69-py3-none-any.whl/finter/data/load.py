from finter.api.alpha_api import AlphaApi
from finter.api.content_api import ContentApi
from finter.api.flexible_fund_api import FlexibleFundApi
from finter.api.fund_api import FundApi
from finter.api.portfolio_api import PortfolioApi
from finter.framework_model.aws_credentials import get_parquet_df
from finter.log import PromtailLogger
from finter.settings import get_api_client, logger
from finter.utils.convert import to_dataframe


class ModelData:
    """
    A class to handle the loading of various financial model data based on their identity names.

    This class provides functionality to retrieve data for content models, alpha models, portfolio models, fund models, and flexible fund models. It raises errors for unsupported or unknown model types.

    Methods:
        load(identity_name: str) -> pd.DataFrame:
            Determines the model type from the identity name and calls the appropriate method to retrieve and convert the model data into a DataFrame.
        get_cm_df(identity_name: str) -> pd.DataFrame:
            Retrieves content model data using the ContentApi and converts it to a DataFrame.
        get_am_df(identity_name: str) -> pd.DataFrame:
            Retrieves alpha model data using the AlphaApi and converts it to a DataFrame.
        get_pm_df(identity_name: str) -> pd.DataFrame:
            Retrieves portfolio model data using the PortfolioApi and converts it to a DataFrame.
        get_fm_df(identity_name: str) -> pd.DataFrame:
            Retrieves fund model data using the FundApi and converts it to a DataFrame.
        get_ffm_df(identity_name: str) -> pd.DataFrame:
            Retrieves flexible fund model data using the FlexibleFundApi and converts it to a DataFrame.

    Raises:
        NotImplementedError: If an attempt is made to load data for metafund models, which are not supported yet.
        ValueError: If the model type is unknown.
    """

    @classmethod
    def load(cls, identity_name: str, columns: list = None, backup_day=None):
        """
        Loads model data based on the provided identity name by determining the type of model
        and calling the corresponding method to fetch and process the data.

        Args:
            identity_name (str): The identity name of the model, formatted as '<model_type>.<additional_info>'.
                Example: 'alpha.krx.krx.stock.ldh0127.div_2'.
            columns (list; optional): When using cm loading by parquet, you can pre-slice the columns.

        Returns:
            pd.DataFrame: A DataFrame containing the loaded model data.

        Raises:
            NotImplementedError: If the model type is 'metafund', which is currently not supported.
            ValueError: If the model type is unknown, indicating an unsupported or improperly formatted identity name.
        """
        try:
            return get_parquet_df(identity_name, columns, backup_day)
        except PermissionError:
            # Not all model data is currently provided in parquet format.
            model_type = identity_name.split(".")[0]

            if model_type == "content":
                df = cls.get_cm_df(identity_name, backup_day)
            elif model_type == "alpha":
                df = cls.get_am_df(identity_name)
            elif model_type == "portfolio":
                df = cls.get_pm_df(identity_name)
            elif model_type == "fund":
                df = cls.get_fm_df(identity_name)
            elif model_type == "flexible_fund":
                df = cls.get_ffm_df(identity_name)
            elif model_type == "meta_fund":
                logger.error("Metafund model is not supported yet.")
                raise NotImplementedError
            else:
                logger.error(f"Unknown identity_name: {identity_name}")
                raise ValueError

            PromtailLogger.send_log(
                level="INFO",
                message=f"{identity_name}",
                service="finterlabs-jupyterhub",
                user_id=PromtailLogger.get_user_info(),
                operation="load_model_data",
                status="success",
            )
            logger.info(f"Loading {model_type} model: {identity_name}")

            logger.info(
                "Column types not supported well yet. It will be supported soon. Please contact the developer."
            )

            if columns != None:
                logger.info("Parameter 'columns' does not used.")

            return df

    @staticmethod
    def get_cm_df(identity_name, backup_day):
        api_response = (
            ContentApi(get_api_client())
            .content_model_retrieve(identity_name=identity_name, backup_day=backup_day)
            .to_dict()
        )
        return to_dataframe(api_response["cm"], api_response["column_types"])

    @staticmethod
    def get_am_df(identity_name):
        api_response = (
            AlphaApi(get_api_client())
            .alpha_model_retrieve(identity_name=identity_name)
            .to_dict()
        )
        return to_dataframe(
            api_response["am"],  # api_response["column_types"]
        )

    @staticmethod
    def get_pm_df(identity_name):
        api_response = (
            PortfolioApi(get_api_client())
            .portfolio_model_retrieve(identity_name=identity_name)
            .to_dict()
        )
        return to_dataframe(
            api_response["pm"],  # api_response["column_types"]
        )

    @staticmethod
    def get_fm_df(identity_name):
        api_response = (
            FundApi(get_api_client())
            .fund_model_retrieve(identity_name=identity_name)
            .to_dict()
        )
        return to_dataframe(
            api_response["fm"],  # api_response["column_types"]
        )

    @staticmethod
    def get_ffm_df(identity_name):
        api_response = (
            FlexibleFundApi(get_api_client())
            .flexiblefund_model_retrieve(identity_name=identity_name)
            .to_dict()
        )
        return to_dataframe(
            api_response["ffm"],  # api_response["column_types"]
        )

    # @staticmethod
    # def get_mfm_df(identity_name):
    #     api_response = (
    #         MetafundApi(get_api_client())
    #         .metafund_model_retrieve(metafund_name=identity_name)
    #         .to_dict()
    #     )
    #     return to_dataframe(
    #         api_response["mfm"],  # api_response["column_types"]
    #     )


if __name__ == "__main__":
    # ModelData.load(identity_name="content.fnguide.ftp.economy.currency.1d")
    # df = ModelData.load(identity_name="alpha.krx.krx.stock.ldh0127.div_2")
    # df = ModelData.load(identity_name="portfolio.krx.krx.stock.ldh0127.div_1")
    # df = ModelData.load(identity_name="flexible_fund.krx.krx.stock.ldh0127.ipo_event")
    df = ModelData.load(identity_name="fund.krx.krx.stock.soobeom33.cs_fund_2")
