# Cursos Pro Android by Skueletor ©️ 2021

import os
from database import db
from pyrogram import Client, filters
from config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from logging.handlers import RotatingFileHandler


if os.path.exists("log.txt"):
    with open("log.txt", "r+") as f_d:
        f_d.truncate(0)

# Cosas del registro...
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "log.txt", maxBytes=50000000, backupCount=10
        ),
        logging.StreamHandler(),
    ],
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)


PRO_ANDROID = Client("AntiChannelBot",
                api_id=Config.API_ID,
                api_hash=Config.API_HASH,
                bot_token=Config.BOT_TOKEN)


async def whitelist_check(chat_id,channel_id=0):
    if not (await db.is_chat_exist(chat_id)):
        await db.add_chat_list(chat_id)
    _chat_list = await db.get_chat_list(chat_id)
    if int(channel_id) in _chat_list:
        return True
    else:
        return False

async def get_channel_id_from_input(bot, message):
    try:
        a_id = message.text.split(" ",1)[1]
    except:
        await message.reply_text("Envíe el comando junto con el ID del canal")
        return False
    if not str(a_id).startswith("-"):
        try:
            a_id = await bot.get_chat(a_id)
            a_id = a_id.id
        except:
            await message.reply_text("ID de canal no válido")
            return False
    return a_id



custom_message_filter = filters.create(lambda _, __, message: False if message.forward_from_chat or message.from_user else True)
custom_chat_filter = filters.create(lambda _, __, message: True if message.sender_chat else False)

@PRO_ANDROID.on_message(custom_message_filter & filters.group & custom_chat_filter)
async def main_handler(bot, message):
    chat_id = message.chat.id
    a_id = message.sender_chat.id
    if (await whitelist_check(chat_id, a_id)):
        return
    try:
        res = await bot.kick_chat_member(chat_id, a_id)
    except:
        return await message.reply_text("Asciéndeme como administrador con permisos de expulsar usuarios para poder trabajar correctamente.")
    if res:
        mention = f"@{message.sender_chat.username}" if message.sender_chat.username else message.chat_data.title
        await message.reply_text(text=f"{mention} Ha sido baneado.\n\n💡 Puede escribir solo con su perfil pero no a través de otros canales.",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Desbanear", callback_data=f"unban_{chat_id}_{a_id}")]]),
                              )
    await message.delete()


@PRO_ANDROID.on_message(filters.command(["start"]) & filters.private)
async def start_handler(bot, message):
  
    await message.reply_text(text="""¡Hola ☺️!
Mi trabajo como bot es eliminar a los miembros que utilicen sus canales para hablar en tu grupo, eliminaré sólo el canal, no al usuario.
Simplemente agrégame al chat y empezaré a banear a los canales que escriben en el chat,
consulte /help para obtener más información acerca del bot.""",
                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Aprende a crear bots 🤖", url=f"https://t.me/+VDY6scK_lf9HsKRn"),
                                                                 InlineKeyboardButton("👤 Soporte", url=f"https://t.me/DKzippO")]]),
                             disable_web_page_preview=True)

@PRO_ANDROID.on_message(filters.command(["help"]) & filters.private)
async def help_handler(bot, message):
    await message.reply_text(text="""¡Hola, bienvenido al apartado de ayuda!
⇝ /ban [ID del canal] : Banea algún canal para que no pueda escribir desde él.
⇝ /unban [ID del canal] : Desbanea algún canal para que puedan hablar desde él
⇝ /add_whitelist [ID del canal] : Agrega el canal a la lista blanca y proteja el canal para evitar acciones automáticas por parte del bot.
⇝ /del_whitelist [ID del canal] : Elimina el canal de la lista blanca.
⇝ /show_whitelist : Muestra todos los canales de la lista blanca.
Para obtener más ayuda o reportar algún bug, toca el botón de "👤 Soporte" 👇🏻""",
                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Aprende a crear bots 🤖", url=f"https://t.me/+VDY6scK_lf9HsKRn"),
                                                                 InlineKeyboardButton("👤 Soporte", url=f"https://t.me/DKzippO")]]),
                             disable_web_page_preview=True)



@PRO_ANDROID.on_callback_query()
async def cb_handler(bot, query):
    cb_data = query.data
    if cb_data.startswith("unban_"):
        an_id = cb_data.split("_")[-1]
        chat_id = cb_data.split("_")[-2]
        user = await bot.get_chat_member(chat_id, query.from_user.id)
        if user.status == "creator" or user.status == "administrator":
            pass
        else:
            return await query.answer("¡Esta opción no es para ti! 🤨", show_alert=True)
        await bot.resolve_peer(an_id)
        res = await query.message.chat.unban_member(an_id)
        chat_data = await bot.get_chat(an_id)
        mention = f"@{chat_data.username}" if chat_data.username else chat_data.title
        if res:
            await query.message.reply_text(f"{mention} Ha sido desbaneado por {query.from_user.mention}")
            await query.message.edit_reply_markup(reply_markup=None)

