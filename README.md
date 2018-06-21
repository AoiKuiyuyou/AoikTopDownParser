# AoikTopDownParser
A top-down recursive-descendent parser generator.

Tested working with:
- Python 2.7, 3.6

## Table of Contents
- [Setup](#setup)
  - [Setup via pip](#setup-via-pip)
  - [Setup via git](#setup-via-git)
- [Usage](#usage)
- [Demo](#demo)
  - [Generate a calculator parser](#generate-a-calculator-parser)
  - [Generate a JSON parser](#generate-a-json-parser)
  - [Generate the parser of the parser generator](#generate-the-parser-of-the-parser-generator)

## Setup
- [Setup via pip](#setup-via-pip)
- [Setup via git](#setup-via-git)

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
- [Generate a calculator parser](#generate-a-calculator-parser)
- [Generate a JSON parser](#generate-a-json-parser)
- [Generate the parser of the parser generator](#generate-the-parser-of-the-parser-generator)

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
