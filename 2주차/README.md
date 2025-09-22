# 대학교 통합정보시스템 추상클래스로 클론 코딩하기

Streamlit 서버 주소 : http://barahana25.duckdns.org:10081/?waonawklgnwo=abvwnoewinmahwerotknwaoea

## 1. 도메인 설명
대학교 통합정보시스템(데이터베이스)을 클론코딩하여 추상클래스로 구현했습니다.  
크게 보면 학생, 교수, 강의, 구성원 로그인, 접근 로그를 추상클래스로 구현했습니다.  
강의 목록은 2025년 2학기 목록을 그대로 가져왔습니다. (github에는 개인정보 비식별화하여 올렸습니다.)  
구현한 사항  
**학생**: 학생 개인 정보 확인, 전체 강의 조회, 학생 성적 확인  
**교수**: 본인 학과 소속 학생 정보 조회, 성적 조회  
**로그인 기록**: 구성원 로그인 기록 조회  
**접근 로그**: 구성원이 어느 기능을 호출했는지 조회  

## 1-1. 설계 - UML 디자인(Mermaid Diagram)  
추상적으로 Model으로만 구현한 Diagram 사진입니다.  
<img width="300" height="500" alt="image01" src="https://github.com/user-attachments/assets/86fd566d-f9f8-42b4-bd6f-20aa3c1bc4a7" />


Repository, Service로 구현한 Diagram 사진입니다.  
<img width="900" height="300" alt="image02" src="https://github.com/user-attachments/assets/143fe1ac-f2a4-4346-ba3c-765190dcdeea" />  

관계형 데이터베이스처럼 보이지만 정규화는 적용하지 않았고 In-Memory 추상클래스로만 구현했습니다.  

## 2. 코드 설명
## 2-1. Model 부분 (Login, Log 부분은 생략) 
<img width="300" height="600" alt="image03" src="https://github.com/user-attachments/assets/58896020-93f6-4177-9605-835f5ea5c4a8" />  

dataclasses 모듈에 있는 dataclass 데코레이터를 사용해 DAO(Data Access Object) 역할을 하는 클래스를 작성하고 해당 클래스가 가져야 할 요소들을 기술했습니다.

## 2-2. Repository(CRUD 기능 수행) 부분  
<img width="400" height="500" alt="image04" src="https://github.com/user-attachments/assets/73ede15e-50ba-4cea-bfd0-4bd15d818ae9" />  

교수, 학생, 강의, 등록 에 대한 추상 클래스를 Repository로 작성했습니다.  
자식 클래스가 가져야 하는 추상 함수(메서드)에 @abstractmethod 데코레이터를 추가하였습니다.  
CRUD 중 Read와 Update에 관련된 함수가 존재합니다. 후술할 Service 클래스에서 이 함수들을 호출하게 됩니다.  

## 2-3. Service (핵심 로직 구현) 부분
<img width="400" height="500" alt="image" src="https://github.com/user-attachments/assets/c100f059-f71d-4a5b-b651-8844a3679704" />  

학생, 교수, 관리자, 교직원의 기능에 대한 추상 클래스입니다.  

<img width="400" height="500" alt="image" src="https://github.com/user-attachments/assets/5b11ee73-8529-4eb7-98f4-a950992d77e4" />  

학생 서비스 - 학생 개인 정보, 개설 강좌, 성적표 조회 기능을 구현했습니다.  
<img width="398" height="500" alt="image" src="https://github.com/user-attachments/assets/e51536ed-ae6c-4785-9def-7197db7052a1" />  

교수 서비스 - 학생 정보, 성적표 조회 기능을 구현했습니다.  
사용자가 정보를 조회할 때마다 audit 함수를 호출해 접근 로그에 저장합니다.  

## 2-4. In-Memory Repository 부분
<img width="400" height="400" alt="image07" src="https://github.com/user-attachments/assets/dcdcdb0b-5608-4f28-ad84-ba7216735365" />  

SQL같은 데이터베이스로 영속적인 CRUD를 구현하려면 너무 복잡한 프로그램이 될 것 같아
In-Memory Dictionary로 대체했습니다. (실행 종료 후 데이터 휘발)

## 3. 더미 데이터 삽입 및 실행 화면
<img width="400" height="400" alt="image08" src="https://github.com/user-attachments/assets/2330b36c-0bde-46ac-93b9-2c05947bbb9a" />

더미 데이터들을 생성해 각각의 repository에 저장하도록 했습니다.  

아래 화면은 로그인, 정보 조회, 로그 조회를 수행한 화면입니다.  
<img width="900" height="800" alt="image09" src="https://github.com/user-attachments/assets/9ef4a93e-284c-40a0-bb03-9ed4fb0317ab" />

<img width="969" height="542" alt="image" src="https://github.com/user-attachments/assets/1d8da994-b21f-494b-88c2-2e637e7be551" />  

## 4. Streamlit으로 구현 (코드는 생략하고 결과 화면만 캡쳐했습니다.)
## 4-1. 학생 권한 화면
학생 정보 조회 화면입니다.  
<img width="500" height="400" alt="image10" src="https://github.com/user-attachments/assets/9e4979bc-0a51-4ff3-bfc1-9b35371dd631" />

학생 기능 중 개설 강좌 조회 화면입니다.  
<img width="500" height="400" alt="image11" src="https://github.com/user-attachments/assets/fb9a7728-8b31-4251-abfc-ed629d3dbbd7" />

학생 성적표 조회 화면입니다.  
<img width="500" height="400" alt="image12" src="https://github.com/user-attachments/assets/c76716b2-204a-4cc0-8d5e-0578f426a54a" />

학생 로그인 로그 조회 화면입니다.  
<img width="500" height="400" alt="image13" src="https://github.com/user-attachments/assets/cfaf42d8-e28e-4825-9c0f-3846617a407b" />

접근 log 조회 화면입니다.  
<img width="500" height="400" alt="image14" src="https://github.com/user-attachments/assets/125c6f89-3bb6-48a7-9174-bfe3b1a49c4f" />

## 4-2. 교수 권한 화면
학생 정보 조회 화면입니다.  
<img width="500" height="400" alt="image15" src="https://github.com/user-attachments/assets/025919ef-4454-4f75-b449-ba186aff96ea" />

학생 성적 조회 화면입니다.  
<img width="500" height="400" alt="image16" src="https://github.com/user-attachments/assets/3bc710f0-44ff-46b4-82c5-cee5920b9aba" />

교수 접근 log 조회 화면입니다.  
<img width="500" height="400" alt="image17" src="https://github.com/user-attachments/assets/4c6ea7c0-2e64-4320-b13a-6d9faf59d6de" />

## 5. 결론
대학교 통합정보시스템의 데이터베이스를 파이썬으로 추상클래스, 도메인 주도 설계(DDD) 기법을 이용해 클론 코딩을 실습해 보면서 추상화와 계층화에 대해서 더 잘 이해할 수 있었습니다. 또한, 추상화를 통해 Model-Repository-Service 구조를 이해하는데 많은 도움이 된 것 같습니다.
이번 과제에서는 실제 DB를 사용하지 않고 In-Memory Repository로 구현했지만 추후 SQLite나 MySQL같은 관계형 데이터베이스로 고도화하여 영속적으로 데이터를 저장할 수 있도록 발전시키고 싶습니다.

