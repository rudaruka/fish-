import streamlit as st
import random
from collections import Counter

# ================= 2. 물고기 & 가격 정의 =================
fish_prob = {
    # 🐟 일반/흔함 물고기 (Prob 15~30, 강가/바다)
    "멸치": 25, "복어": 25, "누치": 20, "정어리": 15, 
    "빙어": 10, "북어": 10, "꽁치": 10, "은어": 8, "노래미": 7, "쥐치": 5, 
    "고등어": 7, "전갱이": 10,
    "피라냐": 30, "메기": 20, "송어": 20, "붕어": 25, "잉어": 15, "향어": 20,
    "가물치": 25, "쏘가리": 15, "붕장어": 20, "갯장어": 15, "우럭": 15, "삼치": 15,

    # 🦈 희귀 물고기 (Prob 4~10, 바다/희귀 낚시터)
    "참치": 10, "연어": 8, "광어": 7, "도미": 7, "농어": 6, "아귀": 5, 
    "볼락": 5, "갈치": 4, "병어": 4,

    # 🦀 특수/초희귀 물고기 (Prob 1~3, 전설/잃어버린 섬)
    "청새치": 3, "황새치": 2, "랍스터": 2, "킹크랩": 1, "개복치": 1, "해마": 3,

    # ✨ 새로운 합성 기반 물고기 (Prob 15~20, 합성 재료)
    "방어": 20, "날치": 15, "열기": 15,
    
    # 🔱 심해/전설 물고기 (Prob 0.5, 잃어버린 섬 전용)
    "메가참치": 0.5, "번개상어": 0.5, "심연참돔": 0.5 
}

fish_list = list(fish_prob.keys())
fish_weights = list(fish_prob.values())
price_map = {fish: int((100 - prob) * 1) for fish, prob in fish_prob.items()} 

fusion_map = {
    "멸치": "대멸치", "복어": "대복어", "누치": "대누치",
    "정어리": "대정어리", "붕어": "대붕어",
    "방어": "대방어", "날치": "대날치", "열기": "대열기"
}

for base, fused in fusion_map.items():
    price_map[fused] = int(price_map.get(base, 0) * 5)

price_map["오래된 지도 조각"] = 5000
price_map["완성된 오래된 지도"] = 50000
price_map["떡밥"] = 50 

# 🎣 물가 상승 상수 정의 (지속적 증가)
MAX_BAIT_INCREASE = 1500 # 최대 가격 상승 한도
BAIT_INCREASE_STEP = 10  # 1회 상승량
CATCH_THRESHOLD_FOR_STEP = 10 # 10마리마다 상승
BAIT_BASE_PRICE = 200

shop_items = {
    "떡밥": {
        "price": BAIT_BASE_PRICE,
        "desc": "낚시 1회당 1개 필요!",
        "price_increase": 0 # 물가 상승 누적액
    }
}


ROD_UPGRADE_COSTS = {
    1: {"coin": 2000, "success_rate": 0.8},
    2: {"coin": 4000, "success_rate": 0.6},
    3: {"coin": 8000, "success_rate": 0.4},
}

SPECIAL_ITEMS = ["오래된 지도 조각", "완성된 오래된 지도"]
FUSED_FISH = list(fusion_map.values())
ALL_COLLECTIBLES = set(fish_list) | set(SPECIAL_ITEMS) | set(FUSED_FISH)
EXCLUDED_FROM_QUICK_SELL = SPECIAL_ITEMS + FUSED_FISH

RARE_LOCATION_COSTS = {
    "coin": 1500,
    "fish": {"대멸치": 10, "대붕어": 10, "대복어": 10, "대방어": 10, "대날치": 10} 
}

# ================= 1. 세션 초기화 =================
def initialize_session_state():
    defaults = {
        "coin": 0,
        "inventory": [],
        "shop_open": False,
        "inventory_open": False, 
        "fishbook_open": False,  
        "location": "강가",
        "location_selector": "강가",
        "rod_level": 0,
        "bait": 4, 
        "fishbook_complete": False,
        "legendary_unlocked": False,
        "lost_island_unlocked": False,
        "total_fish_caught": 0, # 물가 상승을 위한 총 낚시 마릿수
    }

    if "fishbook" not in st.session_state or not isinstance(st.session_state.fishbook, set):
        st.session_state.fishbook = set()

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # 레벨 기반 인플레이션을 제거했으므로, 관련된 세션 상태 변수 초기화 제거

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

