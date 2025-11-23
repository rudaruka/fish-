import streamlit as st
import random
from collections import Counter

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

# 🌟 새로운 아이템 및 가격 정의
price_map["오래된 지도 조각"] = 5000
price_map["완성된 오래된 지도"] = 25000

shop_items = {
    "떡밥": {
        "price": 50,
        "desc": "낚시 1회당 1개가 필요합니다!!"
    }
}

ROD_UPGRADE_COSTS = {
    1: {"coin": 2000, "success_rate": 0.8},
    2: {"coin": 4000, "success_rate": 0.6},
    3: {"coin": 8000, "success_rate": 0.4},
}

# 🌟 도감 완성 체크를 위한 모든 수집 항목 정의 (지도 완성본 추가)
SPECIAL_ITEMS = ["오래된 지도 조각", "완성된 오래된 지도"]
FUSED_FISH = list(fusion_map.values())
ALL_COLLECTIBLES = set(fish_list) | set(SPECIAL_ITEMS) | set(FUSED_FISH)

# ================= 1. 세션 초기화 =================
def initialize_session_state():
    defaults = {
        "coin": 0,
        "inventory": [],
        "shop_open": False,
        "location": "강가",
        "location_selector": "강가",
        "rod_level": 0,
        "bait": 2,
        "fishbook_complete": False,
        "legendary_unlocked": False,
        "lost_island_unlocked": False
    }

    if "fishbook" not in st.session_state or not isinstance(st.session_state.fishbook, set):
        st.session_state.fishbook = set()

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

initialize_session_state()

# ================= 3. 함수 정의 =================
def check_and_grant_fishbook_reward():
    """도감 완성 여부를 확인하고 보상을 지급합니다. (전설의 해역 잠금 해제)"""
    
    if st.session_state.fishbook_complete:
        return

    if ALL_COLLECTIBLES.issubset(st.session_state.fishbook):
        
        st.session_state.fishbook_complete = True
        st.session_state.legendary_unlocked = True 
        
        st.toast("🎉 도감 완성 보상 획득!", icon='🏆')
        st.balloons()
        st.success("✨ **전설의 낚시꾼** 등극! 새로운 낚시터 **[전설의 해역]** 이 열렸습니다!")


def catch_fish(fish):
    st.session_state.inventory.append(fish)
    st.session_state.fishbook.add(fish)
    check_and_grant_fishbook_reward()

# 🌟 지도 완성 체크 로직 개선: 메시지 출력은 제작 버튼에서만 하도록 분리
def check_for_map_completion():
    # 이미 해금되었거나, 인벤토리에 지도가 없으면 리턴
    if st.session_state.lost_island_unlocked or "완성된 오래된 지도" not in st.session_state.inventory:
        return
    
    # 인벤토리에 지도가 있고, 플래그가 False일 때만 해금 처리
    st.session_state.lost_island_unlocked = True
    st.toast("🏝️ 잃어버린 섬 해금!", icon='🗺️') # 토스트 메시지만 출력 (UX 개선)

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
        elif event == 5 and st.session_state.location == "전설의 해역":
            st.session_state.coin += 500
            st.success("💎 전설의 해역 보너스! 500 코인 획득!")
        elif event == 5 and st.session_state.location == "잃어버린 섬":
            st.session_state.coin += 1500
            st.success("💰 **잃어버린 섬 보너스!** 1500 코인 획득!")
        else:
            st.success("✨ 신비한 바람이 분다… 좋은 기운이 느껴진다!")

