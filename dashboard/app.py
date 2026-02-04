import streamlit as st
import pandas as pd
import plotly.express as px
import asyncio
import sys
import os
import yaml
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.reddit_scraper import RedditScraper
from scrapers.amazon_scraper import AmazonScraper
from scrapers.twitter_scraper import TwitterScraper
from preprocessing.clean_text import TextPreprocessor
from models.sentiment_model import SentimentAnalyzer
from database.db import DatabaseManager
from analytics.trends import SentimentAnalytics

# Page Config
st.set_page_config(page_title="Brand Sentiment Dashboard", layout="wide", page_icon="📊")

# Load Config
def load_config():
    with open("config.yaml", 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# Initialize Components
db = DatabaseManager(config['database']['db_path'])
preprocessor = TextPreprocessor()

# Sidebar
st.sidebar.title("🔍 Search Controls")
brand_query = st.sidebar.text_input("Brand/Product Keyword", placeholder="e.g. iPhone 15")
platforms = st.sidebar.multiselect("Platforms", ["Reddit", "Amazon", "Twitter"], default=["Reddit", "Amazon"])
model_choice = st.sidebar.selectbox("Sentiment Model", ["BERT", "RoBERTa"])
max_posts = st.sidebar.slider("Max posts per platform", 5, 50, 20)

# Main Title
st.title("🛡️ Multi-Platform Brand Sentiment & Trend Dashboard")
st.markdown("Monitor and analyze public perception across the web using Transformer NLP.")

async def run_analysis(keyword, selected_platforms, model_name, limit):
    results = []
    
    # Progress bars
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Scrape
    scrapers = []
    if "Reddit" in selected_platforms: scrapers.append(RedditScraper(max_posts=limit))
    if "Amazon" in selected_platforms: scrapers.append(AmazonScraper(max_reviews=limit))
    if "Twitter" in selected_platforms: scrapers.append(TwitterScraper(max_tweets=limit))
    
    all_raw_data = []
    for i, scraper in enumerate(scrapers):
        status_text.text(f"Scraping {scraper.__class__.__name__}...")
        data = await scraper.scrape(keyword)
        all_raw_data.extend(data)
        progress_bar.progress((i + 1) / (len(scrapers) + 1))
    
    if not all_raw_data:
        st.warning("No data found for the given keyword/platforms.")
        return
    
    # Process and Predict
    status_text.text("Analyzing Sentiment...")
    analyzer = SentimentAnalyzer(model_name)
    
    for item in all_raw_data:
        # 1. Clean
        cleaned = preprocessor.clean(item['text'])
        # 2. Predict
        sentiment = analyzer.predict(cleaned)
        # 3. Store in DB
        raw_id = db.insert_raw_post(item)
        proc_id = db.insert_processed_post(raw_id, cleaned)
        db.insert_sentiment_result(proc_id, sentiment['label'], sentiment['score'], model_name)
    
    progress_bar.progress(1.0)
    status_text.text("Analysis Complete!")
    return True

if st.sidebar.button("🚀 Analyze Now"):
    if brand_query:
        with st.spinner("Processing... This may take a minute."):
            asyncio.run(run_analysis(brand_query, platforms, model_choice, max_posts))
    else:
        st.error("Please enter a brand or product keyword.")

# Display Results
if brand_query:
    raw_data = db.get_dashboard_data(brand_query)
    if raw_data:
        df = SentimentAnalytics.process_data(raw_data)
        
        # --- KPI SECTION ---
        st.subheader("📈 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        pos_pct = len(df[df['sentiment_label'] == 'POSITIVE']) / len(df) * 100
        neg_pct = len(df[df['sentiment_label'] == 'NEGATIVE']) / len(df) * 100
        avg_score = df['sentiment_score'].mean()
        
        col1.metric("Total Posts", len(df))
        col2.metric("% Positive", f"{pos_pct:.1f}%")
        col3.metric("% Negative", f"{neg_pct:.1f}%", delta_color="inverse")
        col4.metric("Avg Sentiment", f"{avg_score:.2f}")
        
        # --- CHARTS SECTION ---
        st.divider()
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Sentiment Distribution")
            dist_df = SentimentAnalytics.get_platform_distribution(df)
            fig_dist = px.bar(dist_df, x='platform', y='count', color='sentiment_label', 
                             barmode='group', color_discrete_map={'POSITIVE': '#00CC96', 'NEUTRAL': '#636EFA', 'NEGATIVE': '#EF553B'})
            st.plotly_chart(fig_dist, use_container_width=True)
            
        with c2:
            st.subheader("Sentiment Trend Over Time")
            trend_df = SentimentAnalytics.get_daily_trends(df)
            fig_trend = px.line(trend_df, x='date', y='avg_sentiment', markers=True)
            fig_trend.update_layout(yaxis_range=[-1.1, 1.1])
            st.plotly_chart(fig_trend, use_container_width=True)
            
        # --- EXAMPLES ---
        st.divider()
        st.subheader("⭐ Top Sentiment Examples")
        examples = SentimentAnalytics.get_top_examples(df)
        
        ex_col1, ex_col2 = st.columns(2)
        with ex_col1:
            st.success("Positive Highlights")
            st.table(examples['positive'])
            
        with ex_col2:
            st.error("Negative Concerns")
            st.table(examples['negative'])
            
        # --- DATA TABLE ---
        st.divider()
        st.subheader("📝 Raw Data Inspection")
        st.dataframe(df[['platform', 'raw_text', 'sentiment_label', 'confidence_score', 'post_timestamp']], use_container_width=True)
        
    else:
        st.info("No data in database for this query yet. Use the sidebar to start a new analysis.")
else:
    st.info("👈 Enter a brand name in the sidebar to begin.")
