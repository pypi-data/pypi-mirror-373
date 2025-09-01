import struct
import sys
from uuid import UUID
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from asyncpg.pgproto.pgproto import utc
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from tortoise.fields import (
    SmallIntField,
    IntField,
    BigIntField,
    CharField,
    BooleanField,
    IntEnumField,
    FloatField,
    JSONField,
    ForeignKeyField,
    OneToOneField,
    ManyToManyField,
    ForeignKeyRelation,
    OneToOneRelation,
    ForeignKeyNullableRelation,
    OneToOneNullableRelation,
    ManyToManyRelation,
    UUIDField,
)
from tortoise.fields.relational import BackwardFKRelation, BackwardOneToOneRelation
from tortoise.functions import Sum
from tortoise.queryset import QuerySet
from tortoise import Model as BaseModel
from tortoise.signals import pre_save

# noinspection PyUnresolvedReferences
from x_auth.models import (
    Model,
    Username as Username,
    User as TgUser,
    Proxy as Proxy,
    Dc as Dc,
    Fcm as Fcm,
    App as App,
    Session as Session,
    Peer as Peer,
    UpdateState as UpdateState,
    Version as Version,
    Country as BaseCountry,
    UniqBinaryField,
)
from x_model.models import TsTrait, DatetimeSecField

from xync_schema.enums import (
    ExType,
    AdStatus,
    OrderStatus,
    ExAction,
    ExStatus,
    PersonStatus,
    UserStatus,
    PmType,
    FileType,
    AddrExType,
    DepType,
    Party,
    Slip,
    SynonymType,
    AbuserType,
    Boundary,
    SbpStrict,
    TransactionStatus as TS,
)


class Country(BaseCountry):
    cur: ForeignKeyRelation["Cur"] = ForeignKeyField("models.Cur", related_name="countries")
    curexs: ManyToManyRelation["CurEx"]
    forbidden_exs: ManyToManyRelation["Ex"]
    fiats: BackwardFKRelation["Fiat"]


class Cur(Model):
    id = SmallIntField(True)
    ticker: str = CharField(3, unique=True)
    scale: int = SmallIntField(default=0)
    rate: float | None = FloatField(default=0, null=True)

    pms: ManyToManyRelation["Pm"] = ManyToManyField("models.Pm", through="pmcur")
    exs: ManyToManyRelation["Ex"] = ManyToManyField("models.Ex", through="curex")
    pairs: BackwardFKRelation["Pair"]
    countries: BackwardFKRelation[Country]
    synonyms: ManyToManyRelation["Synonym"]

    _name = {"ticker"}

    class Meta:
        table_description = "Fiat currencies"


class Coin(Model):
    id: int = SmallIntField(True)
    ticker: str = CharField(15, unique=True)
    rate: float | None = FloatField(default=0)
    is_fiat: bool = BooleanField(default=False)
    scale: int = SmallIntField(default=4)
    exs: ManyToManyRelation["Ex"] = ManyToManyField("models.Ex", through="coinex")

    assets: BackwardFKRelation["Asset"]
    nets: BackwardFKRelation["Net"]
    pairs: BackwardFKRelation["Pair"]
    # deps: BackwardFKRelation["Dep"]
    # deps_reward: BackwardFKRelation["Dep"]
    # deps_bonus: ReverseRelation["Dep"]

    _name = {"ticker"}


class Net(Model):
    id: int = SmallIntField(True)
    name: str = CharField(63)
    native_coin: ForeignKeyRelation[Coin] = ForeignKeyField("models.Coin", related_name="nets")
    native_coin_id: int


class Ex(Model):
    id: int = SmallIntField(True)
    name: str = CharField(31)
    host: str | None = CharField(63, null=True, description="With no protocol 'https://'")
    host_p2p: str | None = CharField(63, null=True, description="With no protocol 'https://'")
    url_login: str | None = CharField(63, null=True, description="With no protocol 'https://'")
    typ: ExType = IntEnumField(ExType)
    status: ExStatus = IntEnumField(ExStatus, default=ExStatus.plan)
    logo: str = CharField(511, default="")

    ads: ManyToManyRelation["Ad"]
    pms: ManyToManyRelation["Pm"]
    curs: ManyToManyRelation[Cur]
    # pmcurs: ManyToManyRelation["PmCur"] = ManyToManyField("models.PmCur", through="pmcurex")
    coins: ManyToManyRelation[Coin]
    forbidden_countries: ManyToManyRelation[Country] = ManyToManyField("models.Country", related_name="forbidden_exs")

    actors: BackwardFKRelation["Actor"]
    pmexs: BackwardFKRelation["PmEx"]
    pm_reps: BackwardFKRelation["PmRep"]
    pairexs: BackwardFKRelation["PairEx"]
    deps: BackwardFKRelation["Dep"]
    stats: BackwardFKRelation["ExStat"]

    class Meta:
        table_description = "Exchanges"
        unique_together = (("name", "typ"),)

    class PydanticMeta(Model.PydanticMeta):
        include = "name", "logo"

    def client(self, bot, **kwargs):
        module_name = f"xync_client.{self.name}.ex"
        __import__(module_name)
        client = sys.modules[module_name].ExClient
        return client(self, bot, **kwargs)


class CurEx(BaseModel):
    cur: ForeignKeyRelation[Cur] = ForeignKeyField("models.Cur")
    cur_id: int
    ex: ForeignKeyRelation[Ex] = ForeignKeyField("models.Ex")
    ex_id: int
    exid: str = CharField(32)
    minimum: int = IntField(null=True)  # /10^cur.scale
    scale: int = SmallIntField(null=True)

    # countries: ManyToManyRelation[Country] = ManyToManyField (
    #     "models.Country", through="curex_country", backward_key="curexs"
    # )

    class Meta:
        table_description = "Currency in Exchange"
        unique_together = (("ex_id", "cur_id"), ("ex_id", "exid"))


class CoinEx(BaseModel):
    coin: ForeignKeyRelation[Coin] = ForeignKeyField("models.Coin")
    coin_id: int
    ex: ForeignKeyRelation[Ex] = ForeignKeyField("models.Ex")
    minimum: int = IntField(null=True)  # /10^self.scale
    scale: int = SmallIntField(default=4)

    exid: str = CharField(32)
    p2p: bool = BooleanField(default=True)

    class Meta:
        table_description = "Currency in Exchange"
        unique_together = (("ex_id", "coin_id"), ("ex_id", "exid"))


