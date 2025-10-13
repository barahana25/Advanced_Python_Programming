import streamlit as st
import sqlite3
import pandas as pd
import os
from bs4 import BeautifulSoup
from datetime import datetime

DB_PATH = "./Univ/LMS.db"
FILES_BASE_PATH = "./Univ/1-2"

def format_datetime(dt_str):
    if dt_str is None or dt_str == "":
        return "N/A"
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")

def read_table(table_name, limit=None):
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    con = sqlite3.connect(DB_PATH)
    try:
        query = f"SELECT * FROM {table_name} ORDER BY id DESC"
        if limit:
            query += f" LIMIT {limit}"
        df = pd.read_sql_query(query, con)
    except Exception as e:
        st.error(f"DB 읽기 오류: {e}")
        df = pd.DataFrame()
    finally:
        con.close()
    return df

def main():
    st.set_page_config(page_title="LMS Dashboard", layout="wide")
    st.title("LMS 모니터링 대시보드")
    st.markdown("---")

    ann_df = read_table("announcement", limit=200)
    asg_df = read_table("assignment", limit=200)
    lec_df = read_table("lecture", limit=500)

    # 전체 course_name 목록 추출
    courses = set()
    if not ann_df.empty:
        courses.update(ann_df["course_name"].unique())
    if not asg_df.empty:
        courses.update(asg_df["course_name"].unique())
    if not lec_df.empty:
        courses.update(lec_df["course_name"].unique())

    if not courses:
        st.info("데이터 없음")
    else:
        course_tabs = st.tabs(sorted(courses))

        for course_name, course_tab in zip(sorted(courses), course_tabs):
            with course_tab:
                st.header(f"{course_name}")

                sub_tab_ann, sub_tab_asg, sub_tab_lec = st.tabs(["공지 사항", "과제", "강의 파일"])

                with sub_tab_ann:
                    course_ann = ann_df[ann_df["course_name"] == course_name] if not ann_df.empty else pd.DataFrame()
                    if course_ann.empty:
                        st.info("공지 데이터 없음")
                    else:
                        h1, h2, h3 = st.columns([4,3,1])
                        with h1:
                            st.markdown("**제목**")
                        with h2:
                            st.markdown("**게시일**")
                        with h3:
                            st.markdown("**보기 버튼**")
                        for i, row in course_ann.iterrows():
                            col1, col2, col3 = st.columns([4,3,1])
                            with col1:
                                st.write(row["announcement_title"])
                            with col2:
                                st.write(format_datetime(row["posted_at"]))
                            with col3:
                                show = st.button("보기", key=f"ann_{row['id']}")

                            if show:
                                st.markdown("---")
                                desc = row.get("announcement_message") or ""
                                desc_text = BeautifulSoup(desc, "html.parser").get_text(separator="\n").strip()
                                st.subheader(row["announcement_title"])
                                st.write(desc_text.replace("\n", "  \n") or "본문 없음")
                                st.markdown("---")

                with sub_tab_asg:
                    course_asg = asg_df[asg_df["course_name"] == course_name] if not asg_df.empty else pd.DataFrame()
                    if course_asg.empty:
                        st.info("과제 데이터 없음")
                    else:
                        h1, h2, h3, h4 = st.columns([4,2,2,1])
                        with h1:
                            st.markdown("**과제명**")
                        with h2:
                            st.markdown("**시작일**")
                        with h3:
                            st.markdown("**마감일**")
                        with h4:
                            st.markdown("**보기 버튼**")
                        for i, row in course_asg.iterrows():
                            col1, col2, col3, col4 = st.columns([4,2,2,1])
                            with col1:
                                st.write(row["assignment_name"])
                            with col2:
                                st.write(format_datetime(row["created_at"]))
                            with col3:
                                st.write(format_datetime(row["end_date"]))
                            with col4:
                                show = st.button("보기", key=f"asg_{row['id']}")

                            if show:
                                st.markdown("---")
                                desc = row.get("description") or ""
                                desc_text = BeautifulSoup(desc, "html.parser").get_text(separator="\n").strip()
                                st.subheader(row["assignment_name"])
                                st.write(desc_text.replace("\n", "  \n") or "본문 없음")
                                st.markdown("---")

                # 강의 파일
                with sub_tab_lec:
                    course_lec = lec_df[lec_df["course_name"] == course_name] if not lec_df.empty else pd.DataFrame()
                    if course_lec.empty:
                        st.info("강의자료 데이터 없음")
                    else:
                        h1, h2, h3 = st.columns([2,4,1])
                        with h1:
                            st.markdown("**생성일**")
                        with h2:
                            st.markdown("**파일 이름**")
                        with h3:
                            st.markdown("**다운로드 버튼**")
                        course_lec = course_lec.sort_values(by="created_at", ascending=False)
                        for i, row in course_lec.iterrows():
                            col1, col2, col3 = st.columns([2,4,1])
                            with col1:
                                st.write(format_datetime(row["created_at"]))
                            with col2:
                                st.write(row["file_name"])
                            with col3:
                                fname = row.get("file_name")
                                possible_paths = [
                                    os.path.join(FILES_BASE_PATH, course_name, "강의자료", fname),
                                    os.path.join(FILES_BASE_PATH, course_name, "기타파일", fname),
                                    os.path.join(FILES_BASE_PATH, course_name, fname),
                                ]
                                found = None
                                for p in possible_paths:
                                    if os.path.exists(p):
                                        found = p
                                        break
                                if found:
                                    with open(found, "rb") as f:
                                        st.download_button("다운로드", data=f, file_name=fname, key=f"lec_{row['id']}")
                                else:
                                    st.write("파일 없음")


if __name__ == "__main__":
    params = st.query_params
    baiwowoefn = params.get("baiwowoefn", ["None"])
    if baiwowoefn == "owpbmawevpnawergiph":
        main()
    else:
        pass