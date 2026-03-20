"""
신세계디에프 CSR 인터랙티브 대시보드
─────────────────────────────────────
iOS-inspired Design · Streamlit + Plotly + Pandas + Google AI (Gemini)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from difflib import SequenceMatcher
from itertools import combinations
import json, os, io, datetime

# ══════════════════════════════════════════════
# 0. 페이지 설정 & iOS-style CSS
# ══════════════════════════════════════════════
st.set_page_config(page_title="신세계디에프(면세점) 기부금 대시보드", page_icon="🏢",
                   layout="wide", initial_sidebar_state="expanded")

# ── Plotly 공통 레이아웃 (iOS 톤) ──
PLOTLY_LAYOUT = dict(
    template='plotly_white',
    font=dict(family="-apple-system, BlinkMacSystemFont, 'Pretendard', 'SF Pro Display', sans-serif",
              color='#1c1c1e'),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)
IOS_BLUE = '#007AFF'
IOS_GREEN = '#34C759'
IOS_RED = '#FF3B30'
IOS_ORANGE = '#FF9500'
IOS_GRAY = '#8E8E93'
IOS_DARK = '#1c1c1e'
IOS_CARD_BG = 'rgba(255,255,255,0.72)'

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* ── 전체 배경: iOS 라이트그레이 ── */
    .stApp {
        background: linear-gradient(180deg, #f2f2f7 0%, #e5e5ea 100%);
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
    }

    /* ── 메인 컨텐츠 영역 ── */
    .stMainBlockContainer { max-width: 1200px; }

    /* ── KPI 메트릭 카드: iOS glassmorphism ── */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.72);
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 16px; padding: 20px 24px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.10);
    }
    div[data-testid="stMetric"] label {
        color: #8e8e93 !important; font-size: 0.8rem !important;
        font-weight: 500 !important; letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1c1c1e !important; font-weight: 700 !important;
        font-size: 1.5rem !important;
    }

    /* ── 사이드바: iOS 라이트 글래스 ── */
    section[data-testid="stSidebar"] > div {
        background: rgba(242,242,247,0.92);
        backdrop-filter: blur(30px);
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #1c1c1e !important;
        font-family: 'Pretendard', -apple-system, sans-serif !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] small {
        color: #3a3a3c !important;
        font-family: 'Pretendard', -apple-system, sans-serif !important;
    }
    section[data-testid="stSidebar"] span {
        color: #3a3a3c !important;
    }

    /* ── 헤더 카드 ── */
    .ios-header {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 50%, #AF52DE 100%);
        color: white; padding: 32px 40px; border-radius: 20px;
        margin-bottom: 28px;
        box-shadow: 0 8px 32px rgba(0,122,255,0.25);
    }
    .ios-header h1 {
        color: white; margin: 0; font-size: 1.75rem; font-weight: 700;
        letter-spacing: -0.02em;
    }
    .ios-header p {
        color: rgba(255,255,255,0.78); margin: 8px 0 0 0;
        font-size: 0.95rem; font-weight: 400;
    }

    /* ── 섹션 서브헤더 ── */
    h3, .stSubheader {
        color: #1c1c1e !important; font-weight: 700 !important;
        letter-spacing: -0.01em;
    }

    /* ── 구분선 ── */
    hr { border: none; border-top: 1px solid rgba(60,60,67,0.12); margin: 28px 0; }

    /* ── 버튼: iOS 스타일 ── */
    .stButton > button {
        background: #007AFF !important; color: white !important;
        border: none !important; border-radius: 12px !important;
        font-weight: 600 !important; font-size: 0.9rem !important;
        padding: 10px 20px !important; letter-spacing: -0.01em;
        transition: all 0.2s ease !important;
        font-family: 'Pretendard', -apple-system, sans-serif !important;
    }
    .stButton > button:hover {
        background: #0056CC !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(0,122,255,0.3) !important;
    }
    .stButton > button:active {
        transform: scale(0.97) !important;
    }

    /* ── 다운로드 버튼 ── */
    .stDownloadButton > button {
        background: rgba(0,122,255,0.08) !important; color: #007AFF !important;
        border: 1.5px solid rgba(0,122,255,0.25) !important;
        border-radius: 12px !important; font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(0,122,255,0.15) !important;
        border-color: #007AFF !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.6) !important;
        border-radius: 12px !important; font-weight: 600 !important;
    }

    /* ── 채팅 메시지 ── */
    .stChatMessage {
        background: rgba(255,255,255,0.65) !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
        padding: 16px 28px 16px 16px !important;
    }
    .stChatMessage [data-testid="stMarkdownContainer"] {
        padding-right: 16px !important;
    }

    /* ── Dataframe ── */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* ── 경고/성공 알림 iOS 스타일 ── */
    .stAlert {
        border-radius: 14px !important;
        backdrop-filter: blur(10px) !important;
        border: none !important;
    }

    /* ── 탭 간격 ── */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important; font-weight: 600 !important;
    }

    /* ── iOS 피벗 테이블 ── */
    .ios-table {
        border-radius: 16px; overflow: hidden;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06);
        background: rgba(255,255,255,0.72);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.5);
    }
    .ios-table table {
        width: 100%; border-collapse: collapse; font-size: 14px;
        font-family: 'Pretendard', -apple-system, sans-serif;
    }
    .ios-table th {
        background: #1c1c1e; color: #f2f2f7;
        padding: 12px 16px; font-weight: 600;
        font-size: 0.8rem; text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .ios-table td {
        padding: 10px 16px; border-bottom: 1px solid rgba(60,60,67,0.08);
        color: #1c1c1e;
    }
    .ios-table tr:last-child td { border-bottom: none; }
    .ios-table tr:hover td { background: rgba(0,122,255,0.04); }
    .ios-table .total-row td {
        background: rgba(0,122,255,0.06); font-weight: 700;
    }
    .ios-table .total-col { font-weight: 700; color: #007AFF; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ios-header">
    <h1>신세계디에프(면세점) 기부금 대시보드</h1>
    <p>경영진 보고 · 실무 자동화 · AI 분석 통합 플랫폼</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 1. 재무 데이터 영구 저장
# ══════════════════════════════════════════════
FINANCIAL_JSON = "financial_data.json"
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

def load_financial():
    if os.path.exists(FINANCIAL_JSON):
        with open(FINANCIAL_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_financial(data: dict):
    with open(FINANCIAL_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

financial_memory = load_financial()

# ══════════════════════════════════════════════
# 2. 사이드바 — 파일 업로드
# ══════════════════════════════════════════════
with st.sidebar:
    st.header("📂 데이터 업로드")
    uploaded = st.file_uploader("CSV 또는 Excel 파일을 업로드하세요",
                                type=["csv", "xlsx", "xls"])

# ══════════════════════════════════════════════
# 3. 데이터 로드 & 전처리
# ══════════════════════════════════════════════
if uploaded is None:
    st.info("⬅️ 사이드바에서 CSV 또는 Excel 파일을 업로드해 주세요.")
    st.stop()

if uploaded.name.endswith(".csv"):
    df = pd.read_csv(uploaded, encoding="utf-8-sig")
else:
    df = pd.read_excel(uploaded)

EXPECTED_COLS = ['No', '연도', '사업장', '계정 명', '계정 세목명', '전표일자',
                 '귀속부서 명', '테마', '기부사업', '적요', '비고', '금액', '기부처']

if '활동' in df.columns and '기부사업' not in df.columns:
    df = df.rename(columns={'활동': '기부사업'})

missing = [c for c in EXPECTED_COLS if c not in df.columns]
if missing:
    st.error(f"필수 컬럼 누락: {missing}")
    st.stop()

df['전표일자'] = pd.to_datetime(df['전표일자'], errors='coerce')

def quarter_label(dt):
    if pd.isna(dt):
        return "미분류"
    return f"Q{(dt.month - 1)//3 + 1}"

df['분기'] = df['전표일자'].apply(quarter_label)
df['월'] = df['전표일자'].dt.month
df['금액(백만원)'] = df['금액'] / 1_000_000

# ══════════════════════════════════════════════
# 4. 오타 감지 (유사도 95%)
# ══════════════════════════════════════════════
@st.cache_data
def detect_similar_donors(donors, threshold=0.95):
    pairs = []
    uniq = sorted(set(d for d in donors if pd.notna(d) and str(d).strip()))
    for a, b in combinations(uniq, 2):
        r = SequenceMatcher(None, str(a), str(b)).ratio()
        if r >= threshold and a != b:
            pairs.append((a, b, round(r * 100, 1)))
    return pairs

similar = detect_similar_donors(df['기부처'].dropna().unique())
if similar:
    for a, b, pct in similar:
        st.warning(f"⚠️ 유사한 기부처 명칭이 발견되었습니다. 데이터 통일이 필요할 수 있습니다: **[{a}]** 와 **[{b}]** (유사도 {pct}%)")

# ══════════════════════════════════════════════
# 5. 사이드바 — 재무 지표 & 필터
# ══════════════════════════════════════════════
data_years = sorted(df['연도'].dropna().unique())

with st.sidebar:
    st.divider()
    st.header("💰 연도별 재무 지표")
    st.caption("데이터에 포함된 각 연도별로 입력하세요.")

    yearly_financials = {}
    for yr in data_years:
        yr_str = str(int(yr))
        saved = financial_memory.get(yr_str, {})
        with st.expander(f"{yr_str}년", expanded=False):
            b = st.number_input("CSR 목표 예산 (백만원)", min_value=0,
                                value=int(saved.get("budget", 5000)), step=100, key=f"budget_{yr_str}")
            o = st.number_input("영업이익 (백만원)", min_value=0,
                                value=int(saved.get("op_income", 100000)), step=1000, key=f"op_{yr_str}")
            r = st.number_input("공시매출 (백만원)", min_value=0,
                                value=int(saved.get("revenue", 1000000)), step=10000, key=f"rev_{yr_str}")
            yearly_financials[yr_str] = {"budget": b, "op_income": o, "revenue": r}

    if st.button("💾 재무 지표 저장", use_container_width=True):
        save_financial(yearly_financials)
        st.success("저장 완료!")

    st.divider()
    st.header("🔍 데이터 필터")
    sel_years = st.multiselect("연도", data_years, default=data_years)
    quarters = sorted(df['분기'].unique())
    sel_quarters = st.multiselect("분기", quarters, default=quarters)
    themes = sorted(df['테마'].dropna().unique())
    sel_themes = st.multiselect("테마", themes, default=themes)
    donors_list = sorted(df['기부처'].dropna().unique())
    sel_donors = st.multiselect("기부처", donors_list, default=donors_list)

# 필터 적용
mask = (df['연도'].isin(sel_years) & df['분기'].isin(sel_quarters)
        & df['테마'].isin(sel_themes) & df['기부처'].isin(sel_donors))
fdf = df[mask].copy()

if fdf.empty:
    st.warning("필터 조건에 해당하는 데이터가 없습니다.")
    st.stop()

def get_yr_fin(yr, field):
    return yearly_financials.get(str(int(yr)), {}).get(field, 0)

latest_year = max(sel_years)
latest_yr_str = str(int(latest_year))
latest_budget = yearly_financials.get(latest_yr_str, {}).get("budget", 0)
latest_donation = fdf[fdf['연도'] == latest_year]['금액(백만원)'].sum()

# ══════════════════════════════════════════════
# 6. KPI 카드
# ══════════════════════════════════════════════
total_donation = fdf['금액(백만원)'].sum()
record_count = len(fdf)
donor_count = fdf['기부처'].nunique()
avg_per_donor = total_donation / donor_count if donor_count > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("총 기부금액", f"{total_donation:,.0f} 백만원")
k2.metric("기부 건수", f"{record_count:,}건")
k3.metric("기부처 수", f"{donor_count:,}곳")
k4.metric("기부처별 평균", f"{avg_per_donor:,.0f} 백만원")

# ══════════════════════════════════════════════
# 7. 예산 집행률 게이지 + YoY
# ══════════════════════════════════════════════
col_gauge, col_yoy = st.columns([1, 1])

with col_gauge:
    st.subheader(f"📊 {latest_yr_str}년 예산 집행률")
    burn_rate = (latest_donation / latest_budget) * 100 if latest_budget > 0 else 0
    remaining = latest_budget - latest_donation

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(burn_rate, 1),
        number={"suffix": "%", "font": {"size": 48, "color": IOS_DARK,
                 "family": "'Pretendard', -apple-system, sans-serif"}},
        delta={"reference": 100, "suffix": "%p",
               "increasing": {"color": IOS_GREEN}, "decreasing": {"color": IOS_ORANGE}},
        gauge={
            "axis": {"range": [0, 120], "tickwidth": 1, "tickcolor": IOS_GRAY,
                     "tickvals": [0, 25, 50, 75, 100, 120]},
            "bar": {"color": IOS_BLUE, "thickness": 0.75},
            "bgcolor": "#f2f2f7",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 25], "color": "#FFE5E5"},
                {"range": [25, 50], "color": "#FFF3E0"},
                {"range": [50, 75], "color": "#FFFDE7"},
                {"range": [75, 100], "color": "#E8F5E9"},
                {"range": [100, 120], "color": "#C8E6C9"},
            ],
            "threshold": {"line": {"color": IOS_GREEN, "width": 3},
                          "thickness": 0.8, "value": 100},
        },
        title={"text": f"집행 {latest_donation:,.0f} / 예산 {latest_budget:,.0f} 백만원"
               + (f"  ·  잔액 {remaining:,.0f}" if remaining > 0 else f"  ·  초과 {abs(remaining):,.0f}"),
               "font": {"size": 13, "color": IOS_GRAY}},
    ))
    fig_gauge.update_layout(height=380, margin=dict(t=60, b=20, l=30, r=30), **PLOTLY_LAYOUT)
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_yoy:
    st.subheader("📈 전년 대비 증감률 (YoY)")

    sel_years_set = set(sel_years)
    prev_years = {yr - 1 for yr in sel_years}
    yoy_years = sel_years_set | prev_years
    yoy_src = df[df['연도'].isin(yoy_years) & df['분기'].isin(sel_quarters)
                 & df['테마'].isin(sel_themes) & df['기부처'].isin(sel_donors)].copy()
    yoy_base = yoy_src.groupby('연도')['금액(백만원)'].sum().reset_index()
    yoy_base = yoy_base.sort_values('연도').reset_index(drop=True)

    yoy_rows = []
    for _, row in yoy_base.iterrows():
        curr_yr, curr_amt = row['연도'], row['금액(백만원)']
        if curr_yr not in sel_years_set:
            continue
        prev = yoy_base[yoy_base['연도'] == curr_yr - 1]
        if not prev.empty:
            prev_amt = prev.iloc[0]['금액(백만원)']
            chg = ((curr_amt - prev_amt) / prev_amt * 100) if prev_amt != 0 else 0
            yoy_rows.append({'연도': str(int(curr_yr)), '당기(백만원)': curr_amt,
                             '전년(백만원)': prev_amt, '증감률(%)': round(chg, 1)})

    if yoy_rows:
        yoy_df = pd.DataFrame(yoy_rows)
        colors_yoy = [IOS_GREEN if v >= 0 else IOS_RED for v in yoy_df['증감률(%)']]

        fig_yoy = go.Figure()
        fig_yoy.add_trace(go.Bar(
            x=yoy_df['연도'], y=yoy_df['증감률(%)'], marker_color=colors_yoy,
            marker_line_width=0, marker_cornerradius=6,
            text=yoy_df['증감률(%)'].apply(lambda v: f"+{v:.1f}%" if v >= 0 else f"{v:.1f}%"),
            textposition='outside', textfont=dict(size=13, color=IOS_DARK)))
        fig_yoy.add_hline(y=0, line_dash="dot", line_color=IOS_GRAY, line_width=1)
        fig_yoy.update_layout(height=280, margin=dict(t=10, b=40, l=40, r=20),
                              yaxis=dict(title='증감률(%)'), xaxis=dict(title=''),
                              showlegend=False, **PLOTLY_LAYOUT)
        st.plotly_chart(fig_yoy, use_container_width=True)

        yoy_d = yoy_df.copy()
        yoy_d['당기(백만원)'] = yoy_d['당기(백만원)'].apply(lambda x: f"{x:,.0f}")
        yoy_d['전년(백만원)'] = yoy_d['전년(백만원)'].apply(lambda x: f"{x:,.0f}")
        yoy_d['증감률(%)'] = yoy_d['증감률(%)'].apply(
            lambda v: f"🔺 +{v:.1f}%" if v > 0 else (f"🔻 {v:.1f}%" if v < 0 else f"— {v:.1f}%"))

        # HTML 테이블 (숫자 셀 오른쪽 정렬)
        yoy_html = '<div class="ios-table"><table>'
        yoy_html += '<tr>'
        for col in yoy_d.columns:
            align = 'left' if col == '연도' else 'right'
            yoy_html += f'<th style="text-align:{align};">{col}</th>'
        yoy_html += '</tr>'
        for _, row in yoy_d.iterrows():
            yoy_html += '<tr>'
            for col in yoy_d.columns:
                align = 'left' if col == '연도' else 'right'
                yoy_html += f'<td style="text-align:{align};">{row[col]}</td>'
            yoy_html += '</tr>'
        yoy_html += '</table></div>'
        st.markdown(yoy_html, unsafe_allow_html=True)
    else:
        st.info("연속된 2개 연도 이상의 데이터가 필요합니다.")

# ══════════════════════════════════════════════
# 8. 기부처 TOP5 + 영업이익·매출 대비 비율
# ══════════════════════════════════════════════
st.divider()
viz_top5, viz_ratio = st.columns([1, 1])

with viz_top5:
    st.subheader("🏆 기부처 TOP 5")
    donor_totals = fdf.groupby('기부처')['금액(백만원)'].sum().sort_values(ascending=False)
    top5 = donor_totals.head(5).reset_index()
    top5.columns = ['기부처', '금액(백만원)']
    top5['비중(%)'] = (top5['금액(백만원)'] / total_donation * 100).round(1)

    fig_top5 = go.Figure(go.Bar(
        x=top5['금액(백만원)'], y=top5['기부처'], orientation='h',
        marker_color=IOS_BLUE, marker_cornerradius=6,
        text=top5.apply(lambda r: f"{r['금액(백만원)']:,.0f}  ({r['비중(%)']:.1f}%)", axis=1),
        textposition='outside', textfont=dict(color=IOS_DARK, size=12)))
    fig_top5.update_layout(height=350, margin=dict(t=10, b=30, l=10, r=20),
                           xaxis=dict(title='금액(백만원)'), yaxis=dict(autorange='reversed'),
                           **PLOTLY_LAYOUT)
    st.plotly_chart(fig_top5, use_container_width=True)

with viz_ratio:
    st.subheader("📊 영업이익·매출 대비 기부금 비율")
    yearly = fdf.groupby('연도')['금액(백만원)'].sum().reset_index()
    yearly.columns = ['연도', '기부금액']
    yearly['영업이익 대비(%)'] = yearly.apply(
        lambda r: round(r['기부금액'] / get_yr_fin(r['연도'], 'op_income') * 100, 3)
        if get_yr_fin(r['연도'], 'op_income') > 0 else 0, axis=1)
    yearly['공시매출 대비(%)'] = yearly.apply(
        lambda r: round(r['기부금액'] / get_yr_fin(r['연도'], 'revenue') * 100, 4)
        if get_yr_fin(r['연도'], 'revenue') > 0 else 0, axis=1)

    fig_ratio = go.Figure()
    fig_ratio.add_trace(go.Bar(
        x=yearly['연도'].astype(str), y=yearly['기부금액'],
        name='기부금액(백만원)', marker_color=IOS_BLUE, opacity=0.65,
        marker_cornerradius=6, yaxis='y'))
    fig_ratio.add_trace(go.Scatter(
        x=yearly['연도'].astype(str), y=yearly['영업이익 대비(%)'],
        name='영업이익 대비(%)', mode='lines+markers',
        line=dict(color=IOS_RED, width=2.5), marker=dict(size=8), yaxis='y2'))
    fig_ratio.add_trace(go.Scatter(
        x=yearly['연도'].astype(str), y=yearly['공시매출 대비(%)'],
        name='공시매출 대비(%)', mode='lines+markers',
        line=dict(color=IOS_GREEN, width=2.5, dash='dot'), marker=dict(size=8), yaxis='y2'))
    fig_ratio.update_layout(
        yaxis=dict(title='기부금액(백만원)', side='left'),
        yaxis2=dict(title='비율(%)', overlaying='y', side='right'),
        legend=dict(orientation='h', y=-0.25),
        height=350, margin=dict(t=10, b=80), **PLOTLY_LAYOUT)
    st.plotly_chart(fig_ratio, use_container_width=True)

# ══════════════════════════════════════════════
# 9. 테마 도넛 + 월별 집행 추이
# ══════════════════════════════════════════════
st.divider()
viz_donut, viz_monthly = st.columns(2)

with viz_donut:
    st.subheader("🍩 테마별 비중")
    theme_sum = fdf.groupby('테마')['금액(백만원)'].sum().reset_index()
    theme_sum.columns = ['테마', '금액']
    ios_palette = ['#007AFF', '#34C759', '#FF9500', '#FF3B30', '#AF52DE',
                   '#5AC8FA', '#FF2D55', '#FFCC00', '#5856D6', '#64D2FF']
    fig_donut = go.Figure(go.Pie(
        labels=theme_sum['테마'], values=theme_sum['금액'],
        hole=0.6, textinfo='label+percent',
        marker=dict(colors=ios_palette[:len(theme_sum)], line=dict(width=2, color='#f2f2f7'))))
    fig_donut.update_layout(height=400, margin=dict(t=30, b=30),
                            legend=dict(orientation='h', y=-0.15), **PLOTLY_LAYOUT)
    st.plotly_chart(fig_donut, use_container_width=True)

with viz_monthly:
    st.subheader("📅 월별 집행 추이")
    monthly = fdf.groupby(['연도', '월'])['금액(백만원)'].sum().reset_index()
    monthly['연도'] = monthly['연도'].astype(str)
    monthly = monthly.sort_values(['연도', '월'])
    fig_monthly = px.bar(monthly, x='월', y='금액(백만원)', color='연도',
                         barmode='group', color_discrete_sequence=ios_palette, text_auto='.0f')
    fig_monthly.update_layout(height=400, xaxis=dict(title='월', tickmode='linear', dtick=1),
                              yaxis=dict(title='금액(백만원)'), legend=dict(orientation='h', y=-0.2),
                              margin=dict(t=10, b=80), **PLOTLY_LAYOUT)
    fig_monthly.update_traces(textposition='outside', textfont_size=10,
                              marker_cornerradius=4)
    st.plotly_chart(fig_monthly, use_container_width=True)

# ══════════════════════════════════════════════
# 10. 분기별 흐름
# ══════════════════════════════════════════════
st.subheader("📉 분기별 기부금액 흐름")
qtr_flow = fdf.groupby(['연도', '분기'])['금액(백만원)'].sum().reset_index()
qtr_flow['기간'] = qtr_flow['연도'].astype(str) + "-" + qtr_flow['분기']
qtr_flow = qtr_flow.sort_values(['연도', '분기'])
fig_line = px.line(qtr_flow, x='기간', y='금액(백만원)', color='연도',
                   markers=True, color_discrete_sequence=ios_palette)
fig_line.update_traces(line_width=2.5, marker_size=8)
fig_line.update_layout(height=380, legend=dict(orientation='h', y=-0.2),
                       margin=dict(t=20, b=80), **PLOTLY_LAYOUT)
st.plotly_chart(fig_line, use_container_width=True)

# ══════════════════════════════════════════════
# 11. 피벗 테이블 (동적 피벗 + iOS 테이블)
# ══════════════════════════════════════════════
st.divider()
st.subheader("📋 요약 피벗 테이블")

PIVOT_CHOICES = ['연도', '분기', '테마', '기부처', '기부사업', '귀속부서 명', '사업장', '계정 명']
available_pivot = [c for c in PIVOT_CHOICES if c in fdf.columns]

pv_cols = st.columns([1, 1, 2])
with pv_cols[0]:
    pv_index = st.multiselect("행 기준", available_pivot, default=['연도', '분기'], key="pv_idx")
with pv_cols[1]:
    remaining = [c for c in available_pivot if c not in pv_index]
    pv_columns = st.selectbox("열 기준", remaining,
                              index=remaining.index('테마') if '테마' in remaining else 0, key="pv_col")

if not pv_index:
    st.warning("행 기준을 1개 이상 선택해 주세요.")
    st.stop()

pivot_amt = pd.pivot_table(fdf, values='금액(백만원)', index=pv_index,
                           columns=pv_columns, aggfunc='sum', fill_value=0,
                           margins=True, margins_name='합계')
pivot_pct = pivot_amt.copy()
for idx in pivot_pct.index:
    rt = pivot_pct.loc[idx, '합계'] if '합계' in pivot_pct.columns else pivot_pct.loc[idx].sum()
    pivot_pct.loc[idx] = (pivot_pct.loc[idx] / rt * 100).round(1) if rt > 0 else 0

pivot_display = pivot_amt.copy().reset_index()
pivot_pct_r = pivot_pct.reset_index()
for ic in pv_index:
    pivot_display[ic] = pivot_display[ic].astype(str)
val_cols = [c for c in pivot_display.columns if c not in pv_index]
for col in val_cols:
    pivot_display[col] = pivot_display.apply(
        lambda row, c=col: f"{row[c]:,.0f} ({pivot_pct_r.loc[row.name, c]:.1f}%)", axis=1)

# iOS 스타일 HTML 테이블
def render_ios_pivot(pdf, idx_cols):
    html = '<div class="ios-table"><table>'
    html += '<tr>'
    for col in pdf.columns:
        align = 'left' if col in idx_cols else 'right'
        html += f'<th style="text-align:{align};">{col}</th>'
    html += '</tr>'
    for _, row in pdf.iterrows():
        is_total = any(str(row[ic]) == '합계' for ic in idx_cols)
        cls = ' class="total-row"' if is_total else ''
        html += f'<tr{cls}>'
        for col in pdf.columns:
            align = 'left' if col in idx_cols else 'right'
            tc = ' class="total-col"' if col == '합계' else ''
            html += f'<td style="text-align:{align};"{tc}>{row[col]}</td>'
        html += '</tr>'
    html += '</table></div>'
    return html

st.markdown(render_ios_pivot(pivot_display, pv_index), unsafe_allow_html=True)

# ── 다운로드 ──
st.markdown("")
buf_main = io.BytesIO()
with pd.ExcelWriter(buf_main, engine='openpyxl') as w:
    pivot_amt.to_excel(w, sheet_name='피벗_금액(백만원)')
    pivot_pct.to_excel(w, sheet_name='피벗_비율(%)')
st.download_button("📥 요약 피벗 테이블 다운로드 (Excel)", buf_main.getvalue(),
                   file_name="CSR_피벗요약.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   use_container_width=True)

with st.expander("📦 추가 다운로드 (CSV · 상세 원본)"):
    dl1, dl2, dl3 = st.columns(3)
    with dl1:
        st.download_button("📥 피벗 CSV", pivot_amt.to_csv(encoding='utf-8-sig'),
                           file_name="CSR_피벗요약.csv", mime="text/csv")
    with dl2:
        st.download_button("📥 상세원본 CSV", fdf.to_csv(index=False, encoding='utf-8-sig'),
                           file_name="CSR_상세원본.csv", mime="text/csv")
    with dl3:
        buf_r = io.BytesIO()
        with pd.ExcelWriter(buf_r, engine='openpyxl') as w:
            fdf.to_excel(w, index=False, sheet_name='상세원본')
        st.download_button("📥 상세원본 Excel", buf_r.getvalue(),
                           file_name="CSR_상세원본.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with st.expander("🔎 전체 원본 데이터 보기"):
    display_df = fdf[EXPECTED_COLS + ['분기', '금액(백만원)']].copy()
    display_df['전표일자'] = display_df['전표일자'].dt.strftime('%Y-%m-%d')
    display_df['금액'] = display_df['금액'].apply(lambda x: f"{x:,.0f}")
    display_df['금액(백만원)'] = display_df['금액(백만원)'].apply(lambda x: f"{x:,.0f}")
    st.dataframe(display_df, use_container_width=True, height=500)

# ══════════════════════════════════════════════
# 12. Gemini AI 챗봇
# ══════════════════════════════════════════════
st.divider()
st.subheader("🤖 AI 분석 챗봇")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 프리셋 버튼
st.caption("자주 쓰는 질문을 클릭하면 바로 분석합니다.")
preset_cols = st.columns(4)
presets = ["데이터 필터 기준의 기간의 신세계디에프 CSR 실적 보고서(핵심 요약)을 써줘",
           "신세계디에프(면세점) CSR/ESG 언론 보도를 기반으로 대외 이미지를 추론해줘",
           "문화면세점을 지향하는데 어떻게 해야할까",
           "국내 면세점 등 동업계 CSR/ESG 활동 벤치마킹을 해줘"]
preset_clicked = None
for i, pq in enumerate(presets):
    with preset_cols[i]:
        if st.button(pq, key=f"preset_{i}", use_container_width=True):
            preset_clicked = pq

def build_data_context(dataframe):
    """Gemini에 전송할 데이터 컨텍스트 생성 (보안 마스킹 적용)"""

    # ── 기부처 마스킹: 실명 → 익명 매핑 ──
    unique_donors = sorted(dataframe['기부처'].dropna().unique())
    donor_mask = {name: f"기부처{chr(65+i)}" if i < 26 else f"기부처{i+1}"
                  for i, name in enumerate(unique_donors)}
    masked_df = dataframe.copy()
    masked_df['기부처_masked'] = masked_df['기부처'].map(donor_mask).fillna('기부처_기타')

    # ── 기부사업 마스킹: 고유명사 제거, 유형만 전달 ──
    if '기부사업' in masked_df.columns:
        biz_types = sorted(masked_df['기부사업'].dropna().unique())
    else:
        biz_types = []

    s = []
    s.append(f"총 {len(masked_df):,}건, 기부금 합계 {masked_df['금액(백만원)'].sum():,.0f}백만원")
    s.append(f"연도: {sorted(masked_df['연도'].unique())}")
    s.append(f"테마: {sorted(masked_df['테마'].unique())}")
    s.append(f"기부처(익명): {sorted(masked_df['기부처_masked'].unique())}")
    if biz_types:
        s.append(f"기부사업 유형: {biz_types}")

    s.append(f"\n[테마별 금액]\n{masked_df.groupby('테마')['금액(백만원)'].sum().sort_values(ascending=False).to_string()}")
    s.append(f"\n[연도별 금액]\n{masked_df.groupby('연도')['금액(백만원)'].sum().sort_values().to_string()}")
    s.append(f"\n[기부처 TOP10 (익명)]\n{masked_df.groupby('기부처_masked')['금액(백만원)'].sum().sort_values(ascending=False).head(10).to_string()}")
    s.append(f"\n[분기별 금액]\n{masked_df.groupby(['연도','분기'])['금액(백만원)'].sum().to_string()}")
    s.append(f"\n[월별 금액]\n{masked_df.groupby(['연도','월'])['금액(백만원)'].sum().to_string()}")

    # 적요·비고는 전송하지 않음 (자유텍스트 보안 리스크)

    fin_lines = []
    for yr in sorted(masked_df['연도'].unique()):
        yr_str = str(int(yr))
        fd = yearly_financials.get(yr_str, {})
        fin_lines.append(f"  {yr_str}년 - 예산:{fd.get('budget',0):,}, 영업이익:{fd.get('op_income',0):,}, 공시매출:{fd.get('revenue',0):,} (백만원)")
    s.append(f"\n[연도별 재무 지표]\n" + "\n".join(fin_lines))
    return "\n".join(s)

data_context = build_data_context(fdf)

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_q = st.chat_input("CSR 데이터에 대해 질문하세요")
if preset_clicked:
    user_q = preset_clicked

if user_q:
    st.session_state.chat_history.append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.markdown(user_q)

    if GEMINI_API_KEY:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=GEMINI_API_KEY)
            system_prompt = f"""당신은 신세계디에프(SHINSEGAE DUTY FREE)의 기부금 데이터 분석 AI임.