@PRO_ANDROID.on_message(filters.command(["ban"]) & filters.group)
async def cban_handler(bot, message):
    chat_id = message.chat.id
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator" or user.status == "administrator":
        pass
    else:
        return
    try:
        a_id = await get_channel_id_from_input(bot, message)
        if not a_id:
            return
        if (await whitelist_check(chat_id, a_id)):
            return await message.reply_text("El ID del canal se encuentra en la lista blanca, por lo que no puede prohibir este canal")
        await bot.resolve_peer(a_id)
        res = await bot.kick_chat_member(chat_id, a_id)
        chat_data = await bot.get_chat(a_id)
        mention = f"@{chat_data.username}" if chat_data.username else chat_data.title
        if res:
            await message.reply_text(text=f"{mention} Ha sido baneado.\n\n💡 Él ahora puede escribir solo con su perfil pero no a través de otros canales.",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Desbanear", callback_data=f"unban_{chat_id}_{a_id}")]]),
                              )
        else:
            await message.reply_text("El ID proporcionado no es válido. 💡Revisa el ID del canal con el bot @googleimgbot")
    except Exception as e:
        print(e)

@PRO_ANDROID.on_message(filters.command(["unban"]) & filters.group)
async def uncban_handler(bot, message):
    chat_id = message.chat.id
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator" or user.status == "administrator":
        pass
    else:
        return
    try:
        a_id = await get_channel_id_from_input(bot, message)
        if not a_id:
            return
        if (await whitelist_check(chat_id, a_id)):
            return
        await bot.resolve_peer(a_id)
        res = await message.chat.unban_member(a_id)
        chat_data = await bot.get_chat(a_id)
        mention = f"@{chat_data.username}" if chat_data.username else chat_data.title
        if res:
            await message.reply_text(text=f"{mention} Ha sido desbaneado por {message.from_user.mention}")
        else:
            await message.reply_text("El ID proporcionado no es válido. 💡Revisa el ID del canal con el bot @googleimgbot")
    except Exception as e:
        print(e)
        await message.reply_text(e)


@PRO_ANDROID.on_message(filters.command(["add_whitelist"]) & filters.group)
async def add_whitelist_handler(bot, message):
    chat_id = message.chat.id
    user = await bot.get_chat_member(chat_id, message.from_user.id)
    if user.status == "creator" or user.status == "administrator":
        pass
    else:
        return
    try:
        a_id = await get_channel_id_from_input(bot, message)
        if not a_id:
            return
        if (await whitelist_check(chat_id, a_id)):
            return await message.reply_text("El ID del canal ya se encuentra en la lista blanca.")
        chk,msg = await db.add_chat_list(chat_id, a_id)
        if chk and msg != "":
            await message.reply_text(msg)
        else:
            await message.reply_text("Ha ocurrido un problema al guardar el canal en la lista blanca. 😖")
    except Exception as e:
        print(e)


@PRO_ANDROID.on_message(filters.command(["del_whitelist"]) & filters.group)
async def del_whitelist_handler(bot, message):
    chat_id = message.chat.id
    user = await bot.get_chat_member(chat_id, message.from_user.id)
    if user.status == "creator" or user.status == "administrator":
        pass
    else:
        return
    try:
        a_id = await get_channel_id_from_input(bot, message)
        if not a_id:
            return
        if not (await whitelist_check(chat_id, a_id)):
            return await message.reply_text("No se encontró el ID del canal en la lista blanca")
        chk,msg = await db.del_chat_list(message.chat.id, a_id)
        if chk:
            await message.reply_text(msg)
        else:
            await message.reply_text("Ha ocurrido un problema al eliminar el canal en la lista blanca. 😖")
    except Exception as e:
        print(e)


@PRO_ANDROID.on_message(filters.command(["show_whitelist"]) & filters.group)
async def del_whitelist_handler(bot, message):
    chat_id = message.chat.id
    user = await bot.get_chat_member(chat_id, message.from_user.id)
    if user.status == "creator" or user.status == "administrator":
        pass
    else:
        return
    show_wl = await db.get_chat_list(chat_id)
    if show_wl:
        await message.reply_text(f"Este ID se encuentra en la lista blanca.\n\n{show_wl}")
    else:
        await message.reply_text("Lista blanca no encontrada.")

if __name__ == "__main__":
    PRO_ANDROID.run()
