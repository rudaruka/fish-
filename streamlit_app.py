import streamlit as st
import random

# ================= 세션 초기화 =================
for key, default in [("coin",0), ("inventory",[]), ("shop_open",False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ================= 물고기 & 확률 =================
fish_prob = {
    "멸치": 25, "복어": 25, "누치": 20, "정어리": 15, "붕어": 15,
    "빙어": 10, "북어": 10, "전갱이": 10, "꽁치": 10, "은어": 8,
    "노래미": 7, "고등어": 7, "메기": 6, "잉어": 6, "쥐치": 5,
    "볼락": 5, "열기": 5, "줄돔": 4, "삼치": 4, "병어": 4,
    "향어": 3, "우럭": 3, "송어": 3, "해파리": 2, "꼴뚜기": 2,
    "넙치": 2, "광어": 2, "농어": 2, "가물치": 2, "방어": 1,
    "바다송어": 1, "해마": 1, "연어": 1, "쭈꾸미": 1, "아귀": 1,
    "한치": 1, "오징어": 1, "참치": 1, "홍어": 1, "랍스터": 1,
    "가오리": 1, "상어": 1, "문어": 1, "발광오징어": 1, "킹크랩": 1, "전복": 1
}

fish_list = list(fish_prob.keys())
fish_weights = list(fish_prob.values())

price_map = {
    "멸치":10,"복어":10,"누치":15,"정어리":15,"붕어":20,"빙어":20,"북어":20,
    "전갱이":20,"꽁치":20,"은어":25,"노래미":30,"고등어":30,"메기":30,"잉어":30,
    "쥐치":35,"볼락":35,"열기":35,"줄돔":35,"향어":35,"삼치":40,"병어":40,
    "우럭":45,"송어":45,"연어":45,"해파리":50,"꼴뚜기":60,"넙치":60,"광어":70,
    "농어":70,"가물치":70,"방어":75,"바다송어":75,"해마":75,"쭈꾸미":80,"아귀":85,
    "한치":85,"오징어":90,"참치":95,"홍어":95,"랍스터":110,"가오리":110,"상어":120,
    "문어":120,"발광오징어":120,"킹크랩":120,"전복":120
}

# ================= UI =================
st.title("🎣 전체 물고기 확률 낚시게임")
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
