import streamlit as st
from openai import OpenAI

# 1. 페이지 설정
st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

# CSS: 비정상적인 간격을 잡고, 문단별로 깔끔한 여백을 부여
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-container {
        background-color: #1e2129;
        padding: 40px;
        border-radius: 12px;
        color: #ffffff;
        font-size: 16px;
        line-height: 1.6; /* 기본 줄 간격으로 복구 */
    }
    .notice-paragraph {
        margin-bottom: 25px; /* 문단 사이의 간격을 25px로 고정 */
        display: block;
    }
    stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #FF4B4B; color: white; font-weight: bold; }
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
        category = st.selectbox("공지 카테고리", ["정기 점검 안내", "업데이트 패치노트", "이벤트 안내", "긴급 장애 사과문", "당첨자 발표", "기타(운영 정책/일반 공지)"])
        target_lang = st.selectbox("출력 언어 선택", ["한국어", "영어(English)", "일본어(日本語)", "중국어 간체(简体中文)", "중국어 번체(繁體中文)"])
        title = st.text_input("핵심 제목")
        details = st.text_area("상세 내용", height=150, placeholder="불건전 행위 10개 계정 정지 등 핵심 내용을 적으세요.")
        submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

with col2:
    st.subheader("📝 생성 결과 미리보기")
    
    if submitted:
        if not title or not details:
            st.warning("제목과 내용을 입력해주세요.")
        else:
            with st.spinner('가독성을 교정 중입니다...'):
                try:
                    system_instruction = f"""
                    너는 글로벌 대형 게임사의 시니어 CM 파트장이야. 
                    유저들이 읽기 편하도록 문맥이 자연스럽고 정중한 공지를 {target_lang}로 작성해줘.

                    [작성 지침]
                    1. 인사말은 '안녕하세요.'로 시작할 것.
                    2. 문체는 정중한 '하십시오체'를 사용할 것.
                    3. 문단 구분은 반드시 [P] 라는 기호로 구분할 것.
                    4. 예시: 안녕하세요.[P]최근 게임 내에서...[P]항상 감사드립니다.[P]최선을 다하겠습니다.[P]감사합니다.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": f"제목: {title}\n내용: {details}"}
                        ],
                        temperature=0.3
                    )
                    
                    res_text = response.choices[0].message.content
                    
                    # 💡 [핵심 해결책] [P] 기호를 기준으로 문장을 쪼개서 각각 HTML 태그로 감쌉니다.
                    paragraphs = res_text.split("[P]")
                    
                    html_content = '<div class="notice-container">'
                    for p in paragraphs:
                        if p.strip():
                            html_content += f'<span class="notice-paragraph">{p.strip()}</span>'
                    html_content += '</div>'
                    
                    st.success("공지 생성이 완료되었습니다!")
                    st.divider()
                    
                    # 최종 렌더링
                    st.markdown(html_content, unsafe_allow_html=True)
                    
                    st.divider()
                    # 저장용 파일 (기호 제거)
                    save_text = res_text.replace("[P]", "\n\n")
                    st.download_button(label="💾 파일 저장", data=save_text, file_name="Notice.txt")
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")
