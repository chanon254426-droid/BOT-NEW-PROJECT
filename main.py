import os
import discord
from discord.ext import commands
from discord import app_commands
import json
import requests
from myserver import server_on  

# =================================================================
# ⚙️ ส่วนที่ 1: ตั้งค่าบอท (แก้ไขข้อมูลตรงนี้)
# =================================================================

DISCORD_BOT_TOKEN = os.environ.get('TOKEN') # หรือใส่ 'TOKEN_ของคุณ'
EASYSLIP_API_KEY = 'c5873b2f-d7a9-4f03-9267-166829da1f93' 

# ID ห้องต่างๆ (ตัวเลข)
SHOP_CHANNEL_ID = 1416797606180552714  # ห้องกดซื้อของ
SLIP_CHANNEL_ID = 1416797464350167090  # ห้องส่งสลิป
ADMIN_LOG_ID = 1441466742885978144    # ห้องดูประวัติ (Admin)

# ลิงก์รูป QR Code
QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg' 

# 📦 รายการสินค้า 14 ชิ้น (แก้ชื่อ, ราคา, role_id ตรงนี้)
PRODUCTS = [
    {"id": "item1",  "name": "𝙳𝙾𝙽𝙰𝚃𝙴⭐", "price": 89, "role_id": 1431279741440364625},
    {"id": "item2",  "name": "ᴍᴏᴅ ᴅᴇᴠᴏᴜʀ 👻", "price": 120, "role_id": 1432064283767738571},
    {"id": "item3",  "name": "SETTING PREMIUM", "price": 169, "role_id": 1419373724653588540},
    {"id": "item4",  "name": "𝙰𝙻𝙻 𝚆𝙴𝙰𝙿𝙾𝙽", "price": 139, "role_id": 1444190694674792592},
    {"id": "item5",  "name": "ลบประวัติ CMD", "price": 79, "role_id": 1444191270372114552},
    {"id": "item6",  "name": "ลบประวัติการรันโปรเเกรม", "price": 49, "role_id": 1444191566838370365},
    {"id": "item7",  "name": "𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟷💎", "price": 25, "role_id": 1431250097135419505},
    {"id": "item8",  "name": "𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟸🌈", "price": 25, "role_id": 1431234346202959973},
    {"id": "item9",  "name": "𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟹🔥", "price": 25, "role_id": 1431249584054734929},
    {"id": "item10", "name": "𝚜𝚞𝚗𝚔𝚒𝚜𝚜𝚎𝚍🎧", "price": 25, "role_id": 1431278653760737340},
    {"id": "item11", "name": "𝚖𝚊𝚐𝚒𝚌𝚎𝚢𝚎🌃", "price": 25, "role_id": 1431231640058990652},
    {"id": "item12", "name": "𝚁𝚎𝚊𝚕𝚕𝚒𝚟𝚎 ✿", "price": 25, "role_id": 1431204938373140513},
    {"id": "item13", "name": "ꜰᴀʟʟɪɴɢ🏞️", "price": 25, "role_id": 1444192569754910770},
    {"id": "item14", "name": "𝙱𝙾𝙾𝚂𝚃 𝙵𝙿𝚂 🎮", "price": 99, "role_id": 1432010188340199504},
]

# =================================================================
# 💾 ส่วนที่ 2: ระบบฐานข้อมูล & API
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
    """ส่งรูปไปเช็คกับ EasySlip"""
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
# 🖥️ ส่วนที่ 3: หน้าต่าง UI (Dropdown & ปุ่ม)
# =================================================================

