# LMS API를 이용해 간단한 streamlit App 만들기

Streamlit 서버 주소 : http://barahana25.duckdns.org:8501/?baiwowoefn=owpbmawevpnawergiph 

## 1. 서론
금오공대의 LMS에서는 공지사항이나 과제, 강의 자료 등을 확인하기 위해서 사이트에 접속해 로그인을 하고 해당 강의 탭에 들어가 확인해야 하는 복잡한 과정을 거쳐야 했습니다.  
이러한 과정을 단축시키고자 LMS api를 이용해 크롤러를 만들고 이를 텔레그램 알림으로 전송하며, 모든 강의 자료들을 한 눈에 파악할 수 있는 streamlit app을 만들었습니다.  
<img width="513" height="218" alt="image" src="https://github.com/user-attachments/assets/9931ee0c-dfac-4ba6-bccc-8d15317307ef" />  
1학기 때 작성한 코드에서 일부 수정하여 과제로 활용했습니다.  
(https://github.com/barahana25/LMS_Anouncement)

## 2. 과제 설명
### 2-1. API 키 불러오기   
<img width="500" height="300" alt="image" src="https://github.com/user-attachments/assets/1a4d113b-8e5a-46ae-9aae-a3be6cc46209" />  

TOKEN이나 API KEY는 개인정보에 해당하므로 코드가 공개적인 장소에 올라가도 문제없도록 환경 변수로 설정했습니다.  

### 2-2. 텔레그램봇 함수 구현
<img width="569" height="109" alt="image" src="https://github.com/user-attachments/assets/c9284263-d427-4d89-855f-e9c689a59533" />  

텔레그램은 간단하게 문자만 보낼 수 있는 함수만 구현했습니다.

### 2-3. 데이터베이스 구현 (sqlite3)
<img width="412" height="312" alt="image" src="https://github.com/user-attachments/assets/76ca4d19-4d6b-402e-bab0-b712f1e4f140" />

앞으로 나올 모든 데이터베이스 테이블의 추상클래스입니다.  

### 2-3-1. 과제 테이블
<img width="543" height="266" alt="image" src="https://github.com/user-attachments/assets/7c497e01-9b82-4220-87cc-77562ec70340" />

과제 id, 강의 id, 과제 이름, 과제 시작일, 마감일, 본문을 저장할 수 있도록 테이블을 만들었습니다.

### 2-3-2. 공지 테이블
<img width="569" height="273" alt="image" src="https://github.com/user-attachments/assets/f59c5f04-b91a-46a9-a873-d06d2285eb8c" />

공지 id, 강의 id, 공지 제목, 공지 본문, 공지 날짜 등을 저장하는 공지 테이블을 만들었습니다.

### 2-3-3. 강의자료 테이블
<img width="569" height="394" alt="image" src="https://github.com/user-attachments/assets/eedb7f91-833e-4034-8295-337db14f57fc" />

강의 id, 파일 이름, 파일 크기, 업로드 날짜 등을 저장하는 테이블을 정의했습니다.

### 2-3-4. 파일 감지 클래스
<img width="569" height="262" alt="image" src="https://github.com/user-attachments/assets/8baefbb1-f158-4995-a1d4-0f5a4ea68a80" />

크롤링을 수행한 후에 DB에 추가된 파일을 감지해서 텔레그램으로 알려주기 위해 check_for_update 함수를 작성했습니다.

## 3. main 함수
<img width="448" height="430" alt="image" src="https://github.com/user-attachments/assets/344a4c95-e6e0-4802-b128-460bb7f78605" />

<img width="569" height="326" alt="image" src="https://github.com/user-attachments/assets/f988bdd5-2072-4ff7-a3e0-a86a5370143d" />

courses마다 반복문을 돌면서 공지사항, 과제, 강의자료 등을 크롤링하여 db에 저장합니다.

## 4. loop_main 함수
<img width="569" height="78" alt="image" src="https://github.com/user-attachments/assets/fac5d2fe-03c6-45b4-9f41-64d8e604c845" />

새벽 2시부터 6시까지 휴식  
<img width="569" height="375" alt="image" src="https://github.com/user-attachments/assets/f2882b81-4cb0-4096-b08c-a3b2d0294063" />

10분마다 한 번씩 main함수를 실행하고 DB에 저장된 최신항목들을 텔레그램 알림으로 전송합니다.

## 5. streamlit 앱 구현
<img width="332" height="406" alt="image" src="https://github.com/user-attachments/assets/ac42bee8-1601-41af-80df-64bff8970a39" />

sqlite3을 사용해 DB에서 read_table로 해당 테이블(공지사항, 과제, 강의 파일) 에 있는 레코드들을 pandas의 dataframe으로 가져옵니다.

### 5-1. 강의 탭 설정
<img width="509" height="407" alt="image" src="https://github.com/user-attachments/assets/c74179ae-2343-42c4-a36d-d5ce41d92924" />

<img width="569" height="247" alt="image" src="https://github.com/user-attachments/assets/290720d8-c418-4065-93d7-7112e582f0b9" />

### 5-2. 과제 탭 설정
<img width="569" height="441" alt="image" src="https://github.com/user-attachments/assets/68157642-f62f-482d-bd88-20ebd7447e3c" />

<img width="569" height="269" alt="image" src="https://github.com/user-attachments/assets/dc17f607-1bcf-414c-a9ab-1610bc018c74" />

### 5-3. 강의 파일 탭 설정
<img width="569" height="495" alt="image" src="https://github.com/user-attachments/assets/1f683fd4-125f-4f7f-b29d-a0bc56bc73ea" />

<img width="569" height="282" alt="image" src="https://github.com/user-attachments/assets/2671983f-6beb-4c15-9b9d-254f4b85adc5" />

## 6. 결론
LMS 알리미를 1학기 때 만들고 현재까지 사용하면서 텔레그램으로 알림이 오도록 했었는데, 메신저 앱 특성상 알림이 누적되면서 오래된 내용을 확인하기 불편했고, 알림을 봤지만 까먹는 경우도 있었습니다.  
하지만 streamlit app으로 만들어 전체적인 공지 사항들을 확인하니 한눈에 필요한 정보들을 정리해서 볼 수 있었고, 이전 알림들도 쉽게 다시 확인할 수 있었습니다.
































