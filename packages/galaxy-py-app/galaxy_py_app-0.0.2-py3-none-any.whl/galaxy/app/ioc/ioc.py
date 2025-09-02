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

import uuid
from abc import ABC,                                                        \
                abstractmethod
from collections import OrderedDict
import atexit
from os import path
from typing import Any,                                                     \
                   TYPE_CHECKING

from galaxy.app import constant
from galaxy.app.ioc.parser import YamlCompositionParser,                    \
                                  CompositionParser,                        \
                                  YamlConfigurationParser,                  \
                                  ConfigurationParser
from galaxy.app.ioc.definition import ComponentDefinition,                  \
                                      ConfigurationDefinition
from galaxy.utils.base import Component
from galaxy.error.app import AppReferenceNotFoundError,                     \
                             AppScopeNotSupportedError,                     \
                             AppAbstractCompCannotBeInstantiatedError
from galaxy.error.io import IOFormatNotSupportedError
from galaxy.utils.type import CompId

if TYPE_CHECKING:
    from galaxy.app.ioc.visitor import Visitor


class IOCManager(Component):
    """
    classdocs
    """

    def __init__(self, app: object) -> None:
        """
        Constructor
        """
        super(IOCManager, self).__init__()
        self.name: str = "IOC Manager"
        self.comp_parsers: dict[str, CompositionParser] = {
                                                           "yml": YamlCompositionParser()
                                                          }
        self.conf_parsers: dict[str, ConfigurationParser] = {
                                                             "yml": YamlConfigurationParser()
                                                            }
        self.context: ApplicationContext = ApplicationContext()
        self.init_comps = {
                           uuid.uuid4(): app,
                           uuid.uuid4(): self
                          }
        self.context.add_components(self.init_comps)

    def load_comp(self, comp_file) -> None:
        extension = path.splitext(comp_file)[1][1:]
        if extension in self.comp_parsers:
            self.context.import_comp_file(comp_file, self.comp_parsers[extension])
        else:
            raise IOFormatNotSupportedError(extension)

    def load_conf(self, conf_file) -> None:
        extension = path.splitext(conf_file)[1][1:]
        if extension in self.conf_parsers:
            self.context.import_conf_file(conf_file, self.conf_parsers[extension])
        else:
            raise IOFormatNotSupportedError(extension)

    def __repr__(self) -> str:
        return "<IOCManager(id='{}')>".format(self.id)


class InitializingObject(ABC):
    """
    classdocs
    """

    @abstractmethod
    def after_properties_set(self) -> None:
        raise NotImplementedError("Should implement after_properties_set()")


class ObjectPostProcessor(ABC):
    """
    classdocs
    """

    @abstractmethod
    def post_process_before_initialization(self, comp: object, id_: CompId) -> object:
        raise NotImplementedError("Should implement post_process_before_initialization()")

    @abstractmethod
    def post_process_after_initialization(self, comp: object, id_: CompId) -> object:
        raise NotImplementedError("Should implement post_process_after_initialization()")


class DisposableObject(ABC):
    """
    classdocs
    """

    @abstractmethod
    def destroy(self) -> None:
        raise NotImplementedError("Should implement destroy()")


class ComponentContainer(object):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.comp_defs: dict[CompId, ComponentDefinition] = OrderedDict({})
        self.components: dict[CompId, Component] = OrderedDict({})
        self.conf_defs: dict[CompId, ConfigurationDefinition] = OrderedDict({})

    def get_component(self, id_: CompId, ignore_abstract: bool | None = False) -> object:
        try:
            comp_def = self.comp_defs[id_]
            if comp_def.abstract and not ignore_abstract:
                raise AppAbstractCompCannotBeInstantiatedError(comp_def)
            return self.components[id_]

        except KeyError as e:
            try:
                comp_def = self.comp_defs[id_]
                if comp_def.abstract and not ignore_abstract:
                    raise AppAbstractCompCannotBeInstantiatedError(comp_def)
                comp = self._create_component(comp_def)

                # Evaluate any scopes, and store appropriately.
                if comp_def.scope == constant.SINGLETON:
                    self.components[id_] = comp
                elif comp_def.scope == constant.PROTOTYPE:
                    pass
                else:
                    raise AppScopeNotSupportedError(comp_def)

                return comp
            except KeyError as e:
                raise AppReferenceNotFoundError(id_, internal=e)

    def _get_constructors_pos(self, comp_def: ComponentDefinition) -> tuple:
        if comp_def.pos_constr is None:
            return tuple()
        return tuple([constr.get_value(self) for constr in comp_def.pos_constr if hasattr(constr, "get_value")])

    def _get_constructors_kw(self, comp_def: ComponentDefinition) -> dict:
        if comp_def.named_constr is None:
            return dict()
        return dict([(key, comp_def.named_constr[key].get_value(self)) for key in comp_def.named_constr
                     if hasattr(comp_def.named_constr[key], "get_value")])

    def _create_component(self, comp_def: ComponentDefinition) -> Any:
        if comp_def.pos_constr is not None:
            [constr.prefetch(self) for constr in comp_def.pos_constr if hasattr(constr, "prefetch")]
        if comp_def.named_constr is not None:
            [constr.prefetch(self) for constr in comp_def.named_constr.values() if hasattr(constr, "prefetch")]
        if comp_def.properties is not None:
            [prop.prefetch(self) for prop in comp_def.properties if hasattr(prop, "prefetch")]

        # Res up an instance of the object, with ONLY constructor-based properties set.
        obj = comp_def.factory.create(self._get_constructors_pos(comp_def),
                                      self._get_constructors_kw(comp_def))

        comp: Component = obj
        comp.id = comp_def.id

        # Fill in the other property values.
        if comp_def.properties is not None:
            [prop.set_value(comp, self) for prop in comp_def.properties if hasattr(prop, "set_value")]
        return comp

    def apply_comp_props(self, obj: Any, comp_def: ComponentDefinition) -> None:
        [prop.set_value(obj, self) for prop in comp_def.properties if hasattr(prop, "set_value")]

    def apply_conf_props(self, obj: Any, conf_def: ConfigurationDefinition) -> None:
        conf_def.properties.set_value(obj, self)

    def add_components(self, comps: dict[CompId, object]):
        self.components.update(comps)


