import streamlit as st
import random
from collections import Counter
import math

# ================= 1. 설정 및 초기화 =================
st.set_page_config(layout="wide")

def set_style():
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            height: 50px;
        }
        .stTextInput>div>div>input {
            height: 50px;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
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

    # ✨ 새로운 합성 기반 물고기 (Prob 15~20) - 합성 기반 물고기 4종 추가 (방어, 날치, 열기, 붕어)
    "방어": 20, "날치": 15, "열기": 15,
    
    # 🔱 심해/전설 물고기 (Prob 0.5) - '잃어버린 섬' 전용
    "메가참치": 0.5, "번개상어": 0.5, "심연참돔": 0.5,

    # ☣️ 괴수 물고기 (Prob 0.1) - '전설의 해역'에서 낮은 확률로 등장 (5종)
    "암흑고래수리" : 0.1, "화염비늘룡어" : 0.1, "태풍포식상어" : 0.1, "얼음유령해마" : 0.1, "심해철갑괴치" : 0.1
}

fish_list = list(fish_prob.keys()) # 🐟 60종의 물고기
fish_weights = list(fish_prob.values())
price_map = {fish: int((100 - prob) * 100) + 1000 for fish, prob in fish_prob.items()}

# 🚨 NameError 해결을 위해 fusion_map을 먼저 정의합니다.
fusion_map = {
    "멸치": "대멸치", "복어": "대복어", "누치": "대누치",
    "정어리": "대정어리", 
    "붕어": "대붕어", # 붕어 추가 (합성 기반)
    "방어": "대방어", 
    "날치": "대날치", 
    "열기": "대열기" # 열기 추가 (총 8종)
}

# 2. 합성 물고기 가격 정의
for base, fused in fusion_map.items():
    # 합성 물고기는 기본 물고기 가격의 5배
    price_map[fused] = int(price_map.get(base, 0) * 5) 

# 특수 아이템 가격 (판매 불가)
price_map["오래된 지도 조각"] = 0
price_map["완성된 오래된 지도"] = 0

# ================= 3. 상수 정의 =================
ROD_UPGRADE_COSTS = [50000, 150000, 500000, 1500000] # 낚싯대 업그레이드 비용
RARE_LOCATION_COSTS = {
    "바다": 10000, 
    "전설의 해역": 50000, 
    "잃어버린 섬": 500000
}
MAP_PIECES_NEEDED = 5 # 지도 조각 합성 개수

# 🚨 ALL_COLLECTIBLES 정의를 fusion_map 정의 이후로 옮겼습니다.
SPECIAL_ITEMS = ["오래된 지도 조각", "완성된 오래된 지도"] # 2종
FUSED_FISH = list(fusion_map.values()) # 8종 (총 도감 항목: 60 + 2 + 8 = 70종)
ALL_COLLECTIBLES = set(fish_list) | set(SPECIAL_ITEMS) | set(FUSED_FISH) 
EXCLUDED_FROM_QUICK_SELL = SPECIAL_ITEMS + FUSED_FISH

# ================= 4. 세션 상태 초기화 =================
def initialize_session_state():
    if 'money' not in st.session_state:
        st.session_state.money = 10000
    if 'rod_level' not in st.session_state:
        st.session_state.rod_level = 1
    if 'location' not in st.session_state:
        st.session_state.location = "강가"
    if 'inventory' not in st.session_state:
        st.session_state.inventory = Counter()
    if 'fishbook' not in st.session_state:
        st.session_state.fishbook = set()
    if 'fishbook_open' not in st.session_state:
        st.session_state.fishbook_open = False
    if 'inventory_open' not in st.session_state:
        st.session_state.inventory_open = False
    if 'fishbook_complete' not in st.session_state:
        st.session_state.fishbook_complete = False
    # 🎣 UI 업데이트를 위한 메시지 컨테이너
    if 'message' not in st.session_state:
        st.session_state.message = "낚시를 시작해보세요!"

# ================= 5. 기능 함수 정의 =================

