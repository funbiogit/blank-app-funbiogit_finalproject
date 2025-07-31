import streamlit as st
import openai
import io
from fpdf import FPDF
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # 환경변수에서 API 키를 불러옴

# -------------------------------
# 데이터 정의
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
    "세포는 하나의 생명 시스템이다.",
    "멜라닌을 합성하는 효소가 많은 사람은 피부색이 어둡다.",
    "DNA의 염기 서열의 변화로 단백질의 입체구조가 바뀌었다.",
    "온도를 높였더니 효소의 활성이 나타나지 않았다.",
    "엽록체는 광합성을 수행한다.",
    "세포막은 인지질과 단백질로 이루어져 있다.",
    "다른 생명체에서 채취한 유전자를 삽입해 생명체에 새로운 특성이 부여된다.",
    "효소는 기질 특이성이 있다."
]

# -------------------------------
# 세션 상태 초기화
# -------------------------------
if "sentence_assignments" not in st.session_state:
    st.session_state.sentence_assignments = {s: None for s in example_sentences}

if "feedback_cache" not in st.session_state:
    st.session_state.feedback_cache = {}

# -------------------------------
# 개념 렌즈 관련성 판단 함수 (OpenAI API)
# -------------------------------
def check_relevance(sentence, concept_lens):
    cache_key = (sentence, concept_lens)
    if cache_key in st.session_state.feedback_cache:
        return st.session_state.feedback_cache[cache_key]

    prompt = (
        f"문장: \"{sentence}\"\n"
        f"개념 렌즈: \"{concept_lens}\"\n"
        "위 문장이 해당 개념 렌즈와 의미적으로 관련이 있는지 판단하세요. "
        "관련 있다면 '관련 있음', 관련 없다면 '관련 없음'이라고만 답하세요."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "너는 과학 교과에서 개념 기반 수업을 도와주는 조력자야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        result = response['choices'][0]['message']['content'].strip()
        st.session_state.feedback_cache[cache_key] = result
        return result
    except Exception as e:
        return "오류 발생"

# -------------------------------
# UI 구성
# -------------------------------
st.set_page_config(page_title="개념기반 탐구 수업 도구", layout="wide")
st.title("🧠 개념기반 탐구 수업 도구")

with st.sidebar:
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
            pdf.set_text_color(0, 128, 0) if category == "예시" else pdf.set_text_color(200, 0, 0)
            pdf.cell(200, 10, txt=f"[{category}]", ln=True)
            for s, v in st.session_state.sentence_assignments.items():
                if v == category:
                    pdf.cell(200, 10, txt=f"- {s}", ln=True)

        buf = io.BytesIO()
        pdf.output(buf)
        buf.seek(0)
        st.download_button("PDF 다운로드", data=buf.getvalue(), file_name="개념기반탐구.pdf", mime="application/pdf")

# -------------------------------
# 본문 영역
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
    st.markdown("### 2. 예시/비예시 선택")
    for idx, sent in enumerate(example_sentences):
        cols = st.columns([6, 2])
        with cols[0]:
            st.write(sent)
        with cols[1]:
            prev_value = st.session_state.sentence_assignments[sent]
            choice = st.radio(
                "", ["예시", "비예시", "미선택"],
                index=["예시", "비예시", "미선택"].index(prev_value if prev_value else "미선택"),
                key=f"radio_{idx}", horizontal=True, label_visibility="collapsed"
            )
            st.session_state.sentence_assignments[sent] = choice if choice != "미선택" else None

    # -------------------------------
    # 결과 및 피드백
    # -------------------------------
    st.markdown("---")
    st.markdown("### ✅ 예시/비예시 구분 및 피드백")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("✏️ 예시")
        for s, v in st.session_state.sentence_assignments.items():
            if v == "예시":
                st.markdown(f"- {s}")
                feedback = check_relevance(s, concept_lens)
                if "관련 있음" in feedback:
                    st.success("✔️ 개념 렌즈와 관련 있음")
                elif "관련 없음" in feedback:
                    st.warning("⚠️ 개념 렌즈와 관련 없음")
                else:
                    st.error("❗ 판단 불가")

    with col_right:
        st.subheader("❌ 비예시")
        for s, v in st.session_state.sentence_assignments.items():
            if v == "비예시":
                st.markdown(f"- {s}")
                feedback = check_relevance(s, concept_lens)
                if "관련 있음" in feedback:
                    st.warning("⚠️ 개념 렌즈와 관련 있음")
                elif "관련 없음" in feedback:
                    st.success("👍 비예시로 적절함")
                else:
                    st.error("❗ 판단 불가")

    # -------------------------------
    # 주도 개념 + 질문 입력
    # -------------------------------
    st.markdown("---")
    st.markdown("### 3. 주도 개념")
    green_box = (
        "<div style='background-color:#d4f8d4; padding:10px; border-radius:5px; font-size:18px;'>"
        + ", ".join(leading_concepts[selected_topic]) + "</div>"
    )
    st.markdown(green_box, unsafe_allow_html=True)

    st.markdown("### 4. 질문을 입력하세요")
    user_question = st.text_input("개념 렌즈 또는 주도 개념을 활용한 탐구 질문을 작성하세요")
    if user_question:
        st.markdown("🧠 AI 피드백")
        lens_hit = concept_lens in user_question
        concept_hit = [c for c in leading_concepts[selected_topic] if c in user_question]
        if lens_hit:
            st.success(f"👍 개념 렌즈 '{concept_lens}'와 관련 있음")
        if concept_hit:
            st.success(f"👍 주도 개념과 관련 있음: {', '.join(concept_hit)}")
        if not lens_hit and not concept_hit:
            st.warning("❗ 개념 렌즈나 주도 개념과의 관련성이 명확하지 않습니다.")
