import streamlit as st
import json

from university_ddd import (
    AuthService, StudentService, ProfessorService, AdminLogService,
    AuditLogRepository,
    build_repos_memory, insert_dummy_data,
)

def current_actor():
    return (st.session_state.get("user_id"), st.session_state.get("role"))

@st.cache_resource
def get_repos():
    prof, stu, lec, enr, stu_acc, prof_acc, log_repo, audit_repo = build_repos_memory()
    insert_dummy_data(prof, stu, lec, enr, stu_acc, prof_acc)
    return dict(
        prof=prof, stu=stu, lec=lec, enr=enr,
        stu_acc=stu_acc, prof_acc=prof_acc, login_log=log_repo, audit=audit_repo
    )

def get_services(repos):
    auth = AuthService(repos["stu_acc"], repos["prof_acc"], repos["login_log"], repos["audit"])
    student_svc = StudentService(repos["stu"], repos["lec"], repos["enr"], repos["audit"], current_actor)
    professor_svc = ProfessorService(repos["prof"], repos["stu"], repos["lec"], repos["enr"], repos["audit"], current_actor)
    admin_log_svc = AdminLogService(repos["login_log"])
    return dict(auth=auth, student=student_svc, professor=professor_svc, admin_log=admin_log_svc, audit=repos["audit"])

def init_state():
    st.session_state.setdefault("Cookie", None)
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("role", None)

def require_login():
    if not st.session_state.Cookie:
        st.warning("먼저 로그인하세요.")
        st.stop()

def show_login_box(auth: AuthService):
    with st.sidebar:
        if st.session_state.Cookie:
            st.success(f"안녕하세요 {st.session_state.user_id} ({st.session_state.role})")
            if st.button("로그아웃"):
                st.session_state.Cookie = None
                st.session_state.role = None
                st.session_state.user_id = None
                st.info("로그아웃 되었습니다.")
                st.rerun()
            return
        st.header("로그인")
        uid = st.text_input("ID", value="2025110001")
        pw = st.text_input("비밀번호", type="password", value="2025110001")
        c1, c2 = st.columns(2)
        if c1.button("로그인"):
            info = auth.login(uid, pw)
            if info == False:
                st.error("로그인 실패")
                return
            st.session_state.Cookie = info["Cookie"]
            st.session_state.role = info["role"]
            st.session_state.user_id = uid
            st.success(f"로그인 성공: {uid} ({info['role']})")
            st.rerun()

def show_student_pages(student: StudentService):
    tabs = st.tabs(["프로필", "개설 강좌 조회", "성적표"])
    with tabs[0]:
        require_login()
        sno = st.session_state.user_id
        st.subheader("내 프로필")
        if st.button("조회"):
            p = student.get_profile(sno)
            st.json({
                "sno": p.sno, "sname": p.sname, "gender": p.gender,
                "deptName": p.dept_name, "year": p.year, "phone": p.phone
            })

    with tabs[1]:
        year = st.number_input("연도", min_value=2000, max_value=2100, value=2025, step=1)
        semester = st.selectbox("학기", [1, 2], index=1)
        dept_names = student.lecture_repo.return_all_dep_names()
        dept_name = st.selectbox("학과 이름", [""] + sorted(dept_names), index=0)
        if st.button("조회", key="open_lectures"):
            lectures = student.search_lecture(year=year, semester=semester, dept_name=dept_name or None)
            if not lectures:
                st.info("해당 조건의 개설 강좌가 없습니다.")
            else:
                st.table([{
                    "lec_no": l.lec_no, "lec_name": l.lec_name,
                    "credit": l.credit, "dept": l.dept_name
                } for l in lectures])

    with tabs[2]:
        require_login()
        sno = st.session_state.user_id
        if st.button("내 성적표 조회"):
            details = student.get_grade_report_by_student(sno)
            st.table([{"lec_no": d.lec_no, "lec_name": d.lec_name, "credit": d.credit, "grade": d.grade, "score": f"{d.score:.1f}"}
                    for d in details])