class TopupView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.select(
        placeholder="💳 เลือกช่องทางเติมเงิน...",
        options=[discord.SelectOption(label="โอนผ่านบัญชี (Auto)", value="bank", emoji="🏦", description="สแกน QR Code แล้วเงินเข้าทันที")],
        custom_id="topup_select"
    )
    async def callback(self, interaction, select):
        if select.values[0] == "bank":
            embed = discord.Embed(title="🏦 เติมเงินอัตโนมัติ (Auto)", description=f"1. สแกน QR Code ด้านล่าง\n2. บันทึกรูปสลิป\n3. ส่งสลิปที่ห้อง <#{SLIP_CHANNEL_ID}>\n\n**ระบบจะเติมเงินให้อัตโนมัติใน 3 วินาที**", color=discord.Color.green())
            embed.set_image(url=QR_CODE_URL)
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="เช็คยอดเงิน", style=discord.ButtonStyle.secondary, emoji="💰", custom_id="check_bal")
    async def check(self, interaction, button):
        bal = get_balance(interaction.user.id)
        await interaction.response.send_message(f"💰 ยอดเงินคงเหลือของคุณ: **{bal:.2f} บาท**", ephemeral=True)

    # สร้างตัวเลือกสินค้าจากรายการ PRODUCTS ด้านบน (รองรับได้สูงสุด 25 ชิ้น)
    @discord.ui.select(
        placeholder="🛒 คลิกเพื่อเลือกสินค้าที่ต้องการซื้อ...",
        options=[
            discord.SelectOption(
                label=p["name"], 
                value=p["id"], 
                description=f"ราคา {p['price']} บาท",
                emoji="🏷️"
            ) for p in PRODUCTS
        ],
        custom_id="shop_select"
    )
    async def buy(self, interaction, select):
        pid = select.values[0]
        prod = next(p for p in PRODUCTS if p["id"] == pid)
        
        # ตัดเงิน
        if deduct_balance(interaction.user.id, prod["price"]):
            # ให้ยศ
            role = interaction.guild.get_role(prod["role_id"])
            if role: 
                await interaction.user.add_roles(role)
                msg = f"✅ **ซื้อสำเร็จ!** ได้รับยศ {role.mention} แล้ว"
            else:
                msg = "⚠️ ซื้อสำเร็จ แต่ไม่พบยศในระบบ (กรุณาแจ้งแอดมิน)"
            
            await interaction.response.send_message(msg, ephemeral=True)
            
            # Log ลงห้องแอดมิน
            if log := interaction.guild.get_channel(ADMIN_LOG_ID):
                await log.send(f"🛒 **[BUY]** {interaction.user.mention} ซื้อ **{prod['name']}** ({prod['price']} บาท)")
        else:
            await interaction.response.send_message(f"❌ **เงินไม่พอ!** ขาดอีก `{prod['price'] - get_balance(interaction.user.id):.2f}` บาท", ephemeral=True)

# =================================================================
# 🤖 ส่วนที่ 4: การทำงานหลักของบอท
# =================================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot Online: {bot.user}")
    # โหลด View ค้างไว้เพื่อให้ปุ่มทำงานได้ตลอด
    bot.add_view(TopupView())
    bot.add_view(ShopView())
    try:
        await bot.tree.sync() # Sync คำสั่ง Slash Command
        print("✅ Slash Commands Synced")
    except Exception as e:
        print(e)

@bot.tree.command(name="setup_shop", description="[Admin] สร้างหน้าต่างร้านค้า")
@app_commands.default_permissions(administrator=True)
async def setup(interaction):
    await interaction.channel.send(view=TopupView())
    await interaction.channel.send(view=ShopView())
    await interaction.response.send_message("✅ สร้างหน้าร้านค้าเรียบร้อย", ephemeral=True)

# 🔥 ระบบตรวจสลิปอัตโนมัติ (ไม่มีปุ่มกด Approve แล้ว)
@bot.event
async def on_message(message):
    if message.author.bot: return

    # เช็คว่าส่งรูปในห้องสลิปใช่ไหม
    if message.channel.id == SLIP_CHANNEL_ID and message.attachments:
        
        # แจ้งว่ากำลังทำงาน
        status_msg = await message.channel.send(f"⏳ กำลังตรวจสอบสลิปของ {message.author.mention}...")
        
        # ส่ง API เช็ค
        success, amount, result_msg = check_slip_easyslip(message.attachments[0].url)
        
        if success:
            # ✅ ผ่าน: เติมเงินเลย
            new_bal = add_balance(message.author.id, amount)
            
            # แก้ข้อความเป็นสำเร็จ
            await status_msg.edit(content=f"✅ **เติมเงินสำเร็จ!**\nได้รับเงิน: `{amount} บาท`\nยอดคงเหลือ: `{new_bal} บาท`\n(โดย {message.author.mention})")
            
            # Log ลงห้องแอดมิน
            if log := bot.get_channel(ADMIN_LOG_ID):
                await log.send(f"💰 **[TOPUP]** {message.author.mention} เติมเงินสำเร็จ {amount} บาท")
        else:
            # ❌ ไม่ผ่าน: แจ้งเตือน
            await status_msg.edit(content=f"❌ **ทำรายการไม่สำเร็จ**\nเหตุผล: `{result_msg}`\n(หากสลิปถูกต้องโปรดติดต่อแอดมิน)")
            
    await bot.process_commands(message)

# =================================================================
# 🚀 ส่วนที่ 5: เริ่มรันบอท (แก้ไขตามคำขอ)
# =================================================================

# ✅ บรรทัดนี้จะเรียก Web Server ให้ทำงานก่อนรันบอท
server_on()

# รันบอท
bot.run(os.getenv('TOKEN'))