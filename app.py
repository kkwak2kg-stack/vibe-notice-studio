import streamlit as st
from openai import OpenAI
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

# CSS: 가독성 및 강조 색상 최적화
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
    .notice-line {
        margin-bottom: 15px; 
        display: block;
    }
    .highlight-gold { color: #ffd700; font-weight: bold; }
    .highlight-red { color: #ff4b4b; font-weight: bold; }
    
    /* 표 스타일 */
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
        with c4: reward = st.text_input("지급 보상", placeholder="내용이 없으면 비워두세요")
        details = st.text_area("상세 내용", height=150, placeholder="예: 10개 계정 영구 정지, 전수 조사 완료")
        submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

with col2:
    st.subheader("📝 최종 결과 프리뷰")
    if submitted:
        with st.spinner('최종 검수 중...'):
            try:
                formatted_date = target_date.strftime("%Y년 %m월 %d일")
                
                # 보상 관련 지침 동적 생성
                reward_instruction = f"지급 보상 정보('{reward}')가 비어있다면 관련 문구를 아예 포함하지 마라." if not reward else f"보상 내용인 '{reward}'을 자연스럽게 언급해라."

                system_instruction = f"""
                너는 국내 대형 게임사 시니어 CM이야. 
                [필수 수칙]
                1. 인사말: "안녕하세요 {user_call}, {game_name} 운영팀입니다."
                2. 호칭: 유저 호칭({user_call})은 일반 텍스트로 작성하되, 강조가 꼭 필요한 문맥에서만 한정적으로 사용해라.
                3. 문장 부호: ":." 와 같이 기호가 중복되지 않도록 주의해라.
                4. 중복 제거: '감사합니다'는 마지막에 딱 한 번만 사용해라.
                5. 맺음말: "더욱 즐거운 게임 환경을 제공하기 위해 최선으 다하겠습니다."는 일반 텍스트로 작성해라(색상 금지).
                6. 보상: {reward_instruction}
                7. 가독성: 마침표마다 문장을 끊어서 작성하고, 조치 리스트는 표 형식을 사용해라.
                8. 강조: [R]영구 정지[R] 태그만 사용해라.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"제목: {title}\n내용: {details}\n일자: {formatted_date}"}
                    ],
                    temperature=0.3
                )
                raw_res = response.choices[0].message.content
                
                # 태그 변환
                res_text = raw_res.replace("[R]", '<span class="highlight-red">').replace("[R]", "</span>")
                
                st.markdown('<div class="notice-container">', unsafe_allow_html=True)
                lines = res_text.split('\n')
                for line in lines:
                    if '|' in line:
                        st.markdown(line, unsafe_allow_html=True)
                    elif line.strip():
                        sentences = line.split('. ')
                        for s in sentences:
                            if s.strip():
                                clean_s = s.strip() + ('.' if not s.endswith('.') else '')
                                st.markdown(f'<span class="notice-line">{clean_s}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                save_text = res_text.replace('<span class="highlight-red">', "").replace("</span>", "")
                st.download_button("💾 공지 텍스트 저장", save_text, file_name=f"Notice.txt")
                
            except Exception as e:
                st.error(f"오류 발생: {e}")
