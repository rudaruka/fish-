import streamlit as st
import random
from collections import Counter
import math

# ================= 0. 페이지 설정 및 CSS 스타일링 (밝은 테마 적용) =================
st.set_page_config(
    page_title="낚시터를 낚아보아요",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a clean, light-mode theme
st.markdown("""
<style>
/* Streamlit main content wide - BRIGHT THEME */
.stApp {
    background-color: #f8f9fa; /* Very Light Grey/Off-White */
    color: #212529; /* Dark text color */
}
/* Main Title Style */
h1 {
    color: #007bff; /* Bright Blue for the title */
    text-align: center;
    border-bottom: 3px solid #007bff;
    padding-bottom: 10px;
    margin-bottom: 20px;
}
/* Subheaders Style */
h2, h3, h4, h5, h6 {
    color: #28a745; /* Green for section headers */
}
/* Divider style */
hr {
    border-top: 1px solid #ced4da; /* Light grey divider */
}
/* Section Container for visual grouping */
.game-section {
    border: 1px solid #adb5bd; /* Medium grey border */
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    background-color: #ffffff; /* White background for sections */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
/* Colored text for stats */
.stat-value {
    font-size: 1.2em;
    font-weight: bold;
}

/* 🚨 도감 Grid 레이아웃 적용 (정렬 개선) */
.fishbook-grid {
    display: grid;
    /* 5개의 동일한 크기 열을 만듭니다. (글자 수에 관계없이 정렬) */
    grid-template-columns: repeat(5, 1fr); 
    gap: 5px 0px; /* 줄 간격 5px, 열 간격 0px */
}
/* Grid 항목 스타일 */
.fishbook-item {
    font-size: 0.9em;
    padding: 3px 5px;
    border-radius: 3px;
    white-space: nowrap; /* 항목이 줄 바꿈 되는 것을 방지 */
}
/* 획득한 아이템 스타일 */
.collected {
    font-weight: bold;
    color: #007bff; /* 파란색으로 변경 */
}
/* 미획득 아이템 스타일 */
.uncollected {
    color: #757575; /* 회색 유지 */
}
</style>
""", unsafe_allow_html=True)


# ================= 2. 물고기 & 가격 정의 =================

# 🚩 물고기 확률 재정의 (일반 물고기 내부 확률 차등 적용 및 전체 비율 유지)
fish_prob = {
    # 🐟 일반 물고기 - 아주 흔함 (W=15): 5마리
    "멸치": 15, "복어": 15, "누치": 15, "정어리": 15, "피라냐": 15, 

    # 🐟 일반 물고기 - 흔함 (W=10): 15마리
    "빙어": 10, "북어": 10, "꽁치": 10, "은어": 10, "노래미": 10, "쥐치": 10, 
    "메기": 10, "송어": 10, "붕어": 10, "잉어": 10, "향어": 10,
    "가물치": 10, "쏘가리": 10, "붕장어": 10, "갯장어": 10,

    # 🦈 일반 물고기 - 희귀 바다 (W=6): 13마리
    "고등어": 6, "전갱이": 6, "우럭": 6, "삼치": 6,
    "참치": 6, "연어": 6, "광어": 6, "도미": 6, "농어": 6, "아귀": 6, 
    "볼락": 6, "갈치": 6, "병어": 6,

    # 🦀 일반 물고기 - 매우 희귀/특수 (W=2): 7마리
    "청새치": 2, "황새치": 2, "랍스터": 2, "해마": 2,
    "방어": 2, "날치": 2, "열기": 2,
    
    # 🔱 심해/전설 & 희귀 중 최고가 (W=6): 특수 아이템 7% 목표 그룹 (변화 없음)
    "메가참치": 6, "번개상어": 6, "심연참돔": 6, 
    "킹크랩": 6, "개복치": 6, 

    # ☣️ 괴수 물고기 (W=8): 10% 목표 그룹 (변화 없음)
    "암흑고래수리" : 8, "화염비늘룡어" : 8, "태풍포식상어" : 8, "얼음유령해마" : 8, "심해철갑괴치" : 8,

    # 😂 코믹 물고기 (W=3): 3% 목표 그룹 (변화 없음)
    "현이 물고기" : 3, "스노 물고기" : 3, "위키 물고기" : 3, "루루 물고기" : 3
}

fish_list = list(fish_prob.keys())
fish_weights = list(fish_prob.values())

# 🎣 가격 인하 계수 정의 (물고기 판매 가격 70% 인하)
PRICE_DEFLATION_FACTOR = 0.3 

# 가격 계산 로직: 희귀도에 따라 가격 차별화 후 인하 계수 적용
# 가중치가 낮을수록 (희귀할수록) 가격이 높아지도록 계산
price_map = {
    # 가중치 15(흔함)부터 2(매우 희귀)까지의 분포를 활용하여 가격 책정
    fish: int(((20 - prob) * 200) + 1000) * PRICE_DEFLATION_FACTOR 
    for fish, prob in fish_prob.items()
}
# 가격을 코인 단위로 사용하기 위해 다시 정수로 변환 (소수점 버림)
price_map = {fish: int(price) for fish, price in price_map.items()}


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

# 🎣 물가 상승 상수 정의
MAX_BAIT_INCREASE = 1000
BAIT_INCREASE_STEP = 10 
CATCH_THRESHOLD_FOR_STEP = 40 
BAIT_BASE_PRICE = 70 # ⬅️ 떡밥 기본 가격 70 코인 적용
BAIT_CRAFT_FISH_NEEDED = 2 # 떡밥 제작에 필요한 물고기 개수

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

# 수집 항목 및 판매 제외 항목 분류
SPECIAL_ITEMS = ["오래된 지도 조각", "완성된 오래된 지도"]
FUSED_FISH = list(fusion_map.values())
MONSTER_FISH = ["암흑고래수리", "화염비늘룡어", "태풍포식상어", "얼음유령해마", "심해철갑괴치"]
COMIC_FISH = ["현이 물고기", "스노 물고기", "위키 물고기", "루루 물고기"]

# 일반 물고기 정의 (괴수, 코믹, 특수, 합성 물고기를 제외한 나머지)
EXCLUDED_TYPES = set(MONSTER_FISH) | set(COMIC_FISH) | set(SPECIAL_ITEMS) | set(FUSED_FISH)
NORMAL_FISH = [item for item in fish_list if item not in EXCLUDED_TYPES]

ALL_COLLECTIBLES = set(fish_list) | set(SPECIAL_ITEMS) | set(FUSED_FISH)
EXCLUDED_FROM_QUICK_SELL = SPECIAL_ITEMS + FUSED_FISH 

# 희귀 낚시터 입장 비용
RARE_LOCATION_COSTS = {
    "coin": 1500,
    "fish": {"대멸치": 10, "대붕어": 10, "대복어": 10, "대방어": 10, "대날치": 10} 
}
MAP_PIECES_NEEDED = 5 


# ================= 1. 세션 초기화 =================

# 🚨 기본값 딕셔너리
DEFAULT_STATE = {
    "coin": 1000, 
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
    "total_fish_caught": 0, 
}

def initialize_session_state():
    """세션 상태를 초기화하거나, 이미 존재하는 경우 유지합니다."""

    # fishbook은 set으로 특별히 초기화
    if "fishbook" not in st.session_state or not isinstance(st.session_state.fishbook, set):
        st.session_state.fishbook = set()

    for key, default_value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
initialize_session_state()

# ================= 3. 함수 정의 =================

def reset_game_data():
    """
    Streamlit 세션 상태의 모든 키를 삭제하고 
    앱을 완전히 새로고침하여 초기 상태로 돌아가는 강력한 초기화 함수.
    """
    # 전체 키 제거 (Streamlit 내부 에러 방지)
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # 세션 정리 (추가적인 정리 및 확실한 초기화)
    st.session_state.clear()
    
    st.rerun()


def check_and_grant_fishbook_reward():
    """도감 완성 여부를 확인하고 보상을 지급합니다."""
    if st.session_state.fishbook_complete:
        return

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
    if st.session_state.lost_island_unlocked:
        return
    
    if full_map in st.session_state.inventory:
        st.session_state.lost_island_unlocked = True
    
        # 완성된 지도 소모
        st.session_state.inventory.remove(full_map) 

        st.toast("🏝️ 잃어버린 섬 해금! 완성된 지도가 소모되었습니다.", icon='🗺️')


def update_bait_price():
    """총 낚시 마릿수에 따라 떡밥 가격을 지속적으로 인상하고, 최대치로 제한합니다."""
    current_count = st.session_state.total_fish_caught
    
    potential_increase = (current_count // CATCH_THRESHOLD_FOR_STEP) * BAIT_INCREASE_STEP
    new_increase = min(potential_increase, MAX_BAIT_INCREASE)
    current_increase = shop_items["떡밥"]["price_increase"] 

    if new_increase > current_increase:
        # 이 함수가 호출될 때 가격 변동이 감지되면 토스트 메시지 출력
        st.toast(f"💰 물가 상승! 떡밥 가격 +{new_increase - current_increase} 코인", icon='📈')

    # 세션 상태에 저장된 값이 아닌, 전역 shop_items 딕셔너리를 업데이트
    shop_items["떡밥"]["price"] = BAIT_BASE_PRICE + new_increase 
    shop_items["떡밥"]["price_increase"] = new_increase 


def random_event(event_rate, location):
    """랜덤 이벤트를 발생시키고 결과를 요약 딕셔너리로 반환합니다."""
    summary = {'coin': 0, 'bonus_fish': [], 'lost_fish': [], 'map_pieces': 0, 'special_bonus': 0, 'event_message': None}
    
    if random.random() < event_rate: 
        event = random.randint(1, 6) 
        
        if event == 1: # 코인 보너스
            bonus = random.randint(10, 80)
            if location in ["전설의 해역", "잃어버린 섬"]:
                bonus *= 10
            st.session_state.coin = int(st.session_state.coin + bonus) 
            summary['coin'] += bonus
            summary['event_message'] = "💰 보물 상자 발견!"
        
        elif event == 2: # 물고기 보너스
            # 일반 물고기 중에서 가중치 낮은 (희귀한) 물고기 리스트
            rare_fish_list = [f for f, prob in fish_prob.items() if prob <= 6] 
            f2 = random.choice(rare_fish_list) if rare_fish_list else random.choice(fish_list)
            catch_fish(f2)
            summary['bonus_fish'].append(f2)
            summary['event_message'] = "🎣 물고기 무리 포착!"
            
        elif event == 3: # 물고기 손실
            if st.session_state.inventory:
                losable_items = [i for i in st.session_state.inventory if i not in SPECIAL_ITEMS]
                if losable_items:
                    lost = random.choice(losable_items)
                    st.session_state.inventory.remove(lost)
                    summary['lost_fish'].append(lost)
                    summary['event_message'] = "🔥 갈매기에게 물고기 도난!"
                else:
                    summary['event_message'] = "🌊 파도가 너무 거셉니다."
            else:
                summary['event_message'] = "🌊 파도가 너무 거셉니다."
                
        elif event == 4 and location == "희귀 낚시터": # 지도 조각 획득
            item_name = "오래된 지도 조각"
            catch_fish(item_name)
            summary['map_pieces'] += 1
            summary['event_message'] = "🗺️ 물 속에서 오래된 지도 조각 발견!"
            
        elif event == 4 and location == "전설의 해역": # 전설 해역 보너스 코인
            bonus = random.randint(300, 700)
            st.session_state.coin = int(st.session_state.coin + bonus) 
            summary['special_bonus'] += bonus
            summary['event_message'] = "💎 희귀 광물 발견!"
            
        elif event == 5 and location == "잃어버린 섬": # 잃어버린 섬 보너스 코인
            bonus = random.randint(1000, 2000)
            st.session_state.coin = int(st.session_state.coin + bonus) 
            summary['special_bonus'] += bonus
            summary['event_message'] = "🔱 전설의 보물 상자 발견!"
            
        elif event == 6:
            if st.session_state.bait > 0:
                lost_bait = 1
                st.session_state.bait = max(0, st.session_state.bait - lost_bait)
                summary['event_message'] = "💧 떡밥이 파도에 휩쓸려 사라졌습니다. (떡밥 1개 손실)"
            else:
                summary['event_message'] = "😴 조용합니다."
                
        else:
            summary['event_message'] = "🤔 아무 일도 일어나지 않았습니다."
    
    return summary


def get_fishing_weights():
    """현재 위치와 낚싯대 레벨에 따라 낚시 가중치를 계산합니다."""
    weights = fish_weights.copy()
    rod_bonus_multiplier = 1 + (st.session_state.rod_level * 0.5) 

    base_weights = [math.ceil(w) for w in fish_weights] 

    for i, f in enumerate(fish_list):
        weights[i] = base_weights[i]

    # 1. 위치별 가중치 조정
    if st.session_state.location == "강가":
        for i, f in enumerate(fish_list):
            # 강가에 맞지 않는 물고기는 확률을 대폭 낮춤
            if f in ["고등어", "전갱이", "우럭", "삼치", "참치", "연어", "광어", "도미", "농어", "아귀", "볼락", "갈치", "병어", "청새치", "황새치", "랍스터", "킹크랩", "개복치", "해마", "방어", "날치", "열기", "메가참치", "번개상어", "심연참돔"] or f in MONSTER_FISH or f in COMIC_FISH:
                 weights[i] *= 0.05

    elif st.session_state.location == "바다":
        for i, f in enumerate(fish_list):
            # 바다에 맞지 않는 민물고기는 확률을 대폭 낮춤 (W=10 이상 물고기)
            if fish_prob.get(f, 0) >= 10: 
                weights[i] *= 0.05
            # 바다 희귀템은 확률 2배 증가 (W=6 이하 물고기)
            elif fish_prob.get(f, 0) <= 6 and f not in MONSTER_FISH and f not in COMIC_FISH and f not in ["메가참치", "번개상어", "심연참돔"]:
                weights[i] *= 2.0
            
    elif st.session_state.location == "희귀 낚시터":
        for i, f in enumerate(fish_list):
            # 희귀 물고기 (W=6 이하)는 확률 5배 증가
            if fish_prob.get(f, 0) <= 6:
                weights[i] *= 5.0
            # 합성 가능 물고기는 확률 2.5배 증가
            if f in fusion_map.keys(): 
                weights[i] *= 2.5
            # 흔한 물고기는 확률 대폭 감소 (W=10 이상 물고기)
            elif fish_prob.get(f, 0) >= 10:
                weights[i] *= 0.05
            
    elif st.session_state.location == "전설의 해역":
        for i, f in enumerate(fish_list):
            # 전설의 해역에서만 나오는 괴수/코믹은 확률 100배 증가 (W=8, W=3 그룹)
            if f in MONSTER_FISH or f in COMIC_FISH:
                weights[i] *= 100.0 
            # 일반/희귀 물고기는 확률 대폭 감소 (W=6 이상 물고기)
            elif fish_prob.get(f, 0) >= 6 and f not in ["메가참치", "번개상어", "심연참돔"]:
                weights[i] *= 0.01

    elif st.session_state.location == "잃어버린 섬":
        for i, f in enumerate(fish_list):
            # 잃어버린 섬 전용 물고기 (W=6 그룹 중 메가참치, 번개상어, 심연참돔) 확률 1000배 증가
            if f in ["메가참치", "번개상어", "심연참돔"]: 
                weights[i] *= 1000.0 
            # 다른 물고기는 확률 대폭 감소
            elif f not in ["킹크랩", "개복치"]: # 킹크랩/개복치는 W=6 그룹이지만 낚이는 것은 허용
                weights[i] *= 0.0001
            
    # 2. 낚싯대 보너스 조정 (희귀 물고기만)
    for i, f in enumerate(fish_list):
        if fish_prob.get(f, 1) <= 6: # W=6 이하의 희귀 물고기에만 보너스 적용
            weights[i] *= rod_bonus_multiplier
            
    return [max(1, math.ceil(w)) for w in weights] 

def fishing_batch_run():
    """현재 가진 떡밥 전체를 소모하여 낚시를 시도하고 결과를 요약합니다."""
    bait_used = st.session_state.bait
    if bait_used == 0:
        st.error("❗ 떡밥이 부족하여 전체 낚시를 실행할 수 없습니다.")
        return

    st.session_state.bait = 0 
    st.session_state.total_fish_caught += bait_used
    
    caught_results = Counter()
    total_coin_event_bonus = 0
    
    weights = get_fishing_weights()
    location = st.session_state.location
    event_rate = 0.15 if location in ["전설의 해역", "잃어버린 섬", "희귀 낚시터"] else 0.1
    
    for _ in range(bait_used):
        caught_fish = random.choices(fish_list, weights=weights, k=1)[0]
        caught_results[caught_fish] += 1
        st.session_state.inventory.append(caught_fish)
        st.session_state.fishbook.add(caught_fish)

        event_summary = random_event(event_rate, location)
        total_coin_event_bonus += event_summary['coin'] + event_summary['special_bonus']
        
    update_bait_price() # 물가 상승 체크 및 업데이트
    
    st.markdown(f"### 🎉 **[전체 낚시 {bait_used}회] 결과**")
    st.info(f"**📍 낚시터:** {location}")
    st.success(f"**총 {bait_used}마리** 낚시 성공! 낚시한 물고기 {bait_used}마리 인벤토리에 추가.")
    
    if caught_results:
        st.markdown("**획득한 물고기 목록:**")
        
        caught_data = sorted(caught_results.items(), key=lambda item: item[1], reverse=True)
        st.table({
            "물고기": [item[0] for item in caught_data],
            "마리 수": [item[1] for item in caught_data]
        })
        
    if total_coin_event_bonus > 0:
        st.session_state.coin = int(st.session_state.coin + total_coin_event_bonus)
        st.warning(f"💰 이벤트 보너스 코인 획득: **{total_coin_event_bonus:,} 코인**")

    check_and_grant_fishbook_reward()
    
    st.rerun()


# ================= 4. UI 시작 =================
st.title("🎣 바다의 왕이 되기 위해")
st.subheader("심해 속으로, 섬을 다 찾기 위해서!")
st.write("기본 지급되는 떡밥으로, 낚시를 시작해보자!!")

# --- 상단 통계 컨테이너 ---
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.markdown("### 📊 현재 상태")
stats_col1, stats_col2, stats_col3, stats_col4 = st.columns([1.5, 1.5, 1.5, 4])

with stats_col1:
    st.markdown(f"**💰 코인:** <span class='stat-value' style='color: #ffc107;'>{int(st.session_state.coin):,}</span>", unsafe_allow_html=True)
with stats_col2:
    st.markdown(f"**🧵 떡밥:** <span class='stat-value' style='color: #fd7e14;'>{st.session_state.bait}개</span>", unsafe_allow_html=True)
with stats_col3:
    st.markdown(f"**🎣 낚싯대:** <span class='stat-value' style='color: #adb5bd;'>Lv.{st.session_state.rod_level}</span>", unsafe_allow_html=True)
with stats_col4:
    st.markdown(f"**📍 위치:** <span class='stat-value' style='color: #00bcd4;'>{st.session_state.location}</span>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 메인 게임 섹션 ---
st.markdown("---") # st.divider() 대체
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.subheader("🌊 낚시")

# 낚시터 선택 로직
location_options = ["강가", "바다"]
if st.session_state.legendary_unlocked:
    location_options.append("전설의 해역")
if st.session_state.lost_island_unlocked:
    location_options.append("잃어버린 섬")
    
current_location = st.session_state.location
selector_index = location_options.index(current_location) if current_location in location_options else 0

if current_location != "희귀 낚시터":
    st.session_state.location_selector = st.selectbox(
        "낚시할 장소 선택", 
        options=location_options, 
        index=selector_index,
        key="location_select"
    )
    st.session_state.location = st.session_state.location_selector
else:
    st.info(f"현재 **{current_location}**에 있습니다. 희귀 낚시터에서 낚시를 계속하세요.")


# 희귀 낚시터 입장 로직
if current_location != "희귀 낚시터":
    
    st.markdown("---")
    
    st.markdown("### 💎 희귀 낚시터 입장")
    st.caption(f"입장 비용: {RARE_LOCATION_COSTS['coin']:,} 코인 및 특정 합성 물고기 각 10마리")
    
    can_enter_rare = st.session_state.coin >= RARE_LOCATION_COSTS["coin"]
    counts = Counter(st.session_state.inventory)
    
    fish_requirements_met = True
    required_fishes_str = ""
    for fish, required_qty in RARE_LOCATION_COSTS["fish"].items():
        current_qty = counts.get(fish, 0)
        required_fishes_str += f"{fish} ({current_qty}/{required_qty}) / "
        if current_qty < required_qty:
            fish_requirements_met = False
    
    required_fishes_str = required_fishes_str.strip(' / ')
    
    st.caption(f"필요 물고기: {required_fishes_str}")
    
    if st.button("🗺️ 희귀 낚시터 입장", disabled=not can_enter_rare or not fish_requirements_met, key="enter_rare_fishing_spot"):
        
        st.session_state.coin -= RARE_LOCATION_COSTS["coin"]
        
        for fish, qty in RARE_LOCATION_COSTS["fish"].items():
            for _ in range(qty):
                st.session_state.inventory.remove(fish)
            
        st.session_state.location = "희귀 낚시터" 
        st.success("🎉 희귀 낚시터에 입장했습니다! 낚시를 시작하세요.")
        st.rerun()

# 희귀 낚시터에서 탈출 로직
if current_location == "희귀 낚시터":
    if st.button("⬅️ 강가로 돌아가기", key="exit_rare_fishing_spot"):
        st.session_state.location = "강가"
        st.success("강가로 돌아왔습니다.")
        st.rerun()

st.markdown("---")

# 낚시 실행 버튼 배치
fish_col1, fish_col2 = st.columns(2)

# 1. 단일 낚시
with fish_col1:
    if st.session_state.bait > 0:
        if st.button(f"**🎣 낚시하기!** (떡밥 1개 소모)", type="primary", key="do_fishing_single"):
            st.session_state.bait -= 1
            st.session_state.total_fish_caught += 1
            update_bait_price() 

            weights = get_fishing_weights()
            caught_fish = random.choices(fish_list, weights=weights, k=1)[0]
            catch_fish(caught_fish)
            
            event_rate = 0.15 if st.session_state.location in ["희귀 낚시터", "전설의 해역", "잃어버린 섬"] else 0.1
            event_summary = random_event(event_rate, st.session_state.location)
            
            st.success(f"🎊 **{st.session_state.location}**에서 **{caught_fish}**를 낚았습니다! (💰{price_map.get(caught_fish, 'N/A'):,} 코인)")
            
            if event_summary['event_message']:
                st.warning(f"🚨 이벤트 발생: **{event_summary['event_message']}**")
                
            if event_summary['coin'] > 0:
                st.caption(f"+💰 {event_summary['coin']:,} 코인")
            if event_summary['bonus_fish']:
                st.caption(f"보너스 획득: {event_summary['bonus_fish'][0]}")
            if event_summary['lost_fish']:
                st.caption(f"물고기 손실: -{event_summary['lost_fish'][0]}")
            if event_summary['special_bonus'] > 0:
                st.caption(f"+💎 {event_summary['special_bonus']:,} 코인 (특수 보너스)")
                
            st.rerun()
    else:
        st.error("❗ 떡밥이 부족합니다.")

# 2. 전체 낚시
with fish_col2:
    if st.session_state.bait > 0:
        if st.button(f"**🎣 전체 낚시!** (떡밥 {st.session_state.bait}개 소모)", type="secondary", key="do_fishing_batch"):
            fishing_batch_run() 
    else:
        st.error("❗ 전체 낚시 불가.")
    
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. 인벤토리/도감 섹션 ---
st.markdown("---") # st.divider() 대체
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.subheader("📚 인벤토리 & 도감")

inv_col, fishbook_col = st.columns(2)

# --- 인벤토리 ---
with inv_col:
    if st.button("📦 인벤토리 열기/닫기", key="toggle_inventory"):
        st.session_state.inventory_open = not st.session_state.inventory_open
        st.session_state.fishbook_open = False 
        st.rerun()

    if st.session_state.inventory_open:
        counts = Counter(st.session_state.inventory)
        st.markdown("#### 인벤토리 내용")
        if counts:
            
            sorted_items = sorted(counts.items(), key=lambda item: item[1], reverse=True)
            
            inventory_data_sorted = {
                "아이템": [item[0] for item in sorted_items],
                "수량": [item[1] for item in sorted_items],
                "판매가": [f"{price_map.get(item[0], 0):,}" for item in sorted_items]
            }
            st.table(inventory_data_sorted)
        else:
            st.info("인벤토리가 비어 있습니다.")

# --- 도감 (시각적 개선 적용) ---
def render_fishbook_list(title, fish_list_to_render):
    """CSS Grid를 사용하여 정렬된 도감 목록을 렌더링하는 헬퍼 함수"""
    st.markdown(f"**{title}** ({len([f for f in fish_list_to_render if f in st.session_state.fishbook])}/{len(fish_list_to_render)}종)")
    st.markdown('<div class="fishbook-grid">', unsafe_allow_html=True) 
    
    for item in sorted(fish_list_to_render):
        status = "✅" if item in st.session_state.fishbook else "❓"
        css_class = "collected" if status == "✅" else "uncollected"
        display_name = f"{item}"
        if item in MONSTER_FISH:
            display_name += "--" 
        
        st.markdown(f'<div class="fishbook-item"><span class="{css_class}">{status} {display_name}</span></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

with fishbook_col:
    if st.button("📖 도감 열기/닫기", key="toggle_fishbook_final"):
        st.session_state.fishbook_open = not st.session_state.fishbook_open
        st.session_state.inventory_open = False 
        st.rerun()

    if st.session_state.fishbook_open:
        check_and_grant_fishbook_reward()
        
        st.markdown(f"#### 도감 현황 ({len(st.session_state.fishbook)}/{len(ALL_COLLECTIBLES)})")
        
        if st.session_state.fishbook_complete:
            st.success("🏆 도감 완성! 전설의 낚시꾼!")
        
        render_fishbook_list("🐟 일반 물고기", NORMAL_FISH)
        render_fishbook_list("☣️ 괴수 물고기", MONSTER_FISH)
        render_fishbook_list("😂 코믹 물고기", COMIC_FISH)
        render_fishbook_list("🧪 합성 물고기", FUSED_FISH)
        render_fishbook_list("🗺️ 특수 아이템", SPECIAL_ITEMS)
            
st.markdown('</div>', unsafe_allow_html=True)


# --- 7. 상점 섹션 ---
def shop_interface():
    st.markdown("---") # st.divider() 대체
    st.markdown('<div class="game-section">', unsafe_allow_html=True)
    st.subheader("🏪 상점")
    
    # 떡밥 가격을 포함한 상점 정보 갱신 (물가 상승 반영)
    update_bait_price()
    
    if st.button("🛒 상점 열기/닫기", key="toggle_shop"):
        st.session_state.shop_open = not st.session_state.shop_open
        st.rerun() 

    if st.session_state.shop_open:
        
        counts = Counter(st.session_state.inventory)
        
        # --- 낚싯대 강화 ---
        st.markdown("### 💪 낚싯대 강화")
        current_level = st.session_state.rod_level
        
        if current_level < len(ROD_UPGRADE_COSTS):
            next_level = current_level + 1
            upgrade_info = ROD_UPGRADE_COSTS.get(next_level, {})
            cost = upgrade_info.get("coin", 0)
            rate = upgrade_info.get("success_rate", 0)
            
            st.write(f"**현재 레벨:** Lv.{current_level}")
            st.write(f"**다음 레벨:** Lv.{next_level} (성공률: **{rate * 100:.0f}%**)")
            st.write(f"**강화 비용:** **{cost:,} 코인**")
            
            can_upgrade = st.session_state.coin >= cost
            
            # 폼 내부에서 강화 버튼 처리
            with st.form("rod_upgrade_form"):
                
                upgrade_submitted = st.form_submit_button(
                    f"⬆️ Lv.{next_level} 강화 시도", 
                    disabled=not can_upgrade,
                    type="primary"
                )
            
                if upgrade_submitted:
                    if can_upgrade:
                        st.session_state.coin -= cost
                        
                        if random.random() < rate:
                            st.session_state.rod_level += 1
                            st.success(f"🎉 **강화 성공!** 현재 레벨: Lv.{st.session_state.rod_level}")
                            st.balloons()
                        else:
                            st.error(f"❌ 강화 실패! 코인 {cost:,} 소모. 현재 레벨: Lv.{st.session_state.rod_level}")
                            
                        st.rerun() 
                        
                    else:
                        st.error("❗ 코인 부족!")
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
        
        # 📌📌📌 떡밥 가격 갱신 버튼 추가 📌📌📌
        if st.button("🔄 현재 떡밥 가격 갱신", key="manual_bait_refresh"):
            st.toast("💰 떡밥 가격이 갱신되었습니다.", icon='✅')
            st.rerun() 
            
        with st.form("bait_purchase_form"):
            purchase_qty = st.number_input("구매할 떡밥 개수", min_value=1, value=1, step=1, key="bait_qty_form")
            total_cost = purchase_qty * bait_price
            st.write(f"**총 비용:** **{total_cost:,}** 코인")
            can_purchase = st.session_state.coin >= total_cost

            purchase_submitted = st.form_submit_button(
                f"✅ 떡밥 {purchase_qty}개 구매", 
                disabled=not can_purchase
            )

            if purchase_submitted:
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
            
            # 1. 일반 물고기 판매 로직 (특수/합성/괴수/코믹 제외)
            total_sell_coin_general = 0
            sellable_items_general = []
            
            excluded_from_general_sell = set(EXCLUDED_FROM_QUICK_SELL) | set(MONSTER_FISH) | set(COMIC_FISH)

            for item, qty in counts.items():
                if item not in excluded_from_general_sell:
                    price = price_map.get(item, 0)
                    total_sell_coin_general += price * qty
                    sellable_items_general.append((item, qty))

            st.markdown("##### 🐟 일반/희귀 물고기 일괄 판매")
            if total_sell_coin_general > 0:
                st.write(f"**판매 예상 수입:** **{total_sell_coin_general:,}** 코인")
                
                # 판매 버튼도 폼으로 감싸서 독립적인 제출을 보장
                with st.form("sell_general_form"):
                    sell_general_submitted = st.form_submit_button("💰 일반 물고기 전체 판매", type="primary")

                    if sell_general_submitted:
                        
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
            
            # 2. 특수/합성/괴수/코믹 아이템 판매 로직
            total_sell_coin_special = 0
            sellable_items_special = []
            
            included_for_special_sell = set(EXCLUDED_FROM_QUICK_SELL) | set(MONSTER_FISH) | set(COMIC_FISH)

            for item, qty in counts.items():
                if item in included_for_special_sell:
                    price = price_map.get(item, 0)
                    total_sell_coin_special += price * qty
                    sellable_items_special.append((item, qty))

            st.markdown("##### 💎 특수/합성/고가치 아이템 일괄 판매")
            st.write(f"**판매 예상 수입:** **{total_sell_coin_special:,}** 코인")
            if total_sell_coin_special > 0:
                st.caption("⚠️ 지도 조각, 합성, 괴수, 코믹 등 고가치 아이템이 모두 판매됩니다.")
            else:
                st.caption("현재 특수/고가치 아이템이 없습니다.")
                        
            with st.form("sell_special_form"):
                sell_special_submitted = st.form_submit_button(
                    "💎 특수/고가치 아이템 전체 판매", 
                    disabled=total_sell_coin_special == 0, 
                    type="secondary"
                )
                
                if sell_special_submitted:
                    
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

            available_for_sell = list(counts.keys())
            
            with st.form("sell_manual_form"):

                selected = st.multiselect(
                    "판매할 아이템 선택 (수동)",
                    available_for_sell,
                    format_func=lambda x: f"{x} ({price_map.get(x,'N/A'):,} 코인) x {counts.get(x, 0)}",
                    key="sell_select_form" # 폼 안에 있으므로 키 변경
                )
                
                sell_manual_submitted = st.form_submit_button("선택된 아이템 판매")

                if sell_manual_submitted:
                    counts = Counter(st.session_state.inventory)
                    total = 0
                    items_sold_count = 0

                    for item in selected: 
                        sell_qty = counts[item] 
                        items_sold_count += sell_qty
                        
                        for _ in range(sell_qty):
                            st.session_state.inventory.remove(item)
                            
                        total += price_map.get(item, 0) * sell_qty

                    if total > 0:
                        st.session_state.coin = int(st.session_state.coin + total)
                        st.success(f"{items_sold_count}개 판매 완료! +{total:,} 코인")
                        st.rerun()
                    else:
                        st.warning("선택된 아이템이 없습니다.")
        else:
            st.warning("판매할 아이템이 없습니다.")
    
    st.markdown('</div>', unsafe_allow_html=True)

shop_interface()

# ================= 🔧 떡밥 제작 및 아이템 합성 섹션 =================
st.markdown("---")
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.subheader("🧵 떡밥 제작 및 아이템 합성")
st.caption(f"물고기 **{BAIT_CRAFT_FISH_NEEDED}마리** = 떡밥 1개 (합성, 괴수, 코믹, 지도 조각 제외)")
st.markdown("---")

counts = Counter(st.session_state.inventory)

# --- 떡밥 제작 ---
st.markdown("### 🎣 떡밥 제작")
craft_exclusion = set(FUSED_FISH) | set(SPECIAL_ITEMS) | set(MONSTER_FISH) | set(COMIC_FISH)
craft_able_fish_list = [f for f in NORMAL_FISH if f not in craft_exclusion]
total_craftable_fish = sum(counts.get(f, 0) for f in craft_able_fish_list)
max_bait_to_craft = total_craftable_fish // BAIT_CRAFT_FISH_NEEDED

st.write(f"**제작 가능 떡밥 수:** {max_bait_to_craft}개")

# max_value가 0일 때 오류를 방지하기 위해 max_value를 1로 설정하거나, max_bait_to_craft를 사용
with st.form("craft_bait_form_2"): 
    craft_qty = st.number_input(
        "제작할 떡밥 개수", 
        min_value=1, 
        max_value=max_bait_to_craft if max_bait_to_craft > 0 else 1, 
        value=1, 
        step=1,
        key="craft_qty_input_2"
    )
    craft_submitted = st.form_submit_button("🧵 떡밥 제작", disabled=max_bait_to_craft == 0)

    if craft_submitted:
        if craft_qty > 0 and craft_qty <= max_bait_to_craft:
            used_fish_count = 0
            
            # 인벤토리에서 물고기 제거 로직 (제공된 로직 사용)
            for f in craft_able_fish_list:
                while counts.get(f,0) > 0 and used_fish_count < craft_qty * BAIT_CRAFT_FISH_NEEDED:
                    # 실제 인벤토리에서 제거
                    st.session_state.inventory.remove(f) 
                    counts[f] -= 1 # 임시 카운터 업데이트
                    used_fish_count += 1
            
            st.session_state.bait += craft_qty
            st.success(f"🎉 떡밥 {craft_qty}개 제작 완료!")
            st.rerun()
        else:
            st.error("❗ 제작할 수 없는 개수입니다.")

# --- 아이템 합성 ---
st.markdown("---")
st.markdown("### 🧪 아이템 합성")
st.caption("특정 물고기 **2마리** = 합성된 물고기 1개 (합성 가능 물고기만 해당)")

FUSION_COST_NEW = 2 # 새로운 합성 비용 (2마리)

fusion_options = [f for f in fusion_map.keys() if counts.get(f,0) >= FUSION_COST_NEW]

if fusion_options:
    with st.form("fusion_form_2"):
        selected_fish = st.selectbox("합성할 물고기 선택", fusion_options, key="fusion_select_2")
        
        # 선택된 물고기의 최대 합성 가능 횟수 계산
        max_fusion_for_selected = counts.get(selected_fish, 0) // FUSION_COST_NEW
        
        fusion_count = st.number_input(
            "합성할 횟수", 
            min_value=1, 
            max_value=max_fusion_for_selected, 
            value=min(1, max_fusion_for_selected), 
            step=1, 
            key="fusion_count_2"
        )
        
        fusion_submitted = st.form_submit_button(f"🧪 {fusion_count}회 합성 시도")

        if fusion_submitted:
            fish_to_consume = fusion_count * FUSION_COST_NEW
            fused_result = fusion_map[selected_fish]

            if counts.get(selected_fish,0) >= fish_to_consume:
                for _ in range(fish_to_consume):
                    st.session_state.inventory.remove(selected_fish)
                
                for _ in range(fusion_count):
                    catch_fish(fused_result)
                
                st.success(f"🎉 {selected_fish} {fish_to_consume}마리 → {fused_result} {fusion_count}마리 합성 성공!")
                st.rerun()
            else:
                st.error("❗ 해당 물고기 수량 부족")
else:
    st.info("합성 가능한 물고기가 없습니다.")

# 지도 조각 합성 로직은 이전 코드와 동일하게 유지
st.markdown("---")

# --- 3. 지도 조각 합성 (5조각 -> 완성된 지도) ---
st.markdown("### 🗺️ 지도 조각 합성")

MAP_PIECE_COST = MAP_PIECES_NEEDED # 5
map_piece_name = "오래된 지도 조각"
full_map_name = "완성된 오래된 지도"

map_piece_qty = counts.get(map_piece_name, 0)
max_map_crafts = map_piece_qty // MAP_PIECE_COST

st.write(f"**현재 {map_piece_name} 수량:** {map_piece_qty}개")
st.write(f"**필요 수량:** {MAP_PIECE_COST}개 = {full_map_name} 1개")
st.write(f"**최대 제작 가능 지도:** **{max_map_crafts}개**")

if max_map_crafts > 0:
    
    with st.form("map_craft_form_2"):
        map_craft_qty = st.number_input(
            "제작할 완성 지도 개수",
            min_value=1,
            max_value=max_map_crafts,
            value=min(1, max_map_crafts),
            step=1,
            key="map_craft_qty_input_form_2"
        )
        
        pieces_needed = map_craft_qty * MAP_PIECE_COST

        map_submitted = st.form_submit_button(f"🧭 {full_map_name} {map_craft_qty}개 제작", type="secondary")
        
        if map_submitted:
            
            # 인벤토리에서 지도 조각 소모
            for _ in range(pieces_needed):
                st.session_state.inventory.remove(map_piece_name)
                
            # 인벤토리에 완성된 지도 추가 및 도감 업데이트
            for _ in range(map_craft_qty):
                catch_fish(full_map_name) 
            
            st.success(f"🎉 **{full_map_name}** {map_craft_qty}개 제작 완료! ( {map_piece_name} {pieces_needed}개 소모)")
            check_for_map_completion() # 지도를 완성했으므로 잃어버린 섬 해금 시도
            st.rerun()
else:
    st.info(f"**{map_piece_name}**가 {MAP_PIECE_COST}개 미만으로 완성된 지도를 제작할 수 없습니다.")

st.markdown('</div>', unsafe_allow_html=True)


# ================= 🔚 게임 종료 및 초기화 버튼 =================
st.markdown("---")
st.markdown('<div class="game-section" style="background-color: #f8d7da; border-color: #dc3545;">', unsafe_allow_html=True)
st.subheader("⚙️ 게임 설정 / 초기화")
st.caption("모든 진행 상황이 삭제됩니다. 이 작업은 되돌릴 수 없습니다.")
# 일반 st.button으로 변경 (새로운 요청에 따름)
if st.button("🗑️ 모든 게임 데이터 초기화", key="reset_game"):
    reset_game_data()
st.markdown('</div>', unsafe_allow_html=True)
