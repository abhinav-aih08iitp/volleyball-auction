import streamlit as st
import pandas as pd
import json
import os
import base64
import time
import threading
import plotly.express as px
import urllib.parse
from streamlit_autorefresh import st_autorefresh

# --- 1. PAGE CONFIGURATION & SERVER LOCK ---
st.set_page_config(page_title="Mega Volleyball Auction 2026", layout="wide", page_icon="🏐")
st_autorefresh(interval=1500, limit=10000, key="data_refresh")

@st.cache_resource
def get_lock():
    return threading.Lock()
db_lock = get_lock()

DB_FILE = "auction_db.json"
TOTAL_PURSE = 50000

# --- 2. INTEGRATED LINKS ---
DISCORD_LINK = "https://discord.gg/ePnD2Qqkj"
WHATSAPP_GROUP_LINK = "https://chat.whatsapp.com/KTPQNGAMGh065WGJ8LmsYn"
APP_URL = "https://volleyball-auction.streamlit.app" 

# --- 3. THE 2026 PLAYER SQUAD ---
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

# --- 4. BACKGROUND & CSS ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

def set_background(image_file):
    b64 = get_base64(image_file)
    if b64:
        st.markdown(f"""
<style>
.stApp {{ background: linear-gradient(rgba(10, 15, 20, 0.9), rgba(10, 15, 20, 0.9)), url(data:image/webp;base64,{b64}); background-size: cover; background-position: center; background-attachment: fixed; }}
.big-title {{ text-align: center; font-size: 50px !important; font-weight: 900; color: #FFD700; text-transform: uppercase; text-shadow: 3px 3px 6px #000; letter-spacing: 2px; }}
.player-card {{ background: rgba(25, 25, 25, 0.95); padding: 45px; border-radius: 30px; border: 3px solid #FFD700; backdrop-filter: blur(10px); box-shadow: 0 0 50px rgba(255, 215, 0, 0.2); text-align: center; margin: 10px auto; max-width: 600px; }}
.photo-frame {{ width: 240px; height: 240px; border-radius: 50%; border: 6px solid #FFD700; box-shadow: 0 0 30px rgba(255, 215, 0, 0.5); object-fit: cover; background: #111; margin: 0 auto 20px auto; display: block; }}
.category-badge {{ background-color: #FF4500; color: white; padding: 10px 25px; border-radius: 15px; font-weight: bold; font-size: 22px; text-transform: uppercase; display: inline-block; }}
</style>
        """, unsafe_allow_html=True)

set_background("volleyball.webp")

# --- 5. SECURE DATA PERSISTENCE ---
def load_db():
    default_db = {
        "users": DEFAULT_USER_DATA, "players": DEFAULT_PLAYERS, "player_index": 0, "current_bid": 0, "current_team": "None", 
        "sold_data": [], "last_sold_trigger": False, "winner_name": "", "round_2": False, "last_bid_time": time.time(), 
        "passed_teams": [], "rtm_cards": {v["team"]: True for k, v in DEFAULT_USER_DATA.items() if k != "Masterji"}
    }
    if not os.path.exists(DB_FILE): return default_db
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return default_db

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

db = load_db()
USER_DATA, players = db["users"], db["players"]
teams = [v["team"] for k, v in USER_DATA.items() if k != "Masterji"]

# --- 6. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user_role': None, 'team_name': None})

