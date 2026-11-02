"""
Stance and Sentiment Classification Suite for Policy & Regulatory Feedback.

Components:
1. VADER Sentiment Baseline (Lexical Polarity & Stance Disconnect Metric)
2. TF-IDF + Logistic Regression (Explainable Linear Baseline)
3. TF-IDF + Linear SVM (Calibrated High-Margin Baseline)
4. Fine-Tuned DistilBERT Classifier (Contextual Transformer Model)
5. Explainability: Top Feature N-Gram Weights per Stance Class
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix


STANCE_LABELS = ["oppose", "neutral", "support"]
LABEL2ID = {"oppose": 0, "neutral": 1, "support": 2}
ID2LABEL = {0: "oppose", 1: "neutral", 2: "support"}


class VaderBaseline:
    """VADER Sentiment Intensity Analyzer mapped to 3-class policy stance."""
    def __init__(self, pos_threshold: float = 0.10, neg_threshold: float = -0.10):
        self.analyzer = SentimentIntensityAnalyzer()
        self.pos_threshold = pos_threshold
        self.neg_threshold = neg_threshold

    def predict(self, text: str) -> Dict[str, Any]:
        scores = self.analyzer.polarity_scores(text)
        compound = scores["compound"]
        if compound >= self.pos_threshold:
            vader_stance = "support"
        elif compound <= self.neg_threshold:
            vader_stance = "oppose"
        else:
            vader_stance = "neutral"
            
        return {
            "vader_stance": vader_stance,
            "compound": compound,
            "positive": scores["pos"],
            "negative": scores["neg"],
            "neutral": scores["neu"]
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        return [self.predict(t) for t in texts]


class SklearnStancePipeline:
    """TF-IDF vectorizer + Logistic Regression or Calibrated Linear SVM."""
    def __init__(self, model_type: str = "logistic_regression", ngram_range: Tuple[int, int] = (1, 2)):
        self.model_type = model_type
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=ngram_range,
            max_features=5000,
            sublinear_tf=True
        )
        if model_type == "logistic_regression":
            self.clf = LogisticRegression(class_weight="balanced", max_iter=500, random_state=42)
        elif model_type == "svm":
            base_svm = LinearSVC(class_weight="balanced", random_state=42)
            self.clf = CalibratedClassifierCV(estimator=base_svm, cv=3)
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

    def fit(self, texts: List[str], labels: List[str]):
        y = [LABEL2ID[l] for l in labels]
        X = self.vectorizer.fit_transform(texts)
        self.clf.fit(X, y)

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        X = self.vectorizer.transform(texts)
        return self.clf.predict_proba(X)

    def predict(self, texts: List[str]) -> Tuple[List[str], List[float]]:
        probs = self.predict_proba(texts)
        pred_ids = np.argmax(probs, axis=1)
        confidences = np.max(probs, axis=1)
        pred_labels = [ID2LABEL[i] for i in pred_ids]
        return pred_labels, confidences.tolist()

    def get_feature_importance(self, top_n: int = 10) -> Dict[str, List[Tuple[str, float]]]:
        """Extract top predictive n-grams for each class (available for logistic regression)."""
        if self.model_type != "logistic_regression":
            return {}
        feature_names = self.vectorizer.get_feature_names_out()
        coefs = self.clf.coef_  # shape (n_classes, n_features)
        importance = {}
        for class_idx, class_name in ID2LABEL.items():
            class_coef = coefs[class_idx]
            top_indices = np.argsort(class_coef)[-top_n:][::-1]
            top_features = [(feature_names[i], round(float(class_coef[i]), 4)) for i in top_indices]
            importance[class_name] = top_features
        return importance


try:
    import torch
    import torch.utils.data
    _BaseDataset = torch.utils.data.Dataset
except ImportError:
    _BaseDataset = object


class HFStanceDataset(_BaseDataset):
    def __init__(self, encodings, labels):
        import torch
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        import torch
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.encodings["input_ids"])


class DistilBertStanceClassifier:
    """Lightweight fine-tuned DistilBERT stance classifier."""
    def __init__(self, model_name: str = "distilbert-base-uncased", max_length: int = 128, device: str = "cpu"):
        from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
        self.model_name = model_name
        self.max_length = max_length
        self.device = device
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        self.model = DistilBertForSequenceClassification.from_pretrained(model_name, num_labels=3)
        self.model.to(self.device)

    def fit(self, train_texts: List[str], train_labels: List[str], 
            val_texts: List[str], val_labels: List[str],
            epochs: int = 2, batch_size: int = 16, output_dir: str = "models/distilbert_stance"):
        os.makedirs(output_dir, exist_ok=True)
        
        train_enc = self.tokenizer(train_texts, truncation=True, padding=True, max_length=self.max_length)
        val_enc = self.tokenizer(val_texts, truncation=True, padding=True, max_length=self.max_length)
        
        train_y = [LABEL2ID[l] for l in train_labels]
        val_y = [LABEL2ID[l] for l in val_labels]
        
        train_dataset = HFStanceDataset(train_enc, train_y)
        val_dataset = HFStanceDataset(val_enc, val_y)
        
        from transformers import Trainer, TrainingArguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_ratio=0.1,
            weight_decay=0.01,
            logging_steps=20,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            save_total_limit=1,
            report_to="none",
            use_cpu=(self.device == "cpu")
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset
        )
        
        trainer.train()
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        print(f"DistilBERT successfully fine-tuned and saved to {output_dir}")

    def predict(self, texts: List[str]) -> Tuple[List[str], List[float]]:
        import torch
        self.model.eval()
        enc = self.tokenizer(texts, truncation=True, padding=True, max_length=self.max_length, return_tensors="pt")
        enc = {k: v.to(self.device) for k, v in enc.items()}
        with torch.no_grad():
            outputs = self.model(**enc)
            probs = torch.softmax(outputs.logits, dim=1).cpu().numpy()
            
        pred_ids = np.argmax(probs, axis=1)
        confidences = np.max(probs, axis=1)
        pred_labels = [ID2LABEL[i] for i in pred_ids]
        return pred_labels, confidences.tolist()
