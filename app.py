import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Okun's Law Explorer",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'DM Serif Display', serif;
}
.metric-card {
    background: #f8f5f0;
    border-left: 4px solid #2d5016;
    padding: 16px 20px;
    border-radius: 4px;
    margin-bottom: 12px;
}
.metric-card .label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #888;
    margin-bottom: 4px;
}
.metric-card .value {
    font-size: 26px;
    font-weight: 500;
    color: #1a1a1a;
}
.metric-card .sub {
    font-size: 12px;
    color: #666;
    margin-top: 2px;
}
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: #1a1a1a;
    margin-bottom: 4px;
}
.section-sub {
    font-size: 13px;
    color: #888;
    margin-bottom: 20px;
}
.insight-box {
    background: #eef4e8;
    border: 1px solid #c5ddb0;
    border-radius: 6px;
    padding: 14px 18px;
    font-size: 14px;
    color: #2d5016;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading World Bank data…")
def load_data():
    try:
        import pandas_datareader.wb as wb
        countries = ['CN', 'US', 'GB', 'JP', 'DE', 'FR', 'IN', 'BR']
        gdp = wb.download(
            indicator='NY.GDP.MKTP.KD.ZG',
            country=countries, start=1991, end=2023
        ).rename(columns={'NY.GDP.MKTP.KD.ZG': 'GDP_growth'})
        unem = wb.download(
            indicator='SL.UEM.TOTL.ZS',
            country=countries, start=1991, end=2023
        ).rename(columns={'SL.UEM.TOTL.ZS': 'Unemployment'})
        df = gdp.join(unem).reset_index()
        df['year'] = df['year'].astype(int)
        df = df.dropna()
        # Delta unemployment (change from prior year)
        df = df.sort_values(['country', 'year'])
        df['Delta_U'] = df.groupby('country')['Unemployment'].diff()
        df = df.dropna()
        return df
    except Exception as e:
        st.error(f"Could not fetch live data: {e}\nUsing bundled sample data.")
        return None

@st.cache_data(show_spinner=False)
def fallback_data():
    """Minimal hard-coded sample so the app still works offline."""
    rows = []
    seed = {
        'China':         [(3.0,4.1),(7.6,4.0),(8.4,3.9),(9.1,3.8),(10.1,3.8),(9.2,4.2),(6.9,4.1),(6.7,4.0),(6.9,3.9),(6.6,3.8),(6.1,3.6),(2.2,4.2),(8.4,3.9),(3.0,5.1)],
        'United States': [(3.5,5.6),(2.7,5.4),(4.5,4.9),(4.4,4.5),(4.8,4.2),(4.1,4.7),(1.0,5.8),(-0.1,8.1),(2.5,9.6),(1.6,8.9),(2.2,8.1),(2.2,7.4),(1.7,6.2),(2.5,5.3),(2.9,4.4),(2.3,3.7),(2.3,3.7),(-2.8,8.1),(5.9,5.4),(2.1,3.6)],
        'Germany':       [(1.5,8.0),(1.8,7.8),(0.4,8.7),(-0.2,9.5),(0.9,10.5),(3.9,10.3),(3.0,9.0),(1.5,8.1),(3.3,7.2),(1.1,7.5),(-5.6,7.8),(4.2,7.0),(3.9,5.9),(0.5,5.4),(0.4,5.2),(1.9,4.6),(2.2,3.8),(1.3,3.4),(-4.6,5.9),(3.5,3.8),(3.2,3.4)],
        'Japan':         [(1.8,3.0),(0.4,3.4),(-2.0,4.1),(-0.3,4.7),(0.4,5.0),(0.3,4.7),(-0.4,4.4),(2.0,4.4),(1.7,4.0),(-1.1,3.9),(-5.4,5.1),(4.1,5.1),(-0.1,4.6),(1.5,4.3),(2.2,3.5),(1.2,3.1),(0.6,2.8),(-4.2,2.8),(2.1,2.8)],
    }
    for country, vals in seed.items():
        for i, (g, u) in enumerate(vals):
            rows.append({'country': country, 'year': 2004 + i, 'GDP_growth': g, 'Unemployment': u})
    df = pd.DataFrame(rows).sort_values(['country','year'])
    df['Delta_U'] = df.groupby('country')['Unemployment'].diff()
    return df.dropna()

# ── Load ──────────────────────────────────────────────────────────────────────
df_raw = load_data()
if df_raw is None or df_raw.empty:
    df_raw = fallback_data()

COUNTRY_NAMES = sorted(df_raw['country'].unique().tolist())
COLOR_MAP = {
    c: col for c, col in zip(
        COUNTRY_NAMES,
        ['#2d5016','#e07b39','#1f4e8c','#9b2335','#5c4b8a','#2a7a6e','#b5831a','#3d3d3d']
    )
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.markdown("---")

    selected_countries = st.multiselect(
        "Select countries",
        options=COUNTRY_NAMES,
        default=COUNTRY_NAMES[:4] if len(COUNTRY_NAMES) >= 4 else COUNTRY_NAMES
    )

    year_min = int(df_raw['year'].min())
    year_max = int(df_raw['year'].max())
    year_range = st.slider("Year range", year_min, year_max, (year_min, year_max))

    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown("""
**Okun's Law** proposes that when GDP grows faster than its potential rate,
unemployment tends to fall. The typical *Okun coefficient* ranges from
**−0.3 to −0.5** in developed economies.

*Data: World Bank (indicators NY.GDP.MKTP.KD.ZG & SL.UEM.TOTL.ZS)*
    """)

# ── Filter data ───────────────────────────────────────────────────────────────
if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()

df = df_raw[
    df_raw['country'].isin(selected_countries) &
    df_raw['year'].between(year_range[0], year_range[1])
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 📉 Okun's Law Explorer")
st.markdown(
    "An interactive tool examining the relationship between **GDP growth** and **unemployment** "
    "across countries. Built with World Bank open data."
)
st.markdown("---")

# ── Tab layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trend Overview", "🔍 Okun's Law Analysis", "📊 Country Comparison", "🔮 Prediction Mode", "📋 Data Table"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Trend Overview
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-title">GDP Growth & Unemployment Over Time</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Dual-axis chart — GDP growth rate (left axis) vs unemployment rate (right axis)</p>', unsafe_allow_html=True)

    for country in selected_countries:
        cdf = df[df['country'] == country]
        if cdf.empty:
            continue
        col = COLOR_MAP.get(country, '#333')

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cdf['year'], y=cdf['GDP_growth'],
            name='GDP Growth (%)', line=dict(color=col, width=2.5),
            mode='lines+markers', marker=dict(size=5)
        ))
        fig.add_trace(go.Scatter(
            x=cdf['year'], y=cdf['Unemployment'],
            name='Unemployment (%)', line=dict(color=col, width=2, dash='dot'),
            mode='lines+markers', marker=dict(size=5),
            yaxis='y2'
        ))
        fig.add_hline(y=0, line_dash='dash', line_color='#ccc', line_width=1)
        fig.update_layout(
            title=dict(text=country, font=dict(size=15, family='DM Serif Display')),
            xaxis=dict(title='Year', showgrid=False),
            yaxis=dict(title='GDP Growth (%)', showgrid=True, gridcolor='#f0f0f0'),
            yaxis2=dict(title='Unemployment (%)', overlaying='y', side='right', showgrid=False),
            legend=dict(orientation='h', y=-0.2),
            plot_bgcolor='white', paper_bgcolor='white',
            height=320, margin=dict(l=40, r=40, t=50, b=50)
        )
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Okun's Law Scatter
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-title">Okun\'s Law: GDP Growth vs ΔUnemployment</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Each point is one country-year. The slope of the trend line is the estimated Okun coefficient.</p>', unsafe_allow_html=True)

    fig2 = go.Figure()
    okun_results = []

    for country in selected_countries:
        cdf = df[df['country'] == country].dropna(subset=['GDP_growth', 'Delta_U'])
        if len(cdf) < 5:
            continue
        col = COLOR_MAP.get(country, '#333')

        # Scatter points
        fig2.add_trace(go.Scatter(
            x=cdf['GDP_growth'], y=cdf['Delta_U'],
            mode='markers',
            name=country,
            marker=dict(color=col, size=8, opacity=0.75, line=dict(width=1, color='white')),
            text=cdf['year'], hovertemplate='<b>%{text}</b><br>GDP: %{x:.1f}%<br>ΔU: %{y:.2f}pp<extra>' + country + '</extra>'
        ))

        # Regression line
        slope, intercept, r, p, _ = stats.linregress(cdf['GDP_growth'], cdf['Delta_U'])
        x_line = np.linspace(cdf['GDP_growth'].min(), cdf['GDP_growth'].max(), 60)
        y_line = slope * x_line + intercept
        fig2.add_trace(go.Scatter(
            x=x_line, y=y_line,
            mode='lines', showlegend=False,
            line=dict(color=col, width=1.5, dash='dot')
        ))
        okun_results.append({'Country': country, 'Okun Coeff': round(slope, 3),
                              'R²': round(r**2, 3), 'p-value': round(p, 3), 'n': len(cdf)})

    fig2.add_hline(y=0, line_dash='dash', line_color='#aaa', line_width=1)
    fig2.add_vline(x=0, line_dash='dash', line_color='#aaa', line_width=1)
    fig2.update_layout(
        xaxis=dict(title='GDP Growth Rate (%)', showgrid=False, zeroline=False),
        yaxis=dict(title='Change in Unemployment Rate (pp)', showgrid=True, gridcolor='#f0f0f0'),
        legend=dict(orientation='h', y=-0.2),
        plot_bgcolor='white', paper_bgcolor='white',
        height=460, margin=dict(l=50, r=30, t=30, b=80)
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Okun coefficient table
    if okun_results:
        st.markdown('<p class="section-title">Estimated Okun Coefficients</p>', unsafe_allow_html=True)
        res_df = pd.DataFrame(okun_results).set_index('Country')

        cols = st.columns(len(okun_results))
        for i, row in enumerate(okun_results):
            with cols[i]:
                sig = "✅ Significant" if row['p-value'] < 0.05 else "⚠️ Not significant"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">{row['Country']}</div>
                    <div class="value">{row['Okun Coeff']}</div>
                    <div class="sub">R² = {row['R²']} &nbsp;|&nbsp; {sig}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("""
        <div class="insight-box">
        📌 <b>How to read the Okun coefficient:</b> A value of −0.4 means that each additional 1 percentage point 
        of GDP growth is associated with a 0.4 pp <i>fall</i> in unemployment. 
        Coefficients closer to zero suggest a weaker GDP–employment link in that economy.
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Country Comparison
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-title">Country Summary Statistics</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Average GDP growth, average unemployment rate, and volatility across the selected period.</p>', unsafe_allow_html=True)

    summary = (
        df.groupby('country')
        .agg(
            Avg_GDP_Growth=('GDP_growth', 'mean'),
            Avg_Unemployment=('Unemployment', 'mean'),
            Std_GDP=('GDP_growth', 'std'),
            Std_Unem=('Unemployment', 'std'),
            Years=('year', 'count')
        )
        .round(2)
        .reset_index()
    )
    summary.columns = ['Country', 'Avg GDP Growth (%)', 'Avg Unemployment (%)',
                        'GDP Volatility (σ)', 'Unem Volatility (σ)', 'Observations']

    # Bubble chart
    fig3 = px.scatter(
        summary,
        x='Avg GDP Growth (%)', y='Avg Unemployment (%)',
        size='GDP Volatility (σ)', color='Country',
        color_discrete_map=COLOR_MAP,
        text='Country', hover_data=['Observations'],
        size_max=50, height=420
    )
    fig3.update_traces(textposition='top center', marker=dict(opacity=0.8))
    fig3.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(showgrid=False, zeroline=True, zerolinecolor='#ddd'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        showlegend=False, margin=dict(l=50, r=30, t=30, b=50)
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Bubble size = GDP growth volatility (standard deviation). Higher = more volatile economic cycles.")

    st.dataframe(summary.set_index('Country'), use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — Prediction Mode
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-title">🔮 Prediction Mode</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter a hypothetical GDP growth rate — the app will predict the expected change in unemployment for each country using its estimated Okun coefficient.</p>', unsafe_allow_html=True)

    # Build regression models for all available countries (full dataset)
    pred_models = {}
    for country in COUNTRY_NAMES:
        cdf = df_raw[df_raw['country'] == country].dropna(subset=['GDP_growth', 'Delta_U'])
        if len(cdf) >= 5:
            slope, intercept, r, p, _ = stats.linregress(cdf['GDP_growth'], cdf['Delta_U'])
            pred_models[country] = {
                'slope': slope, 'intercept': intercept,
                'r2': round(r**2, 3), 'p': round(p, 3),
                'avg_unem': cdf['Unemployment'].iloc[-1]  # most recent unemployment
            }

    st.markdown("---")
    col_input, col_info = st.columns([1, 2])

    with col_input:
        st.markdown("#### ⚙️ Scenario Settings")
        gdp_input = st.slider(
            "GDP Growth Rate (%)",
            min_value=-10.0, max_value=15.0,
            value=2.5, step=0.1,
            help="Drag to set a hypothetical annual GDP growth rate"
        )
        pred_countries = st.multiselect(
            "Countries to predict",
            options=list(pred_models.keys()),
            default=list(pred_models.keys())[:4]
        )
        st.markdown(f"""
        <div class="insight-box">
        You entered: <b>GDP growth = {gdp_input:+.1f}%</b><br>
        {"🔴 Recession territory" if gdp_input < 0 else ("🟡 Slow growth" if gdp_input < 2 else "🟢 Strong growth")}
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.markdown("#### 📖 How This Works")
        st.markdown("""
        This prediction uses each country's **estimated Okun coefficient** (β) from historical OLS regression:

        > **ΔUnemployment = α + β × GDP Growth**

        A negative β means higher GDP growth → falling unemployment.
        The prediction assumes the historical relationship holds — it is an *econometric estimate*, not a guarantee.
        """)

    st.markdown("---")

    if not pred_countries:
        st.warning("Please select at least one country above.")
    else:
        # Compute predictions
        pred_rows = []
        for country in pred_countries:
            m = pred_models[country]
            delta_u = m['slope'] * gdp_input + m['intercept']
            new_u = m['avg_unem'] + delta_u
            pred_rows.append({
                'Country': country,
                'Okun Coeff (β)': round(m['slope'], 3),
                'Predicted ΔUnemployment (pp)': round(delta_u, 3),
                'Current Unemployment (%)': round(m['avg_unem'], 2),
                'Predicted Unemployment (%)': round(max(new_u, 0), 2),
                'R²': m['r2'],
                'Reliable': '✅' if m['p'] < 0.05 else '⚠️'
            })
        pred_df = pd.DataFrame(pred_rows)

        # Bar chart — predicted ΔU
        bar_colors = ['#c0392b' if v > 0 else '#2d5016' for v in pred_df['Predicted ΔUnemployment (pp)']]
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Bar(
            x=pred_df['Country'],
            y=pred_df['Predicted ΔUnemployment (pp)'],
            marker_color=bar_colors,
            text=[f"{v:+.2f} pp" for v in pred_df['Predicted ΔUnemployment (pp)']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>ΔU = %{y:+.3f} pp<extra></extra>'
        ))
        fig_pred.add_hline(y=0, line_dash='dash', line_color='#aaa', line_width=1.5)
        fig_pred.update_layout(
            title=dict(
                text=f"Predicted Change in Unemployment when GDP Growth = {gdp_input:+.1f}%",
                font=dict(size=14, family='DM Serif Display')
            ),
            xaxis=dict(title='Country', showgrid=False),
            yaxis=dict(title='ΔUnemployment (percentage points)', showgrid=True, gridcolor='#f0f0f0'),
            plot_bgcolor='white', paper_bgcolor='white',
            height=380, margin=dict(l=50, r=30, t=60, b=50)
        )
        st.plotly_chart(fig_pred, use_container_width=True)

        # Gauge-style metric cards
        st.markdown("#### Predicted Unemployment Level (based on most recent data)")
        card_cols = st.columns(len(pred_countries))
        for i, row in pred_df.iterrows():
            delta = row['Predicted ΔUnemployment (pp)']
            arrow = "📉" if delta < 0 else "📈"
            color = "#2d5016" if delta < 0 else "#9b2335"
            with card_cols[i]:
                st.markdown(f"""
                <div class="metric-card" style="border-left-color:{color}">
                    <div class="label">{row['Country']} {row['Reliable']}</div>
                    <div class="value" style="color:{color}">{row['Predicted Unemployment (%)']:.1f}%</div>
                    <div class="sub">{arrow} {delta:+.2f} pp from current {row['Current Unemployment (%)']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Full Prediction Table")
        st.dataframe(pred_df.set_index('Country'), use_container_width=True)

        st.markdown("""
        <div class="insight-box">
        ⚠️ <b>Disclaimer:</b> Predictions are based on historical OLS regressions and assume a stable linear relationship.
        Countries marked ⚠️ have a statistically insignificant Okun coefficient (p ≥ 0.05) — treat those predictions with caution.
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — Raw Data
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-title">Underlying Dataset</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Source: World Bank Open Data. Indicators: NY.GDP.MKTP.KD.ZG (GDP growth) & SL.UEM.TOTL.ZS (Unemployment). Accessed April 2026.</p>', unsafe_allow_html=True)

    display_df = df[['country', 'year', 'GDP_growth', 'Unemployment', 'Delta_U']].copy()
    display_df.columns = ['Country', 'Year', 'GDP Growth (%)', 'Unemployment (%)', 'ΔUnemployment (pp)']
    display_df = display_df.sort_values(['Country', 'Year'])

    st.dataframe(
        display_df.set_index(['Country', 'Year']).style.format("{:.2f}"),
        use_container_width=True,
        height=400
    )

    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", data=csv, file_name='okun_data.csv', mime='text/csv')

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='font-size:12px;color:#aaa;text-align:center;'>"
    "ACC102 Mini Assignment · Track 4 · Xi'an Jiaotong-Liverpool University · 2024–25 Semester 2"
    "</p>",
    unsafe_allow_html=True
)
