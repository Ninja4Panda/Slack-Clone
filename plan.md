## Timeline Overview
This plan may change once we know what documentation is required and when the requirements will change.

| Task                                           | Start  | End    |
| ---------------------------------------------- |:------:|:------:|
| Identify changes in iteration and modify code  | 7/10   | 8/10   |
| Implement functions and test them              | 8/10   | 17/10  |
| Reiterate the tests based on new requirements  | 17/10  | 21/10  |   
| Reiterate the functions and test them          | 21/10  | 25/10  |
| Write documentation                            | 25/10  | 27/10  |

## Function Dependencies
Our diagram can be viewed [here](https://i.imgur.com/87wxa1i.png).

## Task Delegation 
We are planning to implement the functions in an order according to the dependencies illustrated in the above diagram. They will be delegated as follows:

| Deki          | Felicia       | Solomon       |Zhou           |
|:------------- |:------------- |:------------- |:------------- |          
| Auth_reg      | Auth_logout   | Auth_pass_rst | Chl_create    |
| Auth_login    | Auth_pass_req | Ad_perm_change| Chl_join      |
|               |               |               |               | 
| Chl_leave     | Chl_rmv_Owner | Chl_listall   | Chl_details   |
| Chl_add_Owner | Chl_list      | Chl_messages  | Msg_send      |
|               |               |               |               | 
| Chl_invite    | Msg_remove    | Msg_react     | Msg_pin       |
| Msg_sendlater | Msg_edit      | Msg_unreact   | Msg_unpin     |
|               |               |               |               | 
| Standup_start | Search        | Usr_setname   | Usr_sethandle |
| Standup_send  | User_profile  | Usr_setemail  | User_photo    |

We have one and a half weeks to write the functions and test it with iteration 1 test functions. Each pair of rows of functions must be done first in order to do any of the ones after it. Therefore, we need to finish the first two rows in the first three days. Next two in two days, the next two in another two days and then the final two in three days. 

## List of Software Tools we will use in Iteration Two
- Draw.io for flowcharts
- Visual Studio Code, gedit
- Token generators and validators
- Facebook Messenger, Trello, Google Drive, Discord
- In built python checkers: Pylint, coverage.py
