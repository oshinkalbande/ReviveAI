import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

DATA_PATH = "data/ml_ready_data.csv"

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("REVIVEAI - AI RECOVERY PREDICTION MODEL")
print("=" * 60)

print("\nDataset loaded successfully.")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# --------------------------------------------------
# 2. DEFINE TARGET
# --------------------------------------------------

TARGET = "recovered"

print("\nTarget variable:", TARGET)

print("\nTarget distribution:")
print(df[TARGET].value_counts())

print("\nTarget percentage:")
print(df[TARGET].value_counts(normalize=True) * 100)


# --------------------------------------------------
# 3. SELECT ML FEATURES
# --------------------------------------------------

features = [
    "invoice_amount",
    "days_overdue",
    "previous_payments",
    "previous_late_payments",
    "average_payment_delay",
    "payment_failures",
    "communication_count",
    "last_contact_days",
    "discount_used",
    "customer_lifetime_value",
    "payment_delay",
    "invoice_age",
    "late_payment_ratio",
    "payment_reliability_score",
    "payment_behavior_score",
    "communication_effectiveness",
    "customer_value_score",
    "overdue_risk_score"
]


# --------------------------------------------------
# 4. CHECK FEATURES
# --------------------------------------------------

missing_features = [
    feature for feature in features
    if feature not in df.columns
]

if missing_features:
    print("\nERROR: Missing features:")
    print(missing_features)
    raise ValueError("Some ML features are missing from dataset.")


print("\nNumber of ML features:", len(features))

X = df[features].copy()
y = df[TARGET].copy()


# --------------------------------------------------
# 5. CLEAN ML DATA
# --------------------------------------------------

X = X.replace([np.inf, -np.inf], np.nan)

X = X.fillna(X.median(numeric_only=True))

print("\nMissing values after cleaning:")
print(X.isnull().sum().sum())


# --------------------------------------------------
# 6. TRAIN / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# --------------------------------------------------
# 7. RANDOM FOREST MODEL
# --------------------------------------------------

print("\n" + "=" * 60)
print("TRAINING RANDOM FOREST")
print("=" * 60)

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    class_weight="balanced"
)

rf_model.fit(X_train, y_train)

rf_predictions = rf_model.predict(X_test)

rf_probabilities = rf_model.predict_proba(X_test)[:, 1]


# --------------------------------------------------
# 8. RANDOM FOREST METRICS
# --------------------------------------------------

rf_accuracy = accuracy_score(y_test, rf_predictions)
rf_precision = precision_score(y_test, rf_predictions, zero_division=0)
rf_recall = recall_score(y_test, rf_predictions, zero_division=0)
rf_f1 = f1_score(y_test, rf_predictions, zero_division=0)
rf_auc = roc_auc_score(y_test, rf_probabilities)

print("\nRandom Forest Results:")
print("Accuracy :", round(rf_accuracy, 4))
print("Precision:", round(rf_precision, 4))
print("Recall   :", round(rf_recall, 4))
print("F1 Score :", round(rf_f1, 4))
print("ROC-AUC  :", round(rf_auc, 4))

print("\nClassification Report:")
print(classification_report(
    y_test,
    rf_predictions,
    zero_division=0
))


# --------------------------------------------------
# 9. LOGISTIC REGRESSION MODEL
# --------------------------------------------------

print("\n" + "=" * 60)
print("TRAINING LOGISTIC REGRESSION")
print("=" * 60)

lr_model = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ))
])

lr_model.fit(X_train, y_train)

lr_predictions = lr_model.predict(X_test)

lr_probabilities = lr_model.predict_proba(X_test)[:, 1]


# --------------------------------------------------
# 10. LOGISTIC REGRESSION METRICS
# --------------------------------------------------

lr_accuracy = accuracy_score(y_test, lr_predictions)
lr_precision = precision_score(y_test, lr_predictions, zero_division=0)
lr_recall = recall_score(y_test, lr_predictions, zero_division=0)
lr_f1 = f1_score(y_test, lr_predictions, zero_division=0)
lr_auc = roc_auc_score(y_test, lr_probabilities)

print("\nLogistic Regression Results:")
print("Accuracy :", round(lr_accuracy, 4))
print("Precision:", round(lr_precision, 4))
print("Recall   :", round(lr_recall, 4))
print("F1 Score :", round(lr_f1, 4))
print("ROC-AUC  :", round(lr_auc, 4))


# --------------------------------------------------
# 11. COMPARE MODELS
# --------------------------------------------------

results = pd.DataFrame({
    "Model": [
        "Random Forest",
        "Logistic Regression"
    ],
    "Accuracy": [
        rf_accuracy,
        lr_accuracy
    ],
    "Precision": [
        rf_precision,
        lr_precision
    ],
    "Recall": [
        rf_recall,
        lr_recall
    ],
    "F1 Score": [
        rf_f1,
        lr_f1
    ],
    "ROC-AUC": [
        rf_auc,
        lr_auc
    ]
})

print("\n" + "=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

print(results.round(4).to_string(index=False))


# --------------------------------------------------
# 12. SELECT BEST MODEL
# --------------------------------------------------

if rf_auc >= lr_auc:
    best_model = rf_model
    best_model_name = "Random Forest"
    best_auc = rf_auc
else:
    best_model = lr_model
    best_model_name = "Logistic Regression"
    best_auc = lr_auc


print("\nBest Model:", best_model_name)
print("Best ROC-AUC:", round(best_auc, 4))


# --------------------------------------------------
# 13. SAVE MODEL
# --------------------------------------------------

MODEL_PATH = "models/recovery_model.pkl"

joblib.dump(best_model, MODEL_PATH)

print("\nModel saved successfully:")
print(MODEL_PATH)


# --------------------------------------------------
# 14. SAVE FEATURE LIST
# --------------------------------------------------

FEATURE_PATH = "models/model_features.pkl"

joblib.dump(features, FEATURE_PATH)

print("Feature list saved:")
print(FEATURE_PATH)


# --------------------------------------------------
# 15. FEATURE IMPORTANCE
# --------------------------------------------------

if best_model_name == "Random Forest":

    importance_df = pd.DataFrame({
        "Feature": features,
        "Importance": best_model.feature_importances_
    })

    importance_df = importance_df.sort_values(
        by="Importance",
        ascending=False
    )

    print("\n" + "=" * 60)
    print("TOP FEATURES")
    print("=" * 60)

    print(
        importance_df.head(10).round(4).to_string(index=False)
    )

    importance_df.to_csv(
        "outputs/feature_importance.csv",
        index=False
    )


# --------------------------------------------------
# 16. CREATE TEST PREDICTIONS
# --------------------------------------------------

prediction_output = X_test.copy()

prediction_output["actual_recovery"] = y_test.values
prediction_output["predicted_recovery"] = best_model.predict(X_test)

prediction_output["recovery_probability"] = (
    best_model.predict_proba(X_test)[:, 1]
)

prediction_output["recovery_probability"] = (
    prediction_output["recovery_probability"] * 100
).round(2)


prediction_output.to_csv(
    "outputs/test_predictions.csv",
    index=False
)


# --------------------------------------------------
# 17. FINAL MESSAGE
# --------------------------------------------------

print("\n" + "=" * 60)
print("STEP 8 COMPLETED SUCCESSFULLY!")
print("=" * 60)

print("\nCreated files:")
print("1. models/recovery_model.pkl")
print("2. models/model_features.pkl")
print("3. outputs/feature_importance.csv")
print("4. outputs/test_predictions.csv")

print("\nReviveAI can now predict recovery probability.")