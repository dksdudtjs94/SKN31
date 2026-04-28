import streamlit as st
import pandas as pd
import FAQ_Data as qd
import re

# DB에서 DataFrame 형태로 로드
df = qd.load_data_to_db("SELECT * FROM car_faq")

st.title("Car FAQ")
st.markdown("---")

# 카테고리 선택
with st.container():
    st.markdown('<div class="input-box"><span class="input-label">📂 카테고리를 선택하세요</span>', unsafe_allow_html=True)
    selected_category = st.selectbox("", df['category'].unique(), label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# 검색어 입력
with st.container():
    st.markdown('<div class="input-box"><span class="input-label">🔍 검색어를 입력하세요</span>', unsafe_allow_html=True)
    search_query = st.text_input("", "", placeholder="예: 견적, 기준...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# ── 카테고리/검색어 바뀌면 페이지 초기화 ──
state_key = f"{selected_category}_{search_query}"
if "prev_state_key" not in st.session_state or st.session_state.prev_state_key != state_key:
    st.session_state.current_page = 1
    st.session_state.prev_state_key = state_key

# 필터링
filtered_df = df[df['category'] == selected_category].copy()
filtered_df['question'] = filtered_df['question'].apply(
    lambda x: x.rstrip()[:-4].rstrip() if isinstance(x, str) and x.rstrip().endswith("연장하다") else x
)

if search_query:
    filtered_df = filtered_df[
        filtered_df['question'].str.contains(search_query, case=False, na=False) |
        filtered_df['answer'].str.contains(search_query, case=False, na=False)
    ]

# 결과 개수 & 페이지 계산
results_len = len(filtered_df)
PAGE_SIZE = 10
total_pages = max(1, -(-results_len // PAGE_SIZE))  # 올림 나눗셈

if results_len > 0:
    st.info(f"총 {results_len}개의 FAQ가 검색되었습니다.")
else:
    st.warning("검색 결과가 없습니다. 다시 입력해주세요.")

# 하이라이트 함수
def highlight_keyword(text, keyword):
    if not keyword:
        return text
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(f'<span style="color:#ff4757;font-weight:600;">\\g<0></span>', text)

# CSS
st.markdown("""
<style>
div[data-baseweb="select"] * {
    cursor: pointer !important;
}
.faq-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 20px 25px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.faq-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}
.faq-question {
    font-size: 19px;
    font-weight: 700;
    color: #2d3436;
    margin-bottom: 12px;
}
.faq-answer {
    font-size: 16px;
    color: #444;
    line-height: 1.6;
    padding-left: 5px;
    border-left: 3px solid #ff6b6b20;
}
.faq-answer-line {
    margin-bottom: 6px;
}
.faq-source {
    font-size: 14px;
    color: #636e72;
    margin-top: 12px;
}

/* 첫번째 컬럼 - 왼쪽 정렬 */
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child [data-testid="stVerticalBlock"] {
    align-items: flex-start;
}


/* 두번째 컬럼 - 가운데 정렬 */
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stVerticalBlock"] {
    align-items: center;
    justify-content: center;
    height: 100%;
}
            
/* 세번째 컬럼 - 오른쪽 정렬 */
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stVerticalBlock"] {
    align-items: flex-end;
}

/* 버튼 자체 세로 가운데 */
[data-testid="stHorizontalBlock"] [data-testid="stButton"] button {
    height: 40px;
}
</style>
""", unsafe_allow_html=True)

# ── 현재 페이지 슬라이싱 ──
if results_len > 0:
    start = (st.session_state.current_page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    display_df = filtered_df.iloc[start:end]

    for idx, row in display_df.iterrows():
        q_text = row['question'].strip()
        question_html = highlight_keyword(q_text, search_query)

        answer_lines = row['answer'].splitlines()
        answer_html = "".join(
            [f'<div class="faq-answer-line">{highlight_keyword(line, search_query)}</div>'
             for line in answer_lines if line.strip()]
        )

        st.markdown(f"""
        <div class="faq-card">
            <div class="faq-question">💬 {question_html}</div>
            <div class="faq-answer">{answer_html}</div>
            {f'<div class="faq-source">🔗 출처: {row["site"]}</div>' if pd.notna(row.get("site")) else ""}
        </div>
        """, unsafe_allow_html=True)

    # ── 페이지네이션 버튼 ──
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns([1, 2, 1])

    with cols[0]:
        if st.session_state.current_page > 1:
            if st.button("◀ 이전"):
                st.session_state.current_page -= 1
                st.rerun()

    with cols[1]:
        st.markdown(
            f'<div style="text-align:center; font-weight:600;">'
            f'{st.session_state.current_page} / {total_pages} 페이지</div>',
            unsafe_allow_html=True
        )

    with cols[2]:
        if st.session_state.current_page < total_pages:
            if st.button("다음 ▶"):
                st.session_state.current_page += 1
                st.rerun()