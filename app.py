import streamlit as st
from openai import OpenAI

# 1. 페이지 설정 및 디자인
st.set_page_config(
    page_title="Global Game Notice Studio Pro", 
    page_icon="🌐", 
    layout="wide"
)

# 다크 모드 기반의 깔끔한 UI 설정
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
        border: none;
    }
    .stTextArea textarea { font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 글로벌 게임 공지사항 생성기")
st.caption("전문 CM의 격식 있는 문체와 글로벌 로컬라이징을 지원합니다.")

# 2. 보안 설정: Secrets에서만 키를 가져오며 입력창은 제거됨
try:
    # Streamlit Cloud Settings > Secrets에 OPENAI_API_KEY가 저장되어 있어야 합니다.
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except KeyError:
    st.error("⚠️ Streamlit Secrets에 'OPENAI_API_KEY'가 설정되지 않았습니다.")
    st.stop()
except Exception as e:
    st.error(f"❌ 오류 발생: {e}")
    st.stop()

# 3. UI 레이아웃
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📋 공지 데이터 입력")
    with st.form("notice_form"):
        # 카테고리 구성
        category = st.selectbox("공지 카테고리", 
                            ["정기 점검 안내", "업데이트 패치노트", "이벤트 안내", 
                             "긴급 장애 사과문", "당첨자 발표", "기타(운영 정책/일반 공지)"])
        
        # 다국어 선택
        target_lang = st.selectbox("출력 언어 선택", 
                            ["한국어", "영어(English)", "일본어(日本語)", 
                             "중국어 간체(简体中文)", "중국어 번체(繁體中文)"])
        
        title = st.text_input("핵심 제목", placeholder="예: 비인가 프로그램 대응 및 운영 정책 안내")
        
        schedule = st.text_input("일정/시간", placeholder="예: 2026.03.12 10:00 ~ 14:00 (KST)")
        
        details = st.text_area("상세 내용", 
                            placeholder="공지할 핵심 데이터를 적어주세요. (예: 10개 계정 영구 제재, 모니터링 강화 등)", 
                            height=200)
        
        reward = st.text_input("보상 아이템", placeholder="예: 루비 500개 (없을 경우 비워둠)")
        
        submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

with col2:
    st.subheader("📝 생성 결과 미리보기")
    
    if submitted:
        if not title or not details:
            st.warning("제목과 상세 내용을 입력해야 공지를 생성할 수 있습니다.")
        else:
            with st.spinner(f'{target_lang} 버전 공지를 작성 중입니다...'):
                try:
                    # 언어별 격식 있는 말투 지침
                    lang_guidelines = {
                        "한국어": "무조건 격식 있는 '하십시오체(~합니다, ~드립니다)'만 사용하세요. '~해요', '~요'는 절대 금지입니다.",
                        "영어(English)": "Maintain a formal and authoritative tone. Use passive voice where appropriate for professionalism. Address as 'Adventurers'.",
                        "일본어(日本語)": "Use 'Desu/Masu' style with high-level Keigo (honorifics). Address as '冒険者の皆様'. Avoid casual expressions.",
                        "중국어 간체(简体中文)": "Formal corporate tone. Use '尊敬的玩家' or '各位勇士'. Use Simplified Chinese.",
                        "중국어 번체(繁體中文)": "Formal corporate tone. Use Traditional Chinese characters."
                    }

                    # AI 페르소나 및 작성 지침 (피드백 반영)
                    system_instruction = f"""
                    너는 국내 대형 게임사의 시니어 파트장급 커뮤니티 매니저(CM)야. 
                    유저들에게 공식적인 신뢰감과 무게감을 전달할 수 있는 공지사항을 {target_lang}로 작성해줘.
                    
                    [핵심 준수 사항]
                    1. 문체: {lang_guidelines.get(target_lang, "")}
                    2. 레이블 제거: '내용 요약', '상세 정보', '맺음말'과 같은 구분용 소제목 레이블을 텍스트로 직접 노출하지 마라. 자연스러운 문단 구분으로 대체하라.
                    3. 가독성: 마크다운(Markdown)을 활용하되, 본문은 서술형으로, 시간/명단/아이템 등은 불렛포인트나 표를 활용해라.
                    4. 운영 정책 공지: 비인가 프로그램이나 불건전 행위 대응 시에는 감정을 배제하고 단호하며 법적인 엄중함이 느껴지도록 작성해라.
                    5. 구성: [인사말] - [상세 안내 본문] - [주의사항 및 보상] - [마무리 인사] 순서로 작성하되, 각 섹션의 이름을 적지 말고 내용만 출력하라.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": f"카테고리: {category}\n제목: {title}\n일정: {schedule}\n상세내용: {details}\n보상: {reward}\n\n위 데이터를 기반으로 {target_lang} 공식 공지문을 작성해줘."}
                        ],
                        temperature=0.4  # 일관성을 위해 낮춤
                    )
                    
                    final_notice = response.choices[0].message.content
                    
                    st.success(f"[{target_lang}] 공지 생성이 완료되었습니다!")
                    st.divider()
                    st.markdown(final_notice)
                    st.divider()
                    
                    st.download_button(
                        label=f"💾 {target_lang} 공지 파일 저장",
                        data=final_notice,
                        file_name=f"Official_Notice_{target_lang}.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"공지 생성 중 오류 발생: {e}")
    else:
        st.info("데이터를 입력한 뒤 '공지 생성 시작' 버튼을 눌러주세요.")

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Game Notice Studio Pro")