def show_professor_pages(prof: ProfessorService):
    tabs = st.tabs(["학생 검색", "학생 성적표"])
    pno = st.session_state.user_id

    with tabs[0]:
        kw = st.text_input("키워드(학번/이름 일부)")
        if st.button("검색"):
            res = prof.search_students(pno, kw)
            if not res:
                st.info("검색 결과가 없습니다.")
            else:
                st.table([{"sno": s.sno, "sname": s.sname, "gender": s.gender,
                            "dept": s.dept_name, "year": s.year, "phone": s.phone} for s in res])

    with tabs[1]:
        student_snos = prof.student_repo.return_all_student_sno()
        target_sno = st.selectbox("학생 학번", sorted(student_snos), index=0)
        if st.button("성적표 조회"):
            details = prof.get_student_grade_report_by_professor(target_sno)
            st.table([{"lec_no": d.lec_no, "lec_name": d.lec_name, "credit": d.credit, "grade": d.grade, "score": f"{d.score:.1f}"}
                        for d in details])

def show_admin_log_page(admin_log: AdminLogService, audit_repo: AuditLogRepository):
    st.subheader("시스템 로그인 로그")
    kw = st.text_input("로그인 로그 검색 (user_id 일부)", value="2025110001", key="loginlog_kw")
    if st.button("로그인 로그 조회"):
        logs = admin_log.search_login_logs(kw)
        if not logs:
            st.info("로그가 없습니다.")
        else:
            st.table([{
                "id": l.id, "user_id": l.user_id, "role": l.role,
                "last_login": l.last_login.strftime("%Y-%m-%d %H:%M:%S") if l.last_login else ""
            } for l in logs])

    st.divider()
    st.subheader("접근 Log")

    col1, col3 = st.columns([1.2, 1])
    actor_kw = col1.text_input("사용자 검색(포함일치)", value=st.session_state.get("user_id") or "")
    limit = col3.number_input("최대 건수", min_value=10, max_value=2000, value=200, step=10)

    if st.button("접근 로그 조회"):
        rows = audit_repo.search(actor_kw=actor_kw, limit=int(limit))
        if not rows:
            st.info("접근 로그가 없습니다.")
            return
        
        table = []
        for r in rows:
            params = json.loads(r.params_json)
            table.append({
                "시간": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "사용자": r.actor_id,
                "역할": r.role,
                "액션": r.action,
                "파라미터": json.dumps(params, ensure_ascii=False),
            })
        st.dataframe(table, width='stretch')

def main():
    st.set_page_config(page_title="대학교 통합정보시스템 클론", layout="wide")
    init_state()
    repos = get_repos()
    svcs  = get_services(repos)
    auth = svcs["auth"]
    student_svc = svcs["student"]
    professor_svc = svcs["professor"]
    admin_log_svc = svcs["admin_log"]
    audit_repo = svcs["audit"]

    st.title("대학교 통합정보시스템 클론")
    show_login_box(auth)

    st.sidebar.divider()
    page = st.sidebar.radio("메뉴", ["Home", "학생 기능", "교수 기능", "로그(관리)"])
    st.sidebar.info(f"세션: {st.session_state.user_id or '미로그인'} / {st.session_state.role or '-'}")

    if page == "Home":
        pass
    elif page == "학생 기능":
        require_login()
        if st.session_state.role != "student":
            st.error("학생 계정으로 로그인해야 합니다.")
        else:
            show_student_pages(student_svc)
    elif page == "교수 기능":
        require_login()
        if st.session_state.role != "professor":
            st.error("교수 계정으로 로그인해야 합니다.")
        else:
            show_professor_pages(professor_svc)
    elif page == "로그(관리)":
        show_admin_log_page(admin_log_svc, audit_repo)

if __name__ == "__main__":
    params = st.query_params
    waonawklgnwo = params.get("waonawklgnwo", ["None"])
    if waonawklgnwo == "abvwnoewinmahwerotknwaoea":
        main()
    else:
        pass