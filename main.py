import os
import discord
from discord.ext import commands
from discord import app_commands
import json
import requests
import io
import traceback
import re
import uuid
import asyncio
from datetime import datetime, timedelta
from myserver import server_on
from github import Github, InputFileContent

# =================================================================
# ⚙️ CONFIGURATION (ตั้งค่าระบบ)
# =================================================================

DISCORD_BOT_TOKEN = os.environ.get('TOKEN')
EASYSLIP_API_KEY = '12710681-efd6-412f-bce7-984feb9aa4cc'.strip()

# --------------------------------------------------------
# 🐱 GITHUB CONFIG
# --------------------------------------------------------
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# --------------------------------------------------------
# 🔑 ZONE: ตั้งค่า ID ห้อง
# --------------------------------------------------------

# 🔥 [สำคัญ] ใส่ ID ห้องที่โปรแกรม GHOSTX ส่ง Log Login เข้ามา
LISTEN_CHANNELS = [
    1434154279068762116,  # ID ห้อง LOG-CMD-REBORNKILL
    222222222222222222,  # ID ห้อง LOG-CMD-NEWCLEAN
    333333333333333333   # ID ห้อง LOG-CMD-ALLWEAPON
]

# 1. ห้องหน้าร้าน & ลูกค้าใช้งาน
SHOP_CHANNEL_ID = 1416797606180552714       
SLIP_CHANNEL_ID = 1416797464350167090       
REDEEM_CHANNEL_ID = 1449749949918089289     

# 2. ห้อง LOGS หลังบ้าน (แอดมิน)
PURCHASE_LOG_ID = 1450487180416778321       
SLIP_LOG_ID = 1444390933297631512           
ADD_MONEY_LOG_ID = 1450470356979683328      
REDEEM_LOG_ID = 1450457258663215146         

# 3. ห้อง DATABASE & DASHBOARD
DASHBOARD_CMD_CHANNEL_ID = 1444662199674081423 
BALANCE_LOG_ID = 1444662604940181667           

# --------------------------------------------------------

# Assets & Theme
THEME_COLOR = 0x2b2d31   
ACCENT_COLOR = 0x5865F2  
SUCCESS_COLOR = 0x57F287 
ERROR_COLOR = 0xED4245 
TOPUP_COLOR = 0x00f7ff  
CYBER_COLOR = 0x00f7ff 

QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg'
SHOP_BANNER_URL = 'https://media.discordapp.net/attachments/1303249085347926058/1444212368937586698/53ad0cc3373bbe0ea51dd878241952c6.gif' 
SUCCESS_GIF_URL = 'https://cdn.discordapp.com/attachments/1233098937632817233/1444077217230491731/Fire_Force_Sho_Kusakabe_GIF.gif'

# 🔥 ชื่อผู้รับเงิน
EXPECTED_NAMES = [
    'ชานนท์ ขันทอง',    
    'ชานนท์',           
    'chanon khantong', 
    'chanon',           
    'khantong'          
]
MIN_AMOUNT = 1.00

# 🔗 ลิงก์สินค้า (Gist Raw แบบไม่มี Hash)
PRODUCT_LINKS = {
    "[CMD] ลบประวัติ CMD": "https://gist.githubusercontent.com/chanon254426-droid/7666888514952966fdcf230bb7a65d22/raw/cleaner.txt",
    "[CMD] ALL WEAPON": "https://gist.githubusercontent.com/chanon254426-droid/c83112e3ab72327fd0d19a6cd2d0177c/raw/allweapon.txt",
    "[CMD] REBORNKILL": "https://gist.githubusercontent.com/chanon254426-droid/dc091d05cad4cbe41017a5844da93bb8/raw/rebornkill.txt",
    "[CMD] 60 7ET 8ACK": "https://gist.githubusercontent.com/chanon254426-droid/5c41a78a958cb41c26a6654a66486f0a/raw/hogetback.txt",
}

# =================================================================
# 🛍️ PRODUCTS DATA
# =================================================================
PRODUCTS = [
    # หมวด: VIP & DONATE
    {"id": "item1", "emoji": "🏆",  "name": "VVIP [ยศทั้งร้าน]🏆", "price": 599,  "role_id": 1449658582244262041, "category": "🏆 Rank & Donate"},
    {"id": "item2",  "emoji": "⭐",  "name": "DONATE", "price": 89,  "role_id": 1431279741440364625, "category": "🏆 Rank & Donate"},
    
    # หมวด: BOOST & MODS
    {"id": "item3", "emoji": "🎮",  "name": "BOOST FPS", "price": 99,  "role_id": 1432010188340199504, "category": "🎮 Boost & Mods"},
    {"id": "item4",  "emoji": "👻",  "name": "MODS DEVOUR", "price": 120, "role_id": 1432064283767738571, "category": "🎮 Boost & Mods"},
    {"id": "item5", "emoji": "🚧",  "name": "TOGYO MOD", "price": 59,  "role_id": 1448142708286947449, "category": "🎮 Boost & Mods"},
    
    # หมวด: CMD / SCRIPTS
    {"id": "item6",  "emoji": "🗑️",  "name": "ลบประวัติรันโปรแกรม","price": 49,  "role_id": 1444191566838370365, "category": "💻 CMD Scripts"},
    {"id": "item7",  "emoji": "👑",  "name": "[CMD] SETTING PREMIUM", "price": 169, "role_id": 1419373724653588540, "category": "💻 CMD Scripts"},
    {"id": "item8",  "emoji": "⚔️",  "name": "[CMD] ALL WEAPON", "price": 139, "role_id": 1444190694674792592, "category": "💻 CMD Scripts"},
    {"id": "item9",  "emoji": "💻",  "name": "[CMD] ลบประวัติ CMD", "price": 79,  "role_id": 1444191270372114552, "category": "💻 CMD Scripts"},
    {"id": "item10", "emoji": "🚀",  "name": "[CMD] FRAME SYNC", "price": 120,  "role_id": 1449653924209492098, "category": "💻 CMD Scripts"},
    {"id": "item11", "emoji": "💻",  "name": "[CMD] REBORNKILL", "price": 159,  "role_id": 1449657396497743883, "category": "💻 CMD Scripts"},
    {"id": "item12", "emoji": "💻",  "name": "[CMD] 60 7ET 8ACK", "price": 159,  "role_id": 1449658031301333153, "category": "💻 CMD Scripts"},
    
    # หมวด: RESHADE
    {"id": "item13", "emoji": "🎧",  "name": "[RESHADE] SUNKISSED", "price": 25,  "role_id": 1431278653760737340, "category": "🎨 ReShade"},
    {"id": "item14", "emoji": "🌃",  "name": "[RESHADE] MAGICEYE", "price": 25,  "role_id": 1431231640058990652, "category": "🎨 ReShade"},
    {"id": "item15", "emoji": "🌷",  "name": "[RESHADE] REALLIVE", "price": 25,  "role_id": 1431204938373140513, "category": "🎨 ReShade"},
    {"id": "item16", "emoji": "🏞️",  "name": "[RESHADE] FALLING", "price": 25,  "role_id": 1444192569754910770, "category": "🎨 ReShade"},
    {"id": "item17", "emoji": "⚡",  "name": "[RESHADE] X TOGYO MODS", "price": 35,  "role_id": 1448217708146589747, "category": "🎨 ReShade"},
    {"id": "item18", "emoji": "❓",  "name": "[RESHADE] TONE DARK", "price": 35,  "role_id": 1448197995701993543, "category": "🎨 ReShade"},
    {"id": "item19", "emoji": "🍰",  "name": "[RESHADE] PEKKY", "price": 40,  "role_id": 1448263468355424298, "category": "🎨 ReShade"},
    {"id": "item20",  "emoji": "💎",  "name": "[RESHADE] REALISTICV1", "price": 25,  "role_id": 1431250097135419505, "category": "🎨 ReShade"},
    {"id": "item21",  "emoji": "🌈",  "name": "[RESHADE] REALISTICV2", "price": 25,  "role_id": 1431234346202959973, "category": "🎨 ReShade"},
    {"id": "item22",  "emoji": "🔥",  "name": "[RESHADE] REALISTICV3", "price": 25,  "role_id": 1431249584054734929, "category": "🎨 ReShade"},
    {"id": "item23", "emoji": "🎀",  "name": "[RESHADE] REALISTICV4", "price": 35,  "role_id": 1448142438131699722, "category": "🎨 ReShade"},
    {"id": "item24", "emoji": "🌌",  "name": "[RESHADE] REALISTICV5", "price": 35,  "role_id": 1448171343022526574, "category": "🎨 ReShade"},
    {"id": "item25", "emoji": "🍀",  "name": "[RESHADE] REALISTICV6", "price": 35,  "role_id": 1448171385942966392, "category": "🎨 ReShade"},
    {"id": "item26", "emoji": "🚣",  "name": "[RESHADE] REALISTIC𝚅7", "price": 35,  "role_id": 1448313586915999755, "category": "🎨 ReShade"},
    {"id": "item27", "emoji": "🍕",  "name": "[RESHADE] REALISTIC𝚅8", "price": 35,  "role_id": 1449643401908584490, "category": "🎨 ReShade"},
    {"id": "item28", "emoji": "🕵️‍♂️",  "name": "[RESHADE] REALISTIC𝚅9", "price": 35,  "role_id": 1449723125381206158, "category": "🎨 ReShade"},
    {"id": "item29", "emoji": "🐤",  "name": "[RESHADE] REALISTIC𝚅10", "price": 35,  "role_id": 1449723195740520459, "category": "🎨 ReShade"},
    {"id": "item30", "emoji": "🍯",  "name": "[RESHADE] REALISTIC𝚅11", "price": 35,  "role_id": 1449723197074440283, "category": "🎨 ReShade"},
    {"id": "item31", "emoji": "🦋",  "name": "[RESHADE] MMJ", "price": 35,  "role_id": 1449724755086147696, "category": "🎨 ReShade"},
    {"id": "item32", "emoji": "🐇",  "name": "[RESHADE] 𝖡𝖠𝖡𝖸 𝖦", "price": 40,  "role_id": 1449725249036877874, "category": "🎨 ReShade"},
    {"id": "item33", "emoji": "🍥",  "name": "[RESHADE] ✦colour﹒₊˚੭", "price": 40,  "role_id": 1449726152456409139, "category": "🎨 ReShade"},
]

