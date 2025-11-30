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

# ⚠️ Token บอท (แนะนำให้ใส่ตรงนี้เลยเพื่อความชัวร์)
DISCORD_BOT_TOKEN = 'ใส่_TOKEN_บอท_ของคุณ_ตรงนี้' 

# API Key EasySlip
EASYSLIP_API_KEY = 'c5873b2f-d7a9-4f03-9267-166829da1f93'.strip()

# Channel IDs
SHOP_CHANNEL_ID = 1416797606180552714     # ห้องกดซื้อของ
SLIP_CHANNEL_ID = 1416797464350167090     # ห้องส่งสลิป
ADMIN_LOG_ID = 1441466742885978144        # ห้อง Log แอดมิน
HISTORY_CHANNEL_ID = 1444390933297631512  # ห้องเก็บรูปสลิปย้อนหลัง

# 🔥 [NEW] ห้องสำหรับระบบ Dashboard (ต้องใส่ ID จริง)
DASHBOARD_CMD_CHANNEL_ID = 1444662199674081423 # ห้องวางปุ่มกดอัปเดต
DASHBOARD_LOG_CHANNEL_ID = 1444662604940181667 # ห้องแสดงยอดเงินลูกค้า (แยกรายคน)

# Images
QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg'
SHOP_GIF_URL = 'https://media.discordapp.net/attachments/1303249085347926058/1444212368937586698/53ad0cc3373bbe0ea51dd878241952c6.gif?ex=692be314&is=692a9194&hm=bf9bfce543bee87e6334726e99e6f19f37cf457595e5e5b1ba05c0b678317cac&=&width=640&height=360'
SUCCESS_GIF_URL = 'https://cdn.discordapp.com/attachments/1233098937632817233/1444077217230491731/Fire_Force_Sho_Kusakabe_GIF_-_Fire_Force_Sho_Kusakabe_-_Descobrir_e_Compartilhar_GIFs.gif?ex=692d5f76&is=692c0df6&hm=a3344a6e695ceb3a513281745b49616df9e99da3e7960635fa2b94b3b8770ce4&'

# 🔥 [STRICT SECURITY] รายชื่อที่อนุญาต (ต้องตรงเป๊ะๆ หรือมีอยู่ในชื่อ)
VALID_RECEIVERS = [
    "นายชานนท์ ขันทอง",
    "นาย ชานนท์ ขันทอง",
    "CHANON KHANTONG",
    "chanon khantong"
]
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
TOTAL_DB_FILE = "total_topup.json"     # เก็บยอดเติมรวมทั้งหมด
LOG_MSG_DB = "log_messages.json"       # เก็บ ID ข้อความ Log

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
    """อัปเดตเงินและยอดรวม (ปลอดภัย ไม่เพี้ยน)"""
    bal_db = load_json(DB_FILE)
    total_db = load_json(TOTAL_DB_FILE)
    uid = str(user_id)
    
    # อัปเดตยอดคงเหลือ
    current_bal = float(bal_db.get(uid, 0.0))
    new_bal = current_bal + float(amount)
    bal_db[uid] = new_bal
    
    # อัปเดตยอดเติมรวม (เฉพาะตอนเติมเงิน)
    if is_topup and amount > 0:
        current_total = float(total_db.get(uid, 0.0))
        total_db[uid] = current_total + float(amount)
        save_json(TOTAL_DB_FILE, total_db)
        
    save_json(DB_FILE, bal_db)
    return new_bal

def deduct_balance(user_id, amount):
    return update_money(user_id, -amount) >= 0

# --- Slip Management ---
def is_slip_used(trans_ref):
    slips = load_json(SLIP_DB_FILE)
    if isinstance(slips, dict): slips = list(slips.keys())
    return trans_ref in slips

def save_used_slip(trans_ref):
    slips = load_json(SLIP_DB_FILE)
    if isinstance(slips, dict): slips = list(slips.keys())
    slips.append(trans_ref)
    with open(SLIP_DB_FILE, "w") as f: json.dump(slips, f)

