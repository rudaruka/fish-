import streamlit as st
import random

# ================= 페이지 설정 =================
st.set_page_config(page_title="🎣 낚시 게임", page_icon="🎣")

# ================= 세션 상태 안전 초기화 =================
if "coin" not in st.session_state:
    st.session_state.coin = 0

if "inventory" not in st.session_state:
    st.session_state.inventory = []

# items가 없거나 딕셔너리가 아니면 새로 생성
if "items" not in st.session_state or not isinstance(st.session_state.items, dict):
    st.session_state.items = {"행운 미끼": 1}

if "shop_open" not in st.session_state:
    st.session_state.shop_open = False

if "last_fish" not in st.session_state:
    st.session_state.last_fish = []

# ================= 물고기 종류 & 가격 & 확률 =================
fish_list = [
    "누치","정어리","붕어","빙어","북어","전갱이","꽁치","은어","노래미","고등어",
    "메기","잉어","쥐치","볼락","열기","줄돔","삼치","병어","향어","우럭",
    "송어","해파리","꼴뚜기","넙치","광어","농어","가물치","방어","바다송어",
    "해마","연어","쭈꾸미","아귀","한치","오징어","참치","홍어","랍스터",
    "가오리","상어","문어","발광오징어","킹크랩","전복"
]

weights = [
    20,20,15,15,15,15,15,10,10,10,
    10,10,8,8,8,7,7,7,7,6,
    6,5,5,5,4,4,4,4,3,
    3,3,2,2,2,2,2,2,1,
    1,1,1,1,1,1
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

# ================= 페이지 UI =================
st.title("🎣낚시다!! -낚시터 게임-")
st.write("같이 낚시하지 않을래?")
st.divider()

col1, col2, col3, col4 = st.columns(4)

# --- 낚시 카드 ---
with col1:
    st.subheader("🎣 낚시하기")
    st.write("1~2번 낚시 가능!")

    if st.button("1번 낚시"):
        luck_multiplier = 2 if st.session_state.items.get("행운 미끼",0) > 0 else 1
        if luck_multiplier == 2:
            st.session_state.items["행운 미끼"] -= 1
            st.info("행운 미끼를 사용! 희귀 물고기 확률 증가!")
        fish_caught = random.choices(fish_list, weights=[w*luck_multiplier for w in weights], k=1)[0]
        st.session_state.inventory.append(fish_caught)
        st.session_state.last_fish = [fish_caught]
        st.success(f"🎣 {fish_caught} 낚았습니다!")

    if st.button("2번 낚시"):
        luck_multiplier = 2 if st.session_state.items.get("행운 미끼",0) > 0 else 1
        if luck_multiplier == 2:
            st.session_state.items["행운 미끼"] -= 1
            st.info("행운 미끼를 사용! 희귀 물고기 확률 증가!")
        fish_caught = random.choices(fish_list, weights=[w*luck_multiplier for w in weights], k=2)
        st.session_state.inventory.extend(fish_caught)
        st.session_state.last_fish = fish_caught
        st.success(f"🎣 {', '.join(fish_caught)} 낚았습니다!")

# --- 인벤토리 카드 ---
with col2:
    st.subheader("🎒 인벤토리")
    st.write(f"보유 물고기: **{len(st.session_state.inventory)}**")
    st.write(st.session_state.inventory)
    if st.session_state.items:
        st.write("보유 아이템:", st.session_state.items)

# --- 상점 카드 ---
with col3:
    st.subheader("🏪 상점")
    if st.button("상점 열기"):
        st.session_state.shop_open = True

# --- 코인 카드 ---
with col4:
    st.subheader("💰 코인")
    st.write(f"현재 코인: **{st.session_state.coin} 코인**")

st.divider()

# ================= 상점 로직 =================
if st.session_state.shop_open:
    st.subheader("🏪 상점")
    if len(st.session_state.inventory) == 0 and all(v==0 for v in st.session_state.items.values()):
        st.warning("인벤토리와 아이템이 모두 비어 있습니다!")
    else:
        # 물고기 판매
        if st.session_state.inventory:
            selected = st.selectbox("판매할 물고기를 선택하세요", st.session_state.inventory)
            if st.button("판매하기"):
                price = price_map.get(selected,0)
                st.session_state.coin += price
                st.session_state.inventory.remove(selected)
                st.success(f"{selected} 판매 완료! +{price} 코인")

        # 아이템 사용
        available_items = [k for k,v in st.session_state.items.items() if v>0]
        if available_items:
            selected_item = st.selectbox("사용할 아이템을 선택하세요", available_items)
            if st.button("사용하기"):
                st.session_state.items[selected_item] -= 1
                st.info(f"{selected_item} 사용 완료!")

    # 상점 닫기 버튼
    if st.button("상점 닫기"):
        st.session_state.shop_open = False
