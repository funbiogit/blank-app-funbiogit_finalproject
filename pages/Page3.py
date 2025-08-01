import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# NanumGothic 폰트 경로 지정
font_path = "./fonts/NanumGothic-Regular.ttf"
fontprop = fm.FontProperties(fname=font_path)

# matplotlib에 폰트 등록 및 기본 폰트로 설정
plt.rcParams['font.family'] = fontprop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 깨짐 방지

st.title("Matplotlib 데이터 시각화 예시")

# 샘플 데이터 생성
x = np.arange(1, 11)
y = np.random.randint(10, 100, size=10)

# 그래프 그리기
fig, ax = plt.subplots()
ax.plot(x, y, marker='o', label='데이터 값', color='blue')
ax.set_title('샘플 데이터 그래프 (한글 제목)', fontproperties=fontprop)
ax.set_xlabel('X축 (한글)', fontproperties=fontprop)
ax.set_ylabel('Y축 (한글)', fontproperties=fontprop)
ax.legend(prop=fontprop)

# Streamlit에 그래프 표시
st.pyplot(fig)