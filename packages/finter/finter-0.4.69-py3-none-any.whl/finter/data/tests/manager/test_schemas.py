"""Test suite for data validation schemas."""

from datetime import datetime

import numpy as np
import pytest
from pydantic import ValidationError

from finter.data.manager.schemas import (
    EntityDataInput,
    MacroDataInput,
    StaticDataInput,
    StockDataInput,
)


# Fixtures
@pytest.fixture
def sample_datetime_list():
    """Generate sample datetime list for tests."""
    return [datetime(2021, 1, i) for i in range(1, 4)]


@pytest.fixture
def sample_entity_list():
    """Generate sample entity list for tests."""
    return ["Entity_A", "Entity_B", "Entity_C"]


class TestStockDataInput:
    """Tests for StockDataInput validation schema."""

    def test_valid_stock_data(self):
        """Test valid stock data input."""
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2), datetime(2021, 1, 3)]
        N = ["A", "B", "C"]
        F = "returns"

        stock_data = StockDataInput(data=data, T=T, N=N, F=F)

        assert stock_data.data.shape == (3, 3)
        assert stock_data.T == T
        assert stock_data.N == N
        assert stock_data.F == F
        assert stock_data.coords == {"T": T, "N": N, "F": F}

    def test_invalid_data_dimension(self):
        """Test that 3D array raises validation error."""
        data = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])  # 3D array
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]
        N = ["A", "B"]
        F = "returns"

        with pytest.raises(ValidationError) as exc_info:
            StockDataInput(data=data, T=T, N=N, F=F)

        assert "Expected 2D array" in str(exc_info.value)

    def test_mismatched_time_length(self):
        """Test that mismatched T length raises error."""
        data = np.array([[1, 2], [3, 4], [5, 6]])  # 3x2 array
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]  # Length 2, should be 3
        N = ["A", "B"]
        F = "returns"

        with pytest.raises(ValidationError) as exc_info:
            StockDataInput(data=data, T=T, N=N, F=F)

        assert "Coordinate length mismatch" in str(exc_info.value)

    def test_mismatched_entity_length(self):
        """Test that mismatched N length raises error."""
        data = np.array([[1, 2, 3], [4, 5, 6]])  # 2x3 array
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]
        N = ["A", "B"]  # Length 2, should be 3
        F = "returns"

        with pytest.raises(ValidationError) as exc_info:
            StockDataInput(data=data, T=T, N=N, F=F)

        assert "Coordinate length mismatch" in str(exc_info.value)

    def test_invalid_time_type(self):
        """Test that non-datetime T values raise error."""
        data = np.array([[1, 2], [3, 4]])
        T = ["2021-01-01", "2021-01-02"]  # Strings instead of datetime
        N = ["A", "B"]
        F = "returns"

        with pytest.raises(ValidationError) as exc_info:
            StockDataInput(data=data, T=T, N=N, F=F)

        assert "All T coordinates must be datetime objects" in str(exc_info.value)

    def test_empty_coordinates(self):
        """Test that empty coordinate lists raise error."""
        data = np.array([[1, 2]])

        # Test empty T
        with pytest.raises(ValidationError):
            StockDataInput(data=data, T=[], N=["A", "B"], F="returns")

        # Test empty N
        with pytest.raises(ValidationError):
            StockDataInput(data=data, T=[datetime.now()], N=[], F="returns")

    def test_mixed_entity_types(self):
        """Test that mixed entity types (str, int, float) work correctly."""
        data = np.array([[1, 2, 3], [4, 5, 6]])
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]
        N = ["A", 1, 2.5]  # Mixed types
        F = "returns"

        stock_data = StockDataInput(data=data, T=T, N=N, F=F)
        assert stock_data.N == ["A", 1, 2.5]


class TestMacroDataInput:
    """Tests for MacroDataInput validation schema."""

    def test_valid_macro_data(self):
        """Test valid macro data input."""
        data = np.array([1.5, 2.5, 3.5])
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2), datetime(2021, 1, 3)]
        F = "gdp_growth"

        macro_data = MacroDataInput(data=data, T=T, F=F)

        assert macro_data.data.shape == (3,)
        assert macro_data.T == T
        assert macro_data.F == F
        assert macro_data.coords == {"T": T, "F": F}

    def test_invalid_data_dimension(self):
        """Test that 2D array raises validation error."""
        data = np.array([[1, 2], [3, 4]])  # 2D array
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]
        F = "gdp_growth"

        with pytest.raises(ValidationError) as exc_info:
            MacroDataInput(data=data, T=T, F=F)

        assert "Expected 1D array" in str(exc_info.value)

    def test_mismatched_time_length(self):
        """Test that mismatched T length raises error."""
        data = np.array([1, 2, 3])
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]  # Length 2, should be 3
        F = "gdp_growth"

        with pytest.raises(ValidationError) as exc_info:
            MacroDataInput(data=data, T=T, F=F)

        assert "Coordinate length mismatch" in str(exc_info.value)

    def test_mixed_time_types(self):
        """Test that mixed datetime and non-datetime raises error."""
        data = np.array([1, 2])
        T = [datetime(2021, 1, 1), "2021-01-02"]  # Mixed types
        F = "gdp_growth"

        with pytest.raises(ValidationError) as exc_info:
            MacroDataInput(data=data, T=T, F=F)

        assert "All T coordinates must be datetime objects" in str(exc_info.value)


