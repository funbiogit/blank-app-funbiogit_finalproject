import streamlit as st
import os
from fpdf import FPDF

# --------------------
# 기본 설정
# --------------------
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        justify-content: center;
        display: flex;
    }
    section[data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .center-box {
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #e0f0ff;
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------
# 사이드바 구성
# --------------------
st.sidebar.markdown("## 학습 주제 선택")
topic = st.sidebar.selectbox("학습 주제", ["생태계와 환경 변화", "진화와 생물 다양성"])

if topic == "생태계와 환경 변화":
    lens = "관계"
    lens_def = "관계는 두 개 이상의 요소가 한 방향 또는 상호 영향을 주고받는 방식이나 연결 방식을 의미한다."
    lens_feat = "- 각 요소 중 하나 이상에 변화가 나타남.\n- 요소 간 주고받는 영향을 통해 복합적인 의미가 나타남."

elif topic == "진화와 생물 다양성":
    lens = "변화"
    lens_def = "하나의 형태, 상태, 가치가 다른 형태, 상태, 가치로 전환, 변형 또는 이동하는 현상을 말한다."
    lens_feat = "- 원인, 과정, 결과의 틀 속에서 무엇이, 왜, 어떻게 달라지는지 설명할 수 있음.\n- 연속적 혹은 불연속적으로 일어날 수 있음."
else:
    lens = ""
    lens_def = ""
    lens_feat = ""

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align:center; font-weight:bold; font-size:18px;'>개념 렌즈</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='background-color:#d1f5d3; padding:8px; border-radius:8px; text-align:center; font-weight:bold;'>{lens}</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='background-color:#fff4c2; padding:8px; border-radius:8px; font-weight:normal; text-align:left;'><strong>정의:</strong> {lens_def}</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='background-color:#fff4c2; padding:8px; border-radius:8px; font-weight:normal; text-align:left; white-space:pre-wrap;'><strong>특징:</strong> {lens_feat}</div>", unsafe_allow_html=True)
st.sidebar.markdown("---")

api_key = st.sidebar.text_input("OpenAI API Key 입력", type="password")

if st.sidebar.button("PDF로 저장"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="학습 결과 저장 예시", ln=True, align='C')
    with open("output.pdf", "wb") as f:
        pdf.output(f)
    st.sidebar.success("PDF로 저장되었습니다.")

# --------------------
# 메인 페이지 구성
# --------------------
if topic == "생태계와 환경 변화":
    st.title("생태계 구성 요소와 관계")

    st.subheader("1. 생물 요소와 비생물 요소")
    cols = st.columns(4)
    all_elements = ["벼", "참새", "빛", "공기", "족제비", "세균", "온도", "메뚜기", "곰팡이", "콩"]

    for i, elem in enumerate(all_elements):
        with cols[i % 4]:
            st.markdown(f"<div class='center-box'>{elem}</div>", unsafe_allow_html=True)

    st.subheader("2. 요소 분류하기")
    bio_selected = st.multiselect("생물 요소로 분류할 것들", all_elements)
    abio_selected = st.multiselect("비생물 요소로 분류할 것들", all_elements)

    st.subheader("3. 생물 요소와 비생물 요소 간의 관계")
    st.markdown("다음에 제시된 요소 사이에서 나타나는 상호 관계의 예시를 조사하여 작성해보세요:")
    relation_blight = st.text_area("빛 - 생물 요소")
    relation_temp = st.text_area("온도 - 생물 요소")
    relation_air = st.text_area("공기 - 생물 요소")

    st.subheader("4. 생물 요소의 세 가지 역할")
    st.markdown("- 생물 요소는 **생산자, 소비자, 분해자**로 구분됩니다.")
    st.markdown("다음 각각의 용어에 해당하는 설명을 골라보세요.")
    role_options = ["생산자", "소비자", "분해자"]
    definitions = {
        "생산자": "광합성을 통해 스스로 먹이를 생산하고 소비하는 생물",
        "소비자": "다른 생물을 먹고 에너지를 얻는 생물",
        "분해자": "죽은 생물을 분해하여 에너지를 얻는 생물"
    }

    for role in role_options:
        answer = st.selectbox(f"{role}의 정의로 가장 적절한 것을 고르세요.", ["선택하세요"] + list(definitions.values()), key=role)
        if answer == definitions[role]:
            st.success("정답입니다!")
        elif answer != "선택하세요":
            st.warning("다시 생각해보세요.")

    st.subheader("5. 생물 요소 분류하기")
    producers = st.multiselect("생산자", bio_selected)
    consumers = st.multiselect("소비자", bio_selected)
    decomposers = st.multiselect("분해자", bio_selected)

    st.subheader("6. 생물 간 상호작용 조사")
    st.markdown("**역할별로 분류한 생물 중 한 가지 씩을 고르세요.**")

    selected_producer = st.selectbox("생산자 중 하나 선택", ["선택하세요"] + producers, key="select_producer")
    selected_consumer_1 = st.selectbox("소비자 중 1차 소비자를 하나 선택", ["선택하세요"] + consumers, key="select_consumer_1")
    selected_consumer_2 = st.selectbox("소비자 중 2차 소비자를 하나 선택", ["선택하세요"] + consumers, key="select_consumer_2")
    selected_decomposer = st.selectbox("분해자 중 하나 선택", ["선택하세요"] + decomposers, key="select_decomposer")

    if selected_producer != "선택하세요" and selected_consumer_1 != "선택하세요":
        st.markdown(f"**{selected_producer}와/과 {selected_consumer_1} 간 상호작용을 작성해보세요.**")
        st.text_area("각 요소가 상호작용으로 받는 영향을 모두 작성해보세요", key="interaction_producer_consumer")

    if selected_consumer_1 != "선택하세요" and selected_consumer_2 != "선택하세요":
        st.markdown(f"**{selected_consumer_1}와/과 {selected_consumer_2} 간 상호작용을 작성해보세요.**")
        st.text_area("각 요소가 상호작용으로 받는 영향을 모두 작성해보세요", key="interaction_1st_2nd_consumer")

    if selected_decomposer != "선택하세요":
        involved = ", ".join([s for s in [selected_producer, selected_consumer_1, selected_consumer_2] if s != "선택하세요"])
        st.markdown(f"**{involved}와/과 {selected_decomposer} 간 상호작용을 작성해보세요.**")
        st.text_area("각 요소가 상호작용으로 받는 영향을 모두 작성해보세요", key="interaction_with_decomposer")

    st.markdown("**이들 사례를 종합하여 아래 문장의 빈칸을 채워보세요.**")
    st.text_input("생물 요소 사이에는 [            ] 관계가 있다.")

elif topic == "진화와 생물 다양성":
    st.switch_page("/page3")