def check_for_map_completion():
    """인벤토리에 완성된 지도가 있으면 잃어버린 섬을 해금합니다."""
    if st.session_state.lost_island_unlocked or "완성된 오래된 지도" not in st.session_state.inventory:
        return
    
    st.session_state.lost_island_unlocked = True
    st.toast("🏝️ 잃어버린 섬 해금!", icon='🗺️')


def update_bait_price():
    """총 낚시 마릿수에 따라 떡밥 가격을 지속적으로 인상하고, 최대치(1500)로 제한합니다."""
    
    current_count = st.session_state.total_fish_caught
    
    # 1. 10마리당 10 코인씩 오르는 잠재적 인상액 계산
    # 예: 50마리 -> (50 // 10) * 10 = 50
    # 예: 105마리 -> (105 // 10) * 10 = 100
    potential_increase = (current_count // CATCH_THRESHOLD_FOR_STEP) * BAIT_INCREASE_STEP
    
    # 2. 최대 상승액 (1500)으로 제한
    new_increase = min(potential_increase, MAX_BAIT_INCREASE)
    
    current_increase = shop_items["떡밥"]["price_increase"] 

    if new_increase != current_increase:
        # 물가 상승이 발생한 경우만 토스트 알림
        if new_increase > current_increase:
             st.toast(f"💰 물가 상승! 떡밥 가격 +{new_increase - current_increase} 코인", icon='📈')

        shop_items["떡밥"]["price"] = BAIT_BASE_PRICE + new_increase # 실제 가격 업데이트
        shop_items["떡밥"]["price_increase"] = new_increase # 누적 상승액 업데이트
        st.session_state.coin = int(st.session_state.coin) # 코인 정수화 유지


def random_event(event_rate, location):
    """
    랜덤 이벤트를 발생시키고 결과를 요약 딕셔너리로 반환합니다. 
    이벤트 발동 시 코인 값은 int()로 명시적으로 형 변환하여 소수점을 방지합니다.
    """
    summary = {
        'coin': 0, 'bonus_fish': [], 'lost_fish': [], 
        'map_pieces': 0, 'special_bonus': 0, 'no_effect': 0
    }
    
    if random.random() < event_rate: 
        event = random.randint(1, 5)
        
        if event == 1: # 코인 보너스
            bonus = random.randint(10, 80)
            st.session_state.coin = int(st.session_state.coin + bonus) 
            summary['coin'] += bonus
        
        elif event == 2: # 물고기 보너스
            f2 = random.choice(fish_list)
            catch_fish(f2)
            summary['bonus_fish'].append(f2)
            
        elif event == 3: # 물고기 손실
            if st.session_state.inventory:
                losable_items = [i for i in st.session_state.inventory if i not in SPECIAL_ITEMS]
                if losable_items:
                    lost = random.choice(losable_items)
                    st.session_state.inventory.remove(lost)
                    summary['lost_fish'].append(lost)
                else:
                    summary['no_effect'] += 1
            else:
                summary['no_effect'] += 1
                
        elif event == 5 and location == "희귀 낚시터": # 지도 조각 획득
            item_name = "오래된 지도 조각"
            catch_fish(item_name)
            summary['map_pieces'] += 1
            
        elif event == 5 and location == "전설의 해역": # 전설 해역 보너스 코인
            st.session_state.coin = int(st.session_state.coin + 500) 
            summary['special_bonus'] += 500
        
        elif event == 5 and location == "잃어버린 섬": # 잃어버린 섬 보너스 코인
            st.session_state.coin = int(st.session_state.coin + 1500) 
            summary['special_bonus'] += 1500
            
        else: # 기타 긍정적 효과 (메시지 대신 누적)
            summary['no_effect'] += 1
    
    return summary


def get_fishing_weights():
    weights = fish_weights.copy()
    rod_bonus_multiplier = 1 + (st.session_state.rod_level * 0.2)

    # 1. 위치별 가중치 조정 (로직 생략 - 변화 없음)
    if st.session_state.location == "바다":
        for i, f in enumerate(fish_list):
            if f in ["고등어", "전갱이", "꽁치", "우럭", "삼치", "참치", "광어", "도미", "농어", "갈치", "병어", "청새치", "황새치", "랍스터", "킹크랩"]:
                weights[i] *= 1.5 
            else:
                weights[i] *= 0.5 
    elif st.session_state.location == "희귀 낚시터":
        for i, f in enumerate(fish_list):
            if fish_prob.get(f, 1) <= 10 or f in ["참치", "연어", "광어"]:
                weights[i] *= 4 
            if f in fusion_map:
                 weights[i] *= 2
    elif st.session_state.location == "전설의 해역":
        for i, f in enumerate(fish_list):
            if fish_prob.get(f, 1) <= 10 or f in ["청새치", "황새치", "랍스터", "킹크랩", "개복치"]:
                weights[i] *= 8
            if f in fusion_map:
                weights[i] *= 3
    elif st.session_state.location == "잃어버린 섬":
        for i, f in enumerate(fish_list):
            if f in ["킹크랩", "개복치", "메가참치", "번개상어", "심연참돔"]:
                weights[i] *= 25 
            else:
                weights[i} /= 10 
            if f in fusion_map:
                weights[i] *= 0 
    
    # 2. 낚싯대 보너스 조정 (희귀 물고기만)
    for i, f in enumerate(fish_list):
        if fish_prob.get(f, 1) <= 10: 
            weights[i] *= rod_bonus_multiplier
            
    return weights


# ================= 4. UI =================
st.title("🎣 낚시터에 오신 것을 환영합니다!!")
st.subheader("이게 첫 작품이라고?! 🐟")

st.write(f"💰 현재 코인: **{int(st.session_state.coin)}**")
st.write(f"🧵 현재 떡밥: **{st.session_state.bait}개**")
st.write(f"✨ 낚싯대 레벨: **Lv.{st.session_state.rod_level}**")
st.caption(f"🐟 **총 낚시 마릿수:** {st.session_state.total_fish_caught}마리") 

if st.session_state.fishbook_complete:
    st.markdown("---")
    st.info("🏆 **전설의 낚시꾼** 등극! [전설의 해역]이 열렸습니다.")
if st.session_state.lost_island_unlocked:
    st.info("🧭 **잃어버린 섬**의 좌표를 확보했습니다!")
st.divider()

# ================= 낚시터 선택 =================
# (로직 생략 - 변화 없음)
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

# 낚시터 변경 로직
if temp_location != current_location:
    if temp_location == "희귀 낚시터":
        
        required_coin = RARE_LOCATION_COSTS["coin"]
        required_fish = RARE_LOCATION_COSTS["fish"]
        current_inventory_counts = Counter(st.session_state.inventory)
        
        has_coin = st.session_state.coin >= required_coin
        has_fish = all(current_inventory_counts.get(name, 0) >= qty for name, qty in required_fish.items())

        st.markdown("##### 💎 희귀 낚시터 입장 조건")
        st.write(f"💰 코인: **{required_coin}** (현재: {int(st.session_state.coin)})")

        fish_status_msg = ""
        for name, qty in required_fish.items():
            current_qty = current_inventory_counts.get(name, 0)
            status = '✔' if current_qty >= qty else '✖'
            fish_status_msg += f"**{name}** {qty}마리 (현재 {current_qty}개) ({status}) / "
        st.write(f"🐟 물고기: {fish_status_msg[:-3]}")
        st.markdown("---")
        st.caption("입장 후에는 낚시터가 변경됩니다.")
        
        can_enter_by_coin = has_coin
        can_enter_by_fish = has_fish

        if can_enter_by_coin or can_enter_by_fish:
            
            if can_enter_by_coin:
                if st.button(f"💰 코인 소모 입장 ({required_coin} 코인)", key="enter_rare_coin"):
                    st.session_state.coin = int(st.session_state.coin - required_coin)
                    st.session_state.location = temp_location
                    st.success(f"🔥 희귀 낚시터 입장! (-{required_coin} 코인)")
                    st.rerun() 
            
            if can_enter_by_fish:
                fish_cost_str = f"({' + '.join([f'{name} {qty}마리' for name, qty in required_fish.items()])} 소모)"
                if st.button(f"🐟 물고기 소모 입장 {fish_cost_str}", key="enter_rare_fish"):
                    for name, qty in required_fish.items():
                        for _ in range(qty):
                            st.session_state.inventory.remove(name)
                    
                    st.session_state.location = temp_location
                    st.success("🔥 희귀 낚시터 입장! (물고기 소모)")
                    st.rerun() 

        else:
            st.warning("❗ 입장 조건 부족")
            st.session_state.location_selector = current_location
            
    elif temp_location in ["전설의 해역", "잃어버린 섬"]:
        st.session_state.location = temp_location
        st.success(f"🌌 **{temp_location}** 입장!")
        st.rerun()
    
    else: 
        st.session_state.location = temp_location
        st.info(f"📍 낚시터를 **{temp_location}** 로 변경")
        st.rerun()

st.markdown(f"**현재 위치:** {st.session_state.location}")
st.divider()

col1, col2, col3 = st.columns(3)

# ================= 🎣 낚시하기 =================
with col1:
    st.subheader("🎣 낚시하기")

    if st.session_state.bait <= 0:
        st.error("❗ 떡밥이 부족합니다! 상점에서 구매하거나 제작하세요.")

    current_location = st.session_state.location
    if current_location == "잃어버린 섬":
        prefix, event_rate, success_msg_prefix = "🔱 ", 0.45, "전설의 "
    elif current_location == "전설의 해역":
        prefix, event_rate, success_msg_prefix = "🌌 ", 0.35, "희귀한 "
    elif current_location == "희귀 낚시터":
        prefix, event_rate, success_msg_prefix = "💎 ", 0.25, "빛나는 "
    else:
        prefix, event_rate, success_msg_prefix = "🎣 ", 0.15, ""

    # 1번 낚시 (떡밥 1 소모)
    button_text_1 = f"{prefix}1번 낚시 **(떡밥 1 소모)**"
    if st.button(button_text_1, key="fish_1", disabled=st.session_state.bait < 1):
        if st.session_state.bait >= 1:
            st.session_state.bait -= 1 
            fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
            catch_fish(fish)
            st.success(f"{prefix}{success_msg_prefix}**{fish}** 낚았다! (남은 떡밥: {st.session_state.bait}개)")
            
            st.session_state.total_fish_caught += 1
            update_bait_price() 
            
            event_result = random_event(event_rate, current_location)
            if any(event_result.values()):
                st.info("🎲 랜덤 이벤트 발동!")
            
            st.rerun()
    
    # 2번 낚시 (떡밥 2 소모)
    button_text_2 = f"{prefix}2번 낚시 **(떡밥 2 소모)**"
    if st.button(button_text_2, key="fish_2", disabled=st.session_state.bait < 2):
        if st.session_state.bait >= 2:
            st.session_state.bait -= 2 
            fish_caught = random.choices(fish_list, weights=get_fishing_weights(), k=2)
            for f in fish_caught: catch_fish(f)
            st.success(f"{prefix}{success_msg_prefix}{', '.join(fish_caught)} 낚았다! (남은 떡밥: {st.session_state.bait}개)")
            
            st.session_state.total_fish_caught += 2
            update_bait_price()

            event_result = random_event(event_rate + 0.1, current_location)
            if any(event_result.values()):
                st.info("🎲 랜덤 이벤트 발동!")

            st.rerun()

    # 3번 낚시 (떡밥 모두 소모) 
    bait_count = st.session_state.bait
    button_text_3 = f"{prefix}**물고기 전체 낚기!** (떡밥 {bait_count}개 소모)" 
    
    if st.button(button_text_3, key="fish_all", disabled=bait_count < 1):
        if bait_count >= 1:
            
            # 1. 낚시 결과 처리
            fish_caught = random.choices(fish_list, weights=get_fishing_weights(), k=bait_count)
            for f in fish_caught: catch_fish(f)
            
            st.session_state.bait = 0
            
            if bait_count == 1:
                 st.success(f"{prefix}{success_msg_prefix}{fish_caught[0]} 낚았다! (떡밥 모두 소진)")
            else:
                catch_counts = Counter(fish_caught)
                summary_msg = ', '.join([f'{f} x{c}' for f, c in catch_counts.items()])
                st.success(f"{prefix}{success_msg_prefix}총 **{bait_count}회** 낚시 성공! ({summary_msg}) (떡밥 모두 소진)")
            
            st.session_state.total_fish_caught += bait_count
            update_bait_price() 

            # 2. 이벤트 결과 누적 및 요약
            total_event_summary = {
                'coin': 0, 'bonus_fish': [], 'lost_fish': [], 
                'map_pieces': 0, 'special_bonus': 0, 'no_effect': 0
            }
            events_triggered = 0
            
            for _ in range(bait_count):
                event_result = random_event(event_rate, current_location)
                
                if any(event_result.values()):
                    events_triggered += 1
                    total_event_summary['coin'] += event_result['coin']
                    total_event_summary['bonus_fish'].extend(event_result['bonus_fish'])
                    total_event_summary['lost_fish'].extend(event_result['lost_fish'])
                    total_event_summary['map_pieces'] += event_result['map_pieces']
                    total_event_summary['special_bonus'] += event_result['special_bonus']
                    total_event_summary['no_effect'] += event_result['no_effect']
            
            # 3. 최종 이벤트 요약 메시지 출력
            summary_messages = []
            
            if total_event_summary['coin'] > 0:
                summary_messages.append(f"💰 보너스 코인: **+{total_event_summary['coin']}**")
                
            if total_event_summary['bonus_fish']:
                bonus_fish_counts = Counter(total_event_summary['bonus_fish'])
                fish_list_str = ', '.join([f'{f} x{c}' for f, c in bonus_fish_counts.items()])
                summary_messages.append(f"🎣 보너스 물고기: **{fish_list_str}**")
            
            if total_event_summary['lost_fish']:
                lost_fish_counts = Counter(total_event_summary['lost_fish'])
                lost_list_str = ', '.join([f'{f} x{c}' for f, c in lost_fish_counts.items()])
                summary_messages.append(f"🔥 물고기 손실: **{lost_list_str}**")
            
            if total_event_summary['map_pieces'] > 0:
                summary_messages.append(f"🗺️ 지도 조각: **+{total_event_summary['map_pieces']}**")

            if total_event_summary['special_bonus'] > 0:
                summary_messages.append(f"💎 특수 보너스 코인: **+{total_event_summary['special_bonus']}**")

            # 요약 메시지 출력
            if events_triggered > 0:
                st.info(f"🎲 랜덤 이벤트 **{events_triggered}회** 발동 결과:\n\n* " + "\n* ".join(summary_messages))
            else:
                 st.info("🎲 랜덤 이벤트 발생 없음.")

            st.rerun()


# ================= 🎒 인벤토리 (토글) =================
with col2:
    # (로직 생략 - 변화 없음)
    open_inventory = st.checkbox("🎒 인벤토리 열기", value=st.session_state.inventory_open, key="inventory_open_cb")
    st.session_state.inventory_open = open_inventory
    
    if st.session_state.inventory_open:
        st.write("---")
        display_inventory = st.session_state.inventory.copy()

        if display_inventory:
            counts = Counter(display_inventory)
            for item, cnt in counts.items():
                sell_note = " (⚠️수동 전용)" if item in EXCLUDED_FROM_QUICK_SELL else ""
                st.write(f"**{item}** x {cnt} (판매가: {price_map.get(item,'N/A')} 코인){sell_note}")
        else:
            st.info("인벤토리가 비어 있습니다.")

# ================= 🏪 상점 / 강화 =================
with col3:
    st.subheader("🏪 상점 / 강화")
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open, key="shop_open_cb")
    st.session_state.shop_open = open_shop