def get_current_weights():
    location = st.session_state.location
    weights = []
    for fish, prob in fish_prob.items():
        weight = prob
        
        # 낚싯대 레벨 보너스: 레벨 2 이상은 확률 1.2배, 레벨 4 이상은 1.5배
        if st.session_state.rod_level >= 4:
            weight *= 1.5
        elif st.session_state.rod_level >= 2:
            weight *= 1.2

        # 낚시터 보너스:
        if location == "바다":
            if fish in ["고등어", "참치", "광어", "갈치", "병어"]:
                weight *= 2.5
        elif location == "전설의 해역":
            if fish in ["청새치", "황새치", "랍스터", "킹크랩", "암흑고래수리", "화염비늘룡어", "태풍포식상어", "얼음유령해마", "심해철갑괴치"]:
                weight *= 3.0
        elif location == "잃어버린 섬":
            if fish in ["메가참치", "번개상어", "심연참돔"]:
                weight *= 5.0
                
        weights.append(weight)
    return weights

def fish(message_placeholder):
    weights = get_current_weights()
    fished_item = random.choices(fish_list + SPECIAL_ITEMS, weights=weights + [10, 0], k=1)[0]
    
    # 🎣 낚싯대 레벨에 따른 획득 개수
    num_fished = st.session_state.rod_level
    
    if fished_item in fish_prob:
        st.session_state.inventory[fished_item] += num_fished
        st.session_state.fishbook.add(fished_item)
        msg = f"🎣 **{fished_item}** {num_fished}마리를 낚았습니다! (총 {st.session_state.inventory[fished_item]}마리)"
        
    elif fished_item == "오래된 지도 조각":
        st.session_state.inventory[fished_item] += 1
        st.session_state.fishbook.add(fished_item)
        msg = "🗺️ **오래된 지도 조각** 1개를 발견했습니다!"
        
    elif fished_item == "완성된 오래된 지도": # 확률이 0이라 사실상 낚이지 않음
        st.session_state.inventory[fished_item] += 1
        st.session_state.fishbook.add(fished_item)
        msg = "🧭 **완성된 오래된 지도**를 획득했습니다! (판매 불가)"

    else:
        # 이 else는 weights에 0이 아닌 값이 있을 때만 실행됨
        msg = "아무것도 낚지 못했습니다..."
        
    message_placeholder.info(msg)
    
    # 도감 완성 확인
    if not st.session_state.fishbook_complete and len(st.session_state.fishbook) == len(ALL_COLLECTIBLES):
        st.session_state.fishbook_complete = True

def quick_sell():
    total_money = 0
    items_to_remove = []
    
    # 재고에서 판매 불가 목록(특수/합성 물고기)을 제외하고 판매
    for item, count in st.session_state.inventory.items():
        if item not in EXCLUDED_FROM_QUICK_SELL:
            total_money += price_map.get(item, 0) * count
            items_to_remove.append(item)

    for item in items_to_remove:
        del st.session_state.inventory[item]

    if total_money > 0:
        st.session_state.money += total_money
        st.success(f"💰 일반 아이템을 모두 판매하여 **{total_money:,.0f} 골드**를 획득했습니다.")
    else:
        st.warning("판매할 수 있는 일반 물고기가 없습니다.")

def upgrade_rod():
    current_level = st.session_state.rod_level
    if current_level >= len(ROD_UPGRADE_COSTS) + 1:
        st.warning("더 이상 낚싯대를 업그레이드할 수 없습니다. (최고 레벨)")
        return
    
    cost = ROD_UPGRADE_COSTS[current_level - 1]
    
    if st.session_state.money >= cost:
        st.session_state.money -= cost
        st.session_state.rod_level += 1
        st.success(f"🎉 낚싯대 레벨 **{st.session_state.rod_level}**로 업그레이드! 낚는 양이 늘어납니다.")
    else:
        st.error(f"⚠️ 업그레이드 비용 **{cost:,.0f} 골드**가 부족합니다. (현재: {st.session_state.money:,.0f} 골드)")

