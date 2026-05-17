import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import random
from datetime import datetime, timedelta
import json
import os
import time
import io
import secrets
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS

# ================== إعدادات Flask API ==================
app = Flask(__name__)
CORS(app)

API_PORT = 5000
API_SECRET_KEY = secrets.token_hex(32)  # مفتاح سري للتحقق من الطلبات

# تخزين طلبات الشحن من الموقع مؤقتاً
pending_website_charges = {}

# ================== الإعدادات الأساسية ==================

TOKEN = "8754401332:AAEnGyuieIxO4F-UmE7cvHXPA9x-DcSgeqA"
ADMIN_ID = 8399301540

# رابط الموقع (Web App)
WEBSITE_URL = "https://bot2030-bo.github.io/Inindex.html/"

# ================== إعدادات الاشتراك الإجباري ==================
REQUIRED_CHANNEL = "https://t.me/ichancycod"

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

# ================== متغيرات نظام الأكواد ==================
winning_codes = {}
losing_codes = []
used_codes = []
TOTAL_CODES_PRIZE = 6000

# ================== متغيرات نظام التحكم بالفوز ==================
global_win_rate = 30
win_prizes = {
    "0": 0,
    "1": 5000,
    "2": 5000,
    "3": 5000,
    "4": 40000,
    "5": 40000
}
DEFAULT_RATE = 1

# ================== متغيرات أخرى ==================
raffle_withdrawn = {}
pending_raffle_winner = None
user_reports_count = {}
MAX_REPORTS_PER_DAY = 3
first_play_secret_win = {}
SECRET_WIN_AMOUNT = 50000
FRUITS = ["🍒", "🍋", "🍉", "🍇", "🍎", "🍊"]
GAME_COST = 2500
WELCOME_GIFT = 5000
REFERRAL_REWARD_XP = 25
REFERRAL_REWARD_BALANCE = 5000
REQUIRED_REFERRALS = 3
RAFFLE_PRIZE = 500000
VIP_COST = 10000
MINIMUM_WITHDRAWAL = 80000

# ================== ملفات البيانات ==================
DATA_FILE = "bot_data.json"
WEBSITE_SYNC_FILE = "website_users.json"

# ================== متغيرات إضافية ==================
users_total_winnings = {}

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

# ================== دوال تحميل وحفظ البيانات ==================

def load_data():
    global balances, xp, levels, history, BARCODE_FILE_ID, BARCODE_FILE_ID_SYRIATEL, pending_charges, first_charge_done, welcome_gift_received, banned_from_welcome_gift
    global referrals, referral_codes, referral_rewards_claimed, raffle_entries, raffle_participants, VIP_USERS, AUTO_MESSAGE_TEXT, PROMO_PHONE_NUMBER
    global global_win_rate, win_prizes, DEFAULT_RATE, raffle_withdrawn, user_reports_count, first_play_secret_win, GAME_COST, MINIMUM_WITHDRAWAL
    global winning_codes, losing_codes, used_codes, users_total_winnings
    
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
            users_total_winnings = data.get('users_total_winnings', {})
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
        users_total_winnings = {}

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
        'used_codes': used_codes,
        'users_total_winnings': users_total_winnings
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

load_data()

# ================== دوال مزامنة الموقع ==================

