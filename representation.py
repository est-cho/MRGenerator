from dataclasses import dataclass
import operator


OPERATORS = ["==", "<=", ">=", "<", ">", "!="]
OPERATOR_DICT = {"==": operator.eq, "<=": operator.le, ">=": operator.ge,
                 "<": operator.lt, ">": operator.gt, "!=": operator.ne}

VAL_TYPE_VAR = 'v'
VAL_TYPE_CONS = 'c'


@dataclass
class Value:
    type: str = ''
    index: int = 0
    time: int = None

    def copy(self):
        copy = Value()
        copy.type = self.type
        copy.index = self.index
        copy.time = self.time
        return copy


@dataclass
class Prop:
    v_left: Value = Value()
    op: str = ''
    v_right: Value = Value()

    def copy(self):
        copy = Prop()
        copy.v_left = self.v_left.copy()
        copy.op = self.op
        copy.v_right = self.v_right.copy()
        return copy


@dataclass
class Statement:
    index: int = 0
    p_left: Prop = Prop()
    p_right: Prop = Prop()

    def copy(self):
        copy = Statement()
        copy.index = self.index
        copy.p_left = self.p_left.copy()
        copy.p_right = self.p_right.copy()
        return copy



