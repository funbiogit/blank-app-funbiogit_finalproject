import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import os

# --- NanumGothic 한글폰트 강제 고정 ---
font_path = "fonts/NanumGothic.ttf"
if not os.path.isfile(font_path):
    st.error("fonts/NanumGothic.ttf 경로에 한글 폰트 파일이 필요합니다!")
fontprop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fontprop.get_name()
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="4단계 먹이사슬 시뮬레이션", layout="wide")
st.title("4단계 먹이 피라미드와 생태계 평형 시뮬레이터")

with st.sidebar:
    st.header("초기 개체수와 섭식률")
    P0 = st.number_input("생산자(풀) 초기 개체수", min_value=100, value=1000, step=50)
    H1_0 = st.number_input("1차소비자(토끼) 초기 개체수", min_value=1, value=120, step=1)
    H2_0 = st.number_input("2차소비자(여우) 초기 개체수", min_value=0, value=24, step=1)
    H3_0 = st.number_input("3차소비자(매) 초기 개체수", min_value=0, value=4, step=1)
    N = st.slider("진행 단계(시간)", 1, 200, 50, 1)
    st.markdown("### [Only] 섭식률(먹이관계 강도) 조절")
    b1 = st.slider("1차소비자 섭식률(b1; 풀→토끼)", 0.0005, 0.02, 0.002, 0.0005, format="%.4f")
    b2 = st.slider("2차소비자 섭식률(b2; 토끼→여우)", 0.0001, 0.008, 0.001, 0.0001, format="%.4f")
    b3 = st.slider("3차소비자 섭식률(b3; 여우→매)", 0.0001, 0.006, 0.0007, 0.0001, format="%.4f")
    st.info("*섭식률만 조작하며 각 수준의 변동·진동·파급효과를 확인하세요.")

a = 0.08         # 생산자 성장률
e1, d1 = 0.004, 0.022
e2, d2 = 0.002, 0.011
e3, d3 = 0.0012, 0.007

P = [P0]
H1 = [H1_0]
H2 = [H2_0]
H3 = [H3_0]
prev_dP = 0  # prev_dP 변수 초기화 오류 대응

for t in range(N):
    prev_P, prev_H1, prev_H2, prev_H3 = P[-1], H1[-1], H2[-1], H3[-1]

    prev_dH1 = H1[-1] - H1[-2] if t >= 1 else 0
    prev_dH2 = H2[-1] - H2[-2] if t >= 1 else 0
    prev_dH3 = H3[-1] - H3[-2] if t >= 1 else 0

    # --- 생산자 ---
    growth = a * prev_P
    loss_by_H1 = b1 * prev_P * prev_H1
    feedback1 = 0
    if prev_dH1 < 0:
        feedback1 = abs(prev_dH1) * (0.08 + 0.2*abs(np.tanh(prev_dH1/(prev_H1+0.1))))
    next_P = prev_P + growth - loss_by_H1 + feedback1
    next_P = max(next_P, 1)

    # --- 1차소비자 ---
    gain = e1 * b1 * prev_P * prev_H1
    nat_loss = d1 * prev_H1
    loss_by_H2 = b2 * prev_H1 * prev_H2
    feedback2 = 0
    if prev_dH2 < 0:
        feedback2 = abs(prev_dH2) * 0.09
    if prev_dP > 0:
        feedback2 += abs(prev_dP) * 0.047
    next_H1 = prev_H1 + gain - nat_loss - loss_by_H2 + feedback2
    next_H1 = max(next_H1, 1)

    # --- 2차소비자 ---
    gain2 = e2 * b2 * prev_H1 * prev_H2
    nat_loss2 = d2 * prev_H2
    loss_by_H3 = b3 * prev_H2 * prev_H3
    feedback3 = 0
    if prev_dH3 < 0:
        feedback3 = abs(prev_dH3) * 0.15
    if prev_dH1 > 0:
        feedback3 += abs(prev_dH1) * 0.04
    next_H2 = prev_H2 + gain2 - nat_loss2 - loss_by_H3 + feedback3
    next_H2 = max(next_H2, 0)

    # --- 3차소비자 ---
    gain3 = e3 * b3 * prev_H2 * prev_H3
    nat_loss3 = d3 * prev_H3
    feedback4 = 0
    if prev_dH2 > 0:
        feedback4 = abs(prev_dH2) * 0.032
    next_H3 = prev_H3 + gain3 - nat_loss3 + feedback4
    next_H3 = max(next_H3, 0)

    P.append(next_P)
    H1.append(next_H1)
    H2.append(next_H2)
    H3.append(next_H3)
    prev_dP = next_P - prev_P

# ---------- 1. 개체수 변화 그래프 ----------
st.subheader("🍀 개체수 변화 그래프 (상호 피드백 진동)")
levels = ["생산자", "1차소비자", "2차소비자", "3차소비자"]
t_list = np.arange(1, N+2)
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(t_list, P, label=levels[0], color="green")
ax.plot(t_list, H1, label=levels[1], color="orange")
ax.plot(t_list, H2, label=levels[2], color="red")
ax.plot(t_list, H3, label=levels[3], color="purple")
ax.set_xlabel("단계(시간, 1부터)", fontproperties=fontprop)
ax.set_ylabel("개체수", fontproperties=fontprop)
ax.grid(alpha=0.3)
ax.legend(prop=fontprop)
st.pyplot(fig)

# ---------- 2. 특정 단계의 피라미드 ----------
st.subheader("🌲 특정 단계에서의 생태 피라미드")
select_step = st.slider("피라미드로 보고 싶은 단계를 선택하세요", 1, N+1, N+1, 1)
curvals = [P[select_step-1], H1[select_step-1], H2[select_step-1], H3[select_step-1]]
maxv = max(curvals+[1])
fig2, ax2 = plt.subplots(figsize=(5, 6))
for i, (level, val) in enumerate(zip(levels, curvals)):
    width = val / maxv * 0.9
    ax2.barh([3-i], width, left=(1-width)/2, height=0.8, color=f"C{i}", edgecolor="k")
    ax2.text(1, 3-i, f"{level}: {int(val)}", va='center', ha='right', fontsize=14, fontweight='bold', fontproperties=fontprop)
ax2.set_xlim(0, 1)
ax2.set_yticks(range(4))
ax2.set_yticklabels(reversed(levels), fontsize=14, fontproperties=fontprop)
ax2.invert_yaxis()
ax2.axis('off')
st.pyplot(fig2)

# ---------- 3. 데이터 표 ----------
st.markdown("#### 단계별 개체수 변화 표")
data = {
    "단계": list(range(1, N+2)),
    "생산자": [int(x) for x in P],
    "1차소비자": [int(x) for x in H1],
    "2차소비자": [int(x) for x in H2],
    "3차소비자": [int(x) for x in H3],
}
st.dataframe(data)

st.markdown("""
- 단계별로 생산자와 각 소비자가 증가·감소를 반복하며, **상호 피드백** 메커니즘이 실제 자연처럼 작동하며 시각적으로 확인됩니다.
- 그래프와 피라미드, 표 모두 한글이 깨짐 없이 잘 표시됩니다.
""")
