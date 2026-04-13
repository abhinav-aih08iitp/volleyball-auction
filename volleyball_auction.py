import streamlit as st
import pandas as pd
import json
import os
import base64
import time
import threading
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- 1. PAGE CONFIGURATION & SERVER LOCK ---
st.set_page_config(page_title="Mega Volleyball Auction", layout="wide", page_icon="🏐")
st_autorefresh(interval=1500, limit=10000, key="data_refresh")

@st.cache_resource
def get_lock():
    return threading.Lock()
db_lock = get_lock()

DB_FILE = "auction_db.json"
TOTAL_PURSE = 50000
DISCORD_LINK = "https://discord.gg/ePnD2Qqkj"

# --- 2. THE ULTIMATE PLAYER LIST (NO STATS - ONLY ESSENTIALS) ---
DEFAULT_PLAYERS = [
    {"Name": "GOLU", "Photo": "golu.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 900},
    {"Name": "SIDHU", "Photo": "sidhu.jpg", "Role": "SETTER", "Base_Points": 2000},
    {"Name": "MITHU", "Photo": "mithu.jpg", "Role": "MIDDLE BLOCKER", "Base_Points": 2000},
    {"Name": "ABHISHEK", "Photo": "abhishek.jpg", "Role": "LIBERO", "Base_Points": 1600},
    {"Name": "ROHIT", "Photo": "rohit.jpg", "Role": "ALL ROUNDER", "Base_Points": 1600},
    {"Name": "YASH", "Photo": "yash.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 1000},
    {"Name": "SHASHWAT", "Photo": "shashwat.jpg", "Role": "RIGHT SIDE HITTER", "Base_Points": 1200},
    {"Name": "MOHIT", "Photo": "mohit.jpg", "Role": "LIBERO", "Base_Points": 1800},
    {"Name": "ABHINANDAN", "Photo": "abhinandan.jpg", "Role": "SETTER", "Base_Points": 500},
    {"Name": "RISHI", "Photo": "rishi.jpg", "Role": "LIBERO", "Base_Points": 1200},
    {"Name": "RAHIL", "Photo": "rahil.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 900},
    {"Name": "KISHU", "Photo": "kishu.jpg", "Role": "LIBERO", "Base_Points": 1100},
    {"Name": "KESHAV", "Photo": "keshav.jpg", "Role": "RIGHT SIDE HITTER", "Base_Points": 800},
    {"Name": "KUNAL", "Photo": "kunal.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 250},
    {"Name": "CHULBUL", "Photo": "chulbul.jpg", "Role": "SETTER", "Base_Points": 1400},
    {"Name": "PIYUSH", "Photo": "piyush.jpg", "Role": "ALL ROUNDER", "Base_Points": 2000},
    {"Name": "PIYUSH 1", "Photo": "piyush1.jpg", "Role": "SETTER", "Base_Points": 500},
    {"Name": "PIYUSH 2", "Photo": "piyush2.jpg", "Role": "SETTER", "Base_Points": 250},
    {"Name": "PANCHAM", "Photo": "pancham.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 800},
    {"Name": "ABHI", "Photo": "abhi.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 500},
    {"Name": "RISHU", "Photo": "rishu.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 700},
    {"Name": "RITIK", "Photo": "ritik.jpg", "Role": "LIBERO", "Base_Points": 1500},
    {"Name": "ANKUSH", "Photo": "ankush.jpg", "Role": "LIBERO", "Base_Points": 1600},
    {"Name": "AYUSH", "Photo": "ayush.jpg", "Role": "MIDDLE BLOCKER", "Base_Points": 1750},
    {"Name": "PRITHVI", "Photo": "prithvi.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 900},
    {"Name": "SHRESHTH", "Photo": "shreshth.jpg", "Role": "OUTSIDE HITTER", "Base_Points": 1000},
]

DEFAULT_USER_DATA = {"Masterji": {"password": "Mishraji041411", "team": "👑 ADMIN"}}

# --- 3. BACKGROUND & CSS (FIXED LAYOUT) ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

def set_background(image_file):
    b64 = get_base64(image_file)
    if b64:
        st.markdown(f"""
<style>
.stApp {{ background: linear-gradient(rgba(10, 15, 20, 0.85), rgba(10, 15, 20, 0.85)), url(data:image/webp;base64,{b64}); background-size: cover; background-position: center; background-attachment: fixed; }}
.big-title {{ text-align: center; font-size: 50px !important; font-weight: 900; color: #FFD700; text-transform: uppercase; text-shadow: 3px 3px 6px #000; }}
.player-card {{ background: rgba(20, 20, 20, 0.9); padding: 40px; border-radius: 25px; border: 2px solid #FFD700; backdrop-filter: blur(8px); box-shadow: 0 10px 40px rgba(255, 215, 0, 0.3); text-align: center; margin-bottom: 20px; }}
.photo-frame {{ width: 230px; height: 230px; border-radius: 50%; border: 6px solid #FFD700; box-shadow: 0 0 30px #FFD700; object-fit: cover; background: #111; margin: 10px auto; }}
.category-badge {{ background-color: #FF4500; color: white; padding: 8px 20px; border-radius: 12px; font-weight: bold; font-size: 20px; text-transform: uppercase; }}
.ticker-wrap {{ position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.9); color: #FFD700; padding: 12px; font-weight: bold; border-top: 2px solid #FFD700; z-index: 999; }}
</style>
        """, unsafe_allow_html=True)

set_background("volleyball.webp")

# --- 4. SECURE DATABASE LOGIC ---
def load_db():
    default_db = {
        "users": DEFAULT_USER_DATA, "players": DEFAULT_PLAYERS, "player_index": 0, "current_bid": 0, "current_team": "None", 
        "sold_data": [], "last_sold_trigger": False, "winner_name": "", "round_2": False, "last_bid_time": time.time(), 
        "passed_teams": [], "rtm_cards": {v["team"]: True for k, v in DEFAULT_USER_DATA.items() if k != "Masterji"}
    }
    if not os.path.exists(DB_FILE): return default_db
    for _ in range(5):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                for k, v in default_db.items():
                    if k not in data: data[k] = v
                return data
        except: time.sleep(0.1)
    return default_db

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

db = load_db()
USER_DATA, players = db["users"], db["players"]
teams = [v["team"] for k, v in USER_DATA.items() if k != "Masterji"]

# --- 5. LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user_role': None, 'team_name': None})

if not st.session_state['logged_in']:
    st.markdown("<h1 class='big-title'>🔐 Auction Arena Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.link_button("🎧 JOIN DISCORD LIVE WAR ROOM", DISCORD_LINK, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login"):
            st.markdown("### 🧑‍✈️ Captain / Masterji Login")
            uid, pwd = st.text_input("User ID"), st.text_input("Password", type="password")
            if st.form_submit_button("Enter Arena"):
                if uid in USER_DATA and USER_DATA[uid]["password"] == pwd:
                    st.session_state.update({'logged_in':True, 'user_role':uid, 'team_name':USER_DATA[uid]["team"]})
                    st.rerun()
                else: st.error("Wrong ID/Password")
        if st.button("👁️ WATCH LIVE AS GUEST", use_container_width=True):
            st.session_state.update({'logged_in':True, 'user_role':'viewer', 'team_name':'👤 LIVE AUDIENCE'})
            st.rerun()
    st.stop()

sold_names = [x["Player"].replace(" (RTM)", "").replace(" (Retained)", "") for x in db["sold_data"]]
while db["player_index"] < len(players) and players[db["player_index"]]["Name"] in sold_names:
    db["player_index"] += 1

# --- 6. SIDEBAR ---
spent = {t: sum(x["Final Points"] for x in db["sold_data"] if x["Sold To"] == t) for t in teams}
purses = {t: TOTAL_PURSE - spent.get(t, 0) for t in teams}

with st.sidebar:
    st.markdown(f"### {st.session_state['team_name']}")
    if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()
    st.write("---")
    st.markdown("### 🎙️ Live War Room")
    st.link_button("🎧 Join Discord Chat", DISCORD_LINK, use_container_width=True)
    st.write("---")
    st.markdown("### 📊 Budget War")
    if teams:
        fig = px.pie(values=list(purses.values()), names=list(purses.keys()), hole=0.6, color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    for t in teams: st.caption(f"{t}: {purses[t]} pts")

# --- 7. MAIN ARENA (FIXED HTML BUNDLE) ---
st.markdown(f"<p class='big-title'>🏆 AUCTION DASHBOARD 🏆</p>", unsafe_allow_html=True)
colA, colB, colC = st.columns([1,2,1])
with colB: st.link_button("🎧 JOIN DISCORD LIVE WAR ROOM", DISCORD_LINK, use_container_width=True)

if db["player_index"] >= len(players):
    st.success("AUCTION QUEUE COMPLETED!")
else:
    current_player = players[db["player_index"]]
    actual_base = current_player["Base_Points"] // 2 if db.get("round_2") else current_player["Base_Points"]
    
    # Auto-sell logic
    time_left = 20
    if db["current_team"] != "None":
        elapsed = time.time() - db.get("last_bid_time", time.time())
        time_left = max(0, 20 - int(elapsed))
        st.markdown(f"<h2 style='text-align: center; color: {'#FF4500' if time_left <= 5 else '#00FA9A'};'>⏳ AUTO-SELL IN: {time_left}s</h2>", unsafe_allow_html=True)
        if time_left == 0:
            with db_lock:
                fdb = load_db()
                if not any(p["Player"] == current_player["Name"] for p in fdb["sold_data"]) and fdb["current_team"] != "None":
                    fdb["sold_data"].append({"Player": current_player["Name"], "Sold To": fdb["current_team"], "Final Points": fdb["current_bid"]})
                    fdb.update({"winner_name":f"SOLD TO {fdb['current_team']}!", "last_sold_trigger":True, "player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None", "passed_teams":[], "last_bid_time":time.time()})
                    save_db(fdb)
            st.rerun()

    # --- THE FIXED CARD (ALL IN ONE HTML) ---
    col1, col2, col3 = st.columns([1,1.8,1])
    with col2:
        p_img_b64 = get_base64(current_player.get("Photo", "default.jpg"))
        photo_html = f'<img src="data:image/jpeg;base64,{p_img_b64}" class="photo-frame">' if p_img_b64 else '<div class="photo-frame" style="display:flex; align-items:center; justify-content:center; font-size:100px;">🏐</div>'
        
        st.markdown(f"""
        <div class="player-card">
            {photo_html}
            <br>
            <span class="category-badge">{current_player["Role"]}</span>
            <h1 style="color:#FFD700; margin-top:20px; font-size:55px; text-shadow: 2px 2px #000;">{current_player["Name"]}</h1>
            <h2 style="color:#00FA9A; font-weight:bold; letter-spacing:2px;">BASE: {actual_base} PTS</h2>
        </div>
        """, unsafe_allow_html=True)

    # Controls
    m1, m2, m3 = st.columns(3)
    m1.metric("Highest Bid", f"{db['current_bid']}")
    m2.metric("Highest Bidder", db["current_team"])
    m3.metric("Your Budget", purses.get(st.session_state['team_name'], "VIEWER"))

    if st.session_state['user_role'] not in ["Masterji", "viewer"]:
        me = st.session_state['team_name']
        nxt = db["current_bid"] + 100 if db["current_team"] != "None" else actual_base
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            if st.button(f"🚀 BID {nxt}", disabled=(purses.get(me, 0) < nxt or me in db["passed_teams"]), use_container_width=True, type="primary"):
                with db_lock:
                    fdb = load_db()
                    cur_nxt = fdb["current_bid"] + 100 if fdb["current_team"] != "None" else actual_base
                    fdb.update({"current_team":me, "current_bid":cur_nxt, "last_bid_time":time.time(), "passed_teams":[]})
                    save_db(fdb)
                st.rerun()
        with bc2:
            if st.button("❌ PASS", disabled=(me in db["passed_teams"] or me == db["current_team"]), use_container_width=True):
                with db_lock:
                    fdb = load_db(); fdb["passed_teams"].append(me); save_db(fdb)
                st.rerun()
        with bc3:
            can_rtm = db["rtm_cards"].get(me) and db["current_team"] not in ["None", me]
            if st.button("🃏 RTM CARD", disabled=not can_rtm, use_container_width=True):
                with db_lock:
                    fdb = load_db()
                    fdb["sold_data"].append({"Player": current_player["Name"] + " (RTM)", "Sold To": me, "Final Points": fdb["current_bid"]})
                    fdb["rtm_cards"][me] = False
                    fdb.update({"winner_name":f"RTM USED!", "last_sold_trigger":True, "player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None"})
                    save_db(fdb)
                st.rerun()

# --- 8. MASTERJI CONTROLS ---
if st.session_state['user_role'] == "Masterji":
    with st.expander("🛠️ Masterji Control Panel", expanded=False):
        st.markdown("#### ⚡ Admin Actions")
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            if db["player_index"] < len(players) and st.button("🔨 FORCE SOLD"):
                with db_lock:
                    fdb = load_db()
                    fdb["sold_data"].append({"Player": current_player["Name"], "Sold To": fdb["current_team"], "Final Points": fdb["current_bid"]})
                    fdb.update({"player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None", "passed_teams":[]})
                    save_db(fdb); st.rerun()
        with ac2:
            if db["player_index"] < len(players) and st.button("❌ FORCE UNSOLD"):
                with db_lock:
                    fdb = load_db()
                    fdb["sold_data"].append({"Player": current_player["Name"], "Sold To": "UNSOLD", "Final Points": 0})
                    fdb.update({"player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None", "passed_teams":[]})
                    save_db(fdb); st.rerun()
        with ac3:
            if st.button("🔄 RESET DATABASE"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.rerun()

        st.write("---")
        st.markdown("#### 🎯 Call Player (Manual Override)")
        avail = [p["Name"] for p in players if p["Name"] not in sold_names]
        if avail:
            call = st.selectbox("Select Player", avail)
            if st.button("📢 Bring to Stage"):
                idx = next(i for i, p in enumerate(players) if p["Name"] == call)
                with db_lock:
                    fdb = load_db(); fdb.update({"player_index":idx, "current_bid":0, "current_team":"None", "passed_teams":[]})
                    save_db(fdb); st.rerun()
        
        st.write("---")
        st.markdown("#### ⚙️ Manage Teams")
        tm1, tm2 = st.columns(2)
        with tm1:
            with st.form("add_team"):
                n_id, n_pass, n_name = st.text_input("ID"), st.text_input("Pass"), st.text_input("Name")
                if st.form_submit_button("Add Team"):
                    with db_lock:
                        fdb = load_db(); fdb["users"][n_id] = {"password":n_pass, "team":n_name}; fdb["rtm_cards"][n_name]=True
                        save_db(fdb); st.rerun()
        with tm2:
            with st.form("rem_team"):
                r_id = st.selectbox("Remove", [k for k in db["users"] if k != "Masterji"])
                if st.form_submit_button("Remove Team", disabled=not [k for k in db["users"] if k != "Masterji"]):
                    with db_lock:
                        fdb = load_db(); del fdb["users"][r_id]; save_db(fdb); st.rerun()

# --- 9. SQUADS ---
st.write("---")
if teams:
    tabs = st.tabs(teams)
    for i, t in enumerate(teams):
        with tabs[i]:
            team_players = [x for x in db["sold_data"] if x["Sold To"] == t]
            st.dataframe(pd.DataFrame(team_players), use_container_width=True)
