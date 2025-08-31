import pandas as pd
import polars as pl


def match_df(
    description_file_path: str,
    df,
    hs_code_version: str,
    hs_code_column_name="hs_code",
    new_column_name="hs_code_description",
):
    is_pandas = False

    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)
        is_pandas = True

    # Read and filter the description file
    df_description = pl.read_parquet(description_file_path)
    df_description = df_description.filter(pl.col("version") == hs_code_version)

    # Perform join.
    df = df.join(
        df_description.select(
            pl.col("code").alias(hs_code_column_name),
            pl.col("description").alias(new_column_name),
        ),
        on=hs_code_column_name,
        how="left",
        coalesce=True,
    )

    if is_pandas:
        df = df.to_pandas()

    return df
