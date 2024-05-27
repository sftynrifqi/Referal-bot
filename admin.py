from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, CallbackQuery
from buttons import *
from database.otherservice import *
from database.userservice import *
from database.adminservice import *
from states import ChangeAdminInfo

# TODO изменить метод получения айди админа
admin_id = 305896408
admin_router = Router()

@admin_router.message(Command(commands=["admin"]))
async def admin_mm(message: Message):
    # if message.from_user.id == admin_id:
    info = admin_menu_info()
    await message.bot.send_message(message.from_user.id, f"🕵️‍<b>️Пользователей в боте</b>: {info[0]}\n"
                                                         f"💶<b>Заявок на вывод</b>: {info[1]}", parse_mode="html",
                                   reply_markup= await admin_menu_in())

@admin_router.callback_query(F.data.in_(["all_payments", "cancel", "none", "change_money", "change_min",
                                         "change_channels", "add_channel", "delete_channel", "mailing",
                                         "imp"]))
async def call_backs(query: CallbackQuery, state: FSMContext):
    await state.clear()
    if query.data == "all_payments":
        active_payments = get_all_wait_payment()
        if active_payments != []:
            for i in active_payments:
                await query.bot.send_message(query.from_user.id, f"<b>Заявка на выплату № {i[0]}</b>\n"
                                                                 f"ID: <code>{i[1]}</code>\n"
                                                                 f"Сумма выплаты: {i[2]}\n"
                                                                 f"Карта: <code>{i[3]}</code>\n"
                                                                 f"Банк: {i[4]}", parse_mode="html",
                                             reply_markup=await payments_action_in(i[0]))
        elif active_payments != []:
            await query.bot.send_message(query.from_user.id, "Нет никаких заявок на выплату")
    elif query.data == "cancel":
        await query.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        await state.clear()
    elif query.data == "none":
        pass
    elif query.data == "change_money":
        await query.bot.send_message(query.from_user.id, "Введите новую награду за рефералов",
                                     reply_markup= await cancel_bt())
        await state.set_state(ChangeAdminInfo.get_amount)
    elif query.data == "change_min":
        await query.bot.send_message(query.from_user.id, "Введите новую минимальную выплату",
                                     reply_markup= await cancel_bt())
        await state.set_state(ChangeAdminInfo.get_min)
    elif query.data == "change_channels":
        text = "Обязательные подписки: \n"
        all_channels = get_channels_for_admin()
        for i in all_channels:
            text += (f"\nАйди подписки: {i[0]}\n"
                     f"Username канала: {i[1]}\n")
        await query.bot.send_message(query.from_user.id, text=text,
                                     reply_markup=await admin_channels_in())
    elif query.data == "add_channel":
        await query.bot.send_message(query.from_user.id, "Введите username канала через @",
                                     reply_markup= await cancel_bt())
        await state.set_state(ChangeAdminInfo.get_channel)
    elif query.data == "delete_channel":
        await query.bot.send_message(query.from_user.id, "Введите ID подписки для удаления",
                                     reply_markup=await cancel_bt())
        await state.set_state(ChangeAdminInfo.delete_channel)
    elif query.data == "mailing":
        await query.bot.send_message(query.from_user.id, "Введите сообщение для рассылки, либо отправьте фотографии с описанием",
                                     reply_markup=await cancel_bt())
        await state.set_state(ChangeAdminInfo.mailing)
    elif query.data == "imp":
        await query.bot.send_message(query.from_user.id, "Введите ID пользователя",
                                     reply_markup=await cancel_bt())
        await state.set_state(ChangeAdminInfo.imp)



@admin_router.callback_query(lambda call: "ban_" in call.data)
async def banning(query: CallbackQuery):
    id_of_user = int(query.data.replace("ban_", ""))
    ban_unban_db(id=id_of_user, bool=True)
    await query.bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        reply_markup= await imp_menu_in(id_of_user, True))
@admin_router.callback_query(lambda call: "razb_" in call.data)
async def banning(query: CallbackQuery):
    id_of_user = int(query.data.replace("razb_", ""))
    ban_unban_db(id=id_of_user, bool=False)
    await query.bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                        reply_markup= await imp_menu_in(id_of_user, False))

