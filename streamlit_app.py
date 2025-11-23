import streamlit as st
import random
from collections import Counter

# ================= 1. 세션 초기화 =================
def initialize_session_state():
    defaults = {
        "coin": 0,
        "inventory": [],
        "shop_open": False,
        "location": "강가",
        "location_selector": "강가",
        "rod_level": 0,
        "bait": 2    # 🧵 떡밥 기본 2개
    }

    if "fishbook" not in st.session_state or not isinstance(st.session_state.fishbook, set):
        st.session_state.fishbook = set()

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

initialize_session_state()

# ================= 2. 물고기 & 가격 정의 =================
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

# 🛒 떡밥 상점 아이템 추가
shop_items = {
    "떡밥": {
        "price": 200,
        "desc": "낚시 1회당 1개 필요!"
    }
}

ROD_UPGRADE_COSTS = {
    1: {"coin": 2000, "success_rate": 0.8},
    2: {"coin": 4000, "success_rate": 0.6},
    3: {"coin": 8000, "success_rate": 0.4},
}

# ================= 3. 함수 정의 =================
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

# ================= 4. UI =================
st.title("🎣 낚시터에 오신 것을 환영합니다!!")
st.subheader("이게 첫 작품이라고?! 🐟")

st.write(f"💰 현재 코인: **{st.session_state.coin}**")
st.write(f"🧵 현재 떡밥: **{st.session_state.bait}개**")
st.write(f"✨ 낚싯대 레벨: **Lv.{st.session_state.rod_level}**")
st.divider()

# ================= 낚시터 선택 =================
st.subheader("🌍 낚시터 선택")

current_location = st.session_state.location
temp_location = st.selectbox(
    "현재 낚시터",
    ["강가","바다","희귀 낚시터"],
    index=["강가","바다","희귀 낚시터"].index(current_location),
    key="location_selector"
)

if temp_location != current_location:
    if temp_location == "희귀 낚시터":

        required_coin = 2000
        required_fish = {"대멸치": 20, "대붕어": 20}

        current_inventory_counts = Counter(st.session_state.inventory)
        has_coin = st.session_state.coin >= required_coin
        has_fish = all(current_inventory_counts.get(name, 0) >= qty for name, qty in required_fish.items())

        st.markdown("##### 💎 희귀 낚시터 입장 조건")
        st.write(f"💰 코인: **{required_coin}** (현재: {st.session_state.coin})")

        fish_status_msg = ""
        for name, qty in required_fish.items():
            current_qty = current_inventory_counts.get(name, 0)
            status = '✔' if current_qty >= qty else '✖'
            fish_status_msg += f"**{name}** {qty}마리 (현재 {current_qty}개) ({status}) / "
        st.write(f"🐟 물고기: {fish_status_msg[:-3]}")

        entry_options = []
        if has_coin:
            entry_options.append("코인만 소모 (2000 코인)")
        if has_fish:
            entry_options.append("대멸치 20마리 + 대붕어 20마리 소모")

        if not entry_options:
            st.warning("❗ 입장 조건 부족")
            st.session_state.location_selector = current_location
            st.stop()

        entry_method = st.radio("입장 방법 선택", entry_options, key="entry_radio")

        can_enter = False
        cost_msg = ""

        if "코인만 소모" in entry_method:
            if has_coin:
                st.session_state.coin -= required_coin
                cost_msg = f"🔥 희귀 낚시터 입장! (-{required_coin} 코인)"
                can_enter = True

        elif "대멸치" in entry_method:
            if has_fish:
                for name, qty in required_fish.items():
                    for _ in range(qty):
                        st.session_state.inventory.remove(name)
                cost_msg = "🔥 희귀 낚시터 입장! (물고기 소모)"
                can_enter = True

        if can_enter:
            st.session_state.location = temp_location
            st.success(cost_msg)
        else:
            st.session_state.location_selector = current_location

    else:
        st.session_state.location = temp_location
        st.info(f"📍 낚시터를 **{temp_location}** 로 변경")

st.markdown(f"**현재 위치:** {st.session_state.location}")
st.divider()

col1, col2, col3 = st.columns(3)

