import json

import pandas as pd

from finter.api import MapperApi, SymbolApi
from finter.data import IdTable
from finter.settings import get_api_client


class Symbol:
    """
    A class to handle the conversion of financial symbols between different identifiers based on API responses.

    This class provides methods to convert financial symbol identifiers from one format to another using the SymbolApi,
    and also supports universe-based initialization for search functionality.

    Methods:
        convert(_from: str, to: str, source: Union[str, list], date: Optional[str] = None, universe: Optional[int] = None) -> Optional[dict]:
            Converts financial symbols from one identifier format to another and handles potential errors during API calls.

    Attributes:
        _from (str): The source identifier type (e.g., 'id').
        to (str): The target identifier type (e.g., 'entity_name').
        source (Union[str, list]): The actual identifier(s) to be converted. Can be a single identifier or a list of identifiers.
        date (Optional[str]): The date for which the conversion is applicable (default is None, implying the current date).
        universe (Optional[int]): An optional parameter to specify the universe of the identifiers (default is None).
    """

    def __init__(self, universe=None):
        """
        Initialize Symbol with a specific universe for search functionality.

        Args:
            universe (str, optional): Universe name (e.g., 'kr_stock', 'us_stock', 'spglobal-usa')
        """
        self.universe = universe
        self._id_table = self._get_id_table()

        # Universe to vendor mapping
        self.universe_list = ["kr_stock", "us_stock"]

    def _get_id_table(self):
        """Get IdTable for the current universe."""
        if not self.universe:
            raise ValueError("Universe must be set")

        try:
            if self.universe == "kr_stock":
                fnguide_table = IdTable("fnguide").get_stock()
                fnguide_table["short_code"] = fnguide_table["STK_CD"]
                quantit_table = IdTable("quantit").get_stock()
                quantit_table = quantit_table[
                    ~quantit_table["short_code"].str.startswith("fn_").fillna(True)
                ]
                quantit_table["ccid"] = quantit_table["ccid"].astype(int)
                quantit_table["short_code"] = quantit_table["short_code"].str[-6:]
                self._id_table = pd.merge(
                    fnguide_table, quantit_table, on="short_code", how="left"
                )[["ccid", "STK_CD", "ISIN_CD", "STK_NM_KOR", "STK_NM_ENG"]].set_index(
                    "ccid"
                )
            elif self.universe == "us_stock":
                spglobal_table = IdTable("spglobal-usa").get_stock()
                spglobal_table["gvkeyiid"] = (
                    spglobal_table["gvkey"] + spglobal_table["iid"]
                )
                self._id_table = spglobal_table.set_index("gvkeyiid")[
                    ["conml", "tic", "tpcidesc"]
                ]
            else:
                raise ValueError(f"Invalid universe: {self.universe}")

            return self._id_table

        except Exception as e:
            print(f"Error loading data for {self.universe}: {e}")
            self._id_table = pd.DataFrame()  # Return empty DataFrame on error
            return self._id_table

    @classmethod
    def convert(cls, _from, to, source, date=None, universe=None):
        """
        Converts identifiers from one type to another using the SymbolApi service.

        Args:
            _from (str): The type of the source identifier.
            to (str): The type of the target identifier.
            source (Union[str, list]): The identifier or list of identifiers to convert.
            date (Optional[str]): The date for which the identifier conversion is relevant (not used in current implementation).
            universe (Optional[int]): The universe context for the conversion (not used in current implementation).

        Returns:
            Optional[dict]: A dictionary mapping the source identifiers to the converted identifiers, or None if the API call fails.

        Raises:
            Exception: Captures any exceptions raised during the API call, logs the error, and returns None.
        """
        if isinstance(source, pd.Index):
            source = source.to_list()
        if isinstance(
            source, list
        ):  # Check if the source is a list and convert it to a comma-separated string if true.
            source = ",".join(map(str, source))
        try:
            api_response = SymbolApi(get_api_client()).id_convert_create(
                _from=_from, to=to, source=source
            )
            result = api_response.code_mapped
            if _from == "id":
                result = {int(k): v for k, v in result.items()}
            if _from == "short_code":
                result = {k: v[0] if len(v) == 1 else v for k, v in result.items()}
            return result  # Return the mapping from the API response.
        except Exception as e:
            if hasattr(e, "body"):
                try:
                    error_json = json.loads(e.body)
                    message = error_json.get("message", "Unknown error occurred")
                except (ValueError, AttributeError):
                    message = str(e)
            else:
                message = str(e)
            print(f"Symbol API call failed: {message}")
            return None

    @staticmethod
    def us_convert(_from, to, source):
        if _from not in ["id", "ticker", "company_name"]:
            raise ValueError(
                f"Invalid source: {_from}, supported source: id, ticker, company_name"
            )
        if to not in ["id", "ticker", "company_name"]:
            raise ValueError(
                f"Invalid target: {to}, supported target: id, ticker, company_name"
            )

        table = IdTable("spglobal-usa").get_company()
        table["gvkeyiid"] = table["gvkey"] + table["iid"]
        if _from == "id":
            target_table = table.loc[table["gvkeyiid"].isin(source)]
            diff = [tmp for tmp in source if tmp not in table["gvkeyiid"].to_list()]
            if len(diff) > 0:
                raise ValueError(f"Not existing id: {diff}")
        elif _from == "ticker":
            target_table = table.loc[table["tic"].isin(source)]
            diff = [tmp for tmp in source if tmp not in table["tic"].to_list()]
            if len(diff) > 0:
                raise ValueError(f"Not existing ticker: {diff}")
        elif _from == "company_name":
            target_table = table.loc[table["conml"].isin(source)]
            diff = [tmp for tmp in source if tmp not in table["conml"].to_list()]
            if len(diff) > 0:
                raise ValueError(f"Not existing company name: {diff}")

        mapper = {"id": "gvkeyiid", "ticker": "tic", "company_name": "conml"}
        result = (
            target_table[[mapper[_from], mapper[to]]]
            .set_index(mapper[_from])
            .to_dict()[mapper[to]]
        )
        return result

    def search(self, query, max_results=10):
        """
        Search for symbols within the universe.

        Args:
            query (str): Search query
            max_results (int): Maximum number of results

        Returns:
            pd.DataFrame: Matching symbol data
        """
        if not self.universe:
            raise ValueError(
                "Universe must be set to use search functionality. Initialize with Symbol(universe='your_universe')"
            )

        data = self._id_table
        if data is None or data.empty:
            return pd.DataFrame()

        query_lower = query.lower()

        # Get all searchable text columns
        text_columns = data.select_dtypes(include=["object"]).columns

        # Search results with scores
        results = []

        for idx, row in data.iterrows():
            max_score = 0
            match_column = None

            for col in text_columns:
                value = str(row[col]) if pd.notna(row[col]) else ""
                value_lower = value.lower()

                # Exact match (highest score)
                if query_lower == value_lower:
                    max_score = 1.0
                    match_column = col
                    break

                # Starts with (high score)
                elif value_lower.startswith(query_lower):
                    score = 0.9
                    if score > max_score:
                        max_score = score
                        match_column = col

                # Contains (medium score)
                elif query_lower in value_lower:
                    score = 0.7
                    if score > max_score:
                        max_score = score
                        match_column = col

                # Fuzzy match (lower score)
                else:
                    import re
                    from difflib import SequenceMatcher

                    # Multiple fuzzy matching approaches
                    scores = []

                    # 1. Basic sequence matching
                    similarity = SequenceMatcher(None, query_lower, value_lower).ratio()
                    if similarity > 0.4:
                        scores.append(similarity * 0.6)

                    # 2. Check if removing common typo patterns helps
                    # Remove spaces, dots, dashes for comparison
                    clean_query = re.sub(r"[\s\.-]", "", query_lower)
                    clean_value = re.sub(r"[\s\.-]", "", value_lower)
                    if clean_query != query_lower or clean_value != value_lower:
                        clean_similarity = SequenceMatcher(
                            None, clean_query, clean_value
                        ).ratio()
                        if clean_similarity > 0.5:
                            scores.append(clean_similarity * 0.5)

                    # 3. Levenshtein-like approach for short strings
                    if len(query_lower) >= 3 and len(value_lower) >= 3:
                        # Check if one is substring of other after allowing 1-2 char differences
                        if abs(len(query_lower) - len(value_lower)) <= 2:
                            # Simple edit distance approximation
                            max_len = max(len(query_lower), len(value_lower))
                            if max_len > 0:
                                edit_similarity = 1 - (
                                    abs(len(query_lower) - len(value_lower)) / max_len
                                )
                                if edit_similarity > 0.7:
                                    scores.append(edit_similarity * 0.4)

                    if scores:
                        score = max(scores)
                        if score > max_score:
                            max_score = score
                            match_column = col

            if max_score > 0.3:  # Lowered from 0.5 to catch more typos
                results.append((idx, max_score, match_column))

        # Sort by score (descending) and take top results
        results.sort(key=lambda x: x[1], reverse=True)
        top_indices = [r[0] for r in results[:max_results]]

        return data.loc[top_indices] if top_indices else pd.DataFrame()

    def summary(self):
        """Show summary of available symbol data."""
        if not self.universe:
            raise ValueError(
                "Universe must be set. Initialize with Symbol(universe='your_universe')"
            )

        data = self._id_table
        if data is None or data.empty:
            print(f"No data available for {self.universe}")
            return

        print(f"Symbol Data Summary ({self.universe}):")
        print("-" * 50)
        print(f"Total records: {len(data)}")
        print(f"Columns: {', '.join(data.columns)}")
        print(f"Memory usage: {data.memory_usage(deep=True).sum() / 1024:.1f} KB")