class TestEntityDataInput:
    """Tests for EntityDataInput validation schema."""

    def test_valid_entity_data(self):
        """Test valid entity data input."""
        data = np.array([100, 200, 300])
        N = ["Company_A", "Company_B", "Company_C"]
        F = "market_cap"

        entity_data = EntityDataInput(data=data, N=N, F=F)

        assert entity_data.data.shape == (3,)
        assert entity_data.N == N
        assert entity_data.F == F
        assert entity_data.coords == {"N": N, "F": F}

    def test_invalid_data_dimension(self):
        """Test that 2D array raises validation error."""
        data = np.array([[1, 2], [3, 4]])  # 2D array
        N = ["A", "B"]
        F = "market_cap"

        with pytest.raises(ValidationError) as exc_info:
            EntityDataInput(data=data, N=N, F=F)

        assert "Expected 1D array" in str(exc_info.value)

    def test_mismatched_entity_length(self):
        """Test that mismatched N length raises error."""
        data = np.array([1, 2, 3])
        N = ["A", "B"]  # Length 2, should be 3
        F = "market_cap"

        with pytest.raises(ValidationError) as exc_info:
            EntityDataInput(data=data, N=N, F=F)

        assert "Coordinate length mismatch" in str(exc_info.value)

    def test_numeric_entity_ids(self):
        """Test that numeric entity IDs work correctly."""
        data = np.array([1.5, 2.5, 3.5])
        N = [1, 2, 3]  # Integer IDs
        F = "market_cap"

        entity_data = EntityDataInput(data=data, N=N, F=F)
        assert entity_data.N == [1, 2, 3]

    def test_float_entity_ids(self):
        """Test that float entity IDs work correctly."""
        data = np.array([10, 20])
        N = [1.5, 2.5]  # Float IDs
        F = "score"

        entity_data = EntityDataInput(data=data, N=N, F=F)
        assert entity_data.N == [1.5, 2.5]


class TestStaticDataInput:
    """Tests for StaticDataInput validation schema."""

    def test_valid_static_data(self):
        """Test valid static data input."""
        data = np.array(42.5)
        F = "constant_rate"

        static_data = StaticDataInput(data=data, F=F)

        assert static_data.data.shape == ()
        assert static_data.data == 42.5
        assert static_data.F == F
        assert static_data.coords == {"F": F}

    def test_invalid_data_dimension(self):
        """Test that 1D array raises validation error."""
        data = np.array([1, 2, 3])  # 1D array
        F = "constant_rate"

        with pytest.raises(ValidationError) as exc_info:
            StaticDataInput(data=data, F=F)

        assert "Expected scalar (0D)" in str(exc_info.value)

    def test_integer_scalar(self):
        """Test that integer scalar works correctly."""
        data = np.array(100)
        F = "fixed_value"

        static_data = StaticDataInput(data=data, F=F)
        assert static_data.data == 100
        assert static_data.data.dtype in [np.int32, np.int64]

    def test_float_scalar(self):
        """Test that float scalar works correctly."""
        data = np.array(3.14159)
        F = "pi_constant"

        static_data = StaticDataInput(data=data, F=F)
        assert static_data.data == pytest.approx(3.14159)
        assert static_data.data.dtype in [np.float32, np.float64]