class ApplicationContext(ComponentContainer):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ApplicationContext, self).__init__()
        atexit.register(self.shutdown_hook)

    def import_comp_file(self, comp_file: str, parser: CompositionParser) -> None:
        comp_defs = parser.parse(comp_file)
        self._update_preexisting_comp(list(comp_defs.values()))

        for id_, comp_def in comp_defs.items():
            if id_ in self.comp_defs:
                for prop in comp_def.properties:
                    existing_props = [p for p in self.comp_defs[id_].properties if p.name == prop.name]
                    if len(existing_props) == 1:
                        existing_props[0].value = prop.set_value
                    else:
                        self.comp_defs[id_].properties.append(prop)
            else:
                self.comp_defs[id_] = comp_def

            if not comp_def.lazy_init:
                if comp_def.id not in self.components:
                    self.get_component(comp_def.id, ignore_abstract=True)
                else:
                    self.apply_comp_props(self.components[comp_def.id], comp_def)

        comps = [comp for comp in self.components.values() if isinstance(comp, ObjectPostProcessor)]
        post_processors: list[ObjectPostProcessor] = comps

        for id_, comp in self.components.items():
            if not isinstance(comp, ObjectPostProcessor):
                for post_processor in post_processors:
                    self.components[id_] = post_processor.post_process_before_initialization(comp, id_)

        for comp in self.components.values():
            self._apply(comp)

        for comp_name, comp in self.components.items():
            if not isinstance(comp, ObjectPostProcessor):
                for post_processor in post_processors:
                    self.components[comp_name] = post_processor.post_process_after_initialization(comp, comp_name)

    def import_conf_file(self, conf_file: str, parser: ConfigurationParser) -> None:
        self.conf_defs = parser.parse(conf_file)
        for id_, conf_def in self.conf_defs.items():
            if id_ in self.components:
                self.apply_conf_props(self.components[conf_def.id], conf_def)

    def _update_preexisting_comp(self, comp_defs: list[ComponentDefinition]):
        for comp_def in comp_defs:
            found_comp = ()
            for id_, comp in self.components.items():
                comp_class_name = comp_def.class_.split(".")[-1]
                if comp.__class__.__name__ == comp_class_name:
                    found_comp = (id_, comp)
                    break
            if len(found_comp) == 2:
                self.components.pop(found_comp[0])
                found_comp[1].id = comp_def.id
                self.components[comp_def.id] = found_comp[1]

    def _apply(self, obj: Any) -> None:
        if hasattr(obj, "after_properties_set"):
            obj.after_properties_set()
        if hasattr(obj, "post_process_after_initialization"):
            obj.post_process_after_initialization(self)
        if hasattr(obj, "set_app_context"):
            obj.set_app_context(self)

    def get_components_by_type(self, type_: Any, include_type: bool = True) -> dict[CompId, object]:
        result = {}
        for id_, comp in self.components.items():
            if isinstance(comp, type_):
                if not include_type and type(comp) is type_:
                    continue
                result[id_] = comp
        return result

    def shutdown_hook(self) -> None:
        for id_, comp in self.components.items():
            if isinstance(comp, DisposableObject):
                try:
                    if hasattr(comp, "destroy_method"):
                        destroy_method_name = getattr(comp, "destroy_method")
                    else:
                        destroy_method_name = "destroy"

                    destroy_method = getattr(comp, destroy_method_name)

                except Exception:
                    pass

                else:
                    if callable(destroy_method):
                        try:
                            destroy_method()
                        except Exception:
                            pass

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)


class ApplicationContextAware(object):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.context: ApplicationContext | None = None

    def set_app_context(self, context: ApplicationContext) -> None:
        self.context = context


class ObjectNameAutoProxyCreator(ApplicationContextAware, ObjectPostProcessor):
    """
    classdocs
    """

    def __init__(self, object_names: list[str] | None = None, interceptor_names: list[str] | None = None) -> None:
        """
        Constructor
        """
        super(ObjectNameAutoProxyCreator, self).__init__()
        self.object_names: list[str] = object_names
        self.interceptor_names: list[str] = interceptor_names
