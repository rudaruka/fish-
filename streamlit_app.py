import streamlit as st
import random
from collections import Counter
import math # math.ceil을 사용하기 위해 추가

# ================= 0. 페이지 설정 및 CSS 스타일링 (밝은 테마 적용) =================
st.set_page_config(
    page_title="이제는 더 이상 물러날 곳이 없다!!!",
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
    # 🐟 일반/흔함 물고기 (Prob 15~30) - '강가'의 기본 물고기
    "멸치": 25, "복어": 25, "누치": 20, "정어리": 15, 
    "빙어": 10, "북어": 10, "꽁치": 10, "은어": 8, "노래미": 7, "쥐치": 5, 
    "피라냐": 30, "메기": 20, "송어": 20, "붕어": 25, "잉어": 15, "향어": 20,
    "가물치": 25, "쏘가리": 15, "붕장어": 20, "갯장어": 15,

    # 🦈 바다/희귀 물고기 (Prob 4~10) - '바다'에서 확률 증가
    "고등어": 7, "전갱이": 10, "우럭": 15, "삼치": 15,
    "참치": 10, "연어": 8, "광어": 7, "도미": 7, "농어": 6, "아귀": 5, 
    "볼락": 5, "갈치": 4, "병어": 4,

    # 🦀 특수/초희귀 물고기 (Prob 1~3) - '전설의 해역'에서 확률 증가
    "청새치": 3, "황새치": 2, "랍스터": 2, "킹크랩": 1, "개복치": 1, "해마": 3,

    # ✨ 새로운 합성 기반 물고기 (Prob 15~20)
    "방어": 20, "날치": 15, "열기": 15,
    
    # 🔱 심해/전설 물고기 (Prob 0.5) - '잃어버린 섬' 전용
    "메가참치": 0.5, "번개상어": 0.5, "심연참돔": 0.5,

    # ☣️ 괴수 물고기 (Prob 0.1) - '전설의 해역'에서 낮은 확률로 등장
    "암흑고래수리" : 0.1, "화염비늘룡어" : 0.1, "태풍포식상어" : 0.1, "얼음유령해마" : 0.1, "심해철갑괴치" : 0.1
}

fish_list = list(fish_prob.keys())
fish_weights = list(fish_prob.values())
# 가격 계산 로직 개선: 희귀도에 따라 가격을 더 명확하게 차별화 (예: (100 - prob) * 100 + 1000)
price_map = {fish: int((100 - prob) * 100) + 1000 for fish, prob in fish_prob.items()} 

fusion_map = {
    "멸치": "대멸치", "복어": "대복어", "누치": "대누치",
    "정어리": "대정어리", "붕어": "대붕어",
    "방어": "대방어", "날치": "대날치", "열기": "대열기"
}

# 합성 물고기 가격 정의
for base, fused in fusion_map.items():
    # 합성 물고기 가격을 기본 물고기 가격의 5배로 유지 (기존 로직 유지)
    price_map[fused] = int(price_map.get(base, 0) * 5) 

# 특수 아이템 가격 정의
price_map["오래된 지도 조각"] = 5000
price_map["완성된 오래된 지도"] = 50000
price_map["떡밥"] = 50 # 떡밥의 상점 판매가 (실제 구매가는 shop_items에서 결정)

# 🎣 물가 상승 상수 정의 (요청 1: 떡밥 기준치 50원으로 변경)
MAX_BAIT_INCREASE = 1500 # 최대 가격 상승 한도
BAIT_INCREASE_STEP = 10  # 1회 상승량
CATCH_THRESHOLD_FOR_STEP = 40 # 40마리마다 상승
BAIT_BASE_PRICE = 50 # 🚨 변경됨: 200 -> 50

shop_items = {
    "떡밥": {
        "price": BAIT_BASE_PRICE,
        "desc": "낚시 1회당 1개 필요!",
        "price_increase": 0 # 물가 상승 누적액
    }
}

