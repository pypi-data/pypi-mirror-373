#!/usr/bin/env python3

"""
** Representation of messages as a tree. **
-------------------------------------------

Each branch corresponds to a thread or a process.
This makes it possible to represent the display
of each thread and process in the most easily exploitable way.
"""


import math
import logging
import os
import re

import networkx

from context_verbose.memory import get_lifo



def cut(string, size):
    r"""
    ** Allows to cut the text without breaking the special characters. **

    Parameters
    ----------
    string : str
        The text to be cut, which can contain text formatting characters.

    Returns
    -------
    sections : list
        Each element of the list is a portion of the
        text cut in order to ensure correct formatting.

    Examples
    --------
    >>> from context_verbose.color import format_text
    >>> from context_verbose.tree import cut
    >>> format_text('test_string')
    'test_string'
    >>> cut(_, 7)
    ['test_st', 'ring']
    >>> format_text('test_string', color='blue')
    '\x1b[22m\x1b[34mtest_string\x1b[0m'
    >>> cut(_, 7)
    ['\x1b[22m\x1b[34mtest_st\x1b[0m', '\x1b[22m\x1b[34mring\x1b[0m']
    >>> format_text('test_string', color='blue') + format_text('test_string', blink=True)
    '\x1b[22m\x1b[34mtest_string\x1b[0m\x1b[5mtest_string\x1b[0m'
    >>> cut(_, 11)
    ['\x1b[22m\x1b[34mtest_string\x1b[0m', '\x1b[22m\x1b[34m\x1b[0m\x1b[5mtest_string\x1b[0m']
    >>> cut('', 1)
    ['']
    >>>
    """
    assert isinstance(string, str)
    assert isinstance(size, int)
    assert size > 0

    if not string:
        return ['']

    sections = []
    specials = list(re.finditer(r'\x1b\[\S+?m', string))

    # cutting in packages of the right size
    clean_string = string
    for special_str in {m.group() for m in specials}:
        clean_string = clean_string.replace(special_str, '')
    while clean_string:
        sections.append(clean_string[:size])
        clean_string = clean_string[size:]

    # repositioning of special chains
    dec = 0
    positions = {}
    for special in specials:
        start, end = special.span()
        positions[start-dec] = positions.get(start-dec, '') + special.group()
        dec += end - start

    # added markup
    current_markers = ''
    loc_dec = 0
    for dec, section in enumerate(sections.copy()):
        section = current_markers + section
        loc_dec = len(current_markers)
        for i in range(size):
            if i + dec*size in positions:
                special = positions[i + dec*size]
                section = section[:i+loc_dec] + special + section[i+loc_dec:]
                if special == '\x1b[0m':
                    current_markers = ''
                else:
                    current_markers += special
                loc_dec += len(special)
        if current_markers:
            section += '\x1b[0m'
        sections[dec] = section

    # incomplete chain management
    if not string.endswith('\x1b[0m') and sections[-1].endswith('\x1b[0m'):
        sections[-1] = sections[-1][:-4]
    return sections


def get_terminal_size():
    """
    ** Recover the dimensions of the terminal. **

    Returns
    -------
    columns : int
        The number of columns in the terminal.
    lines : int
        The number of lines present in the terminal.

    Examples
    --------
    >>> import tempfile
    >>> import sys
    >>> from context_verbose.tree import get_terminal_size
    >>> size = get_terminal_size()
    >>> size # doctest: +SKIP
    (100, 30)
    >>> stdout = sys.stdout
    >>> with tempfile.TemporaryFile('w', encoding='utf-8') as file:
    ...     sys.stdout = file
    ...     size = get_terminal_size()
    ...
    >>> sys.stdout = stdout
    >>> size
    (100, inf)
    >>>
    """
    try:
        size = os.get_terminal_size()
    except OSError:
        return get_lifo().columns, math.inf
    else:
        return size.columns, size.lines


def get_length(text):
    r"""
    ** Returns the length of the displayed text. **

    Parameters
    ----------
    text : str
        Single-line text that can contain formatting characters.

    Returns
    -------
    length : int
        The size of the text.

    Examples
    --------
    >>> from context_verbose.tree import get_length
    >>> from context_verbose.color import format_text
    >>> get_length('hello')
    5
    >>> get_length('\thello')
    9
    >>> format_text('hello', color='red')
    '\x1b[22m\x1b[31mhello\x1b[0m'
    >>> get_length(_)
    5
    >>> get_length('')
    0
    >>>
    """
    assert isinstance(text, str)
    assert '\n' not in text

    length = len(text)
    length -= sum((len(c) for c in re.findall(r'\x1b\[\S+?m', text)), start=0)
    length += 3*len(re.findall(r'\t', text))

    return length


