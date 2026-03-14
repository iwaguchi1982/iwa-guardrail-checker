import streamlit as st
import pandas as pd
import io
import plotly.express as px
from src.guardrails import evaluate_guardrails

st.set_page_config(
    page_title="iwa-guardrail-checker",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #f8f9fa;
}
.stAlert {
    border-radius: 10px;
}
.status-card {
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 24px;
    border-left: 8px solid #ccc;
}
.status-ok {
    background-color: #e7f4e9;
    border-left-color: #2e7d32;
    color: #1b5e20;
}
.status-caution {
    background-color: #fff8e1;
    border-left-color: #fbc02d;
    color: #f57f17;
}
.status-danger {
    background-color: #ffebee;
    border-left-color: #c62828;
    color: #b71c1c;
}
.metric-container {
    background: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)


def detect_delimiter(text: str) -> str:
    first_line = text.splitlines()[0] if text.splitlines() else ""
    return "\t" if "\t" in first_line else ","


def auto_detect_columns(df: pd.DataFrame) -> dict:
    all_cols = [str(c).lower() for c in df.columns]
    mapping = {
        "patient_id": ["patient_id", "id", "patient", "case_id"],
        "time": ["time", "duration", "followup", "follow_up", "os_months", "pfs_months"],
        "event": ["event", "status", "os_status", "pfs_status", "vital_status"],
        "group": ["group", "arm", "treatment", "cohort", "stratification"]
    }
    
    defaults = {}
    for key, patterns in mapping.items():
        match = None
        for col in df.columns:
            if str(col).lower() in patterns:
                match = col
                break
        defaults[key] = match
    return defaults


def main():
    st.title("🛡️ iwa-guardrail-checker")
    st.markdown("##### Preflight checker for survival-oriented bioinformatics datasets")

    st.sidebar.header("📁 Data Input")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Clinical Table (CSV/TSV)",
        type=["csv", "tsv", "txt"]
    )

    if uploaded_file is None:
        st.info("Please upload a clinical data file to get started.")
        st.write("#### Expected CSV/TSV Format")
        st.code(
            """patient_id,duration,event,group,age,sex
P001,45.2,1,Treatment A,65,M
P002,12.1,0,Control,72,F"""
        )
        return

    try:
        raw_bytes = uploaded_file.getvalue()
        file_text = raw_bytes.decode("utf-8")
        sep = detect_delimiter(file_text)

        st.sidebar.info(f"Detected Delimiter: **{'Tab' if sep == '\\t' else 'Comma'}**")

        df = pd.read_csv(io.BytesIO(raw_bytes), sep=sep)

    except UnicodeDecodeError:
        st.error("Failed to decode file as UTF-8. Please save the file as UTF-8 and try again.")
        return
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return

    st.sidebar.markdown("---")
    st.sidebar.header("🗺️ Column Mapping")

    all_cols = df.columns.tolist()
    auto_defaults = auto_detect_columns(df)

    mapping = {}
    
    # helper for selectbox index
    def get_idx(col_name):
        default = auto_defaults.get(col_name)
        if default in all_cols:
            return all_cols.index(default) + 1
        return 0

    mapping["patient_id"] = st.sidebar.selectbox("Patient ID", [None] + all_cols, index=get_idx("patient_id"))
    mapping["time"] = st.sidebar.selectbox("Duration / Follow-up Time", [None] + all_cols, index=get_idx("time"))
    mapping["event"] = st.sidebar.selectbox("Event (0/1)", [None] + all_cols, index=get_idx("event"))
    mapping["group"] = st.sidebar.selectbox("Main Group / Factor", [None] + all_cols, index=get_idx("group"))

    selected_required = [v for v in mapping.values() if v is not None]
    covariate_candidates = [c for c in all_cols if c not in selected_required]
    covariates = st.sidebar.multiselect("Optional Covariates (for Cox)", covariate_candidates)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", df.shape[0])
    with col2:
        st.metric("Total Columns", df.shape[1])
    with col3:
        st.metric("Detected Format", "TSV" if sep == "\t" else "CSV")

    st.write("### 🔍 Data Preview")
    st.dataframe(df.head(5), use_container_width=True)

    st.markdown("---")
    st.write("### 🚦 Guardrail Status")

    if any(v is None for v in mapping.values()):
        st.warning("Please map all required columns in the sidebar to run guardrail checks.")
    else:
        results = evaluate_guardrails(df, mapping, covariates)
        status = results["status"]
        summary = results["summary"]

        # 1. Status Card
        status_class = f"status-{status.lower()}"
        st.markdown(f"""
            <div class="status-card {status_class}">
                <h2 style="margin:0;">{status}</h2>
                <p style="margin:5px 0 0 0;">{ "Dataset passed all core preflight checks." if status == "OK" else "Review the reasons below before proceeding with analysis." }</p>
            </div>
        """, unsafe_allow_html=True)

        if results["danger_reasons"]:
            with st.expander("❌ Danger Reasons", expanded=True):
                for reason in results["danger_reasons"]:
                    st.write(f"- {reason}")

        if results["caution_reasons"]:
            with st.expander("⚠️ Caution Reasons", expanded=status == "CAUTION"):
                for reason in results["caution_reasons"]:
                    st.write(f"- {reason}")

        if results["recommendations"]:
            st.write("#### 💡 Recommendations")
            for rec in results["recommendations"]:
                st.info(rec)

        st.markdown("---")
        st.write("#### 📊 Basic Summary")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Unique Patients", summary["unique_patients"])
        with col2:
            st.metric("Duplicate Patient IDs", summary["duplicate_patient_ids"])
        with col3:
            st.metric("Total Events (1)", summary["total_events"])

        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("Missing Time", summary["missing_time"])
        with col5:
            st.metric("Missing Event", summary["missing_event"])
        with col6:
            st.metric("Missing Group", summary["missing_group"])

        st.write(f"**Detected event values**: `{summary['event_unique_values']}` | **Event Rate**: `{summary['event_rate']:.2%}`")

        st.markdown("---")
        col_g1, col_g2 = st.columns([1, 1])
        with col_g1:
            st.write("#### 👥 Group Sizes")
            group_df = pd.DataFrame({
                "group": list(summary["group_counts"].keys()),
                "n": list(summary["group_counts"].values()),
                "events": [summary["events_by_group"].get(g, 0) for g in summary["group_counts"].keys()]
            })
            st.dataframe(group_df, use_container_width=True)
        
        with col_g2:
            st.write("#### 📈 Group Distribution")
            plot_height = max(300, 40 * len(group_df))
            fig = px.bar(group_df, x="n", y="group", orientation='h', 
                         title="Sample Size per Group",
                         labels={"n": "Number of Samples", "group": "Group"},
                         color_discrete_sequence=['#4285F4'])
            fig.update_layout(height=plot_height, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.write("#### 🗺️ Current Mapping")
        
        # Human friendly mapping
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f"""
            - **Patient ID**: `{mapping['patient_id']}`
            - **Time**: `{mapping['time']}`
            - **Event**: `{mapping['event']}`
            - **Group**: `{mapping['group']}`
            """)
        with m_col2:
            st.markdown(f"- **Covariates**: `{', '.join(covariates) if covariates else 'None'}`")
            if covariates:
                retention = results["retention"]
                st.write(f"- **Estimated Retention**: `{retention['retention_rate']:.1%}` ({retention['complete_case_rows']}/{df.shape[0]} rows)")

        with st.expander("View Raw Mapping JSON"):
            st.json({
                "required": mapping,
                "covariates": covariates
            })


if __name__ == "__main__":
    main()