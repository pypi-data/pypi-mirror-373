import os
import logging

_LOGGER = logging.getLogger(__name__)


def get_module_from_module_filepath(module_filepath):

    with open(module_filepath) as f:
        source = f.read()

    c = compile(source, module_filepath, 'exec')

    g = globals()
    g = g.copy()

    exec(c, g)

    return g


def get_module_symbol_with_filepath(module_filepath, name):

    g = get_module_from_module_filepath(module_filepath)
    s = g[name]

    return s


def get_module_symbol_with_reference(root_module_path, reference):

    package_and_module, class_name = reference.rsplit('.', 1)

    rel_package_and_module_filepath_without_extension = package_and_module.replace('.', os.sep)

    package_and_module_filepath_without_extension = os.path.join(root_module_path, rel_package_and_module_filepath_without_extension)
    package_and_module_filepath = package_and_module_filepath_without_extension + '.py'

    _LOGGER.debug("Translating reference [{}]: "
                  "([{}] + [{}]) -> [{}] -> [{}] [{}]".format(
                  reference, root_module_path,
                  rel_package_and_module_filepath_without_extension,
                  package_and_module_filepath_without_extension,
                  package_and_module_filepath, class_name))

    s = get_module_symbol_with_filepath(
            package_and_module_filepath,
            class_name)

    return s
