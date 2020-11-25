# Basic syntax

## Variables

- Usual variables

    ```txt
    someVariable (str) = "Hello"
    ```

- Read-only variables

    ```txt
    someValue (int const) = 10
    ```

## Loops

- For

    ```txt
    for i in iterator:
        doSomething
    ```

- While

    ```txt
    while condition:
        doSomething
    ```

## If instruction

```txt
if condition:
    doSomething
else condition2:
    doSomething2
else:
    doSomething3
```

## Functions

- Function declaration

    ```txt
    functionName (FunctionReturnType)
    argName1 (Arg1Type),
    argName2 (Arg2Type),
    argName3 (Arg3Type):
        return something
    ```

- Function call

    ```txt
    # call a function providing with arg1 and the second argument is the result of anotherFunctionName function
    functionName arg1, (antherFunctionName argForAnotherFunction)
    ```

## Comments

```txt
# As in python
```

## Classes and objects

- Definition

    ```txt
    class Person:
    # constants
        name (String const)
        age (int const)
        passport (Passport const)

    # variables
        mood (private String) = "OK"

    # constructors
        new (Person) # (Person) can be omitted
        name (String),
        age (int):
            this.name = name
            this.age = age
            this.passport = new name age

    # methods
        changeMood (void)
        newMood (String):
            this.mood = newMood
    ```

- Create instance

    ```txt
    somePerson (Person const) = new "Rob", 12
    ```

## Other examples

```txt
# variable assignment
helloVariable (String const) = helloFunction "MyName"

# helloWorld function
helloWorld (String)
name (String),
age (int):
    print ["Hello", name, ", ", age]

# call ctor
person (Person const) = Male.new "Rob"
```