class TestEdgeCases:
    """Tests for edge cases across all schemas."""

    def test_single_element_arrays(self):
        """Test single element arrays for each schema."""
        # Stock data with 1x1 array
        stock_data = StockDataInput(
            data=np.array([[5]]), T=[datetime(2021, 1, 1)], N=["A"], F="value"
        )
        assert stock_data.data.shape == (1, 1)

        # Macro data with single element
        macro_data = MacroDataInput(
            data=np.array([5]), T=[datetime(2021, 1, 1)], F="value"
        )
        assert macro_data.data.shape == (1,)

        # Entity data with single element
        entity_data = EntityDataInput(data=np.array([5]), N=["A"], F="value")
        assert entity_data.data.shape == (1,)

    def test_large_arrays(self):
        """Test with larger arrays to ensure scalability."""
        # Stock data with 1000x500 array
        n_times = 1000
        n_entities = 500

        data = np.random.randn(n_times, n_entities)
        T = [datetime(2021, 1, 1) for _ in range(n_times)]
        N = [f"Entity_{i}" for i in range(n_entities)]
        F = "returns"

        stock_data = StockDataInput(data=data, T=T, N=N, F=F)
        assert stock_data.data.shape == (n_times, n_entities)

    def test_special_characters_in_names(self):
        """Test that special characters in coordinate names work."""
        data = np.array([[1, 2], [3, 4]])
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]
        N = ["Company-A/B", "Company@C#D"]
        F = "metric_1.2.3"

        stock_data = StockDataInput(data=data, T=T, N=N, F=F)
        assert stock_data.N == N
        assert stock_data.F == F

    def test_numpy_dtype_preservation(self):
        """Test that numpy dtypes are preserved."""
        # Float32
        data_f32 = np.array([1, 2, 3], dtype=np.float32)
        macro_data = MacroDataInput(
            data=data_f32, T=[datetime(2021, 1, 1) for _ in range(3)], F="value"
        )
        assert macro_data.data.dtype == np.float32

        # Int64
        data_i64 = np.array([1, 2, 3], dtype=np.int64)
        entity_data = EntityDataInput(data=data_i64, N=["A", "B", "C"], F="count")
        assert entity_data.data.dtype == np.int64


class TestAdvancedValidation:
    """Tests for advanced validation scenarios."""

    @pytest.mark.parametrize("invalid_value", [np.nan, np.inf, -np.inf])
    def test_special_float_values(self, invalid_value):
        """Test handling of NaN and infinity values."""
        # These should work - numpy arrays can contain special values
        data = np.array([[1, invalid_value], [3, 4]])
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]
        N = ["A", "B"]

        stock_data = StockDataInput(data=data, T=T, N=N, F="returns")
        assert np.isnan(stock_data.data[0, 1]) or np.isinf(stock_data.data[0, 1])

    def test_non_contiguous_array(self):
        """Test with non-contiguous numpy arrays."""
        # Create non-contiguous array through slicing
        original = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        data = original[::2, :]  # Non-contiguous: skip every other row

        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]
        N = ["A", "B", "C"]

        stock_data = StockDataInput(data=data, T=T, N=N, F="values")
        assert stock_data.data.shape == (2, 3)

    def test_empty_string_feature(self):
        """Test that empty string F field is rejected."""
        data = np.array([1, 2])
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]

        with pytest.raises(ValidationError):
            MacroDataInput(data=data, T=T, F="")

    def test_duplicate_entity_names(self):
        """Test that duplicate entity names are allowed."""
        data = np.array([[1, 2, 3], [4, 5, 6]])
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]
        N = ["A", "A", "B"]  # Duplicate "A"

        # Should work - duplicates are allowed
        stock_data = StockDataInput(data=data, T=T, N=N, F="values")
        assert stock_data.N == N

    def test_coords_immutability(self):
        """Test that coords property cannot be modified."""
        data = np.array([1, 2])
        N = ["A", "B"]
        F = "metric"
        entity_data = EntityDataInput(data=data, N=N, F=F)

        # coords is a computed property, so it's always regenerated
        original_coords = entity_data.coords
        assert original_coords == {"N": N, "F": F}

        # Attempting to modify the returned dict shouldn't affect the property
        original_coords["N"] = ["X", "Y"]
        assert entity_data.coords == {"N": N, "F": F}


@pytest.mark.parametrize(
    "data_type,expected_dtype",
    [
        (np.float32, np.float32),
        (np.float64, np.float64),
        (np.int32, np.int32),
        (np.int64, np.int64),
        (np.complex128, np.complex128),
    ],
)
class TestDtypePreservation:
    """Test that various numpy dtypes are preserved."""

    def test_stock_data_dtype(self, data_type, expected_dtype):
        """Test dtype preservation in StockDataInput."""
        data = np.array([[1, 2], [3, 4]], dtype=data_type)
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]
        N = ["A", "B"]

        stock_data = StockDataInput(data=data, T=T, N=N, F="values")
        assert stock_data.data.dtype == expected_dtype

    def test_macro_data_dtype(self, data_type, expected_dtype):
        """Test dtype preservation in MacroDataInput."""
        data = np.array([1, 2], dtype=data_type)
        T = [datetime(2021, 1, 1), datetime(2021, 1, 2)]

        macro_data = MacroDataInput(data=data, T=T, F="metric")
        assert macro_data.data.dtype == expected_dtype


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
