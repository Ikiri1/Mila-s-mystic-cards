import json
import random
import os
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, PreCheckoutQueryHandler, MessageHandler, filters

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '8531047689:AAGz-ro79_vNhf85dfYPn3z1KqmOsaz39_o')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN', 'YOUR_PAYMENT_PROVIDER_TOKEN')  # For Stripe, PayPal, etc.
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '8208671058'))  # Admin Telegram user ID
DATA_FILE = 'tarot_orders.json'
CHAT_DATA_FILE = 'chat_messages.json'

# Tarot Reading Types and Prices (in cents, e.g., 500 = $5.00)
TAROT_READINGS = {
    'single_card': {
        'name': '🔮 Советы',
        'description': 'Персональный расклад с советами',
        'price': 500,  # $5.00
        'currency': 'USD'
    },
    'three_card': {
        'name': '✨ Саморазвитие',
        'description': 'Расклад для личностного роста',
        'price': 500,  # $5.00
        'currency': 'USD'
    },
    'celtic_cross': {
        'name': '🌟 Здоровье',
        'description': 'Расклад на здоровье и благополучие',
        'price': 500,  # $5.00
        'currency': 'USD'
    },
    'love_reading': {
        'name': '💕 Любовь и отношения',
        'description': 'Специализированный расклад на любовь',
        'price': 500,  # $5.00
        'currency': 'USD'
    },
    'career_reading': {
        'name': '💼 Финансы и работа',
        'description': 'Расклад на карьеру и финансы',
        'price': 500,  # $5.00
        'currency': 'USD'
    },
    'daily_guidance': {
        'name': '☀️ Советы',
        'description': 'Ежедневные советы и прогнозы',
        'price': 500,  # $5.00
        'currency': 'USD'
    }
}

# Tarot Cards Database
TAROT_CARDS = {
    'major_arcana': [
        'The Fool', 'The Magician', 'The High Priestess', 'The Empress', 'The Emperor',
        'The Hierophant', 'The Lovers', 'The Chariot', 'Strength', 'The Hermit',
        'Wheel of Fortune', 'Justice', 'The Hanged Man', 'Death', 'Temperance',
        'The Devil', 'The Tower', 'The Star', 'The Moon', 'The Sun',
        'Judgement', 'The World'
    ],
    'cups': [
        'Ace of Cups', 'Two of Cups', 'Three of Cups', 'Four of Cups', 'Five of Cups',
        'Six of Cups', 'Seven of Cups', 'Eight of Cups', 'Nine of Cups', 'Ten of Cups',
        'Page of Cups', 'Knight of Cups', 'Queen of Cups', 'King of Cups'
    ],
    'wands': [
        'Ace of Wands', 'Two of Wands', 'Three of Wands', 'Four of Wands', 'Five of Wands',
        'Six of Wands', 'Seven of Wands', 'Eight of Wands', 'Nine of Wands', 'Ten of Wands',
        'Page of Wands', 'Knight of Wands', 'Queen of Wands', 'King of Wands'
    ],
    'swords': [
        'Ace of Swords', 'Two of Swords', 'Three of Swords', 'Four of Swords', 'Five of Swords',
        'Six of Swords', 'Seven of Swords', 'Eight of Swords', 'Nine of Swords', 'Ten of Swords',
        'Page of Swords', 'Knight of Swords', 'Queen of Swords', 'King of Swords'
    ],
    'pentacles': [
        'Ace of Pentacles', 'Two of Pentacles', 'Three of Pentacles', 'Four of Pentacles', 'Five of Pentacles',
        'Six of Pentacles', 'Seven of Pentacles', 'Eight of Pentacles', 'Nine of Pentacles', 'Ten of Pentacles',
        'Page of Pentacles', 'Knight of Pentacles', 'Queen of Pentacles', 'King of Pentacles'
    ]
}