st.divider()

if st.session_state.shop_open:
    
    # --- 낚싯대 강화 ---
    st.subheader("🛠️ 낚싯대 강화")

    current_level = st.session_state.rod_level
    next_level = current_level + 1

    if next_level in ROD_UPGRADE_COSTS:
        cost = ROD_UPGRADE_COSTS[next_level]

        st.write(f"현재 레벨: Lv.{current_level}")
        st.write(f"다음 레벨: Lv.{next_level}")
        st.write(f"필요 코인: {cost['coin']} (현재: {int(st.session_state.coin)})")

        can_upgrade = st.session_state.coin >= cost['coin']
        if st.button(f"Lv.{next_level} 강화 시도", disabled=not can_upgrade, key=f"upgrade_{next_level}"):
            st.session_state.coin = int(st.session_state.coin - cost['coin'])
            if random.random() < cost['success_rate']:
                st.session_state.rod_level = next_level
                st.success(f"🎉 강화 성공! Lv.{next_level}")
            else:
                st.error("💥 강화 실패! 코인만 소모")
            st.rerun()
    else:
        st.info(f"최고 레벨 Lv.{current_level}입니다!")

    # --- 아이템 구매 (떡밥) ---
    st.subheader("🛒 아이템 구매")
    
    bait_item = shop_items["떡밥"]
    bait_price = bait_item["price"]
    increase = bait_item["price_increase"]

    st.write(f"**떡밥** ({BAIT_BASE_PRICE} 코인/개 **+ 물가 상승 {increase} 코인**) -> **{bait_price} 코인/개**")
    st.caption(f"최대 가격은 {BAIT_BASE_PRICE + MAX_BAIT_INCREASE} 코인입니다.")

    purchase_qty = st.number_input("구매할 떡밥 개수", min_value=1, value=1, step=1, key="bait_qty")
    total_cost = purchase_qty * bait_price
    
    st.write(f"총 코인: **{total_cost}**")

    can_purchase = st.session_state.coin >= total_cost

    if st.button(f"떡밥 {purchase_qty}개 구매", key="buy_bait_multi", disabled=not can_purchase):
        if can_purchase:
            st.session_state.coin = int(st.session_state.coin - total_cost)
            st.session_state.bait += purchase_qty
            st.success(f"떡밥 {purchase_qty}개 구매 완료! (-{total_cost} 코인)")
            st.rerun()
        else:
            st.error("❗ 코인 부족!")
    
    st.markdown("---")
    
    # --- 판매 ---
    # (로직 생략 - 변화 없음)
    st.subheader("💰 판매")
    
    if st.session_state.inventory:
        
        counts = Counter(st.session_state.inventory)
        total_sell_coin = 0
        sellable_items = []
        
        for item, qty in counts.items():
            if item not in EXCLUDED_FROM_QUICK_SELL:
                price = price_map.get(item, 0)
                total_sell_coin += price * qty
                sellable_items.append((item, qty))

        if total_sell_coin > 0:
            st.write(f"**일반 물고기 전체 판매 예상 수입:** **{total_sell_coin}** 코인")
            
            if st.button("🐟 일반 물고기 전체 판매", key="sell_all_btn"):
                
                total_items_sold = 0
                for item, qty in sellable_items:
                    total_items_sold += qty
                    for _ in range(qty):
                        st.session_state.inventory.remove(item)
                        
                st.session_state.coin = int(st.session_state.coin + total_sell_coin)
                st.success(f"총 {total_items_sold}마리 판매 완료! +{total_sell_coin} 코인")
                st.rerun()
                
        else:
             st.info("현재 일반 물고기가 없습니다.")

        st.markdown("---")
        st.caption(f"**수동 판매/합성 전용:** {', '.join(EXCLUDED_FROM_QUICK_SELL)}은 전체 판매에서 제외됩니다.")

        selected = st.multiselect(
            "판매할 아이템 선택 (수동)",
            st.session_state.inventory,
            format_func=lambda x: f"{x} ({price_map.get(x,'N/A')} 코인)",
            key="sell_select"
        )

        if st.button("판매", key="sell_btn"):
            counts = Counter(st.session_state.inventory)
            selected_counts = Counter(selected)
            total = 0
            items_sold_count = 0

            for item, qty in selected_counts.items():
                sell_qty = min(qty, counts[item])
                items_sold_count += sell_qty
                for _ in range(sell_qty):
                    st.session_state.inventory.remove(item)
                total += price_map.get(item, 0) * sell_qty

            if total > 0:
                st.session_state.coin = int(st.session_state.coin + total)
                st.success(f"{items_sold_count}개 판매 완료! +{total} 코인")
                st.rerun()
    else:
        st.warning("판매할 아이템이 없습니다.")

