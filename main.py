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

DISCORD_BOT_TOKEN = os.environ.get('TOKEN')
EASYSLIP_API_KEY = '12710681-efd6-412f-bce7-984feb9aa4cc'.strip()

# Channel IDs
SHOP_CHANNEL_ID = 1416797606180552714
SLIP_CHANNEL_ID = 1416797464350167090
ADMIN_LOG_ID = 1441466742885978144
HISTORY_CHANNEL_ID = 1444390933297631512

# Dashboard IDs
DASHBOARD_CMD_CHANNEL_ID = 1444662199674081423
DASHBOARD_LOG_CHANNEL_ID = 1444662604940181667

# Assets & Theme
THEME_COLOR = 0x2b2d31  
ACCENT_COLOR = 0x5865F2 
SUCCESS_COLOR = 0x57F287
ERROR_COLOR = 0xED4245

QR_CODE_URL = 'https://ik.imagekit.io/ex9p4t2gi/IMG_6124.jpg'
SHOP_BANNER_URL = 'https://media.discordapp.net/attachments/1303249085347926058/1444212368937586698/53ad0cc3373bbe0ea51dd878241952c6.gif' 
SUCCESS_GIF_URL = 'https://cdn.discordapp.com/attachments/1233098937632817233/1444077217230491731/Fire_Force_Sho_Kusakabe_GIF.gif'

EXPECTED_NAMES = [
    'ชานนท์ ขันทอง',      'นายชานนท์ ขันทอง',    'นาย ชานนท์ ขันทอง',
    'ชานนท์ ข',          'นายชานนท์ ข',        'นาย ชานนท์ ข',
    'ชานนท์ ขัน',        'นายชานนท์ ขัน',
    'chanon khantong',   'mr. chanon khantong', 'mr chanon khantong',
    'chanon k',          'mr. chanon k',        'mr chanon k',
    'chanon kh',         'chanon khan'
]
MIN_AMOUNT = 1.00

