from dataclasses import dataclass
import datetime
from typing import List

from .date_utils import date_to_epoch_day, datetime_to_time_stamp_millis
from .kawa_types import Types
from typing import Union


@dataclass
class KawaScriptInput:
    dataframe: Union[str, None]
    name: str
    type: str


@dataclass
class KawaScriptOutput:
    name: str
    type: str


@dataclass
class KawaScriptParameter:
    name: str
    type: str
    default: object
    description: str
    values: list
    extensions: list


def kawa_tool(inputs: dict = None,
              outputs: dict = None,
              secrets: dict = None,
              parameters: dict = None,
              description: str = None,
              **kwargs):
    def decorator(func):
        func.inputs = convert_inputs(inputs or {})
        func.outputs = convert_outputs(outputs or {})
        func.parameters = convert_parameters(parameters or {})
        func.secrets = secrets or {}
        func.description = description
        return func

    return decorator


def convert_inputs(dic: dict):
    if len(dic) == 0:
        return []
    first_value = next(iter(dic.values()))
    if isinstance(first_value, dict):
        converted_inputs = []
        for dataframe, columns in dic.items():
            converted_inputs.extend(
                [KawaScriptInput(dataframe=dataframe, name=k, type=python_type_to_kawa_type(v, 'input', k))
                 for k, v in columns.items()]
            )
        return converted_inputs
    else:
        return [KawaScriptInput(dataframe=None, name=k, type=python_type_to_kawa_type(v, 'input', k))
                for k, v in dic.items()]


def convert_outputs(dic: dict):
    return [KawaScriptOutput(name=k, type=python_type_to_kawa_type(v, 'output', k))
            for k, v in dic.items()]


def convert_parameters(dic: dict):
    return [extract_param(k, d) for k, d in dic.items()]


def python_type_to_kawa_type(python_type, parameter_category, parameter_name):
    if not python_type:
        raise Exception(f'The type is missing for the following {parameter_category}: {parameter_name}')
    if python_type == str:
        return Types.TEXT
    if python_type == float:
        return Types.DECIMAL
    if python_type == datetime.date:
        return Types.DATE
    if python_type == datetime.datetime:
        return Types.DATE_TIME
    if python_type == bool:
        return Types.BOOLEAN
    if python_type == list[float] or python_type == List[float]:
        return Types.LIST_OF_DECIMALS
    if python_type == list[str] or python_type == List[str]:
        return Types.LIST_OF_TEXTS

    raise Exception(f'The type {python_type} used for {parameter_category}: {parameter_name} is not available')


def extract_param(param_name, type_default_value_dict) -> KawaScriptParameter:
    extensions = type_default_value_dict.get('extensions', [])
    description = type_default_value_dict.get('description', '')
    if extensions:
        return KawaScriptParameter(name=param_name,
                                   type=Types.TEXT,
                                   default=None,
                                   description=description,
                                   values=[],
                                   extensions=extensions)

    kawa_type = python_type_to_kawa_type(type_default_value_dict.get('type'), 'parameter', param_name)
    value = parse_default_value(type_default_value_dict.get('default'), kawa_type)
    values = type_default_value_dict.get('values', [])
    if not isinstance(values, list):
        raise Exception('values should be a list')

    return KawaScriptParameter(name=param_name,
                               type=kawa_type,
                               default=value,
                               description=description,
                               values=list(map(lambda x: parse_default_value(x, kawa_type), values)),
                               extensions=[])


def parse_default_value(value, kawa_type):
    if value is None:
        return value
    if kawa_type == Types.DATE:
        if isinstance(value, datetime.date):
            return date_to_epoch_day(value)
        return date_to_epoch_day(datetime.date.fromisoformat(value))
    if kawa_type == Types.DATE_TIME:
        if isinstance(value, datetime.datetime):
            return datetime_to_time_stamp_millis(value)
        return datetime_to_time_stamp_millis(datetime.datetime.fromisoformat(value))
    return value
