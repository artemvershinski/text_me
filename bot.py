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

NAMES = [
    "братан", "брат", "родной", "слушай", "короче", "слышь", "дружище",
    "бро", "шеф", "командир", "мужик", "земеля", "старина", "друг",
]

HOOKS = [
    "у меня тема", "есть разговор", "есть движ", "появился вопрос",
    "нарисовалась тема", "есть один момент", "тут такое дело",
    "есть расклад", "надо пересечься", "надо перетереть",
    "есть новости", "есть инфа", "стоит вопрос", "надо обсудить",
    "есть предложение", "нарисовался момент", "появился расклад",
]

TOPICS = [
    "по бабкам", "по переводу", "по заносу", "по проекту", "по сделке",
    "по встрече", "по срокам", "по отгрузке", "по партнёрам", "по контракту",
    "по клиенту", "по оплате", "по поставке", "по закрытию", "по счетам",
    "по документам", "по налогам", "по юрикам", "по логистике", "по возврату",
    "по тендеру", "по персоналу", "по отчётности", "по инвойсу",
]

URGENCY = [
    "срочно", "очень срочно", "горит", "надо решить сегодня",
    "время поджимает", "не откладываем", "до конца дня", "в темпе",
    "вопрос часа", "прямо сейчас", "без затягиваний", "до вечера",
    "крайний срок", "на грани", "в приоритете",
]

ACTIONS = [
    "набери как сможешь", "позвони", "ответь", "маякни",
    "черкни пару слов", "скинь номер", "подтверди", "дай ответ",
    "будь на связи", "выйди на связь", "отпишись", "дай знать",
    "не пропадай", "на связи будь", "дай обратную связь",
]

DETAILS = [
    "детали позже", "подробности по телефону", "не в переписке",
    "объясню на словах", "не пиши сюда", "расскажу лично",
    "потом расскажу", "тут не всё так просто", "лично обсудим",
    "при встрече расскажу", "по телефону объясню",
    "не всё так однозначно", "деталей много",
]

PARTIES = [
    "поставщик", "клиент", "партнёр", "юрлицо", "контрагент",
    "инвестор", "заказчик", "подрядчик", "посредник", "брокер",
    "финдир", "аудитор", "юрист", "налоговая", "банк",
]

DEADLINES = [
    "до пятницы", "до конца недели", "до 25-го", "до конца месяца",
    "в течение дня", "до завтра", "к обеду", "до вечера",
    "сегодня до конца дня", "в течение часа", "в ближайшие дни",
    "до конца квартала", "на этой неделе", "до понедельника",
]

BANKS = [
    "Сбер", "Альфа", "ВТБ", "Тинькофф", "Райффайзен", "Открытие",
    "Газпромбанк", "Россельхоз", "Совкомбанк", "ПСБ",
]


def random_amount() -> str:
    style = random.choice([
        "digits", "digits_spaces", "million_short", "million_long",
        "slang_limon", "slang_lyam", "k_short", "full_verb",
        "million_plus_k", "half_million",
    ])
    base = random.choice([
        1_000_000, 1_200_000, 1_500_000, 1_800_000, 2_000_000, 2_300_000,
        2_500_000, 2_700_000, 3_000_000, 3_200_000, 3_500_000, 4_000_000,
        4_500_000, 5_000_000, 5_500_000, 6_000_000, 6_500_000, 7_000_000,
        7_500_000, 8_000_000, 9_000_000, 10_000_000, 12_000_000,
        15_000_000, 18_000_000, 20_000_000, 25_000_000, 30_000_000,
        35_000_000, 40_000_000, 50_000_000, 60_000_000, 75_000_000,
        80_000_000, 100_000_000, 120_000_000, 150_000_000,
        200_000_000, 250_000_000, 300_000_000, 500_000_000,
    ])
    if style == "digits":
        return f"{base}"
    if style == "digits_spaces":
        return f"{base:,}".replace(",", " ")
    if style == "million_short":
        v = base / 1_000_000
        if v == int(v):
            return f"{int(v)} млн"
        return f"{v:.1f} млн"
    if style == "million_long":
        v = base / 1_000_000
        if v == int(v):
            return f"{int(v)} миллиона"
        return f"{v:.1f} миллиона"
    if style == "slang_limon":
        n = base / 1_000_000
        if n == 1:
            return "один лимон"
        if n < 5:
            return f"{int(n)} лимона"
        return f"{int(n)} лимонов"
    if style == "slang_lyam":
        n = base / 1_000_000
        if n == 1:
            return "лям"
        if n < 5:
            return f"{int(n)} ляма"
        return f"{int(n)} лямов"
    if style == "k_short":
        return f"{int(base / 1000)}к"
    if style == "million_plus_k":
        m = base // 1_000_000
        k = (base % 1_000_000) // 1000
        if k == 0:
            return f"{m} млн"
        return f"{m} млн {k}к"
    if style == "half_million":
        return f"{base / 1_000_000:.1f} млн".replace(".0", "")
    return f"{base} рублей"


