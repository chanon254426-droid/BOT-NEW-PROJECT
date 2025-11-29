import os
import discord
from discord.ext import commands
from discord import app_commands
import json
import requests
import io
import traceback
from myserver import server_on

# =================================================================
# ⚙️ ตั้งค่าบอท
# =================================================================

# ⚠️ แก้ไข: ใส่ Token บอทของคุณตรงนี้
DISCORD_BOT_TOKEN = os.environ.get('TOKEN') 

# API Key EasySlip (ตัดช่องว่างให้แล้ว)
EASYSLIP_API_KEY = 'c5873b2f-d7a9-4f03-9267-166829da1f93'.strip()

SHOP_CHANNEL_ID = 1416797606180552714  
SLIP_CHANNEL_ID = 1416797464350167090  
ADMIN_LOG_ID = 1441466742885978144     

QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg' 
SHOP_GIF_URL = 'https://media.discordapp.net/attachments/1303249085347926058/1444212368937586698/53ad0cc3373bbe0ea51dd878241952c6.gif?ex=692be314&is=692a9194&hm=bf9bfce543bee87e6334726e99e6f19f37cf457595e5e5b1ba05c0b678317cac&=&width=640&height=360'

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
# 💾 ระบบฐานข้อมูล
# =================================================================
DB_FILE = "user_balance.json"

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump({}, f)
        return {}
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict): return {}
            return data
    except:
        return {}

def save_db(data):
    try:
        with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)
    except:
        pass

def get_balance(user_id):
    db = load_db()
    raw_val = db.get(str(user_id), 0.0)
    # ป้องกันค่าเป็น Dict
    if isinstance(raw_val, dict): return 0.0
    return float(raw_val)

def add_balance(user_id, amount):
    db = load_db()
    uid = str(user_id)
    current = get_balance(uid)
    try:
        add_val = float(amount)
        new_bal = current + add_val
        db[uid] = new_bal
        save_db(db)
        return new_bal
    except:
        return current

def deduct_balance(user_id, amount):
    db = load_db()
    uid = str(user_id)
    current = get_balance(uid)
    cost = float(amount)
    if current >= cost:
        db[uid] = current - cost
        save_db(db)
        return True
    return False

# 🔥 แก้ไขฟังก์ชันเช็คสลิป (แก้ API Error)
def check_slip_easyslip(image_url):
    print(f"กำลังเช็คสลิป: {image_url}")
    try:
        img_response = requests.get(image_url)
        if img_response.status_code != 200: return False, 0, "โหลดรูปไม่ได้"
        
        files = {'file': ('slip.jpg', io.BytesIO(img_response.content), 'image/jpeg')}
        response = requests.post(
            "https://developer.easyslip.com/api/v1/verify",
            headers={'Authorization': f'Bearer {EASYSLIP_API_KEY}'},
            files=files, timeout=15
        )
        
        data = response.json()
        
        if response.status_code == 200 and data['status'] == 200:
            raw_amount = data['data']['amount']
            
            # ✅ แก้ไขตรงนี้: ถ้าส่งมาเป็น Dict ให้ดึงค่าออกมา
            if isinstance(raw_amount, dict):
                print(f"⚠️ API ส่ง Dict: {raw_amount}")
                raw_amount = raw_amount.get('amount', 0)
            
            return True, float(raw_amount), "OK"
        else:
            return False, 0, data.get('message', 'Error')
    except Exception as e:
        print(f"API Error: {e}")
        return False, 0, str(e)

# =================================================================
# 📝 ส่วนที่เพิ่มใหม่: หน้าต่างกรอกจำนวนเงิน (Modal)
# =================================================================

class TopupModal(discord.ui.Modal, title="เติมเงินเข้าระบบ (Top Up)"):
    # ช่องกรอกข้อมูล
    amount = discord.ui.TextInput(
        label="ระบุจำนวนเงินที่ต้องการเติม (บาท)", 
        placeholder="เช่น 50, 100, 150", 
        style=discord.TextStyle.short,
        min_length=1,
        max_length=6
    )

    async def on_submit(self, interaction: discord.Interaction):
        # เมื่อลูกค้ากด Enter ส่งข้อมูล
        input_amount = self.amount.value
        
        # สร้างใบแจ้งยอดสวยๆ
        embed = discord.Embed(
            title="🧾 ใบแจ้งการชำระเงิน (Invoice)",
            description=f"กรุณาโอนเงินจำนวน **{input_amount} บาท** ผ่าน QR Code ด้านล่าง",
            color=discord.Color.from_rgb(255, 215, 0)
        )
        embed.add_field(name="1. สแกน QR Code", value="ใช้แอปธนาคารสแกนได้ทันที", inline=False)
        embed.add_field(name="2. บันทึกสลิป", value="เมื่อโอนเสร็จให้บันทึกรูปสลิปไว้", inline=False)
        embed.add_field(name="3. ยืนยันการเติมเงิน", value=f"นำรูปสลิปไปส่งที่ห้อง <#{SLIP_CHANNEL_ID}>", inline=False)
        embed.set_footer(text="ระบบตรวจสลิปอัตโนมัติ 24 ชม.")
        embed.set_image(url=QR_CODE_URL)

        await interaction.response.send_message(embed=embed, ephemeral=True)

