import streamlit as st
import pandas as pd
import numpy as np

st.title("마켓링크 층화비례 표본오차 계산 프로그램 (Stratified Sampling)")

# -------------------
# 초기화 버튼
# -------------------
if st.button("🔄 초기화"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# -------------------
# 1차 입력
# -------------------
N = st.number_input("모집단 수 (Total Population)", min_value=1, value=10000)

# 지역개수와 유형개수
col1, col2 = st.columns(2)
with col1:
    num_regions = st.number_input("지역 개수", min_value=1, value=3)
with col2:
    num_types = st.number_input("유형 개수", min_value=1, value=2)

# session_state 저장
if "detail" not in st.session_state:
    st.session_state.detail = False

# -------------------
# 상세입력 생성 버튼
# -------------------
if st.button("상세입력 생성"):
    st.session_state.detail = True

# -------------------
# 상세 입력창 생성
# -------------------
if st.session_state.detail:

    st.subheader("지역명 입력")
    region_names = []
    for i in range(int(num_regions)):
        region_names.append(
            st.text_input(f"지역명 {i+1}", value=f"지역{i+1}")
        )

    st.subheader("유형명 입력")
    type_names = []
    for j in range(int(num_types)):
        type_names.append(
            st.text_input(f"유형명 {j+1}", value=f"유형{j+1}")
        )

    st.subheader("각 지역 × 유형별 **표본수(nₕ)** 입력")
    sample_matrix = []
    for i in range(int(num_regions)):
        row = []
        st.markdown(f"### 👉 {region_names[i]} 표본수")
        cols = st.columns(int(num_types))
        for j in range(int(num_types)):
            n_h = cols[j].number_input(
                f"{region_names[i]} - {type_names[j]} (표본수 nₕ)",
                min_value=0,
                value=0,
                key=f"n_{i}_{j}"
            )
            row.append(n_h)
        sample_matrix.append(row)

    sample_df = pd.DataFrame(sample_matrix, index=region_names, columns=type_names)
    st.write("### ✔ 입력된 표본수(nₕ) 테이블")
    st.dataframe(sample_df)

    # -----------------------------
    # 층별 모집단 입력 (신규 추가)
    # -----------------------------
    st.subheader("각 지역 × 유형별 **모수(Nₕ)** 입력")
    pop_matrix = []
    for i in range(int(num_regions)):
        row = []
        st.markdown(f"### 👉 {region_names[i]} 모집단")
        cols = st.columns(int(num_types))
        for j in range(int(num_types)):
            Nh_val = cols[j].number_input(
                f"{region_names[i]} - {type_names[j]} (모수 Nₕ)",
                min_value=0,
                value=0,
                key=f"Nh_{i}_{j}"
            )
            row.append(Nh_val)
        pop_matrix.append(row)

    Nh_df = pd.DataFrame(pop_matrix, index=region_names, columns=type_names)
    st.write("### ✔ 입력된 모집단(Nₕ) 테이블")
    st.dataframe(Nh_df)

    # -------------------
    # 표본오차 계산 버튼
    # -------------------
    if st.button("표본오차 계산"):

        n_h = sample_df.values.flatten()
        Nh = Nh_df.values.flatten()

        total_sample = np.sum(n_h)
        total_population_from_Nh = np.sum(Nh)

        if total_sample == 0:
            st.error("표본수(nₕ)를 하나 이상 입력해야 계산이 가능합니다.")
        elif np.any(n_h == 0):
            st.error("각 층의 표본수(nₕ)는 0일 수 없습니다. (표본오차 계산 불가)")
        else:

            # 최대표본오차 p = 0.5
            p = 0.5

            # -----------------------
            # 층별 표본오차(SE_h)
            # -----------------------
            SE_h = np.sqrt((Nh / N)**2 * (p * (1 - p) / n_h))

            # -----------------------
            # 전체 표본오차(SE_total)
            # -----------------------
            SE_total = np.sqrt(np.sum((Nh / N)**2 * (p * (1 - p) / n_h)))
            MOE_total = 1.96 * SE_total

            # 층별 SE를 지역 × 유형 형태로 변환
            se_df = pd.DataFrame(SE_h.reshape(sample_df.shape),
                                 index=region_names, columns=type_names)

            st.subheader("📌 층별 표본오차(SEₕ)")
            st.dataframe(se_df)

            st.subheader("📌 전체 층화비례 표본오차 결과")
            st.write(f"총 표본수 n = {total_sample}")
            st.write(f"입력된 층별 모집단 총합 = {total_population_from_Nh}")
            st.write(f"전체 모집단 N = {N}")
            st.write(f"표본오차(SE_total) = {SE_total:.6f}")
            st.write(f"95% 오차범위(MOE) = ±{MOE_total:.6f}")