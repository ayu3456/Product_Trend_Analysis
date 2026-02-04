# 📊 Multi-Platform Brand Sentiment & Trend Dashboard

A production-ready NLP application that monitors public sentiment for brands across Reddit, Amazon, and Twitter (X). The system scrapes real-time data, processes it through Transformer models, and visualizes insights in an interactive Streamlit dashboard.

## 🏗️ Architecture

```ascii
[ User Input ] --> [ Streamlit UI ]
                        |
          +-------------+-------------+
          |                           |
[ Scraper Layer ]       [ Analytics Layer ]
   |-- Reddit (Playwright)      |-- Trend Analysis
   |-- Amazon (Playwright)      |-- Spike Detection
   |-- Twitter (Playwright)     |-- KPI Calculation
          |                           |
[ Preprocessing ] <-------------------+
   |-- URL/Emoji/Slang Cleaning
          |
[ Model Layer ]
   |-- BERT (DistilBERT)
   |-- RoBERTa (Twitter-refined)
          |
[ Persistence ]
   |-- SQLite Database
```

## 🚀 Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers:**
   ```bash
   playwright install chromium
   ```

3. **Run the Dashboard:**
   ```bash
   streamlit run dashboard/app.py
   ```

## 🛠️ Key Features

- **Multi-Platform Scraping:** Uses Playwright for robust, headless data collection from Reddit, Amazon, and Twitter.
- **Advanced NLP:** Supports model switching between `DistilBERT` (SST-2) and `Twitter-RoBERTa` for platform-specific sentiment accuracy.
- **Clean Pipeline:** Decoupled architecture (Scrapers -> Preprocessing -> Models -> DB -> Analytics).
- **Interactive Visualizations:** KPI cards, sentiment distribution bar charts, and time-series line charts using Plotly.
- **Persistence:** All raw and processed data is stored in SQLite for history tracking and re-analysis.

## 🧠 Interview Talking Points

- **Why Playwright over Selenium?** Playwright is faster, more reliable (auto-waiting), and has better modern browser support for scraping SPAs.
- **Sentiment Model Selection:** I chose `cardiffnlp/twitter-roberta-base-sentiment` because it's specifically trained on social media text (handles slang/emojis better than generic BERT).
- **Error Handling:** Implemented graceful failures for scrapers (e.g., handling Twitter login walls or Amazon bot detection) to ensure the system doesn't crash on one platform's failure.
- **Scalability:** The architecture follows a singleton pattern for model loading to save memory and can be easily extended with more scrapers or models by following the modular structure.

## ⚠️ Limitations & Future Improvements

- **Twitter Auth:** Currently best-effort public scraping. Future versions could integrate the Official API or handle cookie persistence.
- **Amazon Bot Detection:** High-frequency scraping may trigger captchas. Rotating proxies would be the next step for production.
- **Contextual Sentiment:** Current models analyze individual posts; future updates could use LLMs (GPT-4/Llama 3) for deeper contextual understanding of sarcasm.

---
**Author:** Antigravity (Senior ML Engineer)
**License:** MIT
