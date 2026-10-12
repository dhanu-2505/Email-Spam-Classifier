from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from backend.ml.preprocess import normalize_text


def create_eda_reports(df: pd.DataFrame, output_dir: str = "reports") -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    df = df.copy()
    df["text_length"] = df["text"].apply(len)
    df["text"] = df["text"].apply(normalize_text)

    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, x="label", palette={"ham": "#4f46e5", "spam": "#f97316"})
    plt.title("Spam vs Ham Distribution")
    plt.xlabel("Label")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(out / "label_distribution.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.histplot(df["text_length"], bins=30, color="#4f46e5")
    plt.title("Message Length Distribution")
    plt.xlabel("Text Length")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(out / "message_length_distribution.png", dpi=150)
    plt.close()

    spam_words = " ".join(df[df["label"] == "spam"]["text"]).split()
    ham_words = " ".join(df[df["label"] == "ham"]["text"]).split()
    spam_counts = pd.Series(spam_words).value_counts().head(20)
    ham_counts = pd.Series(ham_words).value_counts().head(20)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=spam_counts.values, y=spam_counts.index, palette="Oranges_r")
    plt.title("Top Spam Words")
    plt.tight_layout()
    plt.savefig(out / "top_spam_words.png", dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.barplot(x=ham_counts.values, y=ham_counts.index, palette="Blues_r")
    plt.title("Top Ham Words")
    plt.tight_layout()
    plt.savefig(out / "top_ham_words.png", dpi=150)
    plt.close()

    return {
        "rows": int(len(df)),
        "spam_count": int((df["label"] == "spam").sum()),
        "ham_count": int((df["label"] == "ham").sum()),
        "plots": [
            "label_distribution.png",
            "message_length_distribution.png",
            "top_spam_words.png",
            "top_ham_words.png",
        ],
    }
