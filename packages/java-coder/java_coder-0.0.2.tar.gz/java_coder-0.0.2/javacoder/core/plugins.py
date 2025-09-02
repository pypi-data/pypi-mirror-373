import datetime
import inspect
import os
import platform
import re
import shutil
import zipfile

import javacoder
import requests

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from javacoder.core.operator import ClassOperator, BasicReadableClassOperator
from javacoder.utils.loader import get_git_config_property, get_run_command_output
from javacoder.utils.converter import get_first_element
from javacoder.utils.log import *

class Plugin:
    def __init__(self):
        pass

    def invoke(self, **kwargs):
        invoke_method_name = 'invoke_' + kwargs['invoke_method']
        if hasattr(self, invoke_method_name):
            getattr(self, invoke_method_name)(**kwargs)


class ProjectPlugin(Plugin):
    def __init__(self, project_path):
        super(ProjectPlugin, self).__init__()
        self.project_path = project_path
        self.packages = {}
        self.project_walker = ProjectWalker(project_path)
        self.project_walker.walk()
        self.new_project = len(self.project_walker.project_files) == 0
        self.project_pom = ET.ElementTree()
        self.project_pom_namespace = 'http://maven.apache.org/POM/4.0.0'
        self.maven_walker = None
        if not self.new_project:
            source_path = os.path.join(project_path, 'src', 'main', 'java')
            for file, path in self.project_walker.peek():
                if file == 'pom.xml':
                    self.project_pom.parse(os.path.join(path, file))
                    self.project_pom_namespace = re.findall(r"^{(.+?)}.+$", self.project_pom.getroot().tag)[0]
                    if not self.maven_walker:
                        self.maven_walker = MavenWalker(project_plugin=self)
                if file.endswith('.java'):
                    self.add_package_reference_map(file[:-5], path[len(source_path) + 1:].replace(os.sep, '.'))
            if self.maven_walker:
                self.load_project_dependencies_reference()

    def add_package_reference_map(self, class_name, package_name):
        if class_name not in self.packages:
            self.packages[class_name] = [package_name]
        else:
            self.packages[class_name].append(package_name)

    def _create_project(self):
        if self.new_project:
            os.mkdir(os.path.join(self.project_path, 'src', 'main', 'java'))
            os.mkdir(os.path.join(self.project_path, 'src', 'main', 'resources'))
            with open(os.path.join(self.project_path, 'pom.xml'), 'w') as f:
                self.project_pom.write(f, encoding='utf-8')

    def load_project_dependencies_reference(self):
        if self.maven_walker:
            for key, info in self.get_project_dependencies().items():
                self.maven_walker.get_jar_class(
                    self.maven_walker.get_jar_path(info['groupId'], key, version=info['version']))

    def get_project_dependencies(self):
        dependence_dict = {}
        if self.project_pom:
            dependencies = self.project_pom.getroot().find(self.get_project_pom_tag("dependencies"))
            properties = self.project_pom.getroot().find(self.get_project_pom_tag("properties"))
            properties_map = {}
            if properties and properties.iter():
                for i in properties.iter():
                    properties_map[i.tag[len(self.project_pom_namespace) + 2:]] = i.text
            if dependencies:
                for dependence in dependencies.findall(self.get_project_pom_tag("dependency")):
                    d = dependence.find(self.get_project_pom_tag("artifactId"))
                    if isinstance(d, ET.Element):
                        group_id = dependence.find(self.get_project_pom_tag("groupId")).text
                        version = '' if not isinstance(dependence.find(self.get_project_pom_tag("version")), ET.Element) \
                            else dependence.find(self.get_project_pom_tag("version")).text
                        dependence_dict[d.text] = {
                            'groupId': group_id,
                            'version': version if not re.match(r'\${.+?}', version) else
                            re.sub(r'\${.+?}', properties_map.get(re.findall(r'\${(.+?)}', version)[0]), version)
                        }
        return dependence_dict

    def get_project_pom_tag(self, tag_name):
        return '{' + self.project_pom_namespace + '}' + tag_name

    def fill_imports(self, class_name, operator):
        if class_name:
            if class_name in self.packages:
                if len(self.packages[class_name]) == 1:
                    package_path = self.packages[class_name][0]
                else:
                    info("please select import class:")
                    for index, package in enumerate(self.packages[class_name]):
                        info(index, ": ", package)
                    select_one = int(input(">"))
                    package_path = self.packages[class_name][select_one]
                imported_class = operator.get_import()
                if package_path + '.' + class_name not in imported_class:
                    operator.add_import(package_path + '.' + class_name)

    def invoke_preview_class(self, **kwargs):
        invoke_op = kwargs['invoke_operator']
        self.check_class_package(invoke_op)
        referenced = self.get_operator_element_by_type(invoke_op, 'ReferenceType')
        for reference in referenced:
            self.fill_imports(reference.name, invoke_op)

    def invoke_save(self, **kwargs):
        invoke_op = kwargs['invoke_operator']
        self._create_project()
        self.check_class_package(invoke_op)
        referenced = self.get_operator_element_by_type(invoke_op, 'ReferenceType')
        for reference in referenced:
            self.fill_imports(reference.name, invoke_op)
        if invoke_op.file_path in os.path.join(self.project_path, 'src', 'main',
                                               'java') and invoke_op.class_tree.package:
            self.add_package_reference_map(invoke_op.file_name, invoke_op.class_tree.package.name)

    def get_operator_element_by_type(self, operator, *element_type):
        elements = []
        result = set()
        elements.append(operator.class_tree)
        while len(elements) > 0:
            element = elements.pop()
            if type(element).__name__ in element_type:
                result.add(element)
            if element and hasattr(element, 'children'):
                for obj in element.children:
                    if obj and type(obj) != str:
                        if hasattr(obj, '__iter__') or hasattr(obj, '__getitem__'):
                            for o in obj:
                                elements.append(o)
                        else:
                            elements.append(obj)
        return result

    def check_class_package(self, operator):
        if operator.class_tree.package:
            if not operator.file_path:
                operator.file_path = os.path.join(self.project_path, 'src', 'main', 'java',
                                                  str(operator.class_tree.package.name).replace('.', os.sep))
        else:
            if operator.file_path:
                operator.set_package_name_by_file_path(operator.file_path)

    def get_class_operator(self, package_path):
        path = os.path.join(self.project_path, str(package_path).replace('.', os.sep) + '.java')
        if os.path.exists(path) and os.path.isfile(path):
            try:
                cop = ClassOperator(class_path=path)
                cop.add_plugin(self)
                return cop
            except Exception as e:
                error("parse file - {} error info - {}".format(path, e))
        else:
            if self.maven_walker:
                return self.maven_walker.get_class_operator(package_path)
        return None


