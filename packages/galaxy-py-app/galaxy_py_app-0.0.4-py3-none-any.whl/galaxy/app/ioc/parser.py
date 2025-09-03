#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from os import path
import yaml
from abc import ABC,                                                    \
                abstractmethod
from typing import Any,                                                 \
                   TYPE_CHECKING
from collections import OrderedDict

from galaxy.app import constant
from galaxy.app.ioc.factory import DefinitionFactory
from galaxy.error.io import IOFileNotExistingError,                     \
                            IOFileWrongFormatOrMalformedError
from galaxy.utils.type import CompId

if TYPE_CHECKING:
    from galaxy.app.ioc.definition import ComponentDefinition


def convert(scope_str: str) -> str:
    if scope_str == "prototype":
        return constant.PROTOTYPE
    elif scope_str == "singleton":
        return constant.SINGLETON
    else:
        raise Exception("Can not handle scope {}".format(scope_str))


yaml_mappings: dict[str, str] = {
                                 "str": "types.StringType",
                                 "unicode": "types.UnicodeType",
                                 "int": "types.IntType",
                                 "long": "types.LongType",
                                 "float": "types.FloatType",
                                 "decimal": "decimal.Decimal",
                                 "bool": "types.BooleanType",
                                 "complex": "types.ComplexType",
                                 "list": "types.ListType",
                                 "tuple": "types.TupleType",
                                 "dict": "types.DictType",
                                }


def get_string(value: Any) -> Any:
    """
    classdocs
    """

    try:
        return str(value)
    except UnicodeEncodeError:
        return value


class CompositionParser(ABC):
    """
    classdocs
    """

    @abstractmethod
    def parse(self, comp_file: str) -> dict[CompId, "ComponentDefinition"]:
        raise NotImplementedError("Should implement parse()")


class ConfigurationParser(ABC):
    """
    classdocs
    """

    @abstractmethod
    def parse(self, comp_file: str) -> dict[CompId, "ConfigurationDefinition"]:
        raise NotImplementedError("Should implement parse()")


class YamlCompositionParser(CompositionParser):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(YamlCompositionParser, self).__init__()

    def parse(self, comp_file: str) -> dict[CompId, "ComponentDefinition"]:
        if not path.exists(comp_file):
            raise IOFileNotExistingError(comp_file)

        factory = DefinitionFactory()
        try:
            with open(comp_file) as f:
                doc = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            raise IOFileWrongFormatOrMalformedError(comp_file, None, e)
        comps = factory.create_components(doc)

        #visitor = PrintVisitor()
        #for comp in comps:
        #    comp.accept(visitor)

        return OrderedDict({comp.id: comp for comp in comps})


class YamlConfigurationParser(ConfigurationParser):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(YamlConfigurationParser, self).__init__()

    def parse(self, conf_file: str) -> dict[CompId, "ConfigurationDefinition"]:
        if not path.exists(conf_file):
            raise IOFileNotExistingError(conf_file)

        factory = DefinitionFactory()
        try:
            with open(conf_file) as f:
                doc = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            raise IOFileWrongFormatOrMalformedError(conf_file, None, e)
        confs = factory.create_configurations(doc)

        #visitor = PrintVisitor()
        #for conf in confs:
        #    conf.accept(visitor)

        return OrderedDict({conf.id: conf for conf in confs})
