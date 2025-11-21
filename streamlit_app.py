import streamlit as st
import random

# ================= 세션 초기화 =================
if "coin" not in st.session_state:
    st.session_state.coin = 0
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "shop_open" not in st.session_state:
    st.session_state.shop_open = False
# items가 없거나 dict가 아니면 초기화
if "items" not in st.session_state or not isinstance(st.session_state.items, dict):
    st.session_state.items = {}

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
fusion_map = {
    "멸치": "대멸치", "복어": "대복어", "누치": "대누치",
    "정어리": "대정어리", "붕어": "대붕어"
}
for base, fused in fusion_map.items():
    price_map[fused] = price_map[base]*2

# ================= 아이템 =================
items_price = {"행운 미끼": 50}

# ================= UI =================
st.title("🎣 낚시 + 상점 + 합성 + 아이템")
st.divider()

col1, col2, col3 = st.columns(3)

# --- 낚시 ---
with col1:
    st.subheader("🎣 낚시하기")
    # 안전하게 아이템 갯수 확인
    luck_multiplier = 2 if st.session_state.items.get("행운 미끼", 0) > 0 else 1
    fish_weights_modified = [w*luck_multiplier for w in fish_weights]

    if st.button("1번 낚시"):
        fish = random.choices(fish_list, weights=fish_weights_modified, k=1)[0]
        st.session_state.inventory.append(fish)
        st.success(f"{fish} 낚았다!")

    if st.button("2번 낚시"):
        fish = random.choices(fish_list, weights=fish_weights_modified, k=2)
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
    st.session_state.shop_open = st.checkbox("상점 열기", value=st.session_state.shop_open)

st.divider()

# --- 상점 로직 ---
if st.session_state.shop_open:
    st.subheader("🏪 상점")
    shop_tab = st.radio("거래 종류", ["물고기 판매", "아이템 구매/판매"], key="shop_tab")

    if shop_tab == "물고기 판매":
        if st.session_state.inventory:
            selected = st.selectbox("판매할 물고기 선택", st.session_state.inventory, key="sell_fish")
            if st.button("판매하기", key="sell_fish_btn"):
                price = price_map.get(selected, 0)
                st.session_state.coin += price
                st.session_state.inventory.remove(selected)
                st.success(f"{selected} 판매 완료! +{price} 코인")
        else:
            st.warning("팔 물고기가 없습니다!")

    else:  # 아이템 거래
        action = st.radio("구매/판매", ["구매", "판매"], key="item_action_radio")
        selected_item = st.selectbox("아이템 선택", list(items_price.keys()), key="item_select_box")

        if action == "구매":
            if st.button("구매하기", key="buy_item_btn"):
                price = items_price[selected_item]
                if st.session_state.coin >= price:
                    st.session_state.coin -= price
                    st.session_state.items[selected_item] = st.session_state.items.get(selected_item,0)+1
                    st.success(f"{selected_item} 구매 완료!")
                else:
                    st.error("코인이 부족합니다!")
        else:  # 판매
            if st.button("판매하기", key="sell_item_btn"):
                if st.session_state.items.get(selected_item,0) > 0:
                    st.session_state.coin += items_price[selected_item]
                    st.session_state.items[selected_item] -= 1
                    st.success(f"{selected_item} 판매 완료!")
                else:
                    st.warning("해당 아이템이 없습니다!")

# --- 합성 기능 ---
st.subheader("⚡ 물고기 합성")
fusion_candidates = [f for f in fusion_map.keys() if st.session_state.inventory.count(f) >=2]

if fusion_candidates:
    selected_fuse = st.selectbox("합성할 물고기 선택", fusion_candidates, key="fusion_select")
    if st.button("합성하기", key="fusion_btn"):
        if random.choice([True, False]):  # 50% 확률
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.append(fusion_map[selected_fuse])
            st.success(f"합성 성공! {selected_fuse} 2마리 → {fusion_map[selected_fuse]} 1마리")
        else:
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            st.error(f"합성 실패! {selected_fuse} 2마리 소모")
else:
    st.info("합성 가능한 물고기가 없습니다. 2마리 이상 필요!")

# --- 코인 표시 ---
st.write(f"💰 현재 코인: {st.session_state.coin}")
