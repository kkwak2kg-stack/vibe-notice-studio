import streamlit as st
from openai import OpenAI

# 1. 페이지 설정
st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

# CSS: 텍스트 박스 안의 문단 간격을 강제로 넓힘
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-box {
        background-color: #1e2129;
        padding: 40px;
        border-radius: 12px;
        line-height: 2.5; /* 줄 간격 대폭 확대 */
        color: #ffffff;
        font-size: 16px;
        white-space: pre-line; /* 줄바꿈 기호를 그대로 반영 */
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
        schedule = st.text_input("일정/시간")
        details = st.text_area("상세 내용", height=200)
        reward = st.text_input("보상 아이템")
        submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

with col2:
    st.subheader("📝 생성 결과 미리보기")
    
    if submitted:
        if not title or not details:
            st.warning("제목과 내용을 입력해주세요.")
        else:
            with st.spinner('가독성을 극대화하여 작성 중입니다...'):
                try:
                    system_instruction = f"""
                    너는 글로벌 대형 게임사의 시니어 파트장급 CM이야. 
                    유저들에게 신뢰감을 줄 수 있도록 격식 있고 가독성 좋은 공지를 {target_lang}로 작성해줘.

                    [작성 수칙 - 절대 준수]
                    1. 호칭: '안녕하세요.'로 시작해라.
                    2. 문체: 정중한 '하십시오체'를 사용해라.
                    3. 문단 구분: 각 문단 사이에는 반드시 빈 줄을 삽입해라.
                    4. 마무리 인사: 아래 세 줄은 반드시 각각 개별 줄로 작성하고 사이사이에 빈 줄을 넣어라.
                       항상 저희 게임을 아껴주시는 유저 여러분께 진심으로 감사드립니다.
                       앞으로도 더욱 즐거운 게임 환경을 제공하기 위해 최선을 다하겠습니다.
                       감사합니다.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": f"카테고리: {category}\n제목: {title}\n일정: {schedule}\n내용: {details}\n보상: {reward}"}
                        ],
                        temperature=0.3
                    )
                    
                    # 💡 [핵심 해결책] AI가 준 텍스트의 모든 줄바꿈(\n)을 2배(\n\n)로 변환하여 강제 공간 확보
                    raw_text = response.choices[0].message.content
                    formatted_text = raw_text.replace("\n\n", "\n\n\n").replace("\n", "\n\n")
                    
                    st.success("공지 생성이 완료되었습니다!")
                    st.divider()
                    
                    # 결과 출력 (pre-line 설정을 통해 엔터를 그대로 보여줌)
                    st.markdown(f'<div class="notice-box">{formatted_text}</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    st.download_button(label="💾 파일 저장", data=raw_text, file_name="Notice.txt")
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")