# =================================================================
# 🖥️ UI หลัก
# =================================================================

class MainShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    # 🟢 ปุ่มเติมเงิน -> เด้ง Modal
    @discord.ui.button(label="เติมเงิน (QR Code)", style=discord.ButtonStyle.primary, emoji="💳", row=0, custom_id="topup_btn")
    async def topup(self, interaction, button):
        await interaction.response.send_modal(TopupModal())

    @discord.ui.button(label="เช็คยอดเงิน", style=discord.ButtonStyle.success, emoji="💰", row=0, custom_id="check_bal")
    async def check(self, interaction, button):
        bal = get_balance(interaction.user.id)
        await interaction.response.send_message(f"💳 ยอดเงินคงเหลือของคุณ: **{bal:.2f} บาท**", ephemeral=True)

    @discord.ui.button(label="ล้างตัวเลือก", style=discord.ButtonStyle.danger, emoji="🗑️", row=0, custom_id="clear_select")
    async def clear(self, interaction, button):
        await interaction.response.send_message("🗑️ ล้างการเลือกแล้ว", ephemeral=True)

    @discord.ui.select(
        placeholder="🛒 เลือกสินค้า...",
        options=[discord.SelectOption(label=p['name'], value=p["id"], description=f"{p['price']} บาท", emoji=p["emoji"]) for p in PRODUCTS],
        custom_id="shop_select", row=1 
    )
    async def buy(self, interaction, select):
        pid = select.values[0]
        prod = next(p for p in PRODUCTS if p["id"] == pid)
        if deduct_balance(interaction.user.id, prod["price"]):
            role = interaction.guild.get_role(prod["role_id"])
            if role: await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ ซื้อสำเร็จ! ได้รับยศ {role.mention}", ephemeral=True)
            if log := interaction.guild.get_channel(ADMIN_LOG_ID):
                await log.send(f"🛒 {interaction.user.mention} ซื้อ {prod['name']} ({prod['price']} บ.)")
        else:
            await interaction.response.send_message(f"❌ เงินไม่พอ! (ขาด {prod['price'] - get_balance(interaction.user.id):.2f})", ephemeral=True)

# =================================================================
# 🤖 Main Logic
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

@bot.tree.command(name="setup_shop", description="[Admin] สร้างหน้าต่างร้านค้า")
@app_commands.default_permissions(administrator=True)
async def setup(interaction):
    await interaction.response.defer(ephemeral=True) # กัน Timeout

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

    embed_shop = discord.Embed(
        title="✨ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐒𝐇𝐎𝐏 ✨",
        description=description_text,
        color=discord.Color.from_rgb(47, 49, 54) 
    )
    
    if SHOP_GIF_URL.startswith("http"):
        embed_shop.set_image(url=SHOP_GIF_URL)

    await interaction.channel.send(embed=embed_shop, view=MainShopView())
    await interaction.followup.send("✅ สร้างร้านค้าเรียบร้อย!")

@bot.event
async def on_message(message):
    if message.author.bot: return

    if message.channel.id == SLIP_CHANNEL_ID and message.attachments:
        status_msg = await message.channel.send(f"⏳ กำลังตรวจสอบสลิป... (Modal Mode)")
        
        try:
            success, amount, result_msg = check_slip_easyslip(message.attachments[0].url)
            
            if success:
                new_bal = add_balance(message.author.id, amount)
                success_embed = discord.Embed(title="✅ เติมเงินสำเร็จ!", color=discord.Color.green())
                success_embed.description = f"**จำนวน:** `{amount} บาท`\n**คงเหลือ:** `{new_bal} บาท`"
                
                await status_msg.delete()
                await message.channel.send(content=message.author.mention, embed=success_embed)
                
                if log := bot.get_channel(ADMIN_LOG_ID):
                    await log.send(f"💰 {message.author.mention} เติม {amount} บาท")
            else:
                await status_msg.edit(content=f"❌ ไม่ผ่าน: `{result_msg}`")

        except Exception as e:
            print(traceback.format_exc())
            await status_msg.edit(content=f"⚠️ เกิดข้อผิดพลาด: `{str(e)}`")

    await bot.process_commands(message)

server_on()
# ⚠️⚠️⚠️ เปลี่ยนเป็น Token ของคุณ ⚠️⚠️⚠️
bot.run(os.getenv('TOKEN'))
