# 📚 PaperDigest MVP

> **최신 논문을 AI가 요약해서 이메일로 보내드립니다**

Google Gemini를 활용하여 arXiv의 최신 논문을 검색하고, 한국어로 요약하여 이메일로 전달하는 웹 애플리케이션입니다.

## ✨ 주요 기능

- 🔍 **키워드 기반 논문 검색**: arXiv에서 최근 7일 이내 발표된 논문 자동 검색
- 🤖 **AI 요약**: Google Gemini Lite (gemini-1.5-flash-8b)가 영문 초록을 3줄 한국어 요약으로 변환
- 📧 **단발성 이메일 전송**: 즉시 요약된 논문 정보를 이메일로 발송
- ⏰ **자동화 스케줄링**: 매주 월요일 오전 9시 자동 발송 설정
- 📊 **발송 이력 대시보드**: 모든 발송 기록 및 통계 확인
- 🎨 **직관적인 UI**: Streamlit 기반의 아름다운 웹 인터페이스

## 🛠️ 기술 스택

- **Frontend & Backend**: Python + Streamlit
- **논문 검색**: arXiv API
- **AI 요약**: Google Gemini API (gemini-1.5-flash-8b - Lite 모델)
- **이메일 전송**: Gmail SMTP
- **스케줄링**: APScheduler (백그라운드 작업)
- **데이터베이스**: SQLite (스케줄 및 이력 관리)

## 📋 사전 준비사항

### 1. Python 설치
Python 3.8 이상이 필요합니다.

```bash
python --version  # 3.8 이상 확인
```

### 2. Google Gemini API 키 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Create API Key" 클릭
3. API 키 복사 (나중에 `.env` 파일에 사용)

### 3. Gmail 앱 비밀번호 생성

이메일 전송을 위해 Gmail 앱 비밀번호가 필요합니다.