# ================= 🎣 낚시하기 (잔고 보호 로직 적용) =================
with col1:
    st.subheader("🎣 낚시하기")

    # 🔥 떡밥 부족 체크 (UI 표시)
    if st.session_state.bait <= 0:
        st.error("❗ 떡밥이 부족합니다! 상점에서 구매하거나 제작하세요.")

    # 일반 낚시
    if st.session_state.location != "희귀 낚시터":
        
        # 1번 낚시 (떡밥 1 소모)
        if st.button("1번 낚시 **(떡밥 1 소모)**", key="normal_1", disabled=st.session_state.bait < 1):
            if st.session_state.bait >= 1: # 🌟 보호 로직
                st.session_state.bait -= 1
                fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
                catch_fish(fish)
                st.success(f"**{fish}** 낚았다!")
                random_event(0.15)
        
        # 2번 낚시 (떡밥 2 소모)
        if st.button("2번 낚시 **(떡밥 2 소모)**", key="normal_2", disabled=st.session_state.bait < 2):
            if st.session_state.bait >= 2: # 🌟 보호 로직
                st.session_state.bait -= 2
                fish_caught = random.choices(fish_list, weights=get_fishing_weights(), k=2)
                for f in fish_caught: catch_fish(f)
                st.success(f"{', '.join(fish_caught)} 낚았다!")
                random_event(0.25)

    # 희귀 낚시
    else:
        
        # 희귀 낚시 1회 (떡밥 1 소모)
        if st.button("희귀 낚시 1회 **(떡밥 1 소모)**", key="rare_1", disabled=st.session_state.bait < 1):
            if st.session_state.bait >= 1: # 🌟 보호 로직
                st.session_state.bait -= 1
                fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
                catch_fish(fish)
                st.success(f"💎 {fish} 낚았다!")
                random_event(0.2)

        # 희귀 낚시 2회 (떡밥 2 소모)
        if st.button("희귀 낚시 2회 **(떡밥 2 소모)**", key="rare_2", disabled=st.session_state.bait < 2):
            if st.session_state.bait >= 2: # 🌟 보호 로직
                st.session_state.bait -= 2
                fish_caught = random.choices(fish_list, weights=get_fishing_weights(), k=2)
                for f in fish_caught: catch_fish(f)
                st.success(f"💎 {', '.join(fish_caught)} 낚았다!")
                random_event(0.35)

# ================= 🎒 인벤토리 =================
with col2:
    st.subheader("🎒 인벤토리")
    display_inventory = st.session_state.inventory.copy()
    st.write("---")

    if display_inventory:
        counts = Counter(display_inventory)
        for item, cnt in counts.items():
            st.write(f"**{item}** x {cnt} (판매가: {price_map.get(item,'N/A')} 코인)")
    else:
        st.info("인벤토리가 비어 있습니다.")

# ================= 🏪 상점 / 강화 =================
with col3:
    st.subheader("🏪 상점 / 강화")
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open, key="shop_open_cb")
    st.session_state.shop_open = open_shop

st.divider()

if st.session_state.shop_open:
    # ===== 낚싯대 강화 =====
    st.subheader("🛠️ 낚싯대 강화")

    current_level = st.session_state.rod_level
    next_level = current_level + 1

    if next_level in ROD_UPGRADE_COSTS:
        cost = ROD_UPGRADE_COSTS[next_level]

        st.write(f"현재 레벨: Lv.{current_level}")
        st.write(f"다음 레벨: Lv.{next_level}")
        st.write(f"필요 코인: {cost['coin']} (현재: {st.session_state.coin})")
        st.write(f"성공 확률: {int(cost['success_rate']*100)}%")

        can_upgrade = st.session_state.coin >= cost['coin']
        if st.button(f"Lv.{next_level} 강화 시도", disabled=not can_upgrade, key=f"upgrade_{next_level}"):
            st.session_state.coin -= cost['coin']
            if random.random() < cost['success_rate']:
                st.session_state.rod_level = next_level
                st.success(f"🎉 강화 성공! Lv.{next_level}")
            else:
                st.error("💥 강화 실패! 코인만 소모")
    else:
        st.info(f"최고 레벨 Lv.{current_level}입니다!")

    # ===== 아이템 구매 =====
    st.subheader("🛒 아이템 구매")

    shop_cols = st.columns(2)
    for i, (item, data) in enumerate(shop_items.items()):
        with shop_cols[i % 2]:
            st.write(f"**{item}** ({data['price']} 코인)")
            st.caption(data["desc"])
            if st.button(f"구매 {item}", key=f"buy_{item}"):
                if st.session_state.coin >= data["price"]:
                    st.session_state.coin -= data["price"]
                    if item == "떡밥":
                        st.session_state.bait += 1
                        st.success(f"{item} 구매 완료! (현재 떡밥: {st.session_state.bait}개)")
                    else:
                        st.success(f"{item} 구매 완료!")
                else:
                    st.error("❗ 코인 부족!")

    # ===== 판매 =====
    st.subheader("💰 판매")
    if st.session_state.inventory:
        selected = st.multiselect(
            "판매할 아이템 선택",
            st.session_state.inventory,
            format_func=lambda x: f"{x} ({price_map.get(x,'N/A')} 코인)",
            key="sell_select"
        )

        if st.button("판매", key="sell_btn"):
            counts = Counter(st.session_state.inventory)
            selected_counts = Counter(selected)
            total = 0

            for item, qty in selected_counts.items():
                sell_qty = min(qty, counts[item])
                for _ in range(sell_qty):
                    st.session_state.inventory.remove(item)
                total += price_map.get(item, 0) * sell_qty

            if total > 0:
                st.session_state.coin += total
                st.success(f"{sum(selected_counts.values())}개 판매 완료! +{total} 코인")
    else:
        st.warning("판매할 아이템이 없습니다.")

