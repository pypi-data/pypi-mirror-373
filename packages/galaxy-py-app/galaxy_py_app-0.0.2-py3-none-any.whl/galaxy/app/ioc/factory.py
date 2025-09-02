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

from importlib import import_module
from typing import Any
import sys

from galaxy.app import constant
from galaxy.app.ioc.builder import CompDefinitionBuilder,               \
                                   ConfDefinitionBuilder,               \
                                   RefDefinitionBuilder
from galaxy.app.ioc.definition import ComponentDefinition,              \
                                      ConfigurationDefinition,          \
                                      ReferenceDefinition,              \
                                      ValueDefinition,                  \
                                      InnerComponentDefinition,         \
                                      DictDefinition,                   \
                                      ListDefinition,                   \
                                      TupleDefinition,                  \
                                      SetDefinition,                    \
                                      FrozensetDefinition

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


class DefinitionFactory(object):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        self.comp_defs: list[ComponentDefinition] = []
        self.conf_defs: list[ConfigurationDefinition] = []
        self.abstract_comp_defs: dict = {}

    def create_components(self, def_: dict) -> list[ComponentDefinition]:
        # A dictionary of abstract objects, keyed by their IDs, used in
        # traversing the hierarchies of parents; built upfront here for
        # convenience
        for comp in def_["compo"]:
            if "abstract" in comp:
                self.abstract_comp_defs[comp["component"]] = comp

        for comp in def_["compo"]:
            self.comp_defs.append(self._create_comp_def(comp))
        return self.comp_defs

    def create_configurations(self, def_: dict) -> list[ConfigurationDefinition]:
        for conf in def_["config"]:
            self.conf_defs.append(self._create_conf_def(conf))
        return self.conf_defs

    def _map_custom_class(self, comp: dict, mappings: dict[str, str]) -> None:
        for class_name in mappings:
            if class_name in comp:
                comp["class"] = mappings[class_name]
                comp["constructor-args"] = [comp[class_name]]
                break

    def _create_comp_def(self, comp: dict[str, str], prefix: str = "") -> ComponentDefinition:
        if "class" not in comp and "parent" not in comp:
            self._map_custom_class(comp, yaml_mappings)
        builder = CompDefinitionBuilder().id_(comp["component"])                            \
                                         .class_(comp["class"])                             \
                                         .factory(ReflectiveObjectFactory(comp["class"]))   \
                                         .lazy_init(comp.get("lazy-init", False))           \
                                         .abstract(comp.get("abstract", False))
        if "scope" in comp:
            builder.scope(DefinitionFactory._convert_scope(comp["scope"]))
        if "parent" in comp:
            return self._create_child_comp_def(comp,
                                               comp,
                                               self._get_pos_constr(comp),
                                               self._get_named_constr(comp),
                                               self._get_comp_properties(comp))
        else:
            builder.pos_constr(self._get_pos_constr(comp))              \
                   .named_constr(self._get_named_constr(comp))          \
                   .properties(self._get_comp_properties(comp))
            return builder.build()

    def _create_conf_def(self, conf: dict[str, str], prefix: str = "") -> ConfigurationDefinition:
        return ConfDefinitionBuilder().id_(conf["component"])                       \
                                      .properties(self._get_conf_properties(conf))       \
                                      .build()

    @staticmethod
    def _convert_scope(scope: str) -> str:
        if scope == "prototype":
            return constant.PROTOTYPE
        elif scope == "singleton":
            return constant.SINGLETON
        else:
            raise Exception("Can not handle scope {}".format(scope))

    def _create_child_comp_def(self,
                               leaf: dict[str, str],
                               child_comp: dict[str, str],
                               pos_constr: list,
                               named_constr: dict,
                               properties: list) -> ComponentDefinition:
        parent = self.abstract_comp_defs[child_comp["parent"]]

        # At this point we only build up the lists of parameters but we don't create
        # the object yet because the current parent object may still have its
        # own parent.

        # Positional constructors
        parent_pos_constrs = self._get_pos_constr(parent)

        # Make sure there are as many child positional parameters as there
        # are in the parent's list
        if len(pos_constr) < len(parent_pos_constrs):
            pos_constr.extend([None] * (len(parent_pos_constrs) - len(pos_constr)))

        for idx, parent_pos_constr in enumerate(parent_pos_constrs):
            if not pos_constr[idx]:
                pos_constr[idx] = parent_pos_constr

        # Named constructors
        child_named_constrs = named_constr
        parent_named_constrs = self._get_named_constr(parent)

        for parent_named_constr in parent_named_constrs:
            if parent_named_constr not in child_named_constrs:
                named_constr[parent_named_constr] = parent_named_constrs[parent_named_constr]

        # Properties
        child_properties = [prop.name for prop in properties]
        for parent_prop in self._get_comp_properties(parent):
            if parent_prop.name not in child_properties:
                properties.append(parent_prop)

        if "parent" in parent:
            return self._create_child_comp_def(leaf, parent, pos_constr, named_constr, properties)
        else:
            builder = CompDefinitionBuilder().id_(leaf["component"])                                \
                                             .class_(leaf["class"])                                 \
                                             .factory(ReflectiveObjectFactory(parent["class"]))     \
                                             .lazy_init(leaf.get("lazy-init", False))               \
                                             .abstract(leaf.get("abstract", False))                 \
                                             .pos_constr(pos_constr)                                \
                                             .named_constr(named_constr)                            \
                                             .properties(properties)
            if "scope" in leaf:
                builder.scope(self._convert_scope(leaf["scope"]))
            return builder.build()

    def _get_pos_constr(self, comp: dict) -> list | None:
        if "constructor-args" in comp and isinstance(comp["constructor-args"], list):
            return [self._create_prop_def(comp, constr, comp["object"]) for constr in comp["constructor-args"]]
        return None

    def _get_named_constr(self, comp: dict) -> dict | None:
        if "constructor-args" in comp and isinstance(comp["constructor-args"], dict):
            return dict([(name, self._create_prop_def(comp, constr, comp["object"])) for (name, constr) in comp["constructor-args"].items()])
        return None

    def _get_comp_properties(self, comp: dict) -> list | None:
        if "properties" in comp:
            return [self._create_prop_def(comp, p, name) for (name, p) in comp["properties"].items()]
        return None

    def _get_conf_properties(self, conf: dict) -> DictDefinition | None:
        if "properties" in conf:
            d = {}
            for (name, p) in conf["properties"].items():
                if isinstance(p, dict):
                    d[name] = self._create_prop_def(conf, p, "new_conf.dict['{}']".format(name))
                else:
                    d[name] = self._create_value_def(p, conf["component"], "new_conf.dict['{}']".format(name))
            return DictDefinition("new_conf", d)
        return None

    def _create_ref_def(self, ref_node: Any, name: str) -> ReferenceDefinition:
        if "component" in ref_node:
            return ReferenceDefinition(name, ref_node["component"])
        else:
            builder = RefDefinitionBuilder().name(name).ref_comp_id(ref_node)
            return builder.build()

    def _create_value_def(self, value_node: Any, id_: str, name: str) -> ValueDefinition:
        if isinstance(value_node, dict):
            if "tuple" in value_node:
                return self._create_tuple_def(value_node["tuple"], id_, name)
            elif "list" in value_node:
                return self._create_list_def(value_node["list"], id_, name)
            elif "dict" in value_node:
                return self._create_dict_def(value_node["dict"], id_, name)
            elif "set" in value_node:
                return self._create_set_def(value_node["set"], id_, name)
            elif "frozenset" in value_node:
                return self._create_frozenset_def(value_node["frozenset"], id_, name)
        else:
            return value_node

    def _create_dict_def(self, dict_node: Any, id_: str, name: str) -> DictDefinition:
        d = {}
        for (k, v) in dict_node.items():
            if isinstance(v, dict):
                if "ref" in v:
                    d[k] = self._create_ref_def(v["ref"], "{}.dict['{}']".format(name, k))
                elif "tuple" in v:
                    d[k] = self._create_tuple_def(v["tuple"], id_, "{}.dict['{}']".format(name, k))
                else:
                    d[k] = self._create_dict_def(v, id_, "{}.dict['{}']".format(name, k))
            else:
                d[k] = self._create_value_def(v, id_, "{}.dict['{}']".format(name, k))
        return DictDefinition(name, d)

    def _create_list_def(self, list_node: list, id_: str, name: str) -> ListDefinition:
        list_ = []
        for item in list_node:
            if isinstance(item, dict):
                if "ref" in item:
                    list_.append(self._create_ref_def(item["ref"], "{}.list[{}]".format(name, len(list_))))
                elif "object" in item:
                    list_.append(self._create_inner_comp_def(item, id_, "{}.list[{}]".format(name, len(list_))))
                elif len({"dict", "tuple", "set", "frozenset", "list"} & set(item)) > 0:
                    list_.append(self._create_value_def(item, id_, "{}.list[{}]".format(name, len(list_))))
            else:
                list_.append(item)
        return ListDefinition(name, list_)

    def _create_tuple_def(self, tuple_node: tuple, id_: str, name: str) -> TupleDefinition:
        list_ = []
        for item in tuple_node:
            if isinstance(item, dict):
                if "ref" in item:
                    list_.append(self._create_ref_def(item["ref"], name + ".tuple"))
                elif "object" in item:
                    list_.append(self._create_inner_comp_def(item, id_, "{}.tuple[{}]".format(name, len(list_))))
                elif len({"dict", "tuple", "set", "frozenset", "list"} & set(item)) > 0:
                    list_.append(self._create_value_def(item, id_, "{}.tuple[{}]".format(name, len(list_))))
            else:
                list_.append(item)
        return TupleDefinition(name, tuple(list_))

    def _create_set_def(self, set_node: set, id_: str, name: str) -> SetDefinition:
        s = set()
        for item in set_node:
            if isinstance(item, dict):
                if "ref" in item:
                    s.add(self._create_ref_def(item["ref"], name + ".set"))
                elif "object" in item:
                    s.add(self._create_inner_comp_def(item, id_, "{}.set[{}]".format(name, len(s))))
                elif len({"dict", "tuple", "set", "frozenset", "list"} & set(item)) > 0:
                    s.add(self._create_value_def(item, id_, "{}.set[{}]".format(name, len(s))))
            else:
                s.add(item)
        return SetDefinition(name, s)

    def _create_frozenset_def(self, frozenset_node: set, id_: str, name: str) -> FrozensetDefinition:
        item = self._create_set_def(frozenset_node, id_, name)
        return FrozensetDefinition(name, frozenset(item.value))

    def _create_inner_comp_def(self, comp: dict, id_: str, name: str) -> InnerComponentDefinition:
        inner_comp_def = self._create_comp_def(comp, prefix="{}.{}".format(id_, name))
        self.comp_defs.append(inner_comp_def)
        return InnerComponentDefinition(name, inner_comp_def)

    def _create_prop_def(self, comp: dict, properties: Any, name: str) -> Any:
        # This function translates object properties into useful collections of information for the container.
        if isinstance(properties, dict):
            if "ref" in properties:
                return self._create_ref_def(properties["ref"], name)
            elif "tuple" in properties:
                return self._create_tuple_def(properties["tuple"], comp["component"], name)
            elif "set" in properties:
                return self._create_set_def(properties["set"], comp["component"], name)
            elif "frozenset" in properties:
                return self._create_frozenset_def(properties["frozenset"], comp["component"], name)
            elif "object" in properties:
                return self._create_inner_comp_def(properties, comp["component"], name)
            else:
                return self._create_dict_def(properties, comp["component"], name)
        elif isinstance(properties, list):
            return self._create_list_def(properties, comp["component"], name)
        else:
            return ValueDefinition(name, properties)


