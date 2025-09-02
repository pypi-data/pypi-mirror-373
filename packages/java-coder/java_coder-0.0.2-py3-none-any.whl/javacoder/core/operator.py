import functools
import os
from os import path

from javalang.tree import *

from javacoder.utils.converter import get_first_element
from javacoder.utils.loader import load_content
from javacoder.core.java_generator import JavaCodeGenerator
from javalang import parse
from javacoder.utils.log import *


def pre_notify_plugins(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        op = args[0]
        if isinstance(op, ObjectOperator):
            op.invoke_plugins(invoke_method=func.__name__, invoke_operator=op)
        return func(*args, **kwargs)

    return wrapper


class ObjectOperator:
    def __init__(self, class_path: str = '', class_name: str = ''):
        self.method_cursor = None
        self.field_cursor = None
        self.file_content = None
        self.class_cursor = None
        self.class_tree = None
        self.plugins = []
        self.file_path = None
        if class_path is not None and len(class_path) > 0:
            if path.exists(class_path) and path.isfile(class_path):
                self.file_path = class_path
                self.file_name = path.basename(class_path)
                self.new_file = False
            else:
                self.new_file = True
        else:
            self.new_file = True

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def invoke_plugins(self, **kwargs):
        for p in self.plugins:
            p.invoke(**kwargs)

    def set_package_name_by_file_path(self, file_path: str):
        if os.sep.join(['src', 'main', 'java']) in file_path:
            package_path = self.file_path.split(os.sep.join(['src', 'main', 'java']))[-1].split(os.sep)
            if self.class_tree:
                self.class_tree.package = PackageDeclaration(
                    name='.'.join(list(filter(lambda x: x != '', package_path))))
            else:
                error("failed set package name only if generate class_tree before")

    def set_package_name(self, package_name):
        if self.class_tree:
            self.class_tree.package = PackageDeclaration(name=package_name)

    def format(self):
        pass

    def check_class(self):
        if self.file_path is None:
            raise Exception("save_path_cannot_be_none")
        if self.file_name is None:
            raise Exception("file_name_cannot_be_none")

    @pre_notify_plugins
    def preview_class(self):
        self.format()
        gen = JavaCodeGenerator()
        gen.generate(self.class_tree)
        info('previewed class: \n---{}---\n{}\n---end---'.format(self.file_name, gen.get_code()))

    @pre_notify_plugins
    def save(self):
        self.check_class()
        self.format()
        gen = JavaCodeGenerator()
        gen.generate(self.class_tree)
        self.file_content = gen.get_code()
        if self.new_file:
            if path.isdir(self.file_path):
                if self.file_path.endswith(os.sep):
                    file_path = self.file_path + self.file_name
                else:
                    file_path = self.file_path + os.sep + self.file_name
            else:
                file_path = self.file_path
        else:
            file_path = self.file_path
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.file_content)
        info("save java file success.")

    def set_document(self, document):
        if self.class_cursor:
            self.class_cursor.documentation = Documented(documentation=document)
        else:
            error("failed add document only if set class_cursor before")

    def add_annotation(self, annotation_name, **kwargs):
        if self.class_cursor:
            if not self.class_cursor.annotations:
                self.class_cursor.annotations = []
            self.class_cursor.annotations.append(
                Annotation(name=annotation_name,
                           element=[
                               ElementValuePair(name=key,
                                                value=Literal(value=value) if type(value) in (
                                                    str, int, bool) else value)
                               for
                               key, value
                               in
                               kwargs.items()]))
        else:
            error("failed add annotation only if set class_cursor before")

    def add_import(self, import_path, static=False, wildcard=False):
        if self.class_tree:
            if not self.class_tree.imports:
                self.class_tree.imports = []
            self.class_tree.imports.append(Import(path=import_path, static=static, wildcard=wildcard))
        else:
            error("failed add imports only if generate class_tree before")

    def get_import(self):
        if self.class_tree:
            return [imported.path for imported in self.class_tree.imports]
        else:
            return []

    def filter(self, filter_func, mapper=None):
        if self.class_tree:
            for paths, node in self.class_tree:
                if filter_func(paths, node):
                    if mapper:
                        rst = mapper(node)
                        if rst:
                            yield rst
                    else:
                        yield node


