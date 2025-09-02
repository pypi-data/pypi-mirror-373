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

import yaml
from multipledispatch import dispatch
from typing import Any

from galaxy.app.ioc.definition import ComponentDefinition,          \
                                      ConfigurationDefinition,      \
                                      ReferenceDefinition,          \
                                      InnerComponentDefinition,     \
                                      ValueDefinition,              \
                                      DictDefinition,               \
                                      ListDefinition,               \
                                      TupleDefinition,              \
                                      SetDefinition,                \
                                      FrozensetDefinition
from galaxy.app.ioc.ioc import ApplicationContext
from galaxy.app.app import Application
from galaxy.kernel.kernel import Kernel
from galaxy.service.service import ServiceManager,                  \
                                   ServiceAsyncManager,             \
                                   Manager,                         \
                                   AsyncManager,                    \
                                   Service,                         \
                                   AsyncService
from galaxy.net.net import NetworkService,                          \
                           NetworkAsyncService,                     \
                           Client,                                  \
                           AsyncClient,                             \
                           Server,                                  \
                           AsyncServer
from galaxy.utils.pattern import Visitor
from galaxy.utils.type import TypeUtility
from galaxy.proc.proc import ProcessManager,                        \
                             ProcessAsyncManager,                   \
                             Process,                               \
                             AsyncProcess


class PrintVisitor(Visitor):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(PrintVisitor, self).__init__()

    @dispatch(ComponentDefinition)
    def visit(self, def_: ComponentDefinition) -> None:
        self._print_comp_def(def_)

    def _print_comp_def(self, def_: ComponentDefinition, level: int | None = 0) -> None:
        print("{}component = {}".format("\t" * level, def_.id))
        print("{}scope = {}".format("\t" * (level + 1), def_.scope))
        print("{}properties :".format("\t" * (level + 1)))
        for prop in def_.properties:
            prop.accept(self)
        print("")

    @dispatch(ConfigurationDefinition)
    def visit(self, def_: ComponentDefinition) -> None:
        print("component = {}".format(def_.id))
        print("properties :")
        for prop in def_.properties:
            prop.accept(self)
        print("")

    @dispatch(ReferenceDefinition)
    def visit(self, def_: ReferenceDefinition) -> None:
        print("ReferenceDefinition - {} : {}".format(def_.name, def_.ref_comp_id))

    @dispatch(InnerComponentDefinition)
    def visit(self, def_: InnerComponentDefinition) -> None:
        print(str(def_))

    @dispatch(ValueDefinition)
    def visit(self, def_: ValueDefinition) -> None:
        print("ValueDefinition - {} : {}".format(def_.name, def_.value))

    @dispatch(DictDefinition)
    def visit(self, def_: DictDefinition) -> None:
        print(str(def_))

    @dispatch(ListDefinition)
    def visit(self, def_: ListDefinition) -> None:
        print(str(def_))

    @dispatch(TupleDefinition)
    def visit(self, def_: TupleDefinition) -> None:
        print(str(def_))

    @dispatch(SetDefinition)
    def visit(self, def_: SetDefinition) -> None:
        print(str(def_))

    @dispatch(FrozensetDefinition)
    def visit(self, def_: FrozensetDefinition) -> None:
        print(str(def_))


class Quoted(str):
    pass


class YamlStatusVisitor(Visitor):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(YamlStatusVisitor, self).__init__()
        self.res: dict[str, Any] | None = None
        self._init_yaml()

    def _init_yaml(self):
        def quoted_presenter(dumper, data):
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')

        yaml.add_representer(Quoted, quoted_presenter)
        yaml.representer.SafeRepresenter.add_representer(Quoted, quoted_presenter)

    @dispatch(ApplicationContext)
    def visit(self, obj: ApplicationContext) -> None:
        apps = obj.get_components_by_type(Application)
        res = {}
        if len(apps) > 0:
            self.visit(list(apps.values())[0], depth=True)
            res["status"] = self.res
        self.res = res

    @dispatch(Application, depth=bool)
    def visit(self, obj: Application, depth: bool = False) -> None:
        res = {
               "id": str(obj.id),
               "name": Quoted(obj.name),
               "type": TypeUtility.classname(obj),
               "status": obj.state
              }
        if depth:
            if hasattr(obj, "kernel") and obj.kernel is not None:
                self.visit(obj.kernel)
                res["kernel"] = self.res
            if hasattr(obj, "service") and obj.service is not None:
                self.visit(obj.service, depth=depth)
                res["service_mgr"] = self.res
            if hasattr(obj, "proc") and obj.proc is not None:
                self.visit(obj.proc, depth=depth)
                res["proc_mgr"] = self.res
        self.res = res

    @dispatch((ServiceManager, ServiceAsyncManager), depth=bool)
    def visit(self, obj: ServiceManager | ServiceAsyncManager, depth: bool = False) -> None:
        res = {
               "id": str(obj.id),
               "name": Quoted(obj.name),
               "type": TypeUtility.classname(obj),
               "status": obj.state
              }
        if depth and hasattr(obj, "managers") and obj.managers is not None and len(obj.managers) > 0:
            res["managers"] = []
            for mgr in obj.managers.values():
                self.visit(mgr, depth=depth)
                res["managers"].append(self.res)
        self.res = res

    @dispatch((ProcessManager, ProcessAsyncManager), depth=bool)
    def visit(self, obj: ProcessManager | ProcessAsyncManager, depth: bool = False) -> None:
        res = {
               "id": str(obj.id),
               "name": Quoted(obj.name),
               "type": TypeUtility.classname(obj),
               "status": obj.state
              }
        if depth and hasattr(obj, "procs") and obj.procs is not None and len(obj.procs) > 0:
            res["procs"] = []
            for proc in obj.procs.values():
                self.visit(proc)
                res["procs"].append(self.res)
        self.res = res

    @dispatch((Manager, AsyncManager), depth=bool)
    def visit(self, obj: Manager | AsyncManager, depth: bool = False) -> None:
        res = {
               "id": str(obj.id),
               "name": Quoted(obj.name),
               "type": TypeUtility.classname(obj),
               "status": obj.state
              }
        if depth and hasattr(obj, "services") and obj.services is not None and len(obj.services) > 0:
            res["services"] = []
            for srv in obj.services.values():
                self.visit(srv, depth=depth)
                res["services"].append(self.res)
        self.res = res

    @dispatch((Service, AsyncService), depth=bool)
    def visit(self, obj: Service | AsyncService, depth: bool = False) -> None:
        res = {
               "id": str(obj.id),
               "name": Quoted(obj.name),
               "type": TypeUtility.classname(obj),
               "status": obj.state
              }
        if depth and (isinstance(obj, NetworkService) or isinstance(obj, NetworkAsyncService)):
            if hasattr(obj, "servers") and obj.servers is not None and len(obj.servers) > 0:
                res["servers"] = []
                for srv in obj.servers.values():
                    self.visit(srv)
                    res["servers"].append(self.res)
            if hasattr(obj, "clients") and obj.clients is not None and len(obj.clients) > 0:
                res["clients"] = []
                for client in obj.clients.values():
                    self.visit(client)
                    res["clients"].append(self.res)
        self.res = res

    @dispatch((Kernel, Server, AsyncServer, Client, AsyncClient, Process, AsyncProcess))
    def visit(self, obj: Kernel | Server | AsyncServer | Client | AsyncClient | Process | AsyncProcess) -> None:
        self.res = {
                    "id": str(obj.id),
                    "name": Quoted(obj.name),
                    "type": TypeUtility.classname(obj),
                    "status": obj.state
                   }