# ================= 🔧 떡밥 제작 =================
# (로직 생략 - 변화 없음)
st.divider()
st.subheader("🧵 떡밥 제작")
st.caption("동일한 물고기 2마리를 갈아서 떡밥 1개로 만듭니다. (저렴한 물고기를 사용하는 것이 유리합니다.)")

counts = Counter(st.session_state.inventory)
excluded_items_craft = list(fusion_map.values()) + SPECIAL_ITEMS
craft_candidates = [f for f, count in counts.items() if count >= 2 and f not in excluded_items_craft]

# 🌟 1. 떡밥 전체 제작 로직
st.markdown("##### ⚡ 떡밥 전체 제작 (최적 재료 사용)")

# 판매가가 가장 낮은 물고기를 찾습니다 (가장 효율적인 재료)
best_craft_fish = None
min_price = float('inf')

# 떡밥 제작 가능 항목 중 가장 저렴한 것을 찾기
for fish, count in counts.items():
    if count >= 2 and fish not in excluded_items_craft:
        price = price_map.get(fish, float('inf'))
        if price < min_price:
            min_price = price
            best_craft_fish = fish

if best_craft_fish:
    max_craftable = counts.get(best_craft_fish, 0) // 2
    
    st.write(f"✅ **최적의 제작 재료:** **{best_craft_fish}** (판매가: {min_price} 코인)")
    st.write(f"최대 제작 가능 떡밥: **{max_craftable}개** (재료: {best_craft_fish} {max_craftable * 2}개 소모)")

    if st.button(f"🧵 {best_craft_fish} 전체 사용하여 떡밥 {max_craftable}개 제작", key="craft_all_btn"):
        total_fish_needed = max_craftable * 2
        
        for _ in range(total_fish_needed):
            st.session_state.inventory.remove(best_craft_fish)
            
        st.session_state.bait += max_craftable
        st.success(f"**{best_craft_fish}** {total_fish_needed}개 분쇄 완료! 🧵 **떡밥 {max_craftable}개** 획득!")
        st.rerun()
