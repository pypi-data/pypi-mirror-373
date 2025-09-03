import sys

try:
    from importlib.util import find_spec
    from importlib.abc import MetaPathFinder
except ImportError:
    find_spec = None

from whatap.trace.trace_module_definition import IMPORT_HOOKS, PLUGIN

from whatap import logging
from whatap.conf.configure import Configure as conf


def load_module(module, fullname):
    # if conf.dev:
    #     logging.debug(fullname)

    try:
        if fullname in IMPORT_HOOKS:
            wfullname = IMPORT_HOOKS[fullname]['module']
            wmodule = sys.modules.get(wfullname)
            if not wmodule:
                __import__(wfullname)
                wmodule = sys.modules.get(wfullname)

            if wfullname.endswith('plugin'):
                module = {'module': module, 'class_defs': PLUGIN[fullname]}

            getattr(wmodule,
                    IMPORT_HOOKS[fullname]['def'])(module)
            logging.info("successfully injected %s as %s", fullname, wfullname)
        else:
            if conf.debug:
                logging.info("non-injected module %s ", fullname)
    except Exception as e:
        logging.debug(e, exc_info=True)
    finally:
        return module


class _ImportHookLoader(object):
    def load_module(self, fullname):
        module = sys.modules[fullname]
        return load_module(module, fullname)


class _ImportHookChainedLoader(object):
    def __init__(self, loader):
        self.loader = loader

    def load_module(self, fullname):
        module = self.loader.load_module(fullname)
        return load_module(module, fullname)


class ImportFinder(MetaPathFinder):
    def __init__(self):
        self._hooks = {}

    def find_spec(self, fullname, path=None, target=None):
        if fullname not in IMPORT_HOOKS \
                or fullname.startswith('whatap') \
                or fullname.startswith('pip'):

            if conf.debug:
                logging.info("non-injected module %s ", fullname)

            return None

        if fullname in self._hooks:
            return None
        self._hooks[fullname] = True

        # if conf.dev:
        #     logging.debug(fullname)

        try:
            if find_spec:
                spec = find_spec(fullname, path)
                if spec and spec.loader:
                    spec.loader = _ImportHookChainedLoader(spec.loader)
                    return spec
            else:
                __import__(fullname)
                return _ImportHookLoader()

        except Exception as e:
            if conf.dev:
                print(e)
            return
