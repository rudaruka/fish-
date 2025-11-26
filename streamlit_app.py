import streamlit as st
import random
from collections import Counter
import math # math.ceil을 사용하기 위해 추가

# (생략: 페이지 설정 및 CSS 스타일링)

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

    # ☣️ 괴수 물고기 (Prob 0.1) - '전설의 해역'에서 낮은 확률로 등장 (5종)
    "암흑고래수리" : 0.1, "화염비늘룡어" : 0.1, "태풍포식상어" : 0.1, "얼음유령해마" : 0.1, "심해철갑괴치" : 0.1
}

fish_list = list(fish_prob.keys()) # 🐟 60종의 물고기 모두 포함
fish_weights = list(fish_prob.values())
# (생략: price_map, fusion_map 정의)

# (생략: ROD_UPGRADE_COSTS, RARE_LOCATION_COSTS 정의)
MAP_PIECES_NEEDED = 5 # 지도 조각 합성 개수


# 수집 항목 및 판매 제외 항목 (수정 없음: fish_list가 60종 모두를 포함합니다.)
SPECIAL_ITEMS = ["오래된 지도 조각", "완성된 오래된 지도"] # 2종
FUSED_FISH = list(fusion_map.values()) # 7종
# ALL_COLLECTIBLES = fish_list(60) + SPECIAL_ITEMS(2) + FUSED_FISH(7) = 69종
ALL_COLLECTIBLES = set(fish_list) | set(SPECIAL_ITEMS) | set(FUSED_FISH) 
EXCLUDED_FROM_QUICK_SELL = SPECIAL_ITEMS + FUSED_FISH 

# (생략: 나머지 코드)
# ...
# ...
# --- 도감 ---
with fishbook_col:
    if st.button("📖 도감 열기/닫기", key="toggle_fishbook"):
        st.session_state.fishbook_open = not st.session_state.fishbook_open
        st.session_state.inventory_open = False # 인벤토리는 닫기

    if st.session_state.fishbook_open:
        # len(ALL_COLLECTIBLES)는 이제 69가 됩니다. (60종의 물고기 + 2종의 지도 + 7종의 합성 물고기)
        st.markdown(f"#### 도감 현황 ({len(st.session_state.fishbook)}/{len(ALL_COLLECTIBLES)})")
        
        if st.session_state.fishbook_complete:
            st.success("🏆 도감 완성! 전설의 낚시꾼!")
# (생략: 나머지 코드)
