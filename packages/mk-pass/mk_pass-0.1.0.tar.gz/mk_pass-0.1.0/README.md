[cli-doc]: https://mk-pass.readthedocs.io/en/latest/cli/

<!-- start -->

# Comprehensive Password Generator

This cross-platform compatible software will generate a password comprehensively.

[![rust-ci-badge][rust-ci-badge]][rust-ci-link]
[![cpp-ci-badge][cpp-ci-badge]][cpp-ci-link]
[![python-ci-badge][python-ci-badge]][python-ci-link]
[![node-ci-badge][node-ci-badge]][node-ci-link]
[![codecov-badge][codecov-badge]][codecov-link]
[![rtd-badge][rtd-badge]][rtd-link]
[![CHANGELOG][changelog-badge]][changelog-link]

[rust-ci-badge]: https://github.com/2bndy5/mk-pass/actions/workflows/rust.yml/badge.svg
[rust-ci-link]: https://github.com/2bndy5/mk-pass/actions/workflows/rust.yml
[cpp-ci-badge]: https://github.com/2bndy5/mk-pass/actions/workflows/cpp.yml/badge.svg
[cpp-ci-link]: https://github.com/2bndy5/mk-pass/actions/workflows/cpp.yml
[python-ci-badge]: https://github.com/2bndy5/mk-pass/actions/workflows/python.yml/badge.svg
[python-ci-link]: https://github.com/2bndy5/mk-pass/actions/workflows/python.yml
[node-ci-badge]: https://github.com/2bndy5/mk-pass/actions/workflows/node.yml/badge.svg
[node-ci-link]: https://github.com/2bndy5/mk-pass/actions/workflows/node.yml
[codecov-badge]: https://codecov.io/gh/2bndy5/mk-pass/graph/badge.svg?token=6WKCQFHZTQ
[codecov-link]: https://codecov.io/gh/2bndy5/mk-pass
[rtd-badge]: https://img.shields.io/readthedocs/mk-pass
[rtd-link]: https://mk-pass.readthedocs.io/
[changelog-badge]: https://img.shields.io/badge/keep_a_change_log-v1.1.0-ffec3d
[changelog-link]: https://mk-pass.readthedocs.io/en/latest/CHANGELOG/

## Features

Admittedly, the word "comprehensive" is not a scientific term.
In this software, the term "comprehensive" boasts the following features
when generating a password:

1. No characters are repeated (unless explicitly allowed).
2. Ensure at least one of each type of character is present:
    - uppercase letters
    - lowercase letters
    - decimal integers (if permitted)
    - special characters (if permitted)
3. Ensure the first character is a letter (if enabled).
   When enabled, the first character will be either a uppercase or
   lowercase alphabetical letter.

### What is a "special" character?

This software uses the following set of characters to generate special characters in a password:

> ``- . / \ : ` + & , @ $ ! _ # % ~``

The space character is not actually considered a special character,
but spaces are used to make the above set more readable.

Obviously, this is not an exhaustive list of all printable, non-alphanumeric characters.
However, these are special characters that are widely accepted by most sign-on services.

## Command Line Interface

While this software can be used as a library, a binary executable is also provided for each release.

A document generated from the rust sources details the CLI options.
See the hosted [CLI doc][cli-doc].

The following command will print the available options and their default values.

```shell
mk-pass -h
```
