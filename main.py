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

# พยายาม import myserver
try:
    from myserver import server_on
except ImportError:
    def server_on(): pass

# =================================================================
# ⚙️ ส่วนที่ 1: ตั้งค่าระบบ (CONFIGURATION)
# =================================================================

# ⚠️ TOKEN บอท
DISCORD_BOT_TOKEN = os.environ.get('TOKEN')

# ⚠️ SLIPOK API KEY (เปลี่ยนจาก EasySlip เป็น SlipOK)
SLIPOK_API_KEY = 'SLIPOKA4R309R' 

# Channel IDs
SHOP_CHANNEL_ID = 1416797606180552714      
SLIP_CHANNEL_ID = 1416797464350167090      
ADMIN_LOG_ID = 1441466742885978144        
HISTORY_CHANNEL_ID = 1444390933297631512   
DASHBOARD_CMD_CHANNEL_ID = 1444662199674081423 
DASHBOARD_LOG_CHANNEL_ID = 1444662604940181667 

# Images
QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg' 
SHOP_GIF_URL = 'https://media.discordapp.net/attachments/1303249085347926058/1444212368937586698/53ad0cc3373bbe0ea51dd878241952c6.gif'
SUCCESS_GIF_URL = 'https://cdn.discordapp.com/attachments/1233098937632817233/1444077217230491731/Fire_Force_Sho_Kusakabe_GIF.gif'

# ธีมสี
THEME_COLOR = discord.Color.from_rgb(43, 45, 49)
SUCCESS_COLOR = discord.Color.from_rgb(87, 242, 135)
ERROR_COLOR = discord.Color.from_rgb(237, 66, 69)

# รายชื่อที่อนุญาต (Smart Check)
EXPECTED_NAMES = ['ชานนท์ ขันทอง', 'Chanon Khantong', 'chanon khantong', 'chanon k', 'ชานนท์ ข', 'นายชานนท์ ขันทอง', 'นาย ชานนท์ ขันทอง', 'นายชานนท์ ข', 'นาย ชานนท์ ข']
MIN_AMOUNT = 1.00 

# 🛒 รายการสินค้า (ครบ 20 ชิ้น ใส่ในเมนูเดียวได้เลย Discord รับได้สูงสุด 25 ชิ้น)
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
]

# =================================================================
# 💾 DATABASE SYSTEM
# =================================================================
DB_FILES = {
    "balance": "user_balance.json",
    "slips": "used_slips.json",
    "total": "total_topup.json",
    "logs": "log_messages.json"
}

def load_json(key):
    filename = DB_FILES.get(key)
    if not os.path.exists(filename):
        with open(filename, "w") as f: json.dump({}, f)
        return {}
    try:
        with open(filename, "r") as f: return json.load(f)
    except: return {}

def save_json(key, data):
    with open(DB_FILES.get(key), "w") as f: json.dump(data, f, indent=4)

def get_data(user_id):
    bal_db = load_json("balance")
    total_db = load_json("total")
    uid = str(user_id)
    return {
        "balance": float(bal_db.get(uid, 0.0)),
        "total": float(total_db.get(uid, 0.0))
    }

def update_money(user_id, amount, is_topup=False):
    bal_db = load_json("balance")
    total_db = load_json("total")
    uid = str(user_id)
    
    current_bal = float(bal_db.get(uid, 0.0))
    new_bal = current_bal + float(amount)
    bal_db[uid] = new_bal
    
    if is_topup and amount > 0:
        current_total = float(total_db.get(uid, 0.0))
        total_db[uid] = current_total + float(amount)
        save_json("total", total_db)
        
    save_json("balance", bal_db)
    return new_bal

def is_slip_used(trans_ref):
    slips = load_json("slips")
    if isinstance(slips, dict): slips = list(slips.keys())
    return trans_ref in slips

def save_used_slip(trans_ref):
    slips = load_json("slips")
    if isinstance(slips, dict): slips = list(slips.keys())
    slips.append(trans_ref)
    save_json("slips", slips)

