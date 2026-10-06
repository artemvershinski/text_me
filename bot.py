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
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.environ["BOT_TOKEN"]
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("promo-bot")

WELCOME_TEXT = (
    "Привет, владелец бота - @vrsnsky\n"
    "Функционал бота открывается через него"
)

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
    "по бабкам", "по переводу", "по заносу", "по проекту", "по сделке",
    "по встрече", "по срокам", "по отгрузке", "по партнёрам", "по контракту",
    "по клиенту", "по оплате", "по поставке", "по закрытию", "по счетам",
]
URGENCY = [
    "срочно", "очень срочно", "горит", "надо решить сегодня",
    "время поджимает", "не откладываем", "до конца дня", "в темпе",
]
ACTIONS = [
    "набери как сможешь", "позвони", "ответь", "маякни",
    "черкни пару слов", "скинь номер", "подтверди", "дай ответ",
    "будь на связи", "выйди на связь",
]
DETAILS = [
    "детали позже", "подробности по телефону", "не в переписке",
    "объясню на словах", "не пиши сюда", "расскажу лично",
    "потом расскажу", "тут не всё так просто",
]
MONEY = [
    "бабки зашли", "деньги пришли", "оплата прошла", "перевод упал",
    "средства на счету", "платёж подтвердили", "касса закрылась",
    "лимит согласовали", "сумма согласована", "бабки готовы",
]
PEOPLE = [
    "человек на линии", "клиент ждёт", "партнёр на связи",
    "заказчик на проводе", "инвестор ждёт ответа", "поставщик пишет",
    "юрист звонил", "бухгалтер спрашивает", "человек с той стороны ждёт",
]
RESPONSES = [
    "ок?", "на связи?", "ответь как сможешь", "жду", "будь на телефоне",
    "маякни", "понял?", "как слышно?", "что по этому?", "принял?",
    "да или нет?", "сколько по времени?", "можешь?", "сделаешь?",
    "выходишь?", "подтверждаешь?",
]
TRANSFER = [
    "переведи пока X", "скинь на карту", "перекинь сумму",
    "закинь сколько можешь", "переведи на счёт", "перекинь бабки",
    "скинь на реквизиты", "оплати счёт", "закрой платёж", "переведи остаток",
]
BIZ_TALK = [
    "тема на миллион", "движ пошёл", "всё завертелось", "проект двинулся",
    "сделка на подходе", "контракт подписали", "партнёры согласны",
    "клиент дал добро", "заказчик подтвердил", "условия приняли",
    "вопрос закрыли", "договор завизировали", "всё на мази",
    "расклад поменялся", "ситуация двинулась",
]


def build_phrases() -> list[str]:
    phrases: list[str] = []

    for n in NAMES:
        for h in HOOKS:
            phrases.append(f"{n}, {h}.")
            phrases.append(f"{n}, {h}, {random.choice(ACTIONS)}.")
            phrases.append(f"{n}, {h} — {random.choice(URGENCY)}.")
            phrases.append(f"{n}, {h} {random.choice(TOPICS)}.")
            phrases.append(f"{n}, {h} {random.choice(TOPICS)}, {random.choice(URGENCY)}.")

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

    for p in PEOPLE:
        phrases.append(f"{p.capitalize()}.")
        phrases.append(f"{p.capitalize()}, {random.choice(URGENCY)}.")
        phrases.append(f"У меня {p.lower()}, ждёт ответа.")
        phrases.append(f"{p.capitalize()} — {random.choice(ACTIONS)}.")

    for b in BIZ_TALK:
        phrases.append(f"{b.capitalize()}.")
        phrases.append(f"{b.capitalize()}, {random.choice(ACTIONS)}.")
        phrases.append(f"Короче, {b}.")
        phrases.append(f"Слушай, {b} — {random.choice(URGENCY)}.")

    for r in RESPONSES:
        phrases.append(r.capitalize())
        phrases.append(f"Ну {r.lower()}")
        phrases.append(f"И? {r.lower()}")
        phrases.append(f"Так {r.lower()}")

    for _ in range(400):
        parts = [
            random.choice(NAMES).capitalize(),
            random.choice(HOOKS),
            random.choice(TOPICS),
            random.choice(URGENCY),
            random.choice(ACTIONS),
            random.choice(DETAILS),
        ]
        chunk = parts[:1] + random.sample(parts[1:], k=random.randint(2, 4))
        s = ", ".join(p.strip(",.") for p in chunk)
        phrases.append(s[0].upper() + s[1:] + random.choice([".", "?", "!", "...", ""]))

    for _ in range(300):
        a = random.choice(NAMES).capitalize()
        b = random.choice(HOOKS)
        c = random.choice([*TOPICS, *BIZ_TALK, *MONEY])
        d = random.choice([*URGENCY, *ACTIONS])
        phrases.append(f"{a}, {b} {c} — {d}.")

    phrases = list({p.strip() for p in phrases if p.strip()})
    random.shuffle(phrases)
    return phrases


