import streamlit as st
import random

# ================= 세션 초기화 =================
if "coin" not in st.session_state:
    st.session_state.coin = 0
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "shop_open" not in st.session_state:
    st.session_state.shop_open = False
if "fishbook" not in st.session_state:
    st.session_state.fishbook = set()      # 도감
if "location" not in st.session_state:
    st.session_state.location = "강가"     # 기본 낚시터

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

# 합성 물고기 가격
for base, fused in fusion_map.items():
    price_map[fused] = price_map[base] * 2

# ================= 함수 =================
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
            st.session_state.fishbook.add(f2)
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

# ========== 낚시터별 확률 ==========
def get_fishing_weights():
    if st.session_state.location == "강가":
        # 기본 확률
        return fish_weights

    elif st.session_state.location == "바다":
        # 바다 물고기 확률 증가
        return [
            w * 1.3 if f in ["전갱이", "고등어", "꽁치"] else w * 0.8
            for f, w in zip(fish_list, fish_weights)
        ]

    elif st.session_state.location == "희귀 낚시터":
        # 희귀 물고기 등장률 업 (원래 확률 낮은 애들 버프)
        return [
            w * 3 if w <= 10 else w
            for w in fish_weights
        ]


# ================= UI 시작 =================
st.title("🎣 낚시터!")
st.divider()

# 🌍 낚시터 선택
st.subheader("🌍 낚시터 선택")

location = st.selectbox(
    "현재 낚시터",
    ["강가", "바다", "희귀 낚시터"],
    index=["강가", "바다", "희귀 낚시터"].index(st.session_state.location)
)

# 희귀 낚시터 입장료 30코인
if location == "희귀 낚시터" and st.session_state.location != "희귀 낚시터":
    if st.session_state.coin >= 30:
        st.session_state.coin -= 30
        st.success("🔥 희귀 낚시터 입장! (30코인 차감)")
        st.session_state.location = location
    else:
        st.warning("❗ 코인이 부족합니다! (30코인 필요)")
else:
    st.session_state.location = location

st.divider()

col1, col2, col3 = st.columns(3)

# ================= 낚시 =================
with col1:
    st.subheader("🎣 낚시하기")

    if st.button("1번 낚시"):
        fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
        st.session_state.inventory.append(fish)
        st.session_state.fishbook.add(fish)
        st.success(f"{fish} 을/를 낚았다!")
        random_event(0.15)

    if st.button("2번 낚시"):
        fish = random.choices(fish_list, weights=get_fishing_weights(), k=2)
        st.session_state.inventory.extend(fish)
        for f in fish:
            st.session_state.fishbook.add(f)
        st.success(f"{', '.join(fish)} 을/를 낚았다!")
        random_event(0.25)


# ================= 인벤토리 =================
with col2:
    st.subheader("🎒 인벤토리")
    st.write("물고기:", st.session_state.inventory)

    sort_option = st.radio(
        "정렬 방식 선택",
        ["기본 순서", "가나다 순", "희귀도 순(낮은 확률 먼저)", "가격 높은 순"]
    )

    if sort_option == "가나다 순":
        st.session_state.inventory = sorted(st.session_state.inventory)
    elif sort_option == "희귀도 순(낮은 확률 먼저)":
        st.session_state.inventory = sorted(
            st.session_state.inventory,
            key=lambda x: fish_prob.get(x, 999)
        )
    elif sort_option == "가격 높은 순":
        st.session_state.inventory = sorted(
            st.session_state.inventory,
            key=lambda x: price_map.get(x, 0),
            reverse=True
        )


# ================= 상점 =================
with col3:
    st.subheader("🏪 상점")
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open)
    st.session_state.shop_open = open_shop

st.divider()

if st.session_state.shop_open:
    st.subheader("🏪 상점")
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

# ================= 합성 =================
st.subheader("⚡ 물고기 합성")

fusion_candidates = [f for f in fusion_map.keys() if st.session_state.inventory.count(f) >= 2]

if fusion_candidates:
    selected_fuse = st.selectbox("합성할 물고기 선택", fusion_candidates)
    if st.button("합성하기"):
        if random.choice([True, False]):  # 50%
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            result = fusion_map[selected_fuse]
            st.session_state.inventory.append(result)
            st.session_state.fishbook.add(result)
            st.success(f"합성 성공! {selected_fuse} 2마리 → {result} 1마리")
        else:
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            st.error(f"합성 실패! {selected_fuse} 2마리 소모")
else:
    st.info("합성 가능한 물고기가 없습니다. (같은 물고기 2마리 필요!)")

# ================= 도감 =================
st.subheader("📚 물고기 도감")

for fish in fish_list:
    if fish in st.session_state.fishbook:
        st.write(f"✔ {fish} (발견됨)")
    else:
        st.write(f"✖ {fish} (미발견)")

# ================= 코인 표시 =================
st.write(f"💰 현재 코인: {st.session_state.coin}")
