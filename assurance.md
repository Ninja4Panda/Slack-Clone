# Verification and Validation
Two important aspects of software quality management are verification and validation. Verification is the process of determining whether the software is being developed in a correct way while validation is the process of determining whether the right software is being produced. They ensure the software is secure and prevents unexpected or abnormal data from crashing the software and prevents being spammed with garbage outputs.

## Verification
Verification of our implementation has been done using the pytests written in iteration 1 - we passed all the tests we wrote (except for tests for upload photo, which is for iteration 3). We also performed extensive testing using REST clients such as postman and ARC and using the frontend provided to us. We did this by doing individual testing of the backend and communicating to the team any bugs we found, and possible solutions to fix them. 

## Validation
Validation of our system has been done by ensuring that we meet the acceptance criteria below. Furthermore, we have used pylint and pycoverage on our code to make sure that it is up to standard and that the tests we produced using pytest properly test our code. We received a 9/10 in pylint and 85% in the coverage test. The reason that we did not receive 100% was due to how the tests were engineered. One example is our pytests did not test with an invalid token as our code only tested the function, resulting in slightly less coverage.
Another reason is that we did not test some functions such as password reset requests (since this has to be done using the flask server) or upload photo (since this is part of iteration 3). Overall, we have made sure to check that the majority of our code is up to standard and functioning as intended.

## Acceptance criteria
The following acceptance criteria are based on our user stories, and the specific acceptance criteria are under their respective user stories. We have used these in order to make sure our functions for the backend are fit for purpose and satisfy the requirements that were provided to us.

As a first-time user of Slackr, I want to be able to register a new account so that I can start using the app.
- Provide fields to enter an email, password, first name, and last name
- Show error if the email is not a valid email or is already in use
- Show error if password, first name, or last name is not valid

As a returning user, I want to be able to log in to my account so that I can see any updates and exchange information.
- Require a correct email and password to log in
- Show an error if email or password is incorrect

As a privacy-oriented user, I want to be able to log out to prevent other people from accessing information from my account.
- Show some indication that the user has successfully logged out
- Return to the login page after logging out

As a forgetful user, I want to be able to reset my password if I forget it so that I can log in again.
- Have simple instructions on how to reset provided at the login page
- Provide a field to enter an email to reset, and send an email with a secure code
- Show a message that says the password has been reset

As a new user, I want to be able to see a list of channels so that I can join channels that I find interesting or useful.
- Display names of all channels the user can join
- Distinguish between channels the user is in and those they can join
- Admins and owners of Slackr should be shown both public and private channels

As a channel owner, I want to be able to create channels for relevant topics so that we can talk about different topics in an organised way.
- Provide a field to enter a channel name
- Provide option to make channel private
- The user is made the owner of the channel once it is created
- The channel will initially have no messages or users, apart from the creator

As someone who works in a team, I want to be able to invite people to channels so that we can start a discussion.
- Invited user should be immediately added to the channel
- An easy way to invite a user
- Notify the invited user

As a user, I want to be able to join a channel so that I am able to send and receive messages which are relevant to the channel.
- Show the channel user has joined
- An easy way to join a channel
- See messages in the channel
- A text box to let users write messages
- A send button to send messages

As a user, I want to be able to leave channels so that I can stop seeing irrelevant channels.
- An easy way to leave the channel
- A message that says user left the channel

As a user, I want to be able to view all messages so that I can catch up on previous discussion.
- Show all messages sent in that channel in chronological order
- Allow users to scroll up and down through past channel messages

As a member of a channel I want to see the other members of the channel so I know who will see my messages.
- Users who are owners should be distinguished from normal members 

As a member of a channel I want to know the details of a channel so I know what to post about in that channel.
- Display channel name
- Display members of the channel and owners of the channel

As a user, I want to be able to send messages immediately so I can communicate with others in real-time.
- Only members of a channel can post messages in it
- Special characters can be used within the message
- The message will be sent immediately by default
- The message will specify who sent the message
- Initially, it will have no reacts and will not be pinned

As a lecturer, I want to be able to send a message at a specified time in the future so that I can set reminders for my students.
- A time field that lets users set the time and date in the future for the message to be sent
- An indication that the message is waiting to be sent
- A timer to show how long before the message is sent

As a person who makes lots of mistakes, I want to be able to edit and remove my messages so that I don’t embarrass myself.
- Clear/easy method for editing a message
- Clear/easy method for removing a message
- Ability to edit or remove other people’s messages if the user is an admin/owner

As a lecturer, I want to be able to pin messages so that I can make sure my students can see important notifications.
- The message should be displayed prominently within the channel
- The user must be an admin or owner of Slackr/the channel and be a member of the channel to pin a message
- A message cannot be pinned twice. Doing so will give an error

As a lecturer, I want to be able to unpin messages so that my students don’t see notifications that are no longer important.
- The unpinned message will no longer be given special display treatment in the channel
- The user must be an admin or owner of Slackr/the channel and be a member of the channel to unpin a message
- A message that is not pinned cannot be unpinned. Doing so will give an error

As an emotional user, I want to be able to react to express my feelings towards a particular comment or message.
- Different reacts available
- Show the number and type of reacts for each message and an option to see who reacted
- A user can react in multiple ways to the same message

As a clumsy user, I want to be able to un-react to a message so that no one can notice my clumsiness.
- Be able to remove the react instantly and easily
- Users can only remove reacts that they made

As a user, I want to be able to view other users’ profiles so that I know who they are.
- Display their first name, last name, handle, and email clearly
- Be able to view the profile of any user easily

As a user, I want to be able to modify my profile picture and contact information so that I can personalise my profile.
- Ability to provide a photo from a URL
- Ability to crop the photo as desired

As a user, I want to be able to search past messages so that I can find all messages relevant to a topic.
- Search all channels the user is in
- Should match messages ignoring upper and lower case
- Display messages matching the search in chronological order

As a channel admin, I want to be able to modify the user’s privilege so that I can give permission for certain functionality.
- Options to make a user an owner, admin, or regular user
- Notify the user of the change

As a user, I want to be able to start a standup so that I can record the group discussion automatically.
- All messages sent during the standup should be summarised at the end
- Display some indicator that the standup is taking place
