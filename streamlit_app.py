import streamlit as st
import random

# ================= 세션 초기화 =================
for key, default in [("coin",0), ("inventory",[]), ("shop_open",False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ================= 물고기 & 확률 =================
fish_prob = {
    "멸치": 25,
    "복어": 25,
    "누치": 20,
    "연어": 10,
    "참치": 5
}

fish_list = list(fish_prob.keys())
fish_weights = list(fish_prob.values())

price_map = {
    "멸치": 10, "복어": 10, "누치": 15, "연어": 45, "참치": 95
}

# ================= UI =================
st.title("🎣 확률 낚시 게임")
st.divider()

col1, col2, col3 = st.columns(3)

# --- 낚시 ---
with col1:
    st.subheader("🎣 낚시하기")
    if st.button("1번 낚시", key="fish1"):
        fish = random.choices(fish_list, weights=fish_weights, k=1)[0]
        st.session_state.inventory.append(fish)
        st.success(f"{fish} 낚았다!")

    if st.button("2번 낚시", key="fish2"):
        fish = random.choices(fish_list, weights=fish_weights, k=2)
        st.session_state.inventory.extend(fish)
        st.success(f"{', '.join(fish)} 낚았다!")

# --- 인벤토리 ---
with col2:
    st.subheader("🎒 인벤토리")
    st.write(st.session_state.inventory)

# --- 상점 ---
with col3:
    st.subheader("🏪 상점")
    if st.button("상점 열기", key="open_shop"):
        st.session_state.shop_open = True

st.divider()

# --- 상점 로직 ---
if st.session_state.shop_open:
    st.subheader("🏪 상점")

    if not st.session_state.inventory:
        st.warning("팔 물고기가 없어!")
    else:
        selected = st.selectbox("판매할 물고기 선택", st.session_state.inventory)
        if st.button("판매하기", key="sell"):
            price = price_map.get(selected,0)
            st.session_state.coin += price
            st.session_state.inventory.remove(selected)
            st.success(f"{selected} 판매 완료! +{price} 코인")

    if st.button("상점 닫기", key="close_shop"):
        st.session_state.shop_open = False

# --- 코인 표시 ---
st.write(f"💰 현재 코인: {st.session_state.coin}")
