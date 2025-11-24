import streamlit as st
import random
from collections import Counter

# ==================== 초기 설정 ====================
if "coins" not in st.session_state:
    st.session_state.coins = 0
if "inventory" not in st.session_state:
    st.session_state.inventory = {}
if "items" not in st.session_state:
    st.session_state.items = {}
if "location" not in st.session_state:
    st.session_state.location = "강"

# 물고기 확률
fish_prob = {
    "멸치": 25, "복어": 25, "누치": 20, "정어리": 15,
    "붕어": 10, "전갱이": 10, "꽁치": 10, "은어": 10,
    "볼락": 6, "열기": 6, "노래미": 6, "고등어": 5,
    "메기": 4, "잉어": 4, "쥐치": 4,
    "돌돔": 2, "연어": 2,
    "참돔": 1, "참치": 1
}

# 가격표
fish_price = {
    "멸치": 10, "복어": 10, "누치": 15, "정어리": 15,
    "붕어": 20, "전갱이": 20, "꽁치": 20, "은어": 20,
    "볼락": 40, "열기": 40, "노래미": 40, "고등어": 50,
    "메기": 60, "잉어": 60, "쥐치": 60,
    "돌돔": 120, "연어": 150,
    "참돔": 200, "참치": 300
}

# 대물 확률
rare_fish = {
    "황금참치": ("참치", 0.5, 1200),
    "무지개참돔": ("참돔", 0.7, 900),
    "왕연어": ("연어", 1, 600)
}

# 잃어버린 섬 특별 물고기
island_fish = {
    "킹크랩": 5, "개복치": 3, "메가참치": 2, "번개상어": 1, "심연참돔": 1
}

# ==================== UI ====================
st.title("🎣 Streamlit 낚시 게임")
st.write(f"💰 현재 코인: **{st.session_state.coins} 코인**")

# --------------------------------------------- 위치 선택
location = st.selectbox("어디서 낚시할까?", ["강", "바다", "잃어버린 섬"])
st.session_state.location = location

# --------------------------------------------- 낚시 버튼
if st.button("🐟 낚시하기!"):
    fish_list = list(fish_prob.keys())
    weights = list(fish_prob.values())

    # 잃어버린 섬 보정
    if st.session_state.location == "잃어버린 섬":
        for i, f in enumerate(fish_list):
            if f in island_fish:
                weights[i] *= 25
            else:
                weights[i] /= 10

        # 섬 고유 물고기 추가
        for f, p in island_fish.items():
            fish_list.append(f)
            weights.append(p)

    # 확률 기반 선택
    caught = random.choices(fish_list, weights=weights, k=1)[0]

    # 대물 변환 체크
    for rf, (base, chance, price) in rare_fish.items():
        if caught == base and random.random() < chance:
            caught = rf
            fish_price[rf] = price
            break

    st.success(f"🐠 잡았다! **{caught}**")

    # 인벤토리 저장
    st.session_state.inventory[caught] = st.session_state.inventory.get(caught, 0) + 1

# --------------------------------------------- 인벤토리
st.subheader("📦 인벤토리")
if st.session_state.inventory:
    for f, c in st.session_state.inventory.items():
        st.write(f"{f}: {c} 마리")
else:
    st.write("비어있음")

# --------------------------------------------- 판매
st.subheader("💸 물고기 판매")
if st.session_state.inventory:
    sell_fish = st.selectbox("판매할 물고기", list(st.session_state.inventory.keys()))
    qty = st.number_input("판매 수량", min_value=1, max_value=st.session_state.inventory[sell_fish])

    if st.button("판매하기"):
        earned = fish_price.get(sell_fish, 10) * qty
        st.session_state.coins += earned
        st.session_state.inventory[sell_fish] -= qty
        if st.session_state.inventory[sell_fish] == 0:
            del st.session_state.inventory[sell_fish]
        st.success(f"💰 {earned} 코인 획득!")
else:
    st.write("팔 물고기가 없습니다")