def fill(template: str) -> str:
    return (
        template
        .replace("{name}", random.choice(NAMES))
        .replace("{action}", random.choice(ACTIONS))
        .replace("{urgency}", random.choice(URGENCY))
        .replace("{detail}", random.choice(DETAILS))
        .replace("{topic}", random.choice(TOPICS))
        .replace("{amount}", random_amount())
        .replace("{party}", random.choice(PARTIES))
        .replace("{deadline}", random.choice(DEADLINES))
        .replace("{bank}", random.choice(BANKS))
    )


THREADS: dict[str, dict[str, list[str]]] = {
    "деньги": {
        "open": [
            "Слушай, по бабкам разговор",
            "Братан, тема по деньгам",
            "Короче, надо решить вопрос с переводом",
            "Слушай, там деньги пришли",
            "Братан, надо раскидать {amount}",
            "Есть момент по оплате на {amount}",
            "Слушай, надо закрыть платёж на {amount}",
            "{name}, {amount} надо перевести {party}",
            "Слушай, {party} ждёт {amount}",
        ],
        "detail": [
            "Сумма — {amount}, уже согласована",
            "Счёт открыт на {amount}, надо закрыть",
            "Реквизиты скинул, сумма {amount}",
            "Лимит согласовали — {amount}",
            "Платёж на {amount} висит",
            "{party} ждёт {amount}",
            "Копейка в копейку — {amount}, без задержек",
            "Часть ушла, остаток — {amount}",
            "Перевод через {bank}, сумма {amount}",
            "Срок — {deadline}, сумма {amount}",
        ],
        "push": [
            "Скинь {amount} как сможешь",
            "Подтверди {amount}, и закрываем",
            "Набери, объясню по {amount}",
            "Дай отмашку на {amount}, я запускаю",
            "Ответь по {amount}, я на связи",
            "Переведи {amount} {deadline}",
        ],
        "wait": [
            "Жду ответа по {amount}",
            "На связи? Вопрос на {amount}",
            "Ну что там с {amount}?",
            "Смотрю, читаешь, но по {amount} молчишь",
        ],
        "nudge": [
            "Ты тут вообще? {amount} ждёт",
            "Ответь, вопрос на {amount} не ждёт",
            "Читаешь же, ответь по {amount}",
            "Ау, братан, {amount}",
            "Напоминаю про {amount}",
            "{party} дёргает, {amount} висит",
        ],
        "escalate": [
            "Слушай, уже неудобно напоминать про {amount}",
            "Второй раз пишу, ответь по {amount}",
            "Время уходит, что по {amount}?",
            "Если не можешь, так и скажи по {amount}",
            "Так и будем молчать про {amount}?",
            "Срок {deadline}, а {amount} не переведён",
        ],
        "cold": [
            "Короче, пропал ты, {amount} снимаю",
            "Понял, вопрос на {amount} закрыт",
            "Ладно, сам решу по {amount}",
            "Больше не напоминаю про {amount}",
        ],
        "close": [
            "Всё, {amount} закрыли, спасибо",
            "Принял, тему на {amount} закрываю",
            "Ок, разобрались с {amount}",
        ],
    },
    "перевод": {
        "open": [
            "Слушай, надо перевести {amount}",
            "Братан, скинь {amount} по бизнесу",
            "Короче, вопрос по переводу на {amount}",
            "Слушай, надо перекинуть {amount}",
            "Братан, есть платёж на {amount}",
            "Слушай, надо закрыть счёт на {amount}",
            "{name}, {amount} надо отправить {party}",
            "Перевод на {amount} через {bank}",
        ],
        "detail": [
            "Сумма — {amount}, реквизиты скину",
            "Перевод на {amount}, {party} надёжный",
            "Надо {amount}, срок — {deadline}",
            "Сумма {amount}, всё согласовано",
            "На {amount}, {party} ждёт",
            "Провести надо {amount}, вопрос часа",
            "Банк — {bank}, сумма {amount}",
            "Перевод {party}, сумма {amount}, срок {deadline}",
        ],
        "push": [
            "Переведи {amount}, детали объясню",
            "Скинь {amount}, я в теме",
            "Набери, обсудим перевод на {amount}",
            "Подтверди перевод на {amount}",
            "Дай отмашку на {amount} {deadline}",
        ],
        "wait": [
            "Жду подтверждения по {amount}",
            "Ну что там с переводом на {amount}?",
            "Перевод на {amount} — ответь",
            "Смотрю, читаешь, но {amount} не ушёл",
        ],
        "nudge": [
            "Ау, перевод на {amount} висит",
            "Напоминаю про {amount}",
            "Ты пропал, а сумма {amount} ждёт",
            "Перевод на {amount} не сделан",
            "{party} дёргает по {amount}",
        ],
        "escalate": [
            "Второй раз пишу про {amount}",
            "Сумма {amount} — вопрос серьёзный",
            "Если не можешь, так и скажи по {amount}",
            "Перевод на {amount} — время идёт",
            "Срок {deadline}, {amount} не ушёл",
        ],
        "cold": [
            "Понял, перевод на {amount} снимаю",
            "Ладно, сам проведу {amount}",
            "Больше не напоминаю про {amount}",
        ],
        "close": [
            "Всё, перевод на {amount} прошёл",
            "Принял, {amount} закрыли",
        ],
    },
    "встреча": {
        "open": [
            "Слушай, надо пересечься",
            "Братан, есть разговор не по телефону",
            "Короче, надо встретиться {deadline}",
            "Есть тема, обсудим лично",
            "Слушай, заскочи на пять минут",
            "Надо увидеться, не по переписке",
            "{name}, {party} хочет встретиться",
        ],
        "detail": [
            "Место знаешь, там же",
            "{party} подъедет к обеду",
            "Время поджимает, до вечера надо",
            "{party} ждёт, не затягивай",
            "Детали на месте расскажу",
            "Лучше лично, вопрос тонкий",
            "Приезжай, тут {party} ждёт",
            "Срок — {deadline}, встречаемся",
        ],
        "push": [
            "Скажи во сколько сможешь",
            "Подтверди, я жду",
            "Набери как освободишься",
            "Маякни, когда выедешь",
            "Дай точное время",
        ],
        "wait": [
            "Жду ответа",
            "Ну что по встрече?",
            "Смотрю, читаешь, но молчишь",
        ],
        "nudge": [
            "Ты выезжаешь или нет?",
            "Ау, по встрече что?",
            "Мы вообще встречаемся?",
            "Время идёт, ты не отвечаешь",
        ],
        "escalate": [
            "Второй раз спрашиваю",
            "Слушай, я не могу так планировать",
            "Если не можешь, скажи прямо",
            "Так встречаемся или нет?",
        ],
        "cold": [
            "Понял, встреча отменяется",
            "Ладно, сам разберусь",
            "Больше не дёргаю",
            "Ок, вопрос снимаю",
        ],
        "close": [
            "Всё, увиделись, вопрос закрыли",
            "Принял, до встречи",
        ],
    },
    "сделка": {
        "open": [
            "Слушай, по сделке движ пошёл",
            "Братан, контракт на подходе",
            "Короче, {party} дал добро",
            "Есть новости по проекту",
            "Слушай, условия приняли",
            "Сделка сдвинулась с места",
            "{name}, контракт на {amount}",
        ],
        "detail": [
            "Осталось только подписать",
            "Юрист проверил, всё чисто",
            "{party} согласен с цифрами",
            "Сроки сдвинули, но не критично",
            "Финальный вопрос по {amount}",
            "Подписи только за тобой",
            "Все согласовали, надо запускать",
            "Сумма контракта — {amount}, срок {deadline}",
        ],
        "push": [
            "Выходи на связь, обсудим",
            "Подтверди, что в теме",
            "Набери, детали расскажу",
            "Дай отмашку, я подписываю",
            "Подтверди {amount}, и стартуем",
        ],
        "wait": [
            "Жду ответа",
            "Ну что по сделке?",
            "Читаешь, но молчишь",
        ],
        "nudge": [
            "Слушай, по сделке что?",
            "Ау, ты в теме или нет?",
            "Вопрос по контракту на {amount} висит",
            "Напоминаю про сделку",
        ],
        "escalate": [
            "Уже неудобно напоминать",
            "Второй раз пишу, ответь",
            "Сделка на {amount} ждёт, а ты молчишь",
            "Если не в теме, скажи прямо",
        ],
        "cold": [
            "Понял, сделка отменяется",
            "Ладно, сам решу вопрос",
            "Больше не напоминаю",
            "Ок, тему закрываю",
        ],
        "close": [
            "Всё, подписали, спасибо",
            "Принял, сделку на {amount} закрыли",
        ],
    },
    "поставка": {
        "open": [
            "Слушай, по отгрузке вопрос",
            "Братан, поставка на носу",
            "Короче, товар готов к отправке",
            "Есть момент по логистике",
            "Слушай, надо решить по срокам",
            "{party} ждёт поставку",
        ],
        "detail": [
            "Машину нашли, ждёт загрузки",
            "Склад подтвердил готовность",
            "Документы почти оформлены",
            "Таможня не должна тормознуть",
            "{party} ждёт точную дату",
            "Водила на связи, ждёт адрес",
            "Срок — {deadline}, груз готов",
        ],
        "push": [
            "Дай ответ по срокам",
            "Подтверди, и запускаем",
            "Набери, обсудим детали",
            "Жду отмашки",
        ],
        "wait": ["Жду ответа", "Ну что по поставке?", "Читаешь, но молчишь"],
        "nudge": [
            "Машина стоит, ждёт",
            "Ау, по отгрузке что?",
            "{party} дёргает, ответь",
            "Напоминаю про поставку",
        ],
        "escalate": [
            "Второй раз пишу",
            "Логистика не может ждать",
            "Если не можешь, скажи",
            "Сроки горят, ответь",
        ],
        "cold": [
            "Понял, поставку отменяю",
            "Ладно, сам решу",
            "Больше не напоминаю",
        ],
        "close": ["Всё, отгрузили", "Принял, тему закрыли"],
    },
    "срочно": {
        "open": [
            "Братан, вопрос на миллион",
            "Слушай, тут всё горит",
            "Короче, надо решить прямо сейчас",
            "Есть момент, не терпит",
            "Слушай, время поджимает",
            "{name}, {amount} — вопрос часа",
        ],
        "detail": [
            "{party} на линии, ждёт ответа",
            "Окно возможности закрывается",
            "Если не сейчас, то потом поздно",
            "Всё готово, ждём только тебя",
            "{party} ждёт подтверждения",
            "Сумма {amount}, срок {deadline}",
        ],
        "push": [
            "Ответь срочно",
            "Набери прямо сейчас",
            "Дай ответ в течение часа",
            "Маякни сразу, как прочитаешь",
        ],
        "wait": ["Жду", "Срочно ответь", "Ты тут?"],
        "nudge": [
            "Это реально срочно",
            "Время уходит, ответь",
            "Ау, вопрос на {amount} горит",
        ],
        "escalate": [
            "Я не могу больше ждать",
            "Всё, время вышло",
            "Если не ответишь сейчас, решаю сам",
        ],
        "cold": ["Понял, решаю сам", "Больше не дёргаю"],
        "close": ["Всё, вопрос закрыли"],
    },
    "клиент": {
        "open": [
            "Слушай, {party} вышел на связь",
            "Братан, {party} спрашивает",
            "Короче, по {party} движ",
            "Есть запрос от {party}",
            "Слушай, {party} ждёт ответа",
        ],
        "detail": [
            "Хочет обсудить условия",
            "Готов подписывать, если всё ок",
            "Спрашивает про сроки",
            "Интересуется ценой",
            "Просит встречу {deadline}",
            "Говорит, что рассматривает нас",
            "Бюджет — {amount}",
        ],
        "push": [
            "Что ему ответить?",
            "Подтверди, я передам",
            "Набери, согласуем",
            "Дай отмашку",
        ],
        "wait": ["Жду твоего решения", "Ну что по клиенту?", "Ты в теме?"],
        "nudge": [
            "{party} дёргает, ответь",
            "Ау, что передать?",
            "{party} ждёт, не молчи",
        ],
        "escalate": [
            "Второй раз спрашиваю",
            "{party} уходит, если не ответим",
            "Скажи хоть что-то",
        ],
        "cold": ["Понял, отвечаю сам", "Больше не напоминаю"],
        "close": ["Всё, клиента взяли"],
    },
    "долг": {
        "open": [
            "Слушай, по долгу вопрос",
            "Братан, надо закрыть старый долг — {amount}",
            "Короче, помнишь, я занимал {amount}",
            "Слушай, по возврату {amount}",
        ],
        "detail": [
            "Сумма — {amount}, помнишь",
            "Сроки уже прошли по {amount}",
            "Я не давлю, но {amount} надо решить",
            "Мне самому сейчас нужно {amount}",
            "Срок был {deadline}",
        ],
        "push": [
            "Скинь {amount} как сможешь",
            "Ответь по долгу {amount}",
            "Набери, обсудим {amount}",
        ],
        "wait": [
            "Жду по {amount}",
            "Ну что по долгу {amount}?",
            "Не молчи про {amount}",
        ],
        "nudge": [
            "Напоминаю про {amount}",
            "Ау, вопрос на {amount} висит",
            "Ты пропал, а долг {amount} остался",
        ],
        "escalate": [
            "Слушай, так не делается с {amount}",
            "Второй раз пишу про {amount}",
            "Если не можешь, скажи прямо по {amount}",
        ],
        "cold": [
            "Понял, забудь про {amount}",
            "Больше не напоминаю про {amount}",
        ],
        "close": [
            "Всё, долг {amount} закрыли, спасибо",
        ],
    },
    "отчёт": {
        "open": [
            "Слушай, нужен отчёт",
            "Братан, скинь цифры",
            "Короче, по отчёту вопрос",
            "Есть момент по документам",
            "{party} просит отчёт",
        ],
        "detail": [
            "Нужны цифры за месяц",
            "Бухгалтер спрашивает",
            "Дедлайн — {deadline}",
            "Без отчёта не закрыть период",
            "Сумма оборота — {amount}",
        ],
        "push": ["Скинь как сможешь", "Подтверди сроки", "Набери"],
        "wait": ["Жду отчёт", "Ну что по цифрам?", "Ты в теме?"],
        "nudge": ["Ау, отчёт нужен", "Напоминаю про цифры", "Бухгалтер дёргает"],
        "escalate": ["Второй раз пишу", "Сроки горят", "Если не можешь, скажи"],
        "cold": ["Понял, сам сделаю", "Больше не напоминаю"],
        "close": ["Всё, отчёт получил, спасибо"],
    },
    "партнёр": {
        "open": [
            "Слушай, {party} вышел на связь",
            "Братан, есть предложение от {party}",
            "Короче, по партнёрству вопрос",
        ],
        "detail": [
            "Предлагают войти в долю на {amount}",
            "Хотят обсудить условия",
            "Готовы подписать, если ок",
            "Спрашивают про наши планы",
            "Срок — {deadline}",
        ],
        "push": ["Что ответить?", "Подтверди, я передам", "Набери"],
        "wait": ["Жду решения", "Ну что по партнёру?"],
        "nudge": ["{party} дёргает", "Ау, ответь", "Вопрос висит"],
        "escalate": ["Второй раз пишу", "Окно закрывается", "Скажи хоть что-то"],
        "cold": ["Понял, отвечаю сам"],
        "close": ["Всё, договорились с партнёром"],
    },
    "налог": {
        "open": [
            "Слушай, по налогам вопрос",
            "Братан, надо закрыть налоговую",
            "Короче, сроки по налогам подходят",
        ],
        "detail": [
            "Бухгалтер посчитал — {amount}",
            "Документы готовы",
            "Дедлайн — {deadline}",
            "Через {bank} оплата",
        ],
        "push": ["Подтверди оплату", "Скинь как сможешь", "Набери"],
        "wait": ["Жду", "Ну что по налогам?"],
        "nudge": ["Напоминаю про налоги", "Ау, сроки идут"],
        "escalate": ["Второй раз пишу", "Штрафы будут, ответь"],
        "cold": ["Понял, сам решу"],
        "close": ["Всё, налоги закрыли"],
    },
    "юрист": {
        "open": [
            "Слушай, юрист звонил",
            "Братан, есть вопрос по документам",
            "Короче, надо к юристу заехать",
        ],
        "detail": [
            "Просит подписать бумаги",
            "Нашёл момент в договоре",
            "Надо согласовать правки",
            "Сумма вопроса — {amount}",
        ],
        "push": ["Подтверди, я передам", "Набери", "Дай отмашку"],
        "wait": ["Жду", "Ну что по юристу?"],
        "nudge": ["Ау, юрист ждёт", "Напоминаю про документы"],
        "escalate": ["Второй раз пишу", "Сроки по бумагам горят"],
        "cold": ["Понял, сам решу"],
        "close": ["Всё, бумаги подписали"],
    },
    "логистика": {
        "open": [
            "Слушай, по логистике вопрос",
            "Братан, машина на подходе",
            "Короче, надо решить по доставке",
        ],
        "detail": [
            "Водила на связи",
            "Адрес уточнить надо",
            "Время разгрузки согласовать",
            "Срок — {deadline}",
        ],
        "push": ["Подтверди адрес", "Набери", "Дай отмашку"],
        "wait": ["Жду", "Ну что по логистике?"],
        "nudge": ["Машина стоит", "Ау, ответь"],
        "escalate": ["Второй раз пишу", "Простой будет, ответь"],
        "cold": ["Понял, сам решу"],
        "close": ["Всё, разгрузились"],
    },
    "персонал": {
        "open": [
            "Слушай, по людям вопрос",
            "Братан, надо решить по сотрудникам",
            "Короче, человечка найти надо",
        ],
        "detail": [
            "Резюме скинули",
            "Собеседование {deadline}",
            "Оклад обсуждаем — {amount}",
        ],
        "push": ["Что скажешь?", "Набери", "Дай отмашку"],
        "wait": ["Жду", "Ну что по людям?"],
        "nudge": ["Ау, вопрос по персоналу", "Напоминаю"],
        "escalate": ["Второй раз пишу", "Люди ждут ответа"],
        "cold": ["Понял, сам решу"],
        "close": ["Всё, человека взяли"],
    },
    "тендер": {
        "open": [
            "Слушай, тендер на носу",
            "Братан, надо подать заявку",
            "Короче, по тендеру вопрос",
        ],
        "detail": [
            "Документы почти готовы",
            "Условия подходят",
            "Конкуренты тоже в теме",
            "Сумма тендера — {amount}",
        ],
        "push": ["Подтверди участие", "Набери", "Дай отмашку"],
        "wait": ["Жду", "Ну что по тендеру?"],
        "nudge": ["Ау, сроки подачи", "Напоминаю про тендер"],
        "escalate": ["Второй раз пишу", "Окно закрывается"],
        "cold": ["Понял, не участвуем"],
        "close": ["Всё, заявку подали"],
    },
    "возврат": {
        "open": [
            "Слушай, по возврату вопрос",
            "Братан, {party} хочет вернуть",
            "Короче, надо решить по возврату",
        ],
        "detail": [
            "Сумма — {amount}",
            "Претензий по качеству нет",
            "Хотят просто вернуть",
            "Срок — {deadline}",
        ],
        "push": ["Что делаем?", "Набери", "Дай отмашку"],
        "wait": ["Жду", "Ну что по возврату?"],
        "nudge": ["Ау, {party} ждёт", "Напоминаю"],
        "escalate": ["Второй раз пишу", "Скандал будет"],
        "cold": ["Понял, сам решу"],
        "close": ["Всё, возврат закрыли"],
    },
}

