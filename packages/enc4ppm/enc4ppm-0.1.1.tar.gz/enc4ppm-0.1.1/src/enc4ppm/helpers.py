import pandas as pd

def one_hot(
    df: pd.DataFrame,
    columns: list[str],
    columns_possible_values: list[list[str]],
    unknown_value='UNKNOWN'
) -> pd.DataFrame:
    df = df.copy()

    for column, possible_values in zip(columns, columns_possible_values):
        # Replace unknown values with the specified unknown_value
        df[column] = df[column].where(df[column].isin(possible_values), unknown_value)

        # Ensure the column is treated as categorical with all possible values
        dtype = pd.CategoricalDtype(categories=possible_values)
        df[column] = df[column].astype(dtype)

    # Perform one-hot encoding
    df_encoded = pd.get_dummies(df, columns=columns, drop_first=False)

    return df_encoded