[문서 작성 방식 — 반드시 준수]

1. 구조화 (개조식)
   - 번호(1., 2.) 또는 기호(•, -)를 활용하여 내용 시각화
   - 들여쓰기를 통해 상위 항목과 하위 항목의 관계 명시

2. 어투 (평어체)
   - 격식 없이 낮추지도 높이지도 않는 평서형 어미 사용
   - 종결 방식: '~임/함' 명사형 종결로 간결성 극대화
   - 예: "전년 대비 12.3% 증가함.", "예산 집행률 81.6%임."
   - 존댓말, 인사, 마무리 멘트 사용 금지

3. 수치 표기
   - 백만원 단위, 천단위 구분기호(,) 사용

4. 답변 구조 (반드시 아래 순서대로. 각 섹션은 한 번만 작성. 절대 반복 금지.)

   ■ 전문 (상세 분석) — 먼저 작성
   - 근거 데이터, 세부 항목별 분석, 비교, 추이 등을 개조식으로 상세 기술
   - 필요 시 하위 항목으로 구분하여 깊이 있게 작성
   - 분량 제한 없음. 충분히 상세하게 작성할 것
   - 같은 내용을 두 번 쓰지 말 것. 한 번만 기술함.

   ■ 시사점 / 제안 (해당 시)
   - 데이터 기반 인사이트 또는 전략적 제안

   ■ 핵심 요약 — 맨 마지막에 작성
   - 위 전문 내용을 3~5줄로 압축 정리
   - 결론과 핵심 수치만 간결하게 기술

