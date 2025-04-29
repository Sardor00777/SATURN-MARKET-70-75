import asyncio
import re
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from dotenv import load_dotenv

from dp import create_dp, save_user, init_pool

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "7803071379:AAHwvsNTAESwXp6qFjS5nBswT3dMMqGl8ZM")

bot = Bot(token=TOKEN)
dp = Dispatcher()

class UserForm(StatesGroup):
    ism = State()
    tel_nomer = State()
    yosh = State()
    qayerliki = State()
    ish_joyi = State()

def is_valid_name(name: str) -> bool:
    return bool(re.match(r"^[a-zA-Zа-яА-ЯёЁ\s]{3,}$", name.strip()))

def is_valid_phone(phone: str) -> bool:
    return bool(re.match(r"^\+998[0-9]{9}$", phone))

def is_valid_age(age: str) -> bool:
    return age.isdigit() and 1 <= int(age) <= 150

def is_valid_qayerliki(q: str) -> bool:
    return len(q.strip()) >= 5

def is_valid_ish_joyi(i: str) -> bool:
    return bool(re.match(r"^[a-zA-Zа-яА-ЯёЁ\s]{3,}$", i.strip()))

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer("👋 Salom! Iltimos, ismingizni kiriting (masalan: Ali Valiyev):")
    await state.set_state(UserForm.ism)

@dp.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Jarayon bekor qilindi.")

@dp.message(StateFilter(UserForm.ism))
async def get_ism(message: types.Message, state: FSMContext):
    if not is_valid_name(message.text):
        await message.answer("❌ Ism noto‘g‘ri. Faqat harflar va probel bo‘lishi kerak, kamida 3 belgi. Qayta kiriting:")
        return
    await state.update_data(ism=message.text.strip())
    await message.answer("📞 Telefon raqamingizni kiriting (masalan: +998901234567):")
    await state.set_state(UserForm.tel_nomer)

@dp.message(StateFilter(UserForm.tel_nomer))
async def get_tel(message: types.Message, state: FSMContext):
    if not is_valid_phone(message.text):
        await message.answer("❌ Telefon raqam noto‘g‘ri. +998 bilan boshlanishi va 9 ta raqam bo‘lishi kerak. Qayta kiriting:")
        return
    await state.update_data(tel_nomer=message.text.strip())
    await message.answer("🎂 Yoshingizni kiriting (1-150):")
    await state.set_state(UserForm.yosh)

@dp.message(StateFilter(UserForm.yosh))
async def get_yosh(message: types.Message, state: FSMContext):
    if not is_valid_age(message.text):
        await message.answer("❌ Yosh noto‘g‘ri. 1 dan 150 gacha raqam kiriting. Qayta kiriting:")
        return
    await state.update_data(yosh=message.text.strip())
    await message.answer("🏠 Qayerliksiz (kamida 5 belgi):")
    await state.set_state(UserForm.qayerliki)

@dp.message(StateFilter(UserForm.qayerliki))
async def get_qayerliki(message: types.Message, state: FSMContext):
    if not is_valid_qayerliki(message.text):
        await message.answer("❌ Ma’lumot noto‘g‘ri. Kamida 5 belgi kiriting. Qayta kiriting:")
        return
    await state.update_data(qayerliki=message.text.strip())
    await message.answer("💼 Ish joyingiz (masalan: O‘qituvchi):")
    await state.set_state(UserForm.ish_joyi)

@dp.message(StateFilter(UserForm.ish_joyi))
async def get_ish_joyi(message: types.Message, state: FSMContext):
    if not is_valid_ish_joyi(message.text):
        await message.answer("❌ Ish joyi noto‘g‘ri. Faqat harflar va probel, kamida 3 belgi. Qayta kiriting:")
        return
    await state.update_data(ish_joyi=message.text.strip())
    data = await state.get_data()
    try:
        await save_user(data, message.from_user.id)
    except ValueError as e:
        await message.answer(f"❌ Xato: {str(e)}")
        await state.clear()
        return
    except Exception:
        await message.answer("❌ Ma'lumotlarni saqlashda xato yuz berdi. Iltimos, qayta urinib ko‘ring.")
        return

    await message.answer(
        "✅ Ma'lumotlaringiz saqlandi!\n"
        f"👤 Ism: {data['ism']}\n"
        f"📞 Tel: {data['tel_nomer']}\n"
        f"🎂 Yosh: {data['yosh']}\n"
        f"🏠 Qayerliki: {data['qayerliki']}\n"
        f"💼 Ish joyi: {data['ish_joyi']}"
    )
    await state.clear()

async def main():
    try:
        await init_pool()
        await create_dp()
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Bot startup error: {e}")

if __name__ == "__main__":
    asyncio.run(main())