# Card Meanings
CARD_MEANINGS = {
    'The Fool': 'New beginnings, innocence, spontaneity, a free spirit',
    'The Magician': 'Manifestation, resourcefulness, power, inspired action',
    'The High Priestess': 'Intuition, sacred knowledge, divine feminine, the subconscious mind',
    'The Empress': 'Femininity, beauty, nature, nurturing, abundance',
    'The Emperor': 'Authority, establishment, structure, a father figure',
    'The Hierophant': 'Spiritual wisdom, religious beliefs, conformity, tradition',
    'The Lovers': 'Love, harmony, relationships, values alignment, choices',
    'The Chariot': 'Control, willpower, success, action, determination',
    'Strength': 'Strength, courage, persuasion, influence, compassion',
    'The Hermit': 'Soul searching, introspection, being alone, inner guidance',
    'Wheel of Fortune': 'Good luck, karma, life cycles, destiny, a turning point',
    'Justice': 'Justice, fairness, truth, cause and effect, law',
    'The Hanged Man': 'Pause, surrender, letting go, new perspectives',
    'Death': 'Endings, change, transformation, transition',
    'Temperance': 'Balance, moderation, patience, purpose',
    'The Devil': 'Shadow self, attachment, addiction, restriction, sexuality',
    'The Tower': 'Sudden change, upheaval, chaos, revelation, awakening',
    'The Star': 'Hope, faith, purpose, renewal, spirituality',
    'The Moon': 'Illusion, fear, anxiety, subconscious, intuition',
    'The Sun': 'Positivity, fun, warmth, success, vitality',
    'Judgement': 'Judgement, reflection, evaluation, awakening, rebirth',
    'The World': 'Completion, accomplishment, travel, achievement, fulfillment'
}

