import javacoder.utils.converter as cv
from javacoder.utils.log import *


def convert_class_fields_to_db_ddl_builder(table_name: str, *default_ddl_columns: tuple):
    ddl_template = "create table {} (\nddl_column_template\n);".format(table_name)

    def converter(class_fields: list):
        ddl_columns = ['\t'.join(c) for c in default_ddl_columns]
        ddl_column_template = '''{}\t{}\t{}'''
        for i in class_fields:
            ddl_columns.append(cv.camel_to_snake(ddl_column_template.format(i[0], i[1], i[2])))
        return ddl_template.replace('ddl_column_template', ',\n'.join(ddl_columns))

    return converter


def convert_jpa_entity_to_ddl(op):
    table_name = ''
    for annotation in op.class_cursor.annotations:
        if annotation.name == 'Table':
            if type(annotation.element) in (set, list, tuple):
                for element in annotation.element:
                    if type(element).__name__ == 'ElementValuePair' and element.name == 'name':
                        table_name = element.value.value
                        break
            else:
                table_name = annotation.element.value.value
            break

    builder = convert_class_fields_to_db_ddl_builder(table_name.strip('"'))
    return builder(class_fields=get_jpa_entity_columns(op))


def get_jpa_entity_columns(op):
    rst = []
    for field in op.get_fields():
        column_define = convert_jpa_annotation_column_define(field)
        if column_define:
            rst.append(column_define)

    if op.class_cursor.extends:
        if type(op.class_cursor.extends).__name__ == 'ReferenceType':
            pp = cv.get_first_element(op.plugins, lambda p: type(p).__name__ == 'ProjectPlugin')
            e = cv.get_first_element(op.class_tree.imports,
                                     lambda i: str(i.path).endswith(op.class_cursor.extends.name))
            if pp:
                e_op = pp.get_class_operator(e.path)
                for cd in get_jpa_entity_columns(e_op):
                    rst.append(cd)
            else:
                warning("the columns from extend class not found.")
    return rst


def convert_jpa_annotation_column_define(field):
    transient_annotation = cv.get_first_element(field.annotations,
                                                lambda a: a.name in ('Transient', 'Formula', 'OneToMany', 'ManyToMany'))
    if transient_annotation or field.declarators[0].name == 'serialVersionUID':
        return None
    column_annotation = cv.get_first_element(field.annotations, lambda a: a.name in ('Column', 'JoinColumn'))
    field_name = field.declarators[0].name
    column_name = None
    column_type = None
    column_type_length = 128
    column_remark = []
    if column_annotation:
        if type(column_annotation.element) in (set, list, tuple):
            name_define = cv.get_first_element(column_annotation.element, lambda e: e.name == 'name')
            if name_define:
                column_name = name_define.value.value
            column_define = cv.get_first_element(column_annotation.element, lambda e: e.name == 'columnDefinition')
            if column_define:
                for i, define in enumerate(str(column_define.value.value).strip('"').split(' ')):
                    if i == 0:
                        column_type = define
                    else:
                        column_remark.append(define)
            column_length_define = cv.get_first_element(column_annotation.element, lambda e: e.name == 'length')
            if column_length_define:
                column_type_length = int(column_length_define.value.value)
            column_null_define = cv.get_first_element(column_annotation.element, lambda e: e.name == 'nullable')
            if column_null_define and 'null' not in column_remark:
                if column_null_define.value.value == 'false':
                    column_remark.append('not')
                column_remark.append('null')
        elif column_annotation.element:
            column_name = column_annotation.element.value.value

    enum_column_annotation = cv.get_first_element(field.annotations, lambda a: a.name == 'Enumerated')
    if enum_column_annotation and not column_type:
        if enum_column_annotation.element and enum_column_annotation.element.member == 'STRING':
            column_type = 'varchar({})'.format(column_type_length)
        else:
            column_type = 'int'

    if not column_type:
        if field.type.name == 'String':
            column_type = 'varchar({})'.format(column_type_length)
        elif field.type.name in ('Integer', 'Long'):
            column_type = 'int'
        elif field.type.name in ('Instant', 'Date', 'LocalDate', 'LocalDateTime'):
            column_type = 'datetime(6)'
        else:
            column_type = 'varchar({})'.format(column_type_length)
            warning(f"cannot convert field {field.declarators[0].name} of type {field.type.name},"
                    f" using default type {column_type}")

    id_annotation = cv.get_first_element(field.annotations, lambda a: a.name == 'Id')
    if id_annotation:
        column_remark.append('not null primary key')
    if not column_name:
        column_name = cv.camel_to_snake(field_name)

    if len(column_remark) == 0:
        column_remark.append('default null')

    return column_name.strip('"'), column_type, ' '.join(column_remark)