class YamlCompositionVisitor(Visitor):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(YamlCompositionVisitor, self).__init__()
        self.res: dict[str, Any] | list | None = None
        self._init_yaml()

    def _init_yaml(self):
        def quoted_presenter(dumper, data):
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
        yaml.add_representer(Quoted, quoted_presenter)
        yaml.representer.SafeRepresenter.add_representer(Quoted, quoted_presenter)

    @dispatch(ApplicationContext)
    def visit(self, context: ApplicationContext) -> None:
        res = []
        for comp_def in context.comp_defs.values():
            self.visit(comp_def)
            res.append(self.res)
        self.res = res

    @dispatch(ComponentDefinition)
    def visit(self, comp_def: ComponentDefinition) -> None:
        props = {}
        for prop in comp_def.properties:
            self.visit(prop)
            props.update(self.res)
        self.res = {
                    "component": str(comp_def.id),
                    "class": comp_def.class_,
                    "scope": comp_def.scope,
                    "lazy-init": comp_def.lazy_init,
                    "properties": props
                   }

    @dispatch(ReferenceDefinition)
    def visit(self, prop_def: ReferenceDefinition) -> None:
        self.res = {prop_def.name: "{{ref: {}}}".format(str(prop_def.ref_comp_id))}

    @dispatch(InnerComponentDefinition)
    def visit(self, prop_def: ReferenceDefinition) -> None:
        self.res = {}

    @dispatch(ValueDefinition)
    def visit(self, prop_def: ValueDefinition) -> None:
        if isinstance(prop_def.value, str):
            self.res = {prop_def.name: Quoted(prop_def.value)}
        else:
            self.res = {prop_def.name: prop_def.value}

    @dispatch(DictDefinition)
    def visit(self, prop_def: DictDefinition) -> None:
        self.res = {}

    @dispatch(ListDefinition)
    def visit(self, prop_def: ListDefinition) -> None:
        self.res = {}

    @dispatch(TupleDefinition)
    def visit(self, prop_def: TupleDefinition) -> None:
        self.res = {}

    @dispatch(SetDefinition)
    def visit(self, prop_def: SetDefinition) -> None:
        self.res = {}

    @dispatch(FrozensetDefinition)
    def visit(self, prop_def: FrozensetDefinition) -> None:
        self.res = {}


class YamlConfigurationVisitor(Visitor):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(YamlConfigurationVisitor, self).__init__()
        self.res: dict[str, Any] | list | None = None

    @dispatch(ApplicationContext)
    def visit(self, context: ApplicationContext) -> None:
        res = []
        for conf_def in context.conf_defs.values():
            self.visit(conf_def)
            res.append(self.res)
        self.res = res

    @dispatch(ConfigurationDefinition)
    def visit(self, conf_def: ConfigurationDefinition) -> None:
        self.visit(conf_def.properties)
        props = self.res
        self.res = {
                    "component": str(conf_def.id),
                    "properties": props
                   }

    @dispatch(DictDefinition)
    def visit(self, prop_def: DictDefinition) -> None:
        res = {}
        self._visit_rec(res, prop_def.value)
        self.res = res

    def _visit_rec(self, res: dict, prop_def: dict):
        for name, val in prop_def.items():
            if isinstance(val, str):
                res[name] = Quoted(val)
            elif isinstance(val, dict):
                tmp = {}
                self._visit_rec(tmp, val)
                res[name] = tmp
            else:
                res[name] = val

