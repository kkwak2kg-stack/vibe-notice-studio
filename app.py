import streamlit as st
from openai import OpenAI

# 1. 페이지 설정
st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

# CSS: 문단(<p>) 사이의 간격을 40px로 강제 설정하여 시각적 분리 확보
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-box {
        background-color: #1e2129;
        padding: 45px;
        border-radius: 12px;
        color: #ffffff;
        font-size: 16px;
        line-height: 1.8;
    }
    .notice-box p {
        margin-bottom: 35px; /* 문단 간의 간격을 아주 넓게 설정 */
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
        details = st.text_area("상세 내용", height=200, placeholder="예: 불건전 행위 10개 계정 영구 정지, 공정한 환경 조성 위해 강력 조치 예정")
        reward = st.text_input("보상 아이템")
        submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

with col2:
    st.subheader("📝 생성 결과 미리보기")
    
    if submitted:
        if not title or not details:
            st.warning("제목과 내용을 입력해주세요.")
        else:
            with st.spinner('문맥을 다듬어 공지를 작성 중입니다...'):
                try:
                    # [문맥 자연스러움 및 물리적 문단 분리 지침]
                    system_instruction = f"""
                    너는 대형 게임사의 시니어 CM 파트장이야. 
                    유저들이 읽었을 때 문맥이 매끄럽고 정중하며, 가독성이 뛰어난 공지를 {target_lang}로 작성해줘.

                    [작성 수칙 - 무조건 준수]
                    1. 문장 연결: 단순 나열이 아니라 문장 간의 인과관계를 살려 자연스럽게 연결해라.
                       (예: "영구 정지 조치를 취하였습니다. 이는 ~입니다" 대신 "영구 정지 조치를 진행하였습니다. 앞으로도 ~할 수 있도록 강력한 대응을 지속할 예정입니다"와 같이 연결)
                    2. 호칭: '안녕하세요.'로 시작하고 격식 있는 '하십시오체'를 유지해라.
                    3. **물리적 문단 처리(HTML)**:
                       - 모든 독립된 문단은 반드시 <p>태그로 감싸라. 
                       - 예: <p>안녕하세요.</p><p>본문 내용...</p>
                    4. 마무리 인사: 아래 세 줄은 각각 개별 <p>태그로 감싸서 확실히 분리해라.
                       - 항상 저희 게임을 아껴주시는 유저 여러분께 진심으로 감사드립니다.
                       - 앞으로도 더욱 즐거운 게임 환경을 제공하기 위해 최선을 다하겠습니다.
                       - 감사합니다.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": f"카테고리: {category}\n제목: {title}\n일정: {schedule}\n내용: {details}\n보상: {reward}"}
                        ],
                        temperature=0.4
                    )
                    
                    final_notice = response.choices[0].message.content
                    
                    st.success("공지 생성이 완료되었습니다!")
                    st.divider()
                    
                    # 💡 HTML 렌더링을 통해 <p> 태그의 margin-bottom(간격)을 확실히 적용
                    st.markdown(f'<div class="notice-box">{final_notice}</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    # 저장용 텍스트에서는 태그 제거
                    clean_save = final_notice.replace("<p>", "").replace("</p>", "\n\n")
                    st.download_button(label="💾 파일 저장", data=clean_save, file_name="Official_Notice.txt")
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")
