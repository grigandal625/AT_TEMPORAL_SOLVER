from at_temporal_solver.core.at_temporal_solver import TemporalSolver
from at_temporal_solver.core.wm import WorkingMemory
from at_krl.core.knowledge_base import KnowledgeBase
import json
from xml.etree.ElementTree import fromstring, Element


def test_temporal_solver():
    def get_max_tact(e: Element):
        tact = 0
        for r in e:
            if int(r.attrib["Номер_такта"]) > tact:
                tact = int(r.attrib["Номер_такта"])
        return tact
            
    def get_all_resources_for_tact(e: Element, tact: int):
        return [r for r in e if int(r.attrib["Номер_такта"]) == tact]

    kb = KnowledgeBase.from_dict(json.load(open('.vscode/kb.json')))
    kb.validate()
    solver = TemporalSolver(kb)

    resources_element = fromstring(open('.vscode/ResourceParameters.xml', 'r').read())

    max_tact = get_max_tact(resources_element)

    for tact in range(1, max_tact + 1):
        solver.wm = WorkingMemory(kb)
        print(solver.wm.all_values_dict)
        resources = get_all_resources_for_tact(resources_element, tact)
        for resource in resources:
            for param in resource:
                ref = resource.attrib["Имя_ресурса"] + '.' + param.attrib["Имя_параметра"]
                v = param.text
                try:
                    v = float(v.replace(",", "."))
                    if int(v) == v:
                        v = int(v)
                except:
                    pass

                solver.wm.set_value(ref, v)
        
        print(solver.wm.all_values_dict)
        solver.process_tact()
        print(solver.timeline.__dict__)
        print(solver.wm.locals)


