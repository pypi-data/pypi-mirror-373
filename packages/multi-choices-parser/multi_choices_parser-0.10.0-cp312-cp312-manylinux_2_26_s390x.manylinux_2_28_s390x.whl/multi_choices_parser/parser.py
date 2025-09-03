# Software Name : multi-choices-parser
# SPDX-FileCopyrightText: Copyright (c) 2025 Orange SA
# SPDX-License-Identifier: GPL-2.0-or-later

# This software is distributed under the GNU General Public License v2.0 or later,
# see the "LICENSE.txt" file for more details or GNU General Public License v2.0 or later

# Authors: Hichem Ammar Khodja

from __future__ import annotations

from . import _core
from typing import List, Tuple, Union

class End:
    def __repr__(self) -> str:
        return "End"
    
    def __lt__(self, other) -> bool:
        return False
    
    def __gt__(self, other) -> bool:
        return True
    
    def __eq__(self, value: object) -> bool:
        return False
    
    def __hash__(self) -> int:
        return id(self)

DEFAULT_END_SYMB = End()

class ParserError(Exception):
    pass

class MultiChoicesParser:
    """
    A efficient incremental parser for multi-choice grammars. They are defined as grammars of the form:

    start: list1 list2 ... listn

    list1: choice1_1 | choice1_2 | ... | choice1_k1

    list2: choice2_1 | choice2_2 | ... | choice2_k2

    ...
    
    listn: choicen_1 | choicen_2 | ... | choicen_km

    where choicex_y is a sequence of integers and can possibly be empty

    Example:
    start: det noun
    
    det: "the " | "an " | "a " | ""

    noun: "orange" | "apple" | "banana"
    
    This was particularly optimized when the size of the lists of choices is 
    very large (up to order of millions), which can be helpful
    to represent entities preceeded (or not) by a determinent. 
    For example, in Wikipedia, there are around 7 million entities.

    NOTE: List of integers can be used instead of strings if needed. 

    """


    def __init__(self, list_of_choices: List[List[Union[Tuple[int], str]]], alphabet=None, end_symb=DEFAULT_END_SYMB) -> None:
        """
        Initialize the parser using a list of choices (a list of lists) which correspond
        to the lists introduced in the documentation of the class.

        Args:
            list_of_choices (list[list[Union[tuple[int], str]]]): The grammar choices.
                Each choice can be a tuple of integers or a string.
            end_symb (Union[int, str], optional): An optional end symbol to signify the end of input.
            alphabet has no use, ignore it.
        """
        self.end_symb = end_symb
        self.alphabet = alphabet

        # Determine the mode (string mode or integer mode) based on the first element
        if list_of_choices and list_of_choices[0] and isinstance(list_of_choices[0][0], str):
            self.string_mode = True
        else:
            self.string_mode = False

        # Convert all choices to lists of integers
        self.can_be_empty = []
        if self.string_mode:
            list_of_choices = [[[ord(ch) for ch in choice] for choice in choices] for choices in list_of_choices]
        
        if len(list_of_choices):
            self.root = _core.construct_tree(list_of_choices)

            # Initialize the current state
            self.current_state = _core.ParserState()
            self.current_state.add_node(self.root)
        else:
            self.root = None
            self.current_state = None

        # Initialize success and finished flags
        self.success = False
        self.finished = False

        self._is_at_initial_state = True


    def next(self) -> List[Union[int, str]]:
        """
        Returns all authorized tokens for the current state.

        Returns:
            tuple: A tuple of characters (if in string mode) or integers, or the End symbol.
        """
        if self.finished:
            return []
        next_chars = _core.next(self.current_state)
        if self.string_mode:
            # Convert integers to characters if in string mode
            next_chars = [chr(c) if c != _core.SpecialSymb.END else self.end_symb for c in next_chars]
        else:
            next_chars = [c if c != _core.SpecialSymb.END else self.end_symb for c in next_chars]
        return next_chars

    def step(self, ch: Union[int, str]) -> None:
        """
        Feed the character to the parser.

        Args:
            ch (Union[int, str]): A character (string) or an integer.
        """
        if self.finished:
            raise ParserError("The parser in on 'finished' state!")
        if ch is self.end_symb:
            ch = _core.SpecialSymb.END
        elif isinstance(ch, str):
            ch = ord(ch)
        self.current_state = _core.step(self.current_state, ch)
        if len(self.current_state.nodes) == 0:
            self.finished = True
        elif self.current_state.nodes[0] is None:
            self.finished = True
            self.success = True
        self._is_at_initial_state = False

    def reset(self) -> None:
        """
        Reset the state of the parser to its origin.
        """
        self.current_state = _core.ParserState()
        self.current_state.add_node(self.root)
        self.success = False
        self.finished = False
        self._is_at_initial_state = True

    def copy(self, stateful=True) -> MultiChoicesParser:
        """
        Return a copy of this parser (stateful or not).

        Note: The root ParserNodes remain the same (no additional memory allocation).

        Args:
            stateful (bool): If True, the copy retains the current state. Otherwise, it resets to the root.

        Returns:
            FastMultiChoicesParser: A new parser instance.
        """
        new_parser = MultiChoicesParser([], end_symb=self.end_symb)
        new_parser.root = self.root  # Share the same roots
        new_parser.string_mode = self.string_mode
        if stateful:
            new_parser.current_state = self.current_state
            new_parser.success = self.success
            new_parser.finished = self.finished
            new_parser._is_at_initial_state = self._is_at_initial_state
        else:
            new_parser.reset()
        return new_parser

    def accepts(self, string: Union[Tuple[int], str], must_end=False) -> bool:
        """
        Check whether the input string is correct according to this parser.

        Args:
            string (Union[tuple[int], str]): The input string as a tuple of integers or a string.

        Returns:
            bool: True if the string is accepted, False otherwise.
        """
        if self.finished:
            return len(string) == 0
        # Convert string to tuple of integers when necessary
        f = lambda c : _core.SpecialSymb.END if c is self.end_symb else ord(c) if isinstance(c,str) else c
        string = tuple(f(ch) for ch in string)

        return _core.accepts(self.current_state, string, must_end, True)

    def __eq__(self, other: object) -> bool:
        """
        Check equality between two parsers.

        Args:
            other (object): Another parser instance.

        Returns:
            bool: True if the parsers are equivalent, False otherwise.
        """
        if not isinstance(other, MultiChoicesParser):
            return False
        return (
            self.root is other.root
            and self.current_state is other.current_state
        )

    def __hash__(self) -> int:
        """
        Compute a hash value for the parser.

        Returns:
            int: The hash value.
        """
        return hash((id(self.root), id(self.current_state)))
    
    @property
    def is_at_initial_state(self) -> int:
        return self._is_at_initial_state
    
    @staticmethod
    def prepare_string(string : Union[Tuple[int], str], add_end : bool, special_symb_allowed: bool) -> Tuple[int]:
        if isinstance(string, str):
            string = tuple(ord(ch) for ch in string)
        elif not special_symb_allowed:
            assert _core.SpecialSymb.END not in string and _core.SpecialSymb.EPS not in string, "No special symbols are aloowed in string"
        
        if add_end:
            string = string + (_core.SpecialSymb.END.value,)
        return string
    
    # def delete_sequence(self, string: Union[Tuple[int], str]) -> bool:
    #     """Delete a sequence from the parsing tree. 

    #     IMPORTANT: The end symbol should not be included.

    #     Args:
    #         string (Union[Tuple[int], str]): String to delete

    #     Returns:
    #         bool: If something was deleted.
    #     """
    #     string = MultiChoicesParser.prepare_string(string, add_end=True, special_symb_allowed=False)
    #     return _core.delete_sequence(self.root, string)

        
    def add_sequence(self, string: Union[Tuple[int], str]) -> bool:
        """Add a sequence to the parsing tree. 

        IMPORTANT: The end symbol should not be included.

        Args:
            string (Union[Tuple[int], str]): String to add

        Returns:
            bool: If something was added.
        """
        string = MultiChoicesParser.prepare_string(string, add_end=True, special_symb_allowed=False)
        return _core.add_sequence(self.root, string, [], False)
