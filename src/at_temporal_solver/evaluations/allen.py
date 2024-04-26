from at_krl.core.temporal.kb_allen_operation import KBAllenOperation
from at_krl.core.temporal.kb_event import KBEvent
from at_krl.core.temporal.kb_interval import KBInterval
from at_krl.core.kb_value import KBValue
from typing import TYPE_CHECKING, Union
from dataclasses import dataclass
from at_temporal_solver.core.timeline import IntervalInstance, EventInstance

if TYPE_CHECKING:
    from at_temporal_solver.core.at_temporal_solver import TemporalSolver


@dataclass(kw_only=True)
class TimeSection:
    open: int
    close: int
    orig: Union[KBEvent, KBInterval]


class AllenEvaluator:
    temporal_solver: 'TemporalSolver'

    def __init__(self, temporal_solver: 'TemporalSolver'):
        self.temporal_solver = temporal_solver

    def eval(self, operation: KBAllenOperation, *args, **kwargs) -> KBValue:
        if not operation.validated:
            raise ValueError(f'Operation "{operation.krl}" is not validated')
        
        left = operation.left
        right = operation.right

        left_instance = self.get_instance(left)
        right_instance = self.get_instance(right)

        if left_instance is None or right_instance is None:
            return KBValue(False)
        
        left_section = self.get_section(left_instance)
        right_section = self.get_section(right_instance)

        if left_section is None and right_section is None:
            return KBValue(False)
        
        return ALLEN_EVALUATORS[operation.sign](left_section, right_section)
        
    def get_section(self, orig: Union[EventInstance, IntervalInstance]) -> TimeSection:
        if isinstance(orig, IntervalInstance):
            return TimeSection(
                open=orig.open_tact, 
                close=orig.close_tact if orig.close_tact is not None else self.temporal_solver.current_tact, 
                orig=orig
            )
        elif isinstance(orig, EventInstance):
            return TimeSection(open=orig.occurance_tact, close=orig.occurance_tact, orig=orig)

    def get_instance(self, orig: Union[KBInterval, KBEvent]) -> Union[EventInstance, IntervalInstance, None]:
        if isinstance(orig, KBEvent):
            return self.temporal_solver.timeline.get_last_event_instance(orig)
        elif isinstance(orig, KBInterval):
            return self.temporal_solver.timeline.get_last_interval_instance(orig)
        

def eval_b(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return KBValue(left.close < right.open)


def eval_bi(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_b(left=right, right=left)


def eval_m(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return KBValue(left.close == right.open)


def eval_mi(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_m(left=right, right=left)


def eval_a(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_bi(left, right)


def eval_ai(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_b(left, right)


def eval_s(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return KBValue(left.open == right.open and left.close < right.close)


def eval_si(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_s(left=right, right=left)


def eval_f(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return KBValue(left.close == right.close and left.open > right.open)


def eval_fi(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_fi(left=right, right=left)


def eval_d(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return KBValue(left.open > right.open and left.close < right.close)


def eval_di(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_d(left=right, right=left)


def eval_o(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return KBValue(left.open < right.open and left.close > right.open and left.close < right.close)


def eval_oi(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_o(left=right, right=left)


def eval_e(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return KBValue(left.open == right.open and left.close == right.close)


ALLEN_EVALUATORS = {
    'b': eval_b,
    'bi': eval_bi,
    'm': eval_m,
    'mi': eval_mi,
    'a': eval_a,
    'ai': eval_ai,
    "s": eval_s, 
    "si": eval_si,
    "f": eval_f, 
    "fi": eval_fi,
    "d": eval_d,
    "di": eval_di,
    "o": eval_o,
    "oi": eval_oi,
    "e": eval_e,
}