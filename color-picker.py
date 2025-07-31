import streamlit as st
import numpy as np
from colorspacious import cspace_convert
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def rgb_to_lab(rgb):
    """RGB 값을 LAB 색 공간으로 변환"""
    # RGB 값을 0-1 범위로 정규화
    rgb_normalized = np.array(rgb) / 255.0
    # sRGB에서 CIE LAB으로 변환
    lab = cspace_convert(rgb_normalized, "sRGB1", "CIELab")
    return lab

def lab_to_rgb(lab):
    """LAB 값을 RGB 색 공간으로 변환"""
    # CIE LAB에서 sRGB로 변환
    rgb_normalized = cspace_convert(lab, "CIELab", "sRGB1")
    # 0-255 범위로 변환하고 클리핑
    rgb = np.clip(rgb_normalized * 255, 0, 255).astype(int)
    return rgb

def display_color_swatch(rgb_color, title):
    """색상 견본 표시"""
    fig, ax = plt.subplots(1, 1, figsize=(0.5, 0.5))
    
    # RGB 값을 0-1 범위로 정규화
    color_normalized = np.array(rgb_color) / 255.0
    
    # 색상 사각형 그리기
    rect = patches.Rectangle((0, 0), 1, 1, linewidth=1, 
                           edgecolor='black', facecolor=color_normalized)
    ax.add_patch(rect)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=5, pad=5)
    
    return fig

