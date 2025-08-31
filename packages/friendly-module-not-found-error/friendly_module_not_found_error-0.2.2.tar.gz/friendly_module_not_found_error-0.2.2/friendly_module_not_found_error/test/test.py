import traceback
import unittest
import os
import sys, types, importlib.abc, importlib.util

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

MODULE_TREE = {
    "__init__": "print('mymodule init'); x = 1",
    "submodule": "print('submodule init'); y = 2",
    "subpackage": {
        "__init__": "print('subpackage init'); z = 3"
    }
}

class DictLoader(importlib.abc.Loader):
    def __init__(self, fullname, node):
        self.fullname = fullname
        self.node = node

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        if isinstance(self.node, dict):
            code = self.node.get("__init__")
        else:
            code = self.node
        if code:
            exec(code, module.__dict__)

class DictFinder(importlib.abc.MetaPathFinder):
    def __init__(self, name, tree):
        self.name = name
        self.tree = tree

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith(self.name):
            return None
        parts = fullname.split(".")
        node = self.tree
        for p in parts[1:]:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return None
        loader = DictLoader(fullname, node)
        ispkg = isinstance(node, dict)
        return importlib.util.spec_from_loader(fullname, loader, is_package=ispkg)

    def __find__(self, name=None):
        if not name:
            return [self.name]
        else:
            name_list = name.split(".")
            if name_list[0] != self.name:
                return []
            module_dict = self.tree
            for i in name_list[1:]:
                if i not in module_dict:
                    return []
                module_dict = module_dict[i]
            a = list(module_dict.keys()) # wrong in code
            a.append("a")
            return a

sys.meta_path.insert(0, DictFinder("mymodule", MODULE_TREE))

class ExceptionTest(unittest.TestCase):
    def test_top_import_exception(self):
        import_error_tuple = (
            ("import ant", ModuleNotFoundError, "No module named 'ant'. Did you mean: 'ast'?"),
        )
        for i in import_error_tuple:
            if i:
                self.check_message(i[0], i[1], i[2])

    def test_non_packages_import_exception(self):
        import_error_tuple = (
            ("import os.path.a", ModuleNotFoundError,
             "module 'os.path' has no child module 'a'; 'os.path' is not a package"),
            ("import ast.a", ModuleNotFoundError, "module 'ast' has no child module 'a'; 'ast' is not a package")
        )
        for i in import_error_tuple:
            if i:
                self.check_message(i[0], i[1], i[2])

    def test_packages_import_exception(self):
        import_error_tuple = (
            ("import multiprocessing.dumy", ModuleNotFoundError,
             "module 'multiprocessing' has no child module 'dumy'. Did you mean: 'dummy'?"),
        )
        for i in import_error_tuple:
            if i:
                self.check_message(i[0], i[1], i[2])

    def test_wrong_module_exception(self):
        import_error_tuple = (
            ("import wrong_module", ModuleNotFoundError,
             "module 'wrong_module' has no child module 'wrong_module'"),
            ("import wrong_child_module.wrong_child_module", ModuleNotFoundError,
             "module 'wrong_child_module.wrong_child_module' has no child module 'wrong_child_module'. Did you mean: 'wrong_child_modules'?")
        )
        for i in import_error_tuple:
            if i:
                self.check_message(i[0], i[1], i[2])

    def test_custom_module_hook(self):
        import_error_tuple = (
            ("import module", ModuleNotFoundError, "No module named 'module'. Did you mean: 'mymodule'"),
            ("import mymodule.a", ModuleNotFoundError, "module 'mymodule' has no child module 'a', but it appear in the final result from '__find__'. Is your code wrong?"),
            ("import mymodule.submodule.b", ModuleNotFoundError, "module 'mymodule.submodule' has no child module 'b'; 'mymodule.submodule' is not a package"),
            ("import mymodule.subpackage.aa", ModuleNotFoundError, " module 'mymodule.subpackage' has no child module 'aa'. Did you mean: 'a'?")
        )
        for i in import_error_tuple:
            if i:
                self.check_message(i[0], i[1], i[2])

    def check_message(self, code, exc_type, exc_msg):
        try:
            exec(code)
        except exc_type:
            self.assertIn(exc_msg, traceback.format_exc())


main = unittest.main

if __name__ == '__main__':
    main()
