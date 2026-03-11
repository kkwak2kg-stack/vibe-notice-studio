import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-container {
        background-color: #1e2129;
        padding: 45px;
        border-radius: 12px;
        color: #ffffff;
        font-size: 15.5px;
        line-height: 1.9;
    }
    .notice-paragraph {
        margin-bottom: 28px;
        display: block;
    }
    .highlight {
        color: #FF4B4B;
        font-weight: bold;
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
        category = st.selectbox("공지 카테고리", ["기타(운영 정책/일반 공지)", "정기 점검 안내", "업데이트 패치노트", "이벤트 안내", "긴급 장애 사과문"])
        title = st.text_input("핵심 제목", placeholder="예: 불건전 행위 유저 대응 결과 안내")
        details = st.text_area("상세 내용", height=150, placeholder="예: 제보 접수 후 전수 조사, 10개 계정 영구 정지, 강력 대응 의지")
        submitted = st.form_submit_button("✨ 업계 표준 공지 생성")

with col2:
    st.subheader("📝 생성 결과 미리보기")
    
    if submitted:
        with st.spinner('베테랑 CM의 톤으로 다듬는 중...'):
            try:
                # [업계 표준 톤앤매너 지침]
                system_instruction = """
                너는 국내 1티어 게임사의 시니어 CM 파트장이야. 
                격식 있고 신뢰감 있는 공식 공지사항을 작성해줘.

                [작성 가이드라인]
                1. 인사말: "안녕하세요. 운영팀입니다."로 시작할 것.
                2. 문체: 하십시오체(~합니다, ~드립니다)를 사용하며, 문장 간의 연결이 매끄러워야 함.
                3. 핵심 강조: 적발 건수나 중요한 조치 사항은 텍스트 내에서 강조될 수 있도록 구성할 것.
                4. 문맥 흐름: 상황의 엄중함 인식 -> 조사 결과 및 조치 사항 -> 향후 운영 방침 -> 유저 당부 및 감사 순서.
                5. 문단 구분: 각 문단 끝에 [P] 기호를 넣어 명확히 구분할 것.
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
                paragraphs = res_text.split("[P]")
                
                html_content = '<div class="notice-container">'
                for p in paragraphs:
                    if p.strip():
                        # 특정 키워드(숫자, 영구 정지 등)를 자동으로 강조하는 로직 살짝 가미
                        text = p.strip().replace("10개", '<span class="highlight">10개</span>').replace("영구 정지", '<span class="highlight">영구 정지</span>')
                        html_content += f'<span class="notice-paragraph">{text}</span>'
                html_content += '</div>'
                
                st.markdown(html_content, unsafe_allow_html=True)
                st.download_button(label="💾 공지 텍스트 저장", data=res_text.replace("[P]", "\n\n"), file_name="Official_Notice.txt")
                
            except Exception as e:
                st.error(f"오류 발생: {e}")
