from enum import Enum

class ExplanationMethod(Enum):
    SIMILARITY = "similarity"
    DISSIMILARITY = "dissimilarity"
    COUNT = "count_based"