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

from typing import Any,                     \
                   TYPE_CHECKING,           \
                   Optional
from dataclasses import dataclass,          \
                        field

from galaxy.app import constant
from galaxy.utils.type import CompId

if TYPE_CHECKING:
    from galaxy.app.ioc.visitor import Visitor
    from galaxy.app.ioc.factory import ReflectiveObjectFactory
    from galaxy.app.ioc.ioc import ComponentContainer


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False)
           #match_args=True,
           #kw_only=False,
           #slots=True,
           #weakref_slot=False
class ComponentDefinition(object):
    """
    classdocs
    """
    id: CompId
    class_: str | None = field(init=False)

    # Object Factory
    factory: Optional["ReflectiveObjectFactory"] = field(init=False)

    # Properties
    properties: list = field(init=False, default_factory=list)

    scope: str = field(init=False, default=constant.SINGLETON)
    lazy_init: bool = field(init=False, default=False)
    abstract: bool = field(init=False, default=False)
    _parent_id: CompId | None = field(init=False)

    # Positional constructors
    pos_constr: list = field(init=False, default_factory=list)

    # Named constructors
    named_constr: dict = field(init=False, default_factory=dict)

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __str__(self) -> str:
        return str(self.id)


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False)
           #match_args=True,
           #kw_only=False,
           #slots=True,
           #weakref_slot=False
class ConfigurationDefinition(object):
    """
    classdocs
    """
    id: CompId

    # Properties
    properties: Optional["DictDefinition"] = field(init=False)

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __str__(self) -> str:
        return str(self.id)


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False)
           #match_args=True,
           #kw_only=False,
           #slots=True,
           #weakref_slot=False
class ReferenceDefinition(object):
    """
    classdocs
    """
    name: str
    ref_comp_id: CompId

    def prefetch(self, container: "ComponentContainer") -> None:
        self.get_value(container)

    def get_value(self, container: "ComponentContainer") -> object:
        return container.get_component(self.ref_comp_id)

    def set_value(self, comp: object, container: "ComponentContainer") -> None:
        setattr(comp, self.name, container.components[self.ref_comp_id])

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __str__(self) -> str:
        return self.name


@dataclass(init=True,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False)
           #match_args=True,
           #kw_only=False,
           #slots=True,
           #weakref_slot=False
class InnerComponentDefinition(object):
    """
    classdocs
    """
    name: str
    inner_comp_def: ComponentDefinition

    def prefetch(self, container: "ComponentContainer") -> Any:
        self.get_value(container)

    def get_value(self, container: "ComponentContainer") -> Any:
        return container.get_component(self.inner_comp_def.id)

    def set_value(self, comp: Any, container: "ComponentContainer") -> None:
        setattr(comp, self.name, self.get_value(container))

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __str__(self) -> str:
        return str(self.name)


@dataclass(init=False,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False)
           #match_args=True,
           #kw_only=False,
           #slots=True,
           #weakref_slot=False
class ValueDefinition(object):
    """
    classdocs
    """
    name: str

    def __init__(self, name: str, value: Any) -> None:
        """
        Constructor
        """
        self.name: str = name
        if value == "True":
            self.value: bool = True
        elif value == "False":
            self.value: bool = False
        else:
            self.value = value

    def scan_value(self, container: "ComponentContainer", value: Any) -> Any:
        if hasattr(value, "get_value"):
            return value.get_value(container)
        elif isinstance(value, tuple):
            new_list = [self.scan_value(container, item) for item in value]
            results = tuple(new_list)
            return results
        elif isinstance(value, list):
            new_list = [self.scan_value(container, item) for item in value]
            return new_list
        elif isinstance(value, set):
            results = set([self.scan_value(container, item) for item in value])
            return results
        elif isinstance(value, frozenset):
            results = frozenset([self.scan_value(container, item) for item in value])
            return results
        else:
            if value == "True":
                return True
            elif value == "False":
                return False
            else:
                return value

    def get_value(self, container: "ComponentContainer") -> Any:
        val = self._replace_refs(self.value, container)
        if val is None:
            return self.value
        else:
            return val

    def set_value(self, comp: Any, container: "ComponentContainer") -> None:
        setattr(comp, self.name, self.value)
        self._replace_refs(comp, container)

    def _replace_refs(self, comp: Any, container: Any):
        """Normal values do nothing for this step. However, sub-classes are defined for
        the various containers, like lists, set, dictionaries, etc., to handle iterating
        through and pre-fetching items."""
        pass

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __str__(self) -> str:
        return self.name


