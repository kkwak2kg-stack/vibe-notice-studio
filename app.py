import streamlit as st
from openai import OpenAI
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

# CSS: 프리뷰 박스를 하나로 합치고 마침표 기준 줄바꿈을 위한 스타일 설정
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-container {
        background-color: #1e2129;
        padding: 40px;
        border-radius: 12px;
        color: #e0e0e0;
        font-size: 16px;
        line-height: 2.0; /* 기본 줄간격 */
        border: 1px solid #333;
        white-space: pre-wrap; /* 줄바꿈 유지 */
    }
    .highlight-gold { color: #ffd700; font-weight: bold; }
    .highlight-red { color: #ff4b4b; font-weight: bold; }
    
    /* 표 스타일 */
    .stMarkdown table { width: 100% !important; border-collapse: collapse; margin: 20px 0; }
    .stMarkdown th { background-color: #333 !important; color: #ffd700 !important; text-align: center !important; }
    .stMarkdown td { text-align: center !important; border: 1px solid #444; }
    
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
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("📋 공지 상세 설정")
    with st.form("notice_form"):
        category = st.selectbox("공지 카테고리", ["기타(운영 정책/일반 공지)", "정기 점검 안내", "업데이트 패치노트", "이벤트 안내", "긴급 장애 사과문"])
        
        c1, c2 = st.columns(2)
        with c1:
            game_name = st.text_input("게임 명칭", value="바이브")
        with c2:
            user_call = st.text_input("유저 호칭", value="모험가님")
            
        title = st.text_input("공지 제목", value="불건전 행위 유저 대응 결과 안내")
        
        c3, c4 = st.columns(2)
        with c3:
            target_date = st.date_input("공지/조치 일자", value=datetime.now())
        with c4:
            reward = st.text_input("지급 보상", placeholder="예: 루비 500개 (없으면 비워둠)")
            
        details = st.text_area("상세 내용", height=150, placeholder="예: 10개 계정 영구 정지, 전수 조사 완료")
        
        submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

with col2:
    st.subheader("📝 최종 결과 프리뷰")
    if submitted:
        with st.spinner('전문 CM의 톤으로 내용을 구성 중입니다...'):
            try:
                formatted_date = target_date.strftime("%Y년 %m월 %d일")
                
                system_instruction = f"""
                너는 국내 대형 게임사 시니어 CM이야. 
                유저들에게 신뢰감을 주는 공식 공지사항을 작성해줘.

                [핵심 수칙]
                1. 인사말: "안녕하세요 {user_call}, {game_name} 운영팀입니다."로 시작할 것.
                2. 호칭: '{user_call}' 사용. (강조를 위해 [G]{user_call}[G] 태그 사용)
                3. 마침표 줄바꿈: 문장의 마침표(.)가 끝날 때마다 줄바꿈을 수행해라. 
                4. 단락 구분: 큰 주제가 바뀔 때는 빈 줄(Double Newline)을 넣어라.
                5. 조치 내역: 10개 계정 리스트나 조치 내역은 반드시 마크다운 표(Table) 형식을 사용할 것.
                6. 강조: '영구 정지' 등 경고 문구는 [R]영구 정지[R] 태그 사용.
                7. 날짜 및 보상: '{formatted_date}'와 '{reward}' 정보를 자연스럽게 문맥에 녹여라.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"카테고리: {category}\n제목: {title}\n내용: {details}"}
                    ],
                    temperature=0.3
                )
                
                res_text = response.choices[0].message.content
                
                # 💡 가독성 처리 로직
                # 1. 마침표 뒤에 줄바꿈 추가 (AI가 놓친 부분 보정)
                res_text = res_text.replace(". ", ".\n")
                # 2. 강조 태그 HTML 변환
                res_text = res_text.replace("[G]", '<span class="highlight-gold">').replace("[G]", "</span>")
                res_text = res_text.replace("[R]", '<span class="highlight-red">').replace("[R]", "</span>")
                
                # 💡 결과 출력 (하나의 통합 박스로 렌더링)
                st.markdown(f'<div class="notice-container">{res_text}</div>', unsafe_allow_html=True)
                
                # 저장용 텍스트 (태그 제거)
                save_text = res_text.replace('<span class="highlight-gold">', "").replace('<span class="highlight-red">', "").replace("</span>", "")
                st.download_button("💾 공지 텍스트 저장", save_text, file_name=f"Notice_{formatted_date}.txt")
                
            except Exception as e:
                st.error(f"오류 발생: {e}")