class ObjectFactory(object):
    """
    classdocs
    """

    def create(self, constr, named_constr):
        raise NotImplementedError()


class ReflectiveObjectFactory(ObjectFactory):
    """
    classdocs
    """

    def __init__(self, module_and_class: str) -> None:
        """
        Constructor
        """
        self.module_and_class: str = module_and_class

    def create(self, constr: tuple, named_constr: dict) -> object:
        parts = self.module_and_class.split(".")
        module_name = ".".join(parts[:-1])
        class_name = parts[-1]
        if module_name == "":
            return import_module(class_name)(*constr, **named_constr)
        else:
            import_module(module_name)
            cls = getattr(sys.modules[module_name], class_name)
            try:
                o = cls(*constr, **named_constr)
            except Exception as e:
                print(e)
            return o

    def __str__(self) -> str:
        return "ReflectiveObjectFactory({})".format(self.module_and_class)


class PythonObjectFactory(ObjectFactory):
    """
    classdocs
    """

    def __init__(self, method, wrapper) -> None:
        """
        Constructor
        """
        self.method = method
        self.wrapper = wrapper

    def create(self, constr: list, named_constr: dict) -> Any:

        # Setting wrapper's top_func can NOT be done earlier than this method call,
        # because it is tied to a wrapper decorator, which may not have yet been
        # generated.
        self.wrapper.func_globals["top_func"] = self.method.func_name

        # Because @object-based objects use direct code to specify arguments, and NOT
        # external configuration data, this factory doesn't care about the incoming arguments.

        return self.method()

    def __str__(self) -> str:
        return "PythonObjectFactory({})".format(self.method)