# 낚싯대 강화 비용/확률 (기존 로직 유지)
ROD_UPGRADE_COSTS = {
    1: {"coin": 2000, "success_rate": 0.8},
    2: {"coin": 4000, "success_rate": 0.6},
    3: {"coin": 8000, "success_rate": 0.4},
}

# 수집 항목 및 판매 제외 항목 (기존 로직 유지)
SPECIAL_ITEMS = ["오래된 지도 조각", "완성된 오래된 지도"]
FUSED_FISH = list(fusion_map.values())
ALL_COLLECTIBLES = set(fish_list) | set(SPECIAL_ITEMS) | set(FUSED_FISH)
EXCLUDED_FROM_QUICK_SELL = SPECIAL_ITEMS + FUSED_FISH 

# 희귀 낚시터 입장 비용 (기존 로직 유지)
RARE_LOCATION_COSTS = {
    "coin": 1500,
    "fish": {"대멸치": 10, "대붕어": 10, "대복어": 10, "대방어": 10, "대날치": 10} 
}
MAP_PIECES_NEEDED = 5 # 지도 조각 합성 개수

# 🚨 요청 2: 떡밥 제작 조건 변경 상수
BAIT_CRAFT_FISH_NEEDED = 2 # 🚨 변경됨: 10 -> 2