STAGE_ORDER = ["open", "detail", "push", "wait", "nudge", "escalate", "cold", "close"]


def build_phrases() -> list[str]:
    phrases: list[str] = []
    for n in NAMES:
        for h in HOOKS:
            phrases.append(f"{n}, {h}.")
            phrases.append(f"{n}, {h}, {random.choice(ACTIONS)}.")
            phrases.append(f"{n}, {h} — {random.choice(URGENCY)}.")
            phrases.append(f"{n}, {h} {random.choice(TOPICS)}.")
            phrases.append(f"{n}, {h} {random.choice(TOPICS)}, {random.choice(URGENCY)}.")
    for _ in range(600):
        phrases.append(fill("{name}, {action} — {urgency}."))
        phrases.append(fill("Слушай, {topic}, {action}."))
        phrases.append(fill("Короче, {detail}."))
        phrases.append(fill("{name}, {topic} — {action}."))
        phrases.append(fill("Слушай, {topic}, {urgency}."))
    for _ in range(500):
        phrases.append(fill("Слушай, надо перевести {amount}"))
        phrases.append(fill("Братан, скинь {amount}"))
        phrases.append(fill("Короче, платёж на {amount}"))
        phrases.append(fill("Вопрос на {amount}, {action}"))
        phrases.append(fill("Перевод на {amount} — {urgency}"))
        phrases.append(fill("Надо закрыть {amount}, {action}"))
        phrases.append(fill("{name}, {amount} ждёт, {action}"))
        phrases.append(fill("Сумма {amount}, {detail}"))
        phrases.append(fill("{party} ждёт {amount}, срок {deadline}"))
        phrases.append(fill("Перевод через {bank} на {amount}"))
        phrases.append(fill("{name}, {party} хочет {amount}"))
        phrases.append(fill("Срок {deadline}, сумма {amount}"))
        phrases.append(fill("{party} подтвердил {amount}"))
    phrases = list({p.strip() for p in phrases if p.strip()})
    random.shuffle(phrases)
    return phrases


