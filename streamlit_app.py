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
    st.session_state.items = {}  # 아이템 보유

# ================= 물고기 & 가격 =================
fish_prob = {
    "멸치": 25, "복어": 25, "누치": 20, "정어리": 15, "붕어": 15,
    "빙어": 10, "북어": 10, "전갱이": 10, "꽁치": 10, "은어": 8,
    "노래미": 7, "고등어": 7, "메기": 6, "잉어": 6, "쥐치": 5
}

fish_list = list(fish_prob.keys())
fish_weights = list(fish_prob.values())
price_map = {fish: (prob + 5) * 2 for fish, prob in fish_prob.items()}

# ================= 합성 규칙 =================
fusion_map = {
    "멸치": "대멸치", "복어": "대복어", "누치": "대누치",
    "정어리": "대정어리", "붕어": "대붕어"
}

for base, fused in fusion_map.items():
    price_map[fused] = price_map[base] * 2

# ================= 아이템 =================
item_shop = {
    "행운 미끼": {"price": 50, "description": "낚시 시 보너스 확률 +50%"},
    "합성 강화제": {"price": 100, "description": "합성 성공 확률 +50%"}
}

# ================= UI =================
st.title("🎣 낚시터 + 아이템 시스템")
st.divider()

col1, col2, col3 = st.columns(3)

# --- 랜덤 이벤트 함수 ---
def random_event(event_rate):
    """랜덤 이벤트 시스템"""
    if random.random() < event_rate:
        st.info("🎲 랜덤 이벤트 발생!")
        event = random.randint(1, 4)
        if event == 1:
            bonus = random.randint(10, 80)
            st.session_state.coin += bonus
            st.success(f"💰 보너스 코인 +{bonus}!")
        elif event == 2:
            f2 = random.choice(fish_list)
            st.session_state.inventory.append(f2)
            st.success(f"🎣 보너스 물고기 {f2} 획득!")
        elif event == 3:
            if st.session_state.inventory:
                lost = random.choice(st.session_state.inventory)
                st.session_state.inventory.remove(lost)
                st.error(f"🔥 물고기({lost}) 1마리 도망감!")
            else:
                st.warning("도망갈 물고기가 없어서 아무 일도 일어나지 않았습니다.")
        else:
            st.success("✨ 신비한 바람이 분다… 좋은 기운이 느껴진다!")

# --- 낚시 ---
with col1:
    st.subheader("🎣 낚시하기")
    luck_multiplier = 1.5 if st.session_state.items.get("행운 미끼", 0) > 0 else 1

    # 1번 낚시
    if st.button("1번 낚시"):
        fish = random.choices(fish_list, weights=[w * luck_multiplier for w in fish_weights], k=1)[0]
        st.session_state.inventory.append(fish)
        st.success(f"{fish} 을/를 낚았다!")
        random_event(0.15)  # 15% 확률 이벤트

        if st.session_state.items.get("행운 미끼", 0) > 0:
            st.session_state.items["행운 미끼"] -= 1
            if st.session_state.items["행운 미끼"] == 0:
                del st.session_state.items["행운 미끼"]

    # 2번 낚시
    if st.button("2번 낚시"):
        fish = random.choices(fish_list, weights=[w * luck_multiplier for w in fish_weights], k=2)
        st.session_state.inventory.extend(fish)
        st.success(f"{', '.join(fish)} 을/를 낚았다!")
        random_event(0.25)

        if st.session_state.items.get("행운 미끼", 0) > 0:
            st.session_state.items["행운 미끼"] -= 1
            if st.session_state.items["행운 미끼"] == 0:
                del st.session_state.items["행운 미끼"]

# --- 인벤토리 ---
with col2:
    st.subheader("🎒 인벤토리")
    st.write("물고기:", st.session_state.inventory)

    # ===== 인벤토리 정렬 =====
    sort_option = st.radio(
        "정렬 방식 선택",
        ["기본 순서", "가나다 순", "희귀도 순", "가격 높은 순"]
    )

    if sort_option == "가나다 순":
        st.session_state.inventory = sorted(st.session_state.inventory)
    elif sort_option == "희귀도 순":
        st.session_state.inventory = sorted(st.session_state.inventory, key=lambda x: fish_prob.get(x, 999))
    elif sort_option == "가격 높은 순":
        st.session_state.inventory = sorted(st.session_state.inventory, key=lambda x: price_map.get(x, 0), reverse=True)

# --- 상점 ---
with col3:
    st.subheader("🏪 상점")
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open)
    st.session_state.shop_open = open_shop

st.divider()

# --- 상점 로직 ---
if st.session_state.shop_open:
    st.subheader("🏪 상점")
    # ----- 물고기 판매 -----
    if st.session_state.inventory:
        selected = st.multiselect("판매할 물고기 선택", st.session_state.inventory)
        if st.button("판매하기"):
            total_price = 0
            for f in selected:
                price = price_map.get(f, 0)
                st.session_state.coin += price
                st.session_state.inventory.remove(f)
                total_price += price
            if total_price > 0:
                st.success(f"{', '.join(selected)} 판매 완료! +{total_price} 코인")
    else:
        st.warning("팔 물고기가 없습니다!")

    st.divider()

    # ----- 아이템 구매 -----
    st.subheader("🛒 아이템 구매")
    for item, info in item_shop.items():
        st.write(f"{item} - {info['description']} ({info['price']} 코인)")
        if st.button(f"{item} 구매"):
            if st.session_state.coin >= info['price']:
                st.session_state.coin -= info['price']
                st.session_state.items[item] = st.session_state.items.get(item, 0) + 1
                st.success(f"{item} 구매 완료!")
            else:
                st.error("코인이 부족합니다!")

# --- 합성 기능 ---
st.subheader("⚡ 물고기 합성")
fusion_candidates = [f for f in fusion_map.keys() if st.session_state.inventory.count(f) >= 2]

if fusion_candidates:
    selected_fuse = st.selectbox("합성할 물고기 선택", fusion_candidates)
    if st.button("합성하기"):
        success_rate = 0.5
        if st.session_state.items.get("합성 강화제", 0) > 0:
            success_rate += 0.5  # 강화제 사용시 성공 확률 +50%
            st.session_state.items["합성 강화제"] -= 1
            if st.session_state.items["합성 강화제"] == 0:
                del st.session_state.items["합성 강화제"]

        if random.random() < success_rate:
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.append(fusion_map[selected_fuse])
            st.success(f"합성 성공! {selected_fuse} 2마리 → {fusion_map[selected_fuse]} 1마리")
        else:
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            st.error(f"합성 실패! {selected_fuse} 2마리 소모")
else:
    st.info("합성 가능한 물고기가 없습니다. (2마리 이상 필요!)")

# --- 코인 & 아이템 표시 ---
st.write(f"💰 현재 코인: {st.session_state.coin}")
st.write(f"🎁 아이템: {st.session_state.items if st.session_state.items else '없음'}")
