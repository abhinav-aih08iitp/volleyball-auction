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

# 👇 AAPKA DISCORD LINK YAHAN SET HAI 👇
DISCORD_LINK = "https://discord.gg/ePnD2Qqkj"

# --- 2. DEFAULT SYSTEM DATA ---
DEFAULT_USER_DATA = {
    "Masterji": {"password": "Mishraji041411", "team": "👑 ADMIN"}
}

DEFAULT_PLAYERS = [
    {"Name": "Golu bhiya", "Role": "OUTSIDE HITTER", "Base_Points": 800, "Spike": 8, "Defense": 6, "Speed": 7},
    {"Name": "Bheem", "Role": "OUTSIDE HITTER", "Base_Points": 500, "Spike": 6, "Defense": 5, "Speed": 7},
    {"Name": "Rishu", "Role": "OUTSIDE HITTER", "Base_Points": 500, "Spike": 7, "Defense": 5, "Speed": 8},
    {"Name": "Shreshth", "Role": "OUTSIDE HITTER", "Base_Points": 1000, "Spike": 8, "Defense": 7, "Speed": 7},
    {"Name": "Prithvi", "Role": "OUTSIDE HITTER", "Base_Points": 800, "Spike": 7, "Defense": 6, "Speed": 8},
    {"Name": "Rahil", "Role": "RIGHT SIDE HITTER", "Base_Points": 800, "Spike": 8, "Defense": 5, "Speed": 7},
    {"Name": "Keshav", "Role": "RIGHT SIDE HITTER", "Base_Points": 900, "Spike": 8, "Defense": 6, "Speed": 7},
    {"Name": "Shashwat", "Role": "RIGHT SIDE HITTER", "Base_Points": 1200, "Spike": 9, "Defense": 7, "Speed": 8},
    {"Name": "Chulbul bhiya", "Role": "SETTER", "Base_Points": 1000, "Spike": 6, "Defense": 8, "Speed": 9},
    {"Name": "Mohit", "Role": "SETTER", "Base_Points": 1500, "Spike": 7, "Defense": 8, "Speed": 8},
    {"Name": "Kishu", "Role": "SETTER", "Base_Points": 1000, "Spike": 6, "Defense": 7, "Speed": 9},
    {"Name": "Abhi", "Role": "SETTER", "Base_Points": 500, "Spike": 5, "Defense": 6, "Speed": 8},
    {"Name": "Piyush renter 1", "Role": "SETTER", "Base_Points": 400, "Spike": 5, "Defense": 5, "Speed": 7},
    {"Name": "Piyush renter 2", "Role": "SETTER", "Base_Points": 200, "Spike": 4, "Defense": 5, "Speed": 6},
    {"Name": "Mithu", "Role": "MIDDLE BLOCKER", "Base_Points": 2000, "Spike": 9, "Defense": 10, "Speed": 7},
    {"Name": "Ayush", "Role": "MIDDLE BLOCKER", "Base_Points": 1900, "Spike": 8, "Defense": 9, "Speed": 8},
    {"Name": "Ankush", "Role": "LIBERO", "Base_Points": 2000, "Spike": 4, "Defense": 10, "Speed": 10},
    {"Name": "Rishi", "Role": "LIBERO", "Base_Points": 1500, "Spike": 5, "Defense": 9, "Speed": 9},
    {"Name": "Sidhu", "Role": "ALL ROUNDER", "Base_Points": 2000, "Spike": 9, "Defense": 8, "Speed": 9},
    {"Name": "Piyush", "Role": "ALL ROUNDER", "Base_Points": 2000, "Spike": 9, "Defense": 9, "Speed": 8},
    {"Name": "Rohit bhiya", "Role": "SERVICE SPECIALIST", "Base_Points": 1500, "Spike": 8, "Defense": 7, "Speed": 8},
]

# --- 3. BACKGROUND & CSS ---
def set_background(image_file):
    try:
        with open(image_file, "rb") as f: data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
