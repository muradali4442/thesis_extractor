from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def plot_metrics(csv_path: str | Path) -> None:
    df = pd.read_csv(csv_path)
    if {"precision", "recall", "f1"}.issubset(df.columns):
        df.plot(kind="bar", xlabel="run", ylabel="score", title="Precision/Recall/F1")
        plt.tight_layout()
        plt.show()
    else:
        raise ValueError("CSV must contain precision, recall, f1 columns")


def wordcloud_from_text(text: str) -> None:
    wc = WordCloud(width=800, height=400).generate(text)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("Word Cloud")
    plt.show()
