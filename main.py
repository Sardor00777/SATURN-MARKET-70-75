import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

TOKEN = "7803071379:AAEAVfw7__d7ncefEjQE5nEFw3i4MKc6X0U"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

products = [
    {"name": "🍎 Olma", "price": 12000},
    {"name": "🍌 Banan", "price": 15000},
    {"name": "🍇 Uzum", "price": 20000},
    {"name": "🍑 Shaftoli", "price": 14000},
    {"name": "🍒 Gilos", "price": 25000},
    {"name": "🍍 Ananas", "price": 28000},
    {"name": "🥑 Avokado", "price": 30000},
    {"name": "🥭 Mango", "price": 27000},
    {"name": "🍋 Limon", "price": 13000},
    {"name": "🍊 Mandarin", "price": 16000},
]

ITEMS_PER_PAGE = 5

def start_menu():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🛒 Mahsulotlar",
        callback_data="products:0"
    )
    builder.adjust(1)
    return builder.as_markup()

def product_list_keyboard(page: int = 0):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = products[start:end]

    builder = InlineKeyboardBuilder()

    for idx, item in enumerate(page_items, start=start):
        builder.button(
            text=f"{item['name']} - {item['price']:,} so'm",
            callback_data=f"select:{idx}"
        )

    builder.adjust(1)

    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"products:{page - 1}"))
    navigation.append(InlineKeyboardButton(text="🏠 Bosh sahifa", callback_data="home"))
    if end < len(products):
        navigation.append(InlineKeyboardButton(text="➡️ Keyingi", callback_data=f"products:{page + 1}"))

    builder.row(*navigation)

    return builder.as_markup()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "<b>Assalomu alaykum SATURN MARKETGA hush kelibsiz!</b>\n\n🛒 Mahsulotlarni ko'rish uchun tugmani bosing:",
        reply_markup=start_menu()
    )

@dp.callback_query(F.data.startswith("products:"))
async def products_handler(callback: types.CallbackQuery):
    page = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "<b>🛍 Mahsulotlar ro'yxati:</b>",
        reply_markup=product_list_keyboard(page)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("select:"))
async def product_select_handler(callback: types.CallbackQuery):
    product_idx = int(callback.data.split(":")[1])
    item = products[product_idx]

    builder = InlineKeyboardBuilder()

    for kg in [10, 20, 30, 40, 50]:
        builder.button(
            text=f"{kg} kg - {item['price'] * kg} so'm",
            callback_data=f"buy:{product_idx}:{kg}"
        )

    builder.row(
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="home")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"products:{callback.data.split(':')[1]}")
    )

    await callback.message.edit_text(
        f"Siz <b>{item['name']}</b> mahsulotini tanladingiz.\n"
        f"Mahsulot narxi: <b>{item['price']} so'm</b>\n\n"
        "Iltimos, qancha kilogramm sotib olishni tanlang:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy:"))
async def buy_handler(callback: types.CallbackQuery):
    product_idx, kg = map(int, callback.data.split(":")[1:])
    item = products[product_idx]
    total_price = item["price"] * kg

    builder = InlineKeyboardBuilder()
    builder.button(
        text="💳 To'lash",
        callback_data=f"pay:{product_idx}:{kg}"
    )
    builder.row(
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="home")
    )

    await callback.message.edit_text(
        f"Siz <b>{kg} kg {item['name']}</b> mahsulotini tanladingiz.\n"
        f"Jami narx: <b>{total_price} so'm</b>\n\n"
        "To'lovni amalga oshirish uchun 'To'lash' tugmasini bosing.",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("pay:"))
async def pay_handler(callback: types.CallbackQuery):
    product_idx, kg = map(int, callback.data.split(":")[1:])
    item = products[product_idx]
    total_price = item["price"] * kg

    await callback.message.answer(
        f"✅ To'lov muvaffaqiyatli amalga oshirildi yanna SATURN MARKETGA kelib turing!\n"
        f"Siz <b>{kg} kg {item['name']}</b> mahsulotini sotib oldingiz.\n"
        f"💰 Jami: <b>{total_price} so'm</b>\n\n"
        "🛒 Yana mahsulotlarni sotib olish uchun /start buyrug'ini bosing.",
        reply_markup=start_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "home")
async def home_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "<b>Assalomu alaykum hush kelibsiz SATURN MARKETGA 70/75!</b>\n\n🛒 Mahsulotlarni ko'rish uchun tugmani bosing:",
        reply_markup=start_menu()
    )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