class Pair(Model):
    id = SmallIntField(True)
    coin: ForeignKeyRelation[Coin] = ForeignKeyField("models.Coin", related_name="pairs")
    cur: ForeignKeyRelation[Cur] = ForeignKeyField("models.Cur", related_name="pairs")

    _name = {"coin__ticker", "cur__ticker"}

    class Meta:
        table_description = "Coin/Currency pairs"
        unique_together = (("coin_id", "cur_id"),)


class PairSide(Model):  # Way
    id = SmallIntField(True)
    pair: ForeignKeyRelation[Pair] = ForeignKeyField("models.Pair", related_name="pair_sides")
    pair_id: int
    is_sell: bool = BooleanField()

    class Meta:
        table = "pair_side"
        unique_together = (("pair_id", "is_sell"),)


class NetAddr(Model):  # Way
    net: ForeignKeyRelation[Net] = ForeignKeyField("models.Net", "net_addrs")
    net_id: int
    addr: ForeignKeyRelation["Addr"] = ForeignKeyField("models.Addr", "net_addrs")
    addr_id: int
    val: str = CharField(200)
    memo: str | None = CharField(54, null=True)
    qr: str | None = CharField(255, null=True)

    class Meta:
        table = "net_addr"
        unique_together = (("net_id", "addr_id"),)


class PairEx(Model, TsTrait):  # todo: refact to PairSideEx?
    # todo: различаются ли комиссии на buy/sell по одной паре хоть на одной бирже? если да, то переделать
    pair: ForeignKeyRelation[Pair] = ForeignKeyField("models.Pair", related_name="pairexs")
    pair_id: int
    fee: int = SmallIntField(default=0)  # /10_000
    ex: ForeignKeyRelation[Ex] = ForeignKeyField("models.Ex", related_name="pairs")
    ex_id: int
    pair_sides: BackwardFKRelation["PairSide"]

    _name = {"pair__coin__ticker", "pair__cur__ticker", "ex__name"}

    class Meta:
        table_description = "Pairs on Exs"
        unique_together = (("pair_id", "ex_id"),)


class Person(Model, TsTrait):
    status: PersonStatus = IntEnumField(PersonStatus, default=PersonStatus.DEFAULT)
    name: str | None = CharField(127, null=True)
    note: bool = CharField(255, null=True)

    tg: OneToOneNullableRelation[Username] = OneToOneField("models.Username", "person", null=True)
    tg_id: int

    user: BackwardOneToOneRelation["User"]
    creds: BackwardFKRelation["Cred"]
    actors: BackwardFKRelation["Actor"]
    pm_agents: BackwardFKRelation["PmAgent"]


class User(TgUser, TsTrait):
    status: UserStatus = IntEnumField(UserStatus, default=UserStatus.SLEEP)
    person: OneToOneRelation[Person] = OneToOneField("models.Person", related_name="user")
    person_id: int
    ref: ForeignKeyNullableRelation["User"] = ForeignKeyField("models.User", related_name="proteges", null=True)
    ref_id: int | None

    actors: BackwardFKRelation["Actor"]
    contacts: BackwardFKRelation["User"]
    created_forums: BackwardFKRelation["Forum"]
    creds: BackwardFKRelation["Cred"]
    pm_agents: BackwardFKRelation["PmAgent"]
    gmail: BackwardOneToOneRelation["Gmail"]
    forum: BackwardOneToOneRelation["Forum"]
    limits: BackwardFKRelation["Limit"]
    msgs: BackwardFKRelation["Msg"]
    proteges: BackwardFKRelation["User"]
    sends: BackwardFKRelation["Transaction"]
    receives: BackwardFKRelation["Transaction"]
    validates: BackwardFKRelation["Transaction"]
    vpn: BackwardOneToOneRelation["Vpn"]
    invite_requests: BackwardFKRelation["Invite"]
    invite_approvals: BackwardFKRelation["Invite"]
    lends: BackwardFKRelation["Credit"]
    borrows: BackwardFKRelation["Credit"]
    investments: BackwardFKRelation["Investment"]

    async def free_assets(self):
        assets = await Asset.filter(agent__actor__person__user__id=self.id).values("free", "addr__coin__rate")
        return sum(asset["free"] * asset["addr__coin__rate"] for asset in assets)

    async def fiats_sum(self):
        fiats = await Fiat.filter(cred__person__user__id=self.id).values("amount", "cred__pmcur__cur__rate")
        return sum(fiat["amount"] * Decimal(fiat["cred__pmcur__cur__rate"]) for fiat in fiats)

    async def balance_sum(self) -> int:
        return int(await self.free_assets()) + int(await self.fiats_sum())

    async def balances(self, ctd: bool = True) -> dict[int, int | float]:  # ctd - convert to decimal
        dbt = {
            c: v * 10 ** (-s) if ctd else v
            for c, v, s in await Transaction.filter(receiver=self, status=TS.valid)
            .prefetch_related("cur")
            .group_by("cur_id", "cur__scale")
            .annotate(debit=Sum("amount"))
            .values_list("cur_id", "debit", "cur__scale")
        }
        crd = {
            c: v * 10 ** (-s) if ctd else v
            for c, v, s in await Transaction.filter(sender=self, status=TS.valid)
            .prefetch_related("cur")
            .group_by("cur_id", "cur__scale")
            .annotate(credit=Sum("amount"))
            .values_list("cur_id", "credit", "cur__scale")
        }
        return {c: dbt.get(c, 0) - crd.get(c, 0) for c in dbt.keys() | crd.keys()}

    async def balance(self, cur_id: int) -> int:
        dbt = (
            await Transaction.filter(receiver=self, cur_id=cur_id, status=TS.valid)
            .group_by("cur_id")
            .annotate(debit=Sum("amount"))
            .values_list("debit", flat=True)
        ) or [0]
        crd = (
            await Transaction.filter(sender=self, cur_id=cur_id, status=TS.valid)
            .group_by("cur_id")
            .annotate(credit=Sum("amount"))
            .values_list("credit", flat=True)
        ) or [0]
        return dbt[0] - crd[0]

    # async def keygen(self):  # moved to front
    #     prv = Ed25519PrivateKey.generate()
    #     self.prv = prv.private_bytes_raw()
    #     self.pub = prv.public_key().public_bytes_raw()
    #     # await self.save(update_fields=["prv", "pub"])

    async def get_validator(self, amount: int, cur_id: int, receiver_id: int) -> "User":
        r = {
            c: v
            for c, v in await Transaction.filter(  # todo: rm ` or receiver_id` - is hack for first trans
                receiver_id__not_in={receiver_id, self.id or receiver_id}, status=TS.valid, cur_id=cur_id
            )
            .group_by("receiver_id")
            .annotate(debit=Sum("amount"))
            .values_list("receiver_id", "debit")
        }
        s = {
            c: v
            for c, v in await Transaction.filter(
                sender_id__not_in={self.id, receiver_id}, status=TS.valid, cur_id=cur_id
            )
            .group_by("sender_id")
            .annotate(credit=Sum("amount"))
            .values_list("sender_id", "credit")
            if c is not None  # todo: rm `if c is not None` - is hack
        }
        val_ids = r.keys() | s.keys()
        # noinspection PyUnboundLocalVariable
        vals = {c: am for c in val_ids if c is not None and (am := r.get(c, 0) - s.get(c, 0)) > amount}
        val_id, _ = sorted(vals.items(), key=lambda x: x[1], reverse=True)[0]
        if val_id is None:
            raise ValueError("No available validators:(")
        validator = await User[val_id]
        return validator

    async def req(self, amount: int, cur_id: int, sender_id: int = None, ts: int = None) -> "Transaction":
        ts = {"ts": datetime.now(utc) + timedelta(minutes=ts)} if ts else {}
        return await Transaction.create(
            receiver=self,
            sender_id=sender_id,
            amount=amount,
            cur_id=cur_id,
            status=TS.request,
            **ts,
        )

    async def send(
        self, uid: UUID, amount: int, cur_id: int, receiver_id: int, sign: bytes, ts: int
    ) -> "Transaction":  # | int
        b = await self.balance(cur_id)
        if self.id and b < amount:
            return b
        # validator = await self.get_validator(amount, cur_id, receiver_id)
        transaction = await Transaction.create(
            id=uid,
            sender=self,
            receiver_id=receiver_id,
            amount=amount,
            cur_id=cur_id,
            # validator=validator,
            proof=sign,
            status=TS.signed,
            ts=ts,
        )
        return transaction

    async def send_by_req(self, req: "Transaction") -> "Transaction":
        assert req.status == TS.request, "its not a request"
        assert not req.sender_id or self.id == req.sender_id, "sender id is incorrect"
        b = await self.balance(req.cur_id)
        assert b >= req.amount, "not enough balance"
        sender_prv = Ed25519PrivateKey.from_private_bytes(self.prv)
        req.sender = self
        req.validator = await self.get_validator(req.amount, req.cur_id, req.receiver_id)
        req.ts = datetime.now()
        req.proof = sender_prv.sign(req.pack)
        req.status = TS.signed
        await req.save()
        return req
        # async with in_transaction():
        #     await req.fetch_related("sender", "validator")
        #     req.proof = req.validator.proof_trans(req, sender_sig)
        #     if not req.check():
        #         raise ValueError("Transaction check failed")
        #     req.status = TS.valid
        #     await req.save(update_fields=["proof", "status"])
        # return transaction

    def name(self):
        return f"{self.first_name} {self.last_name}".rstrip()

    class PydanticMeta(Model.PydanticMeta):
        max_recursion = 0
        include = "role", "status"
        # computed = ["balance"]


