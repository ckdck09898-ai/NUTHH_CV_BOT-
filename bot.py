import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import telebot
from telebot import types
from database import init_db, ensure_user, get_language, set_language, save_cv, load_cv, list_cvs
from templates import TEMPLATES, get_categories, templates_for_category, get_template
from cv_builder import FIELDS, make_preview, build_pdf, build_docx, ats_check, write_assistance

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
if not BOT_TOKEN or BOT_TOKEN == "PASTE_TELEGRAM_BOT_TOKEN_HERE":
    raise RuntimeError("BOT_TOKEN is missing. Copy .env.example to .env and add your token.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
SESSIONS = {}
PHOTO_DIR = Path(__file__).parent / "generated_cvs" / "photos"
PHOTO_DIR.mkdir(parents=True, exist_ok=True)

TEXT = {
    "en": {
        "welcome": "Welcome to NUTHH’ CV BOT\nCreate a professional CV, cover letter, and job application email.",
        "menu": "Choose a function:", "create": "📝 Create CV", "edit": "🛠 Edit CV", "mycv": "📂 My CV", "templates": "🎨 Templates",
        "cover": "✉️ Cover Letter", "email": "📧 Application Email", "ats": "🔎 ATS / Job Match", "improve": "✨ CV Assistant",
        "language": "🌐 Language", "help": "❔ Help", "cancel": "Cancelled. Use /start to return to menu.",
        "choose_cat": "Choose a CV category:", "choose_template": "Choose a template to preview:",
        "ask_photo": "Send a profile photo now, or type SKIP to continue without one.",
        "skip": "SKIP", "saved": "CV saved. Choose a file format:", "notfound": "No saved CV found. Choose Create CV first.",
        "lang_prompt": "Choose interface and CV language:", "help_text": "Use the menu buttons. Create CV → category → template preview → fill in fields.\nCommands: /start /cancel /mycv /templates\nFree writing helper uses templates and rules, not a paid AI API.",
        "done": "Your file is ready.", "enter_job": "Paste the job description to check your CV match, or type SKIP for ATS score only.",
        "invalid": "Please choose a button or enter the requested text. Use /cancel to stop.",
    },
    "km": {
        "welcome": "សូមស្វាគមន៍មកកាន់ NUTHH’ CV BOT\nបង្កើត CV លិខិតដាក់ពាក្យ និង Email ស្វែងរកការងារ។",
        "menu": "សូមជ្រើសរើសមុខងារ៖", "create": "📝 បង្កើត CV", "edit": "🛠 កែ CV", "mycv": "📂 CV របស់ខ្ញុំ", "templates": "🎨 គំរូ CV",
        "cover": "✉️ លិខិតដាក់ពាក្យ", "email": "📧 Email ដាក់ពាក្យ", "ats": "🔎 ពិនិត្យ ATS / ផ្គូផ្គងការងារ", "improve": "✨ ជំនួយកែលម្អ CV",
        "language": "🌐 ភាសា", "help": "❔ ជំនួយ", "cancel": "បានបោះបង់។ ប្រើ /start ដើម្បីត្រឡប់ទៅ Menu។",
        "choose_cat": "សូមជ្រើសរើសប្រភេទ CV៖", "choose_template": "ជ្រើសរើសគំរូ ដើម្បីមើល Preview៖",
        "ask_photo": "សូមផ្ញើរូបថត Profile ឬវាយ SKIP ដើម្បីបន្តដោយគ្មានរូបថត។", "skip": "SKIP",
        "saved": "បានរក្សាទុក CV។ សូមជ្រើសរើសទម្រង់ឯកសារ៖", "notfound": "មិនទាន់មាន CV ទេ។ សូមចុច បង្កើត CV ជាមុន។",
        "lang_prompt": "សូមជ្រើសរើសភាសា៖", "help_text": "ប្រើប៊ូតុង Menu។ បង្កើត CV → ប្រភេទ → Preview → បំពេញព័ត៌មាន។\nCommands: /start /cancel /mycv /templates\nមុខងារជួយសរសេរឥតគិតថ្លៃប្រើ Templates និង Rules មិនប្រើ Paid AI API ទេ។",
        "done": "ឯកសាររបស់អ្នករួចរាល់ហើយ។", "enter_job": "សូម Paste ព័ត៌មានការងារ ដើម្បីពិនិត្យការផ្គូផ្គង ឬវាយ SKIP ដើម្បីពិនិត្យ ATS តែប៉ុណ្ណោះ។",
        "invalid": "សូមចុចប៊ូតុង ឬបញ្ចូលព័ត៌មានដែលបានស្នើ។ ប្រើ /cancel ដើម្បីបោះបង់។",
    },
    "zh": {"welcome":"欢迎使用 NUTHH’ CV BOT","menu":"请选择功能：","create":"📝 创建简历","edit":"🛠 编辑简历","mycv":"📂 我的简历","templates":"🎨 简历模板","cover":"✉️ 求职信","email":"📧 求职邮件","ats":"🔎 ATS / 职位匹配","language":"🌐 语言","help":"❔ 帮助","improve":"✨ 简历优化","cancel":"已取消。发送 /start 返回菜单。","choose_cat":"请选择简历类别：","choose_template":"请选择模板预览：","ask_photo":"发送头像，或输入 SKIP 跳过。","skip":"SKIP","saved":"简历已保存，请选择格式：","notfound":"没有找到简历，请先创建。","lang_prompt":"请选择语言：","help_text":"使用菜单按钮创建简历。免费写作助手使用模板和规则，不使用付费 AI API。","done":"文件已生成。","enter_job":"粘贴职位描述进行匹配，或输入 SKIP 只检查 ATS。","invalid":"请选择按钮或输入所需内容。","" : ""},
    "fr": {"welcome":"Bienvenue sur NUTHH’ CV BOT","menu":"Choisissez une fonction :","create":"📝 Créer un CV","edit":"🛠 Modifier le CV","mycv":"📂 Mon CV","templates":"🎨 Modèles","cover":"✉️ Lettre de motivation","email":"📧 E-mail de candidature","ats":"🔎 ATS / Correspondance","language":"🌐 Langue","help":"❔ Aide","improve":"✨ Améliorer le CV","cancel":"Annulé. Envoyez /start pour revenir au menu.","choose_cat":"Choisissez une catégorie :","choose_template":"Choisissez un modèle à prévisualiser :","ask_photo":"Envoyez une photo ou tapez SKIP.","skip":"SKIP","saved":"CV enregistré. Choisissez un format :","notfound":"Aucun CV enregistré. Créez-en un d’abord.","lang_prompt":"Choisissez la langue :","help_text":"Utilisez les boutons du menu. L’assistant gratuit utilise des modèles et des règles, sans API IA payante.","done":"Votre fichier est prêt.","enter_job":"Collez la description du poste ou tapez SKIP.","invalid":"Choisissez un bouton ou saisissez le texte demandé."},
}
LANG_NAMES = {"km":"🇰🇭 Khmer", "en":"🇬🇧 English", "zh":"🇨🇳 中文", "fr":"🇫🇷 Français"}

def lang(uid):
    return get_language(uid) if get_language(uid) in TEXT else "en"
def t(uid, key):
    chosen = TEXT[lang(uid)]
    return chosen.get(key, TEXT["en"].get(key, key))
def main_menu(uid):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(t(uid,"create"), t(uid,"edit"), t(uid,"mycv"), t(uid,"templates"), t(uid,"cover"), t(uid,"email"), t(uid,"ats"), t(uid,"improve"), t(uid,"language"), t(uid,"help"))
    return m
def set_state(uid, **kwargs):
    SESSIONS.setdefault(uid, {})
    SESSIONS[uid].update(kwargs)
def reset_state(uid):
    SESSIONS[uid] = {"lang": lang(uid)}
def categories_markup():
    m=types.InlineKeyboardMarkup(row_width=2)
    for key,name in get_categories():
        m.add(types.InlineKeyboardButton(name, callback_data=f"cat:{key}"))
    m.add(types.InlineKeyboardButton("⬅️ Menu", callback_data="menu"))
    return m
def templates_markup(category_key, page=0):
    items=templates_for_category(category_key); per_page=5
    start=page*per_page
    m=types.InlineKeyboardMarkup(row_width=1)
    for item in items[start:start+per_page]:
        m.add(types.InlineKeyboardButton(f"{item['number']:03d}. {item['name']} · {item['layout']}", callback_data=f"tpl:{item['id']}"))
    nav=[]
    if page>0: nav.append(types.InlineKeyboardButton("◀ Previous", callback_data=f"page:{category_key}:{page-1}"))
    if start+per_page<len(items): nav.append(types.InlineKeyboardButton("Next ▶", callback_data=f"page:{category_key}:{page+1}"))
    if nav: m.row(*nav)
    m.add(types.InlineKeyboardButton("⬅️ Categories", callback_data="categories"))
    return m
def file_markup():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("📄 PDF", callback_data="file:pdf"), types.InlineKeyboardButton("📝 Word DOCX", callback_data="file:docx"))
    m.add(types.InlineKeyboardButton("🔁 Change template", callback_data="categories"), types.InlineKeyboardButton("⬅️ Menu", callback_data="menu"))
    return m
