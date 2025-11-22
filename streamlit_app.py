import streamlit as st
import random
from collections import Counter

# ================= 세션 초기화 (강화됨) =================
# items가 딕셔너리임을 확실히 보장합니다.
if "items" not in st.session_state or not isinstance(st.session_state.items, dict):
    st.session_state.items = {
        "강화 미끼": 0,
        "자동 낚시권": 0
    }
    
if "coin" not in st.session_state:
    st.session_state.coin = 0
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "shop_open" not in st.session_state:
    st.session_state.shop_open = False
if "fishbook" not in st.session_state:
    st.session_state.fishbook = set()
if "location" not in st.session_state:
    st.session_state.location = "강가"
if "location_selector" not in st.session_state:
    st.session_state.location_selector = "강가"
if "rod_level" not in st.session_state:
    st.session_state.rod_level = 0

# ================= 물고기 & 가격 =================
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

shop_items = {
    "강화 미끼": {"price": 500, "desc": "낚싯대 강화에 필요한 핵심 재료입니다."},
    "자동 낚시권": {"price": 1000, "desc": "자동으로 낚시를 진행할 수 있는 권한입니다."},
}

ROD_UPGRADE_COSTS = {
    1: {"coin": 2000, "bait": 2, "success_rate": 0.8},
    2: {"coin": 4000, "bait": 4, "success_rate": 0.6},
    3: {"coin": 8000, "bait": 8, "success_rate": 0.4},
}

# ================= 함수 =================
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

def auto_fish(num_tries=5):
    items_dict = st.session_state.get("items", {})
    if items_dict.get("자동 낚시권", 0) <= 0:
        st.error("자동 낚시권이 없습니다.")
        return
    
    # 이 부분은 초기화 로직에 의해 딕셔너리임이 보장됨
    st.session_state.items["자동 낚시권"] -= 1
    st.info(f"🎫 자동 낚시권 1개를 소모했습니다. ({num_tries}회 낚시 시작)")
    
    fish_caught_list = []
    for _ in range(num_tries):
        fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
        catch_fish(fish)
        fish_caught_list.append(fish)
        random_event(0.1)
        
    st.success(f"✅ 자동 낚시 완료! 잡은 물고기: {', '.join(fish_caught_list)}")

# ================= UI =================
st.title("🎣 낚시는 운이야!!")
st.write(f"💰 현재 코인: **{st.session_state.coin}**")
st.write(f"✨ 낚싯대 레벨: **Lv.{st.session_state.rod_level}**")
st.divider()

# 낚시터 선택
st.subheader("🌍 낚시터 선택")
current_location = st.session_state.location
temp_location = st.selectbox("현재 낚시터",
                              ["강가","바다","희귀 낚시터"],
                              index=["강가","바다","희귀 낚시터"].index(current_location),
                              key="location_selector")
if temp_location != current_location:
    if temp_location == "희귀 낚시터":
        if st.session_state.coin >= 1000:
            st.session_state.coin -= 1000
            st.session_state.location = temp_location
            st.success("🔥 희귀 낚시터 입장! (-1000코인)")
        else:
            st.warning("❗ 코인이 부족합니다! (1000 필요)")
            st.session_state.location_selector = current_location 
    else:
        st.session_state.location = temp_location
        st.info(f"📍 낚시터를 {temp_location} 로 변경")
    
st.markdown(f"**현재 위치:** {st.session_state.location}")
st.divider()

col1,col2,col3 = st.columns(3)

