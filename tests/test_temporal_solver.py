from xml.etree.ElementTree import Element

from at_krl.core.knowledge_base import KnowledgeBase
from at_solver.core.wm import WorkingMemory

from at_temporal_solver.core.at_temporal_solver import TemporalSolver


def test_temporal_solver():
    def get_max_tact(e: Element):
        tact = 0
        for r in e:
            if int(r.attrib["Номер_такта"]) > tact:
                tact = int(r.attrib["Номер_такта"])
        return tact

    def get_all_resources_for_tact(e: Element, tact: int):
        return [r for r in e if int(r.attrib["Номер_такта"]) == tact]

    kb_dict = {
        "tag": "knowledge-base",
        "problem_info": None,
        "types": [{"tag": "type", "id": "TEST", "desc": None, "meta": "number", "from": 0, "to": 1000}],
        "classes": [
            {
                "tag": "class",
                "id": "КЛАСС_object1",
                "group": "ГРУППА1",
                "desc": "object1",
                "properties": [
                    {
                        "tag": "property",
                        "id": "attr1",
                        "type": {"tag": "ref", "id": "TEST", "ref": None, "meta": "type_or_class"},
                        "desc": None,
                        "value": None,
                        "source": "asked",
                        "question": None,
                        "query": None,
                    },
                    {
                        "tag": "property",
                        "id": "attr2",
                        "type": {"tag": "ref", "id": "TEST", "ref": None, "meta": "type_or_class"},
                        "desc": None,
                        "value": None,
                        "source": "asked",
                        "question": None,
                        "query": None,
                    },
                    {
                        "tag": "property",
                        "id": "attr3",
                        "type": {"tag": "ref", "id": "TEST", "ref": None, "meta": "type_or_class"},
                        "desc": None,
                        "value": None,
                        "source": "asked",
                        "question": None,
                        "query": None,
                    },
                ],
                "rules": [],
            },
            {
                "tag": "interval",
                "id": "TEST_INTERVAL",
                "group": "ИНТЕРВАЛ",
                "desc": "TEST_INTERVAL",
                "open": {
                    "tag": "lt",
                    "left": {"tag": "ref", "id": "object1", "ref": {"tag": "ref", "id": "attr2", "ref": None}},
                    "right": {"tag": "value", "content": 2},
                },
                "close": {
                    "tag": "ge",
                    "left": {"tag": "ref", "id": "object1", "ref": {"tag": "ref", "id": "attr2", "ref": None}},
                    "right": {"tag": "value", "content": 2},
                },
            },
            {
                "tag": "event",
                "id": "TEST_EVENT",
                "group": "СОБЫТИЕ",
                "desc": "TEST_EVENT",
                "occurance_condition": {
                    "tag": "gt",
                    "left": {"tag": "ref", "id": "object1", "ref": {"tag": "ref", "id": "attr1", "ref": None}},
                    "right": {"tag": "value", "content": 4},
                },
            },
            {
                "tag": "class",
                "id": "world",
                "group": None,
                "desc": "Класс верхнего уровня, включающий в себя экземпляры других классов и общие правила",
                "properties": [
                    {
                        "tag": "property",
                        "id": "object1",
                        "type": {"tag": "ref", "id": "КЛАСС_object1", "ref": None, "meta": "type_or_class"},
                        "desc": "object1",
                        "value": None,
                        "source": "asked",
                        "question": None,
                        "query": None,
                    }
                ],
                "rules": [
                    {
                        "tag": "rule",
                        "id": "TEST_RULE1",
                        "condition": {
                            "tag": "and",
                            "left": {
                                "tag": "ge",
                                "left": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {"tag": "ref", "id": "attr1", "ref": None},
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "right": {
                                    "tag": "value",
                                    "content": 0,
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                            },
                            "right": {
                                "tag": "lt",
                                "left": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {"tag": "ref", "id": "attr2", "ref": None},
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "right": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {"tag": "ref", "id": "attr1", "ref": None},
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                            },
                            "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                        },
                        "instructions": [
                            {
                                "tag": "assign",
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                "ref": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {
                                        "tag": "ref",
                                        "id": "attr3",
                                        "ref": None,
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "value": {
                                    "tag": "add",
                                    "left": {
                                        "tag": "ref",
                                        "id": "object1",
                                        "ref": {"tag": "ref", "id": "attr2", "ref": None},
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "right": {
                                        "tag": "ref",
                                        "id": "object1",
                                        "ref": {"tag": "ref", "id": "attr1", "ref": None},
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                            }
                        ],
                        "else_instructions": [],
                        "meta": "simple",
                        "period": None,
                        "desc": None,
                    },
                    {
                        "tag": "rule",
                        "id": "TEST_RULE2",
                        "condition": {
                            "tag": "ge",
                            "left": {
                                "tag": "ref",
                                "id": "object1",
                                "ref": {"tag": "ref", "id": "attr3", "ref": None},
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                            },
                            "right": {
                                "tag": "value",
                                "content": 5,
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                            },
                            "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                        },
                        "instructions": [
                            {
                                "tag": "assign",
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                "ref": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {
                                        "tag": "ref",
                                        "id": "attr1",
                                        "ref": None,
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "value": {
                                    "tag": "value",
                                    "content": 0,
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                            },
                            {
                                "tag": "assign",
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                "ref": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {
                                        "tag": "ref",
                                        "id": "attr2",
                                        "ref": None,
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "value": {
                                    "tag": "value",
                                    "content": 0,
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                            },
                        ],
                        "else_instructions": [],
                        "meta": "simple",
                        "period": None,
                        "desc": None,
                    },
                    {
                        "tag": "rule",
                        "id": "TEST_RULE3",
                        "condition": {
                            "tag": "and",
                            "left": {
                                "tag": "b",
                                "left": {"tag": "ref", "id": "TEST_EVENT", "index": None, "meta": "allen_reference"},
                                "right": {
                                    "tag": "ref",
                                    "id": "TEST_INTERVAL",
                                    "index": None,
                                    "meta": "allen_reference",
                                },
                            },
                            "right": {
                                "tag": "gt",
                                "left": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {"tag": "ref", "id": "attr3", "ref": None},
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "right": {
                                    "tag": "value",
                                    "content": 2,
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                            },
                            "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                        },
                        "instructions": [
                            {
                                "tag": "assign",
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                "ref": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {
                                        "tag": "ref",
                                        "id": "attr3",
                                        "ref": None,
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "value": {
                                    "tag": "value",
                                    "content": 8,
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                            },
                            {
                                "tag": "assign",
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                "ref": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {
                                        "tag": "ref",
                                        "id": "attr3",
                                        "ref": None,
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "value": {
                                    "tag": "value",
                                    "content": 0,
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                            },
                        ],
                        "else_instructions": [],
                        "meta": "simple",
                        "period": None,
                        "desc": None,
                    },
                ],
            },
        ],
    }

    kb = KnowledgeBase.from_json(kb_dict)
    solver = TemporalSolver(kb)

    tacts = [
        {
            "current_tick": 1,
            "resources": [
                {"resource_name": "object1", "attr1": 2, "attr2": 4, "attr3": 0},
            ],
        },
        {
            "current_tick": 2,
            "resources": [
                {"resource_name": "object1", "attr1": 3, "attr2": 3, "attr3": 0},
            ],
        },
        {
            "current_tick": 3,
            "resources": [
                {"resource_name": "object1", "attr1": 5, "attr2": 3, "attr3": 0},
            ],
        },
        {
            "current_tick": 4,
            "resources": [
                {"resource_name": "object1", "attr1": 2, "attr2": 1, "attr3": 0},
            ],
        },
        {
            "current_tick": 5,
            "resources": [
                {"resource_name": "object1", "attr1": 2, "attr2": 1, "attr3": 0},
            ],
        },
        {
            "current_tick": 6,
            "resources": [
                {"resource_name": "object1", "attr1": 2, "attr2": 2, "attr3": 0},
            ],
        },
        {
            "current_tick": 7,
            "resources": [
                {"resource_name": "object1", "attr1": 2, "attr2": 2, "attr3": 6},
            ],
        },
    ]
    for tact in tacts:
        solver.wm = WorkingMemory(kb=kb)
        print(solver.wm.all_values_dict)
        resources = tact["resources"]
        for resource in resources:
            resource_name = resource.pop("resource_name")
            for param, value in resource.items():
                ref = f"{resource_name}.{param}"

                solver.wm.set_value(ref, value)
        print(solver.wm.all_values_dict)
        solver.process_tact()
        print(solver.timeline.__dict__)
        print(solver.wm.locals)
