from logging.config import valid_ident
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from keyboards.inline.admin import keyboard
from data.config import ADMINS
from keyboards.default.delete_menu import menu_delete
from loader import dp,kino_db,bot,user_db
from aiogram.dispatcher.handler import CancelHandler
from keyboards.inline.admin import ad_menu
from aiogram import types
from states.states import KinoAddState,KinoDeleteState
from utils.db_api.kino import KinoDatabase




@dp.message_handler(commands='kino_add')
async def kino_add_function(message:types.Message):
    if message.from_user.id==7126357860:
        await KinoAddState.kino_add.set()
        await message.reply("Kinoni Yuboring")
    else:
        await message.answer("Siz admin emassiz")


@dp.message_handler(state=KinoAddState.kino_add,content_types=types.ContentType.VIDEO)
async def message_kino_added(message:types.Message,state:FSMContext):
    async with state.proxy() as data:
        data['file_id']=message.video.file_id
        data['caption']=message.caption

    await KinoAddState.kino_kod.set()
    await message.reply("Kino uchun Kod yuboring .")

@dp.message_handler(state=KinoAddState.kino_kod,content_types=types.ContentType.TEXT)
async def message_kino_kod_handler(message:types.Message,state:FSMContext):
    try:
        post_id=int(message.text)
        async with state.proxy() as data:
            data['post_id']=post_id
            kino_db.add_kino(post_id,file_id=data['file_id'],caption=data['caption'])
        await message.reply("Kino muvaffaqiyatli qo'shildi")
        await state.finish()
    except ValueError:
        await message.reply("Iltimos Kino Kod sifatida  faqat raqam kiriting")





#kinoni o'chirish
@dp.message_handler(commands='delete_kino')
async def message_delete_kino(message:types.Message):
    if message.from_user.id==7126357860:
        await KinoDeleteState.kino_kod.set()
        await message.answer("0'chirmoqchi bo'lgan Kino kodini yuboring ")
    else:

        await message.answer("Siz admin emassiz")


@dp.message_handler(state=KinoDeleteState.kino_kod,content_types=types.ContentType.TEXT)
async def kino_code_handler(message:types.Message,state:FSMContext):
    async with state.proxy() as data:
        data['post_id']=int(message.text)
        result=kino_db.get_kino_by_post_id(data['post_id'])
        if result:
            await message.answer_video(video=result['file_id'],caption=result['caption'])
            await message.answer("Quyidagi tugmalardan birini tanlang",reply_markup=menu_delete)
            await KinoDeleteState.is_confirm.set()
        else:
            await message.answer(f"{data['post_id']} raqam bilan kino topilmadi")

@dp.message_handler(state=KinoDeleteState.is_confirm,content_types=types.ContentType.TEXT)
async def message_is_confirm(message:types.Message,state:FSMContext):
    async with state.proxy() as data:
        data['confirm']=message.text
        if message.text=="✅Tasdiqlash":
            kino_db.delete_kino_by_postid(data['post_id'])
            await message.answer("Kino muvaffaqiyatli o'chirildi")
            await state.finish()
        elif message.text=="❌Bekor Qilish":
            await state.finish()
            await message.answer("Bekor qilindi")
        else:
            await message.answer("Iltimos quyidagi  tugmalardan birini tanlang",reply_markup=menu_delete)













#kino kodini yuborsa videoni yuborish
# In your kino_handlers.py (or wherever the handler is defined)
@dp.message_handler(lambda x : x.text.isdigit())
async def wait_for_post_id(message: types.Message, state: FSMContext):
    try:
        if message.text.isdigit():
            kino_kod = message.text  # Expecting a valid post_id (integer)
    except ValueError:
        await message.reply(
            "Siz kino kodi yubormadingiz.\nKino kodi raqamdan iborat.\nQayta qidirishga kirish uchun /start ni bosing")
        return


    kino = kino_db.get_kino_by_post_id(kino_kod)

    if kino:
        file_id = kino['file_id']
        caption = kino['caption']
        await message.answer_video(file_id, caption=caption, protect_content=True)
    else:
        await message.answer("Kino topilmadi.\n Qayta /start ni bosing")
    await state.finish()