@pre_save(User)
async def person(_meta, user: User, _db, _updated: dict) -> None:
    if user.person_id is None:
        user.person = await Person.create(name=f"{user.first_name} {user.last_name or ''}".strip())


class Gmail(Model):
    login: str = CharField(127)
    password: str = CharField(127)
    auth: dict = JSONField(default={})
    updated_at: datetime | None = DatetimeSecField(auto_now=True)

    user: OneToOneRelation[User] = OneToOneField("models.User", "gmail")


class Forum(Model, TsTrait):
    id: int = BigIntField(True)
    joined: bool = BooleanField(default=False)
    user: OneToOneRelation[User] = OneToOneField("models.User", "forum")
    user_id: int
    # created_by: BackwardFKRelation[User] = ForeignKeyField("models.User", "created_forums")


class Actor(Model):
    exid: int = BigIntField()
    name: int = CharField(63)
    ex: ForeignKeyRelation[Ex] = ForeignKeyField("models.Ex", related_name="actors")
    ex_id: int
    person: ForeignKeyRelation[Person] = ForeignKeyField("models.Person", "actors")
    person_id: int

    agent: BackwardOneToOneRelation["Agent"]
    conds: BackwardFKRelation["Cond"]
    my_ads: BackwardFKRelation["Ad"]
    taken_orders: BackwardFKRelation["Order"]

    def client(self, bot):
        module_name = f"xync_client.{self.ex.name}.agent"
        __import__(module_name)
        client = sys.modules[module_name].AgentClient
        return client(self, bot, headers=self.agent.auth.get("headers"), cookies=self.agent.auth.get("cookies"))

    def in_client(self, bot):
        module_name = f"xync_client.{self.ex.name}.InAgent"
        __import__(module_name)
        client = sys.modules[module_name].InAgentClient
        return client(self, bot)

    def asset_client(self):
        module_name = f"xync_client.{self.ex.name}.asset"
        __import__(module_name)
        client = sys.modules[module_name].AssetClient
        return client(self)

    class Meta:
        table_description = "Actors"
        unique_together = (("ex_id", "exid"), ("ex_id", "person_id"))


class Agent(Model, TsTrait):
    auth: dict = JSONField(default={})
    actor: OneToOneRelation[Actor] = OneToOneField("models.Actor", "agent")
    actor_id: int

    assets: BackwardFKRelation["Asset"]

    _name = {"actor__name"}

    # def balance(self) -> int:
    #     return sum(asset.free * (asset.coin.rate or 0) for asset in self.assets)

    # class PydanticMeta(Model.PydanticMeta):
    # max_recursion = 3
    # include = "id", "actor__ex", "auth", "updated_at"
    # computed = ["balance"]


class Cond(Model, TsTrait):
    raw_txt: str = CharField(4095, unique=True)
    last_ver: str = CharField(4095, null=True)

    ads: BackwardFKRelation["Ad"]
    parsed: BackwardOneToOneRelation["CondParsed"]
    sim: BackwardOneToOneRelation["Cond"]

    async def sims(self):
        return {self.raw_txt: await self.sim.sims()} if await self.sim else self.raw_txt


