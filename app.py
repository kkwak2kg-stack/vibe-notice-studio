import streamlit as st
from openai import OpenAI

# 1. 페이지 설정 및 디자인 (기존 툴과 통일감 유지)
st.set_page_config(
    page_title="Global Game Notice Studio Pro", 
    page_icon="🌐", 
    layout="wide"
)

# 커스텀 CSS로 좀 더 '게임 운영 툴'다운 분위기 연출
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 글로벌 게임 공지사항 생성기")
st.caption("OpenAI GPT-4o 기반 | 정기 점검, 패치노트, 이벤트 및 불건전 행위 대응 공지 지원")

# 2. 보안 설정: Secrets에서 API 키 자동 로드
# 이 방식은 화면에 키가 노출되지 않으며 보안상 가장 안전합니다.
try:
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        # 로컬 테스트 환경 배려 (Secrets가 없을 경우 사이드바 노출)
        api_key = st.sidebar.text_input("OpenAI API Key (Secrets 미설정 시 입력)", type="password")
    
    if not api_key:
        st.info("사이드바에서 API 키를 입력하거나 Streamlit Secrets 설정을 완료해주세요.")
        st.stop()
        
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"설정 오류: {e}")
    st.stop()

# 3. UI 레이아웃 구성
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📋 공지 데이터 입력")
    with st.form("notice_form"):
        # 카테고리 구성 (기타/일반 공지 포함)
        category = st.selectbox("공지 카테고리", 
                            ["정기 점검 안내", "업데이트 패치노트", "이벤트 안내", 
                             "긴급 장애 사과문", "당첨자 발표", "기타(운영 정책/일반 공지)"])
        
        # 다국어 선택 드롭다운
        target_lang = st.selectbox("출력 언어 선택", 
                            ["한국어", "영어(English)", "일본어(日本語)", 
                             "중국어 간체(简体中文)", "중국어 번체(繁體中文)"])
        
        title = st.text_input("핵심 제목", placeholder="예: 불건전 행위 대응 및 운영 정책 안내")
        
        schedule = st.text_input("일정/시간", placeholder="예: 2026.03.12 10:00 ~ 14:00 (KST)")
        
        details = st.text_area("상세 내용", 
                            placeholder="공지할 핵심 데이터를 적어주세요. (예: 정지 계정 수, 패치 리스트, 이벤트 보상 등)", 
                            height=200)
        
        reward = st.text_input("보상 아이템", placeholder="예: 루비 500개 (없을 경우 비워둠)")
        
        submitted = st.form_submit_button("✨ 글로벌 공지 생성 시작")

with col2:
    st.subheader("📝 생성 결과 미리보기")
    
    if submitted:
        if not title or not details:
            st.warning("제목과 상세 내용을 입력해야 공지를 생성할 수 있습니다.")
        else:
            with st.spinner(f'{target_lang} 버전으로 전문 CM이 작성 중입니다...'):
                try:
                    # 언어별 맞춤 로컬라이징 지시문
                    lang_guidelines = {
                        "한국어": "정중한 '해요체'를 사용하고 유저를 '모험가님' 혹은 '계승자님'이라 불러줘.",
                        "영어(English)": "Use a professional yet friendly tone. Address users as 'Adventurers' or 'Players'. Use standard game industry terminology.",
                        "일본어(日本語)": "Very polite 'Desu/Masu' style. Address users as '冒험者の皆様' (Adventurers). Use formal game service honorifics.",
                        "중국어 간체(简体中文)": "Professional and formal tone. Address users as '各位勇士' or '各位玩家'. Use simplified characters.",
                        "중국어 번체(繁體中文)": "Professional and formal tone using Traditional Chinese characters. Address users as '各位勇士'."
                    }

                    # AI 페르소나 및 작성 지침 (바이브 코딩의 핵심)
                    system_instruction = f"""
                    너는 글로벌 게임사의 10년차 시니어 커뮤니티 매니저(CM)야. 
                    유저들이 신뢰를 느낄 수 있도록 전문적이면서도 친근한 공지사항을 {target_lang}로 작성해줘.
                    
                    [작성 지침]
                    1. 톤앤매너: {lang_guidelines.get(target_lang, "")}
                    2. 가독성: 마크다운(Markdown) 형식을 사용하여 제목, 리스트, 강조(볼드)를 적절히 섞을 것.
                    3. 내용 구성: [인사말] - [내용 요약] - [상세 정보] - [주의사항/보상] - [맺음말] 순서로 구성할 것.
                    4. 특수 상황: 만약 '기타(운영 정책)' 카테고리라면, 불건전 행위에 대해 단호한 운영 의지를 밝히고 클린한 게임 환경을 강조할 것.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": f"카테고리: {category}\n제목: {title}\n일정: {schedule}\n상세내용: {details}\n보상: {reward}\n\n위 데이터를 기반으로 {target_lang} 버전의 공지 전문을 작성해줘."}
                        ],
                        temperature=0.7
                    )
                    
                    final_notice = response.choices[0].message.content
                    
                    # 결과 표시
                    st.success(f"[{target_lang}] 공지 생성이 성공적으로 완료되었습니다!")
                    st.divider()
                    st.markdown(final_notice)
                    st.divider()
                    
                    # 저장 버튼
                    st.download_button(
                        label=f"💾 {target_lang} 공지 파일로 저장",
                        data=final_notice,
                        file_name=f"GameNotice_{target_lang}.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"공지 생성 중 오류가 발생했습니다: {e}")
    else:
        # 초기 화면 가이드
        st.info("왼쪽 양식을 작성한 뒤 '공지 생성 시작' 버튼을 눌러주세요.")
        st.markdown("""
        **💡 활용 팁:**
        * **불건전 행위 대응:** 상세 내용에 '정지 계정 수'와 '위반 항목'을 적어보세요.
        * **글로벌 배포:** 동일한 내용을 입력하고 '언어'만 바꿔서 여러 번 생성할 수 있습니다.
        * **가독성:** AI가 표(Table) 형식을 사용해 가동 시간을 정리해줍니다.
        """)

# 사이드바 하단 정보
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Game Notice Studio Pro")