@admin_router.callback_query(lambda call: "changebalance_" in call.data)
async def change_balance(query: CallbackQuery, state: FSMContext):
    id_of_user = int(query.data.replace("changebalance_", ""))
    await query.bot.send_message(query.from_user.id, "Введите новую сумму баланса",
                                 reply_markup= await cancel_bt())
    await state.set_state(ChangeAdminInfo.change_balance)
    await state.set_data({"user_id": id_of_user})
@admin_router.callback_query(lambda call: "addbalance_" in call.data)
async def add_balance(query: CallbackQuery, state: FSMContext):
    id_of_user = int(query.data.replace("addbalance_", ""))
    await query.bot.send_message(query.from_user.id, "Сколько нужно добавить к балансу?",
                                 reply_markup= await cancel_bt())
    await state.set_state(ChangeAdminInfo.add_balance)
    await state.set_data({"user_id": id_of_user})
@admin_router.callback_query(lambda call: "changerefs_" in call.data)
async def change_refs(query: CallbackQuery, state: FSMContext):
    id_of_user = int(query.data.replace("changerefs_", ""))
    await query.bot.send_message(query.from_user.id, "Введите новое количество рефералов",
                                 reply_markup= await cancel_bt())
    await state.set_state(ChangeAdminInfo.change_refs)
    await state.set_data({"user_id": id_of_user})


@admin_router.callback_query(lambda call: "accept_" in call.data)
async def acception(query: CallbackQuery):
    id_of_wa = int(query.data.replace("accept_", ""))
    user_info = status_accepted(id_of_wa)
    await query.bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                              reply_markup=await accepted_in())
    await query.bot.send_message(user_info[0], f"Ваша завявка на выплату {user_info[1]} была подтверждена ✅")

@admin_router.callback_query(lambda call: "decline_" in call.data)
async def acception(query: CallbackQuery):
    id_of_wa = int(query.data.replace("decline_", ""))
    user_info = status_declined(id_of_wa)
    await query.bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                              reply_markup=await declined_in())
    await query.bot.send_message(user_info[0], f"Ваша завявка на выплату {user_info[1]} была отклонена❌")

