import sys
import os
import json
import importlib

from stadle.lib.util.states import BaseModelConvFormat
from stadle.lib.entity.model import BaseModel

def upload_bm_from_config(config_path):
    with open(config_path) as f:
        config_dict = json.load(f)

    model_dict = config_dict['base_model']
    name = model_dict['model_name']
    model_module = model_dict['model_fn_src']
    model_func = model_dict['model_fn']
    type = model_dict['model_format']

    if ('model_fn_args' in model_dict):
        model_func_args = model_dict['model_fn_args']
    else:
        model_func_args = None

    base_model = get_base_model(name, model_module, model_func, model_func_args, type)

    send_base_model(base_model, config_path)

# def module_from_file(module_name, file_path):
#     spec = importlib.util.spec_from_file_location(module_name, file_path)
#     module = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(module)
#     return module

def get_format_from_str(format_str):
    lower_str = format_str.lower()
    if (lower_str == 'pytorch'):
        return BaseModelConvFormat.pytorch_format
    elif (lower_str == 'keras'):
        return BaseModelConvFormat.keras_format
    elif (lower_str == 'tf' or lower_str == 'tensorflow'):
        return BaseModelConvFormat.tensorflow_format
    else:
        raise ValueError(f"Invalid model type {format_str} provided")

def get_base_model(name, model_module, model_func, model_func_args, type):
    sys.path.insert(0, '')
    model_module = importlib.import_module(model_module)
    
    if (model_func_args is not None):
        model_object = getattr(model_module, model_func)(**model_func_args)
    else:
        model_object = getattr(model_module, model_func)()

    return BaseModel(name, model_object, get_format_from_str(type))

def send_base_model(base_model, config_path):
    from stadle import AdminAgent

    admin_agent = AdminAgent(base_model=base_model, config_file=config_path, agent_name='admin_agent')
    admin_agent.preload()
    admin_agent.initialize()