def main():
    st.set_page_config(page_title="RGB ↔ LAB 색상 변환기", layout="wide")
    
    st.title("RGB ↔ LAB 색상 변환기")
    
    # LAB → RGB 탭의 슬라이더 값을 위한 세션 상태 초기화
    if 'L_lab' not in st.session_state:
        st.session_state.L_lab = 50.0
    if 'a_lab' not in st.session_state:
        st.session_state.a_lab = 0.0
    if 'b_lab' not in st.session_state:
        st.session_state.b_lab = 0.0

    
    # 사이드바에서 변환 방향 선택
    # conversion_mode = st.sidebar.selectbox(
    #     "변환 방향을 선택하세요",
    #     ["RGB → LAB", "LAB → RGB"]
    # )
    tab1, tab2 = st.tabs(["RGB → LAB", "LAB → RGB"])
    
    
    with tab1:
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("RGB 입력")
            
            col11, col12 = st.columns(2)
            with col11:
                # 컬러 피커로 색상 선택
                color_picker = st.color_picker("색상을 선택하세요 (혹은 HEX코드/RBG 입력)", value="#FF0000")
            
                # hex를 RGB로 변환
                hex_color = color_picker.lstrip('#')
                rgb_from_picker = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            with col12:
                # RGB 값 수동 입력 옵션
                # st.write("또는 RGB 값을 직접 입력하세요:")
                
                col1_1, col1_2, col1_3 = st.columns(3)
                with col1_1:
                    r = st.number_input("R", min_value=0, max_value=255, value=rgb_from_picker[0])
                with col1_2:
                    g = st.number_input("G", min_value=0, max_value=255, value=rgb_from_picker[1])
                with col1_3:
                    b = st.number_input("B", min_value=0, max_value=255, value=rgb_from_picker[2])
                
                rgb_values = [r, g, b]
            
            # 선택된 색상 표시
            fig = display_color_swatch(rgb_values, f"RGB({r}, {g}, {b})")
            st.pyplot(fig)
            plt.close()


        with col2:
            st.subheader("→Lab* 변환 결과")
            
            try:
                # RGB를 LAB으로 변환
                lab_values = rgb_to_lab(rgb_values)
                L, a, b_lab = lab_values
                
                # 결과 표시
                col_l, col_a, col_b = st.columns(3)
                with col_l:
                    st.metric("L* (명도)", f"{L:.2f}", help="0(검정) ~ 100(흰색)")
                with col_a:
                    st.metric("a* (녹색-빨간색)", f"{a:.2f}", help="음수: 녹색, 양수: 빨간색")
                with col_b:
                    st.metric("b* (파란색-노란색)", f"{b_lab:.2f}", help="음수: 파란색, 양수: 노란색")
                
                # 상세 정보
                with st.expander("상세 정보"):
                    st.write(f"**원본 RGB:** ({r}, {g}, {b})")
                    st.write(f"**변환된 LAB:** L*={L:.3f}, a*={a:.3f}, b*={b_lab:.3f}")
                    st.write(f"**Hex 코드:** {color_picker}")
                    
                    # RGB→LAB 변환 주의사항
                    st.caption("참고: 모니터 색상과 실제 색차계 측정값은 조명 조건과 디스플레이 특성에 따라 차이가 날 수 있습니다.")
                
            except Exception as e:
                st.error(f"변환 중 오류가 발생했습니다: {str(e)}")

    with tab2:
        cola, colb = st.columns(2)
        with cola:
            st.subheader("Lab* 입력")
            
            col1_1, col1_2, col1_3 = st.columns(3)
            with col1_1:
                st.session_state.L_lab = st.slider("L*", min_value=0.0, max_value=100.0, step=0.01, key="L_lab")
            with col1_2:
                st.session_state.a_lab = st.slider("a*", min_value=-128.0, max_value=127.0, step=0.01, key="a_lab")
            with col1_3:
                st.session_state.b_lab = st.slider("b*", min_value=-128.0, max_value=127.0, step=0.01, key="b_lab")
            
            lab_values = [st.session_state.L_lab, st.session_state.a_lab, st.session_state.b_lab]
            
            #  st.info(f"입력된 LAB 값: L*={st.session_state.L_lab:.1f}, a*={st.session_state.a_lab:.1f}, b*={st.session_state.b_lab:.1f}")
            
        with colb:
            st.subheader("→RGB 변환 결과")
            
            try:
                # LAB을 RGB로 변환
                rgb_values = lab_to_rgb(lab_values)
                r, g, b = rgb_values
                
                # 결과 표시
                col_r, col_g, col_b = st.columns(3)
                with col_r:
                    st.metric("R (빨강)", f"{r}")
                with col_g:
                    st.metric("G (녹색)", f"{g}")
                with col_b:
                    st.metric("B (파랑)", f"{b}")
                
                # 변환된 색상 표시
                if all(0 <= val <= 255 for val in rgb_values):
                    fig = display_color_swatch(rgb_values, f"RGB({r}, {g}, {b})")
                    st.pyplot(fig)
                    plt.close()
                    
                    # Hex 코드 계산
                    hex_code = f"#{r:02x}{g:02x}{b:02x}".upper()
                    st.write(f"**Hex 코드:** {hex_code}")
                    
                    st.success("정상적인 RGB 범위 내 변환 완료")
                else:
                    st.error("색역 경고: 입력된 LAB 값이 sRGB 색역을 벗어납니다!")
                    st.warning("모니터에서 정확한 색상 재현이 불가능합니다. 색차계 측정값과 차이가 날 수 있습니다.")
                
                # 상세 정보
                with st.expander("상세 정보"):
                    st.write(f"**원본 LAB:** L*={L:.3f}, a*={a:.3f}, b*={b_lab:.3f}")
                    st.write(f"**변환된 RGB:** ({r}, {g}, {b})")
                    
                    # LAB→RGB 변환 주의사항
                    st.caption("참고: LAB 값이 sRGB 색역을 벗어나는 경우 색상이 클리핑되어 원본과 다를 수 있습니다.")
                
            except Exception as e:
                st.error(f"변환 중 오류가 발생했습니다: {str(e)}")
    
    # 정보 섹션
    st.markdown("---")

    # 주의사항 표시
    with st.expander("변환 시 주의사항", expanded=False):
        st.warning("""
        **색 공간 한계:**
        - RGB는 sRGB 색역에 제한되어 모든 LAB 색상을 표현할 수 없습니다
        - LAB → RGB 변환 시 색역을 벗어나는 경우 정확한 색상 재현이 불가능합니다
        """)
        
        st.info("""
        **색차계 vs 모니터 차이:**
        - 색차계는 물리적 색상 측정 (절대값), 모니터는 상대값입니다
        - 동일한 LAB 값이라도 실제 색상과 화면 표시가 다를 수 있습니다
        - 조명 조건(D65 표준광)과 관찰자 각도 차이로 인한 오차가 발생할 수 있습니다
        """)
        
        st.error("""
        **정확도 한계:**
        - 변환 과정에서 반올림 오차가 누적될 수 있습니다
        - 실무에서는 ΔE < 2 정도를 동일 색상으로 간주합니다
        - 광택/무광택, 메탈릭 등 표면 특성은 변환으로 재현 불가합니다
        """)
    
    
    # 실무 팁 추가
    with st.expander("실무 활용 팁"):
        col_tip1, col_tip2 = st.columns(2)
        
        with col_tip1:
            st.markdown("""
            **정확한 측정을 위해:**
            - 색차계와 모니터 정기적 캘리브레이션
            - 동일한 조명 환경에서 비교
            - 표면 상태(광택/무광택) 고려
            """)
        
        with col_tip2:
            st.markdown("""
            **허용 오차 기준:**
            - ΔE < 1: 전문가도 구분 어려움
            - ΔE < 2: 일반적으로 동일 색상
            - ΔE < 3.5: 육안으로 구분 가능
            """)
    
    with st.expander("색 공간에 대한 정보"):
        st.markdown("""
        **RGB 색 공간:**
        - R(빨강), G(녹색), B(파랑) 각각 0-255 범위
        - 디스플레이 및 디지털 이미지에서 주로 사용
        - sRGB 색역에 제한됨 (모든 색상 표현 불가)
        
        **CIE LAB 색 공간:**
        - L*: 명도 (0=검정, 100=흰색)
        - a*: 녹색(-) ↔ 빨간색(+) 축
        - b*: 파란색(-) ↔ 노란색(+) 축
        - 색차 측정 및 색상 분석에 주로 사용
        - 인간의 시각 인지와 더 일치하는 색 공간
        - RGB보다 넓은 색역을 가짐
        
        **중요:** 색 공간 간 변환은 이론적 계산이며, 실제 물리적 색상과는 차이가 있을 수 있습니다.
        """)

if __name__ == "__main__":
    # 필요한 패키지 설치 안내
    # st.sidebar.markdown("""
    # ### 필요한 패키지
    # ```bash
    # pip install streamlit colorspacious matplotlib numpy
    # ```
    # """)
    
    main()