PHRASES = build_phrases()
log.info("Загружено базовых фраз: %d", len(PHRASES))


def random_phrase() -> str:
    return fill(random.choice(PHRASES))


def build_series(stage_index: int) -> list[str]:
    thread = random.choice(list(THREADS.values()))
    n = random.randint(2, 4)
    series: list[str] = []
    for i in range(n):
        idx = min(stage_index + i, len(STAGE_ORDER) - 1)
        stage = STAGE_ORDER[idx]
        pool = thread.get(stage) or thread.get("wait") or ["..."]
        series.append(fill(random.choice(pool)))
    return series


def next_stage_index(current: int) -> int:
    if current == 0:
        return 1
    return min(current + 1, len(STAGE_ORDER) - 2)


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
    USERS.setdefault(uid, {
        "mode": "off",
        "next_ts": 0.0,
        "stage": 0,
        "ignored": 0,
    })
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
    USERS[uid]["stage"] = 0
    USERS[uid]["ignored"] = 0
    schedule_next(uid)
    await cb.message.edit_reply_markup(reply_markup=kb_for(uid))
    await cb.answer(f"Режим: {MODE_LABELS[mode]}")


@dp.message()
async def fallback(msg: types.Message):
    uid = msg.from_user.id
    if uid not in USERS:
        await msg.answer(WELCOME_TEXT)
        return
    u = USERS[uid]
    if u["mode"] == "off":
        return
    u["stage"] = 0
    u["ignored"] = 0
    schedule_next(uid)


async def send_series(uid: int) -> None:
    u = USERS.get(uid)
    if not u:
        return
    series = build_series(u["stage"])
    for i, text in enumerate(series):
        try:
            await bot.send_message(uid, text)
        except Exception as e:
            log.warning("Не смог отправить %s: %s", uid, e)
            return
        if i < len(series) - 1:
            await asyncio.sleep(random.randint(2, 5))
    u["ignored"] += 1
    u["stage"] = next_stage_index(u["stage"])


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
                        asyncio.create_task(send_series(uid))
                        u["next_ts"] = time.time() + random.randint(1, 60)
                    else:
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