@dp.message_handler(commands='admin')
async def user_count(message: types.Message):
    if str(message.from_user.id) == ADMINS[0]:
        await message.answer(text='.', reply_markup=keyboard)
    else:
        await message.answer("Siz admin emassiz.")

@dp.callback_query_handler(text='today')
async def bugun_stat(call: CallbackQuery):
    bugun = kino_db.get_movies_bugun()
    if bugun:
        for movie in bugun:
            await call.message.answer(movie["name"] + "\n")
    else:
        await call.message.answer("Bugungi kinolar yo'q")





@dp.callback_query_handler(text='stats')
async def statistika(call: CallbackQuery):
    await call.message.delete()
    count = user_db.count_users()
    await call.message.answer(f"Bazada <b>{count}</b> ta foydalanuvchi bor")

stop = False

@dp.callback_query_handler(text='ad')
async def reklama(call: CallbackQuery):
    if  str(call.from_user.id) == 7126357860:
        await call.message.answer("Reklama yuborilmaydi, adminlar uchun.")
        return

    else:
        await call.answer("siz admin emmassiz!")

    await call.message.delete()
    await call.message.answer("Reklama videosi yoki rasmini yoziv bilan yuboring.")


@dp.message_handler(content_types=['photo', 'video', 'text'])
async def handle_ad_message(ad_message: types.Message):
    if str(ad_message.from_user.id) == 7126357860:
        global stop  # Use the global stop flag
        not_sent = 0
        sent = 0
        admins = 0
        text = f"Xabar yuborish\nYuborilgan: {sent}\nYuborilmagan: {not_sent}\nUmumiy: 0/{user_db.count_users()}\n\nStatus: Boshlanmoqda"
        status_message = await ad_message.answer(text, reply_markup=ad_menu)
        users = user_db.select_all_user_ids()

        for user_id in users:
            if str(user_id) in ADMINS:
                not_sent += 1
                admins += 1
                continue

            try:
                await ad_message.forward(user_id)
                sent += 1
            except:
                not_sent += 1

            text = f"Xabar yuborish\nYuborilgan: {sent}\nYuborilmagan: {not_sent} ({admins}ta Admin)\nUmumiy: {sent + not_sent}/{user_db.count_users()}\nStatus: Davom etmoqda"
            await bot.edit_message_text(text, chat_id=ad_message.chat.id, message_id=status_message.message_id, reply_markup=ad_menu)

            if stop:
                stop = False
                raise CancelHandler
        else:
            await ad_message.answer("siz admin emasiz!")


        text = f"Xabar yuborish\nYuborilgan: {sent}\nYuborilmagan: {not_sent} ({admins}ta Admin)\nUmumiy: {user_db.count_users()}/{user_db.count_users()}\nStatus: Tugatildi"
        await bot.edit_message_text(text, chat_id=ad_message.chat.id, message_id=status_message.message_id)

@dp.callback_query_handler(text='pause_ad')
async def stop_ad(call: CallbackQuery):
    global stop
    stop = True
    await call.message.answer("To'xtatildi.")
    raise CancelHandler
@dp.callback_query_handler(text='admin_menu_ad')
async def back_from_ad(call:CallbackQuery):
    global stop
    stop = True
    await call.message.delete()
    await call.message.answer("To'xtatildi",reply_markup=keyboard)
    raise CancelHandler


@dp.callback_query_handler(text='count_movie')
async def counting(call: CallbackQuery):
    counter = kino_db.count_kino()
    if counter:
        await call.message.delete()
        await call.message.answer(f"Bazada <b>{counter}</b> ta kino bor")
    else:
        await call.message.delete()
        await call.message.answer("Bazada kino yo'q")