# 🌟 get_fishing_weights 함수 수정 (인덱스 접근 안정화 및 가독성 개선)
def get_fishing_weights():
    weights = fish_weights.copy()
    rod_bonus_multiplier = 1 + (st.session_state.rod_level * 0.2)

    # 1. 위치별 가중치 조정
    if st.session_state.location == "바다":
        for i, f in enumerate(fish_list):
            if f in ["전갱이","고등어","꽁치"]:
                weights[i] *= 1.3
            else:
                weights[i] *= 0.8
    elif st.session_state.location == "희귀 낚시터":
        for i, f in enumerate(fish_list):
            if fish_prob.get(f, 1) <= 10: # 희귀 물고기
                weights[i] *= 3
            if f in fusion_map: # 합성 기반 물고기
                 weights[i] *= 1.5
    elif st.session_state.location == "전설의 해역":
        for i, f in enumerate(fish_list):
            if fish_prob.get(f, 1) <= 15:
                weights[i] *= 5
            if f in fusion_map:
                weights[i] *= 2
    elif st.session_state.location == "잃어버린 섬":
        for i, f in enumerate(fish_list):
            if fish_prob.get(f, 1) <= 10:
                weights[i] *= 10
            else:
                weights[i] /= 2
            if f in fusion_map:
                weights[i] *= 5
    
    # 2. 낚싯대 보너스 조정 (희귀 물고기만)
    for i, f in enumerate(fish_list):
        if fish_prob.get(f, 1) <= 10:
            weights[i] *= rod_bonus_multiplier
            
    return weights

# ================= 4. UI =================
check_for_map_completion()

st.title("🎣 낚시터에 오신 것을 환영합니다!!")
st.subheader("이게 첫 작품이라고?! 🐟")

st.write(f"💰 현재 코인: **{st.session_state.coin}**")
st.write(f"🧵 현재 떡밥: **{st.session_state.bait}개**")
st.write(f"✨ 낚싯대 레벨: **Lv.{st.session_state.rod_level}**")

if st.session_state.fishbook_complete:
    st.markdown("---")
    st.info("🏆 **전설의 낚시꾼** 등극! [전설의 해역]이 열렸습니다.")
if st.session_state.lost_island_unlocked:
    st.info("🧭 **잃어버린 섬**의 좌표를 확보했습니다!")
st.divider()

# ================= 낚시터 선택 =================
st.subheader("🌍 낚시터 선택")

current_location = st.session_state.location

LOCATIONS = ["강가", "바다", "희귀 낚시터"]
if st.session_state.legendary_unlocked:
    LOCATIONS.append("전설의 해역")
if st.session_state.lost_island_unlocked:
    LOCATIONS.append("잃어버린 섬")

current_location_index = LOCATIONS.index(current_location) if current_location in LOCATIONS else 0

temp_location = st.selectbox(
    "현재 낚시터",
    LOCATIONS,
    index=current_location_index,
    key="location_selector"
)

if temp_location != current_location:
    if temp_location == "희귀 낚시터":

        required_coin = 1500
        required_fish = {"대멸치": 10, "대붕어": 10}

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
            entry_options.append("코인만 소모 (1500 코인)")
        if has_fish:
            entry_options.append("대멸치 10마리 + 대붕어 10마리 소모")
            
        if not entry_options:
            st.warning("❗ 입장 조건 부족")
            st.session_state.location_selector = current_location
        else: 
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
                
    elif temp_location in ["전설의 해역", "잃어버린 섬"]:
        st.session_state.location = temp_location
        st.success(f"🌌 **{temp_location}** 입장!")

    else:
        st.session_state.location = temp_location
        st.info(f"📍 낚시터를 **{temp_location}** 로 변경")

st.markdown(f"**현재 위치:** {st.session_state.location}")
st.divider()

col1, col2, col3 = st.columns(3)

