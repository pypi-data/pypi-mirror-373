# Syncraft

Syncraft is a parser/generator combinator library with full round-trip support:

- Parse source code into AST or dataclasses
- Generate source code from dataclasses
- SQLite syntax support included

## Installation

```bash
pip install syncraft
```


## TODO
- [ ] define DSL over Variable to construct predicates
- [ ] Try the parsing, generation, and data processing machinery on SQLite3 syntax. So that I can have direct feedback on the usability of this library and a fully functional SQLite3 library.
- [ ] Make the library as fast as possible and feasible.