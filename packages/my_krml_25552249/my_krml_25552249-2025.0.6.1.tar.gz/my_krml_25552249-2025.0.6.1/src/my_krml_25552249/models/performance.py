def print_regressor_scores(y_preds, y_actuals, set_name=None):
    """Print the RMSE and MAE for the provided data

    Parameters
    ----------
    y_preds : Numpy Array
        Predicted target
    y_actuals : Numpy Array
        Actual target
    set_name : str
        Name of the set to be printed

    Returns
    -------
    """
    from sklearn.metrics import root_mean_squared_error as rmse
    from sklearn.metrics import mean_absolute_error as mae

    print(f"RMSE {set_name}: {rmse(y_actuals, y_preds)}")
    print(f"MAE {set_name}: {mae(y_actuals, y_preds)}")


def print_aucroc_score(y_preds, y_actuals, set_name=None):
    """Print the AUC-ROC score for the provided data

    Parameters
    ----------
    y_preds : Numpy Array or list
        Predicted probabilities or scores for the positive class
    y_actuals : Numpy Array or list
        Actual binary target labels (0 or 1)
    set_name : str
        Name of the set to be printed

    Returns
    -------
    """
    from sklearn.metrics import roc_auc_score

    aucroc = roc_auc_score(y_actuals, y_preds)
    print(f"AUC-ROC {set_name}: {aucroc}")


# Function for plotting confusmion matrix directly from X and y with model
def plot_confusion_matrix(model, X, y, title="Confusion Matrix"):
    """
    Fits the model (if not already fitted) and plots the confusion matrix for given X, y.
    
    Parameters:
    model: Fitted classifier with a .predict() method
    X: Features
    y: True labels
    title: Title for the confusion matrix
    """
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
    import matplotlib.pyplot as plt

    y_pred = model.predict(X)
    cm = confusion_matrix(y, y_pred)
    
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(values_format='d', cmap='Blues')
    plt.title(title)
    plt.show()

# Function to print classification report and confusion matrix
def report_and_conf_matrix(y_true, y_pred, title="Confusion Matrix"):
    """
    Print classification report and plot confusion matrix with custom title.
    
    Args:
        y_true (array-like): True labels
        y_pred (array-like): Predicted labels
        title (str): Title for the confusion matrix plot
    """
    from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
    import matplotlib.pyplot as plt
    
    # Print classification report
    print("\nClassification Report:\n", classification_report(y_true, y_pred))
    
    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Display confusion matrix
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(values_format='d', cmap='Blues')
    plt.title(title)
    plt.show()



def cross_val_metrics(model_class, X, y, params=None, n_splits=5, random_state=33):
    """
    Perform stratified k-fold cross-validation and collect metrics + predictions.

    Args:
        model_class: scikit-learn model class (e.g., RandomForestClassifier)
        X (pd.DataFrame or np.ndarray): Features
        y (pd.Series or np.ndarray): Target labels
        params (dict, optional): Model hyperparameters
        n_splits (int): Number of folds for stratified K-fold
        random_state (int): Random seed

    Returns:
        metrics (list of dict): Per-fold evaluation metrics
        y_true_all (np.ndarray): True labels across folds
        y_prob_all (np.ndarray): Predicted probabilities across folds
        y_pred_all (np.ndarray): Predicted classes across folds
    """
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import (
        roc_auc_score, average_precision_score,
        precision_score, recall_score, f1_score
    )
    import numpy as np
    y_true_all, y_prob_all, y_pred_all = [], [], []
    metrics = []

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        model = model_class(**(params or {}))
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_val)
        y_prob = model.predict_proba(X_val)[:, 1]
        
        metrics.append({
            'fold': fold,
            'roc_auc': roc_auc_score(y_val, y_prob),
            'pr_auc': average_precision_score(y_val, y_prob),
            'precision': precision_score(y_val, y_pred),
            'recall': recall_score(y_val, y_pred),
            'f1': f1_score(y_val, y_pred)
        })
        
        y_true_all.extend(y_val)
        y_prob_all.extend(y_prob)
        y_pred_all.extend(y_pred)

    return (
        metrics,
        np.array(y_true_all),
        np.array(y_prob_all),
        np.array(y_pred_all)
    )