1. [Google 계정 설정](https://myaccount.google.com/) 접속
2. **보안** → **2단계 인증** 활성화 (필수)
3. **보안** → **앱 비밀번호** 클릭
4. 앱 선택: "메일", 기기 선택: "기타" (PaperDigest 입력)
5. 생성된 16자리 비밀번호 복사 (나중에 `.env` 파일에 사용)

⚠️ **주의**: 일반 Gmail 비밀번호가 아닌 앱 비밀번호를 사용해야 합니다!

## 🚀 설치 및 실행

### 1. 프로젝트 클론 또는 다운로드

```bash
cd /Users/kimsaeam/.gemini/antigravity/playground/electric-magnetar
```

### 2. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
# venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성합니다:

```bash
cp .env.example .env
```

`.env` 파일을 열어 실제 값으로 수정합니다:

```env
# Google Gemini API Key
GOOGLE_API_KEY=your_actual_gemini_api_key_here

# Gmail SMTP Configuration
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_16_digit_app_password_here
```

### 5. 애플리케이션 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 애플리케이션을 확인할 수 있습니다.

## 📖 사용 방법

### 🚀 단발성 발송 (즉시 발송)

1. **키워드 입력**: 관심 있는 연구 주제 키워드 입력 (예: "LLM", "Quantum Computing")
2. **이메일 입력**: 요약본을 받을 이메일 주소 입력
3. **전송 요청**: "🚀 논문 요약 받기" 버튼 클릭
4. **대기**: 논문 검색 및 AI 요약 진행 (약 10~30초 소요)
5. **확인**: 이메일 받은편지함에서 요약본 확인

### ⏰ 자동화 설정 (매주 월요일 오전 9시 자동 발송)

1. 사이드바에서 **"⏰ 자동화 관리"** 메뉴 선택
2. **키워드**와 **이메일** 입력
3. **"추가"** 버튼 클릭
4. 매주 월요일 오전 9시에 자동으로 논문 요약 이메일 발송
5. 자동화 목록에서 언제든지 삭제 가능 (🗑️ 버튼)

### 📊 발송 이력 확인

1. 사이드바에서 **"📊 발송 이력"** 메뉴 선택
2. 총 발송, 성공, 실패 통계 확인
3. 상태별 필터링 (전체/성공/실패)
4. 각 발송 기록 클릭하여 상세 내용 확인
   - 키워드, 수신자, 논문 수
   - 발송 시각, 유형 (단발성/자동화)
   - 이메일 전체 내용 아카이빙

## 📧 이메일 형식 예시

```
PaperDigest - 'LLM' 관련 최신 논문 (2026년 01월 17일)
======================================================================

[논문 1]
제목: Attention Is All You Need
저자: Ashish Vaswani, Noam Shazeer, Niki Parmar 외 5명
링크: https://arxiv.org/pdf/1706.03762
발표일: 2026-01-15

📝 Gemini 요약:
• Transformer 아키텍처를 제안하여 RNN 없이도 sequence-to-sequence 모델을 구현해요.
• Self-attention 메커니즘으로 입력 시퀀스의 모든 위치 간 관계를 효율적으로 학습해요.
• 기계 번역 태스크에서 SOTA 성능을 달성하면서 학습 시간도 크게 단축했어요.

----------------------------------------------------------------------
```

## 🔧 문제 해결

### 이메일 전송 실패

**증상**: "이메일 전송 중 오류가 발생했습니다"

**해결 방법**:
1. `.env` 파일의 `SENDER_EMAIL`과 `SENDER_PASSWORD` 확인
2. Gmail 앱 비밀번호가 올바른지 확인 (16자리, 공백 없이)
3. Gmail 2단계 인증이 활성화되어 있는지 확인

### Gemini API 오류

**증상**: "요약 생성 중 오류가 발생했습니다"

**해결 방법**:
1. `.env` 파일의 `GOOGLE_API_KEY` 확인
2. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키 상태 확인
3. API 사용량 한도 확인

### 논문을 찾지 못함

**증상**: "키워드로 최근 7일 이내 논문을 찾지 못했습니다"

**해결 방법**:
1. 더 일반적인 키워드 사용 (예: "machine learning" 대신 "ML")
2. 영어 키워드 사용 권장
3. 최근 7일 이내 해당 주제의 논문이 실제로 없을 수 있음

## 📁 프로젝트 구조

```
electric-magnetar/
├── app.py                 # 메인 Streamlit 애플리케이션
├── database.py            # 데이터베이스 모델 (스케줄, 이력)
├── scheduler.py           # 자동화 스케줄러
├── requirements.txt       # Python 의존성
├── .env.example          # 환경 변수 템플릿
├── .env                  # 실제 환경 변수 (git에서 제외됨)
├── .gitignore           # Git 제외 파일 목록
├── paperdigest.db       # SQLite 데이터베이스 (자동 생성)
└── README.md            # 프로젝트 문서 (이 파일)
```

## 🎯 주요 기능 상세

### arXiv 검색 로직
- 최근 7일 이내 발표된 논문만 필터링
- 최신순 정렬
- 최대 5개 논문 반환

### Gemini 요약 프롬프트
- 역할: "연구 보조 AI"
- 출력: 정확히 3개의 불릿 포인트
- 톤: 전문적이면서도 읽기 쉬운 해요체
- 기술 용어: 어색한 번역 대신 영어 유지

### 이메일 구성
- 제목: `[PaperDigest] '{키워드}' 관련 최신 논문 (YY/MM/DD)`
- 본문: 논문별로 제목, 저자, 링크, 발표일, Gemini 요약 포함

## 🔒 보안 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- API 키와 비밀번호를 코드에 직접 작성하지 마세요
- 공개 저장소에 업로드 시 `.gitignore` 확인 필수

## 📝 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 자유롭게 사용 가능합니다.

## 🙏 크레딧

- **arXiv**: 오픈 액세스 논문 저장소
- **Google Gemini**: AI 요약 생성
- **Streamlit**: 웹 애플리케이션 프레임워크

---

**Made with ❤️ for researchers**
