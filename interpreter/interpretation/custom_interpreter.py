from lark import Tree
from lark.visitors import Interpreter

from interpretation.activation_record import ActivationRecord, ARType


class CustomInterpreter(Interpreter):
    def __init__(self):
        pass

    def start(self, node: Tree):
        print("Interpreter is inside the start")
        ar = ActivationRecord(
            name='start',
            record_type=ARType.START,
            nesting_level=1,
        )
        self.visit_children(node)



    # def assignment(self, tree: TreeWithLanguageUnitAndSymbol):
    #     print("Interpreter is inside the assignment")
