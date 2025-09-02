### CERT-C++ Coding Standards 

### CON50-CPP 
**Description**: Do not destroy a mutex while it is locked 
**Exception**: None

### CON51-CPP 
**Description**: Ensure actively held locks are released on exceptional conditions 
**Exception**: None

### CON52-CPP 
**Description**: Prevent data races when accessing bit-fields from multiple threads 
**Exception**: None

### CON53-CPP 
**Description**: Avoid deadlock by locking in a predefined order 
**Exception**: None

### CON54-CPP 
**Description**: Wrap functions that can spuriously wake up in a loop 
**Exception**: None

### CON55-CPP 
**Description**: Preserve thread safety and liveness when using condition variables 
**Exception**: None

### CON56-CPP 
**Description**: Do not speculatively lock a non-recursive mutex that is already owned by the calling thread 
**Exception**: None

### CTR50-CPP 
**Description**: Guarantee that container indices and iterators are within the valid range 
**Exception**: None

### CTR51-CPP 
**Description**: Use valid references, pointers, and iterators to reference elements of a container 
**Exception**: None

### CTR52-CPP 
**Description**: Guarantee that library functions do not overflow 
**Exception**: None

### CTR53-CPP 
**Description**: Use valid iterator ranges 
**Exception**: None

### CTR54-CPP 
**Description**: Do not subtract iterators that do not refer to the same container 
**Exception**: None

### CTR55-CPP 
**Description**: Do not use an additive operator on an iterator if the result would overflow 
**Exception**: None

### CTR56-CPP 
**Description**: Do not use pointer arithmetic on polymorphic objects 
**Exception**: None

### CTR57-CPP 
**Description**: Provide a valid ordering predicate 
**Exception**: None

### CTR58-CPP 
**Description**: Predicate function objects should not be mutable 
**Exception**: None

### DCL50-CPP 
**Description**: Do not define a C-style variadic function 
**Exception**: None

### DCL51-CPP 
**Description**: Do not declare or define a reserved identifier 
**Exception**: None

### DCL52-CPP 
**Description**: Never qualify a reference type with const or volatile 
**Exception**: None

### DCL53-CPP 
**Description**: Do not write syntactically ambiguous declarations 
**Exception**: None

### DCL54-CPP 
**Description**: Overload allocation and deallocation functions as a pair in the same scope 
**Exception**: None

### DCL55-CPP 
**Description**: Avoid information leakage when passing a class object across a trust boundary 
**Exception**: None

### DCL56-CPP 
**Description**: Avoid cycles during initialization of static objects 
**Exception**: None

### DCL57-CPP 
**Description**: Do not let exceptions escape from destructors or deallocation functions 
**Exception**: None

### DCL58-CPP 
**Description**: Do not modify the standard namespaces 
**Exception**: None

### DCL59-CPP 
**Description**: Do not define an unnamed namespace in a header file 
**Exception**: None

### DCL60-CPP 
**Description**: Obey the one-definition rule 
**Exception**: None

### ERR50-CPP 
**Description**: Do not abruptly terminate the program 
**Exception**: None

### ERR51-CPP 
**Description**: Handle all exceptions 
**Exception**: None

### ERR52-CPP 
**Description**: Do not use setjmp() or longjmp() 
**Exception**: None

### ERR53-CPP 
**Description**: Do not reference base classes or class data members in a constructor or destructor function-try-block handler 
**Exception**: None

### ERR54-CPP 
**Description**: Catch handlers should order their parameter types from most derived to least derived 
**Exception**: None

### ERR55-CPP 
**Description**: Honor exception specifications 
**Exception**: None

### ERR56-CPP 
**Description**: Guarantee exception safety 
**Exception**: None

### ERR57-CPP 
**Description**: Do not leak resources when handling exceptions 
**Exception**: None

### ERR58-CPP 
**Description**: Handle all exceptions thrown before main() begins executing 
**Exception**: None

### ERR59-CPP 
**Description**: Do not throw an exception across execution boundaries 
**Exception**: None

### ERR60-CPP 
**Description**: Exception objects must be nothrow copy constructible 
**Exception**: None

### ERR61-CPP 
**Description**: Catch exceptions by lvalue reference 
**Exception**: None

### ERR62-CPP 
**Description**: Detect errors when converting a string to a number 
**Exception**: None

### EXP50-CPP 
**Description**: Do not depend on the order of evaluation for side effects 
**Exception**: None

### EXP51-CPP 
**Description**: Do not delete an array through a pointer of the incorrect type 
**Exception**: None

