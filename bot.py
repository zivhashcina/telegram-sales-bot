import logging
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from datetime import datetime, timezone
import config
from database import db_session, init_db
from models import User, Product, Interaction, Search

# מצבי שיחה לצור קשר – רק שם והודעה
CONTACT_NAME, CONTACT_MESSAGE = range(2)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    return url and isinstance(url, str) and (url.startswith('http://') or url.startswith('https://'))

async def save_user(update: Update):
    tg_user = update.effective_user
    user = db_session.get(User, tg_user.id)
    if not user:
        user = User(
            id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            language_code=tg_user.language_code
        )
        db_session.add(user)
    user.last_interaction = datetime.now(timezone.utc)
    db_session.commit()
    return user

def log_interaction(user_id, product_id, action):
    interaction = Interaction(user_id=user_id, product_id=product_id, action=action)
    db_session.add(interaction)
    product = db_session.get(Product, product_id)
    if product:
        if action == 'view':
            product.views += 1
        elif action == 'click':
            product.clicks += 1
    db_session.commit()

async def show_main_menu(chat_id, context, text=None):
    """הצגת התפריט הראשי"""
    keyboard = [
        [InlineKeyboardButton("🔍 חפש מוצר", callback_data="search")],
        [InlineKeyboardButton("📂 קטגוריות", callback_data="categories")],
        [InlineKeyboardButton("⭐ המוצרים החמים", callback_data="top_products")],
        [InlineKeyboardButton("💬 צור קשר", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if text is None:
        text = "🛍 *ברוכים הבאים לחנות החכמה!*\n\nכאן תוכלו למצוא מוצרים במחירים מעולים.\nפשוט חפשו או בחרו קטגוריה."
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await save_user(update)
    await show_main_menu(update.effective_chat.id, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *עזרה*\n\n"
        "🔍 חיפוש – לחץ על כפתור החיפוש והקלד מילות חיפוש.\n"
        "📂 קטגוריות – בחר קטגוריה וקבל מוצרים.\n"
        "⭐ מוצרים חמים – המוצרים הפופולריים ביותר.\n"
        "💬 צור קשר – השאר פרטים ונחזור אליך.",
        parse_mode="Markdown"
    )

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """חיפוש Inline – לא שינינו"""
    query = update.inline_query.query
    if not query:
        return

    user = await save_user(update)
    search = Search(user_id=user.id, query=query)
    db_session.add(search)

    products = db_session.query(Product).filter(
        Product.is_active == True,
        (Product.name.ilike(f'%{query}%') | Product.description.ilike(f'%{query}%'))
    ).limit(10).all()

    search.results_count = len(products)
    db_session.commit()

    results = []
    for p in products:
        keyboard = [[InlineKeyboardButton("🛒 קנה עכשיו", url=p.affiliate_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        thumbnail = p.image_url if is_valid_url(p.image_url) else None
        results.append(
            update.inline_query.result_article(
                id=str(p.id),
                title=p.name,
                description=f"💰 {p.price} ₪",
                thumbnail_url=thumbnail,
                reply_markup=reply_markup,
                input_message_content=update.inline_query.InputMessageContent(
                    message_text=f"*{p.name}*\n{p.description}\n💰 מחיר: {p.price} ₪",
                    parse_mode="Markdown"
                )
            )
        )

    await update.inline_query.answer(results, cache_time=0)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """טיפול בהודעות טקסט – חיפוש או שיחת צור קשר"""
    if context.user_data.get('in_conversation'):
        return

    query_text = update.message.text
    user = await save_user(update)

    search = Search(user_id=user.id, query=query_text)
    db_session.add(search)

    products = db_session.query(Product).filter(
        Product.is_active == True,
        (Product.name.ilike(f'%{query_text}%') | Product.description.ilike(f'%{query_text}%'))
    ).limit(5).all()

    search.results_count = len(products)
    db_session.commit()

    if not products:
        await update.message.reply_text("😕 לא נמצאו מוצרים. נסה מילות חיפוש אחרות.")
        return

    for p in products:
        keyboard = [
            [InlineKeyboardButton("🛒 קנה עכשיו", url=p.affiliate_link)],
            [InlineKeyboardButton("🔍 חזרה לתפריט", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        log_interaction(user.id, p.id, 'view')
        if is_valid_url(p.image_url):
            await update.message.reply_photo(
                photo=p.image_url,
                caption=f"*{p.name}*\n{p.description}\n💰 מחיר: {p.price} ₪",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text=f"*{p.name}*\n{p.description}\n💰 מחיר: {p.price} ₪",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

# ------------------ פונקציות עזר לשליחת מוצר ------------------
async def send_product(chat_id, context, product, extra_buttons=None):
    """שולח הודעה עם מוצר (תמונה או טקסט) ומוסיף כפתורים"""
    keyboard = [
        [InlineKeyboardButton("🛒 קנה עכשיו", url=product.affiliate_link)]
    ]
    if extra_buttons:
        keyboard.extend(extra_buttons)
    # תמיד נוסיף כפתור חזרה לתפריט ראשי בתחתית
    keyboard.append([InlineKeyboardButton("🔍 חזרה לתפריט", callback_data="back_to_main")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    if is_valid_url(product.image_url):
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=product.image_url,
            caption=f"*{product.name}*\n{product.description}\n💰 מחיר: {product.price} ₪",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*{product.name}*\n{product.description}\n💰 מחיר: {product.price} ₪",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

# ------------------ שיחת צור קשר (ללא אימייל) ------------------
async def contact_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except telegram.error.TimedOut:
        logger.warning("Answer callback query timed out, continuing anyway")
    chat_id = query.message.chat_id
    await query.message.delete()
    await context.bot.send_message(
        chat_id=chat_id,
        text="📝 אנא הקלד את *שמך* (או לחץ /cancel לביטול):",
        parse_mode="Markdown"
    )
    context.user_data['in_conversation'] = True
    return CONTACT_NAME

async def contact_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact_name'] = update.message.text
    await update.message.reply_text("💬 אנא הקלד את *הודעתך*:", parse_mode="Markdown")
    return CONTACT_MESSAGE

async def contact_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact_message'] = update.message.text
    user = await save_user(update)
    chat_id = update.effective_chat.id

    lead_text = (
        f"🔔 *ליד חדש!*\n"
        f"👤 שם: {context.user_data['contact_name']}\n"
        f"🆔 משתמש: {user.id}\n"
        f"👤 שם משתמש: @{user.username if user.username else 'אין'}\n"
        f"💬 הודעה: {context.user_data['contact_message']}"
    )
    await context.bot.send_message(
        chat_id=config.LEADS_GROUP_ID,
        text=lead_text,
        parse_mode="Markdown"
    )

    keyboard = [[InlineKeyboardButton("🔍 חזרה לחנות", callback_data="back_to_main")]]
    await update.message.reply_text(
        "✅ תודה! הפרטים שלך נשלחו ונחזור אליך בהקדם.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data.clear()
    return ConversationHandler.END

async def contact_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ בוטל.")
    await show_main_menu(update.effective_chat.id, context)
    return ConversationHandler.END

# ------------------ טיפול בכפתורים (ניווט חדש) ------------------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except telegram.error.TimedOut:
        logger.warning("Answer callback query timed out, continuing anyway")

    data = query.data
    user = await save_user(update)
    chat_id = query.message.chat_id
    logger.info(f"Button clicked: {data} by user {user.id}")

    # ------------------ כפתור חיפוש ------------------
    if data == "search":
        await query.message.delete()
        await context.bot.send_message(
            chat_id=chat_id,
            text="🔍 הקלד את מילות החיפוש שלך:"
        )
        return

    # ------------------ כפתור קטגוריות (תפריט ראשי) ------------------
    if data == "categories":
        categories = db_session.query(Product.category).filter(Product.is_active == True).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        if not categories:
            await context.bot.send_message(chat_id, "אין קטגוריות זמינות כרגע.")
            return
        # שולחים הודעה חדשה עם רשימת קטגוריות
        keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in categories]
        keyboard.append([InlineKeyboardButton("🔙 חזרה לתפריט", callback_data="back_to_main")])
        await context.bot.send_message(
            chat_id=chat_id,
            text="📂 בחר קטגוריה:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        # מוחקים את ההודעה הקודמת (התפריט הראשי)
        await query.message.delete()
        return

    # ------------------ בחירת קטגוריה ------------------
    if data.startswith("cat_"):
        category = data[4:]
        products = db_session.query(Product).filter(Product.category == category, Product.is_active == True).limit(10).all()
        if not products:
            await context.bot.send_message(chat_id, f"אין מוצרים בקטגוריה {category}.")
            return
        # שמירת המידע ב-user_data לניווט
        context.user_data['current_category'] = category
        context.user_data['category_products'] = [p.id for p in products]
        context.user_data['category_index'] = 0

        # שליחת המוצר הראשון
        product = products[0]
        log_interaction(user.id, product.id, 'view')
        extra_buttons = [
            [InlineKeyboardButton("▶ למוצר הבא", callback_data="cat_next")]
        ]
        await send_product(chat_id, context, product, extra_buttons)
        await query.message.delete()  # מוחקים את רשימת הקטגוריות
        return

    # ------------------ כפתור "הבא" בקטגוריה ------------------
    if data == "cat_next":
        # שליפת המידע מה-user_data
        if 'category_products' not in context.user_data:
            await context.bot.send_message(chat_id, "אין מידע על קטגוריה. נסה שוב.")
            return
        products_ids = context.user_data['category_products']
        current_index = context.user_data.get('category_index', 0)
        next_index = (current_index + 1) % len(products_ids)
        context.user_data['category_index'] = next_index

        product = db_session.get(Product, products_ids[next_index])
        if not product:
            await context.bot.send_message(chat_id, "שגיאה בשליפת המוצר.")
            return

        log_interaction(user.id, product.id, 'view')
        extra_buttons = [
            [InlineKeyboardButton("▶ למוצר הבא", callback_data="cat_next")]
        ]
        await send_product(chat_id, context, product, extra_buttons)
        # מוחקים את ההודעה הקודמת (המוצר הקודם)
        await query.message.delete()
        return

    # ------------------ מוצרים חמים ------------------
    if data == "top_products":
        products = db_session.query(Product).filter(Product.is_active == True).order_by(Product.clicks.desc()).limit(10).all()
        if not products:
            await context.bot.send_message(chat_id, "אין מוצרים חמים כרגע.")
            return
        # שמירת המידע ב-user_data
        context.user_data['hot_products'] = [p.id for p in products]
        context.user_data['hot_index'] = 0

        product = products[0]
        log_interaction(user.id, product.id, 'view')
        extra_buttons = [
            [InlineKeyboardButton("▶ למוצר הבא", callback_data="hot_next")]
        ]
        await send_product(chat_id, context, product, extra_buttons)
        await query.message.delete()
        return

    # ------------------ כפתור "הבא" במוצרים חמים ------------------
    if data == "hot_next":
        if 'hot_products' not in context.user_data:
            await context.bot.send_message(chat_id, "אין מידע על מוצרים חמים. נסה שוב.")
            return
        products_ids = context.user_data['hot_products']
        current_index = context.user_data.get('hot_index', 0)
        next_index = (current_index + 1) % len(products_ids)
        context.user_data['hot_index'] = next_index

        product = db_session.get(Product, products_ids[next_index])
        if not product:
            await context.bot.send_message(chat_id, "שגיאה בשליפת המוצר.")
            return

        log_interaction(user.id, product.id, 'view')
        extra_buttons = [
            [InlineKeyboardButton("▶ למוצר הבא", callback_data="hot_next")]
        ]
        await send_product(chat_id, context, product, extra_buttons)
        await query.message.delete()
        return

    # ------------------ חזרה לתפריט ראשי ------------------
    if data == "back_to_main":
        # מנקה את כל המידע הזמני
        context.user_data.clear()
        await show_main_menu(chat_id, context)
        await query.message.delete()
        return

# ======================== יצירת אובייקט application לייצוא ל-main.py ========================
application = Application.builder().token(config.BOT_TOKEN).build()

# ConversationHandler לצור קשר
contact_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(contact_start, pattern='^contact$')],
    states={
        CONTACT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_name)],
        CONTACT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_message)],
    },
    fallbacks=[CommandHandler("cancel", contact_cancel)],
    allow_reentry=True
)
application.add_handler(contact_conv)

# Handlers רגילים
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(InlineQueryHandler(inline_query))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ======================== (לא חובה) הרצה ישירה – אפשר להשאיר או למחוק ========================
if __name__ == "__main__":
    init_db()
    print("Bot started locally with polling...")
    application.run_polling()