## Rule LGEDV_CRCL_0001:
Definition: Use definition/enumerations instead of magic number.

## Rule LGEDV_CRCL_0002:
Definition: Remove duplicated source code. Make a common class to handle similar actions.

## Rule LGEDV_CRCL_0003:
Definition: Allows up to 1 return point in a function. Multiple returns are a violation.

## Rule LGEDV_CRCL_0004:
Definition: Default (Initialization) value of return need to be a negative/false/failure or any other error meaning. Initialize the returning value to FAILED or the negative meaning value.

## Rule LGEDV_CRCL_0005:
Definition: Use a meaningful variable name. Avoid to use uncommon naming without any related meaning.

## Rule LGEDV_CRCL_0007:
Definition: Do not use thread, looper unless there is an unavoidable reason.

## Rule LGEDV_CRCL_0009:
Definition: Recommended Cyclomatic Complexity is lower than 10 (some of function should be break down for readability, maintainability).

## Rule LGEDV_CRCL_0010:
Definition: Return value should be valid. Only return True has no meaning. Make change on return type if return value is not necessary.

## Rule LGEDV_CRCL_0011:
Definition: Add at least one log in the beginning of each function for log traceability, especially the interface function which called by other component. Add log to track the important information for branching.

## Rule LGEDV_CRCL_0012:
Definition: Should sync the data to make sure the actual file content reflect our modification. Interact with raw file need to call sync after flush or close with consideration of performance trade-off.

## Rule LGEDV_CRCL_0013 
Definition: Every switch case must have a break, if there is no break it is a violation.

## Rule LGEDV_CRCL_0014:
Definition: Pointer parameters need to be null checked before using it, and out-of-bound index memory accessing (access array/vector by index) should be checked before using it.

## Rule LGEDV_CRCL_0015:
Definition: A case (having >= 2 logical lines) in switch case should be a block of code. Wrap statements of a case in a curly bracce pair {}.

## Rule LGEDV_CRCL_0016:
Definition: Use bounded C functions instead of unbounded ones to prevent buffer overrun, for example, replace sprintf by snprintf.

## Rule LGEDV_CRCL_0018:
Definition: Using name space to void conflict class, constants name between library and apps. Wrap library in a namespace.

## Rule LGEDV_CRCL_0019:
Definition: Every function need to return valuable/meaningful return value. For void return functions need to be rechecked if void is really enough or not. 

## Rule LGEDV_CRCL_0020:
Definition: Every allocated resources (memory, file, mutex lock, etc) need to be released properly. Delete, free memories, close files, unlock mutex etc before leave the function.

## Rule MISRA 6-4-2
Definition: All if â€¦ else if constructs shall be terminated with an else clause.

## Rule MISRA 6-5-1
Definition: A for loop shall contain a single loop-counter which shall not have floating type.

## Rule MISRA 6-5-5
Definition: A loop-control-variable other than the loop-counter shall not be modified within condition or expression

## Rule MISRA 6-6-2
Definition: The goto statement shall jump to a label declared later in the same function body.

## Rule MISRA 6-6-4
Definition: For any iteration statement there shall be no more than one break or goto statement used for loop termination.

## Rule MISRA 7-5-1
Definition: A function shall not return a reference or a pointer to an automatic variable (including parameters), defined within the function

## Rule MISRA 7-5-2
Definition: The address of an object with automatic storage shall not be assigned to another object that may persist after the first object has ceased to exist

## Rule MISRA 8-4-3
Definition: All exit paths from a function with non-void return type shall have an explicit return statement with an expression

## Rule MISRA 8-5-1
Definition: All variables shall have a defined value before they are used

## Rule MISRA 10-3-3
Definition: A virtual function shall only be overridden by a pure virtual function if it is itself declared as pure virtual

## Rule MISRA 11-0-1
Definition: Member data in non-POD class types shall be private

## Rule MISRA 15-0-2
Definition: An exception object should not have pointer type

## Rule MISRA 16-0-6
Definition: In the definition of a function-like macro, each instance of a parameter shall be enclosed in parentheses, unless it is used as the operand of # or ##

## Rule MISRA 18-0-5
Definition: The unbounded functions of library <cstring> shall not be used
