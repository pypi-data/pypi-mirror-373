# pacfix-python
Python re-implementation of [pacfix](https://github.com/pslhy/pacfix/tree/main).

## Install
```shell
python3 -m pip install pacfix
# Or, you can install from source code
# python3 -m pip install .
pysmt-install --z3
```

## Usage
To see how it works, check out the examples in the [examples](./examples/) directory.

```shell
cd examples/example01
python3 -m pacfix run -i ./mem -l live-variables.txt
```

## Inputs
### live variables file
Specify the live variables file using `-l` or `--live-vars` [live-variables.txt](./examples/example01/live-variables.txt).

```
1 x int
2 y int
3 z bool
4 b int
5 c int
```
Each line lists a variable's ID, name, and type, separated by spaces.

### Input directory
Specify the input directory using `-i` or `--input-dir` [input-dir](./examples/example01/mem).

The input directory should contain neg and pos subdirectories, each with valuation files.
```
[begin]
1 7
2 1
3 0
4 8
5 6
[end]
[begin]
1 1
2 7
3 1
4 8
5 -6
[end]
```
Each file should list variable IDs and their corresponding values. Multiple iterations can be included, with each iteration separated by [begin] and [end].

## Output
Specify the output file using `-o` or `--output`. 

If not specified, the output will be printed to the standard output.

```
[metadata] [live-variables] [total 5] [int 4]
[metadata] [hypothesis-space] [original 1857] [final 1]
[metadata] [valuation] [neg 3] [pos 48] [uniq 51] [init-neg 4] [init-pos 54] [non-uniq 58]
[metadata] [pac] [delta 0.01] [eps 0.09029745462721749]
[metadata] [pac-no-uniq] [delta 0.01] [eps 0.07939948596531193]
[final] --------------
[invariant] [expr (c != 0)]
```

### Output as SMT format
Specify the output directory as `-s` or `--output-smt`.

If not specified, it will not be stored.


```
python3 -m pacfix run -i ./mem -l live-variables.txt -s ./smt
```
In `./smt/0.smt`

```
(set-logic QF_IDL)
(declare-fun c () Int)
(assert (let ((.def_0 (= c 0))) (let ((.def_1 (not .def_0))) .def_1)))
(check-sat)
```

### Debug log
You can enable debug log with `-d` option.