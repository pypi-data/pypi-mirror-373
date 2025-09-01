import pandas as pd

def clean_missing(df, strategy="mean"):
    if strategy == "mean":
        return df.fillna(df.mean())
    elif strategy == "median":
        return df.fillna(df.median())
    elif strategy == "drop":
        return df.dropna()
    else:
        raise ValueError("Invalid strategy")
