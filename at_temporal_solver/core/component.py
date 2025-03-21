from typing import Any
from typing import Coroutine
from typing import Dict
from typing import List
from typing import Optional
from typing import TypedDict
from typing import Union
from uuid import UUID
from xml.etree.ElementTree import Element

from aio_pika import IncomingMessage
from at_config.core.at_config_handler import ATComponentConfig
from at_krl.core.kb_value import KBValue
from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.non_factor import NonFactor
from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method
from at_solver.core.wm import WorkingMemory

from at_temporal_solver.core.at_temporal_solver import TemporalSolver
from at_temporal_solver.core.timeline import Timeline


class WMItemDict(TypedDict):
    ref: str
    value: Optional[Union[str, int, float, bool]]
    belief: Optional[Union[int, float]]
    probability: Optional[Union[int, float]]
    accuracy: Optional[Union[int, float]]


class OpenedIntervalDict(TypedDict):
    interval: str
    open_tact: int
    close_tact: int


class EventDict(TypedDict):
    event: str
    occurrance_tact: int


class TactRecordDict(TypedDict):
    tact: int
    opened_intervals: List[OpenedIntervalDict]
    events: List[EventDict]


class TimelineDict(TypedDict):
    tacts: List[TactRecordDict]


class ProcessTactResultDict(TypedDict):
    wm: Dict[str, Union[int, float, str, bool, None]]
    timeline: TimelineDict


class ATTemporalSolver(ATComponent):
    temporal_solvers: Dict[str, TemporalSolver]

    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        self.temporal_solvers = {}

    def get_kb_from_config(self, config: ATComponentConfig) -> KnowledgeBase:
        kb_item = config.items.get("kb")
        if kb_item is None:
            kb_item = config.items.get("knowledge_base")
        if kb_item is None:
            kb_item = config.items.get("knowledge-base")
        if kb_item is None:
            raise ValueError("Knowledge base is required")
        kb_data = kb_item.data
        if isinstance(kb_data, Element):
            return KnowledgeBase.from_xml(kb_data)
        elif isinstance(kb_data, dict):
            return KnowledgeBase.from_json(kb_data)
        elif isinstance(kb_data, str):
            return KnowledgeBase.from_krl(kb_data)
        else:
            raise TypeError("Not valid type of knowledge base configuration")

    async def perform_configurate(
        self, config: ATComponentConfig, auth_token: str = None, *args, **kwargs
    ) -> Coroutine[Any, Any, bool]:
        kb = self.get_kb_from_config(config)
        return await self.create_temporal_solver(kb, auth_token=auth_token)

    async def create_temporal_solver(self, kb: KnowledgeBase, auth_token: str = None) -> bool:
        auth_token = auth_token or "default"

        knowledge_base = kb
        # knowledge_base.validate()
        solver = TemporalSolver(knowledge_base)

        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        self.temporal_solvers[auth_token_or_user_id] = solver

        return True

    async def check_configured(
        self,
        *args,
        message: Dict,
        sender: str,
        message_id: str | UUID,
        reciever: str,
        msg: IncomingMessage,
        auth_token: str = None,
        **kwargs
    ) -> bool:
        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        return self.has_temporal_solver(auth_token_or_user_id=auth_token_or_user_id)

    def has_temporal_solver(self, auth_token_or_user_id: str | int) -> bool:
        try:
            self.get_solver(auth_token_or_user_id)
            return True
        except ValueError:
            return False

    def get_solver(self, auth_token_or_user_id: str | int) -> TemporalSolver:
        auth_token_or_user_id = auth_token_or_user_id or "default"
        solver = self.temporal_solvers.get(auth_token_or_user_id)
        if solver is None:
            raise ValueError("Temporal solver for provided token or user id is not created")
        return solver

    @authorized_method
    async def reset(self, auth_token: str = None) -> bool:
        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        solver = self.get_solver(auth_token_or_user_id=auth_token_or_user_id)
        solver.wm = WorkingMemory(kb=solver.kb)
        solver.timeline = Timeline()
        solver.current_tact = None
        return True

    @authorized_method
    async def update_wm(self, items: List[WMItemDict], clear_before: bool = True, auth_token: str = None) -> bool:
        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        solver = self.get_solver(auth_token_or_user_id=auth_token_or_user_id)
        if clear_before:
            solver.wm = WorkingMemory(solver.kb)
        for item in items:
            nf = NonFactor(
                belief=item.get("belief", 50),
                probability=item.get("probability", 100),
                accuracy=item.get("accuracy", 0),
            )
            v = KBValue(content=item["value"], non_factor=nf)
            solver.wm.set_value(item["ref"], v)

        return True

    @authorized_method
    async def update_wm_from_bb(self, clear_before: bool = True, auth_token: str = None) -> bool:
        items = await self.exec_external_method("ATBlackBoard", "get_all_items", {}, auth_token=auth_token)
        return self.update_wm(items=items, clear_before=clear_before, auth_token=auth_token)

    @authorized_method
    async def process_tact(self, auth_token: str) -> ProcessTactResultDict:
        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        solver = self.get_solver(auth_token_or_user_id=auth_token_or_user_id)
        solver.process_tact()
        return {
            "wm": solver.wm.all_values_dict,
            "timeline": solver.timeline.__dict__,
            "signified": {key: value.content for key, value in solver.wm.locals.items()},
            "signified_meta": solver.signified_meta,
        }
