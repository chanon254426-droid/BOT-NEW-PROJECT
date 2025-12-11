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

# =================================================================
# ⚙️ CONFIGURATION
# =================================================================

# ⚠️ Token บอท
DISCORD_BOT_TOKEN = os.environ.get('TOKEN')

# API Key EasySlip
EASYSLIP_API_KEY = '12710681-efd6-412f-bce7-984feb9aa4cc'.strip()

# Channel IDs
SHOP_CHANNEL_ID = 1416797606180552714
SLIP_CHANNEL_ID = 1416797464350167090
ADMIN_LOG_ID = 1441466742885978144
HISTORY_CHANNEL_ID = 1444390933297631512

# ห้อง Dashboard
DASHBOARD_CMD_CHANNEL_ID = 1444662199674081423
DASHBOARD_LOG_CHANNEL_ID = 1444662604940181667

# Images
QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg'
SHOP_GIF_URL = 'https://media.discordapp.net/attachments/1303249085347926058/1444212368937586698/53ad0cc3373bbe0ea51dd878241952c6.gif'
SUCCESS_GIF_URL = 'https://cdn.discordapp.com/attachments/1233098937632817233/1444077217230491731/Fire_Force_Sho_Kusakabe_GIF.gif'

# 🔥 [SMART CHECK] รายชื่อผู้รับ
EXPECTED_NAMES = [
    'ชานนท์ ขันทอง',      'นายชานนท์ ขันทอง',    'นาย ชานนท์ ขันทอง',
    'ชานนท์ ข',          'นายชานนท์ ข',        'นาย ชานนท์ ข',
    'ชานนท์ ขัน',        'นายชานนท์ ขัน',
    'chanon khantong',   'mr. chanon khantong', 'mr chanon khantong',
    'chanon k',          'mr. chanon k',        'mr chanon k',
    'chanon kh',         'chanon khan'
]
MIN_AMOUNT = 1.00

PRODUCTS = [
    {"id": "item1",  "emoji": "⭐",  "name": "𝙳𝙾𝙽𝙰𝚃𝙴",         "price": 89,  "role_id": 1431279741440364625},
    {"id": "item2",  "emoji": "👻",  "name": "ᴍᴏᴅ ᴅᴇᴠᴏᴜʀ",      "price": 120, "role_id": 1432064283767738571},
    {"id": "item3",  "emoji": "👑",  "name": "SETTING PREMIUM", "price": 169, "role_id": 1419373724653588540},
    {"id": "item4",  "emoji": "⚔️",  "name": "𝙰𝙻𝙻 𝚆𝙴𝙰𝙿𝙾𝙽",       "price": 139, "role_id": 1444190694674792592},
    {"id": "item5",  "emoji": "💻",  "name": "ลบประวัติ CMD",     "price": 79,  "role_id": 1444191270372114552},
    {"id": "item6",  "emoji": "🗑️",  "name": "ลบประวัติรันโปรแกรม","price": 49,  "role_id": 1444191566838370365},
    {"id": "item7",  "emoji": "💎",  "name": "𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟷",      "price": 25,  "role_id": 1431250097135419505},
    {"id": "item8",  "emoji": "🌈",  "name": "𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟸",      "price": 25,  "role_id": 1431234346202959973},
    {"id": "item9",  "emoji": "🔥",  "name": "𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟹",      "price": 25,  "role_id": 1431249584054734929},
    {"id": "item10", "emoji": "🎧",  "name": "𝚜𝚞𝚗𝚔𝚒𝚜𝚜𝚎𝚍",       "price": 25,  "role_id": 1431278653760737340},
    {"id": "item11", "emoji": "🌃",  "name": "𝚖𝚊𝚐𝚒𝚌𝚎𝚢𝚎",        "price": 25,  "role_id": 1431231640058990652},
    {"id": "item12", "emoji": "🌷",  "name": "𝚁𝚎𝚊𝚕𝚕𝚒𝚟𝚎",        "price": 25,  "role_id": 1431204938373140513},
    {"id": "item13", "emoji": "🏞️",  "name": "ꜰᴀʟʟɪɴɢ",         "price": 25,  "role_id": 1444192569754910770},
    {"id": "item14", "emoji": "🎀",  "name": "realistic𝚅4",         "price": 35,  "role_id": 1448142438131699722},
    {"id": "item15", "emoji": "🌌",  "name": "realistic𝚅5",         "price": 35,  "role_id": 1448171343022526574},
    {"id": "item16", "emoji": "🍀",  "name": "realistic𝚅6",         "price": 35,  "role_id": 1448171385942966392},
    {"id": "item17", "emoji": "🎮",  "name": "𝙱𝙾𝙾𝚂𝚃 𝙵𝙿𝚂",        "price": 99,  "role_id": 1432010188340199504},
    {"id": "item18", "emoji": "🚧",  "name": "TOGYO MOD",        "price": 59,  "role_id": 1448142708286947449},
    {"id": "item19", "emoji": "⚡",  "name": "X Togyo mod",        "price": 35,  "role_id": 1448217708146589747},
    {"id": "item20", "emoji": "❓",  "name": "Tonedark❓",        "price": 35,  "role_id": 1448197995701993543},
    {"id": "item21", "emoji": "🚣",  "name": "realistic𝚅7",        "price": 35,  "role_id": 1448313586915999755},
    {"id": "item22", "emoji": "🍰",  "name": "PEKKY",        "price": 35,  "role_id": 1448263468355424298},
]