# =================================================================
# 💾 DATABASE SYSTEM
# =================================================================
DB_FILE = "user_balance.json"
SLIP_DB_FILE = "used_slips.json"
TOTAL_DB_FILE = "total_topup.json"
LOG_MSG_DB = "log_messages.json"
RECEIPT_DB = "used_receipts.json"
KEYS_DB = "distributed_keys.json"

def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f: json.dump([] if "used" in filename or "keys" in filename else {}, f)
        return [] if "used" in filename or "keys" in filename else {}
    try:
        with open(filename, "r") as f: return json.load(f)
    except: return [] if "used" in filename or "keys" in filename else {}

def save_json(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# --- Shop DB Functions ---
def get_data(user_id):
    bal_db = load_json(DB_FILE)
    total_db = load_json(TOTAL_DB_FILE)
    uid = str(user_id)
    return {
        "balance": float(bal_db.get(uid, 0.0)),
        "total": float(total_db.get(uid, 0.0))
    }

def update_money(user_id, amount, is_topup=False):
    bal_db = load_json(DB_FILE)
    total_db = load_json(TOTAL_DB_FILE)
    uid = str(user_id)
    current_bal = float(bal_db.get(uid, 0.0))
    new_bal = current_bal + float(amount)
    bal_db[uid] = new_bal
    
    if is_topup and amount > 0:
        current_total = float(total_db.get(uid, 0.0))
        total_db[uid] = current_total + float(amount)
        save_json(TOTAL_DB_FILE, total_db)
        
    save_json(DB_FILE, bal_db)
    return new_bal

def is_slip_used(trans_ref):
    slips = load_json(SLIP_DB_FILE)
    if isinstance(slips, dict): slips = list(slips.keys())
    return trans_ref in slips

def save_used_slip(trans_ref):
    slips = load_json(SLIP_DB_FILE)
    if isinstance(slips, dict): slips = list(slips.keys())
    slips.append(trans_ref)
    with open(SLIP_DB_FILE, "w") as f: json.dump(slips, f, indent=4)

# --- Redeem DB Functions ---
def is_receipt_used(receipt_id):
    used = load_json(RECEIPT_DB)
    return receipt_id in used

def mark_receipt_used(receipt_id):
    used = load_json(RECEIPT_DB)
    if receipt_id not in used:
        used.append(receipt_id)
        save_json(RECEIPT_DB, used)

def is_key_distributed(key):
    used = load_json(KEYS_DB)
    return key in used

def mark_key_distributed(key):
    used = load_json(KEYS_DB)
    if key not in used:
        used.append(key)
        save_json(KEYS_DB, used)

# =================================================================
# 🤖 BOT INITIALIZATION
# =================================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# =================================================================
# ⚙️ SYSTEM FUNCTIONS
# =================================================================

def clean_text(text):
    if not text: return ""
    return re.sub(r'[^a-zA-Z0-9ก-๙]', '', str(text)).lower()

async def restore_database_from_logs(bot):
    print("🔄 Syncing database from Cyberpunk Logs...")
    channel = bot.get_channel(BALANCE_LOG_ID) 
    if not channel: return
    balances = load_json(DB_FILE)
    totals = load_json(TOTAL_DB_FILE)
    msg_ids = load_json(LOG_MSG_DB)
    count = 0
    async for message in channel.history(limit=None):
        if message.author.id != bot.user.id or not message.embeds: continue
        embed = message.embeds[0]
        user_id = None
        if embed.description:
            id_match = re.search(r"UID\s*=\s*(\d+)", embed.description)
            if id_match: user_id = id_match.group(1)
        if not user_id and embed.footer and embed.footer.text:
            id_match_old = re.search(r"ID: (\d+)", embed.footer.text)
            if id_match_old: user_id = id_match_old.group(1)
        if not user_id: continue

        for field in embed.fields:
            if "CREDIT" in field.name or "เงินคงเหลือ" in field.name:
                bal_match = re.search(r"([\d,]+\.?\d*)", field.value)
                if bal_match:
                    clean_bal = float(bal_match.group(1).replace(',', ''))
                    if float(balances.get(user_id, 0)) == 0: balances[user_id] = clean_bal
            if "LIFETIME" in field.name or "ยอดเติมสะสม" in field.name:
                total_match = re.search(r"([\d,]+\.?\d*)", field.value)
                if total_match:
                    clean_total = float(total_match.group(1).replace(',', ''))
                    if float(totals.get(user_id, 0)) == 0: totals[user_id] = clean_total
        msg_ids[user_id] = message.id
        count += 1
    save_json(DB_FILE, balances)
    save_json(TOTAL_DB_FILE, totals)
    save_json(LOG_MSG_DB, msg_ids)
    print(f"✅ กู้คืนข้อมูลสำเร็จ {count} รายการ")

def check_slip_easyslip(image_url):
    print(f"Checking slip: {image_url}")
    try:
        img_data = requests.get(image_url).content
        files = {'file': ('slip.jpg', io.BytesIO(img_data), 'image/jpeg')}
        
        response = requests.post(
            "https://developer.easyslip.com/api/v1/verify",
            headers={'Authorization': f'Bearer {EASYSLIP_API_KEY}'},
            files=files, timeout=15
        )
        data = response.json()

        if response.status_code == 200 and data['status'] == 200:
            slip = data['data']
            raw_amount = slip.get('amount', {}).get('amount', 0)
            amount = float(raw_amount)
            if amount < MIN_AMOUNT: 
                return False, 0, None, f"ยอดเงินต่ำกว่ากำหนด ({amount})"
            
            receiver_info = slip.get('receiver', {})
            api_names = [receiver_info.get('displayName'), receiver_info.get('name'), receiver_info.get('account', {}).get('name')]
            valid_api_names = [clean_text(n) for n in api_names if n]
            cleaned_expected = [clean_text(n) for n in EXPECTED_NAMES]
            
            is_name_match = False
            for api_name in valid_api_names:
                for expected in cleaned_expected:
                    if expected in api_name or api_name in expected:
                        is_name_match = True
                        break
                if is_name_match: break

            if not is_name_match:
                return False, 0, None, f"ชื่อบัญชีไม่ตรง ({receiver_info.get('displayName', 'Unknown')})"

            d_str = str(slip.get('date', '')); t_str = str(slip.get('time', ''))
            dt_str = f"{d_str} {t_str}".replace("T", " ").split("+")[0].split(".")[0]
            slip_dt = None
            for fmt in ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M"]:
                try: slip_dt = datetime.strptime(dt_str, fmt); break
                except: continue
            
            if slip_dt:
                if slip_dt.year > 2500: slip_dt = slip_dt.replace(year=slip_dt.year - 543)
                now = datetime.utcnow() + timedelta(hours=7)
                diff = (now - slip_dt).total_seconds() / 60 
                if diff > 5: return False, 0, None, "สลิปไม่สามารถใช้งานได้" 
                if diff < -5: return False, 0, None, "สลิปไม่สามารถใช้งานได้"
            return True, amount, slip['transRef'], "OK"
        else:
            return False, 0, None, data.get('message', 'อ่าน QR ไม่ได้ / ไม่ใช่สลิป')
    except Exception as e:
        return False, 0, None, f"System Error: {str(e)}"

# 🔥 GIST: ระบบแก้ไฟล์อัจฉริยะ (วนลูปหาไฟล์สินค้าเอง)
def update_gist_hwid(target_key, new_hwid):
    try:
        g = Github(GITHUB_TOKEN)
        
        # วนลูปเช็คสินค้าทุกตัวในร้าน
        for product_name, link in PRODUCT_LINKS.items():
            try:
                parts = link.split('/')
                current_gist_id = parts[4]
                current_filename = parts[-1]
            except: continue

            try:
                gist = g.get_gist(current_gist_id)
                file = gist.files[current_filename]
                content = file.content
            except: continue

            if target_key not in content: continue

            new_lines = []
            found = False
            already_bind = False
            
            for line in content.splitlines():
                clean_line = line.strip()
                if not clean_line: continue
                
                parts_line = clean_line.split(',')
                current_key_in_file = parts_line[0].strip()
                
                if current_key_in_file == target_key:
                    found = True
                    old_hwid = parts_line[1].strip() if len(parts_line) > 1 else ""
                    
                    if old_hwid == "" or old_hwid == "RESET": # ✅ เพิ่มเงื่อนไข ถ้าเป็น RESET ก็ให้แก้ทับ
                        new_lines.append(f"{current_key_in_file},{new_hwid}")
                    else:
                        new_lines.append(clean_line)
                        already_bind = True
                else:
                    new_lines.append(clean_line)
            
            if found:
                if already_bind:
                    # ถ้า HWID เดิมไม่ตรงกับอันใหม่ แปลว่ามีคนใช้อยู่แล้ว
                    return False, f"⚠️ คีย์นี้มีเจ้าของแล้ว! ({product_name})"
                
                final_content = "\n".join(new_lines)
                # ใช้ InputFileContent จาก library github
                gist.edit(files={current_filename: InputFileContent(final_content)})
                return True, f"✅ **AUTO BIND:** ผูก HWID สำเร็จ!\nสินค้า: `{product_name}`"

        return False, f"❌ ไม่พบคีย์ `{target_key}` ในระบบทุกสินค้า"

    except Exception as e:
        return False, f"GitHub Error: {str(e)}"

# --- REDEEM LOGIC ---
def fetch_available_key(pastebin_url):
    try:
        response = requests.get(pastebin_url)
        if response.status_code != 200: return None, "Link Error"
        lines = response.text.splitlines()
        for line in lines:
            line = line.strip()
            if not line: continue
            parts = line.split(',')
            if len(parts) >= 1:
                key = parts[0].strip()
                hwid = parts[1].strip() if len(parts) > 1 else ""
                if hwid == "" and not is_key_distributed(key):
                    return key, "OK"
        return None, "No Keys Left" 
    except Exception as e:
        return None, str(e)

async def verify_receipt(bot, receipt_id):
    # ⚠️ ใช้ห้อง PURCHASE_LOG_ID เพื่อเช็คออเดอร์
    log_channel = bot.get_channel(PURCHASE_LOG_ID) 
    if not log_channel: return False, None, "Log Channel Not Found"
    async for message in log_channel.history(limit=300):
        if not message.embeds: continue
        embed = message.embeds[0]
        content = str(embed.description) + str(embed.footer.text if embed.footer else "")
        clean_input_id = receipt_id.replace("#", "").strip()
        if clean_input_id in content:
            item_match = re.search(r"ITEM\s*:\s*(.+)", content)
            if item_match:
                product_name = item_match.group(1).strip()
                product_name = product_name.replace("`", "") 
                return True, product_name, "Found"
    return False, None, "Receipt Not Found"

# =================================================================
# 🎨 UI SYSTEM (ADMIN PANEL)
# =================================================================

# 1. กล่องกรอก HWID (เด้งขึ้นมาเมื่อกดปุ่ม Bind)
class HwidInputModal(discord.ui.Modal, title="🔗 BIND HWID"):
    def __init__(self, key):
        super().__init__()
        self.target_key = key
        self.hwid = discord.ui.TextInput(label="ENTER HWID", placeholder="วาง HWID ของลูกค้าที่นี่", min_length=5)
        self.add_item(self.hwid)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        hwid_val = self.hwid.value.strip()
        success, msg = update_gist_hwid(self.target_key, hwid_val)
        color = discord.Color.green() if success else discord.Color.red()
        await interaction.followup.send(embed=discord.Embed(description=msg, color=color), ephemeral=True)

# 2. ปุ่ม BIND HWID (อยู่ใต้ Embed รายละเอียดออเดอร์)
class HwidActionView(discord.ui.View):
    def __init__(self, key):
        super().__init__(timeout=None)
        self.key = key

    @discord.ui.button(label="🔗 BIND HWID", style=discord.ButtonStyle.success)
    async def bind_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HwidInputModal(self.key))