# ================= 🎣 낚시 =================
with col1:
    st.subheader("🎣 낚시하기")
    # items에 안전하게 접근
    items_dict = st.session_state.get("items", {}) 
    current_auto_pass = items_dict.get("자동 낚시권", 0)
    
    if st.button(f"자동 낚시 (5회 소모)", key="auto_fish_btn", disabled=(current_auto_pass == 0)):
        auto_fish(5)

    if st.session_state.location == "희귀 낚시터":
        if st.button("희귀 낚시 1회", key="rare_1"):
            fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
            catch_fish(fish)
            st.success(f"💎 **{fish}** 낚았다!")
            random_event(0.2)
        if st.button("희귀 낚시 2회", key="rare_2"):
            fish_caught = random.choices(fish_list, weights=get_fishing_weights(), k=2)
            for f in fish_caught: catch_fish(f)
            st.success(f"💎 **{', '.join(fish_caught)}** 낚았다!")
            random_event(0.35)
    else:
        if st.button("1번 낚시", key="normal_1"):
            fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
            catch_fish(fish)
            st.success(f"**{fish}** 낚았다!")
            random_event(0.15)
        if st.button("2번 낚시", key="normal_2"):
            fish_caught = random.choices(fish_list, weights=get_fishing_weights(), k=2)
            for f in fish_caught: catch_fish(f)
            st.success(f"**{', '.join(fish_caught)}** 낚았다!")
            random_event(0.25)

# ================= 🎒 인벤토리 =================
with col2:
    st.subheader("🎒 인벤토리")
    display_inventory = st.session_state.inventory.copy()
    st.write("---")
    if display_inventory:
        counts = Counter(display_inventory)
        for item, cnt in counts.items():
            st.write(f"**{item}** x **{cnt}** (판매가: {price_map.get(item,'N/A')} 코인)")
    else:
        st.info("인벤토리가 비어 있습니다.")
    st.write("---")
    st.subheader("🛒 구매 아이템")
    # items 딕셔너리를 안전하게 가져와서 표시
    items_dict = st.session_state.get("items", {})
    if any(items_dict.values()):
        for item, cnt in items_dict.items():
            if cnt>0:
                st.write(f"**{item}** x **{cnt}**")
    else:
        st.info("구매한 아이템이 없습니다.")

# ================= 🏪 상점 / 강화 =================
with col3:
    st.subheader("🏪 상점 / 강화")
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open, key="shop_open_cb")
    st.session_state.shop_open = open_shop

st.divider()

