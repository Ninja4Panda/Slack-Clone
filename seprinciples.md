# Refactoring

### Date: 08/11/2019
Description: changed error messages for exceptions so they are the same for the
same error

Reason: more uniform and consistent error messages


### Date: 09/11/2019 - 17/11/2019
Description: changed some functions so they used helpers where possible instead
of doing the same thing within the function, e.g. checking if a user is a 
member of a channel. Note: this overrides the previous change

Reason: less repetition, more readable code, more consistency


### Date: 10/11/2019
Description: got rid of wildcard imports and unnecessary imports

Reason: more specific and clearer purpose for each import


### Date: 10/11/2019
Description: got rid of unnecessary "data = get_data()", which returns "global database"

Reason: we initially thought it was necessary to declare global database in each function
that used/accessed the data, but have now realised this was unnecessary


### Date: 11/11/2019
Description: made some helpers that test values and raise exceptions for values that have to
be tested in multiple different functions

Reason: less repetition and easier to read functions, ensures that error messages are uniform


### Date: 15/11/2019
Description: Updated auth_register so that there was no more if else statement and made it more concise.

Reason: Refactoring the long if else statement reduced the number of lines to make it more readable as multiple things 
were assigned which were duplicated in the if and the else statements. Also made it easier to read and understand.

### Date: 15/11/2019
Description: Made the variable names uniform such as changing all user_id, userId, userid to u_id. 

Reason: This ensures the code is uniform and similar performining variables have similar names to increase simplicity and readibility.

### Date: 15/11/2019
Description: Moved all the repeating exceptions in stub.py to validation_helper.py

Reason: This ensures the main file (stub.py) is readible as repetitive valueerror/accesserror exceptions are raised in another file and only a function is called.

### Date: 16/11/2019
Description: Changed the code according to pylint

Reason: Pylint is useful for checking code style and readibility, therefore, we tried to change our code according to the pylint warnings and ignored ones which were not avoidable.

### Date: 17/11/2019
Description: Changed helper function names to match the helper file name it came from such as added get in a fuction thats from the get_info_helper.py file. 

Reason: This is to ensure when the functions are called in files, it can easily be located in which file it is imported from. 