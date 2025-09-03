import typing
from dataclasses import dataclass
import datetime

import xml.etree.ElementTree as ET


@dataclass
class TreeNode:
    id: str
    children: list['TreeNode']
    name: typing.Optional[str] = None
    value: typing.Optional[typing.Union[str, int, float, bool, datetime.datetime, datetime.date]] = None
    to_xml_func: any = None
    column_index = {}

    def to_xml(self, sheet, parameters):

        column_index = {}
        parameter_index = {}

        for column in sheet.get('indicatorColumns', []) + sheet.get('computedColumns', []):
            column_index[column.get('displayInformation').get('displayName')] = column.get('columnId')

        for parameter in parameters:
            parameter_index[parameter.get('name')] = parameter.get('id')

        self._inject_column_ids(column_index, parameter_index)
        raw_xml = '<xml>' + self._to_xml() + '</xml>'
        element = ET.XML(raw_xml)
        ET.indent(element)
        return ET.tostring(element, encoding='unicode')

    def alias(self, alias: str):
        self.name = alias
        return self

    def _inject_column_ids(self,
                           column_index: dict[str, str],
                           parameter_index: dict[str, str]):
        for child in self.children:
            # In-place mutate the identifiers
            if child.id == 'column_identifier':
                column_name = child.value.strip()
                column_id = column_index.get(column_name)
                if not column_id:
                    raise ValueError(f'The column with name "{column_name}" was not found')
                child.value = column_id
            elif child.id == 'parameter_identifier':
                parameter_name = child.value.strip()
                parameter_id = parameter_index.get(parameter_name)
                if not parameter_id:
                    raise ValueError(f'The parameter with name "{parameter_name}" was not found')
                child.value = parameter_id
            else:
                child._inject_column_ids(column_index, parameter_index)

    def _to_xml(self):
        node = self
        return self.to_xml_func(node)

    def binary_expression_xml(self):
        return f'''
        <block type="BINARY_EXPRESSION">
            <field name="operation_id">{self.id}</field>
            <value name="left">{self.children[0]._to_xml()}</value>
            <value name="right">{self.children[1]._to_xml()}</value>
        </block>'''

    def call_expression_xml(self):
        inputs = []
        input_counter = 0
        for child in self.children:
            input_counter += 1
            inputs.append(f'<value name="input{input_counter}">{child._to_xml()}</value>')

        inputs_xml = '\n'.join(inputs)
        return f'''
            <block type="CALL_EXPRESSION">
                <field name="operation_id">{self.id}</field>
                {inputs_xml}
            </block>'''

    def literal_xml(self):
        if isinstance(self.value, str):
            kawa_type = 'text'
        elif isinstance(self.value, float):
            kawa_type = 'decimal'
        elif isinstance(self.value, bool):
            kawa_type = 'boolean'
        elif isinstance(self.value, datetime.date):
            kawa_type = 'date'
        else:
            kawa_type = 'integer'

        if kawa_type == 'date':
            return f'''
            <block type="CALL_EXPRESSION">
              <field name="operation_id">PARSE_ISO_DATE</field>
              <value name="input1">
                 <block type="LITERAL">
                    <field name="type">text</field>
                    <field name="value">{self.value}</field>
                 </block>
              </value>
           </block>
           '''

        else:
            return f'''
                <block type="LITERAL">
                    <field name="type">{kawa_type}</field>
                    <field name="value">{self.value}</field>
                </block>
            '''

    def identifier_xml(self):
        return f'''
              <block type="IDENTIFIER">
                <field name="type">text</field>
                <field name="reference">{self.value}</field>
            </block>
           '''


def binary_expression(operation_id: str, node1: TreeNode, node2: TreeNode) -> TreeNode:
    return TreeNode(
        id=operation_id,
        children=[node1, node2],
        to_xml_func=lambda node: node.binary_expression_xml(),
    )


def call_expression(operation_id: str, children: list[TreeNode]) -> TreeNode:
    return TreeNode(
        id=operation_id,
        children=children,
        to_xml_func=lambda node: node.call_expression_xml(),
    )


def val(value: typing.Union[str , int , float , bool , datetime.datetime , datetime.date]) -> TreeNode:
    if value == ' ':
        return space()
    else:
        return TreeNode(
            id='val',
            children=[],
            value=value,
            to_xml_func=lambda node: node.literal_xml(),
        )


def col_identifier(identifier_value: str) -> TreeNode:
    return TreeNode(
        id='column_identifier',
        children=[],
        value=identifier_value,
        to_xml_func=lambda node: node.identifier_xml(),
    )


def param_identifier(identifier_value: str) -> TreeNode:
    return TreeNode(
        id='parameter_identifier',
        children=[],
        value=identifier_value,
        to_xml_func=lambda node: node.identifier_xml(),
    )


def col(column_name: str): return call_expression('COLUMN', [col_identifier(column_name)])


def param(parameter_name: str): return call_expression('PARAMETER', [param_identifier(parameter_name)])


def today(): return call_expression('TODAY', [])


