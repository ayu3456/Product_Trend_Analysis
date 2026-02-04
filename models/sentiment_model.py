import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import logging
from typing import Dict, Any

# Setup logging
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    _instances = {}

    def __new__(cls, model_name: str):
        """Singleton-like pattern to avoid reloading models."""
        if model_name not in cls._instances:
            instance = super(SentimentAnalyzer, cls).__new__(cls)
            instance._initialize(model_name)
            cls._instances[model_name] = instance
        return cls._instances[model_name]

    def _initialize(self, model_name: str):
        """Loads the HuggingFace model and pipeline."""
        logger.info(f"Loading model: {model_name}...")
        try:
            # Map friendly names to HF paths if necessary
            hf_path = model_name
            if model_name == "BERT":
                hf_path = "distilbert-base-uncased-finetuned-sst-2-english"
            elif model_name == "RoBERTa":
                hf_path = "cardiffnlp/twitter-roberta-base-sentiment"

            self.model_name = model_name
            self.pipe = pipeline(
                "sentiment-analysis",
                model=hf_path,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info(f"Model {model_name} loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            self.pipe = None

    def predict(self, text: str) -> Dict[str, Any]:
        """Runs sentiment analysis on the text."""
        if not self.pipe:
            return {"label": "unknown", "score": 0.0}

        try:
            # Truncate text if it's too long for the model
            # Most BERT-based models have a 512 token limit
            # Simplistic truncation here; better to use tokenizer if needed
            result = self.pipe(text[:512])[0]
            
            # Map labels to a standard format (POSITIVE, NEGATIVE, NEUTRAL)
            label = result['label'].upper()
            
            # Specific mapping for RoBERTa (LABEL_0: Negative, LABEL_1: Neutral, LABEL_2: Positive)
            if "LABEL_" in label:
                mapping = {"LABEL_0": "NEGATIVE", "LABEL_1": "NEUTRAL", "LABEL_2": "POSITIVE"}
                label = mapping.get(label, label)
            
            return {
                "label": label,
                "score": result['score']
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {"label": "error", "score": 0.0}

if __name__ == "__main__":
    # Test BERT
    analyzer = SentimentAnalyzer("BERT")
    print(analyzer.predict("I absolutely love this new phone!"))
    
    # Test RoBERTa
    analyzer_rb = SentimentAnalyzer("RoBERTa")
    print(analyzer_rb.predict("This product is okay, but could be better."))
