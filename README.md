# 📉 Okun's Law Explorer

An interactive Streamlit tool that examines the relationship between **GDP growth rate** and **unemployment** across eight countries, based on Okun's Law.

 Live App🔗https://acc102track4.streamlit.app
---

## Analytical Problem

**Research question:** Does Okun's Law hold across different economies, and do the estimated Okun coefficients differ significantly between developed and developing countries?

**Okun's Law** (Okun, 1962) proposes that when GDP grows faster than its potential rate, unemployment tends to fall. The difference version used in this project is:

> ΔUnemployment = α + β × GDP Growth

Where **β (the Okun coefficient)** is expected to be negative. A value of −0.4 means each additional 1 percentage point of GDP growth is associated with a 0.4 pp fall in unemployment.

**Intended users:** Economics students and policy researchers who want to explore macroeconomic relationships across countries interactively, without manually processing raw data.

---

## Dataset

| Field | Detail |
|---|---|
| Provider | World Bank Open Data |
| GDP indicator | `NY.GDP.MKTP.KD.ZG` — GDP growth (annual %) |
| Unemployment indicator | `SL.UEM.TOTL.ZS` — Unemployment, total (% of total labour force) |
| Countries | China, United States, United Kingdom, Germany, Japan, France, India, Brazil |
| Period | 1991–2023 |
| Access date | April 2026 |
| How data is loaded | Fetched live via `pandas_datareader.wb` on app startup. No local data file is required. If the network is unavailable, the app automatically falls back to a built-in sample dataset. |

---

## Python Methods

- **Data retrieval:** `pandas_datareader.wb.download()` — pulls data directly from the World Bank API
- **Data cleaning:** `pandas` — joining tables, dropping missing values, computing year-over-year unemployment changes via `.diff()`
- **Statistical analysis:** `scipy.stats.linregress` — OLS regression to estimate Okun coefficients (β), R², and p-values per country
- **Prediction:** Linear model applied to user-defined GDP growth inputs to forecast unemployment changes
- **Visualisation:** `plotly` — interactive dual-axis time series, scatter plots with regression lines, bar charts, bubble charts
- **Interface:** `streamlit` — sidebar controls, tabbed layout, sliders, metric cards, CSV download button

---

## Key Findings

- Okun's Law is **statistically significant** (p < 0.05) in most developed economies including the United States, Germany, and the United Kingdom, with Okun coefficients typically in the −0.3 to −0.5 range consistent with the existing literature.
- **Developing economies** such as China and India show weaker or statistically insignificant coefficients, suggesting that labour market structures and informal employment reduce the GDP–unemployment sensitivity.
- The **2008 financial crisis** and **2020 COVID-19 shock** are clearly visible as outlier points in the scatter plots, highlighting the limits of a simple linear model during structural breaks.
- The **Prediction Mode** demonstrates that a 1% GDP growth scenario produces meaningfully different unemployment outcomes across countries, reinforcing that a single global Okun coefficient is an oversimplification.

---

## Project Structure

```
okun_explorer/
├── app.py              # Main Streamlit application (5 interactive tabs)
├── analysis.ipynb      # Full analytical workflow: data loading → cleaning → regression → prediction
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/okun-explorer.git
cd okun-explorer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch the app

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

> **Note:** An internet connection is recommended so the app can fetch live World Bank data on first load. If unavailable, it will use the built-in sample dataset automatically — no extra setup needed.

---

## App Features

| Tab | What it does |
|---|---|
| 📈 Trend Overview | Dual-axis time series: GDP growth vs unemployment per country |
| 🔍 Okun's Law Analysis | Scatter plot + OLS regression lines + Okun coefficient cards |
| 📊 Country Comparison | Bubble chart comparing average growth, unemployment, and volatility |
| 🔮 Prediction Mode | User inputs a GDP growth rate via slider → app predicts ΔUnemployment for each country |
| 📋 Data Table | Full underlying dataset with CSV download |

---

## Dependencies

See `requirements.txt`. Key libraries:

```
streamlit
pandas
pandas-datareader
numpy
plotly
scipy
```

Install all with:

```bash
pip install -r requirements.txt
```