def now(): return call_expression('NOW', [])


def length(input_node: TreeNode): return call_expression('LEN', [input_node])


def first(input_node: TreeNode): return call_expression('FIRST', [input_node])


def total(input_node: TreeNode): return call_expression('SUM', [input_node])


def average(input_node: TreeNode): return call_expression('AVG', [input_node])


def str_(input_node: TreeNode): return call_expression('TEXT', [input_node])


def extract(input_text: TreeNode, regexp: TreeNode):
    return call_expression('EXTRACT', [input_text, regexp])


def add(node1: TreeNode, node2: TreeNode): return binary_expression('ADDITION', node1, node2)


def sub(node1: TreeNode, node2: TreeNode): return binary_expression('SUBTRACTION', node1, node2)


def mul(node1: TreeNode, node2: TreeNode): return binary_expression('MULTIPLICATION', node1, node2)


def div(node1: TreeNode, node2: TreeNode): return binary_expression('DIVISION', node1, node2)


def ge(node1: TreeNode, node2: TreeNode): return binary_expression('GREATER_THAN_OR_EQUAL', node1, node2)


def gt(node1: TreeNode, node2: TreeNode): return binary_expression('STRICTLY_GREATER_THAN', node1, node2)


def le(node1: TreeNode, node2: TreeNode): return binary_expression('LESSER_THAN_OR_EQUAL', node1, node2)


def lt(node1: TreeNode, node2: TreeNode): return binary_expression('STRICTLY_LESSER_THAN', node1, node2)


def eq(node1: TreeNode, node2: TreeNode): return binary_expression('EQUAL', node1, node2)


def ne(node1: TreeNode, node2: TreeNode): return binary_expression('NOT_EQUAL', node1, node2)


def space(): return call_expression('SPACE', [])


def power(node1: TreeNode, node2: TreeNode): return call_expression('POWER', [node1, node2])


def starts_with(node1: TreeNode, node2: TreeNode): return call_expression('BEGINS_WITH', [node1, node2])


def ends_with(node1: TreeNode, node2: TreeNode): return call_expression('ENDS_WITH', [node1, node2])


def contains(node1: TreeNode, node2: TreeNode): return call_expression('CONTAINS', [node1, node2])


def left(node1: TreeNode, node2: TreeNode): return call_expression('LEFT', [node1, node2])


def right(node1: TreeNode, node2: TreeNode): return call_expression('RIGHT', [node1, node2])


def find(node1: TreeNode, node2: TreeNode): return call_expression('FIND', [node1, node2])


def substring(*nodes: list[TreeNode]): return call_expression('SUBSTRING', list(nodes))


def replace_all(node1: TreeNode, node2: TreeNode, node3: TreeNode):
    return call_expression('SUBSTITUTE_ALL', [node1, node2, node3])


def replace_first(node1: TreeNode, node2: TreeNode, node3: TreeNode):
    return call_expression('SUBSTITUTE', [node1, node2, node3])


def abs_(node1: TreeNode): return call_expression('ABS', [node1])


def not_(node1: TreeNode): return call_expression('NOT', [node1])


def in_list(*nodes: list[TreeNode]): return call_expression('IN_LIST', list(nodes))


def largest(node1: TreeNode, node2: TreeNode): return call_expression('LARGEST', [node1, node2])


def smallest(node1: TreeNode, node2: TreeNode): return call_expression('SMALLEST', [node1, node2])


def empty(node1: TreeNode): return call_expression('IS_EMPTY', [node1])


def not_empty(node1: TreeNode): return call_expression('IS_NOT_EMPTY', [node1])


def lower(node1: TreeNode): return call_expression('LOWER', [node1])


def upper(node1: TreeNode): return call_expression('UPPER', [node1])


def trim(node1: TreeNode): return call_expression('TRIM', [node1])


def concat(*nodes: list[TreeNode]): return call_expression('CONCAT', list(nodes))


def if_then_else(*nodes: list[TreeNode]): return call_expression('IF', list(nodes))


def or_(*nodes: list[TreeNode]): return call_expression('OR', list(nodes))


def and_(*nodes: list[TreeNode]): return call_expression('AND', list(nodes))


def adddays(node1: TreeNode, node2: TreeNode):
    return call_expression('ADD_DAYS', [node1, node2])


def datediff(node1: TreeNode, node2: TreeNode):
    return call_expression('DATETIME_DIFF', [node1, node2, val('D')])


def datetimediff(node1: TreeNode, node2: TreeNode):
    return call_expression('DATETIME_DIFF', [node1, node2, val('s')])


def date(node1: TreeNode):
    return call_expression('DATE', [node1])


def day_of_year(node1: TreeNode):
    return call_expression('DAY_OF_YEAR', [node1])


def year(node1: TreeNode):
    return call_expression('YEAR', [node1])


def month(node1: TreeNode):
    return call_expression('MONTH', [node1])


def week(node1: TreeNode):
    return call_expression('WEEK', [node1])


def weekday(node1: TreeNode):
    return call_expression('WEEKDAY', [node1])
