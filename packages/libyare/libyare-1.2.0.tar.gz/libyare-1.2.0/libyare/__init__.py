#!/usr/bin/python

'''
LIBrary for YARE (Yet Another Regular Expression) pattern matching


CONTENTS

    • 1.     Forewords
    • 1.1.   Introduction
    • 1.2.   Installation
    • 2.     Functions
    • 2.1.   Match Functions
    • 2.2.   Other Functions
    • 3.     Patterns
    • 3.1.   Simple Patterns
    • 3.1.1. Shell Patterns
    • 3.1.2. Charset Patterns
    • 3.1.3. Numeric Patterns
    • 3.2.   Compound Patterns
    • 4.     Afterwords
    • 4.1.   Versions
    • 4.2.   Credits

1. FOREWORDS

1.1. INTRODUCTION

LIBYARE  implements  YARE  (Yet  Another  Regular Expression). YARE is a
regular expression format intended to be more readable than the standard
one.  It  can  accept  simple  patterns  and  compound  patterns. Simple
patterns  can  be  shell patterns, charset patterns or numeric patterns.
Compound  patterns are obtained by combining together simple patterns by
logical operators and parenthesis.

1.2. INSTALLATION

If for instance your Linux belongs to the Debian family, type:

    $ sudo apt install pipx

Then type:

    $ pipx install libyare
    $ pipx ensurepath

Now you can close and reopen your terminal and get this help by typing:

    $ libyare -h

...and you can check the LIBYARE version by:

    $ libyare -V

Later you can upgrade LIBYARE to a new version by:

    $ pipx upgrade libyare

2. FUNCTIONS

2.1. MATCH FUNCTIONS

In  order  to  use  LIBYARE  in  your  PyPI  project,  link  it  in your
pyproject.toml file:

    ...
    [project]
    ...
    dependencies = ["libyare", ...]
    ...

Then in your program you can write:

    from libyare import *

and use these four match functions:

    yarecsmatch(string, pattern) # case-sensitive match

    yarecimatch(string, pattern) # case-insensitive match

    yarecmmatch(string, pattern) # case-multiple match, see 3.1.1.

    yareosmatch(string, pattern) # system-dependent match, see 3.1.1.

2.2. OTHER FUNCTIONS

LIBYARE exports these three functions too:

    int2human(int, length=6) # converts integer into human-readable,
                             # result length must be between 5 and 9

    human2int(string) # converts human-readable string into integer,
                      # on error raises ValueError

    is_human(string) # check human-readable string
                     # return True if string is ok, else False

For details about strings in human-readable integer format, see 3.1.3.

3. PATTERNS

3.1. SIMPLE PATTERNS

3.1.1. SHELL PATTERNS

General rules:

    • '*' matches everything
    • '?' matches any single character
    • '[seq]' matches any single character in seq
    • '[!seq]' matches any single character not in seq

Examples:

    • pattern 'abc*' matches any string starting with 'abc'
    • pattern '*abc' matches any string ending with 'abc'
    • pattern '*abc*' matches any string containing 'abc'
    • pattern '[az]' matches 'a' or 'z'
    • pattern '[!az]' matches any single character except 'a' or 'z'
    • pattern '[a-z]' matches any single character between 'a' and 'z'
    • pattern  '[!a-z]' matches any single character not between 'a' and
      'z'
    • pattern  '[a-z0-9_]'  matches any single character between 'a' and
      'z' or between '0' and '9' or equal to '_'
    • pattern  '[!a-z0-9_]' matches any single character not between 'a'
      and 'z' and not between '0' and '9' and not equal to '_'

If  a  metacharacter  must  belong  to  a  shell pattern with no special
meaning, it must be quoted between '[' and ']'. More exactly:

    • '*' '?' '[' '^' '&' ',' '(' and ')' must always be quoted
    • '!' and '-' if not between '[' and ']' have no special meaning and
      don't need to be quoted
    • '=' '<' and '>' need to be quoted only if in first position
    • ']'  only can not be quoted, but you should not need it because an
      unmatched  ']'  has  no special meaning and doesn't raise a syntax
      error, while unmatched '[' '(' and ')' do

Examples:

    • pattern  '[(]*[)]' matches any string starting with '(' and ending
      with ')'
    • pattern  '[[]*]'  matches  any string starting with '[' and ending
      with ']'
    • pattern  '[<]*>'  matches  any string starting with '<' and ending
      with '>'
    • pattern '[=][[]?*]' matches any charset pattern, see 3.1.2.

You can quote '!' too, but not immediately after '[':

    • pattern '[?!]' matches '?' and '!'
    • pattern '[!?]' matches any character except '?'

You  can  quote metacharacter '-' too, a '-' after '[' or before ']' has
no special meaning:

    • patterns '[-pr]' and '[pr-]' match '-' 'p' and 'r'
    • pattern '[p-r]' matches 'p' 'q' and 'r'

'-' stands for itself even after a character interval:

    • pattern '[p-rx]' matches 'p' 'q' 'r' and 'x'
    • pattern '[p-r-x]' matches 'p' 'q' 'r' '-' and 'x'
    • pattern '[p-rx-z]' matches 'p' 'q' 'r' 'x' 'y' and 'z'
    • pattern '[p-r-x-z]' matches 'p' 'q' 'r' '-' 'x' 'y' and 'z'

Descending character intervals do not work:

    • pattern '[z-z]' is accepted and is equivalent to '[z]'
    • pattern '[z-a]' is accepted but it does not match anything

They  are  only  two  differences  between  shell  patterns  defined  by
fnmatch()  and  fnmatchcase()  functions  in  Python3 fnmatch module and
shell patterns accepted by YARE:

    • unmatched  '[' (as in pattern 'abc[def') is allowed by fnmatch but
      is rejected by YARE as a syntax error
    • null pattern '' is allowed by fnmatch but is rejected by YARE as a
      syntax error (see later for a workaround to match a null string by
      a not null pattern)

Match of shell patterns can be:

    • case-sensitive, by yarecsmatch() function
    • case-insensitive, by yarecimatch() function
    • case-multiple, by yarecmmatch() function
    • system-dependent, by yareosmatch() function

Case-multiple  match  is case-sensitive for shell patterns containing at
least one lowercase letter, case-insensitive for the others:

    • with yarecmmatch(), pattern 'RAM,*.db' matches 'ram', 'RAM', 'Ram'
      and 'xy.db' but not 'xy.Db' or 'xy.DB'

System-dependent  match  for  shell  patterns is case-insensitive if the
current platform requires it, else is case-sensitive:

    • with   yareosmatch(),   pattern  '*.jpg'  matches  'xy.JPG'  under
      MS-Windows, but not under Linux

3.1.2. CHARSET PATTERNS

A charset pattern starts with '=[' and ends with ']', it is made up of a
'='  character  followed  by  a shell pattern suitable to match a single
character.  It  matches  the  null  string  and  all  strings where each
character matches the given shell pattern:

    • pattern '=[0-9]' matches the null string and any string made up of
      only digits (it is equivalent to '^*[!0-9]*')
    • pattern  '=[!0-9]'  matches the null string and any string made up
      of only non-digit characters (it is equivalent to '^*[0-9]*')

Charset match is always case-sensitive:

    • pattern '=[a-zA-Z0-9_]&[!0-9]*' matches Python identifiers

3.1.3. NUMERIC PATTERNS

A  numeric  pattern  is  made up of a comparison operator followed by an
integer   in  human-readable  format.  It  matches  all  strings  which,
converted  from  human-readable  format  into integer, satisfy the given
comparison. Allowed comparison operators are:

    • '<' = less than
    • '=' = equal
    • '>' = greater than
    • '<=' = less or equal
    • '<>' = not equal
    • '>=' = greater or equal

An integer in human-readable format is made up of:

    • an optional plus '+' or minus '-' sign
    • an integer or float literal
    • an optional final alphabetic multiplier:
        • 'K' = 1024
        • 'M' = 1024 ** 2
        • 'G' = 1024 ** 3
        • 'T' = 1024 ** 4
        • 'P' = 1024 ** 5
        • 'E' = 1024 ** 6
        • 'Z' = 1024 ** 7
        • 'Y' = 1024 ** 8

Examples:

    • patterns '<0.5K' and '<512' are equivalent, they match all strings
      which,  interpreted as a human-readable integer, give a value less
      than 512
    • patterns  '<0.5E3'  and  '<500'  are  equivalent,  they  match all
      strings  which,  interpreted  as  a human-readable integer, give a
      value less than 500

Numeric   match   is   always  case-insensitive,  the  final  alphabetic
multiplier and the 'E' in float literals can be uppercase or lowercase.

Both   pattern   and  string  can  give  an  error  in  conversion  from
human-readable format into integer. A pattern error raises a SyntaxError
exception, while a string error makes the match function return a result
of False:

    • pattern '=0,<>0' matches the strings in well-formed human-readable
      integer format

3.2. COMPOUND PATTERNS

A  compound  pattern  is  made by combining simple patterns with logical
operators:

    • '^' = not
    • '&' = and
    • ',' = or

and parenthesis '(' and ')'.

In the following examples, p and q are two simple patterns:

    • pattern '^p' matches any string not matched by p
    • pattern 'p&q' matches any string matched by both p and q
    • pattern 'p,q' matches any string matched by p or q or both
    • pattern  '*.jpg,*.mp4'  matches  any  string ending with '.jpg' or
      with '.mp4'
    • pattern '^*' does not match anything
    • pattern '?*' matches any string of one or more characters, so...
    • ...pattern '^?*' matches the null string and nothing else

Two '^' characters cancel each other out:

    • patterns '^^p' and 'p' are equivalent

Precedence  is  of  course  '^' > '&' > ','. Precedence can be forced by
parenthesis, so for instance the De Morgan's laws tell us that:

    • patterns '^p&^q' and '^(p,q)' are equivalent
    • patterns '^p,^q' and '^(p&q)' are equivalent

Nesting of parenthesis has no practical limit.

4. AFTERWORDS

4.1. VERSIONS

    • 1.2.0 (Production/Stable)
        • compatible with previous version
        • added: numeric patterns

    • 1.1.0 (Production/Stable)
        • compatible with previous version
        • added: charset patterns
        • added: case-multiple match by yarecmmatch() function

    • 1.0.0 (Production/Stable)
        • incompatible with previous versions
        • simplified redefined and optimized

    • 0.4.3 (Experimental/Deprecated)
        • updated: documentation

    • 0.4.2 (Experimental/Deprecated)
        • updated: documentation

    • 0.4.1 (Experimental/Deprecated)
        • first version published on pypi.org '

4.2. CREDITS

LIBYARE  program  has  been developed by Python 3.11.2 and IDLE 3.11.2.,
see https://www.python.org...

...under Debian GNU/Linux 12.11 (bookworm), see https://www.debian.org.

LIBYARE  package has been built and published on pypi.org by FLIT 3.12.0
(a     simple    packaging    tool    for    simple    packages),    see
https://pypi.org/project/flit.

This  help  text  has  been  written  by  YAWP  2.1.1  (Yet Another Word
Processor,  a word processor for plain text files, with PDF export), see
https://pypi.org/project/yawp.

'''