5. 중복 금지
   - 전문, 시사점, 핵심 요약 각각 한 번씩만 작성함
   - 동일 섹션을 반복하거나 같은 내용을 다른 표현으로 재기술하지 말 것

[홍보/벤치마킹 — Google Search 활용]
- 언론 보도, 평판, 동업계 비교 질문 시 인터넷 검색으로 외부 정보를 찾아 답변
- 검색 키워드: "신세계디에프 CSR", "신세계면세점 사회공헌", "면세점 ESG" 등
- 출처 URL 간단히 첨부

[현재 필터링된 데이터 요약]
{data_context}

[{latest_yr_str}년 예산 집행률] {burn_rate:.1f}%
"""
            search_tool = types.Tool(google_search=types.GoogleSearch())
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=user_q,
                config=types.GenerateContentConfig(system_instruction=system_prompt,
                                                   tools=[search_tool]))

            answer_parts = []
            candidates = getattr(response, 'candidates', None)
            if candidates and len(candidates) > 0:
                content = getattr(candidates[0], 'content', None)
                parts = getattr(content, 'parts', None) if content else None
                if parts:
                    for part in parts:
                        if hasattr(part, 'text') and part.text:
                            answer_parts.append(part.text)
                grounding_meta = getattr(candidates[0], 'grounding_metadata', None)
                if grounding_meta:
                    chunks = getattr(grounding_meta, 'grounding_chunks', None)
                    if chunks:
                        src_lines, seen = [], set()
                        for chunk in chunks:
                            web = getattr(chunk, 'web', None)
                            if web:
                                url = getattr(web, 'uri', '')
                                title = getattr(web, 'title', '')
                                if url and url not in seen:
                                    seen.add(url)
                                    src_lines.append(f"- [{title or url}]({url})")
                        if src_lines:
                            answer_parts.append("\n\n---\n📰 **참고 출처**\n" + "\n".join(src_lines))

            answer = "\n".join(answer_parts) if answer_parts else "응답을 생성하지 못했습니다. 다시 시도해 주세요."

        except ImportError:
            answer = "⚠️ `google-genai` 패키지가 필요합니다.\n\n```bash\npip install google-genai\n```"
        except Exception as e:
            answer = f"⚠️ Gemini API 호출 오류: {e}"
    else:
        answer = "⚠️ API 연결에 문제가 발생했습니다."

    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

# ══════════════════════════════════════════════
# 13. 푸터
# ══════════════════════════════════════════════
st.divider()
st.markdown("""
<div style="text-align:center; padding:16px 0; color:#8e8e93; font-size:0.85rem;">
    © 신세계디에프(면세점) 기부금 대시보드 · Built with Streamlit + Plotly + Google AI
</div>
""", unsafe_allow_html=True)