PHRASES = build_phrases()
log.info("Загружено фраз: %d", len(PHRASES))


def random_phrase() -> str:
    return random.choice(PHRASES)


THREADS = {
    "деньги": {
        "start": [
            "Слушай, по бабкам разговор",
            "Братан, тема по деньгам",
            "Короче, надо решить вопрос с переводом",
            "Слушай, там деньги пришли",
            "Братан, надо раскидать сумму",
        ],
        "mid": [
            "Сумма уже согласована",
            "Человек ждёт подтверждения",
            "Счёт открыт, надо закрыть",
            "Реквизиты скинул, глянь",
            "Лимит согласовали только что",
            "Платёж висит, надо провести",
        ],
        "end": [
            "Скинь как сможешь",
            "Подтверди, и закрываем",
            "Ответь, я на связи",
            "Жду от тебя отмашки",
            "Набери, объясню детали",
        ],
    },
    "встреча": {
        "start": [
            "Слушай, надо пересечься",
            "Братан, есть разговор не по телефону",
            "Короче, надо встретиться сегодня",
            "Есть тема, обсудим лично",
            "Слушай, заскочи на пять минут",
        ],
        "mid": [
            "Место знаешь, там же",
            "Человек подъедет к обеду",
            "Время поджимает, до вечера надо",
            "Партнёр ждёт, не затягивай",
            "Детали на месте расскажу",
        ],
        "end": [
            "Скажи во сколько сможешь",
            "Подтверди, я жду",
            "Набери как освободишься",
            "Маякни, когда выедешь",
            "Жду ответа",
        ],
    },
    "сделка": {
        "start": [
            "Слушай, по сделке движ пошёл",
            "Братан, контракт на подходе",
            "Короче, клиент дал добро",
            "Есть новости по проекту",
            "Слушай, условия приняли",
        ],
        "mid": [
            "Осталось только подписать",
            "Юрист проверил, всё чисто",
            "Партнёры согласны с цифрами",
            "Сроки сдвинули, но не критично",
            "Финальный вопрос по оплате",
        ],
        "end": [
            "Выходи на связь, обсудим",
            "Подтверди, что в теме",
            "Набери, детали расскажу",
            "Жду ответа до конца дня",
            "Маякни, как прочитаешь",
        ],
    },
    "поставка": {
        "start": [
            "Слушай, по отгрузке вопрос",
            "Братан, поставка на носу",
            "Короче, товар готов к отправке",
            "Есть момент по логистике",
            "Слушай, надо решить по срокам",
        ],
        "mid": [
            "Машину нашли, ждёт загрузки",
            "Склад подтвердил готовность",
            "Документы почти оформлены",
            "Таможня не должна тормознуть",
            "Клиент ждёт точную дату",
        ],
        "end": [
            "Дай ответ по срокам",
            "Подтверди, и запускаем",
            "Набери, обсудим детали",
            "Жду отмашки",
            "Маякни, как сможешь",
        ],
    },
    "срочно": {
        "start": [
            "Братан, вопрос на миллион",
            "Слушай, тут всё горит",
            "Короче, надо решить прямо сейчас",
            "Есть момент, не терпит",
            "Слушай, время поджимает",
        ],
        "mid": [
            "Человек на линии, ждёт ответа",
            "Окно возможности закрывается",
            "Если не сейчас, то потом поздно",
            "Всё готово, ждём только тебя",
            "Контрагент ждёт подтверждения",
        ],
        "end": [
            "Ответь срочно",
            "Набери прямо сейчас",
            "Дай ответ в течение часа",
            "Маякни сразу, как прочитаешь",
            "Жду, вопрос реально срочный",
        ],
    },
    "клиент": {
        "start": [
            "Слушай, клиент вышел на связь",
            "Братан, заказчик спрашивает",
            "Короче, по клиенту движ",
            "Есть запрос от партнёра",
            "Слушай, человек ждёт ответа",
        ],
        "mid": [
            "Хочет обсудить условия",
            "Готов подписывать, если всё ок",
            "Спрашивает про сроки",
            "Интересуется ценой",
            "Просит встречу на этой неделе",
        ],
        "end": [
            "Что ему ответить?",
            "Подтверди, я передам",
            "Набери, согласуем",
            "Дай отмашку",
            "Жду твоего решения",
        ],
    },
}


