import streamlit as st
import random

# ================= 세션 초기화 =================
if "coin" not in st.session_state:
    st.session_state.coin = 0
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "shop_open" not in st.session_state:
    st.session_state.shop_open = False

# ================= 물고기 & 가격 =================
fish_prob = {
    "멸치": 25, "복어": 25, "누치": 20, "정어리": 15, "붕어": 15,
    "빙어": 10, "북어": 10, "전갱이": 10, "꽁치": 10, "은어": 8,
    "노래미": 7, "고등어": 7, "메기": 6, "잉어": 6, "쥐치": 5
}

fish_list = list(fish_prob.keys())
fish_weights = list(fish_prob.values())
price_map = {fish: (prob+5)*2 for fish, prob in fish_prob.items()}

# ================= 합성 규칙 =================
# 동일 물고기 2마리 -> 상위 물고기 1마리
fusion_map = {
    "멸치": "대멸치", "복어": "대복어", "누치": "대누치",
    "정어리": "대정어리", "붕어": "대붕어"
}

# 상위 물고기 가격
for base, fused in fusion_map.items():
    price_map[fused] = price_map[base] * 2

# ================= UI =================
st.title("🎣 낚시 + 상점 + 합성")
st.divider()

col1, col2, col3 = st.columns(3)

# --- 낚시 ---
with col1:
    st.subheader("🎣 낚시하기")
    if st.button("1번 낚시"):
        fish = random.choices(fish_list, weights=fish_weights, k=1)[0]
        st.session_state.inventory.append(fish)
        st.success(f"{fish} 낚았다!")
    if st.button("2번 낚시"):
        fish = random.choices(fish_list, weights=fish_weights, k=2)
        st.session_state.inventory.extend(fish)
        st.success(f"{', '.join(fish)} 낚았다!")

# --- 인벤토리 ---
with col2:
    st.subheader("🎒 인벤토리")
    st.write("물고기:", st.session_state.inventory)

# --- 상점 ---
with col3:
    st.subheader("🏪 상점")
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open)
    st.session_state.shop_open = open_shop

st.divider()

# --- 상점 로직 ---
if st.session_state.shop_open:
    st.subheader("🏪 상점")
    if st.session_state.inventory:
        selected = st.selectbox("판매할 물고기 선택", st.session_state.inventory)
        if st.button("판매하기"):
            price = price_map.get(selected, 0)
            st.session_state.coin += price
            st.session_state.inventory.remove(selected)
            st.success(f"{selected} 판매 완료! +{price} 코인")
    else:
        st.warning("팔 물고기가 없습니다!")

# --- 합성 기능 ---
st.subheader("⚡ 물고기 합성")
fusion_candidates = [f for f in fusion_map.keys() if st.session_state.inventory.count(f) >= 2]

if fusion_candidates:
    selected_fuse = st.selectbox("합성할 물고기 선택", fusion_candidates)
    if st.button("합성하기"):
        # 50% 확률
        if random.choice([True, False]):
            # 성공
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.append(fusion_map[selected_fuse])
            st.success(f"합성 성공! {selected_fuse} 2마리 → {fusion_map[selected_fuse]} 1마리")
        else:
            # 실패
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            st.error(f"합성 실패! {selected_fuse} 2마리 소모")
else:
    st.info("합성 가능한 물고기가 없습니다. 2마리 이상 필요!")

# --- 코인 표시 ---
st.write(f"💰 현재 코인: {st.session_state.coin}")
