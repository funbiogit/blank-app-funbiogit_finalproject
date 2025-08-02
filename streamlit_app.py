import streamlit as st
import io
from fpdf import FPDF
from openai import OpenAI


st.markdown("""
<style>
    [data-testid="stSidebar"] * { color: black !important; }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h1 {
        font-size: 1.25rem !important;
        margin-bottom: 6px !important;
        margin-top: 18px !important;
        font-weight: 700;
    }
    [data-testid="stSidebar"] .element-container, [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stButton {
        margin-top: 2px !important;
        margin-bottom: 7px !important;
    }
    [data-testid="stSidebar"] .sidebar-lens-box {
        background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%);
        color: #212121;
        padding: 10px 0;
        border-radius: 14px;
        text-align: center;
        font-size: 20px;
        font-weight: 600;
        margin: 10px auto 6px auto;
        width: 210px;
        box-shadow: 0 6px 18px rgba(248, 187, 208, 0.18);
        border: 1.3px solid #f06292;
        letter-spacing: 1px;
    }
    [data-testid="stSidebar"] button { min-width: 170px !important; max-width: 270px; white-space:nowrap !important; font-size: 15px; }

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
        font-size: 15px; color:#353535; font-weight:500; margin-top:6px; margin-bottom:4px;
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
</style>
""", unsafe_allow_html=True)


lens_data = {
    "관계": {
        "정의": "서로 다른 요소 사이에 존재하는 연관성 또는 관련이 있는 상태를 의미함.",
        "특징": "- 각 요소 중 하나 이상에 변화가 나타남<br> - 요소 간 주고받는 영향을 통해 복합적인 의미가 나타남"
    },
    "변화": {
        "정의": "사물이나 현상의 성질, 모양, 상태 바뀌어 달라지는 현상.",
        "특징": "- 원인, 과정, 결과에서 무엇이, 어떻게, 왜 달라지는지 설명할 수 있음<br>- 연속적 혹은 불연속적으로 일어날 수 있음"
    }
}
lens_map = {
    "생태계와 환경 변화": "관계",
    "진화와 생물 다양성": "변화"
}
leading_concepts = {
    "생태계와 환경 변화": ["상호작용", "에너지 흐름", "평형"],
    "진화와 생물 다양성": ["자연선택", "생물 다양성"]
}
example_sentences = [
    " 1. 세포는 하나의 생명 시스템이다.",
    " 2. 멜라닌을 합성하는 효소가 많은 사람은 피부색이 어둡다.",
    " 3. DNA의 염기 서열의 변화로 단백질의 입체구조가 바뀌었다.",
    " 4. 온도를 높였더니 효소의 활성이 나타나지 않았다.",
    " 5. 엽록체는 광합성을 수행한다.",
    " 6. 세포막은 인지질과 단백질로 이루어져 있다.",
    " 7. 다른 생명체에서 채취한 유전자를 삽입해 생명체에 새로운 특성이 부여된다.",
    " 8. 효소는 기질 특이성이 있다."
]
truth_data = {
    " 1. 세포는 하나의 생명 시스템이다.": {"예시": False, "비예시": True},
    " 2. 멜라닌을 합성하는 효소가 많은 사람은 피부색이 어둡다.": {"예시": True, "비예시": False},
    " 3. DNA의 염기 서열의 변화로 단백질의 입체구조가 바뀌었다.": {"예시": True, "비예시": False},
    " 4. 온도를 높였더니 효소의 활성이 나타나지 않았다.": {"예시": True, "비예시": False},
    " 5. 엽록체는 광합성을 수행한다.": {"예시": False, "비예시": True},
    " 6. 세포막은 인지질과 단백질로 이루어져 있다.": {"예시": False, "비예시": True},
    " 7. 다른 생명체에서 채취한 유전자를 삽입해 생명체에 새로운 특성이 부여된다.": {"예시": True, "비예시": False},
    " 8. 효소는 기질 특이성이 있다.": {"예시": False, "비예시": True}
}

if "sentence_assignments" not in st.session_state:
    st.session_state.sentence_assignments = {s: None for s in example_sentences}
if "feedback_cache" not in st.session_state:
    st.session_state.feedback_cache = {}
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""
if "reason_explanations" not in st.session_state:
    st.session_state.reason_explanations = {s: "" for s in example_sentences}
if "final_inquiry_question" not in st.session_state:
    st.session_state.final_inquiry_question = ""

st.set_page_config(page_title="개념기반 탐구 수업 도구", layout="wide")

