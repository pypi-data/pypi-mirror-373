import pandas as pd
import numpy as np
from collections import Counter


def initial_data_overview(df: pd.DataFrame, target: str = None, is_classification: bool = True, verbose: bool = True):
    """
    Perform an initial structured overview of a dataset.
    
    This function checks for missing values, duplicates, outliers, validity issues, 
    low variance features, and (optionally) target distribution. 
    Results are summarized and optionally printed in a consistent format.
    
    Parameters
    ----------
    df : pd.DataFrame
        The input dataset.
    target : str, optional
        Target column name (for supervised tasks). Default is None.
    is_classification : bool, default=True
        Whether the task is classification (True) or regression (False).
    verbose : bool, default=True
        If True, prints results to console. If False, only returns summary dictionary.
    
    Returns
    -------
    dict
        A dictionary summarizing missing values, duplicates, outliers, validity issues,
        and low variance features.
    """
    summary = {}

    # ==============================
    # 1. Missing Values
    # ==============================
    missing = df.isna().sum()
    missing_pct = df.isna().mean() * 100

    missing_categories = {
        "Small (≤5%)": {"cols": [], "advice": "Use simple imputation (mean/median/mode) or drop rows."},
        "Moderate (5–10%)": {"cols": [], "advice": "Drop rows if dataset is large, or use statistical/model-based imputation."},
        "Large (10–40%)": {"cols": [], "advice": "Consider dropping the feature or using advanced imputation (KNN, regression, interpolation)."},
        "Severe (>40%)": {"cols": [], "advice": "Feature has too many missing values – better to drop it."}
    }

    for col in df.columns:
        if missing[col] > 0:
            pct = missing_pct[col]
            if pct <= 5:
                missing_categories["Small (≤5%)"]["cols"].append(f"{col} ({pct:.2f}%)")
            elif pct <= 10:
                missing_categories["Moderate (5–10%)"]["cols"].append(f"{col} ({pct:.2f}%)")
            elif pct <= 40:
                missing_categories["Large (10–40%)"]["cols"].append(f"{col} ({pct:.2f}%)")
            else:
                missing_categories["Severe (>40%)"]["cols"].append(f"{col} ({pct:.2f}%)")

    summary["missing_values"] = missing_categories

    # ==============================
    # 2. Duplicates
    # ==============================
    dup_count = df.duplicated().sum()
    summary["duplicates"] = {"count": int(dup_count)}

    # ==============================
    # 3. Outliers (IQR Method)
    # ==============================
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_results = []

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        pct = len(outliers) / len(df) * 100
        if len(outliers) > 0:
            outlier_results.append({"feature": col, "count": int(len(outliers)), "percentage": round(pct, 2)})

    outlier_categories = {
        "Small (≤1%)": {"cols": [], "advice": "Generally safe, ignore or simple handling."},
        "Moderate (1–5%)": {"cols": [], "advice": "Check distribution, consider mild treatment."},
        "Large (5–15%)": {"cols": [], "advice": "Consider transformations (log/boxcox) or trimming."},
        "Severe (>15%)": {"cols": [], "advice": "High risk feature – investigate or drop."}
    }

    if outlier_results:
        for r in outlier_results:
            col, pct = r["feature"], r["percentage"]
            if pct <= 1:
                outlier_categories["Small (≤1%)"]["cols"].append(f"{col} ({pct:.2f}%)")
            elif pct <= 5:
                outlier_categories["Moderate (1–5%)"]["cols"].append(f"{col} ({pct:.2f}%)")
            elif pct <= 15:
                outlier_categories["Large (5–15%)"]["cols"].append(f"{col} ({pct:.2f}%)")
            else:
                outlier_categories["Severe (>15%)"]["cols"].append(f"{col} ({pct:.2f}%)")

    summary["outliers"] = outlier_categories

    # ==============================
    # 4. Validity Checks
    # ==============================
    validity_issues = []
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            if (df[col] < 0).any():
                validity_issues.append(f"Column '{col}' contains negative values")
        elif df[col].dtype == 'object':
            if df[col].str.strip().eq('').any():
                validity_issues.append(f"Column '{col}' contains empty strings")

    summary["validity"] = validity_issues

    # ==============================
    # 5. Low Variance Features
    # ==============================
    low_var = [col for col in df.columns if df[col].nunique() <= 1]
    summary["low_variance"] = low_var

    # ==============================
    # Verbose Print
    # ==============================
    if verbose:
        print("=" * 50)
        print("📊 INITIAL DATA OVERVIEW")
        print("=" * 50)

        # Missing values
        print("\n[1] MISSING VALUES")
        if all(len(info["cols"]) == 0 for info in missing_categories.values()):
            print("✅ No missing values detected.")
        else:
            for cat, info in missing_categories.items():
                if info["cols"]:
                    print(f"\n📊 {cat}")
                    print(f" - Number of features: {len(info['cols'])}")
                    print(f" - Features: {info['cols']}")
                    print(f" - Recommendation: {info['advice']}")

        # Duplicates
        print("\n[2] DUPLICATES")
        if dup_count > 0:
            print(f"⚠️ Number of duplicate rows: {dup_count}")
        else:
            print("✅ No duplicate rows detected.")

        # Outliers
        print("\n[3] OUTLIERS (IQR METHOD)")
        if not outlier_results:
            print("✅ No outliers detected.")
        else:
            for cat, info in outlier_categories.items():
                if info["cols"]:
                    print(f"\n📊 {cat}")
                    print(f" - Number of features: {len(info['cols'])}")
                    print(f" - Features: {info['cols']}")
                    print(f" - Recommendation: {info['advice']}")

        # Validity
        print("\n[4] VALIDITY CHECK")
        if validity_issues:
            for issue in validity_issues:
                print(f"⚠️ {issue}")
        else:
            print("✅ No validity issues detected.")

        # Low variance
        print("\n[5] LOW VARIANCE FEATURES")
        if low_var:
            print(f"⚠️ Columns with constant value: {low_var}")
        else:
            print("✅ No constant columns detected.")

        print("\n" + "=" * 50)
        print("✅ INITIAL DATA CHECK COMPLETE")
        print("=" * 50)

    return summary

