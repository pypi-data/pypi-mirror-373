# argparse\_decoration

A argparse wrapper through decorations

## 30 sec tutorial

Given `test.py` with:

```
#!/bin/python3

from argparse_decorations import init, Command, parse_and_run

init()

@Command('mycommand')
def handler():
    print('Hello!')

parse_and_run()

```

then `./test.py` produces:

```
usage: test.py [-h] {mycommand} ...

Help message

positional arguments:
  {mycommand}

options:
  -h, --help   show this help message and exit
```


and `./test.py mycommand`:

```
Hello!
```


## 1 min tutorial

The program:

```
from argparse_decorations import init, Command, SubCommand, Argument, parse_and_run

init()

@Command('mycommand')
@SubCommand('add')
@Argument('a', type=int)
@Argument('b', type=int)
def add_handler_but_could_be_any_identifier(a, b):
    print(a + b)

parse_and_run()
```

when called `./test.py mycommand add 1 2` produces:

`3`


`@Command` and `@SubCommand` will make a call to `ArgumentParser.add_parser()` and `@Argument` will call `ArgumentParser.add_argument`
These calls are made 'as-is' passing every `*args` and `**kwargs` passed on decorations to commands


A complete example whose explore all possibilities:

```python
@Command('math')
@SubCommand('add')
@Argument('valueA', type=int)
@Argument('valueB', type=int)
def add_handler(valueA, valueB):
    print('Adding args ' + str(valueA) + ' and ' + str(valueB))
    print(valueA + valueB)


@Command('math')
@SubCommand('sub')
@Argument('valueA', type=int)
@Argument('valueB', type=int)
def subtract_handler(valueA, valueB):
    print('Subtracting args ' + str(valueA) + ' and ' + str(valueB))
    print(valueA - valueB)


@Command('math')
@SubCommand('mul')
@Argument('valueA', type=int)
@Argument('valueB', type=int)
def subtract_handler(valueA, valueB):
    print('Multiplying args ' + str(valueA) + ' and ' + str(valueB))
    print(valueA * valueB)


@Command('math')
@SubCommand('pi')
def pi():
    print('3.1415926535979')
```