### EXP52-CPP 
**Description**: Do not rely on side effects in unevaluated operands 
**Exception**: None

### EXP53-CPP 
**Description**: Do not read uninitialized memory 
**Exception**: None

### EXP54-CPP 
**Description**: Do not access an object outside of its lifetime 
**Exception**: None

### EXP55-CPP 
**Description**: Do not access a cv-qualified object through a cv-unqualified type 
**Exception**: None

### EXP56-CPP 
**Description**: Do not call a function with a mismatched language linkage 
**Exception**: None

### EXP57-CPP 
**Description**: Do not cast or delete pointers to incomplete classes 
**Exception**: None

### EXP58-CPP 
**Description**: Pass an object of the correct type to va_start 
**Exception**: None

### EXP59-CPP 
**Description**: Use offsetof() on valid types and members 
**Exception**: None

### EXP60-CPP 
**Description**: Do not pass a nonstandard-layout type object across execution boundaries 
**Exception**: None

### EXP61-CPP 
**Description**: A lambda object must not outlive any of its reference captured objects 
**Exception**: None

### EXP62-CPP 
**Description**: Do not access the bits of an object representation that are not part of the object's value representation 
**Exception**: None

### EXP63-CPP 
**Description**: Do not rely on the value of a moved-from object 
**Exception**: None

### FIO50-CPP 
**Description**: Do not alternately input and output from a file stream without an intervening positioning call 
**Exception**: None

### FIO51-CPP 
**Description**: Close files when they are no longer needed 
**Exception**: None

### INT50-CPP 
**Description**: Do not cast to an out-of-range enumeration value 
**Exception**: None

### MEM50-CPP 
**Description**: Do not access freed memory 
**Exception**: None

### MEM51-CPP 
**Description**: Properly deallocate dynamically allocated resources 
**Exception**: None

### MEM52-CPP 
**Description**: Detect and handle memory allocation errors 
**Exception**: None

### MEM53-CPP 
**Description**: Explicitly construct and destruct objects when manually managing object lifetime 
**Exception**: None

### MEM54-CPP 
**Description**: Provide placement new with properly aligned pointers to sufficient storage capacity 
**Exception**: None

### MEM55-CPP 
**Description**: Honor replacement dynamic storage management requirements 
**Exception**: None

### MEM56-CPP 
**Description**: Do not store an already-owned pointer value in an unrelated smart pointer 
**Exception**: None

### MEM57-CPP 
**Description**: Avoid using default operator new for over-aligned types 
**Exception**: None

### MSC50-CPP 
**Description**: Do not use std::rand() for generating pseudorandom numbers 
**Exception**: None

### MSC51-CPP 
**Description**: Ensure your random number generator is properly seeded 
**Exception**: None

### MSC52-CPP 
**Description**: Value-returning functions must return a value from all exit paths 
**Exception**: None

### MSC53-CPP 
**Description**: Do not return from a function declared [[noreturn]] 
**Exception**: None

### MSC54-CPP 
**Description**: A signal handler must be a plain old function 
**Exception**: None

### OOP50-CPP 
**Description**: Do not invoke virtual functions from constructors or destructors 
**Exception**: None

### OOP51-CPP 
**Description**: Do not slice derived objects 
**Exception**: None

### OOP52-CPP 
**Description**: Do not delete a polymorphic object without a virtual destructor 
**Exception**: None

### OOP53-CPP 
**Description**: Write constructor member initializers in the canonical order 
**Exception**: None

### OOP54-CPP 
**Description**: Gracefully handle self-copy assignment 
**Exception**: None

### OOP55-CPP 
**Description**: Do not use pointer-to-member operators to access None
xistent members 
**Exception**: None

### OOP56-CPP 
**Description**: Honor replacement handler requirements 
**Exception**: None

### OOP57-CPP 
**Description**: Prefer special member functions and overloaded operators to C Standard Library functions 
**Exception**: None

### OOP58-CPP 
**Description**: Copy operations must not mutate the source object 
**Exception**: None

### STR50-CPP 
**Description**: Guarantee that storage for strings has sufficient space for character data and the null terminator 
**Exception**: None

### STR51-CPP 
**Description**: Do not attempt to create a std::string from a null pointer 
**Exception**: None

### STR52-CPP 
**Description**: Use valid references, pointers, and iterators to reference elements of a basic_string 
**Exception**: None

### STR53-CPP 
**Description**: Range check element access 
**Exception**: None