# 🔥 ระบบเช็คสลิป (Strict Mode: ชื่อเป๊ะ + เวลาเป๊ะ)
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
            
            # ถ้าไม่มีชื่อผู้รับ -> ปัดตกทันที (ตามข้อ 4)
            if not receiver:
                 return False, 0, None, "❌ ไม่พบชื่อผู้รับในสลิป (API ไม่ส่งมา)"

            # ล้างชื่อให้สะอาดเพื่อเปรียบเทียบ
            clean_receiver = " ".join(receiver.lower().split())
            
            is_name_valid = False
            for valid_name in VALID_RECEIVERS:
                clean_valid = " ".join(valid_name.lower().split())
                # เช็คว่าชื่อในสลิป ตรงกับรายชื่อที่กำหนดไหม (อนุโลมให้มีคำนำหน้าเกินมาได้ แต่ต้องมีชื่อหลักครบ)
                if clean_valid in clean_receiver: 
                    is_name_valid = True
                    break
            
            if not is_name_valid:
                 return False, 0, None, f"❌ ชื่อผู้รับไม่ถูกต้อง (โอนให้: {receiver})"

            # 3. เช็คเวลา (Strict Time: 5 Minutes)
            try:
                dt_str = f"{slip['date']} {slip['time']}".replace("T", " ").split("+")[0].split(".")[0]
                slip_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                if slip_dt.year > 2500: slip_dt = slip_dt.replace(year=slip_dt.year - 543)
                
                now = datetime.utcnow() + timedelta(hours=7)
                diff = (now - slip_dt).total_seconds() / 60
                
                if diff > 5: return False, 0, None, f"❌ สลิปเก่าเกิน 5 นาที ({int(diff)} นาที)"
                if diff < -5: return False, 0, None, "❌ เวลาสลิปผิดปกติ (อนาคต)"
                
            except Exception as e:
                print(f"Time Error: {e}")
                return False, 0, None, "❌ อ่านวันเวลาในสลิปไม่ได้"

            return True, amount, slip['transRef'], "OK"
        else:
            return False, 0, None, data.get('message', 'สลิปไม่ผ่านการตรวจสอบ')
    except Exception as e:
        return False, 0, None, f"System Error: {str(e)}"

# =================================================================
# 🎛️ DASHBOARD SYSTEM (Log ยอดรวม)
# =================================================================

class DashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔄 อัปเดตข้อมูลลูกค้า (Sync)", style=discord.ButtonStyle.primary, custom_id="update_db_btn")
    async def update_db(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        await update_all_user_logs(interaction.client)
        await interaction.followup.send("✅ อัปเดต Dashboard เรียบร้อยแล้ว!")

async def update_user_log(bot, user_id):
    """สร้างหรือแก้ไข Log ของลูกค้าในห้อง Dashboard"""
    log_channel = bot.get_channel(DASHBOARD_LOG_CHANNEL_ID)
    if not log_channel: return

    data = get_data(user_id)
    # ถ้าไม่เคยเติมเงินเลย ไม่ต้องสร้าง Log
    if data['total'] <= 0 and data['balance'] <= 0: return

    user = bot.get_user(int(user_id))
    user_name = user.name if user else f"User {user_id}"
    avatar = user.display_avatar.url if user else None

    # Embed บัตรสมาชิก
    embed = discord.Embed(title=f"👤 ข้อมูลลูกค้า: {user_name}", color=discord.Color.blue())
    if avatar: embed.set_thumbnail(url=avatar)
    embed.add_field(name="💰 เงินคงเหลือ", value=f"`{data['balance']:.2f} บาท`", inline=True)
    embed.add_field(name="📈 ยอดเติมสะสม", value=f"`{data['total']:.2f} บาท`", inline=True)
    embed.set_footer(text=f"ID: {user_id} | Update: {datetime.now().strftime('%H:%M')}")

    # เช็คว่ามีข้อความเก่าให้แก้ไหม
    msg_db = load_json(LOG_MSG_DB)
    msg_id = msg_db.get(str(user_id))

    if msg_id:
        try:
            msg = await log_channel.fetch_message(msg_id)
            await msg.edit(embed=embed)
            return
        except:
            pass # ถ้าข้อความเก่าหาย ให้สร้างใหม่

    # สร้างใหม่
    msg = await log_channel.send(embed=embed)
    msg_db[str(user_id)] = msg.id
    save_json(LOG_MSG_DB, msg_db)

async def update_all_user_logs(bot):
    """อัปเดตทุกคน (ใช้ตอนกดปุ่ม Refresh)"""
    all_users = load_json(DB_FILE)
    for uid in all_users:
        await update_user_log(bot, uid)
        await asyncio.sleep(1) # หน่วงเวลาไม่ให้ติด Rate Limit

# =================================================================
# 🛒 SHOP UI & VIEWS
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

        # ตัดเงิน (update_money จะไปแก้ balance ใน DB)
        new_bal = update_money(interaction.user.id, -price)
        
        # ให้ยศ
        role = interaction.guild.get_role(self.product["role_id"])
        if role: await interaction.user.add_roles(role)

        # อัปเดต Dashboard ทันที
        await update_user_log(interaction.client, interaction.user.id)

        # ใบเสร็จ
        order_id = str(uuid.uuid4())[:8].upper()
        embed = discord.Embed(title="✅ Order Successful", color=discord.Color.green())
        desc = (f"👤 ผู้ซื้อ: {interaction.user.mention}\n"
                f"📦 สินค้า: {self.product['name']}\n"
                f"🧾 Order ID: {order_id}")
        embed.description = f"```yaml\n{desc}\n```"
        embed.set_image(url=SUCCESS_GIF_URL)
        
        await interaction.response.edit_message(content=None, embed=embed, view=None)

    @discord.ui.button(label="❌ ยกเลิก", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction, button):
        if interaction.user.id == self.user_id:
            await interaction.response.edit_message(content="ยกเลิกแล้ว", view=None, embed=None)

class TopupModal(discord.ui.Modal, title="เติมเงิน (Top Up)"):
    amount = discord.ui.TextInput(label="จำนวนเงิน", placeholder="50", min_length=1, max_length=6)
    async def on_submit(self, interaction: discord.Interaction):
        try: val = float(self.amount.value)
        except: return await interaction.response.send_message("❌ ใส่ตัวเลขเท่านั้น", ephemeral=True)
        
        embed = discord.Embed(title="🧾 ใบแจ้งการชำระเงิน", description=f"ยอดโอน: **{val} บาท**", color=discord.Color.gold())
        embed.set_image(url=QR_CODE_URL)
        embed.set_footer(text="ส่งสลิปใน 5 นาที")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MainShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="เติมเงิน", style=discord.ButtonStyle.primary, emoji="💳", custom_id="topup")
    async def topup(self, interaction, button): await interaction.response.send_modal(TopupModal())

    @discord.ui.button(label="เช็คยอด", style=discord.ButtonStyle.success, emoji="💰", custom_id="check")
    async def check(self, interaction, button):
        bal = get_data(interaction.user.id)['balance']
        await interaction.response.send_message(f"💳 คงเหลือ: **{bal:.2f} บาท**", ephemeral=True)

    @discord.ui.button(label="ล้างค่า", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="clear")
    async def clear(self, interaction, button): await interaction.response.edit_message(view=MainShopView())

    @discord.ui.select(placeholder="เลือกสินค้า...", options=[discord.SelectOption(label=p['name'], value=p['id'], description=f"{p['price']} บาท") for p in PRODUCTS], custom_id="shop_select")
    async def buy(self, interaction, select):
        prod = next(p for p in PRODUCTS if p['id'] == select.values[0])
        bal = get_data(interaction.user.id)['balance']
        embed = discord.Embed(title="🛒 ยืนยันการสั่งซื้อ", description=f"สินค้า: {prod['name']}\nราคา: {prod['price']} บาท", color=discord.Color.blue())
        if bal < prod['price']: embed.color = discord.Color.red(); embed.set_footer(text="❌ เงินไม่พอ")
        await interaction.response.send_message(embed=embed, view=ConfirmBuyView(prod, interaction.user.id), ephemeral=True)

# =================================================================
# 🤖 MAIN BOT
# =================================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot Online: {bot.user}")
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
    await interaction.channel.send(embed=discord.Embed(title="🛒 SHOP", description="เลือกรายการด้านล่าง", color=discord.Color.blue()), view=MainShopView())
    await interaction.response.send_message("Done", ephemeral=True)

@bot.tree.command(name="add_money")
async def add_money(interaction, user: discord.Member, amount: float):
    # is_topup=True เพื่อให้นับรวมในยอดสะสมด้วย
    new_bal = update_money(user.id, amount, is_topup=True) 
    await update_user_log(interaction.client, user.id)
    await interaction.response.send_message(f"✅ ปรับเงิน {user.mention} เป็น {new_bal} บาท")

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
                
                # ✅ เติมเงิน + อัปเดต Log + เก็บสลิป
                new_bal = update_money(message.author.id, amount, is_topup=True)
                save_used_slip(ref)
                await update_user_log(bot, message.author.id)

                await msg.edit(content=f"✅ เติมเงินสำเร็จ {amount} บาท\nคงเหลือ {new_bal} บาท")
                
                if hist := bot.get_channel(HISTORY_CHANNEL_ID):
                    f = discord.File(io.BytesIO(img_data), filename="slip.jpg")
                    await hist.send(f"💰 {message.author.mention} เติม {amount} (Ref: {ref})", file=f)

                await asyncio.sleep(5)
                await message.delete()
                await msg.delete()
            else:
                await msg.edit(content=f"❌ {txt}")
        except Exception as e:
            await msg.edit(content=f"Error: {e}")

server_on()
bot.run(os.getenv('TOKEN'))
