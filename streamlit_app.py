import streamlit as st
import random
from collections import Counter

# ================= 0. 페이지 설정 및 CSS 스타일링 =================
st.set_page_config(
    page_title="바다의 전설: 낚시 마스터!",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a game-like dark theme and visual flair
st.markdown("""
<style>
/* Streamlit main content wide */
.stApp {
    background-color: #0d1117; /* Dark background color (GitHub Dark theme) */
    color: white;
}
/* Main Title Style */
h1 {
    color: #00bcd4; /* Light Blue/Cyan for the title */
    text-align: center;
    border-bottom: 3px solid #00bcd4;
    padding-bottom: 10px;
    margin-bottom: 20px;
}
/* Subheaders Style */
h2, h3, h4, h5, h6 {
    color: #4CAF50; /* Green for section headers */
}
/* Divider style */
hr {
    border-top: 1px solid #28a745; /* Greenish divider */
}
/* Section Container for visual grouping */
.game-section {
    border: 1px solid #30363d; /* Darker grey border */
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    background-color: #161b22; /* Slightly lighter dark background for contrast */
}
/* Button style (using Streamlit's native buttons, but good for context) */
.stButton>button {
    width: 100%;
    margin-top: 5px;
    border-radius: 5px;
}
/* Colored text for stats */
.stat-value {
    font-size: 1.2em;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


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

# 합성 물고기 가격 정의
for base, fused in fusion_map.items():
    price_map[fused] = int(price_map.get(base, 0) * 5)

# 특수 아이템 가격 정의
price_map["오래된 지도 조각"] = 5000
price_map["완성된 오래된 지도"] = 50000
price_map["떡밥"] = 50 

# 🎣 물가 상승 상수 정의
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

# 낚싯대 강화 비용/확률
ROD_UPGRADE_COSTS = {
    1: {"coin": 2000, "success_rate": 0.8},
    2: {"coin": 4000, "success_rate": 0.6},
    3: {"coin": 8000, "success_rate": 0.4},
}

# 수집 항목 및 판매 제외 항목
SPECIAL_ITEMS = ["오래된 지도 조각", "완성된 오래된 지도"]
FUSED_FISH = list(fusion_map.values())
ALL_COLLECTIBLES = set(fish_list) | set(SPECIAL_ITEMS) | set(FUSED_FISH)
EXCLUDED_FROM_QUICK_SELL = SPECIAL_ITEMS + FUSED_FISH 

# 희귀 낚시터 입장 비용
RARE_LOCATION_COSTS = {
    "coin": 1500,
    "fish": {"대멸치": 10, "대붕어": 10, "대복어": 10, "대방어": 10, "대날치": 10} 
}
MAP_PIECES_NEEDED = 5 # 지도 조각 합성 개수


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
    
initialize_session_state()

# ================= 3. 함수 정의 =================
def check_and_grant_fishbook_reward():
    """도감 완성 여부를 확인하고 보상을 지급합니다. (전설의 해역 잠금 해제)"""
    
    if st.session_state.fishbook_complete:
        return

    # 모든 물고기/아이템을 다 잡았는지 확인
    if ALL_COLLECTIBLES.issubset(st.session_state.fishbook):
        
        st.session_state.fishbook_complete = True
        st.session_state.legendary_unlocked = True 
        
        st.toast("🎉 도감 완성 보상 획득!", icon='🏆')
        st.balloons()
        st.success("✨ **전설의 낚시꾼** 등극! 새로운 낚시터 **[전설의 해역]** 이 열렸습니다!")


def catch_fish(fish):
    """물고기를 인벤토리에 추가하고 도감을 업데이트합니다."""
    st.session_state.inventory.append(fish)
    st.session_state.fishbook.add(fish)
    check_and_grant_fishbook_reward()

def check_for_map_completion():
    """인벤토리에 완성된 지도가 있으면 잃어버린 섬을 해금하고 지도를 소모합니다."""
    full_map = "완성된 오래된 지도"
    if st.session_state.lost_island_unlocked or full_map not in st.session_state.inventory:
        return
    
    st.session_state.lost_island_unlocked = True
    
    # 완성된 지도 소모
    st.session_state.inventory.remove(full_map) 

    st.toast("🏝️ 잃어버린 섬 해금! 완성된 지도가 소모되었습니다.", icon='🗺️')


def update_bait_price():
    """총 낚시 마릿수에 따라 떡밥 가격을 지속적으로 인상하고, 최대치(1500)로 제한합니다."""
    
    current_count = st.session_state.total_fish_caught
    
    # 물가 상승액 계산
    potential_increase = (current_count // CATCH_THRESHOLD_FOR_STEP) * BAIT_INCREASE_STEP
    new_increase = min(potential_increase, MAX_BAIT_INCREASE)
    current_increase = shop_items["떡밥"]["price_increase"] 

    if new_increase > current_increase:
        st.toast(f"💰 물가 상승! 떡밥 가격 +{new_increase - current_increase} 코인", icon='📈')

    shop_items["떡밥"]["price"] = BAIT_BASE_PRICE + new_increase 
    shop_items["떡밥"]["price_increase"] = new_increase 


def random_event(event_rate, location):
    """랜덤 이벤트를 발생시키고 결과를 요약 딕셔너리로 반환합니다."""
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
                # 특수 아이템 제외하고 손실 가능한 목록 생성
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
            bonus = random.randint(300, 700)
            st.session_state.coin = int(st.session_state.coin + bonus) 
            summary['special_bonus'] += bonus
        
        elif event == 5 and location == "잃어버린 섬": # 잃어버린 섬 보너스 코인
            bonus = random.randint(1000, 2000)
            st.session_state.coin = int(st.session_state.coin + bonus) 
            summary['special_bonus'] += bonus
            
        else:
            summary['no_effect'] += 1
    
    return summary


def get_fishing_weights():
    """현재 위치와 낚싯대 레벨에 따라 낚시 가중치를 계산합니다."""
    weights = fish_weights.copy()
    rod_bonus_multiplier = 1 + (st.session_state.rod_level * 0.2)

    # 1. 위치별 가중치 조정 
    if st.session_state.location == "바다":
        for i, f in enumerate(fish_list):
            if f in ["고등어", "전갱이", "꽁치", "우럭", "삼치", "참치", "광어", "도미", "농어", "갈치", "병어", "청새치", "황새치", "랍스터", "킹크랩"]:
                weights[i] *= 1.5 
            else:
                weights[i] *= 0.5 
    elif st.session_state.location == "희귀 낚시터":
        for i, f in enumerate(fish_list):
            if fish_prob.get(f, 1) <= 10 or f in ["참치", "연어", "광어"]: # 희귀 물고기
                weights[i] *= 4 
            if f in fusion_map: # 합성 재료 물고기
                weights[i] *= 2
    elif st.session_state.location == "전설의 해역":
        for i, f in enumerate(fish_list):
            if fish_prob.get(f, 1) <= 10 or f in ["청새치", "황새치", "랍스터", "킹크랩", "개복치"]: # 초희귀 물고기
                weights[i] *= 8
            if f in fusion_map:
                weights[i] *= 3
    elif st.session_state.location == "잃어버린 섬":
        for i, f in enumerate(fish_list):
            if f in ["킹크랩", "개복치", "메가참치", "번개상어", "심연참돔"]: # 심해 전설 물고기
                weights[i] *= 25 
            else:
                weights[i] /= 10 
            if f in fusion_map:
                weights[i] *= 0 # 잃어버린 섬에서는 합성 재료 물고기 나오지 않음
            
    # 2. 낚싯대 보너스 조정 (희귀 물고기만)
    for i, f in enumerate(fish_list):
        if fish_prob.get(f, 1) <= 10: 
            weights[i] *= rod_bonus_multiplier
            
    return weights


# ================= 4. UI 시작 =================
st.title("🎣 바다의 왕이 되기 위해")
st.subheader("심해 속으로, 섬을 다 찾기 위해서!")
st.write(": 여러분의 자유로운 섬 탐방! 히튼 퀘스트를 달성하여 섬을 찾아보자!") 

# --- 상단 통계 컨테이너 ---
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.markdown("### 📊 현재 상태")
stats_col1, stats_col2, stats_col3, stats_col4 = st.columns([1.5, 1.5, 1.5, 4])

with stats_col1:
    st.markdown(f"**💰 코인:** <span class='stat-value' style='color: #ffc107;'>{int(st.session_state.coin):,}</span>", unsafe_allow_html=True)
with stats_col2:
    st.markdown(f"**🧵 떡밥:** <span class='stat-value' style='color: #fd7e14;'>{st.session_state.bait}개</span>", unsafe_allow_html=True)
with stats_col3:
    st.markdown(f"**✨ 낚싯대:** <span class='stat-value' style='color: #17a2b8;'>Lv.{st.session_state.rod_level}</span>", unsafe_allow_html=True)

st.caption(f"🐟 **총 낚시 마릿수:** {st.session_state.total_fish_caught:,}마리 | 도감 상태: {'🏆 완성' if st.session_state.fishbook_complete else '미완성'} ({len(st.session_state.fishbook)}/{len(ALL_COLLECTIBLES)}) | 해금: {'🧭 잃어버린 섬' if st.session_state.lost_island_unlocked else '일반 해역'}")

if st.session_state.fishbook_complete:
    st.success("🏆 **전설의 낚시꾼** 등극! [전설의 해역]이 열렸습니다.", icon='🌟')
if st.session_state.lost_island_unlocked:
    st.info("🧭 **잃어버린 섬** 해금 완료!", icon='🔱')

st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# ================= 낚시터 선택 =================
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.markdown("### 📍 낚시터 변경")

current_location = st.session_state.location

LOCATIONS = ["강가", "바다", "희귀 낚시터"]
if st.session_state.legendary_unlocked:
    LOCATIONS.append("전설의 해역")
if st.session_state.lost_island_unlocked:
    LOCATIONS.append("잃어버린 섬")

current_location_index = LOCATIONS.index(current_location) if current_location in LOCATIONS else 0

location_col1, location_col2 = st.columns([3, 1])

with location_col1:
    temp_location = st.selectbox(
        "현재 낚시터 선택",
        LOCATIONS,
        index=current_location_index,
        key="location_selector",
        label_visibility="collapsed"
    )

st.markdown(f"**➡️ 현재 위치:** **{st.session_state.location}**", unsafe_allow_html=True)

# 낚시터 변경 로직
if temp_location != current_location:
    if temp_location == "희귀 낚시터":
        
        required_coin = RARE_LOCATION_COSTS["coin"]
        required_fish = RARE_LOCATION_COSTS["fish"]
        current_inventory_counts = Counter(st.session_state.inventory)
        
        has_coin = st.session_state.coin >= required_coin
        has_fish = all(current_inventory_counts.get(name, 0) >= qty for name, qty in required_fish.items())

        st.markdown("##### 💎 희귀 낚시터 입장 조건")
        st.write(f"💰 코인: **{required_coin:,}** (현재: {int(st.session_state.coin):,}) {'✔' if has_coin else '✖'}")

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
            btn_col1, btn_col2 = st.columns(2)
            
            if can_enter_by_coin:
                with btn_col1:
                    if st.button(f"💰 코인 소모 입장 ({required_coin:,} 코인)", key="enter_rare_coin"):
                        st.session_state.coin = int(st.session_state.coin - required_coin)
                        st.session_state.location = temp_location
                        st.success(f"🔥 희귀 낚시터 입장! (-{required_coin:,} 코인)")
                        st.rerun() 
            
            if can_enter_by_fish:
                with btn_col2:
                    fish_cost_str = f"({' + '.join([f'{name} {qty}마리' for name, qty in required_fish.items()])})"
                    if st.button(f"🐟 물고기 소모 입장", help=fish_cost_str, key="enter_rare_fish"):
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

st.markdown('</div>', unsafe_allow_html=True)
st.divider()

col1, col2, col3 = st.columns(3)

# ================= 🎣 낚시하기 =================
with col1:
    st.markdown('<div class="game-section">', unsafe_allow_html=True)
    st.subheader("🎣 낚시 액션")

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
        prefix, event_rate, success_msg_prefix = "🛶 ", 0.15, ""
    
    st.markdown(f"**현재 해역:** **{current_location}**")
    st.markdown("---")

    # 1번 낚시 (떡밥 1 소모)
    button_text_1 = f"1️⃣ 1회 낚시 (떡밥 1 소모)"
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
    button_text_2 = f"2️⃣ 2회 낚시 (떡밥 2 소모)"
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
    button_text_3 = f"🎣 **물고기 전체 낚기!** (떡밥 {bait_count}개 소모)" 
        
    if st.button(button_text_3, key="fish_all", disabled=bait_count < 1, type="primary"):
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
                summary_messages.append(f"💰 보너스 코인: **+{total_event_summary['coin']:,}**")
                
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
                summary_messages.append(f"💎 특수 보너스 코인: **+{total_event_summary['special_bonus']:,}**")

            # 요약 메시지 출력
            if events_triggered > 0:
                st.info(f"🎲 랜덤 이벤트 **{events_triggered}회** 발동 결과:\n\n* " + "\n* ".join(summary_messages))
            else:
                st.info("😴 조용하고 평화로운 낚시였습니다. (이벤트 발생 없음)")

            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ================= 🎒 인벤토리 =================
with col2:
    st.markdown('<div class="game-section">', unsafe_allow_html=True)
    st.subheader("🎒 인벤토리")
    
    counts = Counter(st.session_state.inventory) # 인벤토리 카운터 미리 계산

    with st.expander("인벤토리 상세 보기", expanded=st.session_state.inventory_open):
        st.session_state.inventory_open = True 
        
        display_inventory = st.session_state.inventory.copy()

        if display_inventory:
            for item, cnt in counts.items():
                sell_note = " (⚠️ 중요 아이템)" if item in EXCLUDED_FROM_QUICK_SELL else ""
                st.write(f"**{item}** x {cnt} (판매가: **{price_map.get(item,'N/A'):,}** 코인){sell_note}")
        else:
            st.info("인벤토리가 비어 있습니다. 🎣 낚시하세요!")
    
    st.markdown("---")
    st.subheader("📚 물고기 도감")
    with st.expander(f"도감 상태 보기 ({len(st.session_state.fishbook)}/{len(ALL_COLLECTIBLES)})", expanded=st.session_state.fishbook_open):
        st.session_state.fishbook_open = True

        st.markdown(f"**전체 {len(ALL_COLLECTIBLES)}종** 중 **{len(st.session_state.fishbook)}종** 발견")
        
        sorted_fish_list = sorted(fish_list, key=lambda f: fish_prob[f], reverse=True)

        st.markdown("##### 🐟 물고기 목록")
        cols_fish = st.columns(3)
        for i, fish in enumerate(sorted_fish_list):
            with cols_fish[i % 3]:
                status = "✅" if fish in st.session_state.fishbook else "❌"
                st.write(f"{status} {fish} (P:{fish_prob[fish]})")

        st.markdown("##### 💎 특수/합성 아이템")
        cols_special = st.columns(3)
        all_special = SPECIAL_ITEMS + FUSED_FISH
        for i, item in enumerate(all_special):
            with cols_special[i % 3]:
                status = "✅" if item in st.session_state.fishbook else "❌"
                st.write(f"{status} {item}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================= 🏪 상점 / 강화 =================
with col3:
    st.markdown('<div class="game-section">', unsafe_allow_html=True)
    st.subheader("🏪 상점 / 강화")
    open_shop = st.checkbox("상점 기능 열기", value=st.session_state.shop_open, key="shop_open_cb")
    st.session_state.shop_open = open_shop

    if st.session_state.shop_open:
        
        # --- 낚싯대 강화 ---
        st.markdown("### 🛠️ 낚싯대 강화")

        current_level = st.session_state.rod_level
        next_level = current_level + 1

        if next_level in ROD_UPGRADE_COSTS:
            cost = ROD_UPGRADE_COSTS[next_level]

            st.write(f"**현재 레벨:** Lv.{current_level}")
            st.write(f"**다음 레벨:** Lv.{next_level} (성공률: {cost['success_rate']*100}%)")
            st.write(f"**필요 코인:** **{cost['coin']:,}** (현재: {int(st.session_state.coin):,})")

            can_upgrade = st.session_state.coin >= cost['coin']
            if st.button(f"✨ Lv.{next_level} 강화 시도", disabled=not can_upgrade, key=f"upgrade_{next_level}", type="primary"):
                st.session_state.coin = int(st.session_state.coin - cost['coin'])
                if random.random() < cost['success_rate']:
                    st.session_state.rod_level = next_level
                    st.success(f"🎉 강화 성공! Lv.{next_level}")
                else:
                    st.error("💥 강화 실패! 코인만 소모되었습니다.")
                st.rerun()
        else:
            st.info(f"최고 레벨 Lv.{current_level}입니다! 더 이상 강화할 수 없습니다.")

        st.markdown("---")

        # --- 아이템 구매 (떡밥) ---
        st.markdown("### 🛒 떡밥 구매")
        
        bait_item = shop_items["떡밥"]
        bait_price = bait_item["price"]
        increase = bait_item["price_increase"]

        st.write(f"**🧵 떡밥:** **{bait_price:,} 코인/개** (기본 {BAIT_BASE_PRICE} + 물가 상승 {increase} 코인)")
        st.caption(f"최대 가격은 {BAIT_BASE_PRICE + MAX_BAIT_INCREASE:,} 코인입니다.")

        purchase_qty = st.number_input("구매할 떡밥 개수", min_value=1, value=1, step=1, key="bait_qty")
        total_cost = purchase_qty * bait_price
        
        st.write(f"**총 비용:** **{total_cost:,}** 코인")

        can_purchase = st.session_state.coin >= total_cost

        if st.button(f"✅ 떡밥 {purchase_qty}개 구매", key="buy_bait_multi", disabled=not can_purchase):
            if can_purchase:
                st.session_state.coin = int(st.session_state.coin - total_cost)
                st.session_state.bait += purchase_qty
                st.success(f"떡밥 {purchase_qty}개 구매 완료! (-{total_cost:,} 코인)")
                st.rerun()
            else:
                st.error("❗ 코인 부족!")
        
        st.markdown("---")
        
        # --- 판매 ---
        st.markdown("### 💰 물고기 판매")
        
        if st.session_state.inventory:
            
            # 1. 일반 물고기 판매 로직 (특수/합성 제외)
            total_sell_coin_general = 0
            sellable_items_general = []
            
            for item, qty in counts.items():
                if item not in EXCLUDED_FROM_QUICK_SELL:
                    price = price_map.get(item, 0)
                    total_sell_coin_general += price * qty
                    sellable_items_general.append((item, qty))

            st.markdown("##### 🐟 일반 물고기 일괄 판매")
            if total_sell_coin_general > 0:
                st.write(f"**판매 예상 수입:** **{total_sell_coin_general:,}** 코인")
                
                if st.button("💰 일반 물고기 전체 판매", key="sell_general_btn"):
                    
                    total_items_sold = 0
                    for item, qty in sellable_items_general:
                        total_items_sold += qty
                        for _ in range(qty):
                            st.session_state.inventory.remove(item)
                            
                    st.session_state.coin = int(st.session_state.coin + total_sell_coin_general)
                    st.success(f"총 {total_items_sold}마리 판매 완료! +{total_sell_coin_general:,} 코인")
                    st.rerun()
            else:
                st.info("현재 일반 물고기가 없습니다.")
                    
            st.markdown("---")
            
            # 2. 특수/합성 아이템 판매 로직
            total_sell_coin_special = 0
            sellable_items_special = []
            
            for item, qty in counts.items():
                if item in EXCLUDED_FROM_QUICK_SELL:
                    price = price_map.get(item, 0)
                    total_sell_coin_special += price * qty
                    sellable_items_special.append((item, qty))

            st.markdown("##### 💎 특수/합성 아이템 일괄 판매")
            st.write(f"**판매 예상 수입:** **{total_sell_coin_special:,}** 코인")
            if total_sell_coin_special > 0:
                st.caption("⚠️ 지도 조각, 합성 물고기 등 고가치 아이템이 모두 판매됩니다.")
            else:
                st.caption("현재 특수/합성 아이템이 없습니다.")
                        
            if st.button("💎 특수 아이템 전체 판매", key="sell_special_btn", disabled=total_sell_coin_special == 0, type="secondary"):
                
                total_items_sold = 0
                for item, qty in sellable_items_special:
                    total_items_sold += qty
                    for _ in range(qty):
                        st.session_state.inventory.remove(item)
                        
                st.session_state.coin = int(st.session_state.coin + total_sell_coin_special)
                st.success(f"총 {total_items_sold}개 판매 완료! +{total_sell_coin_special:,} 코인")
                st.rerun()

            st.markdown("---")
            
            # 3. 수동 판매 (선택)
            st.markdown("##### 🖐️ 수동 판매 (선택)")

            selected = st.multiselect(
                "판매할 아이템 선택 (수동)",
                st.session_state.inventory,
                format_func=lambda x: f"{x} ({price_map.get(x,'N/A'):,} 코인)",
                key="sell_select"
            )

            if st.button("선택된 아이템 판매", key="sell_btn"):
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
                    st.success(f"{items_sold_count}개 판매 완료! +{total:,} 코인")
                    st.rerun()
        else:
            st.warning("판매할 아이템이 없습니다.")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ================= 🔧 떡밥 제작 & 합성 섹션 시작 =================
st.divider()
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.subheader("🧵 떡밥 제작 및 아이템 합성")
st.caption("물고기 2마리 = 떡밥 1개 (합성 물고기, 지도 조각 제외)")
st.markdown("---")

counts = Counter(st.session_state.inventory)
excluded_items_craft = list(fusion_map.values()) + SPECIAL_ITEMS
craft_candidates = [f for f, count in counts.items() if count >= 2 and f not in excluded_items_craft]

# 🌟 1. 떡밥 전체 제작 로직
st.markdown("### ⚡ 떡밥 전체 제작 (최적 재료 사용)")

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
    
    st.write(f"✅ **최적의 재료:** **{best_craft_fish}** (판매가: {min_price} 코인)")
    st.write(f"**최대 제작 떡밥:** **{max_craftable}개** (재료: {best_craft_fish} {max_craftable * 2}개 소모)")

    if st.button(f"🧵 {best_craft_fish} 전체 사용하여 떡밥 {max_craftable}개 제작", key="craft_all_btn", type="primary"):
        total_fish_needed = max_craftable * 2
        
        for _ in range(total_fish_needed):
            st.session_state.inventory.remove(best_craft_fish)
            
        st.session_state.bait += max_craftable
        st.success(f"**{best_craft_fish}** {total_fish_needed}개 분쇄 완료! 🧵 **떡밥 {max_craftable}개** 획득!")
        st.rerun()
else:
    st.info("현재 떡밥 전체 제작에 사용할 수 있는 물고기가 없습니다. (동일 물고기 2마리 필요)")

st.markdown("---")

# 🌟 2. 수동 제작
st.markdown("### 🛠️ 수동 제작")

if craft_candidates:
    craft_col1, craft_col2 = st.columns([2, 1])

    with craft_col1:
        selected_fish_to_grind = st.selectbox("분쇄할 물고기 선택 (2마리 소모)", craft_candidates, key="craft_select")
        max_craftable_single = counts.get(selected_fish_to_grind, 0) // 2
        st.caption(f"최대 제작 가능: {max_craftable_single}개")

    with craft_col2:
        craft_qty = st.number_input("제작할 떡밥 개수", min_value=1, max_value=max_craftable_single, value=min(1, max_craftable_single), step=1, key="craft_qty")

    if st.button(f"'{selected_fish_to_grind}' {craft_qty * 2}개 갈아서 떡밥 {craft_qty}개 제작", key="craft_btn", disabled=max_craftable_single==0):
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

# ================= 🧪 물고기 합성 (Fusion) - 희귀 낚시터 재료 획득을 위해 필수! =================
st.markdown("---")
st.markdown("### 🧪 물고기 합성 (10+1)")
st.caption("특정 물고기 10마리를 합성하여 **대(大) 사이즈 물고기 1마리**를 제작합니다.")

FUSION_INGREDIENT_QTY = 10 # 합성 재료 개수

# 합성 가능한 아이템 목록 (인벤토리에 재료가 10개 이상 있는 경우)
fusion_candidates = []
for base_fish, fused_fish in fusion_map.items():
    if counts.get(base_fish, 0) >= FUSION_INGREDIENT_QTY:
        fusion_candidates.append((base_fish, fused_fish))

if fusion_candidates:
    
    # 튜플 리스트를 (베이스 물고기 이름)만 있는 리스트로 변경
    base_fish_names = [item[0] for item in fusion_candidates]
    selected_base_fish = st.selectbox(
        "합성할 물고기 선택", 
        base_fish_names, 
        key="fusion_select"
    )
    
    # 선택된 물고기의 합성 결과물 찾기
    selected_fused_fish = fusion_map.get(selected_base_fish, None)
    
    current_count = counts.get(selected_base_fish, 0)
    max_fusion_count = current_count // FUSION_INGREDIENT_QTY
    
    st.write(f"**재료:** **{selected_base_fish}** {FUSION_INGREDIENT_QTY}개")
    st.write(f"**결과:** **{selected_fused_fish}** 1개 (판매가: **{price_map.get(selected_fused_fish,'N/A'):,}** 코인)")
    st.caption(f"현재 최대 **{max_fusion_count}회** 합성 가능")

    fusion_qty = st.number_input(
        "합성할 횟수", 
        min_value=1, 
        max_value=max_fusion_count, 
        value=min(1, max_fusion_count), 
        step=1, 
        key="fusion_qty"
    )

    total_fish_needed = fusion_qty * FUSION_INGREDIENT_QTY

    if st.button(f"🧪 {selected_base_fish} {total_fish_needed}개로 {selected_fused_fish} {fusion_qty}개 합성", key="fusion_btn", disabled=max_fusion_count == 0):
        
        if counts.get(selected_base_fish, 0) >= total_fish_needed:
            # 재료 소모
            for _ in range(total_fish_needed):
                st.session_state.inventory.remove(selected_base_fish)
                
            # 결과물 획득
            for _ in range(fusion_qty):
                catch_fish(selected_fused_fish)
            
            st.success(f"**{selected_base_fish}** {total_fish_needed}개 소모하여 🧪 **{selected_fused_fish} {fusion_qty}개** 합성 성공!")
            st.rerun()
        else:
            st.warning("물고기 수가 부족합니다.")
else:
    st.info("현재 합성 가능한 물고기가 없습니다. (동일 물고기 10마리 이상 필요)")


# ================= ⚡ 지도 조각 합성 =================
st.markdown("---")
st.markdown("### 🗺️ 지도 조각 합성")

MAP_PIECE_NAME = "오래된 지도 조각"
FULL_MAP_NAME = "완성된 오래된 지도"

current_map_pieces = counts.get(MAP_PIECE_NAME, 0)
can_craft_map = current_map_pieces >= MAP_PIECES_NEEDED

st.write(f"**필요 조각:** **{MAP_PIECES_NEEDED}개** (현재: {current_map_pieces}개)")
st.caption(f"성공 시, 🏝️ **잃어버린 섬**을 해금할 수 있는 **{FULL_MAP_NAME}** 1개를 획득합니다.")

if st.button("🗺️ 지도 조각 합성", key="craft_map_btn", disabled=not can_craft_map, type="secondary"):
    
    if can_craft_map:
        # 1. 재료 소모
        for _ in range(MAP_PIECES_NEEDED):
            st.session_state.inventory.remove(MAP_PIECE_NAME)
        
        # 2. 완성품 획득
        st.session_state.inventory.append(FULL_MAP_NAME)
        st.session_state.fishbook.add(FULL_MAP_NAME)
        
        st.success(f"🎉 **{FULL_MAP_NAME}** 획득! ({MAP_PIECES_NEEDED}개 소모)")
        
        # 3. 잃어버린 섬 해금 로직 즉시 실행 (완성된 지도를 소모하며 해금)
        check_for_map_completion() 
        
        st.rerun()
    else:
        st.warning(f"❗ **{MAP_PIECE_NAME}**이 {MAP_PIECES_NEEDED}개 필요합니다.")
        
st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# ================= 🔄 데이터 초기화 (선택적) =================
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.subheader("⚠️ 데이터 초기화 (Reset)")
st.caption("게임을 처음부터 다시 시작합니다.")
if st.button("💀 게임 데이터 초기화", key="reset_game"):
    keys_to_delete = list(st.session_state.keys())
    for key in keys_to_delete:
        del st.session_state[key]
    st.experimental_rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br><p style='text-align:center;color:#6c757d;'>바다의 전설: 낚시 마스터 - Streamlit Game Example</p>", unsafe_allow_html=True)