class Mapper:
    """
    A class to handle the conversion of financial symbols using different MapperApi functions.

    This class provides methods to retrieve mappers for converting financial symbol identifiers between different formats using MapperApi.

    Methods:
        get_ccid_to_short_code_mapper() -> Optional[dict]:
            Retrieves the CCID to short code mapper.
        get_entity_id_to_ccid_mapper() -> Optional[dict]:
            Retrieves the entity ID to CCID mapper.
    """

    @classmethod
    def get_ccid_to_short_code_mapper(cls):
        """
        Retrieves the CCID to short code mapper using the MapperApi service.

        Args:
            None

        Returns:
            Optional[dict]: A dictionary containing the CCID to short code mappings, or None if the API call fails.

        Raises:
            Exception: Captures any exceptions raised during the API call, logs the error, and returns None.
        """
        try:
            api_response = MapperApi(
                get_api_client()
            ).mapper_ccid_to_short_code_retrieve()
            return api_response.mapper  # Return the mapping from the API response.
        except Exception as e:
            print(
                f"Mapper API call failed: {e}"
            )  # Log any exceptions encountered during the API call.
            return None

    @classmethod
    def get_entity_id_to_ccid_mapper(cls):
        """
        Retrieves the entity ID to CCID mapper using the MapperApi service.

        Args:
            None

        Returns:
            Optional[dict]: A dictionary containing the entity ID to CCID mappings, or None if the API call fails.

        Raises:
            Exception: Captures any exceptions raised during the API call, logs the error, and returns None.
        """
        try:
            api_response = MapperApi(
                get_api_client()
            ).mapper_entity_id_to_ccid_retrieve()
            return api_response.mapper  # Return the mapping from the API response.
        except Exception as e:
            print(
                f"Mapper API call failed: {e}"
            )  # Log any exceptions encountered during the API call.
            return None
