import pandas as pd
from .validation import validate_numeric, check_event_values

def build_basic_summary(df: pd.DataFrame, mapping: dict) -> dict:
    patient_col = mapping["patient_id"]
    time_col = mapping["time"]
    event_col = mapping["event"]
    group_col = mapping["group"]

    summary = {}

    summary["total_rows"] = int(df.shape[0])
    summary["unique_patients"] = int(df[patient_col].nunique(dropna=True))
    summary["duplicate_patient_ids"] = int(df[patient_col].duplicated().sum())
    
    # Missingness
    summary["missing_patient_id"] = int(df[patient_col].isna().sum())
    summary["missing_time"] = int(df[time_col].isna().sum())
    summary["missing_event"] = int(df[event_col].isna().sum())
    summary["missing_group"] = int(df[group_col].isna().sum())

    # Time validation
    time_numeric, time_failures = validate_numeric(df[time_col])
    summary["time_non_numeric_count"] = time_failures
    # 欠損を拾う可能性あり
    # summary["time_non_positive_count"] = int((time_numeric <= 0).sum())
    summary["time_non_positive_count"] = int(((time_numeric.notna()) & (time_numeric <= 0)).sum())

    # Event validation
    event_v, event_failures = check_event_values(df[event_col])
    summary["event_unique_values"] = event_v
    summary["event_invalid_count"] = event_failures
    
    event_numeric = pd.to_numeric(df[event_col], errors="coerce")
    summary["total_events"] = int((event_numeric == 1).sum())
    summary["total_censored"] = int((event_numeric == 0).sum())
    summary["event_rate"] = float(summary["total_events"] / summary["total_rows"]) if summary["total_rows"] > 0 else 0

    # Group statistics
    group_counts = df[group_col].fillna("(missing)").value_counts().to_dict()
    summary["group_counts"] = {str(k): int(v) for k, v in group_counts.items()}
    
    group_counts_valid = df[group_col].dropna().value_counts().to_dict()
    summary["group_counts_valid"] = {str(k): int(v) for k, v in group_counts_valid.items()}
    summary["num_groups"] = int(df[group_col].nunique(dropna=True))

    tmp = df[[group_col, event_col]].copy()
    tmp[group_col] = tmp[group_col].fillna("(missing)")
    tmp[event_col] = pd.to_numeric(tmp[event_col], errors="coerce")

    events_per_group = tmp.groupby(group_col)[event_col].apply(lambda x: int((x == 1).sum())).to_dict()
    summary["events_by_group"] = {str(k): int(v) for k, v in events_per_group.items()}

    # Covariate retention (Complete-case analysis)
    # Note: mapping keys for required are passed separately in guardrails? 
    # Let's just handle covariates passed via the dashboard.
    # Actually, summary logic is context-free of which covariates are selected in the sidebar 
    # until we pass them. Let's make summary.py take covariates as well or compute them in guardrails.
    # I'll update build_basic_summary signature.

    return summary

def compute_covariate_retention(df: pd.DataFrame, covariates: list) -> dict:
    if not covariates:
        return {"missing_rows": 0, "retention_rate": 1.0, "complete_case_rows": len(df)}
    
    missing_mask = df[covariates].isna().any(axis=1)
    missing_rows = int(missing_mask.sum())
    complete_case_rows = len(df) - missing_rows
    retention_rate = float(complete_case_rows / len(df)) if len(df) > 0 else 0
    
    return {
        "missing_rows": missing_rows,
        "complete_case_rows": complete_case_rows,
        "retention_rate": retention_rate
    }