def begin_cv(message):
    uid=message.from_user.id
    set_state(uid, mode="create", data={}, photo=None, page=0)
    bot.send_message(message.chat.id, t(uid,"choose_cat"), reply_markup=categories_markup())
def begin_fields(chat_id, uid):
    session=SESSIONS[uid]
    session["field_index"]=0
    ask_field(chat_id, uid)
def ask_field(chat_id, uid):
    s=SESSIONS[uid]; idx=s["field_index"]
    if idx>=len(FIELDS):
        s["step"]="photo"
        m=types.ReplyKeyboardMarkup(resize_keyboard=True); m.add(t(uid,"skip"), "/cancel")
        bot.send_message(chat_id, t(uid,"ask_photo"), reply_markup=m)
        return
    key,label,required=FIELDS[idx]
    s["step"]="field"
    m=types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("SKIP", "/cancel")
    current = s.get("data", {}).get(key, "")
    prompt = f"{idx+1}/{len(FIELDS)} — {label}" + (" *" if required else "")
    if current: prompt += f"\nCurrent value: {current}\nType SKIP to keep it."
    bot.send_message(chat_id, prompt, reply_markup=m)
def deliver_cv(chat_id, uid, fmt):
    saved=load_cv(uid)
    if not saved:
        bot.send_message(chat_id,t(uid,"notfound"),reply_markup=main_menu(uid)); return
    data=saved["data"]; template_id=saved["template_id"]
    photo=SESSIONS.get(uid,{}).get("photo") or saved["data"].get("_photo_path")
    try:
        if fmt=="pdf": path=build_pdf(data,template_id,lang(uid),photo,user_id=uid)
        else: path=build_docx(data,template_id,lang(uid),photo,user_id=uid)
        with open(path,"rb") as f: bot.send_document(chat_id,f,caption=f"{t(uid,'done')} · {get_template(template_id)['name']}")
    except Exception as exc:
        logging.exception("Document generation failed")
        bot.send_message(chat_id, f"Could not create file: {exc}")
