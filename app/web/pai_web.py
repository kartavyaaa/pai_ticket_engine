import uuid
import streamlit as st
import pandas as pd
import io
import requests

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="PAI Ticket Engine",
    layout="wide"
)

if "session_id" not in st.session_state:

    st.session_state.session_id = str(uuid.uuid4())

# -----------------------
# HEADER
# -----------------------
st.markdown("""
# 🧠 PAI Ticket Engine

### AI-Powered Incident Intelligence Platform

Ask natural language questions about incidents, outages, priorities, SLAs and operational trends.
""")

st.divider()

# -----------------------
# SESSION STATE
# -----------------------
if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "query_result" not in st.session_state:
    st.session_state.query_result = None

if "selected_cols" not in st.session_state:
    st.session_state.selected_cols = None

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

# -----------------------
# HELPERS
# -----------------------
def df_to_excel_bytes(df):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)
    return output.getvalue()

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.title("📂 Upload")

uploaded = st.sidebar.file_uploader(
    "Upload Ticket Excel/CSV",
    type=["xlsx", "xls", "csv"]
)

st.sidebar.markdown("---")

st.sidebar.markdown("## 🕘 Recent Queries")

if st.session_state.query_history:
    for q in st.session_state.query_history:
        st.sidebar.caption(f"• {q}")
else:
    st.sidebar.caption("No recent queries")

# -----------------------
# FILE UPLOAD
# -----------------------
if uploaded:

    if uploaded.name.endswith(("xlsx", "xls")):
        df = pd.read_excel(uploaded)
    else:
        df = pd.read_csv(uploaded)

    # normalize
    df.columns = [c.strip() for c in df.columns]

    # FIX STREAMLIT ARROW ERRORS
    df = df.astype(str)

    st.session_state.uploaded_df = df

    files = {
        "file": (
            uploaded.name,
            uploaded.getvalue(),
            uploaded.type
        )
    }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/upload",
            files=files
        )

        if response.status_code == 200:

            data = response.json()

            st.sidebar.success(
                f"✅ Loaded {data['rows']} rows"
            )

        else:
            st.sidebar.error("Backend upload failed")
            st.stop()

    except Exception as e:
        st.sidebar.error(f"API Connection Failed: {e}")
        st.stop()

else:
    st.info("Upload a ticket report to begin.")
    st.stop()

# -----------------------
# TABS
# -----------------------
tab1, tab2, tab3 = st.tabs([
    "🔎 Query",
    "🗂 Dataset",
    "📈 Analytics"
])

