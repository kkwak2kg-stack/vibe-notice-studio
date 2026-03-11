import streamlit as st
from openai import OpenAI

# 1. 페이지 설정
st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

# CSS 보정 (가독성을 위한 간격 및 폰트 설정)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-box {
        background-color: #1e2129;
        padding: 40px;
        border-radius: 12px;
        line-height: 2.2; /* 줄 간격을 더 넓게 설정 */
        color: #ffffff;
        font-size: 16px;
    }
    stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #FF4B4B; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 글로벌 게임 공지사항 생성기")

# 2. 보안 설정 (Secrets)
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
            with st.spinner('가독성 최적화 공지를 작성 중입니다...'):
                try:
                    # [줄바꿈 태그(<br>) 사용 강제 지침]
                    system_instruction = f"""
                    너는 글로벌 대형 게임사의 시니어 파트장급 CM이야. 
                    유저들에게 신뢰감을 줄 수 있도록 격식 있고 가독성 좋은 공지를 {target_lang}로 작성해줘.

                    [작성 수칙 - 무조건 준수]
                    1. 호칭: '안녕하세요.'로 시작해라.
                    2. 문체: 정중한 '하십시오체'를 사용해라.
                    3. **물리적 줄바꿈(가장 중요)**: 
                       - 모든 문단(Paragraph)이 끝날 때마다 반드시 HTML 태그인 '<br><br>'를 삽입해라.
                       - 특히 마지막 인사 세 줄은 각각 뒤에 '<br><br>'를 붙여서 완전히 분리해라.
                    4. 분량: 본문은 3~5문장으로 풍성하게 작성해라.
                    5. 예시 구조:
                       안녕하세요.<br><br>
                       본문 내용입니다...<br><br>
                       상세 내용입니다...<br><br>
                       항상 저희 게임을 아껴주시는 유저 여러분께 진심으로 감사드립니다.<br><br>
                       앞으로도 더욱 즐거운 게임 환경을 제공하기 위해 최선을 다하겠습니다.<br><br>
                       감사합니다.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": f"카테고리: {category}\n제목: {title}\n일정: {schedule}\n내용: {details}\n보상: {reward}"}
                        ],
                        temperature=0.3 # 약간의 유연함 부여
                    )
                    
                    # AI가 생성한 텍스트에서 혹시 모를 레이블 제거
                    final_notice = response.choices[0].message.content.replace("본문:", "").replace("인사말:", "")
                    
                    st.success("공지 생성이 완료되었습니다!")
                    st.divider()
                    
                    # HTML 렌더링으로 <br> 태그를 확실하게 반영
                    st.markdown(f'<div class="notice-box">{final_notice}</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    # 파일 저장 시에는 브라우저용 태그를 제거하고 저장
                    clean_text = final_notice.replace("<br>", "\n")
                    st.download_button(label="💾 파일 저장", data=clean_text, file_name="Official_Notice.txt")
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")
