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

# ================= 물고기 & 가격 =================
fish_list = [
    "누치", "정어리", "붕어", "빙어", "북어", "전갱이", "꽁치", "은어",
    "노래미", "고등어", "메기", "잉어", "쥐치", "볼락", "열기",
    "줄돔", "삼치", "병어", "향어", "우럭", "송어", "해파리",
    "꼴뚜기", "넙치", "광어", "농어", "가물치", "방어", "바다송어",
    "해마", "연어", "쭈꾸미", "아귀", "한치", "오징어", "참치",
    "홍어", "랍스터", "가오리", "상어", "문어", "발광오징어",
    "킹크랩", "전복"
]

# 가격은 단순 예시
price_map = {fish: (i+1)*10 for i, fish in enumerate(fish_list)}

# ================= 합성 규칙 =================
fusion_map = {
    "누치": "대누치",
    "정어리": "대정어리",
    "붕어": "대붕어",
    "연어": "왕연어",
    "참치": "왕참치"
}

for base, fused in fusion_map.items():
    price_map[fused] = price_map[base] * 2

# ================= 아이템 =================
items_price = {"행운 미끼": 50}

# ================= UI =================
st.title("🎣 낚시 게임 - 완전체")
st.divider()

col1, col2, col3 = st.columns(3)

# --- 낚시 ---
with col1:
    st.subheader("🎣 낚시하기")
    luck_multiplier = 2 if st.session_state.items.get("행운 미끼",0) > 0 else 1

    if st.button("1번 낚시"):
        fish = random.choices(fish_list, k=1)[0]
        st.session_state.inventory.append(fish)
        st.success(f"{fish} 낚았다!")

    if st.button("2번 낚시"):
        fish = random.choices(fish_list, k=2)
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
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open)
    st.session_state.shop_open = open_shop

st.divider()

# --- 상점 로직 ---
if st.session_state.shop_open:
    st.subheader("🏪 상점")
    tab = st.radio("판매/아이템 거래", ["물고기 판매", "아이템 구매/판매"], key="shop_tab")

    if tab == "물고기 판매":
        if st.session_state.inventory:
            selected = st.selectbox("판매할 물고기 선택", st.session_state.inventory, key="sell_fish_select")
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
fusion_candidates = [f for f in fusion_map.keys() if st.session_state.inventory.count(f) >= 2]

if fusion_candidates:
    selected_fuse = st.selectbox("합성할 물고기 선택", fusion_candidates, key="fusion_select")
    if st.button("합성하기", key="fusion_btn"):
        if random.choice([True, False]):  # 50% 성공
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
