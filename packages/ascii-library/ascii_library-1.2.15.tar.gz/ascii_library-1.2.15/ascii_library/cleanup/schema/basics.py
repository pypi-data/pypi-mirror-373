import re

import pandas as pd
import yaml

try:
    import pyspark
except ImportError:
    print("you may need pyspark for the full functionality of this package")


def clean_column_name(column_name: str) -> str:
    """Clean up a column name by converting it to snake case."""
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    column_name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", column_name)
    column_name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", column_name)
    column_name = column_name.strip()
    column_name = re.sub(r"\s+", " ", column_name)
    column_name = (
        column_name.lower()
        .strip()
        .replace(" ", "_")
        .replace(".", "_")
        .replace(":", "_")
        .replace("-", "_")
        .replace(",_", "_")
        .replace("__+", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("ä", "ae")
        .replace("ü", "ue")
        .replace("ö", "oe")
        .replace("ß", "ss")
        .replace("&", "_")
        .replace("/", "_per_")
        .replace("\n", "_")
        .replace("%", "_percent")
        .replace("=", "_eq_")
    )

    column_name = re.sub(r"__+", "_", column_name)
    column_name = column_name.strip("_")
    return column_name


def clean_pandas_columns(df: pd.DataFrame):
    """Column cleanup function. Snake cases everything"""
    df.columns = [clean_column_name(col) for col in df.columns]
    return df


def clean_spark_columns(df: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:  # type: ignore
    """Apply column name cleanup for PySpark DataFrame."""
    for col in df.columns:
        df = df.withColumnRenamed(col, clean_column_name(col))
    return df


# Function to read and modify DBT schema YAML
def clean_dbt_schema_yaml(file_path: str):  # noqa: C901
    """Read a DBT schema YAML file, clean column names, and return the modified schema."""
    with open(file_path, "r") as file:
        schema = yaml.safe_load(file)

    # Assuming the schema follows the structure of DBT schema.yml
    if "models" in schema:
        for model in schema["models"]:
            if "columns" in model:
                for column in model["columns"]:
                    if "name" in column:
                        column["name"] = clean_column_name(column["name"])

    return schema
