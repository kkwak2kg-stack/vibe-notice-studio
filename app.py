import streamlit as st
from openai import OpenAI

# 1. 페이지 설정
st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

# CSS 보정 (결과창의 가독성 향상)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-box {
        background-color: #1e2129;
        padding: 30px;
        border-radius: 10px;
        line-height: 2.0;
        color: #ffffff;
        font-size: 16px;
        white-space: pre-wrap;
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
        title = st.text_input("핵심 제목", placeholder="공지 제목을 입력하세요.")
        schedule = st.text_input("일정/시간", placeholder="예: 2026.03.12 10:00 ~ 14:00 (KST)")
        details = st.text_area("상세 내용", placeholder="주요 내용을 상세히 적을수록 결과가 풍성해집니다.", height=200)
        reward = st.text_input("보상 아이템", placeholder="보상이 없다면 비워두세요.")
        submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

with col2:
    st.subheader("📝 생성 결과 미리보기")
    
    if submitted:
        if not title or not details:
            st.warning("제목과 내용을 입력해주세요.")
        else:
            with st.spinner(f'전문적인 공지를 작성 중입니다...'):
                try:
                    # [내용 풍성함 및 가독성 지침 강화]
                    system_instruction = f"""
                    너는 글로벌 대형 게임사의 시니어 파트장급 CM이야. 
                    유저들에게 신뢰감을 줄 수 있도록 격식 있고 풍성한 공지를 {target_lang}로 작성해줘.

                    [작성 수칙 - 무조건 준수]
                    1. 호칭 및 말투: '안녕하세요'로 시작하고 무조건 '하십시오체'를 사용해라.
                    2. 분량 확보: 본문은 입력된 정보를 바탕으로 최소 3~5문장 이상의 정중한 설명을 덧붙여 풍성하게 작성해라. (너무 짧게 요약하지 마라)
                    3. 가독성(엔터): 각 문단 사이에는 반드시 빈 줄(엔터 2번)을 넣어라. 특히 마무리 인사 세 줄은 각각 개별 줄로 작성해라.
                    4. 레이블 금지: '본문:', '상세:' 같은 단어를 노출하지 마라.
                    5. 마무리 양식:
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
                        temperature=0.5 # 일관성과 창의성의 적절한 조화
                    )
                    
                    final_notice = response.choices[0].message.content
                    
                    st.success("공지 생성이 완료되었습니다!")
                    st.divider()
                    
                    # 결과를 박스 안에 담아 가독성을 극대화함
                    st.markdown(f'<div class="notice-box">{final_notice}</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    st.download_button(label="💾 파일 저장", data=final_notice, file_name="Notice.md")
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")
