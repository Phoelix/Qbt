import logging
import requests
from telegram import (ReplyKeyboardMarkup, ParseMode, ReplyKeyboardRemove)
from telegram.ext import (Updater,CommandHandler,MessageHandler,Filters,RegexHandler,
                          ConversationHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)