import pytest
import pandas as pd
from claridata import Claridata  # Correct import for Datacraft package

def test_pipeline():
    # Sample DataFrame with missing values
    df = pd.DataFrame({
        "Age": [25, None, 35],
        "Salary": [50000, 60000, None],
        "Dept": ["HR", None, "IT"]
    })
    
    # Initialize DataMolder with auto mode
    dm = Claridata(df, mode='auto', verbose=False)
    df_cleaned = dm.output
    
    # Assert that there are no missing values after processing
    assert df_cleaned.isna().sum().sum() == 0
    
    # Assert that categorical columns have been encoded (label or one-hot)
    assert any(col.startswith("Dept") for col in df_cleaned.columns)
