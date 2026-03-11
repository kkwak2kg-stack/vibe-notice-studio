import streamlit as st
from openai import OpenAI
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

# CSS: 실제 게임사 공홈(Official Site)의 공지 게시판 느낌을 재현
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-container {
        background-color: #1e2129;
        padding: 50px;
        border-radius: 15px;
        color: #e0e0e0;
        font-size: 16px;
        line-height: 2.0;
        border: 1px solid #333;
    }
    .notice-paragraph {
        margin-bottom: 30px;
        display: block;
    }
    .highlight-red { color: #ff4b4b; font-weight: bold; }
    .highlight-gold { color: #ffd700; font-weight: bold; }
    
    /* 표(Table) 스타일링 */
    table { width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #262a33; }
    th, td { border: 1px solid #444; padding: 12px; text-align: left; }
    th { background-color: #333; color: #ffd700; }
    
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
    st.subheader("📋 공지 디테일 설정")
    with st.form("notice_form"):
        category = st.selectbox("공지 카테고리", ["기타(운영 정책/일반 공지)", "정기 점검 안내", "업데이트 패치노트", "이벤트 안내", "긴급 장애 사과문"])
        
        # [추가] 게임별 호칭 설정
        user_call = st.text_input("유저 호칭 (예: 모험가님, 기사님, 계승자님)", value="모험가님")
        
        title = st.text_input("핵심 제목", placeholder="예: 불건전 행위 유저 대응 결과 안내")
        
        # [추가] 오늘 날짜 자동 반영용
        today_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        details = st.text_area("상세 내용", height=150, placeholder="예: 10개 계정 영구 정지, 전수 조사 완료, 강력 대응")
        
        submitted = st.form_submit_button("🔥 업계 표준 최종본 생성")

with col2:
    st.subheader("📝 최종 결과 프리뷰")
    
    if submitted:
        with st.spinner('최정상급 CM의 문체로 튜닝 중입니다...'):
            try:
                # [Ultimate 프롬프트 지침]
                system_instruction = f"""
                너는 국내 1티어 게임사(넥슨, NC 등)의 시니어 운영 파트장이야. 
                유저들에게 신뢰감과 무게감을 동시에 주는 공식 공지사항을 작성해줘.

                [핵심 가이드라인]
                1. 인사말: "안녕하세요. 운영팀입니다."로 시작.
                2. 호칭: 유저를 무조건 '{user_call}'으로 불러라.
                3. 날짜: 오늘 날짜인 '{today_date}'를 문맥에 맞게 활용해라.
                4. 표(Table) 활용: 조치 내역(일시, 대상, 조치 내용 등)은 반드시 마크다운 표 형식을 사용하여 정리해라.
                5. 문체: 하십시오체(~합니다, ~드립니다) 고정. 문장 간의 유기적 연결을 강화할 것.
                6. 구분자: 각 문단 사이에는 [P] 기호를 넣어라.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"제목: {title}\n내용: {details}"}
                    ],
                    temperature=0.4
                )
                
                res_text = response.choices[0].message.content
                
                # HTML 렌더링 로직 (표와 강조색 반영)
                paragraphs = res_text.split("[P]")
                html_content = '<div class="notice-container">'
                
                for p in paragraphs:
                    if p.strip():
                        text = p.strip()
                        # 핵심 키워드 강조색 부여
                        text = text.replace("영구 정지", '<span class="highlight-red">영구 정지</span>')
                        text = text.replace(user_call, f'<span class="highlight-gold">{user_call}</span>')
                        
                        # 표(Markdown Table) 인식 및 변환
                        if "|" in text:
                            # 텍스트 내 마크다운 표를 HTML 표로 변환하는 간단한 처리 (Streamlit 기본 markdown 기능 활용 가능)
                            st.markdown(html_content + '</div>', unsafe_allow_html=True)
                            st.markdown(text)
                            html_content = '<div class="notice-container" style="margin-top:-20px; border-top:none; border-radius:0 0 15px 15px;">'
                        else:
                            html_content += f'<span class="notice-paragraph">{text}</span>'
                
                html_content += '</div>'
                st.markdown(html_content, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"오류 발생: {e}")

st.sidebar.markdown("---")
st.sidebar.info(f"📅 생성일: {today_date}")
