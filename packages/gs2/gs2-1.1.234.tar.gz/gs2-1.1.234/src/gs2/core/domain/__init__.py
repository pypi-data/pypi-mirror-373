from typing import Optional

from core import Gs2RestSession

from account.domain import Gs2Account
from auth.domain import Gs2Auth
from chat.domain import Gs2Chat
from datastore.domain import Gs2Datastore
from dictionary.domain import Gs2Dictionary
from distributor.domain import Gs2Distributor
from enhance.domain import Gs2Enhance
from exchange.domain import Gs2Exchange
from experience.domain import Gs2Experience
from formation.domain import Gs2Formation
from friend.domain import Gs2Friend
from gateway.domain import Gs2Gateway
from identifier.domain import Gs2Identifier
from inbox.domain import Gs2Inbox
from inventory.domain import Gs2Inventory
from job_queue.domain import Gs2JobQueue
from key.domain import Gs2Key
from limit.domain import Gs2Limit
from lock.domain import Gs2Lock
from log.domain import Gs2Log
from lottery.domain import Gs2Lottery
from matchmaking.domain import Gs2Matchmaking
from mission.domain import Gs2Mission
from money.domain import Gs2Money
from news.domain import Gs2News
from quest.domain import Gs2Quest
from ranking.domain import Gs2Ranking
from realtime.domain import Gs2Realtime
from schedule.domain import Gs2Schedule
from gs2.script import Gs2Script
from showcase.domain import Gs2Showcase
from stamina.domain import Gs2Stamina
from version.domain import Gs2Version


