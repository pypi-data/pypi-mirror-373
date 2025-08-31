"""
**AveyTense Exceptions**

@lifetime >= 0.3.27a1 \\
© 2024-Present Aveyzan // License: MIT \\
https://aveyzan.xyz/aveytense#aveytense.exceptions

Exception classes for AveyTense. Used in any scope modules scattered around the project. \\
Globally accessible since 0.3.44.
"""
class MissingValueError(Exception):
    """
    @lifetime >= 0.3.19
    ```
    # 0.3.26b3 - 0.3.26c3 in module tense.tcs
    # to 0.3.26b3 in module tense.primary
    ```
    Missing value (empty parameter).
    
    Usually not thrown at all, common cause is lacking values in probability methods from class `~.Tense`
    """
    ...
class IncorrectValueError(Exception):
    """
    @lifetime >= 0.3.19
    ```
    # 0.3.26b3 - 0.3.26c3 in module tense.tcs
    # to 0.3.26b3 in module tense.primary
    ```
    Incorrect value of a parameter, having correct type.
    
    Mostly replaced by `TypeError` inbuilt exception.
    """
    ...
class NotInitializedError(Exception):
    """
    @lifetime >= 0.3.25
    ```
    # 0.3.26b3 - 0.3.26c3 in module tense.tcs
    # to 0.3.26b3 in module tense.primary
    ```
    Class was not instantiated
    """
    ...
class InitializedError(Exception):
    """
    @lifetime >= 0.3.26b3
    
    Class was instantiated.
    
    This exception is thrown by definitions with the 'abstract' word in their names in `~.util` submodule.
    """
    ...
class NotReassignableError(Exception):
    """
    @lifetime >= 0.3.26b3
    
    Attempt to re-assign a value
    """
    ...
class NotComparableError(Exception):
    """
    @lifetime >= 0.3.26rc1
    
    Attempt to compare a value with another one.
    """
    ...

class NotIterableError(Exception):
    """
    @lifetime >= 0.3.26rc1
    
    Attempt to iterate a non-iterable object.
    
    This exception is thrown if an object is object of a class extending class `~.types_collection.NotIterable`
    """
    ...

class NotCallableError(Exception):
    """
    @lifetime >= 0.3.45
    
    Attempt to call an object.
    
    This exception is thrown to indicate non-callable objects.
    """
    ...
    
NotInvocableError = NotCallableError # >= 0.3.26rc1
    
class SubclassedError(Exception):
    """
    @lifetime >= 0.3.27rc1
    
    Class has been inherited by the other class.
    
    This exception is thrown by definitions with the 'final' word in their names in `~.util` submodule.
    """
    ...

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error