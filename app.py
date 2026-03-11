import streamlit as st
from openai import OpenAI

# 1. 페이지 설정
st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

# CSS: 줄 간격과 문단 간격을 코드 레벨에서 제어할 수 있도록 설정
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-box {
        background-color: #1e2129;
        padding: 45px;
        border-radius: 12px;
        color: #ffffff;
        font-size: 16px;
        line-height: 2.2; /* 문장 자체의 간격 */
    }
    /* 강제 줄바꿈을 위한 스타일 */
    .line-break {
        display: block;
        margin-bottom: 30px; 
        content: "";
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
        details = st.text_area("상세 내용", height=200, placeholder="예: 불건전 행위 10개 계정 영구 정지...")
        reward = st.text_input("보상 아이템")
        submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

with col2:
    st.subheader("📝 생성 결과 미리보기")
    
    if submitted:
        if not title or not details:
            st.warning("제목과 내용을 입력해주세요.")
        else:
            with st.spinner('문맥을 다듬고 가독성을 최적화 중입니다...'):
                try:
                    system_instruction = f"""
                    너는 대형 게임사의 시니어 CM 파트장이야. 
                    유저들이 읽었을 때 문맥이 자연스럽고 정중한 공지를 {target_lang}로 작성해줘.

                    [핵심 지침]
                    1. 문장 연결: 나열식이 아닌 자연스러운 문맥으로 작성해라. (예: ~진행하였습니다. 앞으로도 ~할 수 있도록 강력 대응하겠습니다.)
                    2. 말투: 무조건 '안녕하세요'로 시작하고 '하십시오체'를 유지해라.
                    3. 문단 구분: 각 문단 사이에는 반드시 [BR] 이라는 문자를 삽입해라.
                    4. 마무리 인사: 아래 세 줄 사이에도 각각 [BR]을 삽입해라.
                       - 항상 저희 게임을 아껴주시는 유저 여러분께 진심으로 감사드립니다.
                       - 앞으로도 더욱 즐거운 게임 환경을 제공하기 위해 최선을 다하겠습니다.
                       - 감사합니다.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": f"카테고리: {category}\n제목: {title}\n내용: {details}"}
                        ],
                        temperature=0.4
                    )
                    
                    res_text = response.choices[0].message.content
                    
                    # 💡 [핵심 해결책] AI가 넣은 [BR] 또는 줄바꿈 기호를 강력한 HTML 태그로 강제 치환
                    # 일반적인 줄바꿈(\n)을 모두 제거하고 HTML의 <br><br>로 직접 박아넣습니다.
                    formatted_notice = res_text.replace("[BR]", "<br><br>").replace("\n\n", "<br><br>").replace("\n", "<br><br>")
                    
                    st.success("공지 생성이 완료되었습니다!")
                    st.divider()
                    
                    # 결과를 안전하게 HTML로 렌더링
                    st.markdown(f'<div class="notice-box">{formatted_notice}</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    # 저장용은 태그 제거
                    save_text = formatted_notice.replace("<br><br>", "\n\n")
                    st.download_button(label="💾 파일 저장", data=save_text, file_name="Official_Notice.txt")
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")