with st.sidebar:
    
    st.markdown("<h3 style='text-align:center; margin-bottom:11px;'>학습 주제를 선택하세요</h3>", unsafe_allow_html=True)
    with st.container():
        selected_topic = st.selectbox(
            "주제 선택",
            ["-- 주제를 선택하세요 --"] + list(lens_map.keys()),
            label_visibility="collapsed"
        )
    st.markdown("---")
    st.markdown("<h3 style='text-align:center; margin-bottom:10px;'>개념 렌즈</h3>", unsafe_allow_html=True)
    if selected_topic != "-- 주제를 선택하세요 --":
        st.markdown(
            f"<div class='sidebar-lens-box'>{lens_map[selected_topic]}</div>",
            unsafe_allow_html=True
        )
    else:
        st.info("학습 주제를 선택하면 표시됩니다.")
    st.markdown("---")
    
    st.markdown("<h3 style='text-align:center; margin-bottom:12px;'>OpenAI API 키 입력</h3>", unsafe_allow_html=True)
    with st.container():
        api_key_input = st.text_input(
            "API 키 입력", type="password",
            value=st.session_state.openai_api_key,
            help="API 키를 입력해 주세요.",
            label_visibility="collapsed"
        )
    if api_key_input != st.session_state.openai_api_key:
        st.session_state.openai_api_key = api_key_input
        st.success("API 키가 저장되었습니다.")

    st.markdown("---")

    st.markdown("<h3 style='text-align:center; margin-bottom:10px;'>PDF 저장하기</h3>", unsafe_allow_html=True)
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
                pdf.cell(200, 10, txt=f"[{category}]", ln=True)
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

st.markdown("<h1 class='main-title'>개념 익히기</h1>", unsafe_allow_html=True)

client = None
if st.session_state.openai_api_key.strip() != "":
    try:
        client = OpenAI(api_key=st.session_state.openai_api_key)
    except Exception as e:
        st.error(f"OpenAI 클라이언트 초기화 오류: {e}")

def get_local_feedback(sentence, user_choice, concept_lens):
    if user_choice not in ["예시", "비예시"]:
        return ""
    correct = truth_data.get(sentence, {}).get(user_choice, None)
    if correct is None:
        return "⚠️ 이 문장에 대한 정답 데이터가 없습니다."
    if correct:
        return ""
    else:
        return f"⚠️ '{concept_lens}'의 어떤 특성을 반영하는지 생각해보세요."