# ================= 🎣 낚시하기 (잔고 보호 로직 포함) =================
with col1:
    st.subheader("🎣 낚시하기")

    if st.session_state.bait <= 0:
        st.error("❗ 떡밥이 부족합니다! 상점에서 구매하거나 제작하세요.")

    current_location = st.session_state.location
    prefix = ""
    if current_location == "잃어버린 섬":
        prefix = "🔱 "
        event_rate = 0.45
        success_msg_prefix = "전설의 "
    elif current_location == "전설의 해역":
        prefix = "🌌 "
        event_rate = 0.35
        success_msg_prefix = "희귀한 "
    elif current_location == "희귀 낚시터":
        prefix = "💎 "
        event_rate = 0.25
        success_msg_prefix = "빛나는 "
    else: # 강가, 바다
        prefix = "🎣 "
        event_rate = 0.15
        success_msg_prefix = ""

    # 1번 낚시 (떡밥 1 소모)
    button_text_1 = f"{prefix}1번 낚시 **(떡밥 1 소모)**"
    if st.button(button_text_1, key="fish_1", disabled=st.session_state.bait < 1):
        if st.session_state.bait < 1: 
            st.error("❗ 떡밥이 부족하여 낚시를 진행할 수 없습니다.")
        else:
            st.session_state.bait -= 1 
            fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
            catch_fish(fish)
            st.success(f"{prefix}{success_msg_prefix}**{fish}** 낚았다! (남은 떡밥: {st.session_state.bait}개)")
            random_event(event_rate)
    
    # 2번 낚시 (떡밥 2 소모)
    button_text_2 = f"{prefix}2번 낚시 **(떡밥 2 소모)**"
    if st.button(button_text_2, key="fish_2", disabled=st.session_state.bait < 2):
        if st.session_state.bait < 2: 
            st.error("❗ 떡밥이 부족하여 낚시를 진행할 수 없습니다.")
        else:
            st.session_state.bait -= 2 
            fish_caught = random.choices(fish_list, weights=get_fishing_weights(), k=2)
            for f in fish_caught: catch_fish(f)
            st.success(f"{prefix}{success_msg_prefix}{', '.join(fish_caught)} 낚았다! (남은 떡밥: {st.session_state.bait}개)")
            random_event(event_rate + 0.1)


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
    # ===== 낚싯대 강화 / 아이템 구매 / 판매 =====
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

    st.subheader("🛒 아이템 구매")
    
    # 떡밥 대량 구매 기능
    bait_item = shop_items["떡밥"]
    bait_price = bait_item["price"]

    st.write(f"**{bait_item}** ({bait_price} 코인/개)")
    st.caption(bait_item["desc"])

    purchase_qty = st.number_input("구매할 떡밥 개수", min_value=1, value=1, step=1, key="bait_qty")
    total_cost = purchase_qty * bait_price
    
    st.write(f"총 코인: **{total_cost}**")

    can_purchase = st.session_state.coin >= total_cost

    if st.button(f"떡밥 {purchase_qty}개 구매", key="buy_bait_multi", disabled=not can_purchase):
        if can_purchase:
            st.session_state.coin -= total_cost
            st.session_state.bait += purchase_qty
            st.success(f"떡밥 {purchase_qty}개 구매 완료! (-{total_cost} 코인)")
        else:
            st.error("❗ 코인 부족!")
    
    st.markdown("---")
    
    # 판매
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

# ================= 🔧 떡밥 제작 =================
st.divider()
st.subheader("🧵 떡밥 제작")
st.caption("동일한 물고기 2마리를 갈아서 떡밥 1개로 만듭니다. (저렴한 물고기를 사용하는 것이 유리합니다.)")

counts = Counter(st.session_state.inventory)
excluded_items_craft = list(fusion_map.values()) + SPECIAL_ITEMS
craft_candidates = [f for f, count in counts.items() if count >= 2 and f not in excluded_items_craft]

if craft_candidates:
    selected_fish_to_grind = st.selectbox("분쇄할 물고기 선택 (2마리 소모)", craft_candidates, key="craft_select")
    
    # 🌟 떡밥 제작 수량 입력 필드 추가
    max_craftable = counts.get(selected_fish_to_grind, 0) // 2
    craft_qty = st.number_input("제작할 떡밥 개수", min_value=1, max_value=max_craftable, value=min(1, max_craftable), step=1, key="craft_qty")

    if st.button(f"'{selected_fish_to_grind}' {craft_qty * 2}개 갈아서 떡밥 {craft_qty}개 제작", key="craft_btn", disabled=max_craftable==0):
        total_fish_needed = craft_qty * 2
        if counts.get(selected_fish_to_grind, 0) >= total_fish_needed:
            for _ in range(total_fish_needed):
                st.session_state.inventory.remove(selected_fish_to_grind)
            st.session_state.bait += craft_qty
            st.success(f"**{selected_fish_to_grind}** {total_fish_needed}마리 분쇄 완료! 🧵 **떡밥 {craft_qty}개** 획득! (현재 떡밥: {st.session_state.bait}개)")
        else:
            st.warning("물고기 수가 부족합니다.")
