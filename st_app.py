import streamlit as st
import random

# 페이지 설정
st.set_page_config(page_title="졸라맨 판타지 RPG", page_icon="⚔️", layout="wide")

# 1. 게임 상태 초기화 (Session State)
if 'player' not in st.session_state:
    st.session_state.player = {
        'rank': 1,  # 1~5등급
        'base_hp': 100,
        'base_en': 50,
        'base_atk': 10,
        'base_control': 5,
        'weapon': "손짓",
        'affinity': {'life': 0, 'light': 0, 'dark': 0, 'cosmos': 0},
        'element': 'none', # fire, water, earth, air
        'sub_element': None,
        'final_element': None,
        'kills': 0,
        'slime_talks': 0,
        'location': '인간 지역 - 고대 마법 유적',
        'logs': ["의식이 눈을 뜬다. 손끝에 감기는 것은 무엇인가?"]
    }

player = st.session_state.player

# 2. 등급별 곱연산 배율 계산
RANK_MULTIPLIERS = {1: 1.0, 2: 2.5, 3: 10.0, 4: 50.0, 5: 1000.0}
mult = RANK_MULTIPLIERS[player['rank']]

max_hp = int(player['base_hp'] * mult)
max_en = int(player['base_en'] * mult)
atk = int(player['base_atk'] * mult)
control = int(player['base_control'] * mult)

# 3. 사이드바 (플레이어 스탯 및 상태)
st.sidebar.title("📊 캐릭터 정보")
st.sidebar.markdown(f"**현재 등급:** `{player['rank']}등급` (배율: x{mult})")
st.sidebar.markdown(f"**HP:** `{max_hp}` | **EN:** `{max_en}`")
st.sidebar.markdown(f"**출력(공격력):** `{atk}`")
st.sidebar.markdown(f"**제어력:** `{control}`")
st.sidebar.markdown(f"**장착 매개체:** `{player['weapon']}`")

element_display = player['final_element'] or player['sub_element'] or player['element']
st.sidebar.markdown(f"**현재 속성:** `{element_display}`")
st.sidebar.markdown(f"**현재 위치:** `{player['location']}`")

# 4. 메인 화면 & 2D 졸라맨 연출 (SVG 그래픽)
st.title("🗡️ 졸라맨 원소 판타지 RPG")

def get_stickman_svg(rank, element):
    # 속성별 오라 색상 설정
    color_map = {
        'none': '#FFFFFF', 'fire': '#FF4500', 'water': '#1E90FF', 
        'earth': '#8B4513', 'air': '#00FA9A', '태양의 신성염': '#FFD700',
        '심연의 흑염': '#800080', '불사조의 야성염': '#FF6347'
    }
    aura_color = color_map.get(element, '#FFFFFF')
    stroke_width = 3 + (rank * 1.5)
    
    return f"""
    <svg width="250" height="250" viewBox="0 0 200 200" style="background-color: #111; border-radius: 10px; display: block; margin: auto;">
        <!-- 오라 이펙트 -->
        <circle cx="100" cy="100" r="{40 + rank*8}" fill="none" stroke="{aura_color}" stroke-width="{rank*2}" opacity="0.6"/>
        <!-- 졸라맨 머리 -->
        <circle cx="100" cy="50" r="16" fill="none" stroke="#FFF" stroke-width="{stroke_width}"/>
        <!-- 몸통 -->
        <line x1="100" y1="66" x2="100" y2="120" stroke="#FFF" stroke-width="{stroke_width}"/>
        <!-- 팔 -->
        <line x1="100" y1="80" x2="60" y2="100" stroke="#FFF" stroke-width="{stroke_width}"/>
        <line x1="100" y1="80" x2="140" y2="70" stroke="#FFF" stroke-width="{stroke_width}"/>
        <!-- 다리 -->
        <line x1="100" y1="120" x2="70" y2="170" stroke="#FFF" stroke-width="{stroke_width}"/>
        <line x1="100" y1="120" x2="130" y2="170" stroke="#FFF" stroke-width="{stroke_width}"/>
    </svg>
    """

