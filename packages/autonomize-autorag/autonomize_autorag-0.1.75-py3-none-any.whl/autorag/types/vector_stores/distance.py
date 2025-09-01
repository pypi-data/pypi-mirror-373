# pylint: disable=missing-class-docstring, missing-module-docstring

from enum import Enum


class DistanceType(str, Enum):
    DOT_PRODUCT = "DOT_PRODUCT"
    COSINE = "COSINE"
    EUCLIDEAN = "EUCLIDEAN"