else:
    st.info("떡밥 제작 가능한 물고기가 없습니다. (동일 물고기 2마리 필요)")

# ================= ⚡ 지도 조각 합성 =================
st.subheader("🧭 지도 조각 합성")
MAP_PIECE_COUNT = counts.get("오래된 지도 조각", 0)
MAP_PIECES_REQUIRED = 10
can_craft_map = MAP_PIECE_COUNT >= MAP_PIECES_REQUIRED

st.caption(f"**오래된 지도 조각** 10개를 모으면 **완성된 오래된 지도**를 제작할 수 있습니다.")
st.write(f"현재 보유: {MAP_PIECE_COUNT}개 / 필요: {MAP_PIECES_REQUIRED}개")

if st.button("🗺️ 완성된 오래된 지도 제작 (조각 10개 소모)", key="craft_map_btn", disabled=not can_craft_map):
    if can_craft_map:
        for _ in range(MAP_PIECES_REQUIRED):
            st.session_state.inventory.remove("오래된 지도 조각")
        
        catch_fish("완성된 오래된 지도")
        
        st.balloons()
        st.success("🎉 **완성된 오래된 지도** 제작 성공! 새로운 낚시터가 해금되었습니다! 🧭")
    else:
        st.error("❗ 지도 조각이 부족합니다.")


# ================= ⚡ 물고기 합성 =================
st.subheader("⚡ 물고기 합성")

counts = Counter(st.session_state.inventory)
fusion_candidates = [f for f in fusion_map.keys() if counts.get(f,0) >= 2]

if fusion_candidates:
    sel = st.selectbox("합성할 물고기 선택", fusion_candidates, key="fusion_select")
    
    # 🌟 물고기 합성 수량 입력 필드 추가
    max_fusion_attempts = counts.get(sel, 0) // 2
    fusion_qty = st.number_input("합성 시도 횟수", min_value=1, max_value=max_fusion_attempts, value=min(1, max_fusion_attempts), step=1, key="fusion_qty")

    if st.button(f"물고기 {fusion_qty * 2}개로 {fusion_qty}회 합성 시도", key="fusion_btn", disabled=max_fusion_attempts==0):
        total_fish_needed = fusion_qty * 2
        success_count = 0
        
        if counts.get(sel,0) >= total_fish_needed:
            for _ in range(total_fish_needed):
                st.session_state.inventory.remove(sel)
            
            for _ in range(fusion_qty):
                if random.choice([True, False]): # 50% 확률 성공
                    result = fusion_map[sel]
                    catch_fish(result)
                    success_count += 1
            
            if success_count > 0:
                st.balloons()
                st.success(f"합성 시도 {fusion_qty}회 완료. **{fusion_map[sel]}** {success_count}개 획득!")
            else:
                st.error(f"합성 시도 {fusion_qty}회 완료. 아쉽게도 **모두 실패**했습니다. {total_fish_needed}마리 소모됨.")
        else:
            st.warning("수량 부족")
else:
    st.info("합성 가능한 물고기가 없습니다.")

# ================= 📚 도감 =================
st.divider()
st.subheader(f"📚 물고기 도감 ({len(st.session_state.fishbook)}/{len(ALL_COLLECTIBLES)})")

st.markdown("##### 🐟 일반 물고기")
cols = st.columns(5)
for i, fish in enumerate(fish_list):
    with cols[i % 5]:
        status = "✔ 발견" if fish in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{fish}** ({status})")

st.markdown("##### 💎 특수 아이템")
cols_special = st.columns(5)
for i, item in enumerate(SPECIAL_ITEMS):
    with cols_special[i % 5]:
        status = "✔ 발견" if item in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{item}** ({status})")

st.markdown("##### ✨ 합성 물고기")
fuse_cols = st.columns(5)
for i, fused in enumerate(FUSED_FISH):
    with fuse_cols[i % 5]:
        status = "✔ 발견" if fused in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{fused}** ({status})")

st.write("---")
st.write(f"💰 최종 코인: **{st.session_state.coin}**")
st.write(f"🧵 최종 떡밥: **{st.session_state.bait}**")