def start(message):
    uid=message.from_user.id; ensure_user(uid); SESSIONS.setdefault(uid,{"lang":lang(uid)})
    bot.send_message(message.chat.id,t(uid,"welcome")+"\n\n"+t(uid,"menu"),reply_markup=main_menu(uid))
@bot.message_handler(commands=["start"])
def start_cmd(message): start(message)
@bot.message_handler(commands=["cancel"])
def cancel_cmd(message):
    uid=message.from_user.id; reset_state(uid)
    bot.send_message(message.chat.id,t(uid,"cancel"),reply_markup=main_menu(uid))
@bot.message_handler(commands=["mycv"])
def mycv_cmd(message): show_mycv(message.chat.id,message.from_user.id)
@bot.message_handler(commands=["templates"])
def templates_cmd(message): bot.send_message(message.chat.id,t(message.from_user.id,"choose_cat"),reply_markup=categories_markup())
def show_mycv(chat_id,uid):
    saved=load_cv(uid)
    if not saved:
        bot.send_message(chat_id,t(uid,"notfound"),reply_markup=main_menu(uid)); return
    d=saved["data"]
    preview=make_preview(saved["template_id"])
    with open(preview,"rb") as f: bot.send_photo(chat_id,f,caption=f"{saved['title']} · {get_template(saved['template_id'])['name']}")
    summary="\n".join(f"{k}: {v}" for k,v in d.items() if v and not k.startswith("_"))
    bot.send_message(chat_id,summary[:3500]+"\n\n"+t(uid,"saved"),reply_markup=file_markup())