# สินค้า
PRODUCTS = [
    {"id": "item1",  "emoji": "⭐",  "name": "𝙳𝙾𝙽𝙰𝚃𝙴",         "price": 89,  "role_id": 1431279741440364625},
    {"id": "item2",  "emoji": "👻",  "name": "ᴍᴏᴅ ᴅᴇᴠᴏᴜʀ",       "price": 120, "role_id": 1432064283767738571},
    {"id": "item3",  "emoji": "👑",  "name": "[CMD] SETTING PREMIUM", "price": 169, "role_id": 1419373724653588540},
    {"id": "item4",  "emoji": "⚔️",  "name": "[CMD] 𝙰𝙻𝙻 𝚆𝙴𝙰𝙿𝙾𝙽",        "price": 139, "role_id": 1444190694674792592},
    {"id": "item5",  "emoji": "💻",  "name": "[CMD] ลบประวัติ CMD",      "price": 79,  "role_id": 1444191270372114552},
    {"id": "item6",  "emoji": "🗑️",  "name": "ลบประวัติรันโปรแกรม","price": 49,  "role_id": 1444191566838370365},
    {"id": "item7",  "emoji": "💎",  "name": "[Reshade] 𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟷",       "price": 25,  "role_id": 1431250097135419505},
    {"id": "item8",  "emoji": "🌈",  "name": "[Reshade] 𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟸",       "price": 25,  "role_id": 1431234346202959973},
    {"id": "item9",  "emoji": "🔥",  "name": "[Reshade] 𝚛𝚎𝚊𝚕𝚒𝚜𝚝𝚒𝚌𝚅𝟹",       "price": 25,  "role_id": 1431249584054734929},
    {"id": "item10", "emoji": "🎧",  "name": "[Reshade] 𝚜𝚞𝚗𝚔𝚒𝚜𝚜𝚎𝚍",        "price": 25,  "role_id": 1431278653760737340},
    {"id": "item11", "emoji": "🌃",  "name": "[Reshade] 𝚖𝚊𝚐𝚒𝚌𝚎𝚢𝚎",         "price": 25,  "role_id": 1431231640058990652},
    {"id": "item12", "emoji": "🌷",  "name": "[Reshade] 𝚁𝚎𝚊𝚕𝚕𝚒𝚟𝚎",         "price": 25,  "role_id": 1431204938373140513},
    {"id": "item13", "emoji": "🏞️",  "name": "[Reshade] ꜰᴀʟʟɪɴɢ",          "price": 25,  "role_id": 1444192569754910770},
    {"id": "item14", "emoji": "🎀",  "name": "[Reshade] realistic𝚅4",          "price": 35,  "role_id": 1448142438131699722},
    {"id": "item15", "emoji": "🌌",  "name": "[Reshade] realistic𝚅5",          "price": 35,  "role_id": 1448171343022526574},
    {"id": "item16", "emoji": "🍀",  "name": "[Reshade] realistic𝚅6",          "price": 35,  "role_id": 1448171385942966392},
    {"id": "item17", "emoji": "🎮",  "name": "𝙱𝙾𝙾𝚂𝚃 𝙵𝙿𝚂",         "price": 99,  "role_id": 1432010188340199504},
    {"id": "item18", "emoji": "🚧",  "name": "TOGYO MOD",         "price": 59,  "role_id": 1448142708286947449},
    {"id": "item19", "emoji": "⚡",  "name": "[Reshade] X Togyo mod",         "price": 35,  "role_id": 1448217708146589747},
    {"id": "item20", "emoji": "❓",  "name": "[Reshade] Tonedark❓",         "price": 35,  "role_id": 1448197995701993543},
    {"id": "item21", "emoji": "🚣",  "name": "[Reshade] realistic𝚅7",         "price": 35,  "role_id": 1448313586915999755},
    {"id": "item22", "emoji": "🍰",  "name": "[Reshade] PEKKY",         "price": 40,  "role_id": 1448263468355424298},
    {"id": "item23", "emoji": "🍕",  "name": "[Reshade] Realistic-𝚅8",         "price": 35,  "role_id": 1449643401908584490},
    {"id": "item24", "emoji": "🚀",  "name": "[CMD] 𝖥𝖱𝖠𝖬𝖤 𝖲𝖸𝖭𝖢",         "price": 120,  "role_id": 1449653924209492098},
    {"id": "item25", "emoji": "💻",  "name": "[CMD] 𝖱𝖤𝖡𝖮𝖱𝖭𝖪𝖨𝖫𝖫",         "price": 159,  "role_id": 1449657396497743883},
    {"id": "item26", "emoji": "💻",  "name": "[CMD] 𝟨𝟢 𝟩𝖤𝖳 𝟪𝖠𝖢𝖪",        "price": 159,  "role_id": 1449658031301333153},
    {"id": "item27", "emoji": "🏆",  "name": "VVIP [ของยกร้าน]🏆",        "price": 599,  "role_id": 1449658582244262041},
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

def is_slip_used(trans_ref):
    slips = load_json(SLIP_DB_FILE)
    if isinstance(slips, dict): slips = list(slips.keys())
    return trans_ref in slips

def save_used_slip(trans_ref):
    slips = load_json(SLIP_DB_FILE)
    if isinstance(slips, dict): slips = list(slips.keys())
    slips.append(trans_ref)
    with open(SLIP_DB_FILE, "w") as f: json.dump(slips, f, indent=4)

# =================================================================
# ⚙️ SYSTEM FUNCTIONS
# =================================================================

async def restore_database_from_logs(bot):
    print("🔄 Syncing database from Cyberpunk Logs...")
    channel = bot.get_channel(DASHBOARD_LOG_CHANNEL_ID)
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
            raw_amount = slip['amount']
            if isinstance(raw_amount, dict): raw_amount = raw_amount.get('amount', 0)
            amount = float(raw_amount)
            if amount < MIN_AMOUNT: return False, 0, None, f"Amount too low ({amount})"
            
            receiver = slip.get('receiver', {}).get('displayName') or slip.get('receiver', {}).get('name') or ""
            receiver = receiver.strip()
            if receiver:
                clean_receiver = " ".join(receiver.lower().split())
                is_name_valid = any(" ".join(n.lower().split()) in clean_receiver for n in EXPECTED_NAMES)
                if not is_name_valid: return False, 0, None, f"Wrong Receiver: {receiver}"

            d_str = str(slip.get('date', '')); t_str = str(slip.get('time', ''))
            dt_str = f"{d_str} {t_str}".replace("T", " ").split("+")[0].split(".")[0]
            slip_dt = None
            for fmt in ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M"]:
                try: slip_dt = datetime.strptime(dt_str, fmt); break
                except: continue
            
            if slip_dt:
                if slip_dt.year > 2500: slip_dt = slip_dt.replace(year=slip_dt.year - 543)
                now = datetime.utcnow() + timedelta(hours=7)
                diff = (now - slip_dt).total_seconds() / 60
                if diff > 10: return False, 0, None, "Slip Expired (>10 min)" 
                if diff < -5: return False, 0, None, "Invalid Future Time"
            return True, amount, slip['transRef'], "OK"
        else: return False, 0, None, data.get('message', 'Check Failed')
    except Exception as e: return False, 0, None, f"Error: {str(e)}"

# =================================================================
# 🎨 UI SYSTEM (GRID 3 COLUMNS - CLEAN LAYOUT)
# =================================================================

class DashboardView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="FORCE SYNC DATA", style=discord.ButtonStyle.danger, custom_id="admin_sync", emoji="🔄")
    async def update_db(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator: return
        await interaction.response.defer(ephemeral=True)
        await restore_database_from_logs(interaction.client) 
        await update_all_user_logs(interaction.client)
        await interaction.followup.send("✅ System Synced Successfully!")

async def update_user_log(bot, user_id):
    log_channel = bot.get_channel(DASHBOARD_LOG_CHANNEL_ID)
    if not log_channel: return
    data = get_data(user_id)
    if data['total'] <= 0 and data['balance'] <= 0: return

    user = bot.get_user(int(user_id))
    user_name = user.name if user else f"USER_{user_id}"
    
    embed = discord.Embed(color=THEME_COLOR)
    embed.description = f"```ini\n[ USER DATABASE RECORD ]\nUID      = {user_id}\nUSERNAME = {user_name}```"
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

# --- SHOPPING LOGIC ---

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
            f"DATE       : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"CUSTOMER   : {interaction.user.name}\n"
            f"------------------------------\n"
            f"ITEM       : {self.product['name']}\n"
            f"PRICE      : {price:.2f} THB\n"
            f"BALANCE    : {data['balance'] - price:.2f} THB\n"
            f"```"
        )
        embed.set_thumbnail(url=SUCCESS_GIF_URL)
        embed.set_footer(text="Thank you for your purchase", icon_url=interaction.user.display_avatar.url)
        
        await interaction.edit_original_response(content=None, embed=embed, view=None)
        
        if log := interaction.guild.get_channel(ADMIN_LOG_ID):
            await log.send(embed=embed)

    @discord.ui.button(label="CANCEL", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await interaction.response.edit_message(content="❌ Transaction Cancelled", embed=None, view=None)

# 🔥 ปุ่มสินค้า (Product Button)
class ProductButton(discord.ui.Button):
    def __init__(self, product, row_index):
        # เพิ่มจำนวนตัวอักษรเป็น 20 ได้ เพราะเราเหลือแค่ 3 ปุ่มต่อแถว
        super().__init__(style=discord.ButtonStyle.secondary, label=product['name'][:20], emoji=product['emoji'], row=row_index)
        self.product = product

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"{self.product['emoji']} {self.product['name']}", color=ACCENT_COLOR)
        embed.add_field(name="Price", value=f"```fix\n฿ {self.product['price']:.2f}```", inline=True)
        embed.add_field(name="Info", value="Auto Role / Fast Delivery", inline=True)
        await interaction.response.send_message(embed=embed, view=ProductConfirmView(self.product, interaction.user.id), ephemeral=True)

