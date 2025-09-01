from pyspark.sql import DataFrame

def validate_checks(
    dq_config_df: DataFrame, 
    check_function_map: dict
):
    """
    Validate that all checks in dq_config_df are defined 
    in check_function_map (built-in + custom).

    Parameters
    ----------
    dq_config_df : DataFrame
        Flattened DQ config dataframe with columns (table, column, check, params)
    check_function_map : dict
        Dictionary of available checks {check_name: function}

    Raises
    ------
    ValueError
        If any checks in config.yml are not implemented
    """
    configured_checks = [row["check"] for row in dq_config_df.collect()]
    available_checks = set(check_function_map.keys())

    missing_checks = set(configured_checks) - available_checks

    if missing_checks:
        raise ValueError(
            f"The following checks are defined in config.yml but not implemented: {missing_checks}. "
            f"Please add them to custom_checks or remove from YAML."
        )
    else:
        print("All configured checks are available.")
