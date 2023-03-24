import streamlit as st
import pandas as pd
import numpy as np

def filter_passing_candidates(data, class_threshold, quiz_threshold, min_class_score, min_quiz_score):
    return data[
        (data['class_score'] >= class_threshold) &
        (data['quiz_score'] >= quiz_threshold) &
        (data['class_score'] >= min_class_score) &
        (data['quiz_score'] >= min_quiz_score)
    ]

def specialty_ratio_distance(filtered_data, min_specialty_ratio, use_specialty_threshold):
    if not use_specialty_threshold:
        return 0

    specialty_counts = filtered_data['specialty'].value_counts()
    total_pass = len(filtered_data)
    specialty_ratios = specialty_counts / total_pass
    min_specialty_ratios_series = pd.Series(min_specialty_ratio).reindex(specialty_ratios.index, fill_value=0)
    distance = ((specialty_ratios - min_specialty_ratios_series) ** 2).sum() ** 0.5
    return distance

def find_optimal_thresholds(data, min_total_pass, max_total_pass, min_highschool, min_specialty_ratio, use_specialty_threshold, min_class_score, min_quiz_score):
    best_thresholds = None
    best_distance = float("inf")
    for class_threshold in range(1, 16):
        for quiz_threshold in range(1, 12):
            filtered_data = filter_passing_candidates(data, class_threshold, quiz_threshold, min_class_score, min_quiz_score)
            total_pass = len(filtered_data)
            highschool_pass = sum(filtered_data['is_highschool'] == 1)
            if total_pass < min_total_pass or total_pass > max_total_pass or highschool_pass < min_highschool:
                continue
            distance = specialty_ratio_distance(filtered_data, min_specialty_ratio, use_specialty_threshold)
            if distance < best_distance:
                best_thresholds = (class_threshold, quiz_threshold)
                best_distance = distance
    return best_thresholds

st.title("Candidates Threshold Optimizer")
st.write("Upload your data in CSV format:")
uploaded_file = st.file_uploader("", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    st.sidebar.header("Constraints")
    min_total_pass = st.sidebar.number_input("Minimum total pass", min_value=0, max_value=None, value=100)
    max_total_pass = st.sidebar.number_input("Maximum total pass", min_value=0, max_value=None, value=110)
    min_highschool = st.sidebar.number_input("Minimum highschool students", min_value=0, max_value=None, value=15)
    min_class_score = st.sidebar.number_input("Minimum class score", min_value=0, max_value=15, value=5)
    min_quiz_score = st.sidebar.number_input("Minimum quiz score", min_value=0, max_value=11, value=5)
    use_specialty_threshold = st.sidebar.checkbox("Use specialty threshold", value=False)

    min_specialty_ratio = {
        "Technology": st.sidebar.slider("Minimum technology ratio", min_value=0.0, max_value=1.0, value=0.3, step=0.01),
        "Business": st.sidebar.slider("Minimum business ratio", min_value=0.0, max_value=1.0, value=0.3, step=0.01),
        "Design": st.sidebar.slider("Minimum design ratio", min_value=0.0, max_value=1.0, value=0.3, step=0.01),
    }

    if st.button("Calculate optimal thresholds"):
        optimal_thresholds = find_optimal_thresholds(
            data, min_total_pass, max_total_pass, min_highschool, min_specialty_ratio, use_specialty_threshold, min_class_score, min_quiz_score
        )

        if optimal_thresholds is None:
            st.error("Impossible to find threshold from the current constraints. Please adjust the constraints and try again.")
        else:
            filtered_data = filter_passing_candidates(data, *optimal_thresholds, min_class_score, min_quiz_score)

        specialty_counts = filtered_data['specialty'].value_counts()
        total_pass = len(filtered_data)
        specialty_ratios = (specialty_counts / total_pass).to_dict()
        min_highschool_filtered = filtered_data.query("is_highschool == 1")

        st.subheader("Results")
        st.write("Optimal thresholds (Without constraints) :", optimal_thresholds)
        st.write("Specialty ratios:", specialty_ratios)
        st.write("Number of people who pass:", len(filtered_data))
        st.write("Number of highschool who pass:", len(min_highschool_filtered))
        st.write(f"Pass ratio: {np.floor(len(filtered_data) / len(data) * 100)} %")
        st.write("Cut Class Score at:", filtered_data['class_score'].min(), "times")
        st.write("Cut Quiz Score at:", filtered_data['quiz_score'].min(), "times")
        # st.write(f"Cut at: class >= {filtered_data['class_score'].min()} and quiz >= {filtered_data['quiz_score'].min()}")
        st.dataframe(filtered_data['specialty'].value_counts())
else:
    data = pd.read_csv("data.csv")
    st.sidebar.header("Constraints")
    min_total_pass = st.sidebar.number_input("Minimum total pass", min_value=0, max_value=None, value=100)
    max_total_pass = st.sidebar.number_input("Maximum total pass", min_value=0, max_value=None, value=110)
    min_highschool = st.sidebar.number_input("Minimum highschool students", min_value=0, max_value=None, value=15)
    min_class_score = st.sidebar.number_input("Minimum class score", min_value=0, max_value=15, value=5)
    min_quiz_score = st.sidebar.number_input("Minimum quiz score", min_value=0, max_value=11, value=5)
    use_specialty_threshold = st.sidebar.checkbox("Use specialty threshold", value=False)

    min_specialty_ratio = {
        "Technology": st.sidebar.slider("Minimum technology ratio", min_value=0.0, max_value=1.0, value=0.3, step=0.01),
        "Business": st.sidebar.slider("Minimum business ratio", min_value=0.0, max_value=1.0, value=0.3, step=0.01),
        "Design": st.sidebar.slider("Minimum design ratio", min_value=0.0, max_value=1.0, value=0.3, step=0.01),
    }

    if st.button("Calculate optimal thresholds"):
        optimal_thresholds = find_optimal_thresholds(
            data, min_total_pass, max_total_pass, min_highschool, min_specialty_ratio, use_specialty_threshold, min_class_score, min_quiz_score
        )

        if optimal_thresholds is None:
            st.error("Impossible to find threshold from the current constraints. Please adjust the constraints and try again.")
        else:
            filtered_data = filter_passing_candidates(data, *optimal_thresholds, min_class_score, min_quiz_score)
        
            specialty_counts = filtered_data['specialty'].value_counts()
            total_pass = len(filtered_data)
            specialty_ratios = (specialty_counts / total_pass).to_dict()
            min_highschool_filtered = filtered_data.query("is_highschool == 1")

            st.subheader("Results")
            st.write("Optimal thresholds (Without constraints) :", optimal_thresholds)
            st.write("Specialty ratios:", specialty_ratios)
            st.write("Number of people who pass:", len(filtered_data))
            st.write("Number of highschool who pass:", len(min_highschool_filtered))
            st.write(f"Pass ratio: {np.floor(len(filtered_data) / len(data) * 100)} %")
            st.write("Cut Class Score at:", filtered_data['class_score'].min(), "times")
            st.write("Cut Quiz Score at:", filtered_data['quiz_score'].min(), "times")
            # st.write(f"Cut at: class >= {filtered_data['class_score'].min()} and quiz >= {filtered_data['quiz_score'].min()}")
            st.dataframe(filtered_data['specialty'].value_counts())