class Synonym(BaseModel):
    typ: SynonymType = IntEnumField(SynonymType, db_index=True)
    txt: str = CharField(255, unique=True)
    boundary: Boundary = IntEnumField(Boundary, default=Boundary.no)
    curs: ManyToManyRelation[Cur] = ManyToManyField("models.Cur", "synonym_cur", related_name="synonyms")
    val: int | None = SmallIntField(null=True)  # SynonymType dependent (e.g., no-slavic for name, approx for ppo.)
    is_re: bool = BooleanField(default=False)


class CondSim(BaseModel):
    cond: OneToOneRelation[Cond] = OneToOneField("models.Cond", "sim", primary_key=True)
    cond_id: int  # new
    similarity: int = SmallIntField(db_index=True)  # /1000
    cond_rel: ForeignKeyRelation[Cond] = ForeignKeyField("models.Cond", "sims_rel")
    cond_rel_id: int  # old

    class Meta:
        table = "cond_sim"


class PmGroup(Model):
    id: int = SmallIntField(True)
    name: str = CharField(127)
    pms: BackwardFKRelation["Pm"]

    class Meta:
        table = "pm_group"


class Pm(Model):
    # name: str = CharField(63)  # mv to pmex cause it diffs on each ex
    norm: str | None = CharField(63)
    acronym: str | None = CharField(7, null=True)
    country: ForeignKeyNullableRelation[Country] = ForeignKeyField("models.Country", "pms", null=True)
    df_cur: ForeignKeyNullableRelation[Cur] = ForeignKeyField("models.Cur", "df_pms", null=True)
    grp: ForeignKeyNullableRelation[PmGroup] = ForeignKeyField("models.PmGroup", "pms", null=True)
    alias: str | None = CharField(63, null=True)
    extra: str | None = CharField(63, null=True)
    ok: bool = BooleanField(default=True)
    bank: bool | None = BooleanField(null=True)
    qr: bool = BooleanField(default=False)
    fee: int | None = SmallIntField(null=True)  # /10_000

    typ: PmType | None = IntEnumField(PmType, null=True)

    ads: ManyToManyRelation["Ad"]
    curs: ManyToManyRelation[Cur]
    no_conds: ManyToManyRelation[Cond]
    only_conds: ManyToManyRelation[Cond]
    exs: ManyToManyRelation[Ex] = ManyToManyField("models.Ex", "pmex")  # no need. use pmexs[.exid]
    conds: BackwardFKRelation["CondParsed"]
    orders: BackwardFKRelation["Order"]
    pmcurs: BackwardFKRelation["PmCur"]  # no need. use curs
    pmexs: BackwardFKRelation["PmEx"]

    class Meta:
        table_description = "Payment methods"
        unique_together = (("norm", "country_id"), ("alias", "country_id"))

    # class PydanticMeta(Model.PydanticMeta):
    #     max_recursion = 3
    #     backward_relations = True
    #     include = "id", "name", "logo", "pmexs__sbp"

    # def epyd(self):
    #     module_name = f"xync_client.{self.ex.name}.pyd"
    #     __import__(module_name)
    #     return sys.modules[module_name].PmEpyd


class CondParsed(Model, TsTrait):
    cond: OneToOneNullableRelation[Cond] = OneToOneField("models.Cond", "parsed", null=True)
    cond_id: int  # new
    to_party: Party = IntEnumField(Party, null=True)
    from_party: Party = IntEnumField(Party, null=True)
    ppo: int = SmallIntField(null=True)  # Payments per order
    slip_req: Slip = IntEnumField(Slip, null=True)
    slip_send: Slip = IntEnumField(Slip, null=True)
    abuser: AbuserType = IntEnumField(AbuserType, default=AbuserType.no)
    slavic: bool = BooleanField(null=True)
    mtl_like: bool = BooleanField(null=True)
    scale: int = SmallIntField(null=True)
    bank_side: bool = BooleanField(null=True)  # False - except these banks, True - only this banks
    sbp_strict: SbpStrict = IntEnumField(SbpStrict, default=SbpStrict.no)
    contact: str | None = CharField(127, null=True)
    done: bool = BooleanField(default=False, db_index=True)
    banks: ManyToManyRelation[Pm] = ManyToManyField("models.Pm", "cond_banks", related_name="conds")

    class Meta:
        table = "cond_parsed"


class Ad(Model, TsTrait):
    exid: int = BigIntField(db_index=True)  # todo: спарить уникальность с биржей, тк на разных биржах могут совпасть
    pair_side: ForeignKeyRelation[PairSide] = ForeignKeyField("models.PairSide", related_name="ads")
    price: int = IntField()  # /10^cur.scale
    premium: int = SmallIntField(null=True)  # /10_000
    amount: int = IntField()  # /10^cur.scale
    quantity: int = BigIntField(null=True)  # /10^coinex.scale
    min_fiat: int = IntField()  # /10^cur.scale
    max_fiat: int | None = IntField(null=True)  # /10^cur.scale
    auto_msg: str | None = CharField(4095, null=True)
    status: AdStatus = IntEnumField(AdStatus, default=AdStatus.active)

    cond: ForeignKeyNullableRelation[Cond] = ForeignKeyField("models.Cond", "ads", null=True)
    cond_id: int
    maker: ForeignKeyRelation[Actor] = ForeignKeyField("models.Actor", "my_ads")
    maker_id: int

    pms: ManyToManyRelation["Pm"] = ManyToManyField("models.Pm", "ad_pm", related_name="ads")
    my_ad: BackwardOneToOneRelation["MyAd"]
    orders: BackwardFKRelation["Order"]

    _icon = "ad"
    _name = {"pair_side__pairex__coin__ticker", "pair_side__pairex__cur__ticker", "pair_side__sell", "price"}

    class Meta:
        table_description = "P2P Advertisements"
        unique_together = (("exid", "maker_id"),)

    # def epyds(self) -> tuple[PydModel, PydModel, PydModel, PydModel, PydModel, PydModel]:
    #     module_name = f"xync_client.{self.maker.ex.name}.pyd"
    #     __import__(module_name)
    #     return (
    #         sys.modules[module_name].AdEpyd,
    #         sys.modules[module_name].AdFullEpyd,
    #         sys.modules[module_name].MyAdEpydPurchase,
    #         sys.modules[module_name].MyAdInEpydPurchase,
    #         sys.modules[module_name].MyAdEpydSale,
    #         sys.modules[module_name].MyAdInEpydSale,
    #     )


