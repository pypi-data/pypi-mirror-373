# MISRA-C++:2008 Coding Guidelines

### Rule 0-1-1 
**Description**: A Project shall not contain unreachable code 
**Exception**: None

### Rule 0-1-2 
**Description**: A Project shall not contain infeasible paths 
**Exception**: None

### Rule 0-1-3 
**Description**: A Project shall not contain unused variables 
**Exception**: None

### Rule 0-1-4 
**Description**: A project shall not conatin non-volatile POD variables having only one use. 
**Exception**: None

### Rule 0-1-5 
**Description**: A project shall not contain unused type declarations. 
**Exception**: None

### Rule 0-1-6 
**Description**: A project shall not contain instances of non-volatile variables being given values that are never subsequently used 
**Exception**: None

### Rule 0-1-7 
**Description**: The value returned by a function having a non-void return type that is not an overloaded operator shall always be used 
**Exception**: None

### Rule 0-1-8 
**Description**: All functions with void return type shall have external side effect(s) 
**Exception**: None

### Rule 0-1-9 
**Description**: There shall be no dead code 
**Exception**: None

### Rule 0-1-10 
**Description**: Every defined function shall be called at least once 
**Exception**: None

### Rule 0-1-11 
**Description**: There shall be no unused parameters (named or unnamed) in non-virtual functions 
**Exception**: None

### Rule 0-1-12 
**Description**: There shall be no unused parameters (named or unnamed) in the set of parameters for a virtual function and all the functions that override it 
**Exception**: None

### Rule 0-2-1 
**Description**: An object shall not be assigned to an overlapping object 
**Exception**: None

### Rule 0-3-1 
**Description**: "Minimization of run-time failures shall be ensured by the use of at least one of :
(a) static analysis tool/techniques
(b) dynamic analysis tools/techniques
(c) explicit coding of checks to handle run-time faults." 
**Exception**: None

### Rule 0-3-2 
**Description**: If a function generates error information, then that error information shall be tested 
**Exception**: None

### Rule 0-4-1 
**Description**: Use of scaled-integer or fixed-point arithmetic shall be documented 
**Exception**: None

### Rule 0-4-2 
**Description**: Use of floating-point arithmetic shall be documented 
**Exception**: None

### Rule 0-4-3 
**Description**: Floating-point implementations shall comply with a defined floating-point standard 
**Exception**: None

### Rule 1-0-1 
**Description**: All code shall confrom to ISO/IEC 14882:2003 "The C++ Standard Incorporating Technical Corrigendum 1" 
**Exception**: None

### Rule 1-0-2 
**Description**: Multiple compilers shall be only be used if they have a common, defined interface 
**Exception**: None

### Rule 1-0-3 
**Description**: The Implementation of integer division in the chosen compiler shall be determined and documented 
**Exception**: None

### Rule 2-2-1 
**Description**: The character set and the corresponding encoding shall be documented 
**Exception**: None

### Rule 2-3-1 
**Description**: Trigraphs shall not be used 
**Exception**: None

### Rule 2-5-1 
**Description**: Digraphs should not be used 
**Exception**: None

