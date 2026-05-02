# 도시 생존 성향 테스트

**오픈소스소프트웨어실습** 중간고사 대체 과제로 제작된 Streamlit 기반 웹 애플리케이션입니다.
프로젝트문(Project Moon)의 세계관을 바탕으로, 사용자의 성향과 죄악 속성을 분석하여 가장 잘 어울리는 '소속'을 판별해 줍니다.

---

## 개발자 정보
- **학번:** 2021204045
- **이름:** 이성민

---

## 주요 기능
1. **로그인 및 회원가입 (`auth.py`)**
   - Pandas를 활용하여 `data/users.csv`에 회원 정보를 안전하게 암호화(SHA-256)하여 저장하고 관리합니다.
2. **캐싱 기능 (`@st.cache_data`)**
   - 방대한 퀴즈 데이터(`questions.json`)와 결과 매핑 엑셀 데이터(`소속 죄악.xlsx`)를 불러올 때 캐싱을 적용하여 페이지 로딩 속도를 최적화했습니다.
3. **퀴즈 및 결과 판별 알고리즘**
   - 총 21개의 선택형 퀴즈를 제공합니다.
   - 엑셀 데이터 기반으로 사용자의 7대 죄악 비율(%)과 소속별 죄악 비율의 거리를 계산하고, 파벌 가중치를 적용하여 최적의 결과를 도출합니다.
4. **히스토리 기록 기능**
   - 테스트 결과를 시간에 따라 자동 저장(`data/history_[유저명].json`)하고 열람할 수 있습니다.

---

## 실행 방법

### 1. 저장소 클론
```bash
git clone https://github.com/Alphrit/face-the-sin-test
cd face-the-sin-test
```
### 2. 필수 라이브러리 설치
Python 가상환경(venv) 생성을 권장합니다.

```bash
pip install -r requirements.txt
```
### 3. 애플리케이션 실행
프로젝트 최상위 디렉토리에서 아래 명령어를 실행합니다.

```bash
streamlit run app.py
```
실행 후 터미널에 표시되는 Local URL (보통 http://localhost:8501)을 클릭하여 웹 브라우저에서 확인할 수 있습니다.

## 프로젝트 구조
``` plaintext
face-the-sin-test
 ┣ data/
 ┃ ┣ history_*.json       # (자동생성) 유저별 테스트 기록
 ┃ ┣ questions.json       # 퀴즈 문항 및 선택지 데이터
 ┃ ┣ users.csv            # (자동생성) 회원가입 데이터
 ┃ ┗ 소속 죄악.xlsx       # 결과 매핑 알고리즘용 엑셀 데이터
 ┣ images/                # UI용 배경, 로고, 캐릭터 이미지 폴더
 ┣ app.py                 # Streamlit 메인 실행 파일
 ┣ auth.py                # 로그인/회원가입 처리 모듈
 ┣ .gitignore             # Git 제외 파일 목록
 ┣ requirements.txt       # 필수 라이브러리 목록
 ┗ README.md              # 프로젝트 설명서 (현재 파일)
