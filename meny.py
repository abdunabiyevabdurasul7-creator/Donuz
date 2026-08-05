import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

# === BAZAVIY SOZLAMALAR ===
BOT_TOKEN = "8659066280:AAG7hXRKMV1KGrldB1fFAgysHACo9_3zuzM"
ADMIN_ID = 5692925792
KARTA_RAQAM = "9860 6067 6078 9275 AAbdurasul(HUMO)"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === MA'LUMOTLAR BAZASI (SQLite) ===
conn = sqlite3.connect("shop_bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item_name TEXT,
    price INTEGER,
    status TEXT DEFAULT 'Bajarildi'
)
''')
conn.commit()

# === HOLATLAR (FSM) ===
class Form(StatesGroup):
    wait_transfer_id = State()
    wait_transfer_amount = State()
    wait_receipt = State()
    wait_order_check = State()
    wait_promo = State()

# === BARCHA MAHSULOTLAR VA NARXLAR BAZASI ===
PRODUCTS = {
    "tg": {
        "title": "📲 Telegram Xizmatlari",
        "items": {
            "tg_3m": ("Telegram Premium 3 oylik", 178000, "TG-PREM-3M-CODE"),
            "tg_6m": ("Telegram Premium 6 oylik", 246000, "TG-PREM-6M-CODE"),
            "tg_12m": ("Telegram Premium 12 oylik", 440000, "TG-PREM-12M-CODE"),
            "tg_acc": ("Telegram Akkaunt", 8000, "+998901234567:session_data"),
        }
    },
    "grand_5x": {
        "title": "📱 Grand Mobile 5x ID",
        "items": {
            "g5_75": ("75 Gc", 3000, "GM5X-75GC-KEY"),
            "g5_150": ("150 Gc", 5500, "GM5X-150GC-KEY"),
            "g5_450": ("450 Gc", 15500, "GM5X-450GC-KEY"),
            "g5_1000": ("1000 Gc", 34000, "GM5X-1000GC-KEY"),
            "g5_2525": ("2.525 Gc", 85000, "GM5X-2525GC-KEY"),
            "g5_5100": ("5100 Gc", 169000, "GM5X-5100GC-KEY"),
            "g5_12875": ("12.875 Gc", 422000, "GM5X-12875GC-KEY"),
        }
    },
    "grand_4x": {
        "title": "📱 Grand Mobile 4x ID",
        "items": {
            "g4_60": ("60gc", 3000, "GM4X-60GC-KEY"),
            "g4_120": ("120gc", 5500, "GM4X-120GC-KEY"),
            "g4_360": ("360gc", 15500, "GM4X-360GC-KEY"),
            "g4_800": ("800 gc", 34000, "GM4X-800GC-KEY"),
            "g4_2025": ("2025 gc", 85000, "GM4X-2025GC-KEY"),
            "g4_4100": ("4100 gc", 169000, "GM4X-4100GC-KEY"),
            "g4_10375": ("10375 gc", 422000, "GM4X-10375GC-KEY"),
        }
    },
    "grand_3x": {
        "title": "📱 Grand Mobile 3x ID",
        "items": {
            "g3_45": ("45 gc", 3000, "GM3X-45GC-KEY"),
            "g3_90": ("90 gc", 5500, "GM3X-90GC-KEY"),
            "g3_270": ("270 gc", 15500, "GM3X-270GC-KEY"),
            "g3_600": ("600 gc", 34000, "GM3X-600GC-KEY"),
            "g3_1525": ("1525 gc", 85000, "GM3X-1525GC-KEY"),
            "g3_3100": ("3100 gc", 169000, "GM3X-3100GC-KEY"),
            "g3_7875": ("7875 gc", 422000, "GM3X-7875GC-KEY"),
        }
    },
    "grand_1x": {
        "title": "📱 Grand Mobile ID",
        "items": {
            "g1_15": ("15 gc", 3000, "GM-15GC-KEY"),
            "g1_30": ("30 gc", 5500, "GM-30GC-KEY"),
            "g1_90": ("90 gc", 15500, "GM-90GC-KEY"),
            "g1_200": ("200 gc", 34000, "GM-200GC-KEY"),
            "g1_500": ("500 gc", 85000, "GM-500GC-KEY"),
            "g1_1000": ("1000 gc", 169000, "GM-1000GC-KEY"),
            "g1_2500": ("2500 gc", 422000, "GM-2500GC-KEY"),
        }
    },
    "pubg": {
        "title": "🔫 PUBG Mobile Global UC",
        "items": {
            "p_30": ("30 uc", 7000, "PUBG-30UC-CODE"),
            "p_60": ("60 uc", 12000, "PUBG-60UC-CODE"),
            "p_120": ("120 uc", 24000, "PUBG-120UC-CODE"),
            "p_325": ("325 uc", 58000, "PUBG-325UC-CODE"),
            "p_385": ("385 uc", 70000, "PUBG-385UC-CODE"),
            "p_660": ("660 uc", 115000, "PUBG-660UC-CODE"),
            "p_985": ("985 uc", 170000, "PUBG-985UC-CODE"),
            "p_1320": ("1320 uc", 230000, "PUBG-1320UC-CODE"),
            "p_1800": ("1800 uc", 280000, "PUBG-1800UC-CODE"),
            "p_2460": ("2460 uc", 400000, "PUBG-2460UC-CODE"),
            "p_3850": ("3850 uc", 550000, "PUBG-3850UC-CODE"),
            "p_5650": ("5650 uc", 830000, "PUBG-5650UC-CODE"),
            "p_8100": ("8100 uc", 1100000, "PUBG-8100UC-CODE"),
            "p_16200": ("16.200 uc", 2200000, "PUBG-16200UC-CODE"),
            "p_20050": ("20.050 uc", 2750000, "PUBG-20050UC-CODE"),
            "p_red": ("Qizil keys", 60000, "PUBG-KEY-RED"),
            "p_white": ("Oq keys", 15000, "PUBG-KEY-WHITE"),
            "p_yellow": ("Sariq keys", 37000, "PUBG-KEY-YELLOW"),
        }
    },
    "wow": {
        "title": "⚔️ WoW Karta Valyutasi",
        "items": {
            "w_60": ("60 wow valyutasi", 12000, "WOW-60VAL-CODE"),
            "w_325": ("325 wow valyutasi", 59000, "WOW-325VAL-CODE"),
            "w_660": ("660 wow valyutasi", 120000, "WOW-660VAL-CODE"),
            "w_1800": ("1800 wow valyutasi", 295000, "WOW-1800VAL-CODE"),
            "w_3850": ("3850 wow valyutasi", 585000, "WOW-3850VAL-CODE"),
            "w_8100": ("8100 wow valyutasi", 1160000, "WOW-8100VAL-CODE"),
        }
    }
}

# === ASOSIY MENYU TUGMALARI ===
def get_main_menu():
    kb = [
        [KeyboardButton(text="🛍 Buyurtma berish"), KeyboardButton(text="💳 Balans to'ldirish")],
        [KeyboardButton(text="💸 Pul o'tkazish"), KeyboardButton(text="🔍 Buyurtmani tekshirish")],
        [KeyboardButton(text="🎁 Promokod"), KeyboardButton(text="👤 Balans va Profil")],
        [KeyboardButton(text="📊 Statistika")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# === BOT START BUYRUG'I ===
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
    conn.commit()
    
    await message.answer("Asalomu Aleykum! Xush kelibsiz. Bo'limlardan birini tanlang:", reply_markup=get_main_menu())

# === PROFIL VA BALANS ===
@dp.message(F.text == "👤 Balans va Profil")
async def show_profile(message: types.Message):
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (message.from_user.id,))
    res = cursor.fetchone()
    balance = res[0] if res else 0
    await message.answer(f"🆔 Sizing ID: `{message.from_user.id}`\n💰 Balans: {balance:,} so'm", parse_mode="Markdown")

# === BUYURTMA BERISH (KATEGORIYALAR) ===
@dp.message(F.text == "🛍 Buyurtma berish")
async def show_categories(message: types.Message):
    inline_kb = []
    for cat_id, cat_data in PRODUCTS.items():
        inline_kb.append([InlineKeyboardButton(text=cat_data["title"], callback_data=f"cat_{cat_id}")])
    
    markup = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    await message.answer("🎮 Kerakli o'yin yoki xizmatni tanlang:", reply_markup=markup)

# Kategoriya tanlanganda paketlarni ko'rsatish
@dp.callback_query(F.data.startswith("cat_"))
async def show_products(call: types.CallbackQuery):
    cat_id = call.data.replace("cat_", "")
    category = PRODUCTS.get(cat_id)
    
    if not category:
        await call.answer("Kategoriya topilmadi!", show_alert=True)
        return

    inline_kb = []
    for item_id, (name, price, _) in category["items"].items():
        inline_kb.append([InlineKeyboardButton(text=f"{name} — {price:,} so'm", callback_data=f"buy_{cat_id}_{item_id}")])
    
    inline_kb.append([InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_cats")])
    markup = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    
    await call.message.edit_text(f"✨ **{category['title']}**\n\nPaketni ustiga bosing:", reply_markup=markup, parse_mode="Markdown")

@dp.callback_query(F.data == "back_to_cats")
async def back_cats(call: types.CallbackQuery):
    inline_kb = []
    for cat_id, cat_data in PRODUCTS.items():
        inline_kb.append([InlineKeyboardButton(text=cat_data["title"], callback_data=f"cat_{cat_id}")])
    
    markup = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    await call.message.edit_text("🎮 Kerakli o'yin yoki xizmatni tanlang:", reply_markup=markup)

# === AVTOMATIK BUYURTMA XARIDI ===
@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(call: types.CallbackQuery):
    _, cat_id, item_id = call.data.split("_", 2)
    item_info = PRODUCTS[cat_id]["items"].get(item_id)

    if not item_info:
        await call.answer("Mahsulot topilmadi!", show_alert=True)
        return

    item_name, price, auto_data = item_info
    user_id = call.from_user.id

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    balance = res[0] if res else 0

    if balance < price:
        await call.answer(f"❌ Balansingizda pul yetarli emas!\nKerakli summa: {price:,} so'm\nSizda: {balance:,} so'm", show_alert=True)
    else:
        new_balance = balance - price
        cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        
        cursor.execute("INSERT INTO orders (user_id, item_name, price) VALUES (?, ?, ?)", (user_id, item_name, price))
        conn.commit()
        order_id = cursor.lastrowid

        await call.message.answer(
            f"✅ **Buyurtma muvaffaqiyatli xarid qilindi!**\n\n"
            f"🆔 Buyurtma ID: `{order_id}`\n"
            f"📦 Mahsulot: {item_name}\n"
            f"💵 Yechildi: {price:,} so'm\n\n"
            f"🎁 **Sizning mahsulotingiz / kodingiz:**\n`{auto_data}`",
            parse_mode="Markdown"
        )
        await call.answer("Xarid qilindi!")

# === BALANS TO'LDIRISH VA CHEK ===
@dp.message(F.text == "💳 Balans to'ldirish")
async def top_up(message: types.Message, state: FSMContext):
    await message.answer(
        f"💳 **To'lov uchun karta raqami:**\n`{KARTA_RAQAM}`\n\n"
        f"To'lovni amalga oshirgach, chekning rasmini yuboring.",
        parse_mode="Markdown"
    )
    await state.set_state(Form.wait_receipt)

@dp.message(Form.wait_receipt, F.photo)
async def process_receipt(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    user_id = message.from_user.id

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_id,
        caption=f"📥 **Yangi to'lov cheki!**\nFoydalanuvchi ID: `{user_id}`\n\n"
                f"Pul qo'shish uchun buyruq: `/add_bal {user_id} SUMMA`",
        parse_mode="Markdown"
    )
    await message.answer("✅ Chek adminga yuborildi. Tekshirilgach balans tayinlanadi.")
    await state.clear()

# === PUL O'TKAZISH ===
@dp.message(F.text == "💸 Pul o'tkazish")
async def transfer_start(message: types.Message, state: FSMContext):
    await message.answer("Pul o'tkazmoqchi bo'lgan foydalanuvchining ID raqamini kiriting:")
    await state.set_state(Form.wait_transfer_id)

@dp.message(Form.wait_transfer_id)
async def transfer_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat ID raqamini kiriting:")
        return
    await state.update_data(target_id=int(message.text))
    await message.answer("O'tkaziladigan summani kiriting (so'mda):")
    await state.set_state(Form.wait_transfer_amount)

@dp.message(Form.wait_transfer_amount)
async def transfer_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, summani raqamlarda kiriting:")
        return

    amount = int(message.text)
    user_id = message.from_user.id
    data = await state.get_data()
    target_id = data.get("target_id")

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    sender_bal = cursor.fetchone()[0]

    if sender_bal < amount:
        await message.answer("❌ Balansingizda yetarli mablag' mavjud emas!")
    else:
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (target_id,))
        target_res = cursor.fetchone()
        if not target_res:
            await message.answer("❌ Bunday ID ga ega foydalanuvchi topilmadi.")
        else:
            cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_id))
            conn.commit()

            await message.answer(f"✅ ID: `{target_id}` foydalanuvchisiga {amount:,} so'm muvaffaqiyatli o'tkazildi!", parse_mode="Markdown")
            try:
                await bot.send_message(target_id, f"🎁 ID: `{user_id}` sizga {amount:,} so'm pul o'tkazdi!", parse_mode="Markdown")
            except:
                pass
    await state.clear()

# === BUYURTMANI TEKSHIRISH ===
@dp.message(F.text == "🔍 Buyurtmani tekshirish")
async def check_order_start(message: types.Message, state: FSMContext):
    await message.answer("Buyurtma ID raqamini kiriting:")
    await state.set_state(Form.wait_order_check)

@dp.message(Form.wait_order_check)
async def check_order_process(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Buyurtma ID si faqat sonlardan iborat bo'ladi.")
        return

    order_id = int(message.text)
    cursor.execute("SELECT item_name, price, status FROM orders WHERE order_id = ?", (order_id,))
    order = cursor.fetchone()

    if order:
        await message.answer(f"📦 **Buyurtma #{order_id}**\n\n📌 Nomi: {order[0]}\n💵 Narxi: {order[1]:,} so'm\n⚡️ Holati: {order[2]}", parse_mode="Markdown")
    else:
        await message.answer("❌ Bunday ID ga ega buyurtma topilmadi.")
    await state.clear()

# === PROMOKOD ===
@dp.message(F.text == "🎁 Promokod")
async def promo_start(message: types.Message, state: FSMContext):
    await message.answer("Promokodni kiriting:")
    await state.set_state(Form.wait_promo)

@dp.message(Form.wait_promo)
async def promo_process(message: types.Message, state: FSMContext):
    code = message.text.strip().upper()
    user_id = message.from_user.id

    if code == "VIP2026":
        cursor.execute("UPDATE users SET balance = balance + 10000 WHERE user_id = ?", (user_id,))
        conn.commit()
        await message.answer("🎉 Promokod qabul qilindi! Balansga +10,000 so'm qo'shildi.")
    else:
        await message.answer("❌ Noto'g'ri promokod.")
    await state.clear()

# === STATISTIKA ===
@dp.message(F.text == "📊 Statistika")
async def show_stats(message: types.Message):
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    await message.answer(f"📊 **Bot Statistikasi:**\n\n👥 Foydalanuvchilar: {total_users} ta\n🛍 Bajarilgan buyurtmalar: {total_orders} ta", parse_mode="Markdown")

# === ADMIN BUYRUQLARI (PUL QO'SHISH VA AYRISH) ===

# Pul qo'shish: /add_bal USER_ID SUMMA
@dp.message(Command("add_bal"))
async def admin_add_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        args = message.text.split()
        target_id, amount = int(args[1]), int(args[2])
        
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_id))
        conn.commit()
        
        await message.answer(f"✅ ID `{target_id}` ga {amount:,} so'm qo'shildi.", parse_mode="Markdown")
        try:
            await bot.send_message(target_id, f"💳 Balansingizga {amount:,} so'm qo'shildi!")
        except:
            pass
    except:
        await message.answer("❌ Noto'g'ri format. Namuna: `/add_bal 123456789 50000`", parse_mode="Markdown")

# Pul ayirish: /sub_bal USER_ID SUMMA
@dp.message(Command("sub_bal"))
async def admin_sub_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        args = message.text.split()
        target_id, amount = int(args[1]), int(args[2])
        
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, target_id))
        conn.commit()
        
        await message.answer(f"✅ ID `{target_id}` dan {amount:,} so'm ayirildi.", parse_mode="Markdown")
        try:
            await bot.send_message(target_id, f"⚠️ Balansingizdan {amount:,} so'm ayirildi.")
        except:
            pass
    except:
        await message.answer("❌ Noto'g'ri format. Namuna: `/sub_bal 123456789 50000`", parse_mode="Markdown")

# === BOTNI ISHGA TUSHIRISH ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
