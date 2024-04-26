from at_queue.core.session import ConnectionParameters
from at_temporal_solver.core.at_temporal_solver import TemporalSolver
from at_queue.core.at_component import ATComponent
from at_queue.utils.decorators import authorized_method
from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.kb_value import KBValue
from at_krl.core.non_factor import NonFactor
from typing import Dict, TypedDict, Union, Optional, List
from at_temporal_solver.core.wm import WorkingMemory


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

    @authorized_method
    def create_temporal_solver(self, kb_dict: dict, auth_token: str = None) -> bool:
        auth_token = auth_token or 'default'
        
        kb = KnowledgeBase.from_dict(kb_dict)
        kb.validate()

        solver = TemporalSolver(kb)
        self.temporal_solvers[auth_token] = solver
        return True
    
    def get_solver(self, auth_token: str = None) -> TemporalSolver:
        auth_token = auth_token or 'default'
        solver = self.temporal_solvers.get(auth_token)
        if solver is None:
            raise ValueError("Temporal solver for token '%s' is not created" % auth_token)
        return solver

    @authorized_method
    def update_wm(self, items: List[WMItemDict], clear_befor: bool = True, auth_token: str = None) -> bool:
        
        solver = self.get_solver(auth_token=auth_token)
        if clear_befor:
            solver.wm = WorkingMemory(solver.kb)
        for item in items:
            nf = NonFactor(
                belief=item.get('belief'), 
                probability=item.get('probability'), 
                accuracy=item.get('accuracy')
            )
            v = KBValue(content=item['value'], non_factor=nf)
            solver.wm.set_value(item['ref'], v)
        
        return True
    
    @authorized_method
    def process_tact(self, auth_token: str) -> ProcessTactResultDict:
        
        solver = self.get_solver(auth_token)
        solver.process_tact()
        return {
            'wm': solver.wm.all_values_dict,
            'timeline': solver.timeline.__dict__
        }