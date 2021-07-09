import os

import telebot
from dotenv import load_dotenv

from loggers import get_logger
from qrcode_detect import QRCodeExtractor

load_dotenv()  # load os environments from .env file


TOKEN = os.getenv('BOT_TOKEN')
NOT_FOUND_QRCODE = os.path.join(os.getcwd(), 'images/images_without_qrcode/')
FOUND_QRCODE = os.path.join(os.getcwd(), 'images/images_with_qrcode/')
logger = get_logger('telegram-bot')

bot = telebot.TeleBot(TOKEN)
logger.info('Bot starting success')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(content_types=['photo'])
def handle_docs_voice(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        raw_photo = bot.download_file(file_info.file_path)

        image = QRCodeExtractor.read_image_from_bytes(raw_photo)
        barcode, image_with_qr = QRCodeExtractor.find_qrcode(image)
        path = QRCodeExtractor.save_image(FOUND_QRCODE, image_with_qr, name='tmp')
        bot.send_photo(message.chat.id, photo=open(path, 'rb'), reply_to_message_id=message.message_id)

        if barcode:
            bot.send_message(message.chat.id, "QR код успешно распознан. Подождите немного")
            path = QRCodeExtractor.save_image(FOUND_QRCODE, image_with_qr)
            logger.warning(f"Bar code found. Image save to {path}")
        else:
            bot.reply_to(message, "Bar code not found")
            path = QRCodeExtractor.save_image(NOT_FOUND_QRCODE, image_with_qr)
            logger.warning(f"Bar code not found. Image save to {path}")
    except Exception as e:
        logger.exception("Error")
        bot.reply_to(message, "Server error")


if __name__ == '__main__':
    bot.polling(none_stop=False, interval=0, timeout=20)