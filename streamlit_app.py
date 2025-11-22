import streamlit as st
import random
from collections import Counter
from PIL import Image

# ================= 세션 초기화 =================
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

if "items" not in st.session_state:
    st.session_state.items = {
        "강화 미끼": 0,
        "자동 낚시권": 0
    }

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
    "강화 미끼": {"price": 500, "desc": "희귀 물고기 확률을 소폭 올려줍니다."},
    "자동 낚시권": {"price": 1000, "desc": "자동으로 낚시를 진행할 수 있는 권한입니다."},
}

location_images = {
    "강가": "images/river.jpg",
    "바다": "images/sea.jpg",
    "희귀 낚시터": "images/legend.jpg"
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
    if st.session_state.location == "바다":
        weights = [w*1.3 if f in ["전갱이","고등어","꽁치"] else w*0.8
                   for f,w in zip(fish_list, fish_weights)]
    elif st.session_state.location == "희귀 낚시터":
        weights = [w*3 if w<=10 else w for w in fish_weights]
        weights = [w*1.5 if fish_list[i] in fusion_map else w for i,w in enumerate(weights)]
    return weights

# ================= UI 시작 =================
st.title("🎣 낚시는 운이야!!")
st.write(f"💰 현재 코인: {st.session_state.coin}")
st.divider()

# 🌍 낚시터 선택
st.subheader("🌍 낚시터 선택")
temp_location = st.selectbox("현재 낚시터",
                             ["강가","바다","희귀 낚시터"],
                             index=["강가","바다","희귀 낚시터"].index(st.session_state.location),
                             key="location_selector")

if temp_location != st.session_state.location:
    if temp_location == "희귀 낚시터":
        if st.session_state.coin >= 1000:
            st.session_state.coin -= 1000
            st.session_state.location = temp_location
            st.success("🔥 희귀 낚시터 입장! (-1000코인)")
        else:
            st.warning("❗ 코인이 부족합니다! (1000 필요)")
            st.session_state.location_selector = st.session_state.location
    else:
        st.session_state.location = temp_location
        st.info(f"📍 낚시터를 {temp_location} 로 변경")

# 배경 이미지 표시
img = Image.open(location_images[st.session_state.location])
st.image(img, use_column_width=True)
st.divider()

col1,col2,col3 = st.columns(3)

# ================= 🎣 낚시 =================
with col1:
    st.subheader("🎣 낚시하기")
    if st.session_state.location == "희귀 낚시터":
        if st.button("희귀 낚시 1회"):
            fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
            catch_fish(fish)
            st.success(f"💎 {fish} 낚았다!")
            random_event(0.2)
        if st.button("희귀 낚시 2회"):
            fish_caught = random.choices(fish_list, weights=get_fishing_weights(), k=2)
            for f in fish_caught: catch_fish(f)
            st.success(f"💎 {', '.join(fish_caught)} 낚았다!")
            random_event(0.35)
    else:
        if st.button("1번 낚시"):
            fish = random.choices(fish_list, weights=get_fishing_weights(), k=1)[0]
            catch_fish(fish)
            st.success(f"{fish} 낚았다!")
            random_event(0.15)
        if st.button("2번 낚시"):
            fish_caught = random.choices(fish_list, weights=get_fishing_weights(), k=2)
            for f in fish_caught: catch_fish(f)
            st.success(f"{', '.join(fish_caught)} 낚았다!")
            random_event(0.25)

# ================= 🎒 인벤토리 =================
with col2:
    st.subheader("🎒 인벤토리")
    display_inventory = st.session_state.inventory.copy()
    if st.session_state.location != "희귀 낚시터":
        sort_option = st.radio("정렬 방식", ["기본","가나다","희귀도","가격"], key="sort")
        if sort_option == "가나다":
            display_inventory.sort()
        elif sort_option == "희귀도":
            display_inventory.sort(key=lambda x: fish_prob.get(x,1))
        elif sort_option == "가격":
            display_inventory.sort(key=lambda x: price_map.get(x,0), reverse=True)
    st.write("---")
    if display_inventory:
        counts = Counter(display_inventory)
        for item, cnt in counts.items():
            st.write(f"{item} x {cnt} (판매가: {price_map.get(item,'N/A')} 코인)")
    else:
        st.info("인벤토리가 비어 있습니다.")
    st.write("---")
    st.markdown("##### 🛒 구매 아이템")
    for item, cnt in st.session_state.items.items():
        if cnt>0:
            st.write(f"{item} x {cnt}")

# ================= 🏪 상점 =================
with col3:
    st.subheader("🏪 상점")
    open_shop = st.checkbox("상점 열기", value=st.session_state.shop_open)
    st.session_state.shop_open = open_shop

st.divider()
if st.session_state.shop_open:
    st.subheader("🛒 아이템 구매")
    shop_cols = st.columns(2)
    for i,(item,data) in enumerate(shop_items.items()):
        with shop_cols[i%2]:
            st.write(f"{item} ({data['price']} 코인)")
            st.caption(data["desc"])
            if st.button(f"구매 {item}", key=f"buy_{item}"):
                if st.session_state.coin >= data["price"]:
                    st.session_state.coin -= data["price"]
                    st.session_state.items[item] += 1
                    st.success(f"{item} 1개 구매 완료!")
                else:
                    st.error("코인 부족!")

    st.markdown("---")
    st.subheader("💰 판매")
    if st.session_state.inventory:
        selected = st.multiselect("판매할 아이템 선택", st.session_state.inventory,
                                  format_func=lambda x: f"{x} ({price_map.get(x,'N/A')} 코인)")
        if st.button("판매 선택 아이템"):
            total = 0
            for item in selected:
                total += price_map.get(item,0)
                st.session_state.inventory.remove(item)
                st.session_state.coin += price_map.get(item,0)
            if total>0:
                st.success(f"{len(selected)}개 판매 완료! +{total} 코인")
    else:
        st.warning("판매할 아이템이 없습니다.")

# ================= ⚡ 합성 =================
st.subheader("⚡ 물고기 합성")
counts = Counter(st.session_state.inventory)
fusion_candidates = [f for f in fusion_map.keys() if counts.get(f,0)>=2]
if fusion_candidates:
    sel = st.selectbox("합성할 물고기 선택", fusion_candidates)
    if st.button("합성하기"):
        if counts.get(sel,0)>=2:
            st.session_state.inventory.remove(sel)
            st.session_state.inventory.remove(sel)
            if random.choice([True,False]):
                result = fusion_map[sel]
                catch_fish(result)
                st.balloons()
                st.success(f"합성 성공! {sel} 2마리 → {result} 1마리")
            else:
                st.error(f"합성 실패! {sel} 2마리 소모")
else:
    st.info("합성 가능한 물고기가 없습니다. (2마리 필요)")

# ================= 📚 도감 =================
st.subheader("📚 물고기 도감")
cols = st.columns(5)
for i, fish in enumerate(fish_list):
    with cols[i%5]:
        status = "✔ 발견" if fish in st.session_state.fishbook else "✖ 미발견"
        st.write(f"{fish} ({status})")

st.markdown("##### 💎 특수 아이템")
special_items = ["오래된 지도 조각"]
cols_special = st.columns(5)
for i,item in enumerate(special_items):
    with cols_special[i%5]:
        status = "✔ 발견" if item in st.session_state.fishbook else "✖ 미발견"
        st.write(f"{item} ({status})")

st.markdown("##### ✨ 합성 물고기")
fuse_cols = st.columns(5)
for i,(base,fused) in enumerate(fusion_map.items()):
    with fuse_cols[i%5]:
        status = "✔ 발견" if fused in st.session_state.fishbook else "✖ 미발견"
        st.write(f"{fused} ({status})")

st.write("---")
st.write(f"💰 최종 코인: {st.session_state.coin}")