# 🔥 GRID BROWSER (3 COLUMNS)
class ProductGridBrowser(discord.ui.View):
    def __init__(self, products, page=0):
        super().__init__(timeout=None)
        self.products = products
        self.page = page
        
        # ปรับเป็น 3 คอลัมน์ x 4 แถว = 12 ชิ้นต่อหน้า
        # ทำให้มีพื้นที่ด้านข้างเยอะขึ้นสำหรับชื่อยาวๆ
        COLUMNS = 3
        ROWS = 4
        ITEMS_PER_PAGE = COLUMNS * ROWS 
        
        start = page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        current_items = products[start:end]

        # วนลูปสร้างปุ่มแบบ Grid
        for i, prod in enumerate(current_items):
            # i // 3 หมายถึงทุกๆ 3 ปุ่มจะขึ้นแถวใหม่ (0, 0, 0 -> 1, 1, 1)
            row_idx = i // COLUMNS 
            self.add_item(ProductButton(prod, row_idx))

        # Navigation (Row 4)
        if page > 0:
            self.add_item(self.create_nav_button("⬅️ Prev", "prev_page", discord.ButtonStyle.primary))
        
        total_pages = (len(products) - 1) // ITEMS_PER_PAGE + 1
        self.add_item(self.create_nav_button(f"Page {page + 1}/{total_pages}", "info", discord.ButtonStyle.gray, disabled=True))

        if end < len(products):
            self.add_item(self.create_nav_button("Next ➡️", "next_page", discord.ButtonStyle.primary))

    def create_nav_button(self, label, cid, style, disabled=False):
        # ปุ่มเปลี่ยนหน้าอยู่แถวที่ 5 (index 4) เสมอ
        btn = discord.ui.Button(label=label, custom_id=cid, style=style, disabled=disabled, row=4)
        btn.callback = self.nav_callback
        return btn

    async def nav_callback(self, interaction: discord.Interaction):
        custom_id = interaction.data['custom_id']
        if custom_id == "next_page":
            await interaction.response.edit_message(view=ProductGridBrowser(self.products, self.page + 1))
        elif custom_id == "prev_page":
            await interaction.response.edit_message(view=ProductGridBrowser(self.products, self.page - 1))

