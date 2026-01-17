import streamlit as st
import arxiv
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import time
import re
from database import init_db, get_session, Schedule, EmailHistory
from scheduler import get_scheduler

# 환경 변수 로드
load_dotenv()

# Gemini API 설정 (Lite 모델로 변경)
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# 데이터베이스 초기화
engine = init_db()

# 스케줄러 초기화
scheduler = get_scheduler()

# 페이지 설정
st.set_page_config(
    page_title="스터디레터 - 논문 요약 서비스",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
    <style>
    /* 전체 배경 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 메인 컨테이너 */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin: 1rem auto;
    }
    
    /* 헤더 스타일 */
    .header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .header p {
        color: #666;
        font-size: 1rem;
        margin-top: 0;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 0.8rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
    }
    
    /* 테이블 스타일 */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* 메트릭 카드 */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


def validate_email(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def search_arxiv(keyword, max_results=10):
    """arXiv에서 최근 7일 이내 논문 검색"""
    try:
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        client = arxiv.Client()
        search = arxiv.Search(
            query=f"all:{keyword}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = []
        for result in client.results(search):
            if result.published.replace(tzinfo=None) >= seven_days_ago:
                papers.append({
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'abstract': result.summary,
                    'pdf_url': result.pdf_url,
                    'published': result.published
                })
                
                if len(papers) >= 5:
                    break
        
        return papers
    except Exception as e:
        st.error(f"논문 검색 중 오류가 발생했습니다: {str(e)}")
        return []


def summarize_with_gemini(abstract):
    """Gemini Lite 모델을 사용하여 초록을 한국어로 요약"""
    try:
        # gemini-1.5-flash-8b (Lite 모델)로 변경
        model = genai.GenerativeModel('gemini-1.5-flash-8b')
        
        prompt = f"""You are a helpful research assistant.
Summarize the given academic paper abstract into Korean.

Requirements:
- Summarize in exactly 3 bullet points
- Maintain technical terms in English if the Korean translation is awkward
- Use professional yet easy-to-read tone (해요체)
- Each bullet point should be concise but informative

Abstract:
{abstract}

Provide only the 3 bullet points in Korean, starting each with "• ":
"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"• 요약 생성 중 오류가 발생했습니다: {str(e)}"


def format_email_content(papers, keyword):
    """이메일 본문 포맷팅"""
    today = datetime.now().strftime('%Y년 %m월 %d일')
    
    email_body = f"""
스터디레터 - '{keyword}' 관련 최신 논문 ({today})
{'=' * 70}

안녕하세요!

'{keyword}' 키워드로 검색된 최근 7일 이내 논문 {len(papers)}편을 요약해드립니다.

{'=' * 70}

"""
    
    for idx, paper in enumerate(papers, 1):
        authors = paper['authors'][:3]
        author_str = ', '.join(authors)
        if len(paper['authors']) > 3:
            author_str += f" 외 {len(paper['authors']) - 3}명"
        
        email_body += f"""
[논문 {idx}]
제목: {paper['title']}
저자: {author_str}
링크: {paper['pdf_url']}
발표일: {paper['published'].strftime('%Y-%m-%d')}

📝 Gemini 요약:
{paper['summary']}

{'-' * 70}

"""
    
    email_body += f"""

이 이메일은 스터디레터 서비스를 통해 자동으로 생성되었습니다.
Powered by arXiv & Google Gemini

"""
    
    return email_body


def send_email(recipient, subject, body):
    """SMTP를 통해 이메일 전송"""
    try:
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            raise ValueError("이메일 설정이 .env 파일에 없습니다.")
        
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient
        message['Subject'] = subject
        
        message.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True, None
    except Exception as e:
        return False, str(e)


def save_email_history(session, schedule_id, keyword, recipient, papers, status, error_msg, email_content):
    """이메일 발송 이력 저장"""
    history = EmailHistory(
        schedule_id=schedule_id,
        keyword=keyword,
        recipient=recipient,
        paper_count=len(papers),
        status=status,
        error_message=error_msg,
        email_content=email_content,
        sent_at=datetime.now()
    )
    session.add(history)
    session.commit()


def process_and_send(keyword, email, schedule_id=None):
    """논문 검색, 요약, 이메일 발송 프로세스"""
    session = get_session(engine)
    
    try:
        # 1. arXiv 검색
        papers = search_arxiv(keyword)
        
        if not papers:
            save_email_history(session, schedule_id, keyword, email, [], 'failed', 
                             '최근 7일 이내 논문을 찾지 못했습니다.', None)
            return False, "논문을 찾지 못했습니다."
        
        # 2. Gemini로 요약
        for paper in papers:
            paper['summary'] = summarize_with_gemini(paper['abstract'])
            time.sleep(1)  # API 호출 간격
        
        # 3. 이메일 포맷팅
        subject = f"[스터디레터] '{keyword}' 관련 최신 논문 ({datetime.now().strftime('%y/%m/%d')})"
        email_body = format_email_content(papers, keyword)
        
        # 4. 이메일 전송
        success, error_msg = send_email(email, subject, email_body)
        
        # 5. 이력 저장
        status = 'success' if success else 'failed'
        save_email_history(session, schedule_id, keyword, email, papers, status, error_msg, email_body)
        
        # 6. 스케줄 업데이트 (자동화인 경우)
        if schedule_id and success:
            schedule = session.query(Schedule).filter_by(id=schedule_id).first()
            if schedule:
                schedule.last_sent = datetime.now()
                session.commit()
        
        return success, error_msg
        
    finally:
        session.close()


def scheduled_job(schedule_id, keyword, email):
    """스케줄러에서 실행될 작업"""
    print(f"[{datetime.now()}] 자동 발송 시작: {keyword} → {email}")
    success, error = process_and_send(keyword, email, schedule_id)
    if success:
        print(f"[{datetime.now()}] 자동 발송 성공!")
    else:
        print(f"[{datetime.now()}] 자동 발송 실패: {error}")


def main():
    """메인 애플리케이션"""
    
    # 사이드바 - 메뉴
    with st.sidebar:
        st.markdown("## 📚 스터디레터")
        st.markdown("---")
        
        menu = st.radio(
            "메뉴",
            ["🚀 단발성 발송", "⏰ 자동화 관리", "📊 발송 이력"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ 정보")
        st.info("""
        **단발성 발송**: 즉시 논문 요약 이메일 발송
        
        **자동화 관리**: 매주 월요일 오전 9시 자동 발송 설정
        
        **발송 이력**: 모든 발송 기록 확인
        """)
    
    # 메인 영역
    if menu == "🚀 단발성 발송":
        show_instant_send()
    elif menu == "⏰ 자동화 관리":
        show_automation_management()
    else:
        show_email_history()


def show_instant_send():
    """단발성 발송 화면"""
    st.markdown("""
        <div class="header">
            <h1>📚 스터디레터</h1>
            <p>최신 논문을 AI가 요약해서 이메일로 보내드립니다</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔍 관심 키워드")
        keyword = st.text_input(
            "키워드 입력",
            placeholder="예: LLM, Quantum Computing, RAG",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("### 📧 이메일 주소")
        email = st.text_input(
            "이메일 입력",
            placeholder="your.email@example.com",
            label_visibility="collapsed"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 논문 요약 받기", use_container_width=True):
        if not keyword:
            st.error("⚠️ 키워드를 입력해주세요.")
            return
        
        if not email:
            st.error("⚠️ 이메일 주소를 입력해주세요.")
            return
        
        if not validate_email(email):
            st.error("⚠️ 올바른 이메일 형식이 아닙니다.")
            return
        
        if not os.getenv('GOOGLE_API_KEY'):
            st.error("⚠️ GOOGLE_API_KEY가 설정되지 않았습니다.")
            return
        
        with st.spinner('📖 논문을 찾고 Gemini가 읽고 있습니다...'):
            papers = search_arxiv(keyword)
            
            if not papers:
                st.warning(f"'{keyword}' 키워드로 최근 7일 이내 논문을 찾지 못했습니다.")
                return
            
            st.info(f"✅ {len(papers)}편의 논문을 찾았습니다!")
            
            progress_bar = st.progress(0)
            for idx, paper in enumerate(papers):
                with st.spinner(f'논문 {idx + 1}/{len(papers)} 요약 중...'):
                    paper['summary'] = summarize_with_gemini(paper['abstract'])
                    time.sleep(1)
                    progress_bar.progress((idx + 1) / len(papers))
            
            subject = f"[스터디레터] '{keyword}' 관련 최신 논문 ({datetime.now().strftime('%y/%m/%d')})"
            email_body = format_email_content(papers, keyword)
            
            with st.spinner('📨 이메일 전송 중...'):
                success, error = send_email(email, subject, email_body)
                
                # 이력 저장
                session = get_session(engine)
                status = 'success' if success else 'failed'
                save_email_history(session, None, keyword, email, papers, status, error, email_body)
                session.close()
                
                if success:
                    st.success("✨ 이메일 발송 완료! 받은 편지함을 확인해주세요.")
                    st.balloons()
                else:
                    st.error(f"이메일 전송 실패: {error}")


def show_automation_management():
    """자동화 관리 화면"""
    st.markdown("## ⏰ 자동화 관리")
    st.markdown("매주 월요일 오전 9시에 자동으로 논문 요약을 발송합니다.")
    
    # 새 자동화 추가
    st.markdown("### ➕ 새 자동화 추가")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        new_keyword = st.text_input("키워드", placeholder="예: LLM", key="new_keyword")
    
    with col2:
        new_email = st.text_input("이메일", placeholder="your.email@example.com", key="new_email")
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("추가", use_container_width=True):
            if not new_keyword or not new_email:
                st.error("키워드와 이메일을 모두 입력해주세요.")
            elif not validate_email(new_email):
                st.error("올바른 이메일 형식이 아닙니다.")
            else:
                session = get_session(engine)
                
                # 중복 체크
                existing = session.query(Schedule).filter_by(
                    keyword=new_keyword, 
                    email=new_email,
                    is_active=True
                ).first()
                
                if existing:
                    st.warning("이미 동일한 자동화가 존재합니다.")
                else:
                    # DB에 저장
                    schedule = Schedule(
                        keyword=new_keyword,
                        email=new_email,
                        is_active=True,
                        created_at=datetime.now()
                    )
                    session.add(schedule)
                    session.commit()
                    
                    # 스케줄러에 작업 추가
                    scheduler.add_weekly_job(scheduled_job, schedule.id, new_keyword, new_email)
                    
                    st.success(f"✅ 자동화가 추가되었습니다! (매주 월요일 09:00)")
                    st.rerun()
                
                session.close()
    
    st.markdown("---")
    
    # 현재 자동화 목록
    st.markdown("### 📋 활성 자동화 목록")
    
    session = get_session(engine)
    schedules = session.query(Schedule).filter_by(is_active=True).order_by(Schedule.created_at.desc()).all()
    
    if not schedules:
        st.info("등록된 자동화가 없습니다.")
    else:
        for schedule in schedules:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**🔑 키워드:** {schedule.keyword}")
                
                with col2:
                    st.markdown(f"**📧 이메일:** {schedule.email}")
                
                with col3:
                    if schedule.last_sent:
                        st.markdown(f"**📅 마지막 발송:** {schedule.last_sent.strftime('%Y-%m-%d %H:%M')}")
                    else:
                        st.markdown("**📅 마지막 발송:** 없음")
                
                with col4:
                    st.markdown(f"**⏰ 다음 발송:** 월요일 09:00")
                
                with col5:
                    if st.button("🗑️", key=f"delete_{schedule.id}"):
                        schedule.is_active = False
                        session.commit()
                        scheduler.remove_job(schedule.id)
                        st.success("자동화가 비활성화되었습니다.")
                        st.rerun()
                
                st.markdown("---")
    
    session.close()
    
    # 스케줄러 상태
    st.markdown("### 🔧 스케줄러 상태")
    jobs = scheduler.get_jobs()
    st.info(f"현재 {len(jobs)}개의 작업이 스케줄러에 등록되어 있습니다.")


def show_email_history():
    """발송 이력 화면"""
    st.markdown("## 📊 발송 이력")
    
    session = get_session(engine)
    
    # 통계
    total_count = session.query(EmailHistory).count()
    success_count = session.query(EmailHistory).filter_by(status='success').count()
    failed_count = session.query(EmailHistory).filter_by(status='failed').count()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📨 총 발송", f"{total_count}건")
    
    with col2:
        st.metric("✅ 성공", f"{success_count}건")
    
    with col3:
        st.metric("❌ 실패", f"{failed_count}건")
    
    st.markdown("---")
    
    # 필터
    col1, col2 = st.columns([1, 3])
    
    with col1:
        filter_status = st.selectbox(
            "상태 필터",
            ["전체", "성공", "실패"]
        )
    
    # 이력 조회
    query = session.query(EmailHistory).order_by(EmailHistory.sent_at.desc())
    
    if filter_status == "성공":
        query = query.filter_by(status='success')
    elif filter_status == "실패":
        query = query.filter_by(status='failed')
    
    histories = query.limit(50).all()
    
    if not histories:
        st.info("발송 이력이 없습니다.")
    else:
        for history in histories:
            with st.expander(
                f"{'✅' if history.status == 'success' else '❌'} "
                f"{history.keyword} → {history.recipient} "
                f"({history.sent_at.strftime('%Y-%m-%d %H:%M')})"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**키워드:** {history.keyword}")
                    st.markdown(f"**수신자:** {history.recipient}")
                    st.markdown(f"**논문 수:** {history.paper_count}편")
                
                with col2:
                    st.markdown(f"**상태:** {history.status}")
                    st.markdown(f"**발송 시각:** {history.sent_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    if history.schedule_id:
                        st.markdown(f"**유형:** 자동화 (ID: {history.schedule_id})")
                    else:
                        st.markdown(f"**유형:** 단발성")
                
                if history.error_message:
                    st.error(f"**오류:** {history.error_message}")
                
                if history.email_content:
                    st.markdown("**이메일 내용:**")
                    st.code(history.email_content, language="text")
    
    session.close()


if __name__ == "__main__":
    main()