class InterfaceOperator(ObjectOperator):
    def __init__(self, interface_path: str = '', name: str = ''):
        super().__init__(interface_path, name)
        if self.new_file:
            self.__create_default_interface(name=name, file_path=interface_path)
        else:
            self.file_content = load_content(interface_path)
            self.class_tree = parse.parse(self.file_content)
            self.class_cursor = self.class_tree.types[0]

    def __create_default_interface(self, name, file_path):
        self.class_tree = CompilationUnit()
        self.class_tree.types = []
        self.class_tree.imports = []
        if len(name) > 0:
            self.__create_interface(name)
            self.file_name = name + '.java'
            self.class_cursor = self.class_tree.types[0]
        if len(file_path) > 0:
            self.file_path = file_path
            self.set_package_name_by_file_path(file_path)

    def __create_interface(self, name):
        modifier = set()
        modifier.add('public')
        declaration = InterfaceDeclaration(modifiers=modifier, name=name, body=[])
        self.class_tree.types.append(declaration)
        return declaration

    def get_method_cursor(self):
        if self.method_cursor is None:
            self.method_cursor = MethodOperator(self)
        return self.method_cursor

    def add_method(self, name):
        self.get_method_cursor().add_public_method(name)

    def add_extend_interface(self, extend_interface, *template_class):
        if self.class_cursor:
            if not self.class_cursor.extends:
                self.class_cursor.extends = []
            if template_class:
                self.class_cursor.extends.append(ReferenceType(name=extend_interface, arguments=[
                    ReferenceType(name=tn) for tn in template_class
                ]))
            else:
                self.class_cursor.extends.append(ReferenceType(name=extend_interface, ))


class AnnotationOperator(ObjectOperator):
    def __init__(self, annotation_path: str = '', name: str = '', target: list = []):
        super().__init__(annotation_path, name)
        if self.new_file:
            self.__create_default_annotation(name=name, file_path=annotation_path, annotation_type=target)
        else:
            self.file_content = load_content(annotation_path)
            self.class_tree = parse.parse(self.file_content)
            self.class_cursor = self.class_tree.types[0]

    def __create_default_annotation(self, name, file_path, annotation_type):
        self.class_tree = CompilationUnit()
        self.class_tree.types = []
        self.class_tree.imports = []
        if len(name) > 0:
            self.__create_annotation(name)
            self.file_name = name + '.java'
            self.class_cursor = self.class_tree.types[0]
            self.add_annotation('Retention', value=MemberReference(qualifier=ReferenceType(name='RetentionPolicy'),
                                                                   member='RUNTIME'))
            target_types = []
            if 'class' in annotation_type:
                target_types.append(MemberReference(qualifier=ReferenceType(name='ElementType'),
                                                    member='TYPE'))
            if 'field' in annotation_type:
                target_types.append(MemberReference(qualifier=ReferenceType(name='ElementType'),
                                                    member='FIELD'))
            if 'method' in annotation_type:
                target_types.append(MemberReference(qualifier=ReferenceType(name='ElementType'),
                                                    member='METHOD'))
            if 'parameter' in annotation_type:
                target_types.append(MemberReference(qualifier=ReferenceType(name='ElementType'),
                                                    member='PARAMETER'))
            if len(target_types) > 0:
                self.add_annotation('Type', value=ArrayInitializer(initializers=target_types))
            self.add_annotation('Documented')
            self.add_annotation('Inherited')
        if len(file_path) > 0:
            self.file_path = file_path
            self.set_package_name_by_file_path(file_path)

    def __create_annotation(self, name):
        modifier = set()
        modifier.add('public')
        declaration = AnnotationDeclaration(modifiers=modifier, name=name, body=[])
        self.class_tree.types.append(declaration)
        return declaration

    def method(self, name, annotation_type, default):
        if self.class_cursor:
            if not self.class_cursor.body:
                self.class_cursor.body = []
            annotation_parameter = AnnotationMethod(name=name, return_type=ReferenceType(name=annotation_type),
                                                    default=default)
            self.class_cursor.body.append(annotation_parameter)