else:
    st.info("현재 떡밥 전체 제작에 사용할 수 있는 물고기가 없습니다. (동일 물고기 2마리 필요)")

st.markdown("---")

# 🌟 2. 수동 제작 (기존 로직 유지)
st.markdown("##### 🛠️ 수동 제작")

if craft_candidates:
    selected_fish_to_grind = st.selectbox("분쇄할 물고기 선택 (2마리 소모)", craft_candidates, key="craft_select")
    
    max_craftable = counts.get(selected_fish_to_grind, 0) // 2
    craft_qty = st.number_input("제작할 떡밥 개수", min_value=1, max_value=max_craftable, value=min(1, max_craftable), step=1, key="craft_qty")

    if st.button(f"'{selected_fish_to_grind}' {craft_qty * 2}개 갈아서 떡밥 {craft_qty}개 제작", key="craft_btn", disabled=max_craftable==0):
        total_fish_needed = craft_qty * 2
        if counts.get(selected_fish_to_grind, 0) >= total_fish_needed:
            for _ in range(total_fish_needed):
                st.session_state.inventory.remove(selected_fish_to_grind)
            st.session_state.bait += craft_qty
            st.success(f"**{selected_fish_to_grind}** {total_fish_needed}마리 분쇄 완료! 🧵 **떡밥 {craft_qty}개** 획득! (현재 떡밥: {st.session_state.bait}개)")
            st.rerun()
        else:
            st.warning("물고기 수가 부족합니다.")