# ================= 🔧 떡밥 제작 (선택 기능 적용) =================
st.divider()
st.subheader("🧵 떡밥 제작")
st.caption("동일한 물고기 2마리를 갈아서 떡밥 1개로 만듭니다. (저렴한 물고기를 사용하는 것이 유리합니다.)")

counts = Counter(st.session_state.inventory)
# 2마리 이상 있고, 특수 아이템이 아닌 물고기만 제작 후보에 포함
excluded_items = list(fusion_map.values()) + ["오래된 지도 조각"]
craft_candidates = [f for f, count in counts.items() if count >= 2 and f not in excluded_items]

if craft_candidates:
    # 어떤 물고기를 2마리 소모할지 선택
    selected_fish_to_grind = st.selectbox("분쇄할 물고기 선택 (2마리 소모)", craft_candidates, key="craft_select")
    
    if st.button(f"'{selected_fish_to_grind}' 2개 갈아서 떡밥 1개 제작", key="craft_btn"):
        # 안전성 확인
        if counts.get(selected_fish_to_grind, 0) >= 2:
            st.session_state.inventory.remove(selected_fish_to_grind)
            st.session_state.inventory.remove(selected_fish_to_grind)
            st.session_state.bait += 1
            st.success(f"**{selected_fish_to_grind}** 2마리 분쇄 완료! 🧵 **떡밥 1개** 획득! (현재 떡밥: {st.session_state.bait}개)")
        else:
            st.warning("물고기 수가 부족합니다.")
else:
    st.info("떡밥 제작 가능한 물고기가 없습니다. (동일 물고기 2마리 필요)")

# ================= ⚡ 합성 =================
st.divider()
st.subheader("⚡ 물고기 합성")

counts = Counter(st.session_state.inventory)
fusion_candidates = [f for f in fusion_map.keys() if counts.get(f,0) >= 2]

if fusion_candidates:
    sel = st.selectbox("합성할 물고기 선택", fusion_candidates, key="fusion_select")
    if st.button("합성하기", key="fusion_btn"):
        if counts.get(sel,0)>=2:
            st.session_state.inventory.remove(sel)
            st.session_state.inventory.remove(sel)

            if random.choice([True,False]):
                result = fusion_map[sel]
                catch_fish(result)
                st.balloons()
                st.success(f"합성 성공! {result} 획득!")
            else:
                st.error("합성 실패! 2마리 소모됨")
        else:
            st.warning("수량 부족")
else:
    st.info("합성 가능한 물고기가 없습니다.")

# ================= 📚 도감 =================
st.divider()
st.subheader("📚 물고기 도감")

st.markdown("##### 🐟 일반 물고기")
cols = st.columns(5)
for i, fish in enumerate(fish_list):
    with cols[i % 5]:
        status = "✔ 발견" if fish in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{fish}** ({status})")

st.markdown("##### 💎 특수 아이템")
special_items = ["오래된 지도 조각"]
cols_special = st.columns(5)
for i, item in enumerate(special_items):
    with cols_special[i % 5]:
        status = "✔ 발견" if item in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{item}** ({status})")

st.markdown("##### ✨ 합성 물고기")
fuse_cols = st.columns(5)
for i, (base, fused) in enumerate(fusion_map.items()):
    with fuse_cols[i % 5]:
        status = "✔ 발견" if fused in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{fused}** ({status})")

st.write("---")
st.write(f"💰 최종 코인: **{st.session_state.coin}**")
st.write(f"🧵 최종 떡밥: **{st.session_state.bait}**")