class MyAd(Model):  # Road
    ad: OneToOneRelation[Ad] = OneToOneField("models.Ad", "my_ad")
    ad_id: int  # new
    target_place: int = SmallIntField(default=1)

    pay_req: ForeignKeyNullableRelation["PayReq"] = ForeignKeyField("models.PayReq", "maked_ads", null=True)
    creds: ManyToManyRelation["Cred"] = ManyToManyField("models.CredEx", through="myad_cred", related_name="my_ads")
    race: BackwardFKRelation["Cred"]

    class Meta:
        table = "my_ad"


class Race(Model):
    road: ForeignKeyRelation[MyAd] = ForeignKeyField("models.MyAd", "race")
    road_id: int
    ceil: int = IntField()  # /10^cur.scale
    target_place: int = SmallIntField(default=1)
    vm_filter: bool = BooleanField(default=True)
    started: bool = BooleanField(default=True)
    updated_at: datetime | None = DatetimeSecField(auto_now=True)

    stats: BackwardFKRelation["RaceStat"]

    # def overprice_filter(self, ads: list[BaseAd]):
    #     ads[0]
    #     # вырезаем ads с ценами выше потолка
    #     if ads and (self.ceil - Decimal(ads[0].price)) * k > 0:
    #         if int(ads[0].userId) != self.actor.exid:
    #             ads.pop(0)
    #             self.overprice_filter(ads, self.ceil, k)


class RaceStat(Model):
    race: ForeignKeyRelation[Race] = ForeignKeyField("models.Race", "stats")
    race_id: int
    rivals: ManyToManyRelation[Ad] = ManyToManyField("models.Ad", "rivals", related_name="stats")
    rival_id: int
    price: int = IntField()  # /10^cur.scale
    premium: int = SmallIntField(null=True)  # /10_000
    place: int = SmallIntField()
    created_at: datetime | None = DatetimeSecField(auto_now_add=True)

    class Meta:
        table = "race_stat"


class PmRep(Model):
    ex: ForeignKeyNullableRelation[Ex] = ForeignKeyField("models.Ex", "pm_reps", null=True)
    ex_id: int
    src: str | None = CharField(63, unique=True)
    target: str | None = CharField(63)
    used_at: datetime | None = DatetimeSecField(null=True)

    class Meta:
        table = "pm_rep"


class PmAgent(Model):
    pm: ForeignKeyRelation[Pm] = ForeignKeyField("models.Pm", related_name="agents")
    user: ForeignKeyRelation[User] = ForeignKeyField("models.User", related_name="pm_agents")
    user_id: int
    auth: dict = JSONField(default={})
    state: dict = JSONField(default={})

    class Meta:
        table = "pm_agent"
        unique_together = (("pm_id", "user_id"),)


class PmCur(Model):  # for fiat with no exs tie
    pm: ForeignKeyRelation[Pm] = ForeignKeyField("models.Pm")
    pm_id: int
    cur: ForeignKeyRelation[Cur] = ForeignKeyField("models.Cur")
    cur_id: int

    creds: BackwardFKRelation["Cred"]
    sends: BackwardFKRelation["Transfer"]
    exs: ManyToManyRelation[Ex]

    class Meta:
        table_description = "Payment methods - Currencies"
        unique_together = (("pm_id", "cur_id"),)

    class PydanticMeta(Model.PydanticMeta):
        max_recursion: int = 2  # default: 3
        include = "cur_id", "pm"


class PmEx(BaseModel):  # existence pm in ex with no cur tie
    ex: ForeignKeyRelation[Ex] = ForeignKeyField("models.Ex", "pmexs")
    ex_id: int
    pm: ForeignKeyRelation[Pm] = ForeignKeyField("models.Pm", "pmexs")
    pm_id: int
    logo: ForeignKeyNullableRelation["File"] = ForeignKeyField("models.File", "pmex_logos", null=True)
    logo_id: int
    exid: str = CharField(63)
    name: str = CharField(63)

    banks: BackwardFKRelation["PmExBank"]

    class Meta:
        unique_together = (("ex_id", "exid"),)  # , ("ex", "pm"), ("ex", "name")  # todo: tmp removed for HTX duplicates


class PmExBank(BaseModel):  # banks for SBP
    pmex: ForeignKeyRelation[PmEx] = ForeignKeyField("models.PmEx", "banks")
    pmex_id: int
    exid: str = CharField(63)
    name: str = CharField(63)

    creds: ManyToManyRelation["Cred"]

    class Meta:
        table = "pmex_bank"
        unique_together = (("pmex", "exid"),)


# class PmCurEx(BaseModel):  # existence pm in ex for exact cur, with "blocked" flag
#     pmcur: ForeignKeyRelation[PmCur] = ForeignKeyField("models.PmCur")
#     pmcur_id: int
#     ex: ForeignKeyRelation[Ex] = ForeignKeyField("models.Ex")
#     ex_id: int
#     blocked: bool = BooleanField(default=False)  # todo: move to curex or pmex?
#
#     # class Meta:
#     #     unique_together = (("ex_id", "pmcur_id"),)


class Cred(Model):
    pmcur: ForeignKeyRelation[PmCur] = ForeignKeyField("models.PmCur")
    pmcur_id: int
    detail: str = CharField(127)
    name: str | None = CharField(127, null=True)
    extra: str | None = CharField(255, null=True)
    person: ForeignKeyRelation[Person] = ForeignKeyField("models.Person", "creds")
    person_id: int
    from_chat: int  # todo: ForeignKeyNullableRelation["Order"] = ForeignKeyField("models.Order", null=True)

    banks: ManyToManyRelation[PmExBank] = ManyToManyField("models.PmExBank", related_name="creds")

    fiat: BackwardOneToOneRelation["Fiat"]
    receives: BackwardOneToOneRelation["Transfer"]
    credexs: BackwardFKRelation["CredEx"]
    orders: BackwardFKRelation["Order"]
    pay_reqs: BackwardFKRelation["PayReq"]

    _name = {"detail"}

    def repr(self):
        xtr = f" ({self.extra})" if self.extra else ""
        name = f", имя: {self.name}" if self.name else ""
        return f"`{self.detail}`{name}{xtr}"

    class Meta:
        table_description = "Currency accounts"
        unique_together = (("person_id", "pmcur_id", "detail"),)


class CredEx(Model):
    exid: int = BigIntField()
    cred: ForeignKeyRelation[Cred] = ForeignKeyField("models.Cred", "credexs")
    cred_id: int
    ex: ForeignKeyRelation[Ex] = ForeignKeyField("models.Ex", "credexs")
    ex_id: int

    _name = {"exid"}

    class Meta:
        table_description = "Credential on Exchange"
        unique_together = (("ex_id", "exid"),)


