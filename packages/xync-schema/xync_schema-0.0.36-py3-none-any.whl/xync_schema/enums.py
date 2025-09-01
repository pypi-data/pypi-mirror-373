from enum import IntEnum


class PersonStatus(IntEnum):
    VIP = 2
    DEFAULT = 1
    BLOCKED = 0


class TransactionStatus(IntEnum):
    request = 2  # no proof
    signed = 3  # in proof: sender sign for transfer
    valid = 4  # in proof: validator sign for transfer is valid


class UserStatus(IntEnum):
    SLEEP = 0
    PAY = 1
    ACTIVE = 2


class AdStatus(IntEnum):
    defActive = 0
    active = 1
    soldOut = 2
    old = 3
    four = 4
    notFound = 9


class OrderStatus(IntEnum):
    deleted = 0
    requested = 1
    request_canceled = 2
    created = 3
    rejected = 4
    paid = 5
    canceled = 6
    completed = 7
    appealable = 8
    appealed_by_seller = 9
    appealed_by_buyer = 10
    seller_appeal_disputed_by_buyer = 11
    buyer_appeal_disputed_by_seller = 12
    # todo: 8T - один вирт экшн на бездействие обеих сторон, а 12T и 13T - по отдельности?
    # COMPLETED, PENDING, TRADING, BUYER_PAYED, DISTRIBUTING, COMPLETED, IN_APPEAL, CANCELLED, CANCELLED_BY_SYSTEM


class ExType(IntEnum):
    p2p = 1
    cex = 2
    main = 3  # p2p+cex
    dex = 4
    tg = 5
    futures = 8


class DepType(IntEnum):
    earn = 1
    stake = 2
    beth = 3
    lend = 4


class AddrExType(IntEnum):
    spot = 1
    earn = 2
    found = 3


class TradeType(IntEnum):
    BUY = 0
    SELL = 1


class PmType(IntEnum):
    bank = 0
    emoney = 1
    cash = 2
    card = 4
    gift_card = 3
    IFSC = 5
    SBP = 6
    phone = 7


class TaskType(IntEnum):
    invite_approve = 1


class FileType(IntEnum):
    pdf = 1
    jpg = 2
    png = 3
    webp = 4
    mov = 5
    mp4 = 6
    gif = 7
    svg = 8
    tgs = 9
    jpeg = 10


class SynonymType(IntEnum):
    name = 1
    ppo = 2
    from_party = 3
    to_party = 4
    slip_req = 5
    slip_send = 6
    abuser = 7
    scale = 8
    slavic = 9
    mtl_like = 10
    bank = 11
    bank_side = 12
    sbp_strict = 13
    contact = 14


class Boundary(IntEnum):
    no = 0
    left = 1
    right = 2
    both = 3


class SbpStrict(IntEnum):
    no = 0
    sbp = 1
    card = 2


class Party(IntEnum):
    fst = 0
    fam = 1
    lk = 2  # lk-photo/video/comment
    trd = 3


class Slip(IntEnum):
    no = 0
    screen = 1
    pdf = 2
    pdf_mail = 3


class NameType(IntEnum):
    no_slavic = 0
    slavic = 1
    fake = 2


class AbuserType(IntEnum):
    no = 0
    rating = 1  # рейт: жмет "Оплачено" сразу, "Отмена" по аппеляции
    fake = 2  # реклама
    cash = 3  # типа кэш обменник, но хз


class ExStatus(IntEnum):
    plan = 0
    parted = 1
    full = 2