def build_thread() -> list[str]:
    thread = random.choice(list(THREADS.values()))
    chain = [random.choice(thread["start"])]
    n_mid = random.randint(0, 2)
    if n_mid:
        chain.extend(random.sample(thread["mid"], k=n_mid))
    chain.append(random.choice(thread["end"]))
    return chain


USERS: dict[int, dict] = {}

MODES = {
    "off": None,
    "rare": (60 * 60 * 3, 60 * 60 * 8),
    "normal": (60 * 30, 60 * 90),
    "often": (60 * 5, 60 * 15),
    "hard": (60, 60),
}

MODE_LABELS = {
    "off": "Выключить",
    "rare": "Редко",
    "normal": "Обычно",
    "often": "Очень часто",
    "hard": "Жесткий спам",
}


def schedule_next(user_id: int) -> None:
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
        mark = "[+] " if key == cur else ""
        kb.button(text=f"{mark}{label}", callback_data=f"mode:{key}")
    kb.adjust(1)
    return kb.as_markup()


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    await msg.answer(WELCOME_TEXT)


@dp.message(Command("start-sending"))
async def cmd_start_sending(msg: types.Message):
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
        await cb.answer("Сначала отправь /start-sending", show_alert=True)
        return
    mode = cb.data.split(":", 1)[1]
    if mode not in MODES:
        await cb.answer("Неизвестный режим", show_alert=True)
        return
    USERS[uid]["mode"] = mode
    schedule_next(uid)
    await cb.message.edit_reply_markup(reply_markup=kb_for(uid))
    await cb.answer(f"Режим: {MODE_LABELS[mode]}")


@dp.message()
async def fallback(msg: types.Message):
    uid = msg.from_user.id
    if uid in USERS:
        return
    await msg.answer(WELCOME_TEXT)


async def send_thread(uid: int) -> None:
    chain = build_thread()
    for i, text in enumerate(chain):
        try:
            await bot.send_message(uid, text)
        except Exception as e:
            log.warning("Не смог отправить %s: %s", uid, e)
            return
        if i < len(chain) - 1:
            await asyncio.sleep(random.randint(2, 5))


async def scheduler_loop():
    log.info("Планировщик запущен")
    while True:
        try:
            now = time.time()
            for uid, u in list(USERS.items()):
                if u["mode"] == "off":
                    continue
                if u["next_ts"] and now >= u["next_ts"]:
                    if u["mode"] == "hard":
                        asyncio.create_task(send_thread(uid))
                    else:
                        try:
                            await bot.send_message(uid, random_phrase())
                        except Exception as e:
                            log.warning("Не смог отправить %s: %s", uid, e)
                    if u["mode"] == "hard":
                        u["next_ts"] = time.time() + random.randint(1, 60)
                    else:
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
