from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
import hashlib, re, uuid, json
try:
    from syllabus_2025_2 import syllabus_2025_2
except:
    from anonymized_syllabus_2025_2 import syllabus_2025_2

@dataclass
class Professor:
    pno: str
    pname: str
    dept_name: str

@dataclass
class Student:
    sno: str
    sname: str
    gender: str
    dept_name: str
    year: int
    phone: Optional[str] = None

@dataclass
class Lecture:
    lec_no: str
    pno: str
    lec_name: str
    credit: int
    dept_name: Optional[str] = None
    year: Optional[int] = 2025
    semester: Optional[int] = 2

@dataclass(frozen=True)
class EnrollmentId:
    sno: str
    lec_no: str

@dataclass
class Enrollment:
    id: EnrollmentId
    grade: Optional[str] = None
    mid_score: Optional[int] = None
    final_score: Optional[int] = None

@dataclass
class StudentAccount:
    sno: str
    password_hash: str
    last_login: Optional[datetime] = None

@dataclass
class ProfessorAccount:
    pno: str
    password_hash: str
    last_login: Optional[datetime] = None

@dataclass
class LoginLog:
    id: str
    user_id: str
    role: str
    last_login: datetime

@dataclass
class StudentProfileDTO:
    sno: str
    sname: str
    gender: str
    dept_name: str
    year: int
    phone: Optional[str]

@dataclass
class GradeDetailDTO:
    lec_no: str
    lec_name: str
    credit: int
    grade: str
    score: float

def sha256_hex(raw):
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def grade_to_score(g):
    m = {
        "A+": 4.5, "A": 4.0,
        "B+": 3.5, "B": 3.0,
        "C+": 2.5, "C": 2.0,
        "D+": 1.5, "D": 1.0,
        "F": 0.0
    }
    return m.get(g.upper(), 0.0)

def is_valid_student_id(s):
    return s.isnumeric()

def is_valid_prof_id(p):
    return re.fullmatch(r"F\d{5}", p) is not None

class ProfessorRepository(ABC):
    @abstractmethod
    def find_by_id(self, pno): ...
    @abstractmethod
    def save(self, prof): ...
    @abstractmethod
    def search_by_dept(self, dept_name): ...

class StudentRepository(ABC):
    @abstractmethod
    def find_by_id(self, sno): ...
    @abstractmethod
    def save(self, stu): ...
    @abstractmethod
    def search_by_dept_and_keyword(self, dept_name, keyword): ...

class LectureRepository(ABC):
    @abstractmethod
    def find_by_id(self, lec_no): ...
    @abstractmethod
    def save(self, lec): ...
    @abstractmethod
    def find_lecture(self, *, year, semester, dept_name): ...
    @abstractmethod
    def find_by_professor(self, pno, *, year=None, semester=None): ...

class EnrollmentRepository(ABC):
    @abstractmethod
    def find_by_student(self, sno): ...
    @abstractmethod
    def find_by_lecture(self, lec_no): ...
    @abstractmethod
    def save(self, e): ...

class StudentAccountRepository(ABC):
    @abstractmethod
    def find_by_id(self, sno): ...
    @abstractmethod
    def save(self, acc): ...

class ProfessorAccountRepository(ABC):
    @abstractmethod
    def find_by_id(self, pno): ...
    @abstractmethod
    def save(self, acc): ...

class LoginLogRepository(ABC):
    @abstractmethod
    def save(self, log): ...
    @abstractmethod
    def search_by_userid_keyword(self, keyword): ...

@dataclass
class AuditLog:
    id: str
    timestamp: datetime
    actor_id: Optional[str]
    role: Optional[str]
    action: str
    params_json: str

class AuditLogRepository(ABC):
    @abstractmethod
    def save(self, log): ...
    @abstractmethod
    def search(self, *, actor_kw: str = "", limit: int = 200): ...

def _audit(audit_repo, *, actor_id, role,
           action, params=None):
    if audit_repo is None:
        print("returning because audit_repo is None")
        return
    
    params_json = json.dumps(params or {}, ensure_ascii=False)
    log = AuditLog(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        actor_id=actor_id, role=role, action=action,
        params_json=params_json)
    audit_repo.save(log)

