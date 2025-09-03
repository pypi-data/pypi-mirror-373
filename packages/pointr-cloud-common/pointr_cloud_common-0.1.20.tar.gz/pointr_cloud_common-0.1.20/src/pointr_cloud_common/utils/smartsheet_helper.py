import smartsheet
import pandas as pd
from typing import List, Dict, Any, Callable


def _version_gte(version: str, minimum: str) -> bool:
    """Return True if version string is >= minimum."""
    try:
        v_parts = [int(p) for p in str(version).split(".")]
        m_parts = [int(p) for p in str(minimum).split(".")]
    except ValueError:
        return False

    # Pad with zeros
    length = max(len(v_parts), len(m_parts))
    v_parts += [0] * (length - len(v_parts))
    m_parts += [0] * (length - len(m_parts))
    return tuple(v_parts) >= tuple(m_parts)


def get_smartsheet_as_dataframe(token: str, sheet_id: str) -> pd.DataFrame:
    ss = smartsheet.Smartsheet(token)
    ss.errors_as_exceptions(True)
    sheet = ss.Sheets.get_sheet(sheet_id)
    col_map = {col.id: col.title for col in sheet.columns}
    data = []
    for row in sheet.rows:
        row_data = {col_map[cell.column_id]: cell.display_value for cell in row.cells}
        data.append(row_data)
    df = pd.DataFrame(data)
    return df


def filter_environments(
    df: pd.DataFrame,
    version_value: str,
    version_column: str,
    is_active_column: str,
    api_version_column: str,
    client_name_column: str,
    environment_name_column: str,
    api_endpoint_column: str,
    client_id_column: str,
    client_secret_column: str,
    min_dashboard_version: str = None,
    version_compare_func: Callable[[str, str], bool] = _version_gte,
) -> List[Dict[str, Any]]:
    # Defensive: ensure expected columns exist
    for col in [version_column, is_active_column, api_version_column]:
        if col not in df.columns:
            raise ValueError(f"Expected column '{col}' not found in Smartsheet.")

    mask = (
        (df[version_column].astype(str).str.upper() == version_value.upper())
        & (df[is_active_column].astype(str).str.lower() == "yes")
    )
    if min_dashboard_version:
        mask = mask & df[api_version_column].apply(lambda v: version_compare_func(v, min_dashboard_version))

    envs = df[mask].copy()
    envs["ENVIRONMENT_NAME"] = envs[client_name_column] + " - " + envs[environment_name_column]
    columns = [
        "ENVIRONMENT_NAME",
        api_endpoint_column,
        client_id_column,
        client_secret_column,
    ]
    if api_version_column in envs.columns:
        columns.append(api_version_column)
    result = envs[columns].dropna()
    result[api_endpoint_column] = result[api_endpoint_column].str.rstrip('/')
    return result.to_dict(orient="records") 