async def restore_database_from_logs(bot):
    print("🔄 กำลังกู้คืนข้อมูลจากห้อง Dashboard Log...")
    channel = bot.get_channel(DASHBOARD_LOG_CHANNEL_ID)
    if not channel: return

    balances = load_json("balance")
    totals = load_json("total")
    msg_ids = load_json("logs")
    
    count = 0
    async for message in channel.history(limit=None):
        if message.author.id != bot.user.id: continue
        if not message.embeds: continue
        embed = message.embeds[0]
        
        if not embed.footer or not embed.footer.text: continue
        id_match = re.search(r"ID: (\d+)", embed.footer.text)
        if not id_match: continue
        user_id = id_match.group(1)

        bal_field = next((f for f in embed.fields if "เงินคงเหลือ" in f.name or "Balance" in f.name), None)
        if bal_field:
             bal_match = re.search(r"([\d.]+)", bal_field.value)
             if bal_match and float(balances.get(user_id, 0)) == 0:
                 balances[user_id] = float(bal_match.group(1))

        total_field = next((f for f in embed.fields if "ยอดเติมสะสม" in f.name or "Total" in f.name), None)
        if total_field:
             total_match = re.search(r"([\d.]+)", total_field.value)
             if total_match and float(totals.get(user_id, 0)) == 0:
                 totals[user_id] = float(total_match.group(1))
        
        msg_ids[user_id] = message.id
        count += 1

    save_json("balance", balances)
    save_json("total", totals)
    save_json("logs", msg_ids)
    print(f"✅ กู้คืนข้อมูลสำเร็จ {count} รายการ")

# =================================================================
# 🔍 ระบบตรวจสอบสลิป (SLIPOK)
# =================================================================
def check_slip_slipok(image_url):
    print(f"Checking slip: {image_url}")
    try:
        img_data = requests.get(image_url).content
        files = {'files': ('slip.jpg', io.BytesIO(img_data), 'image/jpeg')}
        response = requests.post(
            "https://api.slipok.com/api/line/apikey/verification",
            headers={'x-authorization': SLIPOK_API_KEY},
            files=files, timeout=15
        )
        data = response.json()

        if response.status_code == 200 and data.get('success'):
            slip = data['data']
            amount = float(slip['amount'])

            if amount < MIN_AMOUNT:
                return False, 0, None, f"❌ ยอดต่ำกว่ากำหนด ({amount} < {MIN_AMOUNT})"

            receiver = slip.get('receiver', {}).get('displayName') or slip.get('receiver', {}).get('name') or ""
            clean_receiver = " ".join(receiver.strip().lower().split())
            
            is_valid = any(" ".join(n.lower().split()) in clean_receiver for n in EXPECTED_NAMES)
            if not is_valid:
                 return False, 0, None, f"❌ ชื่อผู้รับไม่ถูกต้อง ({receiver})"

            return True, amount, slip['transRef'], "OK"
        else:
            return False, 0, None, data.get('message', 'สลิปไม่ผ่านการตรวจสอบ')
    except Exception as e:
        return False, 0, None, f"System Error: {e}"

# =================================================================
# 🎛️ UI & VIEWS
# =================================================================

class DashboardView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔄 อัปเดต & กู้คืน", style=discord.ButtonStyle.primary, custom_id="db_update")
    async def update(self, interaction, button):
        if not interaction.user.guild_permissions.administrator: return
        await interaction.response.defer(ephemeral=True)
        await restore_database_from_logs(interaction.client)
        await update_all_user_logs(interaction.client)
        await interaction.followup.send("✅ Done!")