def change_location(new_location):
    if new_location == "강가":
        st.session_state.location = "강가"
        st.success("🏞️ 낚시터를 **강가**로 변경했습니다. 기본 물고기가 잘 낚입니다.")
        return
    
    cost = RARE_LOCATION_COSTS.get(new_location, 0)
    
    if st.session_state.money >= cost:
        st.session_state.money -= cost
        st.session_state.location = new_location
        st.success(f"🌊 낚시터를 **{new_location}**으로 변경했습니다. ({cost:,.0f} 골드 소모)")
    else:
        st.error(f"⚠️ 낚시터 이동 비용 **{cost:,.0f} 골드**가 부족합니다.")

def fuse_map():
    pieces = st.session_state.inventory["오래된 지도 조각"]
    
    if pieces >= MAP_PIECES_NEEDED:
        st.session_state.inventory["오래된 지도 조각"] -= MAP_PIECES_NEEDED
        st.session_state.inventory["완성된 오래된 지도"] += 1
        st.session_state.fishbook.add("완성된 오래된 지도")
        st.success(f"🧭 지도 조각 {MAP_PIECES_NEEDED}개를 모아 **완성된 오래된 지도** 1개를 만들었습니다!")
    else:
        st.error(f"⚠️ **오래된 지도 조각**이 {MAP_PIECES_NEEDED}개 필요합니다. (현재: {pieces}개)")

def fuse_fish():
    fusion_success = False
    
    # 멸치, 복어, 누치, 정어리, 붕어, 방어, 날치, 열기 (총 8종)
    fusion_targets = list(fusion_map.keys())
    
    for base_fish in fusion_targets:
        fused_fish = fusion_map[base_fish]
        count = st.session_state.inventory[base_fish]
        
        # 10마리 단위로 합성 가능
        if count >= 10:
            num_fusion = count // 10
            st.session_state.inventory[base_fish] -= num_fusion * 10
            st.session_state.inventory[fused_fish] += num_fusion
            st.session_state.fishbook.add(fused_fish)
            
            st.success(f"🧪 **{base_fish}** {num_fusion*10}마리를 합성하여 **{fused_fish}** {num_fusion}마리를 만들었습니다!")
            fusion_success = True
            
    if not fusion_success:
        st.warning("⚠️ 합성할 수 있는 물고기가 없습니다. (합성 기반 물고기 10마리 필요)")

# ================= 6. UI/메인 로직 =================
set_style()
initialize_session_state()

st.title("🐟 방치형 낚시 타이쿤")

money_col, rod_col, location_col = st.columns(3)
with money_col:
    st.markdown(f"**💰 골드:** {st.session_state.money:,.0f} G")
with rod_col:
    st.markdown(f"**🎣 낚싯대 레벨:** {st.session_state.rod_level} (Lv. {st.session_state.rod_level}/{len(ROD_UPGRADE_COSTS)+1})")
with location_col:
    st.markdown(f"**🗺️ 현재 낚시터:** {st.session_state.location}")

st.divider()

# 낚시 결과 메시지를 위한 컨테이너
message_placeholder = st.empty()

# --- 낚시 및 판매 ---
fish_col, sell_col = st.columns(2)
with fish_col:
    if st.button("🎣 낚시하기"):
        fish(message_placeholder)

with sell_col:
    if st.button("💰 일반 물고기 일괄 판매"):
        quick_sell()

st.divider()

# --- 업그레이드, 낚시터, 합성 ---
upgrade_col, location_col, fuse_col = st.columns(3)

with upgrade_col:
    st.markdown("#### 🎣 낚싯대 업그레이드")
    next_level = st.session_state.rod_level + 1
    if next_level <= len(ROD_UPGRADE_COSTS) + 1:
        cost = ROD_UPGRADE_COSTS[st.session_state.rod_level - 1]
        st.markdown(f"다음 레벨 ({next_level}): **{cost:,.0f} G**")
        if st.button("업그레이드", key="upgrade_rod"):
            upgrade_rod()
    else:
        st.markdown("**(최고 레벨 달성)**")