# ================= 1. 세션 초기화 =================
def initialize_session_state():
    # 초기 코인 지급
    defaults = {
        "coin": 1000, # 초기 코인을 0에서 1000으로 변경하여 게임 시작 용이
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
    # 기존 로직 유지
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
    # 이미 해금되었거나, 지도가 없다면 리턴 (지도 조각 소모 로직은 합성 섹션으로 이동)
    if st.session_state.lost_island_unlocked:
        return
    
    # 완성된 지도를 인벤토리에서 찾아서 해금
    if full_map in st.session_state.inventory:
        st.session_state.lost_island_unlocked = True
    
        # 완성된 지도 소모
        st.session_state.inventory.remove(full_map) 

        st.toast("🏝️ 잃어버린 섬 해금! 완성된 지도가 소모되었습니다.", icon='🗺️')


def update_bait_price():
    """총 낚시 마릿수에 따라 떡밥 가격을 지속적으로 인상하고, 최대치(1500)로 제한합니다."""
    # 기존 로직 유지
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
    # 이벤트 결과 로직을 좀 더 명확하게 개선
    summary = {
        'coin': 0, 'bonus_fish': [], 'lost_fish': [], 
        'map_pieces': 0, 'special_bonus': 0, 'event_message': None
    }
    
    if random.random() < event_rate: 
        event = random.randint(1, 6) # 이벤트 1~6까지로 확장
        
        if event == 1: # 코인 보너스
            bonus = random.randint(10, 80)
            if location in ["전설의 해역", "잃어버린 섬"]:
                bonus *= 10
            st.session_state.coin = int(st.session_state.coin + bonus) 
            summary['coin'] += bonus
            summary['event_message'] = "💰 보물 상자 발견!"
        
        elif event == 2: # 물고기 보너스
            # 잡기 힘든 희귀 물고기가 나올 확률 높이기
            rare_fish_list = [f for f, prob in fish_prob.items() if prob < 10]
            f2 = random.choice(rare_fish_list) if rare_fish_list else random.choice(fish_list)
            catch_fish(f2)
            summary['bonus_fish'].append(f2)
            summary['event_message'] = "🎣 물고기 무리 포착!"
            
        elif event == 3: # 물고기 손실 (기존 로직 유지)
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
        
        # 추가 이벤트 (떡밥 손실)
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
    rod_bonus_multiplier = 1 + (st.session_state.rod_level * 0.5) # 낚싯대 보너스 0.2 -> 0.5로 상향 조정

    # 가중치 초기값 (강가 기본 가중치)
    base_weights = [math.ceil(w) for w in fish_weights] # 가중치를 정수로 올림 처리하여 안정성 확보

    for i, f in enumerate(fish_list):
        weights[i] = base_weights[i]

    # 1. 위치별 가중치 조정
    if st.session_state.location == "강가":
        for i, f in enumerate(fish_list):
            # 바다/초희귀/전설 물고기 확률 대폭 감소
            if fish_prob.get(f, 1) < 10 or f in ["고등어", "전갱이", "우럭", "삼치"]:
                weights[i] *= 0.1

    elif st.session_state.location == "바다":
        for i, f in enumerate(fish_list):
            # 강가 물고기 확률 대폭 감소
            if f in ["멸치", "복어", "누치", "피라냐", "메기", "붕어", "잉어", "가물치"]:
                weights[i] *= 0.1
            # 바다 물고기 확률 증가
            elif fish_prob.get(f, 1) <= 15 and f not in FUSED_FISH and f not in SPECIAL_ITEMS:
                weights[i] *= 2.0
            
    elif st.session_state.location == "희귀 낚시터":
        for i, f in enumerate(fish_list):
            # 희귀 물고기 (Prob <= 10) 확률 대폭 증가
            if fish_prob.get(f, 1) <= 10:
                weights[i] *= 5.0
            # 합성 재료 물고기 확률 증가 (입장 조건 반영)
            if f in fusion_map.keys(): 
                weights[i] *= 2.5
            # 일반 물고기 확률 감소
            elif fish_prob.get(f, 1) > 15:
                weights[i] *= 0.05
            
    elif st.session_state.location == "전설의 해역":
        for i, f in enumerate(fish_list):
            # 초희귀 물고기 (Prob <= 3) 확률 대폭 증가
            if fish_prob.get(f, 1) <= 3: 
                weights[i] *= 15.0
            # 괴수 물고기 (Prob 0.1) 확률 증가
            if fish_prob.get(f, 1) == 0.1:
                weights[i] *= 100.0 # 0.1 * 100 = 10으로 조정
            # 일반/희귀 물고기 확률 대폭 감소
            elif fish_prob.get(f, 1) > 10:
                weights[i] *= 0.01

    elif st.session_state.location == "잃어버린 섬":
        for i, f in enumerate(fish_list):
            # 심해/전설 물고기 (Prob 0.5) 확률 극대화
            if fish_prob.get(f, 1) == 0.5: 
                weights[i] *= 1000.0 # 0.5 * 1000 = 500으로 조정
            # 모든 다른 물고기 확률 대폭 감소 또는 0으로 처리
            elif f in fusion_map.keys() or fish_prob.get(f, 1) >= 1:
                weights[i] *= 0.0001
            
    # 2. 낚싯대 보너스 조정 (희귀 물고기만) - 모든 해역에서 적용
    for i, f in enumerate(fish_list):
        if fish_prob.get(f, 1) <= 10: # 희귀도 10 이하 물고기에 보너스
            weights[i] *= rod_bonus_multiplier
            
    # 최종 가중치를 정수로 변환하여 반환
    return [max(1, math.ceil(w)) for w in weights] # 가중치가 최소 1이 되도록 보장


# ================= 4. UI 시작 =================
st.title("🎣 바다의 왕이 되기 위해")
st.subheader("심해 속으로, 섬을 다 찾기 위해서!")
st.write("기본 지급되는 떡밥으로, 낚시를 시작해보자!!") # 떡밥 4개 지급 메시지 제거 (코인 지급으로 변경)

# --- 상단 통계 컨테이너 ---
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.markdown("### 📊 현재 상태")
stats_col1, stats_col2, stats_col3, stats_col4 = st.columns([1.5, 1.5, 1.5, 4])

with stats_col1:
    st.markdown(f"**💰 코인:** <span class='stat-value' style='color: #ffc107;'>{int(st.session_state.coin):,}</span>", unsafe_allow_html=True)
with stats_col2:
    # 🚨 수정: 마크다운 내부에서 st.rerun() 호출 오류 수정
    st.markdown(f"**🧵 떡밥:** <span class='stat-value' style='color: #fd7e14;'>{st.session_state.bait}개</span>", unsafe_allow_html=True)
with stats_col3:
    st.markdown(f"**🎣 낚싯대:** <span class='stat-value' style='color: #adb5bd;'>Lv.{st.session_state.rod_level}</span>", unsafe_allow_html=True)
with stats_col4:
    st.markdown(f"**📍 위치:** <span class='stat-value' style='color: #00bcd4;'>{st.session_state.location}</span>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ================= 5. 메인 게임 섹션 =================
st.divider()
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.subheader("🌊 낚시")

# 낚시터 선택 로직
location_options = ["강가", "바다"]
if st.session_state.legendary_unlocked:
    location_options.append("전설의 해역")
if st.session_state.lost_island_unlocked:
    location_options.append("잃어버린 섬")
    
# 희귀 낚시터는 별도 입장 버튼이 있으므로 선택지에 넣지 않습니다.

# 낚시터 선택
st.session_state.location_selector = st.selectbox(
    "낚시할 장소 선택", 
    options=location_options, 
    index=location_options.index(st.session_state.location) if st.session_state.location in location_options else 0,
    key="location_select"
)
st.session_state.location = st.session_state.location_selector

# 희귀 낚시터 입장 로직
if st.session_state.location != "희귀 낚시터":
    
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
    
    if st.button("🗺️ 희귀 낚시터 입장", disabled=not can_enter_rare or not fish_requirements_met):
        
        # 비용 지불
        st.session_state.coin -= RARE_LOCATION_COSTS["coin"]
        
        # 물고기 소모
        for fish, qty in RARE_LOCATION_COSTS["fish"].items():
            for _ in range(qty):
                st.session_state.inventory.remove(fish)
            
        st.session_state.location = "희귀 낚시터"
        st.success("🎉 희귀 낚시터에 입장했습니다! 낚시를 시작하세요.")
        st.rerun()

# 희귀 낚시터에서 탈출 로직
if st.session_state.location == "희귀 낚시터":
    st.info("현재 **희귀 낚시터**에 있습니다. 이 곳에서는 희귀 물고기와 지도 조각을 획득할 수 있습니다.")
    if st.button("⬅️ 강가로 돌아가기"):
        st.session_state.location = "강가"
        st.success("강가로 돌아왔습니다.")
        st.rerun()

st.markdown("---")

# 낚시 실행 로직
if st.session_state.bait > 0:
    if st.button(f"**낚시하기!** (떡밥 1개 소모)", type="primary"):
        st.session_state.bait -= 1
        st.session_state.total_fish_caught += 1
        update_bait_price() # 물가 상승 체크

        # 가중치 획득
        weights = get_fishing_weights()
        
        # 낚시 결과
        caught_fish = random.choices(fish_list, weights=weights, k=1)[0]
        catch_fish(caught_fish)
        
        # 랜덤 이벤트
        event_rate = 0.15 if st.session_state.location in ["희귀 낚시터", "전설의 해역", "잃어버린 섬"] else 0.1
        event_summary = random_event(event_rate, st.session_state.location)
        
        # 결과 메시지
        st.success(f"🎊 **{st.session_state.location}**에서 **{caught_fish}**를 낚았습니다! (💰{price_map.get(caught_fish, 'N/A'):,} 코인)")
        
        if event_summary['event_message']:
            st.warning(f"🚨 이벤트 발생: **{event_summary['event_message']}**")
            
        # 보상/손실 요약
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
    st.error("❗ 떡밥이 부족합니다. 상점에서 구매하거나 인벤토리에서 제작하세요.")
    
st.markdown('</div>', unsafe_allow_html=True)

# ================= 6. 인벤토리/도감 섹션 =================
st.divider()
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.subheader("📚 인벤토리 & 도감")

inv_col, fishbook_col = st.columns(2)

# --- 인벤토리 ---
with inv_col:
    if st.button("📦 인벤토리 열기/닫기", key="toggle_inventory"):
        st.session_state.inventory_open = not st.session_state.inventory_open
        st.session_state.fishbook_open = False # 도감은 닫기

    if st.session_state.inventory_open:
        counts = Counter(st.session_state.inventory)
        st.markdown("#### 인벤토리 내용")
        if counts:
            
            # 인벤토리 테이블 표시
            inventory_data = {
                "아이템": list(counts.keys()),
                "수량": [counts[item] for item in counts.keys()],
                "판매가": [f"{price_map.get(item, 0):,}" for item in counts.keys()]
            }
            st.table(inventory_data)
        else:
            st.info("인벤토리가 비어 있습니다.")

# --- 도감 ---
with fishbook_col:
    if st.button("📖 도감 열기/닫기", key="toggle_fishbook"):
        st.session_state.fishbook_open = not st.session_state.fishbook_open
        st.session_state.inventory_open = False # 인벤토리는 닫기

    if st.session_state.fishbook_open:
        st.markdown(f"#### 도감 현황 ({len(st.session_state.fishbook)}/{len(ALL_COLLECTIBLES)})")
        
        if st.session_state.fishbook_complete:
            st.success("🏆 도감 완성! 전설의 낚시꾼!")
        
        # 정렬된 목록 생성
        collected = sorted(list(st.session_state.fishbook))
        remaining = sorted(list(ALL_COLLECTIBLES - st.session_state.fishbook))
        
        if collected:
            st.markdown("##### 획득한 아이템")
            st.write(", ".join(collected))
        
        if remaining:
            st.markdown("##### 미획득 아이템")
            st.caption(", ".join([f"???({len(r)})" for r in remaining]))
            
st.markdown('</div>', unsafe_allow_html=True)


# ================= 7. 상점 섹션 =================
st.divider()
def shop_interface():
    st.markdown('<div class="game-section">', unsafe_allow_html=True)
    st.subheader("🏪 상점")
    
    if st.button("🛒 상점 열기/닫기", key="toggle_shop"):
        st.session_state.shop_open = not st.session_state.shop_open
        st.rerun() # 상태 변경 후 재실행

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

            if st.button(f"⬆️ Lv.{next_level} 강화 시도", key="upgrade_rod_btn", disabled=not can_upgrade):
                if can_upgrade:
                    st.session_state.coin -= cost
                    
                    if random.random() < rate:
                        st.session_state.rod_level += 1
                        st.success(f"🎉 **강화 성공!** 현재 레벨: Lv.{st.session_state.rod_level}")
                        st.balloons()
                    else:
                        # 🚨 수정: 중복 rerun 제거 및 return으로 흐름 제어
                        st.error(f"❌ 강화 실패! 코인 {cost:,} 소모. 현재 레벨: Lv.{st.session_state.rod_level}")
                    
                    # 강화 결과에 관계없이 한번만 재실행
                    st.rerun() 
                    
                else:
                    st.error("❗ 코인 부족!")
                    st.rerun()
        else:
            st.info(f"최고 레벨 Lv.{current_level}입니다! 더 이상 강화할 수 없습니다.")

        st.markdown("---")

        # --- 아이템 구매 (떡밥) ---
        st.markdown("### 🛒 떡밥 구매")
        
        update_bait_price() # 가격 정보 업데이트를 상점에서 다시 호출 (실시간 반영)
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

            # 수동 판매를 위한 Multi-select에 현재 재고가 있는 아이템만 표시 (UX 개선)
            available_for_sell = list(counts.keys())

            selected = st.multiselect(
                "판매할 아이템 선택 (수동)",
                available_for_sell,
                format_func=lambda x: f"{x} ({price_map.get(x,'N/A'):,} 코인) x {counts.get(x, 0)}",
                key="sell_select"
            )
            # Multi-select는 항목만 반환하므로, 선택된 항목으로 재고 카운터를 새로 계산해야 함
            # 사용자가 직접 수량을 입력할 수 있도록 변경하는 것이 더 정확함 (복잡성 증가로 일단 기존 로직 유지)

            if st.button("선택된 아이템 판매", key="sell_btn"):
                counts = Counter(st.session_state.inventory)
                selected_counts = Counter(selected)
                total = 0
                items_sold_count = 0

                for item, qty in selected_counts.items():
                    # Multi-select의 작동 방식을 고려하여, '선택된 항목'은 전부 판매하는 것으로 로직을 해석합니다.
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

# ================= 🔧 떡밥 제작 & 합성 섹션 시작 =================
st.divider()
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.subheader("🧵 떡밥 제작 및 아이템 합성")
# 🚨 변경된 제작 조건 표시: 2마리
st.caption(f"물고기 **{BAIT_CRAFT_FISH_NEEDED}마리** = 떡밥 1개 (합성 물고기, 지도 조각 제외)")
st.markdown("---")

counts = Counter(st.session_state.inventory)
excluded_items_craft = list(fusion_map.values()) + SPECIAL_ITEMS
# 🚨 변경된 제작 조건 사용: BAIT_CRAFT_FISH_NEEDED
craft_candidates = [f for f, count in counts.items() if count >= BAIT_CRAFT_FISH_NEEDED and f not in excluded_items_craft]

# 🌟 1. 떡밥 전체 제작 로직
st.markdown("### ⚡ 떡밥 전체 제작 (최적 재료 사용)")

# 판매가가 가장 낮은 물고기를 찾습니다 (가장 효율적인 재료)
best_craft_fish = None
min_price = float('inf')

# 떡밥 제작 가능 항목 중 가장 저렴한 것을 찾기
for fish, count in counts.items():
    if count >= BAIT_CRAFT_FISH_NEEDED and fish not in excluded_items_craft:
        price = price_map.get(fish, float('inf'))
        if price < min_price:
            min_price = price
            best_craft_fish = fish

if best_craft_fish:
    # 🚨 변경된 제작 조건 사용
    max_craftable = counts.get(best_craft_fish, 0) // BAIT_CRAFT_FISH_NEEDED 
    
    st.write(f"✅ **최적의 재료:** **{best_craft_fish}** (판매가: {min_price:,} 코인)")
    st.write(f"**최대 제작 떡밥:** **{max_craftable}개** (재료: {best_craft_fish} {max_craftable * BAIT_CRAFT_FISH_NEEDED}개 소모)")

    if st.button(f"🧵 {best_craft_fish} 전체 사용하여 떡밥 {max_craftable}개 제작", key="craft_all_btn", type="primary"):
        total_fish_needed = max_craftable * BAIT_CRAFT_FISH_NEEDED
        
        for _ in range(total_fish_needed):
            st.session_state.inventory.remove(best_craft_fish)
            
        st.session_state.bait += max_craftable
        st.success(f"**{best_craft_fish}** {total_fish_needed}개 분쇄 완료! 🧵 **떡밥 {max_craftable}개** 획득!")
        st.rerun()
else:
    # 🚨 변경된 제작 조건 반영
    st.info(f"현재 떡밥 전체 제작에 사용할 수 있는 물고기가 없습니다. (동일 물고기 {BAIT_CRAFT_FISH_NEEDED}마리 필요)")

st.markdown("---")

# 🌟 2. 수동 제작
st.markdown("### 🛠️ 수동 제작")

if craft_candidates:
    craft_col1, craft_col2 = st.columns([2, 1])

    with craft_col1:
        selected_fish_to_grind = st.selectbox("분쇄할 물고기 선택 (2마리 소모)", craft_candidates, key="craft_select")
        # 🚨 변경된 제작 조건 사용
        max_craftable_single = counts.get(selected_fish_to_grind, 0) // BAIT_CRAFT_FISH_NEEDED
        st.caption(f"최대 제작 가능: {max_craftable_single}개")

    with craft_col2:
        craft_qty = st.number_input("제작할 떡밥 개수", min_value=1, max_value=max_craftable_single, value=min(1, max_craftable_single) if max_craftable_single > 0 else 0, step=1, key="craft_qty")
    
    # 🚨 변경된 제작 조건 반영
    if st.button(f"'{selected_fish_to_grind}' {craft_qty * BAIT_CRAFT_FISH_NEEDED}개 갈아서 떡밥 {craft_qty}개 제작", key="craft_btn", disabled=max_craftable_single==0 or craft_qty == 0):
        total_fish_needed = craft_qty * BAIT_CRAFT_FISH_NEEDED
        if counts.get(selected_fish_to_grind, 0) >= total_fish_needed:
            for _ in range(total_fish_needed):
                st.session_state.inventory.remove(selected_fish_to_grind)
            st.session_state.bait += craft_qty
            st.success(f"**{selected_fish_to_grind}** {total_fish_needed}마리 분쇄 완료! 🧵 **떡밥 {craft_qty}개** 획득! (현재 떡밥: {st.session_state.bait}개)")
            st.rerun()
else:
    # 🚨 변경된 제작 조건 반영
    st.info(f"수동 제작 가능한 물고기가 없습니다. (인벤토리에 {BAIT_CRAFT_FISH_NEEDED}마리 이상 있는 물고기가 필요합니다.)")

st.markdown("---")

# 🌟 3. 물고기 합성 (Fusion)
st.markdown("### ✨ 물고기 합성 (Mega-Fish)")
st.caption("특정 물고기 10마리를 합성하여 5배 가격의 '대물고기' 1마리를 만듭니다. (합성된 물고기는 판매만 가능)")

fusion_candidates = [base for base, fused in fusion_map.items() if counts.get(base, 0) >= 10]

if fusion_candidates:
    fusion_col1, fusion_col2 = st.columns([2, 1])

    with fusion_col1:
        selected_fish_to_fuse = st.selectbox("합성할 재료 물고기 선택 (10마리 소모)", fusion_candidates, key="fusion_select")
        max_fusion = counts.get(selected_fish_to_fuse, 0) // 10
        st.caption(f"최대 합성 가능: {max_fusion}마리")
        
    with fusion_col2:
        fusion_qty = st.number_input("합성할 횟수", min_value=0, max_value=max_fusion, value=min(1, max_fusion) if max_fusion > 0 else 0, step=1, key="fusion_qty")

    if st.button(f"'{selected_fish_to_fuse}' {fusion_qty * 10}개로 대물고기 {fusion_qty}마리 합성", key="fusion_btn", disabled=max_fusion == 0 or fusion_qty == 0, type="primary"):
        total_fish_needed = fusion_qty * 10
        fused_fish = fusion_map[selected_fish_to_fuse]

        if counts.get(selected_fish_to_fuse, 0) >= total_fish_needed:
            for _ in range(total_fish_needed):
                st.session_state.inventory.remove(selected_fish_to_fuse)
            
            for _ in range(fusion_qty):
                catch_fish(fused_fish) # 인벤토리에 추가 및 도감 업데이트
            
            st.success(f"🔥 **{selected_fish_to_fuse}** {total_fish_needed}마리가 **{fused_fish}** {fusion_qty}마리로 합성되었습니다! (판매가: {price_map.get(fused_fish, 0):,} 코인)")
            st.rerun()
else:
    st.info("합성할 수 있는 물고기가 없습니다. (재료 물고기 10마리 필요)")

st.markdown("---")

# 🌟 4. 지도 조각 합성 (Map Assembly)
st.markdown("### 🗺️ 오래된 지도 조각 조립")
st.caption(f"**오래된 지도 조각** {MAP_PIECES_NEEDED}개를 조합하여 **완성된 오래된 지도** 1개를 만듭니다. (잃어버린 섬 해금 필요)")

map_piece_name = "오래된 지도 조각"
full_map_name = "완성된 오래된 지도"
current_pieces = counts.get(map_piece_name, 0)
max_assemble = current_pieces // MAP_PIECES_NEEDED

st.write(f"**현재 조각:** **{current_pieces}개** / 필요: {MAP_PIECES_NEEDED}개")

if st.button(f"조각 {MAP_PIECES_NEEDED}개로 {full_map_name} 1개 조립", key="assemble_map_btn", disabled=current_pieces < MAP_PIECES_NEEDED):
    
    # 조각 소모
    for _ in range(MAP_PIECES_NEEDED):
        st.session_state.inventory.remove(map_piece_name)
    
    # 완성된 지도 획득
    catch_fish(full_map_name)

    # 잃어버린 섬 해금 확인
    check_for_map_completion() 
    
    st.success(f"🎊 **{full_map_name}** 획득! 인벤토리를 확인하세요.")
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