# 3. กล่องค้นหา Order (เด้งเมื่อกด Search)
class OrderSearchModal(discord.ui.Modal, title="🔍 SEARCH ORDER"):
    order_id = discord.ui.TextInput(label="RECEIPT ID", placeholder="#xxxxxx", min_length=3)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        target_oid = self.order_id.value.replace("#", "").strip().upper()
        
        # ค้นหาในห้อง Log แลกคีย์ (เพราะคีย์อยู่ที่นี่)
        log_channel = interaction.guild.get_channel(REDEEM_LOG_ID)
        if not log_channel:
            return await interaction.followup.send("❌ หาห้อง Redeem Log ไม่เจอ", ephemeral=True)

        found_data = None
        async for msg in log_channel.history(limit=500):
            if not msg.embeds: continue
            embed = msg.embeds[0]
            desc = embed.description or ""
            
            # ใช้ Regex ดึงข้อมูลจาก Log เก่า
            if target_oid in desc:
                key_match = re.search(r"KEY\s*=\s*(.+)", desc)
                user_match = re.search(r"USER\s*=\s*(.+)", desc)
                prod_match = re.search(r"PRODUCT\s*=\s*(.+)", desc)
                
                if key_match:
                    found_data = {
                        "key": key_match.group(1).strip(),
                        "user": user_match.group(1).strip() if user_match else "Unknown",
                        "product": prod_match.group(1).strip() if prod_match else "Unknown"
                    }
                    break
        
        if found_data:
            res_embed = discord.Embed(title="🧾 ORDER DETAILS", color=CYBER_COLOR)
            res_embed.description = (
                f"```ini\n"
                f"[ ORDER FOUND ]\n"
                f"ID        = #{target_oid}\n"
                f"USER      = {found_data['user']}\n"
                f"PRODUCT   = {found_data['product']}\n"
                f"KEY       = {found_data['key']}\n"
                f"```"
            )
            await interaction.followup.send(embed=res_embed, view=HwidActionView(found_data['key']), ephemeral=True)
        else:
            await interaction.followup.send(f"❌ ไม่พบออเดอร์ `#{target_oid}` ในประวัติการแลกคีย์", ephemeral=True)

