import json
from typing import Dict
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from .config import dq_config
from .validate_checks import validate_checks

def run_dq_pipeline(
    spark: SparkSession,
    df_dict: Dict[str, DataFrame],
    config_path: str,
    checks: Dict[str, callable] = None
) -> Dict[str, Dict[str, DataFrame]]:
    """
    DQ pipeline for multiple DataFrames using YAML config and return_mode.

    return_mode (from YAML) options:
      - "summary" -> only summary_df
      - "all" -> summary_df + clean_df + error_df
      - "summary+clean" -> summary + clean_df
      - "summary+error" -> summary + error_df

    Returns a dictionary of per-table outputs:
      {
        "table_name": {
            "clean": clean_df,       # optional
            "error": error_df,       # optional
            "summary": summary_df    # always included
        },
        ...
      }
    """

    # Load config + return_mode
    dq_config_df, return_mode = dq_config(spark, config_path)
    validate_checks(dq_config_df, checks)

    result_dict = {}
    summary_rows = []

    for table_name, df in df_dict.items():
        df = df.persist()
        try:
            total_rows = df.count()
            clean_df = df
            error_df = None

            # Wrap checks with param injection
            def _wrapped(func):
                def call(df_, row_):
                    params = json.loads(row_["params"]) if row_["params"] else {}
                    return func(df_, row_, **params)
                return call

            table_check_map = {name: _wrapped(func) for name, func in checks.items()}

            for row in dq_config_df.filter(F.col("table") == table_name).collect():
                column = row["column"]
                check_name = row["check"]

                if check_name not in table_check_map:
                    raise ValueError(f"Check {check_name} not found in provided checks")

                # Run check
                valid_df, invalid_df, _ = table_check_map[check_name](clean_df, row)
                clean_df = valid_df

                # Accumulate error_df
                if error_df:
                    error_df = error_df.unionByName(invalid_df, allowMissingColumns=True)
                else:
                    error_df = invalid_df

                # Aggregation for summary
                stats = (
                    invalid_df.agg(
                        F.count(F.lit(1)).alias("failed_count"),
                        F.to_json(
                            F.collect_list(F.struct(*[F.col(c) for c in invalid_df.columns])),
                            options={"ignoreNullFields": "false"}
                        ).alias("failed_records_json")
                    ).collect()[0]
                )

                failed_count = int(stats["failed_count"]) if stats["failed_count"] else 0
                failed_percentage = round((failed_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
                failed_records_json = stats["failed_records_json"] or "[]"

                summary_rows.append((
                    table_name,
                    column,
                    check_name,
                    total_rows,
                    failed_count,
                    failed_percentage,
                    failed_records_json
                ))

            # Build return dictionary based on return_mode
            table_result = {}
            if "summary+clean" in return_mode:
                table_result["clean"] = clean_df
            if "summary+error" in return_mode:
                table_result["error"] = error_df
            if "all" in return_mode:
                table_result['clean'] = clean_df
                table_result['error'] = error_df

            if table_result:
                result_dict[table_name.lower()] = table_result

        finally:
            df.unpersist()
    
    summary_schema = "table_name STRING, column_name STRING, check_type STRING, total_rows LONG, failed_count LONG, failed_percentage DOUBLE, failed_records_json STRING"
    summary_df = spark.createDataFrame(summary_rows, schema=summary_schema)

    result_dict['summary'] = summary_df

    return result_dict