# =========================================================
# TAB 1 — QUERY
# =========================================================
with tab1:

    st.header("🔎 AI Query Assistant")

    st.markdown("#### ⚡ Quick Queries")

    quick_queries = [
        "show open tickets",
        "show high priority tickets",
        "tickets from last 7 days",
        "tickets from March to December 2024",
        "show medium priority tickets with connection issues",
        "show resolved tickets from slough",
        "tickets with SLA breach",
        "show low priority incidents"
    ]

    selected_q = st.selectbox(
        "Try an example",
        [""] + quick_queries
    )

    col1, col2 = st.columns([5, 1])

    with col1:

        nlp_query = st.text_input(
            "Enter your query",
            value=selected_q if selected_q else "",
            placeholder="e.g. show unresolved medium priority connection issues from 2024"
        )

    with col2:

        run_btn = st.button(
            "Run Query",
            width="stretch"
        )

    # -----------------------
    # RUN QUERY
    # -----------------------
    if run_btn:

        if nlp_query.strip():

            status_box = st.empty()

            status_box.info("🧠 Understanding query...")

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/query",
                    json={"query": nlp_query,
                          "session_id": st.session_state.session_id
                    }
                )

                status_box.info("🔍 Searching incidents...")

                if nlp_query not in st.session_state.query_history:
                    st.session_state.query_history.insert(0, nlp_query)

                st.session_state.query_history = st.session_state.query_history[:10]

                if response.status_code == 200:

                    backend_response = response.json()

                    # =====================================
                    # STORE SESSION ID
                    # =====================================
                    if "session_id" in backend_response:

                        st.session_state.session_id = backend_response["session_id"]

                    # =====================================
                    # STORE ACTUAL RESULT
                    # =====================================
                    st.session_state.query_result = backend_response["result"]

                    status_box.success("✅ Analysis complete")

                else:

                    st.session_state.query_result = {
                        "type": "message",
                        "data": "Backend query failed"
                    }

                    status_box.error("❌ Backend query failed")

            except Exception as e:

                st.session_state.query_result = {
                    "type": "message",
                    "data": f"API Error: {e}"
                }

                status_box.error("❌ API connection failed")

    result = st.session_state.query_result

    # -----------------------
    # EMPTY STATE
    # -----------------------
    if result is None:

        st.info("""
Try asking things like:

• show high priority tickets  
• unresolved incidents from november 2024  
• connection issues in slough  
• resolved tickets assigned to runcorn  
• medium priority tickets with SLA breach  
• show tickets where priority change is yes
""")

    # =====================================================
    # DATAFRAME RESULT
    # =====================================================
    elif result.get("type") == "dataframe":

        df_out = pd.DataFrame(result["data"]).astype(str)

        df_out.columns = [
            c.replace("_", " ").title()
            for c in df_out.columns
        ]

        # -----------------------
        # AI INSIGHTS
        # -----------------------
        st.markdown("## 🧠 AI Insights")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("Tickets Found", len(df_out))

        with c2:

            high_count = df_out.astype(str).apply(
                lambda x: x.str.contains("high", case=False)
            ).any(axis=1).sum()

            st.metric("High Priority", high_count)

        with c3:

            resolved_count = df_out.astype(str).apply(
                lambda x: x.str.contains("resolved", case=False)
            ).any(axis=1).sum()

            st.metric("Resolved", resolved_count)

        with c4:

            st.metric(
                "Columns",
                len(df_out.columns)
            )

        st.markdown("---")

        # -----------------------
        # COLUMN SELECTION
        # -----------------------
        if st.session_state.selected_cols is None:
            st.session_state.selected_cols = df_out.columns.tolist()

        selected_cols = st.multiselect(
            "Select columns",
            df_out.columns,
            default=st.session_state.selected_cols
        )

        st.session_state.selected_cols = selected_cols

        display_df = df_out[selected_cols]

        # -----------------------
        # DOWNLOAD
        # -----------------------
        st.download_button(
            "⬇️ Download Excel",
            df_to_excel_bytes(display_df),
            "results.xlsx"
        )

        st.markdown("### 📊 Results")

        # -----------------------
        # PREMIUM TABLE
        # -----------------------
        st.data_editor(
            display_df,
            width="stretch",
            height=550,
            disabled=True
        )

    # =====================================================
    # FALLBACK RESULT
    # =====================================================
    elif result.get("type") == "fallback":

        st.warning(result.get("message"))

        if "debug" in result:

            st.markdown("### 🔍 Match Breakdown")

            for k, v in result["debug"].items():
                st.write(f"{k} → {v} matches")

        df_out = pd.DataFrame(
            result["results"]
        ).astype(str)

        df_out.columns = [
            c.replace("_", " ").title()
            for c in df_out.columns
        ]

        st.markdown("### 📊 Closest Matches")

        st.data_editor(
            df_out,
            width="stretch",
            height=550,
            disabled=True
        )

    # =====================================================
    # MESSAGE RESULT
    # =====================================================
    elif result.get("type") == "message":

        st.info(result["data"])

# =========================================================
# TAB 2 — DATASET
# =========================================================
with tab2:

    st.header("🗂 Uploaded Dataset")

    if st.session_state.uploaded_df is not None:

        st.metric(
            "Total Records",
            len(st.session_state.uploaded_df)
        )

        st.data_editor(
            st.session_state.uploaded_df.head(200),
            width="stretch",
            height=600,
            disabled=True
        )

# =========================================================
# TAB 3 — ANALYTICS
# =========================================================
with tab3:

    st.header("📈 Incident Analytics Dashboard")

    df = st.session_state.uploaded_df.copy()

    # -----------------------
    # DATE CONVERSION
    # -----------------------
    for col in df.columns:

        try:
            df[col] = pd.to_datetime(df[col])
        except:
            continue

    # -----------------------
    # FIND DATE COLUMN
    # -----------------------
    date_cols = df.select_dtypes(include=["datetime"]).columns

    if len(date_cols) > 0:

        date_col = date_cols[0]

        # -----------------------
        # DAILY TREND
        # -----------------------
        st.subheader("📅 Daily Incident Trend")

        daily = df.groupby(
            df[date_col].dt.date
        ).size()

        st.line_chart(daily)

        # -----------------------
        # MONTHLY TREND
        # -----------------------
        st.subheader("📈 Monthly Incident Trend")

        monthly = df.groupby(
            df[date_col].dt.to_period("M")
        ).size()

        monthly.index = monthly.index.astype(str)

        st.bar_chart(monthly)

    # -----------------------
    # PRIORITY ANALYTICS
    # -----------------------
    priority_col = None

    for c in df.columns:
        if "priority" in c.lower():
            priority_col = c
            break

    if priority_col:

        st.subheader("🚨 Incidents by Priority")

        priority_counts = df[priority_col].value_counts()

        st.bar_chart(priority_counts)

    # -----------------------
    # STATUS ANALYTICS
    # -----------------------
    status_col = None

    for c in df.columns:
        if "status" in c.lower():
            status_col = c
            break

    if status_col:

        st.subheader("📌 Incidents by Status")

        status_counts = df[status_col].value_counts()

        st.bar_chart(status_counts)