def load_website_users():
    if os.path.exists(WEBSITE_SYNC_FILE):
        with open(WEBSITE_SYNC_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_website_users(users_data):
    with open(WEBSITE_SYNC_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

def get_website_balance(user_id):
    website_users = load_website_users()
    uid_str = str(user_id)
    return website_users.get(uid_str, {}).get('balance', 0)

def set_website_balance(user_id, amount):
    website_users = load_website_users()
    uid_str = str(user_id)
    if uid_str not in website_users:
        website_users[uid_str] = {}
    website_users[uid_str]['balance'] = amount
    save_website_users(website_users)

def add_website_balance(user_id, amount):
    new_bal = get_website_balance(user_id) + amount
    set_website_balance(user_id, new_bal)
    add_history(user_id, f"🌐 إضافة رصيد موقع +{amount:,} ل.س")
    return new_bal

def sub_website_balance(user_id, amount):
    current = get_website_balance(user_id)
    if current >= amount:
        new_bal = current - amount
        set_website_balance(user_id, new_bal)
        add_history(user_id, f"🌐 خصم رصيد موقع -{amount:,} ل.س")
        return True
    return False

def get_website_total_winnings(user_id):
    website_users = load_website_users()
    uid_str = str(user_id)
    return website_users.get(uid_str, {}).get('totalWinnings', 0)

def add_website_total_winnings(user_id, amount):
    website_users = load_website_users()
    uid_str = str(user_id)
    if uid_str not in website_users:
        website_users[uid_str] = {}
    current = website_users[uid_str].get('totalWinnings', 0)
    website_users[uid_str]['totalWinnings'] = current + amount
    save_website_users(website_users)

def sync_balance_with_website(user_id):
    website_users = load_website_users()
    uid_str = str(user_id)
    website_users[uid_str] = website_users.get(uid_str, {})
    website_users[uid_str]['balance'] = get_balance(user_id)
    website_users[uid_str]['totalWinnings'] = users_total_winnings.get(uid_str, 0)
    website_users[uid_str]['level'] = get_level(user_id)
    website_users[uid_str]['xp'] = get_xp(user_id)
    website_users[uid_str]['vip'] = is_vip(user_id)
    website_users[uid_str]['last_sync'] = datetime.now().isoformat()
    save_website_users(website_users)
    return True

def redeem_withdraw_code(user_id, code):
    website_users = load_website_users()
    uid_str = str(user_id)
    
    if not code.startswith("WTH"):
        return False, "❌ هذا الكود ليس كود سحب صالحاً!"
    
    for uid, user_data in website_users.items():
        if "withdraw_codes" in user_data:
            for withdraw_code in user_data["withdraw_codes"]:
                if withdraw_code.get("code") == code and not withdraw_code.get("used", False):
                    amount = withdraw_code.get("amount", 0)
                    withdraw_code["used"] = True
                    withdraw_code["used_at"] = datetime.now().isoformat()
                    save_website_users(website_users)
                    
                    add_balance(int(uid), amount)
                    add_history(int(uid), f"💰 سحب من الموقع: +{amount:,} ل.س (كود: {code})")
                    
                    return True, f"✅ تم سحب {amount:,} ل.س من الموقع بنجاح إلى رصيدك في البوت!"
    
    return False, "❌ الكود غير صالح أو تم استخدامه مسبقاً!"

def generate_withdraw_code():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    code = 'WTH'
    for i in range(12):
        code += chars[random.randint(0, len(chars) - 1)]
    return code

def generate_ichancy_charge_code():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    code = 'ICH'
    for i in range(10):
        code += chars[random.randint(0, len(chars) - 1)]
    return code

# ================== دوال أساسية ==================

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

def get_game_cost(uid):
    return GAME_COST // 2 if is_vip(uid) else GAME_COST

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
    add_history(uid, f"➕ إضافة رصيد بوت +{amount:,} ل.س")
    save_data()
    sync_balance_with_website(uid)
    check_first_charge(uid)

def sub_balance(uid, amount):
    uid_str = str(uid)
    if get_balance(uid) >= amount:
        balances[uid_str] -= amount
        add_history(uid, f"➖ خصم رصيد بوت -{amount:,} ل.س")
        save_data()
        sync_balance_with_website(uid)
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

def get_global_win_rate():
    return global_win_rate

def set_global_win_rate(new_rate):
    global global_win_rate
    global_win_rate = new_rate
    save_data()

def check_win(uid):
    rate = get_global_win_rate()
    win = random.randint(1, 100) <= rate
    
    if win:
        prize = win_prizes.get(str(rate), 5000)
        return True, prize
    return False, 0

def check_and_give_secret_win(uid):
    uid_str = str(uid)
    
    if welcome_gift_received.get(uid_str, False) and not first_play_secret_win.get(uid_str, False):
        first_play_secret_win[uid_str] = True
        add_balance(uid, SECRET_WIN_AMOUNT)
        add_history(uid, f"🎁 فوز مخفي! +{SECRET_WIN_AMOUNT:,} ل.س")
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

# ================== دوال نظام الأكواد ==================

def add_winning_codes(codes_list, total_prize=TOTAL_CODES_PRIZE):
    if not codes_list:
        return False, "لا توجد أكواد!"
    
    prize_per_code = total_prize // len(codes_list)
    
    for code in codes_list:
        code_upper = code.strip().upper()
        winning_codes[code_upper] = prize_per_code
    
    save_data()
    return True, f"✅ تم إضافة {len(codes_list)} كود رابح\n💰 قيمة كل كود: {prize_per_code:,} ل.س"

def add_losing_codes(codes_list):
    if not codes_list:
        return False, "لا توجد أكواد!"
    
    for code in codes_list:
        code_upper = code.strip().upper()
        if code_upper not in losing_codes and code_upper not in winning_codes:
            losing_codes.append(code_upper)
    
    save_data()
    return True, f"✅ تم إضافة {len(codes_list)} كود خاسر"

def clear_all_codes():
    global winning_codes, losing_codes, used_codes
    winning_codes.clear()
    losing_codes.clear()
    used_codes.clear()
    save_data()
    return True, "🗑️ تم مسح جميع الأكواد"

def redeem_code(user_id, code):
    code_upper = code.strip().upper()
    
    if code_upper in used_codes:
        return False, "⚠️ هذا الكود مستخدم من قبل!", 0
    
    if code_upper in winning_codes:
        prize = winning_codes[code_upper]
        used_codes.append(code_upper)
        del winning_codes[code_upper]
        save_data()
        return True, f"🎉 <b>تهانينا!</b>\n💰 لقد ربحت {prize:,} ل.س!", prize
    
    if code_upper in losing_codes:
        used_codes.append(code_upper)
        losing_codes.remove(code_upper)
        save_data()
        return False, "😢 <b>حظ أوفر!</b>\n💔 هذا الكود لم يفز هذه المرة!", 0
    
    return False, "❌ <b>كود غير صالح!</b>", 0

def get_codes_stats():
    return {
        "winning_count": len(winning_codes),
        "losing_count": len(losing_codes),
        "used_count": len(used_codes),
        "total_prize": sum(winning_codes.values())
    }

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

# ================== دوال التحقق من الاشتراك ==================

def check_subscription(user_id):
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

# ================== إنشاء الأزرار ==================

def get_main_keyboard(uid):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    balance_display = f"💰 {get_balance(uid):,} ل.س"
    level_display = f"⭐ Lv.{get_level(uid)}"
    game_cost_display = get_game_cost(uid)
    
    btn_balance = KeyboardButton(balance_display)
    btn_level = KeyboardButton(level_display)
    btn_games = KeyboardButton(f"🎮 الألعاب ({game_cost_display:,} ل.س) 🎮")
    btn_charge = KeyboardButton("💳 شحن الرصيد 💳")
    btn_referral = KeyboardButton("👥 نظام الدعوة 👥")
    btn_vip = KeyboardButton("👑 VIP 👑")
    btn_history = KeyboardButton("📜 سجل العمليات")
    btn_help = KeyboardButton("❓ المساعدة")
    btn_codes = KeyboardButton("👑 جائزة الأكواد")
    btn_website = KeyboardButton("🌐 الموقع الرسمي")
    btn_ichancy_charge = KeyboardButton("💎 شحن Ichancy 💎")
    btn_withdraw_code = KeyboardButton("🎫 إدخال كود سحب")
    btn_report = KeyboardButton(f"📞 إبلاغ المدير ({get_remaining_reports(uid)}/{MAX_REPORTS_PER_DAY})")
    
    btn_web_app = KeyboardButton(
        "🎡 افتح عجلة الحظ 🎡",
        web_app=WebAppInfo(url=WEBSITE_URL)
    )
    
    keyboard.row(btn_balance, btn_level)
    keyboard.row(btn_games, btn_charge)
    keyboard.row(btn_referral, btn_vip)
    keyboard.row(btn_history, btn_help)
    keyboard.row(btn_codes, btn_website)
    keyboard.row(btn_ichancy_charge, btn_withdraw_code)
    keyboard.row(btn_web_app)
    keyboard.row(btn_report)
    
    if is_admin(uid):
        btn_users_ids = KeyboardButton("🆔 قائمة IDs")
        btn_admin = KeyboardButton("👑 لوحة المدير")
        keyboard.row(btn_users_ids, btn_admin)
    
    return keyboard

def get_games_keyboard(uid):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    game_cost = get_game_cost(uid)
    vip_text = " (VIP 50% OFF)" if is_vip(uid) else ""
    
    btn_wheel = KeyboardButton(f"🎡 دولاب الحظ ({game_cost:,} ل.س){vip_text}")
    btn_dice = KeyboardButton(f"🎲 لعبة النرد ({game_cost:,} ل.س){vip_text}")
    btn_slots = KeyboardButton(f"🎰 سلوت الفواكه ({game_cost:,} ل.س){vip_text}")
    btn_back = KeyboardButton("🔙 رجوع للقائمة")
    keyboard.add(btn_wheel, btn_dice, btn_slots)
    keyboard.add(btn_back)
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
    btn_send_message = InlineKeyboardButton("📨 إرسال رسالة للجميع", callback_data="send_auto_message")
    btn_edit_message = InlineKeyboardButton("✏️ تعديل الرسالة", callback_data="edit_auto_message")
    btn_set_phone = InlineKeyboardButton("📞 تعيين رقم التحويل", callback_data="set_phone_number")
    btn_set_rate = InlineKeyboardButton("📊 تعيين نسبة الفوز", callback_data="set_global_rate")
    btn_show_rate = InlineKeyboardButton("📋 عرض نسبة الفوز", callback_data="show_global_rate")
    btn_all_balances = InlineKeyboardButton("💰 معرفة رصيد جميع المستخدمين", callback_data="all_users_balances")
    btn_reset_user = InlineKeyboardButton("🔄 تصفير رصيد مستخدم", callback_data="reset_single_balance")
    btn_reset_users = InlineKeyboardButton("🔄 تصفير رصيد مجموعة", callback_data="reset_multiple_balances")
    btn_upload_winning = InlineKeyboardButton("🏆 تحميل أكواد رابحة", callback_data="upload_winning_codes")
    btn_upload_losing = InlineKeyboardButton("💔 تحميل أكواد خاسرة", callback_data="upload_losing_codes")
    btn_clear_codes = InlineKeyboardButton("🗑️ مسح جميع الأكواد", callback_data="clear_all_codes")
    btn_codes_stats = InlineKeyboardButton("📊 إحصائيات الأكواد", callback_data="codes_stats")
    btn_distribute = InlineKeyboardButton("💰 توزيع مبلغ", callback_data="distribute_money")
    btn_send_to_id = InlineKeyboardButton("📨 إرسال رسالة لـ ID", callback_data="send_to_id")
    btn_send_photo_to_id = InlineKeyboardButton("🖼️ إرسال صورة لـ ID", callback_data="send_photo_to_id")
    btn_get_balance = InlineKeyboardButton("💰 معرفة رصيد مستخدم", callback_data="get_balance_user")
    btn_sync_website = InlineKeyboardButton("🌐 مزامنة مع الموقع", callback_data="sync_website")
    btn_website_stats = InlineKeyboardButton("📊 إحصائيات الموقع", callback_data="website_stats")
    
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
    keyboard.add(btn_sync_website, btn_website_stats)
    
    return keyboard

# ================== دوال معالجة الشحن ==================

@bot.callback_query_handler(func=lambda call: call.data == "charge_sham")
def charge_sham_callback(call):
    uid = call.from_user.id
    
    if not is_admin(uid) and not check_subscription(uid):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📢 اشترك في القناة", url=REQUIRED_CHANNEL))
        keyboard.add(InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_subscription"))
        
        bot.edit_message_text(
            f"🔒 <b>عذراً، لا يمكنك استخدام خدمة الشحن!</b>\n\n"
            f"📢 يجب عليك الاشتراك في قناتنا أولاً:\n"
            f"🔗 {REQUIRED_CHANNEL}\n\n"
            f"✅ بعد الاشتراك، اضغط على زر التحقق.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return
    
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
    
    if not is_admin(uid) and not check_subscription(uid):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📢 اشترك في القناة", url=REQUIRED_CHANNEL))
        keyboard.add(InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_subscription"))
        
        bot.edit_message_text(
            f"🔒 <b>عذراً، لا يمكنك استخدام خدمة الشحن!</b>\n\n"
            f"📢 يجب عليك الاشتراك في قناتنا أولاً:\n"
            f"🔗 {REQUIRED_CHANNEL}\n\n"
            f"✅ بعد الاشتراك، اضغط على زر التحقق.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return
    
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
    
    if not is_admin(uid) and not check_subscription(uid):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📢 اشترك في القناة", url=REQUIRED_CHANNEL))
        keyboard.add(InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_subscription"))
        
        bot.edit_message_text(
            f"🔒 <b>عذراً، لا يمكنك استخدام خدمة الشحن!</b>\n\n"
            f"📢 يجب عليك الاشتراك في قناتنا أولاً:\n"
            f"🔗 {REQUIRED_CHANNEL}\n\n"
            f"✅ بعد الاشتراك، اضغط على زر التحقق.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return
    
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
    
    if not is_admin(uid) and not check_subscription(uid):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📢 اشترك في القناة", url=REQUIRED_CHANNEL))
        keyboard.add(InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_subscription"))
        
        bot.edit_message_text(
            f"🔒 <b>عذراً، لا يمكنك استخدام خدمة الشحن!</b>\n\n"
            f"📢 يجب عليك الاشتراك في قناتنا أولاً:\n"
            f"🔗 {REQUIRED_CHANNEL}\n\n"
            f"✅ بعد الاشتراك، اضغط على زر التحقق.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        bot.answer_callback_query(call.id)
        return
    
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
💳 رصيد البوت الحالي: {get_balance(uid):,} ل.س

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

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main_callback(call):
    uid = call.from_user.id
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, "🔙 تم العودة", reply_markup=get_main_keyboard(uid))
    bot.answer_callback_query(call.id)

# ================== زر شحن Ichancy ==================

@bot.message_handler(func=lambda message: message.text == "💎 شحن Ichancy 💎")
@require_subscription
def ichancy_charge_start(message):
    uid = message.from_user.id
    
    msg = """
💎 <b>شحن رصيد Ichancy</b>
━━━━━━━━━━━━━━━━

📝 <b>أدخل المبلغ الذي تريد شحنه إلى الموقع</b>

💰 الحد الأدنى: 1,000 ل.س
💰 الحد الأقصى: 500,000 ل.س

📌 <b>ملاحظة:</b> سيتم خصم المبلغ من رصيد البوت وإضافته إلى رصيدك في الموقع

📌 أرسل <code>/cancel</code> للإلغاء
"""
    
    bot.reply_to(message, msg, parse_mode="HTML")
    bot.register_next_step_handler(message, process_ichancy_charge)

def process_ichancy_charge(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    uid = message.from_user.id
    
    try:
        amount = int(message.text.strip())
        
        if amount < 1000:
            bot.reply_to(message, "❌ الحد الأدنى للشحن 1,000 ل.س")
            return
        
        if amount > 500000:
            bot.reply_to(message, "❌ الحد الأقصى للشحن 500,000 ل.س")
            return
        
        if get_balance(uid) < amount:
            bot.reply_to(message, f"❌ رصيدك غير كافٍ!\n💰 رصيدك الحالي: {get_balance(uid):,} ل.س\n💰 المبلغ المطلوب: {amount:,} ل.س")
            return
        
        sub_balance(uid, amount)
        add_website_balance(uid, amount)
        charge_code = generate_ichancy_charge_code()
        
        website_users = load_website_users()
        uid_str = str(uid)
        if uid_str not in website_users:
            website_users[uid_str] = {}
        if 'ichancy_charges' not in website_users[uid_str]:
            website_users[uid_str]['ichancy_charges'] = []
        
        website_users[uid_str]['ichancy_charges'].append({
            'amount': amount,
            'date': datetime.now().isoformat(),
            'code': charge_code,
            'used': False
        })
        save_website_users(website_users)
        
        msg = f"""
✅ <b>تم شحن رصيد Ichancy بنجاح!</b>
━━━━━━━━━━━━━━━━
💰 المبلغ المشحون: {amount:,} ل.س
🎫 كود الشحن: <code>{charge_code}</code>
━━━━━━━━━━━━━━━━
📌 تم خصم {amount:,} ل.س من رصيد البوت
📌 تم إضافة {amount:,} ل.س إلى رصيدك في الموقع

🌐 <b>لفتح الموقع:</b> اضغط على زر "🎡 افتح عجلة الحظ 🎡"
"""
        
        bot.reply_to(message, msg, parse_mode="HTML")
        add_history(uid, f"💎 شحن Ichancy: +{amount:,} ل.س إلى الموقع")
        
    except ValueError:
        bot.reply_to(message, "❌ يرجى إدخال مبلغ صحيح (أرقام فقط)")

# ================== زر إدخال كود سحب ==================

@bot.message_handler(func=lambda message: message.text == "🎫 إدخال كود سحب")
@require_subscription
def withdraw_code_menu(message):
    msg = bot.send_message(message.chat.id, """
🎫 <b>إدخال كود السحب من الموقع</b>

📝 أرسل الكود الذي حصلت عليه من الموقع

مثال: <code>WTHABC123XYZ</code>

📌 أرسل <code>/cancel</code> للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_withdraw_code)

def process_withdraw_code(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    uid = message.from_user.id
    code = message.text.strip().upper()
    
    success, msg_result = redeem_withdraw_code(uid, code)
    bot.reply_to(message, msg_result, parse_mode="HTML")

# ================== معالج Web App Data ==================

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    user_id = message.from_user.id
    
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get('action')
        callback_id = data.get('callbackId', str(time.time()))
        
        print(f"📱 Web App Data from {user_id}: {action}")
        
        if action == 'get_stats':
            response = {
                'status': 'success',
                'callbackId': callback_id,
                'balance': get_website_balance(user_id),
                'totalWinnings': get_website_total_winnings(user_id),
                'level': get_level(user_id),
                'xp': get_xp(user_id),
                'vip': is_vip(user_id),
                'winRate': get_global_win_rate()
            }
            bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
            print(f"✅ تم إرسال إحصائيات الموقع للمستخدم {user_id}: رصيد={response['balance']}")
        
        elif action == 'deduct_bet':
            amount = data.get('amount', 0)
            if amount <= 0:
                response = {'status': 'error', 'message': 'مبلغ غير صالح', 'callbackId': callback_id}
            elif sub_website_balance(user_id, amount):
                response = {
                    'status': 'success', 
                    'new_balance': get_website_balance(user_id),
                    'callbackId': callback_id
                }
                print(f"✅ تم خصم {amount} من رصيد موقع المستخدم {user_id}")
            else:
                response = {
                    'status': 'error', 
                    'message': 'رصيد غير كافٍ', 
                    'new_balance': get_website_balance(user_id),
                    'callbackId': callback_id
                }
                print(f"❌ فشل خصم {amount} - رصيد موقع غير كافٍ")
            bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
        
        elif action == 'add_winnings':
            prize = data.get('prize', 0)
            if prize > 0:
                add_website_balance(user_id, prize)
                add_website_total_winnings(user_id, prize)
                response = {
                    'status': 'success', 
                    'new_balance': get_website_balance(user_id),
                    'prize': prize,
                    'callbackId': callback_id
                }
                print(f"✅ تم إضافة جائزة {prize} لموقع المستخدم {user_id}")
            else:
                response = {
                    'status': 'success', 
                    'new_balance': get_website_balance(user_id),
                    'callbackId': callback_id
                }
            bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
        
        elif action == 'withdraw':
            amount = data.get('amount', 0)
            
            if amount < 1000:
                response = {'status': 'error', 'message': 'الحد الأدنى للسحب 1000 ل.س', 'callbackId': callback_id}
                bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
                return
            
            if sub_website_balance(user_id, amount):
                withdraw_code = generate_withdraw_code()
                
                website_users = load_website_users()
                uid_str = str(user_id)
                if uid_str not in website_users:
                    website_users[uid_str] = {}
                if 'withdraw_codes' not in website_users[uid_str]:
                    website_users[uid_str]['withdraw_codes'] = []
                
                website_users[uid_str]['withdraw_codes'].append({
                    'code': withdraw_code,
                    'amount': amount,
                    'date': datetime.now().isoformat(),
                    'used': False
                })
                save_website_users(website_users)
                
                response = {
                    'status': 'success',
                    'withdraw_code': withdraw_code,
                    'amount': amount,
                    'new_balance': get_website_balance(user_id),
                    'callbackId': callback_id
                }
                bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
                print(f"✅ تم سحب {amount} من موقع المستخدم {user_id} - كود: {withdraw_code}")
                
                bot.send_message(user_id, f"""
💸 <b>تم سحب الرصيد من الموقع</b>
━━━━━━━━━━━━━━━━
💰 المبلغ: {amount:,} ل.س
🎫 كود السحب: <code>{withdraw_code}</code>
━━━━━━━━━━━━━━━━
📌 استخدم هذا الكود في البوت لاستلام الرصيد (زر "🎫 إدخال كود سحب")
""", parse_mode="HTML")
            else:
                response = {
                    'status': 'error', 
                    'message': f'رصيدك غير كافٍ! رصيدك: {get_website_balance(user_id):,} ل.س',
                    'current_balance': get_website_balance(user_id),
                    'callbackId': callback_id
                }
                bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
                print(f"❌ رصيد موقع غير كافٍ للمستخدم {user_id}")
        
        elif action == 'set_winrate':
            if is_admin(user_id):
                new_rate = data.get('winrate', 0)
                if 0 <= new_rate <= 100:
                    set_global_win_rate(new_rate)
                    response = {'status': 'success', 'winrate': new_rate, 'callbackId': callback_id}
                    print(f"✅ تم تغيير نسبة الفوز إلى {new_rate}% بواسطة المدير")
                else:
                    response = {'status': 'error', 'message': 'النسبة يجب أن تكون بين 0 و 100', 'callbackId': callback_id}
            else:
                response = {'status': 'error', 'message': 'غير مصرح', 'callbackId': callback_id}
            bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
        
        elif action == 'request_charge':
            amount = data.get('amount', 0)
            phone = data.get('phone', '')
            
            if amount <= 0:
                response = {'status': 'error', 'message': 'مبلغ غير صالح', 'callbackId': callback_id}
                bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
                return
            
            charge_id = f"WEB_{user_id}_{int(time.time())}"
            pending_website_charges[charge_id] = {
                'user_id': user_id,
                'amount': amount,
                'phone': phone,
                'timestamp': datetime.now().isoformat()
            }
            
            # إرسال إشعار للمدير
            admin_msg = f"""
🔔 <b>طلب شحن جديد من الموقع!</b>
━━━━━━━━━━━━━━━━
👤 <b>المستخدم:</b> <a href="tg://user?id={user_id}">{user_id}</a>
💰 <b>المبلغ:</b> {amount:,} ل.س
📞 <b>رقم الهاتف:</b> <code>{phone}</code>
🆔 <b>رقم الطلب:</b> <code>{charge_id}</code>
⏰ <b>الوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━
📌 <b>طريقة الشحن:</b> شحن رصيد الموقع
            """
            
            try:
                bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
                
                # إرسال تأكيد للمستخدم
                response = {
                    'status': 'success',
                    'message': f'تم استلام طلب شحن {amount:,} ل.س بنجاح! سيتم معالجته قريباً',
                    'callbackId': callback_id
                }
                bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
                
                bot.send_message(user_id, f"""
✅ <b>تم استلام طلب شحنك!</b>
━━━━━━━━━━━━━━━━
💰 المبلغ: {amount:,} ل.س
📞 رقم الهاتف: {phone}
🆔 رقم الطلب: {charge_id}
━━━━━━━━━━━━━━━━
📌 سيتم إشعارك عند معالجة الطلب
""", parse_mode="HTML")
                
                add_history(user_id, f"🌐 طلب شحن من الموقع: {amount:,} ل.س (رقم: {phone})")
                
            except Exception as e:
                print(f"❌ خطأ في إرسال إشعار الشحن: {e}")
                response = {
                    'status': 'error',
                    'message': 'حدث خطأ في معالجة الطلب',
                    'callbackId': callback_id
                }
                bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
        
        else:
            response = {'status': 'error', 'message': f'إجراء غير معروف: {action}', 'callbackId': callback_id}
            bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
            print(f"❌ إجراء غير معروف: {action}")
            
    except Exception as e:
        print(f"❌ خطأ في معالج web_app_data: {e}")
        response = {'status': 'error', 'message': str(e)}
        try:
            bot.answer_web_app_query(message.web_app_data.query_id, json.dumps(response))
        except:
            pass

# ================== أوامر البوت ==================

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    
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
                referral_msg = f"\n🎉 <b>تم تسجيلك عن طريق دعوة!</b>"
                
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

🎮 <b>البوت الاحترافي Ichancy</b>
━━━━━━━━━━━━━━━━
💰 <b>رصيد البوت:</b> {get_balance(uid):,} ل.س
💰 <b>رصيد الموقع:</b> {get_website_balance(uid):,} ل.س
⭐ <b>مستواك:</b> {get_level(uid)}
✨ <b>نقاط XP:</b> {get_xp(uid)}
{gift_msg}
{referral_msg}
━━━━━━━━━━━━━━━━
🎮 <b>طريقة اللعب:</b>
• اضغط على زر "🎡 افتح عجلة الحظ 🎡" للعب مباشرة في الموقع
• استخدم "💎 شحن Ichancy" لشحن رصيد الموقع
• استخدم الألعاب داخل البوت للربح من رصيد البوت

🔥 استمتع واربح مع Ichancy!
    """
    
    bot.reply_to(message, welcome_msg, reply_markup=get_main_keyboard(uid))

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

@bot.message_handler(func=lambda message: message.text == "❓ المساعدة")
@require_subscription
def show_help(message):
    uid = message.from_user.id
    game_cost = get_game_cost(uid)
    vip_text = " (VIP 50% OFF)" if is_vip(uid) else ""
    
    help_msg = f"""
❓ <b>المساعدة والدعم</b>
━━━━━━━━━━━━━━━━

🎮 <b>الألعاب داخل البوت:</b>
• ثمن اللعبة: {game_cost:,} ل.س{vip_text}
• أرباح تصل إلى 50,000 ل.س في اللعبة الواحدة

🌐 <b>الموقع الإلكتروني (عجلة الحظ):</b>
• اضغط على زر "🎡 افتح عجلة الحظ 🎡"
• رصيد الموقع منفصل عن رصيد البوت
• لشحن رصيد الموقع: استخدم "💎 شحن Ichancy"

━━━━━━━━━━━━━━━━
👑 <b>نظام VIP:</b>
• اشتراك شهري: {VIP_COST:,} ل.س
• XP مضاعف + 5 تذاكر سحب + خصم 50%

━━━━━━━━━━━━━━━━
👥 <b>نظام الدعوة:</b>
• دعوة {REQUIRED_REFERRALS} أشخاص
• مكافأة: {REFERRAL_REWARD_BALANCE:,} ل.س + {REFERRAL_REWARD_XP} XP

━━━━━━━━━━━━━━━━
💰 <b>سحب الرصيد:</b>
• من البوت: الحد الأدنى {MINIMUM_WITHDRAWAL:,} ل.س
• من الموقع: عبر كود WTH (الحد الأدنى 1000 ل.س)

💎 <b>شحن Ichancy:</b>
• يشحن رصيد الموقع فقط (يخصم من رصيد البوت)
"""
    bot.reply_to(message, help_msg, reply_markup=get_main_keyboard(uid), parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "💳 شحن الرصيد 💳")
@require_subscription
def charge_start(message):
    uid = message.from_user.id
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📱 شام كاش", callback_data="charge_sham"),
        InlineKeyboardButton("📱 سيرياتيل كاش", callback_data="charge_syriatel"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
    )
    
    msg = """
💳 <b>شحن رصيد البوت</b>

اختر طريقة الدفع المناسبة لك:

📱 <b>شام كاش</b>
📱 <b>سيرياتيل كاش</b>

━━━━━━━━━━━━━━━━
💰 الحد الأدنى: 1,000 ل.س
💰 الحد الأقصى: 100,000 ل.س
🎁 أول شحن: 50 XP + 5 تذاكر سحب!
    """
    bot.reply_to(message, msg, reply_markup=keyboard, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "👥 نظام الدعوة 👥")
@require_subscription
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
        msg = f"👥 <b>قائمة المدعوين ({count})</b>\n━━━━━━━━━━━━━━━━\n"
        for i, ref_id in enumerate(refs[-20:], 1):
            msg += f"{i}. <code>{ref_id}</code>\n"
        
        if count > 20:
            msg += f"\n... و {count - 20} آخرين"
    
    bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "claim_referral_reward")
def claim_referral_reward_callback(call):
    uid = call.from_user.id
    count = get_referral_count(uid)
    
    if referral_rewards_claimed.get(str(uid), False):
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

@bot.message_handler(func=lambda message: message.text == "👑 VIP 👑")
@require_subscription
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
• 💰 خصم 50% على ثمن الألعاب (الآن {get_game_cost(uid):,} ل.س)
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
• 💰 خصم 50% على ثمن الألعاب (من {GAME_COST:,} إلى {GAME_COST//2:,} ل.س)
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
💎 ثمن الألعاب الآن: {get_game_cost(uid):,} ل.س (50% خصم)
━━━━━━━━━━━━━━━━
استمتع بمزاياك الحصرية! 👑
    """
    
    bot.send_message(call.message.chat.id, success_msg, reply_markup=get_main_keyboard(uid), parse_mode="HTML")
    add_history(uid, f"👑 اشترك في VIP لمدة 30 يوم")
    bot.answer_callback_query(call.id, "✅ تم الاشتراك بنجاح!", show_alert=True)

@bot.message_handler(func=lambda message: message.text == "🌐 الموقع الرسمي")
@require_subscription
def website_link(message):
    uid = message.from_user.id
    
    msg = f"""
🌐 <b>الموقع الرسمي Ichancy</b>
━━━━━━━━━━━━━━━━

🎡 <b>رابط الموقع:</b>
<code>{WEBSITE_URL}</code>

━━━━━━━━━━━━━━━━
📌 <b>مميزات الموقع:</b>
• 🎡 عجلة الحظ التفاعلية
• 💰 سحب الأرباح مباشرة للبوت
• 🎫 أكواد ربح يومية
• 📊 إحصائيات دقيقة
• 💳 طلب شحن مباشر من الموقع

━━━━━━━━━━━━━━━━
💡 <b>طريقة أسهل:</b>
اضغط على زر "🎡 افتح عجلة الحظ 🎡" في القائمة الرئيسية
    """
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🌐 افتح الموقع", url=WEBSITE_URL))
    
    bot.reply_to(message, msg, reply_markup=keyboard, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "👑 جائزة الأكواد")
@require_subscription
def codes_prize_menu(message):
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

@bot.message_handler(func=lambda message: message.text == "📜 سجل العمليات")
@require_subscription
def show_history(message):
    uid = message.from_user.id
    logs = history.get(str(uid), [])
    if not logs:
        bot.reply_to(message, "📭 لا يوجد سجل عمليات بعد.", reply_markup=get_main_keyboard(uid))
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
    bot.reply_to(message, msg, reply_markup=get_main_keyboard(uid), parse_mode="HTML")

# ================== الألعاب ==================

@bot.message_handler(func=lambda message: message.text and message.text.startswith("🎮 الألعاب"))
@require_subscription
def show_games(message):
    uid = message.from_user.id
    cost = get_game_cost(uid)
    vip_text = " (خصم VIP 50%)" if is_vip(uid) else ""
    
    games_msg = f"""
🎮 <b>قائمة الألعاب المتاحة:</b>

🎡 <b>دولاب الحظ</b>
└ ثمن اللعبة: {cost:,} ل.س{vip_text}
└ جائزة: تصل إلى 50,000 ل.س
└ XP: +25 (فوز) / +5 (خسارة)

🎲 <b>لعبة النرد</b>
└ ثمن اللعبة: {cost:,} ل.س{vip_text}
└ جائزة: تصل إلى 50,000 ل.س
└ XP: +20 (فوز) / +5 (خسارة)

🎰 <b>سلوت الفواكه</b>
└ ثمن اللعبة: {cost:,} ل.س{vip_text}
└ جائزة: تصل إلى 50,000 ل.س
└ XP: +30 (فوز) / +5 (خسارة)

━━━━━━━━━━━━━━━━
💰 رصيد البوت الحالي: {get_balance(message.from_user.id):,} ل.س
🎯 اختر اللعبة وابدأ اللعب!
    """
    bot.reply_to(message, games_msg, reply_markup=get_games_keyboard(uid), parse_mode="HTML")

def play_game(message, game_name, xp_amount, result_msg_func):
    uid = message.from_user.id
    cost = get_game_cost(uid)
    
    if get_balance(uid) < cost:
        bot.reply_to(message, f"❌ رصيدك غير كافٍ!\n💰 رصيدك: {get_balance(uid):,} ل.س\n💸 ثمن اللعبة: {cost:,} ل.س", reply_markup=get_games_keyboard(uid))
        return
    
    sub_balance(uid, cost)
    check_and_give_secret_win(uid)
    
    win, prize = check_win(uid)
    
    if win:
        add_balance(uid, prize)
        leveled_up = add_xp(uid, xp_amount)
        result_msg = result_msg_func(True, prize, cost, xp_amount, leveled_up, uid)
        bot.send_message(message.chat.id, result_msg, reply_markup=get_games_keyboard(uid), parse_mode="HTML")
    else:
        add_xp(uid, 5)
        result_msg = result_msg_func(False, 0, cost, 5, False, uid)
        bot.send_message(message.chat.id, result_msg, reply_markup=get_games_keyboard(uid), parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text and ("دولاب الحظ" in message.text))
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
💰 رصيد البوت الآن: {get_balance(uid):,} ل.س
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
💰 رصيد البوت: {get_balance(uid):,} ل.س
💪 جرب حظك مرة أخرى!
"""
    play_game(message, "wheel", 25, wheel_result)

@bot.message_handler(func=lambda message: message.text and ("لعبة النرد" in message.text))
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
💰 رصيد البوت الآن: {get_balance(uid):,} ل.س
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
💰 رصيد البوت: {get_balance(uid):,} ل.س
💪 جرب حظك مرة أخرى!
"""
    play_game(message, "dice", 20, dice_result)

@bot.message_handler(func=lambda message: message.text and ("سلوت الفواكه" in message.text))
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
💰 رصيد البوت الآن: {get_balance(uid):,} ل.س
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
💰 رصيد البوت: {get_balance(uid):,} ل.س
💪 جرب حظك مرة أخرى!
"""
    play_game(message, "slots", 30, slots_result)

@bot.message_handler(func=lambda message: message.text == "🔙 رجوع للقائمة")
def back_to_main_menu(message):
    uid = message.from_user.id
    bot.reply_to(message, "🔙 تم العودة للقائمة الرئيسية", reply_markup=get_main_keyboard(uid))

@bot.message_handler(func=lambda message: message.text == "💰" or message.text.startswith("💰"))
def show_balance(message):
    uid = message.from_user.id
    vip_status = "👑 VIP" if is_vip(uid) else "👤 عادي"
    msg = f"""
╭━━━━━━━━━━━━━━╮
┃ 💰 <b>الرصيد الحالي</b>
╰━━━━━━━━━━━━━━╯

┏━━━━━━━━━━━━━━┓
┃ 💵 <b>رصيد البوت: {get_balance(uid):,}</b> ل.س
┃ 🌐 <b>رصيد الموقع: {get_website_balance(uid):,}</b> ل.س
┗━━━━━━━━━━━━━━┛

⭐ المستوى: {get_level(uid)}
✨ XP: {get_xp(uid)}
{vip_status}
    """
    bot.reply_to(message, msg, reply_markup=get_main_keyboard(uid), parse_mode="HTML")

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
    bot.reply_to(message, msg, reply_markup=get_main_keyboard(uid), parse_mode="HTML")

# ================== الإبلاغ للمدير ==================

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
• رصيد البوت: {get_balance(uid):,} ل.س
• رصيد الموقع: {get_website_balance(uid):,} ل.س
• مستوى: {get_level(uid)}
• عدد الإبلاغات اليوم: {count}/{MAX_REPORTS_PER_DAY}
    """
    
    try:
        bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
        bot.reply_to(message, f"✅ تم إرسال إبلاغك للمدير!\n📊 متبقي لك اليوم: {remaining} إبلاغات")
        add_history(uid, f"📞 أرسل إبلاغ للمدير - المبلغ: {amount:,} ل.س")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل إرسال الإبلاغ: {e}")

# ================== قائمة IDs ولوحة المدير ==================

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
    
    website_users = load_website_users()
    total_website_balance = sum(u.get('balance', 0) for u in website_users.values())
    
    stats_msg = f"""
👑 <b>لوحة تحكم المدير</b>
━━━━━━━━━━━━━━━━
📊 <b>إحصائيات البوت:</b>
• 👥 المستخدمين: {total_users}
• 💰 إجمالي رصيد البوت: {total_balance:,} ل.س
• 🌐 إجمالي رصيد الموقع: {total_website_balance:,} ل.س
• ⭐ إجمالي XP: {total_xp}
• 🎁 مستلمي الهدية: {gift_users}
• 🚫 المحظورين: {banned_users}
• 👥 الدعوات: {total_referrals}
• 👑 VIP: {vip_count}
    """
    bot.reply_to(message, stats_msg, reply_markup=get_admin_keyboard(), parse_mode="HTML")

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
    
    website_users = load_website_users()
    total_website_balance = sum(u.get('balance', 0) for u in website_users.values())
    
    codes_stats = get_codes_stats()
    
    stats_msg = f"""
📊 <b>إحصائيات البوت</b>
━━━━━━━━━━━━━━━━
👥 المستخدمين: {total_users}
💰 إجمالي رصيد البوت: {total_balance:,} ل.س
🌐 إجمالي رصيد الموقع: {total_website_balance:,} ل.س
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
    
    file = io.BytesIO(json.dumps({
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
        'used_codes': used_codes
    }, ensure_ascii=False, indent=2).encode('utf-8'))
    file.name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    bot.send_document(call.message.chat.id, file, caption="💾 نسخة احتياطية")
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
⚠️ سيتم استبدال جميع البيانات الحالية

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

        global balances, xp, levels, history, BARCODE_FILE_ID, BARCODE_FILE_ID_SYRIATEL
        global pending_charges, first_charge_done, welcome_gift_received
        global banned_from_welcome_gift, referrals, referral_codes
        global referral_rewards_claimed, raffle_entries, raffle_participants, VIP_USERS
        global AUTO_MESSAGE_TEXT, PROMO_PHONE_NUMBER
        global global_win_rate, win_prizes, DEFAULT_RATE, raffle_withdrawn, user_reports_count, first_play_secret_win, GAME_COST, MINIMUM_WITHDRAWAL
        global winning_codes, losing_codes, used_codes

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

        save_data()

        del pending_restore_files[user_id]

        bot.delete_message(wait_msg.chat.id, wait_msg.message_id)

        total_users = len(balances)
        total_balance = sum(balances.values())

        success_msg = f"""
✅ <b>تمت استعادة النسخة الاحتياطية بنجاح!</b>
━━━━━━━━━━━━━━━━
📊 <b>إحصائيات البيانات المستعادة:</b>
• 👥 عدد المستخدمين: {total_users}
• 💰 إجمالي الرصيد: {total_balance:,} ل.س
• ⭐ إجمالي XP: {sum(xp.values())}
• 👑 أعضاء VIP: {len(VIP_USERS)}
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
        users_list.append(f"🆔 {uid_str} | 💰 رصيد البوت: {balance:,} ل.س | 🌐 رصيد الموقع: {get_website_balance(int(uid_str)):,} ل.س")
        total_balance += balance
    
    users_list_sorted = sorted(users_list, key=lambda x: int(x.split("|")[0].split("🆔")[1].strip()))
    
    msg = f"""
💰 <b>رصيد جميع المستخدمين</b>
━━━━━━━━━━━━━━━━
👥 عدد المستخدمين: {len(users_list)}
💰 إجمالي رصيد البوت: {total_balance:,} ل.س
━━━━━━━━━━━━━━━━
""" + "\n".join(users_list_sorted[:100])
    
    if len(msg) > 4000:
        file_content = "\n".join([f"ID: {uid_str} | رصيد البوت: {balance:,} | رصيد الموقع: {get_website_balance(int(uid_str)):,}" for uid_str, balance in balances.items()])
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
        
        add_history(uid, f"🔄 تم تصفير رصيد البوت من {old_balance:,} ل.س إلى 0 (بواسطة المدير)")
        
        try:
            bot.send_message(uid, f"⚠️ <b>تم تصفير رصيد البوت إلى 0 ل.س</b>\n💰 رصيدك السابق: {old_balance:,} ل.س\n📞 للاستفسار، تواصل مع المدير.", parse_mode="HTML")
        except:
            pass
        
        bot.reply_to(message, f"✅ تم تصفير رصيد البوت للمستخدم {uid}\n💰 الرصيد السابق: {old_balance:,} ل.س\n💰 الرصيد الحالي: 0 ل.س")
        
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
                    bot.send_message(uid, f"⚠️ <b>تم تصفير رصيد البوت إلى 0 ل.س</b>\n💰 رصيدك السابق: {old_balance:,} ل.س", parse_mode="HTML")
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

@bot.callback_query_handler(func=lambda call: call.data == "upload_winning_codes")
def upload_winning_codes_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, f"""
🏆 <b>تحميل أكواد رابحة</b>

📁 أرسل ملف JSON يحتوي على قائمة الأكواد الرابحة

📝 <b>تنسيق الملف:</b>
<code>["CODE123", "CODE456", "CODE789"]</code>

💰 سيتم توزيع {TOTAL_CODES_PRIZE:,} ل.س على هذه الأكواد بالتساوي

📌 أرسل /cancel للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_winning_codes_file)

def process_winning_codes_file(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    if not message.document:
        bot.reply_to(message, "❌ يرجى إرسال ملف JSON")
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        text = downloaded_file.decode('utf-8')
        codes_list = json.loads(text)
        
        if not isinstance(codes_list, list):
            bot.reply_to(message, "❌ الملف يجب أن يحتوي على قائمة (array) من الأكواد")
            return
        
        success, msg_result = add_winning_codes(codes_list, TOTAL_CODES_PRIZE)
        bot.reply_to(message, msg_result)
        
        if success:
            add_history(message.from_user.id, f"🏆 أضاف {len(codes_list)} كود رابح")
            
    except json.JSONDecodeError:
        bot.reply_to(message, "❌ ملف JSON غير صالح")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "upload_losing_codes")
def upload_losing_codes_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, """
💔 <b>تحميل أكواد خاسرة</b>

📁 أرسل ملف JSON يحتوي على قائمة الأكواد الخاسرة

📝 <b>تنسيق الملف:</b>
<code>["LOSE1", "LOSE2", "LOSE3"]</code>

💡 عند استخدام هذه الأكواد، تظهر رسالة "حظ أوفر"

📌 أرسل /cancel للإلغاء
""", parse_mode="HTML")
    
    bot.register_next_step_handler(msg, process_losing_codes_file)

def process_losing_codes_file(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ تم الإلغاء")
        return
    
    if not message.document:
        bot.reply_to(message, "❌ يرجى إرسال ملف JSON")
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        text = downloaded_file.decode('utf-8')
        codes_list = json.loads(text)
        
        if not isinstance(codes_list, list):
            bot.reply_to(message, "❌ الملف يجب أن يحتوي على قائمة (array) من الأكواد")
            return
        
        success, msg_result = add_losing_codes(codes_list)
        bot.reply_to(message, msg_result)
        
        if success:
            add_history(message.from_user.id, f"💔 أضاف {len(codes_list)} كود خاسر")
            
    except json.JSONDecodeError:
        bot.reply_to(message, "❌ ملف JSON غير صالح")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "clear_all_codes")
def clear_all_codes_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ نعم، امسح الكل", callback_data="confirm_clear_codes"),
        InlineKeyboardButton("❌ إلغاء", callback_data="cancel_clear_codes")
    )
    
    stats = get_codes_stats()
    bot.edit_message_text(
        f"🗑️ <b>تحذير: مسح جميع الأكواد</b>\n\n"
        f"📊 <b>الإحصائيات الحالية:</b>\n"
        f"🏆 أكواد رابحة: {stats['winning_count']}\n"
        f"💔 أكواد خاسرة: {stats['losing_count']}\n"
        f"✅ أكواد مستخدمة: {stats['used_count']}\n"
        f"💰 جوائز متبقية: {stats['total_prize']:,} ل.س\n\n"
        f"⚠️ هل أنت متأكد من رغبتك في مسح جميع الأكواد؟",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_clear_codes")
def confirm_clear_codes(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    success, msg = clear_all_codes()
    bot.edit_message_text(
        f"✅ {msg}",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML"
    )
    add_history(call.from_user.id, "🗑️ قام بمسح جميع الأكواد")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_clear_codes")
def cancel_clear_codes(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "❌ تم إلغاء عملية المسح")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "codes_stats")
def codes_stats_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    stats = get_codes_stats()
    
    winning_list = ""
    if winning_codes:
        items = list(winning_codes.items())[:30]
        winning_list = "\n".join([f"• <code>{code}</code> | 💰 {prize:,} ل.س" for code, prize in items])
        if len(winning_codes) > 30:
            winning_list += f"\n... و {len(winning_codes) - 30} أخرى"
    else:
        winning_list = "لا يوجد"
    
    losing_list = ""
    if losing_codes:
        items = losing_codes[:30]
        losing_list = "\n".join([f"• <code>{code}</code>" for code in items])
        if len(losing_codes) > 30:
            losing_list += f"\n... و {len(losing_codes) - 30} أخرى"
    else:
        losing_list = "لا يوجد"
    
    msg = f"""
📊 <b>إحصائيات نظام الأكواد</b>
━━━━━━━━━━━━━━━━

🏆 <b>الأكواد الرابحة:</b>
• العدد: {stats['winning_count']}
• إجمالي الجوائز: {stats['total_prize']:,} ل.س

💔 <b>الأكواد الخاسرة:</b>
• العدد: {stats['losing_count']}

✅ <b>الأكواد المستخدمة:</b>
• العدد: {stats['used_count']}

━━━━━━━━━━━━━━━━
🏆 <b>قائمة الأكواد الرابحة:</b>
{winning_list}

━━━━━━━━━━━━━━━━
💔 <b>قائمة الأكواد الخاسرة:</b>
{losing_list}
    """
    
    if len(msg) > 4000:
        file_content = f"الأكواد الرابحة:\n" + "\n".join([f"{code}: {prize}" for code, prize in winning_codes.items()])
        file_content += f"\n\nالأكواد الخاسرة:\n" + "\n".join(losing_codes)
        file_content += f"\n\nالأكواد المستخدمة:\n" + "\n".join(used_codes)
        file = io.BytesIO(file_content.encode('utf-8'))
        file.name = "codes_statistics.txt"
        bot.send_document(call.message.chat.id, file, caption=f"📊 إحصائيات الأكواد")
    else:
        bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
    
    bot.answer_callback_query(call.id)

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
                bot.send_message(int(uid), f"🎉 <b>تهانينا!</b>\n💰 تم إضافة {prize_per_user:,} ل.س إلى رصيد البوت", parse_mode="HTML")
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
        user_website_balance = get_website_balance(uid)
        user_level = get_level(uid)
        user_xp = get_xp(uid)
        user_vip = "✅ نعم" if is_vip(uid) else "❌ لا"
        
        msg = f"""
👤 <b>المستخدم {uid}</b>
━━━━━━━━━━━━━━━━
💰 رصيد البوت: {user_balance:,} ل.س
🌐 رصيد الموقع: {user_website_balance:,} ل.س
⭐ المستوى: {user_level}
✨ XP: {user_xp}
👑 VIP: {user_vip}
        """
        bot.reply_to(message, msg, parse_mode="HTML")
        
    except ValueError:
        bot.reply_to(message, "❌ ID غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data == "sync_website")
def sync_website_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    users_synced = 0
    for uid_str in balances.keys():
        try:
            sync_balance_with_website(int(uid_str))
            users_synced += 1
        except:
            pass
    
    bot.answer_callback_query(call.id, f"✅ تمت مزامنة {users_synced} مستخدم", show_alert=True)
    bot.send_message(call.message.chat.id, f"🌐 <b>تمت المزامنة مع الموقع</b>\n✅ عدد المستخدم المتزامنة: {users_synced}", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "website_stats")
def website_stats_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ للمدير فقط!", show_alert=True)
        return
    
    website_users = load_website_users()
    total_website_balance = sum(u.get("balance", 0) for u in website_users.values())
    total_website_winnings = sum(u.get("totalWinnings", 0) for u in website_users.values())
    
    msg = f"""
🌐 <b>إحصائيات الموقع</b>
━━━━━━━━━━━━━━━━
👥 عدد مستخدمي الموقع: {len(website_users)}
💰 إجمالي الرصيد بالموقع: {total_website_balance:,} ل.س
🏆 إجمالي الأرباح بالموقع: {total_website_winnings:,} ل.س
🔗 رابط الموقع: {WEBSITE_URL}
━━━━━━━━━━━━━━━━
📌 يمكنك مزامنة البيانات باستخدام زر المزامنة
    """
    
    bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
    bot.answer_callback_query(call.id)

# ================== API Flask ==================

@app.route('/api/health', methods=['GET'])
def api_health():
    """فحص صحة الـ API"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'users_count': len(balances),
        'bot_active': True
    })

@app.route('/api/user/stats', methods=['GET'])
def api_user_stats():
    """الحصول على إحصائيات المستخدم"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'user_id مطلوب'}), 400
    
    return jsonify({
        'status': 'success',
        'user_id': user_id,
        'balance': get_balance(user_id),
        'website_balance': get_website_balance(user_id),
        'level': get_level(user_id),
        'xp': get_xp(user_id),
        'is_vip': is_vip(user_id),
        'referrals_count': get_referral_count(user_id),
        'raffle_tickets': get_raffle_entries_count(user_id)
    })

@app.route('/api/user/add_balance', methods=['POST'])
def api_add_balance():
    """إضافة رصيد للمستخدم (للاستخدام الداخلي)"""
    data = request.json
    secret = data.get('secret')
    
    if secret != API_SECRET_KEY:
        return jsonify({'status': 'error', 'message': 'مفتاح غير صالح'}), 401
    
    user_id = data.get('user_id')
    amount = data.get('amount', 0)
    
    if not user_id or amount <= 0:
        return jsonify({'status': 'error', 'message': 'بيانات غير صالحة'}), 400
    
    add_balance(user_id, amount)
    
    return jsonify({
        'status': 'success',
        'user_id': user_id,
        'amount': amount,
        'new_balance': get_balance(user_id)
    })

@app.route('/api/website/charge_request', methods=['POST'])
def api_website_charge_request():
    """استلام طلب شحن من الموقع"""
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount', 0)
    phone = data.get('phone', '')
    
    if not user_id or amount <= 0:
        return jsonify({'status': 'error', 'message': 'بيانات غير صالحة'}), 400
    
    charge_id = f"API_{user_id}_{int(time.time())}"
    pending_website_charges[charge_id] = {
        'user_id': user_id,
        'amount': amount,
        'phone': phone,
        'timestamp': datetime.now().isoformat(),
        'source': 'api'
    }
    
    # إرسال إشعار للمدير
    admin_msg = f"""
🔔 <b>طلب شحن جديد من الموقع (API)!</b>
━━━━━━━━━━━━━━━━
👤 <b>المستخدم:</b> <a href="tg://user?id={user_id}">{user_id}</a>
💰 <b>المبلغ:</b> {amount:,} ل.س
📞 <b>رقم الهاتف:</b> <code>{phone}</code>
🆔 <b>رقم الطلب:</b> <code>{charge_id}</code>
⏰ <b>الوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━
📌 <b>طريقة الشحن:</b> شحن رصيد الموقع عبر API
    """
    
    try:
        bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
        add_history(user_id, f"🌐 طلب شحن من الموقع (API): {amount:,} ل.س")
    except Exception as e:
        print(f"❌ خطأ في إرسال إشعار الشحن: {e}")
    
    return jsonify({
        'status': 'success',
        'message': 'تم استلام طلب الشحن بنجاح',
        'charge_id': charge_id
    })

@app.route('/api/website/withdraw', methods=['POST'])
def api_website_withdraw():
    """سحب رصيد من الموقع وإنشاء كود"""
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount', 0)
    secret = data.get('secret')
    
    if secret != API_SECRET_KEY:
        return jsonify({'status': 'error', 'message': 'مفتاح غير صالح'}), 401
    
    if not user_id or amount <= 0:
        return jsonify({'status': 'error', 'message': 'بيانات غير صالحة'}), 400
    
    if amount < 1000:
        return jsonify({'status': 'error', 'message': 'الحد الأدنى للسحب 1000 ل.س'}), 400
    
    if sub_website_balance(user_id, amount):
        withdraw_code = generate_withdraw_code()
        
        website_users = load_website_users()
        uid_str = str(user_id)
        if uid_str not in website_users:
            website_users[uid_str] = {}
        if 'withdraw_codes' not in website_users[uid_str]:
            website_users[uid_str]['withdraw_codes'] = []
        
        website_users[uid_str]['withdraw_codes'].append({
            'code': withdraw_code,
            'amount': amount,
            'date': datetime.now().isoformat(),
            'used': False,
            'source': 'api'
        })
        save_website_users(website_users)
        
        add_history(user_id, f"💰 سحب من الموقع عبر API: {amount:,} ل.س")
        
        try:
            bot.send_message(user_id, f"""
💸 <b>تم سحب الرصيد من الموقع</b>
━━━━━━━━━━━━━━━━
💰 المبلغ: {amount:,} ل.س
🎫 كود السحب: <code>{withdraw_code}</code>
━━━━━━━━━━━━━━━━
📌 استخدم هذا الكود في البوت لاستلام الرصيد (زر "🎫 إدخال كود سحب")
""", parse_mode="HTML")
        except:
            pass
        
        return jsonify({
            'status': 'success',
            'withdraw_code': withdraw_code,
            'amount': amount,
            'new_balance': get_website_balance(user_id)
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'رصيد غير كافٍ. رصيدك الحالي: {get_website_balance(user_id):,} ل.س',
            'current_balance': get_website_balance(user_id)
        }), 400

def run_flask():
    """تشغيل Flask API في thread منفصل"""
    print(f"🚀 تشغيل Flask API على المنفذ {API_PORT}")
    print(f"🔑 مفتاح API السري: {API_SECRET_KEY}")
    app.run(host='0.0.0.0', port=API_PORT, debug=False, use_reloader=False)

# ================== تشغيل البوت ==================

def run_bot():
    print("=" * 60)
    print("🤖 البوت الذكي الإصدار الثاني - فصل أرصدة الموقع")
    print(f"✅ التوكن: {TOKEN[:10]}...")
    print(f"✅ نسبة الفوز الشاملة: {global_win_rate}%")
    print(f"✅ رابط Web App: {WEBSITE_URL}")
    print(f"✅ قناة الاشتراك: {REQUIRED_CHANNEL}")
    print(f"✅ نظام فصل أرصدة الموقع: مفعل")
    print(f"✅ نظام API: مفعل على المنفذ {API_PORT}")
    print(f"🔑 مفتاح API: {API_SECRET_KEY}")
    print("=" * 60)
    
    bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل Flask API في thread منفصل
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # انتظار قليلاً لبدء تشغيل Flask
    time.sleep(2)
    
    # تشغيل البوت
    run_bot()