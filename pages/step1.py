import streamlit as st
import os
from fpdf import FPDF
import io
from openai import OpenAI


st.markdown("""
<style>
    [data-testid="stSidebar"] * { color: black !important; }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h1 {
        font-size: 1.25rem !important;
        margin-bottom: 2px !important;
        margin-top: 2px !important;
        font-weight: 700;
    }
    [data-testid="stSidebar"] .element-container, [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stButton {
        margin-top: 2px !important;
        margin-bottom: 2px !important;
    }
    [data-testid="stSidebar"] .sidebar-lens-box {
        background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%);
        color: #212121;
        padding: 10px 0;
        border-radius: 14px;
        text-align: center;
        font-size: 20px;
        font-weight: 600;
        margin: 2px auto 2px auto;
        width: 210px;
        box-shadow: 0 6px 18px rgba(248, 187, 208, 0.18);
        border: 1.3px solid #f06292;
        letter-spacing: 1px;
    }
    [data-testid="stSidebar"] button {
        min-width: 170px !important;
        max-width: 270px;
        white-space:nowrap !important;
        font-size: 15px;
    }
    .section-header {
        color: #2d3748;
        font-size: 1.7rem !important;
        font-weight: 900 !important;
        margin: 30px 0 20px 0;
        text-align: left;
    }
    .main-lens-box {
        background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%);
        color: #212121;
        padding: 10px 0;
        border-radius: 14px;
        text-align: center;
        font-size: 20px;
        font-weight: 600;
        margin: 12px auto 6px auto;
        width: 210px;
        min-width: 160px;
        box-shadow: 0 6px 18px rgba(248, 187, 208, 0.18);
        border: 1.3px solid #f06292;
        letter-spacing: 1px;
    }
    .concepttitle { font-size: 23px !important; text-align:center; font-weight:700; margin-bottom:4px; margin-top:8px;}
    .definition-card, .feature-card {
        background: linear-gradient(135deg, #def7fe 0%, #e7eeff 100%);
        padding: 18px;
        border-radius: 12px;
        margin: 7px 0;
        box-shadow: 0 4px 13px rgba(51,153,255,0.09);
        font-size: 17px;
        border: none;
        color: #174a7c !important;
    }
    .example-guide {
        font-size: 15px;
        color:#353535;
        font-weight:500;
        margin-top:6px;
        margin-bottom:4px;
    }
    .leading-box {
        background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%);
        color: #212121;
        padding: 15px 0;
        border-radius: 16px;
        text-align: center;
        font-size: 19px;
        font-weight: 600;
        margin: 14px auto 10px auto;
        width: 30%;
        min-width: 130px;
        box-shadow: 0 6px 18px rgba(248, 187, 208, 0.13);
        border: 1.2px solid #f06292;
        letter-spacing: 1px;
    }
    .inquiry-guide, .inquiry-limit, .final-inquiry, .final-guide {
        font-size: 15px;
        font-weight: 500;
        color: #203a4d;
        margin: 7px 0 4px 0;
        padding: 0;
        text-indent: 2em;
    }
    .ai-suggestion {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 13px 16px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #ff9a56;
        box-shadow: 0 3px 9px rgba(255, 154, 86, 0.13);
        font-size: 13px;
        color: #663c00;
    }
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 36px;
        font-weight: 800;
        text-align: left;
        margin: 30px 0;
    }
    [data-testid="stSidebar"] input[type="password"] {
        width: 100% !important;
        min-width: 250px !important;
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
        font-size: 17px;
        color: #222;
    }
    .sidebar-divider {
        border-top: 1.5px solid #f06292;
        margin: 10px auto 6px auto;
        width: 210px;
    }
</style>
""", unsafe_allow_html=True)


st.set_page_config(layout="wide")