if st.session_state.shop_open:
    # 낚싯대 강화
    st.subheader("🛠️ 낚싯대 강화")
    current_level = st.session_state.rod_level
    next_level = current_level + 1
    if next_level in ROD_UPGRADE_COSTS:
        cost = ROD_UPGRADE_COSTS[next_level]
        # items에 안전하게 접근
        items_dict = st.session_state.get("items", {}) 
        current_bait = items_dict.get("강화 미끼", 0)
        
        st.write(f"**현재 레벨: Lv.{current_level}**")
        st.write(f"**다음 레벨: Lv.{next_level}**")
        st.write(f"필요 코인: **{cost['coin']}** (현재: {st.session_state.coin})")
        st.write(f"필요 강화 미끼: **{cost['bait']}** (현재: {current_bait})")
        st.write(f"성공 확률: **{int(cost['success_rate']*100)}%**")
        can_upgrade = st.session_state.coin >= cost['coin'] and current_bait >= cost['bait']
        if st.button(f"Lv.{next_level} 강화 시도", key=f"upgrade_{next_level}", disabled=not can_upgrade):
            st.session_state.coin -= cost['coin']
            # 초기화로 인해 안전하다고 가정
            st.session_state.items["강화 미끼"] -= cost['bait']
            if random.random() < cost['success_rate']:
                st.session_state.rod_level = next_level
                st.success(f"🎉 **강화 성공!** 낚싯대 Lv.{next_level}")
            else:
                st.error("💥 **강화 실패!** 재료만 소모")
    else:
        st.info(f"낚싯대가 **최고 레벨 Lv.{current_level}**입니다!")

    # 아이템 구매
    st.subheader("🛒 아이템 구매")
    shop_cols = st.columns(2)
    for i,(item,data) in enumerate(shop_items.items()):
        with shop_cols[i%2]:
            st.write(f"**{item}** ({data['price']} 코인)")
            st.caption(data["desc"])
            if st.button(f"구매 {item}", key=f"buy_{item}"):
                if st.session_state.coin >= data["price"]:
                    st.session_state.coin -= data["price"]
                    
                    # 💡 최종 수정 로직: 오류 발생 가능성이 있는 모든 접근을 try-except로 감쌈.
                    # 오류 발생 시 items를 강제로 딕셔너리로 복구하고 다시 시도함.
                    try:
                        current_count = st.session_state.items.get(item, 0)
                        st.session_state.items[item] = current_count + 1
                        st.success(f"**{item}** 1개 구매 완료!")
                    except (AttributeError, TypeError):
                        # ❌ 라인 275 오류 발생 시 실행되는 복구 로직 수정 ❌
                        st.error("❌ 아이템 구매 중 오류 발생! 세션 상태를 복구합니다.")
                        # st.session_state.items를 안전하게 초기 딕셔너리로 재설정 (버그의 원인 제거)
                        st.session_state.items = {
                            "강화 미끼": 0,
                            "자동 낚시권": 0
                        }
                        # 초기화 후 다시 업데이트 시도 (재귀 호출 방지를 위해 직접 업데이트)
                        st.session_state.items[item] = st.session_state.items.get(item, 0) + 1
                        st.success(f"**{item}** 1개 구매 완료 (복구 후).")

                else:
                    st.error("❗ 코인 부족!")

    # 판매
    st.subheader("💰 판매")
    if st.session_state.inventory:
        selected = st.multiselect("판매할 아이템 선택", st.session_state.inventory,
                                  format_func=lambda x: f"{x} ({price_map.get(x,'N/A')} 코인)", key="sell_select")
        if st.button("판매 선택 아이템", key="sell_btn"):
            counts = Counter(st.session_state.inventory)
            selected_counts = Counter(selected)
            total = 0
            for item, qty in selected_counts.items():
                sell_qty = min(qty, counts[item])
                for _ in range(sell_qty):
                    st.session_state.inventory.remove(item)
                total += price_map.get(item,0) * sell_qty
            if total>0:
                st.session_state.coin += total
                st.success(f"**{sum(selected_counts.values())}**개 판매 완료! +**{total}** 코인")
    else:
        st.warning("판매할 아이템이 없습니다.")

# ================= ⚡ 합성 =================
st.subheader("⚡ 물고기 합성")
counts = Counter(st.session_state.inventory)
fusion_candidates = [f for f in fusion_map.keys() if counts.get(f,0)>=2]
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
                st.success(f"**합성 성공!** {sel} 2마리 → **{result}** 1마리")
            else:
                st.error(f"**합성 실패!** {sel} 2마리 소모")
        else:
            st.warning("합성 가능한 물고기 수가 부족합니다.")
else:
    st.info("합성 가능한 물고기가 없습니다. (2마리 필요)")

# ================= 📚 도감 =================
st.subheader("📚 물고기 도감")
st.markdown("##### 🐟 일반 물고기")
cols = st.columns(5)
for i, fish in enumerate(fish_list):
    with cols[i%5]:
        status = "✔ 발견" if fish in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{fish}** ({status})")

st.markdown("##### 💎 특수 아이템")
special_items = ["오래된 지도 조각"]
cols_special = st.columns(5)
for i,item in enumerate(special_items):
    with cols_special[i%5]:
        status = "✔ 발견" if item in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{item}** ({status})")

st.markdown("##### ✨ 합성 물고기")
fuse_cols = st.columns(5)
for i,(base,fused) in enumerate(fusion_map.items()):
    with fuse_cols[i%5]:
        status = "✔ 발견" if fused in st.session_state.fishbook else "✖ 미발견"
        st.write(f"**{fused}** ({status})")

st.write("---")
st.write(f"💰 **최종 코인:** **{st.session_state.coin}**")
