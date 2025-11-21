import streamlit as st
import random

# ========== 세션 초기화 ==========
if "coin" not in st.session_state:
    st.session_state.coin = 0

if "inventory" not in st.session_state:
    st.session_state.inventory = []

if "shop_open" not in st.session_state:
    st.session_state.shop_open = False

# ========== 물고기 & 가격 ==========
fish_list = [
    "누치","정어리","붕어","빙어","북어","전갱이","꽁치","은어","노래미","고등어",
    "메기","잉어","쥐치","볼락","열기","줄돔","삼치","병어","향어","우럭",
    "송어","해파리","꼴뚜기","넙치","광어","농어","가물치","방어","바다송어",
    "해마","연어","쭈꾸미","아귀","한치","오징어","참치","홍어","랍스터",
    "가오리","상어","문어","발광오징어","킹크랩","전복"
]

price_map = {
    "멸치": 10, "복어": 10, "누치": 15, "정어리": 15,
    "붕어": 20, "빙어": 20, "북어": 20, "전갱이": 20, "꽁치": 20,
    "은어": 25,
    "노래미": 30, "고등어": 30, "메기": 30, "잉어": 30,
    "쥐치": 35, "볼락": 35, "열기": 35, "줄돔": 35, "향어": 35,
    "삼치": 40, "병어": 40,
    "우럭": 45, "송어": 45, "연어": 45,
    "해파리": 50,
    "꼴뚜기": 60, "넙치": 60,
    "광어": 70, "농어": 70, "가물치": 70,
    "방어": 75, "바다송어": 75, "해마": 75,
    "쭈꾸미": 80,
    "아귀": 85, "한치": 85,
    "오징어": 90,
    "참치": 95, "홍어": 95,
    "랍스터": 110, "가오리": 110,
    "상어": 120, "문어": 120, "발광오징어": 120, "킹크랩": 120, "전복": 120
}

# ========== UI ==========
st.title("🎣 낚시다!! - 낚시터 게임 -")
st.write("같이 낚시할래?")
st.divider()

col1, col2, col3, col4 = st.columns(4)

# --- 낚시 ---
with col1:
    st.subheader("🎣 낚시하기")
    if st.button("1번 낚시", key="fish1"):
        fish = random.choice(fish_list)
        st.session_state.inventory.append(fish)
        st.success(f"{fish} 낚았다!")

    if st.button("2번 낚시", key="fish2"):
        f1 = random.choice(fish_list)
        f2 = random.choice(fish_list)
        st.session_state.inventory.extend([f1, f2])
        st.success(f"{f1}, {f2} 낚았다!")

# --- 인벤토리 ---
with col2:
    st.subheader("🎒 인벤토리")
    st.write(st.session_state.inventory)

# --- 상점 ---
with col3:
    st.subheader("🏪 상점")
    if st.button("상점 열기", key="open_shop"):
        st.session_state.shop_open = True

# --- 코인 ---
with col4:
    st.subheader("💰 코인")
    st.write(f"{st.session_state.coin} 코인")

st.divider()

# ========== 상점 로직 ==========
if st.session_state.shop_open:
    st.subheader("🏪 상점")

    if len(st.session_state.inventory) == 0:
        st.warning("팔 물고기가 없어!")
    else:
        selected = st.selectbox("판매할 물고기 선택", st.session_state.inventory)

        if st.button("판매하기", key="sell"):
            price = price_map.get(selected, 0)
            st.session_state.coin += price
            st.session_state.inventory.remove(selected)
            st.success(f"{selected} 판매! +{price} 코인")

    if st.button("상점 닫기", key="close_shop"):
        st.session_state.shop_open = False
