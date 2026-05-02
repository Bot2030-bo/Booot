import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import random
from datetime import datetime, timedelta
import json
import os
import time
import io
import secrets

# ================== الإعدادات الأساسية ==================

TOKEN = "8754401332:AAEHgRgXn20RnpkPsFr9P_qMCb_2sxKd7Dw"
ADMIN_ID = 8399301540

# ================== إعدادات الاشتراك الإجباري ==================
REQUIRED_CHANNEL = "https://t.me/ichancycod"  # رابط القناة

# متغير لتخزين ملفات الاستعادة المؤقتة
pending_restore_files = {}

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================== تعريف المتغيرات العالمية ==================

balances = {}
xp = {}
levels = {}
history = {}
BARCODE_FILE_ID = None
BARCODE_FILE_ID_SYRIATEL = None
pending_charges = {}
first_charge_done = {}
welcome_gift_received = {}
banned_from_welcome_gift = []
referrals = {}
referral_codes = {}
referral_rewards_claimed = {}
raffle_entries = {}
raffle_participants = []
VIP_USERS = {}
AUTO_MESSAGE_TEXT = ""
PROMO_PHONE_NUMBER = "09XXXXXXXX"

# ================== متغيرات نظام الأكواد الجديدة ==================
winning_codes = {}      # { "CODE123": prize_amount }
losing_codes = []       # ["CODE456", "CODE789"]
used_codes = []         # ["CODE123"] الأكواد التي تم استخدامها
TOTAL_CODES_PRIZE = 6000  # إجمالي الجائزة الموزعة على الأكواد الرابحة

# ================== متغيرات نظام التحكم بالفوز ==================

# متغير جديد لتخزين نسبة الفوز الشاملة (لجميع المستخدمين)
global_win_rate = 30  # النسبة المئوية للفوز لجميع المستخدمين
win_prizes = {
    "0": 0,
    "1": 5000,
    "2": 5000,
    "3": 5000,
    "4": 40000,
    "5": 40000
}
DEFAULT_RATE = 1

# ================== متغير سحب الربح ==================

raffle_withdrawn = {}
pending_raffle_winner = None

# ================== متغيرات الإبلاغ للمدير ==================

user_reports_count = {}
MAX_REPORTS_PER_DAY = 3

# ================== متغير خاص بالفوز المخفي لأول مرة ==================

first_play_secret_win = {}  # {user_id: True/False} - هل حصل على الفوز المخفي أم لا
SECRET_WIN_AMOUNT = 50000  # مبلغ الفوز المخفي

# ================== إعدادات الألعاب ==================

FRUITS = ["🍒", "🍋", "🍉", "🍇", "🍎", "🍊"]

GAME_COST = 2500  # تم رفع سعر الألعاب إلى 2500
WELCOME_GIFT = 5000

# ================== إعدادات نظام الدعوة ==================

REFERRAL_REWARD_XP = 25
REFERRAL_REWARD_BALANCE = 5000
REQUIRED_REFERRALS = 3
RAFFLE_PRIZE = 500000

# ================== إعدادات VIP ==================

VIP_COST = 10000

# ================== شروط سحب الرصيد ==================
MINIMUM_WITHDRAWAL = 80000  # تم التعديل إلى 80000

# ================== حفظ البيانات ==================

DATA_FILE = "bot_data.json"

# النص الافتراضي للرسالة التلقائية
AUTO_MESSAGE_TEXT_DEFAULT = """
🎉 <b>الف مبروك الك!</b> 🎉

🤖 <b>بوت Ichancy.900 يدعوكم للربح الذهبي</b>

💰 اذا كنت مقطوع من الرصيد مالك الا تربح معنا

📞 <b>حط رقمك والباقي علينا</b>

🔥 <b>العرض الجديد لليوم فقط - لحق حالك!</b>

━━━━━━━━━━━━━━━━
✨ <b>عبي رصيدك واحصل على 5 اضعافه</b> ✨

💎 عبي 1000 واحصل على 5000
💎 شو ماطلبت رصيد رح يوصلك اضعافه

━━━━━━━━━━━━━━━━
✅ <b>لايوجد حد لسحب الرصيد</b>

🏆 <b>مبروك ل حماده حسن الراعي</b>
🎡 مبلغ 50000 ل.س بدولاب الحظ

━━━━━━━━━━━━━━━━
📞 <b>رقم التحويل:</b> <code>{phone_number}</code>

🚀 انتهت الرسالة
"""

# ================== متغيرات نظام ICHANCY (جديد) ==================
ichancy_accounts = {}
ICHANCY_DATA_FILE = "ichancy_data.json"

def load_ichancy_data():
    global ichancy_accounts
    if os.path.exists(ICHANCY_DATA_FILE):
        with open(ICHANCY_DATA_FILE, 'r', encoding='utf-8') as f:
            ichancy_accounts = json.load(f)
    else:
        ichancy_accounts = {}

