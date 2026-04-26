import streamlit as st
import json
from auth import init_user_db, register_user, login_user
import base64
import os
import mimetypes
import random
import datetime
import pandas as pd

SIN_COLORS = {
    "분노": "#FF4B4B",
    "색욕": "#FF8C00",
    "나태": "#FFD700",
    "탐식": "#4CAF50",
    "우울": "#00BFFF",
    "오만": "#4169E1",
    "질투": "#9C27B0"
}

init_user_db()

@st.cache_data
def load_affiliation_data():
    try:
        df = pd.read_excel("data/소속 죄악.xlsx")
        return df
    except Exception as e:
        st.error(f"엑셀 파일을 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()
    
@st.cache_data
def load_questions():
    with open("data/questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions_data = load_questions()

if "logged_in" not in st.session_state:
    if st.query_params.get("logged_in") == "true":
        st.session_state.logged_in = True
        st.session_state.user_name = st.query_params.get("user_name", "사용자")
    else:
        st.session_state.logged_in = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False        
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "test_started" not in st.session_state:
    st.session_state.test_started = False
def get_result_char_html(result_name, char_num, flip=False, angle=0, width_pct=100, margin_top=0):
    char_path = f"images/ch{result_name}{char_num}.png"
    encoded_string = get_image_base64(char_path)
    
    if not encoded_string: return ""
    
    transform_css = f"rotate({angle}deg)"
    if flip:
        transform_css += " scaleX(-1)"
        
    return f'''
    <div style="text-align: center; margin-top: {margin_top}px;">
        <img src="{encoded_string}" 
             style="width: {width_pct}%; 
                    transform: {transform_css}; 
                    drop-shadow: 2px 4px 6px rgba(0,0,0,0.5);">
    </div>
    '''

def load_history(user_id):
    path = f"data/history_{user_id}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(user_id, record):
    os.makedirs("data", exist_ok=True)
    history = load_history(user_id)
    history.append(record)
    with open(f"data/history_{user_id}.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_result_logo_html(result_name):
    logo_path = f"images/{result_name}.png"
    encoded_string = get_image_base64(logo_path)
    
    if not encoded_string: return ""
    
    return f'<img src="{encoded_string}" style="height: 1.5em; vertical-align: middle; margin-right: 10px;">'

def get_sin_icon_html(sin_name, skill_num):
    icon_path = f"images/{sin_name}{skill_num}.png"
    encoded_string = get_image_base64(icon_path)
    
    if not encoded_string: return ""
    
    return f'<img src="{encoded_string}" style="height: 1.1em; vertical-align: middle; margin-right: 8px;">'
    
def set_result_background(result_name, apply_blur=True):
    bg_path = f"images/{result_name}배경.webp"
    encoded_string = get_image_base64(bg_path)
    
    if not encoded_string: return

    blur_css = "filter: blur(8px) brightness(0.6);" if apply_blur else "filter: brightness(0.6);"
    
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] > .main {{
            background-color: transparent !important;
            position: relative;
            z-index: 1;
        }}
        [data-testid="stHeader"] {{
            background: transparent !important;
        }}
        
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            background-image: url("{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            position: fixed;
            top: -5%;
            left: -5%;
            width: 110vw;
            height: 110vh;
            z-index: 0;
            {blur_css}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def get_image_base64(image_path):
    if not os.path.exists(image_path):
        st.warning(f"이미지 없음: {image_path}")
        return None
    
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None: mime_type = "image/png"
        
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:{mime_type};base64,{encoded}"

def set_background(image_path, apply_blur=True):
    if not os.path.exists(image_path):
        st.warning(f"배경 이미지 없음: {image_path} 경로를 확인해주세요!")
        return 
        
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/png" 
        
    with open(image_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
        
    blur_css = "filter: blur(8px) brightness(0.6);" if apply_blur else "filter: brightness(0.6);"
    
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] > .main {{
            background-color: transparent !important;
            position: relative;
            z-index: 1;
        }}
        [data-testid="stHeader"] {{
            background: transparent !important;
        }}
        
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            background-image: url("data:{mime_type};base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            position: fixed;
            top: -5%;
            left: -5%;
            width: 110vw;
            height: 110vh;
            z-index: 0;
            {blur_css}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("""
    <style>
    .stRadio p, .stRadio label {
        color: white !important;
        text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000 !important;
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)

def get_char_html(img_path, flip=False, angle=0, width_pct=100, margin_top=0):
    if not os.path.exists(img_path):
        return ""
    
    mime_type, _ = mimetypes.guess_type(img_path)
    if mime_type is None: mime_type = "image/png"
        
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    
    transform_css = f"rotate({angle}deg)"
    if flip:
        transform_css += " scaleX(-1)"
        
    return f'''
    <div style="text-align: center; margin-top: {margin_top}px;">
        <img src="data:{mime_type};base64,{encoded}" 
             style="width: {width_pct}%; 
                    transform: {transform_css}; 
                    drop-shadow: 2px 4px 6px rgba(0,0,0,0.5);">
    </div>
    '''
def calculate_results():
    sin_stats = {sin: {"score": 0, "count": 0} for sin in ["분노", "색욕", "나태", "탐식", "우울", "오만", "질투"]}
    faction_stats = {"손가락": 0, "날개": 0}
    
    for ans in st.session_state.answers:
        scores_dict = ans.get("scores", {}) 
        for attr, score in scores_dict.items():
            if attr in ["손가락", "날개"]:
                faction_stats[attr] += score
            elif attr in sin_stats:
                sin_stats[attr]["score"] += score
                sin_stats[attr]["count"] += 1

    total_sin_score = sum(item["score"] for item in sin_stats.values())
    if total_sin_score == 0: total_sin_score = 1 # 0으로 나누기 방지
    
    user_pct = {sin: (data["score"] / total_sin_score) * 100 for sin, data in sin_stats.items()}
    
    total_faction_score = faction_stats["손가락"] + faction_stats["날개"]
    preferred_faction = "손가락" if faction_stats["손가락"] >= faction_stats["날개"] else "날개"
    
    faction_strength = 0
    if total_faction_score > 0:
        faction_strength = max(faction_stats["손가락"], faction_stats["날개"]) / total_faction_score

    df = load_affiliation_data()
    best_affiliation = "도시의 유랑자"
    min_distance = float('inf')
    
    sins = ["분노", "색욕", "나태", "탐식", "우울", "오만", "질투"]
    
    if not df.empty:
        for index, row in df.iterrows():
            affiliation_name = row.get('겹치는 단어 (키워드)', '')
            row_faction = row.get('소속', '')
            
            distance = 0
            for sin in sins:
                col_name = f"{sin}(%)"
                if col_name in row:
                    row_val = row[col_name]
                    if isinstance(row_val, str):
                        row_val = float(row_val.replace('%', '').strip())
                    elif pd.isna(row_val):
                        row_val = 0.0
                    elif row_val <= 1.0 and row_val > 0: 
                        row_val *= 100
                    distance += abs(user_pct[sin] - row_val)
            
            if str(row_faction).strip() == preferred_faction:
                distance -= (30 * faction_strength)
                
            if distance < min_distance:
                min_distance = distance
                best_affiliation = affiliation_name

    sorted_sins = sorted(
        sin_stats.items(), 
        key=lambda x: (x[1]["score"], x[1]["count"]), 
        reverse=True
    )
    
    top_3 = [item[0] for item in sorted_sins[:3]]
    while len(top_3) < 3:
        top_3.append("기본 공격")

    return best_affiliation, top_3[2], top_3[1], top_3[0], sorted_sins

if not st.session_state.logged_in:
    set_background("images/림버스.webp", apply_blur=True)
    if not st.session_state.show_login:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:  
            st.markdown(
                """
                <h1 style="text-align: center; color: white; text-shadow: -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000;">
                도시 생존 성향 테스트
                </h1>
                <p style="text-align: center; color: white; text-shadow: 1px 1px 2px #000;">
                뒷골목부터 둥지까지, 당신은 어느 곳에 어울리는 사람일까요?
                <p style="text-align: center; color: white; text-shadow: 1px 1px 2px #000;">
                2021204045 이성민
                </p>
                """,
                unsafe_allow_html=True,
                
            )

            if st.button("로그인하고 테스트 시작하기", type="primary", use_container_width=True):
                st.session_state.show_login = True
                st.rerun()
            
            pm_logo_b64 = get_image_base64("images/프문.webp")
            l1_logo = get_image_base64("images/로보토미.webp")
            l2_logo = get_image_base64("images/라오루.webp")
            l3_logo = get_image_base64("images/limbus_logo.jpg")

            pm_logo_html = f'<div style="margin-top: 15px;"><img src="{pm_logo_b64}" style="width: 150px; drop-shadow: 2px 2px 4px rgba(0,0,0,0.8);"></div>' if pm_logo_b64 else ""
            l1_logo_html = f'<div style="margin-top: 15px;"><img src="{l1_logo}" style="width: 150px; drop-shadow: 2px 2px 4px rgba(0,0,0,0.8);"></div>' if pm_logo_b64 else ""
            l2_logo_html = f'<div style="margin-top: 15px;"><img src="{l2_logo}" style="width: 150px; drop-shadow: 2px 2px 4px rgba(0,0,0,0.8);"></div>' if pm_logo_b64 else ""
            l3_logo_html = f'<div style="margin-top: 15px;"><img src="{l3_logo}" style="width: 150px; drop-shadow: 2px 2px 4px rgba(0,0,0,0.8);"></div>' if pm_logo_b64 else ""

            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 30px;">
                    <p style="color: rgba(255, 255, 255, 0.8); text-shadow: 1px 1px 2px #000; font-size: 0.85em; margin-bottom: 5px;">
                    본 심리테스트는 '프로젝트문' 게임사의 도시 세계관(로보토미 코퍼레이션, 라이브러리 오브 루이나, 림버스 컴퍼니)을 바탕으로 만들어진 심리테스트입니다.
                    </p>
                    <p style="color: rgba(255, 255, 255, 0.8); text-shadow: 1px 1px 2px #000; font-size: 0.85em;">
                    본 심리테스트에서 사용된 모든 일러스트와 세계관의 저작권은 '프로젝트문'에 있음을 밝힙니다.
                    </p>
                    {pm_logo_html}
                    {l1_logo_html}
                    {l2_logo_html}
                    {l3_logo_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown("""
        <style>
        div[data-testid="stTabs"] button p, 
        div[data-testid="stTextInput"] label p {
            color: black !important;
            text-shadow: 
                -1px -1px 0 #FFFFFF,  
                 1px -1px 0 #FFFFFF,
                -1px  1px 0 #FFFFFF,
                 1px  1px 0 #FFFFFF !important;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

        col_L, col_C, col_R = st.columns([1, 2, 1])
        with col_C:
            st.markdown("<h2 style='color: black; text-align: center; text-shadow: -1.5px -1.5px 0 #FFF, 1.5px -1.5px 0 #FFF, -1.5px 1.5px 0 #FFF, 1.5px 1.5px 0 #FFF;'>로그인 / 회원가입</h2>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["로그인", "회원가입"])
            with tab1:
                login_id = st.text_input("아이디", key="login_id")
                login_pw = st.text_input("비밀번호", type="password", key="login_pw")
                if st.button("로그인", use_container_width=True):
                    success, user_name = login_user(login_id, login_pw)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_id = login_id
                        st.session_state.user_name = user_name
                        
                        st.query_params["logged_in"] = "true"
                        st.query_params["user_id"] = login_id
                        st.query_params["user_name"] = user_name
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 틀렸습니다.")
                        
            with tab2:
                reg_id = st.text_input("아이디 설정", key="reg_id")
                reg_pw = st.text_input("비밀번호 설정", type="password", key="reg_pw")
                reg_name = st.text_input("이름(또는 닉네임)", key="reg_name")
                if st.button("가입하기", use_container_width=True):
                    res, msg = register_user(reg_id, reg_pw, reg_name)
                    if res: st.success(msg)
                    else: st.error(msg)
            
            st.write("")
            if st.button("← 처음 화면으로 돌아가기", use_container_width=True):
                st.session_state.show_login = False
                st.rerun()
else:
    col1, col2, col3 = st.columns([6, 2, 2])
    with col1:
        st.markdown(f"""
        <h3 style='color: white; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'>
        {st.session_state.user_name}님, 환영합니다!
        </h3>
        """, unsafe_allow_html=True)
        
    with col2:
        if st.button("히스토리", use_container_width=True):
            st.session_state.show_history = not st.session_state.get("show_history", False)
            st.rerun()
            
    with col3:
        if st.button("로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.test_started = False
            st.session_state.show_login = False
            st.session_state.show_history = False
            st.session_state.user_name = None
            st.session_state.current_q = 0
            st.session_state.answers = []
            st.session_state.result_saved = False
            st.query_params.clear()
            st.rerun()
            
    st.divider()
    total_q = len(questions_data)

    if st.session_state.get("show_history", False):
        set_background("images/림버스.webp", apply_blur=True)
        st.markdown("<h2 style='color: white; text-align: center; text-shadow: 2px 2px 4px #000;'>나의 테스트 기록</h2>", unsafe_allow_html=True)
        st.markdown("""
        <style>
        [data-testid="stExpander"] summary p {
            color: black !important;
            text-shadow: -1.5px -1.5px 0 #FFF, 1.5px -1.5px 0 #FFF, -1.5px 1.5px 0 #FFF, 1.5px 1.5px 0 #FFF !important;
            font-weight: bold !important;
            font-size: 1.05em !important;
        }
        [data-testid="stExpander"] summary svg {
            color: white !important;
            fill: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        history_data = load_history(st.session_state.user_id)
        if not history_data:
            st.info("아직 저장된 테스트 결과가 없습니다. 테스트를 먼저 진행해주세요!")
        else:
            for record in reversed(history_data):
                with st.expander(f"{record['time']} - {record['affiliation']}"):
                    c_color = SIN_COLORS.get(record['skill_3'], "#FFFFFF")
                    logo_icon = get_result_logo_html(record['affiliation'])
                    
                    st.markdown(f"""
                    <div style="padding: 15px; border-radius: 8px; border: 2px solid {c_color}; background: rgba(0,0,0,0.6); text-align: center;">
                        <h2 style="color: white; margin: 0; text-shadow: 2px 2px 4px #000;">{logo_icon} {record['affiliation']}</h2>
                        <p style="color: #ddd; margin-top: 15px; font-weight: bold; text-shadow: 1px 1px 2px #000;">
                            1스킬: <span style="color:{SIN_COLORS.get(record['skill_1'])}">{record['skill_1']}</span> | 
                            2스킬: <span style="color:{SIN_COLORS.get(record['skill_2'])}">{record['skill_2']}</span> | 
                            3스킬: <span style="color:{SIN_COLORS.get(record['skill_3'])}">{record['skill_3']}</span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        st.write("")
        if st.button("← 퀴즈 화면으로 돌아가기"):
            st.session_state.show_history = False
            st.rerun()
    elif not st.session_state.test_started:
        set_background("images/림버스.webp", apply_blur=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:    
            st.markdown(
                """
                <h1 style="text-align: center; color: white; text-shadow: -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000;">
                도시 생존 성향 테스트
                </h1>
                <p style="text-align: center; color: white; text-shadow: 1px 1px 2px #000;">
                뒷골목부터 둥지까지, 당신은 어느 곳에 어울리는 사람일까요?
                <p style="text-align: center; color: white; text-shadow: 1px 1px 2px #000;">
                2021204045 이성민
                </p>
                """,
                unsafe_allow_html=True,
                
            )
            if st.button("테스트 시작하기", type="primary", use_container_width=True):
                st.session_state.test_started = True
                st.rerun()

            pm_logo_b64 = get_image_base64("images/프문.webp")
            l1_logo = get_image_base64("images/로보토미.webp")
            l2_logo = get_image_base64("images/라오루.webp")
            l3_logo = get_image_base64("images/limbus_logo.jpg")

            pm_logo_html = f'<div style="margin-top: 15px;"><img src="{pm_logo_b64}" style="width: 150px; drop-shadow: 2px 2px 4px rgba(0,0,0,0.8);"></div>' if pm_logo_b64 else ""
            l1_logo_html = f'<div style="margin-top: 15px;"><img src="{l1_logo}" style="width: 150px; drop-shadow: 2px 2px 4px rgba(0,0,0,0.8);"></div>' if pm_logo_b64 else ""
            l2_logo_html = f'<div style="margin-top: 15px;"><img src="{l2_logo}" style="width: 150px; drop-shadow: 2px 2px 4px rgba(0,0,0,0.8);"></div>' if pm_logo_b64 else ""
            l3_logo_html = f'<div style="margin-top: 15px;"><img src="{l3_logo}" style="width: 150px; drop-shadow: 2px 2px 4px rgba(0,0,0,0.8);"></div>' if pm_logo_b64 else ""

            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 30px;">
                    <p style="color: rgba(255, 255, 255, 0.8); text-shadow: 1px 1px 2px #000; font-size: 0.85em; margin-bottom: 5px;">
                    본 심리테스트는 '프로젝트문' 게임사의 도시 세계관(로보토미 코퍼레이션, 라이브러리 오브 루이나, 림버스 컴퍼니)을 바탕으로 만들어진 심리테스트입니다.
                    </p>
                    <p style="color: rgba(255, 255, 255, 0.8); text-shadow: 1px 1px 2px #000; font-size: 0.85em;">
                    본 심리테스트에서 사용된 모든 일러스트와 세계관의 저작권은 '프로젝트문'에 있음을 밝힙니다.
                    </p>
                    {pm_logo_html}
                    {l1_logo_html}
                    {l2_logo_html}
                    {l3_logo_html}
                </div>
                """,
                unsafe_allow_html=True,
            )


    elif st.session_state.current_q < total_q:
        current_data = questions_data[st.session_state.current_q]
        
        bg_path = f"images/bg_q{st.session_state.current_q}.webp"
        set_background(bg_path, apply_blur=True)
        
        rng = random.Random(st.session_state.current_q)
        char_paths = [
            f"images/ch{st.session_state.current_q}-1.png",
            f"images/ch{st.session_state.current_q}-2.png"
        ]
        rng.shuffle(char_paths)
        
        col_left, col_center, col_right = st.columns([0.8, 3, 0.8])
        
        with col_left:
            angle_left = rng.randint(-35, 35)
            size_left = rng.randint(90, 130)  
            push_down_left = rng.randint(40, 250) 
            st.markdown(get_char_html(char_paths[0], flip=False, angle=angle_left, width_pct=size_left, margin_top=push_down_left), unsafe_allow_html=True)
            
        with col_right:
            angle_right = rng.randint(-35, 35)
            size_right = rng.randint(90, 130)
            push_down_right = rng.randint(40, 250)
            st.markdown(get_char_html(char_paths[1], flip=True, angle=angle_right, width_pct=size_right, margin_top=push_down_right), unsafe_allow_html=True)
            
        with col_center:
            progress = st.session_state.current_q / total_q
            st.markdown(f"""
            <p style='color: white; font-weight: bold; margin-bottom: 5px; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'>
            진행도: {st.session_state.current_q + 1} / {total_q}
            </p>
            """, unsafe_allow_html=True)
            st.progress(progress)
            
            st.markdown(f"""
            <h3 style='color: white; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'>
            Q{st.session_state.current_q + 1}. {current_data.get('question', '')}
            </h3>
            """, unsafe_allow_html=True)
            
            st.write("") 
            
            btn_col1, btn_col2 = st.columns(2)
            
            if "options" in current_data and len(current_data["options"]) > 0:
                option_texts = [opt["text"] for opt in current_data["options"]]
                user_choice = st.radio("당신의 선택은?", options=option_texts, index=None, key=f"q_{st.session_state.current_q}")
                
                st.write("")
                with btn_col1:
                    if st.session_state.current_q > 0:
                        if st.button("이전 문제", use_container_width=True):
                            st.session_state.current_q -= 1
                            if len(st.session_state.answers) > st.session_state.current_q:
                                st.session_state.answers.pop()
                            st.rerun()

                with btn_col2:
                    if user_choice is not None:
                        if st.button("다음 문제" if st.session_state.current_q < total_q - 1 else "결과 확인", type="primary", use_container_width=True):
                            selected_option = next(item for item in current_data["options"] if item["text"] == user_choice)
                            st.session_state.answers.append(selected_option)
                            st.session_state.current_q += 1
                            st.rerun()
            else:
                st.write("") 
                with btn_col1:
                    if st.session_state.current_q > 0:
                        if st.button("이전 문제", use_container_width=True):
                            st.session_state.current_q -= 1
                            if len(st.session_state.answers) > st.session_state.current_q:
                                st.session_state.answers.pop()
                            st.rerun()

                with btn_col2:
                    if st.session_state.current_q < total_q - 1:
                        btn_text = "다음으로 넘어가기"
                        btn_type = "secondary"
                    else:
                        btn_text = "죄악을 직면하기"
                        btn_type = "primary"
                        
                    if st.button(btn_text, type=btn_type, use_container_width=True):
                        st.session_state.answers.append({"text": "스킵", "scores": {}})
                        st.session_state.current_q += 1
                        st.rerun()

    else:
        affiliation, skill_1, skill_2, skill_3, all_sorted_sins = calculate_results()
        if "result_saved" not in st.session_state:
            st.session_state.result_saved = False
            
        if not st.session_state.result_saved:
            now_str = datetime.datetime.now().strftime("%y년 %m월 %d일 %H시 %M분")
            record = {
                "time": now_str,
                "affiliation": affiliation,
                "skill_1": skill_1,
                "skill_2": skill_2,
                "skill_3": skill_3
            }
            save_history(st.session_state.user_id, record)
            st.session_state.result_saved = True

        set_result_background(affiliation, apply_blur=True)
        rng = random.Random(affiliation)
        
        col_left, col_center, col_right = st.columns([0.8, 3, 0.8])
        
        with col_left:
            angle_left = rng.randint(-35, 35)
            size_left = rng.randint(90, 130)
            push_down_left = rng.randint(40, 250)
            st.markdown(get_result_char_html(affiliation, 1, flip=False, angle=angle_left, width_pct=size_left, margin_top=push_down_left), unsafe_allow_html=True)
            
        with col_right:
            angle_right = rng.randint(-35, 35)
            size_right = rng.randint(90, 130)
            push_down_right = rng.randint(40, 250)
            st.markdown(get_result_char_html(affiliation, 2, flip=True, angle=angle_right, width_pct=size_right, margin_top=push_down_right), unsafe_allow_html=True)
            
        with col_center:
            st.markdown("""
            <h3 style='color: white; text-align: center; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000; margin-bottom: 15px;'>
            테스트가 완료되었습니다!
            </h3>
            <p style='color: white; font-weight: bold; margin-bottom: 5px; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'>
            진행도: 100%
            </p>
            """, unsafe_allow_html=True)
            st.progress(1.0)
            
            logo_html = get_result_logo_html(affiliation)
            core_color = SIN_COLORS.get(skill_3, "#FFFFFF")
            
            st.markdown(f"""
            <div style="padding: 20px; border-radius: 10px; background-color: rgba(30, 30, 35, 0.85); border: 2px solid {core_color}; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
                <h2 style="margin: 0; color: {core_color}; text-shadow: 1px 1px 2px #000;">당신과 어울리는 소속</h2>
                <h1 style="font-size: 3em; margin: 10px 0; color: white; text-shadow: 2px 2px 4px #000;">
                    {logo_html}{affiliation}
                </h1>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <h2 style='color: white; text-align: center; margin-bottom: 20px; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'>
            당신의 죄악 속성
            </h2>
            """, unsafe_allow_html=True)
            
            def make_skill_card(label, sin_name, skill_num):
                color = SIN_COLORS.get(sin_name, "#FFFFFF")
                icon_path = f"images/{sin_name}{skill_num}.png"
                icon_b64 = get_image_base64(icon_path)
                
                icon_html = f'<img src="{icon_b64}" style="height: 4em; margin: 15px 0; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));">' if icon_b64 else ""
                
                return f"""
                <div style="background-color: rgba(0, 0, 0, 0.7); border: 2px solid {color}; border-radius: 8px; padding: 15px 5px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.6); height: 100%;">
                    <div style="color: {color}; font-weight: bold; font-size: 1.1em; text-shadow: 1px 1px 2px #000;">{label}</div>
                    {icon_html}
                    <div style="color: {color}; font-size: 1.5em; font-weight: bold; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;">{sin_name}</div>
                </div>
                """

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(make_skill_card("1스킬", skill_1, 1), unsafe_allow_html=True)
            with col2:
                st.markdown(make_skill_card("2스킬", skill_2, 2), unsafe_allow_html=True)
            with col3:
                st.markdown(make_skill_card("3스킬", skill_3, 3), unsafe_allow_html=True)\
                
            st.markdown("""
            <style>
            [data-testid="stExpander"] summary {
                justify-content: center !important;
            }
            [data-testid="stExpander"] summary p {
                color: black !important;
                text-shadow: -1px -1px 0 #FFF, 1px -1px 0 #FFF, -1px 1px 0 #FFF, 1px 1px 0 #FFF !important;
                font-weight: bold !important;
                font-size: 1.1em !important;
            }
            [data-testid="stExpander"] summary svg {
                color: white !important;
                fill: white !important;
            }
            
            .icon-bg-wrapper {
                position: relative;
                width: 55px;
                height: 55px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 15px;
            }
            .icon-bg-wrapper img {
                position: absolute !important;
                top: 43% !important;
                left: 52% !important;
                transform: translate(-50%, -50%) !important;
                height: 4.5em !important;
                width: auto !important;
                margin: 0 !important;
                z-index: 0 !important;
                opacity: 0.9 !important;
            }
            .rank-number {
                position: relative;
                z-index: 1 !important;
                color: white;
                font-weight: bold;
                font-size: 1.1em;
                text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
            }
            </style>
            """, unsafe_allow_html=True)
            
            with st.expander("모든 죄악 순위 확인하기"):
                st.write("")
                for i, (sin_name, stats) in enumerate(all_sorted_sins, start=1):
                    color = SIN_COLORS.get(sin_name, "#FFFFFF")
                    
                    if i == 1:
                        skill_num = 3
                    elif i == 2:
                        skill_num = 2
                    else:
                        skill_num = 1
                        
                    icon_html = get_sin_icon_html(sin_name, skill_num)
                    
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 10px; padding: 10px; background: rgba(0,0,0,0.4); border-radius: 8px; border-left: 5px solid {color};">
                        <div class="icon-bg-wrapper">
                            {icon_html}
                            <span class="rank-number">{i}위</span>
                        </div>
                        <span style="color: {color}; font-weight: bold; font-size: 1.1em; text-shadow: 1px 1px 2px #000;">{sin_name}</span>
                    </div>
                    """, unsafe_allow_html=True)
            st.divider()

            st.markdown("<p style='text-align: center; color: #aaa; font-size: 0.9em;'>기록은 상단의 '히스토리'에 자동으로 보관됩니다.</p>", unsafe_allow_html=True)
            
            empty_col1, btn_col, empty_col2 = st.columns([1, 1, 1])
            with btn_col:
                if st.button("다시 테스트하기", use_container_width=True):
                    st.session_state.test_started = False
                    st.session_state.current_q = 0
                    st.session_state.answers = []
                    st.session_state.result_saved = False
                    st.rerun()