import functools

import javalang.parse
from javalang.parser import JavaSyntaxError
from javalang.tree import ReferenceType

from javacoder.core.operator import ClassOperator, InterfaceOperator, AbstractClassOperator, ObjectOperator, \
    AnnotationOperator, EnumOperator
from javacoder.core.plugins import ProjectPlugin, AuthorPlugin


def edit_operator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ob = args[0]
        if isinstance(ob, ObjectBuilder):
            ob.check_closed()
        return func(*args, **kwargs)

    return wrapper


def parse_expression(expression):
    if type(expression) == str:
        try:
            return javalang.parse.parse_member_signature(expression)
        except JavaSyntaxError:
            pass
        try:
            return javalang.parse.parse_expression(expression)
        except JavaSyntaxError:
            pass
    return expression


class ObjectBuilder:

    def __init__(self):
        self.closed = False
        self.operator = None
        self.extended = False

    @edit_operator
    def build(self) -> ObjectOperator:
        self.operator.format()
        self.closed = True
        return self.operator

    @edit_operator
    def document(self, document):
        self.operator.set_document(document)

    @edit_operator
    def annotation(self, annotation_name, **kwargs):
        self.operator.add_annotation(annotation_name, **kwargs)

    @edit_operator
    def imports(self, path, static=False, wildcard=False):
        self.operator.add_import(path, static=static, wildcard=wildcard)

    @edit_operator
    def project(self, project_path=None):
        if project_path:
            self.operator.add_plugin(ProjectPlugin(project_path))

    @edit_operator
    def add_plugin(self, plugin):
        if plugin:
            self.operator.add_plugin(plugin)

    @edit_operator
    def author(self, author='', email='', **kwargs):
        self.operator.add_plugin(AuthorPlugin(author, email, **kwargs))

    @edit_operator
    def package(self, package_name):
        self.operator.set_package_name(package_name)

    def check_closed(self):
        if self.closed:
            raise Warning("builder has been closed, cannot edit it.")

    @edit_operator
    def extend_builder(self, builder):
        if not builder.closed:
            raise Warning("parent builder is active, cannot extend it, please build the code before.")
        if builder.extended:
            raise Warning("parent builder has been extended, cannot extend it again.")
        for plugin in builder.operator.plugins:
            self.add_plugin(plugin)
        builder.operator.plugins.clear()
        builder.extended = True


class ClassBuilder(ObjectBuilder):
    def __init__(self, name, class_path=''):
        super().__init__()
        self.operator = ClassOperator(class_name=name, class_path=class_path)

    @edit_operator
    def field(self, field, value='', annotation='', **annotation_kwargs):
        self.operator.add_private_string(field, value)
        if len(annotation) > 0:
            self.operator.add_field_annotation(field, annotation, **annotation_kwargs)

    @edit_operator
    def extend(self, extend_class):
        self.operator.set_extend_class(extend_class)

    @edit_operator
    def add_fields_getter_and_setter(self):
        for field in self.operator.get_fields():
            self.operator.add_getter_and_setter(field.declarators[0].name)

    @edit_operator
    def implement(self, implement_class):
        self.operator.add_implement(implement_class)

    @edit_operator
    def constructor(self, *body, **kwargs):
        if 'modifiers' not in kwargs.keys():
            kwargs['modifiers'] = ["public"]

        if 'parameters' not in kwargs.keys():
            kwargs['parameters'] = []
        else:
            kwargs['parameters'] = [parse_expression(e) for e in kwargs['parameters']]

        if not body or len(body) == 0:
            kwargs['body'] = []
        else:
            kwargs['body'] = [parse_expression(e) for e in body]
        self.operator.get_method_cursor().add_constructor(kwargs['modifiers'], kwargs['parameters'], kwargs['body'])

    @edit_operator
    def method(self, name, *body, **kwargs):
        if 'modifiers' not in kwargs.keys():
            kwargs['modifiers'] = ["public"]
        if 'return_type' not in kwargs.keys():
            kwargs['return_type'] = None
        elif type(kwargs['return_type']) == str:
            kwargs['return_type'] = ReferenceType(name=kwargs['return_type'])
        if 'parameters' not in kwargs.keys():
            kwargs['parameters'] = []
        else:
            kwargs['parameters'] = [parse_expression(e) for e in kwargs['parameters']]
        if not body or len(body) == 0:
            kwargs['body'] = []
        else:
            kwargs['body'] = [parse_expression(e) for e in body]

        self.operator.get_method_cursor().add_method(kwargs['modifiers'], kwargs['return_type'], name,
                                                     kwargs['parameters'], kwargs['body'])