@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    uid=call.from_user.id; chat_id=call.message.chat.id; data=call.data
    try: bot.answer_callback_query(call.id)
    except Exception: pass
    if data=="menu":
        bot.send_message(chat_id,t(uid,"menu"),reply_markup=main_menu(uid)); return
    if data=="categories":
        bot.send_message(chat_id,t(uid,"choose_cat"),reply_markup=categories_markup()); return
    if data.startswith("cat:"):
        key=data.split(":",1)[1]
        bot.send_message(chat_id,t(uid,"choose_template"),reply_markup=templates_markup(key,0)); return
    if data.startswith("page:"):
        _,key,page=data.split(":",2)
        bot.send_message(chat_id,t(uid,"choose_template"),reply_markup=templates_markup(key,int(page))); return
    if data.startswith("tpl:"):
        tid=data.split(":",1)[1]; item=get_template(tid)
        set_state(uid,selected_template=tid)
        path=make_preview(tid)
        m=types.InlineKeyboardMarkup(row_width=2)
        m.add(types.InlineKeyboardButton("✅ Use this template",callback_data=f"use:{tid}"),types.InlineKeyboardButton("🔄 More templates",callback_data=f"more:{tid}"))
        with open(path,"rb") as f: bot.send_photo(chat_id,f,caption=f"{item['number']:03d}/100 · {item['name']}\nCategory: {item['category']}\nLayout: {item['layout']} · Color: {item['palette']}",reply_markup=m)
        return
    if data.startswith("more:"):
        tid=data.split(":",1)[1]; item=get_template(tid)
        key=next((k for k,v in get_categories() if v==item['category']),None)
        bot.send_message(chat_id,t(uid,"choose_template"),reply_markup=templates_markup(key or "professional",0)); return
    if data.startswith("use:"):
        tid=data.split(":",1)[1]
        set_state(uid,mode="create",step="field",data={},template_id=tid,photo=None,field_index=0)
        begin_fields(chat_id,uid); return
    if data.startswith("file:"):
        deliver_cv(chat_id,uid,data.split(":",1)[1]); return
    if data.startswith("lang:"):
        language=data.split(":",1)[1]; set_language(uid,language); SESSIONS[uid]={"lang":language}
        bot.send_message(chat_id,t(uid,"menu"),reply_markup=main_menu(uid)); return
    if data=="newcv":
        msg=call.message; begin_cv(msg); return

@bot.message_handler(content_types=["photo"])
def photo_handler(message):
    uid=message.from_user.id; s=SESSIONS.get(uid,{})
    if s.get("step")!="photo":
        bot.send_message(message.chat.id,"To add a CV photo, start or finish the CV form first.",reply_markup=main_menu(uid)); return
    try:
        photo=message.photo[-1]
        info=bot.get_file(photo.file_id); raw=bot.download_file(info.file_path)
        path=PHOTO_DIR/f"{uid}_profile.jpg"; path.write_bytes(raw)
        s["photo"]=str(path); complete_cv(message.chat.id,uid)
    except Exception:
        bot.send_message(message.chat.id,"Could not save photo. Please type SKIP or try another photo.")
