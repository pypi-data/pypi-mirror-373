from enum import Enum
from typing import Optional, Dict, Any, List

from code_loader.contract.mapping import NodeConnection, NodeMappingType, NodeMapping  # type: ignore
from keras import Model  # type: ignore

from leap_model_parser.contract.graph import Node as Node, OutputData, ConnectionOutput, ConnectionInput, InputData



class LeapGraphEditor:
    def __init__(self, model_graph: Dict[str, Node], keras_model: Model):
        self.model_graph = model_graph
        self.keras_model = keras_model

        node_ids_as_int = [int(node_id) for node_id in model_graph.keys()]
        self._next_node_id_index = max(node_ids_as_int) + 1


    def add_connections_to_graph(self, connections: List[NodeConnection]):
        connections = self._replace_prediction_node_name_with_correct_name(connections)
        for connection in connections:
            self._add_node_connection_to_graph(connection)

    def _add_node_connection_to_graph(self, node_connection: NodeConnection):
        if node_connection.node.type == NodeMappingType.PredictionLabels:
            prediction_labels_name = node_connection.node.name
            prediction_node = list(node_connection.node_inputs.values())[0]
            prediction_mapping_node = self._find_node_by_origin_name(prediction_node.name)
            assert prediction_mapping_node is not None, \
                f"Prediction node with name {prediction_node.name} not found in model graph"
            prediction_node_id = prediction_mapping_node.id
            self.model_graph[prediction_node_id].data['prediction_type'] = prediction_labels_name
        elif node_connection.node.type == NodeMappingType.Visualizer:
            new_visualizer_node_id = self._add_visualizer_node(
                node_connection.node.name, node_connection.node.sub_type,
                node_connection.node.user_unique_name, node_connection.node.arg_names)
            for input_name, node in node_connection.node_inputs.items():
                input_node_id = self._find_or_add_input_node(node)
                self._add_connection_to_node(new_visualizer_node_id, input_name, input_node_id)
        elif node_connection.node.type == NodeMappingType.Metric:
            new_metric_node_id = self._add_metric_node(
                node_connection.node.name,
                node_connection.node.user_unique_name, node_connection.node.arg_names)
            for input_name, node in node_connection.node_inputs.items():
                input_node_id = self._find_or_add_input_node(node)
                self._add_connection_to_node(new_metric_node_id, input_name, input_node_id)
        elif node_connection.node.type in (NodeMappingType.Loss, NodeMappingType.CustomLoss):
            new_loss_node_id = self._add_loss_node(node_connection.node.name,
                                                   node_connection.node.type == NodeMappingType.CustomLoss,
                                                   node_connection.node.arg_names)
            for input_name, node in node_connection.node_inputs.items():
                input_node_id = self._find_or_add_input_node(node)
                self._add_connection_to_node(new_loss_node_id, input_name, input_node_id)
        else:
            raise Exception(f"Can't add node of type {node_connection.node.type.name}")

    def model_graph_dict(self) -> Dict[str, Any]:
        json_model_graph = {}
        for node_id, node in self.model_graph.items():
            json_model_graph[node_id] = node.__dict__

        return json_model_graph


    def _find_node_by_origin_name(self, origin_name: str) -> Optional[Node]:
        for node in self.model_graph.values():
            if node.data.get('origin_name') == origin_name:
                return node
        return None

    def _find_input_node_by_origin_name(self, origin_name: str) -> Optional[Node]:
        for node in self.model_graph.values():
            if node.data.get('original_output_name') == origin_name:
                return node
            if node.data.get('output_name') == origin_name:
                return node
        return None

    def _replace_prediction_node_name_with_correct_name(self, connections: List[NodeConnection]) -> List[NodeConnection]:
        for connection in connections:
            if connection.node_inputs is None:
                continue
            for input_name, input_node in connection.node_inputs.items():
                if 'Prediction' in input_node.type.value:
                    prediction_index = int(input_node.type.value.replace('Prediction', ''))
                    origin_name = self.keras_model.outputs[prediction_index].node.layer.name
                    input_node.name = origin_name

        return connections


    def _find_encoder_node_id(self, encoder_name: str) -> Optional[str]:
        for node_id, node_response in self.model_graph.items():
            if 'type' in node_response.data and (node_response.data['type'] in ('Input', 'GroundTruth')):
                if f'{node_id}-{encoder_name}' in node_response.outputs:
                    return node_id
        return None

    def _find_layer_node_id(self, layer_name: str) -> str:
        for node_id, node_response in self.model_graph.items():
            if 'type' in node_response.data and node_response.data['type'] == 'Layer':
                if node_response.data['origin_name'] == layer_name:
                    return node_id
        raise Exception(f"Couldn't find node for layer {layer_name}")

    def _generate_new_node_id(self) -> str:
        self._next_node_id_index += 1
        return str(self._next_node_id_index - 1)

    def _add_ground_truth_node(self, ground_truth_name: str) -> str:
        new_node_id = self._generate_new_node_id()
        ground_truth_node = Node(
            new_node_id,
            'GroundTruth',
            position=[0, 0],
            data={'name': ground_truth_name, 'output_name': ground_truth_name,
                  'type': 'GroundTruth', "selected": ground_truth_name},
            inputs={},
            outputs={
                f'{new_node_id}-{ground_truth_name}': ConnectionOutput([])
            }
        )
        self.model_graph[new_node_id] = ground_truth_node
        return new_node_id

    def _add_visualizer_node(self, visualizer_name: str, visualizer_type: str,
                             user_unique_name: str, arg_names: List[str]) -> str:
        new_node_id = self._generate_new_node_id()

        visualizer_node = Node(
            new_node_id,
            'Visualizer',
            position=[0, 0],
            data={'visualizer_name': visualizer_name, 'type': 'Visualizer',
                  'selected': visualizer_name, 'name': visualizer_name, 'visualizer_type': visualizer_type,
                  'arg_names': arg_names, "user_unique_name": user_unique_name},
            inputs={},
            outputs={})

        self.model_graph[new_node_id] = visualizer_node
        return new_node_id

    def _add_metric_node(self, metric_name: str,
                             user_unique_name: str, arg_names: List[str]) -> str:
        new_node_id = self._generate_new_node_id()

        metric_node = Node(
            new_node_id,
            'Metric',
            position=[0, 0],
            data={'metric_name': metric_name, 'type': 'Metric', 'name': metric_name,
                  'arg_names': arg_names, "user_unique_name": user_unique_name},
            inputs={},
            outputs={})

        self.model_graph[new_node_id] = metric_node
        return new_node_id

    def _add_loss_node(self, loss_name: str, is_custom_loss: bool, arg_names: Optional[List[str]]=None) -> str:
        new_node_id = self._generate_new_node_id()

        loss_type = 'CustomLoss' if is_custom_loss else 'Loss'
        loss_node_name = 'CustomLoss' if is_custom_loss else loss_name

        loss_node = Node(
            new_node_id,
            loss_node_name,
            position=[0, 0],
            data={'type': loss_type, 'selected': loss_name, 'name': loss_name},
            inputs={},
            outputs={
                f'{new_node_id}-loss': ConnectionOutput([])
            }
        )
        if arg_names is not None:
            loss_node.data['arg_names'] = arg_names


        self.model_graph[new_node_id] = loss_node
        return new_node_id

    def _get_output_name_from_node_id(self, input_node_id: str, input_name: Optional[str] = None) -> str:
        input_node_outputs_len = len(self.model_graph[input_node_id].outputs)
        if input_node_outputs_len == 0:
            output_name_to_add = f'{input_node_id}-feature_map'
            self.model_graph[input_node_id].outputs[output_name_to_add] = ConnectionOutput([])

            return output_name_to_add
        if input_node_outputs_len == 1:
            return list(self.model_graph[input_node_id].outputs.keys())[0]
        if input_name is not None:
            guessed_output_name = f'{input_node_id}-{input_name}'
            if guessed_output_name in self.model_graph[input_node_id].outputs:
                return guessed_output_name

        # todo: layers with multiple outputs
        raise Exception("Can't decide on output name")

    def _add_connection_to_node(self, node_id: str, input_name: str, input_node_id: str):
        # todo: layers with multiple outputs
        output_name = self._get_output_name_from_node_id(input_node_id, input_name)
        input_name = f'{node_id}-{input_name}'
        self.model_graph[node_id].inputs[input_name] = ConnectionInput([InputData(input_node_id, output_name)])

        output_connection = OutputData(node_id, input_name)
        self.model_graph[input_node_id].outputs[output_name].connections.append(output_connection)

    def _handle_input_node_with_index(self, input_node: NodeMapping) -> str:
        input_index = int(input_node.type.value.replace('Input', ''))
        origin_name = self.keras_model.inputs[input_index].node.layer.name
        input_node_by_origin = self._find_input_node_by_origin_name(origin_name)
        assert input_node_by_origin is not None, f"Input node with origin name {origin_name} not found in model graph"
        input_node_id = input_node_by_origin.id
        if 'original_output_name' not in self.model_graph[input_node_id].data:
            self.model_graph[input_node_id].data['original_output_name'] = self.model_graph[input_node_id].data['output_name']
        self.model_graph[input_node_id].data['output_name'] = input_node.name

        output_keys = list(self.model_graph[input_node_id].outputs.keys())
        for output_key in output_keys:
            new_output_key = f'{input_node_id}-{input_node.name}'
            if output_key == new_output_key:
                continue
            self.model_graph[input_node_id].outputs[new_output_key] = self.model_graph[input_node_id].outputs[
                output_key]
            del self.model_graph[input_node_id].outputs[output_key]
            for connection in self.model_graph[input_node_id].outputs[new_output_key].connections:
                for connection_input in self.model_graph[connection.node].inputs[connection.input].connections:
                    if connection_input.output == output_key:
                        connection_input.output = new_output_key

        return input_node_id

    def _find_or_add_input_node(self, input_node: NodeMapping) -> str:
        if input_node.type in (NodeMappingType.Input, NodeMappingType.GroundTruth):
            input_node_id = self._find_encoder_node_id(input_node.name)
            if input_node_id is None:
                if input_node.type == NodeMappingType.GroundTruth:
                    input_node_id = self._add_ground_truth_node(input_node.name)
                else:
                    raise Exception(f'Couldnt find input node name {input_node.name}')
        elif 'Input' in input_node.type.value:
            input_node_id = self._handle_input_node_with_index(input_node)
        elif input_node.type.value.startswith('Prediction'):
            node_by_origin_name = self._find_node_by_origin_name(input_node.name)
            assert node_by_origin_name is not None, \
                f"Prediction node with name {input_node.name} not found in model graph"
            input_node_id = node_by_origin_name.id
        else:
            input_node_id = self._find_layer_node_id(input_node.name)

        return input_node_id

    def _get_all_loss_node_ids(self):
        loss_node_ids = []
        for node_id, node_response in self.model_graph.items():
            if 'type' in node_response.data and node_response.data['type'] in ('CustomLoss', 'Loss'):
                loss_node_ids.append(node_id)
        return loss_node_ids

    @staticmethod
    def _convert_dataclass_to_json_dict(_dataclass):
        if isinstance(_dataclass, Enum):
            return _dataclass.name
        if hasattr(_dataclass, '__dict__'):
            return {
                key: LeapGraphEditor._convert_dataclass_to_json_dict(_dataclass.__dict__[key])
                for key in _dataclass.__dict__
            }
        if isinstance(_dataclass, list):
            return [
                LeapGraphEditor._convert_dataclass_to_json_dict(element)
                for element in _dataclass
            ]
        return _dataclass
