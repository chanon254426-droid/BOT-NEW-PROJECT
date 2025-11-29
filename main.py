import os
import discord
from discord.ext import commands
from discord import app_commands
import json
import requests
from myserver import server_on  # <--- เรียกใช้งานไฟล์ myserver.py

# =================================================================
# ⚙️ ส่วนที่ 1: ตั้งค่าบอท (แก้ไขข้อมูลตรงนี้)
# =================================================================

DISCORD_BOT_TOKEN = os.environ.get('TOKEN') # ใส่ Token บอท
EASYSLIP_API_KEY = 'c5873b2f-d7a9-4f03-9267-166829da1f93'  # ใส่ API Key EasySlip

# ID ห้องต่างๆ
SHOP_CHANNEL_ID = 1416797606180552714  # ห้องขายของ
SLIP_CHANNEL_ID = 1416797464350167090 # ห้องส่งสลิป
ADMIN_LOG_ID = 1441466742885978144    # ห้อง Log

# ลิงก์ QR Code
QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg' 

# 📦 รายการสินค้า (ผมแกะชื่อและ Emoji ตามรูปให้แล้ว **อย่าลืมใส่ role_id**)
PRODUCTS = [
    {"id": "p1",  "emoji": "👑", "name": "SETTING PREMIUM", "price": 169, "role_id": 1111111111},
    {"id": "p2",  "emoji": "👻", "name": "MOD DEVOUR",      "price": 120, "role_id": 2222222222},
    {"id": "p3",  "emoji": "⭐", "name": "DONATE",          "price": 89,  "role_id": 3333333333},
    {"id": "p4",  "emoji": "🌷", "name": "Reallive",        "price": 25,  "role_id": 4444444444},
    {"id": "p5",  "emoji": "🎧", "name": "sunkissed",       "price": 25,  "role_id": 5555555555},
    {"id": "p6",  "emoji": "🌃", "name": "magiceye",        "price": 25,  "role_id": 6666666666},
    {"id": "p7",  "emoji": "💎", "name": "realisticV1",     "price": 25,  "role_id": 7777777777},
    {"id": "p8",  "emoji": "🌈", "name": "realisticV2",     "price": 25,  "role_id": 8888888888},
    {"id": "p9",  "emoji": "🔥", "name": "realisticV3",     "price": 25,  "role_id": 9999999999},
    {"id": "p10", "emoji": "🎮", "name": "BOOSTFPS",        "price": 99,  "role_id": 1010101010},
]

