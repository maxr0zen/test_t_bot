from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
import datetime


def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client


async def view_sheet(update: Update, context: CallbackContext) -> None:
    try:
        client = context.bot_data['google_sheet_client']
        sheet = client.open("Telegram Bot Sheet").sheet1  
        data = sheet.get_all_values()
        formatted_data = '\n'.join(
            [f'({i + 1}, {chr(65 + j)}) = {data[i][j]}' for i in range(len(data)) for j in range(len(data[i]))])
        await update.message.reply_text(f'Данные из таблицы:\n{formatted_data}')
    except gspread.exceptions.SpreadsheetNotFound as e:
        await update.message.reply_text('Не удалось найти указанную таблицу Google Sheets.')
        print(e)


async def edit_sheet(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            'Пожалуйста, укажите ячейку и текст для вставки, используя команду /edit_sheet <ячейка> <текст>.')
        return

    cell = args[0]
    text_to_insert = ' '.join(args[1:])

    try:
        client = context.bot_data['google_sheet_client']
        sheet = client.open("Telegram Bot Sheet").sheet1  # Имя вашего Google Sheet
        sheet.update_acell(cell, text_to_insert)
        await update.message.reply_text(f'Значение ячейки {cell} обновлено на: {text_to_insert}')
    except gspread.exceptions.SpreadsheetNotFound as e:
        await update.message.reply_text('Не удалось найти указанную таблицу Google Sheets.')
        print(e)
    except gspread.exceptions.CellNotFound as e:
        await update.message.reply_text('Не удалось найти указанную ячейку в таблице Google Sheets.')
        print(e)


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Кнопка 1", url="https://yandex.ru/maps/?text=Ленина%201")],
        [InlineKeyboardButton("Кнопка 2", url="https://maxr0zen.github.io/test_t_bot/payment/payment.html")],
        [InlineKeyboardButton("Кнопка 3", callback_data='send_image')],
        [InlineKeyboardButton("Кнопка 4", callback_data='get_sheet_value')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'send_image':
        await query.message.reply_photo(photo=open('img1.jpg', 'rb'), caption='Картинка')
    elif query.data == 'get_sheet_value':
        try:
            client = context.bot_data['google_sheet_client']
            sheet = client.open("Telegram Bot Sheet").sheet1
            value = sheet.acell('A2').value
            await query.message.reply_text(f'Значение ячейки A2: {value}')
        except gspread.exceptions.SpreadsheetNotFound:
            await query.message.reply_text('Не удалось найти указанную таблицу Google Sheets.')
        except gspread.exceptions.CellNotFound:
            await query.message.reply_text('Не удалось найти указанную ячейку в таблице Google Sheets.')


async def handle_text(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    date_format = "%d.%m.%Y"
    try:
        date = datetime.datetime.strptime(user_input, date_format)
        if date.date() != datetime.date.today():
            raise ValueError("Дата не может быть в прошлом")

        client = context.bot_data['google_sheet_client']
        sheet = client.open("Telegram Bot Sheet").sheet1
        sheet.append_row([date.strftime(date_format)], value_input_option='USER_ENTERED',
                         insert_data_option='INSERT_ROWS')
        await update.message.reply_text('Дата верна')
    except ValueError:
        current_date = datetime.datetime.now().strftime(date_format)
        await update.message.reply_text(f'Неверно, сегодня {current_date}')
    except gspread.exceptions.SpreadsheetNotFound:
        await update.message.reply_text('Не удалось найти указанную таблицу Google Sheets.')


def main() -> None:
    google_sheet_client = connect_to_gsheet()

    application = Application.builder().token(config.token).build()
    application.bot_data['google_sheet_client'] = google_sheet_client

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CommandHandler("view_sheet", view_sheet))
    application.add_handler(CommandHandler("edit_sheet", edit_sheet))

    application.run_polling()


if __name__ == '__main__':
    main()