class AuthService:
    def __init__(self, student_account_repo, prof_account_repo,
                 login_log_repo, audit_repo):
        self.student_account_repo = student_account_repo
        self.prof_account_repo = prof_account_repo
        self.login_log_repo = login_log_repo
        self.audit_repo = audit_repo

    def login(self, user_id, password_plain):
        if is_valid_student_id(user_id):
            account = self.student_account_repo.find_by_id(user_id); role = "student"
            if not account or account.password_hash != sha256_hex(password_plain):
                return False
            account.last_login = datetime.now(); self.student_account_repo.save(account)
        elif is_valid_prof_id(user_id):
            account = self.prof_account_repo.find_by_id(user_id); role = "professor"
            if not account or account.password_hash != sha256_hex(password_plain):
                return False
            account.last_login = datetime.now(); self.prof_account_repo.save(account)
        else:
            return False

        self.login_log_repo.save(LoginLog(str(uuid.uuid4()), user_id, role, datetime.now()))
        Cookie = f"demo-Cookie::{user_id}::{role}::{int(datetime.now().timestamp())}"
        _audit(self.audit_repo, actor_id=user_id, role=role, action="auth.login",
                params={"user_id": user_id})
        return {"Cookie": Cookie, "role": role}
    
class StudentService:
    def __init__(self, student_repo,
                 lecture_repo, enrollment_repo,
                 audit_repo, current_actor):
        self.student_repo = student_repo;self.lecture_repo = lecture_repo; self.enrollment_repo = enrollment_repo
        self.audit_repo = audit_repo
        self.current_actor = current_actor

    def get_profile(self, sno):
        actor, role = self.current_actor()
        stu = self.student_repo.find_by_id(sno)
        if not stu:
            raise ValueError(f"학생 없음: {sno}")
        dto = StudentProfileDTO(stu.sno, stu.sname, stu.gender, stu.dept_name, stu.year, stu.phone)
        _audit(self.audit_repo, actor_id=actor, role=role, action="student.get_profile",
                params={})
        return dto

    def search_lecture(self, *, year, semester, dept_name):
        actor, role = self.current_actor()
        res = self.lecture_repo.find_lecture(year=year, semester=semester, dept_name=dept_name)
        _audit(self.audit_repo, actor_id=actor, role=role, action="student.search_lecture",
               params={"year":year,"semester":semester,"dept_name":dept_name})
        return res

    def get_grade_report_by_student(self, sno):
        actor, role = self.current_actor()
        details = []
        for e in self.enrollment_repo.find_by_student(sno):
            lec = self.lecture_repo.find_by_id(e.id.lec_no)
            if not lec or not e.grade:
                continue
            sc = grade_to_score(e.grade)
            details.append(GradeDetailDTO(lec.lec_no, lec.lec_name, lec.credit, e.grade, sc))

        _audit(self.audit_repo, actor_id=actor, role=role, action="student.get_grade_report_by_student",
               params={})
        return details

class ProfessorService:
    def __init__(self, professor_repo, student_repo,
                 lecture_repo, enrollment_repo,
                 audit_repo, current_actor):
        self.professor_repo=professor_repo; self.student_repo=student_repo; 
        self.lecture_repo=lecture_repo; self.enrollment_repo=enrollment_repo; self.audit_repo=audit_repo
        self.current_actor=current_actor

    def search_students(self, pno, keyword):
        actor, role = self.current_actor()
        prof = self.professor_repo.find_by_id(pno)
        if not prof:
            raise ValueError(f"교수 없음: {pno}")
        dept_name = prof.dept_name if prof else ""
        res = [StudentProfileDTO(s.sno, s.sname, s.gender, dept_name, s.year, s.phone)
               for s in self.student_repo.search_by_dept_and_keyword(dept_name, keyword)]
        _audit(self.audit_repo, actor_id=actor, role=role, action="prof.search_students",
               params={"keyword":keyword})
        return res

    def get_student_grade_report_by_professor(self, sno):
        actor, role = self.current_actor()
        details = []
        for e in self.enrollment_repo.find_by_student(sno):
            lec = self.lecture_repo.find_by_id(e.id.lec_no)
            if not lec or not e.grade:
                continue
            sc = grade_to_score(e.grade)
            details.append(GradeDetailDTO(lec.lec_no, lec.lec_name, lec.credit, e.grade, sc))

        _audit(self.audit_repo, actor_id=actor, role=role, action="prof.get_student_grade_report_by_professor",
               params={})
        return details