async def update_user_log(bot, user_id):
    log_channel = bot.get_channel(DASHBOARD_LOG_CHANNEL_ID)
    if not log_channel: return
    data = get_data(user_id)
    if data['total'] <= 0 and data['balance'] <= 0: return

    user = bot.get_user(int(user_id))
    user_name = user.name if user else f"User({user_id})"
    
    embed = discord.Embed(color=discord.Color.blue())
    embed.set_author(name=f"👤 {user_name}", icon_url=user.display_avatar.url if user else None)
    embed.add_field(name="💰 เงินคงเหลือ", value=f"`{data['balance']:.2f}`", inline=True)
    embed.add_field(name="📈 ยอดเติมสะสม", value=f"`{data['total']:.2f}`", inline=True)
    embed.set_footer(text=f"ID: {user_id}")

    msg_db = load_json("logs")
    if uid := str(user_id) in msg_db:
        try:
            msg = await log_channel.fetch_message(msg_db[str(user_id)])
            await msg.edit(embed=embed)
            return
        except: pass
    
    msg = await log_channel.send(embed=embed)
    msg_db[str(user_id)] = msg.id
    save_json("logs", msg_db)

async def update_all_user_logs(bot):
    for uid in load_json("balance"):
        await update_user_log(bot, uid)
        await asyncio.sleep(0.5)

class ConfirmBuyView(discord.ui.View):
    def __init__(self, product, user_id):
        super().__init__(timeout=60)
        self.product = product
        self.user_id = user_id

    @discord.ui.button(label="ยืนยัน (Confirm)", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, interaction, button):
        if interaction.user.id != self.user_id: return
        data = get_data(interaction.user.id)
        price = self.product["price"]
        
        if data['balance'] < price:
            return await interaction.response.send_message(f"❌ เงินไม่พอ (ขาด {price - data['balance']:.2f})", ephemeral=True)
        
        update_money(interaction.user.id, -price)
        role = interaction.guild.get_role(self.product["role_id"])
        if role: await interaction.user.add_roles(role)
        await update_user_log(interaction.client, interaction.user.id)
        
        order_id = str(uuid.uuid4())[:8].upper()
        embed = discord.Embed(title="✅ Order Successful", color=SUCCESS_COLOR)
        embed.description = f"```yaml\nITEM : {self.product['name']}\nPRICE: {price}\nID   : {order_id}\n```"
        embed.set_image(url=SUCCESS_GIF_URL)
        
        await interaction.response.edit_message(content=None, embed=embed, view=None)
        if log := interaction.guild.get_channel(ADMIN_LOG_ID):
            await log.send(f"🛒 {interaction.user.mention} bought {self.product['name']}")

    @discord.ui.button(label="ยกเลิก", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction, button):
        if interaction.user.id == self.user_id:
            await interaction.response.edit_message(content="❌ ยกเลิกแล้ว", view=None, embed=None)

class TopupModal(discord.ui.Modal, title="เติมเงิน (Top Up)"):
    amount = discord.ui.TextInput(label="จำนวนเงิน", placeholder="50", max_length=6)
    async def on_submit(self, interaction):
        try: val = float(self.amount.value)
        except: return
        embed = discord.Embed(title="💳 สแกน QR Code", description=f"ยอดโอน: **{val} บาท**\n(ส่งสลิปในห้องนี้ภายใน 5 นาที)", color=THEME_COLOR)
        embed.set_image(url=QR_CODE_URL)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MainShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    # 🔥 ส่วนนี้คือ "ตัวเลือกช่องใหญ่ๆ" (Select Menu) ที่คุณต้องการ
    # รายการสินค้าจะซ่อนอยู่ในนี้ พอกดแล้วจะมี Scroll bar ให้เลื่อนดูถ้าเยอะ
    @discord.ui.select(
        placeholder="🛒 คลิกเพื่อเลือกสินค้าที่ต้องการสั่งซื้อ...",
        options=[
            discord.SelectOption(
                label=p['name'], 
                value=p['id'], 
                description=f"ราคา {p['price']} บาท", 
                emoji=p["emoji"]
            ) for p in PRODUCTS
        ],
        custom_id="shop_select",
        row=0
    )
    async def select_callback(self, interaction, select):
        prod = next(p for p in PRODUCTS if p['id'] == select.values[0])
        bal = get_data(interaction.user.id)['balance']
        
        embed = discord.Embed(title="🛒 ยืนยันคำสั่งซื้อ", color=THEME_COLOR)
        embed.add_field(name="สินค้า", value=prod['name'])
        embed.add_field(name="ราคา", value=f"{prod['price']} บาท")
        embed.add_field(name="เงินคงเหลือ", value=f"{bal:.2f} บาท")
        
        # รีเซ็ต Placeholder ให้กลับมาสวยงาม
        select.placeholder = "🛒 คลิกเพื่อเลือกสินค้าที่ต้องการสั่งซื้อ..."
        await interaction.message.edit(view=self)
        
        await interaction.response.send_message(embed=embed, view=ConfirmBuyView(prod, interaction.user.id), ephemeral=True)

    @discord.ui.button(label="เติมเงิน", style=discord.ButtonStyle.primary, emoji="💳", row=1)
    async def topup(self, interaction, button): await interaction.response.send_modal(TopupModal())

    @discord.ui.button(label="เช็คยอด", style=discord.ButtonStyle.success, emoji="💰", row=1)
    async def check(self, interaction, button):
        bal = get_data(interaction.user.id)['balance']
        await interaction.response.send_message(f"💰 ยอดเงินคงเหลือ: `{bal:.2f}` บาท", ephemeral=True)

