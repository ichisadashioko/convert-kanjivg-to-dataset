"""
https://www.w3.org/TR/SVG/paths.html#PathDataGeneralInformation

A path is defined by include a `path` element on which the `d` property
specifies the path data. The path data contains the `moveto`, `lineto`,
`curveto` (both cubic and quadratic Beziers), `arc` and `closepath`
instructions.

Path data can contain newline characters and thus can be broken up into
multiple lines to improve readability. Newlines inside attributes in
markup will be normalized to space characters while parsing.

The syntax of path data is concise inorder to allow for minimal file
size and efficient downloads, since many SVG files will be dominated by
their path data. Some of the ways that SVG attempts to minimize the size
of path data are as follows:

- All instructions are expressed as one character (e.g. a `moveto` is
expressed as an `M`).

- Superfluous white space and separators (such as commas) may be
eliminated; for instance, the following contains unnecessary spaces:

```
M 100 100 L 200 200
```

It may be expressed more compactly as:

```
M100 100L200 200
```

- A command letter may be eliminated if an identical command letter
would otherwise precede it; for instance, the following contains an
unnecessary second "L" command:

```
M 100 200 L 200 100 L -100 -200
```

It may be expressed more compactly as:

```
M 100 200 L 200 100 -100 -200
```

- For most commands there are absolute and relative versions available
(uppercase means absolute coordinates, lowercase means relative
coordinates).

- Alternate forms of `lineto` are available to optimize the special
cases of horizontal and vertical lines (absolute and relative).

- Alternate forms of `curve` are available to optimize the special cases
where some of the control points on the current segment can be
determined automatically from the control points on the previous
segment.

The path data syntaxis a prefix notation (i.e., commands followed by
parameters). The only allowable decimal point is a Unicode U+0046
FULL STOP (".") character (also referred to in Unicode as PERIOD, dot
and decimal point) and no other delimiter characters are allowed. (For
example, the following is an invalid numeric value in a path data
stream: "13,000.56". Instead, say: "13000.56".)

For the relative versions of the commands, all coordinate values are
relative to the current point at the start of the command.

In the tables below, the following notation is used to describe the
syntax of a given path command:

- `()`: grouping of parameters
- `+`: 1 or more the given parameter(s) is required

In the description of the path commands, `cpx` and `cpy` represent the
coordinates of the current point.
"""

sep_chars = ' ,\n'

minus_sign = '-'
decimal_point = '.'
numbers = '0123456789'
numberic_chars = numbers + minus_sign + decimal_point

# https://www.w3.org/TR/SVG/paths.html#PathDataMovetoCommands
moveto_absolute = 'M'
moveto_relative = 'm'
moveto_commands = moveto_absolute + moveto_relative

# https://www.w3.org/TR/SVG/paths.html#PathDataCubicBezierCommands
curveto_absolute = 'C'
curveto_relative = 'c'
curveto_commands = curveto_absolute + curveto_relative

smooth_curveto_absolute = 'S'
smooth_curveto_relative = 's'
smooth_curveto_commands = smooth_curveto_absolute + smooth_curveto_relative

commands = moveto_commands + curveto_commands + smooth_curveto_commands


def raise_unexpected_char(d, pos):
    raise Exception(f'Unexpected {repr(d[pos])} at {pos} in {repr(d)}!')


def raise_unexpected_end_of_data(d, pos):
    raise Exception(f'Unexpected end of data at {pos} in {repr(d)}!')


def skip_seps(d: str, pos: int):
    d_length = len(d)

    while pos < d_length:
        c = d[pos]

        if c in sep_chars:
            pos += 1
            continue
        else:
            break

    return pos


def skip_numbers(d: str, pos: int):
    d_length = len(d)

    while pos < d_length:
        c = d[pos]

        if c in numbers:
            pos += 1
            continue
        else:
            break

    return pos


def parse_number(d: str, pos: int):
    d_length = len(d)
    pos = skip_seps(d, pos)

    if not pos < d_length:
        raise_unexpected_end_of_data(d, pos)

    if not d[pos] in numberic_chars:
        raise_unexpected_char(d, pos)

    # indicate the starting index of numeric value
    number_start_pos = pos

    # we may have negative value
    if d[pos] == minus_sign:
        pos += 1

    if not d[pos] in numbers:
        raise_unexpected_char(d, pos)

    pos = skip_numbers(d, pos)

    if pos < d_length and d[pos] == decimal_point:
        pos += 1
    else:
        return pos, int(d[number_start_pos:pos])

    # there may be a floating-point number
    if not d[pos] in numbers:
        raise_unexpected_char(d, pos)

    pos = skip_numbers(d, pos)

    return pos, float(d[number_start_pos:pos])


def parse_cooridate(d: str, pos: int):
    d_length = len(d)

    pos, x = parse_number(d, pos)

    pos = skip_seps(d, pos)
    if not pos < d_length:
        raise_unexpected_end_of_data(d, pos)

    pos = skip_seps(d, pos)

    pos, y = parse_number(d, pos)

    return pos, (x, y)


class PathCommand:
    def __init__(self, command: str, args: tuple):
        self.command = command
        self.args = args

    def __repr__(self):
        return repr((self.command, self.args))


def parse_command(c: str, d: str, pos: int):

    if c in moveto_commands:
        pos, (x, y) = parse_cooridate(d, pos)
        return pos, PathCommand(c, (x, y))

    elif c in curveto_commands:
        pos, (x1, y1) = parse_cooridate(d, pos)
        pos, (x2, y2) = parse_cooridate(d, pos)
        pos, (x, y) = parse_cooridate(d, pos)
        return pos, PathCommand(c, (x1, y1, x2, y2, x, y))

    elif c in smooth_curveto_commands:
        pos, (x2, y2) = parse_cooridate(d, pos)
        pos, (x, y) = parse_cooridate(d, pos)
        return pos, PathCommand(c, (x2, y2, x, y))

    else:
        raise Exception(f'Unsupported command {c} at {pos} in {repr(d)}!')


def parse_d_property(d: str):
    if len(d) == 0:
        raise Exception('Cannot parse empty string!')

    command_list = []
    pos = 0
    d_length = len(d)
    pos = skip_seps(d, pos)

    last_command = None

    pos = skip_seps(d, pos)

    while pos < d_length:
        c = d[pos]
        pos += 1

        if c in commands:
            pos, path_command = parse_command(c, d, pos)
            command_list.append(path_command)
            last_command = c
        elif (c in numberic_chars) and (last_command is not None):
            pos, path_command = parse_command(last_command, d, pos - 1)
            command_list.append(path_command)
        else:
            raise_unexpected_char(d, pos)

        pos = skip_seps(d, pos)

    return command_list


if __name__ == '__main__':
    sample_d = 'M47.92,48.66c0.27,0.35,0.28,0.59,0.43,1.03c1.24,3.62,2.82,14.22,3.59,20.96'
    data = parse_d_property(sample_d)
    print(sample_d)
    print(*data)