class EnumOperator(ObjectOperator):
    def __init__(self, enum_path: str = '', name: str = ''):
        super().__init__(enum_path, name)
        if self.new_file:
            self.__create_default_enum(name=name, file_path=enum_path)
            self.enum_body = None
        else:
            self.file_content = load_content(enum_path)
            self.class_tree = parse.parse(self.file_content)
            self.class_cursor = self.class_tree.types[0]
            self.enum_body = get_first_element(self.class_cursor.body, lambda f: type(f) == EnumBody)

    def __create_default_enum(self, name, file_path):
        self.class_tree = CompilationUnit()
        self.class_tree.types = []
        self.class_tree.imports = []
        if len(name) > 0:
            self.__create_enum(name)
            self.file_name = name + '.java'
            self.class_cursor = self.class_tree.types[0]
        if len(file_path) > 0:
            self.file_path = file_path
            self.set_package_name_by_file_path(file_path)

    def __create_enum(self, name):
        modifier = set()
        modifier.add('public')
        declaration = EnumDeclaration(modifiers=modifier, name=name, body=[])
        self.class_tree.types.append(declaration)
        return declaration

    def enumerate(self, name):
        if self.class_cursor:
            if not self.class_cursor.body:
                self.class_cursor.body = []
            if not self.enum_body:
                self.enum_body = EnumBody(constants=[])
                self.class_cursor.body.append(self.enum_body)
            enum = EnumConstantDeclaration(name=name)
            self.enum_body.constants.append(enum)

    def get_method_cursor(self):
        if self.method_cursor is None:
            self.method_cursor = MethodOperator(self)
        return self.method_cursor


class ClassOperator(ObjectOperator):
    def __init__(self, class_path: str = '', class_name: str = ''):
        super().__init__(class_path, class_name)
        if self.new_file:
            self.__create_default_class(name=class_name, file_path=class_path)
        else:
            self.file_content = load_content(class_path)
            self.class_tree = parse.parse(self.file_content)
            self.class_cursor = self.class_tree.types[0]

    def __create_default_class(self, name: str = '', file_path: str = ''):
        self.class_tree = CompilationUnit()
        self.class_tree.types = []
        self.class_tree.imports = []
        if len(name) > 0:
            self.add_class(name)
            self.file_name = name + '.java'
            self.class_cursor = self.class_tree.types[0]
        if len(file_path) > 0:
            self.file_path = file_path
            self.set_package_name_by_file_path(file_path)

    def add_class(self, class_name: str):
        modifier = set()
        modifier.add('public')
        class_declaration = ClassDeclaration(modifiers=modifier, name=class_name, body=[])
        self.class_tree.types.append(class_declaration)
        return class_declaration

    def get_fields(self):
        if len(self.class_tree.types) == 1:
            # if this class file only have one class declare
            class_declare = self.class_tree.types[0]
            fields = []
            for item in class_declare.body:
                if type(item) == FieldDeclaration:
                    fields.append(item)
            return fields

    def format(self):
        self.class_cursor.body = sorted(self.class_cursor.body, key=get_class_member_type_order)

    def add_private_string(self, field_name, field_value=''):
        self.get_field_cursor().add_private_string_field(field_name, field_value)

    def add_getter_and_setter(self, field_name):
        self.get_method_cursor().add_getter_and_setter(field_name)

    def add_field_annotation(self, field_name, annotation, **kwargs):
        self.get_field_cursor().add_field_annotation(field_name, annotation, **kwargs)

    def get_field_cursor(self):
        if self.field_cursor is None:
            self.field_cursor = FieldOperator(self)
        return self.field_cursor

    def get_method_cursor(self):
        if self.method_cursor is None:
            self.method_cursor = MethodOperator(self)
        return self.method_cursor

    def set_extend_class(self, extend, *template_class):
        if self.class_cursor is not None:
            if template_class:
                self.class_cursor.extends = ReferenceType(name=extend, arguments=[
                    ReferenceType(name=tn) for tn in template_class
                ])
            else:
                self.class_cursor.extends = ReferenceType(name=extend)

    def add_implement(self, implement_class):
        if self.class_cursor is not None:
            if self.class_cursor.implements is None:
                self.class_cursor.implements = []
            self.class_cursor.implements.append(ReferenceType(name=implement_class))