class Fiat(Model):
    cred: OneToOneRelation[Cred] = OneToOneField("models.Cred", "fiat")
    cred_id: int
    amount: int = IntField()  # /10^cur.scale
    target: int = IntField(null=True)  # /10^cur.scale
    min_deposit: int = IntField(null=True)  # /10^cur.scale

    class Meta:
        table_description = "Currency balances"

    class PydanticMeta(Model.PydanticMeta):
        # max_recursion: int = 2
        backward_relations = False
        include = "id", "cred__pmcur", "cred__detail", "cred__name", "amount"

    @staticmethod
    def epyd(ex: Ex):
        module_name = f"xync_client.{ex.name}.pyd"
        __import__(module_name)
        return sys.modules[module_name].FiatEpyd


class Limit(Model):
    pmcur: ForeignKeyRelation[PmCur] = ForeignKeyField("models.PmCur")
    pmcur_id: int
    amount: int = IntField(null=True)  # '$' if unit >= 0 else 'transactions count'
    unit: int = IntField(default=30)  # positive: $/days, 0: $/transaction, negative: transactions count / days
    level: float | None = IntField(
        default=0, null=True
    )  # 0 - same group, 1 - to parent group, 2 - to grandparent # only for output trans, on input = None
    income: bool = BooleanField(default=False)
    added_by: ForeignKeyRelation["User"] = ForeignKeyField("models.User", related_name="limits")
    added_by_id: int

    _name = {"pmcur__pm__name", "pmcur__cur__ticker", "unit", "income", "amount"}

    class Meta:
        table_description = "Currency accounts balance"


class Addr(Model):
    coin: ForeignKeyRelation[Coin] = ForeignKeyField("models.Coin", "addrs")
    coin_id: int
    actor: ForeignKeyRelation[Actor] = ForeignKeyField("models.Actor", "addrs")
    actor_id: int

    nets: ManyToManyRelation[Net] = ManyToManyField("models.Net", "net_addr", related_name="addrs")

    pay_reqs: BackwardFKRelation["PayReq"]

    _name = {"coin__ticker", "free"}

    class Meta:
        table_description = "Coin address on cex"
        unique_together = (("coin_id", "actor_id"),)


class Asset(Model):
    addr: ForeignKeyRelation[Addr] = ForeignKeyField("models.Addr", related_name="addrs")
    addr_id: int
    agent: ForeignKeyRelation[Agent] = ForeignKeyField("models.Agent", "assets")
    agent_id: int
    typ: AddrExType = IntEnumField(AddrExType, default=AddrExType.found)
    free: int = BigIntField()  # /10^coinex.scale
    freeze: int | None = BigIntField(default=0)  # /10^coinex.scale
    lock: int | None = BigIntField(default=0)  # /10^coinex.scale
    target: int | None = BigIntField(default=0, null=True)  # /10^coinex.scale

    _name = {"asset__coin__ticker", "free"}

    class Meta:
        table_description = "Coin balance"
        unique_together = (("addr_id", "agent_id", "typ"),)

    def epyd(self):
        module_name = f"xync_client.{self.agent.ex.name}.pyd"
        __import__(module_name)
        return sys.modules[module_name].AssetEpyd


class PayReq(Model, TsTrait):
    pay_until: datetime = DatetimeSecField()
    addr: ForeignKeyNullableRelation[Addr] = ForeignKeyField("models.Addr", "pay_reqs", null=True)
    addr_id: int
    cred: ForeignKeyNullableRelation[Cred] = ForeignKeyField("models.Cred", "pay_reqs", null=True)
    cred_id: int
    user: ForeignKeyRelation[User] = ForeignKeyField("models.User", "pay_reqs")
    user_id: int
    amount: float = FloatField()
    parts: int = IntField(default=1)
    payed_at: datetime | None = DatetimeSecField(null=True)

    maked_ads: BackwardFKRelation["MyAd"]
    taken_orders: BackwardFKRelation["Order"]

    _icon = "pay"
    _name = {"ad_id"}

    class Meta:
        table_description = "Payment request"
        unique_together = (("user_id", "cred_id", "addr_id"),)


class Order(Model):
    exid: int = BigIntField(unique=True)  # todo: спарить уникальность с биржей, тк на разных биржах могут совпасть
    ad: ForeignKeyRelation[Ad] = ForeignKeyField("models.Ad", related_name="ads")
    ad_id: int
    amount: int = IntField()  # /10^cur.scale
    quantity: int = BigIntField(null=True)  # /10^coinex.scale
    cred: ForeignKeyRelation[Cred] = ForeignKeyField("models.Cred", related_name="orders", null=True)
    cred_id: int | None
    taker: ForeignKeyRelation[Actor] = ForeignKeyField("models.Actor", "taken_orders")
    taker_id: int
    payreq: ForeignKeyNullableRelation[PayReq] = ForeignKeyField("models.PayReq", "taken_orders", null=True)
    payreq_id: int
    maker_topic: int = IntField(null=True)  # todo: remove nullability
    taker_topic: int = IntField(null=True)
    status: OrderStatus = IntEnumField(OrderStatus)
    created_at: datetime | None = DatetimeSecField(auto_now_add=True)
    payed_at: datetime | None = DatetimeSecField(null=True)
    confirmed_at: datetime | None = DatetimeSecField(null=True)
    appealed_at: datetime | None = DatetimeSecField(null=True)
    chat_parsed: bool = BooleanField(default=False)

    msgs: BackwardFKRelation["Msg"]
    transfer: BackwardOneToOneRelation["Transfer"]

    _name = {"cred__pmcur__pm__name"}

    async def client(self):
        if isinstance(self.ad, QuerySet):
            # noinspection PyTypeChecker
            self.ad: Ad = await self.ad.prefetch_related("agent__ex")
        elif isinstance(self.ad, Ad) and isinstance(self.ad.agent, QuerySet):
            # noinspection PyTypeChecker
            self.ad.agent = await self.ad.agent.prefetch_related("ex")
        elif isinstance(self.ad.agent, Agent) and isinstance(self.ad.agent.ex, QuerySet):
            # noinspection PyTypeChecker
            self.ad.agent.ex = await self.ad.agent.ex
        client = sys.modules[f"xync_client.{self.ad.maker.ex.name}.order"].Client
        return client(self)

    async def get_chat(self):
        await self.fetch_related("ad__pair_side", "msgs")
        return [
            f"{'b' if self.ad.pair_side.is_sell == m.to_maker else 's'}{m.to_maker and 't' or 'm'}: {m.txt or '<file>'}"
            for m in self.msgs
        ]

    # def epyd(self):  # todo: for who?
    #     module_name = f"xync_client.{self.ex.name}.pyd"
    #     __import__(module_name)
    #     return sys.modules[module_name].OrderEpyd

    class Meta:
        table_description = "P2P Orders"

    class PydanticMeta(Model.PydanticMeta):
        max_recursion: int = 0
        exclude_raw_fields: bool = False
        exclude = ("taker", "ad", "cred", "msgs")


