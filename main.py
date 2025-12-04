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
# ⚙️ ส่วนที่ 1: ตั้งค่าบอท
# =================================================================

# ⚠️⚠️⚠️ แก้ไข: เอา Token บอทของคุณมาใส่ตรงนี้ ⚠️⚠️⚠️
DISCORD_BOT_TOKEN = os.environ.get('TOKEN') 

# API Key EasySlip
EASYSLIP_API_KEY = 'c5873b2f-d7a9-4f03-9267-166829da1f93'.strip()

# ID ห้องต่างๆ
SHOP_CHANNEL_ID = 1416797606180552714  
SLIP_CHANNEL_ID = 1416797464350167090  
ADMIN_LOG_ID = 1441466742885978144     
HISTORY_CHANNEL_ID = 1444390933297631512 

# 🔥 [NEW] ห้องสำหรับระบบ Dashboard
DASHBOARD_CMD_CHANNEL_ID = 1444662199674081423 
DASHBOARD_LOG_CHANNEL_ID = 1444662604940181667 

# ลิงก์รูปภาพ
QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg' 
SHOP_GIF_URL = 'https://media.discordapp.net/attachments/1303249085347926058/1444212368937586698/53ad0cc3373bbe0ea51dd878241952c6.gif?ex=692be314&is=692a9194&hm=bf9bfce543bee87e6334726e99e6f19f37cf457595e5e5b1ba05c0b678317cac&=&width=640&height=360'
SUCCESS_GIF_URL = 'https://cdn.discordapp.com/attachments/1233098937632817233/1444077217230491731/Fire_Force_Sho_Kusakabe_GIF_-_Fire_Force_Sho_Kusakabe_-_Descobrir_e_Compartilhar_GIFs.gif?ex=692d5f76&is=692c0df6&hm=a3344a6e695ceb3a513281745b49616df9e99da3e7960635fa2b94b3b8770ce4&'

# 🔥 [SMART CHECK] รายชื่อผู้รับที่ถูกต้อง
EXPECTED_NAMES = ['ชานนท์ ขันทอง', 'Chanon Khantong', 'chanon khantong', 'chanon k', 'ชานนท์ ข', 'นายชานนท์ ขันทอง', 'นาย ชานนท์ ขันทอง', 'นายชานนท์ ข', 'นาย ชานนท์ ข']
MIN_AMOUNT = 1.00 

