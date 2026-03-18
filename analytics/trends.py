import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any

# Setup logging
logger = logging.getLogger(__name__)

class SentimentAnalytics:
    @staticmethod
    def process_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Converts raw database results into a Pandas DataFrame with numeric scores."""
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # Map labels to numeric scores for aggregation
        # POSITIVE: 1, NEUTRAL: 0, NEGATIVE: -1
        score_map = {"POSITIVE": 1, "NEUTRAL": 0, "NEGATIVE": -1}
        df['sentiment_score'] = df['sentiment_label'].map(score_map).fillna(0)
        
        # Ensure timestamp is datetime
        df['post_timestamp'] = pd.to_datetime(df['post_timestamp'], errors='coerce')
        df = df.dropna(subset=['post_timestamp'])
        
        return df

    @staticmethod
    def get_platform_distribution(df: pd.DataFrame) -> pd.DataFrame:
        """Returns sentiment distribution counts per platform."""
        if df.empty:
            return pd.DataFrame()
        return df.groupby(['platform', 'sentiment_label']).size().reset_index(name='count')

    @staticmethod
    def get_daily_trends(df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates average sentiment score by day."""
        if df.empty:
            return pd.DataFrame()
        
        df_copy = df.copy()
        df_copy['date'] = df_copy['post_timestamp'].dt.date
        
        daily_avg = df_copy.groupby('date')['sentiment_score'].mean().reset_index()
        daily_avg.columns = ['date', 'avg_sentiment']
        return daily_avg

    @staticmethod
    def detect_spikes(daily_trends: pd.DataFrame, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Detects sudden drops or rises in sentiment.
        Returns a list of dates where the score changed significantly from the previous day.
        """
        if daily_trends.empty or len(daily_trends) < 2:
            return []
            
        daily_trends = daily_trends.sort_values('date')
        daily_trends['diff'] = daily_trends['avg_sentiment'].diff()
        
        spikes = daily_trends[daily_trends['diff'].abs() >= threshold]
        return spikes.to_dict('records')

    @staticmethod
    def get_top_examples(df: pd.DataFrame, n: int = 3) -> Dict[str, pd.DataFrame]:
        """Returns the most positive and most negative posts."""
        if df.empty:
            return {"positive": pd.DataFrame(), "negative": pd.DataFrame()}
            
        positive = df.sort_values('confidence_score', ascending=False)[df['sentiment_label'] == 'POSITIVE'].head(n)
        negative = df.sort_values('confidence_score', ascending=False)[df['sentiment_label'] == 'NEGATIVE'].head(n)
        
        return {
            "positive": positive[['platform', 'raw_text', 'confidence_score']],
            "negative": negative[['platform', 'raw_text', 'confidence_score']]
        }
