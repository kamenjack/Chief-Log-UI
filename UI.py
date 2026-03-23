import streamlit as st
import pandas as pd
import textwrap

from dict import getDeptName, getSystemName, getSymptomName, getserviceName

st.set_page_config(page_title="Train Delay Viewer", layout="wide")

st.markdown("""
<style>
input[disabled], textarea[disabled] {
    color: black !important;
    -webkit-text-fill-color: black !important;
    background-color: white !important;
    opacity: 1 !important;
}

div[data-baseweb="input"] {
    background-color: white !important;
}


label {
    color: black !important;
    font-weight: 600;
}

/* Delay code row */
.delay-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 8px 0 20px 0;
    flex-wrap: nowrap;
}

.delay-label {
    font-size: 18px;
    font-weight: 600;
    margin-right: 10px;
    white-space: nowrap;
}

.delay-box {
    width: 48px;
    height: 38px;
    border: 1px solid #bdbdbd;
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: white;
    font-size: 20px;
    color: black;
    box-sizing: border-box;
}

.delay-box-wide {
    width: 60px;
    height: 38px;
    border: 1px solid #bdbdbd;
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: white;
    font-size: 20px;
    color: black;
    box-sizing: border-box;
}

.delay-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.delay-note {
    margin-top: 10px;
    width: 100%;
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    color: #2f3340;
    white-space: nowrap;
}

</style>
""", unsafe_allow_html=True)

