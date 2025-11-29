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

DISCORD_BOT_TOKEN = os.environ.get('TOKEN') # ใส่ Token บอท
EASYSLIP_API_KEY = 'c5873b2f-d7a9-4f03-9267-166829da1f93'  # ใส่ API Key EasySlip

# ID ห้องต่างๆ
SHOP_CHANNEL_ID = 1416797606180552714  # ห้องขายของ
SLIP_CHANNEL_ID = 1416797464350167090  # ห้องส่งสลิป
ADMIN_LOG_ID = 1441466742885978144    # ห้อง Log

# 🖼️ ลิงก์รูปภาพ (แก้ตรงนี้)
QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg' 
SHOP_GIF_URL = 'https://media.discordapp.net/attachments/1303249085347926058/1444212368937586698/53ad0cc3373bbe0ea51dd878241952c6.gif?ex=692be314&is=692a9194&hm=bf9bfce543bee87e6334726e99e6f19f37cf457595e5e5b1ba05c0b678317cac&=&width=640&height=360' # <--- ⚠️ เอาลิงก์ GIF มาใส่ตรงนี้ครับ

# 📦 รายการสินค้า 14 ชิ้น (อัปเดตใหม่ตามสั่ง)
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
    {"id": "item12", "emoji": "✿",   "name": "𝚁𝚎𝚊𝚕𝚕𝚒𝚟𝚎",       "price": 25,  "role_id": 1431204938373140513},
    {"id": "item13", "emoji": "🏞️",  "name": "ꜰᴀʟʟɪɴɢ",        "price": 25,  "role_id": 1444192569754910770},
    {"id": "item14", "emoji": "🎮",  "name": "𝙱𝙾𝙾𝚂𝚃 𝙵𝙿𝚂",       "price": 99,  "role_id": 1432010188340199504},
]

# =================================================================
# 💾 ส่วนที่ 2: Database & API
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
# 🖥️ ส่วนที่ 3: UI รวม (Button + Dropdown)
# =================================================================

class MainShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    # --- แถวที่ 1 : ปุ่มกด (Buttons) ---
    @discord.ui.button(label="เติมเงิน (QR Code)", style=discord.ButtonStyle.primary, emoji="💳", row=0, custom_id="topup_btn")
    async def topup(self, interaction, button):
        embed = discord.Embed(
            title="🏦 เติมเงินอัตโนมัติ (Auto Topup)",
            description=f"1. สแกน QR Code เพื่อโอนเงิน\n2. ส่งสลิปที่ห้อง <#{SLIP_CHANNEL_ID}>\n3. รอระบบตรวจสอบและเพิ่มเครดิตทันที", 
            color=discord.Color.gold()
        )
        embed.set_image(url=QR_CODE_URL)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="เช็คยอดเงิน", style=discord.ButtonStyle.success, emoji="💰", row=0, custom_id="check_bal")
    async def check(self, interaction, button):
        bal = get_balance(interaction.user.id)
        await interaction.response.send_message(f"💳 ยอดเงินคงเหลือของคุณ: **{bal:.2f} บาท**", ephemeral=True)

    @discord.ui.button(label="ล้างตัวเลือก", style=discord.ButtonStyle.danger, emoji="🗑️", row=0, custom_id="clear_select")
    async def clear(self, interaction, button):
        await interaction.response.send_message("🗑️ ล้างการเลือกเรียบร้อยแล้ว", ephemeral=True)

    # --- แถวที่ 2 : รายการสินค้า (Dropdown) ---
    @discord.ui.select(
        placeholder="🛒 คลิกเพื่อเลือกสินค้าที่ต้องการซื้อ...",
        options=[
            discord.SelectOption(
                label=f"{p['name']}", # ชื่อสินค้า
                value=p["id"], 
                description=f"ราคา {p['price']} บาท",
                emoji=p["emoji"]
            ) for p in PRODUCTS
        ],
        custom_id="shop_select",
        row=1 
    )
    async def buy(self, interaction, select):
        pid = select.values[0]
        prod = next(p for p in PRODUCTS if p["id"] == pid)
        
        if deduct_balance(interaction.user.id, prod["price"]):
            role = interaction.guild.get_role(prod["role_id"])
            if role: 
                await interaction.user.add_roles(role)
                msg = f"✅ **ชำระเงินสำเร็จ!** ได้รับยศ {role.mention} เรียบร้อยแล้ว"
            else:
                msg = "⚠️ ซื้อสำเร็จ (แต่ไม่พบยศในระบบ โปรดติดต่อแอดมิน)"
            
            await interaction.response.send_message(msg, ephemeral=True)
            
            if log := interaction.guild.get_channel(ADMIN_LOG_ID):
                await log.send(f"🛒 **[BUY]** {interaction.user.mention} ซื้อ **{prod['name']}** ราคา {prod['price']} บาท")
        else:
            await interaction.response.send_message(f"❌ **เงินไม่พอ!** ขาดอีก `{prod['price'] - get_balance(interaction.user.id):.2f}` บาท\n(กดปุ่ม 'เติมเงิน' ด้านบนได้เลย)", ephemeral=True)

