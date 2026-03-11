import streamlit as st
from openai import OpenAI
import json

# 1. 페이지 설정 (기존 툴과 통일감 유지)
st.set_page_config(page_title="Game Notice Studio Pro", page_icon="📢", layout="wide")
st.title("📢 전문 게임 공지사항 생성기")

# 2. API 키 설정 (기존 방식과 동일하게 유지)
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    # [공지 생성 전용] 시스템 프롬프트 설정
    SYSTEM_PROMPT = (
        "너는 10년 차 베테랑 게임 커뮤니티 매니저(CM)이자 운영팀장이야.\n\n"
        "### [작성 원칙]\n"
        "1. 말투: 항상 정중하고 따뜻한 '해요체'를 사용하며, 유저를 '모험가님' 또는 '계승자님'으로 지칭해라.\n"
        "2. 가독성: 마크다운(Markdown) 형식을 적극 활용하여 중요 정보를 표(Table)나 불렛포인트로 정리해라.\n"
        "3. 감성적 접근: 단순 정보 전달을 넘어 유저의 기대감을 높이거나(업데이트), 진심으로 미안함을 전달(사과문)해라.\n"
        "4. 전문성: 실제 대형 게임사(넥슨, 엔씨, 넷마블 등)의 공지 양식을 참고하여 격식을 갖춰라."
    )

    # UI 레이아웃 구성
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("📋 공지 데이터 입력")
        with st.form("notice_form"):
            category = st.selectbox("공지 카테고리", 
                                ["정기 점검 안내", "업데이트 패치노트", "이벤트 안내", "긴급 장애 사과문", "당첨자 발표"])
            
            title = st.text_input("핵심 제목", placeholder="예: 신규 영웅 '아이린' 등장 및 밸런스 조정")
            
            schedule = st.text_input("점검/이벤트 일정", placeholder="예: 2026.03.12 10:00 ~ 14:00 (4시간)")
            
            details = st.text_area("주요 상세 내용", placeholder="패치 내역, 버그 수정 리스트, 이벤트 참여 방법 등을 적어주세요.", height=200)
            
            reward = st.text_input("지급 보상", placeholder="예: 다이아 500개, 골드 100만")
            
            submitted = st.form_submit_button("✨ 전문 공지 생성 시작")

    with col2:
        st.subheader("📝 생성된 공지 미리보기")
        if submitted:
            if not title or not details:
                st.warning("제목과 상세 내용을 입력해주세요.")
            else:
                with st.spinner('베테랑 CM이 공지문을 작성 중입니다...'):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": f"분류: {category}\n제목: {title}\n일정: {schedule}\n내용: {details}\n보상: {reward}\n\n위 데이터를 기반으로 공식 커뮤니티에 올릴 완성된 공지문을 작성해줘."}
                            ],
                            temperature=0.7
                        )
                        
                        generated_text = response.choices[0].message.content
                        
                        # 결과 출력 카드 UI 스타일
                        st.success("공지문 생성이 완료되었습니다!")
                        st.divider()
                        st.markdown(generated_text)
                        
                        st.divider()
                        st.download_button("텍스트 파일로 저장", generated_text, file_name=f"notice_{category}.txt")
                        
                    except Exception as e:
                        st.error(f"분석 중 오류 발생: {e}")
        else:
            st.info("왼쪽 폼에 데이터를 입력하고 생성 버튼을 눌러주세요.")

else:

    st.info("사이드바에서 OpenAI API 키를 설정해주세요.")