@admin_router.message(ChangeAdminInfo.get_amount)
async def get_new_amount(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text:
        try:
            change_price(float(message.text))
            await message.bot.send_message(message.from_user.id, f"Награда за реферала изменена на {message.text}",
                                           reply_markup=await main_menu_bt())
            await state.clear()
        except:
            await message.bot.send_message(message.from_user.id, "🚫Не удалось изменить",
                                           reply_markup=await main_menu_bt())
            await state.clear()
@admin_router.message(ChangeAdminInfo.get_min)
async def get_new_min(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text:
        try:
            change_min_amount(float(message.text))
            await message.bot.send_message(message.from_user.id, f"Минимальная выплата изменена на {message.text}",
                                           reply_markup=await main_menu_bt())
            await state.clear()
        except:
            await message.bot.send_message(message.from_user.id, "🚫Не удалось изменить",
                                           reply_markup=await main_menu_bt())
            await state.clear()
    else:
        await message.bot.send_message(message.from_user.id, "️️❗Ошибка", reply_markup=await main_menu_bt())
        await state.clear()
@admin_router.message(ChangeAdminInfo.get_channel)
async def get_new_channel(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text:
        try:
            new_channel = add_new_channel_db(message.text)
            if new_channel:
                await message.bot.send_message(message.from_user.id, f"Подписка добавлена ✅",
                                               reply_markup=await main_menu_bt())
                await state.clear()
            else:
                await message.bot.send_message(message.from_user.id, f"Подписка не добавлена. Нельзя добавить более 6 обязательных подписок\n"
                                                                     f"Чтобы добавить новую, удалите старую подписку",
                                               reply_markup=await main_menu_bt())
                await state.clear()
        except:
            await message.bot.send_message(message.from_user.id, "🚫Не удалось изменить",
                                           reply_markup=await main_menu_bt())
            await state.clear()
    else:
        await message.bot.send_message(message.from_user.id, "️️❗Ошибка", reply_markup=await main_menu_bt())
        await state.clear()
@admin_router.message(ChangeAdminInfo.delete_channel)
async def delete_channel(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text == "1":
        await message.bot.send_message(message.from_user.id, "🚫Нельзя удалить эту подписку", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text != "1" and message.text.isdigit():
        try_del = delete_channel_db(int(message.text))
        if try_del:
            await message.bot.send_message(message.from_user.id, f"Подписка успешно удалена ✅",
                                           reply_markup=await main_menu_bt())
            await state.clear()
        else:
            await message.bot.send_message(message.from_user.id, "🚫Не удалось удалить",
                                           reply_markup=await main_menu_bt())
            await state.clear()
    else:
        await message.bot.send_message(message.from_user.id, "️️❗Ошибка", reply_markup=await main_menu_bt())
        await state.clear()

@admin_router.message(ChangeAdminInfo.mailing)
async def mailing_admin(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    else:
        all_users = get_all_users_tg_id()
        success = 0
        unsuccess = 0
        for i in all_users:
            try:
                await message.bot.copy_message(chat_id=i, from_chat_id=message.from_user.id,
                                               message_id = message.message_id)
                success += 1
            except:
                unsuccess +=1
        await message.bot.send_message(message.from_user.id, f"Рассылка завершена!\n"
                                                             f"Успешно отправлено: {success}\n"
                                                             f"Неуспешно: {unsuccess}", reply_markup=await main_menu_bt())
        await state.clear()


@admin_router.message(ChangeAdminInfo.imp)
async def get_imp_id(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text.isdigit():
        user_id = int(message.text)
        try:
            status = check_ban(user_id)
            user_info = get_user_info_db(user_id)
            print(user_info)
            if user_info:
                await message.bot.send_message(message.from_user.id, f"📝Имя юзера: {user_info[0]}\n"
                                                                     f"🆔ID юзера: <code>{user_info[1]}</code>\n"
                                                                     f"👥 Пригласил: {user_info[3]}\n"
                                                                     f"💳 Баланс юзера: {user_info[2]}\n"
                                                                     f"📤Вывел {user_info[5]}\n",
                                               parse_mode="html", reply_markup=await imp_menu_in(user_info[1], status))
                await state.clear()
            else:
                await message.bot.send_message(message.from_user.id, f"Подписка не добавлена. Нельзя добавить более 6 обязательных подписок\n"
                                                                     f"Чтобы добавить новую, удалите старую подписку",
                                               reply_markup=await main_menu_bt())
                await state.clear()
        except:
            await message.bot.send_message(message.from_user.id, "🚫Не удалось изменить",
                                           reply_markup=await main_menu_bt())
            await state.clear()
    else:
        await message.bot.send_message(message.from_user.id, "️️❗Ошибка", reply_markup=await main_menu_bt())
        await state.clear()

@admin_router.message(ChangeAdminInfo.add_balance)
async def add_balance_amount(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text.isdigit():
        try:
            amount = float(message.text)
            user_id = await state.get_data()
            addbalance_db(user_id["user_id"], amount)
            await message.bot.send_message(message.from_user.id, f"Баланс пополнен ✅",
                                           reply_markup=await main_menu_bt())
            await state.clear()

        except:
            await message.bot.send_message(message.from_user.id, "🚫Не удалось изменить",
                                           reply_markup=await main_menu_bt())
            await state.clear()
    else:
        await message.bot.send_message(message.from_user.id, "️️❗Ошибка", reply_markup=await main_menu_bt())
        await state.clear()





@admin_router.message(ChangeAdminInfo.change_balance)
async def change_balance_amount(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text.isdigit():
        try:
            amount = float(message.text)
            user_id = await state.get_data()
            changebalance_db(user_id["user_id"], amount)
            await message.bot.send_message(message.from_user.id, f"Баланс изменен ✅",
                                           reply_markup=await main_menu_bt())
            await state.clear()

        except:
            await message.bot.send_message(message.from_user.id, "🚫Не удалось изменить",
                                           reply_markup=await main_menu_bt())
            await state.clear()
    else:
        await message.bot.send_message(message.from_user.id, "️️❗Ошибка", reply_markup=await main_menu_bt())
        await state.clear()
@admin_router.message(ChangeAdminInfo.change_refs)
async def change_refs_amount(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text.isdigit():
        try:
            amount = float(message.text)
            user_id = await state.get_data()
            changerefs_db(user_id["user_id"], amount)
            await message.bot.send_message(message.from_user.id, f"Рефералы изменены ✅",
                                           reply_markup=await main_menu_bt())
            await state.clear()

        except:
            await message.bot.send_message(message.from_user.id, "🚫Не удалось изменить",
                                           reply_markup=await main_menu_bt())
            await state.clear()
    else:
        await message.bot.send_message(message.from_user.id, "️️❗Ошибка", reply_markup=await main_menu_bt())
        await state.clear()