class Gs2:

    def __init__(
            self,
            session: Gs2RestSession,
    ):
        self._session: Gs2RestSession = session
        self._account: Optional[Gs2Account] = None
        self._auth: Optional[Gs2Auth] = None
        self._chat: Optional[Gs2Chat] = None
        self._datastore: Optional[Gs2Datastore] = None
        self._dictionary: Optional[Gs2Dictionary] = None
        self._distributor: Optional[Gs2Distributor] = None
        self._enhance: Optional[Gs2Enhance] = None
        self._exchange: Optional[Gs2Exchange] = None
        self._experience: Optional[Gs2Experience] = None
        self._formation: Optional[Gs2Formation] = None
        self._friend: Optional[Gs2Friend] = None
        self._gateway: Optional[Gs2Gateway] = None
        self._identifier: Optional[Gs2Identifier] = None
        self._inbox: Optional[Gs2Inbox] = None
        self._inventory: Optional[Gs2Inventory] = None
        self._job_queue: Optional[Gs2JobQueue] = None
        self._key: Optional[Gs2Key] = None
        self._limit: Optional[Gs2Limit] = None
        self._lock: Optional[Gs2Lock] = None
        self._log: Optional[Gs2Log] = None
        self._lottery: Optional[Gs2Lottery] = None
        self._matchmaking: Optional[Gs2Matchmaking] = None
        self._mission: Optional[Gs2Mission] = None
        self._money: Optional[Gs2Money] = None
        self._news: Optional[Gs2News] = None
        self._quest: Optional[Gs2Quest] = None
        self._ranking: Optional[Gs2Ranking] = None
        self._realtime: Optional[Gs2Realtime] = None
        self._schedule: Optional[Gs2Schedule] = None
        self._script: Optional[Gs2Script] = None
        self._showcase: Optional[Gs2Showcase] = None
        self._stamina: Optional[Gs2Stamina] = None
        self._version: Optional[Gs2Version] = None

    @property
    def account(self) -> Gs2Account:
        if self._account is not None:
            return self._account
        self._account = Gs2Account(
            session=self._session,
        )
        return self._account

    @property
    def auth(self) -> Gs2Auth:
        if self._auth is not None:
            return self._auth
        self._auth = Gs2Auth(
            session=self._session,
        )
        return self._auth

    @property
    def chat(self) -> Gs2Chat:
        if self._chat is not None:
            return self._chat
        self._chat = Gs2Chat(
            session=self._session,
        )
        return self._chat

    @property
    def datastore(self) -> Gs2Datastore:
        if self._datastore is not None:
            return self._datastore
        self._datastore = Gs2Datastore(
            session=self._session,
        )
        return self._datastore

    @property
    def dictionary(self) -> Gs2Dictionary:
        if self._dictionary is not None:
            return self._dictionary
        self._dictionary = Gs2Dictionary(
            session=self._session,
        )
        return self._dictionary

    @property
    def distributor(self) -> Gs2Distributor:
        if self._distributor is not None:
            return self._distributor
        self._distributor = Gs2Distributor(
            session=self._session,
        )
        return self._distributor

    @property
    def enhance(self) -> Gs2Enhance:
        if self._enhance is not None:
            return self._enhance
        self._enhance = Gs2Enhance(
            session=self._session,
        )
        return self._enhance

    @property
    def exchange(self) -> Gs2Exchange:
        if self._exchange is not None:
            return self._exchange
        self._exchange = Gs2Exchange(
            session=self._session,
        )
        return self._exchange

    @property
    def experience(self) -> Gs2Experience:
        if self._experience is not None:
            return self._experience
        self._experience = Gs2Experience(
            session=self._session,
        )
        return self._experience

    @property
    def formation(self) -> Gs2Formation:
        if self._formation is not None:
            return self._formation
        self._formation = Gs2Formation(
            session=self._session,
        )
        return self._formation

    @property
    def friend(self) -> Gs2Friend:
        if self._friend is not None:
            return self._friend
        self._friend = Gs2Friend(
            session=self._session,
        )
        return self._friend

    @property
    def gateway(self) -> Gs2Gateway:
        if self._gateway is not None:
            return self._gateway
        self._gateway = Gs2Gateway(
            session=self._session,
        )
        return self._gateway

    @property
    def identifier(self) -> Gs2Identifier:
        if self._identifier is not None:
            return self._identifier
        self._identifier = Gs2Identifier(
            session=self._session,
        )
        return self._identifier

    @property
    def inbox(self) -> Gs2Inbox:
        if self._inbox is not None:
            return self._inbox
        self._inbox = Gs2Inbox(
            session=self._session,
        )
        return self._inbox

    @property
    def inventory(self) -> Gs2Inventory:
        if self._inventory is not None:
            return self._inventory
        self._inventory = Gs2Inventory(
            session=self._session,
        )
        return self._inventory

    @property
    def job_queue(self) -> Gs2JobQueue:
        if self._job_queue is not None:
            return self._job_queue
        self._job_queue = Gs2JobQueue(
            session=self._session,
        )
        return self._job_queue

    @property
    def key(self) -> Gs2Key:
        if self._key is not None:
            return self._key
        self._key = Gs2Key(
            session=self._session,
        )
        return self._key

    @property
    def limit(self) -> Gs2Limit:
        if self._limit is not None:
            return self._limit
        self._limit = Gs2Limit(
            session=self._session,
        )
        return self._limit

    @property
    def lock(self) -> Gs2Lock:
        if self._lock is not None:
            return self._lock
        self._lock = Gs2Lock(
            session=self._session,
        )
        return self._lock

    @property
    def log(self) -> Gs2Log:
        if self._log is not None:
            return self._log
        self._log = Gs2Log(
            session=self._session,
        )
        return self._log

    @property
    def lottery(self) -> Gs2Lottery:
        if self._lottery is not None:
            return self._lottery
        self._lottery = Gs2Lottery(
            session=self._session,
        )
        return self._lottery

    @property
    def matchmaking(self) -> Gs2Matchmaking:
        if self._matchmaking is not None:
            return self._matchmaking
        self._matchmaking = Gs2Matchmaking(
            session=self._session,
        )
        return self._matchmaking

    @property
    def mission(self) -> Gs2Mission:
        if self._mission is not None:
            return self._mission
        self._mission = Gs2Mission(
            session=self._session,
        )
        return self._mission

    @property
    def money(self) -> Gs2Money:
        if self._money is not None:
            return self._money
        self._money = Gs2Money(
            session=self._session,
        )
        return self._money

    @property
    def news(self) -> Gs2News:
        if self._news is not None:
            return self._news
        self._news = Gs2News(
            session=self._session,
        )
        return self._news

    @property
    def quest(self) -> Gs2Quest:
        if self._quest is not None:
            return self._quest
        self._quest = Gs2Quest(
            session=self._session,
        )
        return self._quest

    @property
    def ranking(self) -> Gs2Ranking:
        if self._ranking is not None:
            return self._ranking
        self._ranking = Gs2Ranking(
            session=self._session,
        )
        return self._ranking

    @property
    def realtime(self) -> Gs2Realtime:
        if self._realtime is not None:
            return self._realtime
        self._realtime = Gs2Realtime(
            session=self._session,
        )
        return self._realtime

    @property
    def schedule(self) -> Gs2Schedule:
        if self._schedule is not None:
            return self._schedule
        self._schedule = Gs2Schedule(
            session=self._session,
        )
        return self._schedule

    @property
    def script(self) -> Gs2Script:
        if self._script is not None:
            return self._script
        self._script = Gs2Script(
            session=self._session,
        )
        return self._script

    @property
    def showcase(self) -> Gs2Showcase:
        if self._showcase is not None:
            return self._showcase
        self._showcase = Gs2Showcase(
            session=self._session,
        )
        return self._showcase

    @property
    def stamina(self) -> Gs2Stamina:
        if self._stamina is not None:
            return self._stamina
        self._stamina = Gs2Stamina(
            session=self._session,
        )
        return self._stamina

    @property
    def version(self) -> Gs2Version:
        if self._version is not None:
            return self._version
        self._version = Gs2Version(
            session=self._session,
        )
        return self._version
