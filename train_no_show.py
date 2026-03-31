import os
import glob
import warnings
from datetime import datetime
from typing import Dict, Tuple, Optional

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    RocCurveDisplay,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

warnings.filterwarnings("ignore", category=UserWarning)

try:
    from imblearn.over_sampling import SMOTE
    from imblearn.pipeline import Pipeline as ImbPipeline
except ImportError:  # fallback if imblearn missing
    SMOTE = None
    ImbPipeline = Pipeline

try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None

RANDOM_STATE = 42
DATA_DIR = "data"
OUTPUT_DIR = "outputs"


def ensure_output_dir(path: str = OUTPUT_DIR) -> None:
    os.makedirs(path, exist_ok=True)


def pick_dataset(data_dir: str = DATA_DIR) -> str:
    """Pick the no-show dataset if present, else first CSV."""
    preferred = ["KaggleV2-May-2016.csv", "appointments.csv", "noshow.csv"]
    for name in preferred:
        candidate = os.path.join(data_dir, name)
        if os.path.exists(candidate):
            return candidate
    csvs = glob.glob(os.path.join(data_dir, "*.csv"))
    if not csvs:
        raise FileNotFoundError("No CSV files found in /data directory")
    return csvs[0]


def load_raw_dataframe(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # standardize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def add_waiting_days(df: pd.DataFrame) -> pd.DataFrame:
    if "scheduledday" in df.columns and "appointmentday" in df.columns:
        df["scheduledday"] = pd.to_datetime(df["scheduledday"], errors="coerce")
        df["appointmentday"] = pd.to_datetime(df["appointmentday"], errors="coerce")
        df["waiting_days"] = (df["appointmentday"] - df["scheduledday"]).dt.days
    return df


def identify_target(df: pd.DataFrame) -> str:
    candidates = ["no-show", "no_show", "noshow", "status", "outcome", "target"]
    for col in df.columns:
        if col.lower() in candidates:
            return col
    raise ValueError("Could not find a target column (expected no-show/outcome)")


def clean_and_split(df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.Series]:
    y = df[target_col]
    X = df.drop(columns=[target_col])

    if y.dtype == object or y.dtype == "category":
        y = y.str.strip().str.lower().replace({"yes": 1, "y": 1, "1": 1, "true": 1, "no": 0, "n": 0, "0": 0, "false": 0})
    y = y.astype(int)

    drop_cols = [c for c in X.columns if "id" in c or c in {"appointmentid", "patientid"}]
    X = X.drop(columns=drop_cols, errors="ignore")

    X = add_waiting_days(pd.concat([X, y], axis=1)).drop(columns=[target_col], errors="ignore")

    datetime_cols = [c for c in X.columns if str(X[c].dtype).startswith("datetime64")]
    X = X.drop(columns=datetime_cols + ["scheduledday", "appointmentday"], errors="ignore")

    return X, y


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    cat_cols = [c for c in X.columns if X[c].dtype == "object" or str(X[c].dtype).startswith("category")]
    num_cols = [c for c in X.columns if c not in cat_cols]

    numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])
    categorical_transformer = Pipeline(steps=[("encoder", OneHotEncoder(handle_unknown="ignore"))])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, num_cols),
            ("cat", categorical_transformer, cat_cols),
        ],
        remainder="drop",
    )
    return preprocessor


def make_models(class_weight: Optional[Dict[int, float]], use_smote: bool, preprocessor: ColumnTransformer):
    models = {}

    lr = LogisticRegression(max_iter=1000, class_weight=class_weight, n_jobs=1)
    rf = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_leaf=2,
        class_weight=class_weight,
        n_jobs=1,
        random_state=RANDOM_STATE,
    )

    if SMOTE and use_smote:
        lr_pipe = ImbPipeline([
            ("preprocess", preprocessor),
            ("smote", SMOTE(random_state=RANDOM_STATE)),
            ("model", lr),
        ])
        rf_pipe = ImbPipeline([
            ("preprocess", preprocessor),
            ("model", rf),
        ])
    else:
        lr_pipe = Pipeline([
            ("preprocess", preprocessor),
            ("model", lr),
        ])
        rf_pipe = Pipeline([
            ("preprocess", preprocessor),
            ("model", rf),
        ])

    models["LogisticRegression"] = lr_pipe
    models["RandomForest"] = rf_pipe

    if XGBClassifier is not None:
        xgb_model = XGBClassifier(
            random_state=RANDOM_STATE,
            n_estimators=400,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary:logistic",
            eval_metric="logloss",
            n_jobs=1,
            scale_pos_weight=class_weight.get(1, 1) if class_weight else 1,
        )
        if SMOTE and use_smote:
            xgb_pipe = ImbPipeline([
                ("preprocess", preprocessor),
                ("smote", SMOTE(random_state=RANDOM_STATE)),
                ("model", xgb_model),
            ])
        else:
            xgb_pipe = Pipeline([
                ("preprocess", preprocessor),
                ("model", xgb_model),
            ])
        models["XGBoost"] = xgb_pipe

    return models


def grid_search_if_needed(model_name: str, model: Pipeline, X_train, y_train) -> Pipeline:
    return model


