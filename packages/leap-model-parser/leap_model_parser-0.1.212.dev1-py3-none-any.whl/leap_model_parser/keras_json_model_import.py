import json
from collections import defaultdict
from pathlib import Path
from typing import Set, Dict, Any, List, Type, Optional, Tuple

import tensorflow as tf  # type: ignore
from keras.engine.keras_tensor import KerasTensor  # type: ignore
from keras.engine.node import Node  # type: ignore
from keras.engine.node import Node as keras_node # type: ignore
from keras.layers import Layer # type: ignore
from keras.layers.convolutional.base_conv import Conv # type: ignore
from tensorflow.python.keras.utils.generic_utils import func_load  # type: ignore

from leap_model_parser.contract.graph import InputInfo, Node, WrapperData, ConnectionOutput, OutputData, \
    ConnectionInput, InputData

layer_attributes_adaptation = {'bias_initializer', 'kernel_initializer'}

nojsonable_arg_serialization_prefix = '*tensorleap-nojsonable*'


def deserialize_non_json_arg(arg: str):
    return eval(arg[len(nojsonable_arg_serialization_prefix):])


class KerasJsonModelImport:
    def __init__(self, custom_layers: Optional[Dict[str, Type[tf.keras.layers.Layer]]] = None) -> None:
        self.id = 1
        self.nodes_cache: Dict[str, Node] = defaultdict()
        self.layer_name_to_layer: Dict[str, Dict] = defaultdict()
        self.visited_connections: Set[str] = set()
        self.ui_components: Dict[str, Dict] = defaultdict()
        self.connected_inputs: List[InputInfo] = []

        if custom_layers is None:
            custom_layers = {}
        self.custom_layers = custom_layers

    def prepare_model_to_import(self, model_schema) -> None:
        ui_components_file_path = Path(
            __file__).parent / 'contract' / 'ui_components.json'
        with open(str(ui_components_file_path), 'r') as f:
            ui_component_json = json.load(f)

        for layer in model_schema['config']['layers']:
            layer['is_representation_block'] = KerasJsonModelImport.is_representation_block(
                layer)
            self.layer_name_to_layer[layer['name']] = layer

        self.ui_components = {layer['name']: layer for layer in ui_component_json}

    @staticmethod
    def is_representation_block(layer: Dict[str, Any]) -> bool:
        return len(layer['inbound_nodes']) > 1

    def generate_graph(
            self, model_schema: Dict, layer_name_to_inbound_nodes: Dict[str, List[Node]]) -> Tuple[
        Dict[str, Node], List[InputInfo]]:
        self.prepare_model_to_import(model_schema)
        for graph_output_layer in model_schema['config']['output_layers']:
            current_layer = self.layer_name_to_layer[graph_output_layer[0]]
            self.generate_graph_recursive(
                current_layer, graph_output_layer[1], layer_name_to_inbound_nodes)

        nodes = {node.id: node for node in self.nodes_cache.values()}
        _add_origin_name_to_nodes(nodes)
        return nodes, self.connected_inputs

    def generate_graph_recursive(self, current_layer: Dict[str, Any], instance_index: int,
                                 layer_name_to_inbound_nodes: Dict[str, List[keras_node]]):
        self.generate_node(current_layer, instance_index,
                           layer_name_to_inbound_nodes)

        inbound_nodes = layer_name_to_inbound_nodes[current_layer['config']['name']]
        if len(inbound_nodes) == 0:
            return
        inbound_node = inbound_nodes[instance_index]
        inbound_layers = [
            parent_node.layer for parent_node in inbound_node.parent_nodes]
        for input_index, inbound_layer in enumerate(inbound_layers):
            input_id = inbound_node.flat_input_ids[input_index]
            input_node_instance_index = [node.flat_output_ids[0]
                                         for node in inbound_layer.inbound_nodes].index(input_id)
            layer_name = inbound_layer.name
            input_layer = self.layer_name_to_layer[layer_name]
            self.generate_node(
                input_layer, input_node_instance_index, layer_name_to_inbound_nodes)

            input_node_name = f"{input_layer['name']}_{input_node_instance_index}"
            current_node_name = f"{current_layer['name']}_{instance_index}"
            connection_name = f"{input_node_name}_{current_node_name}_{input_index}"
            if connection_name in self.visited_connections:
                continue

            self.visited_connections.add(connection_name)
            self.attach(input_layer, input_node_name,
                        current_node_name, input_index)
            self.generate_graph_recursive(current_layer=input_layer, instance_index=input_node_instance_index,
                                          layer_name_to_inbound_nodes=layer_name_to_inbound_nodes)

    def attach(self, input_layer: Dict, node_input_layer_name: str, node_output_layer_name: str, input_index: int):
        node_output_layer = self.nodes_cache[node_output_layer_name]
        if input_layer['class_name'] == 'InputLayer':
            if node_output_layer.name == 'Lambda':
                return
            node_input_layer_name = '-'.join(['input', input_layer['name']])

        node_input_layer = self.nodes_cache[node_input_layer_name]
        node_output_key = self.get_connection_key(
            input_layer, node_input_layer, 'outputs', input_index)
        node_input_key = self.get_connection_key(
            input_layer, node_output_layer, 'inputs', input_index)
        if node_output_key is None or node_input_key is None:
            return

        if node_output_key not in node_input_layer.outputs:
            node_input_layer.outputs[node_output_key] = ConnectionOutput(connections=[])
        node_input_layer.outputs[node_output_key].connections.append(OutputData(node=node_output_layer.id,
                                                                                input=node_input_key
                                                                                ))

        if node_input_key not in node_output_layer.inputs:
            node_output_layer.inputs[node_input_key] = ConnectionInput(connections=[])
        node_output_layer.inputs[node_input_key].connections.append(InputData(
            node=node_input_layer.id,
            output=node_output_key
        ))

    def _get_layer_metadata(self, layer_json: Dict) -> Optional[Dict]:
        layer_metadata = self.ui_components.get(layer_json['class_name'])
        if layer_metadata is None:
            if layer_json['class_name'] in self.custom_layers:
                layer_metadata = {
                    'type': 'CustomLayer',
                    'class_name': 'CustomLayer',
                    'selected': layer_json['class_name']
                }
        return layer_metadata

    def generate_node(
            self, layer: Dict[str, Any], instance_index: int, layer_name_to_inbound_nodes: Dict[str, List[keras_node]]):
        if layer['class_name'] == 'InputLayer':
            self._handle_input_layer(layer)
            return

        node_key = f"{layer['name']}_{instance_index}"
        if node_key in self.nodes_cache:
            return

        layer = self.handle_cudnn(layer)
        layer_metadata = self._get_layer_metadata(layer)
        if layer_metadata is None:
            raise Exception(
                f"{layer['class_name']} layer is not supported, please try to contact Tensorleap support")

        if layer_metadata['type'] == 'wrapper':
            wrapped_layer = self.handle_wrapper_layer(layer)
            layer_name_to_inbound_nodes[wrapped_layer['config']['name']] = layer_name_to_inbound_nodes[layer['config']['name']]
            self.generate_node(wrapped_layer, instance_index,
                               layer_name_to_inbound_nodes)
            return

        inbound_nodes = layer_name_to_inbound_nodes[layer['config']['name']]
        inbound_node = inbound_nodes[instance_index]
        keras_layer = inbound_node.layer
        if hasattr(keras_layer, "layer"):
            keras_layer = keras_layer.layer
        if isinstance(keras_layer, Conv) and keras_layer.input.shape[-1] is None:
            self.handle_dynamic_input(layer, keras_layer)

        if layer['is_representation_block']:
            self.generate_rp_node(layer, layer_metadata, node_key)
        else:
            self.generate_regular_node(
                layer, layer_metadata, node_key, layer_name_to_inbound_nodes)
        self.id += 1

    @staticmethod
    def _serialize_arg(arg):
        if isinstance(arg, KerasTensor):
            return arg.name
        if hasattr(arg, 'numpy'):
            arg = arg.numpy()
        if hasattr(arg, 'tolist'):
            return arg.tolist()
        if isinstance(arg, (str, float, int, bool, type(None))):
            return arg
        if isinstance(arg, tf.dtypes.DType):
            return f'{nojsonable_arg_serialization_prefix}tf.{arg.name}'
        if isinstance(arg, (list, tuple)):
            return [KerasJsonModelImport._serialize_arg(a) for a in arg]
        if isinstance(arg, dict):
            return {k: KerasJsonModelImport._serialize_arg(v) for k, v in arg.items()}
        if isinstance(arg, tf.TensorShape):
            return f'{nojsonable_arg_serialization_prefix}tf.TensorShape({str([v for v in arg])})'
        raise Exception('Unsupported call arg')

    @staticmethod
    def _serialize_call_args(call_args: Tuple, call_kwargs: Dict) -> str:
        serialized_call_args = [
            KerasJsonModelImport._serialize_arg(arg) for arg in call_args]
        serialized_call_kwargs = {k: KerasJsonModelImport._serialize_arg(
            v) for k, v in call_kwargs.items()}

        return json.dumps({'serialized_call_args': serialized_call_args,
                           'serialized_call_kwargs': serialized_call_kwargs})

    def generate_regular_node(self, layer: Dict[str, Any], layer_metadata: Dict[str, Any], node_key: str,
                              layer_name_to_inbound_nodes: Dict[str, List[Node]]):
        data = layer['config']
        if layer['class_name'] in ('TFOpLambda', 'SlicingOpLambda') or layer['class_name'] in self.custom_layers:
            call_args = layer_name_to_inbound_nodes[layer['config']
            ['name']][0].call_args
            call_kwargs = layer_name_to_inbound_nodes[layer['config']
            ['name']][0].call_kwargs
            data['call_args'] = self._serialize_call_args(
                call_args, call_kwargs)
        elif layer['class_name'] == "Lambda":
            lambda_func = func_load(layer['config']['function'])
            data['arg_names'] = list(lambda_func.__code__.co_varnames)

        self.layer_data_adjustments(data, layer_metadata)
        node = Node(id=str(self.id), name=layer_metadata.get(
            "class_name", layer["class_name"]), data=data, position=[0, 0])
        if 'wrapper' in layer:
            node.wrapper = layer['wrapper']
        self.nodes_cache[node_key] = node

    @classmethod
    def handle_wrapper_layer(cls, layer):
        wrapped_layer = layer['config']['layer']
        wrapped_layer['name'] = layer['name']
        wrapped_layer['is_representation_block'] = layer['is_representation_block']
        wrapper_data = layer['config'].copy()
        wrapper_data.pop('layer')
        wrapper_data.pop('name')
        # TODO: remove this hard coded condition after support
        if 'merge_mode' in wrapper_data and wrapper_data.get('merge_mode') is None:
            raise Exception(f"{layer['class_name']} layer with merge_mode None is not supported,"
                            f" please try to contact Tensorleap support")
        wrapped_layer['wrapper'] = WrapperData(
            layer['class_name'], wrapper_data)
        return wrapped_layer

    @classmethod
    def layer_data_adjustments(cls, layer_config: Dict[str, Any], layer_metadata: Dict[str, Any]) -> None:
        for layer_attribute in layer_attributes_adaptation:
            if layer_attribute in layer_config:
                layer_config[layer_attribute] = layer_config[layer_attribute]['class_name']

        layer_config["type"] = layer_metadata.get('type')
        if 'selected' in layer_metadata:
            layer_config["selected"] = layer_metadata['selected']
        # TODO: remove this hard coded condition after support
        if layer_config.get('return_state'):
            raise Exception(f"{layer_metadata.get('name')} layer with return_state True is not supported,"
                            f" please try to contact Tensorleap support")

    def generate_rp_node(self, layer: Dict[str, Any], layer_metadata: Dict[str, Any], node_key: str) -> None:
        if layer['name'] not in self.nodes_cache:
            data = layer['config']
            self.layer_data_adjustments(data, layer_metadata)
            data["output_blocks"] = []
            node = Node(id=str(self.id),
                        name=layer["class_name"], data=data, position=[0, 0])
            if 'wrapper' in layer:
                node.wrapper = layer['wrapper']
            self.nodes_cache[layer['name']] = node

            self.id += 1
        data = {
            "output_name": "Action",
            "node_id": self.nodes_cache[layer["name"]].id,
            "parent_name": layer["class_name"]
        }
        self.nodes_cache[node_key] = Node(
            id=str(self.id), name='Representation Block', data=data, position=[0, 0])
        self.nodes_cache[layer["name"]].data["output_blocks"].append({
            "block_node_id": self.nodes_cache[node_key].id,
            "output_name": "Action"
        })

    def get_connection_key(self, node_input_layer, node: Node, direction: str, index: int) -> Optional[str]:
        layer_metadata = self.ui_components.get(node.name)
        if _is_represntaion_block_node(node) or layer_metadata is None:
            if direction == 'inputs':
                connection_format = f"{node.id}-input"
            else:
                connection_format = f"{node.id}-feature_map"
        elif _is_input_node(node):
            connection_format = f"{node.id}-{node_input_layer['name']}"
        else:
            try:
                connection_format = layer_metadata[f"{direction}_data"][direction][index]['name']
            except IndexError:
                connection_format = layer_metadata[f"{direction}_data"][direction][0]['name']
            if connection_format.count('${id}') > 0:
                connection_format = f"{node.id}-{index}"
                if 'custom_input_keys' not in node.data:
                    node.data['custom_input_keys'] = []
                node.data['custom_input_keys'].append(connection_format)
            else:
                connection_format = f"{node.id}-{connection_format}"
        return connection_format

    def handle_cudnn(self, layer: Dict[str, Any]) -> Dict[str, Any]:
        if layer['class_name'] == 'CuDNNGRU':
            layer['class_name'] = 'GRU'
            gru_metadata = self.ui_components['GRU']
            gru_config = {}
            for gru_prop in gru_metadata["properties"]:
                if gru_prop["name"] in layer['config']:
                    gru_config[gru_prop["name"]
                    ] = layer['config'][gru_prop["name"]]
                elif gru_prop["isdefault"]:
                    gru_config[gru_prop["name"]] = gru_prop["default_val"]

            gru_config["name"] = layer['config']["name"]
            gru_config["trainable"] = layer['config']["trainable"]

            layer['config'] = gru_config
        return layer

    def _handle_input_layer(self, layer: Dict[str, Any]):
        input_name = layer['name']
        node_key = '-'.join(['input', input_name])
        inputNode = self.nodes_cache.get(node_key)
        if inputNode is not None:
            return
        shape = layer['config']['batch_input_shape']
        input_info = InputInfo(name=input_name, shape=shape[1:])
        self.connected_inputs.append(input_info)
        input_copy = {
            'type': 'Input',
            'output_name': input_name
        }
        inputNode = Node(
            id=str(self.id), name='Input', data=input_copy, position=[0, 0])
        self.nodes_cache[node_key] = inputNode
        self.id += 1

    @staticmethod
    def handle_dynamic_input(layer: Dict[str, Any], keras_layer: Layer):
        layer['config']["input_spec"] = keras_layer.input_spec.get_config()


def _add_origin_name_to_nodes(nodes: Dict[str, Node]):
    for node in nodes.values():
        if "name" in node.data:
            node.data["origin_name"] = node.data["name"]
            node.data.pop("name")
        elif "output_name" in node.data:
            node.data["origin_name"] = node.data["output_name"]


def _is_input_node(node: Node) -> bool:
    return node.name == 'Input'


def _is_represntaion_block_node(node: Node) -> bool:
    return node.name == 'Representation Block'