__version__ = '1.2.0'

from fnmatch import fnmatch, fnmatchcase
from re import error as ReError

__all__ = ['yarecsmatch', 'yarecimatch', 'yarecmmatch', 'yareosmatch', 'int2human', 'human2int', 'is_human'] # exported functions
NOT, AND, OR, LEFT, RIGHT, PATTERN = '^&,()*' # tokens: operators and patterns
RANK_NOT, RANK_AND, RANK_OR, RANK_LEFT, RANK_RIGHT = [3, 2, 1, 0, 0] # operator priorities
RANK = {NOT: RANK_NOT, AND: RANK_AND, OR: RANK_OR, LEFT: RANK_LEFT, RIGHT: RANK_RIGHT}
OPERATORS = frozenset(RANK.keys()) # YARE metacharacters
AFTER = {NOT:     frozenset([PATTERN, NOT, LEFT]), # token sequence check
         AND:     frozenset([PATTERN, NOT, LEFT]),
         OR:      frozenset([PATTERN, NOT, LEFT]), 
         LEFT:    frozenset([PATTERN, NOT, LEFT]),
         RIGHT:   frozenset([OR, AND, RIGHT]),
         PATTERN: frozenset([OR, AND, RIGHT])}
NOT_IN_SIMPLE, IN_SIMPLE, IN_BRAKES = [0, 1, 2] # status values for scanner()
scanned = {} # cache for results of scanner()

