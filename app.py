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

# 지역개수와 유형개수를 옆에 배치
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
        st.markdown(f"### 👉 {region_names[i]} 층의 표본수")
        cols = st.columns(int(num_types))

        for j in range(int(num_types)):
            n_h = cols[j].number_input(
                f"{region_names[i]} - {type_names[j]}",
                min_value=0,
                value=0,
                key=f"N_{i}_{j}"
            )
            row.append(n_h)

        sample_matrix.append(row)

    sample_df = pd.DataFrame(sample_matrix, index=region_names, columns=type_names)

    st.write("### ✔ 입력된 표본수 테이블")
    st.dataframe(sample_df)

    # -------------------
    # 표본오차 계산 버튼
    # -------------------
    if st.button("표본오차 계산"):

        # 층별 표본수(n_h)
        n_h = sample_df.values.flatten()
        total_sample = np.sum(n_h)

        if total_sample == 0:
            st.error("표본수를 하나라도 입력해야 계산이 가능합니다.")
        else:
            # 기본 가정: 비례할당 → 분산 공식
            # Var(p̂) = Σ (Nh^2 / N^2) * (p(1-p) / nh)
            # 최대표본오차 p=0.5 가정
            p = 0.5

            # 층별 모집단은 비율 없이 N/층수 로 단순 가정 (필요하면 입력 확장 가능)
            H = len(n_h)
            Nh = np.repeat(N / H, H)

            # 분산 계산
            variance = np.sum((Nh**2 / N**2) * (p * (1 - p) / n_h), where=n_h != 0, initial=0)
            std_error = np.sqrt(variance)

            # 95% 신뢰구간 오차
            margin_error = 1.96 * std_error

            st.subheader("📌 계산 결과")
            st.write(f"**총 표본수:** {total_sample}")
            st.write(f"**표본오차 (95% CI)**: ± **{margin_error * 100:.2f}%**")
