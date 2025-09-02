"""Module with functionality for detecting used local modules."""
import ast
import importlib
import inspect
import site
import sys
import sysconfig
from typing import Set, Tuple


class ModuleFinder:
    """Class with functions for modules detection."""

    def _get_imported_modules(self, name: str, node_iter: ast.NodeVisitor) -> set:
        self.modules = set()
        try:
            filename = inspect.getfile(sys.modules[name])
        except Exception:
            return self.modules
        with open(filename) as f:
            node_iter.visit(ast.parse(f.read()))
        for module_name in self.modules.copy():
            try:
                module = sys.modules[module_name]
            except KeyError:
                module = importlib.import_module(module_name)  # raise ModuleNotFound if module does not present.
            if self.check_module_is_not_local(module_name, module):
                self.modules.remove(module_name)

        return self.modules

    def _visit_import(self, node):
        for name in node.names:
            self.modules.add(name.name)

    def _visit_import_from(self, node):
        if node.module is not None and node.level == 0:
            self.modules.add(node.module)

    def _find_submodules(self, name: str) -> set:
        node_iter = ast.NodeVisitor()
        node_iter.visit_Import = self._visit_import
        node_iter.visit_ImportFrom = self._visit_import_from
        module_set = self._get_imported_modules(name, node_iter)

        for module in module_set:
            if module != name:
                module_set = module_set.union(self._find_submodules(module))

        return module_set

    def find_root_submodules(self, root_name: str = "__main__") -> Set[str]:
        """Find all local submodules used by the root module."""
        if hasattr(sys.modules[root_name], "__file__"):
            submodules: set[str] = self._find_submodules(root_name)
            submodules.add(root_name)
            return submodules

        submodules: set[str] = set()
        for obj_name, obj in inspect.getmembers(sys.modules[root_name]):
            try:
                module_name, module_obj = self.get_module_name_obj_for_classes_funcs_modules(obj_name, obj)
                if self.check_module_is_not_local(module_name, module_obj):
                    continue
                submodules = submodules | {module_name} | self._find_submodules(module_name)
            except TypeError:
                continue
        return (submodules | {root_name}) - {"__builtin__", "__builtins__"}

    @staticmethod
    def get_module_name_obj_for_classes_funcs_modules(obj_name, obj) -> Tuple[str, object]:
        """Get module name and module object for class, function or module."""
        if inspect.isclass(obj) or inspect.isfunction(obj):
            return obj.__module__, sys.modules[obj.__module__]
        if inspect.ismodule(obj):
            return obj_name, obj
        raise TypeError("Object is not either function, class or module")

    @staticmethod
    def import_modules_by_name(names: Set[str]) -> None:
        """Import modules by it's names."""
        for name in names:
            importlib.import_module(name=name)

    @staticmethod
    def check_module_is_not_local(module_name, module_obj):
        """Check if module is local file or not."""
        paths = sysconfig.get_paths()
        return (
            paths["stdlib"] in str(module_obj)
            or paths["platstdlib"] in str(module_obj)
            or paths["platlib"] in str(module_obj)
            or paths["purelib"] in str(module_obj)
            or module_name in sys.builtin_module_names
            or "ML_management" in str(module_obj)
            or (site.USER_SITE) in str(module_obj)
        )

    @staticmethod
    def get_my_caller_module_name() -> str:
        """Return the name of the module in which the function was called or None."""
        module = inspect.getmodule(inspect.stack()[2][0])
        # for example for code, that is result of cloudpickle.load
        # and does not have module.
        if module is None:
            return "__main__"
        return module.__name__
