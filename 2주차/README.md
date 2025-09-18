# 대학교 통합정보시스템 추상클래스로 클론 코딩하기

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
<img width="183" height="261" alt="image" src="https://github.com/user-attachments/assets/fd985b21-7f2a-4ae2-aa4c-692cc6bce072" />

Repository, Service로 구현한 Diagram 사진입니다.  
<img width="569" height="140" alt="image" src="https://github.com/user-attachments/assets/893b758f-ff0f-4fd6-b837-d85690f4dc0f" />  

관계형 데이터베이스처럼 보이지만 정규화는 적용하지 않았고 In-Memory 추상클래스로만 구현했습니다.  

## 2. 코드 설명
## 2-1. Model 부분 (Login, Log 부분은 생략)
<img width="162" height="332" alt="image" src="https://github.com/user-attachments/assets/1f154643-cf28-4d47-a1c1-66fe31677cd2" />    

dataclasses 모듈에 있는 dataclass 데코레이터를 사용해 DAO(Data Access Object) 역할을 하는 클래스를 작성하고 해당 클래스가 가져야 할 요소들을 기술했습니다.

## 2-2. Repository(CRUD 기능 수행) 부분
<img width="382" height="435" alt="image" src="https://github.com/user-attachments/assets/56b3e28b-4653-4370-9798-9865e5104f99" />  

교수, 학생, 강의, 등록 에 대한 추상 클래스를 Repository로 작성했습니다.  
자식 클래스가 가져야 하는 추상 함수(메서드)에 @abstractmethod 데코레이터를 추가하였습니다.  
CRUD 중 Read와 Update에 관련된 함수가 존재합니다. 후술할 Service 클래스에서 이 함수들을 호출하게 됩니다.  

## 2-3. Service (핵심 로직 구현) 부분
<img width="481" height="394" alt="image" src="https://github.com/user-attachments/assets/36fb544a-28c7-4b9e-bd33-c4683647509a" />  

학생 서비스 - 학생 개인 정보, 개설 강좌, 성적표 조회 기능을 구현했습니다.

<img width="481" height="379" alt="image" src="https://github.com/user-attachments/assets/2fcedf3e-04c0-4acb-8916-6cffb115910f" />  

교수 서비스 - 학생 정보, 성적표 조회 기능을 구현했습니다.  
사용자가 정보를 조회할 때마다 audit 함수를 호출해 접근 로그에 저장합니다.  

## 2-4. In-Memory Repository 부분
<img width="410" height="399" alt="image" src="https://github.com/user-attachments/assets/09e0e1a2-a92a-44e0-b76f-a8783a95e5f5" />

SQL같은 데이터베이스로 영속적인 CRUD를 구현하려면 너무 복잡한 프로그램이 될 것 같아
In-Memory Dictionary로 대체했습니다. (실행 종료 후 데이터 휘발)

## 3. 더미 데이터 삽입 및 실행 화면
<img width="431" height="349" alt="image" src="https://github.com/user-attachments/assets/28cf2de5-0870-48b7-9046-4e8e3586fb9e" />

더미 데이터들을 생성해 각각의 repository에 저장하도록 했습니다.  

아래 화면은 로그인, 정보 조회, 로그 조회를 수행한 화면입니다.  
<img width="540" height="333" alt="image" src="https://github.com/user-attachments/assets/9f957cef-6029-4708-9146-b0a8de61c7fc" />

<img width="969" height="542" alt="image" src="https://github.com/user-attachments/assets/1d8da994-b21f-494b-88c2-2e637e7be551" />  

## 4. Streamlit으로 구현 (코드는 생략하고 결과 화면만 캡쳐했습니다.)
## 4-1. 학생 권한 화면
학생 정보 조회 화면입니다.  
<img width="419" height="262" alt="image" src="https://github.com/user-attachments/assets/193a8477-afcd-4f9f-8518-a253ca0b1810" />

학생 기능 중 개설 강좌 조회 화면입니다.  
<img width="495" height="270" alt="image" src="https://github.com/user-attachments/assets/a55322f8-6fa3-4c70-84bd-91654243070d" />

학생 성적표 조회 화면입니다.  
<img width="499" height="188" alt="image" src="https://github.com/user-attachments/assets/375dfb61-b8ea-4769-8b23-16b16d626f4a" />

학생 로그인 로그 조회 화면입니다.  
<img width="564" height="207" alt="image" src="https://github.com/user-attachments/assets/267b2a79-15b5-4523-99ee-90d4340b43df" />

접근 log 조회 화면입니다.  
<img width="538" height="237" alt="image" src="https://github.com/user-attachments/assets/29f8a296-9e2f-4c63-aeb5-9f718ab41877" />

## 4-2. 교수 권한 화면
학생 정보 조회 화면입니다.  
<img width="569" height="206" alt="image" src="https://github.com/user-attachments/assets/afec21eb-ebc4-4fd9-9252-4b3ef56fb2cc" />

학생 성적 조회 화면입니다.  
<img width="547" height="249" alt="image" src="https://github.com/user-attachments/assets/a8989576-b334-4b74-a5a2-ac1691d771f3" />

교수 접근 log 조회 화면입니다.  
<img width="569" height="239" alt="image" src="https://github.com/user-attachments/assets/2fa4b0c3-ee48-4b63-aa49-17e8f45b30b7" />

## 5. 결론
대학교 통합정보시스템의 데이터베이스를 파이썬으로 추상클래스, 도메인 주도 설계(DDD) 기법을 이용해 클론 코딩을 실습해 보면서 추상화와 계층화에 대해서 더 잘 이해할 수 있었습니다. 또한, 추상화를 통해 Model-Repository-Service 구조를 이해하는데 많은 도움이 된 것 같습니다.
이번 과제에서는 실제 DB를 사용하지 않고 In-Memory Repository로 구현했지만 추후 SQLite나 MySQL같은 관계형 데이터베이스로 고도화하여 영속적으로 데이터를 저장할 수 있도록 발전시키고 싶습니다.