def complete_cv(chat_id,uid):
    s=SESSIONS[uid]; data=s["data"]; tid=s.get("template_id","professional_01")
    if s.get("photo"): data["_photo_path"] = s["photo"]
    save_cv(uid,data,tid)
    try:
        preview=make_preview(tid, output_path=Path(__file__).parent / "previews" / f"{uid}_final.png", data=data)
        with open(preview,"rb") as f: bot.send_photo(chat_id,f,caption=f"Personalized preview · {get_template(tid)['name']}")
    except Exception: pass
    bot.send_message(chat_id,t(uid,"saved"),reply_markup=file_markup())
    s["step"]="done"
@bot.message_handler(content_types=["text"])
def text_handler(message):
    uid=message.from_user.id; text=message.text.strip(); ensure_user(uid)
    current=lang(uid); s=SESSIONS.setdefault(uid,{"lang":current})
    # menu matching works in selected language and English aliases
    if text in (t(uid,"create"),"Create CV","📝 Create CV","📝 បង្កើត CV"):
        begin_cv(message); return
    if text in (t(uid,"edit"), "Edit CV", "🛠 Edit CV", "🛠 កែ CV", "🛠 编辑简历", "🛠 Modifier le CV"):
        saved=load_cv(uid)
        if not saved:
            bot.send_message(message.chat.id,t(uid,"notfound"),reply_markup=main_menu(uid)); return
        set_state(uid, mode="edit", data=saved["data"].copy(), template_id=saved["template_id"], photo=saved["data"].get("_photo_path"), field_index=0)
        begin_fields(message.chat.id,uid); return
    if text in (t(uid,"mycv"),"My CV","📂 My CV","📂 CV របស់ខ្ញុំ"):
        show_mycv(message.chat.id,uid); return
    if text in (t(uid,"templates"),"Templates","🎨 Templates","🎨 គំរូ CV"):
        bot.send_message(message.chat.id,t(uid,"choose_cat"),reply_markup=categories_markup()); return
    if text in (t(uid,"language"),"Language","🌐 Language","🌐 ភាសា"):
        m=types.InlineKeyboardMarkup(row_width=2)
        for code,name in LANG_NAMES.items(): m.add(types.InlineKeyboardButton(name,callback_data=f"lang:{code}"))
        bot.send_message(message.chat.id,t(uid,"lang_prompt"),reply_markup=m); return
    if text in (t(uid,"help"),"Help","❔ Help","❔ ជំនួយ"):
        bot.send_message(message.chat.id,t(uid,"help_text"),reply_markup=main_menu(uid)); return
    if text in (t(uid,"cover"),"Cover Letter","✉️ Cover Letter","✉️ លិខិតដាក់ពាក្យ"):
        saved=load_cv(uid)
        if not saved: bot.send_message(message.chat.id,t(uid,"notfound"),reply_markup=main_menu(uid)); return
        output=write_assistance("cover",saved["data"],lang(uid))
        bot.send_message(message.chat.id,output[:4000],reply_markup=main_menu(uid)); return
    if text in (t(uid,"email"),"Application Email","📧 Application Email","📧 Email ដាក់ពាក្យ"):
        saved=load_cv(uid)
        if not saved: bot.send_message(message.chat.id,t(uid,"notfound"),reply_markup=main_menu(uid)); return
        output=write_assistance("email",saved["data"],lang(uid))
        bot.send_message(message.chat.id,output[:4000],reply_markup=main_menu(uid)); return
    if text in (t(uid,"improve"), "✨ CV Assistant", "✨ ជំនួយកែលម្អ CV", "✨ 简历优化", "✨ Améliorer le CV"):
        saved=load_cv(uid)
        if not saved:
            bot.send_message(message.chat.id,t(uid,"notfound"),reply_markup=main_menu(uid)); return
        d=saved["data"]
        summary=write_assistance("summary",d,lang(uid))
        skills=d.get("skills", "").strip()
        tips=[]
        if not d.get("summary", "").strip(): tips.append("• Add the generated summary to your CV.")
        if not skills: tips.append("• Add 5–8 relevant skills that you genuinely have.")
        if d.get("experience", "").strip().lower() in ("none", "no experience", "n/a", "មិនមាន", "អត់មាន"):
            tips.append("• If you have no work history, highlight school projects, volunteering, training, or practical skills instead.")
        answer=("Suggested profile / Career Objective:\n\n"+summary+"\n\nImprovement tips:\n"+("\n".join(tips) if tips else "• Tailor this CV to each job description.\n• Use clear, truthful achievements and action verbs."))
        bot.send_message(message.chat.id,answer[:4000],reply_markup=main_menu(uid)); return
    if text in (t(uid,"ats"),"ATS / Job Match","🔎 ATS / Job Match","🔎 ពិនិត្យ ATS / ផ្គូផ្គងការងារ"):
        saved=load_cv(uid)
        if not saved: bot.send_message(message.chat.id,t(uid,"notfound"),reply_markup=main_menu(uid)); return
        s["step"]="job_description"
        bot.send_message(message.chat.id,t(uid,"enter_job"),reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("SKIP","/cancel")); return
    if text == "/admin":
        if ADMIN_ID and str(uid)==ADMIN_ID:
            rows=[]
            # lightweight stats; DB is local to this app
            from database import connect
            with connect() as db:
                users=db.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
                cvs=db.execute("SELECT COUNT(*) n FROM cvs").fetchone()["n"]
            bot.send_message(message.chat.id,f"Admin stats\nUsers: {users}\nSaved CV profiles: {cvs}")
        else: bot.send_message(message.chat.id,"Not authorized.")
        return
    if s.get("step")=="field":
        idx=s["field_index"]; key,label,required=FIELDS[idx]
        if text.upper()=="SKIP":
            if s.get("mode")=="edit":
                s["field_index"]+=1; ask_field(message.chat.id,uid); return
            if required:
                bot.send_message(message.chat.id,"This field is required. Please enter it, or use /cancel."); return
            s["data"][key]=""
        else:
            s["data"][key]=text
        s["field_index"]+=1; ask_field(message.chat.id,uid); return
    if s.get("step")=="photo":
        if text.upper() in ("SKIP",t(uid,"skip")):
            s["photo"]=None; complete_cv(message.chat.id,uid)
        else: bot.send_message(message.chat.id,t(uid,"ask_photo"))
        return
    if s.get("step")=="job_description":
        saved=load_cv(uid); job="" if text.upper()=="SKIP" else text
        result=ats_check(saved["data"],job)
        lines=[f"ATS completeness score: {result['score']}/100", "", "Checks:"]
        lines += [("✅ " if ok else "❌ ")+name for name,ok in result["checks"].items()]
        if result["suggestions"]: lines += ["", "Suggestions: "]+["• Add "+x for x in result["suggestions"]]
        if result["match"] is not None:
            lines += ["",f"Keyword overlap estimate: {result['match']['score']}%", "Matched: "+(", ".join(result["match"]["matched"]) or "None"), "Potential missing keywords: "+(", ".join(result["match"]["missing"]) or "None")]
        lines += ["", "This is a simple keyword/completeness estimate, not a guarantee of passing an employer's ATS."]
        s["step"]="done"
        bot.send_message(message.chat.id,"\n".join(lines)[:4000],reply_markup=main_menu(uid)); return
    bot.send_message(message.chat.id,t(uid,"menu"),reply_markup=main_menu(uid))

if __name__ == "__main__":
    init_db()
    logging.info("NUTHH’ CV BOT is starting. Templates loaded: %s", len(TEMPLATES))
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