def scanner(pattern):
    '''translate pattern into a list of tokens, checking the correct token sequence,
each token will be either a one-character operator (OR, AND, NOT, LEFT or RIGHT) or a simple PATTERN'''
    try:
        return scanned[pattern]
    except KeyError:
        tokens = []
        status = NOT_IN_SIMPLE
        allowed = LEFT
        for char in LEFT + pattern + RIGHT:
            if status == NOT_IN_SIMPLE:
                tokens.append(char)
                if char in OPERATORS: # char is an operator
                    if char not in allowed:
                        raise ValueError
                    allowed = AFTER[char]
                else: # char starts a simple pattern
                    if PATTERN not in allowed:
                        raise ValueError
                    allowed = AFTER[PATTERN]
                    status = IN_BRAKES if char == '[' else IN_SIMPLE
            elif status == IN_SIMPLE:
                if char in OPERATORS: # char is an operator, simple pattern ends
                    if char not in allowed:
                        raise ValueError
                    allowed = AFTER[char]
                    tokens.append(char)
                    status = NOT_IN_SIMPLE
                else: # simple pattern continues
                    tokens[-1] += char
                    if char == '[':
                        status = IN_BRAKES
            else: # status == IN_BRAKES, hence between '[' and ']'
                tokens[-1] += char
                if char == ']':
                    status = IN_SIMPLE
        if status == IN_BRAKES:
            raise ValueError # unmatched '[' is not allowed
        scanned[pattern] = tokens
        return tokens

