
***********************************************************
Library to improve the display of your code in the console.
***********************************************************

By adding only a few lines of code at strategic places in your program, you will get a nice console display that will let you know what stage your code is at.

fork of **context-printer**:
----------------------------

This project is a fork of the `context_printer <https://pypi.org/project/context-printer/>`_ project. The philosophy of this project is strictly the same as the original project. Nevertheless, this project offers the following improvements:

* Support for the ``with`` keyword (context manager).
* Formatting of exceptions for better debugging.
* Added decorator behavior.
* Possibility to implicitly name a section.
* More formatting possible (adding highlighting and flashing).
* No conflicts between thread and process (clients send text to a single server).
* Integrated timer for display the sections duration.

Basic usage example:
--------------------

.. code:: python

    from context_verbose import printer as ctp
    with ctp('Main Section', color='blue'):
        ctp.print('Text in main section')
        for i in range(3):
            with ctp(f'Subsection {i}'):
                ctp.print('Text in subsection')
                ctp.print('Text in subsection')

The above example will print the following:

.. figure:: https://framagit.org/robinechuca/context-verbose/-/raw/main/basic_example.png

Exaustive example of usage:
---------------------------

.. code:: python

    from context_verbose import printer as ctp

    @ctp
    def decorated_func(x):
        return x**x**x

    def error_func():
        with ctp('Section that will fail'):
            return 1/0

    ctp.print('we will enter the main section')
    with ctp('Main Section', color='cyan'):
        ctp.print('text in main section')
        try:
            with ctp('Subsection 1'):
                for x in [1, 8]:
                    decorated_func(x)
                error_func()
        except ZeroDivisionError:
            pass
        with ctp('Subsection 2', color='magenta'):
            ctp.print('text in bold', bold=True)
            ctp.print('underlined text', underline=True)
            ctp.print('blinking text', blink=True)
            ctp.print('yellow text', color='yellow')
            ctp.print('text highlighted in blue', bg='blue')
            ctp.print('text in several ', end='')
            ctp.print('parts', print_headers=False)
            ctp.print('''text in several
                         lines''')
        with ctp(color='green'):
            ctp.print('this subsection is automatically named')
    ctp.print('we are out of the main section')

The above example will print the following:

.. figure:: https://framagit.org/robinechuca/context-verbose/-/raw/main/exaustive_example.png

See Also
--------

* `fabric-verbose <https://pypi.org/project/fabric-verbose/>`_
* `pretty-verbose <https://pypi.org/project/pretty-verbose/>`_
