#!/usr/bin/env python3

"""
** Allows you to make code blocks verbose. **
---------------------------------------------

Examples
--------
>>> from context_verbose.memory import _reset_memory
>>> _reset_memory()
>>> from context_verbose.printer import Printer
>>>
>>> with Printer('Main section') as ctp:
...     ctp.print('Text in main section')
...     for i in range(3):
...         with ctp(f'Subsection {i+1}'):
...             ctp.print('Text in subsection')
...             ctp.print('Text in subsection')
...
Main section
█ Text in main section
█ Subsection 1
█ █ Text in subsection
█ █ Text in subsection
█ Subsection 2
█ █ Text in subsection
█ █ Text in subsection
█ Subsection 3
█ █ Text in subsection
█ █ Text in subsection
"""

# python3 -m pytest --full-trace --doctest-modules context_verbose/

from context_verbose.printer import Printer

__version__ = '2.2.1'
__author__ = 'Robin RICHARD (robinechuca) <serveurpython.oz@gmail.com>'
__license__ = 'GNU Affero General Public License v3 or later (AGPLv3+)'
__all__ = ['Printer', 'printer']

printer = Printer()