# Below are functions for AUC-ROC and Precision Recall curves

import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, average_precision_score

# AUC-ROC Curve
def plot_roc(y_true, y_probs, title=None):
    """
    Plot ROC curve for a single dataset.
    
    Parameters:
    - y_true: array-like, true labels (0 or 1)
    - y_probs: array-like, predicted probabilities for the positive class
    - title: optional, custom title
    """
    fpr, tpr, _ = roc_curve(y_true, y_probs)
    auc_score = roc_auc_score(y_true, y_probs)
    
    plt.figure(figsize=(6,6))
    plt.plot(fpr, tpr, lw=2, label=f'ROC (AUC = {auc_score:.4f})')
    plt.plot([0,1], [0,1], 'k--', label='Random Guess')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title or 'ROC Curve')
    plt.legend()
    plt.show()

# Precision Recall Curve
def plot_pr(y_true, y_probs, positive_class_fraction=None, title=None):
    """
    Plot Precision-Recall curve for a single dataset.
    
    Parameters:
    - y_true: array-like, true labels (0 or 1)
    - y_probs: array-like, predicted probabilities for the positive class
    - positive_class_fraction: optional, baseline for PR curve (fraction of positives)
    - title: optional, custom title
    """
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    pr_auc = average_precision_score(y_true, y_probs)
    
    plt.figure(figsize=(6,6))
    plt.plot(recall, precision, lw=2, label=f'PR (AUC = {pr_auc:.4f})')
    if positive_class_fraction is not None:
        plt.hlines(y=positive_class_fraction, xmin=0, xmax=1, colors='red', linestyles='--', label='Baseline Precision')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(title or 'Precision-Recall Curve')
    plt.legend()
    plt.show()

# print_classifier_scores
def print_classifier_scores(y_preds, y_actuals, set_name=None):
    """Print the Accuracy and F1 score for the provided data.
    The value of the 'average' parameter for F1 score will be determined according to the number of distinct values of the target variable: 'binary' for bianry classification' or 'weighted' for multi-classs classification

    Parameters
    ----------
    y_preds : Numpy Array
        Predicted target
    y_actuals : Numpy Array
        Actual target
    set_name : str
        Name of the set to be printed
    Returns
    -------
    """
    from sklearn.metrics import accuracy_score
    from sklearn.metrics import f1_score
    import pandas as pd

    average = 'weighted' if pd.Series(y_actuals).nunique() > 2 else 'binary'

    print(f"Accuracy {set_name}: {accuracy_score(y_actuals, y_preds)}")
    print(f"F1 {set_name}: {f1_score(y_actuals, y_preds, average=average)}")


# assess_classifier_set
def assess_classifier_set(model, features, target, set_name=''):
    """Save the predictions from a trained model on a given set and print its accuracy and F1 scores

    Parameters
    ----------
    model: sklearn.base.BaseEstimator
        Trained Sklearn model with set hyperparameters
    features : Numpy Array
        Features
    target : Numpy Array
        Target variable
    set_name : str
        Name of the set to be printed

    Returns
    -------
    """
    preds = model.predict(features)
    print_classifier_scores(y_preds=preds, y_actuals=target, set_name=set_name)


# fit_assess_classifier
def fit_assess_classifier(model, X_train, y_train, X_val, y_val):
    """Train a classifier model, print its accuracy and F1 scores on the training and validation set and return the trained model

    Parameters
    ----------
    model: sklearn.base.BaseEstimator
        Instantiated Sklearn model with set hyperparameters
    X_train : Numpy Array
        Features for the training set
    y_train : Numpy Array
        Target for the training set
    X_train : Numpy Array
        Features for the validation set
    y_train : Numpy Array
        Target for the validation set

    Returns
    sklearn.base.BaseEstimator
        Trained model
    -------
    """
    model.fit(X_train, y_train)
    assess_classifier_set(model, X_train, y_train, set_name='Training')
    assess_classifier_set(model, X_val, y_val, set_name='Validation')
    return model