def check_class_balance(y, imbalance_threshold=0.2):
    """
    Check class balance in a target variable and provide recommendations.
    
    Parameters
    ----------
    y : array-like or pd.Series
        Target labels.
    imbalance_threshold : float, default=0.2
        Threshold for imbalance (max difference ratio between classes).
    
    Returns
    -------
    dict
        Dictionary containing class distribution, imbalance status, 
        and recommended actions.
    """
    
    counts = Counter(y)
    total = sum(counts.values())
    distribution = {cls: round(cnt/total, 4) for cls, cnt in counts.items()}
    
    # Check imbalance based on max-min ratio
    imbalance_ratio = max(distribution.values()) - min(distribution.values())
    is_imbalanced = imbalance_ratio > imbalance_threshold
    
    # Recommendations
    if is_imbalanced:
        recommendation = (
            "⚠️ The dataset appears imbalanced.\n"
            "- If the imbalance reflects the real-world distribution (e.g., fraud detection, medical rare cases), "
            "do NOT artificially balance the data. Instead, consider using F1-score, Precision-Recall AUC, "
            "or other metrics that handle imbalance better.\n"
            "- If the imbalance is undesired, consider resampling techniques "
            "(oversampling minority, undersampling majority, or SMOTE).\n"
            "- You can also try using class weights in your model."
        )
    else:
        recommendation = (
            "✅ The dataset appears balanced.\n"
            "- Standard metrics like Accuracy, Precision, Recall, and ROC-AUC are reliable.\n"
            "- No resampling or weighting is necessary."
        )
    
    return {
        "class_distribution": distribution,
        "imbalance_ratio": round(imbalance_ratio, 4),
        "is_imbalanced": is_imbalanced,
        "recommendation": recommendation
    }