class Transaction(Model):
    id: UUID = UUIDField(primary_key=True)
    amount: int = IntField()  # /10^cur.scale
    cur: ForeignKeyRelation["Cur"] = ForeignKeyField("models.Cur", related_name="transfers")
    cur_id: int
    sender: ForeignKeyRelation[User] = ForeignKeyField("models.User", "sends", null=True)
    sender_id: int | None
    receiver: ForeignKeyRelation[User] = ForeignKeyField("models.User", "receives")
    receiver_id: int
    # validator: ForeignKeyRelation[User] = ForeignKeyField("models.User", "validates", null=True)
    # validator_id: int
    status: TS = IntEnumField(TS)
    proof: bytes = UniqBinaryField(unique=True, null=True)  # len=128
    ts: datetime | None = DatetimeSecField(null=True)

    def is_expired(self) -> bool:
        """Проверка истёк ли запрос"""
        assert not self.proof and self.ts, "It is method for ttl requests only"
        return datetime.now(timezone.utc) > self.ts

    def is_valid_sender(self, sender_id: int) -> bool:
        """Проверка может ли отправитель оплатить этот запрос"""
        assert self.proof is None, "It is method for requests only"
        return self.sender_id is None or self.sender_id == sender_id

    @property
    def pack(self) -> bytes:
        def cr(cur_id: int, rec_id: int):
            """Упаковка валюта + получатель в 1+4=5 байт"""
            return struct.pack(">BL", cur_id, rec_id)

        def cra(cur_id: int, rec_id: int, amount: int):
            """Упаковка валюта + получатель + сумма в 1+4+4=9 байт"""
            return cr(cur_id, rec_id) + struct.pack(">L", amount)

        def tcras(ts: int, cur_id: int, rec_id: int, amount: int, sender_id: int):
            """Упаковка время+валюта+получатель+сумма+отправитель в 1+3+4+4+4=16 байт"""
            tsb = struct.pack(">L", ts - 1756566000)[:3]  # 3 todo: upd base ts
            return tsb + cra(cur_id, rec_id, amount) + struct.pack(">L", sender_id)

        # если это запрос, то все, пруфа нет и не нужен
        if self.status == TS.request:
            assert not self.proof, f"no need proof `{self.proof}` for request"
            return cra(
                self.cur_id,  # 1
                self.receiver_id,  # 4
                self.amount,  # 4
            )

        # иначе это отправка
        assert self.ts, "Time of sending is required"
        assert (
            ((pl := len(self.proof or b"")) == 0 and not self.status)
            or (self.status == TS.signed and pl == 64)
            or (self.status == TS.valid and pl == 128)
        ), f"wrong proof length `{pl}` for `{self.status.name}` transaction"

        return tcras(int(self.ts.timestamp()), self.cur_id, self.receiver_id, self.amount, self.sender_id)

    # async def sender_sign(self):  # moved to front
    #     assert self.status == TS.not_signed, "It is method for not signed transfers only"
    #     await self.fetch_related("sender")
    #     sender_prv = Ed25519PrivateKey.from_private_bytes(self.sender.prv)
    #     self.proof = sender_prv.sign(self.pack)
    #     # после создания прупа(+64) отправителя пак удлиннился с 21 байта до 85
    #     await self.save(update_fields=["proof"])

    async def approve(self, prv: bytes):
        assert self.status == TS.signed, "It is method for signed transfers only"
        assert len(self.proof) == 64, "Sender did not signed yet"
        # 1. Проверяем подпись отправителя
        snd_pub = Ed25519PublicKey.from_public_bytes(self.sender.pub)
        # отправитель подписывал транзу когда в ней еще не было пруфа, поэтому проверяем обрезок пака до него
        snd_pub.verify(self.proof, self.pack)
        # 2. Проверяем что баланс отправителя не меньшы отправляемой суммы. # todo: remove origin hack
        assert await self.sender.balance(self.cur_id) >= self.amount or not self.sender_id, "B"
        # 3. Подписываем
        pk = Ed25519PrivateKey.from_private_bytes(prv)
        self.proof += pk.sign(self.pack)  # и добавляет эту подпись к пруфу 85+64=149
        self.status = TS.valid
        # Только две подписи: отправителя + валидатора (128 байт)
        await self.save(update_fields=["proof", "status"])

    def check(self, vld_pub: bytes = None) -> bool:
        """Проверка доказательства"""
        if len(self.proof) != 128:  # 64 + 64
            return False  # wrong size
        sender_sig, vld_sig = self.proof[:64], self.proof[64:128]
        try:
            # Проверяем подпись отправителя
            sender_pub = Ed25519PublicKey.from_public_bytes(self.sender.pub)
            sender_pub.verify(sender_sig, self.pack)
            # Проверяем подпись валидатора
            if vld_pub:
                vld_pub = Ed25519PublicKey.from_public_bytes(vld_pub)
                vld_pub.verify(vld_sig, self.pack)
            return True
        except InvalidSignature as _:
            return False  # wrong sign


class Sign(Model):
    transaction: ForeignKeyRelation[Transaction] = ForeignKeyField("models.Transaction", "signs")
    transaction_id: int
    validator: ForeignKeyRelation[User] = ForeignKeyField("models.User", "approves")
    validator_id: int
    created_at: datetime | None = DatetimeSecField(auto_now_add=True)


# class Checkpoint(Model):
#     amount: int = BigIntField()  # /10^cur.scale
#     cur: ForeignKeyRelation["Cur"] = ForeignKeyField("models.Cur", related_name="transfers")
#     cur_id: int
#     user: ForeignKeyRelation[User] = ForeignKeyField("models.User", "checkpoints", null=True)
#     user_id: int | None
#
#     class Meta:
#         unique_together = (("user_id", "cur_id"),)