# =================================================================
# 🤖 BOT COMMANDS
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
    await bot.tree.sync()

@bot.tree.command(name="setup_shop")
async def setup_shop(interaction):
    await interaction.response.defer()
    
    # 🔥 ปรับปรุง: ลบรายการสินค้าที่เป็นข้อความยาวๆ ออก เพื่อให้ดู "เรียบร้อย"
    # และให้ลูกค้าไปกดดูใน Select Menu แทน
    desc = (
        "# 🛒 STORE SYSTEM\n"
        "ยินดีต้อนรับสู่ร้านค้าอัตโนมัติ 24 ชม.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "### 📌 วิธีการใช้งาน\n"
        "1. กดปุ่ม `💳 เติมเงิน` เพื่อรับ QR Code\n"
        "2. ส่งสลิปในห้องนี้เพื่อเติมเครดิต\n"
        "3. **เลือกสินค้าจากเมนูตัวเลือกด้านล่าง** เพื่อซื้อทันที\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    embed = discord.Embed(description=desc, color=THEME_COLOR)
    if SHOP_GIF_URL: embed.set_image(url=SHOP_GIF_URL)
    
    await interaction.channel.send(embed=embed, view=MainShopView())
    await interaction.followup.send("✅ Setup Done!", ephemeral=True)

@bot.tree.command(name="setup_dashboard")
async def setup_dash(interaction):
    embed = discord.Embed(title="🎛️ Admin Dashboard", color=discord.Color.orange())
    await interaction.channel.send(embed=embed, view=DashboardView())
    await interaction.response.send_message("Done", ephemeral=True)

@bot.tree.command(name="add_money")
async def add_money(interaction, user: discord.Member, amount: float):
    update_money(user.id, amount, True)
    await update_user_log(interaction.client, user.id)
    await interaction.response.send_message(f"✅ Added {amount} to {user.mention}")

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.channel.id == SLIP_CHANNEL_ID and message.attachments:
        msg = await message.channel.send("⏳ กำลังตรวจสอบสลิป...")
        try:
            success, amount, ref, info = check_slip_slipok(message.attachments[0].url)
            if success:
                if is_slip_used(ref):
                    await msg.edit(content="❌ สลิปซ้ำ")
                    return
                new_bal = update_money(message.author.id, amount, True)
                save_used_slip(ref)
                await update_user_log(bot, message.author.id)
                await msg.edit(content=f"✅ เติมเงินสำเร็จ {amount} บาท (คงเหลือ {new_bal})")
                if hist := bot.get_channel(HISTORY_CHANNEL_ID):
                    await hist.send(embed=discord.Embed(title="Log", description=f"{message.author.mention} +{amount}", color=SUCCESS_COLOR))
            else:
                await msg.edit(content=f"❌ {info}")
        except Exception as e:
            await msg.edit(content=f"Error: {e}")
        await asyncio.sleep(5)
        await message.delete()
        await msg.delete()

server_on()
bot.run(os.getenv('TOKEN'))

