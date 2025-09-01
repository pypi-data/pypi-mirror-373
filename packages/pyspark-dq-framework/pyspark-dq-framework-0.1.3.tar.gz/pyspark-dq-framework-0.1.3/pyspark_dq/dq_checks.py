from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, row_number
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType

# Common schema for (optional) logs; we won't compute counts here
error_schema = StructType([
    StructField("table", StringType()),
    StructField("column", StringType()),
    StructField("check_type", StringType()),
    StructField("passed", BooleanType()),
    StructField("invalid_count", IntegerType())
])

def _empty_log(df, table, column, check_type):
    # No counts here to avoid triggering actions
    return df.sparkSession.createDataFrame(
        [(table, column, check_type, None, None)],
        schema=error_schema
    )

def null_check(df, row):
    table = row["table"]; column = row["column"]; check_type = "null_check"
    valid_df = df.filter(col(column).isNotNull())
    invalid_df = df.filter(col(column).isNull()) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def unique_check(df, row):
    table = row["table"]; column = row["column"]; check_type = "unique_check"
    window_spec = Window.partitionBy(column).orderBy(column)
    df_with_rn = df.withColumn("row_num", row_number().over(window_spec))
    valid_df = df_with_rn.filter(col("row_num") == 1).drop("row_num")
    invalid_df = df_with_rn.filter(col("row_num") > 1).drop("row_num") \
                           .withColumn("table", lit(table)) \
                           .withColumn("column", lit(column)) \
                           .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def allowed_values_check(df, row, allowed_values):
    table = row["table"]; column = row["column"]; check_type = "allowed_values_check"
    valid_df = df.filter(col(column).isin(allowed_values))
    invalid_df = df.filter(~col(column).isin(allowed_values)) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def range_check(df, row, min_value=None, max_value=None):
    table = row["table"]; column = row["column"]; check_type = "range_check"
    # Build condition robustly
    if min_value is None and max_value is None:
        condition = col(column).isNotNull()  # trivially true for non-nulls
    elif min_value is None:
        condition = col(column) <= max_value
    elif max_value is None:
        condition = col(column) >= min_value
    else:
        condition = (col(column) >= min_value) & (col(column) <= max_value)

    valid_df = df.filter(condition)
    invalid_df = df.filter(~condition) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def non_negative_check(df, row):
    table = row["table"]; column = row["column"]; check_type = "non_negative_check"
    valid_df = df.filter(col(column) >= 0)
    invalid_df = df.filter(col(column) < 0) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def regex_check(df, row, pattern):
    table = row["table"]; column = row["column"]; check_type = "regex_check"
    valid_df = df.filter(col(column).rlike(pattern))
    invalid_df = df.filter(~col(column).rlike(pattern)) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def not_empty_check(df, row):
    table = row["table"]; column = row["column"]; check_type = "not_empty_check"
    # We skip counting here; the pipeline will compute table counts once.
    valid_df = df
    invalid_df = df.limit(0) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df

def data_type_check(df, row):
    table = row["table"]; column = row["column"]; check_type = "data_type_check"
    # Expect type must be provided via params at runtime; checks runner will handle logic if needed.
    # Keeping as a pass-through placeholder; real type enforcement is usually schema-level.
    valid_df = df
    invalid_df = df.limit(0) \
                   .withColumn("table", lit(table)) \
                   .withColumn("column", lit(column)) \
                   .withColumn("check_type", lit(check_type))
    log_df = _empty_log(df, table, column, check_type)
    return valid_df, invalid_df, log_df
