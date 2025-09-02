#!/user/bin/env python
# -*- coding: utf-8 -*-
# Time: 2025/8/17 19:42
# Author: chonmb
# Software: PyCharm
from javacoder.core.builder import ClassBuilder, InterfaceBuilder, EnumBuilder, AbstractClassBuilder, AnnotationBuilder
from javacoder.core.plugins import AuthorPlugin, ProjectPlugin
import os
from javacoder.utils.log import *


class Project:
    def __init__(self, project_path):
        self.project_path = project_path
        self.plugin_author = AuthorPlugin()
        self.plugin_project = ProjectPlugin(self.project_path)
        self.current_package = 'com.app.demo'
        self.temp_builders = []

    def set_current_package(self, package_name):
        self.current_package = package_name

    def add_maven_dependency(self):
        # todo: add dependency
        pass

    def source(self):
        pass

    def class_builder(self, name):
        class_path = self.__get_class_path(name)
        builder = ClassBuilder(name, class_path='' if not class_path else class_path)
        self.__config_builder(builder, class_path)
        return builder

    def interface_builder(self, name):
        class_path = self.__get_class_path(name)
        builder = InterfaceBuilder(name, class_path='' if not class_path else class_path)
        self.__config_builder(builder, class_path)
        return builder

    def enum_builder(self, name):
        class_path = self.__get_class_path(name)
        builder = EnumBuilder(name, class_path='' if not class_path else class_path)
        self.__config_builder(builder, class_path)
        return builder

    def abstract_class_builder(self, name):
        class_path = self.__get_class_path(name)
        builder = AbstractClassBuilder(name, class_path='' if not class_path else class_path)
        self.__config_builder(builder, class_path)
        return builder

    def annotation_builder(self, name):
        class_path = self.__get_class_path(name)
        builder = AnnotationBuilder(name, class_path='' if not class_path else class_path)
        self.__config_builder(builder, class_path)
        return builder

    def save(self):
        # todo: save source, dependency...
        for builder in self.temp_builders:
            if not builder.closed:
                builder.build()

    def __config_builder(self, builder, class_path):
        builder.add_plugin(self.plugin_project)
        builder.add_plugin(self.plugin_author)
        if not class_path:
            builder.package(self.current_package)
        self.temp_builders.append(builder)

    def __get_class_path(self, name):
        if name in self.plugin_project.packages:
            if len(self.plugin_project.packages[name]) == 1:
                if self.current_package != self.plugin_project.packages[name][0]:
                    selected_class_package = self.plugin_project.packages[name][0]
                    info("do you mean the class in package [{}]? Y/n".format(selected_class_package))
                    check_new_class = input('>')
                    if check_new_class.lower() != 'y':
                        self.current_package = selected_class_package
                        info("checkout current package to {}".format(self.current_package))
                    else:
                        return None
            else:
                info('do you mean the class in follow packages? No./n')
                for i, p in enumerate(self.plugin_project.packages[name]):
                    info('{} : {}'.format(i, p))
                check_new_class = input('>')
                if check_new_class.lower() == 'n':
                    return None
                selected_class_package = self.plugin_project.packages[name][int(check_new_class)]
                self.current_package = selected_class_package
                info("checkout current package to {}".format(self.current_package))
            return self.__convert_package_path_to_file_path(self.current_package) + os.sep + name + '.java'
        return None

    def __convert_package_path_to_file_path(self, package: str):
        return os.path.join(self.project_path, 'src', 'main', 'java', package.replace('.', os.sep))
