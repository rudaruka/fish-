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
fusion_map = {
    "멸치": "대멸치", "복어": "대복어", "누치": "대누치",
    "정어리": "대정어리", "붕어": "대붕어"
}

# 상위 물고기 가격 설정
for base, fused in fusion_map.items():
    price_map[fused] = price_map[base] * 2

# ================= UI =================
st.title("🎣 낚시터!")
st.divider()

col1, col2, col3 = st.columns(3)

# --- 낚시 ---
with col1:
    st.subheader("🎣 낚시하기")

    # 1번
    if st.button("1번: 기본 낚시"):
        fish = random.choices(fish_list, weights=fish_weights, k=1)[0]
        st.session_state.inventory.append(fish)
        st.success(f"{fish} 을/를 낚았다!")

    # 2번
    if st.button("2번: 더블 낚시"):
        fish = random.choices(fish_list, weights=fish_weights, k=2)
        st.session_state.inventory.extend(fish)
        st.success(f"{', '.join(fish)} 을/를 낚았다!")

    # ⭐ 3번: 랜덤 이벤트
    if st.button("3번: 랜덤 이벤트 🎲"):
        event = random.randint(1, 6)

        if event == 1:
            coin = random.randint(20, 100)
            st.session_state.coin += coin
            st.success(f"🎉 행운의 코인 +{coin} 획득!")

        elif event == 2:
            fish = random.choices(fish_list, weights=fish_weights, k=1)[0]
            st.session_state.inventory.append(fish)
            st.success(f"🎣 특별 보너스! {fish} 획득!")

        elif event == 3:
            box = random.choice(["코인 50", "코인 100", "희귀 상위 물고기"])
            if box == "코인 50":
                st.session_state.coin += 50
                st.success("🎁 상자 보상: +50 코인")
            elif box == "코인 100":
                st.session_state.coin += 100
                st.success("🎁 상자 보상: +100 코인")
            else:
                rare = random.choice(list(fusion_map.values()))
                st.session_state.inventory.append(rare)
                st.success(f"🎁 초희귀! {rare} 획득!")

        elif event == 4:
            lose = random.randint(10, 40)
            st.session_state.coin = max(0, st.session_state.coin - lose)
            st.error(f"💸 벌칙! 코인 {lose} 감소!")

        elif event == 5:
            if st.session_state.inventory:
                lost_fish = random.choice(st.session_state.inventory)
                st.session_state.inventory.remove(lost_fish)
                st.error(f"💀 사고 발생! {lost_fish} 이(가) 사라졌다…")
            else:
                st.info("🎲 벌칙이었지만, 잃을 물고기가 없어서 패스!")

        else:
            st.success("😎 아무 일도 일어나지 않았다...")

# --- 인벤토리 ---
with col2:
    st.subheader("🎒 인벤토리")
    st.write(st.session_state.inventory)

# --- 상점 ---
with col3:
    st.subheader("🏪 상점")
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open)
    st.session_state.shop_open = open_shop

st.divider()

# ================= 상점 로직 =================
if st.session_state.shop_open:
    st.subheader("판매하기")
    if st.session_state.inventory:
        selected = st.selectbox("판매할 물고기 선택", st.session_state.inventory)
        if st.button("판매!"):
            price = price_map.get(selected, 0)
            st.session_state.coin += price
            st.session_state.inventory.remove(selected)
            st.success(f"{selected} 판매 완료! +{price} 코인")
    else:
        st.warning("팔 물고기가 없습니다!")

# ================= 합성 =================
st.subheader("⚡ 물고기 합성")

fusion_candidates = [
    f for f in fusion_map.keys()
    if st.session_state.inventory.count(f) >= 2
]

if fusion_candidates:
    selected_fuse = st.selectbox("합성할 물고기", fusion_candidates)
    if st.button("합성하기"):
        if random.choice([True, False]):
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.append(fusion_map[selected_fuse])
            st.success(f"합성 성공! {fusion_map[selected_fuse]} 획득!")
        else:
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            st.error("합성 실패! 물고기 2마리 소모됨")
else:
    st.info("합성 가능한 물고기가 없습니다!")

# --- 코인 ---
st.write(f"💰 현재 코인: {st.session_state.coin}")
