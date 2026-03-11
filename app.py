import streamlit as st
from openai import OpenAI
from datetime import datetime

st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-container {
        background-color: #1e2129;
        padding: 40px;
        border-radius: 12px;
        color: #e0e0e0;
        font-size: 16px;
        line-height: 2.0;
        border: 1px solid #333;
    }
    .notice-paragraph { margin-bottom: 25px; display: block; }
    .highlight-gold { color: #ffd700; font-weight: bold; }
    .highlight-red { color: #ff4b4b; font-weight: bold; }
    
    /* 표(Table) 가독성 극대화 */
    .stMarkdown table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    .stMarkdown th { background-color: #333 !important; color: #ffd700 !important; text-align: center !important; }
    .stMarkdown td { text-align: center !important; border: 1px solid #444; }
    
    stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #FF4B4B; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 글로벌 게임 공지사항 생성기")

try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except Exception:
    st.error("⚠️ Streamlit Secrets 설정을 확인해주세요.")
    st.stop()

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📋 공지 디테일 설정")
    with st.form("notice_form"):
        category = st.selectbox("공지 카테고리", ["기타(운영 정책/일반 공지)", "정기 점검 안내", "업데이트 패치노트", "이벤트 안내", "긴급 장애 사과문"])
        user_call = st.text_input("유저 호칭", value="모험가님")
        title = st.text_input("핵심 제목", value="불건전 행위 유저 대응 결과 안내")
        today_date = datetime.now().strftime("%Y년 %m월 %d일")
        details = st.text_area("상세 내용", height=150, placeholder="예: 10개 계정 영구 정지, 전수 조사 완료")
        submitted = st.form_submit_button("🔥 업계 표준 최종본 생성")

with col2:
    st.subheader("📝 최종 결과 프리뷰")
    if submitted:
        with st.spinner('베테랑 CM이 최종 검수 중...'):
            try:
                system_instruction = f"""
                너는 국내 대형 게임사 시니어 CM이야. 
                격식 있고 신뢰감 있는 공식 공지사항을 작성해줘.

                [핵심 수칙]
                1. 인사말: "안녕하세요. 운영팀입니다." 고정.
                2. 호칭: '{user_call}' 사용. (황금색 강조를 위해 문구 앞뒤에 [G]태그를 붙여라. 예: [G]{user_call}[G])
                3. 표 사용: 조치 내역은 반드시 마크다운 표 형식을 사용하여 작성해라. (표 내부에는 HTML 태그를 넣지 마라)
                4. 강조: 문장 내 '영구 정지' 같은 핵심 키워드 앞뒤에는 [R]태그를 붙여라. (예: [R]영구 정지[R])
                5. 문단: 각 섹션 사이에 [P] 기호를 넣어라.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"제목: {title}\n내용: {details}\n날짜: {today_date}"}
                    ],
                    temperature=0.3
                )
                
                res_text = response.choices[0].message.content
                
                # 가독성을 위한 태그 변환 로직
                res_text = res_text.replace("[G]", f'<span class="highlight-gold">').replace("[G]", "</span>") # 호칭 강조
                res_text = res_text.replace("[R]", f'<span class="highlight-red">').replace("[R]", "</span>") # 경고 강조
                
                sections = res_text.split("[P]")
                
                for section in sections:
                    if "|" in section: # 표 형식인 경우
                        st.markdown(section, unsafe_allow_html=True)
                    elif section.strip():
                        st.markdown(f'<div class="notice-container" style="margin-bottom:20px;">{section.strip()}</div>', unsafe_allow_html=True)
                
                st.download_button("💾 공지 텍스트 저장", res_text.replace("[P]", "\n\n").replace('<span class="highlight-gold">', "").replace('<span class="highlight-red">', "").replace("</span>", ""), file_name="Notice.txt")
                
            except Exception as e:
                st.error(f"오류 발생: {e}")
