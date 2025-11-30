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

# ลิงก์รูปภาพ
QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg' 
SHOP_GIF_URL = 'https://media.discordapp.net/attachments/1303249085347926058/1444212368937586698/53ad0cc3373bbe0ea51dd878241952c6.gif?ex=692be314&is=692a9194&hm=bf9bfce543bee87e6334726e99e6f19f37cf457595e5e5b1ba05c0b678317cac&=&width=640&height=360'
# รูป GIF ตอนซื้อสำเร็จ
SUCCESS_GIF_URL = 'https://cdn.discordapp.com/attachments/1303249085347926058/1444212370573361153/f5f27448c036af645c27467c789ad759.gif?ex=692d3495&is=692be315&hm=86e870796dd13f905523c4a352baad7daf382a9926730ac97ee32f5705a69962&'

# 🔥 [SMART CHECK] ตั้งค่าความปลอดภัย
EXPECTED_NAMES = ['ชานนท์ ขันทอง', 'Chanon Khantong', 'chanon khantong'] 
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
# 💾 ระบบฐานข้อมูล (ปรับปรุงให้เหนียวแน่น ไม่หายง่ายๆ)
# =================================================================
DB_FILE = "user_balance.json"
SLIP_DB_FILE = "used_slips.json"

def load_db():
    # ถ้าไม่มีไฟล์ ให้สร้างใหม่
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump({}, f)
        print("📂 สร้างไฟล์ Database ใหม่เรียบร้อย")
        return {}
    
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict): 
                print("⚠️ Database เสียหาย! กำลังรีเซ็ต...")
                return {}
            print(f"📂 โหลดข้อมูลลูกค้าสำเร็จ: {len(data)} คน")
            return data
    except Exception as e:
        print(f"❌ Load DB Error: {e}")
        return {}

def save_db(data):
    try:
        with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ Save DB Error: {e}")

def get_balance(user_id):
    db = load_db()
    raw_val = db.get(str(user_id), 0.0)
    if isinstance(raw_val, dict): return 0.0
    return float(raw_val)

def add_balance(user_id, amount):
    db = load_db() # โหลดข้อมูลล่าสุดเสมอ
    uid = str(user_id)
    current = float(db.get(uid, 0.0))
    
    new_bal = current + float(amount)
    db[uid] = new_bal
    
    save_db(db) # บันทึกทันที
    return new_bal

def deduct_balance(user_id, amount):
    db = load_db() # โหลดข้อมูลล่าสุดเสมอ
    uid = str(user_id)
    current = float(db.get(uid, 0.0))
    cost = float(amount)
    
    if current >= cost:
        db[uid] = current - cost
        save_db(db) # บันทึกทันที
        return True
    return False

def is_slip_used(trans_ref):
    if not os.path.exists(SLIP_DB_FILE): return False
    try:
        with open(SLIP_DB_FILE, "r") as f:
            return trans_ref in json.load(f)
    except:
        return False

def save_used_slip(trans_ref):
    used_slips = []
    if os.path.exists(SLIP_DB_FILE):
        try:
            with open(SLIP_DB_FILE, "r") as f:
                used_slips = json.load(f)
        except:
            pass
    used_slips.append(trans_ref)
    with open(SLIP_DB_FILE, "w") as f:
        json.dump(used_slips, f, indent=4)

