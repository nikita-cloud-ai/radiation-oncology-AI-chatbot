    }

    tabs = st.tabs([f"{labels[k]} ({len(v)})" for k, v in grouped.items()])

    for tab, (key, faqs) in zip(tabs, grouped.items()):
        with tab:
            if not faqs:
                st.info(T["no_faq"])
                continue
            for question, answer in faqs:
                with st.expander(question):
                    st.markdown(answer)


def page_support():
    page_header("💙", U["nav"]["support"], C["support_sub"])

    tab_well, tab_daily, tab_care = st.tabs(
        [U["tab_wellbeing"], U["tab_daily"], U["tab_caregivers"]]
    )
    with tab_well:
        info_cards(C["support_cards"])
    with tab_daily:
        info_cards(C["daily_cards"])
    with tab_care:
        info_cards(C["caregiver_cards"])


def page_after():
    page_header("🌿", U["nav"]["after"], C["after_sub"])
    info_cards(C["after_cards"])
    hospital_box()
    contact_team_box()


def page_admin():
    if not st.session_state.get("admin_ok"):
        st.warning("Admin access required.")
        return

    st.markdown("### 🔐 Admin dashboard")

    feedback = read_csv_rows(FEEDBACK_FILE)
    unanswered = read_csv_rows(UNANSWERED_FILE)

    up = sum(1 for r in feedback if r.get("feedback") == "up")
    down = sum(1 for r in feedback if r.get("feedback") == "down")

    c1, c2, c3 = st.columns(3)
    c1.metric("👍 Helpful", up)
    c2.metric("👎 Not helpful", down)
    c3.metric("Unanswered questions", len(unanswered))

    tab_un, tab_down, tab_all = st.tabs(["Unanswered questions", "Not-helpful answers", "All feedback"])

    with tab_un:
        counts = Counter(
            r.get("question", "").strip().lower() for r in unanswered if r.get("question")
        )
        if counts:
            st.caption("Add answers for these to your FAQ file, most asked first.")
            st.dataframe(
                [{"question": q, "times asked": n} for q, n in counts.most_common(100)],
                use_container_width=True,
            )
            st.download_button(
                "⬇️ Download unanswered_log.csv",
                UNANSWERED_FILE.read_bytes(),
                file_name="unanswered_log.csv",
            )
        else:
            st.info("No unanswered questions logged yet.")

    with tab_down:
        rows = [r for r in feedback if r.get("feedback") == "down"]
        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No 👎 feedback yet.")

    with tab_all:
        if feedback:
            st.dataframe(feedback, use_container_width=True)
        else:
            st.info("No feedback yet.")

    if st.button("Log out of admin"):
        st.session_state.admin_ok = False
        st.session_state.page = "chat"
        st.rerun()


# ============================================================
# ROUTER
# ============================================================

render_nav()

PAGES = {
    "chat": page_chat,
    "journey": page_journey,
    "info": page_info,
    "effects": page_effects,
    "safety": page_safety,
    "diet": page_diet,
    "video": page_video,
    "faq": page_faq,
    "support": page_support,
    "after": page_after,
    "admin": page_admin,
}

PAGES.get(st.session_state.page, page_chat)()

footer_html = U["disclaimer"]
if REVIEW["by"]:
    footer_html += "<br>" + html.escape(
        U["reviewed"].format(by=REVIEW["by"], date=REVIEW["date"])
    )

st.markdown(
    f'<div class="footer-note">{footer_html}</div>',
    unsafe_allow_html=True,
)