st.title("MNR Delay Report with LLM")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
chief_log_file="ChiefLog 2023-01-01 to 2023-12-31.csv"
chiefLogDataFrame = pd.read_csv(chief_log_file)
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    date_column = "RUN_DATE"
    train_column = "TRAIN_NAME"
    location_column = "LOCATION_NAME"
    performance_column = "LATENESS"
    display_logid_column = "DISPLAY_LOG_ID"

    code_columns = [
        "DEPT_CODE",
        "SYSTEM_CODE",
        "SYMPTOM_CODE"
        "SERVICE_TYPE_CODE"
    ]

    if date_column not in df.columns:
        st.error(f"Column '{date_column}' not found.")
        st.stop()

    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    df = df.dropna(subset=[date_column])

    if df.empty:
        st.warning("No valid dates found in the uploaded CSV.")
        st.stop()

    selected_date = st.date_input(
        "Run Date",
        value=df[date_column].dt.date.min(),
        min_value=df[date_column].dt.date.min(),
        max_value=df[date_column].dt.date.max()
    )

    daily_df = df[df[date_column].dt.date == selected_date].copy()

    chiefLogDateColumn = "Log Date"
    chiefLogDataFrame[chiefLogDateColumn] = pd.to_datetime(chiefLogDataFrame[chiefLogDateColumn], errors="coerce")

    chiefLogDailyDf = chiefLogDataFrame[chiefLogDataFrame[chiefLogDateColumn].dt.date == selected_date].copy()
    merged_comment_df = (
        chiefLogDailyDf.groupby("DisplayLogId", sort=False)["Comments"]
        .apply(
            lambda commentSeries: "\n".join(
                str(singleComment).strip()
                for singleComment in commentSeries
                if pd.notna(singleComment) and str(singleComment).strip() != ""
            )
        )
        .reset_index()
    )


    if daily_df.empty:
        st.info("No records found for the selected date.")
        st.stop()

    display_columns = [
        col for col in [train_column, location_column, performance_column]
        if col in daily_df.columns
    ]
    log_id_columns=[col for col in["DisplayLogId","Comments"] if col in chiefLogDailyDf.columns]

    st.markdown("### Daily Records")

    event = st.dataframe(
        daily_df[display_columns],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="daily_records_table",
    )

    st.dataframe(
        merged_comment_df,
        use_container_width=True,
        hide_index=True
    )

    selected_row = None
    selected_rows = event.selection.rows

    if selected_rows:
        row_position = selected_rows[0]
        selected_row = daily_df.iloc[row_position]
        selected_train=str(selected_row.get("TRAIN_NAME","")).strip()

    st.markdown("### Train Details")

    if selected_row is None:
        st.info("Click a train row in Daily Records.")
    else:
        service_code=str(selected_row.get("SERVICE_TYPE_CODE","")).strip()
        dept_code = str(selected_row.get("DEPT_CODE", "")).strip()
        system_code = str(selected_row.get("SYSTEM_CODE", "")).strip()
        symptom_code = str(selected_row.get("SYMPTOM_CODE", "")).strip()
        service_name=getserviceName(service_code)
        dept_name=getDeptName(dept_code)
        system_name=getSystemName(dept_code,system_code)
        symptom_name=getSymptomName(dept_code,system_code,symptom_code)

        def safe_display(value):
            if value == "nan":
                return ""
            return value





        html = textwrap.dedent(f"""
            <div class="delay-row">
                <div class="delay-label">Delay Code:</div>
                  <div class="delay-item">
                    <div class="delay-box">{safe_display(service_code)}</div>
                    <div class="delay-note">{service_name}</div>
                </div>
                <div class="delay-item">
                    <div class="delay-box">{safe_display(dept_code)}</div>
                    <div class="delay-note">{dept_name}</div>
                </div>
                <div class="delay-item">
                    <div class="delay-box">{safe_display(system_code)}</div>
                    <div class="delay-note">{system_name}</div>
                </div>
                <div class="delay-item">
                    <div class="delay-box delay-box-wide">{safe_display(symptom_code)}</div>
                    <div class="delay-note">{symptom_name}</div>
                </div>
            </div>
        """).strip()
        st.markdown(html, unsafe_allow_html=True)

        with st.form("delay_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                value1 = st.text_input("SERVICE_TYPE_CODE", key="SERVICE_TYPE_CODE", label_visibility="collapsed")
            with col2:
                value2 = st.text_input("DEPT_CODE", key="DEPT_CODE", label_visibility="collapsed")
            with col3:
                value3 = st.text_input("SYSTEM_CODE", key="SYSTEM_CODE", label_visibility="collapsed")
            with col4:
                value4 = st.text_input("SYMPTOM_CODE", key="SYMPTOM_CODE",
                                       label_visibility="collapsed")
            submitted = st.form_submit_button("Submit")

        value1_name = getserviceName(value1)
        value2_name = getDeptName(value2)
        value3_name = getSystemName(value2, value3)
        value4_name = getSymptomName(value2, value3, value4)

        html = textwrap.dedent(f"""
            <div class="delay-row">
                <div class="delay-label">Delay Code Updated:</div>
                  <div class="delay-item">
                    <div class="delay-box">{safe_display(value1)}</div>
                    <div class="delay-note">{value1_name}</div>
                </div>
                <div class="delay-item">
                    <div class="delay-box">{safe_display(value2)}</div>
                    <div class="delay-note">{value2_name}</div>
                </div>
                <div class="delay-item">
                    <div class="delay-box">{safe_display(value3)}</div>
                    <div class="delay-note">{value3_name}</div>
                </div>
                <div class="delay-item">
                    <div class="delay-box delay-box-wide">{safe_display(value4)}</div>
                    <div class="delay-note">{value4_name}</div>
                </div>
            </div>
        """).strip()
        st.markdown(html, unsafe_allow_html=True)


        # Skip these fields in the normal detail list
        skip_fields = set(code_columns)
        skip_fields.update(["DEPT_NAME", "SYSTEM_NAME", "SYMPTOM_NAME","DelayCode", "SERVICE_TYPE_NAME",
                            "SERVICE_TYPE_CODE","SERVICE_TYPE","SYMPTOM_CODE"])
        LogidCommentMap = (
            chiefLogDailyDf.groupby("DisplayLogId")["Comments"]
            .apply(
                lambda commentSeries: "\n".join(
                    dict.fromkeys(
                        str(singleComment).strip()
                        for singleComment in commentSeries
                        if pd.notna(singleComment) and str(singleComment).strip() != ""
                    )
                )
            )
            .to_dict()
        )
        selected_id = str(selected_row["DISPLAY_LOG_ID"]).strip()
        matched_file2_comment = LogidCommentMap.get(selected_id, "")

        for index, field in enumerate(selected_row.index):
            if field in skip_fields:
                continue

            value = selected_row[field]

            if pd.isna(value) or str(value).strip() == "":
                continue

            st.markdown(f"**{field}**")

            if isinstance(value, str) and len(value) > 80:
                st.text_area(
                    label="",
                    value=value,
                    height=120,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"area_{row_position}_{field}_{index}"
                )
            else:
                st.text_input(
                    label="",
                    value=str(value),
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"text_{row_position}_{field}_{index}"
                )

            if field == "COMMENTS":
                st.markdown("**ChiefLog Comment**")
                st.text_area(
                    label="",
                    value=matched_file2_comment,
                    height=120,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"area_comment2_{row_position}_{index}"
                )

