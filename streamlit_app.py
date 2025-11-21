import streamlit as st
import random

# ================= 세션 초기화 =================
if "coin" not in st.session_state:
    st.session_state.coin = 0
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "shop_open" not in st.session_state:
    st.session_state.shop_open = False
if "items" not in st.session_state:
    st.session_state.items = {}

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

price_map = {fish: (prob+5)*2 for fish, prob in fish_prob.items()}

# ================= 아이템 =================
items_price = {"행운 미끼": 50, "강철 미끼": 100}

# ================= UI =================
st.title("🎣 확률 낚시 + 아이템 상점")
st.divider()

col1, col2, col3 = st.columns(3)

# --- 낚시 ---
with col1:
    st.subheader("🎣 낚시하기")

    # 행운 미끼 적용
    luck_multiplier = 2 if st.session_state.items.get("행운 미끼", 0) > 0 else 1
    weights = [w*luck_multiplier for w in fish_weights]

    if st.button("1번 낚시", key="fish1"):
        fish = random.choices(fish_list, weights=weights, k=1)[0]
        st.session_state.inventory.append(fish)
        st.success(f"{fish} 낚았다!")

    if st.button("2번 낚시", key="fish2"):
        fish = random.choices(fish_list, weights=weights, k=2)
        st.session_state.inventory.extend(fish)
        st.success(f"{', '.join(fish)} 낚았다!")

# --- 인벤토리 ---
with col2:
    st.subheader("🎒 인벤토리")
    st.write("물고기:", st.session_state.inventory)
    st.write("아이템:", st.session_state.items)

# --- 상점 ---
with col3:
    st.subheader("🏪 상점")
    if st.button("상점 열기", key="open_shop"):
        st.session_state.shop_open = True

st.divider()

# --- 상점 로직 ---
if st.session_state.shop_open:
    st.subheader("🏪 상점")

    shop_tab = st.radio("판매/구매 선택", ["물고기 판매", "아이템 구매/판매"], key="shop_tab")

    if shop_tab == "물고기 판매":
        if not st.session_state.inventory:
            st.warning("팔 물고기가 없어!")
        else:
            selected = st.selectbox("판매할 물고기 선택", st.session_state.inventory, key="sell_fish_select")
            if st.button("판매하기", key="sell_fish_btn"):
                price = price_map.get(selected,0)
                st.session_state.coin += price
                st.session_state.inventory.remove(selected)
                st.success(f"{selected} 판매 완료! +{price} 코인")

    else:  # 아이템 구매/판매
        item_names = list(items_price.keys())
        action = st.radio("구매/판매", ["구매", "판매"], key="item_action")
        selected_item = st.selectbox("아이템 선택", item_names, key="item_select")

        if action == "구매":
            if st.button("구매하기", key="buy_item_btn"):
                price = items_price[selected_item]
                if st.session_state.coin >= price:
                    st.session_state.coin -= price
                    st.session_state.items[selected_item] = st.session_state.items.get(selected_item,0)+1
                    st.success(f"{selected_item} 구매 완료!")
                else:
                    st.error("코인이 부족합니다!")
        else:
            if st.button("판매하기", key="sell_item_btn"):
                if st.session_state.items.get(selected_item,0) > 0:
                    st.session_state.coin += items_price[selected_item]
                    st.session_state.items[selected_item] -= 1
                    st.success(f"{selected_item} 판매 완료!")
                else:
                    st.warning("해당 아이템이 없습니다!")

    if st.button("상점 닫기", key="close_shop_btn"):
        st.session_state.shop_open = False

# --- 코인 표시 ---
st.write(f"💰 현재 코인: {st.session_state.coin}")
