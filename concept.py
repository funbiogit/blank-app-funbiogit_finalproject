import streamlit as st
import io
from fpdf import FPDF
from openai import OpenAI


# -------------------------------
# 데이터 정의 및 정답 매핑
# -------------------------------
lens_data = {
    "관계": {
        "정의": "관계는 두 개 이상의 요소가 한 방향 또는 상호 영향을 주고받는 방식이나 연결 방식을 의미한다.",
        "특징": "- 각 요소 중 하나 이상에 변화가 나타남\n- 요소 간 주고받는 영향을 통해 복합적인 의미가 나타남"
    },
    "변화": {
        "정의": "하나의 형태, 상태, 가치가 다른 형태, 상태, 가치로 전환, 변형 또는 이동하는 현상을 말한다.",
        "특징": "- 원인, 과정, 결과의 틀 속에서 무엇이, 왜, 어떻게 달라지는지 설명할 수 있음\n- 연속적 혹은 불연속적으로 일어날 수 있음"
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


# -------------------------------
# 세션 상태 초기화
# -------------------------------
if "sentence_assignments" not in st.session_state:
    st.session_state.sentence_assignments = {s: None for s in example_sentences}


if "feedback_cache" not in st.session_state:
    st.session_state.feedback_cache = {}


if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""


if "reason_explanations" not in st.session_state:
    st.session_state.reason_explanations = {s: "" for s in example_sentences}

# 새로 추가: 사용자가 AI 제안 외에 최종적으로 직접 작성 또는 수정한 질문 저장 공간
if "final_inquiry_question" not in st.session_state:
    st.session_state.final_inquiry_question = ""

# -------------------------------
# 페이지 설정
# -------------------------------
st.set_page_config(page_title="개념기반 탐구 수업 도구", layout="wide")


# -------------------------------
# 사이드바: OpenAI API 키 입력 + 주제 선택 + PDF 생성
# -------------------------------
with st.sidebar:
    st.markdown("<h3 style='text-align:center;'>🔑 OpenAI API 키 입력</h3>", unsafe_allow_html=True)
    api_key_input = st.text_input(
        "API 키 입력 (https://platform.openai.com/account/api-keys 발급)", 
        type="password", 
        value=st.session_state.openai_api_key,
        help="API 키를 입력해 주세요."
    )
    if api_key_input != st.session_state.openai_api_key:
        st.session_state.openai_api_key = api_key_input
        st.success("API 키가 저장되었습니다.")


    st.markdown("---")
    st.markdown("<h3 style='text-align:center;'>학습 주제를 선택하세요</h3>", unsafe_allow_html=True)
    selected_topic = st.selectbox("", ["-- 주제를 선택하세요 --"] + list(lens_map.keys()))


    st.markdown("---")
    st.markdown("<h3 style='text-align:center;'>🔍 개념 렌즈</h3>", unsafe_allow_html=True)
    if selected_topic != "-- 주제를 선택하세요 --":
        st.markdown(
            f"<div style='text-align:center; background-color:#d4f8d4; padding:10px; border-radius:5px; font-size:18px;'>"
            f"{lens_map[selected_topic]}</div>", unsafe_allow_html=True)
    else:
        st.info("학습 주제를 선택하면 표시됩니다.")


    st.markdown("---")
    st.markdown("<h3 style='text-align:center;'>📄 PDF 저장하기</h3>", unsafe_allow_html=True)
    if st.button("PDF 생성"):
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
        st.download_button("PDF 다운로드", data=buf.getvalue(), file_name="개념기반탐구.pdf", mime="application/pdf")


# -------------------------------
# 메인 타이틀
# -------------------------------
st.title("🧠 개념 익히기")


# -------------------------------
# OpenAI API 클라이언트 초기화 (질문 제안용)
# -------------------------------
client = None
if st.session_state.openai_api_key.strip() != "":
    try:
        client = OpenAI(api_key=st.session_state.openai_api_key)
    except Exception as e:
        st.error(f"OpenAI 클라이언트 초기화 오류: {e}")


# -------------------------------
# 예시/비예시 피드백 (API 없이 로컬 판단)
# -------------------------------
def get_local_feedback(sentence, user_choice, concept_lens):
    if user_choice not in ["예시", "비예시"]:
        return ""
    correct = truth_data.get(sentence, {}).get(user_choice, None)
    if correct is None:
        return "⚠️ 이 문장에 대한 정답 데이터가 없습니다."
    if correct:
        return ""  # 적절한 선택이면 피드백 없음
    else:
        return f"⚠️ '{concept_lens}'의 어떤 특성을 반영하는지 생각해보세요."


# -------------------------------
# AI 탐구 질문 제안 (OpenAI API)
# -------------------------------
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
        f"- 출력은 번호 없이 각 질문을 한 줄씩 나열만 해줘"
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


# -------------------------------
# 본문: 주제 선택 후 UI 및 기능 구현
# -------------------------------
if selected_topic != "-- 주제를 선택하세요 --":
    concept_lens = lens_map[selected_topic]

    st.markdown("### 1. 개념 정의 및 특성")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 정의")
        st.info(lens_data[concept_lens]["정의"])
    with col2:
        st.markdown("#### 특징")
        st.success(lens_data[concept_lens]["특징"])

    st.markdown("---")
    st.markdown("### 2. 예시/비예시 선택 및 피드백")
    st.markdown("##### 다음 문장이 개념 렌즈의 사례라고 생각되면 예시, 그렇지 않으면 비예시를 선택하세요.")
    for idx, sent in enumerate(example_sentences):
        cols = st.columns([6, 4])
        with cols[0]:
            st.markdown(f"<span style='font-weight:bold; font-size:18px;'>{sent}</span>", unsafe_allow_html=True)
        with cols[1]:
            prev_value = st.session_state.sentence_assignments[sent]
            choice = st.radio(
                "", ["예시", "비예시", "미선택"],
                index=["예시", "비예시", "미선택"].index(prev_value if prev_value else "미선택"),
                key=f"radio_{idx}", horizontal=True, label_visibility="collapsed"
            )
            st.session_state.sentence_assignments[sent] = choice if choice != "미선택" else None

        # 피드백 영역
        user_choice = st.session_state.sentence_assignments[sent]
        feedback = get_local_feedback(sent, user_choice, concept_lens)
        if feedback:
            st.markdown(f"**피드백:** {feedback}")
        else:
            st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 3. 주도 개념")

    # 크기를 50%로, 가운데 정렬 스타일
    green_box_html = f"""
    <div style="
        background-color:#d4f8d4; 
        padding:10px; 
        border-radius:5px; 
        font-size:16px; 
        width:50%; 
        margin-left:auto; 
        margin-right:auto; 
        text-align:center;">
        {', '.join(leading_concepts[selected_topic])}
    </div>
    """
    st.markdown(green_box_html, unsafe_allow_html=True)

    st.markdown("---")  # 4번 질문 입력 전 구분선 추가
    st.markdown("### 4. 탐구 질문 만들기")

    # 4. 질문 입력 변경 부분: 안내문과 텍스트 영역 추가
    st.markdown(f"사용자가 선택한 학습 주제 **'{selected_topic}'**와 관련하여 주도 개념을 활용한 탐구 질문을 생각하여 작성하세요.")
    user_question = st.text_area(
        "탐구 질문을 작성하세요 (최대 5문장까지 작성할 수 있습니다.)",
        value="",
        max_chars=1000,  # 글자수 제한 임의 설정 (5문장 정도 넉넉히)
        height=130,
        key="user_inquiry_input"
    )

    st.markdown("#### AI의 제안")
    suggestions = suggest_inquiry_questions(
        selected_topic, concept_lens, leading_concepts[selected_topic]
    )
    for q in suggestions:
        st.markdown(f"- {q}")

    # 사용자 최종 수정/선택 질문 입력란 추가
    st.markdown("#### 최종적으로 선택하거나 수정한 탐구 질문을 작성하세요.")
    final_question = st.text_area(
        "최종 탐구 질문 입력",
        value=st.session_state.final_inquiry_question,
        max_chars=1000,
        height=130,
        key="final_inquiry_question"
    )

else:
    st.info("왼쪽 사이드바에서 학습 주제를 선택하세요.")
