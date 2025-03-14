from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from at_krl.core.temporal.allen_event import KBEvent
from at_krl.core.temporal.allen_interval import KBInterval
from at_krl.core.temporal.allen_reference import AllenReference


@dataclass(kw_only=True)
class EventInstance:
    event: KBEvent
    occurance_tact: int


@dataclass(kw_only=True)
class IntervalInstance:
    interval: KBInterval
    open_tact: int
    close_tact: Optional[int] = None

    @property
    def closed(self):
        return self.close_tact is not None


class TactRecord:
    tact: int
    event_instances: List[EventInstance]
    opened_interval_instances: List[IntervalInstance]

    def __init__(self, tact: int):
        self.tact = tact
        self.event_instances = []
        self.opened_interval_instances = []

    def has_event_instance(self, event: Union[str, KBEvent]):
        return self.get_event_instance_by_event(event) is not None

    def get_event_instance_by_event(self, event: Union[str, KBEvent]) -> Optional[EventInstance]:
        event_name = event.id if isinstance(event, KBEvent) else event
        for instance in self.event_instances:
            if instance.event.id == event_name:
                return instance
        return None

    def create_event_instance(self, event: KBEvent) -> EventInstance:
        existing_instance = self.get_event_instance_by_event(event)
        if existing_instance is not None:
            return existing_instance
        instance = EventInstance(event=event, occurance_tact=self.tact)
        self.event_instances.append(instance)
        return instance

    def get_interval_instance_by_interval(self, interval: Union[str, KBInterval]) -> Optional[IntervalInstance]:
        interval_name = interval.id if isinstance(interval, KBInterval) else interval
        for instance in self.opened_interval_instances:
            if instance.interval.id == interval_name:
                return instance
        return None

    def has_interval_instance(self, interval: Union[str, KBInterval]):
        return self.get_interval_instance_by_interval(interval) is not None

    def open_interval_instance(self, interval: KBInterval) -> IntervalInstance:
        existing_instance = self.get_interval_instance_by_interval(interval)
        if existing_instance is not None:
            return existing_instance
        instance = IntervalInstance(interval=interval, open_tact=self.tact)
        self.opened_interval_instances.append(instance)
        return instance

    def close_interval_instances(
        self, interval: Union[str, KBInterval, IntervalInstance], tact: int
    ) -> IntervalInstance:
        if isinstance(interval, IntervalInstance):
            interval = interval.interval
        if isinstance(interval, KBInterval):
            interval = interval.id
        existing_instance = self.get_interval_instance_by_interval(interval)
        if existing_instance is None:
            raise ReferenceError(f"No interval instance {interval} found at tact {self.tact}")
        if existing_instance.open_tact >= tact:
            raise ValueError(
                f"Supposed close tact must be greater than open tact {existing_instance.open_tact}, but got {tact}"
            )
        index = self.opened_interval_instances.index(existing_instance)
        if existing_instance.closed and (existing_instance.close_tact != tact):
            raise ValueError(f"Interval {interval} is already closed at tact {existing_instance.close_tact}")
        elif existing_instance.close_tact == tact:
            return existing_instance
        existing_instance.close_tact = tact
        self.opened_interval_instances[index] = existing_instance
        return existing_instance

    @property
    def __dict__(self):
        return {
            "tact": self.tact,
            "opened_intervals": [
                {"interval": instance.interval.id, "open_tact": instance.open_tact, "close_tact": instance.close_tact}
                for instance in self.opened_interval_instances
            ],
            "events": [
                {"event": instance.event.id, "occurance_tact": instance.occurance_tact}
                for instance in self.event_instances
            ],
        }


