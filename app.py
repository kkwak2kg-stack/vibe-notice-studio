import streamlit as st
from openai import OpenAI

# 1. 페이지 설정 및 디자인
st.set_page_config(
    page_title="Global Game Notice Studio Pro", 
    page_icon="🌐", 
    layout="wide"
)

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
    .stMarkdown p {
        line-height: 1.8;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 글로벌 게임 공지사항 생성기")

# 2. 보안 설정
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
                    # [가독성 및 호칭 지침 대폭 강화]
                    lang_guidelines = {
                        "한국어": "첫 인사는 반드시 '안녕하세요'로 시작하세요. 모든 문단 사이에는 반드시 엔터를 두 번 입력하여 '빈 줄'을 만드세요.",
                        "영어(English)": "Start with 'Hello'. Use double line breaks between paragraphs.",
                        "일본어(日本語)": "Start with 'こんにちは'. Ensure clear spacing between sections.",
                        "중국어 간체(简体中文)": "Start with '你好'. Use clear line breaks.",
                        "중국어 번체(繁體中文)": "Start with '你好'. Use clear line breaks."
                    }

                    system_instruction = f"""
                    너는 글로벌 대형 게임사의 시니어 파트장급 CM이야. 
                    유저들에게 공식적인 신뢰감을 주는 공지를 {target_lang}로 작성해줘.

                    [작성 수칙 - 절대 준수]
                    1. 인사말: 한국어 기준, 무조건 '안녕하세요'로 시작해라. '안녕하십니까'는 금지다.
                    2. **문단 간격(가독성)**: 문단과 문단 사이에는 반드시 '완전한 빈 줄'이 하나 이상 존재해야 한다. (텍스트 사이에 \n\n을 강제로 넣어라)
                    3. 문체: {lang_guidelines.get(target_lang)} 하십시오체(~합니다)를 사용해라.
                    4. 레이블 금지: '내용 요약', '상세 정보' 같은 제목을 텍스트로 노출하지 마라.
                    5. 구성 예시:
                       안녕하세요. 운영팀입니다. (빈 줄)
                       본문 내용입니다. (빈 줄)
                       - 상세 리스트 (빈 줄)
                       항상 감사드립니다. (빈 줄)
                       최선을 다하겠습니다. (빈 줄)
                       감사합니다.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": f"카테고리: {category}\n제목: {title}\n일정: {schedule}\n내용: {details}\n보상: {reward}"}
                        ],
                        temperature=0 # 일관성 고정
                    )
                    
                    final_notice = response.choices[0].message.content
                    
                    st.success("공지 생성이 완료되었습니다!")
                    st.divider()
                    
                    # 💡 [핵심] 생성된 텍스트의 가독성을 위해 마크다운 뷰어에 표시
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
