# coding: utf-8
from __future__ import absolute_import

import os.path
import sys
from traceback import format_exc


def setup_syspath(package_root, current_dir=None):
    """
    Set up `sys.path` for import resolution.

    :param package_root: Package root directory path. Will be added to \
        `sys.path`. In the repository the package root directory is `src`. \
        After installation the package root directory is `site-packages`.

    :param current_dir: Current directory path. If given, will be removed \
        from `sys.path`.

    :return: None.
    """
    removing_dirs = ['', '.']

    if current_dir is not None:
        current_dir = os.path.abspath(current_dir)

        removing_dirs.append(current_dir)

    for path in removing_dirs:
        while True:
            try:
                sys.path.remove(path)
            except ValueError:
                break

    package_root = os.path.abspath(package_root)

    dep_root = os.path.join(package_root, 'aoiktopdownparserdep')

    if os.path.isdir(dep_root) and dep_root not in sys.path:
        sys.path.insert(0, dep_root)

    if os.path.isdir(package_root) and package_root not in sys.path:
        sys.path.insert(0, package_root)

    pythonpath = os.environ.get('PYTHONPATH', '')

    pythonpath_dirs = pythonpath.split(os.pathsep)

    pythonpath_dirs = [os.path.abspath(p) for p in pythonpath_dirs]

    if dep_root not in pythonpath_dirs:
        pythonpath_dirs.insert(0, dep_root)

    if package_root not in pythonpath_dirs:
        pythonpath_dirs.insert(0, package_root)

    new_pythonpath = os.pathsep.join(pythonpath_dirs)

    os.environ['PYTHONPATH'] = new_pythonpath


def main(args=None):
    try:
        setup_syspath(
            package_root=os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ),
            current_dir=os.path.dirname(os.path.abspath(__file__)),
        )

        from aoiktopdownparser.main.main_imp import main_imp

        return main_imp(args)

    except SystemExit:
        raise

    except KeyboardInterrupt:
        return 0

    except BaseException:
        msg = 'Traceback:\n---\n{0}---\n'.format(format_exc())

        sys.stderr.write(msg)

        return 255


if __name__ == '__main__':
    exit(main())