# =================================================================
# 💾 ส่วนที่ 2: Database & API (ระบบหลังบ้าน)
# =================================================================
DB_FILE = "user_balance.json"

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump({}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

def get_balance(user_id):
    return load_db().get(str(user_id), 0)

def add_balance(user_id, amount):
    db = load_db()
    uid = str(user_id)
    db[uid] = db.get(uid, 0) + amount
    save_db(db)
    return db[uid]

def deduct_balance(user_id, amount):
    db = load_db()
    uid = str(user_id)
    current = db.get(uid, 0)
    if current >= amount:
        db[uid] = current - amount
        save_db(db)
        return True
    return False

def check_slip_easyslip(image_url):
    """ส่งรูปไปเช็คกับ EasySlip แบบ Auto"""
    try:
        response = requests.post(
            "https://developer.easyslip.com/api/v1/verify",
            headers={'Authorization': f'Bearer {EASYSLIP_API_KEY}'},
            json={'image': image_url},
            timeout=10
        )
        data = response.json()
        if response.status_code == 200 and data['status'] == 200:
            return True, data['data']['amount'], "OK"
        else:
            return False, 0, data.get('message', 'Error')
    except Exception as e:
        return False, 0, str(e)

# =================================================================
# 🖥️ ส่วนที่ 3: UI สวยงาม (Dropdown & Buttons)
# =================================================================

class TopupView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.select(
        placeholder="💳 เลือกช่องทางเติมเงิน...",
        options=[discord.SelectOption(label="โอนผ่านบัญชี (Auto)", value="bank", emoji="🏦", description="ระบบตรวจสลิปอัตโนมัติ 24 ชม.")],
        custom_id="topup_select"
    )
    async def callback(self, interaction, select):
        if select.values[0] == "bank":
            embed = discord.Embed(
                title="🏦 เติมเงินอัตโนมัติ (Auto Topup)",
                description=f"1. สแกน QR Code เพื่อโอนเงิน\n2. นำรูปสลิปส่งที่ห้อง <#{SLIP_CHANNEL_ID}>\n3. รอระบบตรวจสอบและเพิ่มเงินทันที (ไม่ต้องรอแอดมิน)", 
                color=discord.Color.from_rgb(255, 215, 0)
            )
            embed.set_image(url=QR_CODE_URL)
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    # ปุ่มเช็คยอดเงิน
    @discord.ui.button(label="เช็คยอดเงิน", style=discord.ButtonStyle.success, emoji="💰", custom_id="check_bal")
    async def check(self, interaction, button):
        bal = get_balance(interaction.user.id)
        await interaction.response.send_message(f"💳 ยอดเงินคงเหลือของคุณ: **{bal:.2f} บาท**", ephemeral=True)

    # ปุ่มเคลียร์ค่า (ตามที่ขอข้อ 3)
    @discord.ui.button(label="ล้างตัวเลือก", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="clear_select")
    async def clear(self, interaction, button):
        await interaction.response.send_message("🗑️ ล้างการเลือกเรียบร้อยแล้ว (คุณสามารถเลือกสินค้าใหม่ได้เลย)", ephemeral=True)

    # Dropdown เลือกสินค้า (แต่งสวยๆ ตามรูปข้อ 2)
    @discord.ui.select(
        placeholder="🛒 เลือกยศที่คุณต้องการสั่งซื้อ...",
        options=[
            discord.SelectOption(
                label=f"{p['emoji']} {p['name']} | {p['price']} บาท", # โชว์แบบ Emoji + ชื่อ + ราคา
                value=p["id"], 
                description=f"ราคา {p['price']} บาท",
                emoji=p["emoji"]
            ) for p in PRODUCTS
        ],
        custom_id="shop_select"
    )
    async def buy(self, interaction, select):
        pid = select.values[0]
        prod = next(p for p in PRODUCTS if p["id"] == pid)
        
        # ตัดเงิน
        if deduct_balance(interaction.user.id, prod["price"]):
            role = interaction.guild.get_role(prod["role_id"])
            if role: 
                await interaction.user.add_roles(role)
                msg = f"✅ **ซื้อสำเร็จ!** ได้รับยศ {role.mention} เรียบร้อยแล้ว"
            else:
                msg = "⚠️ ซื้อสำเร็จ (แต่ไม่พบยศในระบบ โปรดติดต่อแอดมิน)"
            
            await interaction.response.send_message(msg, ephemeral=True)
            
            # Log
            if log := interaction.guild.get_channel(ADMIN_LOG_ID):
                await log.send(f"🛒 **[BUY]** {interaction.user.mention} ซื้อ **{prod['name']}** ราคา {prod['price']} บาท")
        else:
            await interaction.response.send_message(f"❌ **เงินไม่พอ!** ขาดอีก `{prod['price'] - get_balance(interaction.user.id):.2f}` บาท\n(กรุณาเติมเงินที่เมนูด้านบน)", ephemeral=True)

# =================================================================
# 🤖 ส่วนที่ 4: การทำงานหลัก (Main Logic)
# =================================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot Online: {bot.user}")
    bot.add_view(TopupView())
    bot.add_view(ShopView())
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)

