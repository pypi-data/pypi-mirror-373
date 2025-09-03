"""
Test file for basic functions in v0.0.7.
"""

import pytest
import sys
import os
import pandas as pd

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def test_data_types():
    """Test that all data types are available and working."""
    try:
        from synthetic_generator import DataType
        
        # Check that all data types are available
        expected_types = [
            'INTEGER', 'FLOAT', 'STRING', 'BOOLEAN', 'CATEGORICAL',
            'EMAIL', 'PHONE', 'ADDRESS', 'NAME', 'DATE', 'DATETIME'
        ]
        
        for type_name in expected_types:
            assert hasattr(DataType, type_name)
            data_type = getattr(DataType, type_name)
            assert data_type is not None
        
        print("✅ All data types available")
        print(f"   - Available types: {[t.value for t in DataType]}")

    except Exception as e:
        pytest.fail(f"Failed to test data types: {e}")


def test_distribution_types():
    """Test that all distribution types are available."""
    try:
        from synthetic_generator import DistributionType
        
        # Check that all distribution types are available
        expected_distributions = [
            'UNIFORM', 'NORMAL', 'EXPONENTIAL', 'GAMMA', 'BETA', 'WEIBULL',
            'POISSON', 'BINOMIAL', 'GEOMETRIC', 'CATEGORICAL', 'CONSTANT'
        ]
        
        for dist_name in expected_distributions:
            assert hasattr(DistributionType, dist_name)
            dist_type = getattr(DistributionType, dist_name)
            assert dist_type is not None
        
        print("✅ All distribution types available")
        print(f"   - Available distributions: {[d.value for d in DistributionType]}")

    except Exception as e:
        pytest.fail(f"Failed to test distribution types: {e}")


def test_basic_imports():
    """Test that basic modules can be imported."""
    try:
        from synthetic_generator import schemas, generators, export, quick

        print("✅ Basic module imports successful")
        assert True
    except Exception as e:
        pytest.fail(f"Failed to import basic modules: {e}")


def test_schema_creation():
    """Test that schemas can be created with proper types."""
    try:
        from synthetic_generator import DataSchema, ColumnSchema, DataType, DistributionType

        # Create a comprehensive schema
        schema = DataSchema(
            columns=[
                ColumnSchema(
                    name="age",
                    data_type=DataType.INTEGER,
                    distribution=DistributionType.UNIFORM,
                    parameters={"low": 18, "high": 65},
                    nullable=True,
                    null_probability=0.05,
                ),
                ColumnSchema(
                    name="income",
                    data_type=DataType.FLOAT,
                    distribution=DistributionType.NORMAL,
                    parameters={"mean": 50000, "std": 20000},
                    min_value=20000,
                    max_value=150000,
                ),
                ColumnSchema(
                    name="category",
                    data_type=DataType.CATEGORICAL,
                    distribution=DistributionType.CATEGORICAL,
                    parameters={"categories": ["A", "B", "C"]},
                ),
            ]
        )

        assert len(schema.columns) == 3
        assert schema.columns[0].name == "age"
        assert schema.columns[1].name == "income"
        assert schema.columns[2].name == "category"
        
        # Check constraints
        assert schema.columns[0].nullable == True
        assert schema.columns[0].null_probability == 0.05
        assert schema.columns[1].min_value == 20000
        assert schema.columns[1].max_value == 150000
        
        print("✅ Schema creation successful with constraints")

    except Exception as e:
        pytest.fail(f"Failed to create schema: {e}")


def test_web_ui_basic():
    """Test that web UI can be imported and basic functionality works."""
    try:
        from synthetic_generator.web import app, api

        print("✅ Web UI import successful")
        assert True
    except Exception as e:
        pytest.fail(f"Failed to import web UI: {e}")


def test_export_functionality():
    """Test that export functionality works."""
    try:
        from synthetic_generator.export import export_data
        import pandas as pd
        import tempfile
        import os
        
        # Create sample data
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'score': [85.5, 92.0, 78.5]
        })
        
        # Test CSV export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            export_data(data, 'csv', filepath=f.name)
            assert os.path.exists(f.name)
            os.unlink(f.name)
        
        # Test JSON export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_data(data, 'json', filepath=f.name)
            assert os.path.exists(f.name)
            os.unlink(f.name)
        
        print("✅ Export functionality successful")

    except Exception as e:
        pytest.fail(f"Failed to test export functionality: {e}")


if __name__ == "__main__":
    print("Running function tests for v0.0.7...")
    test_data_types()
    test_distribution_types()
    test_basic_imports()
    test_schema_creation()
    test_web_ui_basic()
    test_export_functionality()
    print("✅ All function tests passed!")
