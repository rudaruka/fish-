import streamlit as st
import random

# ------------------------------------------------
# 기본 세션 초기화
# ------------------------------------------------
if "coin" not in st.session_state:
    st.session_state.coin = 0
if "bait" not in st.session_state:
    st.session_state.bait = 10
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "items" not in st.session_state:
    st.session_state.items = {}
if "shop_open" not in st.session_state:
    st.session_state.shop_open = False
if "location" not in st.session_state:
    st.session_state.location = "일반 낚시터"

# ------------------------------------------------
# 기본 물고기 테이블
# ------------------------------------------------
fish_list = [
    "멸치", "고등어", "붕어", "참돔", "연어",
    "돌돔", "문어", "오징어", "참치", "상어"
]

price_map = {
    "멸치": 5,
    "고등어": 10,
    "붕어": 12,
    "참돔": 25,
    "연어": 30,
    "돌돔": 40,
    "문어": 50,
    "오징어": 15,
    "참치": 60,
    "상어": 100
}

# ------------------------------------------------
# 합성 시스템
# ------------------------------------------------
fusion_map = {
    "멸치": "대멸치",
    "고등어": "대고등어",
    "붕어": "대붕어"
}

# 합성 물고기 가격 생성 (base 가격 ×5)
for base, fused in fusion_map.items():
    if base in price_map:
        price_map[fused] = price_map[base] * 5
    else:
        price_map[fused] = 50  # 안전 기본값


# ------------------------------------------------
# 확률 계산
# ------------------------------------------------
def get_fishing_weights(location):
    base_weights = [40, 25, 20, 7, 5, 2, 1, 5, 3, 2]

    if len(base_weights) != len(fish_list):
        base_weights = [1] * len(fish_list)

    if location == "희귀 낚시터":
        base_weights = [x * 0.5 for x in base_weights]
        base_weights[-3] *= 3
        base_weights[-2] *= 3
        base_weights[-1] *= 4

    return base_weights


# ------------------------------------------------
# 낚시 함수
# ------------------------------------------------
def do_fishing():
    if st.session_state.bait < 1:
        st.error("미끼가 부족합니다!")
        return

    st.session_state.bait -= 1
    weights = get_fishing_weights(st.session_state.location)
    fish = random.choices(fish_list, weights=weights, k=1)[0]
    st.session_state.inventory.append(fish)
    st.success(f"🎣 {fish} 을(를) 낚았습니다!")


# ------------------------------------------------
# 물고기 합성
# ------------------------------------------------
def do_fusion():
    inv = st.session_state.inventory

    for base, fused in fusion_map.items():
        if inv.count(base) >= 5:
            st.success(f"합성 성공! {base} → {fused}")
            for _ in range(5):
                inv.remove(base)
            inv.append(fused)
            return

    st.warning("합성 가능한 물고기가 없습니다.")


# ------------------------------------------------
# 물고기 판매 (중복 선택 버그 수정)
# ------------------------------------------------
def sell_fish(selected):
    inv = st.session_state.inventory

    for fish in selected:
        actual_count = inv.count(fish)
        sell_count = min(actual_count, selected.count(fish))

        for _ in range(sell_count):
            inv.remove(fish)
            st.session_state.coin += price_map.get(fish, 0)

    st.success("판매 완료!")


# ------------------------------------------------
# UI 시작
# ------------------------------------------------
st.title("🎣 낚시 게임 v2 (버그 수정 버전)")

# ------------------------------------------------
# 장소 선택
# ------------------------------------------------
location = st.selectbox("낚시터 선택", ["일반 낚시터", "희귀 낚시터"])

# 희귀 낚시터 입장 조건 (20마리로 통일)
if location == "희귀 낚시터":
    if st.session_state.inventory.count("대멸치") >= 20 and st.session_state.inventory.count("대붕어") >= 20:
        st.success("희귀 낚시터 입장 성공!")
        st.session_state.location = "희귀 낚시터"
    else:
        st.warning("입장 조건: 대멸치 20마리 + 대붕어 20마리 필요!")
        st.stop()
else:
    st.session_state.location = "일반 낚시터"


# ------------------------------------------------
# 상점 UI
# ------------------------------------------------
st.markdown("---")
open_shop = st.checkbox("상점 열기", key="shop_open")

if open_shop:
    st.subheader("🛒 상점")

    if st.button("미끼 구매 (1개 = 10코인)"):
        if st.session_state.coin >= 10:
            st.session_state.coin -= 10
            st.session_state.bait += 1
            st.success("미끼 1개 구매!")
        else:
            st.error("코인이 부족합니다!")


# ------------------------------------------------
# 낚시 버튼
# ------------------------------------------------
if st.button("🎣 낚시하기"):
    do_fishing()

# ------------------------------------------------
# 합성 버튼
# ------------------------------------------------
if st.button("✨ 물고기 합성"):
    do_fusion()

# ------------------------------------------------
# 인벤토리 출력
# ------------------------------------------------
st.subheader("🎒 인벤토리")
st.write(st.session_state.inventory)

# ------------------------------------------------
# 판매 시스템
# ------------------------------------------------
st.subheader("💰 판매하기")
selected_sell = st.multiselect("판매할 물고기 선택", st.session_state.inventory)

if st.button("판매"):
    sell_fish(selected_sell)

# ------------------------------------------------
# 상태 표시
# ------------------------------------------------
st.markdown("---")
st.write(f"코인: {st.session_state.coin}")
st.write(f"미끼: {st.session_state.bait}")
st.write(f"현재 위치: {st.session_state.location}")