def load_orders():
    """Load order data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_orders(data):
    """Save order data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_chats():
    """Load chat messages from JSON file"""
    if os.path.exists(CHAT_DATA_FILE):
        with open(CHAT_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_chats(data):
    """Save chat messages to JSON file"""
    with open(CHAT_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_chat_message(user_id, username, message_text, is_admin=False):
    """Add a chat message to the database"""
    chats = load_chats()
    
    if str(user_id) not in chats:
        chats[str(user_id)] = {
            'username': username,
            'messages': [],
            'active': True,
            'created_at': datetime.now().isoformat()
        }
    
    chats[str(user_id)]['messages'].append({
        'text': message_text,
        'is_admin': is_admin,
        'timestamp': datetime.now().isoformat()
    })
    
    save_chats(chats)

def draw_card():
    """Draw a random tarot card"""
    all_cards = []
    for suit in TAROT_CARDS.values():
        all_cards.extend(suit)
    
    card = random.choice(all_cards)
    meaning = CARD_MEANINGS.get(card, 'A card of mystery and potential')
    
    # Determine if reversed (30% chance)
    is_reversed = random.random() < 0.3
    
    return {
        'name': card,
        'meaning': meaning,
        'reversed': is_reversed
    }

def generate_single_card_reading():
    """Generate a single card reading"""
    card = draw_card()
    
    if card['reversed']:
        reading = f"🔮 *{card['name']}* (Перевернутая)\n\n"
        reading += f"*Значение:* {card['meaning']}\n\n"
        reading += "✨ Это перевернутое положение suggests challenges or blocked energy. Подумайте, как это относится к вашей ситуации."
    else:
        reading = f"🔮 *{card['name']}*\n\n"
        reading += f"*Значение:* {card['meaning']}\n\n"
        reading += "✨ Доверьтесь своей интуиции и будьте открыты к сообщениям, которые приносит эта карта."
    
    return reading

def generate_three_card_reading():
    """Generate a three card spread (Past, Present, Future)"""
    past = draw_card()
    present = draw_card()
    future = draw_card()
    
    reading = "✨ *Расклад из трех карт*\n\n"
    
    reading += f"📜 *ПРОШЛОЕ*\n{past['name']}"
    if past['reversed']:
        reading += " 🔄"
    reading += f"\n{past['meaning']}\n\n"
    
    reading += f"🌟 *НАСТОЯЩЕЕ*\n{present['name']}"
    if present['reversed']:
        reading += " 🔄"
    reading += f"\n{present['meaning']}\n\n"
    
    reading += f"🔮 *БУДУЩЕЕ*\n{future['name']}"
    if future['reversed']:
        reading += " 🔄"
    reading += f"\n{future['meaning']}\n\n"
    
    reading += "✨ Ваше прошлое формирует вас, настоящее направляет, а будущее показывает потенциальные исходы."
    
    return reading

def generate_celtic_cross_reading():
    """Generate a Celtic Cross spread"""
    cards = [draw_card() for _ in range(10)]
    positions = [
        "Настоящее", "Вызов", "Прошлое", "Недавнее прошлое",
        "Возможное будущее", "Ближайшее будущее", "Подход", "Внешнее", "Надежды/Страхи", "Исход"
    ]
    
    reading = "🌟 *Кельтский крест*\n\n"
    
    for i, (card, position) in enumerate(zip(cards, positions), 1):
        reading += f"*{i}. {position}*\n{card['name']}"
        if card['reversed']:
            reading += " 🔄"
        reading += f"\n{card['meaning']}\n\n"
    
    reading += "✨ Этот комплексный расклад раскрывает несколько уровней вашей ситуации. Подумайте о том, как эти карты связаны между собой."
    
    return reading

def generate_themed_reading(theme):
    """Generate a themed reading (love, career, etc.)"""
    cards = [draw_card() for _ in range(3)]
    
    themes = {
        'love': {
            'title': '💕 Любовь и отношения',
            'positions': ['Текущая ситуация', 'Что нужно знать', 'Будущее']
        },
        'career': {
            'title': '💼 Финансы и работа',
            'positions': ['Текущее состояние', 'Возможности', 'Перспективы']
        }
    }
    
    theme_info = themes.get(theme, themes['love'])
    
    reading = f"{theme_info['title']}\n\n"
    
    for i, (card, position) in enumerate(zip(cards, theme_info['positions']), 1):
        reading += f"*{i}. {position}*\n{card['name']}"
        if card['reversed']:
            reading += " 🔄"
        reading += f"\n{card['meaning']}\n\n"
    
    reading += "✨ Подумайте, как эти карты связаны с вашей ситуацией."
    
    return reading

def generate_daily_guidance():
    """Generate daily guidance reading"""
    card = draw_card()
    
    reading = f"☀️ *Карта дня: {card['name']}*"
    if card['reversed']:
        reading += " 🔄"
    reading += "\n\n"
    
    reading += f"*Значение:* {card['meaning']}\n\n"
    
    if card['reversed']:
        reading += "✨ Сегодня могут быть вызовы. Используйте это как возможность для роста."
    else:
        reading += "✨ Примите эту энергию и позвольте ей направлять ваш день."
    
    return reading

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = (
        "*Таро-бот Милы*\n\n"
        "Привет! Я — Мила, таролог с 9-летним опытом. Мой бот поможет вам найти ответы на важные вопросы и понять будущее через карты Таро прямо в Telegram. ✨\n\n"
        "*🔮 Что предлагает бот*\n\n"
        "🌟 Прогнозы на будущее\n"
        "🌟 Расклады на любовь и отношения ❤️\n"
        "🌟 Помощь в принятии решений ⚖️\n"
        "🌟 Анализ текущей ситуации 🔍\n\n"
        "По всем вопросам пишите [@sunnyweather17](https://t.me/sunnyweather17)"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 Начни сейчас", callback_data="show_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command - show all available readings"""
    await show_menu(update, context)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the menu of available readings"""
    message = "🔮 *Выберите свою категорию*\n\n"
    
    keyboard = []
    # Group buttons in rows of 2 for compact layout
    row = []
    for reading_id, reading_info in TAROT_READINGS.items():
        price_dollars = reading_info['price'] / 100
        button_text = f"{reading_info['name']}\n${price_dollars:.2f}"
        
        row.append(InlineKeyboardButton(button_text, callback_data=f"order_{reading_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    # Add remaining button if odd number
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "show_menu":
        context.user_data['in_chat'] = False  # Exit chat mode
        await show_menu(update, context)
    elif query.data.startswith("order_"):
        reading_id = query.data.replace("order_", "")
        await process_order(update, context, reading_id)
    elif query.data.startswith("pay_"):
        reading_id = query.data.replace("pay_", "")
        await show_payment_methods(update, context, reading_id)
    elif query.data.startswith("payment_card_"):
        reading_id = query.data.replace("payment_card_", "")
        await show_bank_options(update, context, reading_id)
    elif query.data.startswith("payment_mia_"):
        reading_id = query.data.replace("payment_mia_", "")
        await show_mia_option(update, context, reading_id)
    elif query.data.startswith("payment_crypto_"):
        reading_id = query.data.replace("payment_crypto_", "")
        await show_crypto_options(update, context, reading_id)
    elif query.data.startswith("bank_"):
        # Extract bank name and reading_id from callback data
        parts = query.data.split('_')
        if len(parts) >= 3:
            bank_name = parts[1]
            reading_id = '_'.join(parts[2:])
            await show_bank_confirmation(update, context, bank_name, reading_id)
    elif query.data.startswith("copy_mia_"):
        reading_id = query.data.replace("copy_mia_", "")
        await show_mia_confirmation(update, context, reading_id)
    elif query.data.startswith("copy_crypto_"):
        # Extract currency and reading_id
        parts = query.data.split('_')
        if len(parts) >= 4:
            currency = parts[2].upper()
            reading_id = '_'.join(parts[3:])
            await show_crypto_confirmation(update, context, currency, reading_id)
    elif query.data.startswith("confirm_payment_"):
        reading_id = query.data.replace("confirm_payment_", "")
        await confirm_payment(update, context, reading_id)
    elif query.data == "back_to_menu":
        context.user_data['in_chat'] = False  # Exit chat mode
        await show_menu(update, context)
    elif query.data == "end_chat":
        context.user_data['in_chat'] = False
        await query.edit_message_text(
            "💬 Чат завершен. Вы можете начать новый чат после следующего заказа.\n\n"
            "Спасибо за использование нашего сервиса! ✨"
        )
        keyboard = [
            [InlineKeyboardButton("📋 Вернуться в меню", callback_data="show_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Выберите свой следующий расклад:",
            reply_markup=reply_markup
        )

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    help_text = (
        "❓ *Помощь*\n\n"
        "*Как это работает:*\n"
        "1️⃣ Выберите расклад\n"
        "2️⃣ Завершите оплату\n"
        "3️⃣ Получите свой расклад\n\n"
        "*Команды:*\n"
        "/start - Запустить бота\n"
        "/menu - Просмотреть расклады\n"
        "/help - Показать помощь\n\n"
        "✨ Каждый расклад уникален и персонализирован."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def process_order(update: Update, context: ContextTypes.DEFAULT_TYPE, reading_id: str):
    """Process an order for a tarot reading"""
    if reading_id not in TAROT_READINGS:
        await update.callback_query.answer("❌ Неверный тип расклада", show_alert=True)
        return
    
    reading_info = TAROT_READINGS[reading_id]
    user_id = update.effective_user.id
    
    # Store the order in context for later retrieval
    context.user_data['pending_order'] = reading_id
    
    price_dollars = reading_info['price'] / 100
    
    # Show invoice card with payment button (matching demo format)
    invoice_text = (
        f"*{reading_info['name']}*\n"
        f"*${price_dollars:.2f}*"
    )
    
    keyboard = [
        [InlineKeyboardButton(f"💳 Pay ${price_dollars:.2f}", callback_data=f"pay_{reading_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        invoice_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE, reading_id: str):
    """Show payment method options"""
    payment_text = "*💳 Выберите способ оплаты*"
    
    keyboard = [
        [InlineKeyboardButton("💳 Банковская карта", callback_data=f"payment_card_{reading_id}")],
        [InlineKeyboardButton("↔️ MIA", callback_data=f"payment_mia_{reading_id}")],
        [InlineKeyboardButton("₿ Криптовалюта", callback_data=f"payment_crypto_{reading_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        payment_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_bank_options(update: Update, context: ContextTypes.DEFAULT_TYPE, reading_id: str):
    """Show bank card options"""
    bank_text = (
        "*💳 Выберите банк*\n\n"
        "Victoriabank\n"
        "`0000 0000 0000 0000`\n\n"
        "MAIB\n"
        "`0000 0000 0000 0000`\n\n"
        "OTP\n"
        "`0000 0000 0000 0000`"
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Victoriabank", callback_data=f"bank_victoria_{reading_id}")],
        [InlineKeyboardButton("📋 MAIB", callback_data=f"bank_maib_{reading_id}")],
        [InlineKeyboardButton("📋 OTP", callback_data=f"bank_otp_{reading_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        bank_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_bank_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, bank_name: str, reading_id: str):
    """Show bank account confirmation"""
    bank_names = {
        'victoria': 'Victoriabank',
        'maib': 'MAIB',
        'otp': 'OTP'
    }
    bank_display = bank_names.get(bank_name, bank_name)
    
    confirmation_text = (
        f"✅ {bank_display} номер счёта скопирован: `0000 0000 0000 0000`"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить платеж", callback_data=f"confirm_payment_{reading_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        confirmation_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_mia_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, reading_id: str):
    """Show MIA number confirmation"""
    confirmation_text = (
        "✅ MIA номер скопирован: `68766888`"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить платеж", callback_data=f"confirm_payment_{reading_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        confirmation_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_crypto_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, currency: str, reading_id: str):
    """Show cryptocurrency address confirmation"""
    address = "LTCXXXX XXX XXXXXXXXXXX"
    confirmation_text = (
        f"✅ {currency} адрес скопирован: `{address}`"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить платеж", callback_data=f"confirm_payment_{reading_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        confirmation_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_mia_option(update: Update, context: ContextTypes.DEFAULT_TYPE, reading_id: str):
    """Show MIA payment option"""
    mia_text = (
        "*↔️ MIA*\n\n"
        "068 766 888\n"
        "_Artiom C_"
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Копировать номер", callback_data=f"copy_mia_{reading_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        mia_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_crypto_options(update: Update, context: ContextTypes.DEFAULT_TYPE, reading_id: str):
    """Show cryptocurrency payment options"""
    crypto_text = (
        "*₿ Криптовалюта*\n\n"
        "USD\n"
        "`LTCXXXX XXX XXXXXXXXXXX`\n\n"
        "LTC\n"
        "`LTCXXXX XXX XXXXXXXXXXX`"
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Копировать адрес USD", callback_data=f"copy_crypto_usd_{reading_id}")],
        [InlineKeyboardButton("📋 Копировать адрес LTC", callback_data=f"copy_crypto_ltc_{reading_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        crypto_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, reading_id: str):
    """Confirm payment and deliver reading"""
    # Show confirmation message first
    await update.callback_query.edit_message_text("✅ Платеж подтвержден!")
    
    # Save order
    orders = load_orders()
    order_id = f"{update.effective_user.id}_{datetime.now().timestamp()}"
    orders[order_id] = {
        'user_id': update.effective_user.id,
        'username': update.effective_user.username,
        'reading_type': reading_id,
        'amount': TAROT_READINGS[reading_id]['price'],
        'currency': TAROT_READINGS[reading_id]['currency'],
        'timestamp': datetime.now().isoformat()
    }
    save_orders(orders)
    
    # Wait 1 second before redirecting (matching demo behavior)
    await asyncio.sleep(1)
    
    # Deliver the reading
    await deliver_reading(update, context, reading_id, payment=True)
    
    # Redirect to chat after payment
    await redirect_to_chat(update, context)

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pre-checkout query"""
    query = update.pre_checkout_query
    
    # Extract reading ID from payload
    payload_parts = query.invoice_payload.split('_')
    if len(payload_parts) >= 2 and payload_parts[1] in TAROT_READINGS:
        # Answer the pre-checkout query
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Неверный заказ")

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payment"""
    payment = update.message.successful_payment
    
    # Extract reading ID from payload
    payload_parts = payment.invoice_payload.split('_')
    if len(payload_parts) >= 2:
        reading_id = payload_parts[1]
        
        # Save order
        orders = load_orders()
        order_id = f"{update.effective_user.id}_{datetime.now().timestamp()}"
        orders[order_id] = {
            'user_id': update.effective_user.id,
            'username': update.effective_user.username,
            'reading_type': reading_id,
            'amount': payment.total_amount,
            'currency': payment.currency,
            'timestamp': datetime.now().isoformat()
        }
        save_orders(orders)
        
        # Deliver the reading
        await deliver_reading(update, context, reading_id, payment=True)
        
        # Redirect to chat after payment
        await redirect_to_chat(update, context)
    else:
        await update.message.reply_text("❌ Ошибка обработки заказа. Пожалуйста, свяжитесь с поддержкой.")

async def deliver_reading(update: Update, context: ContextTypes.DEFAULT_TYPE, reading_id: str, payment: bool = False):
    """Generate and deliver the tarot reading"""
    user = update.effective_user
    
    # Generate reading based on type
    if reading_id == 'single_card':
        reading_text = generate_single_card_reading()
    elif reading_id == 'three_card':
        reading_text = generate_three_card_reading()
    elif reading_id == 'celtic_cross':
        reading_text = generate_celtic_cross_reading()
    elif reading_id == 'love_reading':
        reading_text = generate_themed_reading('love')
    elif reading_id == 'career_reading':
        reading_text = generate_themed_reading('career')
    elif reading_id == 'daily_guidance':
        reading_text = generate_daily_guidance()
    else:
        reading_text = generate_single_card_reading()
    
    if payment:
        full_message = f"✨ *{user.first_name}, вот ваш расклад:*\n\n{reading_text}\n\n💫 *Пусть это принесет вам ясность.*"
    else:
        full_message = f"✨ *{user.first_name}, вот ваш расклад:*\n\n{reading_text}\n\n💫 *Пусть это принесет вам ясность.*"
    
    keyboard = [
        [InlineKeyboardButton("📋 Заказать еще", callback_data="show_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query and not payment:
        await update.callback_query.edit_message_text(
            full_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            full_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def redirect_to_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redirect user to chat interface after payment"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Mark user as in chat mode
    context.user_data['in_chat'] = True
    
    welcome_message = (
        "*💬 Добро пожаловать в чат поддержки*\n\n"
        "Теперь вы можете напрямую общаться с нашим администратором о прочитанном или задавать любые вопросы!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎴 Перетасуйте карты", url="https://t.me/sunnyweather17")],
        [InlineKeyboardButton("📋 Вернуться в меню", callback_data="show_menu")],
        [InlineKeyboardButton("❌ Завершить чат", callback_data="end_chat")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Handle both callback queries and regular messages
    if update.message:
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        # For callback queries, send a new message
        await context.bot.send_message(
            chat_id=chat_id,
            text=welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # Notify admin about new chat
    if ADMIN_USER_ID and ADMIN_USER_ID > 0:
        try:
            admin_message = (
                f"🔔 *Новый чат начат*\n\n"
                f"👤 Пользователь: {user.first_name} (@{user.username or 'N/A'})\n"
                f"🆔 ID: `{user.id}`\n\n"
                f"Используйте /chats для просмотра всех активных чатов или /reply_{user.id} для ответа."
            )
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=admin_message,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Error notifying admin: {e}")

async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages when user is in chat mode"""
    user = update.effective_user
    message_text = update.message.text
    
    # Skip if this is a registered command (let CommandHandler deal with it)
    # But handle /reply_* as it's a dynamic command
    if message_text.startswith('/'):
        if message_text.startswith('/reply_') and user.id == ADMIN_USER_ID and ADMIN_USER_ID > 0:
            # Handle admin reply command
            command_parts = message_text.split(' ', 1)
            if len(command_parts) < 2:
                await update.message.reply_text(
                    "Использование: /reply_<user_id> <ваше сообщение>\n\n"
                    "Пример: /reply_123456789 Привет! Чем могу помочь?"
                )
                return
            
            target_user_id_str = command_parts[0].replace('/reply_', '')
            reply_text = command_parts[1]
            
            try:
                target_user_id_int = int(target_user_id_str)
                
                # Save admin message
                add_chat_message(target_user_id_int, 'Admin', reply_text, is_admin=True)
                
                # Send to customer
                await context.bot.send_message(
                    chat_id=target_user_id_int,
                    text=f"💬 *Сообщение от администратора*\n\n{reply_text}",
                    parse_mode='Markdown'
                )
                
                await update.message.reply_text(f"✅ Сообщение отправлено пользователю {target_user_id_str}")
                
            except ValueError:
                await update.message.reply_text("❌ Неверный ID пользователя.")
            except Exception as e:
                await update.message.reply_text(f"❌ Ошибка отправки сообщения: {str(e)}")
        # For other commands, let CommandHandler process them
        return
    
    # Check if user is in chat mode (after payment)
    if context.user_data.get('in_chat', False):
        # Save customer message
        add_chat_message(user.id, user.username or user.first_name, message_text, is_admin=False)
        
        # Forward to admin
        if ADMIN_USER_ID and ADMIN_USER_ID > 0:
            try:
                forward_message = (
                    f"💬 *Сообщение от {user.first_name}*\n"
                    f"👤 @{user.username or 'N/A'} (ID: `{user.id}`)\n\n"
                    f"_{message_text}_\n\n"
                    f"Ответить: /reply_{user.id} <ваше сообщение>"
                )
                await context.bot.send_message(
                    chat_id=ADMIN_USER_ID,
                    text=forward_message,
                    parse_mode='Markdown'
                )
                
                # Confirm to customer
                await update.message.reply_text(
                    "✅ Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время. ✨"
                )
            except Exception as e:
                print(f"Error forwarding message to admin: {e}")
                await update.message.reply_text(
                    "⚠️ Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте еще раз."
                )
        else:
            await update.message.reply_text(
                "✅ Ваше сообщение получено! Мы свяжемся с вами в ближайшее время. ✨"
            )
    else:
        # User is not in chat mode, suggest starting a chat or ordering
        keyboard = [
            [InlineKeyboardButton("🚀 Начать заказ", callback_data="show_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "👋 Привет! Чтобы общаться с нашим администратором, сначала завершите расклад.\n\n"
            "Выберите расклад, чтобы начать! 🔮",
            reply_markup=reply_markup
        )

async def admin_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to view all active chats"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID or ADMIN_USER_ID == 0:
        await update.message.reply_text("❌ Эта команда доступна только администраторам.")
        return
    
    chats = load_chats()
    
    if not chats:
        await update.message.reply_text("📭 Нет активных чатов.")
        return
    
    message = "💬 *Активные чаты*\n\n"
    for user_id_str, chat_data in chats.items():
        if chat_data.get('active', True):
            username = chat_data.get('username', 'Неизвестно')
            message_count = len(chat_data.get('messages', []))
            message += f"👤 {username} (ID: `{user_id_str}`)\n"
            message += f"   Сообщений: {message_count}\n"
            message += f"   Ответить: /reply_{user_id_str} <сообщение>\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')


def main():
    """Start the bot"""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Please set your BOT_TOKEN environment variable or update it in tarot_bot.py")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers (order matters - commands first, then other handlers)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("chats", admin_chats))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    # Add text message handler last (catches non-command text and /reply_* commands)
    application.add_handler(MessageHandler(filters.TEXT, handle_chat_message))
    
    # Start the bot
    print("🔮 Mila's Mystic Cards is running...")
    print("💡 Note: Set PROVIDER_TOKEN environment variable to enable payments")
    if ADMIN_USER_ID == 0:
        print("⚠️  Note: Set ADMIN_USER_ID environment variable to enable admin chat features")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

