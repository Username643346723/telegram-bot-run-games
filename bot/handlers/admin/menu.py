from aiogram import Router, F, types
from bot.views.keyboards.admin import admin_main_kb, AdminCallback, AdminAction

router = Router()


@router.message(F.text == "/admin")
async def admin_panel(message: types.Message):
    await message.answer("Панель администратора:", reply_markup=admin_main_kb())


@router.callback_query(AdminCallback.filter(F.action == AdminAction.back))
async def admin_back(callback: types.CallbackQuery):
    await callback.message.edit_text("Панель администратора:", reply_markup=admin_main_kb())
