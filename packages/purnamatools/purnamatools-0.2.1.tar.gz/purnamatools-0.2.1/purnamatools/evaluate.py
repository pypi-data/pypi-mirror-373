from sklearn.metrics import r2_score,accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report

def evaluate_model_regression(model, X_train, y_train, X_test, y_test, metric_fn, metric_name="Score"):
    """
    Evaluate a regression model on train and test sets using a given metric function.
    
    Parameters
    ----------
    model : object
        Trained regression model with .predict method
    X_train, y_train : array-like
        Training features and target
    X_test, y_test : array-like
        Testing features and target
    metric_fn : function
        Metric function (e.g., r2_score, mean_squared_error, etc.)
    metric_name : str, optional
        Name of the metric (default: "Score")
    """
    # Predict
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Calculate scores
    train_score = metric_fn(y_train, y_pred_train)
    test_score = metric_fn(y_test, y_pred_test)

    # Print results
    print(f"{metric_name} on Training Set: {train_score:.4f}")
    print(f"{metric_name} on Testing Set : {test_score:.4f}")

    # Static interpretation
    if train_score < 0 or test_score < 0:
        print("⚠️ The model performs poorly (negative score). Consider rechecking features or model choice.")
    elif train_score > test_score + 0.1:
        print("⚠️ Possible overfitting: training score is much higher than testing score.")
    elif abs(train_score - test_score) <= 0.1:
        print("✅ Model generalizes well: training and testing scores are balanced.")
    elif test_score > train_score:
        print("⚠️ Possible underfitting: testing score is higher than training score. Feature importance may not be reliable.")
    else:
        print("ℹ️ Model evaluation completed.")

def evaluate_model_classification(model, X_train, y_train, X_test, y_test, metrics=None):
    """
    Evaluate a classification model using provided metrics.
    
    Parameters
    ----------
    model : object
        Trained classification model (must implement fit/predict).
    X_train : array-like
        Training features.
    y_train : array-like
        Training labels.
    X_test : array-like
        Test features.
    y_test : array-like
        Test labels.
    metrics : dict, optional
        Dictionary of metric names and functions, e.g.:
        {
            "Accuracy": accuracy_score,
            "Precision": lambda y_true, y_pred: precision_score(y_true, y_pred, average="weighted"),
            "Recall": lambda y_true, y_pred: recall_score(y_true, y_pred, average="weighted"),
            "F1 Score": lambda y_true, y_pred: f1_score(y_true, y_pred, average="weighted")
        }
        If None, a default set of metrics will be used.
    
    Returns
    -------
    None
        Prints evaluation results.
    """
    
    # Default metrics if none provided
    if metrics is None:
        metrics = {
            "Accuracy": accuracy_score,
            "Precision (weighted)": lambda y_true, y_pred: precision_score(y_true, y_pred, average="weighted"),
            "Recall (weighted)": lambda y_true, y_pred: recall_score(y_true, y_pred, average="weighted"),
            "F1 Score (weighted)": lambda y_true, y_pred: f1_score(y_true, y_pred, average="weighted"),
        }
    
    # Predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    print("=== Training Performance ===")
    for name, func in metrics.items():
        print(f"{name}: {func(y_train, y_pred_train):.4f}")
    
    print("\n=== Test Performance ===")
    for name, func in metrics.items():
        print(f"{name}: {func(y_test, y_pred_test):.4f}")
    
    print("\n=== Classification Report (Test) ===")
    print(classification_report(y_test, y_pred_test))
    
    print("Confusion Matrix (Test):")
    print(confusion_matrix(y_test, y_pred_test))
