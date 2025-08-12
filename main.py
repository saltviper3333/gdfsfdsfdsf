# meta developer: @your_username
# scope: hikka_only

import asyncio
import random
import os
from telethon import errors
from .. import loader, utils

@loader.tds
class AutoSpamMod(loader.Module):
    """Автоматический спам из фиксированного файла"""
    
    strings = {
        "name": "AutoSpam",
        "spam_started": "🚀 <b>Спам запущен!</b>\n📁 Файл: <code>messages.txt</code>\n⚡ Задержка: <b>0.5 сек</b>",
        "spam_stopped": "⛔ <b>Спам остановлен!</b>",
        "spam_error": "❌ <b>Ошибка:</b> <code>{}</code>",
        "file_not_found": "❌ <b>Файл messages.txt не найден!</b>\nСоздайте файл messages.txt в папке с ботом",
        "file_empty": "❌ <b>Файл messages.txt пуст!</b>\nДобавьте текст в файл",
        "already_running": "⚠️ <b>Спам уже запущен!</b>\nИспользуйте .stopspam для остановки",
        "not_running": "❌ <b>Спам не активен</b>",
        "flood_wait": "🚫 <b>FloodWait!</b> Ожидание <b>{}</b> секунд...",
    }
    
    def __init__(self):
        self.spam_active = False
        self.file_name = "messages.txt"  # Фиксированный файл
    
    def read_messages(self):
        """Читает сообщения из файла messages.txt"""
        try:
            if not os.path.exists(self.file_name):
                return None
            
            with open(self.file_name, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            return lines if lines else []
        except Exception:
            return []
    
    @loader.command()
    async def startspam(self, message):
        """Запустить спам из файла messages.txt"""
        
        if self.spam_active:
            await utils.answer(message, self.strings["already_running"])
            return
        
        # Читаем файл
        messages = self.read_messages()
        
        if messages is None:
            await utils.answer(message, self.strings["file_not_found"])
            return
        
        if not messages:
            await utils.answer(message, self.strings["file_empty"])
            return
        
        # Запускаем спам
        self.spam_active = True
        await utils.answer(message, self.strings["spam_started"])
        
        try:
            while self.spam_active:
                # Выбираем случайную строку
                random_message = random.choice(messages)
                
                try:
                    # Отправляем сообщение
                    await message.client.send_message(message.chat_id, random_message)
                    
                    # Минимальная задержка
                    await asyncio.sleep(0.5)
                    
                except errors.FloodWaitError as e:
                    await utils.answer(message, self.strings["flood_wait"].format(e.seconds))
                    await asyncio.sleep(e.seconds)
                    continue
                
                except Exception as e:
                    await utils.answer(message, self.strings["spam_error"].format(str(e)))
                    break
                    
        except Exception as e:
            await utils.answer(message, self.strings["spam_error"].format(str(e)))
        
        finally:
            self.spam_active = False
    
    @loader.command()
    async def stopspam(self, message):
        """Остановить спам"""
        if self.spam_active:
            self.spam_active = False
            await utils.answer(message, self.strings["spam_stopped"])
        else:
            await utils.answer(message, self.strings["not_running"])
