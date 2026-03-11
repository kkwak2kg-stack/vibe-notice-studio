import streamlit as st
from openai import OpenAI

# 1. 페이지 설정 및 디자인
st.set_page_config(
    page_title="Global Game Notice Studio Pro", 
    page_icon="🌐", 
    layout="wide"
)

# UI 레이아웃 스타일
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 글로벌 게임 공지사항 생성기")
st.caption("일관된 문체와 최적화된 가독성으로 전문적인 공지를 생성합니다.")

# 2. 보안 설정 (Secrets 사용)
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except Exception:
    st.error("⚠️ Streamlit Secrets 설정을 확인해주세요.")
    st.stop()

# 3. UI 레이아웃
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📋 공지 데이터 입력")
    with st.form("notice_form"):
        category = st.selectbox("공지 카테고리", 
                            ["정기 점검 안내", "업데이트 패치노트", "이벤트 안내", 
                             "긴급 장애 사과문", "당첨자 발표", "기타(운영 정책/일반 공지)"])
        
        target_lang = st.selectbox("출력 언어 선택", 
                            ["한국어", "영어(English)", "일본어(日本語)", 
                             "중국어 간체(简体中文)", "중국어 번체(繁體中文)"])
        
        title = st.text_input("핵심 제목", placeholder="공지 제목을 입력하세요.")
        schedule = st.text_input("일정/시간", placeholder="예: 2026.03.12 10:00 ~ 14:00 (KST)")
        details = st.text_area("상세 내용", placeholder="주요 내용을 입력하세요.", height=200)
        reward = st.text_input("보상 아이템", placeholder="보상이 없다면 비워두세요.")
        
        submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

with col2:
    st.subheader("📝 생성 결과 미리보기")
    
    if submitted:
        if not title or not details:
            st.warning("제목과 내용을 입력해주세요.")
        else:
            with st.spinner(f'공지를 작성 중입니다...'):
                try:
                    # 격식 있는 말투 및 가독성 지침
                    lang_guidelines = {
                        "한국어": "엄격한 '하십시오체' 사용. 각 문단 사이에는 반드시 빈 줄을 삽입하여 줄바꿈을 명확히 하세요.",
                        "영어(English)": "Formal tone. Use clear paragraph breaks with empty lines.",
                        "일본어(日本語)": "Formal Keigo. Ensure double line breaks between sections.",
                        "중국어 간체(简体中文)": "Formal tone. Clear spacing between paragraphs.",
                        "중국어 번체(繁體中文)": "Formal tone. Clear spacing between paragraphs."
                    }

                    system_instruction = f"""
                    너는 글로벌 대형 게임사의 시니어 파트장급 CM이야. 
                    유저들에게 공식적인 신뢰감을 주는 공지를 {target_lang}로 작성해줘.

                    [작성 수칙 - 절대 준수]
                    1. 문체: {lang_guidelines.get(target_lang)}
                    2. 가독성: 각 문단이나 섹션(인사말, 본문, 안내, 맺음말 등) 사이에는 반드시 **'2번의 줄바꿈(Double Newline)'**을 수행하여 빈 줄을 삽입해라.
                    3. 레이블 금지: '내용 요약', '상세 정보' 같은 불필요한 소제목 레이블을 텍스트로 쓰지 마라.
                    4. 형식: 제목은 마크다운 큰 제목(#)으로 작성하고, 중요한 일정이나 항목은 리스트(-) 형식을 사용해라.
                    5. 구조: [인사말] - [공지 본문] - [일정/항목 안내] - [주의사항 및 보상] - [감사 인사] 순으로 섹션 이름 없이 작성해라.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": f"카테고리: {category}\n제목: {title}\n일정: {schedule}\n내용: {details}\n보상: {reward}"}
                        ],
                        # temperature를 0으로 설정하여 일관성을 확보합니다.
                        temperature=0
                    )
                    
                    final_notice = response.choices[0].message.content
                    
                    st.success("공지 생성이 완료되었습니다!")
                    st.divider()
                    # 마크다운 렌더링을 통해 가독성을 확보합니다.
                    st.markdown(final_notice)
                    st.divider()
                    
                    st.download_button(
                        label=f"💾 {target_lang} 공지 파일 저장",
                        data=final_notice,
                        file_name=f"Official_Notice.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")