class InterfaceBuilder(ObjectBuilder):
    def __init__(self, name, class_path=''):
        super(InterfaceBuilder, self).__init__()
        self.operator = InterfaceOperator(name=name, interface_path=class_path)

    @edit_operator
    def method(self, name):
        self.operator.add_method(name)

    @edit_operator
    def extend(self, extend_interface, *template_class):
        self.operator.add_extend_interface(extend_interface, *template_class)


class EnumBuilder(ObjectBuilder):
    def __init__(self, name, class_path=''):
        super().__init__()
        self.operator = EnumOperator(name=name, enum_path=class_path)

    @edit_operator
    def construct(self, *body, **kwargs):
        if 'modifiers' not in kwargs.keys():
            kwargs['modifiers'] = ["public"]

        if 'parameters' not in kwargs.keys():
            kwargs['parameters'] = []
        else:
            kwargs['parameters'] = [parse_expression(e) for e in kwargs['parameters']]

        if not body or len(body) == 0:
            kwargs['body'] = []
        else:
            kwargs['body'] = [parse_expression(e) for e in body]
        self.operator.get_method_cursor().add_constructor(kwargs['modifiers'], kwargs['parameters'], kwargs['body'])

    @edit_operator
    def enum(self, name, *parameters):
        self.operator.enumerate(name)

    @edit_operator
    def method(self, name, *body, **kwargs):
        if 'modifiers' not in kwargs.keys():
            kwargs['modifiers'] = ["public"]
        if 'return_type' not in kwargs.keys():
            kwargs['return_type'] = None
        elif type(kwargs['return_type']) == str:
            kwargs['return_type'] = ReferenceType(name=kwargs['return_type'])
        if 'parameters' not in kwargs.keys():
            kwargs['parameters'] = []
        else:
            kwargs['parameters'] = [parse_expression(e) for e in kwargs['parameters']]
        if not body or len(body) == 0:
            kwargs['body'] = []
        else:
            kwargs['body'] = [parse_expression(e) for e in body]

        self.operator.get_method_cursor().add_method(kwargs['modifiers'], kwargs['return_type'], name,
                                                     kwargs['parameters'], kwargs['body'])


class AbstractClassBuilder(ClassBuilder):
    def __init__(self, name, class_path=''):
        super(ObjectBuilder, self).__init__()
        self.operator = AbstractClassOperator(class_name=name, class_path=class_path)

    @edit_operator
    def abstract_method(self, name, **kwargs):
        if 'return_type' not in kwargs.keys():
            kwargs['return_type'] = None
        elif type(kwargs['return_type']) == str:
            kwargs['return_type'] = ReferenceType(name=kwargs['return_type'])
        if 'parameters' not in kwargs.keys():
            kwargs['parameters'] = []
        else:
            kwargs['parameters'] = [parse_expression(e) for e in kwargs['parameters']]

        self.operator.add_abstract_method(name, kwargs['return_type'], kwargs['parameters'])


class AnnotationBuilder(ObjectBuilder):
    def __init__(self, name, target='class', class_path=''):
        super().__init__()
        self.operator = AnnotationOperator(name=name, annotation_path=class_path, target=target)

    @edit_operator
    def method(self, name, return_type, default):
        self.operator.method(name, return_type, default=default)


def create_builder(name, builder_type: type = None, template_builder: ObjectBuilder = None) -> ObjectBuilder:
    new_builder = None
    if builder_type:
        new_builder = builder_type
    elif template_builder:
        new_builder = type(ObjectBuilder)
    if issubclass(new_builder, ObjectBuilder):
        new_instance = new_builder(name)
        if template_builder:
            new_instance.extend_builder(template_builder)
        return new_instance
    raise Exception("unsupported builder type.")
