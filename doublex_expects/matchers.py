# -*- coding: utf-8 -*-

from expects import (
    equal as equal_matcher,
    be_above_or_equal,
    be_below_or_equal)
from expects.matchers import Matcher
from expects.texts import plain_enumerate

MAX_TIMES = be_below_or_equal
MIN_TIMES = be_above_or_equal


class _have_been_called(Matcher):
    @property
    def twice(self):
        return self._called.twice

    @property
    def once(self):
        return self._called.once

    def min(self, times):
        return self._called.min(times)

    def max(self, times):
        return self._called.max(times)

    def exactly(self, times):
        return self._called.exactly(times)

    def _match(self, subject):
        return self._called._match(subject)

    def _description(self, subject):
        return self._called._description(subject)

    @property
    def _called(self):
        return have_been_called_with()


class have_been_called_with(Matcher):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._times = None
        self._times_description = ''

    @property
    def once(self):
        self._times = equal_matcher(1)
        self._times_description = 'once'
        return self

    @property
    def twice(self):
        self._times = equal_matcher(2)
        self._times_description = 'twice'
        return self

    def exactly(self, times):
        self._times = equal_matcher(times)
        self._times_description = 'exactly {} times'.format(times)
        return self

    def max(self, times):
        self._times = MAX_TIMES(times)
        self._times_description = 'max {} times'.format(times)
        return self

    def min(self, times):
        self._times = MIN_TIMES(times)
        self._times_description = 'min {} times'.format(times)
        return self

    def _match(self, subject):
        calls_matching = len(self._calls_matching(subject))

        if self._times is None:
            return calls_matching != 0

        return self._times._match(calls_matching)

    def _calls_matching(self, subject):
        calls = []

        for call in subject.calls:
            if self._match_call(call):
                calls.append(call)

        return calls

    def _match_call(self, call):
        for i, matcher in enumerate(self._args):
            if not hasattr(matcher, '_match'):
                matcher = equal_matcher(matcher)

            try:
                arg = call.args[i]
            except IndexError:
                return False
            else:
                if not matcher._match(arg):
                    return False

        for k, matcher in self._kwargs.items():
            if not hasattr(matcher, '_match'):
                matcher = equal_matcher(matcher)

            try:
                value = call.kargs[k]
            except KeyError:
                return False
            else:
                if not matcher._match(value):
                    return False

        return True

    def _description(self, subject):
        message = 'have been called'

        if self._args or self._kwargs:
            message += ' with {}'.format(plain_enumerate(self._args, self._kwargs))


        if len(self._times_description) != 0:
            message += ' ' + self._times_description

        message += ' but calls that actually ocurred were:\n{}'.format(subject.double._recorded.show(indent=10))

        return message

have_been_called = _have_been_called()
