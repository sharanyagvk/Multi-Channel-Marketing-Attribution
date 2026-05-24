
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import os

# PAGE CONFIG
st.set_page_config(page_title="Multi Channel Attribution", layout="wide")

st.title("📊 Multi-Channel Marketing Attribution")

# SHOW FILES
st.subheader("📁 Files Available")
st.write(os.listdir())

# UPLOAD FILE
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:

    # LOAD DATA
    df = pd.read_csv(uploaded_file)

    st.success("✅ Dataset Loaded Successfully")

    # CLEAN COLUMNS
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # PREVIEW
    st.subheader("📌 Dataset Preview")
    st.dataframe(df.head())

    st.subheader("📌 Columns")
    st.write(df.columns.tolist())

    # REQUIRED COLUMNS
    required_cols = ['user_id', 'timestamp', 'channel', 'conversion']

    missing = [col for col in required_cols if col not in df.columns]

    if len(missing) > 0:
        st.error(f"❌ Missing Columns: {missing}")

    else:

        # CONVERT TIMESTAMP
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # CONVERT CONVERSION COLUMN TO 1/0
        df['conversion'] = df['conversion'].astype(str).str.lower()

        df['conversion'] = df['conversion'].replace({
            'yes': 1,
            'true': 1,
            'converted': 1,
            '1': 1,
            'no': 0,
            'false': 0,
            '0': 0
        })

        df['conversion'] = pd.to_numeric(df['conversion'], errors='coerce').fillna(0)

        # SORT DATA
        df = df.sort_values(by=['user_id', 'timestamp'])

        # CUSTOMER JOURNEYS
        st.subheader("🧭 Customer Journeys")

        journeys = df.groupby('user_id')['channel'].apply(
            lambda x: ' → '.join(x.astype(str))
        ).reset_index()

        journeys.columns = ['user_id', 'journey_path']

        st.dataframe(journeys.head(10))

        # LAST CLICK ATTRIBUTION
        st.subheader("🎯 Last Click Attribution")

        last_click = df.groupby('user_id').last().reset_index()

        converted_last = last_click[last_click['conversion'] == 1]

        last_click_result = converted_last['channel'].value_counts()

        if len(last_click_result) > 0:

            st.dataframe(last_click_result)

            fig1, ax1 = plt.subplots(figsize=(8,5))

            ax1.bar(
                last_click_result.index,
                last_click_result.values
            )

            ax1.set_title("Last Click Attribution")
            ax1.set_xlabel("Channel")
            ax1.set_ylabel("Conversions")

            plt.xticks(rotation=45)

            st.pyplot(fig1)

        else:
            st.warning("⚠️ No conversion data available for Last Click Attribution")

        # FIRST CLICK ATTRIBUTION
        st.subheader("🎯 First Click Attribution")

        first_click = df.groupby('user_id').first().reset_index()

        converted_first = first_click[first_click['conversion'] == 1]

        first_click_result = converted_first['channel'].value_counts()

        if len(first_click_result) > 0:

            st.dataframe(first_click_result)

            fig2, ax2 = plt.subplots(figsize=(8,5))

            ax2.bar(
                first_click_result.index,
                first_click_result.values
            )

            ax2.set_title("First Click Attribution")
            ax2.set_xlabel("Channel")
            ax2.set_ylabel("Conversions")

            plt.xticks(rotation=45)

            st.pyplot(fig2)

        else:
            st.warning("⚠️ No conversion data available for First Click Attribution")

        # LINEAR ATTRIBUTION
        st.subheader("🎯 Linear Attribution")

        linear_scores = defaultdict(float)

        for user, group in df.groupby('user_id'):

            if group['conversion'].max() == 1:

                channels = group['channel'].tolist()

                score = 1 / len(channels)

                for ch in channels:
                    linear_scores[ch] += score

        if len(linear_scores) > 0:

            linear_df = pd.DataFrame(
                linear_scores.items(),
                columns=['Channel', 'Linear Score']
            )

            st.dataframe(linear_df)

            fig3, ax3 = plt.subplots(figsize=(8,5))

            ax3.bar(
                linear_df['Channel'],
                linear_df['Linear Score']
            )

            ax3.set_title("Linear Attribution")
            ax3.set_xlabel("Channel")
            ax3.set_ylabel("Score")

            plt.xticks(rotation=45)

            st.pyplot(fig3)

        else:
            st.warning("⚠️ No data available for Linear Attribution")

        # PIE CHART
        if len(last_click_result) > 0:

            st.subheader("🥧 Conversion Share")

            fig4, ax4 = plt.subplots(figsize=(7,7))

            ax4.pie(
                last_click_result.values,
                labels=last_click_result.index,
                autopct='%1.1f%%'
            )

            ax4.set_title("Channel Conversion Share")

            st.pyplot(fig4)

        # SUMMARY
        st.subheader("📌 Summary")

        st.metric("Total Users", df['user_id'].nunique())
        st.metric("Total Conversions", int(df['conversion'].sum()))

        st.success("✅ Project Completed Successfully")

else:
    st.info("📂 Upload Dataset to Start")