class Timeline:
    _tacts: Dict[int, TactRecord]

    def __init__(self) -> None:
        self._tacts = {}

    @property
    def tact_numbers(self):
        return list(self._tacts.keys())

    def get_or_create_tact_record(self, tact: int) -> TactRecord:
        tact_record = self._tacts.get(tact)
        if tact_record is None:
            lact_tact_num = 0
            if not len(self.tact_numbers):
                if tact != 0:
                    raise ValueError("tact number must be equal to 0 when the set of tacts is empty")
            else:
                lact_tact_num = self.tact_numbers[-1]
                if tact > lact_tact_num and tact - lact_tact_num != 1:
                    raise ValueError(f"New tact is {tact} that differs from the last tact {lact_tact_num} more then 1")
            tact_record = TactRecord(tact)
            self._tacts[tact] = tact_record
        return tact_record

    def still_opened_intervals(self, last_tact: int = None) -> List[IntervalInstance]:
        last_tact = last_tact if last_tact is not None else self.last_tact_number
        if last_tact is None:
            return []
        result = []
        for tact in range(last_tact + 1):
            tact_record = self._tacts.get(tact)
            if tact_record is not None:
                for interval_instance in tact_record.opened_interval_instances:
                    if not interval_instance.closed:
                        result.append(interval_instance)
        return result

    @property
    def last_tact_number(self):
        tacts_list = list(self._tacts.keys())
        if not len(tacts_list):
            return None
        return max(list(self._tacts.keys()))

    @property
    def sorted_tact_list(self) -> List[TactRecord]:
        if self.last_tact_number is None:
            return []
        return [self._tacts[tact] for tact in range(self.last_tact_number + 1)]

    def interval_is_still_opened(self, interval: Union[IntervalInstance, KBInterval, str]) -> bool:
        if isinstance(interval, IntervalInstance):
            interval = interval.interval
        if isinstance(interval, KBInterval):
            interval = interval.id
        still_opened_intervals = self.still_opened_intervals()
        return interval in [instance.interval.id for instance in still_opened_intervals]

    def open_interval_instance(self, tact: int, interval: KBInterval) -> IntervalInstance:
        if self.interval_is_still_opened(interval):
            return self.get_interval_instance(interval)
        tact_record = self.get_or_create_tact_record(tact)
        result = tact_record.open_interval_instance(interval)
        self._tacts[tact] = tact_record
        return result

    def close_interval_instance(self, tact: int, interval: KBInterval) -> Optional[IntervalInstance]:
        instance = self.get_interval_instance(interval)
        if (instance is None) ^ instance.closed:
            return None
        instance.close_tact = tact
        return instance

    def create_event_instance(self, tact, event: KBEvent) -> EventInstance:
        tact_record = self.get_or_create_tact_record(tact)
        result = tact_record.create_event_instance(event)
        self._tacts[tact] = tact_record
        return result

    def get_event_instance(self, event: Union[str, AllenReference, EventInstance], index=-1) -> Optional[EventInstance]:
        all_instances = self.get_all_event_instances(event)
        if all_instances and index in range(-len(all_instances), len(all_instances)):
            return all_instances[index]

    def get_interval_instance(
        self, interval: Union[AllenReference, KBInterval, str], index=-1
    ) -> Optional[IntervalInstance]:
        all_instances = self.get_all_interval_instances(interval)
        if all_instances and index in range(-len(all_instances), len(all_instances)):
            return all_instances[index]

    def get_all_event_instances(self, event: Union[str, AllenReference, EventInstance]):
        if isinstance(event, EventInstance):
            event = event.event
        elif isinstance(event, AllenReference):
            event = event.target
        result = []
        tact_list: List[TactRecord] = self.sorted_tact_list
        for tact_record in tact_list:
            instance = tact_record.get_event_instance_by_event(event)
            if instance is not None:
                result.append(instance)
        return result

    def get_all_interval_instances(self, interval: Union[AllenReference, KBInterval, str]):
        if isinstance(interval, IntervalInstance):
            interval = interval.interval
        elif isinstance(interval, AllenReference):
            interval = interval.target
        result = []
        tact_list: List[TactRecord] = self.sorted_tact_list
        for tact_record in tact_list:
            instance = tact_record.get_interval_instance_by_interval(interval)
            if instance is not None:
                result.append(instance)
        return result

    @property
    def __dict__(self):
        return {"tacts": [tact.__dict__ for tact in self.sorted_tact_list]}
