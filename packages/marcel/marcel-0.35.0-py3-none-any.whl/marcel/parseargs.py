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


class Arg(object):

    def __init__(self):
        self.envvar = None  # Filled in after construction

    def register_flags(self, all_flags):
        assert False

    def has_flag(self, flag):
        assert False


class AnonArg(Arg):

    def __repr__(self):
        return 'AnonArg()'

    def register_flags(self, all_flags):
        return True

    def has_flag(self, flag):
        return False

    def is_anon(self):
        return True

    def is_boolean(self):
        return False


class FlagArg(AnonArg):

    def __init__(self, f1, f2):
        super().__init__()
        assert f1 is not None
        self.short = None
        self.long = None
        if f2 is None:
            if FlagArg.short(f1):
                self.short = f1
            elif FlagArg.long(f1):
                self.long = f1
            else:
                assert False  # check_valid_flag calls should prevent us getting here
        else:
            if FlagArg.short(f1) and FlagArg.long(f2):
                self.short = f1
                self.long = f2
            elif FlagArg.long(f1) and FlagArg.short(f2):
                self.long = f1
                self.short = f2
            else:
                raise SyntaxError(f'If two flags are specified, one must be long and one must be short: {f1}, {f2}')
        self.boolean = False

    def __repr__(self):
        return (f'{self.short}|{self.long}' if self.short and self.long else
                self.short if self.short else
                self.long)

    def register_flags(self, all_flags):
        def register(flag):
            if flag is not None:
                if flag in all_flags:
                    raise SyntaxError(f'Duplicated flag: {flag}')
                else:
                    all_flags.add(flag)
        register(self.short)
        register(self.long)

    def has_flag(self, flag):
        return self.short == flag or self.long == flag

    def is_anon(self):
        return False

    @staticmethod
    def short(f):
        FlagArg.check_valid_flag(f)
        return f[0] == '-' and f[1] != '-'

    @staticmethod
    def long(f):
        FlagArg.check_valid_flag(f)
        return f[0] == '-' and f[1] == '-'

    @staticmethod
    def check_valid_flag(f):
        # Long enough
        if len(f) < 2:
            raise SyntaxError(f'Invalid flag: {f}')
        # Not just -
        if f.startswith('--'):
            f = f[2:]
        elif f.startswith('-'):
            f = f[1:]
        if len(f) == 0:
            raise SyntaxError(f'Invalid flag: {f}')


class BooleanFlagArg(FlagArg):

    def __init__(self, short, long):
        super().__init__(short, long)
        self.boolean = True

    def __repr__(self):
        flag_str = super().__repr__()
        return f'BooleanFlag{flag_str[flag_str.find("("):]}'

    def is_boolean(self):
        return True


def flag(f1, f2=None):
    return FlagArg(f1, f2)


def boolean_flag(f1, f2=None):
    return BooleanFlagArg(f1, f2)


def anon():
    return AnonArg()


class CommandLine(object):

    def __init__(self, var_arg):
        self.argv = None  # The uninterpreted args. argv[0] is the path to the script being executed.
        self.var_arg = var_arg
        anon_seen = False
        for var, arg in self.var_arg.items():
            if not (type(var) is str and var.isidentifier()):
                raise SyntaxError(f'Var must be valid as a Python identifier: {var}')
            if type(arg) not in (AnonArg, FlagArg, BooleanFlagArg):
                raise SyntaxError(f'Arg value must be flag(), boolean_flag(), or anon(): {arg}')
            if arg.is_anon():
                if anon_seen:
                    raise SyntaxError('Too many anon() specified.')
                else:
                    anon_seen = True
            arg.envvar = var
        all_flags = set()
        for arg in self.var_arg.values():
            arg.register_flags(all_flags)
        # If register_flags didn't raise an exception, there are no duplicates

    def parse(self, argv):
        def isflag(arg):
            return arg.startswith('-')

        def arg_of(flag):
            for arg in self.var_arg.values():
                if arg.has_flag(flag):
                    return arg
            raise SyntaxError(f'Unrecognized flag: {flag}')

        def anon_arg():
            for arg in self.var_arg.values():
                if arg.is_anon():
                    return arg
            return None

        values = {}  # envvar -> value (from command line)
        for var in self.var_arg:
            values[var] = None
        flag = None
        arg = anon_arg()
        anon = []
        for token in argv:
            print(f'token: {token}, flag: {flag}, arg: {arg}')
            if isflag(token):
                if flag is not None:
                    # If flag was set on a previous iteration, then var should also be set.
                    assert token is not None, flag
                    # Two flags in a row, so the previous flag must be boolean
                    if arg.is_boolean():
                        values[arg.envvar] = True
                    else:
                        raise SyntaxError(f'Value missing for flag {flag}')
                flag = token
                arg = arg_of(flag)
            else:
                if arg.is_anon():
                    anon.append(token)
                elif arg.is_boolean():
                    raise SyntaxError(f'Value should not be specified for flag {flag}')
                else:
                    values[arg.envvar] = token
                    flag = None
                    arg = anon_arg()
        values[anon_arg().envvar] = anon
        return values
