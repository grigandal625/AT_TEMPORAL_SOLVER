from dataclasses import dataclass
from typing import List
from typing import TYPE_CHECKING
from typing import Union

from at_krl.core.kb_reference import KBReference
from at_krl.core.kb_value import Evaluatable
from at_krl.core.kb_value import KBValue
from at_krl.core.simple.simple_value import SimpleValue
from at_krl.core.temporal.allen_attribute_expression import AllenAttributeExpression
from at_krl.core.temporal.allen_evaluatable import AllenEvaluatable
from at_krl.core.temporal.allen_event import KBEvent
from at_krl.core.temporal.allen_interval import KBInterval
from at_krl.core.temporal.allen_operation import AllenOperation
from at_krl.core.temporal.allen_reference import AllenReference
from at_solver.evaluations.basic import BasicEvaluator

from at_temporal_solver.core.timeline import EventInstance
from at_temporal_solver.core.timeline import IntervalInstance

if TYPE_CHECKING:
    from at_temporal_solver.core.at_temporal_solver import TemporalSolver


@dataclass
class ModifiedBasicEvaluator(BasicEvaluator):
    temporal_solver: "TemporalSolver"

    def eval(self, v: Evaluatable | AllenEvaluatable, ref_stack: List[KBReference] = None) -> KBValue:
        if not isinstance(v, AllenEvaluatable):
            return super().eval(v, ref_stack)
        evaluator = AllenEvaluator(temporal_solver=self.temporal_solver)
        return evaluator.eval(v, ref_stack=ref_stack)


@dataclass(kw_only=True)
class TimeSection:
    open: int
    close: int
    orig: Union[KBEvent, KBInterval]


class AllenEvaluator:
    temporal_solver: "TemporalSolver"

    def __init__(self, temporal_solver: "TemporalSolver"):
        self.temporal_solver = temporal_solver

    def eval(self, operation: AllenEvaluatable, *args, **kwargs) -> SimpleValue:
        if isinstance(operation, AllenAttributeExpression):
            instance = self.get_instance(operation.ref)

            if operation.id == "ДЛИТЕЛЬНОСТЬ" and isinstance(instance, IntervalInstance) and instance.closed:
                return SimpleValue(content=instance.close_tact - instance.open_tact)
            elif operation.id == "КОЛ_ВОЗН" and isinstance(instance, EventInstance):
                return SimpleValue(content=len(self.get_all_instances(operation.ref)))
            elif operation.id == "КОЛ_НАЧ" and isinstance(instance, IntervalInstance):
                return SimpleValue(content=len(self.get_all_instances(operation.ref)))
            elif operation.id == "КОЛ_ОКОНЧ" and isinstance(instance, IntervalInstance):
                return SimpleValue(
                    content=len([interval for interval in self.get_all_instances(operation.ref) if interval.closed])
                )
            elif operation.id == "ТАКТ_НАЧ" and isinstance(instance, IntervalInstance):
                return SimpleValue(content=instance.open_tact)
            elif operation.id == "ТАКТ_ОКОНЧ" and isinstance(instance, IntervalInstance):
                return SimpleValue(content=instance.close_tact if instance.closed else None)
            elif operation.id == "ТАКТ_ВОЗН" and isinstance(instance, EventInstance):
                return SimpleValue(content=instance.occurance_tact)

        if isinstance(operation, AllenOperation):
            left = operation.left
            right = operation.right

            left_instance = self.get_instance(left)
            right_instance = self.get_instance(right)

            if left_instance is None or right_instance is None:
                return SimpleValue(content=None)

            left_section = self.get_section(left_instance)
            right_section = self.get_section(right_instance)

            if left_section is None and right_section is None:
                return SimpleValue(content=None)

            return ALLEN_EVALUATORS[operation.sign](left_section, right_section)

    def get_section(self, orig: Union[EventInstance, IntervalInstance]) -> TimeSection:
        if isinstance(orig, IntervalInstance):
            return TimeSection(
                open=orig.open_tact,
                close=orig.close_tact if orig.close_tact is not None else self.temporal_solver.current_tact,
                orig=orig,
            )
        elif isinstance(orig, EventInstance):
            return TimeSection(open=orig.occurance_tact, close=orig.occurance_tact, orig=orig)

    def get_all_instances(self, ref: AllenReference) -> Union[List[EventInstance], List[IntervalInstance]]:
        if isinstance(ref.target, KBEvent):
            return self.temporal_solver.timeline.get_all_event_instances(ref)
        elif isinstance(ref.target, KBInterval):
            return self.temporal_solver.timeline.get_all_interval_instances(ref)

    def get_instance(self, ref: AllenReference) -> Union[EventInstance, IntervalInstance, None]:
        index = -1
        if ref.index:
            m_evaluator = ModifiedBasicEvaluator(wm=self.temporal_solver.wm, temporal_solver=self.temporal_solver)
            index = m_evaluator.eval(ref.index).to_simple()
            if index.content is None:
                return None
        if isinstance(ref.target, KBEvent):
            return self.temporal_solver.timeline.get_event_instance(ref, index)
        elif isinstance(ref.target, KBInterval):
            return self.temporal_solver.timeline.get_interval_instance(ref, index)


def eval_b(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return SimpleValue(content=left.close < right.open)


def eval_bi(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_b(left=right, right=left)


def eval_m(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return SimpleValue(content=left.close == right.open)


def eval_mi(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_m(left=right, right=left)


def eval_a(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_bi(left, right)


def eval_ai(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_b(left, right)


def eval_s(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return SimpleValue(content=left.open == right.open and left.close < right.close)


def eval_si(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_s(left=right, right=left)


def eval_f(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return SimpleValue(content=left.close == right.close and left.open > right.open)


def eval_fi(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_fi(left=right, right=left)


def eval_d(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return SimpleValue(content=left.open > right.open and left.close < right.close)


def eval_di(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_d(left=right, right=left)


def eval_o(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return SimpleValue(content=left.open < right.open and left.close > right.open and left.close < right.close)


def eval_oi(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return eval_o(left=right, right=left)


def eval_e(left: TimeSection, right: TimeSection, *args, **kwargs) -> KBValue:
    return SimpleValue(content=left.open == right.open and left.close == right.close)


ALLEN_EVALUATORS = {
    "b": eval_b,
    "bi": eval_bi,
    "m": eval_m,
    "mi": eval_mi,
    "a": eval_a,
    "ai": eval_ai,
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
