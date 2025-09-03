import pandas as pd

def inspect_dataframe(df: pd.DataFrame) -> dict:
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "head": df.head(3).to_dict('records'),
        "null_counts": df.isnull().sum().to_dict()
    }
