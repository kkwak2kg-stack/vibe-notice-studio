import streamlit as st
from openai import OpenAI
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

# CSS: 공백 버그 해결 및 가독성 극대화
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-container {
        background-color: #1e2129;
        padding: 40px;
        border-radius: 12px;
        color: #e0e0e0;
        font-size: 16px;
        line-height: 1.8;
        border: 1px solid #333;
    }
    /* 문장/문단 단위 스타일 - 여기서 간격을 조절합니다 */
    .notice-line {
        margin-bottom: 15px; 
        display: block;
    }
    .highlight-gold { color: #ffd700; font-weight: bold; }
    .highlight-red { color: #ff4b4b; font-weight: bold; }
    
    /* 표 스타일 최적화 */
    .stMarkdown table { width: 100% !important; border-collapse: collapse; margin: 20px 0; background-color: #262a33; }
    .stMarkdown th { background-color: #333 !important; color: #ffd700 !important; text-align: center !important; }
    .stMarkdown td { text-align: center !important; border: 1px solid #444; padding: 10px; }
    
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
col1, col2 = st.columns([1, 1.3], gap="large")

with col1:
    st.subheader("📋 공지 상세 설정")
    with st.form("notice_form"):
        category = st.selectbox("공지 카테고리", ["기타(운영 정책/일반 공지)", "정기 점검 안내", "업데이트 패치노트", "이벤트 안내", "긴급 장애 사과문"])
        c1, c2 = st.columns(2)
        with c1: game_name = st.text_input("게임 명칭", value="바이브")
        with c2: user_call = st.text_input("유저 호칭", value="모험가님")
        title = st.text_input("공지 제목", value="불건전 행위 유저 대응 결과 안내")
        c3, c4 = st.columns(2)
        with c3: target_date = st.date_input("공지 일자", value=datetime.now())
        with c4: reward = st.text_input("지급 보상", placeholder="예: 루비 500개")
        details = st.text_area("상세 내용", height=150, placeholder="예: 10개 계정 영구 정지, 전수 조사 완료")
        submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

with col2:
    st.subheader("📝 최종 결과 프리뷰")
    if submitted:
        with st.spinner('문장을 정렬 중입니다...'):
            try:
                formatted_date = target_date.strftime("%Y년 %m월 %d일")
                system_instruction = f"""
                너는 국내 대형 게임사 시니어 CM이야. 격식 있는 공지사항을 작성해줘.
                [필수 수칙]
                1. 인사말: "안녕하세요 {user_call}, {game_name} 운영팀입니다."
                2. 호칭: [G]{user_call}[G] 태그 사용.
                3. 마침표마다 문장을 끊어서 작성해라.
                4. 강조: [R]영구 정지[R] 태그 사용.
                5. 표: 조치 리스트는 마크다운 표 형식을 사용할 것.
                """
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"제목: {title}\n내용: {details}\n일자: {formatted_date}\n보상: {reward}"}
                    ],
                    temperature=0.3
                )
                raw_res = response.choices[0].message.content
                
                # 💡 [핵심 해결 로직]
                # 1. 강조 태그 변환
                raw_res = raw_res.replace("[G]", '<span class="highlight-gold">').replace("[G]", "</span>")
                raw_res = raw_res.replace("[R]", '<span class="highlight-red">').replace("[R]", "</span>")
                
                # 2. 결과 출력 (표와 일반 문장 분리 처리)
                st.markdown('<div class="notice-container">', unsafe_allow_html=True)
                
                # 문장별로 쪼개기 (마침표 기준)
                lines = raw_res.split('\n')
                for line in lines:
                    if '|' in line: # 표(Table) 부분은 그대로 출력
                        st.markdown(line, unsafe_allow_html=True)
                    elif line.strip():
                        # 마침표 기준으로 한 번 더 쪼개서 줄바꿈 적용
                        sentences = line.split('. ')
                        for s in sentences:
                            if s.strip():
                                clean_s = s.strip() + ('.' if not s.endswith('.') else '')
                                st.markdown(f'<span class="notice-line">{clean_s}</span>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 저장용 텍스트
                save_text = raw_res.replace('<span class="highlight-gold">', "").replace('<span class="highlight-red">', "").replace("</span>", "")
                st.download_button("💾 공지 텍스트 저장", save_text, file_name=f"Notice.txt")
                
            except Exception as e:
                st.error(f"오류 발생: {e}")
