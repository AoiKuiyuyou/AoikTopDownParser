[:var_set('', """
# Compile command
aoikdyndocdsl -s README.src.md -g README.md
""")]\
[:HDLR('heading', 'heading')]\
# AoikTopDownParser
A top-down recursive-descendent parser generator.

Tested working with:
- Python 2.7, 3.6

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
cd AoikTopdownParser

python src/aoiktopdownparser/__main__.py
```

## Demo
[:tod()]

### Generate a calculator parser
See the [rules file](/src/aoiktopdownparser/demo/calculator/rules.txt).

Generate the parser:
```
aoiktopdownparser -r src/aoiktopdownparser/demo/calculator/rules.txt -o src/aoiktopdownparser/demo/calculator/opts.py::OPTS -g parser.py
```

### Generate a JSON parser
See the [rules file](/src/aoiktopdownparser/demo/json/rules.txt).

Generate the parser:
```
aoiktopdownparser -r src/aoiktopdownparser/demo/json/rules.txt -o src/aoiktopdownparser/demo/json/opts.py::OPTS -g parser.py
```

### Generate the parser of the parser generator
See the [rules file](/src/aoiktopdownparser/gen/me/rules.txt).

Generate the parser:
```
aoiktopdownparser -r src/aoiktopdownparser/gen/me/rules.txt -o src/aoiktopdownparser/gen/me/opts.py::OPTS -g parser.py
```