class InMemoryProfessorRepo(ProfessorRepository):
    def __init__(self): self.data = {}
    def find_by_id(self, pno):
        return self.data.get(pno)
    def save(self, prof):
        self.data[prof.pno] = prof
    def search_by_dept(self, dept_name):
        return [p for p in self.data.values() if p.dept_name == dept_name]

class InMemoryStudentRepo(StudentRepository):
    def __init__(self): self.data = {}
    def find_by_id(self, sno):
        return self.data.get(sno)
    def save(self, stu):
        self.data[stu.sno] = stu
    def search_by_dept_and_keyword(self, dept_name, keyword):
        kw = keyword.lower()
        return [s for s in self.data.values()
                if s.dept_name == dept_name and (kw in s.sno.lower() or kw in s.sname.lower())]
    def return_all_student_sno(self):
        return list(self.data.keys())

class InMemoryLectureRepo(LectureRepository):
    def __init__(self): self.data = {}
    def find_by_id(self, lec_no):
        return self.data.get(lec_no)
    def save(self, lec):
        self.data[lec.lec_no] = lec
    def find_lecture(self, *, year, semester, dept_name):
        res = [l for l in self.data.values() if l.year == year and l.semester == semester]
        return [l for l in res if (dept_name is None or l.dept_name == dept_name)]
    def find_by_professor(self, pno, *, year=None, semester=None):
        res = [l for l in self.data.values() if l.pno == pno]
        if year is not None:
            res = [l for l in res if l.year == year]
        if semester is not None:
            res = [l for l in res if l.semester == semester]
        return res
    def return_all_dep_names(self):
        deps = set()
        for l in self.data.values():
            deps.add(l.dept_name)
        return list(deps)

class InMemoryEnrollmentRepo(EnrollmentRepository):
    def __init__(self): self.data = {}
    def find_by_student(self, sno):
        return [e for (s, _), e in self.data.items() if s == sno]
    def find_by_lecture(self, lec_no):
        return [e for (_, l), e in self.data.items() if l == lec_no]
    def save(self, e):
        self.data[(e.id.sno, e.id.lec_no)] = e

class InMemoryStudentAccountRepo(StudentAccountRepository):
    def __init__(self): self.data = {}
    def find_by_id(self, sno):
        return self.data.get(sno)
    def save(self, acc): self.data[acc.sno] = acc

class InMemoryProfessorAccountRepo(ProfessorAccountRepository):
    def __init__(self): self.data = {}
    def find_by_id(self, pno):
        return self.data.get(pno)
    def save(self, acc): self.data[acc.pno] = acc

class InMemoryLoginLogRepo(LoginLogRepository):
    def __init__(self): self.data = {}
    def save(self, log): self.data[log.id] = log
    def search_by_userid_keyword(self, keyword):
        kw = keyword.lower()
        rows = [l for l in self.data.values() if kw in l.user_id.lower()]
        rows.sort(key=lambda x: x.last_login, reverse=True)
        return rows

class InMemoryAuditLogRepo(AuditLogRepository):
    def __init__(self): self.rows = []
    def save(self, log): self.rows.append(log)
    def search(self, *, actor_kw: str = "", limit: int = 200):
        ak = actor_kw.lower()
        res = []
        for r in reversed(self.rows):
            if ak and (r.actor_id or "").lower().find(ak) < 0: continue
            res.append(r)
            if len(res) >= limit: break
        return res

class AdminLogService:
    def __init__(self, login_log_repo):
        self.login_log_repo = login_log_repo
    def search_login_logs(self, keyword):
        return self.login_log_repo.search_by_userid_keyword(keyword)

def build_repos_memory():
    prof = InMemoryProfessorRepo()
    stu  = InMemoryStudentRepo()
    lec  = InMemoryLectureRepo()
    enr  = InMemoryEnrollmentRepo()
    stu_acc = InMemoryStudentAccountRepo()
    prof_acc = InMemoryProfessorAccountRepo()
    log_repo = InMemoryLoginLogRepo()
    audit_repo = InMemoryAuditLogRepo()
    return prof, stu, lec, enr, stu_acc, prof_acc, log_repo, audit_repo