# --- MAIN DASHBOARD ---

class TopupModal(discord.ui.Modal, title="💳 TOPUP SYSTEM"):
    amount = discord.ui.TextInput(label="Enter Amount (THB)", placeholder="Example: 50", min_length=1, max_length=6)
    async def on_submit(self, interaction: discord.Interaction):
        try: val = float(self.amount.value)
        except: return await interaction.response.send_message("❌ Invalid Number", ephemeral=True)
        embed = discord.Embed(title="🧾 PAYMENT INVOICE", color=discord.Color.gold())
        embed.description = f"**AMOUNT:** `{val:.2f} THB`\n\n**INSTRUCTIONS:**\n1. Scan QR Code\n2. Send Slip to <#{SLIP_CHANNEL_ID}>\n3. Wait 1-5 Seconds"
        embed.set_image(url=QR_CODE_URL)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MainShopView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="BROWSE PRODUCTS", style=discord.ButtonStyle.primary, emoji="🛒", custom_id="browse_btn", row=0)
    async def browse(self, interaction: discord.Interaction, button: discord.ui.Button):
        # สร้าง Embed "กรอบ" สวยๆ
        embed = discord.Embed(title="🛍️ PRODUCT CATALOG", color=THEME_COLOR)
        embed.description = "```Click on the item below to view details or purchase.```"
        embed.set_footer(text="Select an item from the list below")
        
        await interaction.response.send_message(
            embed=embed,
            view=ProductGridBrowser(PRODUCTS), 
            ephemeral=True
        )

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

# =================================================================
# 🤖 BOT SETUP
# =================================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ SYSTEM ONLINE: {bot.user}")
    load_db()
    bot.add_view(MainShopView())
    bot.add_view(DashboardView())
    try: await bot.tree.sync()
    except: pass