@dataclass(init=False,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False)
           #match_args=True,
           #kw_only=False,
           #slots=True,
           #weakref_slot=False
class DictDefinition(ValueDefinition):
    """
    classdocs
    """

    def __init__(self, name: str, value: Any) -> None:
        """
        Constructor
        """
        super(DictDefinition, self).__init__(name, value)

    def _replace_refs(self, comp: Any, container: "ComponentContainer"):
        for key in self.value.keys():
            if hasattr(self.value[key], "ref"):
                self.value[key] = container.get_component(self.value[key].ref)
            else:
                self.value[key] = self.scan_value(container, self.value[key])

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __str__(self) -> str:
        return self.name


@dataclass(init=False,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False)
           #match_args=True,
           #kw_only=False,
           #slots=True,
           #weakref_slot=False
class ListDefinition(ValueDefinition):
    """
    classdocs
    """

    def __init__(self, name: str, value: Any) -> None:
        """
        Constructor
        """
        super(ListDefinition, self).__init__(name, value)

    def _replace_refs(self, comp: Any, container: "ComponentContainer"):
        for i in range(0, len(self.value)):
            if hasattr(self.value[i], "ref"):
                self.value[i] = container.get_component(self.value[i].ref)
            else:
                self.value[i] = self.scan_value(container, self.value[i])

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __str__(self) -> str:
        return self.name


@dataclass(init=False,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False)
           #match_args=True,
           #kw_only=False,
           #slots=True,
           #weakref_slot=False
class TupleDefinition(ValueDefinition):
    """
    classdocs
    """

    def __init__(self, name: str, value: Any) -> None:
        """
        Constructor
        """
        super(TupleDefinition, self).__init__(name, value)

    def _replace_refs(self, comp: Any, container: "ComponentContainer"):
        new_value = list(self.value)
        for i in range(0, len(new_value)):
            if hasattr(new_value[i], "ref"):
                new_value[i] = container.get_component(new_value[i].ref)
            else:
                new_value[i] = self.scan_value(container, new_value[i])
        try:
            setattr(comp, self.name, tuple(new_value))
        except AttributeError:
            pass
        return tuple(new_value)

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __str__(self) -> str:
        return self.name


@dataclass(init=False,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False)
           #match_args=True,
           #kw_only=False,
           #slots=True,
           #weakref_slot=False
class SetDefinition(ValueDefinition):
    """
    classdocs
    """

    def __init__(self, name: str, value: Any) -> None:
        """
        Constructor
        """
        super(SetDefinition, self).__init__(name, value)

    def _replace_refs(self, comp: Any, container: "ComponentContainer"):
        new_set = set()
        for item in self.value:
            if hasattr(item, "ref"):
                newly_fetched_value = container.get_component(item.ref)
                new_set.add(newly_fetched_value)
            else:
                newly_scanned_value = self.scan_value(container, item)
                new_set.add(newly_scanned_value)
        try:
            setattr(comp, self.name, new_set)
        except AttributeError:
            pass
        return new_set

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __str__(self) -> str:
        return self.name


@dataclass(init=False,
           repr=True,
           eq=True,
           order=False,
           unsafe_hash=False,
           frozen=False)
           #match_args=True,
           #kw_only=False,
           #slots=True,
           #weakref_slot=False
class FrozensetDefinition(ValueDefinition):
    """
    classdocs
    """

    def __init__(self, name: str, value: Any) -> None:
        """
        Constructor
        """
        super(FrozensetDefinition, self).__init__(name, value)

    def _replace_refs(self, comp: Any, container: "ComponentContainer"):
        new_set = set()
        for item in self.value:
            if hasattr(item, "ref"):
                newly_fetched_value = container.get_component(item.ref)
                new_set.add(newly_fetched_value)
            else:
                newly_scanned_value = self.scan_value(container, item)
                new_set.add(newly_scanned_value)
        new_frozenset = frozenset(new_set)
        try:
            setattr(comp, self.name, new_frozenset)
        except AttributeError:
            pass
        except TypeError:
            pass
        return new_frozenset

    def accept(self, visitor: "Visitor"):
        visitor.visit(self)

    def __str__(self) -> str:
        return self.name
