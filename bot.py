import asyncio
import logging
import os
import random
import time
from contextlib import suppress

from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# =========================================================
# КОНФИГ
# =========================================================

BOT_TOKEN = os.environ["BOT_TOKEN"]  
PORT = int(os.environ.get("PORT", 8080))  

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("promo-bot")

NAMES = ["братан", "брат", "родной", "слушай", "короче", "слышь", "дружище", "бро", "шеф", "командир"]
HOOKS = [
    "у меня тема",
    "есть разговор",
    "есть движ",
    "появился вопрос",
    "нарисовалась тема",
    "есть один момент",
    "тут такое дело",
    "есть расклад",
    "надо пересечься",
    "надо перетереть",
]
TOPICS = [
    "по бабкам",
    "по переводу",
    "по заносу",
    "по проекту",
    "по сделке",
    "по встрече",
    "по срокам",
    "по отгрузке",
    "по партнёрам",
    "по контракту",
    "по клиенту",
    "по оплате",
    "по поставке",
    "по закрытию",
    "по счетам",
]
URGENCY = [
    "срочно",
    "очень срочно",
    "горит",
    "надо решить сегодня",
    "время поджимает",
    "не откладываем",
    "до конца дня",
    "в темпе",
]
ACTIONS = [
    "набери как сможешь",
    "позвони",
    "ответь",
    "маякни",
    "черкни пару слов",
    "скинь номер",
    "подтверди",
    "дай ответ",
    "будь на связи",
    "выйди на связь",
]
DETAILS = [
    "детали позже",
    "подробности по телефону",
    "не в переписке",
    "объясню на словах",
    "не пиши сюда",
    "расскажу лично",
    "потом расскажу",
    "тут не всё так просто",
]
MONEY = [
    "бабки зашли",
    "деньги пришли",
    "оплата прошла",
    "перевод упал",
    "средства на счету",
    "платёж подтвердили",
    "касса закрылась",
    "лимит согласовали",
    "сумма согласована",
    "бабки готовы",
]
PEOPLE = [
    "человек на линии",
    "клиент ждёт",
    "партнёр на связи",
    "заказчик на проводе",
    "инвестор ждёт ответа",
    "поставщик пишет",
    "юрист звонил",
    "бухгалтер спрашивает",
    "человек с той стороны ждёт",
]
RESPONSES = [
    "ок?",
    "на связи?",
    "ответь как сможешь",
    "жду",
    "будь на телефоне",
    "маякни",
    "понял?",
    "как слышно?",
    "что по этому?",
    "принял?",
    "да или нет?",
    "сколько по времени?",
    "можешь?",
    "сделаешь?",
    "выходишь?",
    "подтверждаешь?",
]
TRANSFER = [
    "переведи пока X",
    "скинь на карту",
    "перекинь сумму",
    "закинь сколько можешь",
    "переведи на счёт",
    "перекинь бабки",
    "скинь на реквизиты",
    "оплати счёт",
    "закрой платёж",
    "переведи остаток",
]
BIZ_TALK = [
    "тема на миллион",
    "движ пошёл",
    "всё завертелось",
    "проект двинулся",
    "сделка на подходе",
    "контракт подписали",
    "партнёры согласны",
    "клиент дал добро",
    "заказчик подтвердил",
    "условия приняли",
    "вопрос закрыли",
    "договор завизировали",
    "всё на мази",
    "расклад поменялся",
    "ситуация двинулась",
]


def build_phrases() -> list[str]:
    """Собираем большой пул фраз из шаблонов."""
    phrases: list[str] = []

    # 1) Короткие приветствия + хук
    for n in NAMES:
        for h in HOOKS:
            phrases.append(f"{n}, {h}.")
            phrases.append(f"{n}, {h}, {random.choice(ACTIONS)}.")
            phrases.append(f"{n}, {h} — {random.choice(URGENCY)}.")
            phrases.append(f"{n}, {h} {random.choice(TOPICS)}.")
            phrases.append(f"{n}, {h} {random.choice(TOPICS)}, {random.choice(URGENCY)}.")

    # 2) Деньги / переводы
    for m in MONEY:
        phrases.append(f"Слушай, {m}.")
        phrases.append(f"Короче, {m}, надо решить.")
        phrases.append(f"Братан, {m} — что дальше?")
        phrases.append(f"{m.capitalize()}, {random.choice(ACTIONS)}.")
    for t in TRANSFER:
        phrases.append(f"{t.capitalize()}, потом объясню.")
        phrases.append(f"{t.capitalize()}, {random.choice(URGENCY)}.")
        phrases.append(f"Надо так: {t.lower()}.")
        phrases.append(f"{t.capitalize()}, {random.choice(DETAILS)}.")

    # 3) Люди на связи
    for p in PEOPLE:
        phrases.append(f"{p.capitalize()}.")
        phrases.append(f"{p.capitalize()}, {random.choice(URGENCY)}.")
        phrases.append(f"У меня {p.lower()}, ждёт ответа.")
        phrases.append(f"{p.capitalize()} — {random.choice(ACTIONS)}.")

    # 4) Бизнес-движ
    for b in BIZ_TALK:
        phrases.append(f"{b.capitalize()}.")
        phrases.append(f"{b.capitalize()}, {random.choice(ACTIONS)}.")
        phrases.append(f"Короче, {b}.")
        phrases.append(f"Слушай, {b} — {random.choice(URGENCY)}.")

    # 5) Ответы-реакции (как будто ты уже что-то написал)
    for r in RESPONSES:
        phrases.append(r.capitalize())
        phrases.append(f"Ну {r.lower()}")
        phrases.append(f"И? {r.lower()}")
        phrases.append(f"Так {r.lower()}")

    # 6) Комбинированные «живые» реплики
    for _ in range(400):
        parts = [
            random.choice(NAMES).capitalize(),
            random.choice(HOOKS),
            random.choice(TOPICS),
            random.choice(URGENCY),
            random.choice(ACTIONS),
            random.choice(DETAILS),
        ]
        # берём 3-4 случайных элемента и склеиваем
        chunk = parts[:1] + random.sample(parts[1:], k=random.randint(2, 4))
        s = ", ".join(p.strip(",.") for p in chunk)
        phrases.append(s[0].upper() + s[1:] + random.choice([".", "?", "!", "...", ""]))

    # 7) Ещё немного «живых диалогов»
    for _ in range(300):
        a = random.choice(NAMES).capitalize()
        b = random.choice(HOOKS)
        c = random.choice([*TOPICS, *BIZ_TALK, *MONEY])
        d = random.choice([*URGENCY, *ACTIONS])
        phrases.append(f"{a}, {b} {c} — {d}.")

    # убираем пустые и дубли, перемешиваем
    phrases = list({p.strip() for p in phrases if p.strip()})
    random.shuffle(phrases)
    return phrases


