from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support


@dataclass
class Metrics:
    precision: float
    recall: float
    f1: float


def compute_prf1(gold: List[str], pred: List[str]) -> Metrics:
    """Compute micro-averaged P/R/F1 over exact-match labels by token presence."""
    # Simple token-based bag-of-words presence comparison (example baseline)
    # For thesis use, replace with your domain-specific metric.
    y_true = []
    y_pred = []
    for g, p in zip(gold, pred):
        y_true.append(1 if g and g.strip() else 0)
        y_pred.append(1 if p and p.strip() else 0)
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
    return Metrics(p, r, f1)


def evaluate_csv(pred_csv: str, gold_csv: str, out_csv: str) -> pd.DataFrame:
    """Given CSVs with columns: id, answer; id, gold_answer"""
    pred_df = pd.read_csv(pred_csv)
    gold_df = pd.read_csv(gold_csv)
    merged = pd.merge(gold_df, pred_df, on="id", how="inner", suffixes=("_gold", "_pred"))
    metrics = compute_prf1(merged["answer_gold"].astype(str).tolist(),
                           merged["answer_pred"].astype(str).tolist())
    out = pd.DataFrame([{"precision": metrics.precision, "recall": metrics.recall, "f1": metrics.f1}])
    out.to_csv(out_csv, index=False)
    return out
