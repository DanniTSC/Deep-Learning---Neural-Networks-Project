from __future__ import annotations
import math
import numpy as np


def binary_classification_metrics(
    y_true: list[int], y_pred: list[int]
) -> dict[str, float]:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length.")
    if not y_true:
        raise ValueError("Cannot evaluate empty inputs.")

    tp = sum(1 for actual, pred in zip(y_true, y_pred) if actual == 1 and pred == 1)
    tn = sum(1 for actual, pred in zip(y_true, y_pred) if actual == 0 and pred == 0)
    fp = sum(1 for actual, pred in zip(y_true, y_pred) if actual == 0 and pred == 1)
    fn = sum(1 for actual, pred in zip(y_true, y_pred) if actual == 1 and pred == 0)

    accuracy = (tp + tn) / len(y_true)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positive": float(tp),
        "true_negative": float(tn),
        "false_positive": float(fp),
        "false_negative": float(fn),
    }


def regression_metrics(y_true: list[float], y_pred: list[float]) -> dict[str, float]:
    true_values, predicted_values = _validate_regression_inputs(y_true, y_pred)
    errors = predicted_values - true_values
    absolute_errors = np.abs(errors)
    squared_errors = errors**2

    mae = float(np.mean(absolute_errors))
    mse = float(np.mean(squared_errors))
    rmse = float(math.sqrt(mse))

    total_sum_squares = float(np.sum((true_values - np.mean(true_values)) ** 2))
    residual_sum_squares = float(np.sum(squared_errors))
    r2 = 1.0 - residual_sum_squares / total_sum_squares if total_sum_squares else 0.0

    correlation = _pearson_correlation(true_values, predicted_values)

    return {
        "mae": mae,
        "mse": mse,
        "rmse": rmse,
        "r2": float(r2),
        "correlation": correlation,
        "mean_actual": float(np.mean(true_values)),
        "mean_predicted": float(np.mean(predicted_values)),
    }


def regression_metrics_template() -> dict[str, str]:
    return {
        "mae": "Mean Absolute Error; average absolute drawdown error.",
        "mse": "Mean Squared Error; penalizes larger errors more strongly.",
        "rmse": "Root Mean Squared Error; same unit as the drawdown target.",
        "r2": "Coefficient of determination; share of target variance explained.",
        "correlation": "Pearson correlation between actual and predicted drawdown.",
        "mean_actual": "Average actual future max drawdown.",
        "mean_predicted": "Average predicted future max drawdown.",
    }


def _validate_regression_inputs(
    y_true: list[float],
    y_pred: list[float],
) -> tuple[np.ndarray, np.ndarray]:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length.")
    if not y_true:
        raise ValueError("Cannot evaluate empty inputs.")

    true_values = np.asarray(y_true, dtype=float)
    predicted_values = np.asarray(y_pred, dtype=float)
    if not np.isfinite(true_values).all() or not np.isfinite(predicted_values).all():
        raise ValueError("Regression inputs must contain only finite numeric values.")

    return true_values, predicted_values


def _pearson_correlation(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 2:
        return 0.0
    if np.std(y_true) == 0 or np.std(y_pred) == 0:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])