else:
    st.info("수동 제작 가능한 물고기가 없습니다. (동일 물고기 2마리 필요)")

# ================= ⚡ 지도 조각 합성 =================
# (로직 생략 - 변화 없음)
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
        
        check_for_map_completion() 
        
        st.balloons()
        st.success("🎉 **완성된 오래된 지도** 제작 성공! 새로운 낚시터가 해금되었습니다! 🧭")
        st.rerun()
    else:
        st.error("❗ 지도 조각이 부족합니다.")


# ================= ⚡ 물고기 합성 =================
# (로직 생략 - 변화 없음)
st.subheader("⚡ 물고기 합성")

counts = Counter(st.session_state.inventory)
fusion_candidates = [f for f in fusion_map.keys() if counts.get(f,0) >= 2]

if fusion_candidates:
    sel = st.selectbox("합성할 물고기 선택", fusion_candidates, key="fusion_select")
    
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
            st.rerun()
        else:
            st.warning("수량 부족")
else:
    st.info("합성 가능한 물고기가 없습니다.")

# ================= 📚 도감 (토글) =================
# (로직 생략 - 변화 없음)
st.divider()
open_fishbook = st.checkbox("📚 물고기 도감 열기", value=st.session_state.fishbook_open, key="fishbook_open_cb")
st.session_state.fishbook_open = open_fishbook

if st.session_state.fishbook_open:
    st.subheader(f"📚 물고기 도감 ({len(st.session_state.fishbook)}/{len(ALL_COLLECTIBLES)})")

    sorted_fish_list = sorted(fish_list, key=lambda f: fish_prob[f], reverse=True)

    st.markdown("##### 🐟 일반/희귀 물고기")
    cols = st.columns(5)
    for i, fish in enumerate(sorted_fish_list):
        with cols[i % 5]:
            status = "✔ 발견" if fish in st.session_state.fishbook else "✖ 미발견"
            st.write(f"**{fish}** ({status}, P:{fish_prob[fish]})")

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
st.write(f"💰 최종 코인: **{int(st.session_state.coin)}**")
st.write(f"🧵 최종 떡밥: **{st.session_state.bait}**")