def save_ichancy_data():
    with open(ICHANCY_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(ichancy_accounts, f, ensure_ascii=False, indent=2)

# تحميل بيانات ICHANCY
load_ichancy_data()

# ================== دوال التحقق من الاشتراك ==================

def check_subscription(user_id):
    """التحقق من اشتراك المستخدم في القناة المطلوبة"""
    if not REQUIRED_CHANNEL:
        return True
    
    try:
        channel = REQUIRED_CHANNEL
        if channel.startswith('https://t.me/'):
            channel = channel.replace('https://t.me/', '@')
        if not channel.startswith('@'):
            channel = '@' + channel
        
        member = bot.get_chat_member(channel, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

def require_subscription(func):
    """ديكوراتور للتحقق من الاشتراك قبل تنفيذ أي أمر"""
    def wrapper(message):
        user_id = message.from_user.id
        
        if is_admin(user_id):
            return func(message)
        
        if not check_subscription(user_id):
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("📢 اشترك في القناة", url=REQUIRED_CHANNEL))
            keyboard.add(InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_subscription"))
            
            bot.reply_to(
                message,
                f"🔒 <b>عذراً، لا يمكنك استخدام البوت!</b>\n\n"
                f"📢 يجب عليك الاشتراك في قناتنا أولاً:\n"
                f"🔗 {REQUIRED_CHANNEL}\n\n"
                f"✅ بعد الاشتراك، اضغط على زر التحقق.",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            return None
        return func(message)
    return wrapper

# ================== دوال نظام الأكواد ==================

def add_winning_codes(codes_list, total_prize=TOTAL_CODES_PRIZE):
    """إضافة أكواد رابحة وتوزيع الجائزة بالتساوي"""
    if not codes_list:
        return False, "لا توجد أكواد!"
    
    prize_per_code = total_prize // len(codes_list)
    
    for code in codes_list:
        code_upper = code.strip().upper()
        winning_codes[code_upper] = prize_per_code
    
    save_data()
    return True, f"✅ تم إضافة {len(codes_list)} كود رابح\n💰 قيمة كل كود: {prize_per_code:,} ل.س"

def add_losing_codes(codes_list):
    """إضافة أكواد خاسرة"""
    if not codes_list:
        return False, "لا توجد أكواد!"
    
    for code in codes_list:
        code_upper = code.strip().upper()
        if code_upper not in losing_codes and code_upper not in winning_codes:
            losing_codes.append(code_upper)
    
    save_data()
    return True, f"✅ تم إضافة {len(codes_list)} كود خاسر"

def clear_all_codes():
    """مسح جميع الأكواد (رابحة، خاسرة، مستخدمة)"""
    global winning_codes, losing_codes, used_codes
    winning_codes.clear()
    losing_codes.clear()
    used_codes.clear()
    save_data()
    return True, "🗑️ تم مسح جميع الأكواد (رابحة، خاسرة، ومستخدمة)"

def redeem_code(user_id, code):
    """استخدام كود - يعيد (نجاح، رسالة، قيمة الجائزة)"""
    code_upper = code.strip().upper()
    
    # التحقق من أن الكود لم يستخدم من قبل
    if code_upper in used_codes:
        return False, "⚠️ هذا الكود مستخدم من قبل!", 0
    
    # التحقق من الأكواد الرابحة
    if code_upper in winning_codes:
        prize = winning_codes[code_upper]
        used_codes.append(code_upper)
        del winning_codes[code_upper]
        save_data()
        return True, f"🎉 <b>تهانينا!</b>\n💰 لقد ربحت {prize:,} ل.س!", prize
    
    # التحقق من الأكواد الخاسرة
    if code_upper in losing_codes:
        used_codes.append(code_upper)
        losing_codes.remove(code_upper)
        save_data()
        return False, "😢 <b>حظ أوفر!</b>\n💔 هذا الكود لم يفز هذه المرة، جرب كود آخر!", 0
    
    # كود غير موجود
    return False, "❌ <b>كود غير صالح!</b>\n📝 تأكد من كتابة الكود بشكل صحيح.", 0

def get_codes_stats():
    """إحصائيات الأكواد للمدير"""
    return {
        "winning_count": len(winning_codes),
        "losing_count": len(losing_codes),
        "used_count": len(used_codes),
        "total_prize": sum(winning_codes.values())
    }

# ================== تحميل البيانات (معدل) ==================

def load_data():
    global balances, xp, levels, history, BARCODE_FILE_ID, BARCODE_FILE_ID_SYRIATEL, pending_charges, first_charge_done, welcome_gift_received, banned_from_welcome_gift
    global referrals, referral_codes, referral_rewards_claimed, raffle_entries, raffle_participants, VIP_USERS, AUTO_MESSAGE_TEXT, PROMO_PHONE_NUMBER
    global global_win_rate, win_prizes, DEFAULT_RATE, raffle_withdrawn, user_reports_count, first_play_secret_win, GAME_COST, MINIMUM_WITHDRAWAL
    global winning_codes, losing_codes, used_codes
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            balances = data.get('balances', {})
            xp = data.get('xp', {})
            levels = data.get('levels', {})
            history = data.get('history', {})
            BARCODE_FILE_ID = data.get('barcode', None)
            BARCODE_FILE_ID_SYRIATEL = data.get('barcode_syriatel', None)
            pending_charges = data.get('pending_charges', {})
            first_charge_done = data.get('first_charge_done', {})
            welcome_gift_received = data.get('welcome_gift_received', {})
            banned_from_welcome_gift = data.get('banned_from_welcome_gift', [])
            referrals = data.get('referrals', {})
            referral_codes = data.get('referral_codes', {})
            referral_rewards_claimed = data.get('referral_rewards_claimed', {})
            raffle_entries = data.get('raffle_entries', {})
            raffle_participants = data.get('raffle_participants', [])
            VIP_USERS = data.get('vip_users', {})
            AUTO_MESSAGE_TEXT = data.get('auto_message_text', AUTO_MESSAGE_TEXT_DEFAULT)
            PROMO_PHONE_NUMBER = data.get('promo_phone', "09XXXXXXXX")
            global_win_rate = data.get('global_win_rate', 30)
            win_prizes = data.get('win_prizes', {"0": 0, "1": 5000, "2": 5000, "3": 5000, "4": 40000, "5": 40000})
            DEFAULT_RATE = data.get('default_rate', 1)
            raffle_withdrawn = data.get('raffle_withdrawn', {})
            user_reports_count = data.get('user_reports_count', {})
            first_play_secret_win = data.get('first_play_secret_win', {})
            GAME_COST = data.get('game_cost', 2500)
            MINIMUM_WITHDRAWAL = data.get('minimum_withdrawal', 80000)
            winning_codes = data.get('winning_codes', {})
            losing_codes = data.get('losing_codes', [])
            used_codes = data.get('used_codes', [])
    else:
        balances = {}
        xp = {}
        levels = {}
        history = {}
        BARCODE_FILE_ID = None
        BARCODE_FILE_ID_SYRIATEL = None
        pending_charges = {}
        first_charge_done = {}
        welcome_gift_received = {}
        banned_from_welcome_gift = []
        referrals = {}
        referral_codes = {}
        referral_rewards_claimed = {}
        raffle_entries = {}
        raffle_participants = []
        VIP_USERS = {}
        AUTO_MESSAGE_TEXT = AUTO_MESSAGE_TEXT_DEFAULT
        PROMO_PHONE_NUMBER = "09XXXXXXXX"
        global_win_rate = 30
        win_prizes = {"0": 0, "1": 5000, "2": 5000, "3": 5000, "4": 40000, "5": 40000}
        DEFAULT_RATE = 1
        raffle_withdrawn = {}
        user_reports_count = {}
        first_play_secret_win = {}
        GAME_COST = 2500
        MINIMUM_WITHDRAWAL = 80000
        winning_codes = {}
        losing_codes = []
        used_codes = []

def save_data():
    data = {
        'balances': balances,
        'xp': xp,
        'levels': levels,
        'history': history,
        'barcode': BARCODE_FILE_ID,
        'barcode_syriatel': BARCODE_FILE_ID_SYRIATEL,
        'pending_charges': pending_charges,
        'first_charge_done': first_charge_done,
        'welcome_gift_received': welcome_gift_received,
        'banned_from_welcome_gift': banned_from_welcome_gift,
        'referrals': referrals,
        'referral_codes': referral_codes,
        'referral_rewards_claimed': referral_rewards_claimed,
        'raffle_entries': raffle_entries,
        'raffle_participants': raffle_participants,
        'vip_users': VIP_USERS,
        'auto_message_text': AUTO_MESSAGE_TEXT,
        'promo_phone': PROMO_PHONE_NUMBER,
        'global_win_rate': global_win_rate,
        'win_prizes': win_prizes,
        'default_rate': DEFAULT_RATE,
        'raffle_withdrawn': raffle_withdrawn,
        'user_reports_count': user_reports_count,
        'first_play_secret_win': first_play_secret_win,
        'game_cost': GAME_COST,
        'minimum_withdrawal': MINIMUM_WITHDRAWAL,
        'winning_codes': winning_codes,
        'losing_codes': losing_codes,
        'used_codes': used_codes
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================== تحميل البيانات ==================
load_data()

# ================== دوال مساعدة ==================

def is_admin(uid):
    return uid == ADMIN_ID

def is_vip(uid):
    uid_str = str(uid)
    if uid_str not in VIP_USERS:
        return False
    expiry = datetime.strptime(VIP_USERS[uid_str], "%Y-%m-%d")
    if datetime.now() > expiry:
        del VIP_USERS[uid_str]
        save_data()
        return False
    return True

def add_history(uid, action):
    uid_str = str(uid)
    if uid_str not in history:
        history[uid_str] = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history[uid_str].append(f"[{timestamp}] {action}")
    save_data()

def get_balance(uid):
    return balances.get(str(uid), 0)

def add_balance(uid, amount):
    uid_str = str(uid)
    balances[uid_str] = get_balance(uid) + amount
    add_history(uid, f"➕ إضافة رصيد +{amount:,} ل.س")
    save_data()
    check_first_charge(uid)

def sub_balance(uid, amount):
    uid_str = str(uid)
    if get_balance(uid) >= amount:
        balances[uid_str] -= amount
        add_history(uid, f"➖ خصم رصيد -{amount:,} ل.س")
        save_data()
        return True
    return False

def get_xp(uid):
    return xp.get(str(uid), 0)

def get_level(uid):
    return levels.get(str(uid), 1)

def add_xp(uid, amount):
    uid_str = str(uid)
    if is_vip(uid):
        amount = amount * 2
        add_history(uid, f"👑 مضاعف VIP: XP ×2")
    
    old_xp = get_xp(uid)
    new_xp = old_xp + amount
    xp[uid_str] = new_xp
    new_level = new_xp // 100 + 1
    old_level = levels.get(uid_str, 1)
    levels[uid_str] = new_level
    add_history(uid, f"✨ حصل على {amount} XP")
    
    if new_level > old_level:
        add_history(uid, f"🎉 ترقية للمستوى {new_level}!")
    
    save_data()
    return new_level > old_level

def check_first_charge(uid):
    uid_str = str(uid)
    if not first_charge_done.get(uid_str, False):
        first_charge_done[uid_str] = True
        bonus_xp = 50
        add_xp(uid, bonus_xp)
        add_history(uid, f"🎁 هدية أول شحن +{bonus_xp} XP")
        
        for _ in range(5):
            add_raffle_entry(uid)
        add_history(uid, "🎟️ +5 تذاكر إضافية للسحب الكبير (هدية أول شحن)")
        
        save_data()
        return True
    return False

def give_welcome_gift(uid):
    uid_str = str(uid)
    
    if uid in banned_from_welcome_gift:
        add_history(uid, "🚫 محظور من هدية الترحيب")
        return False
    
    if welcome_gift_received.get(uid_str, False):
        return False
    
    welcome_gift_received[uid_str] = True
    add_balance(uid, WELCOME_GIFT)
    add_history(uid, f"🎁 هدية ترحيب +{WELCOME_GIFT:,} ل.س")
    save_data()
    return True

# ================== دوال نظام الفوز ==================

def get_global_win_rate():
    return global_win_rate

def set_global_win_rate(new_rate):
    global global_win_rate
    global_win_rate = new_rate
    save_data()

def get_prize_for_rate(rate):
    return win_prizes.get(str(rate), 5000)

def check_win(uid):
    rate = get_global_win_rate()
    win = random.randint(1, 100) <= rate
    
    if win:
        prize = get_prize_for_rate(rate)
        return True, prize
    return False, 0

# دالة الفوز المخفي (أول مرة بعد الهدية)
def check_and_give_secret_win(uid):
    uid_str = str(uid)
    
    if welcome_gift_received.get(uid_str, False) and not first_play_secret_win.get(uid_str, False):
        first_play_secret_win[uid_str] = True
        add_balance(uid, SECRET_WIN_AMOUNT)
        add_history(uid, f"🎁 فوز مخفي! +{SECRET_WIN_AMOUNT:,} ل.س (أول لعبة بعد الهدية)")
        save_data()
        return True
    return False

# ================== دوال نظام الدعوة ==================

def generate_referral_code(uid):
    uid_str = str(uid)
    if uid_str in referral_codes:
        return referral_codes[uid_str]
    
    code = secrets.token_hex(4).upper()
    referral_codes[uid_str] = code
    save_data()
    return code

def get_referral_code(uid):
    uid_str = str(uid)
    if uid_str not in referral_codes:
        return generate_referral_code(uid)
    return referral_codes[uid_str]

def get_uid_by_referral_code(code):
    for uid_str, ref_code in referral_codes.items():
        if ref_code == code.upper():
            return int(uid_str)
    return None

def add_referral(inviter_uid, invited_uid):
    inviter_str = str(inviter_uid)
    invited_str = str(invited_uid)
    
    if inviter_str not in referrals:
        referrals[inviter_str] = []
    
    if invited_str not in referrals[inviter_str]:
        referrals[inviter_str].append(invited_str)
        save_data()
        return True
    return False

def get_referral_count(uid):
    uid_str = str(uid)
    if uid_str not in referrals:
        return 0
    return len(referrals[uid_str])

def get_referral_list(uid):
    uid_str = str(uid)
    if uid_str not in referrals:
        return []
    return referrals[uid_str]

def check_and_give_referral_reward(uid):
    uid_str = str(uid)
    
    if referral_rewards_claimed.get(uid_str, False):
        return False, "already_claimed"
    
    count = get_referral_count(uid)
    if count >= REQUIRED_REFERRALS:
        add_balance(uid, REFERRAL_REWARD_BALANCE)
        add_xp(uid, REFERRAL_REWARD_XP)
        referral_rewards_claimed[uid_str] = True
        add_raffle_entry(uid)
        add_history(uid, f"🎁 مكافأة الدعوة: +{REFERRAL_REWARD_BALANCE:,} ل.س و +{REFERRAL_REWARD_XP} XP")
        save_data()
        return True, "success"
    
    return False, f"need_{REQUIRED_REFERRALS - count}_more"

def add_raffle_entry(uid):
    uid_str = str(uid)
    if uid_str not in raffle_entries:
        raffle_entries[uid_str] = 0
    raffle_entries[uid_str] += 1
    
    if uid not in raffle_participants:
        raffle_participants.append(uid)
    
    add_history(uid, f"🎟️ تم إدخالك في سحب {RAFFLE_PRIZE:,} ل.س")
    save_data()

def get_raffle_entries_count(uid):
    uid_str = str(uid)
    return raffle_entries.get(uid_str, 0)

# ================== دوال الإبلاغ للمدير ==================

def reset_user_reports_if_needed(uid):
    uid_str = str(uid)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if uid_str not in user_reports_count:
        user_reports_count[uid_str] = {"count": 0, "last_reset": today}
        return True
    
    if user_reports_count[uid_str]["last_reset"] != today:
        user_reports_count[uid_str] = {"count": 0, "last_reset": today}
        return True
    
    return False

def can_user_report(uid):
    uid_str = str(uid)
    reset_user_reports_if_needed(uid)
    
    if uid_str not in user_reports_count:
        return True
    
    return user_reports_count[uid_str]["count"] < MAX_REPORTS_PER_DAY

def add_user_report(uid):
    uid_str = str(uid)
    reset_user_reports_if_needed(uid)
    
    if uid_str not in user_reports_count:
        user_reports_count[uid_str] = {"count": 1, "last_reset": datetime.now().strftime("%Y-%m-%d")}
    else:
        user_reports_count[uid_str]["count"] += 1
    
    save_data()
    return user_reports_count[uid_str]["count"]

def get_remaining_reports(uid):
    uid_str = str(uid)
    reset_user_reports_if_needed(uid)
    
    if uid_str not in user_reports_count:
        return MAX_REPORTS_PER_DAY
    
    used = user_reports_count[uid_str]["count"]
    return max(0, MAX_REPORTS_PER_DAY - used)

# ================== دوال الرسالة التلقائية ==================

def send_auto_message_to_all_users():
    users = list(balances.keys())
    if not users:
        try:
            bot.send_message(ADMIN_ID, "📭 لا يوجد مستخدمين لإرسال الرسالة لهم!")
        except:
            pass
        return
    
    success_count = 0
    fail_count = 0
    
    msg = AUTO_MESSAGE_TEXT.format(phone_number=PROMO_PHONE_NUMBER)
    
    for uid_str in users:
        try:
            bot.send_message(int(uid_str), msg, parse_mode="HTML")
            success_count += 1
            time.sleep(0.05)
        except Exception as e:
            fail_count += 1
    
    try:
        report = f"""
📨 <b>تقرير إرسال الرسالة التلقائية</b>
━━━━━━━━━━━━━━━━
✅ تم الإرسال لـ: {success_count} مستخدم
❌ فشل الإرسال لـ: {fail_count} مستخدم
📞 رقم التحويل: {PROMO_PHONE_NUMBER}
        """
        bot.send_message(ADMIN_ID, report, parse_mode="HTML")
    except:
        pass
    
    print(f"[{datetime.now()}] تم إرسال رسالة لـ {success_count} مستخدم")

# ================== إنشاء الأزرار ==================

def get_main_keyboard(uid):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    balance_display = f"💰 {get_balance(uid):,} ل.س"
    level_display = f"⭐ Lv.{get_level(uid)}"
    
    btn_balance = KeyboardButton(balance_display)
    btn_level = KeyboardButton(level_display)
    btn_games = KeyboardButton("🎮 الألعاب 🎮")
    btn_charge = KeyboardButton("💳 شحن الرصيد 💳")
    btn_referral = KeyboardButton("👥 نظام الدعوة 👥")
    btn_vip = KeyboardButton("👑 VIP 👑")
    btn_history = KeyboardButton("📜 سجل العمليات")
    btn_help = KeyboardButton("❓ المساعدة")
    btn_codes = KeyboardButton("👑 جائزة الأكواد")
    btn_report = KeyboardButton(f"📞 إبلاغ المدير ({get_remaining_reports(uid)}/{MAX_REPORTS_PER_DAY})")
    
    keyboard.row(btn_balance, btn_level)
    keyboard.row(btn_games, btn_charge)
    keyboard.row(btn_referral, btn_vip)
    keyboard.row(btn_history, btn_help)
    keyboard.row(btn_codes)
    keyboard.row(btn_report)
    
    if is_admin(uid):
        btn_users_ids = KeyboardButton("🆔 قائمة IDs")
        btn_admin = KeyboardButton("👑 لوحة المدير")
        keyboard.row(btn_users_ids, btn_admin)
    
    return keyboard

def get_referral_keyboard(uid):
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn_my_code = InlineKeyboardButton("📋 رمز الدعوة الخاص بي", callback_data="my_referral_code")
    btn_my_referrals = InlineKeyboardButton(f"👥 المدعوين ({get_referral_count(uid)})", callback_data="my_referrals")
    btn_claim_reward = InlineKeyboardButton("🎁 استلام المكافأة", callback_data="claim_referral_reward")
    btn_raffle = InlineKeyboardButton("🎟️ السحب الكبير", callback_data="raffle_info")
    btn_how_to = InlineKeyboardButton("❓ كيف يعمل؟", callback_data="how_referral_works")
    keyboard.add(btn_my_code, btn_my_referrals, btn_claim_reward, btn_raffle, btn_how_to)
    return keyboard

def get_games_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_wheel = KeyboardButton(f"🎡 دولاب الحظ ({GAME_COST:,} ل.س)")
    btn_dice = KeyboardButton(f"🎲 لعبة النرد ({GAME_COST:,} ل.س)")
    btn_slots = KeyboardButton(f"🎰 سلوت الفواكه ({GAME_COST:,} ل.س)")
    btn_back = KeyboardButton("🔙 رجوع للقائمة")
    keyboard.add(btn_wheel, btn_dice, btn_slots)
    keyboard.add(btn_back)
    return keyboard

def get_admin_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_barcode = InlineKeyboardButton("📸 تعيين باركود شام كاش", callback_data="set_barcode")
    btn_barcode_syriatel = InlineKeyboardButton("📸 تعيين باركود سيرياتيل", callback_data="set_barcode_syriatel")
    btn_stats = InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")
    btn_users_ids = InlineKeyboardButton("🆔 قائمة IDs", callback_data="users_ids")
    btn_gift_list = InlineKeyboardButton("🎁 قائمة المحظورين", callback_data="gift_list")
    btn_backup = InlineKeyboardButton("💾 نسخ احتياطي", callback_data="backup")
    btn_restore = InlineKeyboardButton("📂 استعادة نسخة", callback_data="restore_info")
    btn_raffle_draw = InlineKeyboardButton("🎰 إجراء السحب", callback_data="raffle_draw")
    
    # أزرار الرسائل
    btn_send_message = InlineKeyboardButton("📨 إرسال رسالة للجميع", callback_data="send_auto_message")
    btn_edit_message = InlineKeyboardButton("✏️ تعديل الرسالة", callback_data="edit_auto_message")
    btn_set_phone = InlineKeyboardButton("📞 تعيين رقم التحويل", callback_data="set_phone_number")
    
    # أزرار التحكم بالفوز
    btn_set_rate = InlineKeyboardButton("📊 تعيين نسبة الفوز (شامل)", callback_data="set_global_rate")
    btn_show_rate = InlineKeyboardButton("📋 عرض نسبة الفوز الحالية", callback_data="show_global_rate")
    
    # أزرار إدارة المستخدمين
    btn_all_balances = InlineKeyboardButton("💰 معرفة رصيد جميع المستخدمين", callback_data="all_users_balances")
    btn_reset_user = InlineKeyboardButton("🔄 تصفير رصيد مستخدم واحد", callback_data="reset_single_balance")
    btn_reset_users = InlineKeyboardButton("🔄 تصفير رصيد مجموعة", callback_data="reset_multiple_balances")
    
    # أزرار إدارة الأكواد الجديدة
    btn_upload_winning = InlineKeyboardButton("🏆 تحميل أكواد رابحة", callback_data="upload_winning_codes")
    btn_upload_losing = InlineKeyboardButton("💔 تحميل أكواد خاسرة", callback_data="upload_losing_codes")
    btn_clear_codes = InlineKeyboardButton("🗑️ مسح جميع الأكواد", callback_data="clear_all_codes")
    btn_codes_stats = InlineKeyboardButton("📊 إحصائيات الأكواد", callback_data="codes_stats")
    
    # أزرار إضافية
    btn_distribute = InlineKeyboardButton("💰 توزيع مبلغ", callback_data="distribute_money")
    btn_send_to_id = InlineKeyboardButton("📨 إرسال رسالة لـ ID", callback_data="send_to_id")
    btn_send_photo_to_id = InlineKeyboardButton("🖼️ إرسال صورة لـ ID", callback_data="send_photo_to_id")
    btn_get_balance = InlineKeyboardButton("💰 معرفة رصيد مستخدم", callback_data="get_balance_user")
    
    keyboard.add(btn_barcode, btn_barcode_syriatel)
    keyboard.add(btn_stats)
    keyboard.add(btn_users_ids, btn_gift_list)
    keyboard.add(btn_backup, btn_restore)
    keyboard.add(btn_raffle_draw)
    keyboard.add(btn_send_message, btn_edit_message)
    keyboard.add(btn_set_phone)
    keyboard.add(btn_set_rate, btn_show_rate)
    keyboard.add(btn_all_balances)
    keyboard.add(btn_reset_user, btn_reset_users)
    keyboard.add(btn_upload_winning, btn_upload_losing)
    keyboard.add(btn_clear_codes, btn_codes_stats)
    keyboard.add(btn_distribute)
    keyboard.add(btn_send_to_id, btn_send_photo_to_id)
    keyboard.add(btn_get_balance)
    
    return keyboard

# ================== زر جائزة الأكواد ==================

@bot.message_handler(func=lambda message: message.text == "👑 جائزة الأكواد")
@require_subscription
def codes_prize_menu(message):
    uid = message.from_user.id
    
    msg = """
👑 <b>نظام جائزة الأكواد</b>
━━━━━━━━━━━━━━━━

📝 <b>كيفية الاستخدام:</b>
1️⃣ احصل على كود من المسابقات أو العروض
2️⃣ أرسل الكود في رسالة منفردة
3️⃣ احصل على جائزتك فوراً!

━━━━━━━━━━━━━━━━
💰 <b>جوائز تصل إلى 6,000 ل.س للكود الواحد!</b>

📌 <b>أرسل الكود الآن:</b>
    """
    
    bot.reply_to(message, msg, parse_mode="HTML")
    bot.register_next_step_handler(message, process_code_redemption)

def process_code_redemption(message):
    uid = message.from_user.id
    code = message.text.strip()
    
    success, msg, prize = redeem_code(uid, code)
    
    if success:
        add_balance(uid, prize)
        bot.reply_to(message, msg, parse_mode="HTML")
    else:
        bot.reply_to(message, msg, parse_mode="HTML")

# ================== كولبك التحقق من الاشتراك ==================

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription_callback(call):
    uid = call.from_user.id
    
    if check_subscription(uid):
        bot.edit_message_text(
            f"✅ <b>تم التحقق بنجاح!</b>\n\n🎉 مرحباً بك في البوت!",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id, "✅ تم التحقق!", show_alert=True)
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📢 اشترك في القناة", url=REQUIRED_CHANNEL))
        keyboard.add(InlineKeyboardButton("🔄 تحقق مرة أخرى", callback_data="check_subscription"))
        
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboard)

# ================== الأوامر الرئيسية ==================

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not check_subscription(uid) and not is_admin(uid):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📢 اشترك في القناة", url=REQUIRED_CHANNEL))
        keyboard.add(InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_subscription"))
        
        bot.reply_to(
            message,
            f"🔒 <b>عذراً، لا يمكنك استخدام البوت!</b>\n\n"
            f"📢 يجب عليك الاشتراك في قناتنا أولاً:\n"
            f"🔗 {REQUIRED_CHANNEL}\n\n"
            f"✅ بعد الاشتراك، اضغط على زر التحقق.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return
    
    uid_str = str(uid)
    
    is_new_user = False
    
    if uid_str not in balances:
        balances[uid_str] = 0
        xp[uid_str] = 0
        levels[uid_str] = 1
        history[uid_str] = []
        first_charge_done[uid_str] = False
        welcome_gift_received[uid_str] = False
        save_data()
        is_new_user = True
        add_history(uid, "🚀 بدأ استخدام البوت")
    
    referral_msg = ""
    args = message.text.split()
    if len(args) > 1:
        ref_code = args[1].upper()
        inviter_uid = get_uid_by_referral_code(ref_code)
        if inviter_uid and inviter_uid != uid:
            if add_referral(inviter_uid, uid):
                add_history(inviter_uid, f"👤 قام بدعوة مستخدم جديد ({uid})")
                referral_msg = f"\n🎉 <b>تم تسجيلك عن طريق دعوة!</b>\n👤 المستخدم الذي دعاك حصل على نقاط!"
                
                try:
                    bot.send_message(inviter_uid, f"🎉 <b>تهانينا!</b>\n👤 قام شخص جديد بالانضمام باستخدام رمز الدعوة الخاص بك!\n📊 عدد المدعوين الآن: {get_referral_count(inviter_uid)}")
                    
                    rewarded, status = check_and_give_referral_reward(inviter_uid)
                    if rewarded:
                        bot.send_message(inviter_uid, f"🎁 <b>مبروك! لقد حصلت على مكافأة الدعوة!</b>\n💰 +{REFERRAL_REWARD_BALANCE:,} ل.س\n✨ +{REFERRAL_REWARD_XP} XP\n🎟️ + دخول في سحب {RAFFLE_PRIZE:,} ل.س")
                except:
                    pass
    
    gift_msg = ""
    if is_new_user:
        if give_welcome_gift(uid):
            gift_msg = f"\n🎁 <b>هدية الترحيب: +{WELCOME_GIFT:,} ل.س</b> 🎁"
    
    welcome_msg = f"""
✨ <b>مرحباً بك {message.from_user.first_name}!</b> ✨

🎮 <b>البوت الاحترافي</b>
━━━━━━━━━━━━━━━━
💰 <b>رصيدك الحالي:</b> {get_balance(uid):,} ل.س
⭐ <b>مستواك:</b> {get_level(uid)}
✨ <b>نقاط XP:</b> {get_xp(uid)}
{gift_msg}
{referral_msg}
━━━━━━━━━━━━━━━━
📌 <b>مميزات البوت:</b>
• 🎡 ألعاب متنوعة (ثمن اللعبة: {GAME_COST:,} ل.س)
• 💳 شحن رصيد آمن (الحد الأدنى للسحب: {MINIMUM_WITHDRAWAL:,} ل.س)
• 👥 نظام الدعوة والأصدقاء
• 👑 نظام VIP بمزايا حصرية

استخدم الأزرار أدناه للبدء 🚀
    """
    
    # إضافة زر ICHANCY إلى الكيبورد (بدون تعديل الدالة الأصلية)
    keyboard = get_main_keyboard(uid)
    keyboard.row(KeyboardButton("👑 ICHANCY 👑"))
    
    bot.reply_to(message, welcome_msg, reply_markup=keyboard)

# ================== باقي الكود الأصلي ==================

@bot.message_handler(func=lambda message: message.text == "👥 نظام الدعوة 👥")
def show_referral_system(message):
    uid = message.from_user.id
    
    code = get_referral_code(uid)
    count = get_referral_count(uid)
    
    bot_username = bot.get_me().username
    bot_link = f"https://t.me/{bot_username}?start={code}"
    
    remaining = max(0, REQUIRED_REFERRALS - count)
    progress = min(count, REQUIRED_REFERRALS)
    progress_bar = "█" * progress + "░" * (REQUIRED_REFERRALS - progress)
    
    claimed = referral_rewards_claimed.get(str(uid), False)
    reward_status = "✅ تم الاستلام" if claimed else "⏳ في الانتظار"
    
    raffle_tickets = get_raffle_entries_count(uid)
    
    msg = f"""
👥 <b>نظام الدعوة والأصدقاء</b>
━━━━━━━━━━━━━━━━

📋 <b>رمز الدعوة الخاص بك:</b>
<code>{code}</code>

🔗 <b>رابط الدعوة:</b>
<code>{bot_link}</code>

💡 <b>طريقة الاستخدام:</b>
انسخ الرابط وأرسله لأصدقائك، عندما ينضمون عبر رابطك سيتم احتسابهم كمدعوين.

━━━━━━━━━━━━━━━━
📊 <b>إحصائياتك:</b>
👤 المدعوين: {count} / {REQUIRED_REFERRALS}
[{progress_bar}]

🎁 <b>المكافأة:</b>
💰 +{REFERRAL_REWARD_BALANCE:,} ل.س
✨ +{REFERRAL_REWARD_XP} XP
🎟️ دخول سحب {RAFFLE_PRIZE:,} ل.س

📌 <b>حالة المكافأة:</b> {reward_status}
🎟️ <b>بطاقات السحب:</b> {raffle_tickets}
━━━━━━━━━━━━━━━━
📌 <b>ملاحظة:</b> المكافأة تُمنح تلقائياً عند اكتمال {REQUIRED_REFERRALS} دعوات ناجحة.
    """
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn_copy = InlineKeyboardButton("📋 نسخ الرابط", callback_data=f"copy_link_{code}")
    btn_my_referrals = InlineKeyboardButton(f"👥 المدعوين ({count})", callback_data="my_referrals")
    btn_raffle = InlineKeyboardButton("🎟️ السحب الكبير", callback_data="raffle_info")
    btn_how_to = InlineKeyboardButton("❓ كيف يعمل؟", callback_data="how_referral_works")
    keyboard.add(btn_copy, btn_my_referrals, btn_raffle, btn_how_to)
    
    bot.reply_to(message, msg, reply_markup=keyboard, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_link_"))
def copy_link_callback(call):
    code = call.data.split("_")[2]
    bot_username = bot.get_me().username
    bot_link = f"https://t.me/{bot_username}?start={code}"
    
    bot.send_message(call.message.chat.id, f"🔗 <b>رابط دعوتك:</b>\n<code>{bot_link}</code>\n\n📋 اضغط مع الاستمرار على الرابط ثم اختر نسخ", parse_mode="HTML")
    bot.answer_callback_query(call.id, "✅ تم إرسال الرابط", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "my_referrals")
def show_my_referrals(call):
    uid = call.from_user.id
    refs = get_referral_list(uid)
    count = len(refs)
    
    if count == 0:
        msg = "📭 لم تقم بدعوة أي شخص بعد.\n💡 شارك رابط الدعوة مع أصدقائك!"
    else:
        msg = f"""
👥 <b>قائمة المدعوين ({count})</b>
━━━━━━━━━━━━━━━━
"""
        for i, ref_id in enumerate(refs[-20:], 1):
            msg += f"{i}. <code>{ref_id}</code>\n"
        
        if count > 20:
            msg += f"\n... و {count - 20} آخرين"
    
    bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "claim_referral_reward")
def claim_referral_reward_callback(call):
    uid = call.from_user.id
    uid_str = str(uid)
    
    count = get_referral_count(uid)
    
    if referral_rewards_claimed.get(uid_str, False):
        bot.answer_callback_query(call.id, "⚠️ لقد استلمت المكافأة مسبقاً!", show_alert=True)
        return
    
    if count < REQUIRED_REFERRALS:
        remaining = REQUIRED_REFERRALS - count
        bot.answer_callback_query(call.id, f"⚠️ تحتاج إلى {remaining} دعوات إضافية!", show_alert=True)
        return
    
    rewarded, status = check_and_give_referral_reward(uid)
    
    if rewarded:
        msg = f"""
🎉 <b>تهانينا! تم استلام المكافأة!</b>
━━━━━━━━━━━━━━━━
💰 +{REFERRAL_REWARD_BALANCE:,} ل.س
✨ +{REFERRAL_REWARD_XP} XP
🎟️ + دخول في سحب {RAFFLE_PRIZE:,} ل.س

━━━━━━━━━━━━━━━━
💰 رصيدك الحالي: {get_balance(uid):,} ل.س
⭐ مستواك: {get_level(uid)}
🎟️ بطاقات السحب: {get_raffle_entries_count(uid)}
        """
        bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
        bot.answer_callback_query(call.id, "✅ تم استلام المكافأة بنجاح!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ حدث خطأ، حاول مرة أخرى", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "raffle_info")
def show_raffle_info(call):
    uid = call.from_user.id
    
    tickets = get_raffle_entries_count(uid)
    total_participants = len(raffle_participants)
    total_entries = sum(raffle_entries.values())
    
    msg = f"""
🎰 <b>السحب الكبير</b>
━━━━━━━━━━━━━━━━
💰 <b>قيمة الجائزة:</b> {RAFFLE_PRIZE:,} ل.س

📊 <b>إحصائيات السحب:</b>
👥 عدد المشاركين: {total_participants}
🎟️ إجمالي البطاقات: {total_entries}
🎟️ <b>بطاقاتك:</b> {tickets}

━━━━━━━━━━━━━━━━
📌 <b>كيف تدخل السحب؟</b>
• أكمل دعوة {REQUIRED_REFERRALS} أشخاص
• اشترك في VIP لتحصل على 5 تذاكر فورية
• أول شحن يمنحك 5 تذاكر إضافية

🍀 كلما زادت بطاقاتك، زادت فرصتك!
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_referral"))
    
    bot.send_message(call.message.chat.id, msg, reply_markup=keyboard, parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "how_referral_works")
def how_referral_works(call):
    msg = f"""
❓ <b>كيف يعمل نظام الدعوة؟</b>
━━━━━━━━━━━━━━━━

1️⃣ <b>احصل على رابط الدعوة</b>
   اضغط على "📋 نسخ الرابط" في قائمة الدعوة

2️⃣ <b>شارك الرابط</b>
   أرسل الرابط لأصدقائك على تيليجرام أو واتساب

3️⃣ <b>انضمام الأصدقاء</b>
   عندما ينضم صديق عبر رابطك، يتم تسجيله تلقائياً

4️⃣ <b>اكسب المكافأة</b>
   بعد {REQUIRED_REFERRALS} دعوات ناجحة:
   💰 {REFERRAL_REWARD_BALANCE:,} ل.س
   ✨ {REFERRAL_REWARD_XP} XP
   🎟️ دخول سحب {RAFFLE_PRIZE:,} ل.س

━━━━━━━━━━━━━━━━
💡 <b>نصيحة:</b> كلما زاد عدد المدعوين، زادت فرصك في السحب الكبير!
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_referral"))
    
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_referral")
def back_to_referral(call):
    uid = call.from_user.id
    code = get_referral_code(uid)
    count = get_referral_count(uid)
    bot_username = bot.get_me().username
    bot_link = f"https://t.me/{bot_username}?start={code}"
    
    remaining = max(0, REQUIRED_REFERRALS - count)
    progress = min(count, REQUIRED_REFERRALS)
    progress_bar = "█" * progress + "░" * (REQUIRED_REFERRALS - progress)
    
    claimed = referral_rewards_claimed.get(str(uid), False)
    reward_status = "✅ تم الاستلام" if claimed else "⏳ في الانتظار"
    
    raffle_tickets = get_raffle_entries_count(uid)
    
    msg = f"""
👥 <b>نظام الدعوة والأصدقاء</b>
━━━━━━━━━━━━━━━━

📋 <b>رمز الدعوة الخاص بك:</b>
<code>{code}</code>

🔗 <b>رابط الدعوة:</b>
<code>{bot_link}</code>

━━━━━━━━━━━━━━━━
📊 <b>إحصائياتك:</b>
👤 المدعوين: {count} / {REQUIRED_REFERRALS}
[{progress_bar}]

🎁 <b>المكافأة:</b>
💰 +{REFERRAL_REWARD_BALANCE:,} ل.س
✨ +{REFERRAL_REWARD_XP} XP
🎟️ دخول سحب {RAFFLE_PRIZE:,} ل.س

📌 <b>حالة المكافأة:</b> {reward_status}
🎟️ <b>بطاقات السحب:</b> {raffle_tickets}
    """
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn_copy = InlineKeyboardButton("📋 نسخ الرابط", callback_data=f"copy_link_{code}")
    btn_my_referrals = InlineKeyboardButton(f"👥 المدعوين ({count})", callback_data="my_referrals")
    btn_raffle = InlineKeyboardButton("🎟️ السحب الكبير", callback_data="raffle_info")
    btn_how_to = InlineKeyboardButton("❓ كيف يعمل؟", callback_data="how_referral_works")
    keyboard.add(btn_copy, btn_my_referrals, btn_raffle, btn_how_to)
    
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode="HTML")
    bot.answer_callback_query(call.id)

# ================== نظام الشحن ==================

@bot.message_handler(func=lambda message: message.text == "💳 شحن الرصيد 💳")
def charge_start(message):
    uid = message.from_user.id
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📱 شام كاش", callback_data="charge_sham"),
        InlineKeyboardButton("📱 سيرياتيل كاش", callback_data="charge_syriatel"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    )
    
    msg = """
💳 <b>شحن الرصيد</b>

اختر طريقة الدفع المناسبة لك:

📱 <b>شام كاش</b>
📱 <b>سيرياتيل كاش</b>

━━━━━━━━━━━━━━━━
💰 الحد الأدنى: 1,000 ل.س
💰 الحد الأقصى: 100,000 ل.س
🎁 أول شحن: 50 XP + 5 تذاكر سحب!
    """
    bot.reply_to(message, msg, reply_markup=keyboard, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "charge_sham")
def charge_sham_callback(call):
    uid = call.from_user.id
    
    if BARCODE_FILE_ID is None:
        bot.answer_callback_query(call.id, "❌ عذراً، خدمة شام كاش غير متاحة حالياً.", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    amounts = [1000, 5000, 10000, 25000, 50000, 100000]
    for amount in amounts:
        keyboard.add(InlineKeyboardButton(f"{amount:,} ل.س", callback_data=f"charge_sham_{amount}"))
    keyboard.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_charge"))
    
    bot.edit_message_text(
        f"💳 <b>شحن الرصيد - شام كاش</b>\n\nاختر المبلغ الذي تريد شحنه:\n\n🎁 أول شحن: 50 XP + 5 تذاكر سحب!",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "charge_syriatel")
def charge_syriatel_callback(call):
    uid = call.from_user.id
    
    if BARCODE_FILE_ID_SYRIATEL is None:
        bot.answer_callback_query(call.id, "❌ عذراً، خدمة سيرياتيل كاش غير متاحة حالياً.", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    amounts = [1000, 5000, 10000, 25000, 50000, 100000]
    for amount in amounts:
        keyboard.add(InlineKeyboardButton(f"{amount:,} ل.س", callback_data=f"charge_syriatel_{amount}"))
    keyboard.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_charge"))
    
    bot.edit_message_text(
        f"💳 <b>شحن الرصيد - سيرياتيل كاش</b>\n\nاختر المبلغ الذي تريد شحنه:\n\n🎁 أول شحن: 50 XP + 5 تذاكر سحب!",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("charge_sham_"))
def handle_sham_charge(call):
    uid = call.from_user.id
    amount = int(call.data.split("_")[2])
    
    charge_id = f"{uid}_{int(time.time())}"
    pending_charges[charge_id] = {
        'uid': uid,
        'amount': amount,
        'type': 'sham',
        'status': 'pending',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_data()
    
    bot.send_photo(
        call.message.chat.id,
        BARCODE_FILE_ID,
        caption=f"""
💳 <b>طلب شحن الرصيد - شام كاش</b>
━━━━━━━━━━━━━━━━
💰 المبلغ: {amount:,} ل.س
🆔 رقم الطلب: {charge_id}

📝 <b>تعليمات الدفع:</b>
1️⃣ ادفع المبلغ عبر شام كاش
2️⃣ اضغط "📞 إبلاغ المدير"
3️⃣ أرسل رقمك والمبلغ

🎁 <b>ستحصل على جائزة 5,000 ل.س إضافية!</b>
        """,
        parse_mode="HTML"
    )
    
    admin_keyboard = InlineKeyboardMarkup(row_width=2)
    admin_keyboard.add(
        InlineKeyboardButton("✅ موافقة", callback_data=f"approve_charge_{uid}_{amount}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"reject_charge_{uid}_{amount}")
    )
    
    admin_msg = f"""
🔔 <b>طلب شحن جديد - شام كاش!</b>
━━━━━━━━━━━━━━━━
👤 المستخدم: {uid}
👤 الاسم: {call.from_user.first_name}
📱 اليوزر: @{call.from_user.username or 'لا يوجد'}
💰 المبلغ: {amount:,} ل.س
🆔 رقم الطلب: {charge_id}
⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━
📌 <a href="tg://user?id={uid}">اضغط للرد عليه</a>
    """
    
    bot.send_message(ADMIN_ID, admin_msg, reply_markup=admin_keyboard, parse_mode="HTML")
    
    bot.answer_callback_query(call.id, "✅ تم إرسال تعليمات الدفع", show_alert=True)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

@bot.callback_query_handler(func=lambda call: call.data.startswith("charge_syriatel_"))
def handle_syriatel_charge(call):
    uid = call.from_user.id
    amount = int(call.data.split("_")[2])
    
    charge_id = f"{uid}_{int(time.time())}"
    pending_charges[charge_id] = {
        'uid': uid,
        'amount': amount,
        'type': 'syriatel',
        'status': 'pending',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_data()
    
    bot.send_photo(
        call.message.chat.id,
        BARCODE_FILE_ID_SYRIATEL,
        caption=f"""
💳 <b>طلب شحن الرصيد - سيرياتيل كاش</b>
━━━━━━━━━━━━━━━━
💰 المبلغ: {amount:,} ل.س
🆔 رقم الطلب: {charge_id}

📝 <b>تعليمات الدفع:</b>
1️⃣ ادفع المبلغ عبر سيرياتيل كاش
2️⃣ اضغط "📞 إبلاغ المدير"
3️⃣ أرسل رقمك والمبلغ

🎁 <b>ستحصل على جائزة 5,000 ل.س إضافية!</b>
        """,
        parse_mode="HTML"
    )
    
    admin_keyboard = InlineKeyboardMarkup(row_width=2)
    admin_keyboard.add(
        InlineKeyboardButton("✅ موافقة", callback_data=f"approve_charge_{uid}_{amount}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"reject_charge_{uid}_{amount}")
    )
    
    admin_msg = f"""
🔔 <b>طلب شحن جديد - سيرياتيل كاش!</b>
━━━━━━━━━━━━━━━━
👤 المستخدم: {uid}
👤 الاسم: {call.from_user.first_name}
📱 اليوزر: @{call.from_user.username or 'لا يوجد'}
💰 المبلغ: {amount:,} ل.س
🆔 رقم الطلب: {charge_id}
⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━
📌 <a href="tg://user?id={uid}">اضغط للرد عليه</a>
    """
    
    bot.send_message(ADMIN_ID, admin_msg, reply_markup=admin_keyboard, parse_mode="HTML")
    
    bot.answer_callback_query(call.id, "✅ تم إرسال تعليمات الدفع", show_alert=True)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_charge_"))
def approve_charge(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    parts = call.data.split("_")
    uid = int(parts[2])
    amount = int(parts[3])
    
    add_balance(uid, amount)
    
    try:
        bot.send_message(uid, f"""
✅ <b>تم قبول طلب الشحن!</b>
━━━━━━━━━━━━━━━━
💰 المبلغ: {amount:,} ل.س
💳 رصيدك الحالي: {get_balance(uid):,} ل.س

شكراً لثقتك بنا! 🎉
        """, parse_mode="HTML")
    except:
        pass
    
    add_history(uid, f"✅ تم قبول طلب الشحن {amount:,} ل.س")
    
    bot.edit_message_text(
        f"✅ <b>تمت الموافقة على الشحن</b>\n━━━━━━━━━━━━━━━━\n👤 المستخدم: {uid}\n💰 المبلغ: {amount:,} ل.س\n✅ الحالة: تم الشحن بنجاح",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )
    
    bot.answer_callback_query(call.id, f"✅ تم شحن {amount:,} ل.س للمستخدم {uid}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_charge_"))
def reject_charge(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    parts = call.data.split("_")
    uid = int(parts[2])
    amount = int(parts[3])
    
    try:
        bot.send_message(uid, f"""
❌ <b>تم رفض طلب الشحن!</b>
━━━━━━━━━━━━━━━━
💰 المبلغ: {amount:,} ل.س

للأسف، لم يتم قبول طلبك. يرجى التأكد من:
• صحة رقم الهاتف
• إرسال المبلغ الصحيح

للتواصل مع الدعم: اضغط "📞 إبلاغ المدير"
        """, parse_mode="HTML")
    except:
        pass
    
    add_history(uid, f"❌ تم رفض طلب الشحن {amount:,} ل.س")
    
    bot.edit_message_text(
        f"❌ <b>تم رفض الشحن</b>\n━━━━━━━━━━━━━━━━\n👤 المستخدم: {uid}\n💰 المبلغ: {amount:,} ل.س\n❌ الحالة: مرفوض",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )
    
    bot.answer_callback_query(call.id, f"❌ تم رفض شحن {amount:,} ل.س للمستخدم {uid}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_charge")
def back_to_charge(call):
    charge_start(call.message)
    bot.answer_callback_query(call.id)

# ================== نظام VIP ==================

@bot.message_handler(func=lambda message: message.text == "👑 VIP 👑")
def vip_menu(message):
    uid = message.from_user.id
    
    if is_vip(uid):
        expiry = VIP_USERS[str(uid)]
        msg = f"""
👑 <b>حالة عضويتك VIP</b>
━━━━━━━━━━━━━━━━
✅ <b>أنت عضو VIP نشط!</b>
📅 تاريخ الانتهاء: {expiry}

🎁 <b>مزاياك الحالية:</b>
• ✨ XP مضاعف في جميع الألعاب
• 🎟️ أولوية في السحوبات
• 💰 خصم 50% على ثمن الألعاب
━━━━━━━━━━━━━━━━
        """
        bot.reply_to(message, msg, parse_mode="HTML")
        return
    
    msg = f"""
👑 <b>نظام VIP الحصري</b>
━━━━━━━━━━━━━━━━
🎁 <b>مزايا العضوية الذهبية:</b>
• ✨ <b>XP مضاعف</b> - تتطور أسرع بمرتين
• 🎟️ <b>5 تذاكر إضافية</b> للسحب الكبير فور الاشتراك
• 💰 خصم 50% على ثمن الألعاب
• ⭐ وسام VIP خاص

💰 <b>سعر الاشتراك الشهري:</b> {VIP_COST:,} ل.س
━━━━━━━━━━━━━━━━
هل تريد الاشتراك الآن؟
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(f"✅ اشترك الآن - {VIP_COST:,} ل.س", callback_data="buy_vip"))
    keyboard.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main"))
    
    bot.reply_to(message, msg, reply_markup=keyboard, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "buy_vip")
def buy_vip_callback(call):
    uid = call.from_user.id
    uid_str = str(uid)
    
    if is_vip(uid):
        bot.answer_callback_query(call.id, "✅ أنت مشترك VIP بالفعل!", show_alert=True)
        return
    
    if get_balance(uid) < VIP_COST:
        bot.answer_callback_query(call.id, f"❌ رصيدك غير كافٍ. تحتاج {VIP_COST:,} ل.س", show_alert=True)
        return
    
    sub_balance(uid, VIP_COST)
    VIP_USERS[uid_str] = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    save_data()
    
    for _ in range(5):
        add_raffle_entry(uid)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    success_msg = f"""
🎉 <b>مبروك! أنت الآن عضو VIP لمدة 30 يوم!</b>
━━━━━━━━━━━━━━━━
✨ ستحصل على XP مضاعف في جميع الألعاب
🎫 تمت إضافة <b>5 تذاكر</b> إضافية لحسابك في السحب الكبير
💰 رصيدك المتبقي: {get_balance(uid):,} ل.س
━━━━━━━━━━━━━━━━
استمتع بمزاياك الحصرية! 👑
    """
    
    bot.send_message(call.message.chat.id, success_msg, parse_mode="HTML")
    add_history(uid, f"👑 اشترك في VIP لمدة 30 يوم")
    bot.answer_callback_query(call.id, "✅ تم الاشتراك بنجاح!", show_alert=True)

# ================== الألعاب ==================

@bot.message_handler(func=lambda message: message.text == "🎮 الألعاب 🎮")
def show_games(message):
    uid = message.from_user.id
    cost = GAME_COST // 2 if is_vip(uid) else GAME_COST
    
    games_msg = f"""
🎮 <b>قائمة الألعاب المتاحة:</b>

🎡 <b>دولاب الحظ</b>
└ ثمن اللعبة: {cost:,} ل.س {'(خصم VIP 50%)' if is_vip(uid) else ''}
└ جائزة: تصل إلى 50,000 ل.س
└ XP: +25 (فوز) / +5 (خسارة)

🎲 <b>لعبة النرد</b>
└ ثمن اللعبة: {cost:,} ل.س {'(خصم VIP 50%)' if is_vip(uid) else ''}
└ جائزة: تصل إلى 50,000 ل.س
└ XP: +20 (فوز) / +5 (خسارة)

🎰 <b>سلوت الفواكه</b>
└ ثمن اللعبة: {cost:,} ل.س {'(خصم VIP 50%)' if is_vip(uid) else ''}
└ جائزة: تصل إلى 50,000 ل.س
└ XP: +30 (فوز) / +5 (خسارة)

━━━━━━━━━━━━━━━━
💰 رصيدك الحالي: {get_balance(message.from_user.id):,} ل.س
🎯 اختر اللعبة وابدأ اللعب!
    """
    bot.reply_to(message, games_msg, reply_markup=get_games_keyboard(), parse_mode="HTML")

def play_game(message, game_name, xp_amount, result_msg_func):
    uid = message.from_user.id
    cost = GAME_COST // 2 if is_vip(uid) else GAME_COST
    
    if get_balance(uid) < cost:
        bot.reply_to(message, f"❌ رصيدك غير كافٍ!\n💰 رصيدك: {get_balance(uid):,} ل.س\n💸 ثمن اللعبة: {cost:,} ل.س", reply_markup=get_games_keyboard())
        return
    
    sub_balance(uid, cost)
    
    # التحقق من الفوز المخفي (أول لعبة بعد الهدية)
    check_and_give_secret_win(uid)
    
    win, prize = check_win(uid)
    
    if win:
        add_balance(uid, prize)
        leveled_up = add_xp(uid, xp_amount)
        
        result_msg = result_msg_func(True, prize, cost, xp_amount, leveled_up, uid)
        bot.send_message(message.chat.id, result_msg, reply_markup=get_games_keyboard(), parse_mode="HTML")
    else:
        add_xp(uid, 5)
        
        result_msg = result_msg_func(False, 0, cost, 5, False, uid)
        bot.send_message(message.chat.id, result_msg, reply_markup=get_games_keyboard(), parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text in [f"🎡 دولاب الحظ ({GAME_COST:,} ل.س)", f"🎡 دولاب الحظ ({GAME_COST//2:,} ل.س)"])
def wheel_game(message):
    def wheel_result(win, prize, cost, xp, leveled_up, uid):
        if win:
            result = f"""
🎉 <b>🎉 مبارك! لقد ربحت! 🎉</b>

🎡 <b>دولاب الحظ</b>
━━━━━━━━━━━━━━━━
💸 ثمن اللعبة: {cost:,} ل.س
💰 <b>الجائزة:</b> {prize:,} ل.س
✨ XP: +{xp * 2 if is_vip(uid) else xp} {'(VIP ×2)' if is_vip(uid) else ''}
⭐ مستوى: {get_level(uid)}

━━━━━━━━━━━━━━━━
💰 رصيدك الآن: {get_balance(uid):,} ل.س
"""
            if leveled_up:
                result += f"\n🎉 <b>تهانينا! لقد وصلت للمستوى {get_level(uid)}!</b> 🎉"
            return result
        else:
            return f"""
😔 <b>للأسف، لم تربح هذه المرة</b>

🎡 <b>دولاب الحظ</b>
━━━━━━━━━━━━━━━━
💸 ثمن اللعبة: {cost:,} ل.س
💔 الحظ عاندك هذه المرة
✨ XP: +{xp * 2 if is_vip(uid) else xp} {'(VIP ×2)' if is_vip(uid) else ''}

━━━━━━━━━━━━━━━━
💰 رصيدك: {get_balance(uid):,} ل.س
💪 جرب حظك مرة أخرى!
"""
    play_game(message, "wheel", 25, wheel_result)

@bot.message_handler(func=lambda message: message.text in [f"🎲 لعبة النرد ({GAME_COST:,} ل.س)", f"🎲 لعبة النرد ({GAME_COST//2:,} ل.س)"])
def dice_game(message):
    def dice_result(win, prize, cost, xp, leveled_up, uid):
        if win:
            d1 = d2 = random.randint(1, 6)
            result = f"""
🎉 <b>🎉 فوز! ستة محظوظة! 🎉</b>

🎲 <b>لعبة النرد</b>
━━━━━━━━━━━━━━━━
💸 ثمن اللعبة: {cost:,} ل.س
🎲 النتيجة: {d1} | {d2}
🎯 Double!
💰 الجائزة: {prize:,} ل.س
✨ XP: +{xp * 2 if is_vip(uid) else xp} {'(VIP ×2)' if is_vip(uid) else ''}
⭐ مستوى: {get_level(uid)}

━━━━━━━━━━━━━━━━
💰 رصيدك الآن: {get_balance(uid):,} ل.س
"""
            if leveled_up:
                result += f"\n🎉 <b>تهانينا! لقد وصلت للمستوى {get_level(uid)}!</b> 🎉"
            return result
        else:
            d1 = random.randint(1, 6)
            d2 = random.randint(1, 6)
            while d1 == d2:
                d2 = random.randint(1, 6)
            return f"""
😔 <b>خسارة... حظ أوفر المرة القادمة</b>

🎲 <b>لعبة النرد</b>
━━━━━━━━━━━━━━━━
💸 ثمن اللعبة: {cost:,} ل.س
🎲 {d1} | {d2}
💔 لم يحالفك الحظ
✨ XP: +{xp * 2 if is_vip(uid) else xp} {'(VIP ×2)' if is_vip(uid) else ''}

━━━━━━━━━━━━━━━━
💰 رصيدك: {get_balance(uid):,} ل.س
💪 جرب حظك مرة أخرى!
"""
    play_game(message, "dice", 20, dice_result)

@bot.message_handler(func=lambda message: message.text in [f"🎰 سلوت الفواكه ({GAME_COST:,} ل.س)", f"🎰 سلوت الفواكه ({GAME_COST//2:,} ل.س)"])
def slots_game(message):
    def slots_result(win, prize, cost, xp, leveled_up, uid):
        if win:
            fruit = random.choice(FRUITS)
            slots = [fruit, fruit, fruit]
            result = f"""
🎉 <b>🎉 جائزة كبرى! 🎉</b>

🎰 <b>سلوت الفواكه</b>
━━━━━━━━━━━━━━━━
💸 ثمن اللعبة: {cost:,} ل.س
🎰 {' ┃ '.join(slots)}
🍀 ثلاث {fruit} متتالية!
💰 الجائزة: {prize:,} ل.س
✨ XP: +{xp * 2 if is_vip(uid) else xp} {'(VIP ×2)' if is_vip(uid) else ''}
⭐ مستوى: {get_level(uid)}

━━━━━━━━━━━━━━━━
💰 رصيدك الآن: {get_balance(uid):,} ل.س
"""
            if leveled_up:
                result += f"\n🎉 <b>تهانينا! لقد وصلت للمستوى {get_level(uid)}!</b> 🎉"
            return result
        else:
            slots = [random.choice(FRUITS) for _ in range(3)]
            while slots[0] == slots[1] == slots[2]:
                slots[2] = random.choice([f for f in FRUITS if f != slots[0]])
            return f"""
😔 <b>خسارة... قريب جداً</b>

🎰 <b>سلوت الفواكه</b>
━━━━━━━━━━━━━━━━
💸 ثمن اللعبة: {cost:,} ل.س
🎰 {' ┃ '.join(slots)}
💔 كان قريباً هذه المرة
✨ XP: +{xp * 2 if is_vip(uid) else xp} {'(VIP ×2)' if is_vip(uid) else ''}

━━━━━━━━━━━━━━━━
💰 رصيدك: {get_balance(uid):,} ل.س
💪 جرب حظك مرة أخرى!
"""
    play_game(message, "slots", 30, slots_result)

# ================== أزرار إضافية ==================

@bot.message_handler(func=lambda message: message.text == "🔙 رجوع للقائمة")
def back_to_main_menu(message):
    uid = message.from_user.id
    keyboard = get_main_keyboard(uid)
    keyboard.row(KeyboardButton("👑 ICHANCY 👑"))
    bot.reply_to(message, "🔙 تم العودة للقائمة الرئيسية", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "💰" or message.text.startswith("💰"))
def show_balance(message):
    uid = message.from_user.id
    vip_status = "👑 VIP" if is_vip(uid) else "👤 عادي"
    msg = f"""
╭━━━━━━━━━━━━━━╮
┃ 💰 <b>الرصيد الحالي</b>
╰━━━━━━━━━━━━━━╯

┏━━━━━━━━━━━━━━┓
┃ 💵 <b>{get_balance(uid):,}</b> ل.س
┗━━━━━━━━━━━━━━┛

⭐ المستوى: {get_level(uid)}
✨ XP: {get_xp(uid)}
{vip_status}
    """
    keyboard = get_main_keyboard(uid)
    keyboard.row(KeyboardButton("👑 ICHANCY 👑"))
    bot.reply_to(message, msg, reply_markup=keyboard, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "⭐" or message.text.startswith("⭐"))
def show_level_info(message):
    uid = message.from_user.id
    level = get_level(uid)
    current_xp = get_xp(uid)
    needed_xp = level * 100
    xp_to_next = needed_xp - current_xp
    
    progress = int((current_xp % 100) / 100 * 20)
    bar = "█" * progress + "░" * (20 - progress)
    
    msg = f"""
╭━━━━━━━━━━━━━━╮
┃ ⭐ <b>المستوى والخبرة</b>
╰━━━━━━━━━━━━━━╯

<b>المستوى:</b> {level}
<b>XP:</b> {current_xp} / {needed_xp}

[{bar}]

<b>المتبقي:</b> {xp_to_next} XP

🎁 هدية الترحيب: {'✅' if welcome_gift_received.get(str(uid), False) else '❌'}
🎁 أول شحن: {'✅' if first_charge_done.get(str(uid), False) else '❌'}
👥 المدعوين: {get_referral_count(uid)}
👑 VIP: {'✅' if is_vip(uid) else '❌'}
    """
    keyboard = get_main_keyboard(uid)
    keyboard.row(KeyboardButton("👑 ICHANCY 👑"))
    bot.reply_to(message, msg, reply_markup=keyboard, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "📜 سجل العمليات")
def show_history(message):
    uid = message.from_user.id
    logs = history.get(str(uid), [])
    if not logs:
        keyboard = get_main_keyboard(uid)
        keyboard.row(KeyboardButton("👑 ICHANCY 👑"))
        bot.reply_to(message, "📭 لا يوجد سجل عمليات بعد.", reply_markup=keyboard)
        return
    
    recent_logs = logs[-15:]
    history_text = "\n".join(recent_logs)
    
    if len(history_text) > 4000:
        history_text = history_text[:4000] + "\n..."
    
    msg = f"""
📋 <b>سجل العمليات</b>
━━━━━━━━━━━━━━━━
{history_text}
━━━━━━━━━━━━━━━━
📌 إجمالي العمليات: {len(logs)}
    """
    keyboard = get_main_keyboard(uid)
    keyboard.row(KeyboardButton("👑 ICHANCY 👑"))
    bot.reply_to(message, msg, reply_markup=keyboard, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "❓ المساعدة")
def show_help(message):
    uid = message.from_user.id
    help_msg = f"""
❓ <b>المساعدة والدعم</b>

━━━━━━━━━━━━━━━━
🎮 <b>الألعاب:</b>
• ثمن اللعبة: {GAME_COST:,} ل.س (خصم 50% لـ VIP)
• أرباح تصل إلى 50,000 ل.س في اللعبة الواحدة

━━━━━━━━━━━━━━━━
👑 <b>نظام VIP:</b>
• اشتراك شهري: {VIP_COST:,} ل.س
• XP مضاعف + 5 تذاكر سحب + خصم 50%

━━━━━━━━━━━━━━━━
👥 <b>الدعوة:</b>
• دعوة {REQUIRED_REFERRALS} أشخاص = {REFERRAL_REWARD_BALANCE:,} ل.س + {REFERRAL_REWARD_XP} XP + دخول سحب {RAFFLE_PRIZE:,} ل.س

🎲 <b>سحب الكبير:</b>
• السحب يتم بين المستخدمين النشطين الذين انضموا عبر رابط الدعوة
• الجائزة: {RAFFLE_PRIZE:,} ل.س

📞 <b>إبلاغ المدير:</b>
• يمكنك إبلاغ المدير عن عملية شحن 3 مرات يومياً

💰 <b>سحب الرصيد:</b>
• الحد الأدنى للسحب: {MINIMUM_WITHDRAWAL:,} ل.س
    """
    keyboard = get_main_keyboard(uid)
    keyboard.row(KeyboardButton("👑 ICHANCY 👑"))
    bot.reply_to(message, help_msg, reply_markup=keyboard, parse_mode="HTML")

# ================== زر الإبلاغ للمدير ==================

@bot.message_handler(func=lambda message: message.text and message.text.startswith("📞 إبلاغ المدير"))
def report_to_admin(message):
    uid = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username or "لا يوجد"
    
    if not can_user_report(uid):
        remaining = get_remaining_reports(uid)
        bot.reply_to(message, f"❌ لقد تجاوزت الحد المسموح للإبلاغ اليوم!\n📊 متبقي لك: {remaining} محاولة\n🔄 يتجدد العدد غداً")
        return
    
    msg = bot.reply_to(message, """
📞 <b>إبلاغ المدير عن عملية شحن</b>

الرجاء إرسال المعلومات بالشكل التالي:

📌 <code>رقمك المبلغ</code>

مثال: <code>0938951343 10000</code>

📌 أرسل <code>/cancel</code> للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_report, uid, name, username)

def process_report(message, uid, name, username):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم إلغاء الإبلاغ")
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "❌ خطأ! استخدم: رقمك المبلغ\nمثال: 0938951343 10000")
        return
    
    phone = parts[0]
    try:
        amount = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ المبلغ يجب أن يكون رقماً!")
        return
    
    count = add_user_report(uid)
    remaining = MAX_REPORTS_PER_DAY - count
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    admin_msg = f"""
🔔 <b>إبلاغ جديد من مستخدم!</b>
━━━━━━━━━━━━━━━━
👤 <b>الاسم:</b> {name}
🆔 <b>ID:</b> <code>{uid}</code>
📱 <b>اليوزر:</b> @{username}
📞 <b>رقم المحول:</b> <code>{phone}</code>
💰 <b>المبلغ:</b> {amount:,} ل.س
⏰ <b>الوقت:</b> {current_time}
━━━━━━━━━━━━━━━━
📊 <b>إحصائيات المستخدم:</b>
• رصيده الحالي: {get_balance(uid):,} ل.س
• مستوى: {get_level(uid)}
• عدد الإبلاغات اليوم: {count}/{MAX_REPORTS_PER_DAY}
    """
    
    try:
        bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
        bot.reply_to(message, f"✅ تم إرسال إبلاغك للمدير!\n📊 متبقي لك اليوم: {remaining} إبلاغات")
        add_history(uid, f"📞 أرسل إبلاغ للمدير - المبلغ: {amount:,} ل.س")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل إرسال الإبلاغ: {e}")

# ================== كولبكات إضافية ==================

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main_callback(call):
    uid = call.from_user.id
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    keyboard = get_main_keyboard(uid)
    keyboard.row(KeyboardButton("👑 ICHANCY 👑"))
    bot.send_message(call.message.chat.id, "🔙 تم العودة", reply_markup=keyboard)
    bot.answer_callback_query(call.id)

# ================== كولبكات لوحة المدير ==================

@bot.callback_query_handler(func=lambda call: call.data == "set_barcode")
def set_barcode_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📸 أرسل صورة باركود شام كاش:")
    bot.register_next_step_handler(msg, save_barcode_admin)

def save_barcode_admin(message):
    global BARCODE_FILE_ID
    if not message.photo:
        bot.reply_to(message, "❌ يرجى إرسال صورة.")
        return
    
    BARCODE_FILE_ID = message.photo[-1].file_id
    save_data()
    bot.reply_to(message, "✅ تم حفظ باركود شام كاش!")

@bot.callback_query_handler(func=lambda call: call.data == "set_barcode_syriatel")
def set_barcode_syriatel_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📸 أرسل صورة باركود سيرياتيل كاش:")
    bot.register_next_step_handler(msg, save_barcode_syriatel_admin)

def save_barcode_syriatel_admin(message):
    global BARCODE_FILE_ID_SYRIATEL
    if not message.photo:
        bot.reply_to(message, "❌ يرجى إرسال صورة.")
        return
    
    BARCODE_FILE_ID_SYRIATEL = message.photo[-1].file_id
    save_data()
    bot.reply_to(message, "✅ تم حفظ باركود سيرياتيل كاش!")

@bot.callback_query_handler(func=lambda call: call.data == "stats")
def stats_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    total_balance = sum(balances.values())
    total_users = len(balances)
    total_xp = sum(xp.values())
    gift_users = len([u for u, received in welcome_gift_received.items() if received])
    banned_users = len(banned_from_welcome_gift)
    total_referrals = sum(len(refs) for refs in referrals.values())
    vip_count = len(VIP_USERS)
    
    codes_stats = get_codes_stats()
    
    stats_msg = f"""
📊 <b>إحصائيات البوت</b>
━━━━━━━━━━━━━━━━
👥 المستخدمين: {total_users}
💰 إجمالي الرصيد: {total_balance:,} ل.س
⭐ إجمالي XP: {total_xp}
🎁 مستلمي الهدية: {gift_users}
🚫 المحظورين: {banned_users}
👥 الدعوات: {total_referrals}
👑 VIP: {vip_count}
━━━━━━━━━━━━━━━━
🏆 <b>نظام الأكواد:</b>
🎫 أكواد رابحة: {codes_stats['winning_count']}
💔 أكواد خاسرة: {codes_stats['losing_count']}
✅ أكواد مستخدمة: {codes_stats['used_count']}
💰 إجمالي الجوائز المتبقية: {codes_stats['total_prize']:,} ل.س
━━━━━━━━━━━━━━━━
👑 <b>نظام ICHANCY:</b>
👥 عدد حسابات ICHANCY: {len(ichancy_accounts)}
💰 إجمالي رصيد ICHANCY: {sum(acc.get('balance', 0) for acc in ichancy_accounts.values()):,} ل.س
    """
    bot.send_message(call.message.chat.id, stats_msg, parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "users_ids")
def users_ids_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    if not balances:
        bot.answer_callback_query(call.id, "📭 لا يوجد مستخدمين!", show_alert=True)
        return
    
    all_ids = list(balances.keys())
    all_ids_sorted = sorted([int(uid) for uid in all_ids])
    
    ids_list = "\n".join([f"• <code>{uid}</code>" for uid in all_ids_sorted])
    total_users = len(all_ids_sorted)
    
    msg = f"""
👥 <b>قائمة IDs</b> ({total_users})
━━━━━━━━━━━━━━━━
{ids_list}
    """
    
    if len(msg) > 4000:
        file_content = "\n".join([str(uid) for uid in all_ids_sorted])
        file = io.BytesIO(file_content.encode('utf-8'))
        file.name = "users_ids.txt"
        bot.send_document(call.message.chat.id, file, caption=f"👥 عدد المستخدمين: {total_users}")
    else:
        bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "gift_list")
def gift_list_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    if not banned_from_welcome_gift:
        bot.send_message(call.message.chat.id, "📋 لا يوجد محظورين.")
    else:
        banned_list = "\n".join([f"• <code>{uid}</code>" for uid in banned_from_welcome_gift])
        bot.send_message(call.message.chat.id, f"🚫 <b>المحظورين:</b>\n{banned_list}", parse_mode="HTML")
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "backup")
def backup_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    data_to_backup = {
        'balances': balances,
        'xp': xp,
        'levels': levels,
        'history': history,
        'barcode': BARCODE_FILE_ID,
        'barcode_syriatel': BARCODE_FILE_ID_SYRIATEL,
        'first_charge_done': first_charge_done,
        'welcome_gift_received': welcome_gift_received,
        'banned_from_welcome_gift': banned_from_welcome_gift,
        'referrals': referrals,
        'referral_codes': referral_codes,
        'referral_rewards_claimed': referral_rewards_claimed,
        'raffle_entries': raffle_entries,
        'raffle_participants': raffle_participants,
        'vip_users': VIP_USERS,
        'auto_message_text': AUTO_MESSAGE_TEXT,
        'promo_phone': PROMO_PHONE_NUMBER,
        'global_win_rate': global_win_rate,
        'win_prizes': win_prizes,
        'default_rate': DEFAULT_RATE,
        'raffle_withdrawn': raffle_withdrawn,
        'user_reports_count': user_reports_count,
        'first_play_secret_win': first_play_secret_win,
        'game_cost': GAME_COST,
        'minimum_withdrawal': MINIMUM_WITHDRAWAL,
        'winning_codes': winning_codes,
        'losing_codes': losing_codes,
        'used_codes': used_codes,
        'ichancy_accounts': ichancy_accounts
    }
    
    file = io.BytesIO(json.dumps(data_to_backup, ensure_ascii=False, indent=2).encode('utf-8'))
    file.name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    bot.send_document(call.message.chat.id, file, caption="💾 نسخة احتياطية كاملة (بما في ذلك حسابات ICHANCY)")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "restore_info")
def restore_info_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    msg = """
📂 <b>استعادة النسخة الاحتياطية</b>
━━━━━━━━━━━━━━━━

📝 أرسل ملف JSON للنسخة الاحتياطية مباشرة
⚠️ سيتم استبدال جميع البيانات الحالية (بما في ذلك حسابات ICHANCY)

📁 أرسل الملف الآن...
    """
    
    bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
    bot.answer_callback_query(call.id)

def is_backup_file(message):
    if not is_admin(message.from_user.id):
        return False
    return bool(message.document)

@bot.message_handler(func=is_backup_file, content_types=['document'])
def handle_backup_restore(message):
    try:
        user_id = message.from_user.id
        file_id = message.document.file_id
        file_name = message.document.file_name or "backup.json"

        pending_restore_files[user_id] = file_id

        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("✅ نعم، استعادة البيانات", callback_data="confirm_restore"),
            InlineKeyboardButton("❌ إلغاء", callback_data="cancel_restore")
        )

        bot.reply_to(
            message,
            f"📂 <b>تم استقبال ملف النسخة الاحتياطية</b>\n\n"
            f"📁 <b>اسم الملف:</b> {file_name}\n"
            f"⚠️ هل تريد استعادة البيانات منه؟",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء استقبال الملف:\n<code>{e}</code>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "confirm_restore")
def confirm_restore_backup(call):
    user_id = call.from_user.id

    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return

    if user_id not in pending_restore_files:
        bot.answer_callback_query(call.id, "❌ لا يوجد ملف لاستعادته!", show_alert=True)
        return

    file_id = pending_restore_files[user_id]
    bot.answer_callback_query(call.id, "⏳ جاري الاستعادة...")

    wait_msg = bot.send_message(call.message.chat.id, "⏳ جاري تحميل الملف...")

    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        try:
            text = downloaded_file.decode('utf-8')
            data = json.loads(text)
        except Exception as e:
            bot.delete_message(wait_msg.chat.id, wait_msg.message_id)
            bot.send_message(call.message.chat.id, f"❌ الملف ليس نسخة احتياطية صالحة:\n<code>{e}</code>", parse_mode="HTML")
            return

        # استعادة البيانات
        global balances, xp, levels, history, BARCODE_FILE_ID, BARCODE_FILE_ID_SYRIATEL
        global pending_charges, first_charge_done, welcome_gift_received
        global banned_from_welcome_gift, referrals, referral_codes
        global referral_rewards_claimed, raffle_entries, raffle_participants, VIP_USERS
        global AUTO_MESSAGE_TEXT, PROMO_PHONE_NUMBER
        global global_win_rate, win_prizes, DEFAULT_RATE, raffle_withdrawn, user_reports_count, first_play_secret_win, GAME_COST, MINIMUM_WITHDRAWAL
        global winning_codes, losing_codes, used_codes, ichancy_accounts

        balances = data.get("balances", {})
        xp = data.get("xp", {})
        levels = data.get("levels", {})
        history = data.get("history", {})
        BARCODE_FILE_ID = data.get("barcode", None)
        BARCODE_FILE_ID_SYRIATEL = data.get("barcode_syriatel", None)
        first_charge_done = data.get("first_charge_done", {})
        welcome_gift_received = data.get("welcome_gift_received", {})
        banned_from_welcome_gift = data.get("banned_from_welcome_gift", [])
        pending_charges = data.get("pending_charges", {})
        referrals = data.get("referrals", {})
        referral_codes = data.get("referral_codes", {})
        referral_rewards_claimed = data.get("referral_rewards_claimed", {})
        raffle_entries = data.get("raffle_entries", {})
        raffle_participants = data.get("raffle_participants", [])
        VIP_USERS = data.get("vip_users", {})
        AUTO_MESSAGE_TEXT = data.get("auto_message_text", AUTO_MESSAGE_TEXT_DEFAULT)
        PROMO_PHONE_NUMBER = data.get("promo_phone", "09XXXXXXXX")
        global_win_rate = data.get("global_win_rate", 30)
        win_prizes = data.get("win_prizes", {"0": 0, "1": 5000, "2": 5000, "3": 5000, "4": 40000, "5": 40000})
        DEFAULT_RATE = data.get("default_rate", 1)
        raffle_withdrawn = data.get("raffle_withdrawn", {})
        user_reports_count = data.get("user_reports_count", {})
        first_play_secret_win = data.get("first_play_secret_win", {})
        GAME_COST = data.get("game_cost", 2500)
        MINIMUM_WITHDRAWAL = data.get("minimum_withdrawal", 80000)
        winning_codes = data.get("winning_codes", {})
        losing_codes = data.get("losing_codes", [])
        used_codes = data.get("used_codes", [])
        ichancy_accounts = data.get("ichancy_accounts", {})

        save_data()
        save_ichancy_data()

        del pending_restore_files[user_id]

        bot.delete_message(wait_msg.chat.id, wait_msg.message_id)

        total_users = len(balances)
        total_balance = sum(balances.values())
        total_ichancy = len(ichancy_accounts)

        success_msg = f"""
✅ <b>تمت استعادة النسخة الاحتياطية بنجاح!</b>
━━━━━━━━━━━━━━━━
📊 <b>إحصائيات البيانات المستعادة:</b>
• 👥 عدد مستخدمي البوت: {total_users}
• 💰 إجمالي رصيد البوت: {total_balance:,} ل.س
• 👑 حسابات ICHANCY: {total_ichancy}
• 💰 إجمالي رصيد ICHANCY: {sum(acc.get('balance', 0) for acc in ichancy_accounts.values()):,} ل.س
━━━━━━━━━━━━━━━━

📌 <b>ملاحظة:</b> لم يتم إرسال أي رسالة للمستخدمين تلقائياً.
        """

        bot.send_message(call.message.chat.id, success_msg, parse_mode="HTML")
        add_history(call.from_user.id, f"💾 تم استعادة نسخة احتياطية ({total_users} مستخدم)")

    except Exception as e:
        bot.delete_message(wait_msg.chat.id, wait_msg.message_id)
        bot.send_message(call.message.chat.id, f"❌ حدث خطأ أثناء الاستعادة:\n<code>{e}</code>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_restore")
def cancel_restore_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    if call.from_user.id in pending_restore_files:
        del pending_restore_files[call.from_user.id]
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "❌ <b>تم إلغاء عملية الاستعادة.</b>", parse_mode="HTML")
    bot.answer_callback_query(call.id, "تم الإلغاء")

# ================== أوامر المدير الإضافية ==================

@bot.message_handler(func=lambda message: message.text == "👑 لوحة المدير")
def admin_panel_button(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.reply_to(message, "❌ هذا الأمر للمدير فقط.")
        return
    
    total_balance = sum(balances.values())
    total_users = len(balances)
    total_xp = sum(xp.values())
    gift_users = len([u for u, received in welcome_gift_received.items() if received])
    banned_users = len(banned_from_welcome_gift)
    total_referrals = sum(len(refs) for refs in referrals.values())
    vip_count = len(VIP_USERS)
    total_ichancy = len(ichancy_accounts)
    total_ichancy_balance = sum(acc.get('balance', 0) for acc in ichancy_accounts.values())
    
    stats_msg = f"""
👑 <b>لوحة تحكم المدير</b>
━━━━━━━━━━━━━━━━
📊 <b>إحصائيات البوت:</b>
• 👥 المستخدمين: {total_users}
• 💰 إجمالي الرصيد: {total_balance:,} ل.س
• ⭐ إجمالي XP: {total_xp}
• 🎁 مستلمي الهدية: {gift_users}
• 🚫 المحظورين: {banned_users}
• 👥 الدعوات: {total_referrals}
• 👑 VIP: {vip_count}
━━━━━━━━━━━━━━━━
👑 <b>نظام ICHANCY:</b>
• 👥 عدد الحسابات: {total_ichancy}
• 💰 إجمالي الرصيد: {total_ichancy_balance:,} ل.س
    """
    bot.reply_to(message, stats_msg, reply_markup=get_admin_keyboard(), parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "🆔 قائمة IDs")
def users_ids_button(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.reply_to(message, "❌ هذا الأمر للمدير فقط.")
        return
    
    if not balances:
        bot.reply_to(message, "📭 لا يوجد مستخدمين.")
        return
    
    all_ids = list(balances.keys())
    all_ids_sorted = sorted([int(uid) for uid in all_ids])
    
    ids_list = "\n".join([f"• <code>{uid}</code>" for uid in all_ids_sorted])
    total_users = len(all_ids_sorted)
    
    msg = f"""
👥 <b>قائمة IDs</b> ({total_users})
━━━━━━━━━━━━━━━━
{ids_list}
    """
    
    if len(msg) > 4000:
        file_content = "\n".join([str(uid) for uid in all_ids_sorted])
        file = io.BytesIO(file_content.encode('utf-8'))
        file.name = "users_ids.txt"
        bot.send_document(message.chat.id, file, caption=f"👥 عدد المستخدمين: {total_users}")
    else:
        bot.reply_to(message, msg, parse_mode="HTML")

@bot.message_handler(commands=['setbarcode'])
def set_barcode_admin(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ للمدير فقط.")
        return
    
    msg = bot.reply_to(message, "📸 أرسل صورة باركود شام كاش:")
    bot.register_next_step_handler(msg, save_barcode_admin)

@bot.message_handler(commands=['setbarcodesyriatel'])
def set_barcode_syriatel_admin(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ للمدير فقط.")
        return
    
    msg = bot.reply_to(message, "📸 أرسل صورة باركود سيرياتيل كاش:")
    bot.register_next_step_handler(msg, save_barcode_syriatel_admin)

@bot.message_handler(commands=['addbalance'])
def add_balance_admin(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ للمدير فقط.")
        return
    
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "/addbalance user_id amount")
        return
    
    uid = int(parts[1])
    amount = int(parts[2])
    
    add_balance(uid, amount)
    bot.reply_to(message, f"✅ تم شحن {amount:,} ل.س للمستخدم {uid}")
    
    try:
        bot.send_message(uid, f"✅ تم شحن رصيدك: {amount:,} ل.س")
    except:
        pass

@bot.message_handler(commands=['sendmsg'])
def send_msg_command(message):
    if not is_admin(message.from_user.id):
        return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "📌 /sendmsg <ID> <الرسالة>\nمثال: /sendmsg 12345 كيفك؟")
        return
    
    try:
        target_id = int(parts[1])
        msg_text = parts[2]
        
        bot.send_message(target_id, f"📨 <b>رسالة من المدير:</b>\n━━━━━━━━━━━━━━━━\n{msg_text}", parse_mode="HTML")
        bot.reply_to(message, f"✅ تم إرسال الرسالة للمستخدم {target_id}")
        add_history(message.from_user.id, f"📨 أرسل رسالة للمستخدم {target_id}")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل الإرسال: {e}")

# ================== كولبكات الرسائل ==================

@bot.callback_query_handler(func=lambda call: call.data == "send_auto_message")
def send_auto_message_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id, "⏳ جاري الإرسال...")
    bot.send_message(call.message.chat.id, "📨 جاري إرسال الرسالة التلقائية لجميع المستخدمين...")
    send_auto_message_to_all_users()

@bot.callback_query_handler(func=lambda call: call.data == "edit_auto_message")
def edit_auto_message_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, """
📝 <b>تعديل الرسالة التلقائية</b>

أرسل النص الجديد للرسالة

💡 ملاحظات:
• استخدم <code>{phone_number}</code> لإضافة رقم التحويل
• يمكنك استخدام تنسيق HTML

📌 أرسل <code>/cancel</code> للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, save_auto_message_from_admin)

def save_auto_message_from_admin(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    global AUTO_MESSAGE_TEXT
    AUTO_MESSAGE_TEXT = message.text
    save_data()
    
    preview = AUTO_MESSAGE_TEXT.format(phone_number=PROMO_PHONE_NUMBER)
    
    bot.reply_to(message, f"""
✅ <b>تم تحديث الرسالة التلقائية بنجاح!</b>

📨 <b>معاينة الرسالة:</b>
━━━━━━━━━━━━━━━━
{preview}
━━━━━━━━━━━━━━━━

📌 يمكنك الآن استخدام "إرسال رسالة للجميع"
""", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "set_phone_number")
def set_phone_number_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, """
📞 <b>تعيين رقم التحويل</b>

أرسل رقم الهاتف الجديد

مثال: <code>0999999999</code>

📌 أرسل <code>/cancel</code> للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, save_phone_number_from_admin)

def save_phone_number_from_admin(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    global PROMO_PHONE_NUMBER
    PROMO_PHONE_NUMBER = message.text
    save_data()
    
    bot.reply_to(message, f"✅ تم تعيين رقم التحويل إلى:\n<code>{PROMO_PHONE_NUMBER}</code>", parse_mode="HTML")

# ================== كولبكات التحكم بالفوز ==================

@bot.callback_query_handler(func=lambda call: call.data == "set_global_rate")
def set_global_rate_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, f"""
📊 <b>تعيين نسبة الفوز الشاملة</b>

أرسل النسبة الجديدة (من 0 إلى 100)

📌 النسبة الحالية: {global_win_rate}%

مثال: <code>40</code>

📌 أرسل /cancel للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_set_global_rate)

def process_set_global_rate(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    try:
        new_rate = int(message.text.strip())
        if new_rate < 0 or new_rate > 100:
            bot.reply_to(message, "❌ النسبة يجب أن تكون بين 0 و 100")
            return
        
        set_global_win_rate(new_rate)
        bot.reply_to(message, f"✅ تم تعيين نسبة الفوز الشاملة إلى {new_rate}% لجميع المستخدمين")
    except ValueError:
        bot.reply_to(message, "❌ يرجى إدخال رقم صحيح")

@bot.callback_query_handler(func=lambda call: call.data == "show_global_rate")
def show_global_rate_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.send_message(call.message.chat.id, f"""
📊 <b>نسبة الفوز الحالية</b>
━━━━━━━━━━━━━━━━
🎯 النسبة الشاملة: {global_win_rate}%
👥 تطبق على جميع المستخدمين بالتساوي
━━━━━━━━━━━━━━━━
📌 يمكنك تغييرها من خلال زر "تعيين نسبة الفوز"
""", parse_mode="HTML")
    bot.answer_callback_query(call.id)

# ================== كولبكات إدارة المستخدمين ==================

@bot.callback_query_handler(func=lambda call: call.data == "all_users_balances")
def all_users_balances_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    if not balances:
        bot.send_message(call.message.chat.id, "📭 لا يوجد مستخدمين")
        bot.answer_callback_query(call.id)
        return
    
    users_list = []
    total_balance = 0
    
    for uid_str, balance in balances.items():
        users_list.append(f"🆔 {uid_str} | 💰 {balance:,} ل.س")
        total_balance += balance
    
    users_list_sorted = sorted(users_list, key=lambda x: int(x.split("|")[0].split("🆔")[1].strip()))
    
    msg = f"""
💰 <b>رصيد جميع المستخدمين</b>
━━━━━━━━━━━━━━━━
👥 عدد المستخدمين: {len(users_list)}
💰 إجمالي الرصيد: {total_balance:,} ل.س
━━━━━━━━━━━━━━━━
""" + "\n".join(users_list_sorted[:100])
    
    if len(msg) > 4000:
        file_content = "\n".join([f"ID: {uid_str} | الرصيد: {balance:,} ل.س" for uid_str, balance in balances.items()])
        file = io.BytesIO(file_content.encode('utf-8'))
        file.name = "all_users_balances.txt"
        bot.send_document(call.message.chat.id, file, caption=f"💰 رصيد جميع المستخدمين ({len(users_list)} مستخدم)")
    else:
        bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "reset_single_balance")
def reset_single_balance_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, """
🔄 <b>تصفير رصيد مستخدم واحد</b>

أرسل ID المستخدم لتصفير رصيده إلى 0

مثال: <code>12345</code>

📌 أرسل /cancel للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_reset_single_balance)

def process_reset_single_balance(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    try:
        uid = int(message.text.strip())
        uid_str = str(uid)
        
        if uid_str not in balances:
            bot.reply_to(message, f"❌ المستخدم {uid} غير موجود!")
            return
        
        old_balance = balances[uid_str]
        balances[uid_str] = 0
        save_data()
        
        add_history(uid, f"🔄 تم تصفير الرصيد من {old_balance:,} ل.س إلى 0 (بواسطة المدير)")
        
        try:
            bot.send_message(uid, f"⚠️ <b>تم تصفير رصيدك إلى 0 ل.س</b>\n💰 رصيدك السابق: {old_balance:,} ل.س\n📞 للاستفسار، تواصل مع المدير.", parse_mode="HTML")
        except:
            pass
        
        bot.reply_to(message, f"✅ تم تصفير رصيد المستخدم {uid}\n💰 الرصيد السابق: {old_balance:,} ل.س\n💰 الرصيد الحالي: 0 ل.س")
        
    except ValueError:
        bot.reply_to(message, "❌ ID غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data == "reset_multiple_balances")
def reset_multiple_balances_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, """
🔄 <b>تصفير رصيد مجموعة من المستخدمين</b>

أرسل قائمة الـ IDs مفصولة بفواصل أو مسافات

مثال: <code>12345,67890,11111</code>
أو: <code>12345 67890 11111</code>

📌 أرسل /cancel للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_reset_multiple_balances)

def process_reset_multiple_balances(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    text = message.text.replace(',', ' ')
    ids_list = text.split()
    
    if not ids_list:
        bot.reply_to(message, "❌ لم يتم إدخال أي IDs!")
        return
    
    success_count = 0
    not_found_count = 0
    results = []
    
    for id_str in ids_list:
        try:
            uid = int(id_str)
            uid_str = str(uid)
            
            if uid_str in balances:
                old_balance = balances[uid_str]
                balances[uid_str] = 0
                results.append(f"✅ {uid}: {old_balance:,} → 0")
                success_count += 1
                
                try:
                    bot.send_message(uid, f"⚠️ <b>تم تصفير رصيدك إلى 0 ل.س</b>\n💰 رصيدك السابق: {old_balance:,} ل.س", parse_mode="HTML")
                except:
                    pass
            else:
                results.append(f"❌ {uid}: غير موجود")
                not_found_count += 1
        except ValueError:
            results.append(f"❌ {id_str}: ID غير صحيح")
            not_found_count += 1
    
    save_data()
    
    report = f"""
🔄 <b>تقرير تصفير الرصيد</b>
━━━━━━━━━━━━━━━━
✅ تم التصفير: {success_count} مستخدم
❌ فشل/غير موجود: {not_found_count} مستخدم
━━━━━━━━━━━━━━━━
<b>التفاصيل:</b>
{chr(10).join(results[:30])}
"""
    
    if len(results) > 30:
        report += f"\n... و {len(results) - 30} نتيجة أخرى"
    
    bot.reply_to(message, report, parse_mode="HTML")
    add_history(message.from_user.id, f"🔄 قام بتصفير رصيد {success_count} مستخدم")

# ================== كولبكات إضافية ==================

@bot.callback_query_handler(func=lambda call: call.data == "raffle_draw")
def raffle_draw_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    referred_users = []
    for inviter, invited_list in referrals.items():
        for invited in invited_list:
            if invited not in referred_users:
                referred_users.append(invited)
    
    if not referred_users:
        bot.answer_callback_query(call.id, "📭 لا يوجد مستخدمين انضموا عبر رابط الدعوة!", show_alert=True)
        return
    
    winner_uid = random.choice(referred_users)
    winner_name = "مستخدم"
    
    try:
        winner_chat = bot.get_chat(int(winner_uid))
        winner_name = winner_chat.first_name
    except:
        pass
    
    add_balance(int(winner_uid), RAFFLE_PRIZE)
    add_history(int(winner_uid), f"🏆 فاز بالسحب الكبير +{RAFFLE_PRIZE:,} ل.س")
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💰 تفقد رصيدك", callback_data=f"check_balance_after_raffle_{winner_uid}"))
    
    try:
        bot.send_message(
            int(winner_uid),
            f"""
🎉 <b>🎉 مبروك! لقد ربحت في السحب الكبير! 🎉</b>

━━━━━━━━━━━━━━━━
🏆 <b>لقد فزت بمبلغ:</b> {RAFFLE_PRIZE:,} ل.س
👑 <b>السحب كان من بين المستخدمين النشطين</b>

💰 <b>رصيدك الجديد:</b> {get_balance(int(winner_uid)):,} ل.س

━━━━━━━━━━━━━━━━
اضغط على الزر أدناه لتفقد رصيدك
""",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except:
        pass
    
    msg = f"""
🎰 <b>نتيجة السحب الكبير</b>
━━━━━━━━━━━━━━━━
🏆 <b>الفائز:</b> {winner_name}
🆔 <b>ID:</b> <code>{winner_uid}</code>
💰 <b>الجائزة:</b> {RAFFLE_PRIZE:,} ل.س
👥 <b>عدد المشاركين:</b> {len(referred_users)}
━━━━━━━━━━━━━━━━
📌 في انتظار تأكيد استلام الفائز للجائزة...
    """
    
    bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
    bot.answer_callback_query(call.id, f"✅ تم اختيار الفائز: {winner_uid}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_balance_after_raffle_"))
def check_balance_after_raffle(call):
    winner_uid = int(call.data.split("_")[3])
    
    if call.from_user.id != winner_uid:
        bot.answer_callback_query(call.id, "❌ هذا الزر ليس لك!", show_alert=True)
        return
    
    current_balance = get_balance(winner_uid)
    
    bot.edit_message_text(
        f"""
✅ <b>تم تأكيد رصيدك!</b>
━━━━━━━━━━━━━━━━
💰 <b>رصيدك الحالي:</b> {current_balance:,} ل.س
🏆 <b>الجائزة المضافة:</b> {RAFFLE_PRIZE:,} ل.س

شكراً لمشاركتك في السحب الكبير! 🎉
""",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )
    
    bot.answer_callback_query(call.id, f"✅ رصيدك الحالي: {current_balance:,} ل.س", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "distribute_money")
def distribute_money_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, """
💰 <b>توزيع مبلغ على المستخدمين</b>

أرسل الأمر بالشكل التالي:
<code>/distribute المبلغ عدد_المستخدمين</code>

مثال: <code>/distribute 1000000 15</code>

📌 سيتم توزيع المبلغ عشوائياً على العدد المحدد
📌 أرسل /cancel للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_distribute)

def process_distribute(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "❌ خطأ! استخدم: /distribute المبلغ عدد_المستخدمين")
        return
    
    try:
        total = int(parts[0])
        count = int(parts[1])
        
        users = list(balances.keys())
        if len(users) < count:
            bot.reply_to(message, f"❌ عدد المستخدمين المتاحين {len(users)} أقل من {count}")
            return
        
        winners = random.sample(users, count)
        prize_per_user = total // count
        
        success_count = 0
        for uid in winners:
            add_balance(int(uid), prize_per_user)
            try:
                bot.send_message(int(uid), f"🎉 <b>تهانينا!</b>\n💰 تم إضافة {prize_per_user:,} ل.س إلى رصيدك", parse_mode="HTML")
                success_count += 1
            except:
                pass
            time.sleep(0.05)
        
        bot.reply_to(message, f"✅ تم توزيع {total:,} ل.س على {success_count} مستخدم\n💰 كل مستخدم حصل على {prize_per_user:,} ل.س")
    except ValueError:
        bot.reply_to(message, "❌ يرجى إدخال أرقام صحيحة")

@bot.callback_query_handler(func=lambda call: call.data == "send_to_id")
def send_to_id_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, """
📨 <b>إرسال رسالة لـ ID محدد</b>

أرسل الأمر بالشكل التالي:
<code>/sendmsg ID الرسالة</code>

مثال: <code>/sendmsg 12345 كيفك؟</code>

📌 أرسل /cancel للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_send_to_id)

def process_send_to_id(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "❌ خطأ! استخدم: /sendmsg ID الرسالة")
        return
    
    try:
        target_id = int(parts[1])
        msg_text = parts[2]
        
        bot.send_message(target_id, f"📨 <b>رسالة من المدير:</b>\n━━━━━━━━━━━━━━━━\n{msg_text}", parse_mode="HTML")
        bot.reply_to(message, f"✅ تم إرسال الرسالة للمستخدم {target_id}")
        add_history(message.from_user.id, f"📨 أرسل رسالة للمستخدم {target_id}")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل الإرسال: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "send_photo_to_id")
def send_photo_to_id_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, """
🖼️ <b>إرسال صورة لـ ID محدد</b>

📌 أرسل ID المستخدم:
مثال: <code>12345</code>

📌 أرسل <code>/cancel</code> للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, get_photo_target_id)

def get_photo_target_id(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    try:
        target_id = int(message.text.strip())
        bot.reply_to(message, f"✅ تم تحديد ID: {target_id}\n━━━━━━━━━━━━━━━━\n📝 الآن أرسل التعليق (اختياري):\n📌 أرسل <code>/skip</code> لتخطي التعليق", parse_mode="HTML")
        bot.register_next_step_handler(message, get_photo_caption, target_id)
    except ValueError:
        bot.reply_to(message, "❌ ID غير صحيح! أرسل رقماً فقط")
        bot.register_next_step_handler(message, get_photo_target_id)

def get_photo_caption(message, target_id):
    caption = ""
    if message.text != "/skip":
        caption = message.text
    
    bot.reply_to(message, f"✅ التعليق: {caption if caption else 'بدون تعليق'}\n━━━━━━━━━━━━━━━━\n📸 أرسل الصورة الآن:")
    bot.register_next_step_handler(message, lambda m: send_photo_to_user_final(m, target_id, caption))

def send_photo_to_user_final(message, target_id, caption):
    if not message.photo:
        bot.reply_to(message, "❌ يرجى إرسال صورة!")
        bot.register_next_step_handler(message, lambda m: send_photo_to_user_final(m, target_id, caption))
        return
    
    try:
        bot.send_photo(target_id, message.photo[-1].file_id, caption=f"📨 <b>رسالة من المدير:</b>\n━━━━━━━━━━━━━━━━\n{caption}" if caption else None, parse_mode="HTML")
        bot.reply_to(message, f"✅ تم إرسال الصورة للمستخدم {target_id}")
        add_history(message.from_user.id, f"🖼️ أرسل صورة للمستخدم {target_id}")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل الإرسال: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "get_balance_user")
def get_balance_user_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, """
💰 <b>معرفة رصيد مستخدم</b>

أرسل ID المستخدم:

مثال: <code>12345</code>

📌 أرسل <code>/cancel</code> للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_get_balance)

def process_get_balance(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    try:
        uid = int(message.text.strip())
        uid_str = str(uid)
        
        if uid_str not in balances:
            bot.reply_to(message, f"❌ المستخدم {uid} غير موجود!")
            return
        
        user_balance = get_balance(uid)
        user_level = get_level(uid)
        user_xp = get_xp(uid)
        user_vip = "✅ نعم" if is_vip(uid) else "❌ لا"
        
        msg = f"""
👤 <b>المستخدم {uid}</b>
━━━━━━━━━━━━━━━━
💰 الرصيد: {user_balance:,} ل.س
⭐ المستوى: {user_level}
✨ XP: {user_xp}
👑 VIP: {user_vip}
        """
        bot.reply_to(message, msg, parse_mode="HTML")
        
    except ValueError:
        bot.reply_to(message, "❌ ID غير صحيح!")

# ================== زر ICHANCY (نظام الحسابات) ==================

@bot.message_handler(func=lambda message: message.text == "👑 ICHANCY 👑")
@require_subscription
def ichancy_menu(message):
    uid = message.from_user.id
    
    # البحث عن حساب موجود للمستخدم
    user_account = None
    for username, data in ichancy_accounts.items():
        if data.get("user_id") == uid:
            user_account = username
            break
    
    if user_account:
        balance = ichancy_accounts[user_account].get("balance", 0)
        msg = f"""
👑 <b>حساب ICHANCY الخاص بك</b>
━━━━━━━━━━━━━━━━
📛 <b>اسم المستخدم:</b> <code>{user_account}</code>
💰 <b>رصيد حساب ICHANCY:</b> {balance:,} ل.س
━━━━━━━━━━━━━━━━
💰 <b>رصيدك في البوت:</b> {get_balance(uid):,} ل.س

📌 استخدم الأزرار أدناه للشحن أو السحب
        """
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("📥 شحن رصيد ICHANCY", callback_data=f"ichancy_charge_{user_account}"),
            InlineKeyboardButton("📤 سحب رصيدي من ICHANCY", callback_data=f"ichancy_withdraw_{user_account}")
        )
        keyboard.add(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main"))
        bot.reply_to(message, msg, reply_markup=keyboard, parse_mode="HTML")
    else:
        # طلب اسم مستخدم جديد
        msg = """
👑 <b>مرحباً بك في ICHANCY</b>
━━━━━━━━━━━━━━━━
✨ أنشئ حسابك الآن للعب على الموقع!

📝 <b>أرسل اسم المستخدم الذي تريده:</b>

📌 أرسل <code>/cancel</code> للإلغاء
        """
        bot.reply_to(message, msg, parse_mode="HTML")
        bot.register_next_step_handler(message, process_register_username)

def process_register_username(message):
    uid = message.from_user.id
    
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    username = message.text.strip()
    if not username or len(username) < 3:
        bot.reply_to(message, "❌ اسم المستخدم يجب أن يكون 3 أحرف على الأقل")
        return
    
    if username in ichancy_accounts:
        bot.reply_to(message, "❌ اسم المستخدم موجود بالفعل! جرب اسماً آخر.")
        return
    
    # حفظ الاسم مؤقتاً
    if not hasattr(bot, 'pending_ichancy'):
        bot.pending_ichancy = {}
    bot.pending_ichancy[uid] = {"username": username}
    
    msg = f"""
✅ <b>تم استلام اسم المستخدم:</b> <code>{username}</code>
━━━━━━━━━━━━━━━━
📝 <b>الآن أرسل كلمة المرور التي تريدها:</b>

📌 أرسل <code>/cancel</code> للإلغاء
    """
    bot.reply_to(message, msg, parse_mode="HTML")
    bot.register_next_step_handler(message, process_register_password)

def process_register_password(message):
    uid = message.from_user.id
    
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        if hasattr(bot, 'pending_ichancy') and uid in bot.pending_ichancy:
            del bot.pending_ichancy[uid]
        return
    
    password = message.text.strip()
    if not password or len(password) < 3:
        bot.reply_to(message, "❌ كلمة المرور يجب أن تكون 3 أحرف على الأقل")
        return
    
    if not hasattr(bot, 'pending_ichancy') or uid not in bot.pending_ichancy:
        bot.reply_to(message, "❌ حدث خطأ، يرجى المحاولة مرة أخرى باستخدام زر ICHANCY")
        return
    
    username = bot.pending_ichancy[uid]["username"]
    
    # إنشاء الحساب
    ichancy_accounts[username] = {
        "password": password,
        "user_id": uid,
        "balance": 0
    }
    save_ichancy_data()
    
    del bot.pending_ichancy[uid]
    
    msg = f"""
✅ <b>تم إنشاء حساب ICHANCY بنجاح!</b>
━━━━━━━━━━━━━━━━
📛 <b>اسم المستخدم:</b> <code>{username}</code>
🔐 <b>كلمة المرور:</b> <code>{password}</code>
💰 <b>الرصيد الابتدائي:</b> 0 ل.س

━━━━━━━━━━━━━━━━
📌 يمكنك الآن:
• شحن رصيد من البوت إلى الحساب
• سحب رصيد من الحساب إلى البوت
• استخدام الحساب لتسجيل الدخول إلى موقع ICHANCY
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📥 شحن رصيد ICHANCY", callback_data=f"ichancy_charge_{username}"),
        InlineKeyboardButton("📤 سحب رصيدي من ICHANCY", callback_data=f"ichancy_withdraw_{username}")
    )
    keyboard.add(InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main"))
    bot.reply_to(message, msg, reply_markup=keyboard, parse_mode="HTML")

# معالجة شحن الرصيد
@bot.callback_query_handler(func=lambda call: call.data.startswith("ichancy_charge_"))
def ichancy_charge_callback(call):
    username = call.data.replace("ichancy_charge_", "")
    uid = call.from_user.id
    
    if username not in ichancy_accounts:
        bot.answer_callback_query(call.id, "❌ الحساب غير موجود!", show_alert=True)
        return
    
    if ichancy_accounts[username].get("user_id") != uid:
        bot.answer_callback_query(call.id, "❌ هذا الحساب ليس لك!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, f"""
💰 <b>شحن رصيد ICHANCY</b>
━━━━━━━━━━━━━━━━
📛 الحساب: <code>{username}</code>
💰 رصيد البوت الحالي: {get_balance(uid):,} ل.س

📝 <b>أرسل المبلغ الذي تريد شحنه:</b>

📌 أرسل <code>/cancel</code> للإلغاء
    """, parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_ichancy_charge, username)

def process_ichancy_charge(message, username):
    uid = message.from_user.id
    
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            bot.reply_to(message, "❌ المبلغ يجب أن يكون أكبر من 0")
            return
        
        if get_balance(uid) < amount:
            bot.reply_to(message, f"❌ رصيدك غير كافٍ!\n💰 رصيدك: {get_balance(uid):,} ل.س")
            return
        
        # خصم من البوت
        sub_balance(uid, amount)
        
        # إضافة إلى حساب ICHANCY
        ichancy_accounts[username]["balance"] = ichancy_accounts[username].get("balance", 0) + amount
        save_ichancy_data()
        
        msg = f"""
✅ <b>تم الشحن بنجاح!</b>
━━━━━━━━━━━━━━━━
📛 الحساب: <code>{username}</code>
💰 المبلغ المشحون: {amount:,} ل.س
💳 رصيد حساب ICHANCY الجديد: {ichancy_accounts[username]['balance']:,} ل.س
💰 رصيدك المتبقي في البوت: {get_balance(uid):,} ل.س

━━━━━━━━━━━━━━━━
🎮 يمكنك الآن استخدام هذا الرصيد في موقع ICHANCY
        """
        bot.reply_to(message, msg, parse_mode="HTML")
        
    except ValueError:
        bot.reply_to(message, "❌ يرجى إدخال مبلغ صحيح")

# معالجة سحب الرصيد
@bot.callback_query_handler(func=lambda call: call.data.startswith("ichancy_withdraw_"))
def ichancy_withdraw_callback(call):
    username = call.data.replace("ichancy_withdraw_", "")
    uid = call.from_user.id
    
    if username not in ichancy_accounts:
        bot.answer_callback_query(call.id, "❌ الحساب غير موجود!", show_alert=True)
        return
    
    if ichancy_accounts[username].get("user_id") != uid:
        bot.answer_callback_query(call.id, "❌ هذا الحساب ليس لك!", show_alert=True)
        return
    
    current_balance = ichancy_accounts[username].get("balance", 0)
    
    if current_balance <= 0:
        bot.answer_callback_query(call.id, "❌ لا يوجد رصيد للسحب!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, f"""
💰 <b>سحب الرصيد من ICHANCY</b>
━━━━━━━━━━━━━━━━
📛 الحساب: <code>{username}</code>
💰 رصيد حساب ICHANCY الحالي: {current_balance:,} ل.س

📝 <b>أرسل المبلغ الذي تريد سحبه:</b>

📌 أرسل <code>/cancel</code> للإلغاء
    """, parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_ichancy_withdraw, username, current_balance)

def process_ichancy_withdraw(message, username, max_amount):
    uid = message.from_user.id
    
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            bot.reply_to(message, "❌ المبلغ يجب أن يكون أكبر من 0")
            return
        
        if amount > max_amount:
            bot.reply_to(message, f"❌ المبلغ يتجاوز رصيد حساب ICHANCY!\n💰 رصيدك: {max_amount:,} ل.س")
            return
        
        # خصم من حساب ICHANCY
        ichancy_accounts[username]["balance"] = ichancy_accounts[username].get("balance", 0) - amount
        save_ichancy_data()
        
        # إضافة إلى البوت
        add_balance(uid, amount)
        
        msg = f"""
✅ <b>تم السحب بنجاح!</b>
━━━━━━━━━━━━━━━━
📛 الحساب: <code>{username}</code>
💰 المبلغ المسحوب: {amount:,} ل.س
💳 رصيد حساب ICHANCY المتبقي: {ichancy_accounts[username]['balance']:,} ل.س
💰 رصيدك الجديد في البوت: {get_balance(uid):,} ل.س
        """
        bot.reply_to(message, msg, parse_mode="HTML")
        
    except ValueError:
        bot.reply_to(message, "❌ يرجى إدخال مبلغ صحيح")

# ================== إضافة API (خادم ويب يعمل بالتوازي) ==================
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

# إنشاء تطبيق Flask للـ API
api_app = Flask(__name__)
CORS(api_app)  # السماح للمواقع الخارجية بالاتصال

# دوال مساعدة للـ API
def get_ichancy_account_by_username(username):
    for acc_username, data in ichancy_accounts.items():
        if acc_username == username:
            return data
    return None

def get_ichancy_account_by_user_id(user_id):
    for username, data in ichancy_accounts.items():
        if data.get("user_id") == user_id:
            return {"username": username, **data}
    return None

# endpoints API
@api_app.route('/api/ichancy/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
    
    account = get_ichancy_account_by_username(username)
    
    if not account:
        return jsonify({'success': False, 'error': 'الحساب غير موجود'}), 404
    
    if account.get('password') != password:
        return jsonify({'success': False, 'error': 'كلمة المرور غير صحيحة'}), 401
    
    return jsonify({
        'success': True,
        'username': username,
        'balance': account.get('balance', 0),
        'user_id': account.get('user_id')
    })

@api_app.route('/api/ichancy/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    user_id = data.get('user_id')
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
    
    if len(username) < 3:
        return jsonify({'success': False, 'error': 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل'}), 400
    
    if len(password) < 3:
        return jsonify({'success': False, 'error': 'كلمة المرور يجب أن تكون 3 أحرف على الأقل'}), 400
    
    if username in ichancy_accounts:
        return jsonify({'success': False, 'error': 'اسم المستخدم موجود بالفعل'}), 409
    
    ichancy_accounts[username] = {
        "password": password,
        "user_id": user_id,
        "balance": 0
    }
    save_ichancy_data()
    
    return jsonify({
        'success': True,
        'username': username,
        'balance': 0,
        'user_id': user_id
    })

@api_app.route('/api/ichancy/balance', methods=['POST'])
def api_balance():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
    
    account = get_ichancy_account_by_username(username)
    
    if not account:
        return jsonify({'success': False, 'error': 'الحساب غير موجود'}), 404
    
    if account.get('password') != password:
        return jsonify({'success': False, 'error': 'كلمة المرور غير صحيحة'}), 401
    
    return jsonify({
        'success': True,
        'username': username,
        'balance': account.get('balance', 0)
    })

@api_app.route('/api/ichancy/update_balance', methods=['POST'])
def api_update_balance():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    amount = data.get('amount', 0)
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
    
    if amount == 0:
        return jsonify({'success': False, 'error': 'المبلغ يجب أن يكون غير صفري'}), 400
    
    account = get_ichancy_account_by_username(username)
    
    if not account:
        return jsonify({'success': False, 'error': 'الحساب غير موجود'}), 404
    
    if account.get('password') != password:
        return jsonify({'success': False, 'error': 'كلمة المرور غير صحيحة'}), 401
    
    current_balance = account.get('balance', 0)
    new_balance = current_balance + amount
    
    if new_balance < 0:
        return jsonify({'success': False, 'error': 'رصيد غير كافٍ'}), 400
    
    ichancy_accounts[username]['balance'] = new_balance
    save_ichancy_data()
    
    return jsonify({
        'success': True,
        'username': username,
        'old_balance': current_balance,
        'new_balance': new_balance,
        'amount_changed': amount
    })

@api_app.route('/api/ichancy/transfer_to_bot', methods=['POST'])
def api_transfer_to_bot():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    amount = data.get('amount', 0)
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
    
    if amount <= 0:
        return jsonify({'success': False, 'error': 'المبلغ يجب أن يكون أكبر من صفر'}), 400
    
    account = get_ichancy_account_by_username(username)
    
    if not account:
        return jsonify({'success': False, 'error': 'الحساب غير موجود'}), 404
    
    if account.get('password') != password:
        return jsonify({'success': False, 'error': 'كلمة المرور غير صحيحة'}), 401
    
    current_balance = account.get('balance', 0)
    
    if current_balance < amount:
        return jsonify({'success': False, 'error': f'رصيد غير كافٍ. رصيدك: {current_balance} ل.س'}), 400
    
    ichancy_accounts[username]['balance'] = current_balance - amount
    save_ichancy_data()
    
    user_id = account.get('user_id')
    if user_id:
        add_balance(user_id, amount)
    
    return jsonify({
        'success': True,
        'username': username,
        'withdrawn_amount': amount,
        'new_balance': ichancy_accounts[username]['balance']
    })

@api_app.route('/api/ichancy/transfer_from_bot', methods=['POST'])
def api_transfer_from_bot():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount', 0)
    
    if not user_id:
        return jsonify({'success': False, 'error': 'user_id مطلوب'}), 400
    
    if amount <= 0:
        return jsonify({'success': False, 'error': 'المبلغ يجب أن يكون أكبر من صفر'}), 400
    
    account_data = get_ichancy_account_by_user_id(user_id)
    
    if not account_data:
        return jsonify({'success': False, 'error': 'لا يوجد حساب ICHANCY مرتبط بهذا المستخدم'}), 404
    
    username = account_data['username']
    
    if get_balance(user_id) < amount:
        return jsonify({'success': False, 'error': f'رصيد غير كافٍ في البوت. رصيدك: {get_balance(user_id)} ل.س'}), 400
    
    sub_balance(user_id, amount)
    
    ichancy_accounts[username]['balance'] = ichancy_accounts[username].get('balance', 0) + amount
    save_ichancy_data()
    
    return jsonify({
        'success': True,
        'username': username,
        'deposited_amount': amount,
        'new_balance': ichancy_accounts[username]['balance'],
        'bot_balance': get_balance(user_id)
    })

@api_app.route('/api/ichancy/check_account', methods=['GET'])
def api_check_account():
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'success': False, 'error': 'user_id مطلوب'}), 400
    
    account_data = get_ichancy_account_by_user_id(user_id)
    
    if account_data:
        return jsonify({
            'success': True,
            'has_account': True,
            'username': account_data['username'],
            'balance': account_data.get('balance', 0)
        })
    else:
        return jsonify({
            'success': True,
            'has_account': False
        })

@api_app.route('/api/ichancy/health', methods=['GET'])
def api_health():
    return jsonify({
        'status': 'running',
        'bot_active': True,
        'ichancy_accounts': len(ichancy_accounts)
    })

# تشغيل API في خيط منفصل
def run_api():
    api_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()
print("✅ API يعمل على المنفذ 8080 (بالتوازي مع البوت)")

# ================== تشغيل البوت ==================

print("🤖 البوت الاحترافي يعمل مع جميع التعديلات...")
print(f"✅ نسبة الفوز الشاملة: {global_win_rate}%")
print(f"✅ ثمن اللعبة: {GAME_COST:,} ل.س")
print(f"✅ الحد الأدنى للسحب: {MINIMUM_WITHDRAWAL:,} ل.س")
print(f"✅ الفوز المخفي: {SECRET_WIN_AMOUNT:,} ل.س (مرة واحدة بعد الهدية - يظهر كفوز عادي)")
print(f"✅ نظام الأكواد: نشط (جائزة {TOTAL_CODES_PRIZE:,} ل.س للأكواد الرابحة)")
print(f"✅ قناة الاشتراك: {REQUIRED_CHANNEL}")
print(f"✅ نظام ICHANCY: نشط ({len(ichancy_accounts)} حساب)")
print(f"✅ API يعمل على المنفذ 8080")
print("=" * 60)
bot.infinity_polling()