PHRASES = build_phrases()
log.info("Загружено фраз: %d", len(PHRASES))


def random_phrase() -> str:
    return random.choice(PHRASES)

# user_id -> {"mode": "off"|"rare"|"normal"|"often", "next_ts": float}
USERS: dict[int, dict] = {}

MODES = {
    "off": None,
    "rare": (60 * 60 * 3, 60 * 60 * 8),       # 3–8 часов
    "normal": (60 * 30, 60 * 90),             # 30–90 минут
    "often": (60 * 5, 60 * 15),               # 5–15 минут
}

MODE_LABELS = {
    "off": "🔴 Выключить",
    "rare": "🟢 Редко",
    "normal": "🟡 Обычно",
    "often": "🔵 Очень часто",
}


def schedule_next(user_id: int) -> None:
    """Пересчитать время следующего сообщения для пользователя."""
    u = USERS.get(user_id)
    if not u:
        return
    mode = u["mode"]
    if mode == "off":
        u["next_ts"] = 0.0
        return
    lo, hi = MODES[mode]
    u["next_ts"] = time.time() + random.randint(lo, hi)


def kb_for(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    cur = USERS.get(user_id, {}).get("mode", "off")
    for key, label in MODE_LABELS.items():
        mark = "✅ " if key == cur else ""
        kb.button(text=f"{mark}{label}", callback_data=f"mode:{key}")
    kb.adjust(1)
    return kb.as_markup()

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    await msg.answer(
        "Привет. Чтобы активировать доступ, отправь команду <code>/promo_1924</code>."
    )


@dp.message(Command("promo_1924"))
async def cmd_promo(msg: types.Message):
    uid = msg.from_user.id
    USERS.setdefault(uid, {"mode": "off", "next_ts": 0.0})
    await msg.answer(
        "Доступ активирован. Выбери частоту сообщений:",
        reply_markup=kb_for(uid),
    )


@dp.callback_query(F.data.startswith("mode:"))
async def cb_mode(cb: types.CallbackQuery):
    uid = cb.from_user.id
    if uid not in USERS:
        await cb.answer("Сначала отправь /promo_1924", show_alert=True)
        return
    mode = cb.data.split(":", 1)[1]
    if mode not in MODES:
        await cb.answer("Неизвестный режим", show_alert=True)
        return
    USERS[uid]["mode"] = mode
    schedule_next(uid)
    await cb.message.edit_reply_markup(reply_markup=kb_for(uid))
    await cb.answer(f"Режим: {MODE_LABELS[mode]}")


# =========================================================
# ПЛАНИРОВЩИК (свой, без APScheduler — проще и надёжнее)
# =========================================================

async def scheduler_loop():
    log.info("Планировщик запущен")
    while True:
        try:
            now = time.time()
            for uid, u in list(USERS.items()):
                if u["mode"] == "off":
                    continue
                if u["next_ts"] and now >= u["next_ts"]:
                    try:
                        await bot.send_message(uid, random_phrase())
                    except Exception as e:
                        log.warning("Не смог отправить %s: %s", uid, e)
                    schedule_next(uid)
        except Exception as e:
            log.exception("Ошибка планировщика: %s", e)
        await asyncio.sleep(5)

async def health(_: web.Request) -> web.Response:
    return web.Response(text="ok")


async def start_web():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info("HTTP-сервер на порту %s", PORT)

async def main():
    await start_web()
    asyncio.create_task(scheduler_loop())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
