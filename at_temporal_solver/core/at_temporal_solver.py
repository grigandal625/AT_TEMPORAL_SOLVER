from at_solver.core.wm import WorkingMemory
from at_temporal_solver.core.timeline import Timeline, TactRecord
from at_temporal_solver.evaluations.simple import SimpleEvaluator
from at_temporal_solver.evaluations.allen import AllenEvaluator
from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.simple.simple_evaluatable import SimpleEvaluatable
from at_krl.core.simple.simple_operation import SimpleOperation
from at_krl.core.temporal.allen_evaluatable import AllenEvaluatable
from at_krl.core.kb_rule import KBRule


class TemporalSolver:
    wm: WorkingMemory
    kb: KnowledgeBase
    timeline: Timeline
    signified_meta: dict = None

    def __init__(self, kb: KnowledgeBase) -> None:
        self.wm = WorkingMemory(kb=kb)
        self.kb = kb
        self.timeline = Timeline()
        self.current_tact = None
        self.signified_meta = {}

    def process_tact(self, as_new=True):
        if as_new:
            if self.current_tact is None:
                self.current_tact = 0
            else:
                self.current_tact += 1
        self.signified_meta = {}
        self.build_timeline_tact()
        self.signify_temporal_operations_in_rules()

    def build_timeline_tact(self) -> TactRecord:
        evaluator = SimpleEvaluator(self.wm)
        for interval in self.kb.classes.intervals:
            open_value = evaluator.eval(interval.open)
            instance = self.timeline.get_interval_instance(interval)
            if open_value.content:
                instance = self.timeline.open_interval_instance(self.current_tact, interval)
            if instance is not None and instance.open_tact != self.current_tact:
                close_value = evaluator.eval(interval.close)
                if close_value.content:
                    self.timeline.close_interval_instance(self.current_tact, interval)

        for event in self.kb.classes.events:
            occurance_value = evaluator.eval(event.occurance_condition)
            if occurance_value.content:
                self.timeline.create_event_instance(self.current_tact, event)
        
        result = self.timeline._tacts.get(self.current_tact)
        if result is None:
            return self.timeline.get_or_create_tact_record(self.current_tact)
        return result
            
    def signify_temporal_operations_in_rules(self):
        for rule in self.kb.rules:
            self.search_and_signify(rule.condition, rule=rule)
    
    def search_and_signify(self, v: SimpleEvaluatable, rule: KBRule):
        if isinstance(v, AllenEvaluatable):
            allen_evaluator = AllenEvaluator(self)
            res = allen_evaluator.eval(v)
            self.wm.set_value('signifier.' + v.xml_owner_path, res)
            self.signified_meta[v.xml_owner_path] = {
                'rule': rule.id,
                'allen_operation': v.krl,
                'value': res.content
            }
        elif isinstance(v, SimpleOperation):
            self.search_and_signify(v.left, rule=rule)
            if v.is_binary:
                self.search_and_signify(v.right, rule=rule)