class AuthorPlugin(Plugin):
    def __init__(self, username='', email='', **kwargs):
        super(AuthorPlugin, self).__init__()
        self.author_map = {
            "author": username if username != '' else get_git_config_property('user.name'),
            "email": email if email != '' else get_git_config_property('user.email')
        }
        for k, v in kwargs.items():
            self.author_map[k] = v

    def get_converted_author_info(self, key):
        return '@' + key + ' ' + self.author_map[key]

    def invoke_preview_class(self, **kwargs):
        invoke_op = kwargs['invoke_operator']
        self.add_author_info(invoke_op)

    def invoke_save(self, **kwargs):
        invoke_op = kwargs['invoke_operator']
        self.add_author_info(invoke_op)

    def add_author_info(self, operator):
        self.author_map['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if operator.class_cursor:
            author_info_document = ''
            if operator.class_cursor.documentation:
                for k in self.author_map.keys():
                    if '@' + k not in operator.class_cursor.documentation.documentation:
                        author_info_document = author_info_document + self.get_converted_author_info(k) + '\n'
                document = author_info_document + operator.class_cursor.documentation.documentation
            else:
                document = '\n'.join([self.get_converted_author_info(k) for k in self.author_map.keys()])
            operator.set_document(document.strip('\n'))


class ProjectWalker:
    def __init__(self, project_path):
        self.project_path = project_path
        self.project_files = {}

    def walk(self):
        self.project_files.clear()
        if self.project_path and len(self.project_path) > 0:
            if os.path.exists(self.project_path) and os.path.isdir(self.project_path):
                for root, dirs, files in os.walk(self.project_path):
                    for file in files:
                        if file not in self.project_files:
                            self.project_files[file] = [root]
                        else:
                            self.project_files[file].append(root)

    def peek(self, fresh=True):
        if fresh:
            self.walk()
        for file, paths in self.project_files.items():
            for path in paths:
                yield file, path

    def peek_class_operator(self, fresh=True):
        if fresh:
            self.walk()
        for file, path in self.peek():
            op = convert_class_operator(file, path)
            if op:
                yield op

    def total_size(self, file_type=None):
        return sum([len(v) if file_type and k.endswith('.' + file_type) else 0 for k, v in self.project_files.items()])


def convert_class_operator(file, path):
    if file.endswith(".java"):
        try:
            return ClassOperator(class_path=os.path.join(path, file))
        except Exception as e:
            error("parse file - {} error info - {}".format(os.path.join(path, file), e))
    else:
        return None


class MavenWalker:
    def __init__(self, project_plugin: ProjectPlugin = None):
        self.project_plugin = project_plugin
        self.mvn_repo_commands = 'mvn help:evaluate -Dexpression=settings.localRepository | find /v "[INFO]"' \
            if 'Windows' in platform.system() else \
            '/usr/local/bin/mvn help:evaluate -Dexpression=settings.localRepository | grep -v "[INFO]"'
        self.mvn_repo_path = get_run_command_output(self.mvn_repo_commands)
        self.mvn_class = {}
        self.cfr_link = 'https://www.benf.org/other/cfr/cfr-0.152.jar'
        self.lib_cfr_path = os.path.join(os.path.dirname(inspect.getfile(javacoder)), 'lib', 'cfr-0.152.jar')
        self.cache_dir = 'zip_files' if not project_plugin.project_path else os.path.join(project_plugin.project_path,
                                                                                          'zip_files')

    def get_jar_path(self, group_id: str, artifact_id, version=None):
        group_path = group_id.replace('.', os.sep)
        package_version = version
        if not version:
            dirs = os.listdir(os.path.join(self.mvn_repo_path, group_path, artifact_id))
            package_version = max(dirs, key=lambda d: os.path.getctime(
                os.path.join(self.mvn_repo_path, group_path, artifact_id, d)))
        return os.path.join(self.mvn_repo_path, group_path, artifact_id, package_version,
                            artifact_id + '-' + package_version + '.jar')

    def get_jar_class(self, jar_path):
        if os.path.isfile(jar_path) and zipfile.is_zipfile(jar_path):
            result = []
            with zipfile.ZipFile(jar_path, 'r') as jar:
                for clazz in jar.namelist():
                    if clazz.endswith('.class'):
                        paths = clazz.split('/')
                        class_info = ('.'.join(paths[:-1]), paths[-1].replace('.class', '').replace('$', '.'))
                        result.append(class_info)
                        self.__put_maven_class(class_info[1], class_info[0], jar_path)
            if self.project_plugin:
                for clazz_info in result:
                    self.project_plugin.add_package_reference_map(clazz_info[1], clazz_info[0])
            return result
        return []

    def __put_maven_class(self, class_name, package_path, jar_path):
        if class_name in self.mvn_class.keys():
            self.mvn_class[class_name].append({'jar_path': jar_path, 'package_path': package_path})
        else:
            self.mvn_class[class_name] = [{'jar_path': jar_path, 'package_path': package_path}]

    def get_jar_class_content(self, jar_path, zip_class_path):
        self.__check_cfr()
        jar_name = str(jar_path).split(os.sep)[-1].replace('.jar', '')
        if not os.path.exists(os.path.join(self.cache_dir, jar_name, zip_class_path.replace('/', os.sep))):
            if os.path.isfile(jar_path) and zipfile.is_zipfile(jar_path):
                with zipfile.ZipFile(jar_path, 'r') as jar:
                    jar.extract(zip_class_path, os.path.join(self.cache_dir, jar_name))
        class_content = get_run_command_output(
            'java -jar ' + self.lib_cfr_path + ' ' + os.path.join(self.cache_dir, jar_name,
                                                                  zip_class_path.replace('/',
                                                                                         os.sep)))
        return class_content

    def get_class_operator(self, import_path):
        class_name = str(import_path).split('.')[-1]
        package_path = '.'.join(str(import_path).split('.')[:-1])
        if class_name in self.mvn_class.keys():
            jar_path = get_first_element(self.mvn_class[class_name], lambda p: p['package_path'] == package_path)[
                'jar_path']
            class_content = self.get_jar_class_content(jar_path, str(import_path).replace('.', '/') + '.class')
            if class_content:
                bop = BasicReadableClassOperator(class_content)
                bop.add_plugin(self.project_plugin)
                return bop
        return None

    def __del__(self):
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)

    def __check_cfr(self):
        if os.path.exists(self.lib_cfr_path):
            return
        lib_path = os.path.join(os.path.dirname(inspect.getfile(javacoder)), 'lib')
        if not os.path.exists(lib_path):
            os.mkdir(lib_path)
        response = requests.get(self.cfr_link)
        if response.status_code == 200:
            with open(self.lib_cfr_path, "wb") as file:
                file.write(response.content)
            info("文件下载完成")
        else:
            warning(f"下载失败，状态码: {response.status_code}")