# 🔥 ระบบเช็คสลิป
def check_slip_easyslip(image_url):
    print(f"Checking slip: {image_url}")
    try:
        img_response = requests.get(image_url)
        if img_response.status_code != 200: return False, 0, None, "ดาวน์โหลดรูปไม่สำเร็จ"
        
        files = {'file': ('slip.jpg', io.BytesIO(img_response.content), 'image/jpeg')}
        response = requests.post(
            "https://developer.easyslip.com/api/v1/verify",
            headers={'Authorization': f'Bearer {EASYSLIP_API_KEY}'},
            files=files, timeout=15
        )
        
        data = response.json()
        
        if response.status_code == 200 and data['status'] == 200:
            slip_data = data['data']
            trans_ref = slip_data['transRef']
            
            raw_amount = slip_data['amount']
            if isinstance(raw_amount, dict): raw_amount = raw_amount.get('amount', 0)
            amount_float = float(raw_amount)

            if amount_float < MIN_AMOUNT:
                return False, 0, None, f"❌ ยอดโอนต่ำกว่ากำหนด ({amount_float} < {MIN_AMOUNT})"

            receiver_info = slip_data.get('receiver', {})
            receiver_name = receiver_info.get('displayName', '') or receiver_info.get('name', '')
            
            if receiver_name:
                name_matched = False
                for name in EXPECTED_NAMES:
                    if name in receiver_name:
                        name_matched = True
                        break
                if not name_matched:
                    return False, 0, None, f"❌ ชื่อผู้รับเงินในสลิปไม่ถูกต้อง (โอนให้: {receiver_name})"

            try:
                slip_date_str = str(slip_data.get('date', '')) + " " + str(slip_data.get('time', ''))
                clean_str = slip_date_str.replace("T", " ").replace("Z", "")
                clean_str = re.sub(r'\+.*', '', clean_str).strip()
                if "." in clean_str: clean_str = clean_str.split(".")[0]
                
                slip_dt = datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
                if slip_dt.year > 2500: slip_dt = slip_dt.replace(year=slip_dt.year - 543)
                
                now = datetime.utcnow() + timedelta(hours=7)
                time_diff = (now - slip_dt).total_seconds() / 60
                
                if time_diff > 5: 
                    return False, 0, None, f"❌ สลิปเก่าเกินไป ({int(time_diff)} นาทีที่แล้ว)"
            except Exception as e:
                pass 

            return True, amount_float, trans_ref, "OK"
        else:
            return False, 0, None, data.get('message', 'สลิปไม่ถูกต้อง หรือไม่ชัดเจน')
    except Exception as e:
        return False, 0, None, f"System Error: {str(e)}"

# =================================================================
# 🛒 View ยืนยันการสั่งซื้อ (UI สวยงาม)
# =================================================================

