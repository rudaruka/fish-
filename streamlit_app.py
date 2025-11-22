import streamlit as st
import random
from collections import Counter
# from PIL import Image # 파일 시스템 오류 방지를 위해 제거

# ================= 세션 초기화 =================
if "coin" not in st.session_state:
    st.session_state.coin = 0  # 👈 시작 코인 0 유지
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "shop_open" not in st.session_state:
    st.session_state.shop_open = False
if "fishbook" not in st.session_state:
    st.session_state.fishbook = set()      # 도감
if "location" not in st.session_state:
    st.session_state.location = "강가"     # 기본 낚시터
if "location_selector" not in st.session_state:
    st.session_state.location_selector = "강가"

# ================= 물고기 & 가격 정의 =================
fish_prob = {
    "멸치": 25, "복어": 25, "누치": 20, "정어리": 15, "붕어": 15,
    "빙어": 10, "북어": 10, "전갱이": 10, "꽁치": 10, "은어": 8,
    "노래미": 7, "고등어": 7, "메기": 6, "잉어": 6, "쥐치": 5
}

fish_list = list(fish_prob.keys())
fish_weights = list(fish_prob.values())
# 🌟🌟 수정 적용: 판매 가격을 *1로 낮춰 장기 플레이 유도 🌟🌟
price_map = {fish: (100 - prob) * 1 for fish, prob in fish_prob.items()} # 👈 * 1로 수정

# ================= 합성 규칙 =================
fusion_map = {
    "멸치": "대멸치", "복어": "대복어", "누치": "대누치",
    "정어리": "대정어리", "붕어": "대붕어"
}

# 합성 물고기 가격 (일반 물고기 가격의 5배 유지)
for base, fused in fusion_map.items():
    price_map[fused] = price_map.get(base, 0) * 5 

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
            st.success(f"🎣 보너스 물고기 **{f2}** 획득!")
        elif event == 3:
            if st.session_state.inventory:
                lost = random.choice(st.session_state.inventory)
                st.session_state.inventory.remove(lost)
                st.error(f"🔥 물고기(**{lost}**) 1마리 도망감!")
            else:
                st.warning("도망갈 물고기가 없어서 아무 일도 일어나지 않았습니다.")
        else:
            st.success("✨ 신비한 바람이 분다… 좋은 기운이 느껴진다!")

def get_fishing_weights():
    """현재 낚시터에 따른 확률 가중치를 반환"""
    current_weights = fish_weights

    if st.session_state.location == "바다":
        current_weights = [
            w * 1.3 if f in ["전갱이", "고등어", "꽁치"] else w * 0.8
            for f, w in zip(fish_list, fish_weights)
        ]

    elif st.session_state.location == "희귀 낚시터":
        current_weights = [
            w * 3 if w <= 10 else w
            for w in fish_weights
        ]
    
    return current_weights

# ================= UI 시작 =================
st.title("🎣 낚시는 운이야!!")
st.write(f"💰 **현재 코인: {st.session_state.coin}**")
st.divider()

# 🌍 낚시터 선택
st.subheader("🌍 낚시터 선택")

current_location = st.session_state.location
temp_location = st.selectbox(
    "현재 낚시터",
    ["강가", "바다", "희귀 낚시터"],
    index=["강가", "바다", "희귀 낚시터"].index(current_location),
    key="location_selector"
)

# 낚시터 변경 및 비용 차감 로직 (1000 코인 유지)
if temp_location != current_location:
    if temp_location == "희귀 낚시터":
        if st.session_state.coin >= 1000:
            st.session_state.coin -= 1000
            st.session_state.location = temp_location
            st.success("🔥 희귀 낚시터 입장! (**1000코인을 차감합니다**)")
        else:
            st.warning("❗ 코인이 부족합니다! (1000코인으로 입장하실 수 있습니다)")
            st.session_state.location = current_location
            st.session_state.location_selector = current_location
    else:
        st.session_state.location = temp_location
        st.info(f"📍 낚시터를 **{temp_location}** 로 변경했습니다.")
else:
    st.session_state.location = temp_location
    
st.markdown(f"**현재 위치:** {st.session_state.location}")
st.divider()

col1, col2, col3 = st.columns(3)