# =================================================================
# 💾 DATABASE SYSTEM
# =================================================================
DB_FILE = "user_balance.json"
SLIP_DB_FILE = "used_slips.json"
TOTAL_DB_FILE = "total_topup.json"
LOG_MSG_DB = "log_messages.json"

def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f: json.dump({}, f)
        return {}
    try:
        with open(filename, "r") as f: return json.load(f)
    except: return {}

def save_json(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

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

def deduct_balance(user_id, amount):
    db = load_json(DB_FILE)
    uid = str(user_id)
    current = float(db.get(uid, 0.0))
    cost = float(amount)
    
    if current >= cost:
        update_money(user_id, -amount) 
        return True
    return False

def is_slip_used(trans_ref):
    slips = load_json(SLIP_DB_FILE)
    if isinstance(slips, dict): slips = list(slips.keys())
    return trans_ref in slips

def save_used_slip(trans_ref):
    slips = load_json(SLIP_DB_FILE)
    if isinstance(slips, dict): slips = list(slips.keys())
    slips.append(trans_ref)
    with open(SLIP_DB_FILE, "w") as f: json.dump(slips, f, indent=4)

# 🔥 ระบบกู้คืนข้อมูลจาก Dashboard Log
async def restore_database_from_logs(bot):
    print("🔄 กำลังกู้คืนข้อมูลจากห้อง Dashboard Log...")
    channel = bot.get_channel(DASHBOARD_LOG_CHANNEL_ID)
    if not channel: return

    balances = load_json(DB_FILE)
    totals = load_json(TOTAL_DB_FILE)
    msg_ids = load_json(LOG_MSG_DB)
    
    count = 0
    async for message in channel.history(limit=None):
        if message.author.id != bot.user.id: continue
        if not message.embeds: continue

        embed = message.embeds[0]
        
        if not embed.footer or not embed.footer.text: continue
        id_match = re.search(r"ID: (\d+)", embed.footer.text)
        if not id_match: continue
        user_id = id_match.group(1)

        bal_field = next((f for f in embed.fields if "เงินคงเหลือ" in f.name), None)
        if bal_field:
             bal_match = re.search(r"([\d.]+)", bal_field.value)
             if bal_match and float(balances.get(user_id, 0)) == 0:
                 balances[user_id] = float(bal_match.group(1))

        total_field = next((f for f in embed.fields if "ยอดเติมสะสม" in f.name), None)
        if total_field:
             total_match = re.search(r"([\d.]+)", total_field.value)
             if total_match and float(totals.get(user_id, 0)) == 0:
                 totals[user_id] = float(total_match.group(1))
        
        msg_ids[user_id] = message.id
        count += 1

    save_json(DB_FILE, balances)
    save_json(TOTAL_DB_FILE, totals)
    save_json(LOG_MSG_DB, msg_ids)
    print(f"✅ กู้คืนข้อมูลลูกค้าสำเร็จ {count} รายการ")

# 🔥 [FIXED] ระบบเช็คสลิป EasySlip (แบบละเอียด Time Check + Name Check)
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
            
            # 1. เช็คยอดเงิน
            raw_amount = slip['amount']
            if isinstance(raw_amount, dict): raw_amount = raw_amount.get('amount', 0)
            amount = float(raw_amount)

            if amount < MIN_AMOUNT:
                return False, 0, None, f"❌ ยอดต่ำกว่ากำหนด ({amount} < {MIN_AMOUNT})"

            # 2. เช็คชื่อผู้รับ (Strict Check)
            receiver = slip.get('receiver', {}).get('displayName') or slip.get('receiver', {}).get('name') or ""
            receiver = receiver.strip()
            
            # 🔥 ถ้าไม่มีชื่อ (เช่น Wallet) -> อนุโลมให้ผ่านได้ (ตามที่คุณขอในรอบก่อนหน้านู้น) 
            # หรือถ้าอยากให้ Strict สุดๆ ก็เอาบรรทัดนี้ออก
            # if not receiver:
            #     return False, 0, None, "❌ สลิปนี้ไม่ระบุชื่อผู้รับ (Wallet ไม่ได้)"

            if receiver:
                clean_receiver = " ".join(receiver.lower().split())
                is_name_valid = False
                for valid_name in EXPECTED_NAMES:
                    clean_valid = " ".join(valid_name.lower().split())
                    if clean_valid in clean_receiver: 
                        is_name_valid = True
                        break
                
                if not is_name_valid:
                    return False, 0, None, f"❌ ชื่อผู้รับไม่ถูกต้อง (โอนไป: {receiver})"

            # 3. เช็คเวลา (Time Check 5 นาที - ปรับปรุงใหม่)
            try:
                # ดึงวันที่และเวลาอย่างปลอดภัย
                d_str = str(slip.get('date', ''))
                t_str = str(slip.get('time', ''))
                dt_str = f"{d_str} {t_str}".replace("T", " ").split("+")[0].split(".")[0]
                
                slip_dt = None
                formats = [
                    "%Y-%m-%d %H:%M:%S", 
                    "%d/%m/%Y %H:%M:%S", 
                    "%Y-%m-%d %H:%M",
                    "%d/%m/%Y %H:%M"
                ]
                
                for fmt in formats:
                    try:
                        slip_dt = datetime.strptime(dt_str, fmt)
                        break
                    except: continue
                
                if slip_dt:
                    if slip_dt.year > 2500: slip_dt = slip_dt.replace(year=slip_dt.year - 543)
                    
                    # เวลาปัจจุบัน (+7 UTC)
                    now = datetime.utcnow() + timedelta(hours=7)
                    diff = (now - slip_dt).total_seconds() / 60
                    
                    # ❌ เก่าเกิน 5 นาที
                    if diff > 5: return False, 0, None, f"❌ เวลาสลิปผิดปกติ ({int(diff)} นาทีที่แล้ว)"
                    # ❌ เวลาอนาคตเกิน 5 นาที
                    if diff < -5: return False, 0, None, "❌ เวลาสลิปผิดปกติ"
                else:
                     # ถ้าอ่านเวลาไม่ออกจริงๆ ให้ผ่านไปก่อน (หรือจะปรับให้ False ก็ได้)
                     pass

            except Exception as e:
                print(f"Time Check Error: {e}")
                # return False, 0, None, "❌ เกิดข้อผิดพลาดในการตรวจสอบเวลา"

            return True, amount, slip['transRef'], "OK"
        else:
            return False, 0, None, data.get('message', 'สลิปไม่ผ่านการตรวจสอบ')
    except Exception as e:
        return False, 0, None, f"System Error: {str(e)}"

# =================================================================
# 🎛️ DASHBOARD & LOG SYSTEM
# =================================================================

class DashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔄 อัปเดตยอดเงิน & กู้คืนข้อมูล", style=discord.ButtonStyle.primary, custom_id="update_db_btn")
    async def update_db(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        await restore_database_from_logs(interaction.client) 
        await update_all_user_logs(interaction.client)
        await interaction.followup.send("✅ กู้คืนข้อมูลและอัปเดต Dashboard เรียบร้อยแล้ว!")

async def update_user_log(bot, user_id):
    log_channel = bot.get_channel(DASHBOARD_LOG_CHANNEL_ID)
    if not log_channel: return

    data = get_data(user_id)
    if data['total'] <= 0 and data['balance'] <= 0: return

    user = bot.get_user(int(user_id))
    user_name = user.name if user else f"Unknown ({user_id})"
    avatar = user.display_avatar.url if user else None

    embed = discord.Embed(title=f"👤 ข้อมูลลูกค้า: {user_name}", color=discord.Color.blue())
    if avatar: embed.set_thumbnail(url=avatar)
    embed.add_field(name="💰 เงินคงเหลือ", value=f"`{data['balance']:.2f} บาท`", inline=True)
    embed.add_field(name="📈 ยอดเติมสะสม", value=f"`{data['total']:.2f} บาท`", inline=True)
    embed.set_footer(text=f"ID: {user_id} | Update: {datetime.now().strftime('%H:%M')}")

    msg_db = load_json(LOG_MSG_DB)
    msg_id = msg_db.get(str(user_id))

    if msg_id:
        try:
            msg = await log_channel.fetch_message(msg_id)
            await msg.edit(embed=embed)
            return
        except:
            pass 

    msg = await log_channel.send(embed=embed)
    msg_db[str(user_id)] = msg.id
    save_json(LOG_MSG_DB, msg_db)

async def update_all_user_logs(bot):
    all_users = load_json(DB_FILE)
    for uid in all_users:
        await update_user_log(bot, uid)
        await asyncio.sleep(1)

# =================================================================
# 🛒 UI VIEWS
# =================================================================

class ConfirmBuyView(discord.ui.View):
    def __init__(self, product, user_id):
        super().__init__(timeout=60)
        self.product = product
        self.user_id = user_id

    @discord.ui.button(label="✅ ยืนยัน", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        await interaction.response.defer()

        data = get_data(interaction.user.id)
        price = self.product["price"]

        if data['balance'] < price:
            return await interaction.followup.send(content=f"❌ เงินไม่พอขาด `{price - data['balance']}`", ephemeral=True)

        update_money(interaction.user.id, -price)
        role = interaction.guild.get_role(self.product["role_id"])
        if role: await interaction.user.add_roles(role)
        await update_user_log(interaction.client, interaction.user.id)

        order_id = str(uuid.uuid4())[:8].upper()
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        embed = discord.Embed(title="✅ Order Successful", color=discord.Color.green())
        receipt_text = (
            f"👤 ผู้สั่ง    : {interaction.user.display_name}\n"
            f"📦 สินค้า     : {self.product['name']}\n"
            f"💎 ราคา      : {price} บาท\n"
            f"🧾 Order ID : {order_id}\n"
            f"🗓️ วันที่      : {now_str}"
        )
        embed.description = f"```yaml\n{receipt_text}\n```"
        embed.add_field(name="💰 ยอดเงินคงเหลือ", value=f"`{data['balance'] - price} บาท`", inline=True)
        embed.add_field(name="📦 สถานะสินค้า", value="`✅ ส่งมอบแล้ว`", inline=True)
        embed.set_image(url=SUCCESS_GIF_URL)
        embed.set_footer(text=f"ขอบคุณที่ใช้บริการครับ", icon_url=interaction.user.display_avatar.url)
        
        await interaction.edit_original_response(content=None, embed=embed, view=None)
        
        if log := interaction.guild.get_channel(ADMIN_LOG_ID):
            await log.send(f"🛒 **[BUY]** {interaction.user.mention} ซื้อ **{self.product['name']}** (ID: {order_id})")

    @discord.ui.button(label="❌ ยกเลิก", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await interaction.response.edit_message(content="🗑️ ยกเลิกรายการเรียบร้อย", view=None, embed=None)

class TopupModal(discord.ui.Modal, title="เติมเงินเข้าระบบ (Top Up)"):
    amount = discord.ui.TextInput(label="จำนวนเงิน", placeholder="50", min_length=1, max_length=6)
    async def on_submit(self, interaction: discord.Interaction):
        try: val = float(self.amount.value)
        except: return await interaction.response.send_message("❌ ใส่ตัวเลขเท่านั้น", ephemeral=True)
        
        # 🔥 เพิ่มการแท็กห้องส่งสลิปตามสั่ง
        embed = discord.Embed(title="🧾 ใบแจ้งการชำระเงิน", description=f"ยอดโอน: **{val} บาท**", color=discord.Color.gold())
        embed.add_field(name="วิธีการ", value=f"1. สแกน QR Code\n2. ส่งรูปสลิปในห้อง <#{SLIP_CHANNEL_ID}>\n3. (ต้องส่งภายใน 5 นาที)", inline=False)
        embed.set_image(url=QR_CODE_URL)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MainShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="เติมเงิน", style=discord.ButtonStyle.primary, emoji="💳", custom_id="topup")
    async def topup(self, interaction, button): await interaction.response.send_modal(TopupModal())

    @discord.ui.button(label="เช็คยอด", style=discord.ButtonStyle.success, emoji="💰", custom_id="check")
    async def check(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        bal = get_data(interaction.user.id)['balance']
        embed = discord.Embed(description=f"🦋 **คุณมียอดเงินคงเหลือ {bal:.2f} บาท**", color=discord.Color.green())
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="ล้างค่า", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="clear")
    async def clear(self, interaction, button): await interaction.response.edit_message(view=MainShopView())

    @discord.ui.select(placeholder="เลือกสินค้า...", options=[discord.SelectOption(label=p['name'], value=p['id'], description=f"{p['price']} บาท", emoji=p["emoji"]) for p in PRODUCTS], custom_id="shop_select")
    async def buy(self, interaction, select):
        await interaction.response.defer(ephemeral=True)
        prod = next(p for p in PRODUCTS if p['id'] == select.values[0])
        bal = get_data(interaction.user.id)['balance']
        embed = discord.Embed(title="🛒 ยืนยันการสั่งซื้อ", description=f"สินค้า: {prod['name']}\nราคา: {prod['price']} บาท", color=discord.Color.blue())
        if bal < prod['price']: embed.color = discord.Color.red(); embed.set_footer(text="❌ เงินไม่พอ")
        await interaction.followup.send(embed=embed, view=ConfirmBuyView(prod, interaction.user.id), ephemeral=True)

# =================================================================
# 🤖 MAIN BOT SETUP
# =================================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot Online: {bot.user}")
    load_db()
    bot.add_view(MainShopView())
    bot.add_view(DashboardView())
    try: await bot.tree.sync()
    except: pass

@bot.tree.command(name="setup_dashboard", description="[Admin] สร้างห้องควบคุมยอดเงิน")
@app_commands.default_permissions(administrator=True)
async def setup_dashboard(interaction):
    if interaction.channel_id != DASHBOARD_CMD_CHANNEL_ID:
        return await interaction.response.send_message("❌ ผิดห้อง (ต้องใช้ในห้อง CMD)", ephemeral=True)
    
    embed = discord.Embed(title="🎛️ Admin Dashboard", description="กดปุ่มด้านล่างเพื่ออัปเดตยอดเงินลูกค้าทุกคนในห้อง Log", color=discord.Color.orange())
    await interaction.channel.send(embed=embed, view=DashboardView())
    await interaction.response.send_message("✅ สร้าง Dashboard แล้ว", ephemeral=True)

@bot.tree.command(name="setup_shop")
async def setup_shop(interaction):
    await interaction.response.defer(ephemeral=True)
    description_text = (
        "ยินดีต้อนรับสู่ **💻 NEW PROJECT!** ระบบอัตโนมัติ 24 ชม.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📜 **ขั้นตอนการสั่งซื้อสินค้า**\n"
        "1️⃣ กดปุ่ม **`เติมเงิน (QR Code)`** ระบบจะให้กรอกจำนวนเงิน\n"
        "2️⃣ กดปุ่ม **`เช็คยอดเงิน`** เพื่อตรวจสอบความถูกต้อง\n"
        "3️⃣ เลือกสินค้าที่ต้องการจาก **`เมนูด้านล่าง`** เพื่อสั่งซื้อทันที\n\n"
        "⚠️ **ข้อตกลงและเงื่อนไข**\n"
        "• โปรดตรวจสอบยอดเงินให้เพียงพอก่อนกดสั่งซื้อ\n"
        "• สินค้าซื้อแล้วไม่รับเปลี่ยนหรือคืนเงินทุกกรณี\n"
        "• หากพบปัญหาติดต่อแอดมินผ่านการเปิดตั๋วเท่านั้น\n\n"
        "🛒 **เลือกสินค้าที่คุณต้องการได้เลย!** 👇"
    )
    embed_shop = discord.Embed(title="✨ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐒𝐇𝐎𝐏 ✨", description=description_text, color=discord.Color.from_rgb(47, 49, 54))
    if SHOP_GIF_URL.startswith("http"): embed_shop.set_image(url=SHOP_GIF_URL)
    await interaction.channel.send(embed=embed_shop, view=MainShopView())
    await interaction.followup.send("✅ Done!")

@bot.tree.command(name="add_money")
async def add_money(interaction, user: discord.Member, amount: float):
    new_bal = update_money(user.id, amount, is_topup=True)
    await update_user_log(interaction.client, user.id)
    
    embed = discord.Embed(description=f"💸 **ปรับยอดเงินสำเร็จ**", color=discord.Color.green())
    embed.add_field(name="ลูกค้า", value=user.mention, inline=True)
    embed.add_field(name="ยอดใหม่", value=f"{new_bal:.2f} บาท", inline=True)
    
    await interaction.response.send_message(embed=embed)
    if log := bot.get_channel(ADMIN_LOG_ID):
        await log.send(f"🔧 **[ADMIN]** {interaction.user.mention} ปรับเงิน {user.mention} {amount} บาท")

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.channel.id == SLIP_CHANNEL_ID and message.attachments:
        msg = await message.channel.send("⏳ ตรวจสอบ...")
        try:
            img_data = requests.get(message.attachments[0].url).content
            success, amount, ref, txt = check_slip_easyslip(message.attachments[0].url)
            
            if success:
                if is_slip_used(ref):
                    await msg.edit(content="❌ สลิปซ้ำ")
                    return
                
                new_bal = update_money(message.author.id, amount, is_topup=True)
                save_used_slip(ref)
                await update_user_log(bot, message.author.id)

                # 🔥🔥 แก้ไขตรงนี้: เพิ่ม Embed แสดงรายละเอียดสำเร็จ (เหมือนเดิม)
                embed_success = discord.Embed(title="✅ เติมเงินสำเร็จ", color=discord.Color.green())
                embed_success.description = (
                    f"👤 **ลูกค้า:** {message.author.mention}\n"
                    f"💰 **ยอดเงิน:** `{amount:.2f}` บาท\n"
                    f"💵 **คงเหลือ:** `{new_bal:.2f}` บาท\n"
                    f"🧾 **Ref:** `{ref}`"
                )
                embed_success.set_thumbnail(url=message.author.display_avatar.url)
                await msg.edit(content=None, embed=embed_success)
                
                if hist := bot.get_channel(HISTORY_CHANNEL_ID):
                    log_embed = discord.Embed(title="🧾 บันทึกการเติมเงิน (Log)", color=discord.Color.blue())
                    log_embed.description = (
                        f"**ลูกค้า:** {message.author.mention}\n"
                        f"**ยอดเติม:** {amount} บาท\n"
                        f"**คงเหลือรวม:** {new_bal} บาท\n"
                        f"**Ref:** {ref}"
                    )
                    f = discord.File(io.BytesIO(img_data), filename="slip.jpg")
                    log_embed.set_image(url="attachment://slip.jpg")
                    await hist.send(embed=log_embed, file=f)

                await asyncio.sleep(5)
                await message.delete()
                await msg.delete()
            else:
                await msg.edit(content=f"❌ {txt}")
        except Exception as e:
            await msg.edit(content=f"Error: {e}")

server_on()
# ⚠️ เปลี่ยน TOKEN ด้วยนะ!
bot.run(os.getenv('TOKEN'))