class ConfirmBuyView(discord.ui.View):
    def __init__(self, product, user_id):
        super().__init__(timeout=60)
        self.product = product
        self.user_id = user_id

    @discord.ui.button(label="✅ ยืนยันการชำระเงิน", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("❌ ไม่ใช่รายการของคุณ", ephemeral=True)

        user_bal = get_balance(interaction.user.id)
        price = self.product["price"]

        if user_bal < price:
            await interaction.response.edit_message(content=f"❌ **เงินไม่พอ!** ขาดอีก `{price - user_bal}` บาท", view=None, embed=None)
            return

        if deduct_balance(interaction.user.id, price):
            role = interaction.guild.get_role(self.product["role_id"])
            if role:
                try:
                    await interaction.user.add_roles(role)
                    order_id = str(uuid.uuid4())[:8].upper()
                    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                    
                    # 🔥 สร้าง Embed ใบเสร็จแบบตาราง (Code Block)
                    embed = discord.Embed(title="✅ สั่งซื้อสำเร็จ | Order Successful", color=discord.Color.green())
                    
                    # จัดข้อความให้ตรงกันด้วย Code Block
                    receipt_text = (
                        f"👤 ผู้ซื้อ   : {interaction.user.display_name}\n"
                        f"📦 สินค้า    : {self.product['name']}\n"
                        f"💎 ราคา     : {price} บาท\n"
                        f"🧾 Order ID : {order_id}\n"
                        f"🗓️ วันที่     : {now_str}"
                    )
                    embed.description = f"```yaml\n{receipt_text}\n```"
                    
                    embed.add_field(name="💰 ยอดเงินคงเหลือ", value=f"`{user_bal - price} บาท`", inline=True)
                    embed.add_field(name="📦 สถานะสินค้า", value="`✅ ส่งมอบแล้ว`", inline=True)
                    
                    embed.set_image(url=SUCCESS_GIF_URL)
                    embed.set_footer(text=f"ขอบคุณที่ใช้บริการครับ", icon_url=interaction.user.display_avatar.url)
                    
                    await interaction.response.edit_message(content=None, embed=embed, view=None)
                    
                    if log := interaction.guild.get_channel(ADMIN_LOG_ID):
                        await log.send(f"🛒 **[BUY]** {interaction.user.mention} ซื้อ **{self.product['name']}** (ID: {order_id})")
                except Exception as e:
                    await interaction.response.edit_message(content=f"⚠️ มอบยศไม่สำเร็จ: {e}", view=None, embed=None)
            else:
                await interaction.response.edit_message(content="⚠️ ไม่พบยศในเซิร์ฟเวอร์", view=None, embed=None)
        else:
            await interaction.response.edit_message(content="❌ ตัดเงินไม่สำเร็จ", view=None, embed=None)

    @discord.ui.button(label="❌ ยกเลิก", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        await interaction.response.edit_message(content="🗑️ ยกเลิกรายการเรียบร้อย", view=None, embed=None)

# =================================================================
# 📝 Modal & Main View
# =================================================================

class TopupModal(discord.ui.Modal, title="เติมเงินเข้าระบบ (Top Up)"):
    amount = discord.ui.TextInput(label="ระบุจำนวนเงิน (บาท)", placeholder="เช่น 50", style=discord.TextStyle.short, min_length=1, max_length=6)

    async def on_submit(self, interaction: discord.Interaction):
        input_amount = self.amount.value.strip()
        try:
            float(input_amount)
        except ValueError:
            await interaction.response.send_message("❌ กรุณากรอกเป็นตัวเลขเท่านั้น", ephemeral=True)
            return

        embed = discord.Embed(title="🧾 ใบแจ้งการชำระเงิน", description=f"ยอดโอน: **{input_amount} บาท**", color=discord.Color.gold())
        embed.add_field(name="วิธีการ", value="1. สแกน QR Code ด้านล่าง\n2. ส่งรูปสลิปในห้องนี้\n3. (ต้องส่งภายใน 5 นาที)", inline=False)
        embed.set_image(url=QR_CODE_URL)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MainShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="เติมเงิน (QR Code)", style=discord.ButtonStyle.primary, emoji="💳", row=0, custom_id="topup_btn")
    async def topup(self, interaction, button):
        await interaction.response.send_modal(TopupModal())

    @discord.ui.button(label="เช็คยอดเงิน", style=discord.ButtonStyle.success, emoji="💰", row=0, custom_id="check_bal")
    async def check(self, interaction, button):
        bal = get_balance(interaction.user.id)
        await interaction.response.send_message(f"💳 คงเหลือ: **{bal:.2f} บาท**", ephemeral=True)

    @discord.ui.button(label="ล้างตัวเลือก", style=discord.ButtonStyle.danger, emoji="🗑️", row=0, custom_id="clear_select")
    async def clear(self, interaction, button):
        await interaction.response.edit_message(view=MainShopView())

    @discord.ui.select(placeholder="🛒 เลือกสินค้า...", options=[discord.SelectOption(label=p['name'], value=p["id"], description=f"{p['price']} บาท", emoji=p["emoji"]) for p in PRODUCTS], custom_id="shop_select", row=1)
    async def buy(self, interaction, select):
        pid = select.values[0]
        prod = next(p for p in PRODUCTS if p["id"] == pid)
        user_bal = get_balance(interaction.user.id)
        
        embed = discord.Embed(title="🛒 ยืนยันการสั่งซื้อ", color=discord.Color.blue())
        embed.description = f"สินค้า: **{prod['name']}**\nราคา: **{prod['price']} บาท**"
        embed.add_field(name="คงเหลือของคุณ", value=f"{user_bal} บาท")
        
        if user_bal < prod['price']:
            embed.color = discord.Color.red()
            embed.set_footer(text="❌ ยอดเงินไม่เพียงพอ")
        
        await interaction.response.send_message(embed=embed, view=ConfirmBuyView(prod, interaction.user.id), ephemeral=True)

# =================================================================
# 🤖 Bot Events & Commands
# =================================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot Online: {bot.user}")
    # โหลด DB เพื่อเช็คว่าไฟล์อยู่ดีไหม
    load_db()
    bot.add_view(MainShopView()) 
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)

