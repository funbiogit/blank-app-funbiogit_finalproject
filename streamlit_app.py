import streamlit as st
import io
from fpdf import FPDF

# -------------------------------
# 0. 데이터 정의
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
    "진화와 생물 다양성": "변화",
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
# 1. 세션 상태 초기화
# -------------------------------
if 'sentence_assignments' not in st.session_state:
    # 문장별 상태: "예시" or "비예시" or None
    st.session_state['sentence_assignments'] = {sent: None for sent in example_sentences}

# -------------------------------
# 2. UI 설정
# -------------------------------
st.set_page_config(page_title="개념기반 탐구 수업 도구", layout="wide")
st.title("🧠 개념기반 탐구 수업 도구")

# -------------------------------
# 3. 사이드바
# -------------------------------
with st.sidebar:
    selected_topic = st.selectbox(
        "### 학습 주제를 선택하세요:",
        ["-- 주제를 선택하세요 --"] + list(lens_map.keys())
    )

    st.markdown("---")
    st.markdown("### 🔍 개념 렌즈")
    if selected_topic != "-- 주제를 선택하세요 --":
        st.success(f"**{lens_map[selected_topic]}**")
    else:
        st.info("학습 주제를 선택하면 표시됩니다.")

    st.markdown("---")
    if st.button("📄 PDF 저장하기"):
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("Arial", "", fname="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="개념기반 탐구 수업 - 예시/비예시 선택 내용", ln=True, align='C')
        pdf.ln(10)

        selected_examples = [s for s, v in st.session_state['sentence_assignments'].items() if v == "예시"]
        selected_nonexamples = [s for s, v in st.session_state['sentence_assignments'].items() if v == "비예시"]

        if selected_examples:
            pdf.set_text_color(0, 128, 0)
            pdf.cell(200, 10, txt="[예시]", ln=True)
            for ex in selected_examples:
                pdf.cell(200, 10, txt=f"- {ex}", ln=True)

        if selected_nonexamples:
            pdf.set_text_color(200, 0, 0)
            pdf.cell(200, 10, txt="[비예시]", ln=True)
            for ne in selected_nonexamples:
                pdf.cell(200, 10, txt=f"- {ne}", ln=True)

        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        st.download_button(
            "PDF 다운로드",
            data=pdf_output.getvalue(),
            file_name="개념기반탐구.pdf",
            mime="application/pdf"
        )

# -------------------------------
# 4. 사이드바 밖에서 concept_lens 정의 (중요!)
# -------------------------------
if selected_topic != "-- 주제를 선택하세요 --":
    concept_lens = lens_map[selected_topic]
else:
    concept_lens = None

# -------------------------------
# 5. 본문 UI
# -------------------------------
if concept_lens:
    st.markdown("### 1. 개념 정의 및 특성")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### **정의**")
        st.info(lens_data[concept_lens]["정의"])
    with col2:
        st.markdown("##### **특징**")
        st.success(lens_data[concept_lens]["특징"])

    st.markdown("---")
    st.markdown("##### 에 해당하는 문장은 예시로, 해당하지 않는 문장은 비예시로 선택하세요.")

    col3, col4 = st.columns(2)

    assigned_examples = [s for s, v in st.session_state['sentence_assignments'].items() if v == "예시"]
    assigned_nonexamples = [s for s, v in st.session_state['sentence_assignments'].items() if v == "비예시"]

    with col3:
        st.markdown("##### ✏️ 예시")
        if assigned_examples:
            for s in assigned_examples:
                st.write(f"- {s}")
        else:
            st.info("아직 예시가 없습니다.")

    with col4:
        st.markdown("##### ❌ 비예시")
        if assigned_nonexamples:
            for s in assigned_nonexamples:
                st.write(f"- {s}")
        else:
            st.info("아직 비예시가 없습니다.")

    st.markdown("---")
    st.markdown("### 전체 문장별 예시/비예시/미선택 구분")

    for idx, sent in enumerate(example_sentences):
        current_value = st.session_state['sentence_assignments'].get(sent, None)
        selection = st.radio(
            label=sent,
            options=["예시", "비예시", "미선택"],
            index={"예시": 0, "비예시": 1, None: 2}[current_value],
            key=f"assign_{idx}",
            horizontal=True
        )
        st.session_state['sentence_assignments'][sent] = selection if selection != "미선택" else None

    st.markdown("---")
    st.markdown("### 2. 주도 개념")
    if selected_topic in leading_concepts:
        st.markdown(", ".join([f"**{c}**" for c in leading_concepts[selected_topic]]))

    st.markdown("### 3. 개념 렌즈 또는 주도 개념에 기반한 질문을 작성해 보세요")
    user_question = st.text_input("질문을 입력하세요")
    if user_question:
        st.markdown("🧠 **AI 피드백 예시**")
        lens_matched = concept_lens in user_question
        concepts_matched = any(concept in user_question for concept in leading_concepts[selected_topic])
        if lens_matched:
            st.success(f"👍 이 질문은 개념 렌즈 ‘{concept_lens}’와 관련이 있습니다.")
        if concepts_matched:
            matched = [c for c in leading_concepts[selected_topic] if c in user_question]
            st.success(f"👍 이 질문은 주도 개념과 관련이 있습니다: {', '.join(matched)}")
        if not lens_matched and not concepts_matched:
            st.warning("❗ 이 질문은 개념 렌즈나 주도 개념과 명확한 관련이 없어 보입니다.")
