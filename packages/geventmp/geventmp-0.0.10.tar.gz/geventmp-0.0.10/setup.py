#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'geventmp',
        version = '0.0.10',
        description = 'Multiprocessing Gevent Extension',
        long_description = "===============================================\n GeventMP_ - Gevent_ Multiprocessing Extension\n===============================================\n\n.. image:: https://img.shields.io/gitter/room/karellen/Lobby?logo=gitter\n   :target: https://app.gitter.im/#/room/#karellen_Lobby:gitter.im\n   :alt: Gitter\n.. image:: https://img.shields.io/github/actions/workflow/status/karellen/geventmp/build.yml?branch=master\n   :target: https://github.com/karellen/geventmp/actions/workflows/build.yml\n   :alt: Build Status\n.. image:: https://img.shields.io/coveralls/github/karellen/geventmp/master?logo=coveralls\n   :target: https://coveralls.io/r/karellen/geventmp?branch=master\n   :alt: Coverage Status\n\n|\n\n.. image:: https://img.shields.io/pypi/v/geventmp?logo=pypi\n   :target: https://pypi.org/project/geventmp/\n   :alt: GeventMP Version\n.. image:: https://img.shields.io/pypi/pyversions/geventmp?logo=pypi\n   :target: https://pypi.org/project/geventmp/\n   :alt: GeventMP Python Versions\n.. image:: https://img.shields.io/pypi/dd/geventmp?logo=pypi\n   :target: https://pypi.org/project/geventmp/\n   :alt: GeventMP Downloads Per Day\n.. image:: https://img.shields.io/pypi/dw/geventmp?logo=pypi\n   :target: https://pypi.org/project/geventmp/\n   :alt: GeventMP Downloads Per Week\n.. image:: https://img.shields.io/pypi/dm/geventmp?logo=pypi\n   :target: https://pypi.org/project/geventmp/\n   :alt: GeventMP Downloads Per Month\n\n|\n\n.. warning::\n    HIC SUNT DRACONES!!!\n\n    This code is experimental (beta). There is some testing, but a lots of things are in flux, and\n    some platforms don't work at all.\n\n    You MAY try to use this in production with the understanding that this is a beta-quality software.\n\n    That said, this code may crash your server, bankrupt your company, burn your house down and be mean\n    to your puppy.\n\n    You've been warned.\n\nProblem\n=======\n\nDue to internal implementation, `multiprocessing` (`MP`) is unsafe to use with Gevent_ even when `monkey-patched`__.\nNamely, the use of OS semaphore primitives and inter-process IO in `MP` will cause the main\nloop to stall/deadlock/block (specific issue depends on the version of CPython).\n\n__ monkey_\n\nSolution\n========\nGeventMP_ (`Gee-vent Em-Pee`) is a gevent_ multiprocessing extension plugin for the `monkey-patching`__ subsystem.\nAs with the rest of the monkey patch subsystem the process is fairly clear:\n\n__ monkey_\n\n1. Identify all places where blocking occurs and where it may stall the loop.\n2. If blocking occurs on a file descriptor (`FD`), try to convert the file descriptor from blocking to non-blocking\n   (sockets/pipes/fifos, sometimes even files where, rarely, appropriate) and replace blocking IO functions with their\n   gevent_ non-blocking equivalents.\n3. If blocking occurs in a Python/OS primitive that does not support non-blocking access and thus cannot be geventized,\n   wrap all blocking access to that primitive with native thread-pool-based wrappers and call it a day (while fully\n   understanding that primitive access latency will increase and raw performance may suffer as a result).\n4. If you are really brave and have lots of free time on your hands, completely replace a standard blocking Python\n   non-`FD`-based primitive with implementation based on an `FD`-based OS primitive (e.g. POSIX semaphore =>\n   Linux `eventfd-based semaphore for kernels > 2.6.30`__).\n5. Due to launching of separate processes in `MP`, figure out how, when, and whether to `monkey-patch`__ spawned/forked\n   children and grandchildren.\n\n__ eventfd_\n\n__ monkey_\n\nInstallation\n============\nThe package is hosted on PyPi_.\n\nFor stable version:\n\n.. code-block:: bash\n\n  pip install geventmp\n\nFor unstable version:\n\n.. code-block:: bash\n\n  pip install --pre geventmp\n\n\nOnce installed, `GeventMP`_ will activate by default in the below stanza.\n\n.. code-block:: python\n\n   from gevent.monkey import patch_all\n   patch_all()\n\nIf you would like `GeventMP`_ to not activate by default, either do not install it or explicitly disable it:\n\n.. code-block:: python\n\n   from gevent.monkey import patch_all\n   patch_all(geventmp=False)\n\nThat's it - there are no other flags, settings, properties or config values so far.\n\nSupported Platforms\n===================\n\n.. note::\n    All claims of support may not be real at all. You're welcome to experiment. See warnings on top.\n\n* Linux and Darwin.\n* CPython 3.9, 3.10, 3.11, 3.12, 3.13\n* PyPy 3.9, 3.10\n\nTODO\n====\n1. Monkey patch Windows to the extent possible.\n2. Lots of applications use `Billiard <https://github.com/celery/billiard>`_ for multiprocessing instead of stock Python\n   package. Consider monkey patching Billiard if detected.\n\nContact Us\n==========\n\nPost feedback and issues on the `Bug Tracker`_, `Gitter`_,\nand `Twitter (@karelleninc)`_.\n\n.. _Gevent: https://github.com/gevent/gevent/\n.. _geventmp: https://github.com/karellen/geventmp\n.. _bug tracker: https://github.com/karellen/geventmp/issues\n.. _gitter: https://gitter.im/karellen/Lobby\n.. _twitter (@karelleninc): https://twitter.com/karelleninc\n.. _monkey: https://en.wikipedia.org/wiki/Monkey_patch\n.. _eventfd: https://linux.die.net/man/2/eventfd\n.. _pypi: https://pypi.org/project/geventmp/\n",
        long_description_content_type = 'text/x-rst; charset=UTF-8',
        classifiers = [
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Programming Language :: Python :: 3.13',
            'Programming Language :: Python :: 3.14',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX',
            'Topic :: Internet',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Intended Audience :: Developers',
            'Development Status :: 4 - Beta'
        ],
        keywords = 'gevent multiprocessing mp monkey',

        author = 'Karellen, Inc.',
        author_email = 'supervisor@karellen.co',
        maintainer = 'Arcadiy Ivanov',
        maintainer_email = 'arcadiy@ivanov.biz',

        license = 'Apache-2.0',

        url = 'https://github.com/karellen/geventmp',
        project_urls = {
            'Bug Tracker': 'https://github.com/karellen/geventmp/issues',
            'Documentation': 'https://github.com/karellen/geventmp/',
            'Source Code': 'https://github.com/karellen/geventmp/'
        },

        scripts = [],
        packages = [
            'geventmp',
            'geventmp._mp',
            'geventmp._mp.3'
        ],
        namespace_packages = [],
        py_modules = [],
        entry_points = {
            'gevent.plugins.monkey.will_patch_all': ['geventmp = geventmp.monkey:_patch_mp']
        },
        data_files = [],
        package_data = {
            'geventmp': ['LICENSE']
        },
        install_requires = ['gevent>=25.8.2'],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '>=3.9',
        obsoletes = [],
    )