# 4. ปุ่มหลักในหน้า Admin Panel
class HwidManagerView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="SEARCH ORDER", style=discord.ButtonStyle.primary, emoji="🔍", custom_id="admin_search_order")
    async def search(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator: return
        await interaction.response.send_modal(OrderSearchModal())

# =================================================================
# 🎨 UI SYSTEM (SHOP & USER)
# =================================================================

class AddMoneyModal(discord.ui.Modal, title="💸 MANUAL ADD BALANCE"):
    target = discord.ui.TextInput(label="User ID or Tag", placeholder="เช่น 123456789 หรือ @laikatfl", min_length=1)
    amount = discord.ui.TextInput(label="Amount (THB)", placeholder="เช่น 100", min_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ **ACCESS DENIED**", ephemeral=True)
        try:
            raw_target = self.target.value
            user_id_match = re.search(r'\d+', raw_target)
            if not user_id_match:
                return await interaction.response.send_message("❌ **INVALID USER:** ไม่พบ ID", ephemeral=True)
            user_id = int(user_id_match.group())
            amount = float(self.amount.value)
            target_user = interaction.guild.get_member(user_id)
            target_name = target_user.name if target_user else f"Unknown ({user_id})"
            new_bal = update_money(user_id, amount, is_topup=True)
            await update_user_log(interaction.client, user_id)
            if log_channel := interaction.guild.get_channel(ADD_MONEY_LOG_ID):
                embed = discord.Embed(title="🔧 MANUAL ADJUSTMENT | เพิ่มเงิน", color=discord.Color.green())
                embed.description = (
                    f"```ini\n"
                    f"[ TRANSACTION RECORD ]\n"
                    f"ADMIN     = {interaction.user.name}\n"
                    f"TARGET    = {target_name}\n"
                    f"UID       = {user_id}\n"
                    f"AMOUNT    = +{amount:,.2f} THB\n"
                    f"BALANCE   = {new_bal:,.2f} THB\n"
                    f"TIME      = {datetime.now().strftime('%H:%M:%S')}\n"
                    f"```"
                )
                embed.set_footer(text="System Manual Adjustment")
                embed.set_thumbnail(url=target_user.display_avatar.url if target_user else None)
                await log_channel.send(embed=embed)
            await interaction.response.send_message(f"✅ เพิ่มเงิน `{amount} THB` ให้ <@{user_id}> สำเร็จ!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ **ERROR:** ใส่จำนวนเงินเป็นตัวเลขเท่านั้น", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ **ERROR:** {str(e)}", ephemeral=True)

class DashboardView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="FORCE SYNC DATA", style=discord.ButtonStyle.danger, custom_id="admin_sync", emoji="🔄")
    async def update_db(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator: return
        await interaction.response.defer(ephemeral=True)
        await restore_database_from_logs(interaction.client) 
        await update_all_user_logs(interaction.client)
        await interaction.followup.send("✅ System Synced Successfully!")

    @discord.ui.button(label="ADD BALANCE", style=discord.ButtonStyle.success, custom_id="admin_add_money", emoji="💸")
    async def add_money_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator: return
        await interaction.response.send_modal(AddMoneyModal())

async def update_user_log(bot, user_id):
    log_channel = bot.get_channel(BALANCE_LOG_ID)
    if not log_channel: return
    data = get_data(user_id)
    if data['total'] <= 0 and data['balance'] <= 0: return
    user = bot.get_user(int(user_id))
    user_name = user.name if user else f"USER_{user_id}"
    embed = discord.Embed(color=THEME_COLOR)
    embed.description = f"```ini\n[ USER DATABASE RECORD ]\nUID       = {user_id}\nUSERNAME = {user_name}```"
    embed.add_field(name="💳 CURRENT CREDIT", value=f"```fix\n฿ {data['balance']:,.2f}```", inline=True)
    embed.add_field(name="📈 LIFETIME TOPUP", value=f"```yaml\n฿ {data['total']:,.2f}```", inline=True)
    embed.set_footer(text=f"LAST UPDATE: {datetime.now().strftime('%H:%M:%S')}")
    msg_db = load_json(LOG_MSG_DB)
    msg_id = msg_db.get(str(user_id))
    if msg_id:
        try:
            msg = await log_channel.fetch_message(msg_id)
            await msg.edit(embed=embed)
            return
        except: pass
    msg = await log_channel.send(embed=embed)
    msg_db[str(user_id)] = msg.id
    save_json(LOG_MSG_DB, msg_db)

async def update_all_user_logs(bot):
    for uid in load_json(DB_FILE):
        await update_user_log(bot, uid)
        await asyncio.sleep(0.5)

# --- SHOPPING UI (NEW APP STORE STYLE) ---

class ProductConfirmView(discord.ui.View):
    def __init__(self, product, user_id):
        super().__init__(timeout=60)
        self.product = product
        self.user_id = user_id

    @discord.ui.button(label="CONFIRM PURCHASE", style=discord.ButtonStyle.success, emoji="🛒")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        await interaction.response.defer()
        data = get_data(interaction.user.id)
        price = self.product["price"]
        if data['balance'] < price:
            embed = discord.Embed(description=f"⚠️ **INSUFFICIENT FUNDS**\nNeed: `{price - data['balance']:.2f} THB`", color=ERROR_COLOR)
            return await interaction.followup.send(embed=embed, ephemeral=True)
        update_money(interaction.user.id, -price)
        role = interaction.guild.get_role(self.product["role_id"])
        if role: await interaction.user.add_roles(role)
        await update_user_log(interaction.client, interaction.user.id)
        order_id = str(uuid.uuid4())[:8].upper()
        
        embed = discord.Embed(title="✅ TRANSACTION SUCCESSFUL", color=SUCCESS_COLOR)
        embed.description = (
            f"```yaml\n"
            f"RECEIPT ID : #{order_id}\n"
            f"DATE        : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"CUSTOMER    : {interaction.user.name}\n"
            f"------------------------------\n"
            f"ITEM        : {self.product['name']}\n"
            f"PRICE       : {price:.2f} THB\n"
            f"BALANCE     : {data['balance'] - price:.2f} THB\n"
            f"```"
            f"👤 **Customer:** <@{interaction.user.id}>"
        )
        embed.set_thumbnail(url=SUCCESS_GIF_URL)
        embed.set_footer(text="Thank you for your purchase", icon_url=interaction.user.display_avatar.url)
        await interaction.edit_original_response(content=None, embed=embed, view=None)
        
        if log := interaction.guild.get_channel(PURCHASE_LOG_ID):
            await log.send(embed=embed)

    @discord.ui.button(label="CANCEL", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await interaction.response.edit_message(content="❌ Transaction Cancelled", embed=None, view=None)

# 1. หน้าแสดงรายละเอียดสินค้า (หน้าสุดท้าย)
class ProductDetailView(discord.ui.View):
    def __init__(self, product):
        super().__init__(timeout=None)
        self.product = product

    @discord.ui.button(label="🛒 BUY NOW", style=discord.ButtonStyle.success, emoji="💳")
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=discord.Embed(description=f"กำลังสั่งซื้อ: **{self.product['name']}**", color=SUCCESS_COLOR),
            view=ProductConfirmView(self.product, interaction.user.id),
            ephemeral=True
        )

    @discord.ui.button(label="🔙 BACK TO LIST", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title=f"📂 หมวดหมู่: {self.product['category']}", 
                description="🔻 **เลือกสินค้าจากเมนูด้านล่าง:**", 
                color=THEME_COLOR
            ),
            view=ProductSelectView(self.product['category'])
        )

# 2. หน้าเลือกสินค้าในหมวดนั้นๆ (หน้ารอง)
class ProductDropdown(discord.ui.Select):
    def __init__(self, category):
        self.filtered_products = [p for p in PRODUCTS if p['category'] == category]
        
        options = []
        for prod in self.filtered_products:
            options.append(discord.SelectOption(
                label=prod["name"][:95], 
                description=f"💵 ราคา: {prod['price']} THB",
                emoji=prod["emoji"],
                value=prod["id"]
            ))
        
        super().__init__(
            placeholder=f"🔍 เลือกสินค้าในหมวด {category}...", 
            min_values=1, 
            max_values=1, 
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_id = self.values[0]
        product = next((p for p in self.filtered_products if p["id"] == selected_id), None)
        
        embed = discord.Embed(title=f"{product['emoji']} {product['name']}", color=ACCENT_COLOR)
        embed.description = (
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏷️ **CATEGORY:** `{product['category']}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✨ **DESCRIPTION:**\n"
            "> สินค้าคุณภาพ ส่งมอบทันทีด้วยระบบอัตโนมัติ\n"
            "> รับประกันความพึงพอใจ 100%\n"
        )
        embed.add_field(name="💵 PRICE", value=f"```fix\n฿ {product['price']:.2f}```", inline=True)
        embed.add_field(name="📦 STOCK", value="`✅ Ready`", inline=True)
        embed.set_image(url=SHOP_BANNER_URL)
        embed.set_footer(text=f"Product ID: {product['id']}")
        
        await interaction.response.edit_message(embed=embed, view=ProductDetailView(product))

class ProductSelectView(discord.ui.View):
    def __init__(self, category):
        super().__init__(timeout=None)
        self.add_item(ProductDropdown(category))
        
    @discord.ui.button(label="🏠 MAIN MENU", style=discord.ButtonStyle.danger, row=1)
    async def home(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🗂️ SHOP CATEGORIES",
            description="📂 **กรุณาเลือกหมวดหมู่สินค้า:**",
            color=THEME_COLOR
        )
        if SHOP_BANNER_URL.startswith("http"): embed.set_thumbnail(url=SHOP_BANNER_URL)
        await interaction.response.edit_message(embed=embed, view=CategorySelectView())

# 3. หน้าเลือกหมวดหมู่ (หน้าแรกสุด)
class CategoryDropdown(discord.ui.Select):
    def __init__(self):
        categories = sorted(list(set(p['category'] for p in PRODUCTS)))
        
        options = []
        for cat in categories:
            options.append(discord.SelectOption(
                label=cat, 
                description="คลิกเพื่อดูสินค้าภายในหมวดนี้",
                emoji="📁"
            ))
            
        super().__init__(
            placeholder="🔻 กรุณาเลือกหมวดหมู่สินค้า... (Select Category)",
            min_values=1, 
            max_values=1, 
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_cat = self.values[0]
        await interaction.response.edit_message(
            embed=discord.Embed(
                title=f"📂 หมวดหมู่: {selected_cat}", 
                description="🔻 **เลือกสินค้าจากเมนูด้านล่าง:**", 
                color=THEME_COLOR
            ),
            view=ProductSelectView(selected_cat)
        )

class CategorySelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CategoryDropdown())

# --- REDEEM UI & VIEWS ---

class RedeemModal(discord.ui.Modal, title="🔐 REDEEM LICENSE KEY"):
    receipt_id = discord.ui.TextInput(
        label="RECEIPT ID (ดูในสลิปที่บอทส่งให้)", 
        placeholder="เช่น #5B058D5F", 
        min_length=5, 
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        rid = self.receipt_id.value.strip().upper()
        clean_rid = rid.replace("#", "")
        if is_receipt_used(clean_rid):
            await interaction.followup.send(f"❌ **ERROR:** ออเดอร์นี้ `{rid}` ถูกใช้งานไปแล้ว!", ephemeral=True)
            return
        
        found, product_name, msg = await verify_receipt(interaction.client, clean_rid)
        if not found:
            await interaction.followup.send(f"❌ **ERROR:** ไม่พบเลข Order `{rid}` ในระบบ\nโปรดตรวจสอบความถูกต้อง หรือรอระบบอัปเดตสักครู่", ephemeral=True)
            return
        pastebin_url = PRODUCT_LINKS.get(product_name)
        if not pastebin_url:
            await interaction.followup.send(f"⚠️ สินค้า `{product_name}` ไม่ใช่สินค้าประเภท Key หรือยังไม่ได้ลงทะเบียน", ephemeral=True)
            return
        key, status = fetch_available_key(pastebin_url)
        if not key:
            await interaction.followup.send(f"😭 **ขออภัย:** สินค้า `{product_name}` คีย์หมดชั่วคราว\nโปรดติดต่อแอดมินเพื่อเติมของ", ephemeral=True)
            if log := interaction.guild.get_channel(REDEEM_LOG_ID):
                await log.send(f"⚠️ **OUT OF STOCK ALERT:** {product_name} (User tried to redeem)")
            return
        mark_receipt_used(clean_rid)
        mark_key_distributed(key)
        try:
            dm_embed = discord.Embed(title="📦 PRODUCT DELIVERY", color=SUCCESS_COLOR)
            dm_embed.description = (
                f"**PRODUCT:** `{product_name}`\n"
                f"**ORDER ID:** `#{clean_rid}`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔑 **YOUR KEY:**\n```\n{key}\n```\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "⚠️ *คีย์นี้ถูกล็อคกับบัญชีของคุณแล้ว ห้ามทำหาย*"
            )
            dm_embed.set_footer(text="Thank you for your support!")
            await interaction.user.send(embed=dm_embed)
            dm_status = "✅ Sent via DM"
        except:
            dm_status = "❌ DM Closed (Sent here)"
        
        success_embed = discord.Embed(title="✅ REDEEM SUCCESSFUL", color=SUCCESS_COLOR)
        success_embed.description = f"รับคีย์สำหรับ **{product_name}** สำเร็จ!\n(ตรวจสอบใน DM ของคุณ)"
        if "Closed" in dm_status:
            success_embed.description += f"\n\n🔑 **YOUR KEY:**\n```{key}```"
        
        await interaction.followup.send(embed=success_embed, ephemeral=True)
        
        if log_channel := interaction.guild.get_channel(REDEEM_LOG_ID):
            log_embed = discord.Embed(title="🔐 KEY REDEEMED LOG", color=CYBER_COLOR)
            log_embed.description = (
                f"```ini\n"
                f"[ REDEEM TRANSACTION ]\n"
                f"USER      = {interaction.user.name} ({interaction.user.id})\n"
                f"ORDER     = #{clean_rid}\n"
                f"PRODUCT   = {product_name}\n"
                f"KEY       = {key}\n"
                f"TIME      = {datetime.now().strftime('%H:%M:%S')}\n"
                f"```"
            )
            log_embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await log_channel.send(embed=log_embed)

class RedeemView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="กดเพื่อรับคีย์ (REDEEM KEY)", style=discord.ButtonStyle.primary, emoji="🎁", custom_id="redeem_btn")
    async def redeem(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RedeemModal())

# --- MAIN DASHBOARD ---

class TopupModal(discord.ui.Modal, title="💸 TOPUP - เติมเงิน"):
    amount = discord.ui.TextInput(label="จำนวนเงิน (บาท)", placeholder="เช่น 50, 100", min_length=1, max_length=6)
    async def on_submit(self, interaction: discord.Interaction):
        try: val = float(self.amount.value)
        except: return await interaction.response.send_message("❌ กรุณาใส่ตัวเลขเท่านั้น", ephemeral=True)
        embed = discord.Embed(title="✨ PAYMENT INVOICE | ใบแจ้งยอด", color=TOPUP_COLOR)
        embed.description = (
            f"# 💵 ยอดชำระ: `{val:.2f} THB`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "**📲 ขั้นตอนการชำระเงิน**\n"
            "> 1. สแกน QR Code ด้านล่าง\n"
            f"> 2. ส่งรูปสลิปในห้อง <#{SLIP_CHANNEL_ID}>\n"
            "> 3. รอระบบตรวจสอบ 5-10 วินาที\n"
            "> 4. ทำการส่งสลีปภายใน 5 นาที\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        embed.set_image(url=QR_CODE_URL)
        embed.set_footer(text="ระบบอัตโนมัติ 24 ชม. • Powered by LAIKA", icon_url=interaction.client.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MainShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="BROWSE PRODUCTS", style=discord.ButtonStyle.primary, emoji="🛒", custom_id="browse_btn", row=0)
    async def browse(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🗂️ SHOP CATEGORIES | หมวดหมู่สินค้า",
            description="📂 **กรุณาเลือกประเภทสินค้าที่คุณต้องการจากเมนูด้านล่าง**\n(Select a category to view products)",
            color=THEME_COLOR
        )
        if SHOP_BANNER_URL.startswith("http"): embed.set_thumbnail(url=SHOP_BANNER_URL)
        
        # เรียกใช้หน้าเลือกหมวดหมู่ (หน้าแรกของระบบใหม่)
        await interaction.response.send_message(embed=embed, view=CategorySelectView(), ephemeral=True)

    @discord.ui.button(label="TOP UP", style=discord.ButtonStyle.success, emoji="💳", custom_id="topup_btn", row=0)
    async def topup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TopupModal())

    @discord.ui.button(label="MY PROFILE", style=discord.ButtonStyle.secondary, emoji="👤", custom_id="profile_btn", row=1)
    async def profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = get_data(interaction.user.id)
        total = data['total']
        rank = "MEMBER"
        if total > 500: rank = "DIAMOND 💎"
        elif total > 100: rank = "GOLD 🏆"
        elif total > 50: rank = "SILVER 🥈"
        embed = discord.Embed(title="💳 MEMBER CARD", color=THEME_COLOR)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="OWNER", value=f"{interaction.user.mention}", inline=True)
        embed.add_field(name="RANK", value=f"`{rank}`", inline=True)
        embed.add_field(name="WALLET BALANCE", value=f"```fix\n฿ {data['balance']:,.2f}```", inline=False)
        embed.add_field(name="TOTAL SPENT", value=f"```yaml\n฿ {data['total']:,.2f}```", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class GiveawayView(discord.ui.View):
    def __init__(self, amount, max_winners, creator_id):
        super().__init__(timeout=None)
        self.amount = amount
        self.max_winners = max_winners
        self.creator_id = creator_id
        self.claimed_users = []

    def update_button(self):
        btn = self.children[0]
        if len(self.claimed_users) >= self.max_winners:
            btn.label = "🔴 MISSION COMPLETED (เต็มแล้ว)"
            btn.style = discord.ButtonStyle.danger
            btn.disabled = True
            btn.emoji = "🔒"
        else:
            btn.label = f"CLAIM {self.amount} THB ({len(self.claimed_users)}/{self.max_winners})"
            btn.style = discord.ButtonStyle.success
            btn.emoji = "🎁"

    @discord.ui.button(label="CLAIM REWARD", style=discord.ButtonStyle.success, emoji="🎁", custom_id="airdrop_claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.claimed_users:
            return await interaction.response.send_message("❌ **ACCESS DENIED:** คุณรับสิทธิ์ไปแล้ว!", ephemeral=True)
        if len(self.claimed_users) >= self.max_winners:
            return await interaction.response.send_message("❌ **MISSION FAILED:** สิทธิ์เต็มแล้ว!", ephemeral=True)
        self.claimed_users.append(interaction.user.id)
        
        # 1. Update JSON (Database)
        update_money(interaction.user.id, self.amount, is_topup=True)
        
        # 2. Update Visual Database (ห้องเก็บยอดเงินรวม)
        await update_user_log(interaction.client, interaction.user.id)

        # 3. Log to History (ห้องประวัติเพิ่มเงิน)
        if log := interaction.guild.get_channel(ADD_MONEY_LOG_ID):
             await log.send(f"🎁 **[AIRDROP CLAIM]** {interaction.user.name} ได้รับ `{self.amount} THB`")

        await interaction.response.send_message(f"✅ **SYSTEM:** โอน `{self.amount} THB` เข้าบัญชีสำเร็จ!", ephemeral=True)
        self.update_button()
        if len(self.claimed_users) >= self.max_winners:
            embed = interaction.message.embeds[0]
            embed.color = 0x2b2d31 
            embed.title = "🏁 EVENT ENDED | จบกิจกรรม"
            embed.description = f"```diff\n- QUOTA REACHED ({self.max_winners}/{self.max_winners})\n- REWARD: {self.amount} THB```\nขอบคุณที่ร่วมสนุก! รอติดตามรอบหน้า"
            embed.set_image(url=None) 
            await interaction.message.edit(embed=embed, view=self)
        else:
            await interaction.message.edit(view=self)

@bot.tree.command(name="create_airdrop", description="[Admin] แจกเงินฟรี (AirDrop)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(amount="จำนวนเงินที่จะแจกต่อคน", winners="จำนวนคนที่รับได้", notify="แท็ก everyone ไหม?")
async def create_airdrop(interaction: discord.Interaction, amount: float, winners: int, notify: bool = False):
    if amount < 1 or winners < 1:
        return await interaction.response.send_message("❌ จำนวนเงินหรือผู้รับต้องมากกว่า 0", ephemeral=True)
    embed = discord.Embed(title="🚀 CYBER AIRDROP INCOMING!", color=0x00ff41) 
    embed.description = (
        f"# 💸 แจกพ้อยฟรี: `{amount:.2f} THB`\n"
        f"**⚡ จำนวนจำกัด:** `{winners} ท่านแรก` เท่านั้น!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**🎯 MISSION:**\n"
        "> กดปุ่มสีเขียวด้านล่างให้ทัน!\n"
        "> *มาก่อนได้ก่อน (First Come First Served)*"
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1233098937632817233/1444077217230491731/Fire_Force_Sho_Kusakabe_GIF.gif") 
    embed.set_footer(text=f"Sponsored by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    view = GiveawayView(amount, winners, interaction.user.id)
    view.update_button() 
    content_msg = "@everyone 🚨 **AIRDROP ALERT!** มารับเงินฟรีเร็ววว!" if notify else "🚨 **AIRDROP ALERT!**"
    await interaction.channel.send(content=content_msg, embed=embed, view=view)
    await interaction.response.send_message("✅ สร้างกิจกรรมเรียบร้อย!", ephemeral=True)

# คำสั่งใหม่: สร้างหน้าจอ HWID MANAGER
@bot.tree.command(name="setup_hwid_panel", description="[Admin] สร้างหน้าจอจัดการ HWID")
@app_commands.default_permissions(administrator=True)
async def setup_hwid_panel(interaction: discord.Interaction):
    embed = discord.Embed(title="🎛️ HWID MANAGER CONSOLE", color=THEME_COLOR)
    embed.description = (
        "**SYSTEM STATUS:** `ONLINE` 🟢\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**HOW TO USE:**\n"
        "1. กดปุ่ม `🔍 SEARCH ORDER`\n"
        "2. กรอกเลข Order (เช่น #A1B2C3)\n"
        "3. ระบบจะแสดงข้อมูลคีย์ที่ลูกค้าได้รับ\n"
        "4. กดปุ่ม `🔗 BIND HWID` เพื่อแก้ไฟล์ GitHub\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1233098937632817233/1444077217230491731/Fire_Force_Sho_Kusakabe_GIF.gif")
    
    await interaction.channel.send(embed=embed, view=HwidManagerView())
    await interaction.response.send_message("✅ Created Admin Panel", ephemeral=True)

# คำสั่งใหม่: สร้างหน้าจอ DASHBOARD (FORCE SYNC & ADD MONEY)
@bot.tree.command(name="setup_dashboard", description="[Admin] Create Control Panel")
@app_commands.default_permissions(administrator=True)
async def setup_dashboard(interaction: discord.Interaction):
    if interaction.channel_id != DASHBOARD_CMD_CHANNEL_ID:
        return await interaction.response.send_message("❌ ผิดห้อง (Wrong Channel)", ephemeral=True)
    
    embed = discord.Embed(title="🎛️ ADMIN DASHBOARD", color=THEME_COLOR)
    embed.description = (
        "**DATA CONTROL CENTER**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "**TOOLS:**\n"
        "🔄 `FORCE SYNC`: กู้คืน Database จากห้อง Logs\n"
        "💸 `ADD BALANCE`: เติมเงินให้ลูกค้า (Manual)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await interaction.channel.send(embed=embed, view=DashboardView())
    await interaction.response.send_message("✅ Dashboard Panel Created", ephemeral=True)

@bot.tree.command(name="setup_shop")
async def setup_shop(interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title="⚡ NEW PROJECT!!", color=THEME_COLOR)
    embed.description = (
        "# 🕹️ ＷＥＬＣＯＭＥ　ＴＯ　ＴＨＥ　ＮＥＷ　ＰＲＯＪＥＣＴ\n"
        "> *Insert coin to continue... Status: ONLINE! 🟢*\n\n"
        "ยินดีต้อนรับสู่โลกดิจิทัลยุค 90s ร้านค้าอัตโนมัติสไตล์คลาสสิก\n"
        "พร้อมให้บริการตลอด 24 ชั่วโมง ไม่มีวันปิดเครื่อง!\n\n"
        "**📺 ＭＡＩＮ　ＭＥＮＵ　（เมนูหลัก）**\n"
        "```ini\n"
        "[1] 💿 INSERT COIN   : เติมเงินเครดิต (Top Up)\n"
        "[2] 🍿 SELECT GAME   : เลือกซื้อสินค้า (Browse Shop)\n"
        "[3] 📟 PLAYER STATS  : เช็คยอดเงินคงเหลือ (Profile)\n"
        "```\n"
        "**🥤 ＳＥＲＶＩＣＥ　ＧＵＩＤＥ （วิธีใช้งาน）**\n"
        "1. กดปุ่ม `💳 TOP UP` เพื่อหยอดเหรียญ (เติมเงินผ่าน QR)\n"
        "2. กดปุ่ม `🛒 BROWSE` เพื่อเลือกตลับเกมที่ต้องการ\n"
        "3. ระบบจะส่ง Item เข้าตัวละครทันที! (Auto Delivery)\n\n"
        "-----------------------------------\n"
        "💾 **AUTO SAVE SYSTEM:** ข้อมูลของท่านถูกบันทึกอัตโนมัติ\n"
        "🌌 **A E S T H E T I C S:** ช้อปปิ้งชิลๆ กับบรรยากาศ Vaporwave"
    )
    if SHOP_BANNER_URL.startswith("http"): embed.set_image(url=SHOP_BANNER_URL)
    await interaction.channel.send(embed=embed, view=MainShopView())
    await interaction.followup.send("✅ Shop Interface Deployed!", ephemeral=True)

@bot.tree.command(name="setup_redeem", description="[Admin] Create Redeem Key Panel")
@app_commands.default_permissions(administrator=True)
async def setup_redeem(interaction):
    if interaction.channel_id != REDEEM_CHANNEL_ID:
        return await interaction.response.send_message("❌ ผิดห้อง", ephemeral=True)
    embed = discord.Embed(title="🔐 REDEEM CENTER", color=0xff0055) 
    embed.description = (
        "# 📥 ＩＴＥＭ　ＲＥＤＥＥＭ　ＺＯＮＥ\n"
        "> *Accessing database... Status: WAITING FOR KEY... [REC]* 🔴\n\n"
        "จุดแลกเปลี่ยนไอเทมและรางวัล ระบบอัตโนมัติความเร็วสูง\n"
        "นำรหัสใบเสร็จ (Receipt ID) มาแลกรับของได้ที่นี่!\n\n"
        "**👾 ＨＯＷ　ＴＯ　ＵＳＥ （วิธีใช้งาน）**\n"
        "```ini\n"
        "[1] 🎫 CHECK RECEIPT : ดูเลข Receipt ID จากสลิป (เช่น #BA5590)\n"
        "[2] 🔘 PUSH START    : กดปุ่ม \"🎁 กดเพื่อรับคีย์\" ด้านล่าง\n"
        "[3] ⌨️ ENTER CODE    : กรอกเลข Order ลงในช่องให้ถูกต้อง\n"
        "[4] 📨 GET ITEM       : เช็คกล่องจดหมาย (DM) เพื่อรับของ\n"
        "```\n"
        "**⚠️ ＳＹＳＴＥＭ　ＷＡＲＮＩＮＧ （ข้อควรระวัง）**\n"
        "• **1 Order = 1 Life** (รับได้เพียง 1 ครั้งต่อ 1 ออเดอร์เท่านั้น)\n"
        "• หากพบ Bug หรือ Error โปรดติดต่อ Game Master (Admin)\n\n"
        "-----------------------------------\n"
        "💾 **DATA ENCRYPTED:** ข้อมูลของท่านปลอดภัย 100%\n"
        "🌌 **T H A N K S　F O R　P L A Y I N G**"
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1233098937632817233/1444077217230491731/Fire_Force_Sho_Kusakabe_GIF.gif")
    await interaction.channel.send(embed=embed, view=RedeemView())
    await interaction.response.send_message("✅ Redeem Panel Created", ephemeral=True)

@bot.tree.command(name="add_money")
async def add_money(interaction, user: discord.Member, amount: float):
    new_bal = update_money(user.id, amount, is_topup=True)
    await update_user_log(interaction.client, user.id)
    embed = discord.Embed(description=f"✅ **ADDED** `{amount} THB` to {user.mention}\nNew Balance: `{new_bal} THB`", color=SUCCESS_COLOR)
    await interaction.response.send_message(embed=embed)
    
    if log := bot.get_channel(ADD_MONEY_LOG_ID):
        await log.send(f"🔧 **[MANUAL ADJ]** {interaction.user.name} added {amount} to {user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        # 🔥🔥🔥 ส่วนสำคัญ: ดักจับ Log Login เพื่อ Auto Bind HWID 🔥🔥🔥
        if message.channel.id == LOGIN_LOG_ID and message.embeds:
            try:
                embed = message.embeds[0]
                # เช็คหัวข้อว่าเป็น Login Success ไหม
                if "LOGIN SUCCESSFUL" in str(embed.title).upper():
                    key = None
                    hwid = None
                    
                    # วนลูปหา Field ที่เป็น Key และ HWID
                    for field in embed.fields:
                        if "License Key" in field.name:
                            # ลบ ``` ออกจาก Value
                            key = field.value.replace("```", "").strip()
                        if "HWID" in field.name:
                            hwid = field.value.replace("```", "").strip()
                    
                    if key and hwid:
                        # ส่งไปอัปเดตที่ GitHub Gist
                        success, msg = update_gist_hwid(key, hwid)
                        
                        # ตอบกลับในห้อง Log ว่าทำอะไรไปบ้าง
                        if success:
                            await message.channel.send(f"🤖 **[AUTO-BIND SYSTEM]**\n✅ ผูก HWID สำเร็จสำหรับคีย์: `{key}`", reference=message)
                        else:
                            # ถ้าผูกไม่ได้ (เช่น มีคนใช้อยู่แล้ว) ก็แจ้งเตือน
                            if "เจ้าของแล้ว" in msg:
                                await message.channel.send(f"⚠️ **[SECURITY ALERT]** คีย์นี้ถูกใช้ซ้ำจากเครื่องอื่น!\nKey: `{key}`", reference=message)
            except Exception as e:
                print(f"Auto Bind Error: {e}")
        return

    # ส่วนเช็คสลิปเดิม
    if message.channel.id == SLIP_CHANNEL_ID and message.attachments:
        try:
            img_url = message.attachments[0].url
            img_data = requests.get(img_url).content
            success, amount, ref, txt = check_slip_easyslip(img_url)
            
            if success:
                if is_slip_used(ref):
                    await message.channel.send(content=f"{message.author.mention}", embed=discord.Embed(description="❌ **SLIP ALREADY USED**", color=ERROR_COLOR), delete_after=10)
                    await message.delete()
                    return
                
                new_bal = update_money(message.author.id, amount, is_topup=True)
                save_used_slip(ref)
                await update_user_log(bot, message.author.id)
                
                embed = discord.Embed(title="✅ TOPUP SUCCESSFUL", color=SUCCESS_COLOR)
                embed.description = f"```ini\n[ RECEIPT ]\nAMOUNT  = {amount:.2f} THB\nBALANCE = {new_bal:.2f} THB\nREF     = {ref}```"
                embed.set_thumbnail(url=message.author.display_avatar.url)
                await message.channel.send(content=f"{message.author.mention}", embed=embed, delete_after=15)
                
                if hist := bot.get_channel(SLIP_LOG_ID):
                    slip_file = discord.File(io.BytesIO(img_data), filename=f"slip_{ref}.jpg")
                    log_embed = discord.Embed(title="💳 SLIP VERIFIED | บันทึกการเติมเงิน", color=CYBER_COLOR)
                    log_embed.description = (
                        f"```ini\n"
                        f"[ TRANSACTION RECORD ]\n"
                        f"USER      = {message.author.name}\n"
                        f"UID       = {message.author.id}\n"
                        f"AMOUNT    = {amount:.2f} THB\n"
                        f"REF       = {ref}\n"
                        f"TIME      = {datetime.now().strftime('%H:%M:%S')}\n"
                        f"```\n"
                        f"👤 **User:** {message.author.mention}"
                    )
                    log_embed.set_thumbnail(url=message.author.display_avatar.url)
                    log_embed.set_image(url=f"attachment://slip_{ref}.jpg")
                    log_embed.set_footer(text="Auto-Verification System")
                    await hist.send(embed=log_embed, file=slip_file)
                
                await message.delete()
            else:
                await message.channel.send(content=f"{message.author.mention}", embed=discord.Embed(description=f"❌ **ERROR:** {txt}", color=ERROR_COLOR), delete_after=10)
                await message.delete()
        except Exception as e:
            print(f"Error: {e}")
    await bot.process_commands(message)

# =================================================================
# ⚙️ RUN
# =================================================================
def load_db():
    load_json(DB_FILE); load_json(SLIP_DB_FILE)
    load_json(TOTAL_DB_FILE); load_json(LOG_MSG_DB)
    load_json(RECEIPT_DB); load_json(KEYS_DB)

@bot.command()
async def sync(ctx):
    if ctx.author.guild_permissions.administrator:
        fmt = await bot.tree.sync()
        await ctx.send(f"✅ Synced {len(fmt)} commands successfully!")

server_on()
bot.run(os.getenv('TOKEN'))