### Rule 2-7-1 
**Description**: The character sequence /* shall not be used within a C-style comment 
**Exception**: None

### Rule 2-7-2 
**Description**: Sections of code shall not be "commented out" using C-style comments 
**Exception**: None

### Rule 2-7-3 
**Description**: Sections of code should not be "commented out" using C++ comments 
**Exception**: None

### Rule 2-10-1 
**Description**: Different identifiers shall be typographically unambiguous 
**Exception**: None

### Rule 2-10-2 
**Description**: Identifiers decalared in an inner scope shall not hide an identifier declared in an outer scope 
**Exception**: None

### Rule 2-10-3 
**Description**: A typedef name (including qualification, if any) shall be a unique identifier 
**Exception**: None

### Rule 2-10-4 
**Description**: A class, union or enum name (including qualification, if any) shall be a unique identifier 
**Exception**: None

### Rule 2-10-5 
**Description**: The identifier name of a non-member object or function with static storage duration should not be reused. 
**Exception**: None

### Rule 2-10-6 
**Description**: If an identifier refers to a type, it shall not also refer to an object or a function in the same scope 
**Exception**: None

### Rule 2-13-1 
**Description**: Only those escape sequence that are defined in ISO/IEC 14882:2003 shall be used 
**Exception**: None

### Rule 2-13-2 
**Description**: Octal constants (other than zero) and octal escape sequences (other than "\0") shall not be used 
**Exception**: None

### Rule 2-13-3 
**Description**: A "u" suffix shall be applied to all octal or hexadecimal integer literals of unsigned type 
**Exception**: None

### Rule 2-13-4 
**Description**: Literal suffixes shall be upper case 
**Exception**: None

### Rule 2-13-5 
**Description**: Narrow and wide string literals shall not be concatenated. 
**Exception**: None

### Rule 3-1-1 
**Description**: It shall be possible to include any header file in multiple translation units without violating the One Definition Rule 
**Exception**: None

### Rule 3-1-2 
**Description**: Functions shall not be declared at block scope 
**Exception**: None

### Rule 3-1-3 
**Description**: When an array is decalared its size shall either be stated explicitly or defined implicitly by initialization 
**Exception**: None

### Rule 3-2-1 
**Description**: All declaration of an object or functions shall have compatible types 
**Exception**: None

### Rule 3-2-2 
**Description**: The One Definition Rule shall not be violated 
**Exception**: None

### Rule 3-2-3 
**Description**: A type, object or function that is used in multiple translation units shall be declared in one and only one file 
**Exception**: None

### Rule 3-2-4 
**Description**: An identifier with external linkage shall have exactly one definition 
**Exception**: None

### Rule 3-3-1 
**Description**: Objects or functions with external linkage shall be declared in a header file 
**Exception**: None

### Rule 3-3-2 
**Description**: If a function has internal linkage then all redeclarations shall include the static storage class specifier 
**Exception**: None

### Rule 3-4-1 
**Description**: An identifier declared to be an object or type shall be defined in a block that minimizes its visibility 
**Exception**: None

### Rule 3-9-1 
**Description**: The types used for an object, a function return type, or a function parameter shall be token-for-token identical in all declarations and re-declarations 
**Exception**: None

### Rule 3-9-2 
**Description**: typedefs that indicate size and signedness should be used in place of the basic numerical types 
**Exception**: None

### Rule 3-9-3 
**Description**: The underlying bit representations of floating-point values shall not be used. 
**Exception**: None

### Rule 4-5-1 
**Description**: Expressions with type bool shall not be used as operands to built-in operators other than the assignment operator=, the logical operators &&, ||, !, the equality operators == and !=, the unary & operstor, and the conditional operator. 
**Exception**: None

### Rule 4-5-2 
**Description**: Expressions with type enum shall not be used as operands to built-in operators other than the subscript operator [ ], the assignment operator =, the equality operators == and !=, the unary & operator, and the relational operators <, <=, >, >= 
**Exception**: None

### Rule 4-5-3 
**Description**: Expressions with type (plain) char and wchar, shall not be used as operands to built-in operators other than the assignment operator =, the equality operators == and !=, and the unary & operator. 
**Exception**: None

### Rule 4-10-1 
**Description**: NULL shall not be used as an integer value. 
**Exception**: None

### Rule 4-10-2 
**Description**: Literal zero (0) shall not be used as the null-pointer-constant. 
**Exception**: None

### Rule 5-0-1 
**Description**: The value of an expression shall be the same under any order of evaluation that the standard permits 
**Exception**: None

### Rule 5-0-2 
**Description**: Limited dependence should be placed on C++ operator precedence rules in expressions 
**Exception**: None

### Rule 5-0-3 
**Description**: A cvalue expression shall not be implicitly convertd to a different underlying type 
**Exception**: None

### Rule 5-0-4 
**Description**: An implicit integral conversion shall not change the signedness of the underlying type 
**Exception**: None

### Rule 5-0-5 
**Description**: There shall be no implicit floating-integral conversions 
**Exception**: None

### Rule 5-0-6 
**Description**: An implicit integral or floating-point conversion shall not reduce the size of the underlying type 
**Exception**: None

### Rule 5-0-7 
**Description**: There shall be no explicit floating-integral conversions of a cvalue expression 
**Exception**: None

### Rule 5-0-8 
**Description**: An explicit integral or floating-point conversion shall not increase the size of the underlying type of a cvalue expression 
**Exception**: None

### Rule 5-0-9 
**Description**: An explicit integral conversion shall not change the signedness of the underlying type of a cvalue expression 
**Exception**: None

### Rule 5-0-10 
**Description**: If the bitwise operators ~ and << are applied to and operand with and underlying type of unsigned char or unsigned short, the result shall be immediately cast to the underlying type of the operand 
**Exception**: None

### Rule 5-0-11 
**Description**: The plain char type shall only be used for the storage and use of character values 
**Exception**: None

### Rule 5-0-12 
**Description**: signed char and unsigned char type shall only be used for the storage and use of numeric values 
**Exception**: None

### Rule 5-0-13 
**Description**: The condition of an if-statement and the condition of an iteration-statement shall have type bool 
**Exception**: None

### Rule 5-0-14 
**Description**: The first operand of a conditional-operator shall have type bool 
**Exception**: None

### Rule 5-0-15 
**Description**: Array indexing shall be the only form of pointer arithmetic 
**Exception**: None

### Rule 5-0-16 
**Description**: A pointer operand and any pointer resulting from pointer arithmetic using that operand shall both address elements of the same array 
**Exception**: None

### Rule 5-0-17 
**Description**: Subtraction between pointers shall only be applied to pointers that address elements of the same array 
**Exception**: None

### Rule 5-0-18 
**Description**: >, >=, <, <= shall not be applied to objects of pointer type, except where they point to the same array 
**Exception**: None

### Rule 5-0-19 
**Description**: The declaration of objects shall contain no more than two levels of pointer indirection 
**Exception**: None

### Rule 5-0-20 
**Description**: Non-constant operands to a binary bitwise operator shall have the same underlying type 
**Exception**: None

### Rule 5-0-21 
**Description**: Bitwise operators shall only be applied to operands of unsigned underlying type 
**Exception**: None

### Rule 5-2-1 
**Description**: Each operand of a logical && or || shall be a postfix-expression 
**Exception**: None

### Rule 5-2-2 
**Description**: A pointer to a virtual base class shall only be cast to a pointer to a derived class by means of dynamic_cast 
**Exception**: None

### Rule 5-2-3 
**Description**: Casts from a base class to a derived class should not be performed on polymorphic types 
**Exception**: None

### Rule 5-2-4 
**Description**: C-style casts (other than void casts) and functional notation casts (other than explicit constructor calls) shall not be used 
**Exception**: None

### Rule 5-2-5 
**Description**: A cast shall not remove any const or volatile qualification from the type of a pointer or reference 
**Exception**: None

### Rule 5-2-6 
**Description**: A cast shall not convert a pointer to a function to any other pointer type, including a pointer to function type 
**Exception**: None

### Rule 5-2-7 
**Description**: An object with pointer type shall not be converted to an unrelated pointer type, either directly or indirectly 
**Exception**: None

### Rule 5-2-8 
**Description**: An object with integer type or pointer to void type shall not be converted to and object with pointer type 
**Exception**: None

### Rule 5-2-9 
**Description**: A cast should not convert a pointer type to an integral type 
**Exception**: None

### Rule 5-2-10 
**Description**: The increment (++) and decrement (--) operators should not be mixed with other operators in and expression 
**Exception**: None

### Rule 5-2-11 
**Description**: The comma operator, && operator and the || operator shall not be overloaded 
**Exception**: None

### Rule 5-2-12 
**Description**: An identifier with array type passed as a function argument shall not decay to a pointer 
**Exception**: None

### Rule 5-3-1 
**Description**: Each operand of the ! Operator, the logical && or the logical || operator shall have the type bool 
**Exception**: None

### Rule 5-3-2 
**Description**: The unary minus operator shall not be applied to an expression whose underlying type is unsigned 
**Exception**: None

### Rule 5-3-3 
**Description**: The unary & operator shall not be overloaded 
**Exception**: None

### Rule 5-3-4 
**Description**: Evaluation of the operand to the sizeof operator shall not contain side effects 
**Exception**: None

### Rule 5-8-1 
**Description**: The right hand operand of a shift operator shall lie between zero and one less than the width in bits of the underlying type of the left hand operand 
**Exception**: None

### Rule 5-14-1 
**Description**: The right hand operand of a logical && or || operator shall not contain side effects 
**Exception**: None

### Rule 5-17-1 
**Description**: The semantic equivalence between a binary operator and its assignment operator form shall be preserved 
**Exception**: None

### Rule 5-18-1 
**Description**: The comma operator shall not be used 
**Exception**: None

### Rule 5-19-1 
**Description**: Evaluation of constant unsigned integer expression should not lead to wrap-around 
**Exception**: None

### Rule 6-2-1 
**Description**: Assignment operators shall not be used in sub-expressions 
**Exception**: None

### Rule 6-2-2 
**Description**: Floating-point expressions shall not be directly or indirectly tested for equality or inequality 
**Exception**: None

### Rule 6-2-3 
**Description**: Before preprocessing, a null statement shall only occur on a line by itself; it may be followed by a comment, provided that the first character following the null statement is a white-space character 
**Exception**: None

### Rule 6-3-1 
**Description**: The statement forming the body of a switch, while, do â€¦ while or for statement shall be a compound statement 
**Exception**: None

### Rule 6-4-1 
**Description**: An if ( condition ) construct shall be followed by a compound statement. The else keyword shall be followed by either a compound statement, or another if statement
**Exception**: None

### Rule 6-4-2 
**Description**: All if ... else if constructs shall be terminated with an else clause. 
**Exception**: None

### Rule 6-4-3 
**Description**: A switch statement shall be a well-formed switch statement 
**Exception**: None

### Rule 6-4-4 
**Description**: A switch-label shall only be used when the most closely enclosing compound statement is the body of a switch statement 
**Exception**: None

### Rule 6-4-5 
**Description**: An unconditional throw or break statement shall terminate every non-empty switch-clause 
**Exception**: None

### Rule 6-4-6 
**Description**: The final clause of a switch statement shall be the default-clause 
**Exception**: None

### Rule 6-4-7 
**Description**: The condition of a switch statement shall not have bool type 
**Exception**: None

### Rule 6-4-8 
**Description**: Every switch statement shall have at least one case-clause 
**Exception**: None

### Rule 6-5-1 
**Description**: A for loop shall contain a single loop-counter which shall not have floating type. 
**Exception**: None

### Rule 6-5-2 
**Description**: If loop-counter is not modified by -- or ++ then, within condition, the loop-counter shall only be used as an operand to <=, <, > or >= 
**Exception**: None

### Rule 6-5-3 
**Description**: The loop-counter shall not be modified within condition or statement 
**Exception**: None

### Rule 6-5-4 
**Description**: The loop-counter shall be modified by one of : --, ++, -=n, or +=n; where n remains constant for the duration of the loop 
**Exception**: None

### Rule 6-5-5 
**Description**: A loop-control-variable other than the loop-counter shall not be modified within condition or expression 
**Exception**: None

### Rule 6-5-6 
**Description**: A loop-control-variable other than the loop-counter which is modified in statement shall have type bool 
**Exception**: None

### Rule 6-6-1 
**Description**: Any label referenced by a goto statement shall be declared in the same block, or in a block enclosing the goto statement 
**Exception**: None

### Rule 6-6-2 
**Description**: The goto statement shall jump to a label declared later in the same function body. 
**Exception**: None

### Rule 6-6-3 
**Description**: The continue statement shall only be used within a well-formed for loop 
**Exception**: None

### Rule 6-6-4 
**Description**: For any iteration statement there shall be no more than one break or goto statement used for loop termination. 
**Exception**: None

### Rule 6-6-5 
**Description**: A function shall have a single point of exit at the end of the function 
**Exception**: None

### Rule 7-1-1 
**Description**: A variable which is not modified shall be const qualified 
**Exception**: None

### Rule 7-1-2 
**Description**: A pointer or reference parameter in a function shall be declared as pointer to const or reference to const if the corresponding object is not modified 
**Exception**: None

### Rule 7-2-1 
**Description**: An expression with enum underlying type shall only have values corresponding to the enumerators of the enumeration 
**Exception**: None

### Rule 7-3-1 
**Description**: The global namespace shall only contain main, namespace declarations and extern "C" declarations. 
**Exception**: None

### Rule 7-3-2 
**Description**: The identifier main shall not be used for a function other than the global function main. 
**Exception**: None

### Rule 7-3-3 
**Description**: There shall be no unnamed namespaces in header files 
**Exception**: None

### Rule 7-3-4 
**Description**: unsing-directives shall not be used 
**Exception**: None

### Rule 7-3-5 
**Description**: Multiple declarations for an identifier in the same namespace shall not straddle a using-declaration for that identifier 
**Exception**: None

### Rule 7-3-6 
**Description**: using-directives and using-declarations (excluding class scope or function scode using-declaration) shall not be used in header files 
**Exception**: None

### Rule 7-4-1 
**Description**: All usage of assembler shall be documented 
**Exception**: None

### Rule 7-4-2 
**Description**: Assembler instructions shall only be introduced using the asm declaration 
**Exception**: None

### Rule 7-4-3 
**Description**: Assembly language shall be encapsulated and isolated 
**Exception**: None

### Rule 7-5-1 
**Description**: A function shall not return a reference or a pointer to an automatic variable (including parameters), defined within the function 
**Exception**: None

### Rule 7-5-2 
**Description**: The address of an object with automatic storage shall not be assigned to another object that may persist after the first object has ceased to exist 
**Exception**: None

### Rule 7-5-3 
**Description**: A function shall not return a reference or a pointer to a parameter that is passed by reference or const reference 
**Exception**: None

### Rule 7-5-4 
**Description**: Functions should not call themselves, either directly or indirectly 
**Exception**: None

### Rule 8-0-1 
**Description**: An init-declarator-list or a member-declarator-list shall consist of a single init-declarator or member-declarator respectively 
**Exception**: None

### Rule 8-3-1 
**Description**: Parameters in an overriding virtual function shall either use the same default arguments as the function they override, or else shall not specify any default arguments 
**Exception**: None

### Rule 8-4-1 
**Description**: Functions shall not be defined using the ellipsis notation 
**Exception**: None

### Rule 8-4-2 
**Description**: The identifiers used for the parameters in a redeclaration of a function shall be identical to those in the declaration 
**Exception**: None

### Rule 8-4-3 
**Description**: All exit paths from a function with non-void return type shall have an explicit return statement with an expression 
**Exception**: None

### Rule 8-4-4 
**Description**: A function identifier shall either be used to call the function or it shall be protected by & 
**Exception**: None

### Rule 8-5-1 
**Description**: All variables shall have a defined value before they are used 
**Exception**: None

### Rule 8-5-2 
**Description**: Braces shall be used to indicate and match the structure in the non-zero initialization of arrays and structures 
**Exception**: None

### Rule 8-5-3 
**Description**: In an enumerator list, the = construct shall not be used to explicity initialize members other than the first, unless all items are explicitly initialized 
**Exception**: None

### Rule 9-3-1 
**Description**: const member functions shall not return non-const pointers or references to class-data 
**Exception**: None

### Rule 9-3-2 
**Description**: Member functions shall not return non-const handles to class-data 
**Exception**: None

### Rule 9-3-3 
**Description**: If a member functions can be made static then it shall be made static, otherwise if it can be made const then it shall be made const 
**Exception**: None

### Rule 9-5-1 
**Description**: Unions shall not be used 
**Exception**: None

### Rule 9-6-1 
**Description**: When the absolute positioning of bits representing a bit-field is required, then the behavior and packing of bit-fields shall be documented 
**Exception**: None

### Rule 9-6-2 
**Description**: Bit-fields shall be either bool type or an explicitly unsigned or signed integral type 
**Exception**: None

### Rule 9-6-3 
**Description**: Bit-fields shall not have enum type 
**Exception**: None

### Rule 9-6-4 
**Description**: Named bit-fields with signed integer type shall have a length of more than one bit. 
**Exception**: None

### Rule 10-1-1 
**Description**: Classes should not be derived from virtual bases 
**Exception**: None

### Rule 10-1-2 
**Description**: A base class shall only be declared virtual if it is used in a diamond hierachy 
**Exception**: None

### Rule 10-1-3 
**Description**: An accessible base class shall not be both virtual and non-virtual in the same hierachy 
**Exception**: None

### Rule 10-2-1 
**Description**: All accessible entity names within a multiple inheritance hierachy should be unique 
**Exception**: None

### Rule 10-3-1 
**Description**: There shall be no more than one definition of each virtual function on each path thorugh the inheritance hierachy 
**Exception**: None

### Rule 10-3-2 
**Description**: Each overriding virtual function shall be declared with the virtual keyword 
**Exception**: None

### Rule 10-3-3 
**Description**: A virtual function shall only be overridden by a pure virtual function if it is itself declared as pure virtual 
**Exception**: None

### Rule 11-0-1 
**Description**: Member data in non-POD class types shall be private 
**Exception**: None

### Rule 12-1-1 
**Description**: An object's dynamic type shall not be used from the body of its constructor or destructor 
**Exception**: None

### Rule 12-1-2 
**Description**: All constructors of a class should explicitly call a constructor for all of its immediate base classes and all virtual base classes 
**Exception**: None

### Rule 12-1-3 
**Description**: All constructors that are callable with a single argument of funcamental type shall be declared explicit 
**Exception**: None

### Rule 12-8-1 
**Description**: A copy constructor shall only initialize its base classes and the non-static members of the class of which it is a member 
**Exception**: None

### Rule 12-8-2 
**Description**: The copy assignment operator shall be declared protected or private in an abstract class 
**Exception**: None

### Rule 14-5-1 
**Description**: A non-member generic function shall only be declared in a namespace that is not an associated namespace 
**Exception**: None

### Rule 14-5-2 
**Description**: A copy constructor shall be declared when there is a template constructor with a single parameter that is a generic parameter 
**Exception**: None

### Rule 14-5-3 
**Description**: A copy assignment operator shall be declared when there is a template assignment operator with a parameter that is a generic parameter 
**Exception**: None

### Rule 14-6-1 
**Description**: In a class template with a dependent base, any name that may be found in that dependent base shall be referred to using a qualified-id or this-> 
**Exception**: None

### Rule 14-6-2 
**Description**: The function chosen by overload resolution shall resolve to a function declared previously in the translation unit 
**Exception**: None

### Rule 14-7-1 
**Description**: All class templates, function templates, class template member functions and class template static members shall be instantiated at least once 
**Exception**: None

### Rule 14-7-2 
**Description**: For any given template specialization, an explicit instantiation of the template with the template-arguments used in the specialization shall not render the program ill-formed 
**Exception**: None

### Rule 14-7-3 
**Description**: All partial and explicit specializations for a template shall be declared in the same file as the declaration of their primary template 
**Exception**: None

### Rule 14-8-1 
**Description**: Overloaded function templates shall not be explicitly specialized 
**Exception**: None

### Rule 14-8-2 
**Description**: The viable function set for a function call should either contain no function specializations, or only contain function specializations 
**Exception**: None

### Rule 15-0-1 
**Description**: Exceptions shall only be used for error handling 
**Exception**: None

### Rule 15-0-2 
**Description**: An exception object should not have pointer type 
**Exception**: None

### Rule 15-0-3 
**Description**: Control shall not be transferred into a try or catch block using a goto or a switch statement 
**Exception**: None

### Rule 15-1-1 
**Description**: The assignment-expression of a throw statement shall not itself cause an exception to be thrown 
**Exception**: None

### Rule 15-1-2 
**Description**: NULL shall not be thrown explicitly 
**Exception**: None

### Rule 15-1-3 
**Description**: An empty throw (throw;) shall only be used in the component-statement of a catch handler 
**Exception**: None

### Rule 15-3-1 
**Description**: Exceptions shall be raised only after start-up and before termination of the program 
**Exception**: None

### Rule 15-3-2 
**Description**: There should be at least one exception handler to catch all otherwise unhandled exceptions 
**Exception**: None

### Rule 15-3-3 
**Description**: Handlers of a function-try-block implementation of a class constructor or destructor shall not reference non-static members from this class or its bases 
**Exception**: None

### Rule 15-3-4 
**Description**: Each exception explicitly thrown in the code shall have a handler of a compatible type in all call path that could lead to that point 
**Exception**: None

### Rule 15-3-5 
**Description**: A class type excpetion shall always be caught by reference 
**Exception**: None

### Rule 15-3-6 
**Description**: Where multiple handlers are provided in a single try-catch statement or function-try-block for a derived class and some or all of its bases, the handlers shall be ordered most-derived to base class 
**Exception**: None

### Rule 15-3-7 
**Description**: Where multiple handlers are provided in a single try-catch statement or function-try-block, any ellipsis (catch-all)handler shall occur last 
**Exception**: None

### Rule 15-4-1 
**Description**: If a function is declared with an exception-specification, then all declarations of the same function (in order translation units) shall be declared with the same set of type-ids 
**Exception**: None

### Rule 15-5-1 
**Description**: A class destructor shall not exit with an exception 
**Exception**: None

### Rule 15-5-2 
**Description**: Where a function's declarations includes an exception-specification, the function shall only be capable of throwing exceptions of the indicated type(s) 
**Exception**: None

### Rule 15-5-3 
**Description**: The terminate( ) function shall not be called implicitly 
**Exception**: None

### Rule 16-0-1 
**Description**: #include directives in a file shall only be preceded by other preprocessor directives or comments 
**Exception**: None

### Rule 16-0-2 
**Description**: Macros shall only be #define'd or #undef'd in the global namespace 
**Exception**: None

### Rule 16-0-3 
**Description**: #undef shall not be used 
**Exception**: None

### Rule 16-0-4 
**Description**: Function-like macros shall not be defined 
**Exception**: None

### Rule 16-0-5 
**Description**: Arguments to a function-like macro shall not contain tokens that look like preprocessing directives 
**Exception**: None

### Rule 16-0-6 
**Description**: In the definition of a function-like macro, each instance of a parameter shall be enclosed in parentheses, unless it is used as the operand of # or ## 
**Exception**: None

### Rule 16-0-7 
**Description**: Undefined macro identifiers shall not be used in #if or #elif preprocessor directives, except as operands to the defined operator 
**Exception**: None

### Rule 16-0-8 
**Description**: If the # token appears as the first token on a line, then it shall be immediately followed by a preprocessing token 
**Exception**: None

### Rule 16-1-1 
**Description**: The defined preprocessor operator shall only be used in one of the two standard forms 
**Exception**: None

### Rule 16-1-2 
**Description**: All #else, #elif and #endif preprocessor directives shall reside in the same file as the #if or #ifdef directive to which they are related 
**Exception**: None

### Rule 16-2-1 
**Description**: The pre-processor shall only be used for file inclusion and include guards 
**Exception**: None

### Rule 16-2-2 
**Description**: C++ macros shall only be used for include guards, type qualifiers, or storage class specifiers 
**Exception**: None

### Rule 16-2-3 
**Description**: Include guards shall be provided 
**Exception**: None

### Rule 16-2-4 
**Description**: The ', ", /* or // characters shall not occur in a header file name 
**Exception**: None

### Rule 16-2-5 
**Description**: The \ character should not occur in a header file name 
**Exception**: None

### Rule 16-2-6 
**Description**: The #include directive shall be followed by either a <filename> or "filename" sequence 
**Exception**: None

### Rule 16-3-1 
**Description**: There shall be at most one occurrence of the # or ## operators in a single macro definition 
**Exception**: None

### Rule 16-3-2 
**Description**: The # and ## operators should not be used 
**Exception**: None

### Rule 16-6-1 
**Description**: All uses of the #pragma directive shall be documented 
**Exception**: None

### Rule 17-0-1 
**Description**: Reserved identifiers, macros and functions in the standard library shall not be defined, redefined or undefined 
**Exception**: None

### Rule 17-0-2 
**Description**: The names of standard library macros and objects shall not be reused 
**Exception**: None

### Rule 17-0-3 
**Description**: The names of standard library functions shall not be overridden 
**Exception**: None

### Rule 17-0-4 
**Description**: All library code shall conform to MISRA C++ 
**Exception**: None

### Rule 17-0-5 
**Description**: The setjmp macro and the longjmp function shall not be used 
**Exception**: None

### Rule 18-0-1 
**Description**: The C library shall not be used 
**Exception**: None

### Rule 18-0-2 
**Description**: The library functions atof, atoi and atol from library <cstdlib> shall not be used 
**Exception**: None

### Rule 18-0-3 
**Description**: The library functions abort, exit, getenv and system from library <cstdlib> shall not be used 
**Exception**: None

### Rule 18-0-4 
**Description**: The time handling functions of library <ctime> shall not be used 
**Exception**: None

### Rule 18-0-5 
**Description**: The unbounded functions of library <cstring> shall not be used 
**Exception**: None

### Rule 18-2-1 
**Description**: The macro offsetof shall not be used 
**Exception**: None

### Rule 18-4-1 
**Description**: Dynamic heap memory allocation shall not be used 
**Exception**: None

### Rule 18-7-1 
**Description**: The signal handling facilities of <csignal> shall not be used 
**Exception**: None

### Rule 19-3-1 
**Description**: The error indicator errno shall not be used 
**Exception**: None

### Rule 27-0-1 
**Description**: The stream input/output library <cstdio> shall not be used 
**Exception**: None