# --------------------
# 사이드바 구성
# --------------------
with st.sidebar:
    st.markdown("<h3 style='text-align:center; margin-bottom:1px;'>학습 주제 선택</h3>", unsafe_allow_html=True)
    topic = st.selectbox(
        "주제 선택",
        ["-- 주제를 선택하세요 --", "생태계와 환경 변화", "진화와 생물 다양성"],
        label_visibility="collapsed"
    )
    # 사용자가 안내 선택 안 했을 때엔 ""으로 바꿔 전체 코드 정상 동작하도록 처리
    if topic == "-- 주제를 선택하세요 --":
        topic = ""
    st.markdown("---")

    st.markdown("<h3 style='text-align:center; margin-bottom:5px;'>개념 렌즈</h3>", unsafe_allow_html=True)
    if topic == "생태계와 환경 변화":
        lens = "관계"
        lens_def = "관계는 두 개 이상의 요소가 한 방향 또는 상호 영향을 주고받는 방식이나 연결 방식을 의미한다."
        lens_feat = "- 각 요소 중 하나 이상에 변화가 나타남.<br>- 요소 간 주고받는 영향을 통해 복합적인 의미가 나타남."
    elif topic == "진화와 생물 다양성":
        lens = "변화"
        lens_def = "하나의 형태, 상태, 가치가 다른 형태, 상태, 가치로 전환, 변형 또는 이동하는 현상을 말한다."
        lens_feat = "- 원인, 과정, 결과의 틀 속에서 무엇이, 왜, 어떻게 달라지는지 설명할 수 있음.<br>- 연속적 혹은 불연속적으로 일어날 수 있음."
    else:
        lens = ""
        lens_def = ""
        lens_feat = ""
    st.markdown(f"<div class='sidebar-lens-box'>{lens}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='definition-card'><b>정의:</b> {lens_def}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='feature-card'><b>특징:</b> {lens_feat}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h3 style='text-align:center; margin-bottom:5px;'>OpenAI API 키 입력</h3>", unsafe_allow_html=True)
    with st.container():
        api_key_input = st.text_input(
            "API 키 입력",
            type="password",
            value=st.session_state.get("openai_api_key", ""),
            help="API 키를 입력해 주세요.",
            label_visibility="collapsed"
        )
    if api_key_input != st.session_state.get("openai_api_key", ""):
        st.session_state["openai_api_key"] = api_key_input
        st.success("API 키가 저장되었습니다.")

    api_key = st.session_state.get("openai_api_key", "")

    st.markdown("---")
    st.markdown("<h3 style='text-align:center; margin-bottom:5px;'>PDF 저장하기</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.2, 1, 1])
    with col2:
        if st.button("PDF 생성", use_container_width=True):
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font("Arial", "", fname="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="개념기반 탐구 수업 - 예시/비예시 선택 내용", ln=True, align='C')
            pdf.ln(10)
            for category in ["예시", "비예시"]:
                if category == "예시":
                    pdf.set_text_color(0, 128, 0)
                else:
                    pdf.set_text_color(200, 0, 0)
                for s, v in st.session_state.sentence_assignments.items():
                    if v == category:
                        pdf.cell(200, 10, txt=f"- {s}", ln=True)
            buf = io.BytesIO()
            pdf.output(buf)
            buf.seek(0)
            st.download_button(
                "PDF 다운로드",
                data=buf.getvalue(),
                file_name="개념기반탐구.pdf",
                mime="application/pdf",
                use_container_width=True
            )


# 메인
if topic == "생태계와 환경 변화":
    st.markdown('<h1 class="main-title">생태계 구성 요소와 관계</h1>', unsafe_allow_html=True)
    st.subheader("1. 생물 요소와 비생물 요소")
    cols = st.columns(4)
    all_elements = ["벼", "참새", "빛", "공기", "족제비", "세균", "온도", "메뚜기", "곰팡이", "콩"]

    for i, elem in enumerate(all_elements):
        with cols[i % 4]:
            st.markdown(f"<div class='center-box'>{elem}</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("2. 요소 분류하기")
    bio_selected = st.multiselect("생물 요소로 분류할 것들", all_elements)
    abio_selected = st.multiselect("비생물 요소로 분류할 것들", all_elements)
    unclassified = set(all_elements) - set(bio_selected) - set(abio_selected)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"**미선택요소(갯수): {len(unclassified)}개**")
    with col2:
        if any(e in bio_selected for e in ["빛", "공기", "온도"]) or any(e in abio_selected for e in ["벼", "참새", "족제비", "세균", "메뚜기", "곰팡이", "콩"]):
            st.markdown("<span style='color:red;'>다시 한 번 생각해보세요.</span>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("3. 생물 요소와 비생물 요소 간의 관계")
    st.markdown("다음에 제시된 요소 사이에서 나타나는 상호 관계의 예시를 조사하여 작성해보세요:")

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
"""당신은 중학생 과학 교육 전문가입니다.
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
4) 두 영향 방향 중 어느 한쪽에 대한 답변이 없는 경우(틀린 경우나 부적절한 답변은 답변이 있는 것으로 간주)
   '생물→{abiotic} 영향(또는 {abiotic}→생물 영향)에 대한 사례가 누락되었습니다.'라고 안내하세요.
5) 평가문은 모두 학생이 쓴 진술을 바탕으로 요약하며,
   절대로 새로운 예시나 사례를 추가하지 마세요.
명확하고 객관적이면서 6문장 이내로 학생이 이해하도록 도우세요.
--- 학생 답변 시작 ---
""".format(abiotic=abiotic)
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

    st.markdown("---")
    st.subheader("4. 생물 요소의 세 가지 역할")
    st.markdown("- 생물 요소는 <b>생산자, 소비자, 분해자</b>로 구분됩니다.", unsafe_allow_html=True)
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

    st.markdown("---")
    st.subheader("5. 생물 요소 분류하기")
    producers = st.multiselect("생산자", bio_selected)
    consumers = st.multiselect("소비자", bio_selected)
    decomposers = st.multiselect("분해자", bio_selected)

    valid_set = set(producers + consumers + decomposers)
    invalid = set(bio_selected) - valid_set
    if invalid:
        st.markdown("<span style='color:red;'>5단계 분류에서 일부 생물이 역할로 지정되지 않았습니다. 다시 생각해보세요.</span>", unsafe_allow_html=True)

    # 역할별 오분류에 대한 피드백 추가
    wrong_classification = []
    correct_producers = {"벼", "콩"}
    correct_consumers = {"참새", "족제비", "메뚜기"}
    correct_decomposers = {"세균", "곰팡이"}
    wrong_prod = set(producers) - correct_producers
    if wrong_prod:
        wrong_classification.append(f"생산자 분류에 잘못된 선택이 포함되었습니다.")
    wrong_cons = set(consumers) - correct_consumers
    if wrong_cons:
        wrong_classification.append(f"소비자 분류에 잘못된 선택이 포함되었습니다.")
    wrong_decom = set(decomposers) - correct_decomposers
    if wrong_decom:
        wrong_classification.append(f"분해자 분류에 잘못된 선택이 포함되었습니다.")
    if wrong_classification:
        st.markdown("<span style='color:red;'><b>분류 오류 피드백:</b><br>" + "<br>".join(wrong_classification) + "</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("6. 생물 간 상호작용 조사")
    st.markdown("**역할별로 분류한 생물 중 한 가지씩을 고르세요.**")
    selected_producer = st.selectbox("생산자 중 하나 선택", ["선택하세요"] + producers, key="select_producer")
    selected_consumer_1 = st.selectbox("소비자 중 1차 소비자 선택", ["선택하세요"] + consumers, key="select_consumer_1")
    selected_consumer_2 = st.selectbox("소비자 중 2차 소비자 선택", ["선택하세요"] + consumers, key="select_consumer_2")
    selected_decomposer = st.selectbox("분해자 중 하나 선택", ["선택하세요"] + decomposers, key="select_decomposer")

    # 1차/2차 소비자 선택 피드백
    consumer_feedback_messages = []
    # 1차 소비자 검증(족제비 불가)
    if selected_consumer_1 != "선택하세요" and selected_consumer_1 == "족제비":
        consumer_feedback_messages.append('<span style="color:red;">"1차" 소비자를 선택해야 합니다.</span>')
    # 2차 소비자 검증(메뚜기 불가)
    if selected_consumer_2 != "선택하세요" and selected_consumer_2 == "메뚜기":
        consumer_feedback_messages.append('<span style="color:red;">"2차" 소비자를 선택해야 합니다.</span>')
    # 1차/2차 동일 생물 불가
    if (
        selected_consumer_1 != "선택하세요"
        and selected_consumer_2 != "선택하세요"
        and selected_consumer_1 == selected_consumer_2
    ):
        consumer_feedback_messages.append('<span style="color:red;">1차 소비자와 2차 소비자를 서로 다르게 선택해주세요.</span>')

    if consumer_feedback_messages:
        st.markdown("<br>".join(consumer_feedback_messages), unsafe_allow_html=True)

    def check_interaction_feedback(title, text):
        if api_key and text.strip():
            client = get_openai_client(api_key)
            if client is None:
                return ""
            prompt_roles = [
                {"role": "system", "content": "당신은 과학 수업 피드백을 제공하는 전문가입니다. 사용자의 상호작용 서술에서 각 생물 요소가 해당 환경 요인으로부터 그리고 환경 요인이 생물 요소로부터 어떤 영향을 받는지 명확히 드러나는지, 영향이 타당한지 확인해 피드백을 주세요. 내용이 불충분하거나 모호한 경우 구체적인 사례를 찾도록 안내하세요. 절대 사례를 직접 제공하지 마세요."},
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
    summary_text = st.text_input("생물 요소 사이에는 [       ] 관계가 있다.")
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
    st.markdown('<h1 class="main-title">진화와 생물 다양성</h1>', unsafe_allow_html=True)
    st.subheader("추후 공개 예정")