with location_col:
    st.markdown("#### 🗺️ 낚시터 변경")
    st.selectbox("낚시터 선택", 
        options=["강가", "바다", "전설의 해역", "잃어버린 섬"], 
        key="new_location",
        index=["강가", "바다", "전설의 해역", "잃어버린 섬"].index(st.session_state.location)
    )
    if st.button("이동하기", key="change_location"):
        change_location(st.session_state.new_location)

with fuse_col:
    st.markdown("#### 🧪 아이템 합성")
    if st.button("지도 조각 합성 (5개 → 1개)", key="fuse_map"):
        fuse_map()
    if st.button("물고기 합성 (10마리 → 1마리)", key="fuse_fish"):
        fuse_fish()

st.divider()

# --- 인벤토리와 도감 ---
inventory_col, fishbook_col = st.columns(2)

with inventory_col:
    if st.button("🎒 인벤토리 열기/닫기", key="toggle_inventory"):
        st.session_state.inventory_open = not st.session_state.inventory_open
        st.session_state.fishbook_open = False # 도감은 닫기

    if st.session_state.inventory_open:
        st.markdown("#### 인벤토리 현황")
        if st.session_state.inventory:
            # 딕셔너리 정렬: 아이템 이름순
            sorted_inventory = sorted(st.session_state.inventory.items())
            
            for item, count in sorted_inventory:
                # 0개인 아이템은 표시하지 않음
                if count > 0:
                    price = price_map.get(item, 0)
                    total_value = price * count
                    
                    sellable_status = "❌ 판매불가" if item in EXCLUDED_FROM_QUICK_SELL else "✅ 일반"
                    
                    st.markdown(f"* **{item}** x {count} ({sellable_status}, 가치: {total_value:,.0f} G)")
        else:
            st.info("인벤토리가 비어있습니다.")

with fishbook_col:
    if st.button("📖 도감 열기/닫기", key="toggle_fishbook"):
        st.session_state.fishbook_open = not st.session_state.fishbook_open
        st.session_state.inventory_open = False # 인벤토리는 닫기

    if st.session_state.fishbook_open:
        # 🚨 수정된 총 도감 항목 수 (60종 물고기 + 2종 지도 + 8종 합성 물고기 = 70)
        st.markdown(f"#### 도감 현황 ({len(st.session_state.fishbook)}/{len(ALL_COLLECTIBLES)})")
        
        if st.session_state.fishbook_complete:
            st.success("🏆 도감 완성! 전설의 낚시꾼!")
        
        # 수집 항목 분류
        fish_caught = [item for item in ALL_COLLECTIBLES if item in fish_list]
        fused_caught = [item for item in ALL_COLLECTIBLES if item in FUSED_FISH]
        special_caught = [item for item in ALL_COLLECTIBLES if item in SPECIAL_ITEMS]
        
        st.markdown("**🐟 물고기** (60종)")
        cols = st.columns(5)
        for i, item in enumerate(sorted(fish_caught)):
            status = "✅" if item in st.session_state.fishbook else "❓"
            cols[i % 5].markdown(f"*{status} {item}*")
            
        st.markdown("**🧪 합성 물고기** (8종)")
        cols = st.columns(5)
        for i, item in enumerate(sorted(fused_caught)):
            status = "✅" if item in st.session_state.fishbook else "❓"
            cols[i % 5].markdown(f"*{status} {item}*")

        st.markdown("**🗺️ 특수 아이템** (2종)")
        cols = st.columns(5)
        for i, item in enumerate(sorted(special_caught)):
            status = "✅" if item in st.session_state.fishbook else "❓"
            cols[i % 5].markdown(f"*{status} {item}*")
            
st.divider()

# 마지막 메시지 컨테이너 정리
if st.session_state.message:
    st.info(st.session_state.message)
