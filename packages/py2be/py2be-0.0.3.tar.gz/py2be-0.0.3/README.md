# py2be <!-- omit in toc -->

![Language](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![GitHub release](https://img.shields.io/github/v/release/synesissoftware/py2be.svg)](https://github.com/synesissoftware/py2be/releases/latest)
[![Last Commit](https://img.shields.io/github/last-commit/synesissoftware/py2be)](https://github.com/synesissoftware/py2be/commits/master)
[![PyPI version](https://badge.fury.io/py/py2be.svg)](https://badge.fury.io/py/py2be)

Simple Python library determining whether strings indicate truey or falsy values.


## Introduction

**to-be** is a library providing facilities for determine whether the truthyness of strings. It implemented in several languages: **py2be** is the **Python** implementation.


## Table of Contents <!-- omit in toc -->


- [Introduction](#introduction)
- [Terminology](#terminology)
- [Project Information](#project-information)
	- [Where to get help](#where-to-get-help)
	- [Contribution guidelines](#contribution-guidelines)
	- [Dependencies](#dependencies)
		- [Dev Dependencies](#dev-dependencies)
	- [Related projects](#related-projects)
	- [License](#license)


## Terminology

The term "*truthy*" is an unhelpfully overloaded term in the programming world, insofar as it is used to refer to the notion of "truthyness" - whether something can be _deemed to be_ interpretable as truth - and also the true side of that interpretation. In this library, the former interpretation is used, leaving us with the following terms:

* "*truthy*" - whether something can be can be _deemed to be_ interpretable as having truth;
* "*falsey*" - whether an object can be _deemed to be_ interpretable as being false;
* "*truey*" - whether an object can be _deemed to be_ interpretable as being true;

For example, consider the following **Python** program:

```Python
from py2be import (
	string_is_falsey,
	string_is_truey,
	string_is_truthy,
)

s1 = "no"
s2 = "True"
s3 = "orange"

# "no" is validly truthy, and is falsey
assert string_is_falsey(s1)
assert !string_is_truey(s1)
assert string_is_truthy(s1)

# "True" is validly truthy, and is truey
assert !string_is_falsey(s2)
assert string_is_truey(s2)
assert string_is_truthy(s2)

# "orange" is not validly truthy, and is neither falsey nor truey
assert !string_is_falsey(s3)
assert !string_is_truey(s3)
assert !string_is_truthy(s3)
```


## Project Information

### Where to get help

[GitHub Page](https://github.com/synesissoftware/py2be "GitHub Page")


### Contribution guidelines

Defect reports, feature requests, and pull requests are welcome on https://github.com/synesissoftware/py2be.


### Dependencies

**py2be** has no (non-development) dependencies.


#### Dev Dependencies

**py2be** has no (additional) development dependencies.


### Related projects

* [**to-be**](https://github.com/synesissoftware/to-be) (**C**);
* [**to_be.Ruby**](https://github.com/synesissoftware/to_be.Ruby);
* [**to-be.Rust**](https://github.com/synesissoftware/to-be.Rust);


### License

**py2be** is released under the 3-clause BSD license. See [LICENSE](./LICENSE) for details.


<!-- ########################### end of file ########################### -->