class Transfer(Model):
    amount: int = IntField()  # /10^cur.scale
    order: OneToOneNullableRelation[Order] = OneToOneField("models.Order", "transfer", null=True)
    order_id: int
    file: OneToOneNullableRelation["File"] = OneToOneField("models.File", "transfer", null=True)
    file_id: int
    pmid: int = BigIntField(null=True)
    created_at: datetime | None = DatetimeSecField(auto_now_add=True)
    accepted_at: datetime | None = DatetimeSecField(null=True)

    class Meta:
        unique_together = (("pmid", "order"),)


class Msg(Model):
    tg_mid: int = IntField(null=True)
    txt: str = CharField(4095, null=True)
    read: bool = BooleanField(default=False, db_index=True)
    to_maker: bool = BooleanField()
    file: OneToOneNullableRelation["File"] = OneToOneField("models.File", related_name="msg", null=True)
    order: ForeignKeyRelation[Order] = ForeignKeyField("models.Order", related_name="msgs")
    sent_at: datetime | None = DatetimeSecField()

    # todo: required txt or file
    class PydanticMeta(Model.PydanticMeta):
        max_recursion: int = 0
        exclude_raw_fields: bool = False
        exclude = ("receiver", "order")

    class Meta:
        unique_together = (
            ("order", "txt"),
            ("order", "sent_at"),
        )


class Dep(Model, TsTrait):
    pid: str = CharField(31)  # product_id
    apr: int = SmallIntField()  # /10_000
    fee: int | None = SmallIntField(null=True)  # /10_000
    apr_is_fixed: bool = BooleanField(default=False)
    duration: int | None = SmallIntField(null=True)
    early_redeem: bool | None = BooleanField(null=True)
    typ: DepType = IntEnumField(DepType)
    # mb: renewable?
    min_limit: float = FloatField()
    max_limit: float | None = FloatField(null=True)
    is_active: bool = BooleanField(default=True)

    coin: ForeignKeyRelation[Coin] = ForeignKeyField("models.Coin", related_name="deps")
    coin_id: int
    reward_coin: ForeignKeyRelation[Coin] = ForeignKeyField("models.Coin", related_name="deps_reward", null=True)
    reward_coin_id: int | None = None
    bonus_coin: ForeignKeyRelation[Coin] = ForeignKeyField("models.Coin", related_name="deps_bonus", null=True)
    bonus_coin_id: int | None = None
    ex: ForeignKeyRelation[Ex] = ForeignKeyField("models.Ex", related_name="deps")
    ex_id: int
    investments: BackwardFKRelation["Investment"]

    _icon = "seeding"
    _name = {"pid"}

    def repr(self):
        return (
            f"{self.coin.ticker}:{self.apr * 100:.3g}% "
            f"{f'{self.duration}d' if self.duration and self.duration > 0 else 'flex'}"
        )

    class Meta:
        table_description = "Investment products"
        unique_together = (("pid", "typ", "ex_id"),)


class Investment(Model, TsTrait):
    dep: ForeignKeyRelation[Dep] = ForeignKeyField("models.Dep", related_name="investments")
    # dep_id: int
    amount: float = FloatField()
    is_active: bool = BooleanField(default=True)
    user: ForeignKeyRelation[User] = ForeignKeyField("models.User", related_name="investments")

    _icon = "trending-up"
    _name = {"dep__pid", "amount"}

    def repr(self):
        return f"{self.amount:.3g} {self.dep.repr()}"

    class Meta:
        table_description = "Investments"


class ExStat(Model):
    ex: ForeignKeyRelation[Ex] = ForeignKeyField("models.Ex", related_name="stats")
    ex_id: int
    action: ExAction = IntEnumField(ExAction)
    ok: bool | None = BooleanField(default=False, null=True)
    updated_at: datetime | None = DatetimeSecField(auto_now=True)

    _icon = "test-pipe"
    _name = {"ex_id", "action", "ok"}

    def repr(self):
        return f"{self.ex_id} {self.action.name} {self.ok}"

    class Meta:
        table = "ex_stat"
        table_description = "Ex Stats"
        unique_together = (("action", "ex_id"),)

    class PydanticMeta(Model.PydanticMeta):
        max_recursion: int = 2


class Vpn(Model):
    user: OneToOneRelation[User] = OneToOneField("models.User", related_name="vpn")
    user_id: int
    prv: str = CharField(63, unique=True)
    pub: str = CharField(63, unique=True)
    created_at: datetime | None = DatetimeSecField(auto_now_add=True)

    _icon = "vpn"
    _name = {"pub"}

    def repr(self):
        return self.user.username

    class Meta:
        table_description = "VPNs"


class File(Model):
    name: str = CharField(178, null=True, unique=True)
    typ: FileType = IntEnumField(FileType)
    ref: bytes = UniqBinaryField(unique=True)
    size: bytes = IntField()
    created_at: datetime | None = DatetimeSecField(auto_now_add=True)

    msg: BackwardOneToOneRelation[Msg]
    transfer: BackwardOneToOneRelation[Transfer]
    pmex_logos: BackwardFKRelation[PmEx]

    _icon = "file"
    _name = {"name"}

    class Meta:
        table_description = "Files"
        # Создаем индекс через raw SQL
        # indexes = ["CREATE UNIQUE INDEX IF NOT EXISTS idx_bytea_unique ON file (encode(sha256(ref), 'hex'))"]


class Invite(Model, TsTrait):
    ref: ForeignKeyRelation[User] = ForeignKeyField("models.User", related_name="invite_approvals")
    ref_id: int
    protege: ForeignKeyRelation[User] = ForeignKeyField("models.User", related_name="invite_requests")
    protege_id: int
    approved: str = BooleanField(default=False)  # status

    _icon = "invite"
    _name = {"ref__username", "protege__username", "approved"}

    def repr(self):
        return self.protege.name

    class Meta:
        table_description = "Invites"


class Credit(Model, TsTrait):
    lender: ForeignKeyRelation[User] = ForeignKeyField("models.User", related_name="lends")
    lender_id: int
    borrower: ForeignKeyRelation[User] = ForeignKeyField("models.User", related_name="borrows")
    borrower_id: int
    borrower_priority: bool = BooleanField(default=True)
    amount: int = IntField(default=None)  # 0 - is all remain borrower balance

    _icon = "credit"
    _name = {"lender__username", "borrower__username", "amount"}

    def repr(self):
        return self.borrower.name

    class Meta:
        table_description = "Credits"