# =================================================================
# 🤖 ส่วนที่ 4: Main Logic
# =================================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot Online: {bot.user}")
    bot.add_view(MainShopView()) 
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)

@bot.tree.command(name="setup_shop", description="[Admin] สร้างหน้าต่างร้านค้า (GIF + Instructions)")
@app_commands.default_permissions(administrator=True)
async def setup(interaction):
    # ข้อความคำอธิบายแบบหรูๆ (ตามที่คุณขอ)
    description_text = (
        "ยินดีต้อนรับสู่ **PREMIUM STORE** ระบบอัตโนมัติ 24 ชม.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📜 **ขั้นตอนการสั่งซื้อสินค้า**\n"
        "1️⃣ กดปุ่ม **`เติมเงิน (QR Code)`** และส่งสลิปเพื่อเติมเครดิต\n"
        "2️⃣ กดปุ่ม **`เช็คยอดเงิน`** เพื่อตรวจสอบความถูกต้อง\n"
        "3️⃣ เลือกสินค้าที่ต้องการจาก **`เมนูด้านล่าง`** เพื่อสั่งซื้อทันที\n\n"
        "⚠️ **ข้อตกลงและเงื่อนไข**\n"
        "• โปรดตรวจสอบยอดเงินให้เพียงพอก่อนกดสั่งซื้อ\n"
        "• สินค้าซื้อแล้วไม่รับเปลี่ยนหรือคืนเงินทุกกรณี\n"
        "• หากพบปัญหาติดต่อแอดมินผ่านการเปิดตั๋วเท่านั้น\n\n"
        "🛒 **เลือกสินค้าที่คุณต้องการได้เลย!** 👇"
    )

    embed_shop = discord.Embed(
        title="✨ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐒𝐇𝐎𝐏 ✨",
        description=description_text,
        color=discord.Color.from_rgb(47, 49, 54) 
    )
    
    # ใส่รูป GIF ที่คุณจะเอาลิงก์มาใส่
    if SHOP_GIF_URL.startswith("http"):
        embed_shop.set_image(url=SHOP_GIF_URL)
    else:
        embed_shop.set_footer(text="⚠️ อย่าลืมใส่ลิงก์รูป GIF ในโค้ดบรรทัดที่ 26")

    await interaction.channel.send(embed=embed_shop, view=MainShopView())
    await interaction.response.send_message("✅ สร้างร้านค้าเรียบร้อย!", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot: return

    if message.channel.id == SLIP_CHANNEL_ID and message.attachments:
        status_msg = await message.channel.send(f"⏳ ระบบกำลังตรวจสอบสลิปของ {message.author.mention} ...")
        success, amount, result_msg = check_slip_easyslip(message.attachments[0].url)
        
        if success:
            new_bal = add_balance(message.author.id, amount)
            success_embed = discord.Embed(title="✅ เติมเงินสำเร็จ!", color=discord.Color.green())
            success_embed.description = f"**ผู้เติม:** {message.author.mention}\n**จำนวนเงิน:** `{amount} บาท`\n**ยอดเงินคงเหลือ:** `{new_bal} บาท`"
            
            await status_msg.edit(content=None, embed=success_embed)
            if log := bot.get_channel(ADMIN_LOG_ID):
                await log.send(f"💰 **[TOPUP]** {message.author.mention} เติมเงินสำเร็จ {amount} บาท (Auto)")
        else:
            await status_msg.edit(content=f"❌ **ทำรายการไม่สำเร็จ**\nเหตุผล: `{result_msg}`")

    await bot.process_commands(message)

server_on()
bot.run(os.getenv('TOKEN'))
