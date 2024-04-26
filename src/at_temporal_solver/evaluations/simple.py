from at_krl.core.temporal.utils import SimpleEvaluatable
from at_krl.core.temporal.utils import SimpleValue
from at_krl.core.temporal.utils import SimpleReference
from at_krl.core.temporal.utils import SimpleOperation
from at_krl.core.kb_value import KBValue
from typing import TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    from at_temporal_solver.core.at_temporal_solver import TemporalSolver

class SimpleEvaluator:
    temporal_solver: 'TemporalSolver' = None

    def __init__(self, temporal_solver: 'TemporalSolver'):
        self.temporal_solver = temporal_solver

    def eval(self, v: SimpleEvaluatable, ref_stack: List[SimpleReference]=None) -> Union[KBValue, SimpleValue]:
        ref_stack = ref_stack or []
        if v is None:
            return KBValue(None)
        elif isinstance(v, KBValue):
            return v
        elif isinstance(v, SimpleValue):
            return v
        elif isinstance(v, SimpleReference):
            if self.temporal_solver.wm.ref_is_accessible(v):
                instance = self.temporal_solver.wm.get_instance_by_ref(v)
                if [r.inner_krl for r in ref_stack].count(v.inner_krl) > 1:
                    raise ValueError(
                        f'''Reference {v.inner_krl} has recursive link in wm to evaluate.
                        
                        Reference value is getting form:
                        {instance.krl}
                        '''
                    ) 
                ref_stack.append(v)
                return self.eval(instance.value, ref_stack=ref_stack)
            else:
                local = self.temporal_solver.wm.locals.get(v.inner_krl)
                return self.eval(local)
            
        elif isinstance(v, SimpleOperation):
            left_v = self.eval(v.left)
            if left_v.content is None:
                return KBValue(None)
            if v.is_binary:
                right_v = self.eval(v.right)
                if right_v.content is None:
                    return KBValue(None)
                return EVALUATORS[v.op](left_v, right_v)
            return EVALUATORS[v.tag](left_v)


def unify_number(n):
    f = float(n)
    i = int(f)
    return i if i == f else f


def eval_eq(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content == right.content
    return SimpleValue(content)


def eval_gt(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content > right.content
    return KBValue(content)


def eval_ge(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content >= right.content
    return KBValue(content)


def eval_lt(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content < right.content
    return KBValue(content)


def eval_le(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content <= right.content
    return KBValue(content)


def eval_ne(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content != right.content
    return KBValue(content)


def eval_and(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content and right.content
    return KBValue(content)


def eval_or(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content or right.content
    return KBValue(content)


def eval_not(v: SimpleValue, *args, **kwargs) -> SimpleValue:
    content = not v.content
    return KBValue(content)


def eval_xor(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = (left.content and not right.content) or (right and not left.content)
    return KBValue(content)


def eval_neg(v: SimpleValue, *args, **kwargs) -> SimpleValue:
    content = -1 * unify_number(v.content)
    return KBValue(content)


def eval_add(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content + right.content
    return KBValue(content)


def eval_sub(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content - right.content
    return KBValue(content)


def eval_mul(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = unify_number(left.content) * unify_number(right.content)
    return KBValue(content)


def eval_div(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = unify_number(left.content) / unify_number(right.content)
    return KBValue(content)


def eval_mod(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = unify_number(left.content) % unify_number(right.content)
    return KBValue(content)


def eval_pow(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = unify_number(left.content) ** unify_number(right.content)
    return KBValue(content)


EVALUATORS = {
    "eq": eval_eq,
    "gt": eval_gt,
    "ge": eval_ge,
    "lt": eval_lt,
    "le": eval_le,
    "ne": eval_ne,
    "and": eval_and,
    "or": eval_or,
    "not": eval_not,
    "xor": eval_xor,
    "neg": eval_neg,
    "add": eval_add,
    "sub": eval_sub,
    "mul": eval_mul,
    "div": eval_div,
    "mod": eval_mod,
    "pow": eval_pow,
}