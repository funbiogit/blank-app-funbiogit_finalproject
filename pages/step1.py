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
# GPT 콜: openai>=1.x 대응 함수
# --------------------
def get_openai_client(api_key):
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"OpenAI 라이브러리 import 오류: {e}")
        return None


def chat_completion_gpt(client, prompt_roles, temperature=0.2):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=prompt_roles,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[오류 발생: {str(e)}]"


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
    unclassified = set(all_elements) - set(bio_selected) - set(abio_selected)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"**선택되지 않은 요소 수: {len(unclassified)}개**")
    with col2:
        if any(e in bio_selected for e in ["빛", "공기", "온도"]) or any(e in abio_selected for e in ["벼", "참새", "족제비", "세균", "메뚜기", "곰팡이", "콩"]):
            st.markdown("<span style='color:red;'>다시 한 번 생각해보세요.</span>", unsafe_allow_html=True)


    st.subheader("3. 생물 요소와 비생물 요소 간의 관계")
    st.markdown("다음에 제시된 요소 사이에서 나타나는 상호 관계의 예시를 조사하여 작성해보세요:")

    def check_relation_feedback(prompt_text, user_input):
        if api_key and user_input.strip():
            client = get_openai_client(api_key)
            if client is None:
                return ""
            abiotic, _ = prompt_text.split(" - ")
            prompt_roles = [
                {
                    "role": "system",
                    "content": (
f"""당신은 중학생 과학 교육 전문가입니다.

학생이 '{abiotic}'과 생물 요소 사이 상호 작용에 대해 여러 문장으로 작성했습니다.
학생 답변에 '{abiotic}'와 관련된 내용이 있는지 우선 판단하세요.
- 만약 관련 내용이 전혀 없으면,
  '입력 내용이 "{abiotic}"와 관련된 내용이 아니므로, 해당 영역과 관련된 적절한 사례를 다시 작성해 주세요.' 라고 안내하세요.
- 만약 내용이 '{abiotic}'와 관련 있다면,
  각 문장을 분리해 다음을 평가하세요:

1) 각 문장이 '생물 요소가 {abiotic}로부터 받는 영향'인지,
   혹은 '{abiotic}가 생물 요소로부터 받는 영향'인지 명확히 구분합니다.
2) 각 진술이 과학적으로 타당한지 판단하고,
   타당하다면 학생이 쓴 구체적 내용을 요약하여 긍정적 피드백에 반영하세요.
3) 틀렸거나 오개념인 경우, 어떤 점이 왜 틀렸는지 구체적으로 지적하세요.
4) 두 영향 방향 중 어느 한쪽에 대한 답변이 없는 경우에만(틀린 경우는 답변이 있는 것으로 간주)
   '생물→{abiotic} 영향(또는 {abiotic}→생물 영향)에 대한 사례가 누락되었습니다.'라고 안내하세요.
5) 평가문은 모두 학생이 쓴 진술을 바탕으로 요약하며,
   절대로 새로운 예시나 사례를 추가하지 마세요.

전반적으로 명확하고 객관적인 문장으로 학생이 이해하도록 도우세요.

--- 학생 답변 시작 ---
"""
                    ),
                },
                {"role": "user", "content": user_input.strip()}
            ]
            return chat_completion_gpt(client, prompt_roles, temperature=0.2)
        return ""

    relation_blight = st.text_area("빛 - 생물 요소", key="rel_blight")
    fb_blight = check_relation_feedback("빛 - 생물 요소", relation_blight)
    if fb_blight:
        st.markdown(f"<div style='color:blue;'>{fb_blight}</div>", unsafe_allow_html=True)


    relation_temp = st.text_area("온도 - 생물 요소", key="rel_temp")
    fb_temp = check_relation_feedback("온도 - 생물 요소", relation_temp)
    if fb_temp:
        st.markdown(f"<div style='color:blue;'>{fb_temp}</div>", unsafe_allow_html=True)


    relation_air = st.text_area("공기 - 생물 요소", key="rel_air")
    fb_air = check_relation_feedback("공기 - 생물 요소", relation_air)
    if fb_air:
        st.markdown(f"<div style='color:blue;'>{fb_air}</div>", unsafe_allow_html=True)


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


    # 피드백: 분류 오류 감지
    valid_set = set(producers + consumers + decomposers)
    invalid = set(bio_selected) - valid_set
    if invalid:
        st.markdown("<span style='color:red;'>5단계 분류에서 일부 생물이 역할로 지정되지 않았습니다. 다시 생각해보세요.</span>", unsafe_allow_html=True)


    st.subheader("6. 생물 간 상호작용 조사")
    st.markdown("**역할별로 분류한 생물 중 한 가지씩을 고르세요.**")
    selected_producer = st.selectbox("생산자 중 하나 선택", ["선택하세요"] + producers, key="select_producer")
    selected_consumer_1 = st.selectbox("소비자 중 1차 소비자 선택", ["선택하세요"] + consumers, key="select_consumer_1")
    selected_consumer_2 = st.selectbox("소비자 중 2차 소비자 선택", ["선택하세요"] + consumers, key="select_consumer_2")
    selected_decomposer = st.selectbox("분해자 중 하나 선택", ["선택하세요"] + decomposers, key="select_decomposer")


    def check_interaction_feedback(title, text):
        if api_key and text.strip():
            client = get_openai_client(api_key)
            if client is None:
                return ""
            prompt_roles = [
                {"role": "system", "content": "당신은 과학 수업 피드백을 제공하는 전문가입니다. 사용자의 상호작용 서술에서 각 생물 요소가 해당 환경 요인으로부터 그리고 환경 요인이 생물 요소로부터 어떤 영향을 받는지 명확히 드러나는지, 영향이 타당한지 확인해 피드백을 주세요. 내용이 불충분하거나 모호한 경우 구체적인 사례를 찾도록 안내하세요. 절대 사례를 직접 제공하지 마세요. "},
                {"role": "user", "content": text.strip()}
            ]
            return chat_completion_gpt(client, prompt_roles, temperature=0.3)
        return ""


    if selected_producer != "선택하세요" and selected_consumer_1 != "선택하세요":
        st.markdown(f"**{selected_producer}와/과 {selected_consumer_1} 간 상호작용을 작성해보세요.**")
        text_pc = st.text_area("각 요소가 받는 영향을 모두 포함하세요.", key="interaction_producer_consumer")
        feedback_pc = check_interaction_feedback("생산자-소비자", text_pc)
        if feedback_pc:
            st.markdown(f"<div style='color:green;'>{feedback_pc}</div>", unsafe_allow_html=True)


    if selected_consumer_1 != "선택하세요" and selected_consumer_2 != "선택하세요":
        st.markdown(f"**{selected_consumer_1}와/과 {selected_consumer_2} 간 상호작용을 작성해보세요.**")
        text_cc = st.text_area("각 요소가 받는 영향을 모두 포함하세요.", key="interaction_1st_2nd_consumer")
        feedback_cc = check_interaction_feedback("1차-2차 소비자", text_cc)
        if feedback_cc:
            st.markdown(f"<div style='color:green;'>{feedback_cc}</div>", unsafe_allow_html=True)


    if selected_decomposer != "선택하세요":
        involved = ", ".join([s for s in [selected_producer, selected_consumer_1, selected_consumer_2] if s != "선택하세요"])
        st.markdown(f"**{involved}와/과 {selected_decomposer} 간 상호작용을 작성해보세요.**")
        text_dc = st.text_area("각 요소가 받는 영향을 모두 포함하세요.", key="interaction_with_decomposer")
        feedback_dc = check_interaction_feedback("생산자-분해자 등", text_dc)
        if feedback_dc:
            st.markdown(f"<div style='color:green;'>{feedback_dc}</div>", unsafe_allow_html=True)


    st.markdown("**이들 사례를 종합하여 아래 문장의 빈칸을 채워보세요.**")
    summary_text = st.text_input("생물 요소 사이에는 [            ] 관계가 있다.")
    if api_key and summary_text.strip():
        client = get_openai_client(api_key)
        if client is not None:
            try:
                prompt_roles=[
                    {"role": "system", "content": "입력된 문장에서 빈칸에 들어간 단어가 생물 요소 간 '상호 의존' 또는 상호작용과 관련된 개념인지 판단하고, 타당한 경우 타당성 근거를, 아닌 경우 타당하지 않은 이유를 피드백으로 작성하세요."},
                    {"role": "user", "content": summary_text.strip()}
                ]
                res = client.chat.completions.create(
                    model="gpt-4",
                    messages=prompt_roles,
                    temperature=0.3
                )
                st.markdown(f"<div style='color:purple;'>{res.choices[0].message.content}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"빈칸 피드백 오류: {e}")

elif topic == "진화와 생물 다양성":
    st.switch_page("/page3")
