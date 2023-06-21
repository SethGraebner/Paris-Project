'''
Additional type definitions to make the code more readable and modular.
'''


from typing import List, Dict,TypedDict
from dataclasses import dataclass

class ProcessedData(TypedDict):
    good: List[List[str]]
    bad: List[List[str]]

class UnprocessedData(TypedDict):
    good: List[str]
    bad: List[str]

class Match(TypedDict):
    monument: str
    snippet: str

class MatchedData(TypedDict):
    good: List[Match]
    bad: List[Match]

class Label(enumerate):
    good: int = 0
    bad: int = 1

class CleanedAndLabeledData(TypedDict):
    label: Label
    text: str
    cleaned: str