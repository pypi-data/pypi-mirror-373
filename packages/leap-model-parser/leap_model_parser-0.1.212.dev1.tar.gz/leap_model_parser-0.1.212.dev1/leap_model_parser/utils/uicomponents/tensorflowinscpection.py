import json
import os
from typing import List, Optional, Callable, Any

import yaml
from leap_model_parser.utils.layerpedia.layerpedia import Layerpedia
from leap_model_parser.utils.tlinspection.leapinspection import LeapInspect
from copy import deepcopy


class TensorFlowInspection(LeapInspect):

    def __init__(self):
        file_path = os.path.dirname(os.path.abspath(__file__))
        with open(f'{file_path}/ui_components_config.yaml') as f:
            self.yaml_conf = yaml.load(f, Loader=yaml.FullLoader)
        self.ignores = self.yaml_conf['ignores']
        self.args = self.yaml_conf['args']
        self.group_type = self.yaml_conf['group_type']

    def get_function_args(self, func):
        _args = []
        args = LeapInspect.get_function_args(func)
        for arg in args.values():
            arg_name = arg['name']
            default_val = arg['default_val']
            if arg_name in self.ignores['args_ignore']:
                continue

            is_tuple = arg.get('type') == 'tuple' and type(arg.get('default_val')) is tuple
            is_number = (arg.get('type') == 'float' or arg.get('type') == 'int') and isinstance(default_val, (int, float))
            if is_tuple or is_number:
                _args.append(arg)
                continue

            if arg_name in list(self.args['arg_group'].keys()):
                arg['type'] = 'select'
                arg['values'] = self.args['arg_values'][self.args['arg_group'][arg_name]]
                arg['isdefault'] = False
                if default_val is not None:
                    arg['isdefault'] = True
                    arg['default_val'] = default_val

            if arg_name in list(self.args['overides'].keys()):
                arg['type'] = self.args['overides'][arg_name]['type']
                arg['isdefault'] = self.args['overides'][arg_name]['isdefault']
                if arg['isdefault']:
                    override_def = self.args['overides'][arg_name]['default_val']
                    if default_val is not None and override_def != default_val:
                        raise "Override_def is not as argument default in class name: {}, argument name: {} ({} =! {})".format(
                            func, arg_name, default_val, override_def)
                    arg['default_val'] = override_def
            _args.append(arg)
        return _args

    def filter_node(self, node):
        return node['name'] in self.ignores['clsignore']

    def get_filled_group_values(self, node_type: str, class_pointer: Callable[..., Any]) -> dict:
        if node_type == 'customonnxlayer':
            class_code = class_pointer.__dict__['call'].__code__
            var_names = class_code.co_varnames
            arg_names = var_names[1:class_code.co_argcount]  # remove self
            if len(arg_names) == 1:
                return self.group_type[node_type]
            else:
                config_dict = deepcopy(self.group_type[node_type])
                inputs_list = config_dict['inputs_data']['inputs']
                for arg in arg_names[1:]:
                    inputs_list.append(
                        {'name': f'{arg}',
                         'approval_connection': ['Input', 'Dataset', 'Layer', 'CustomLayer']}
                    )
                return config_dict
        else:
            return self.group_type[node_type]

    def inspect_lib(self, lib):
        # TODO: extract only classes and not aliases
        classes = LeapInspect.get_classes(lib, self.ignores['lib_ignore'])
        nodes = []
        for node_cls in classes:
            if self.filter_node(node_cls):
                continue
            node = {
                'name': node_cls['name'],
                'parents': node_cls['parents'],
                'properties': self.get_function_args(node_cls['class']),
                'options': self.query_layerpedia_options(node_cls['name'])
            }
            shape_rank = self.query_layerpedia_shape_rank(node_cls['name'])
            if shape_rank:
                node['shape_rank'] = shape_rank
            enable_bigger_input_rank = self.query_layerpedia_enable_bigger_input_rank(
                node_cls['name'])
            if enable_bigger_input_rank:
                node['enable_bigger_input_rank'] = enable_bigger_input_rank
            template_node = {}
            for d in [*node_cls['parents'], node['name']]:
                if d in self.group_type:
                    template_node = {**template_node, **self.get_filled_group_values(d, node_cls['class'])}
            node = {**template_node, **node}
            if 'hash' in node and not self.query_layerpedia_is_trainable(node_cls['name']):
                node.pop('hash')
            nodes.append(node)
        return nodes

    def inspect(self, dist: str) -> List[dict]:
        from keras import layers as tf_layers  # type: ignore
        from keras import losses as tf_losses  # type: ignore
        import tensorflow.keras.optimizers as keras_optimizers  # type: ignore
        from onnx2kerastl import customonnxlayer  # type: ignore

        libs = [tf_layers, tf_losses, keras_optimizers, customonnxlayer]
        tofile = []
        for lib in libs:
            nodes = self.inspect_lib(lib)
            tofile.extend(nodes)
        tofile.extend(self.yaml_conf['nodes'])
        with open(f'{dist}ui_components.json', 'w') as outfile:
            json.dump(tofile, outfile, indent=4)
        return tofile

    def query_layerpedia_shape_rank(self, layer_name):
        layer_knowledge = Layerpedia.get_layer_knowledge(layer_name)
        if layer_knowledge is None:
            return None
        rank = layer_knowledge.get('rank')
        return rank

    def query_layerpedia_enable_bigger_input_rank(self, layer_name) -> Optional[bool]:
        layer_knowledge = Layerpedia.get_layer_knowledge(layer_name)
        return layer_knowledge.get('enable_bigger_input_rank') if layer_knowledge else None

    def query_layerpedia_is_trainable(self, layer_name) -> Optional[bool]:
        layer_knowledge = Layerpedia.get_layer_knowledge(layer_name)
        return layer_knowledge.get('is_trainable') if layer_knowledge else None

    def query_layerpedia_options(self, layer_name):
        layer_knowledge = Layerpedia.get_layer_knowledge(layer_name)
        if layer_knowledge is None:
            return None
        layer_options = {
            "representation_block": False,
            "layer_inspection": False
        }

        if layer_knowledge['is_trainable']:
            layer_options['representation_block'] = True
            layer_options['layer_inspection'] = True

        return layer_options


if __name__ == '__main__':
    tf_inspection = TensorFlowInspection()
    tf_inspection.inspect("")
