[:var_set('', """
# Compile command
aoikdyndocdsl -s README.src.md -g README.md
""")]\
[:HDLR('heading', 'heading')]\
# AoikTopDownParser
A top-down recursive descent predictive or backtracking parser generator.

Tested working with:
- Python 2.7, 3.7

## Table of Contents
[:toc(beg='next', indent=-1)]

## Setup
[:tod()]

### Setup via pip
Run:
```
pip install AoikTopdownParser
```
or:
```
pip install git+https://github.com/AoiKuiyuyou/AoikTopdownParser
```

### Setup via git
Run:
```
git clone https://github.com/AoiKuiyuyou/AoikTopdownParser

cd AoikTopdownParser

python setup.py install
```

## Usage
Run:
```
aoiktopdownparser
```
Or:
```
python -m aoiktopdownparser
```
Or without installation:
```
python AoikTopdownParser/src/aoiktopdownparser/__main__.py
```

## Demo
[:tod()]

### Generate a calculator parser
See the [rules file](/src/aoiktopdownparser/demo/calculator/rules.txt).

Generate the parser:
```
aoiktopdownparser -r AoikTopdownParser/src/aoiktopdownparser/demo/calculator/rules.txt -o AoikTopdownParser/src/aoiktopdownparser/demo/calculator/opts.py::OPTS -g parser.py --rd
```

Run the parser:
```
python parser.py -s _SOURCE_FILE_ -d
```

Generate the parser (without creating a file) and parse a source file:
```
aoiktopdownparser -r AoikTopdownParser/src/aoiktopdownparser/demo/calculator/rules.txt -o AoikTopdownParser/src/aoiktopdownparser/demo/calculator/opts.py::OPTS -s _SOURCE_FILE_ --rd --gd
```

### Generate a JSON parser
See the [rules file](/src/aoiktopdownparser/demo/json/rules.txt).

Generate the parser:
```
aoiktopdownparser -r AoikTopdownParser/src/aoiktopdownparser/demo/json/rules.txt -o AoikTopdownParser/src/aoiktopdownparser/demo/json/opts.py::OPTS -g parser.py --rd
```

Run the parser:
```
python parser.py -s _SOURCE_FILE_ -d
```

Generate the parser (without creating a file) and parse a source file:
```
aoiktopdownparser -r AoikTopdownParser/src/aoiktopdownparser/demo/json/rules.txt -o AoikTopdownParser/src/aoiktopdownparser/demo/json/opts.py::OPTS -s _SOURCE_FILE_ --rd --gd
```

### Generate the parser of the parser generator
See the [rules file](/src/aoiktopdownparser/gen/me/rules.txt).

Generate the parser:
```
aoiktopdownparser -r AoikTopdownParser/src/aoiktopdownparser/gen/me/rules.txt -o AoikTopdownParser/src/aoiktopdownparser/gen/me/opts.py::OPTS -g parser.py --rd
```

Run the parser:
```
export PYTHONPATH=AoikTopdownParser/src
python parser.py -s AoikTopdownParser/src/aoiktopdownparser/gen/me/rules.txt -d
```

Generate the parser (without creating a file) and parse a source file:
```
aoiktopdownparser -r AoikTopdownParser/src/aoiktopdownparser/gen/me/rules.txt -o AoikTopdownParser/src/aoiktopdownparser/gen/me/opts.py::OPTS -s AoikTopdownParser/src/aoiktopdownparser/gen/me/rules.txt --rd --gd
```