def suggest_inquiry_questions(topic, concept_lens, leading_concept_list, num_questions=5):
    if client is None:
        return ["⚠️ API 키를 입력해야 AI의 제안 기능이 동작합니다."]
    prompt = (
        f"학습 주제: {topic}\n"
        f"개념 렌즈: {concept_lens}\n"
        f"주도 개념: {', '.join(leading_concept_list)}\n\n"
        "아래 조건을 모두 만족하는 탐구 질문을 각각 한 줄씩 여러 개 생성해줘.\n"
        "- 탐구 질문은 반드시 무엇, 왜, 어떻게 등 다양한 의문어로 시작\n"
        "- 각 질문에는 주도 개념 중 최소 한 가지가 반드시 포함되어야 함\n"
        "- 각 질문은 학습 주제와 깊은 관련이 있어야 함\n"
        "- 너무 짧지 않고 탐구 가치가 있는 내용을 만들어야 함\n"
        "- 출력은 번호 없이 각 질문을 한 줄씩 나열만 해줘"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "너는 과학 개념기반 수업에서 탐구 질문을 다양하게 제안하는 지능형 조력자다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        lines = [q.strip() for q in response.choices[0].message.content.strip().split('\n') if q.strip()]
        return lines
    except Exception as e:
        return [f"API 호출 오류: {e}"]

def give_inquiry_feedback(user_input, topic, leading_concept_list):
    import re

    # 학습 주제별 키워드(의미적 관련성 체크)
    topic_keywords = {
        "생태계와 환경 변화": ["생태계", "환경", "상호작용", "상호 작용", "변화", "생물", "환경 변화", "에너지 흐름", "평형"],
        "진화와 생물 다양성": ["진화", "생물 다양성", "자연선택", "변화", "종", "적응"]
    }

    # 의문사 및 의미 유사 표현 목록
    interrogative_variants = ["무엇", "어떻게", "왜", "어떠", "뭐", "무슨", "어떤"]

    feedbacks = []
    # 여러 문장 분리 (최대 5개, 빈 문장 제거)
    questions = [q.strip() for q in user_input.split('\n') if q.strip()]
    questions = questions[:5]

    topic_kw = topic_keywords.get(topic, [])
    user_lower = user_input.lower()

    for idx, question in enumerate(questions, start=1):
        q_lower = question.lower()

        # 1) 학습 주제 관련성 체크 (키워드 포함 여부)
        related = any(kw.lower() in q_lower for kw in topic_kw)

        # 2) 주도 개념 포함 여부 (소문자 비교)
        concept_found = any(concept.lower() in q_lower for concept in leading_concept_list)

        # 3) 의문사 포함 여부 (의미적 유사 포함)
        inter_found = any(re.search(iv, question) for iv in interrogative_variants)

        # 개별 질문에 피드백 작성 (타당하면 피드백 안 줌, 부적절하면 경고를 담음)
        lines = []
        if not related:
            lines.append("‣ 학습 주제와 관련된 내용이 포함되어 있지 않습니다.")
        if not concept_found:
            lines.append(f"‣ 주도 개념({', '.join(leading_concept_list)}) 중 하나 이상을 포함해 주세요.")
        if not inter_found:
            lines.append("‣ 탐구 질문에 '무엇', '어떻게', '왜' 중 하나 또는 유사 의문사를 포함해 주세요.")

        if lines:
            feedbacks.append(f"{idx}번 질문: " + " ".join(lines))

    # 전체 피드백 텍스트를 HTML 줄바꿈으로 합침
    return "<br>".join(feedbacks)


if selected_topic != "-- 주제를 선택하세요 --":
    concept_lens = lens_map[selected_topic]
    st.markdown("---")
    st.markdown("<div class='section-header'>1. 개념 정의 및 특성</div>", unsafe_allow_html=True)
    st.markdown("<div class='concepttitle'>개념 렌즈</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='main-lens-box'>{lens_map[selected_topic]}</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='concepttitle'>정의</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='definition-card'>{lens_data[concept_lens]['정의']}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='concepttitle'>특징</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='feature-card'>{lens_data[concept_lens]['특징']}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div class='section-header'>2. 예시/비예시 선택 및 피드백</div>", unsafe_allow_html=True)
    st.markdown("<div class='example-guide'>다음 문장이 개념 렌즈의 사례라고 생각되면 예시, 그렇지 않으면 비예시를 선택하세요.</div>", unsafe_allow_html=True)
    for idx, sent in enumerate(example_sentences):
        cols = st.columns([6, 4])
        with cols[0]:
            st.markdown(f"<span style='font-weight:bold; font-size:17px;'>{sent}</span>", unsafe_allow_html=True)
        with cols[1]:
            prev_value = st.session_state.sentence_assignments[sent]
            choice = st.radio(
                "", ["예시", "비예시", "미선택"],
                index=["예시", "비예시", "미선택"].index(prev_value if prev_value else "미선택"),
                key=f"radio_{idx}", horizontal=True, label_visibility="collapsed"
            )
            st.session_state.sentence_assignments[sent] = choice if choice != "미선택" else None
        user_choice = st.session_state.sentence_assignments[sent]
        feedback = get_local_feedback(sent, user_choice, concept_lens)
        if feedback:
            st.markdown(f"<div class='feedback-warning'>피드백: '{concept_lens}'의 어떤 특성을 반영하는지 생각해보세요.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div class='section-header'>3. 주도 개념</div>", unsafe_allow_html=True)
    st.markdown("<div class='inquiry-guide'>주도 개념은 단원에서의 핵심 주제를 말합니다.</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='leading-box'>{', '.join(leading_concepts[selected_topic])}</div>", unsafe_allow_html=True)


    st.markdown("---")
    st.markdown("<div class='section-header'>4. 탐구 질문 만들기</div>", unsafe_allow_html=True)
    st.markdown(f"<span style='font-size:20px; font-weight:600;'> 1) '{selected_topic}'에 대한 탐구 질문을 작성해보세요.</span>", unsafe_allow_html=True)
    st.markdown("<div class='inquiry-guide'>* 단원과 관련하여 주도 개념에 대해 떠오르는 의문을 작성해보세요.</div>", unsafe_allow_html=True)
    st.markdown("<div class='inquiry-limit'>* 각 질문마다 무엇을, 어떻게, 왜 중 한 가지를 사용해보세요.</div>", unsafe_allow_html=True)
    st.markdown("<div class='inquiry-limit'>* 최대 5개까지  작성할 수 있습니다.</div>", unsafe_allow_html=True)
    user_question = st.text_area(
        "",
        value="",
        max_chars=1000,
        height=130,
        key="user_inquiry_input"
    )
    # ----------------- 여기부터 수정된 피드백 출력 코드 -----------------
    if user_question.strip():
        feedback_html = give_inquiry_feedback(user_question, selected_topic, leading_concepts[selected_topic])
        if feedback_html.strip():
            st.markdown(f"<div class='feedback-warning'>{feedback_html}</div>", unsafe_allow_html=True)
    # --------------------------------------------------------------

    st.markdown("---")
    st.markdown("<span style='font-size:20px; font-weight:600;'> 2) AI가 제안하는 탐구 질문을 자신이 작성한 것과 비교해보세요.</span>", unsafe_allow_html=True)
    st.markdown("<div class='final-inquiry'>* AI의 제안</div>", unsafe_allow_html=True)
    suggestions = suggest_inquiry_questions(
        selected_topic, concept_lens, leading_concepts[selected_topic]
    )
    for q in suggestions:
        st.markdown(f"<div class='ai-suggestion'>{q}</div>", unsafe_allow_html=True)


    st.markdown("---")
    st.markdown("<span style='font-size:20px; font-weight:600;'> 3) 최종 탐구 질문을 작성해보세요.</span>", unsafe_allow_html=True)
    st.markdown("<div class='final-guide'>* 자신이 작성한 것 또는 AI가 제안한 것 중 선택 또는 수정해도 괜찮습니다.</div>", unsafe_allow_html=True)
    final_question = st.text_area(
        "",
        value=st.session_state.final_inquiry_question,
        max_chars=1000,
        height=130,
        key="final_inquiry_question"
    )
else:
    st.info("왼쪽 사이드바에서 학습 주제를 선택하세요.")
