"""
# Module friendly_module_not_found_error
It change the message of ModuleNotFoundError to be more friendly.
## Compare
The original message:
```python repl
>>># right module name: multiprocessing.dummy.connection
>>>import multprocessing.dummy.connection
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
ModuleNotFoundError: No module named 'multprocessing.dummy.connection'
>>>import multiprocessing.dumy.connection
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
ModuleNotFoundError: No module named 'multiprocessing.dumy.connection'
>>>import multiprocessing.dummy.connections
Traceback (most recent call last):
  File "<stdin>", line 4, in <module>
ModuleNotFoundError: No module named 'multiprocessing.dummy.connections'
```
The original messages are not friendly, because it does not tell you where is wrong.
The friendly message:
```python repl
>>># right module name: multiprocessing.dummy.connection
>>>import multprocessing.dummy.connection
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
ModuleNotFoundError: No module named 'multprocessing'. Did you mean 'multiprocessing'?
>>>import multiprocessing.dumy.connection
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
ModuleNotFoundError: module 'multiprocessing' has no child module 'dumy'. Did you mean 'dummy'?
>>>import multiprocessing.dummy.connections
Traceback (most recent call last):
  File "<stdin>", line 4, in <module>
ModuleNotFoundError: module 'multiprocessing.dummy' has no child module 'connections'. Did you mean 'connection'?
```
It tell you where is wrong and give you a suggestion.

## Specific implementation
It change the module traceback.
Here is the code of the mainly change in module traceback(python3.13):
```python
def _compute_suggestion_error(exc_value, tb, wrong_name):
    if wrong_name is None or not isinstance(wrong_name, str):
        return None
    if isinstance(exc_value, AttributeError):
        obj = exc_value.obj
        try:
            try:
                d = dir(obj)
            except TypeError:  # Attributes are unsortable, e.g. int and str
                d = list(obj.__class__.__dict__.keys()) + list(obj.__dict__.keys())
            d = sorted([x for x in d if isinstance(x, str)])
            hide_underscored = (wrong_name[:1] != '_')
            if hide_underscored and tb is not None:
                while tb.tb_next is not None:
                    tb = tb.tb_next
                frame = tb.tb_frame
                if 'self' in frame.f_locals and frame.f_locals['self'] is obj:
                    hide_underscored = False
            if hide_underscored:
                d = [x for x in d if x[:1] != '_']
        except Exception:
            return None
    elif isinstance(exc_value, ImportError):
        try:
            mod = __import__(exc_value.name)
            try:
                d = dir(mod)
            except TypeError:  # Attributes are unsortable, e.g. int and str
                d = list(mod.__dict__.keys())
            d = sorted([x for x in d if isinstance(x, str)])
            if wrong_name[:1] != '_':
                d = [x for x in d if x[:1] != '_']
        except Exception:
            return _suggest_for_module(exc_value)  # original code: return None                      
    else:
        assert isinstance(exc_value, NameError)
        # find most recent frame
        if tb is None:
            return None
        while tb.tb_next is not None:
            tb = tb.tb_next
        frame = tb.tb_frame
        d = (
            list(frame.f_locals)
            + list(frame.f_globals)
            + list(frame.f_builtins)
        )
        d = [x for x in d if isinstance(x, str)]

        # Check first if we are in a method and the instance
        # has the wrong name as attribute
        if 'self' in frame.f_locals:
            self = frame.f_locals['self']
            try:
                has_wrong_name = hasattr(self, wrong_name)
            except Exception:
                has_wrong_name = False
            if has_wrong_name:
                return f"self.{wrong_name}"

    return _calculate_closed_name(wrong_name, d) # original code has no function "_calculate_closed_name", it is in this function.

def _calculate_closed_name(wrong_name, d):
    try:
        d.sort()
    except:
        pass
    try:
        import _suggestions
        return _suggestions._generate_suggestions(d, wrong_name)
    except ImportError:
        if len(d) > _MAX_CANDIDATE_ITEMS:
            return None
        wrong_name_len = len(wrong_name)
        if wrong_name_len > _MAX_STRING_SIZE:
            return None
        best_distance = wrong_name_len
        suggestion = None
        d.sort()
        for possible_name in d:
            if possible_name == wrong_name:
                # A missing attribute is "found". Don't suggest it (see GH-88821).
                continue
            # No more than 1/3 of the involved characters should need changed.
            max_distance = (len(possible_name) + wrong_name_len + 3) * _MOVE_COST // 6
            # Don't take matches we've already beaten.
            max_distance = min(max_distance, best_distance - 1)
            current_distance = _levenshtein_distance(wrong_name, possible_name, max_distance)
            if current_distance > max_distance:
                continue
            if not suggestion or current_distance < best_distance:
                suggestion = possible_name
                best_distance = current_distance
        return suggestion

def _suggest_for_module(exc_value):
    import sys
    import os
    from importlib import machinery
    
    def scan_dir(path):
        \"""
        Return all of the packages in the path without import
        contains：
          - .py file
          - directory with "__init__.py"
          - the .pyd/so file that has right ABI
        \"""
        if not os.path.isdir(path):
            return []
    
        suffixes = machinery.EXTENSION_SUFFIXES
        result = []
    
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
    
            # .py file
            if name.endswith(".py") and os.path.isfile(full_path):
                modname = name[:-3]
                if modname.isidentifier():
                    result.append(modname)
    
            # directory with "__init__.py"
            elif os.path.isdir(full_path):
                init_file = os.path.join(full_path, "__init__.py")
                if os.path.isfile(init_file) and name.isidentifier():
                    result.append(name)
    
            # the .pyd/so file that has right ABI
            elif os.path.isfile(full_path):
                for suf in suffixes:
                    if name.endswith(suf):
                        modname = name[:-len(suf)]
                        if modname.isidentifier():
                            result.append(modname)
                        break
    
        return sorted(result)
    
    def find_all_packages():
        list_d = []
        for hook in sys.meta_path:
            try:
                func = getattr(hook, "__find__", None)
                if callable(func):
                    list_d.append(func())
            except:
                list_d.append([])
        for i in sys.path:
            if isinstance(i, str) and not i.endswith("idlelib"):
                list_d.append(scan_dir(i))
        list_d.append(sorted(sys.builtin_module_names))
        return list_d

    def compare_top_module(module_name):
        result = _calculate_closed_name(module_name, sorted(sys.stdlib_module_names))
        if result:
            return result
        other_result_list = []
        for i in list_d:
            result = _calculate_closed_name(module_name, i)
            if result:
                return result

    def handle_hook_module(name, i, wrong_name_list):
        \"""
        ```
        def __find__(self, name: str=None) -> List[str]:
            return []
        ```
        `__find__` method should return a list about the modules without import them.
        when name is not None, it should return the submodule below it.
        \"""
        for j in sys.meta_path:
            try:
                func = getattr(j, "__find__", None)
                if callable(func):
                    list_d = sorted(func(name))
                    if i in list_d:
                        return handle_hook_wrong_module(j, [name + '.' + i] + wrong_name_list)
                    result = _calculate_closed_name(i, list_d)
                    if result:
                        return result
            except:
                continue

    def handle_wrong_module(module_name, path, child_module_list):
        for i in child_module_list:
            exc_value.msg = f"module '{module_name}' has no child module '{i}'"
            if not os.path.exists(path) or not os.path.isdir(path):
                exc_value.msg += f"; {module_name} is not a package"
                return
            list_d = scan_dir(path)
            if i not in list_d:
                return _calculate_closed_name(i, list_d)
            path = os.path.join(path, i)
            module_name += f".{i}"

    def handle_hook_wrong_module(hook, wrong_name_list):
        nonlocal wrong_code_in_find
        module_name = wrong_name_list[0]
        for i in wrong_name_list[1:]:
            exc_value.msg = f"module '{module_name}' has no child module '{i}'"
            try:
                func = getattr(hook, "__find__", None)                
                if callable(func):
                    list_d = sorted(func(module_name))
                    if i not in list_d:                        
                        return _calculate_closed_name(i, list_d)
            except:
                return
            module_name += "." + i
        exc_value.msg += ", but it appear in the final result from '__find__'. Is your code wrong?"
        wrong_code_in_find = True
        
    if not isinstance(exc_value, ModuleNotFoundError):
        return
    list_d = find_all_packages()            
    _module_name = exc_value.name
    wrong_name_list = _module_name.split(".")
    module_name = wrong_name_list[0]
    wrong_code_in_find = False
    if module_name in sys.modules:
        wrong_name_copy = wrong_name_list[1:]
        for i in wrong_name_list[1:]:
            original_module_name = module_name
            module_name += "." + i
            wrong_name_copy.pop(0)
            if module_name in sys.modules:
                continue            
            exc_value.msg = f"module '{original_module_name}' has no child module '{i}'"            
            result = handle_hook_module(original_module_name, i, wrong_name_copy)
            if wrong_code_in_find:
                return
            if result:
                return result
            if hasattr(sys.modules[original_module_name], "__path__"):
                d=[]
                for ii in sys.modules[original_module_name].__path__:
                    list_path = scan_dir(ii)
                    if i in list_path:
                        return handle_wrong_module(module_name, os.path.join(ii, i), wrong_name_copy)
                    d += list_path
                wrong_name = i
                return _calculate_closed_name(wrong_name, d)
            else:                
                exc_value.msg += f"; '{original_module_name}' is not a package"
                return
    else:
        if len(wrong_name_list) == 1 or module_name not in sum(list_d, []):
            return compare_top_module(module_name)
        else:
            for i in sys.meta_path:
                try:
                    func = getattr(i, "__find__", None)
                    if callable(func):
                        if module_name in func():
                            return handle_hook_wrong_module(i, wrong_name_list)
                except:
                    continue
            for i in sys.path:
                if module_name in scan_dir(i):
                    module_path = f"{i}/{module_name}"
                    break
                return compare_top_module(module_name)
            return handle_wrong_module(module_name, module_path, wrong_name_list[1:])
```

Here is a more simple version for it without custom import hooks:
```
def _compute_suggestion_error(exc_value, tb, wrong_name):
    if wrong_name is None or not isinstance(wrong_name, str):
        return None
    if isinstance(exc_value, AttributeError):
        obj = exc_value.obj
        try:
            try:
                d = dir(obj)
            except TypeError:  # Attributes are unsortable, e.g. int and str
                d = list(obj.__class__.__dict__.keys()) + list(obj.__dict__.keys())
            d = sorted([x for x in d if isinstance(x, str)])
            hide_underscored = (wrong_name[:1] != '_')
            if hide_underscored and tb is not None:
                while tb.tb_next is not None:
                    tb = tb.tb_next
                frame = tb.tb_frame
                if 'self' in frame.f_locals and frame.f_locals['self'] is obj:
                    hide_underscored = False
            if hide_underscored:
                d = [x for x in d if x[:1] != '_']
        except Exception:
            return None
    elif isinstance(exc_value, ImportError):
        try:
            mod = __import__(exc_value.name)
            try:
                d = dir(mod)
            except TypeError:  # Attributes are unsortable, e.g. int and str
                d = list(mod.__dict__.keys())
            d = sorted([x for x in d if isinstance(x, str)])
            if wrong_name[:1] != '_':
                d = [x for x in d if x[:1] != '_']
        except Exception:
            return _suggest_for_module(exc_value)                        
    else:
        assert isinstance(exc_value, NameError)
        # find most recent frame
        if tb is None:
            return None
        while tb.tb_next is not None:
            tb = tb.tb_next
        frame = tb.tb_frame
        d = (
            list(frame.f_locals)
            + list(frame.f_globals)
            + list(frame.f_builtins)
        )
        d = [x for x in d if isinstance(x, str)]

        # Check first if we are in a method and the instance
        # has the wrong name as attribute
        if 'self' in frame.f_locals:
            self = frame.f_locals['self']
            try:
                has_wrong_name = hasattr(self, wrong_name)
            except Exception:
                has_wrong_name = False
            if has_wrong_name:
                return f"self.{wrong_name}"

    return _calculate_closed_name(wrong_name, d)

def _calculate_closed_name(wrong_name, d):
    try:
        d.sort()
    except:
        pass
    try:
        import _suggestions
        return _suggestions._generate_suggestions(d, wrong_name)
    except ImportError:
        if len(d) > _MAX_CANDIDATE_ITEMS:
            return None
        wrong_name_len = len(wrong_name)
        if wrong_name_len > _MAX_STRING_SIZE:
            return None
        best_distance = wrong_name_len
        suggestion = None
        d.sort()
        for possible_name in d:
            if possible_name == wrong_name:
                # A missing attribute is "found". Don't suggest it (see GH-88821).
                continue
            # No more than 1/3 of the involved characters should need changed.
            max_distance = (len(possible_name) + wrong_name_len + 3) * _MOVE_COST // 6
            # Don't take matches we've already beaten.
            max_distance = min(max_distance, best_distance - 1)
            current_distance = _levenshtein_distance(wrong_name, possible_name, max_distance)
            if current_distance > max_distance:
                continue
            if not suggestion or current_distance < best_distance:
                suggestion = possible_name
                best_distance = current_distance
        return suggestion

def _suggest_for_module(exc_value):
    import sys
    import os
    from importlib import machinery
    
    def scan_dir(path):
        \"""
        Return all of the packages in the path without import
        contains：
          - .py file
          - directory with "__init__.py"
          - the .pyd/so file that has right ABI
        \"""
        if not os.path.isdir(path):
            return []
    
        suffixes = machinery.EXTENSION_SUFFIXES
        result = []
    
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
    
            # .py file
            if name.endswith(".py") and os.path.isfile(full_path):
                modname = name[:-3]
                if modname.isidentifier():
                    result.append(modname)
    
            # directory with "__init__.py"
            elif os.path.isdir(full_path):
                init_file = os.path.join(full_path, "__init__.py")
                if os.path.isfile(init_file) and name.isidentifier():
                    result.append(name)
    
            # the .pyd/so file that has right ABI
            elif os.path.isfile(full_path):
                for suf in suffixes:
                    if name.endswith(suf):
                        modname = name[:-len(suf)]
                        if modname.isidentifier():
                            result.append(modname)
                        break
    
        return sorted(result)
    
    def find_all_packages():
        return [scan_dir(i) if isinstance(i, str) and
                not i.endswith("idlelib") else []
                for i in sys.path] + [sorted(sys.builtin_module_names)]

    def compare_top_module(module_name):
        result = _calculate_closed_name(module_name, sorted(sys.stdlib_module_names))
        if result:
            return result
        other_result_list = []
        for i in list_d:
            result = _calculate_closed_name(module_name, i)
            if result:
                other_result_list.append(result)
        if other_result_list:
            return other_result_list[0]
        else:
            return

    def handle_wrong_module(module_name, path, child_module_list):
        for i in child_module_list:
            exc_value.msg = f"module '{module_name}' has no child module '{i}'"
            if not os.path.exists(path) or not os.path.isdir(path):
                exc_value.msg += f"; {module_name} is not a package"
                return
            list_d = scan_dir(path)
            if i not in list_d:
                return _calculate_closed_name(i, list_d)
            path = os.path.join(path, i)
            module_name += f".{i}"
        
    if not isinstance(exc_value, ModuleNotFoundError):
        return
    list_d = find_all_packages()            
    _module_name = exc_value.name
    wrong_name_list = _module_name.split(".")
    module_name = wrong_name_list[0]
    if module_name in sys.modules:
        wrong_name_copy = wrong_name_list[1:]
        for i in wrong_name_list[1:]:
            original_module_name = module_name
            module_name += "." + i
            wrong_name_copy.pop(0)
            if module_name in sys.modules:
                continue            
            exc_value.msg = f"module '{original_module_name}' has no child module '{i}'"
            if hasattr(sys.modules[original_module_name], "__path__"):
                d=[]
                for ii in sys.modules[original_module_name].__path__:
                    list_path = scan_dir(ii)
                    if i in list_path:
                        return handle_wrong_module(module_name, os.path.join(ii, i), wrong_name_copy)
                    d += list_path
                wrong_name = i
                return _calculate_closed_name(wrong_name, d)
            else:
                exc_value.msg += f"; '{original_module_name}' is not a package"
                return
    else:
        if len(wrong_name_list) == 1 or module_name not in sum(list_d, []):
            return compare_top_module(module_name)
        else:
            for i in sys.path:
                if module_name in scan_dir(i):
                    module_path = f"{i}/{module_name}"
                    break
            else:
                return compare_top_module(module_name)
            return handle_wrong_module(module_name, module_path, wrong_name_list[1:])
```
The other change here: in the class "TracebackException", it needs an enter for the exception "ModuleNotFoundError"
"""


import sys
import importlib

major, minor = sys.version_info[:2]
submodule_name = f"{__name__}.traceback-{major}-{minor}"
try:
    module = importlib.import_module(submodule_name)
    sys.modules["traceback"] = module
except ImportError as e:
    pass
