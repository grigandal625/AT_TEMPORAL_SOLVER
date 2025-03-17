from typing import List
from typing import TYPE_CHECKING
from typing import Union

from at_krl.core.kb_value import KBValue
from at_krl.core.simple.simple_evaluatable import SimpleEvaluatable
from at_krl.core.simple.simple_operation import SimpleOperation
from at_krl.core.simple.simple_reference import SimpleReference
from at_krl.core.simple.simple_value import SimpleValue

if TYPE_CHECKING:
    from at_solver.core.wm import WorkingMemory


class SimpleEvaluator:
    wm: "WorkingMemory" = None

    def __init__(self, wm: "WorkingMemory"):
        self.wm = wm

    def eval(self, v: SimpleEvaluatable, ref_stack: List[SimpleReference] = None) -> Union[KBValue, SimpleValue]:
        ref_stack = ref_stack or []
        if v is None:
            return SimpleValue(content=None)
        elif isinstance(v, SimpleValue):
            return v.to_simple()
        elif isinstance(v, SimpleReference):
            if self.wm.ref_is_accessible(v):
                instance = self.wm.get_instance_by_ref(v)
                if [r.to_simple().krl for r in ref_stack].count(v.to_simple().krl) > 1:
                    raise ValueError(
                        f"""Reference {v.to_simple().krl} has recursive link in wm to evaluate.

                        Reference value is getting form:
                        {instance.krl}
                        """
                    )
                ref_stack.append(v)
                return self.eval(instance.value, ref_stack=ref_stack)
            else:
                local = self.wm.locals.get(v.to_simple().krl)
                return self.eval(local)

        elif isinstance(v, SimpleOperation):
            left_v = self.eval(v.left)
            if left_v.content is None:
                return SimpleValue(content=None)
            if v.is_binary:
                right_v = self.eval(v.right)
                if right_v.content is None:
                    return SimpleValue(content=None)
                return EVALUATORS[v.operation_name](left_v, right_v)
            return EVALUATORS[v.operation_name](left_v)


def unify_number(n):
    f = float(n)
    i = int(f)
    return i if i == f else f


def eval_eq(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content == right.content
    return SimpleValue(content=content)


def eval_gt(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content > right.content
    return SimpleValue(content=content)


def eval_ge(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content >= right.content
    return SimpleValue(content=content)


def eval_lt(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content < right.content
    return SimpleValue(content=content)


def eval_le(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content <= right.content
    return SimpleValue(content=content)


def eval_ne(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content != right.content
    return SimpleValue(content=content)


def eval_and(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content and right.content
    return SimpleValue(content=content)


def eval_or(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content or right.content
    return SimpleValue(content=content)


def eval_not(v: SimpleValue, *args, **kwargs) -> SimpleValue:
    content = not v.content
    return SimpleValue(content=content)


def eval_xor(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = (left.content and not right.content) or (right and not left.content)
    return SimpleValue(content=content)


def eval_neg(v: SimpleValue, *args, **kwargs) -> SimpleValue:
    content = -1 * unify_number(v.content)
    return SimpleValue(content=content)


def eval_add(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content + right.content
    return SimpleValue(content=content)


def eval_sub(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = left.content - right.content
    return SimpleValue(content=content)


def eval_mul(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = unify_number(left.content) * unify_number(right.content)
    return SimpleValue(content=content)


def eval_div(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = unify_number(left.content) / unify_number(right.content)
    return SimpleValue(content=content)


def eval_mod(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = unify_number(left.content) % unify_number(right.content)
    return SimpleValue(content=content)


def eval_pow(left: SimpleValue, right: SimpleValue) -> SimpleValue:
    content = unify_number(left.content) ** unify_number(right.content)
    return SimpleValue(content=content)


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
