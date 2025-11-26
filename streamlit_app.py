# ================= 🧪 물고기 합성 및 지도 완성 섹션 =================

st.markdown("---")

# 🌟 3. 물고기 합성 로직
st.markdown("### 🧪 물고기 합성 (5마리 -> 대물)")
st.caption("인벤토리의 일반 물고기 5마리를 소모하여 더 비싼 **대물**로 합성합니다.")

fusion_options = [base for base, fused in fusion_map.items() if counts.get(base, 0) >= 5]

if fusion_options:
    fusion_col1, fusion_col2 = st.columns([2, 1])
    
    with fusion_col1:
        selected_fish_to_fuse = st.selectbox(
            "합성할 물고기 선택 (5마리 소모)",
            fusion_options,
            key="fusion_select"
        )
        max_fusions = counts.get(selected_fish_to_fuse, 0) // 5
        fused_fish_name = fusion_map[selected_fish_to_fuse]
        
        st.write(f"➡️ **결과:** **{fused_fish_name}** (판매가: {price_map.get(fused_fish_name, 'N/A'):,} 코인)")
        st.caption(f"최대 합성 가능: {max_fusions}회")

    with fusion_col2:
        fuse_qty = st.number_input(
            "합성 횟수", 
            min_value=1, 
            max_value=max_fusions, 
            value=min(1, max_fusions), 
            step=1, 
            key="fuse_qty"
        )

    if st.button(f"✨ {selected_fish_to_fuse} {fuse_qty*5}마리 합성하여 {fused_fish_name} {fuse_qty}개 제작", key="fuse_btn", type="secondary", disabled=max_fusions==0):
        total_fish_needed = fuse_qty * 5
        
        # 재료 소모
        for _ in range(total_fish_needed):
            st.session_state.inventory.remove(selected_fish_to_fuse)
        
        # 결과물 획득
        for _ in range(fuse_qty):
            catch_fish(fused_fish_name)
            
        st.success(f"🧪 합성 성공! **{fused_fish_name}** {fuse_qty}개 획득! (재료 {selected_fish_to_fuse} {total_fish_needed}마리 소모)")
        st.rerun()

else:
    st.info("합성할 물고기가 없습니다. (동일 물고기 5마리 필요)")

st.markdown("---")

# 🌟 4. 지도 조각 합성 로직
st.markdown("### 🗺️ 오래된 지도 완성")

map_piece_name = "오래된 지도 조각"
full_map_name = "완성된 오래된 지도"
current_map_pieces = counts.get(map_piece_name, 0)
can_complete_map = current_map_pieces >= MAP_PIECES_NEEDED

st.write(f"**필요 조각:** **{MAP_PIECES_NEEDED}개** (현재 보유: {current_map_pieces}개)")
st.write(f"➡️ **결과:** **{full_map_name}** (판매가: {price_map.get(full_map_name, 'N/A'):,} 코인)")

if st.button(f"🧭 지도 조각 {MAP_PIECES_NEEDED}개 합성하여 지도 완성", key="complete_map_btn", disabled=not can_complete_map):
    
    # 조각 소모
    for _ in range(MAP_PIECES_NEEDED):
        st.session_state.inventory.remove(map_piece_name)
    
    # 완성된 지도 획득
    catch_fish(full_map_name) 

    st.success(f"🎉 **{full_map_name}** 완성! 잃어버린 섬 해금을 위해 인벤토리에서 사용하세요.")
    st.rerun()

elif not can_complete_map and current_map_pieces > 0:
    st.warning(f"지도 조각이 {MAP_PIECES_NEEDED - current_map_pieces}개 더 필요합니다.")
    
# 잃어버린 섬 해금 버튼 (지도 완성 후 인벤토리에서 사용)
st.markdown("---")
if not st.session_state.lost_island_unlocked:
    if st.button("🔱 완성된 지도 사용 (잃어버린 섬 해금)", key="use_map_btn", disabled=full_map_name not in counts):
        if full_map_name in counts:
            check_for_map_completion() # 지도 사용 및 섬 해금 함수 호출
            st.success("🧭 잃어버린 섬 해금 완료! 낚시터에서 변경할 수 있습니다.")
            st.rerun()
        else:
            st.warning("먼저 '완성된 오래된 지도'를 만들어야 합니다.")

st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# ================= 5. 상태 표시 (사이드바) 및 RERUN 방지 =================
# Streamlit의 문제: 위젯의 값이 변경되면 전체 페이지 RERUN. 
# 하지만 이 게임은 버튼 클릭 시 즉시 RERUN해야 하므로, 위의 모든 로직이 완료된 후 이 부분을 실행합니다.
