from enum import Enum


class DatasetKind(Enum):
    Acoustic = 1,
    Language = 2,
    Pronunciation = 3


class ModelType(Enum):
    BaseModel = 1,
    CustomModel = 2,
    ProjectModel = 3