@bot.tree.command(name="setup_dashboard", description="[Admin] Create Control Panel")
@app_commands.default_permissions(administrator=True)
async def setup_dashboard(interaction):
    if interaction.channel_id != DASHBOARD_CMD_CHANNEL_ID: return
    embed = discord.Embed(title="🎛️ CONTROL CENTER", description="Database & Logs Management System", color=discord.Color.orange())
    embed.add_field(name="SYSTEM STATUS", value="```diff\n+ ONLINE\n+ LATENCY: 24ms```")
    await interaction.channel.send(embed=embed, view=DashboardView())
    await interaction.response.send_message("✅ Dashboard Created", ephemeral=True)

@bot.tree.command(name="setup_shop")
async def setup_shop(interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title="⚡ CYBER STORE SYSTEM", color=THEME_COLOR)
    embed.description = (
        "> **WELCOME TO AUTOMATED STORE**\n"
        "> `STATUS:` 🟢 **ONLINE**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛒 **HOW TO BUY**\n"
        "1. Click `TOP UP` to add funds via QR Code\n"
        "2. Click `BROWSE PRODUCTS` to view items\n"
        "3. Select item & Confirm purchase\n\n"
        "💎 **FEATURES**\n"
        "• Auto-Delivery 24/7\n"
        "• Secure Transaction\n"
        "• Instant Role"
    )
    if SHOP_BANNER_URL.startswith("http"): embed.set_image(url=SHOP_BANNER_URL)
    await interaction.channel.send(embed=embed, view=MainShopView())
    await interaction.followup.send("✅ Shop Interface Deployed!", ephemeral=True)

@bot.tree.command(name="add_money")
async def add_money(interaction, user: discord.Member, amount: float):
    new_bal = update_money(user.id, amount, is_topup=True)
    await update_user_log(interaction.client, user.id)
    embed = discord.Embed(description=f"✅ **ADDED** `{amount} THB` to {user.mention}\nNew Balance: `{new_bal} THB`", color=SUCCESS_COLOR)
    await interaction.response.send_message(embed=embed)
    if log := bot.get_channel(ADMIN_LOG_ID):
        await log.send(f"🔧 **[MANUAL ADJ]** {interaction.user.name} added {amount} to {user.name}")

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.channel.id == SLIP_CHANNEL_ID and message.attachments:
        msg = await message.channel.send(embed=discord.Embed(description="⏳ **VERIFYING SLIP...**", color=discord.Color.yellow()))
        try:
            success, amount, ref, txt = check_slip_easyslip(message.attachments[0].url)
            if success:
                if is_slip_used(ref):
                    await msg.edit(content=None, embed=discord.Embed(description="❌ **SLIP ALREADY USED**", color=ERROR_COLOR))
                    return
                new_bal = update_money(message.author.id, amount, is_topup=True)
                save_used_slip(ref)
                await update_user_log(bot, message.author.id)
                embed = discord.Embed(title="✅ TOPUP SUCCESSFUL", color=SUCCESS_COLOR)
                embed.description = f"```ini\n[ RECEIPT ]\nAMOUNT  = {amount:.2f} THB\nBALANCE = {new_bal:.2f} THB\nREF     = {ref}```"
                embed.set_thumbnail(url=message.author.display_avatar.url)
                await msg.edit(content=None, embed=embed)
                if hist := bot.get_channel(HISTORY_CHANNEL_ID):
                    log_embed = discord.Embed(title="🧾 NEW TRANSACTION", color=ACCENT_COLOR)
                    log_embed.description = f"User: {message.author.mention}\nAmount: {amount}\nRef: {ref}"
                    log_embed.set_image(url=message.attachments[0].url)
                    await hist.send(embed=log_embed)
                await asyncio.sleep(5)
                await message.delete()
                await msg.delete()
            else:
                await msg.edit(content=None, embed=discord.Embed(description=f"❌ **ERROR:** {txt}", color=ERROR_COLOR))
        except Exception as e:
            await msg.edit(content=f"Error: {e}")

# =================================================================
# ⚙️ RUN
# =================================================================
def load_db():
    load_json(DB_FILE); load_json(SLIP_DB_FILE)
    load_json(TOTAL_DB_FILE); load_json(LOG_MSG_DB)

server_on()
bot.run(os.getenv('TOKEN'))
