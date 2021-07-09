import os
import telebot
from loggers import get_logger
from qrcode_detect import QRCodeExtractor
from dotenv import load_dotenv
from nalog_python import NalogRuPython
from preprocess import create_df_by_dict, get_info_about_receipt
from create_graph_objects import create_bar_chart, create_pie_chart, del_images_by_chat_id

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
NOT_FOUND_QRCODE = os.path.join(os.getcwd(), 'images/images_without_qrcode/')
FOUND_QRCODE = os.path.join(os.getcwd(), 'images/images_with_qrcode/')
logger = get_logger('telegram-bot')
print(TOKEN)
bot = telebot.TeleBot(TOKEN)
logger.info('Bot starting success')

client = NalogRuPython()


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
        #bot.send_photo(message.chat.id, photo=open(path, 'rb'), reply_to_message_id=message.message_id)
        if barcode:
            #bot.send_message(message.chat.id, barcode)

            bot.send_message(message.chat.id, 'QR code распознан, подождите немного')

            ticket = client.get_ticket(barcode[0])
            path = QRCodeExtractor.save_image(FOUND_QRCODE, image_with_qr)
            print(ticket)
            products_df = create_df_by_dict(ticket)
            create_bar_chart(products_df, message.chat.id)
            create_pie_chart(products_df, message.chat.id)
            bot.send_photo(message.chat.id, photo=open(f'graphs/bar_chart_{message.chat.id}.png', 'rb'))
            bot.send_photo(message.chat.id, photo=open(f'graphs/pie_chart_{message.chat.id}.png', 'rb'))
            del_images_by_chat_id(message.chat.id)

            message_about_receipt = get_info_about_receipt(products_df)
            bot.send_message(message.chat.id, message_about_receipt)
        else:
            bot.reply_to(message, "Не удалось распознать QR-код на изображении. Пожалуйста, отправьте изображение ещё раз.")
            path = QRCodeExtractor.save_image(NOT_FOUND_QRCODE, image_with_qr)
            logger.warning(f"Bar code not found. Image save to {path}")
    except Exception as E:
        logger.exception("Error")
        bot.reply_to(message, "Произошла ошибка. Отправьте изображение ещё раз.")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0, timeout=20)
