
import os  
import logging  
from telegram import Update
from telegram.constants import ParseMode 
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes  
from openai import AzureOpenAI  
  
# Замените токены на ваши  
TELEGRAM_TOKEN = 'TELEGRAM_TOKEN'  
os.environ["AZURE_OPENAI_ENDPOINT"] = "Azure_endpoint"  
os.environ["AZURE_OPENAI_API_KEY"] = "Azure_API"  
  
# Идентификатор пользователя, от которого принимается тема  
AUTHORIZED_USER_ID = User_ID  # Замените на ID владельца  

pending_articles = {}   
# Инициализация клиента Azure OpenAI  
client = AzureOpenAI(  
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2023-03-15-preview"  
)  
  
# Настройка логирования  
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)  
  
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    await update.message.reply_text('Привет! Напишите /write_article <тема>, чтобы получить статью.')  
  
def generate_article(topic: str) -> str:  
    response = client.chat.completions.create(  
        model="gpt-4o",  
        messages=[  
            {"role": "system", "content": "You are a helpful assistant."},  
            {"role": "user", "content": f"{topic}"}  
        ]  
    )  
    return response.choices[0].message.content.strip()  
# Функция экранирования символов в MarkdownV2
def escape_markdown_v2(text):
    escape_chars = r'_[]()~>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])


async def write_article(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    if update.effective_user.id == AUTHORIZED_USER_ID:  
        if context.args:  
            topic = ' '.join(context.args)  # Получаем тему от пользователя  
            article_before = generate_article(topic)
            article = escape_markdown_v2(article_before)
            pending_articles[update.effective_user.id] = article  
            chat_id = '-1001876821651'  # Замените на идентификатор группы  
            await context.bot.send_message(chat_id=AUTHORIZED_USER_ID, text=article, parse_mode=ParseMode.MARKDOWN_V2)  
        else:  
            await update.message.reply_text('Пожалуйста, укажите тему после команды /write_article.')  
    else:  
        await update.message.reply_text('У вас нет прав для использования этой команды.')  
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    if update.effective_user.id == AUTHORIZED_USER_ID:  
        if context.args:  
            user_id = int(context.args[0])  
            if user_id in pending_articles:  
                article = pending_articles.pop(user_id)  
                chat_id = '-1001876821651'  # Идентификатор группы  
                await context.bot.send_message(chat_id=chat_id, text=article, parse_mode=ParseMode.MARKDOWN_V2)  
                await update.message.reply_text('Статья одобрена и отправлена в группу.') 
async def list_pending_articles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
    if update.effective_user.id == AUTHORIZED_USER_ID:  
        if pending_articles:  
            message = "Список ожидающих статей:\n"  
            for user_id, article in pending_articles.items():  
                message += f"Пользователь ID: {user_id}\n" 
                 
            await update.message.reply_text(message)  
        else:  
            await update.message.reply_text("Нет ожидающих статей.")  
    else:  
        await update.message.reply_text('У вас нет прав для использования этой команды.')  
def main() -> None:  
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()  
  
    application.add_handler(CommandHandler("start", start))  
    application.add_handler(CommandHandler("write_article", write_article))  
    application.add_handler(CommandHandler("approve", approve))  
    application.add_handler(CommandHandler("list_pending_articles", list_pending_articles))  
    application.run_polling()  
  
if __name__ == '__main__':  
    main()  