def generate_lectures_from_syllabus(syllabus):
    lectures = []
    for item in syllabus:
        lec_no = item.get("SBJCT_CD_DCLSS")
        pno = item.get("EMPNO")
        lec_name = item.get("SBJCT_NM")
        credit = int(item.get("CRD", 0))
        dept_name = item.get("CRCLM_NM")
        year = 2025
        semester = 2
        lectures.append(Lecture(lec_no, pno, lec_name, credit, dept_name, year, semester))
    return lectures

def insert_dummy_data(
    prof_repo,
    stu_repo,
    lec_repo,
    enr_repo,
    stu_acc_repo,
    prof_acc_repo,
):
    prof_repo.save(Professor("F00001", "정철유", "인공지능공학전공"))
    prof_repo.save(Professor("F00002", "김영성", "컴퓨터공학전공"))

    stu_repo.save(Student("2025110001", "이형주", "M", "인공지능공학전공", 1, "010-1234-5678"))
    stu_repo.save(Student("2025110002", "정윤석", "M", "인공지능공학전공", 2, "010-1357-5555"))

    stu_acc_repo.save(StudentAccount("2025110001", sha256_hex("2025110001")))
    stu_acc_repo.save(StudentAccount("2025110002", sha256_hex("2025110002")))
    prof_acc_repo.save(ProfessorAccount("F00001", sha256_hex("F00001")))
    prof_acc_repo.save(ProfessorAccount("F00002", sha256_hex("F00002")))
    
    for lec in generate_lectures_from_syllabus(syllabus_2025_2):
        lec_repo.save(lec)
        
    enr_repo.save(Enrollment(EnrollmentId("2025110001", "GA2001-01"), grade="A+"))
    enr_repo.save(Enrollment(EnrollmentId("2025110001", "GA2003-01"), grade="A+"))
    enr_repo.save(Enrollment(EnrollmentId("2025110001", "LA0515-13"), grade="A"))
    enr_repo.save(Enrollment(EnrollmentId("2025110001", "LA0513-03"), grade="B+"))
    enr_repo.save(Enrollment(EnrollmentId("2025110001", "LA0365-09"), grade="A"))
    enr_repo.save(Enrollment(EnrollmentId("2025110001", "GA3044-01"), grade="A+"))
    enr_repo.save(Enrollment(EnrollmentId("2025110002", "GA2002-01"), grade="B+"))
    enr_repo.save(Enrollment(EnrollmentId("2025110002", "GA3001-01"), grade="A-"))

def run_demo():
    prof, stu, lec, enr, stu_acc, prof_acc, log_repo, audit_repo = build_repos_memory()

    print("더미 데이터 삽입")
    insert_dummy_data(prof, stu, lec, enr, stu_acc, prof_acc)

    auth = AuthService(stu_acc, prof_acc, log_repo, audit_repo)
    student_svc = StudentService(stu, lec, enr, audit_repo, current_actor=lambda: ("2025110001","student"))
    professor_svc = ProfessorService(prof, stu, lec, enr, audit_repo, current_actor=lambda: ("F00001","professor"))
    admin_log_svc = AdminLogService(log_repo)

    print("\n로그인(2025110001, 초기 비번 2025110001)")
    print(auth.login("2025110001", "2025110001"))

    print("\n학생 프로필(2025110001)")
    print(student_svc.get_profile("2025110001"))

    print("\n2025-2 개설 강좌(인공지능공학전공)")
    for l in student_svc.search_lecture(year=2025, semester=2, dept_name="인공지능공학전공"):
        print(l)

    print("\n성적표(2025110001)")
    print(student_svc.get_grade_report_by_student("2025110001"))

    print("\n교수 학생 검색(F00001, keyword='202511')")
    for sp in professor_svc.search_students("F00001", "202511"):
        print(sp)

    print("\n교수가 보는 학생 성적표(2025110002)")
    print(professor_svc.get_student_grade_report_by_professor("2025110002"))

    print("\n로그인 로그 조회(keyword='2025110001')")
    for log in admin_log_svc.search_login_logs("2025110001"):
        print(log)

if __name__ == "__main__":
    run_demo()
