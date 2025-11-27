# ================= 2. 물고기 & 가격 정의 =================
fish_prob = {
    # 🐟 일반/흔함 물고기 (Prob 15~30)
    "멸치": 25, "복어": 25, "누치": 20, "정어리": 15, 
    "빙어": 10, "북어": 10, "꽁치": 10, "은어": 8, "노래미": 7, "쥐치": 5, 
    "피라냐": 30, "메기": 20, "송어": 20, "붕어": 25, "잉어": 15, "향어": 20,
    "가물치": 25, "쏘가리": 15, "붕장어": 20, "갯장어": 15,

    # 🦈 바다/희귀 물고기 (Prob 4~10)
    "고등어": 7, "전갱이": 10, "우럭": 15, "삼치": 15,
    "참치": 10, "연어": 8, "광어": 7, "도미": 7, "농어": 6, "아귀": 5, 
    "볼락": 5, "갈치": 4, "병어": 4,

    # 🦀 특수/초희귀 물고기 (Prob 1~3)
    "청새치": 3, "황새치": 2, "랍스터": 2, "킹크랩": 1, "개복치": 1, "해마": 3,
    "방어": 20, "날치": 15, "열기": 15,
    
    # 🔱 심해/전설 물고기 (Prob 0.5) - '잃어버린 섬' 전용
    "메가참치": 0.5, "번개상어": 0.5, "심연참돔": 0.5,

    # ☣️ 괴수 물고기 (Prob 0.2)
    "암흑고래수리" : 0.2, "화염비늘룡어" : 0.2, "태풍포식상어" : 0.2, "얼음유령해마" : 0.2, "심해철갑괴치" : 0.2,

    # 😂 코믹 물고기 (prob 0.1)
    "현이 물고기" : 0.1, "스노 물고기" : 0.1, "위키 물고기" : 0.1, "루루 물고기" : 0.1
}

fish_list = list(fish_prob.keys())
fish_weights = list(fish_prob.values())

# 🎣 가격 인하 계수 정의 (예: 0.6 = 가격이 60%가 됨, 즉 40% 인하)
PRICE_DEFLATION_FACTOR = 0.6 

# 가격 계산 로직: 희귀도에 따라 가격 차별화 (예: (100 - prob) * 100 + 1000)
# 가격 인하 계수 (PRICE_DEFLATION_FACTOR) 적용
price_map = {
    fish: int(((100 - prob) * 100) + 1000) * PRICE_DEFLATION_FACTOR 
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
BAIT_BASE_PRICE = 70 # ⬅️ 50 코인에서 70 코인으로 변경
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
