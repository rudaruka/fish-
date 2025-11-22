import streamlit as st
import random
from collections import Counter
# from PIL import Image # 로컬 파일 문제 방지를 위해 주석 처리 유지

# ================= 세션 초기화 =================
# items가 dict인지 확인, 없거나 타입이 다르면 새로 초기화
if "items" not in st.session_state or not isinstance(st.session_state.items, dict):
    st.session_state.items = {
        "강화 미끼": 0,
        "자동 낚시권": 0
    }
    
if "coin" not in st.session_state:
    st.session_state.coin = 0
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "shop_open" not in st.session_state:
    st.session_state.shop_open = False
if "fishbook" not in st.session_state:
    st.session_state.fishbook = set()
if "location" not in st.session_state:
    st.session_state.location = "강가"
if "location_selector" not in st.session_state:
    st.session_state.location_selector = "강가"
if "rod_level" not in st.session_state:
    st.session_state.rod_level = 0
    

# ================= 물고기 & 가격 =================
fish_prob = {
    "멸치": 25, "복어": 25, "누치": 20, "정어리": 15, "붕어": 15,
    "빙어": 10, "북어": 10, "전갱이": 10, "꽁치": 10, "은어": 8,
    "노래미": 7, "고등어": 7, "메기": 6, "잉어": 6, "쥐치": 5
}

fish_list = list(fish_prob.keys())
fish_weights = list(fish_prob.values())
price_map = {fish: (100 - prob) * 1 for fish, prob in fish_prob.items()}

fusion_map = {
    "멸치": "대멸치", "복어": "대복어", "누치": "대누치",
    "정어리": "대정어리", "붕어": "대붕어"
}
for base, fused in fusion_map.items():
    price_map[fused] = price_map.get(base, 0) * 5

price_map["오래된 지도 조각"] = 5000

# 🛒 상점 아이템 정의 (강화 재료 및 일반 아이템)
shop_items = {
    "강화 미끼": {"price": 500, "desc": "낚싯대 강화에 필요한 핵심 재료입니다."},
    "자동 낚시권": {"price": 1000, "desc": "자동으로 낚시를 진행할 수 있는 권한입니다."},
}

# 🎣 강화 비용/확률 정의
ROD_UPGRADE_COSTS = {
    1: {"coin": 2000, "bait": 2, "success_rate": 0.8},
    2: {"coin": 4000, "bait": 4, "success_rate": 0.6},
    3: {"coin": 8000, "bait": 8, "success_rate": 0.4},
}

# ================= 함수 =================
def catch_fish(fish):
    st.session_state.inventory.append(fish)
    st.session_state.fishbook.add(fish)

def random_event(event_rate):
    if random.random() < event_rate:
        st.info("🎲 랜덤 이벤트 발생!")
        event = random.randint(1, 5)
        if event == 1:
            bonus = random.randint(10, 80)
            st.session_state.coin += bonus
            st.success(f"💰 보너스 코인 +{bonus}!")
        elif event == 2:
            f2 = random.choice(fish_list)
            catch_fish(f2)
            st.success(f"🎣 보너스 물고기 **{f2}** 획득!")
        elif event == 3:
            if st.session_state.inventory:
                lost = random.choice(st.session_state.inventory)
                st.session_state.inventory.remove(lost)
                st.error(f"🔥 물고기(**{lost}**) 1마리 도망감!")
            else:
                st.warning("도망갈 물고기가 없어요.")
        elif event == 5 and st.session_state.location == "희귀 낚시터":
            item_name = "오래된 지도 조각"
            catch_fish(item_name)
            st.balloons()
            st.success(f"🗺️ 전설 아이템 획득! **{item_name}** (+{price_map[item_name]} 코인)")
        else:
            st.success("✨ 신비한 바람이 분다… 좋은 기운이 느껴진다!")

def get_fishing_weights():
    weights = fish_weights.copy()
    rod_bonus_multiplier = 1 + (st.session_state.rod_level * 0.2)
    if st.session_state.location == "바다":
        weights = [w*1.3 if f in ["전갱이","고등어","꽁치"] else w*0.8
                    for f,w in zip(fish_list, fish_weights)]
    elif st.session_state.location == "희귀 낚시터":
        weights = [w*3 if w<=10 else w for w in fish_weights]
        weights = [w*1.5 if fish_list[i] in fusion_map else w for i,w in enumerate(weights)]
    weights = [
        w * rod_bonus_multiplier if fish_prob.get(fish_list[i], 1) <= 10 else w
        for i, w in enumerate(weights)
    ]
    return weights

# ================= UI 시작 =================
st.title("🎣 낚시는 운이야!!")
st.write(f"💰 현재 코인: **{st.session_state.coin}**")
st.write(f"✨ 낚싯대 레벨: **Lv.{st.session_state.rod_level}**")
st.divider()

# 🌍 낚시터 선택
st.subheader("🌍 낚시터 선택")
current_location = st.session_state.location
temp_location = st.selectbox("현재 낚시터",
                              ["강가","바다","희귀 낚시터"],
                              index=["강가","바다","희귀 낚시터"].index(current_location),
                              key="location_selector")
if temp_location != current_location:
    if temp_location == "희귀 낚시터":
        if st.session_state.coin >= 1000:
            st.session_state.coin -= 1000
            st.session_state.location = temp_location
            st.success("🔥 희귀 낚시터 입장! (-1000코인)")
        else:
            st.warning("❗ 코인이 부족합니다! (1000 필요)")
            st.session_state.location_selector = current_location 
    else:
        st.session_state.location = temp_location
        st.info(f"📍 낚시터를 {temp_location} 로 변경")
st.markdown(f"**현재 위치:** {st.session_state.location}")
st.divider()

col1,col2,col3 = st.columns(3)

# ================= 🏪 상점 / 강화 =================
with col3:
    st.subheader("🏪 상점 / 강화")
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open)
    st.session_state.shop_open = open_shop

if st.session_state.shop_open:
    st.subheader("🛠️ 낚싯대 강화")
    current_level = st.session_state.rod_level
    next_level = current_level + 1

    if next_level in ROD_UPGRADE_COSTS:
        cost = ROD_UPGRADE_COSTS[next_level]
        # ✅ 안전하게 dict 확인
        if not isinstance(st.session_state.items, dict):
            st.session_state.items = {}
        current_bait = st.session_state.items.get("강화 미끼", 0)

        st.write(f"**현재 레벨: Lv.{current_level}**")
        st.write(f"**다음 레벨: Lv.{next_level}**")
        st.write(f"필요 코인: **{cost['coin']}** (현재: {st.session_state.coin})")
        st.write(f"필요 강화 미끼: **{cost['bait']}** (현재: {current_bait})")
        st.write(f"성공 확률: **{int(cost['success_rate'] * 100)}%**")

        can_upgrade = st.session_state.coin >= cost['coin'] and current_bait >= cost['bait']

        if st.button(f"Lv.{next_level} 강화 시도", disabled=not can_upgrade):
            # 1. 재료/코인 차감
            st.session_state.coin -= cost['coin']
            st.session_state.items["강화 미끼"] = st.session_state.items.get("강화 미끼", 0) - cost['bait']
            # 2. 강화 성공/실패
            if random.random() < cost['success_rate']:
                st.session_state.rod_level = next_level
                st.success(f"🎉 **강화 성공!** 낚싯대가 **Lv.{next_level}**이 되었습니다!")
            else:
                st.error("💥 **강화 실패!** 재료만 소모되었습니다.")
            st.experimental_rerun()
    else:
        st.info(f"낚싯대가 **최고 레벨 (Lv.{current_level})**입니다!")