st.components.v1.html(get_stickman_svg(player['rank'], element_display), height=270)

# 5. 행동 및 탐험 선택지 (로그 업데이트 연동)
col1, col2 = st.columns(2)

def add_log(msg):
    player['logs'].append(msg)
    if len(player['logs']) > 6:
        player['logs'].pop(0)

with col1:
    st.subheader("🌲 주변 둘러보기 & 탐험")
    
    if st.button("고대 쇠검 쥐어보기 (검 매개체)"):
        player['weapon'] = "고대 쇠검"
        player['base_atk'] += 5
        add_log("날카로운 쇠검을 쥐자 검신을 따라 맑은 에너지가 서립니다.")
        st.rerun()

    if st.button("부서진 지팡이 조각에 마력 주입 (지팡이)"):
        player['weapon'] = "마력 지팡이"
        player['base_control'] += 3
        add_log("나무 지팡이 끝에서 원초적 마력 파동이 일렁입니다.")
        st.rerun()

    if st.button("주먹을 불끈 쥐기 (신체 격투)"):
        player['weapon'] = "신체 마력"
        player['base_hp'] += 20
        add_log("신체 전체의 마력이 불끈 솟아오릅니다.")
        st.rerun()

    if st.button("슬라임과 교감 시도하기"):
        player['affinity']['life'] += 5
        player['slime_talks'] += 1
        add_log("슬라임과 손끝을 맞대자 '생명의 신'의 기운이 감돕니다.")
        if player['slime_talks'] >= 3 and player['rank'] == 1:
            player['rank'] = 2
            add_log("✨ [승급] 몬스터 생태계와의 교감으로 2등급 중위 생명체로 진화했습니다!")
        st.rerun()

with col2:
    st.subheader("🔥 원소 파생 & 수련")
    
    # 4대 기본 속성 선택
    if player['element'] == 'none':
        st.write("마력을 수련해 속성을 깨우치세요:")
        if st.button("불(Fire) 속성 획득"):
            player['element'] = 'fire'
            add_log("손끝에서 뜨거운 화염 파동이 피어오릅니다.")
            st.rerun()
    
    # 제어력 기반 1차 파생
    elif player['sub_element'] is None and control >= 10:
        st.write("💡 제어력이 높아져 마법 분기가 열렸습니다!")
        if st.button("용암/열압 (파괴 특화)"):
            player['sub_element'] = "용암 파동"
            player['base_atk'] += 30
            add_log("불꽃이 묵직한 용암 형태로 압축됩니다.")
            st.rerun()
        if st.button("플라즈마/뇌전 (관통/속도 특화)"):
            player['sub_element'] = "플라즈마"
            player['base_control'] += 15
            add_log("불꽃이 날카로운 뇌전 전력 파동으로 변형됩니다.")
            st.rerun()

    # 생명/빛 기운 기반 최종 파생
    elif player['sub_element'] is not None and player['final_element'] is None and player['affinity']['life'] >= 15:
        st.write("🌟 '생명의 신' 기운이 강해져 최종 마법 진화가 가능합니다!")
        if st.button("불사조의 야성염 (최종 파생)"):
            player['final_element'] = "불사조의 야성염"
            player['base_hp'] += 200
            add_log("🔥 [최종 파생] 불사조의 야성염을 완성했습니다!")
            st.rerun()

    # 수련 및 전투
    if st.button("적 몬스터와 전투하기"):
        dmg = atk * random.randint(1, 3)
        player['kills'] += 1
        player['base_atk'] += 2
        player['base_control'] += 1
        add_log(f"⚔️ 적을 제압하여 {dmg}의 피해를 입히고 스탯이 상승했습니다.")
        st.rerun()

# 6. 하단 게임 진행 로그
st.divider()
st.subheader("📜 모험 로그")
for log in reversed(player['logs']):
    st.write(f"- {log}")
