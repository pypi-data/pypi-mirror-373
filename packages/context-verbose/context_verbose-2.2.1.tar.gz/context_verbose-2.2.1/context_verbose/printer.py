#!/usr/bin/env python3

"""
** High level API for contextual verbosity. **
----------------------------------------------

The *Printer* class allows the user to nest multiple
display blocks without worrying about indentation levels.
"""

import inspect
import math
import time

from context_verbose.color import get_section_header, colorize, format_text
from context_verbose.memory import get_lifo
from context_verbose.singleton import MetaSingleton
from context_verbose.thread_safe import print_safe



class Printer(metaclass=MetaSingleton):
    """
    ** Main class, only the instance is manipulated. **
    """

    def __call__(self, title_or_func=None, **formatting):
        """
        ** Update the parameters of the child section. **

        Parameters
        ----------
        title_or_func : str or callable, optional
            The message to display. None allows to display nothing at all.
            Otherwise, it can be the function to decorate.
        **formatting : dict
            Text formatting new parameters. These settings will affect
            not only the child section but also all child of child sections.

        Returns
        -------
        self : Printer
            Returns itself around for compatibility with *with*.
        """
        if isinstance(title_or_func, str):
            self.print(title_or_func, _is_title=True, **{**get_lifo().get_layer(), **formatting})
            get_lifo().update_layer(title=True)
        elif hasattr(title_or_func, '__call__'):
            from context_verbose.decorator import decorate
            return decorate(title_or_func)
        elif title_or_func is not None:
            raise TypeError(
                f'the parameter must be str or function, not {title_or_func.__class__.__name__}'
            )
        get_lifo().update_future_layer(**formatting)
        return self

    def __enter__(self):
        self.enter_section()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.print(
                f"{colorize('red', exc_type.__name__, kind='bg')} l{exc_tb.tb_lineno} ({exc_val})"
            )
        self.exit_section()

    def enter_section(self, title=None, **formatting):
        """
        ** Opens a new section. **

        Parameters
        ----------
        title : str, optional
            The name of the new section.
        **formatting : dict
            Text formatting parameters. These settings will affect
            not only this section but also all child sections.

        Examples
        --------
        >>> from context_verbose.memory import _reset_memory
        >>> _reset_memory()
        >>> from context_verbose.printer import Printer
        >>> ctp = Printer()
        >>> ctp.enter_section() # doctest: +SKIP
        Section __run l1336 in /usr/lib/python3.8/doctest.py
        >>> _reset_memory()
        >>> ctp.enter_section('Section')
        Section
        >>>
        """
        if not get_lifo().get_layer().get('title', False):
            get_lifo().update_future_layer(**formatting)
            if title is None:
                try:
                    frame = inspect.currentframe().f_back.f_back
                except AttributeError:
                    frame = inspect.currentframe().f_back
                if frame.f_code.co_name == '<module>':
                    title = f'Section l{frame.f_lineno} in {frame.f_code.co_filename}'
                else:
                    title = (
                        f'Section {frame.f_code.co_name} l{frame.f_lineno} '
                        f'in {frame.f_code.co_filename}'
                    )

            self.print(
                title,
                _is_title=True,
                **{**get_lifo().get_layer(), **get_lifo().future_context, **formatting}
            )
        elif title is not None:
            raise NameError('there is already a title in this section')
        get_lifo().add_layer(**formatting, title=False)

    @staticmethod
    def exit_section():
        """
        ** Exits the current section to return to the parent section. **
        """
        get_lifo().remove_layer()
        get_lifo().update_layer(title=False)

    @staticmethod
    def print(message, *, print_headers=True, end='\n', _is_title=False, **formatting):
        r"""
        ** Displays the message with the formatting of the current section. **

        Parameters
        ----------
        message : str
            The message to display
        print_headers : boolean, optional
            If set to true, all section headers will be printed before the text.
            (The text wil be indentate.)
        end : str, default='\n'
            Character to print at the end of the line.
        **formatting : dict
            The text formatting parameters are passed to the
            ``context_verbose.color.format_text`` function.
            They apply only to this message, they do not affect future messages.

        Examples
        --------
        >>> from context_verbose.memory import _reset_memory
        >>> _reset_memory()
        >>> from context_verbose.printer import Printer
        >>> ctp = Printer()
        >>> ctp.print('a simple message')
        a simple message
        >>> ctp.print('this is a\nmulti-line message')
        this is a
          multi-line message
        >>> with ctp('Section'):
        ...     ctp.print('a simple message')
        ...     ctp.print('this is a\nmulti-line message')
        ...     ctp.print('start of the message ', end='')
        ...     ctp.print('end of message', print_headers=False)
        ...
        Section
        █ a simple message
        █ this is a
          multi-line message
        █ start of the message end of message
        >>>
        """
        layer = get_lifo().get_layer(_is_title=_is_title)
        if layer.get('title', False):
            raise NameError('maximum one title per section')

        if layer['display']:
            messages = str(message).split('\n')
            _end = '\n'
            for i, mes in enumerate(messages):
                mes = format_text(mes.lstrip(), **formatting)
                if print_headers:
                    print_safe(get_section_header(partial=(i!=0)), end='')
                if i == len(messages)-1:
                    _end = end
                print_safe(mes, end=_end)

    @staticmethod
    def elapsed_time(*, _delta_t=0):
        """
        ** Returns the time elapsed since the entry in the section. **

        Parameters
        ----------
        **formatting : dict
            Text formatting parameters. They apply only to this message.

        Examples
        --------
        >>> from context_verbose.memory import _reset_memory
        >>> _reset_memory()
        >>> from context_verbose.printer import Printer
        >>> with Printer('Section') as ctp:
        ...     t = ctp.elapsed_time()
        ...
        Section
        >>> t # doctest: +SKIP
        '1.91 us'
        >>>
        """
        delta_t = _delta_t or time.time() - get_lifo().get_layer()['time']
        unit, delta_t = 'h', delta_t / 3600.0
        if delta_t < 1:
            unit, delta_t = 'm', delta_t * 60.0
        if delta_t < 1:
            unit, delta_t = 's', delta_t * 60.0
        if delta_t < 1:
            unit, delta_t = 'ms', delta_t * 1000.0
        if delta_t < 1:
            unit, delta_t = 'us', delta_t * 1000.0
        match unit:
            case 'h':
                base = math.floor(delta_t)
                return f"{base} h {round(60.0*(delta_t-base))} min"
            case 'm':
                base = math.floor(delta_t)
                return f"{base} min {round(60.0*(delta_t-base))} s"
            case 's' | 'ms' | 'us':
                return f"{delta_t:.2f} {unit}"


    @staticmethod
    def print_time(elapsed_time=None, **kwargs):
        """
        ** Displays nicely elapsed time. **

        Parameters
        ----------
        elapsed_time : float
            The time displayed is expressed in seconds.
            By default uses the time from the ``Printer.elapsed_time`` function.
        **kwargs : dict
            Given to the ``Printer.print`` function.
        """
        time_str = (
            Printer.elapsed_time()
            if elapsed_time is None
            else Printer.elapsed_time(_delta_t=elapsed_time)
        )
        Printer.print(time_str, **kwargs)

    @staticmethod
    def set_max_depth(value):
        """
        ** Sets a maximum number of nested sections after which the printer will stop printing. **

        It will still be able to enter or exit deeper sections
        but without printing their title or their header at all.

        Parameters
        ----------
        value : int
            Value to set to the max depth parameter.

        Examples
        --------
        >>> from context_verbose.memory import _reset_memory
        >>> _reset_memory()
        >>> from context_verbose.printer import Printer
        >>> ctp = Printer()
        >>> ctp.set_max_depth(2)
        >>> with ctp('Section 1'):
        ...     ctp.print('text in section 1')
        ...     with ctp('Section 2'):
        ...         ctp.print('text in section 2')
        ...         with ctp('Section 3'):
        ...             ctp.print('text in section 3')
        ...
        Section 1
        █ text in section 1
        █ Section 2
        █ █ text in section 2
        >>>
        """
        assert isinstance(value, int)

        get_lifo().set_max_depth(value)

    @staticmethod
    def set_default_columns(nbr):
        """
        ** Defines the number of display columns by default. **

        Normally the number of columns is directly deduced from the size of the terminal.
        But sometimes stdout does not point to a terminal or the size of the terminal is not known.
        In this case the default number of columns is used.

        Parameters
        ----------
        nbr : int
            The number of characters that can fit in 1 column.

        Examples
        --------
        >>> from context_verbose.memory import _reset_memory
        >>> _reset_memory()
        >>> from context_verbose.printer import Printer
        >>> ctp = Printer()
        >>> ctp.print('abcdefghijklmnopqrstuv')
        abcdefghijklmnopqrstuv
        >>> ctp.set_default_columns(10)
        >>> ctp.print('abcdefghijklmnopqrstuv')
        abcdefghij
        klmnopqrst
        uv
        >>>
        """
        assert isinstance(nbr, int)
        assert nbr > 0

        get_lifo().set_default_columns(nbr)
