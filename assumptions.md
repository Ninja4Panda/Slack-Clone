# General Assumptions
- Values such as tokens, channel_id, u_id, and reset code cannot be negative
- If invalid tokens are passed to any function, it will do nothing.
- For some functions there is currently no way to test that they are working when given valid parameters. As a result, we must test that the function returns the correct errors when it is given invalid parameters and that no errors are thrown when given correct parameters.

# Authentication Assumptions 
## Login 
- An empty string will raise ValueError
- Auth_login can be called several times, and as a result, there will be several valid tokens for the same account. This makes sense when you consider things such as the account being logged in on separate devices. Furthermore, our tests may fail to invalidate the token when it fails a pytest. (Note: this can be corrected by adding a try-finally block if it turns out our assumption is wrong) 
- The user is not already logged in on the same device.

## Logout
- The user is already logged in on the same device.

## Register
- An empty string will raise ValueError
- We will only need to use auth_register once when making test accounts, then we can use the auth_login for as many times as we need. This will avoid trying to register an account that's already registered in the tests, thus allowing us to rerun tests more easily. 
- Multiple users are not registering in with the same email at the same time

## Password Reset Request
- Reset request is ignored for invalid or unregistered emails 

## Password Reset 
- Password is not being reset to the current one

## Admin User Permission Change
- Users can change their own permissions as long as they are an admin

# Channel Assumptions 
## Channel Invite
- Channel_invite does nothing if the invited user is already a member of the channel

## Channel messages
- The messages stored are in reverse chronological order

## Channel leave
- Channel_leave will do nothing if the user is not in the channel

## Channel Join
- Channel_join will do nothing if the user is already in the channel
- The user is not blocked from joining the channel

## Channel Add Owner
- The new owner does not have to already be a member of the channel

## Channel Remove Owner
- An owner of a channel can remove themself as an owner

## Channel List
- Only show existing channels that aren't hidden to the user

## Channels Listall
- Private channels will not appear in channel_listall unless they're an admin or owner or they're already in the channel.
- Members of slack can only view the channel_id and name of public channels or channels that they're already in

## Channels Create
- Multiple channels can have the same name
- An empty string is not a valid channel name
- When creating a channel using channel_create, the owner of the channel is the user who created it and the user is automatically a part of the channel when it is made

## For All
- channel_id's are unique

# Profile Assumptions
## Set Name
- The user inputs only the English alphabet for first and names
- Two users can have the same first and/or last names
- The user does not update to their current name
- There is always an input for name if changing name
- User only uses the English alphabet for names 

## Set Email
- The user does not update to their current email
- There is always an email input

## Set Handle
- If the user did not put a handle and resets their name then the handle updates to the new one.
- Two users can have the same handle
- User only uses the English alphabet for handles 
- There is always a handle input if updating user handle 

## Set Profile Picture
- Invalid x_start for setting profile pictures is negative
- The user updates their profile picture with an internet link and not from their local computer.
- Profile Pictures will be images not gifs. 
- There is a default profile pic if the user has not chosen one yet
- Images are rectangular or square and not (png) so you can crop it properly and compare its dimensions with cropping stats. 
 
# Standup Assumptions
## Start Standup 
- For the standup start function assume there is no other on-going standup going on

## End Standup 
- Any sort of media (such as images, videos are gifs) are not included in the standup
- If standup_send is called, a standup is currently active

# Message Assumptions
## Send Message
- You can't send an empty message
- You can't pass any sort of media (such as images, videos or gifs) as messages

## Edit Message
- Cannot edit a message to be more than 1000 characters

## React and Unreact a Message
- Only valid react_id's are sad reacts(0), heart reacts(1) and thumbs up(2).
- The same user can have two different reacts on the same message

## For all
- Messages can contain special characters such as emojis and Unicode.
- Python and the database can handle these special characters
- message_id's are unique