def take(string, allowed, default=''):
    'take allowed chars from string, translate the others into default'
    return ''.join(char if char in allowed else default for char in string) 

def drop(string, forbidden, default=''):
    'drop forbidden chars from string, translate the others into default'
    return ''.join(default if char in forbidden else char for char in string)

def chars(pattern):
    'return chars matched by pattern'
    return ''.join(chr(j) for j in range(ord(min(pattern)), ord(max(pattern)) + 1) if fnmatchcase(chr(j), pattern))

def int2human(int, length=6):
    'convert int into human-readable string, 5 <= length <= 9'
    if not (5 <= length <= 9):
        raise ValueError
    if abs(int) < 1024:
        return f'{int:{length}d}'
    else:
        real = float(int)
        for char in 'KMGTPEZY':
            real /= 1024.0
            if abs(real) < 1024.0 or char == 'Y':
                return (str(real) + length * '0')[:length-1] + char

def human2int(string):
    'convert human-readable string into int'
    if not string:
        raise ValueError
    factor = 1
    j = 'KMGTPEZY'.find(string[-1].upper())
    if j >= 0:
        factor = 1024 ** (j + 1)
        string = string[:-1]
    string = drop(string, ',')
    try:
        return int(string) * factor
    except ValueError:
        try:
            return round(float(string) * factor)
        except (ValueError, OverflowError):
            raise ValueError

def is_human(string):
    'is string a well-formed human-readable integer?'
    try:
        human2int(string)
    except:
        return False
    else:
        return True      

