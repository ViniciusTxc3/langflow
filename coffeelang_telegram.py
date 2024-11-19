import warnings
warnings.simplefilter("ignore", category=RuntimeWarning)

from typing import Final
from telegram import Update
from telegram.ext import Application, Updater, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from langflow.load import run_flow_from_json
import asyncio


TOKEN: Final = "TOKEN_TELGRAM"
BOT_USERNAME: Final = "@NAME_BOT"

TWEAKS = {
  "ChatInput-nsH7J": {},
  "Prompt-MSqxP": {},
  "Memory-CPdEG": {},
  "ChatOutput-eZIAa": {},
  "GoogleGenerativeAIModel-5dB6I": {}
}
# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá, sou o LangCoffee! Um bot Barista de café virtual. Como posso te ajudar?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Se precisar de ajuda, digite algo que eu possa te ajudar!")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Minha respostas são personalizadas, digite algo que eu possa te ajudar!")

# handlers
async def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'oi' in processed:
        return "Oi, tudo bem? Como posso te atender?"
    
    if 'teste' in processed:
        return "Testando 1, 2, 3..."
    
    try:
        chain = await asyncio.to_thread(run_flow_from_json,
            flow="./flow_coffee_lang.json",
            input_value=processed,
            fallback_to_env_vars=True, # False by default
            tweaks=TWEAKS)
        response_chain = chain[0].outputs[0].results['message'].data['text']

        return response_chain
    
    except Exception as e:
        print(f"Error processing flow: {e}")
        return "Desculpe, não entendi o que você disse."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User: ({update.message.chat.id}) in {message_type}: {text}")

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = await handle_response(new_text)
        else:
            return
    else:
        response: str = await handle_response(text)

        print(f"Bot: {response}")
        await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


# Inicializar o bot do Telegram
if __name__ == "__main__":

    app = Application.builder().token(TOKEN).build()
    #commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    #messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    #errors
    app.add_error_handler(error)

    print("Bot is running!")
    app.run_polling(poll_interval=3)