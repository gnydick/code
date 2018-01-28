# Programming Assignment: SQL Evaluator

Write a command-line program that loads table data into memory and executes simple SQL queries on that data.

You don't have to write a SQL parser.  We've provided a program (`sql-to-json`) that will convert [our subset of SQL](#sql-syntax) into an easy-to-use [JSON structure](#json-formatted-sql).

Your program should:
1. Accept a single file as its command-line argument.  This file will contain a JSON-formatted SQL query.
2. Load any tables referenced by the query.  For example, if the query references the table name “countries”, you should load the table data from “countries.table.json” (see [".table.json"](#table-json)).
3. Handle the following SQL clauses:
    * `FROM`
    * `WHERE`
    * `SELECT`
    * inner join (using [implicit join notation](https://en.wikipedia.org/wiki/Join_(SQL)#Inner_join); see example-3.sql)
4. Detect logical errors in the query.
5. If there are no errors, execute the query and print the output in a human-readable tabular format.

You should perform the evaluation entirely in memory, using the standard data structures provided by your programming language.  You can use libraries to help with JSON parsing/loading.

You can assume that the JSON input files are correctly structured.  However, there may be logical errors in the queries that you should detect.  A few examples of logical errors:
- References to column names that don't exist.
- Ambiguous column references (the column name exists in multiple tables).
- Use of a comparison operator (e.g. “>”) on incompatible types (string vs integer).

## Toy Examples

- Make sure you have Python 2.7+ or 3.2+ installed (check: `python --version`).
- Example table data: "countries.table.json" and "cities.table.json"
- Example queries: the ".sql" files.
- Expected output for each query: the ".out" files.  (The order of the rows doesn't matter.)

To test the "example-1.sql" query:

```
$ ./sql-to-json example-1.sql > example-1.json
$ YOUR-PROGRAM example-1.json
```

In the Bash shell, you can do this without creating an intermediate ".json" file:

```
$ YOUR-PROGRAM <(./sql-to-json example-1.sql)
```

## Evaluation Criteria

Primarily, we're looking for code that is correct and easy to understand.

If you've gotten things working, consider ways to improve efficiency, assuming that the common case involves loading the tables once and executing many queries.

Obviously, time is limited so not everything can be perfect.  Just be prepared to discuss why you made the choices you made.

## File Formats

### Table JSON

Each file is a JSON array of rows.  The first element of the array is a list of column definitions.  Each column definition is an array where the first element is the column name and the second element is the column type.  The column type can be "str" or "int".

The rest of the elements are the row values.  They will be strings or integers.

See cities.table.json for an example.

### SQL Syntax

NOTE: You don't have to write a parser for this syntax.  Use the included Python program `sql-to-json` to convert SQL to a JSON-formatted equivalent.

NOTE: This isn't heavily based on standard SQL but isn't exactly compatible.

```
Query =
    "SELECT" Selector ("," Selector)*
    "FROM" TableRef ("," TableRef)*
    ( "WHERE" Comparison ("AND" Comparison)* )?

Selector = SelectorSource ( "AS" <identifier> )?

SelectorSource = ColumnRef
               | "COUNT"
               | "SUM" "(" ColumnRef ")"

Comparison = Term ( "=" | "!=" | ">" | ">=" | "<" | "<=" ) Term

Term = ColumnRef | <string-literal> | <integer-literal>

ColumnRef = <identifier> ("." <identifier>)?
     
TableName = <identifier>
```

Comments start with "--" and go to the end of the line.

### JSON-formatted SQL

```
Query = {
    select: Array<Selector> // non-empty array
    from: Array<TableRef> // non-empty array
    where: Array<Comparison>
}

Selector = {
    source: {column: ColumnRef} | {count: null} | {sum: ColumnRef}
    as: string | null  // Set when there's an "AS" clause
}

TableRef = {
    source: {file: string}
    as: string | null  // Set when there's an "AS" clause
}

Comparison = {
    op: "=" | "!=" | ">" | ">=" | "<" | "<="
    left: Term
    right: Term
}

Term = {column: ColumnRef} | {lit_int: int} | {lit_str: string}

ColumnRef = {
    name: string
    table: string | null  // Set for fully-qualified references ("table1.column2")
}
```
