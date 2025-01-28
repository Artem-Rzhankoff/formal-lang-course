from enum import Enum

class Type(Enum):
    GRAPH = 1
    FA = 2
    CFG = 3
    NUM = 4
    CHAR = 5
    EDGE = 6
    SET = 7
    SET_TUPLES = 8
    RANGE = 9
    VOID = 10

class TypeEnviroment:
    def __init__(self):
        self.vars: dict[str, Type] = {}
    
    def __contains__(self, item: str):
        return item in self.vars
    
    def add(self, var_name: str, var_type: Type):
        self.vars[var_name] = var_type

    def get(self, var_name: str):
        if var_name not in self.vars:
            raise ValueError()
        return self.vars[var_name]
    