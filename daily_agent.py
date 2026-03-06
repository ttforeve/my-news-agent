import google.generativeai as genai
import feedparser
import time
import telebot
import schedule
import threading
import requests
from flask import Flask
import os # 💡 ဒါလေး အပေါ်ဆုံးမှာ ထပ်ထည့်ပါ

# ==========================================
# 🔑 1. CONFIGURATIONS
# ==========================================
# 💡 Key အစစ်တွေ မထည့်တော့ဘဲ os.environ.get ဖြင့် ပြောင်းရေးပါမည်
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# ☁️ 2. CLOUD WEB SERVER (Cloud တွင် မအိပ်သွားစေရန်)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Universal Studio AI News Agent is running 24/7!"

def run_web():
    # Cloud ပေါ်တွင် run ရန် port 8000 ကို ဖွင့်ထားပါသည်
    app.run(host='0.0.0.0', port=8000)

# ==========================================
# 🕵️‍♂️ 3. THE SCOUT AGENT (သတင်းထောက်)
# ==========================================
def scout_latest_news():
    # 💡 သိပ္ပံ နှင့် အားကစား ၂ ခု ထပ်တိုးထားပါသည် (စုစုပေါင်း ၇ ခု)
    news_sources = {
        "🌍 ကမ္ဘာ့ရေးရာ": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en",
        "📈 စီးပွားရေး": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
        "🚀 နည်းပညာ": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
        "💊 ကျန်းမာရေး": "https://news.google.com/rss/headlines/section/topic/HEALTH?hl=en-US&gl=US&ceid=US:en",
        "🎭 ဖျော်ဖြေရေး": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-US&gl=US&ceid=US:en",
        "🔬 သိပ္ပံ": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-US&gl=US&ceid=US:en",
        "⚽️ အားကစား": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-US&gl=US&ceid=US:en"
    }
    
    collected_news = ""
    for category, url in news_sources.items():
        feed = feedparser.parse(url)
        collected_news += f"\n--- {category} ---\n"
        # ကဏ္ဍတစ်ခုစီမှ ထိပ်ဆုံး ၅ ပုဒ်စီ ဆွဲထုတ်မည်
        for entry in feed.entries[:5]:
            collected_news += f"- Title: {entry.title}\n  Link: {entry.link}\n"
            
    return collected_news

# ==========================================
# 🧠 4. THE CHIEF EDITOR (အယ်ဒီတာချုပ်)
# ==========================================
def generate_news_briefing():
    raw_news = scout_latest_news()
    
    prompt = f"""
    You are an elite Chief Editor for a premium news briefing.
    I have provided you with a list of today's top news headlines and their URLs from 7 categories.
    
    YOUR TASK:
    1. Select the TOP 3 absolute most interesting, viral, or highly impactful stories from the entire list.
    2. Write a highly engaging briefing in natural BURMESE language (တယ်, မယ်, တဲ့).
    3. CRITICAL: You MUST include the exact matching URL (Link) for each story you select.
    
    FORMAT:
    🌅 မင်္ဂလာပါ။ ယခုအချိန်အထိ အဟော့ဆုံး သတင်း (၃) ပုဒ်ကို တင်ဆက်ပေးလိုက်ပါတယ်။
    
    1. [Emoji] **[Burmese Title 1]**
    [2-3 sentences summary explaining the story]
    🔗 [Read More / မူရင်းလင့်ခ်]: [Insert EXACT Link from raw data here]
    
    2. [Emoji] **[Burmese Title 2]**
    [2-3 sentences summary]
    🔗 [Read More / မူရင်းလင့်ခ်]: [Insert EXACT Link from raw data here]
    
    3. [Emoji] **[Burmese Title 3]**
    [2-3 sentences summary]
    🔗 [Read More / မူရင်းလင့်ခ်]: [Insert EXACT Link from raw data here]
    
    💡 **Editor's Note:** [1 brief insightful comment about today's news].
    
    RAW NEWS DATA:
    {raw_news}
    """
    
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ အယ်ဒီတာ အမှားအယွင်းဖြစ်နေပါသည်: {e}"

# ==========================================
# 🤖 5. TELEGRAM BOT COMMANDS (Manual Command)
# ==========================================
@bot.message_handler(commands=['start', 'news'])
def send_manual_news(message):
    print(f"📩 User requested news via Telegram at {time.strftime('%H:%M:%S')}")
    bot.reply_to(message, "⏳ ဆရာသမားအတွက် အခုလက်ရှိ အဟော့ဆုံးသတင်းများကို အင်တာနက်ပေါ်တွင် ရှာဖွေနေပါသည်... စက္ကန့်အနည်းငယ် စောင့်ပေးပါဗျာ။")
    
    final_news = generate_news_briefing()
    
    bot.send_message(message.chat.id, final_news, parse_mode="Markdown", disable_web_page_preview=True)
    print("✅ Manual News Sent!")

# ==========================================
# ⏰ 6. SCHEDULER (Auto Auto Auto)
# ==========================================
def auto_morning_post():
    print(f"⏰ Auto Scheduler Triggered at {time.strftime('%H:%M:%S')}!")
    final_news = generate_news_briefing()
    bot.send_message(CHAT_ID, final_news, parse_mode="Markdown", disable_web_page_preview=True)
    print("✅ Auto Morning News Sent!")

# မနက် ၉ နာရီတိတိမှာ auto_morning_post ကို အလုပ်လုပ်ခိုင်းမည်
schedule.every().day.at("09:00").do(auto_morning_post)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# ==========================================
# 🚀 7. SYSTEM START (Main Execution)
# ==========================================
if __name__ == "__main__":
    print("="*50)
    print("🤖 AI NEWS BOT IS NOW LIVE AND LISTENING...")
    print("="*50)
    
    # 1. Cloud Web Server ကို Background တွင် Run မည်
    threading.Thread(target=run_web, daemon=True).start()
    
    # 2. Scheduler ကို Background တွင် Run မည်
    threading.Thread(target=run_scheduler, daemon=True).start()
    
    # 3. Telegram Bot ကို ၂၄ နာရီ နားစွင့်ခိုင်းထားမည်
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:

        print(f"⚠️ Bot Polling Error: {e}")
