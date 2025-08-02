import streamlit as st
import io
from fpdf import FPDF
from openai import OpenAI

st.markdown("""
<style>
    /* 사이드바: 모든 글자 검은색, 제목 크기+간격, 박스 간격 조정 */
    [data-testid="stSidebar"] * { color: black !important; }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h1 {
        font-size: 1.25rem !important; /* 기존보다 약간 크게 */
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

                /* 메인 개념 렌즈 - 사이드 박스와 스타일 동일하게 */
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

    /* 1. 개념정의/특성/렌즈 제목 폰트 동일+크게 */
    .concepttitle { font-size: 23px !important; text-align:center; font-weight:700; margin-bottom:4px; margin-top:8px;}

    /* 정의/특징 파란색 박스 */
    .definition-card, .feature-card {
        background: linear-gradient(135deg, #def7fe 0%, #e7eeff 100%);
        padding: 18px;
        border-radius: 12px;
        margin: 7px 0;
        box-shadow: 0 4px 13px rgba(51,153,255,0.09);
        font-size: 15px;
        border: none;
        color: #174a7c !important;
    }

    /* 2번 지시: 안내문 글자(작게) */
    .example-guide {
        font-size: 15px; color:#353535; font-weight:500; margin-top:6px; margin-bottom:4px;
    }
    /* 3. 주도 개념 박스: 분홍색, 폭 줄이기, 중앙 정렬! */
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

    /* 탐구질문: 모든 안내문 글자/AI/최종 동일계열, 크기/간격 */
    .inquiry-guide, .inquiry-limit, .final-inquiry, .final-guide {
        font-size: 15px;
        font-weight: 500;
        color: #203a4d;
        margin: 7px 0 4px 0;
        padding: 0;
    }
    /* AI 제안 더 작게 */
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

    /* 타이틀 스타일 - 왼쪽 정렬로 변경 */
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
</style>
""", unsafe_allow_html=True)

lens_data = {
    "관계": {
        "정의": "관계는 두 개 이상의 요소가 한 방향 또는 상호 영향을 주고받는 방식이나 연결 방식을 의미한다.",
        "특징": "- 각 요소 중 하나 이상에 변화가 나타남<br> - 요소 간 주고받는 영향을 통해 복합적인 의미가 나타남"
    },
    "변화": {
        "정의": "하나의 형태, 상태, 가치가 다른 형태, 상태, 가치로 전환, 변형 또는 이동하는 현상을 말한다.",
        "특징": "- 원인, 과정, 결과의 틀 속에서 무엇이, 왜, 어떻게 달라지는지 설명할 수 있음<br>- 연속적 혹은 불연속적으로 일어날 수 있음"
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
    "1. 세포는 하나의 생명 시스템이다.",
    "2. 멜라닌을 합성하는 효소가 많은 사람은 피부색이 어둡다.",
    "3. DNA의 염기 서열의 변화로 단백질의 입체구조가 바뀌었다.",
    "4. 온도를 높였더니 효소의 활성이 나타나지 않았다.",
    "5. 엽록체는 광합성을 수행한다.",
    "6. 세포막은 인지질과 단백질로 이루어져 있다.",
    "7. 다른 생명체에서 채취한 유전자를 삽입해 생명체에 새로운 특성이 부여된다.",
    "8. 효소는 기질 특이성이 있다."
]
truth_data = {
    "1. 세포는 하나의 생명 시스템이다.": {"예시": False, "비예시": True},
    "2. 멜라닌을 합성하는 효소가 많은 사람은 피부색이 어둡다.": {"예시": True, "비예시": False},
    "3. DNA의 염기 서열의 변화로 단백질의 입체구조가 바뀌었다.": {"예시": True, "비예시": False},
    "4. 온도를 높였더니 효소의 활성이 나타나지 않았다.": {"예시": True, "비예시": False},
    "5. 엽록체는 광합성을 수행한다.": {"예시": False, "비예시": True},
    "6. 세포막은 인지질과 단백질로 이루어져 있다.": {"예시": False, "비예시": True},
    "7. 다른 생명체에서 채취한 유전자를 삽입해 생명체에 새로운 특성이 부여된다.": {"예시": True, "비예시": False},
    "8. 효소는 기질 특이성이 있다.": {"예시": False, "비예시": True}
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
    st.markdown(f"<div class='leading-box'>{', '.join(leading_concepts[selected_topic])}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div class='section-header'>4. 탐구 질문 만들기</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='inquiry-guide'>'{selected_topic}'에 대한 탐구 질문을 작성해보세요.</div>", unsafe_allow_html=True)
    st.markdown("<div class='inquiry-guide'>주도개념 및 개념 렌즈가 포함되도록 <b>질문</b>을 구성하세요.</div>", unsafe_allow_html=True)
    user_question = st.text_area(
        "",
        value="",
        max_chars=1000,
        height=130,
        key="user_inquiry_input"
    )
    st.markdown("<div class='inquiry-limit'>탐구 질문을 최대 5문장까지 작성할 수 있습니다.</div>", unsafe_allow_html=True)
    st.markdown("<span style='font-size:20px; font-weight:600;'>AI의 제안</span>", unsafe_allow_html=True)
    suggestions = suggest_inquiry_questions(
        selected_topic, concept_lens, leading_concepts[selected_topic]
    )
    for q in suggestions:
        st.markdown(f"<div class='ai-suggestion'>{q}</div>", unsafe_allow_html=True)
    st.markdown("<div class='final-inquiry'>최종 탐구 질문을 작성해보세요.</div>", unsafe_allow_html=True)
    st.markdown("<div class='final-guide'>자신이 작성한 것 또는 AI가 제안한 것 중 선택 또는 수정해도 괜찮습니다.</div>", unsafe_allow_html=True)
    final_question = st.text_area(
        "",
        value=st.session_state.final_inquiry_question,
        max_chars=1000,
        height=130,
        key="final_inquiry_question"
    )
else:
    st.info("왼쪽 사이드바에서 학습 주제를 선택하세요.")