# คำสั่งสร้างหน้าร้านค้า (แต่ง Embed ให้เหมือนรูปข้อ 1)
@bot.tree.command(name="setup_shop", description="[Admin] สร้างหน้าต่างร้านค้าแบบ Full Option")
@app_commands.default_permissions(administrator=True)
async def setup(interaction):
    # 1. ส่วนเติมเงิน
    embed_topup = discord.Embed(
        title="💳 เติมเงินเข้าระบบ (Topup)",
        description="เติมเงินผ่าน QR Code (รองรับทุกธนาคาร)\nเงินเข้าอัตโนมัติทันที ไม่ต้องรออนุมัติ",
        color=discord.Color.gold()
    )
    # embed_topup.set_image(url="ใส่ลิงก์รูปแบนเนอร์เติมเงินตรงนี้ถ้ามี")

    # 2. ส่วนร้านค้า (สร้างรายการสินค้าแบบสวยๆ)
    desc_list = "**เลือกยศที่คุณต้องการสั่งซื้อจากเมนูด้านล่าง:**\n\n"
    for p in PRODUCTS:
        # จัด Format: 👑 SETTING PREMIUM (@Role) | ราคา 169 บาท
        desc_list += f"{p['emoji']} **{p['name']}** (<@&{p['role_id']}>)\n| `ราคา {p['price']} บาท`\n\n"

    embed_shop = discord.Embed(
        title="🛒 ร้านค้าจำหน่ายยศ Premium",
        description=desc_list,
        color=discord.Color.from_rgb(47, 49, 54) # สีเทาเข้มสวยๆ แบบ Discord
    )
    # embed_shop.set_image(url="ใส่ลิงก์รูปแบนเนอร์ร้านค้าตรงนี้ถ้ามี")

    await interaction.channel.send(embed=embed_topup, view=TopupView())
    await interaction.channel.send(embed=embed_shop, view=ShopView())
    await interaction.response.send_message("✅ สร้างร้านค้าเสร็จสิ้น!", ephemeral=True)

# 🔥 ระบบ Auto Check Slip (ไม่มีปุ่มกด Confirm แล้ว)
@bot.event
async def on_message(message):
    if message.author.bot: return

    # ถ้ามีรูปส่งมาในห้องสลิป
    if message.channel.id == SLIP_CHANNEL_ID and message.attachments:
        
        # แจ้งเตือนว่ากำลังเช็ค
        status_msg = await message.channel.send(f"⏳ ระบบกำลังตรวจสอบสลิปของ {message.author.mention} ...")
        
        # ส่งให้ EasySlip ตรวจ
        success, amount, result_msg = check_slip_easyslip(message.attachments[0].url)
        
        if success:
            # ✅ ผ่าน -> เติมเงินเลย
            new_bal = add_balance(message.author.id, amount)
            
            success_embed = discord.Embed(title="✅ เติมเงินสำเร็จ!", color=discord.Color.green())
            success_embed.description = f"**ผู้เติม:** {message.author.mention}\n**จำนวนเงิน:** `{amount} บาท`\n**ยอดเงินคงเหลือ:** `{new_bal} บาท`"
            success_embed.set_footer(text="ขอบคุณที่ใช้บริการ")
            
            await status_msg.edit(content=None, embed=success_embed)
            
            # Log
            if log := bot.get_channel(ADMIN_LOG_ID):
                await log.send(f"💰 **[TOPUP]** {message.author.mention} เติมเงินสำเร็จ {amount} บาท (Auto)")
        else:
            # ❌ ไม่ผ่าน
            await status_msg.edit(content=f"❌ **ทำรายการไม่สำเร็จ**\nเหตุผล: `{result_msg}`\n(หากมั่นใจว่าถูก โปรดติดต่อแอดมิน)")

    await bot.process_commands(message)

# =================================================================
# 🚀 ส่วนที่ 5: เริ่มรันบอท (Server On อยู่ตรงนี้!)
# =================================================================

server_on() #
bot.run(os.getenv('TOKEN'))