<style>
.stApp {{ background: linear-gradient(rgba(10, 15, 20, 0.85), rgba(10, 15, 20, 0.85)), url(data:image/webp;base64,{b64}); background-size: cover; background-position: center; background-attachment: fixed; }}
.big-title {{ text-align: center; font-size: 50px !important; font-weight: 900; color: #FFD700; text-transform: uppercase; text-shadow: 3px 3px 6px #000; }}
.player-card {{ background: rgba(20, 20, 20, 0.9); padding: 30px; border-radius: 20px; border: 2px solid #FFD700; backdrop-filter: blur(5px); box-shadow: 0 10px 30px rgba(255, 215, 0, 0.2); }}
.category-badge {{ background-color: #FF4500; color: white; padding: 5px 15px; border-radius: 10px; font-weight: bold; font-size: 18px; text-transform: uppercase; }}
.stat-bar-bg {{ background: #444; border-radius: 10px; width: 100%; height: 8px; margin-bottom: 10px; }}
.stat-bar-fill {{ background: linear-gradient(90deg, #FF4500, #FFD700); height: 8px; border-radius: 10px; }}
.ticker-wrap {{ position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.9); color: #FFD700; padding: 10px; font-weight: bold; border-top: 2px solid #FFD700; z-index: 999; }}
</style>
        """, unsafe_allow_html=True)
    except: pass

set_background("volleyball.webp")

# --- 4. SECURE DATABASE LOGIC ---
def load_db():
    default_db = {
        "users": DEFAULT_USER_DATA,
        "players": DEFAULT_PLAYERS,
        "player_index": 0, "current_bid": 0, "current_team": "None", 
        "sold_data": [], "last_sold_trigger": False, "winner_name": "", 
        "round_2": False, "last_bid_time": time.time(), "passed_teams": [],
        "rtm_cards": {v["team"]: True for k, v in DEFAULT_USER_DATA.items() if k != "Masterji"}
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

# --- 5. DYNAMIC VARIABLES ---
USER_DATA = db["users"]
players = db["players"]
teams = [v["team"] for k, v in USER_DATA.items() if k != "Masterji"]

# --- 6. LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['team_name'] = None

if not st.session_state['logged_in']:
    st.markdown("<h1 class='big-title'>🔐 Auction Arena Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login"):
            st.markdown("### 🧑‍✈️ Captain / Masterji Login")
            uid = st.text_input("User ID")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Enter Arena"):
                if uid in USER_DATA and USER_DATA[uid]["password"] == pwd:
                    st.session_state.update({'logged_in':True, 'user_role':uid, 'team_name':USER_DATA[uid]["team"]})
                    st.rerun()
                else: st.error("Wrong ID/Password")
        st.markdown("---")
        if st.button("👁️ WATCH LIVE AS GUEST", use_container_width=True, type="primary"):
            st.session_state.update({'logged_in':True, 'user_role':'viewer', 'team_name':'👤 LIVE AUDIENCE'})
            st.rerun()
    st.stop()

# Auto-skip logic for sold players
sold_names = [x["Player"].replace(" (RTM)", "").replace(" (Retained)", "") for x in db["sold_data"]]
while db["player_index"] < len(players) and players[db["player_index"]]["Name"] in sold_names:
    db["player_index"] += 1

# --- 7. SIDEBAR (CHART & STATS & DISCORD) ---
spent = {t: sum(x["Final Points"] for x in db["sold_data"] if x["Sold To"] == t) for t in teams}
purses = {t: TOTAL_PURSE - spent.get(t, 0) for t in teams}

with st.sidebar:
    st.markdown(f"### {st.session_state['team_name']}")
    if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()
    st.write("---")
    
    # 🎤 DISCORD LIVE BUTTON
    st.markdown("### 🎙️ Live War Room")
    st.link_button("🎧 Join Discord Voice/Chat", DISCORD_LINK, use_container_width=True)
    st.write("---")
    
    if db["sold_data"]:
        valid_sales = [x for x in db["sold_data"] if x["Sold To"] not in ["UNSOLD", "UNAVAILABLE"]]
        if valid_sales:
            expensive = max(valid_sales, key=lambda x: x["Final Points"])
            st.markdown(f"""
<div style="background:rgba(255,215,0,0.1); border:1px solid #FFD700; padding:10px; border-radius:10px; text-align:center;">
<span style="color:#FFD700; font-size:12px;">💎 MOST EXPENSIVE</span><br>
<b style="font-size:18px;">{expensive['Player']}</b><br>
<span style="color:#00FA9A;">{expensive['Final Points']} pts</span>
</div>
            """, unsafe_allow_html=True)
    
    st.write("---")
    st.markdown("### 📊 Budget War")
    if len(teams) > 0:
        fig = px.pie(values=list(purses.values()), names=list(purses.keys()), hole=0.6, color_discrete_sequence=['#FFD700', '#FF4500', '#00FA9A', '#1E90FF', '#9370DB', '#FF1493'])
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Captains added yet.")
    
    for t in teams: st.caption(f"{t}: {purses[t]} pts")

# --- 8. AUDIO BALLOONS & CHEER ---
if db.get("last_sold_trigger"):
    st.balloons()
    st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2003/2003-preview.mp3" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    st.markdown(f'<h2 style="color:#00FA9A; text-align:center; text-shadow: 2px 2px 4px #000;">🎊 {db["winner_name"]} 🎊</h2>', unsafe_allow_html=True)

# --- 9. MAIN ARENA (LOCKED AUTO-SELL LOGIC) ---
st.markdown(f"<p class='big-title'>🏆 {st.session_state['team_name']} DASHBOARD 🏆</p>", unsafe_allow_html=True)

if db["player_index"] >= len(players):
    st.success("AUCTION QUEUE COMPLETED!")
    if st.session_state['user_role'] == "Masterji":
        st.write("---")
        unsold_count = sum(1 for x in db["sold_data"] if x["Sold To"] == "UNSOLD")
        if unsold_count > 0:
            if st.button("🔄 Bring Back Unsold Players (50% OFF)", type="primary"):
                with db_lock:
                    fresh_db = load_db()
                    fresh_db["sold_data"] = [x for x in fresh_db["sold_data"] if x["Sold To"] != "UNSOLD"]
                    fresh_db["round_2"] = True
                    fresh_db["player_index"] = 0
                    save_db(fresh_db)
                st.rerun()
else:
    current_player = players[db["player_index"]]
    actual_base = current_player["Base_Points"] // 2 if db.get("round_2") else current_player["Base_Points"]
    is_already_sold = any(p["Player"] == current_player["Name"] for p in db["sold_data"])

    # Auto Unsold dynamically calculated
    if len(db.get("passed_teams", [])) >= len(teams) and len(teams) > 0 and not is_already_sold:
        with db_lock:
            fresh_db = load_db()
            if len(fresh_db.get("passed_teams", [])) >= len(teams) and not any(p["Player"] == current_player["Name"] for p in fresh_db["sold_data"]):
                fresh_db["sold_data"].append({"Player": current_player["Name"], "Sold To": "UNSOLD", "Final Points": 0})
                fresh_db.update({"last_sold_trigger":False, "player_index":fresh_db["player_index"]+1, "current_bid":0, "current_team":"None", "passed_teams":[], "last_bid_time":time.time()})
                save_db(fresh_db)
        st.rerun()

    if db["current_bid"] == 0 and db["current_team"] == "None" and len(db["passed_teams"]) == 0:
        with db_lock:
            fresh_db = load_db()
            if fresh_db["current_bid"] == 0:
                fresh_db.update({"current_bid":actual_base, "last_sold_trigger":False, "last_bid_time":time.time(), "passed_teams":[]})
                save_db(fresh_db)

    time_left = 20
    if db["current_team"] != "None":
        elapsed = time.time() - db.get("last_bid_time", time.time())
        time_left = max(0, 20 - int(elapsed))
        st.markdown(f"<h2 style='text-align: center; color: {'#FF4500' if time_left <= 5 else '#00FA9A'};'>⏳ AUTO-SELL IN: {time_left}s</h2>", unsafe_allow_html=True)
        
        # SECURED AUTO-SELL
        if time_left == 0 and not is_already_sold:
            with db_lock:
                fresh_db = load_db()
                if not any(p["Player"] == current_player["Name"] for p in fresh_db["sold_data"]) and fresh_db["current_team"] != "None":
                    fresh_db["sold_data"].append({"Player": current_player["Name"], "Sold To": fresh_db["current_team"], "Final Points": fresh_db["current_bid"]})
                    fresh_db.update({"winner_name":f"⏰ AUTO-SOLD TO {fresh_db['current_team']}!", "last_sold_trigger":True, "player_index":fresh_db["player_index"]+1, "current_bid":0, "current_team":"None", "passed_teams":[], "last_bid_time":time.time()})
                    save_db(fresh_db)
            st.rerun()

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
<div class="player-card">
<span class="category-badge">🔥 {current_player['Role']}</span>
{"<span class='category-badge' style='background:purple;'>🔁 ROUND 2 (50% OFF)</span>" if db.get("round_2") else ""}
<h2 style='color:#FFD700; margin-top:15px; font-size:45px;'>{current_player['Name']}</h2>
<p style='color:#00FA9A; font-size:26px; font-weight:bold;'>Base: {actual_base}</p>
<hr style="border-color:#555;">
<div style="text-align:left;">
<span style="color:#ddd; font-weight:bold;">Spike ({current_player['Spike']}/10)</span>
<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{current_player['Spike']*10}%"></div></div>
<span style="color:#ddd; font-weight:bold;">Defense ({current_player['Defense']}/10)</span>
<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{current_player['Defense']*10}%"></div></div>
<span style="color:#ddd; font-weight:bold;">Speed ({current_player['Speed']}/10)</span>
<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{current_player['Speed']*10}%"></div></div>
</div>
</div>
""", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Highest Bid", f"{db['current_bid']}")
    m2.metric("Highest Bidder", db["current_team"])
    m3.metric("Your Budget", purses.get(st.session_state['team_name'], "VIEW ONLY"))

    if len(db["passed_teams"]) > 0: st.warning(f"⚠️ Teams OUT: {', '.join(db['passed_teams'])}")
    st.write("---")

    # --- 10. SECURED CAPTAIN CONTROLS ---
    if st.session_state['user_role'] not in ["Masterji", "viewer"]:
        me = st.session_state['team_name']
        nxt = db["current_bid"] + 100 if db["current_team"] != "None" else actual_base
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            if st.button(f"🚀 RAISE BID (+100)", disabled=(purses.get(me, 0) < nxt or me in db["passed_teams"]), use_container_width=True, type="primary"):
                with db_lock:
                    fresh_db = load_db()
                    current_nxt = fresh_db["current_bid"] + 100 if fresh_db["current_team"] != "None" else actual_base
                    fresh_db.update({"current_team":me, "current_bid":current_nxt, "last_bid_time":time.time(), "passed_teams":[]})
                    save_db(fresh_db)
                st.markdown('<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3"></audio>', unsafe_allow_html=True)
                st.rerun()
        with bc2:
            if st.button("❌ I'M OUT (Pass)", disabled=(me in db["passed_teams"] or me == db["current_team"]), use_container_width=True):
                with db_lock:
                    fresh_db = load_db()
                    if me not in fresh_db["passed_teams"]: fresh_db["passed_teams"].append(me)
                    save_db(fresh_db)
                st.rerun()
        with bc3:
            can_rtm = db["rtm_cards"].get(me) and db["current_team"] != "None" and db["current_team"] != me
            if st.button("🃏 USE RTM CARD", disabled=not can_rtm, use_container_width=True):
                with db_lock:
                    fresh_db = load_db()
                    if fresh_db["rtm_cards"].get(me) and fresh_db["current_team"] not in ["None", me]:
                        fresh_db["sold_data"].append({"Player": current_player["Name"] + " (RTM)", "Sold To": me, "Final Points": fresh_db["current_bid"]})
                        fresh_db["rtm_cards"][me] = False
                        fresh_db.update({"winner_name":f"🃏 RTM USED! {me} STEALS IT!", "last_sold_trigger":True, "player_index":fresh_db["player_index"]+1, "current_bid":0, "current_team":"None", "last_bid_time":time.time()})
                        save_db(fresh_db)
                st.rerun()
    elif st.session_state['user_role'] == "viewer":
        st.info("👀 You are watching the Live Broadcast on Discord. Only Captains can bid.")

# --- 11. MASTERJI CONTROLS ---
if st.session_state['user_role'] == "Masterji":
    with st.expander("🛠️ Masterji Controls", expanded=True):
        st.markdown("#### ⚡ Quick Actions")
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            if db["player_index"] < len(players) and st.button("🔨 FORCE SOLD!", use_container_width=True, type="primary"):
                with db_lock:
                    fresh_db = load_db()
                    if not any(p["Player"] == current_player["Name"] for p in fresh_db["sold_data"]):
                        fresh_db["sold_data"].append({"Player": current_player["Name"], "Sold To": fresh_db["current_team"], "Final Points": fresh_db["current_bid"]})
                        fresh_db.update({"winner_name":f"SOLD TO {fresh_db['current_team']}!", "last_sold_trigger":True, "player_index":fresh_db["player_index"]+1, "current_bid":0, "current_team":"None", "passed_teams":[], "last_bid_time":time.time()})
                        save_db(fresh_db)
                st.rerun()
        with ac2:
            if db["player_index"] < len(players) and st.button("❌ FORCE UNSOLD", use_container_width=True):
                with db_lock:
                    fresh_db = load_db()
                    if not any(p["Player"] == current_player["Name"] for p in fresh_db["sold_data"]):
                        fresh_db["sold_data"].append({"Player": current_player["Name"], "Sold To": "UNSOLD", "Final Points": 0})
                        fresh_db.update({"last_sold_trigger":False, "player_index":fresh_db["player_index"]+1, "current_bid":0, "current_team":"None", "passed_teams":[], "last_bid_time":time.time()})
                        save_db(fresh_db)
                st.rerun()
        with ac3:
            if st.button("🔄 RESET DATABASE", use_container_width=True):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.rerun()
        
        st.write("---")
        
        # --- CALL SPECIFIC PLAYER ---
        st.markdown("#### 🎯 Call Specific Player (Manual Override)")
        curr_p_name = players[db["player_index"]]["Name"] if db["player_index"] < len(players) else ""
        available_for_call = [p["Name"] for p in players if p["Name"] not in sold_names and p["Name"] != curr_p_name]
        
        if available_for_call:
            c1, c2 = st.columns([2, 1])
            with c1:
                call_player = st.selectbox("Select Player to bring to stage", available_for_call, key="call_p")
            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📢 Bring to Auction Now", use_container_width=True, type="primary"):
                    p_idx = next((i for i, p in enumerate(players) if p["Name"] == call_player), -1)
                    if p_idx != -1:
                        with db_lock:
                            fresh_db = load_db()
                            fresh_db["player_index"] = p_idx
                            fresh_db["current_bid"] = 0
                            fresh_db["current_team"] = "None"
                            fresh_db["passed_teams"] = []
                            fresh_db["last_bid_time"] = time.time()
                            fresh_db["last_sold_trigger"] = False
                            save_db(fresh_db)
                        st.rerun()
        else:
            st.info("No other available players to call.")

        st.write("---")
        
        # --- DYNAMIC TEAM MANAGEMENT (WITH BUG FIX) ---
        st.markdown("#### ⚙️ Manage Teams (Captains)")
        tm1, tm2 = st.columns(2)
        with tm1:
            with st.form("add_team"):
                st.write("**➕ Add New Team/Captain**")
                n_id = st.text_input("Login ID")
                n_pass = st.text_input("Password")
                n_name = st.text_input("Team Name with Emoji")
                if st.form_submit_button("Add Team", type="primary"):
                    if n_id and n_pass and n_name:
                        with db_lock:
                            fresh_db = load_db()
                            fresh_db["users"][n_id] = {"password": n_pass, "team": n_name}
                            fresh_db["rtm_cards"][n_name] = True
                            save_db(fresh_db)
                        st.success(f"Team {n_name} added!"); time.sleep(1); st.rerun()
        with tm2:
            with st.form("remove_team"):
                st.write("**🗑️ Remove a Team**")
                rem_options = [k for k in db["users"].keys() if k != "Masterji"]
                if rem_options:
                    r_id = st.selectbox("Select Team to Remove", rem_options)
                    if st.form_submit_button("Remove Team"):
                        with db_lock:
                            fresh_db = load_db()
                            del fresh_db["users"][r_id]
                            save_db(fresh_db)
                        st.success("Team Removed!"); time.sleep(1); st.rerun()
                else: 
                    st.info("No teams left to remove.")
                    st.form_submit_button("Remove Team", disabled=True) 

        st.write("---")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### 🤝 Retain Player")
            available_players = [p["Name"] for p in players if p["Name"] not in sold_names]
            if available_players and teams:
                ret_player = st.selectbox("Select Player", available_players, key="ret_p")
                ret_team = st.selectbox("Retain To", teams)
                ret_price = st.number_input("Retain Price", min_value=0, step=100)
                if st.button("🤝 Confirm Retain", use_container_width=True):
                    with db_lock:
                        fresh_db = load_db()
                        fresh_db["sold_data"].append({"Player": ret_player + " (Retained)", "Sold To": ret_team, "Final Points": ret_price})
                        fresh_db.update({"winner_name":f"{ret_player} RETAINED BY {ret_team}!", "last_sold_trigger":True, "current_bid":0, "current_team":"None"})
                        save_db(fresh_db)
                    st.rerun()

        with col_m2:
            st.markdown("#### 🚫 Mark Unavailable")
            if available_players:
                un_player = st.selectbox("Select Player", available_players, key="un_p")
                if st.button("🚫 Mark as Unavailable", use_container_width=True):
                    with db_lock:
                        fresh_db = load_db()
                        fresh_db["sold_data"].append({"Player": un_player, "Sold To": "UNAVAILABLE", "Final Points": 0})
                        if fresh_db["player_index"] < len(fresh_db["players"]) and current_player["Name"] == un_player:
                            fresh_db.update({"last_sold_trigger":False, "player_index":fresh_db["player_index"]+1, "current_bid":0, "current_team":"None", "passed_teams":[], "last_bid_time":time.time()})
                        save_db(fresh_db)
                    st.rerun()

        st.write("---")
        st.markdown("#### ➕ Add New Player")
        with st.form("add_player_form"):
            np_name = st.text_input("Player Name")
            np_role = st.selectbox("Role", ["OUTSIDE HITTER", "RIGHT SIDE HITTER", "SETTER", "MIDDLE BLOCKER", "LIBERO", "ALL ROUNDER", "SERVICE SPECIALIST"])
            np_base = st.number_input("Base Price", min_value=100, step=100, value=500)
            c1, c2, c3 = st.columns(3)
            with c1: np_spike = st.slider("Spike Power", 1, 10, 5)
            with c2: np_def = st.slider("Defense", 1, 10, 5)
            with c3: np_speed = st.slider("Speed", 1, 10, 5)
            if st.form_submit_button("➕ Add Player to Draft", type="primary"):
                if np_name:
                    with db_lock:
                        fresh_db = load_db()
                        fresh_db["players"].append({"Name": np_name, "Role": np_role, "Base_Points": np_base, "Spike": np_spike, "Defense": np_def, "Speed": np_speed})
                        save_db(fresh_db)
                    st.success(f"{np_name} has been added!"); time.sleep(1); st.rerun()

# --- 12. LIVE NEWS TICKER ---
latest = db["sold_data"][-1] if db["sold_data"] else {"Player": "Waiting...", "Sold To": "-", "Final Points": 0}
top_purse_team = max(purses, key=purses.get) if purses else "-"
st.markdown(f"""
<div class="ticker-wrap">
<marquee>⚡ LATEST: {latest['Player']} marked {latest['Sold To']} for {latest['Final Points']} pts | 💰 Highest Purse: {top_purse_team} | 🏐 NEXT UP: {players[db['player_index']+1]['Name'] if db['player_index'] < len(players)-1 else 'End of Draft'}</marquee>
</div><br><br>
""", unsafe_allow_html=True)

# --- 13. SQUADS & DIRECTORY TABS ---
st.write("---")
tab_squads, tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛡️ Team Squads", "Hitters 🏐", "Setters 🎯", "Blockers 🧱", "Liberos 🛡️", "All-Rounders ⭐"])

with tab_squads:
    if len(teams) > 0:
        cols = st.columns(len(teams))
        for i, t in enumerate(teams):
            with cols[i]:
                st.markdown(f"<h4 style='color:#FFD700;'>{t}</h4>", unsafe_allow_html=True)
                st.caption(f"RTM Card: {'✅ Available' if db['rtm_cards'].get(t) else '❌ Used'}")
                team_players = [x for x in db["sold_data"] if x["Sold To"] == t]
                for p in team_players: st.markdown(f"- **{p['Player']}** ({p['Final Points']} pts)")
    else: st.info("No active teams. Add a team from Masterji Controls.")

def get_status(p_name):
    for item in db["sold_data"]:
        if item["Player"].replace(" (RTM)", "").replace(" (Retained)", "") == p_name:
            if item["Sold To"] == "UNSOLD": return "❌ Unsold"
            if item["Sold To"] == "UNAVAILABLE": return "🚫 Unavailable"
            return f"✅ Sold to {item['Sold To']}"
    return "🟢 Available"

def render_table(role_keyword):
    data = [{"Player": p["Name"], "Role": p["Role"], "Base": p["Base_Points"], "Status": get_status(p["Name"])} for p in players if role_keyword in p["Role"]]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

with tab1: render_table("HITTER")
with tab2: render_table("SETTER")
with tab3: render_table("BLOCKER")
with tab4: render_table("LIBERO")
with tab5: 
    data_others = [{"Player": p["Name"], "Role": p["Role"], "Base": p["Base_Points"], "Status": get_status(p["Name"])} for p in players if "ALL ROUNDER" in p["Role"] or "SERVICE" in p["Role"]]
    if data_others: st.dataframe(pd.DataFrame(data_others), use_container_width=True, hide_index=True)
