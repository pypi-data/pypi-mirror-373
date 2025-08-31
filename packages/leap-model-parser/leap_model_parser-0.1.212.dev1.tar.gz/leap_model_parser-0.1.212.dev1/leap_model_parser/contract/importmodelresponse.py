from enum import Enum


class ImportModelTypeEnum(Enum):
    JSON_TF2 = "JSON_TF2"
    ONNX = "ONNX"
    PB_TF2 = "PB_TF2"
    H5_TF2 = "H5_TF2"
