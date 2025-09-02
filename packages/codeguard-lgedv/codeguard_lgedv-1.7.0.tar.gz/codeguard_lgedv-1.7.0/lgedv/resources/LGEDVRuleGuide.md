## Rule LGEDV_CRCL_0001:
Definition: Always use named constants or enumerations instead of hard-coded numeric values (magic numbers) in the code.

## Rule LGEDV_CRCL_0002:
Definition: Eliminate duplicate code by creating shared classes or functions for similar operations.

## Rule LGEDV_CRCL_0003:
Definition: Only allow early return statements for guard clauses (such as input validation) at the start of a function. The main logic of the function must have only one return statement at the end.

## Rule LGEDV_CRCL_0004:
Definition: Initialize return values to an error or failure state (e.g., negative, false, or FAILED) by default.

## Rule LGEDV_CRCL_0008:
All log statements must use a common utility function to ensure a consistent log format throughout the codebase. Do not use custom or ad-hoc logging formats.

## Rule LGEDV_CRCL_0009:
Definition: Functions should have a cyclomatic complexity less than 10. Refactor complex functions for better readability and maintainability.

## Rule LGEDV_CRCL_0010:
Definition: Return values must be meaningful. Avoid returning only a boolean (e.g., just True). Change the return type if a simple boolean is not sufficient.

## Rule LGEDV_CRCL_0011:
Definition: Add a log statement at the start of each function, especially for public interfaces. Log important information for decision branches.

## Rule LGEDV_CRCL_0012:
Definition: Ensure file data is synchronized to disk after modifications by calling sync after flush or close, considering performance impact.

## Rule LGEDV_CRCL_0013:
Definition: Every case in a switch statement must end with a break statement unless intentional fall-through is clearly documented.

## Rule LGEDV_CRCL_0014:
Definition: Always check pointer parameters for null before use, and validate array or vector indices to prevent out-of-bounds access.

## Rule LGEDV_CRCL_0015:
Definition: If a switch case contains two or more statements, enclose them in curly braces to form a code block.

## Rule LGEDV_CRCL_0016:
Definition: Use bounded C functions (e.g., snprintf instead of sprintf) to prevent buffer overflows.

## Rule LGEDV_CRCL_0018:
Definition: Avoid naming conflicts between classes or constants in libraries and applications by using unique names or namespaces.

## Rule LGEDV_CRCL_0019:
Definition: Every function should return a meaningful value. Reconsider the use of void return types; use them only when no return value is necessary.

## Rule LGEDV_CRCL_0020:
Definition: Release all allocated resources (memory, files, mutexes, etc.) before exiting a function to prevent resource leaks.