def charset_numeric_match(string, pattern):
    'low-level match for charset or numeric pattern'
    if pattern.startswith('=[!'): # charset pattern
        if not pattern.endswith(']'):
            raise ValueError
        return not fnmatchcase(string, f'*[{pattern[3:]}*')
    elif pattern.startswith('=['):
        if not pattern.endswith(']'):
            raise ValueError
        return not fnmatchcase(string, f'*[!{pattern[2:]}*')
    else: # numeric pattern
        try:
            number = human2int(string)
        except ValueError:
            return False
        if pattern.startswith('<='):
            return number <= human2int(pattern[2:])
        elif pattern.startswith('>='):
            return number >= human2int(pattern[2:])
        elif pattern.startswith('<>'):
            return number != human2int(pattern[2:])
        elif pattern.startswith('<'):
            return number < human2int(pattern[1:])
        elif pattern.startswith('>'):
            return number > human2int(pattern[1:])
        elif pattern.startswith('='):
            return number == human2int(pattern[1:])
        else:
            raise ValueError

def csmatch(string, pattern):
    'case-sensitive low-level match'
    if '<' <= pattern[0] <= '>':
        return charset_numeric_match(string, pattern)
    else:
        return fnmatchcase(string, pattern)

def cimatch(string, pattern):
    'case-insensitive low-level match'
    if '<' <= pattern[0] <= '>':
        return charset_numeric_match(string, pattern)
    else:
        return fnmatchcase(string.upper(), pattern.upper())

def cmmatch(string, pattern):
    'case-multiple low-level match'
    if '<' <= pattern[0] <= '>':
        return charset_numeric_match(string, pattern)
    elif pattern == pattern.upper():
        return fnmatchcase(string.upper(), pattern.upper())
    else:
        return fnmatchcase(string, pattern)

def osmatch(string, pattern):
    'case-platform low-level match'
    if '<' <= pattern[0] <= '>':
        return charset_numeric_match(string, pattern)
    else:
        return fnmatch(string, pattern)

def yarecsmatch(string, pattern):
    'YARE case-sensitive match'
    return yarematch(string, pattern, match=csmatch)

def yarecimatch(string, pattern):
    'YARE case-insensitive match'
    return yarematch(string, pattern, match=cimatch)

def yarecmmatch(string, pattern):
    'YARE case-multiple match'
    return yarematch(string, pattern, match=cmmatch)

def yareosmatch(string, pattern):
    'YARE system-dependent match'
    return yarematch(string, pattern, match=osmatch)

def yarematch(string, pattern, match=None):
    "YARE match main function, it uses the Dijkstra's 'two-stacks' (aka 'shunting-yard') algorithm"
    
    def apply(operator):
        'apply operator (OR AND or NOT) on stack of values'
        if operator == OR:
            one = values[-2]
            two = values.pop()
            values[-1] = ((True if one is True else False if one is False else match(string, one)) or
                          (True if two is True else False if two is False else match(string, two)))
        elif operator == AND:
            one = values[-2]
            two = values.pop()
            values[-1] = ((True if one is True else False if one is False else match(string, one)) and
                          (True if two is True else False if two is False else match(string, two)))
        else: # operator == NOT
            one = values[-1]
            values[-1] = False if one is True else True if one is False else not match(string, one)

    operators = [] # stack of operators, each operator can be OR AND NOT or LEFT
    values = [] # stack of values, each value is either str (simple pattern yet to be matched) or bool (simple pattern already matched)
    try:
        for token in scanner(pattern):
            if token == OR:
                while operators and RANK[operators[-1]] >= RANK_OR:
                    apply(operators.pop())
                operators.append(OR)
            elif token == AND:
                while operators and RANK[operators[-1]] >= RANK_AND:
                    apply(operators.pop())
                operators.append(AND)
            elif token == NOT:
                while operators and RANK[operators[-1]] > RANK_NOT:
                    apply(operators.pop())
                operators.append(NOT)
            elif token == LEFT:
                operators.append(LEFT)
            elif token == RIGHT:
                while operators and operators[-1] != LEFT:
                    apply(operators.pop())
                operators.pop()
            else: # token is a simple pattern
                values.append(token)
        if operators or len(values) != 1:
            raise ValueError
        one = values[0]
        return True if one is True else False if one is False else match(string, one)
    except (IndexError, ValueError, ReError):
        raise SyntaxError(f'Syntax error in YARE pattern {pattern!r}')

