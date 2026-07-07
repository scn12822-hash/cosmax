import base64
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="올영리뷰 부엉이",
    page_icon="🦉",
    layout="centered",
)

APP_DIR = Path(__file__).parent
HERO_IMAGE_PATH = APP_DIR / "hero_badge.png"
SAMPLE_CSV_PATH = APP_DIR / "review_sample_multi.csv"
MEMO_LOG_PATH = APP_DIR / "memo_log.csv"


# ----------------------------------------------------------------------------
# 스타일 (원본 HTML의 색상/톤을 그대로 반영)
# ----------------------------------------------------------------------------
def load_css():
    st.markdown(
        """
        <style>
        :root{
            --brand-50:#F2FBEE; --brand-100:#AEF0A1; --brand-500:#2E7D32;
            --brand-600:#1B5E20; --brand-700:#123A16;
            --good:#0ca30c; --critical:#d03b3b; --neutral-track:#e1e0d9;
            --surface-2:#ffffff; --page-plane:#F3FBF0;
            --text-primary:#0b0b0b; --text-secondary:#52514e; --text-muted:#898781;
            --border:rgba(11,11,11,0.10); --radius:14px;
        }

        .stApp { background: var(--page-plane); }

        /* ---- Hero ---- */
        .hero-box {
            text-align:center;
            padding:28px 16px 24px;
            min-height:200px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            border-radius:18px;
            margin-bottom: 20px;
            background-size:cover;
            background-position:center 32%;
        }
        .hero-box .logo{ font-size:40px; line-height:1; margin-bottom:8px; }
        .hero-box h1{
            margin:0 0 8px; font-size:28px; font-weight:900; letter-spacing:-0.01em;
            color: var(--text-primary);
            text-shadow: 0 1px 12px rgba(255,255,255,0.9), 0 1px 2px rgba(255,255,255,0.9);
        }
        .hero-box p{
            margin:0; font-size:14px; color:var(--text-secondary); line-height:1.6;
            text-shadow: 0 1px 10px rgba(255,255,255,0.9), 0 1px 2px rgba(255,255,255,0.9);
        }
        .hero-box .tag{
            display:inline-block; margin-top:10px; padding:5px 12px; border-radius:999px;
            background:var(--brand-100); color:var(--brand-700); font-size:13px; font-weight:600;
        }

        /* ---- Card ---- */
        .card{
            background:var(--surface-2); border:1px solid var(--border);
            border-radius:var(--radius); padding:20px; margin-bottom:16px;
        }
        .card h2{ margin:0 0 4px; font-size:17px; font-weight:700; color:var(--text-primary); }
        .card .desc{ margin:0 0 14px; font-size:13px; color:var(--text-muted); }

        /* ---- Product info ---- */
        .product-info{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }
        .info-item{ background:var(--page-plane); border-radius:10px; padding:10px 12px; }
        .info-item.wide{ grid-column:1 / -1; }
        .info-item .k{ font-size:12px; color:var(--text-muted); margin-bottom:2px; }
        .info-item .v{ font-size:14px; font-weight:600; color:var(--text-primary); word-break:break-word; }

        .buy-link{
            display:inline-flex; align-items:center; gap:4px; margin-top:8px; padding:6px 12px;
            background:var(--brand-500); color:#fff !important; border-radius:999px;
            font-size:13px; font-weight:600; text-decoration:none; width:fit-content;
        }
        .buy-link:hover{ background:var(--brand-600); }

        /* ---- Ratio bar ---- */
        .stat-meta{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px; }
        .avg-rating{
            display:inline-flex; align-items:center; gap:4px; padding:4px 10px; border-radius:999px;
            background:var(--page-plane); font-size:13px; font-weight:700; color:var(--text-primary);
        }
        .headline{ display:flex; align-items:baseline; gap:10px; margin-bottom:14px; flex-wrap:wrap; }
        .headline .value{ font-size:34px; font-weight:700; color:var(--good); line-height:1; }
        .headline .value.negative-emphasis{ color:var(--critical); }
        .headline .caption{ font-size:13px; color:var(--text-secondary); }

        .ratio-bar{
            display:flex; width:100%; height:20px; border-radius:999px; overflow:hidden;
            background:var(--neutral-track);
        }
        .ratio-bar .seg{ height:100%; }
        .ratio-bar .seg.positive{ background:var(--good); }
        .ratio-bar .seg.neutral{ background:var(--text-muted); }
        .ratio-bar .seg.negative{ background:var(--critical); }
        .ratio-bar .seg.gap{ width:2px; background:var(--surface-2); }

        .legend{ display:flex; gap:18px; margin-top:12px; font-size:13px; color:var(--text-secondary); flex-wrap:wrap; }
        .legend .item{ display:flex; align-items:center; gap:6px; }
        .legend .dot{ width:8px; height:8px; border-radius:50%; flex-shrink:0; }
        .legend .dot.positive{ background:var(--good); }
        .legend .dot.neutral{ background:var(--text-muted); }
        .legend .dot.negative{ background:var(--critical); }
        .legend b{ color:var(--text-primary); }

        .basis-note{
            margin-top:12px; font-size:12px; color:var(--text-muted);
            border-top:1px solid var(--border); padding-top:10px;
        }

        /* ---- Review summary ---- */
        .review-summary .line{
            display:flex; align-items:flex-start; gap:8px; padding:10px 0;
            border-top:1px solid var(--border);
        }
        .review-summary .line:first-child{ border-top:none; padding-top:0; }
        .review-summary .badge{
            flex-shrink:0; font-size:12px; font-weight:700; padding:2px 8px;
            border-radius:999px; margin-top:1px;
        }
        .review-summary .badge.positive{ background:var(--brand-50); color:var(--good); }
        .review-summary .badge.negative{ background:rgba(208,59,59,0.12); color:var(--critical); }
        .review-summary .badge.neutral{ background:var(--page-plane); color:var(--text-muted); }
        .review-summary .text{ font-size:14px; color:var(--text-primary); line-height:1.5; }

        .app-footer{ text-align:center; font-size:12px; color:var(--text-muted); margin-top:28px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    if HERO_IMAGE_PATH.exists():
        b64 = base64.b64encode(HERO_IMAGE_PATH.read_bytes()).decode()
        bg = (
            "linear-gradient(180deg, rgba(255,255,255,0.95) 0%, "
            "rgba(255,255,255,0.8) 40%, rgba(255,255,255,0.5) 75%), "
            f"url('data:image/png;base64,{b64}')"
        )
    else:
        bg = "linear-gradient(180deg, #ffffff 0%, #F2FBEE 100%)"

    st.markdown(
        f"""
        <div class="hero-box" style="background-image:{bg};">
            <div class="logo">🦉</div>
            <h1>🔍 올영리뷰 부엉이</h1>
            <p>올리브영 리뷰 엑셀을 넣으면<br/>긍정·부정 반응과 개선점을 정리해드려요 ⭐</p>
            <span class="tag">전략마케팅 · OBM 담당자용</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# 헤더(열) 자동 인식 로직 (원본 HEADER_MAP 그대로 이식)
# ----------------------------------------------------------------------------
HEADER_MAP = {
    "name": ["제품명", "상품명", "제품이름", "name", "product"],
    "price": ["가격", "판매가", "가격(원)", "price"],
    "date": ["출시일", "출시일자", "출시년월", "date", "release"],
    "desc": ["핵심 usp", "핵심usp", "usp", "설명", "제품설명", "상세설명", "description"],
    "rating": ["평점", "별점", "rating", "score"],
    "text": ["리뷰내용", "리뷰", "내용", "review", "content"],
    "url": ["구매링크", "제품링크", "상품링크", "상품url", "url", "link"],
    "image": ["대표이미지", "대표 이미지", "제품이미지", "이미지", "이미지url", "image", "image url", "imageurl", "thumbnail"],
    "review_date": ["리뷰작성일", "작성일", "리뷰날짜", "리뷰일자", "등록일", "review date", "reviewdate"],
}


def _norm(s: str) -> str:
    return str(s).replace(" ", "").lower()


def find_key(columns, candidates):
    normalized = {_norm(c): c for c in columns}
    for cand in candidates:
        c = _norm(cand)
        if c in normalized:
            return normalized[c]
    # 부분 일치 fallback
    for cand in candidates:
        c = _norm(cand)
        for col in columns:
            if c in _norm(col):
                return col
    return None


# ----------------------------------------------------------------------------
# 데이터 로딩
# ----------------------------------------------------------------------------
def load_dataframe(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        try:
            return pd.read_csv(uploaded_file, encoding="utf-8-sig")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding="cp949")
    else:
        return pd.read_excel(uploaded_file)


def load_sample_dataframe(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp949")


# ----------------------------------------------------------------------------
# 계산 로직
# ----------------------------------------------------------------------------
def to_numeric_score(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce"
    )


def format_date_value(raw) -> str:
    if pd.isna(raw) or str(raw).strip() == "":
        return "-"
    parsed = pd.to_datetime(raw, errors="coerce")
    if pd.isna(parsed):
        return str(raw)
    return parsed.strftime("%Y-%m-%d")


def truncate(text: str, length: int = 90) -> str:
    text = str(text)
    return text if len(text) <= length else text[:length] + "…"


# ----------------------------------------------------------------------------
# 렌더링: 제품 정보
# ----------------------------------------------------------------------------
def render_product_info(df, keys):
    name_key, price_key, date_key, desc_key, url_key, image_key = (
        keys["name"], keys["price"], keys["date"], keys["desc"], keys["url"], keys["image"]
    )

    distinct_names = set()
    if name_key:
        distinct_names = {str(v).strip() for v in df[name_key] if str(v).strip()}

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2>2. 제품 정보 💄</h2>", unsafe_allow_html=True)
    st.markdown('<p class="desc">엑셀에서 인식된 제품 기본 정보입니다.</p>', unsafe_allow_html=True)

    if len(distinct_names) > 1:
        st.markdown(
            f"""
            <div class="product-info">
              <div class="info-item wide">
                <div class="k">제품명</div>
                <div class="v">전체 제품 ({len(distinct_names)}개)</div>
              </div>
              <div class="info-item"><div class="k">가격</div><div class="v">-</div></div>
              <div class="info-item"><div class="k">출시일자</div><div class="v">-</div></div>
              <div class="info-item wide">
                <div class="k">핵심 USP</div>
                <div class="v">위에서 제품을 선택하면 해당 제품의 상세 정보가 표시됩니다.</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    first = df.iloc[0] if len(df) else {}

    p_name = str(first[name_key]) if name_key else "엑셀에서 제품명을 찾지 못했습니다"
    p_price = str(first[price_key]) if price_key else "-"
    p_date = format_date_value(first[date_key]) if date_key else "-"
    p_desc = str(first[desc_key]) if desc_key else "-"

    image_url = str(first[image_key]).strip() if image_key else ""
    if image_url and image_url.lower().startswith(("http://", "https://")):
        st.image(image_url, use_container_width=True)

    st.markdown(
        f"""
        <div class="product-info">
          <div class="info-item wide">
            <div class="k">제품명</div>
            <div class="v">{p_name}</div>
        """,
        unsafe_allow_html=True,
    )

    url = str(first[url_key]).strip() if url_key else ""
    if url and url.lower().startswith(("http://", "https://")):
        st.markdown(
            f'<a class="buy-link" href="{url}" target="_blank" rel="noopener noreferrer">올리브영에서 구매하기 →</a>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
          </div>
          <div class="info-item"><div class="k">가격</div><div class="v">{p_price}</div></div>
          <div class="info-item"><div class="k">출시일자</div><div class="v">{p_date}</div></div>
          <div class="info-item wide"><div class="k">핵심 USP</div><div class="v">{p_desc}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# 렌더링: 긍정/부정 비율
# ----------------------------------------------------------------------------
def render_ratio(df, keys):
    rating_key = keys["rating"]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2>3. 긍정 · 부정 반응 😊</h2>", unsafe_allow_html=True)
    st.markdown('<p class="desc">리뷰 평점 기준으로 계산한 비율입니다.</p>', unsafe_allow_html=True)

    if not rating_key:
        st.markdown(
            """
            <div class="stat-meta"><span class="avg-rating">⭐ 평균 평점 -</span></div>
            <div class="basis-note">평점 열을 찾지 못해 비율을 계산하지 못했습니다.
            엑셀에 "평점" 또는 "별점" 열이 있는지 확인해주세요.</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    scores = to_numeric_score(df[rating_key]).dropna()
    total = len(scores)

    avg_text = f"⭐ 평균 평점 {scores.mean():.1f} / 5.0" if total else "⭐ 평균 평점 -"

    date_key = keys["review_date"]
    if date_key:
        dates = pd.to_datetime(df[date_key], errors="coerce").dropna()
        if len(dates):
            dmin, dmax = dates.min(), dates.max()
            date_text = (
                f"📅 {dmin.strftime('%Y-%m-%d')}"
                if dmin == dmax
                else f"📅 {dmin.strftime('%Y-%m-%d')} ~ {dmax.strftime('%Y-%m-%d')}"
            )
        else:
            date_text = "📅 리뷰 작성일 값을 인식하지 못했습니다"
    else:
        date_text = "📅 리뷰 작성일 열을 찾지 못했습니다"

    st.markdown(
        f"""
        <div class="stat-meta">
          <span class="avg-rating">{avg_text}</span>
          <span class="avg-rating">{date_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if total == 0:
        st.markdown(
            f"""
            <div class="basis-note">평점 열을 찾지 못해 비율을 계산하지 못했습니다. (총 {len(df)}행)</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    positive = int((scores >= 4).sum())
    negative = int((scores <= 2).sum())
    neutral = total - positive - negative

    pos_pct = round(positive / total * 100)
    neg_pct = round(negative / total * 100)
    neu_pct = max(0, 100 - pos_pct - neg_pct)

    value_class = "value negative-emphasis" if pos_pct < neg_pct else "value"

    st.markdown(
        f"""
        <div class="headline">
          <span class="{value_class}">{pos_pct}%</span>
          <span class="caption">긍정 리뷰 비율 (총 <b>{total}</b>건 기준)</span>
        </div>
        <div class="ratio-bar">
          <div class="seg positive" style="width:{pos_pct}%"></div>
          <div class="seg gap"></div>
          <div class="seg neutral" style="width:{neu_pct}%"></div>
          <div class="seg gap"></div>
          <div class="seg negative" style="width:{neg_pct}%"></div>
        </div>
        <div class="legend">
          <div class="item"><span class="dot positive"></span>긍정 <b>{pos_pct}%</b></div>
          <div class="item"><span class="dot neutral"></span>중립 <b>{neu_pct}%</b></div>
          <div class="item"><span class="dot negative"></span>부정 <b>{neg_pct}%</b></div>
        </div>
        <div class="basis-note">'{rating_key}' 열의 평점을 기준으로, 4점 이상은 긍정, 2점 이하는 부정, 3점은 중립으로 분류했습니다.</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# 렌더링: 주요 리뷰 반응 요약
# ----------------------------------------------------------------------------
def render_summary(df, keys):
    rating_key, text_key = keys["rating"], keys["text"]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2>4. 주요 리뷰 반응 요약 🖌️</h2>", unsafe_allow_html=True)
    st.markdown('<p class="desc">긍정 · 부정 · 중립을 대표하는 리뷰를 한 줄씩 뽑았습니다.</p>', unsafe_allow_html=True)

    if not rating_key or not text_key:
        missing = ", ".join([x for x, k in [("평점", rating_key), ("리뷰내용", text_key)] if not k])
        msg = f"{missing} 열을 찾지 못해 리뷰 요약을 만들 수 없습니다."
        st.markdown(
            f"""
            <div class="review-summary">
              <div class="line"><span class="badge positive">긍정</span><span class="text">{msg}</span></div>
              <div class="line"><span class="badge negative">부정</span><span class="text">{msg}</span></div>
              <div class="line"><span class="badge neutral">중립</span><span class="text">{msg}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    scores = to_numeric_score(df[rating_key])
    texts = df[text_key].astype(str).str.strip()

    valid = scores.notna() & (texts != "")
    pos_texts = texts[valid & (scores >= 4)]
    neg_texts = texts[valid & (scores <= 2)]
    neu_texts = texts[valid & (scores == 3)]

    def pick(series):
        if series.empty:
            return None
        return series.loc[series.str.len().idxmax()]

    pos_pick, neg_pick, neu_pick = pick(pos_texts), pick(neg_texts), pick(neu_texts)

    pos_text = truncate(pos_pick) if pos_pick is not None else "긍정으로 분류된 리뷰가 없습니다."
    neg_text = truncate(neg_pick) if neg_pick is not None else "부정으로 분류된 리뷰가 없습니다."
    neu_text = truncate(neu_pick) if neu_pick is not None else "중립으로 분류된 리뷰가 없습니다."

    st.markdown(
        f"""
        <div class="review-summary">
          <div class="line"><span class="badge positive">긍정</span><span class="text">{pos_text}</span></div>
          <div class="line"><span class="badge negative">부정</span><span class="text">{neg_text}</span></div>
          <div class="line"><span class="badge neutral">중립</span><span class="text">{neu_text}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# 렌더링: 담당자 메모
# ----------------------------------------------------------------------------
def load_memo_log() -> pd.DataFrame:
    if MEMO_LOG_PATH.exists():
        try:
            return pd.read_csv(MEMO_LOG_PATH, encoding="utf-8-sig")
        except Exception:
            pass
    return pd.DataFrame(columns=["시각", "메모"])


def append_memo(text: str):
    log_df = load_memo_log()
    new_row = pd.DataFrame([{"시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "메모": text}])
    log_df = pd.concat([log_df, new_row], ignore_index=True)
    log_df.to_csv(MEMO_LOG_PATH, index=False, encoding="utf-8-sig")


def render_memo():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2>5. 담당자 메모 📝</h2>", unsafe_allow_html=True)
    st.markdown(
        '<p class="desc">리뷰를 검토하며 느낀 의견을 적고 Enter를 누르면 자동으로 저장·기록됩니다.</p>',
        unsafe_allow_html=True,
    )

    with st.form("memo_form", clear_on_submit=True):
        memo_text = st.text_input(
            "담당자 메모",
            placeholder="예: 부정 리뷰에서 흡수력 관련 언급이 많아 제형 개선을 검토해볼 필요가 있어 보입니다.",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("저장", use_container_width=True)

    if submitted and memo_text.strip():
        append_memo(memo_text.strip())
        st.success("메모가 저장되었습니다.")

    log_df = load_memo_log()
    if not log_df.empty:
        st.markdown('<p class="desc" style="margin-top:14px;">저장된 메모 기록</p>', unsafe_allow_html=True)
        rows_html = "".join(
            f"""
            <div class="line">
              <span class="text">
                <span style="color:var(--text-muted); font-size:12px;">{row['시각']}</span><br/>
                {row['메모']}
              </span>
            </div>
            """
            for _, row in log_df.iloc[::-1].iterrows()
        )
        st.markdown(f'<div class="review-summary">{rows_html}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# 메인
# ----------------------------------------------------------------------------
def main():
    load_css()
    render_hero()

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2>1. 리뷰 엑셀 업로드 📊</h2>", unsafe_allow_html=True)
    st.markdown(
        '<p class="desc">올리브영에서 내려받은 리뷰 데이터(.xlsx, .xls, .csv)를 올려주세요.</p>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "파일 선택", type=["xlsx", "xls", "csv"], label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is not None:
        try:
            df = load_dataframe(uploaded_file)
        except Exception as e:
            st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
            return
    elif SAMPLE_CSV_PATH.exists():
        try:
            df = load_sample_dataframe(SAMPLE_CSV_PATH)
        except Exception as e:
            st.error(f"샘플 데이터를 읽는 중 오류가 발생했습니다: {e}")
            return
        st.caption("📎 샘플 데이터(review_sample_multi.csv)로 미리보기 중입니다. 파일을 업로드하면 해당 데이터로 전환됩니다.")
    else:
        st.info("엑셀(또는 CSV) 파일을 업로드하면 분석 결과가 표시됩니다.")
        return

    df = df.dropna(how="all")
    if df.empty:
        st.warning("엑셀에서 데이터를 찾지 못했습니다. 파일을 확인해주세요.")
        return

    st.success(f"총 {len(df)}행을 읽었습니다.")

    columns = list(df.columns)
    keys = {k: find_key(columns, v) for k, v in HEADER_MAP.items()}

    # 제품 필터
    filtered_df = df
    if keys["name"]:
        names_series = df[keys["name"]].astype(str).str.strip()
        distinct_names = [n for n in dict.fromkeys(names_series) if n]
        if len(distinct_names) > 1:
            selected = st.selectbox("제품 선택", ["전체보기"] + distinct_names)
            if selected != "전체보기":
                filtered_df = df[names_series == selected].reset_index(drop=True)

    render_product_info(filtered_df, keys)
    render_ratio(filtered_df, keys)
    render_summary(filtered_df, keys)
    render_memo()

    st.markdown(
        '<div class="app-footer">올영리뷰 부엉이 · 내부 마케팅 도구 프로토타입</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