class ExAction(IntEnum):
    """Order"""

    get_orders = 0  # Получшение заявок за заданное время, в статусе, по валюте, монете, направлению: `get_orders(stauts=OrderStatus.active, coin='USDT', cur='RUB', is_sell=False) => [order]`
    order_request = 1  # [T] Запрос на старт сделки
    order_request_ask = -1  # [M] - Запрос мейкеру на сделку
    cancel_request = 2  # [T] Отмена запроса на сделку
    request_canceled = -2  # [M] - Уведомление об отмене запроса на сделку
    accept_request = 3  # [M] Одобрить запрос на сделку
    request_accepted = -3  # [T] Уведомление об одобрении запроса на сделку
    reject_request = 4  # [M] Отклонить запрос на сделку
    request_rejected = -4  # [T] Уведомление об отклонении запроса на сделку
    mark_payed = 5  # [B] Перевод сделки в состояние "оплачено", c отправкой чека
    payed = -5  # [S] Уведомиление продавца об оплате
    cancel_order = 6  # [B] Отмена сделки
    order_canceled = -6  # [S] Уведомиление продавцу об отмене оредера покупателем
    confirm = 7  # [S] Подтвердить получение оплаты
    order_completed = -7  # [B] Уведомиление покупателю об успешном завершении продавцом
    appeal_available = -8  # [S,B] Уведомление о наступлении возможности подать аппеляцию
    start_appeal = 9  # ,10 # [S,B] Подать аппеляцию cо скриншотом/видео/файлом
    appeal_started = -9  # ,-10 # [S,B] Уведомление о поданной на меня аппеляци
    dispute_appeal = 11  # ,12 # [S,B] Встречное оспаривание полученной аппеляции cо скриншотом/видео/файлом
    appeal_disputed = -11  # ,-12 # [S,B] Уведомление о встречном оспаривание поданной аппеляции
    order_completed_by_appeal = -13  # [S,B] Уведомление о завершении сделки по аппеляции
    order_canceled_by_appeal = -14  # [B,S] Уведомление об отмене сделки по аппеляции
    cancel_appeal = 15  # [B,S] Отмена аппеляции
    appeal_canceled = -15  # [B,S] Уведомление об отмене аппеляции против меня
    send_order_msg = 16  # Отправка сообщения юзеру в чат по ордеру с приложенным файлом
    got_order_msg = -16  # Получение сообщения в чате по ордеру
    send_appeal_msg = 17  # Отправка сообщения по апелляции
    got_appeal_msg = -17  # Получение сообщения по апелляции
    """ Ex: Public """
    # curs = 19  # Список поддерживаемых валют тейкера
    pms = 20  # Список платежных методов по каждой валюте
    cur_pms_map = 21  # Мэппинг валюта => платежные методы
    coins = 22  # Список торгуемых монет (с ограничениям по валютам, если есть)
    pairs = 23  # Список пар валюта/монет
    ads = 24  # Список объяв по покупке/продаже, валюте, монете, платежному методу (buy/sell, cur, coin, pm)
    set_coins = 44  # обновление монет биржи в бд
    set_curs = 19  # обновление валют и платежек биржи в бд
    set_pms = 45  # обновление валют и платежек биржи в бд
    set_pairs = 46  # обновление пар биржи в бд
    ad = 42  # Чужая объява по id
    """ Agent: Fiat """
    my_creds = 25  # Список реквизитов моих платежных методов
    cred_new = 26  # Создание реквизита моего платежного метода
    cred_upd = 27  # Редактирование реквизита моего платежного метода
    cred_del = 28  # Удаление реквизита моего платежного метода
    """ Agent: Ad """
    my_ads = 29  # Список моих объявлений
    my_ad = 43  # Моя объява по id
    ad_new = 30  # Создание объявления
    ad_upd = 31  # Редактирование объявления
    ad_del = 32  # Удаление объявления
    ad_switch = 33  # Вкл/выкл объявления
    ads_switch = 34  # Вкл/выкл всех объявлений
    """ Agent: Taker """
    get_user = 35  # Получить объект юзера по его id
    send_user_msg = 36  # Отправка сообщения юзеру с приложенным файлом
    block_user = 37  # [Раз]Блокировать пользователя
    rate_user = 38  # Поставить отзыв пользователю
    """ Agent: Inbound """
    got_user_msg = -36  # Получение сообщения от пользователя
    got_blocked = -37  # Получение уведомления о [раз]блокировке пользователем
    got_rated = -38  # Получение уведомления о полученном отзыве

    """ Assets """
    assets = 39  # Балансы моих монет
    deposit = 40  # Получить реквизиты для депозита монеты
    deposited = -40  # Получена монета
    withdraw = 41  # Вывести монету
    withdrew = -41  # Монета выведена
