#!/usr/bin/env python3
"""A number of utilities for argument parser."""

from argparse import Action

class CommaSeparatedListAction(Action):
    """Create a list from the comma sepparated numbers at imput."""

    def __call__(self, parser, namespace, values, option_string=None):
        """The actual action."""
        setattr(namespace, self.dest, list(map(int, values.split(','))))


class RangeListAction(Action):
    """Create a list from a range expresion at input.

    The list is made with  numbers or ranges (ch1:ch2 or ch1:ch2:step)
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """The actual action."""
        value = []
        for V in values.split(','):
            try:
                value.append(int(V))
            except ValueError:
                if ':' not in V:
                    continue

                items = V.split(':')
                if len(items)==1:
                    continue

                ival = list(map(int, items))
                ival[1] += 1
                for x in range(*ival):
                    value.append(int(x))


        setattr(namespace, self.dest, value)

