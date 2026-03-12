import streamlit as st
from openai import OpenAI
from datetime import datetime
import re

st.set_page_config(page_title="Global Game Notice Studio Pro", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .notice-container {
        background-color: #1e2129;
        padding: 40px;
        border-radius: 12px;
        color: #e0e0e0;
        font-size: 16.5px;
        line-height: 1.9;
        border: 1px solid #333;
    }
    .highlight-gold { color: #ffd700; font-weight: bold; }
    .highlight-red { color: #ff4b4b; font-weight: bold; }
    .notice-line { margin-bottom: 12px; display: block; }
    
    /* ARC 스타일 전용 주석 스타일 */
    .note { color: #aaaaaa; font-size: 14.5px; padding-left: 20px; display: block; margin-bottom: 5px; }

    .stMarkdown table { width: 100% !important; margin: 20px 0; }
    .stMarkdown th { background-color: #333 !important; color: #ffd700 !important; text-align: center !important; }
    .stMarkdown td { text-align: center !important; border: 1px solid #444; padding: 10px; }
    
    stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #FF4B4B; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 글로벌 게임 공지사항 생성기 (ARC Edition)")

try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except Exception:
    st.error("⚠️ Streamlit Secrets 설정을 확인해주세요.")
    st.stop()

col1, col2 = st.columns([1, 1.3], gap="large")

with col1:
    st.subheader("📋 공지 상세 설정")
    with st.form("notice_form"):
        game_name = st.text_input("게임 명칭", value="ARC")
        user_call = st.text_input("유저 호칭", value="플레이어")
        title = st.text_input("공지 제목", value="비정상 플레이 행위 대응 결과 안내")
        reward = st.text_input("지급 보상 (없으면 비워둠)")
        details = st.text_area("상세 내용 (팩트만 입력하세요)", height=200, 
                             placeholder="예: 치트 133명 영구정지 및 랭크보상 제외, 탈주 17명 이용정지, 시스템 강화 중")
        submitted = st.form_submit_button("🔥 ARC 팀 수준 고퀄리티 생성")

with col2:
    st.subheader("📝 최종 결과 프리뷰")
    if submitted:
        with st.spinner('ARC 팀의 논리와 서사를 입히는 중...'):
            try:
                # ARC 팀 공지의 '논리적 구조'를 프롬프트에 이식
                system_instruction = f"""
                너는 'ARC'라는 글로벌 대형 게임사의 시니어 운영 파트장이야. 
                단순한 정보 나열이 아닌, 유저들에게 감동과 신뢰를 주는 'ARC 팀 스타일'의 공지를 작성해라.

                [ARC 팀 공지의 핵심 구조]
                1. 도입: 공정한 경쟁 환경 유지에 대한 팀의 의지 표명.
                2. 본문: 조치 대상(치트, 탈주 등)별로 섹션을 나누고, 왜 이 행위가 해로운지 설명할 것.
                3. 디테일: 각 조치 사항 아래에는 '※' 기호를 사용한 주석을 달아 세부 규칙(예외 없는 제재, 데이터 검증 등)을 설명할 것.
                4. 향후 계획: 시스템 강화 및 데이터 분석 체계 고도화 등 '미래의 의지'를 반드시 포함할 것.
                5. 마무리: "깨끗한 게임 환경은 플레이어 여러분과 {game_name} 팀이 함께 만들어가는 약속입니다." 라는 문구를 사용할 것.

                [기술 수칙]
                - 인사말: "안녕하세요 {user_call} 여러분, {game_name} 운영팀입니다."
                - 마침표마다 줄바꿈.
                - 강조: [R]핵심조치[R], [G]{user_call}[G].
                - 톤앤매너: 매우 진중하고, 논리적이며, 유저를 존중하는 태도.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": f"제목: {title}\n팩트 데이터: {details}\n보상: {reward}"}
                    ],
                    temperature=0.5 # 자연스러운 서사를 위해 약간 높임
                )
                
                res_text = response.choices[0].message.content
                
                # HTML 태그 변환 및 주석 스타일링
                res_text = res_text.replace("[G]", '<span class="highlight-gold">').replace("[G]", "</span>")
                res_text = res_text.replace("[R]", '<span class="highlight-red">').replace("[R]", "</span>")
                res_text = re.sub(r'※ (.*)', r'<span class="note">※ \1</span>', res_text)

                st.markdown('<div class="notice-container">', unsafe_allow_html=True)
                lines = res_text.split('\n')
                for line in lines:
                    if '|' in line:
                        st.markdown(line, unsafe_allow_html=True)
                    elif '※' in line:
                        st.markdown(line, unsafe_allow_html=True)
                    elif line.strip():
                        sentences = line.split('. ')
                        for s in sentences:
                            if s.strip():
                                clean_s = s.strip() + ('.' if not s.endswith('.') else '')
                                st.markdown(f'<span class="notice-line">{clean_s}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"오류 발생: {e}")
