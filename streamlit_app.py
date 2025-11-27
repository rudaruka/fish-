# ================= 🔧 떡밥 제작 및 아이템 합성 섹션 =================
st.divider()
st.markdown('<div class="game-section">', unsafe_allow_html=True)
st.subheader("🧵 떡밥 제작 및 아이템 합성")
st.caption(f"물고기 **{BAIT_CRAFT_FISH_NEEDED}마리** = 떡밥 1개 (합성, 괴수, 코믹, 지도 조각 제외)")
st.markdown("---")

counts = Counter(st.session_state.inventory)

# --- 1. 떡밥 제작 (안정화 로직 적용) ---
st.markdown("### 🎣 떡밥 제작")

# 떡밥 제작에 사용 가능한 물고기 목록 정의
craft_exclusion = set(FUSED_FISH) | set(SPECIAL_ITEMS) | set(MONSTER_FISH) | set(COMIC_FISH)
craft_able_fish_list = [f for f in NORMAL_FISH if f not in craft_exclusion] 

total_craftable_fish = sum(counts.get(f, 0) for f in craft_able_fish_list)
max_bait_to_craft = total_craftable_fish // BAIT_CRAFT_FISH_NEEDED

st.write(f"**제작 가능 물고기 총합:** {total_craftable_fish}마리")
st.write(f"**최대 제작 가능 떡밥:** **{max_bait_to_craft}개**")

if max_bait_to_craft > 0:
    craft_qty = st.number_input("제작할 떡밥 개수", min_value=1, max_value=max_bait_to_craft, value=min(1, max_bait_to_craft), step=1, key="craft_bait_qty")
    
    if st.button(f"✅ 떡밥 {craft_qty}개 제작", key="craft_bait_btn"):
        fish_needed = craft_qty * BAIT_CRAFT_FISH_NEEDED
        fish_to_consume = {}
        consumed_count = 0
        
        # 수량이 많은 순으로 정렬하여 소모
        sorted_inventory = sorted([
            (f, counts[f]) for f in craft_able_fish_list 
            if counts[f] > 0
        ], key=lambda item: item[1], reverse=True)
        
        for fish, qty in sorted_inventory:
            if consumed_count < fish_needed:
                consume = min(qty, fish_needed - consumed_count)
                fish_to_consume[fish] = consume
                consumed_count += consume

        if consumed_count == fish_needed:
            for fish, qty in fish_to_consume.items():
                for _ in range(qty):
                    st.session_state.inventory.remove(fish)
            
            st.session_state.bait += craft_qty
            st.success(f"떡밥 {craft_qty}개 제작 완료! (물고기 {fish_needed}마리 소모)")
            st.rerun()
        else:
            st.error("❗ 물고기 소모 로직 오류: 필요한 만큼의 물고기를 찾지 못했습니다.")
else:
    st.info("떡밥을 제작할 물고기가 부족합니다.")


st.markdown("---")

# --- 2. 물고기 합성 (일반 -> 대물) ---
st.markdown("### 🧪 물고기 합성 (5마리 -> 1마리)")
st.caption("일반 물고기 5마리를 모아 대물 물고기 1마리로 합성합니다.")

FUSION_COST = 5
fusible_base_fish = [
    fish for fish, fused in fusion_map.items()
]

# 합성 목록을 한 줄로 표시
fusion_options_display = " | ".join([
    f"**{base}** ({counts.get(base, 0)}개) -> **{fusion_map[base]}**"
    for base in fusible_base_fish
])
st.caption(f"합성 가능 품목: {fusion_options_display}")


# 합성할 물고기 선택
selected_base_fish = st.selectbox(
    "합성할 물고기 선택 (5개 필요)",
    options=["--- 선택 ---"] + fusible_base_fish,
    key="select_fusion_base"
)

if selected_base_fish != "--- 선택 ---":
    
    base_qty = counts.get(selected_base_fish, 0)
    
    # 최대 합성 가능 개수
    max_fusions = base_qty // FUSION_COST
    
    if max_fusions > 0:
        
        # 몇 개를 합성할지 결정
        fusion_qty = st.number_input(
            "제작할 대물 물고기 개수",
            min_value=1, 
            max_value=max_fusions, 
            value=min(1, max_fusions), 
            step=1, 
            key="fusion_qty_input"
        )
        
        fish_needed = fusion_qty * FUSION_COST
        fused_fish_name = fusion_map[selected_base_fish]
        
        st.write(f"**필요한 {selected_base_fish} 수량:** {fish_needed}개")
        st.write(f"**제작될 물고기:** {fused_fish_name} {fusion_qty}마리")

        if st.button(f"⚛️ {fused_fish_name} {fusion_qty}개 합성", key="do_fusion_btn", type="primary"):
            
            # 인벤토리에서 기본 물고기 소모
            for _ in range(fish_needed):
                st.session_state.inventory.remove(selected_base_fish)
                
            # 인벤토리에 합성 물고기 추가 및 도감 업데이트
            for _ in range(fusion_qty):
                catch_fish(fused_fish_name) # catch_fish 함수를 사용하여 인벤토리 추가 및 도감 업데이트
            
            st.success(f"🎉 **{fused_fish_name}** {fusion_qty}마리 합성 완료! ( {selected_base_fish} {fish_needed}개 소모)")
            st.rerun()

    else:
        st.info(f"현재 **{selected_base_fish}**가 {FUSION_COST}마리 미만으로 합성할 수 없습니다.")


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
    
    map_craft_qty = st.number_input(
        "제작할 완성 지도 개수",
        min_value=1,
        max_value=max_map_crafts,
        value=min(1, max_map_crafts),
        step=1,
        key="map_craft_qty_input"
    )
    
    pieces_needed = map_craft_qty * MAP_PIECE_COST

    if st.button(f"🧭 {full_map_name} {map_craft_qty}개 제작", key="do_map_craft_btn", type="secondary"):
        
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


# --- 8. 게임 초기화 섹션 (정리용 추가) ---
st.divider()
st.markdown('<div class="game-section" style="background-color: #f8d7da; border-color: #dc3545;">', unsafe_allow_html=True)
st.subheader("⚠️ 게임 데이터 초기화 (모든 진행 상황 삭제)")
st.caption("모든 코인, 물고기, 도감 및 낚싯대 레벨이 초기화됩니다. 이 작업은 되돌릴 수 없습니다.")
if st.button("🗑️ 모든 게임 데이터 초기화", key="reset_game_data_final", type="default"):
    reset_game_data() # 함수 호출로 초기화 및 새로고침
st.markdown('</div>', unsafe_allow_html=True)
