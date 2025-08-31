import glob
import json
import ntpath
import pickle
import tarfile
import tempfile
from importlib.util import find_spec
from pathlib import Path


import tensorflow as tf  # type: ignore
from code_loader.contract.mapping import NodeConnection, NodeMapping  # type: ignore
from keras import Model  # type: ignore
from keras_data_format_converter import convert_channels_first_to_last  # type: ignore
from leap_model_rebuilder import rebuild_model  # type: ignore
from onnx2kerastl import onnx_to_keras  # type: ignore
from onnx2kerastl.converter import ConvertedResponse  # type: ignore
from onnx2kerastl.customonnxlayer import onnx_custom_layers  # type: ignore
from onnx2kerastl.exceptions import OnnxUnsupported  # type: ignore
from tensorflow.keras.models import load_model  # type: ignore

from leap_model_parser.contract.graph import Node, InputInfo
from leap_model_parser.contract.importmodelresponse import ImportModelTypeEnum
from leap_model_parser.keras_json_model_import import KerasJsonModelImport
from leap_model_parser.leap_graph_editor import LeapGraphEditor  # type: ignore

from typing import Callable, Optional, List, Dict, Tuple, Type

onnx_imported = False
package_name = 'onnx'
spec = find_spec(package_name)
if spec is not None:
    import onnx  # type: ignore

    onnx_imported = True

class ModelParser:
    def __init__(self, should_transform_inputs_and_outputs=False,
                 custom_layers=None,
                 mapping_connections: Optional[List[NodeConnection]] = None):
        self._should_transform_inputs_and_outputs = should_transform_inputs_and_outputs
        self.custom_layers = custom_layers
        if custom_layers is None:
            self.custom_layers = {}

        self.custom_layers = {**self.custom_layers, **onnx_custom_layers}

        self.mapping_connections = mapping_connections

        self._model_types_converter = {
            ImportModelTypeEnum.JSON_TF2.value: self.convert_json_model,
            ImportModelTypeEnum.H5_TF2.value: self.convert_h5_model,
            ImportModelTypeEnum.ONNX.value: self.convert_onnx_model,
            ImportModelTypeEnum.PB_TF2.value: self.convert_pb_model,
        }

    def get_keras_model_and_model_graph(
            self, model_path: Path, model_type: ImportModelTypeEnum) -> Tuple[Dict[str, Node], List[InputInfo], Optional[Model], Optional[str]]:
        model_to_keras_converter: Optional[Callable[[str], Tuple[Dict[str, Node], Model, Optional[str]]]] = \
            self._model_types_converter.get(model_type.value)
        if model_to_keras_converter is None:
            raise Exception(
                f"Unable to import external version, {str(model_path)} file format isn't supported")

        file_path = str(model_path)
        model_schema, keras_model_with_weights, error_info = model_to_keras_converter(file_path)
        model_generator = KerasJsonModelImport(self.custom_layers)

        keras_model = keras_model_with_weights
        if keras_model is None:
            keras_model = tf.keras.models.model_from_json(json.dumps(model_schema))
        layer_name_to_inbound_nodes = {
            layer.name: layer.inbound_nodes
            for layer in keras_model.layers
        }

        graph, connected_inputs = model_generator.generate_graph(
            model_schema, layer_name_to_inbound_nodes)

        if self.mapping_connections is not None:
            leap_graph_editor = LeapGraphEditor(graph, keras_model_with_weights)
            leap_graph_editor.add_connections_to_graph(self.mapping_connections)

        return graph, connected_inputs, keras_model_with_weights, error_info


    def _get_k_model_from_pb_path(self, file_path: str):
        tar_file = tarfile.open(file_path)
        with tempfile.TemporaryDirectory() as temp_dir:
            tar_file.extractall(temp_dir)
            pb_files = glob.glob(temp_dir + "/**/*.pb", recursive=True)
            if len(pb_files) == 0:
                raise Exception('no pb files were found')

            pb_file_path = next(iter(pb_files))
            pb_folder_path = next(iter(ntpath.split(pb_file_path)))

            k_model = self._load_keras_model_with_custom_layers(pb_folder_path)
        return k_model

    def generate_model_graph(self, model_path: Path, model_type: ImportModelTypeEnum) -> Tuple[Dict[str, Node], List[InputInfo]]:
        model_graph, connected_inputs, _, error_info = self.get_keras_model_and_model_graph(
            model_path, model_type)
        return model_graph, connected_inputs

    @classmethod
    def convert_json_model(cls, file_path: str) -> Tuple[Dict[str, Node], None, Optional[str]]:
        with open(file_path, 'r') as f:
            model_schema = json.load(f)
        return model_schema, None, None

    def convert_pb_model(self, file_path: str) -> Tuple[Dict[str, Node], Model, Optional[str]]:
        k_model = self._get_k_model_from_pb_path(file_path)
        return self.convert_to_keras_model(k_model)

    def convert_onnx_model(self, file_path: str) -> Tuple[Dict[str, Node], Model, Optional[str]]:
        if not onnx_imported:
            raise OnnxUnsupported()

        onnx_model = onnx.load_model(file_path)
        input_all = [_input.name for _input in onnx_model.graph.input]
        input_initializer = [
            node.name for node in onnx_model.graph.initializer]
        input_names = list(set(input_all) - set(input_initializer))
        converted_response: ConvertedResponse = onnx_to_keras(onnx_model, input_names=input_names,
                                name_policy='attach_weights_name', allow_partial_compilation=False)
        return self.convert_to_keras_model(converted_response.converted_model, converted_response.error_info)

    def _load_keras_model_with_custom_layers(self, file_path: str):
        custom_objects = {}
        if self.custom_layers is not None:
            custom_objects = self.custom_layers
        return load_model(file_path, custom_objects=custom_objects, compile=False)

    def convert_h5_model(self, file_path: str) -> Tuple[Dict[str, Node], Model, Optional[str]]:
        imported_model = self._load_keras_model_with_custom_layers(file_path)
        return self.convert_to_keras_model(imported_model)

    def convert_to_keras_model(self, k_model, error_info: Optional[str] = None) -> Tuple[Dict[str, Node], Model, Optional[str]]:
        converted_k_model = convert_channels_first_to_last(
            k_model, self._should_transform_inputs_and_outputs, self.custom_layers)

        model_schema = json.loads(converted_k_model.to_json())

        return model_schema, converted_k_model, error_info