# ================= 낚시 =================
with col1:
    st.subheader("🎣 낚시하기")

    if st.button("1번 낚시"):
        fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
        st.session_state.inventory.append(fish)
        st.session_state.fishbook.add(fish)
        st.success(f"**{fish}** 을/를 낚았다!")
        random_event(0.15)

    if st.button("2번 낚시"):
        fish_caught = random.choices(fish_list, weights=get_fishing_weights(), k=2)
        st.session_state.inventory.extend(fish_caught)
        for f in fish_caught:
            st.session_state.fishbook.add(f)
        st.success(f"**{', '.join(fish_caught)}** 을/를 낚았다!")
        random_event(0.25)

# ================= 인벤토리 =================
with col2:
    st.subheader("🎒 인벤토리")
    
    display_inventory = st.session_state.inventory.copy()

    sort_option = st.radio(
        "정렬 방식 선택",
        ["기본 순서", "가나다 순", "희귀도 순(낮은 확률 먼저)", "가격 높은 순"]
    )

    if sort_option == "가나다 순":
        display_inventory.sort()
    elif sort_option == "희귀도 순(낮은 확률 먼저)":
        display_inventory.sort(
            key=lambda x: fish_prob.get(x, 1) 
        )
    elif sort_option == "가격 높은 순":
        display_inventory.sort(
            key=lambda x: price_map.get(x, 0),
            reverse=True
        )

    st.write("---")
    if display_inventory:
        inventory_count = Counter(display_inventory)
        
        for fish_name, count in inventory_count.items():
            price = price_map.get(fish_name, "N/A")
            st.write(f"**{fish_name}** x **{count}** (판매가: {price} 코인)")
    else:
        st.info("인벤토리가 비어 있습니다.")


# ================= 상점 =================
with col3:
    st.subheader("🏪 상점")
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open)
    st.session_state.shop_open = open_shop

st.divider()

if st.session_state.shop_open:
    st.subheader("🏪 물고기 판매")
    if st.session_state.inventory:
        selected = st.multiselect(
            "판매할 물고기 선택", 
            st.session_state.inventory,
            format_func=lambda x: f"{x} ({price_map.get(x, 'N/A')} 코인)"
        )
        
        if st.button("선택된 물고기 판매"):
            total_price = 0
            
            for f in selected:
                price = price_map.get(f, 0)
                st.session_state.coin += price
                st.session_state.inventory.remove(f) 
                total_price += price
                
            if total_price > 0:
                st.success(f"{len(selected)} 마리 판매 완료! +**{total_price}** 코인")
    else:
        st.warning("팔 물고기가 없습니다!")

# ================= 합성 =================
st.subheader("⚡ 물고기 합성")

inventory_count = Counter(st.session_state.inventory)

fusion_candidates = [
    f for f in fusion_map.keys() 
    if inventory_count.get(f, 0) >= 2
]

if fusion_candidates:
    selected_fuse = st.selectbox("합성할 물고기 선택", fusion_candidates)
    
    if st.button("합성하기"):
        if inventory_count.get(selected_fuse, 0) >= 2:
            st.session_state.inventory.remove(selected_fuse)
            st.session_state.inventory.remove(selected_fuse)
            
            if random.choice([True, False]):  # 50% 확률
                result = fusion_map[selected_fuse]
                st.session_state.inventory.append(result)
                st.session_state.fishbook.add(result)
                st.balloons()
                st.success(f"**합성 성공!** {selected_fuse} 2마리 → **{result}** 1마리")
            else:
                st.error(f"**합성 실패!** {selected_fuse} 2마리 소모")
        else:
            st.warning("합성 가능한 물고기 수가 부족합니다.")
else:
    st.info("합성 가능한 물고기가 없습니다. (같은 물고기 2마리 필요!)")

# ================= 도감 =================
st.subheader("📚 물고기 도감")

st.markdown("##### 🐟 일반 물고기")
cols = st.columns(5)
for i, fish in enumerate(fish_list):
    with cols[i % 5]:
        status = "✔ 발견됨" if fish in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{fish}** ({status})")

st.markdown("##### ✨ 합성 물고기")
fuse_cols = st.columns(5)
for i, (base, fused) in enumerate(fusion_map.items()):
    with fuse_cols[i % 5]:
        status = "✔ 발견됨" if fused in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{fused}** ({status})")

# ================= 최종 코인 표시 =================
st.write("---")
st.write(f"💰 **최종 코인: {st.session_state.coin}**")
