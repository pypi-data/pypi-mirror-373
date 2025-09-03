#  Copyright (c) 2023 bastien.saltel
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

import uuid
from typing import Any

from galaxy.utils.type import CompId
from galaxy.app.ioc.definition import ComponentDefinition,          \
                                      ConfigurationDefinition,      \
                                      ReferenceDefinition,          \
                                      DictDefinition
from galaxy.utils.pattern import Builder


class CompDefinitionBuilder(Builder):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(CompDefinitionBuilder, self).__init__()
        self._id: CompId | None = None
        self._class: str | None = None
        self._factory: Any | None = None
        self._properties: list = []
        self._scope: str | None = None
        self._lazy_init: bool = False
        self._abstract: bool = False
        self._parent_id: CompId | None = None
        self._pos_constr: list = []
        self._named_constr: dict = {}

    def id_(self, id_: str) -> "CompDefinitionBuilder":
        self._id = uuid.UUID(id_)
        return self

    def class_(self, class_: str) -> "CompDefinitionBuilder":
        self._class = class_
        return self

    def factory(self, factory: "ReflectiveObjectFactory") -> "CompDefinitionBuilder":
        self._factory = factory
        return self

    def properties(self, properties: list) -> "CompDefinitionBuilder":
        self._properties = properties
        return self

    def scope(self, scope: str) -> "CompDefinitionBuilder":
        self._scope = scope
        return self

    def lazy_init(self, lazy_init: bool) -> "CompDefinitionBuilder":
        self._lazy_init = lazy_init
        return self

    def abstract(self, abstract: bool) -> "CompDefinitionBuilder":
        self._abstract = abstract
        return self

    def parent_id(self, parent_id: CompId) -> "CompDefinitionBuilder":
        self._parent_id = parent_id
        return self

    def pos_constr(self, pos_constr: list) -> "CompDefinitionBuilder":
        self._pos_constr = pos_constr
        return self

    def named_constr(self, named_constr: dict) -> "CompDefinitionBuilder":
        self._named_constr = named_constr
        return self

    def build(self) -> ComponentDefinition:
        comp = ComponentDefinition(self._id)
        comp.class_ = self._class
        comp.factory = self._factory
        comp.properties = self._properties
        comp.scope = self._scope
        comp.lazy_init = self._lazy_init
        comp.abstract = self._abstract
        comp.parent_id = self._parent_id
        comp.pos_constr = self._pos_constr
        comp.named_constr = self._named_constr
        return comp


class ConfDefinitionBuilder(Builder):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(ConfDefinitionBuilder, self).__init__()
        self._id: CompId | None = None
        self._properties: DictDefinition | None = None

    def id_(self, id_: str) -> "ConfDefinitionBuilder":
        self._id = uuid.UUID(id_)
        return self

    def properties(self, properties: DictDefinition) -> "ConfDefinitionBuilder":
        self._properties = properties
        return self

    def build(self) -> ConfigurationDefinition:
        conf = ConfigurationDefinition(self._id)
        conf.properties = self._properties
        return conf


class RefDefinitionBuilder(Builder):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(RefDefinitionBuilder, self).__init__()
        self._name: str | None = None
        self._ref_comp_id: CompId | None = None

    def name(self, name: str) -> "RefDefinitionBuilder":
        self._name = name
        return self

    def ref_comp_id(self, id_: str) -> "RefDefinitionBuilder":
        self._ref_comp_id = uuid.UUID(id_)
        return self

    def build(self) -> ReferenceDefinition:
        return ReferenceDefinition(self._name, self._ref_comp_id)