@bot.tree.command(name="setup_shop", description="[Admin] สร้างหน้าต่างร้านค้า")
@app_commands.default_permissions(administrator=True)
async def setup(interaction):
    await interaction.response.defer(ephemeral=True)
    embed_shop = discord.Embed(title="✨ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐒𝐇𝐎𝐏 ✨", description="กดปุ่มด้านล่างเพื่อทำรายการ 👇", color=discord.Color.from_rgb(47, 49, 54))
    if SHOP_GIF_URL.startswith("http"): embed_shop.set_image(url=SHOP_GIF_URL)
    await interaction.channel.send(embed=embed_shop, view=MainShopView())
    await interaction.followup.send("✅ Done!")

@bot.tree.command(name="add_money", description="[Admin] เติมเงินให้ลูกค้า")
@app_commands.default_permissions(administrator=True)
async def add_money_command(interaction: discord.Interaction, user: discord.Member, amount: float):
    new_bal = add_balance(user.id, amount)
    embed = discord.Embed(title="💸 ปรับยอดเงินสำเร็จ", description=f"ลูกค้า: {user.mention}\nยอดใหม่: {new_bal:.2f} บาท", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)
    if log := bot.get_channel(ADMIN_LOG_ID):
        await log.send(f"🔧 **[ADMIN]** {interaction.user.mention} ปรับเงิน {user.mention} {amount} บาท")

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.channel.id == SLIP_CHANNEL_ID and message.attachments:
        status_msg = await message.channel.send(f"⏳ กำลังตรวจสอบสลิป...")
        try:
            img_data = requests.get(message.attachments[0].url).content
            success, amount, trans_ref, result_msg = check_slip_easyslip(message.attachments[0].url)
            if success:
                if is_slip_used(trans_ref):
                    await status_msg.edit(content=f"❌ **สลิปซ้ำ!**")
                    return
                new_bal = add_balance(message.author.id, amount)
                save_used_slip(trans_ref) 

                success_embed = discord.Embed(title="✅ เติมเงินสำเร็จ!", color=discord.Color.green())
                success_embed.description = f"**ยอดเงินเข้า:** `{amount}` บาท\n**คงเหลือ:** `{new_bal}` บาท\n*(ข้อความนี้จะลบใน 10 วินาที)*"
                await status_msg.edit(content=message.author.mention, embed=success_embed)

                if hist_chan := bot.get_channel(HISTORY_CHANNEL_ID):
                    log_embed = discord.Embed(title="🧾 บันทึกการเติมเงิน", color=discord.Color.blue(), timestamp=datetime.utcnow())
                    log_embed.add_field(name="ลูกค้า", value=f"{message.author.mention}", inline=True)
                    log_embed.add_field(name="ยอดเติม", value=f"{amount} บาท", inline=True)
                    log_embed.add_field(name="คงเหลือรวม", value=f"{new_bal} บาท", inline=True)
                    log_embed.add_field(name="Ref", value=trans_ref, inline=False)
                    slip_file = discord.File(io.BytesIO(img_data), filename=f"slip_{trans_ref}.jpg")
                    log_embed.set_image(url=f"attachment://slip_{trans_ref}.jpg")
                    await hist_chan.send(embed=log_embed, file=slip_file)

                await asyncio.sleep(10)
                try:
                    await message.delete()
                    await status_msg.delete()
                except: pass
            else:
                await status_msg.edit(content=f"❌ ไม่ผ่าน: `{result_msg}`")
        except Exception as e:
            print(traceback.format_exc())
            await status_msg.edit(content=f"⚠️ ระบบ Error: `{str(e)}`")
    await bot.process_commands(message)

server_on()
bot.run(os.getenv('TOKEN'))
