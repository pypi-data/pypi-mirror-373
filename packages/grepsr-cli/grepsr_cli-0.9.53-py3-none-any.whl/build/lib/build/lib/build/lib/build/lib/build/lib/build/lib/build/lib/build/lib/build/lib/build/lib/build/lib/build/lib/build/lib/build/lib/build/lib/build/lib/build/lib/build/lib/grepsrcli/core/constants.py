from dataclasses import dataclass
import re
from enum import Enum

PLATFORMS = ['php','node', 'php_next']
COMMENT_BLOCK_PATTERN = re.compile(r"(\/\*\*.?\n)(.*?)(\s*\*\/\s*\n)", re.DOTALL)
CLASS_DECLARATION_PATTERN = re.compile(r'class\s+\w+\s+extends\s(\w+)\b', re.DOTALL)

@dataclass
class LanguageTypeValue:
    index: int
    name: str
    template_name: str

class LanguageType(Enum):
    PHP = ('1', 'php')
    JAVASCRIPT = ('2', 'javascript')
    TYPESCRIPT = ('3', 'typescript')

    def __new__(cls, value, display_name):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.display_name = display_name
        if display_name in ['javascript', 'typescript']:
            obj._template_name = 'node'
        else:
            obj._template_name = 'php'
        return obj
    
    @property
    def template_name(self) -> str:
        return self._template_name
    


NODE_LANGUAGE_TYPES = [LanguageType.JAVASCRIPT, LanguageType.TYPESCRIPT]