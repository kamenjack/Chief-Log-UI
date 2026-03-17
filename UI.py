import streamlit as st
import pandas as pd

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
</style>
""", unsafe_allow_html=True)

st.title("Train Delay Viewer")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    date_column = "RUN_DATE"
    train_column = "TRAIN_NAME"
    location_column = "LOCATION_NAME"
    performance_column = "LATENESS"

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

    if daily_df.empty:
        st.info("No records found for the selected date.")
        st.stop()

    display_columns = [
        col for col in [train_column, location_column, performance_column]
        if col in daily_df.columns
    ]

    st.markdown("### Daily Records")

    event = st.dataframe(
        daily_df[display_columns],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="daily_records_table",
    )

    selected_row = None
    selected_rows = event.selection.rows

    if selected_rows:
        row_position = selected_rows[0]
        selected_row = daily_df.iloc[row_position]

    st.markdown("### Train Details")

    if selected_row is None:
        st.info("Click a train row in Daily Records.")
    else:
        for index, field in enumerate(selected_row.index):
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