class Branch:
    """
    ** Corresponds to the display thread of a thread or a process. **
    """

    def __init__(self, proc_name='MainProcess', thread_name='MainThread'):
        """
        Parameters
        ----------
        proc_name : str
            The name of the process associated with this branch.
        thread_name : str
            The name of the thread associated with this process.
        """
        self.proc_thread = (proc_name, thread_name)
        self.message = ''

    def add_message(self, message):
        """
        ** Adds several display lines linked to this branch. **

        Parameters
        ----------
        message : str
            The new lines to display in this section.
        """
        assert isinstance(message, str)

        self.message += message

    def get_max_length(self):
        r"""
        ** Returns the length of the longest line. **

        Returns
        -------
        length : int
            The number of characters (printable + spaces + tabs) in the longest line.

        Examples
        --------
        >>> from context_verbose.tree import Branch
        >>> branch = Branch()
        >>> branch.get_max_length()
        0
        >>> branch.add_message('hello\n')
        >>> branch.get_max_length()
        5
        >>> branch.add_message('welcome\n')
        >>> branch.get_max_length()
        7
        >>> branch.add_message('yo\n')
        >>> branch.get_max_length()
        7
        >>>
        """
        return max(
            (get_length(l) for l in self.message.split()),
            default=0,
        )

    def __eq__(self, other):
        """
        ** Return True if the 2 branches are the same. **

        Parameters
        ----------
        other : object
            The element of comparison.

        Examples
        --------
        >>> from context_verbose.tree import Branch
        >>> b1 = Branch('p1', 't1')
        >>> b2 = Branch('p1', 't1')
        >>> b3 = Branch('p1', 't2')
        >>> b1 == b1
        True
        >>> b1 == b2
        True
        >>> b1 == b3
        False
        >>>
        """
        if not isinstance(other, Branch):
            return NotImplemented
        return self.proc_thread == other.proc_thread

    def __gt__(self, other):
        """
        ** Compare the depth of the branches. **

        Parameters
        ----------
        other : object
            The element of comparison.

        Examples
        --------
        >>> from context_verbose.tree import Branch
        >>> Branch('p1', 't1') > Branch('p1', 't1')
        False
        >>> Branch('p1', 't1') > Branch('p2', 't1')
        False
        >>> Branch('p2', 't1') > Branch('p1', 't1')
        True
        >>> Branch('p1', 't1') > Branch('p1', 't2')
        False
        >>> Branch('p1', 't2') > Branch('p1', 't1')
        True
        >>>
        """
        if not isinstance(other, Branch):
            return NotImplemented
        if self.proc_thread[0] == other.proc_thread[0]:
            return self.proc_thread[1] > other.proc_thread[1]
        return self.proc_thread[0] > other.proc_thread[0]

    def __hash__(self):
        """
        ** Allows to build hash tables. **

        Examples
        --------
        >>> from context_verbose.tree import Branch
        >>> b1 = Branch('p1', 't1')
        >>> b2 = Branch('p1', 't1')
        >>> b3 = Branch('p1', 't2')
        >>> sorted({b1, b2, b3})
        [Branch(p1, t1), Branch(p1, t2)]
        >>>
        """
        return hash(self.proc_thread)

    def __repr__(self):
        """
        ** Offers a slightly better representation. **

        Examples
        --------
        >>> from context_verbose.tree import Branch
        >>> Branch()
        Branch(MainProcess, MainThread)
        >>>
        """
        proc, thread = self.proc_thread
        return f'Branch({proc}, {thread})'


class Tree(networkx.DiGraph):
    """
    ** This is the complete graph that represents the whole display. **

    Examples
    --------
    >>> from context_verbose.tree import Tree
    >>> tree = Tree()
    >>> print(tree)
    Tree with 0 nodes and 0 edges
    >>>
    """

    def add_message(self, message, proc_name, thread_name, father_proc_name=None):
        """
        ** Add the corresponding text in the right branch. **

        Parameters
        ----------
        message : str
            The display lines to be added to the corresponding branch.
        proc_name : str
            The name of the process associated with this branch.
        thread_name : str
            The name of the thread associated with this process.
        father_proc_name : str or None
            If it is provided, it corresponds to the name of the parent process.


        Examples
        --------
        >>> from context_verbose.tree import Tree
        >>> tree = Tree()
        >>> print(tree)
        Tree with 0 nodes and 0 edges
        >>> tree.add_message('a', proc_name='MainProcess', thread_name='Thread-1')
        >>> print(tree)
        Tree with 2 nodes and 1 edges
        >>> tree.add_message('b', proc_name='MainProcess', thread_name='Thread-2')
        >>> print(tree)
        Tree with 3 nodes and 2 edges
        >>>
        """
        assert isinstance(message, str), message.__class__.__name__
        assert isinstance(proc_name, str), proc_name.__class__.__name__
        assert isinstance(thread_name, str), thread_name.__class__.__name__
        assert father_proc_name is None or isinstance(father_proc_name, str)

        node = (proc_name, thread_name)

        # create new node and edge
        if not self.has_node(node):
            self.add_node(node, branch=Branch(proc_name=proc_name, thread_name=thread_name))
            if thread_name != 'MainThread':
                father = (proc_name, 'MainThread')
            elif proc_name != 'MainProcess':
                if father_proc_name is None:
                    logging.warning(
                        f"the process '{proc_name}' is not attached to any father process"
                    )
                father = (father_proc_name, 'MainThread')
            else:
                father = None
            if father is not None:
                self.add_message('', proc_name=father[0], thread_name=father[1])
                self.add_edge(father, node)

        # update content
        self.nodes[node]['branch'].add_message(message)

    def display(self):
        """
        ** Displays the contents of the tree. **
        """
        # logging.warning("the final display function is all rotten")

        if self.nodes[('MainProcess', 'MainThread')]['branch'].message:
            columns, _ = get_terminal_size()
            lines = [
                small_line
                for line in self.nodes[('MainProcess', 'MainThread')]['branch'].message.split('\n')
                for small_line in cut(line, columns)
            ]
            print('\n'.join(lines), end='')
            self.nodes[('MainProcess', 'MainThread')]['branch'].message = ''

        for node in self.nodes:
            if node != ('MainProcess', 'MainThread'):
                if self.nodes[node]['branch'].message:
                    # header = f'********** {node} **********'
                    # print(header)
                    # print(self.nodes[node]['branch'].message, end='')
                    print(f"{self.nodes[node]['branch'].message} <{node[0]}, {node[1]}>", end='')
                    self.nodes[node]['branch'].message = ''
                    # print('*'*len(header))