def tune_threshold(y_true, probas, positive_label=1) -> Tuple[float, float]:
    thresholds = np.linspace(0.1, 0.9, 17)
    best_thresh, best_f1 = 0.5, -1
    best_recall = 0
    for t in thresholds:
        preds = (probas >= t).astype(int)
        f1 = f1_score(y_true, preds)
        rec = recall_score(y_true, preds)
        if f1 > best_f1 or (np.isclose(f1, best_f1) and rec > best_recall):
            best_f1 = f1
            best_recall = rec
            best_thresh = t
    return best_thresh, best_f1


def evaluate(model, X_test, y_test, threshold=0.5) -> Dict[str, float]:
    probas = model.predict_proba(X_test)[:, 1]
    preds = (probas >= threshold).astype(int)
    return {
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision_score(y_test, preds, zero_division=0),
        "recall": recall_score(y_test, preds),
        "f1": f1_score(y_test, preds),
        "roc_auc": roc_auc_score(y_test, probas),
        "preds": preds,
        "probas": probas,
    }


def plot_confusion(y_true, y_pred, normalized_path: str) -> None:
    cm = confusion_matrix(y_true, y_pred, normalize="true")
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt=".2f", cmap="Blues", xticklabels=["Show", "No-Show"], yticklabels=["Show", "No-Show"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Normalized Confusion Matrix")
    plt.tight_layout()
    plt.savefig(normalized_path)
    plt.close()


def plot_roc(y_true, probas, path: str) -> None:
    plt.figure(figsize=(5, 4))
    RocCurveDisplay.from_predictions(y_true, probas)
    plt.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def plot_feature_importance(model, preprocessor, path: str, top_n: int = 10) -> None:
    feature_names = preprocessor.get_feature_names_out()
    model_step = model.named_steps.get("model") if hasattr(model, "named_steps") else None

    importances = None
    if hasattr(model_step, "feature_importances_"):
        importances = model_step.feature_importances_
    elif hasattr(model_step, "coef_"):
        importances = np.ravel(np.abs(model_step.coef_))

    if importances is None:
        print("Feature importance not available for this model; skipping plot.")
        return

    importance_df = pd.DataFrame({"feature": feature_names, "importance": importances})
    top = importance_df.sort_values("importance", ascending=False).head(top_n)

    plt.figure(figsize=(8, 6))
    sns.barplot(data=top, y="feature", x="importance", orient="h", palette="viridis")
    plt.title("Top Features")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def log_metrics(log_path: str, info: Dict) -> None:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"===== Run at {datetime.now().isoformat()} =====\n")
        for k, v in info.items():
            f.write(f"{k}: {v}\n")
        f.write("\n")


def main():
    ensure_output_dir()

    data_path = pick_dataset()
    df = load_raw_dataframe(data_path)
    target_col = identify_target(df)
    X, y = clean_and_split(df, target_col)

    preprocessor = build_preprocessor(X)

    class_counts = y.value_counts().to_dict()
    class_weight = {
        0: class_counts.get(1, 1) / class_counts.get(0, 1),
        1: 1.0,
    }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    use_smote = SMOTE is not None and y_train.value_counts().min() > 0

    models = make_models(class_weight=class_weight, use_smote=use_smote, preprocessor=preprocessor)

    best_model_name, best_model, best_metrics, best_threshold = None, None, {}, 0.5

    for name, model in models.items():
        print(f"Training {name}...")
        tuned_model = grid_search_if_needed(name, model, X_train, y_train)
        tuned_model.fit(X_train, y_train)

        train_probas = tuned_model.predict_proba(X_train)[:, 1]
        threshold, _ = tune_threshold(y_train, train_probas)

        metrics = evaluate(tuned_model, X_test, y_test, threshold)
        print(f"{name} F1={metrics['f1']:.3f} Recall={metrics['recall']:.3f} Threshold={threshold:.2f}")

        if not best_model or metrics["f1"] > best_metrics.get("f1", -1) or (
            np.isclose(metrics["f1"], best_metrics.get("f1", -1)) and metrics["recall"] > best_metrics.get("recall", -1)
        ):
            best_model_name = name
            best_model = tuned_model
            best_metrics = metrics
            best_threshold = threshold

    if best_model is None:
        raise RuntimeError("No model was trained successfully.")

    # Save artifacts
    joblib.dump({"model": best_model, "threshold": best_threshold}, os.path.join(OUTPUT_DIR, "best_model.pkl"))

    plot_confusion(y_test, (best_metrics["probas"] >= best_threshold).astype(int), os.path.join(OUTPUT_DIR, "confusion_matrix.png"))
    plot_roc(y_test, best_metrics["probas"], os.path.join(OUTPUT_DIR, "roc_curve.png"))
    plot_feature_importance(best_model, preprocessor, os.path.join(OUTPUT_DIR, "feature_importance.png"))

    log_info = {
        "dataset": os.path.basename(data_path),
        "shape": df.shape,
        "class_distribution": class_counts,
        "best_model": best_model_name,
        "threshold": round(best_threshold, 3),
        "metrics": {k: round(v, 4) for k, v in best_metrics.items() if k not in {"preds", "probas"}},
    }
    log_metrics(os.path.join(OUTPUT_DIR, "training_log.txt"), log_info)

    print("Training complete.")
    print(log_info)


if __name__ == "__main__":
    main()
