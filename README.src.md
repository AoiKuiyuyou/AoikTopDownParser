[:var_set('', """
# Compile command
aoikdyndocdsl -s README.src.md -g README.md
""")]\
[:HDLR('heading', 'heading')]\
# AoikTopDownParser
A top-down recursive descent predictive or backtracking parser generator.

Tested working with:
- Python 2.7, 3.0+

## Table of Contents
[:toc(beg='next', indent=-1)]

## Setup
[:tod()]

### Setup via pip
Run:
```
pip install AoikTopDownParser
```
Or run:
```
pip install git+https://github.com/AoiKuiyuyou/AoikTopDownParser
```

### Setup via python
Run:
```
wget https://github.com/AoiKuiyuyou/AoikTopDownParser/archive/master.zip

unzip master.zip

cd master

python setup.py install
```

## Usage
Run after installation:
```
aoiktopdownparser
```
Or run after installation:
```
python -m aoiktopdownparser
```
Or run without installation:
```
python AoikTopDownParser/src/aoiktopdownparser/__main__.py
```

## Demo
[:tod()]

### Create a parser template
Run:
```
aoiktopdownparser -e parser_tplt.py
```

### Generate a calculator parser
See the [rules file](/src/aoiktopdownparser/demo/calculator/parser_rules.txt).

Generate the parser:
```
aoiktopdownparser -r AoikTopDownParser/src/aoiktopdownparser/demo/calculator/parser_rules.txt -t parser_tplt.py -o calculator_parser.py
```

Run the parser:
```
python calculator_parser.py -s _SOURCE_FILE_ -d
```

### Generate a JSON parser
See the [rules file](/src/aoiktopdownparser/demo/json/parser_rules.txt).

Generate the parser:
```
aoiktopdownparser -r AoikTopDownParser/src/aoiktopdownparser/demo/json/parser_rules.txt -t parser_tplt.py -o json_parser.py
```

Run the parser:
```
python json_parser.py -s _SOURCE_FILE_ -d
```

### Generate the parser of the parser generator
See the [rules file](/src/aoiktopdownparser/gen/parser_rules.txt).

Generate the parser:
```
aoiktopdownparser -r AoikTopDownParser/src/aoiktopdownparser/gen/parser_rules.txt -t AoikTopDownParser/src/aoiktopdownparser/gen/parser_tplt.py -o parser_generator_parser.py
```

Run the parser:
```
# Linux
export PYTHONPATH=AoikTopDownParser/src

# Windows
SET PYTHONPATH=AoikTopDownParser/src

python parser_generator_parser.py -s AoikTopDownParser/src/aoiktopdownparser/gen/parser_rules.txt -d
```