if not st.session_state['logged_in']:
    st.markdown("<h1 class='big-title'>🏐 AUCTION ARENA LOGIN</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        lc1, lc2 = st.columns(2)
        lc1.link_button("🎙️ DISCORD", DISCORD_LINK, use_container_width=True)
        lc2.link_button("💬 WHATSAPP", WHATSAPP_GROUP_LINK, use_container_width=True)
        with st.form("login_form"):
            uid = st.text_input("User ID")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER ARENA", type="primary"):
                if uid in USER_DATA and USER_DATA[uid]["password"] == pwd:
                    st.session_state.update({'logged_in':True, 'user_role':uid, 'team_name':USER_DATA[uid]["team"]})
                    st.rerun()
                else: st.error("❌ Invalid Credentials")
    st.stop()

# Auto-skip sold players logic
sold_names = [x["Player"].replace(" (RTM)", "").replace(" (Retained)", "") for x in db["sold_data"]]
while db["player_index"] < len(players) and players[db["player_index"]]["Name"] in sold_names:
    db["player_index"] += 1

# --- 7. SIDEBAR (HUD) ---
spent = {t: sum(x["Final Points"] for x in db["sold_data"] if x["Sold To"] == t) for t in teams}
purses = {t: TOTAL_PURSE - spent.get(t, 0) for t in teams}

with st.sidebar:
    st.markdown(f"### 🚩 {st.session_state['team_name']}")
    if st.button("LOGOUT"): st.session_state['logged_in'] = False; st.rerun()
    st.write("---")
    st.link_button("🎤 Join War Room", DISCORD_LINK, use_container_width=True)
    st.link_button("💬 Join Group", WHATSAPP_GROUP_LINK, use_container_width=True)
    st.write("---")
    if teams:
        fig = px.pie(values=list(purses.values()), names=list(purses.keys()), hole=0.6, color_discrete_sequence=px.colors.sequential.Gold)
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    for t in teams: st.caption(f"{t}: {purses[t]} pts")

# --- 8. AUCTION ARENA (LIVE) ---
st.markdown(f"<p class='big-title'>🏆 AUCTION DASHBOARD 🏆</p>", unsafe_allow_html=True)

if db["player_index"] >= len(players):
    st.success("🎉 AUCTION COMPLETED! CHECK SQUADS BELOW.")
else:
    current_player = players[db["player_index"]]
    actual_base = current_player["Base_Points"] // 2 if db.get("round_2") else current_player["Base_Points"]
    
    # Secure Auto-Sell Timer
    time_left = 20
    if db["current_team"] != "None":
        elapsed = time.time() - db.get("last_bid_time", time.time())
        time_left = max(0, 20 - int(elapsed))
        st.markdown(f"<h2 style='text-align: center; color: {'#FF4500' if time_left <= 5 else '#00FA9A'};'>⏳ AUTO-SELL IN: {time_left}s</h2>", unsafe_allow_html=True)
        if time_left == 0:
            with db_lock:
                fdb = load_db()
                if not any(p["Player"] == current_player["Name"] for p in fdb["sold_data"]):
                    fdb["sold_data"].append({"Player": current_player["Name"], "Sold To": fdb["current_team"], "Final Points": fdb["current_bid"]})
                    fdb.update({"winner_name":f"SOLD!", "last_sold_trigger":True, "player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None", "passed_teams":[], "last_bid_time":time.time()})
                    save_db(fdb); st.rerun()

    # --- THE VIP PLAYER CARD ---
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        p_img_b64 = get_base64(current_player.get("Photo", "default.jpg"))
        p_html = f'<img src="data:image/jpeg;base64,{p_img_b64}" class="photo-frame">' if p_img_b64 else '<div class="photo-frame" style="display:flex; align-items:center; justify-content:center; font-size:100px;">🏐</div>'
        st.markdown(f"""
        <div class="player-card">
            {p_html}
            <span class="category-badge">{current_player["Role"]}</span>
            <h1 style="color:#FFD700; margin-top:20px; font-size:60px; text-shadow: 2px 2px #000;">{current_player["Name"]}</h1>
            <h2 style="color:#00FA9A; letter-spacing:3px;">BASE: {actual_base} PTS</h2>
        </div>
        """, unsafe_allow_html=True)

    # Metrics
    st.write("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("HIGHEST BID", f"{db['current_bid']}")
    m2.metric("CURRENT BIDDER", db["current_team"])
    m3.metric("YOUR BUDGET", purses.get(st.session_state['team_name'], "0"))

    # Bidding Controls
    if st.session_state['user_role'] not in ["Masterji", "viewer"]:
        me = st.session_state['team_name']
        nxt = db["current_bid"] + 100 if db["current_team"] != "None" else actual_base
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            if st.button(f"🚀 RAISE BID {nxt}", disabled=(purses.get(me, 0) < nxt or me in db["passed_teams"]), use_container_width=True, type="primary"):
                with db_lock:
                    fdb = load_db(); fdb.update({"current_team":me, "current_bid":nxt, "last_bid_time":time.time(), "passed_teams":[]})
                    save_db(fdb); st.rerun()
        with bc2:
            if st.button("❌ PASS (OUT)", disabled=(me in db["passed_teams"] or me == db["current_team"]), use_container_width=True):
                with db_lock:
                    fdb = load_db(); fdb["passed_teams"].append(me); save_db(fdb); st.rerun()
        with bc3:
            can_rtm = db["rtm_cards"].get(me) and db["current_team"] not in ["None", me]
            if st.button("🃏 USE RTM CARD", disabled=not can_rtm, use_container_width=True):
                with db_lock:
                    fdb = load_db()
                    fdb["sold_data"].append({"Player": current_player["Name"] + " (RTM)", "Sold To": me, "Final Points": fdb["current_bid"]})
                    fdb["rtm_cards"][me] = False; fdb.update({"winner_name":"RTM USED!", "last_sold_trigger":True, "player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None"})
                    save_db(fdb); st.rerun()

# --- 9. MASTERJI CONTROL PANEL (RESTORED COMPLETELY) ---
if st.session_state['user_role'] == "Masterji":
    with st.expander("🛠️ MASTERJI COMMAND CENTER", expanded=False):
        # 1. WhatsApp Notification
        msg = f"🏐 *Auction Alert!* 🏐\n\nNext Player: {current_player['Name'] if db['player_index'] < len(players) else 'Done'}\n\nJoin Live: {APP_URL}"
        wa_url = f"https://wa.me/?text={urllib.parse.quote(msg)}"
        st.link_button("📢 SEND NOTIFICATION TO WHATSAPP GROUP", wa_url, use_container_width=True)
        
        st.write("---")
        # 2. Quick Actions
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            if db["player_index"] < len(players) and st.button("🔨 FORCE SOLD"):
                with db_lock:
                    fdb = load_db(); fdb["sold_data"].append({"Player": current_player["Name"], "Sold To": fdb["current_team"], "Final Points": fdb["current_bid"]})
                    fdb.update({"player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None"}); save_db(fdb); st.rerun()
        with ac2:
            if db["player_index"] < len(players) and st.button("❌ FORCE UNSOLD"):
                with db_lock:
                    fdb = load_db(); fdb["sold_data"].append({"Player": current_player["Name"], "Sold To": "UNSOLD", "Final Points": 0})
                    fdb.update({"player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None"}); save_db(fdb); st.rerun()
        with ac3:
            if st.button("🔄 EMERGENCY RESET DB"):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.rerun()

        st.write("---")
        # 3. Manual Call
        st.markdown("#### 🎯 Call Specific Player")
        avail = [p["Name"] for p in players if p["Name"] not in sold_names]
        if avail:
            call = st.selectbox("Select Player", avail)
            if st.button("📢 BRING TO STAGE"):
                idx = next(i for i, p in enumerate(players) if p["Name"] == call)
                with db_lock:
                    fdb = load_db(); fdb.update({"player_index":idx, "current_bid":0, "current_team":"None"}); save_db(fdb); st.rerun()

        st.write("---")
        # 4. Manage Teams (Add/Remove)
        st.markdown("#### ⚙️ Manage Teams (Captains)")
        tm1, tm2 = st.columns(2)
        with tm1:
            with st.form("add_team"):
                st.write("**➕ Add New Team/Captain**")
                ni = st.text_input("New User ID")
                np = st.text_input("Password")
                nn = st.text_input("Team Name & Emoji")
                if st.form_submit_button("Add Team"):
                    if ni and np and nn:
                        with db_lock:
                            fdb = load_db(); fdb["users"][ni] = {"password":np, "team":nn}; fdb["rtm_cards"][nn]=True
                            save_db(fdb); st.rerun()
        with tm2:
            with st.form("rem_team"):
                st.write("**🗑️ Remove a Team**")
                rem_options = [k for k in db["users"] if k != "Masterji"]
                ri = st.selectbox("Select Team to Remove", rem_options) if rem_options else None
                if st.form_submit_button("Remove Team", disabled=not rem_options):
                    if ri:
                        with db_lock:
                            fdb = load_db(); del fdb["users"][ri]; save_db(fdb); st.rerun()

        st.write("---")
        # 5. Retain & Mark Unavailable
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### 🤝 Retain Player")
            if avail and teams:
                ret_player = st.selectbox("Select Player", avail, key="ret_p")
                ret_team = st.selectbox("Retain To", teams)
                ret_price = st.number_input("Retain Price", min_value=0, step=100)
                if st.button("🤝 Confirm Retain", use_container_width=True):
                    with db_lock:
                        fdb = load_db()
                        fdb["sold_data"].append({"Player": ret_player + " (Retained)", "Sold To": ret_team, "Final Points": ret_price})
                        fdb.update({"winner_name":f"RETAINED BY {ret_team}!", "last_sold_trigger":True, "current_bid":0, "current_team":"None"})
                        save_db(fdb); st.rerun()

        with col_m2:
            st.markdown("#### 🚫 Mark Unavailable")
            if avail:
                un_player = st.selectbox("Select Player", avail, key="un_p")
                if st.button("🚫 Mark as Unavailable", use_container_width=True):
                    with db_lock:
                        fdb = load_db()
                        fdb["sold_data"].append({"Player": un_player, "Sold To": "UNAVAILABLE", "Final Points": 0})
                        if fdb["player_index"] < len(fdb["players"]) and current_player["Name"] == un_player:
                            fdb.update({"player_index":fdb["player_index"]+1, "current_bid":0, "current_team":"None"})
                        save_db(fdb); st.rerun()

        st.write("---")
        # 6. Add New Player
        st.markdown("#### ➕ Add New Player")
        with st.form("add_player_form"):
            np_name = st.text_input("Player Name")
            np_role = st.selectbox("Role", ["OUTSIDE HITTER", "RIGHT SIDE HITTER", "SETTER", "MIDDLE BLOCKER", "LIBERO", "ALL ROUNDER", "SERVICE SPECIALIST"])
            np_base = st.number_input("Base Price", min_value=100, step=100, value=500)
            if st.form_submit_button("➕ Add Player to Draft", type="primary"):
                if np_name:
                    with db_lock:
                        fdb = load_db()
                        # Formatting photo name as lowercase name.jpg automatically
                        np_photo = np_name.lower().replace(" ", "") + ".jpg"
                        fdb["players"].append({"Name": np_name.upper(), "Photo": np_photo, "Role": np_role, "Base_Points": np_base})
                        save_db(fdb); st.rerun()

# --- 10. SQUAD DISPLAY ---
st.write("---")
if teams:
    tabs = st.tabs([f"🛡️ {t}" for t in teams])
    for i, t in enumerate(teams):
        with tabs[i]:
            df = pd.DataFrame([x for x in db["sold_data"] if x["Sold To"] == t])
            if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
            else: st.info("No players bought yet.")