PRODUCTS = [
    {"id": "item1",  "emoji": "⭐",  "name": "𝙳𝙾𝙽𝙰𝚃𝙴",        "price": 89,  "role_id": 1431279741440364625},
    {"id": "item2",  "emoji": "👻",  "name": "ᴍᴏᴅ ᴅᴇᴠᴏᴜʀ",     "price": 120, "role_id": 1432064283767738571},
    {"id": "item3",  "emoji": "👑",  "name": "SETTING PREMIUM", "price": 169, "role_id": 1419373724653588540},
    {"id": "item4",  "emoji": "⚔️",  "name": "𝙰𝙻𝙻 𝚆𝙴𝙰𝙿𝙾𝙽",      "price": 139, "role_id": 1444190694674792592},
    {"id": "item5",  "emoji": "💻",  "name": "ลบประวัติ CMD",    "price": 79,  "role_id": 1444191270372114552},
    {"id": "item6",  "emoji": "🗑️",  "name": "ลบประวัติรันโปรแกรม","price": 49,  "role_id": 1444191566838370365},
    {"id": "item7",  "emoji": "💎",  "name": "𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟷",     "price": 25,  "role_id": 1431250097135419505},
    {"id": "item8",  "emoji": "🌈",  "name": "𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟸",     "price": 25,  "role_id": 1431234346202959973},
    {"id": "item9",  "emoji": "🔥",  "name": "𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟹",     "price": 25,  "role_id": 1431249584054734929},
    {"id": "item10", "emoji": "🎧",  "name": "𝚜𝚞𝚗𝚔𝚒𝚜𝚜𝚎𝚍",      "price": 25,  "role_id": 1431278653760737340},
    {"id": "item11", "emoji": "🌃",  "name": "𝚖𝚊𝚐𝚒𝚌𝚎𝚢𝚎",       "price": 25,  "role_id": 1431231640058990652},
    {"id": "item12", "emoji": "🌷",  "name": "𝚁𝚎𝚊𝚕𝚕𝚒𝚟𝚎",       "price": 25,  "role_id": 1431204938373140513},
    {"id": "item13", "emoji": "🏞️",  "name": "ꜰᴀʟʟɪɴɢ",        "price": 25,  "role_id": 1444192569754910770},
    {"id": "item14", "emoji": "🎮",  "name": "𝙱𝙾𝙾𝚂𝚃 𝙵𝙿𝚂",       "price": 99,  "role_id": 1432010188340199504},
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

# 🔥 ระบบเช็คสลิป (Strict & Smart)
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
            amount = float(slip['amount']['amount'] if isinstance(slip['amount'], dict) else slip['amount'])
            if amount < MIN_AMOUNT:
                return False, 0, None, f"❌ ยอดต่ำกว่ากำหนด ({amount} < {MIN_AMOUNT})"

            # 2. เช็คชื่อผู้รับ (Strict Name Check)
            receiver = slip.get('receiver', {}).get('displayName') or slip.get('receiver', {}).get('name') or ""
            receiver = receiver.strip()
            
            if not receiver:
                 # 🔥 ถ้า API ไม่ส่งชื่อมา หรืออ่านชื่อไม่ออก -> ปัดตกทันที
                 return False, 0, None, "❌ ไม่พบชื่อผู้รับในสลิป (API ไม่ส่งมา)"

            # ล้างชื่อให้สะอาดเพื่อเปรียบเทียบ
            clean_receiver = " ".join(receiver.lower().split())
            
            is_name_valid = False
            for valid_name in EXPECTED_NAMES:
                clean_valid = " ".join(valid_name.lower().split())
                if clean_valid in clean_receiver: 
                    is_name_valid = True
                    break
            
            if not is_name_valid:
                 return False, 0, None, f"❌ ชื่อผู้รับไม่ถูกต้อง (โอนให้: {receiver})"

            # 3. เช็คเวลา (Strict Time: 5 Minutes)
            try:
                dt_str = f"{slip['date']} {slip['time']}".replace("T", " ").split("+")[0].split(".")[0]
                
                slip_dt = None
                formats = ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d"]
                for fmt in formats:
                    try:
                        slip_dt = datetime.strptime(dt_str, fmt)
                        break
                    except: continue
                
                if slip_dt:
                    if slip_dt.year > 2500: slip_dt = slip_dt.replace(year=slip_dt.year - 543)
                    now = datetime.utcnow() + timedelta(hours=7)
                    diff = (now - slip_dt).total_seconds() / 60
                    
                    if diff > 5: return False, 0, None, f"❌ สลิปเก่าเกิน 5 นาที ({int(diff)} นาที)"
                    if diff < -5: return False, 0, None, "❌ เวลาสลิปผิดปกติ (อนาคต)"
                
            except Exception as e:
                print(f"Time Error: {e}")
                pass 

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

    @discord.ui.button(label="🔄 อัปเดตยอดเงิน (Sync)", style=discord.ButtonStyle.primary, custom_id="update_db_btn")
    async def update_db(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        await update_all_user_logs(interaction.client)
        await interaction.followup.send("✅ อัปเดต Dashboard เรียบร้อยแล้ว!")

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
        
        data = get_data(interaction.user.id)
        price = self.product["price"]

        if data['balance'] < price:
            return await interaction.response.edit_message(content=f"❌ เงินไม่พอขาด `{price - data['balance']}`", view=None, embed=None)

        update_money(interaction.user.id, -price) # ตัดเงิน
        
        role = interaction.guild.get_role(self.product["role_id"])
        if role: await interaction.user.add_roles(role)

        await update_user_log(interaction.client, interaction.user.id) # อัปเดต Log

        order_id = str(uuid.uuid4())[:8].upper()
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        embed = discord.Embed(title="✅ Order Successful", color=discord.Color.green())
        receipt_text = (
            f"👤 ผู้สั่ง   : {interaction.user.display_name}\n"
            f"📦 สินค้า    : {self.product['name']}\n"
            f"💎 ราคา     : {price} บาท\n"
            f"🧾 Order ID : {order_id}\n"
            f"🗓️ วันที่     : {now_str}"
        )
        embed.description = f"```yaml\n{receipt_text}\n```"
        
        embed.add_field(name="💰 ยอดเงินคงเหลือ", value=f"`{data['balance'] - price} บาท`", inline=True)
        embed.add_field(name="📦 สถานะสินค้า", value="`✅ ส่งมอบแล้ว`", inline=True)
        
        embed.set_image(url=SUCCESS_GIF_URL)
        embed.set_footer(text=f"ขอบคุณที่ใช้บริการครับ", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.edit_message(content=None, embed=embed, view=None)
        
        if log := interaction.guild.get_channel(ADMIN_LOG_ID):
            await log.send(f"🛒 **[BUY]** {interaction.user.mention} ซื้อ **{self.product['name']}** (ID: {order_id})")

    @discord.ui.button(label="❌ ยกเลิก", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await interaction.response.edit_message(content="🗑️ ยกเลิกรายการเรียบร้อย", view=None, embed=None)

class TopupModal(discord.ui.Modal, title="เติมเงิน (Top Up)"):
    amount = discord.ui.TextInput(label="จำนวนเงิน", placeholder="50", min_length=1, max_length=6)
    async def on_submit(self, interaction: discord.Interaction):
        try: val = float(self.amount.value)
        except: return await interaction.response.send_message("❌ ใส่ตัวเลขเท่านั้น", ephemeral=True)
        
        embed = discord.Embed(title="🧾 ใบแจ้งการชำระเงิน", description=f"ยอดโอน: **{val} บาท**", color=discord.Color.gold())
        embed.add_field(name="วิธีการ", value="1. สแกน QR Code\n2. ส่งรูปสลิปในห้องนี้\n3. (ต้องส่งภายใน 5 นาที)", inline=False)
        embed.set_image(url=QR_CODE_URL)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MainShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="เติมเงิน", style=discord.ButtonStyle.primary, emoji="💳", custom_id="topup")
    async def topup(self, interaction, button): await interaction.response.send_modal(TopupModal())

    @discord.ui.button(label="เช็คยอด", style=discord.ButtonStyle.success, emoji="💰", custom_id="check")
    async def check(self, interaction, button):
        bal = get_data(interaction.user.id)['balance']
        # 🔥 แก้ไข: ใช้ Embed สีเขียวเล็กๆ ตาม UI เดิม
        embed = discord.Embed(description=f"🦋 **คุณมียอดเงินคงเหลือ {bal:.2f} บาท**", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="ล้างค่า", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="clear")
    async def clear(self, interaction, button): await interaction.response.edit_message(view=MainShopView())

    @discord.ui.select(placeholder="เลือกสินค้า...", options=[discord.SelectOption(label=p['name'], value=p['id'], description=f"{p['price']} บาท", emoji=p["emoji"]) for p in PRODUCTS], custom_id="shop_select")
    async def buy(self, interaction, select):
        prod = next(p for p in PRODUCTS if p['id'] == select.values[0])
        bal = get_data(interaction.user.id)['balance']
        embed = discord.Embed(title="🛒 ยืนยันการสั่งซื้อ", description=f"สินค้า: {prod['name']}\nราคา: {prod['price']} บาท", color=discord.Color.blue())
        if bal < prod['price']: embed.color = discord.Color.red(); embed.set_footer(text="❌ เงินไม่พอ")
        await interaction.response.send_message(embed=embed, view=ConfirmBuyView(prod, interaction.user.id), ephemeral=True)

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
    # 👇 ใส่ข้อความเต็มๆ ตาม UI เดิม 👇
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

# 🔥 [FIXED] คำสั่งแอดมิน UI เดิม (Embed สีเขียว)
@bot.tree.command(name="add_money")
async def add_money(interaction, user: discord.Member, amount: float):
    new_bal = update_money(user.id, amount, is_topup=True)
    await update_user_log(interaction.client, user.id)
    
    # ✅ UI เดิมที่เคยส่งให้
    embed = discord.Embed(description=f"💸 **ปรับยอดเงินสำเร็จ**", color=discord.Color.green())
    embed.add_field(name="ลูกค้า", value=user.mention, inline=True)
    embed.add_field(name="ยอดใหม่", value=f"{new_bal:.2f} บาท", inline=True)
    
    await interaction.response.send_message(embed=embed)
    
    if log := bot.get_channel(ADMIN_LOG_ID):
        await log.send(f"🔧 **[ADMIN]** {interaction.user.mention} ปรับเงิน {user.mention} {amount} บาท")

# 🔥 [FIXED] Log เดิม (แนวตั้ง)
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

                await msg.edit(content=f"✅ เติมเงินสำเร็จ {amount} บาท\nคงเหลือ {new_bal} บาท")
                
                # ✅ Log แบบเดิม (แนวตั้ง + รูป)
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