class ClassMemberOperator:
    def __init__(self, class_operator):
        self.class_operator = class_operator
        if self.class_operator.class_cursor is None:
            raise Exception("please select class before")
        if 'type_parameters' in self.class_operator.class_cursor.attrs and \
                self.class_operator.class_cursor.type_parameters is None:
            self.class_operator.class_cursor.type_parameters = []
        self.field_cursor = self.class_operator.class_cursor.body

    def add_field(self, modifiers, field_type: ReferenceType, declarators: list):
        self.field_cursor.append(FieldDeclaration(modifiers=modifiers, type=field_type, declarators=declarators))

    def get_field(self, field_name):
        for item in self.field_cursor:
            if type(item) == FieldDeclaration and field_name in [d.name for d in item.declarators]:
                return item
        return None

    def add_method(self, modifiers, return_type: ReferenceType, name: str, parameters=None, body=None):
        if body is None:
            body = []
        if parameters is None:
            parameters = []
        method_declaration = MethodDeclaration(modifiers=modifiers, return_type=return_type, name=name,
                                               parameters=parameters, body=body)
        self.field_cursor.append(method_declaration)

    def add_constructor(self, modifiers, parameters=None, body=None):
        if body is None:
            body = []
        if parameters is None:
            parameters = []
        constructor_declaration = ConstructorDeclaration(modifiers=modifiers,
                                                         name=self.class_operator.class_cursor.name,
                                                         parameters=parameters, body=body)
        self.field_cursor.append(constructor_declaration)


class MethodOperator(ClassMemberOperator):
    def __init__(self, class_operator):
        super(MethodOperator, self).__init__(class_operator)

    def add_getter_and_setter(self, field_name):
        self.add_getter(field_name)
        self.add_setter(field_name)

    def add_public_method(self, name, return_type=None, body=None):
        modifier = set()
        modifier.add('public')
        self.add_method(modifier, return_type, name, body=body)

    def add_getter(self, field_name: str):
        modifier = set()
        modifier.add('public')
        field = self.get_field(field_name)
        if field:
            self.add_method(modifier, field.type, 'get' + field_name[0].upper() + field_name[1:],
                            body=[ReturnStatement(expression=MemberReference(member=field_name))])

    def add_setter(self, field_name: str):
        modifier = set()
        modifier.add('public')
        field = self.get_field(field_name)
        if field:
            self.add_method(modifier, None, 'set' + field_name[0].upper() + field_name[1:],
                            parameters=[FormalParameter(type=field.type, name=field_name)],
                            body=[StatementExpression(
                                expression=Assignment(
                                    expressionl=This(selectors=[MemberReference(member=field_name)]),
                                    type='=',
                                    value=MemberReference(member=field_name)))])


class FieldOperator(ClassMemberOperator):
    def __init__(self, class_operator: ClassOperator):
        super(FieldOperator, self).__init__(class_operator)

    def add_private_string_field(self, field_name, value=''):
        modifier = set()
        modifier.add('private')
        self.add_field(modifier, ReferenceType(name="String"), [
            VariableDeclarator(name=field_name, initializer=Literal(value=value) if len(value) > 0 else None)])

    def add_field_annotation(self, field_name, annotation_name, **annotation_kwargs):
        field = self.get_field(field_name)
        if not field.annotations:
            field.annotations = []
        field.annotations.append(Annotation(name=annotation_name,
                                            element=[ElementValuePair(name=key, value=Literal(value=value)) for
                                                     key, value
                                                     in
                                                     annotation_kwargs.items()]))


def get_class_member_type_order(x):
    if type(x) == FieldDeclaration:
        return 0
    if type(x) == ConstructorDeclaration:
        return 1
    if type(x) == MethodDeclaration:
        return 2
    return 3


class AbstractClassOperator(ClassOperator):
    def __init__(self, class_path: str = '', class_name: str = ''):
        super().__init__(class_path, class_name)

    def add_class(self, class_name: str):
        modifier = ['public', 'abstract']
        abstract_class_declaration = ClassDeclaration(modifiers=modifier, name=class_name, body=[])
        self.class_tree.types.append(abstract_class_declaration)
        return abstract_class_declaration

    def add_abstract_method(self, name, return_type=None, *parameters):
        modifier = ['public', 'abstract']
        self.get_method_cursor().add_method(modifiers=modifier, return_type=return_type, name=name,
                                            parameters=list(*parameters))


class BasicReadableClassOperator(ObjectOperator):
    def __init__(self, clazz_content):
        super().__init__()
        self.new_file = False
        self.file_content = clazz_content
        self.class_tree = parse.parse(self.file_content)
        self.class_cursor = self.class_tree.types[0]

    def get_fields(self):
        if len(self.class_tree.types) == 1:
            # if this class file only have one class declare
            class_declare = self.class_tree.types[0]
            fields = []
            for item in class_declare.body:
                if type(item) == FieldDeclaration:
                    fields.append(item)
            return fields
