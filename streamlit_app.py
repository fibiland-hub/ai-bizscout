"""AI BizScout operator console. No automatic email is sent by this app."""
import csv
import io
import streamlit as st
import pandas as pd
from app.core import make_email, parse_csv, ready_to_send, relevance, validate_notice
from app.collector import collect_rss

st.set_page_config(page_title="AI BizScout", page_icon="🌊", layout="wide")
st.title("🌊 AI BizScout")
st.caption("기업 맞춤형 공고 검토 콘솔 | 안전 우선 프로토타입 · 자동 이메일 발송 비활성화")
st.warning("실제 공고 자동 수집·AI 판정·Gmail 발송은 아직 운영 연결 전입니다. 출처와 날짜 검증을 수동 확인하기 전에는 발송하지 않습니다.")
with st.sidebar:
    st.header("기업 설정")
    company = st.text_input("기업명 (이 브라우저 세션에서만 사용)", value="")
    interests = st.text_input("관심 키워드 (쉼표 구분)", value="해양,AI,수산,연구개발")
    st.info("비밀번호·API 키·민감한 기업정보는 입력하지 마세요.")
    st.caption("데이터는 이 앱의 세션에만 유지되며, 서버 저장 기능은 아직 없습니다.")

tab1, tab2, tab3 = st.tabs(["📋 공고 검토", "🔎 RSS 수집", "✉️ 이메일 초안"])
with tab1:
    st.subheader("공고 데이터 업로드")
    st.caption("CSV 필수 열: title, agency, source_url, start_date, end_date. 검증 플래그: source_verified, dates_verified, attachments_reviewed.")
    uploaded = st.file_uploader("공고 CSV 업로드", type=["csv"])
    if uploaded is not None:
        try:
            st.session_state["notices"] = parse_csv(uploaded.getvalue())
            st.success(f"{len(st.session_state['notices'])}건 불러왔습니다.")
        except (ValueError, UnicodeDecodeError, csv.Error) as exc:
            st.error(str(exc))
    notices = st.session_state.get("notices", [])
    if notices:
        records = []
        for n in notices:
            issues = validate_notice(n)
            records.append({
                "공고명": n.get("title", ""), "기관": n.get("agency", ""),
                "마감일": n.get("end_date", ""), "적합도(참고)": relevance(n, interests),
                "상태": "검증 완료" if not issues else "검증 보류",
                "문제": " / ".join(issues),
                "원문": n.get("source_url", ""),
            })
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        st.caption("적합도는 키워드 일치율이며 신청 자격을 뜻하지 않습니다.")
    else:
        st.info("CSV를 업로드하거나 RSS에서 공고를 가져오세요.")
with tab2:
    st.subheader("공식 RSS 주소 수집")
    st.caption("공식 기관에서 제공하는 RSS 주소만 입력하세요. 수집 결과는 검증 보류 상태로 저장됩니다.")
    rss_url = st.text_input("공식 RSS HTTPS 주소", placeholder="https://기관.example/rss")
    if st.button("RSS 수집", type="primary"):
        try:
            fetched = collect_rss(rss_url)
            existing = st.session_state.get("notices", [])
            urls = {n.get("source_url") for n in existing}
            new = [n for n in fetched if n["source_url"] not in urls]
            st.session_state["notices"] = existing + new
            st.success(f"신규 {len(new)}건 수집. 날짜·첨부파일 검증 전이므로 발송 불가.")
        except Exception as exc:
            st.error("수집 실패: " + str(exc))
with tab3:
    st.subheader("검증 완료 공고의 이메일 초안")
    notices = st.session_state.get("notices", [])
    approved = [n for n in notices if ready_to_send(n)]
    if not approved:
        st.info("검증 완료 공고가 없습니다. 공식 출처·기간·첨부파일 확인 후 검증 플래그가 포함된 CSV를 업로드하세요.")
    else:
        options = {f"{n['title']} ({n['id']})": n for n in approved}
        selected = st.selectbox("공고 선택", list(options))
        subject, body = make_email(options[selected])
        st.text_input("메일 제목", value=subject)
        st.text_area("메일 본문 (복사해 검토)", value=body, height=320)
        st.caption("이 화면은 이메일을 발송하지 않습니다. Gmail API 인증과 발송 이력 저장 기능은 별도 구현이 필요합니다.")
