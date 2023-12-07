# Programming assignment 

For this study, you will complete the programming assignment described here.

This will involve completing the list.c file, which is an implementation of a _linked list_.
This linked list represents a shopping list, where each item in the list has an `item_name`, `price`, and `quantity`.

## Overview

You will be completing the functions in `list.c` only.

You may use any online or class resources available to you (e.g. Google, Stackoverflow, etc.). 
You must use the Visual Studio Code Insiders Build with the extensions provided. 
You must not use any other extensions or plugins, including GitHub Copilot or other programming autocomplete tools.

Note that it is not a hard requirement to complete all functionality, but _all of your code is useful_ - do complete as much as you can, and _even if it does not fully work_ please submit non-functional or incomplete code. Further, you do not need to complete this assignment in 'one go', although you can if you would like to. 

## Instructions

Complete the functions in `list.c` to the best of your ability. You do not need to alter any other files.

Here is a recommended guide:
1. Start by implementing the `list_add_item_at_pos()` function. Then, so that you may test it, implement `list_item_to_string()` and `list_print()` functions.
2. Once those three functions are working reliably, we recommend you write the remaining functions in the following order:
 a. `list_update_item_at_pos()`
 b. `list_remove_item_at_pos()`
 c. `list_swap_item_positions()`
 d. `list_find_highest_price_item_position()`
 e. `list_cost_sum()`
3. The next functions are a little more complex, and we recommend that you complete the above functions before proceeding. Once you are satisfied, we recommend tackling the functions in this order:
 a. `list_save()`
 b. `list_load()`
 c. `list_deduplicate()`

For saving and loading file format, the comments in `list.c` provide detailed instructions and we provide an example `example_load_file.txt`.

For printing, the comments provide the detailed format, and we also present this example:
```
Choice: p
1: 2 * apple @ $0.80 ea
2: 3 * banana @ $0.50 ea
3: 1 * cheese @ $10.49 ea
OK.
```


## To compile your code

Open a terminal from vscode. In the `Terminal` menu item, choose `New Terminal`
This will get you to your program's currenct directory
Type: `make`
This will build your program.
Fix compile errors as appropiate

## To test your code 

Open a terminal in vscode. Type: `make`
Then type: `./runtests`
This will tell you which of your tests pass and which don't. If a test is failing, you will see the line where it's failing, which looks like: 
```
[==========] tests: Running 12 test(s).
[ RUN      ] test_list_init
[       OK ] test_list_init
[ RUN      ] test_list_item_to_string
[  ERROR   ] --- 0x1 != 0
[   LINE   ] --- runtests.c:58: error: Failure!
[  FAILED  ] test_list_item_to_string
[ RUN      ] test_list_print
[  ERROR   ] --- 0x1 != 0
[   LINE   ] --- runtests.c:69: error: Failure!
```

Once all your tests pass, you will see an output as follows:

```
[==========] tests: Running 12 test(s).
[ RUN      ] test_list_init
[       OK ] test_list_init
[ RUN      ] test_list_item_to_string
[       OK ] test_list_item_to_string
[ RUN      ] test_list_print
[       OK ] test_list_print
[ RUN      ] test_list_add_item_at_pos
[       OK ] test_list_add_item_at_pos
[ RUN      ] test_list_update_item_at_pos
[       OK ] test_list_update_item_at_pos
[ RUN      ] test_list_remove_item_at_pos
[       OK ] test_list_remove_item_at_pos
[ RUN      ] test_list_swap_item_positions
[       OK ] test_list_swap_item_positions
[ RUN      ] test_list_find_highest_price_item_position
[       OK ] test_list_find_highest_price_item_position
[ RUN      ] test_list_cost_sum
[       OK ] test_list_cost_sum
[ RUN      ] test_list_save
[       OK ] test_list_save
[ RUN      ] test_list_load
[       OK ] test_list_load
[ RUN      ] test_list_deduplicate
[       OK ] test_list_deduplicate
[==========] tests: 12 test(s) run.
[  PASSED  ] 12 test(s).
```

