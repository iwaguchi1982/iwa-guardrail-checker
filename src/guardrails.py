from .summary import build_basic_summary, compute_covariate_retention

def evaluate_guardrails(df, mapping, covariates):
    summary = build_basic_summary(df, mapping)
    retention = compute_covariate_retention(df, covariates)
    
    issues = []
    recommendations = []

    n_rows = summary["total_rows"]
    
    # --- DANGER Rules ---
    # 1. Row count
    if n_rows < 5:
        issues.append({"level": "DANGER", "message": f"Too few rows for survival-oriented validation ({n_rows} < 5)."})
        recommendations.append("Ensure the dataset has at least 5-10 samples for basic checks.")

    # 2. Time checks
    if summary["time_non_numeric_count"] > 0:
        issues.append({"level": "DANGER", "message": f"Non-numeric values detected in time column ({summary['time_non_numeric_count']} cases)."})
        recommendations.append("Convert follow-up time to numeric values.")
    
    if summary["time_non_positive_count"] > 0:
        issues.append({"level": "DANGER", "message": f"Non-positive follow-up time detected ({summary['time_non_positive_count']} cases)."})
        recommendations.append("Filter out or correct rows with zero or negative follow-up time.")

    # 3. Event checks
    if summary["event_invalid_count"] > 0:
        issues.append({"level": "DANGER", "message": "Event column contains values outside {0, 1}."})
        recommendations.append("Recode event column to 0 (censored) and 1 (event).")
    
    if summary["total_events"] == 0:
        issues.append({"level": "DANGER", "message": "No events coded as 1 were detected."})
        recommendations.append("Check if the event column is correctly mapped or if the cohort is too small.")
    
    if summary["total_events"] == n_rows:
        issues.append({"level": "DANGER", "message": "All non-missing event values appear to be coded as 1."})
        recommendations.append("Ensure censoring information is correctly included.")

    # 4. Missing required
    missing_critical = [
        ("Patient ID", summary["missing_patient_id"]),
        ("Time", summary["missing_time"]),
        ("Event", summary["missing_event"]),
        ("Group", summary["missing_group"])
    ]
    for col_name, count in missing_critical:
        if count > 0:
            issues.append({"level": "DANGER", "message": f"Missing values detected in {col_name} column ({count} cases)."})
            recommendations.append(f"Remove or impute missing values in the {col_name} column.")

    # 5. Group checks
    if summary["num_groups"] < 2:
        issues.append({"level": "DANGER", "message": "Fewer than 2 valid groups detected."})
        recommendations.append("A grouping factor must have at least two distinct levels for comparison.")

    # --- CAUTION Rules ---
    # 1. Duplicates
    if summary["duplicate_patient_ids"] > 0:
        issues.append({"level": "CAUTION", "message": f"Duplicate patient IDs detected ({summary['duplicate_patient_ids']} cases)."})
        recommendations.append("Verify if duplicates are intentional (longitudinal) or data entry errors.")

    # 2. Group sizes
    valid_counts = summary["group_counts_valid"].values()
    if any(n < 5 for n in valid_counts):
        issues.append({"level": "CAUTION", "message": "One or more groups have fewer than 5 samples."})
        recommendations.append("Consider merging small groups or filtering them out for more stable estimates.")
    
    if len(valid_counts) > 1:
        max_n = max(valid_counts)
        min_n = min(valid_counts)
        if min_n > 0 and max_n / min_n >= 3:
            issues.append({"level": "CAUTION", "message": "Large imbalance detected between group sizes (ratio >= 3)."})
            recommendations.append("Interpret group comparisons with caution due to size imbalance.")

    # 3. Event counts
    if summary["total_events"] < 5:
        issues.append({"level": "CAUTION", "message": f"Very few total events detected ({summary['total_events']})."})
        recommendations.append("Low event counts limit the statistical power of survival analysis.")
    
    if any(ec == 0 for ec in summary["events_by_group"].values()):
        issues.append({"level": "CAUTION", "message": "At least one group has zero observed events."})
        recommendations.append("Hazard ratio estimation may be unstable or impossible for groups with zero events.")

    # 4. Covariates (Retention-based)
    if retention["missing_rows"] > 0:
        issues.append({"level": "CAUTION", "message": f"Missing values detected in optional covariates ({retention['missing_rows']} rows will be lost)."})
        recommendations.append(f"Covariate retention is {retention['retention_rate']:.1%}. Consider imputation for missing covariates.")

    # --- Final Judgment ---
    danger_count = sum(1 for iss in issues if iss["level"] == "DANGER")
    caution_count = sum(1 for iss in issues if iss["level"] == "CAUTION")

    if danger_count > 0:
        status = "DANGER"
    elif caution_count > 0:
        status = "CAUTION"
    else:
        status = "OK"

    return {
        "status": status,
        "issues": issues, # Unified list
        "danger_reasons": [iss["message"] for iss in issues if iss["level"] == "DANGER"], # Legacy support
        "caution_reasons": [iss["message"] for iss in issues if iss["level"] == "CAUTION"], # Legacy support
        "recommendations": sorted(list(set(recommendations))),
        "summary": summary,
        "retention": retention
    }
