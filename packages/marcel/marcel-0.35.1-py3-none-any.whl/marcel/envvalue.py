# This file is part of Marcel.
#
# Marcel is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, (or at your
# option) any later version.
#
# Marcel is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with Marcel.  If not, see <https://www.gnu.org/licenses/>.

import importlib
import inspect

import marcel.core
import marcel.parser

# Empty is used to denote an empty EnvValue cache. The weird isempty() test is needed because we could be
# checking an EnvValue's cache that originated in another process. So we can't rely on object identity,
# even for classes (I think). It is possible to use None to indicate an uncached EnvValue, but because None
# is a valid value for a variable, we could be reconstituting it repeatedly.
class Empty(object):
    pass

EMPTY = Empty()

def isempty(x):
    t = type(x)
    return t.__module__ == 'marcel.persistence.persistable' and t.__qualname__ == 'Empty'

# Environment variables need to be saved, and transmitted to subprocesses. In both cases, the variables' values
# need to persist beyond the current process. An EnvValue is the internal representation of an environment variable.
# Pickleable values, like int, str, list[str], etc., don't require special handling. But modules and
# functions (often) cannot be pickled, so a pickleable value must be substituted, in such a way that the value
# can be reconstituted in another process.
#
# Lifecycle:
#  An EnvValue has two kinds of state:
#       1. cached value: The value of the envvar, visible to marcel users, not necessarily pickleable.
#       2. persistable state: Definitely pickleable.
#  The cached value is what is assigned to an envvar. This value is dropped when persistence is required.
#  So the lifecycle phases are:
#       - Creation: When a value is assigned to an env var, an EnvValue is created, using inputs
#         suitable for that kind of EnvValue subtype.
#       - Persistence: A value is persisted by calling __getstate__(). __getstate__ discards the cached value,
#         and keeps the persistable state.
#       - Reconstitution: When the value of the EnvValue is required, the envvar value is reconstituted
#         from persistable state if necessary.
# An EnvValue cannot be transmitted with its Environment (via the env attribute). The whole point of EnvValues is
# to deal with limitations in the transmission of Environments! So env is cleared by __getstate__, and filled in
# when the EnvValue's value is obtained.
class EnvValue(object):

    def __init__(self, cached=EMPTY):
        self.cached = cached
        self.env = None

    def __getstate__(self):
        self.env = None
        self.cached = EMPTY
        return self.__dict__

    def unwrap(self, env):
        if self.env is None:
            self.env = env
        else:
            assert self.env is env
        if isempty(self.cached):
            self.cached = self.reconstitute()
        return self.cached

    def reconstitute(self):
        assert False


class Simple(EnvValue):

    def __init__(self, value):
        super().__init__(value)
        self.value = value

    def __repr__(self):
        return str(self.value)

    def reconstitute(self):
        return self.value


class Compilable(EnvValue):

    def __init__(self, source, compiled):
        assert source is not None
        assert compiled is not None
        super().__init__(compiled)
        self.source = source

    def __repr__(self):
        return self.source

    @staticmethod
    def for_function(source, function):
        assert callable(function), function
        return CompilableFunction(source, function)

    @staticmethod
    def for_pipeline(source, pipeline):
        assert isinstance(pipeline, marcel.core.PipelineExecutable)
        return CompilablePipeline(source, pipeline)

class CompilableFunction(Compilable):

    def reconstitute(self):
        assert self.env is not None
        function = marcel.parser.Parser(self.source, self.env).parse_function()
        # The variable owning this Compilable was assigned using this marcel syntax: var = (...).
        # The expression in the parens is evaluated and assigned to the var. For a CompilableFunction (this class),
        # that value is itself a function. That return value of parse_function() needs to be evaluated, similar to
        # what happened during the original assign op.
        return function()

    # A function-valued env var can be called as a function. In that case, env.getvar is bypassed and the Compilable
    # is invoked directly.
    def __call__(self, *args, **kwargs):
        assert False
        assert self.env is not None
        function = self.unwrap(self.env)
        assert callable(function), function
        return function(*args, **kwargs)


class CompilablePipeline(Compilable):

    def reconstitute(self):
        assert self.env is not None
        return marcel.parser.Parser(self.source, self.env).parse_pipeline()


class Module(EnvValue):

    def __init__(self, module):
        super().__init__(module)
        self.module_name = module.__name__

    def __repr__(self):
        return self.module_name

    def reconstitute(self):
        return importlib.import_module(self.module_name)


class Function(EnvValue):

    def __init__(self, function):
        super().__init__(function)
        self.module_name = function.__module__
        self.function_name = function.__name__

    def __repr__(self):
        return f'{self.module_name}.{self.function_name}'

    def reconstitute(self):
        module = importlib.import_module(self.module_name)
        return module.__dict__[self.function_name]


def wrap(value, source=None):
    def is_pipeline(value):
        return type(value) is marcel.core.PipelineExecutable
    return (Function(value) if inspect.isbuiltin(value) else
            Function(value) if inspect.isfunction(value) else
            Module(value) if inspect.ismodule(value) else
            Compilable.for_function(f'({source})', value) if callable(value) else
            Compilable.for_pipeline(source, value) if is_pipeline(value) else
            Simple(value))
