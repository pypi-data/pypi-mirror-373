"""
Core functionality tests for Synthetic Generator v0.0.7.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add the src directory to the path BEFORE the site-packages
src_path = os.path.join(os.path.dirname(__file__), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Also remove the installed package from sys.modules if it exists
if "synthetic_generator" in sys.modules:
    del sys.modules["synthetic_generator"]


def test_core_imports():
    """Test that core modules can be imported correctly."""
    try:
        from synthetic_generator import DataSchema, ColumnSchema, DataType, DistributionType
        from synthetic_generator.generators.base import DataGenerator
        from synthetic_generator.quick import fit, dataset

        print("✅ Core imports successful")
        print(f"   - DataSchema: {DataSchema}")
        print(f"   - DataType: {DataType}")
        print(f"   - DistributionType: {DistributionType}")
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import core classes: {e}")


def test_version():
    """Test that the version is correct."""
    try:
        from synthetic_generator import __version__
        assert __version__ == "0.0.7"
        print(f"✅ Version check successful: {__version__}")
    except Exception as e:
        pytest.fail(f"Failed to verify version: {e}")


def test_schema_creation():
    """Test that schemas can be created with proper data types and distributions."""
    try:
        from synthetic_generator import DataSchema, ColumnSchema, DataType, DistributionType

        # Create a simple schema
        schema = DataSchema(
            columns=[
                ColumnSchema(
                    name="age",
                    data_type=DataType.INTEGER,
                    distribution=DistributionType.UNIFORM,
                    parameters={"low": 18, "high": 65},
                    nullable=True,
                    null_probability=0.1,
                ),
                ColumnSchema(
                    name="income",
                    data_type=DataType.FLOAT,
                    distribution=DistributionType.NORMAL,
                    parameters={"mean": 50000, "std": 20000},
                    min_value=20000,
                    max_value=150000,
                ),
            ]
        )

        assert len(schema.columns) == 2
        assert schema.columns[0].name == "age"
        assert schema.columns[1].name == "income"
        assert schema.columns[0].nullable == True
        assert schema.columns[0].null_probability == 0.1
        print("✅ Schema creation successful")

    except Exception as e:
        pytest.fail(f"Failed to create schema: {e}")


def test_data_generation():
    """Test that data can be generated with proper distributions and constraints."""
    try:
        from synthetic_generator import DataSchema, ColumnSchema, DataType, DistributionType
        from synthetic_generator.generators.base import DataGenerator

        # Create a schema with various data types and constraints
        schema = DataSchema(
            columns=[
                ColumnSchema(
                    name="id",
                    data_type=DataType.INTEGER,
                    distribution=DistributionType.UNIFORM,
                    parameters={"low": 1, "high": 100},
                    unique=True,
                ),
                ColumnSchema(
                    name="score",
                    data_type=DataType.FLOAT,
                    distribution=DistributionType.NORMAL,
                    parameters={"mean": 75, "std": 15},
                    min_value=0,
                    max_value=100,
                ),
                ColumnSchema(
                    name="category",
                    data_type=DataType.CATEGORICAL,
                    distribution=DistributionType.CATEGORICAL,
                    parameters={"categories": ["A", "B", "C"]},
                ),
                ColumnSchema(
                    name="active",
                    data_type=DataType.BOOLEAN,
                    distribution=DistributionType.CATEGORICAL,
                    parameters={"categories": [True, False]},
                    nullable=True,
                    null_probability=0.2,
                ),
            ]
        )

        # Generate data
        generator = DataGenerator(schema)
        data = generator.generate(100, seed=42)

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 100
        assert "id" in data.columns
        assert "score" in data.columns
        assert "category" in data.columns
        assert "active" in data.columns
        
        # Check constraints
        assert data["score"].min() >= 0
        assert data["score"].max() <= 100
        assert data["id"].nunique() == 100  # All unique
        assert data["category"].isin(["A", "B", "C"]).all()
        
        # Check null probability
        null_count = data["active"].isna().sum()
        assert null_count > 0  # Should have some nulls with 20% probability
        
        print("✅ Data generation successful")
        print(f"   - Generated {len(data)} rows")
        print(f"   - Score range: {data['score'].min():.2f} - {data['score'].max():.2f}")
        print(f"   - Null count in 'active': {null_count}")

    except Exception as e:
        pytest.fail(f"Failed to generate data: {e}")


def test_quick_api():
    """Test the quick API functions."""
    try:
        from synthetic_generator.quick import dataset, fit
        
        # Test dataset generation from template
        data = dataset(template="customer_data", rows=10, seed=42)
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 10
        print("✅ Quick dataset generation successful")
        
        # Test fit function (should not infer distributions)
        # Create sample data
        sample_data = pd.DataFrame({
            'age': [25, 30, 35, 40, 45],
            'income': [50000, 60000, 70000, 80000, 90000],
            'category': ['A', 'B', 'A', 'C', 'B']
        })
        
        model = fit(sample_data)
        assert hasattr(model, 'sample')
        
        # Test sampling from fitted model
        new_data = model.sample(5, seed=123)
        assert isinstance(new_data, pd.DataFrame)
        assert len(new_data) == 5
        print("✅ Quick fit and sample successful")

    except Exception as e:
        pytest.fail(f"Failed to test quick API: {e}")


def test_web_ui_imports():
    """Test that web UI components can be imported correctly."""
    try:
        from synthetic_generator.web import app, api

        print("✅ Web UI imports successful")
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import web UI components: {e}")


def test_schema_inference():
    """Test schema inference without distribution inference."""
    try:
        from synthetic_generator import infer_schema
        
        # Create sample data
        sample_data = pd.DataFrame({
            'age': [25, 30, 35, 40, 45],
            'income': [50000.0, 60000.0, 70000.0, 80000.0, 90000.0],
            'category': ['A', 'B', 'A', 'C', 'B'],
            'active': [True, False, True, True, False]
        })
        
        schema = infer_schema(sample_data)
        
        assert len(schema.columns) == 4
        assert schema.columns[0].name == "age"
        assert schema.columns[1].name == "income"
        assert schema.columns[2].name == "category"
        assert schema.columns[3].name == "active"
        
        # Check that default distributions are used (not inferred)
        assert schema.columns[0].distribution is not None
        assert schema.columns[1].distribution is not None
        
        print("✅ Schema inference successful")
        print(f"   - Inferred {len(schema.columns)} columns")
        print(f"   - Age type: {schema.columns[0].data_type}")
        print(f"   - Income type: {schema.columns[1].data_type}")

    except Exception as e:
        pytest.fail(f"Failed to test schema inference: {e}")


if __name__ == "__main__":
    print("Running core functionality tests for v0.0.7...")
    test_core_imports()
    test_version()
    test_schema_creation()
    test_data_generation()
    test_quick_api()
    test_schema_inference()
    test_web_ui_imports()
    print("✅ All core functionality tests passed!")
