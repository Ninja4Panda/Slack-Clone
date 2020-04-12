# pylint: disable=missing-docstring

# User profile function takes too many arguments however, all are needed
# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments

# Data should conform to uppercase however, the variable is nested too deep
# pylint: disable=invalid-name

# Importing functions from helper is a long line however, can not be avoided
# pylint: disable=line-too-long

# Line 28, ValueError, we had to redefine it.
# pylint: disable=redefined-builtin

# Line 0, too many comments, however needed for pylint exceptions
# pylint: disable=too-many-lines

# Line 0, too many comments, however needed for pylint exceptions
# pylint: disable=too-many-lines

from datetime import datetime, timedelta
import hashlib
from sys import path
import copy
import urllib.request
import jwt
from PIL import Image

from server.validation_helper import ValueError, AccessError, is_member, is_owner, is_valid_token, is_invalid_email, is_invalid_name, is_handle_in_data, check_token, check_u_id, check_channel_id, check_react_id, check_email, check_password, check_channel_name
from server.get_info_helper import save, get_user_from_id, get_channel_id_from_message, get_info_about_message, get_member, get_user_from_token, get_channel, generate_handle, generate_reset_code, get_is_this_user_reacted, check_future, get_serializable_datetime, check_standup, get_host_from_path, get_u_id

path.append('../')

SECRET = "peppapig"

data = {
    "users": [],
    "channels": [],
    "reset_requests": [],  # Contains reset code and u_id.
    "n_messages": 0,
}

"""
Dictionary for user with the following keys:
"u_id": int,
"name_first": string,
"name_last": string,
"handle_str": string,
"email": string,
"password": string,
"profile_img_url": string
"valid_tokens": list of strings
"permission_id": int


Dictionary for channel:
"channel_id": int,
"name": string
"is_public": bool
"owner_members": List of dictionaries of members
"all_members": List of dictionaries of members
"messages": List of dictionaries for messages
"future_messages": List of dictionaries for messages
"standup_message": type messages dict
"active_standup" : bool


Dictionary for members:
"u_id": int,
"name_first": string,
"name_last": string,
"profile_img_url": string


Dictionary for messages:
"message_id": int,
"u_id": int,
"message": string,
"time_created": datetime,
"reacts": list of dictionary for reacts,
"is_pinned": bool


Dictionary for reacts:
"react_id": int,
"u_ids": list of ints,


Dictionary for reset requests:
"reset_code": string,
"u_id": int,


Dictionary for tokens (but encoded into a string):
"u_id": int
"login_time": datetime # makes sure that the token is different at every login.
"""


def auth_login(email, password):
    # Check for valid email
    if is_invalid_email(email):
        raise ValueError("Invalid email")

    # Check the email belongs to a user
    if check_email(email):
        raise ValueError("Email address does not belong to a user")

    # Retrieve the u_id
    u_id = get_u_id(email)
    # Check that the password matches the email
    if check_password(u_id, password):
        raise ValueError("Incorrect Password")

    # If authentication is successful generate a new token
    token = jwt.encode({"u_id": u_id,
                        "login_time": str(datetime.utcnow())},
                       SECRET, algorithm='HS256').decode("utf-8")

    # Add token into the user's dictionary
    u_info = get_user_from_id(u_id)
    u_info["valid_tokens"].append(token)

    # Return the u_id & token
    save()
    return {"u_id": u_id, "token": token}


def auth_logout(token):
    # Check for invalid tokens
    check_token(token)

    # Invalidate the tokens - by removing the token on the client
    for user in data["users"]:
        for correct_token in user["valid_tokens"]:
            if correct_token == token:
                user["valid_tokens"].remove(correct_token)
                save()
                return {"is_success": True}

    return {"is_success": False}


def auth_register(email, password, name_first, name_last):
    # check for valid email
    if is_invalid_email(email):
        raise ValueError("Invalid email")

    # Invalid password
    if len(password) < 6:
        raise ValueError("Password cannot be less than 6 characters")

    # Invalid first name
    if is_invalid_name(name_first):
        raise ValueError("First name has to be between 1 and 50 english characters")

    # Invalid first name
    if is_invalid_name(name_last):
        raise ValueError("Last name has to be between 1 and 50 english characters")

    # Check if the email is already registered
    for user in data["users"]:
        if user["email"] == email:
            raise ValueError("Email address already registered")

    # Create a token to pass
    token = jwt.encode({"u_id": len(data["users"]), "login_time": str(datetime.utcnow())}, SECRET, algorithm='HS256').decode("utf-8")

    # create a new user
    new_user = {
        "u_id": len(data["users"]),
        "name_first": name_first,
        "name_last": name_last,
        "handle_str": generate_handle(name_first, name_last, data),
        "email": email,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "profile_img_url": "/static/default.jpg",
        "valid_tokens": [token],
        "permission_id": 1 if data["users"] == [] else 3,
    }

    # store the register account into data
    data["users"].append(new_user)

    # return the u_id & token
    save()
    return {"u_id": new_user["u_id"], "token": token}


def auth_passwordreset_request(email):
    """
    generates a reset code and adds it into data
    email is sent by function in server.py
    """

    # need check if the email belongs to a registered user
    for user in data["users"]:
        if user["email"] == email:
            code = generate_reset_code()
            data["reset_requests"].append({"reset_code": code, "u_id": user["u_id"]})
            save()
            return {"code": code}

    # email did not belong to a registered user, return no code
    return {"code": None}


def auth_passwordreset_reset(reset_code, new_password):
    for request in data["reset_requests"]:
        if request["reset_code"] == reset_code:
            # try to change password
            if len(new_password) < 6:
                # password is invalid
                raise ValueError("Password cannot be less than 6 characters")
            user = get_user_from_id(request["u_id"])
            user["password"] = hashlib.sha256(new_password.encode()).hexdigest()
            # now remove the used code so it can't be used again
            data["reset_requests"].remove(request)
            save()
            return {}

    # code is not in data
    raise ValueError("Invalid reset code")


def channel_invite(token, channel_id, u_id):

    # Check validity of inputs
    check_token(token)
    check_channel_id(channel_id)
    check_u_id(u_id)

    # get info about inviter
    inviter = get_user_from_token(token)

    # Raise access error if they aren't a member of the channel they are creating an invite for
    if is_member(inviter["u_id"], channel_id) is False:
        raise AccessError("Cannot invite to a channel you are not in")

    # get user data from u_id
    invitee = get_user_from_id(u_id)

    # get channel
    channel = get_channel(channel_id)

    # create a dict of type member
    invitee_profile = user_profile(token, u_id)
    member_details = {
        "u_id": u_id,
        "name_first": invitee_profile["name_first"],
        "name_last": invitee_profile["name_last"]
    }

    if is_member(u_id, channel_id) is False:
        # Add user to channel
        channel["all_members"].append(member_details)

        # Add user to owner list if they have perms
        if invitee["permission_id"] != 3:
            channel["owner_members"].append(member_details)

    save()
    return {}


def channel_details(token, channel_id):

    # check validity of inputs
    check_token(token)
    check_channel_id(channel_id)

    # get the channel
    channel = get_channel(channel_id)

    # Check if authorised user is a member of the channel
    u_id = get_user_from_token(token)["u_id"]
    if is_member(u_id, channel_id) is False:
        raise AccessError("User is not a member of the channel")

    # create a copy to return with the correct urls
    owner_members_copy = copy.deepcopy(channel["owner_members"])
    all_members_copy = copy.deepcopy(channel["all_members"])
    for member in owner_members_copy:
        member["profile_img_url"] = get_host_from_path(member["profile_img_url"])
    for member in all_members_copy:
        member["profile_img_url"] = get_host_from_path(member["profile_img_url"])

    return {
        "name": channel["name"],
        "owner_members": owner_members_copy,
        "all_members": all_members_copy,
        }


def channel_messages(token, channel_id, start):

    # check validity of inputs
    check_token(token)
    check_channel_id(channel_id)

    # get the data
    user = get_user_from_token(token)
    channel = get_channel(channel_id)

    check_future(channel_id)
    check_standup(channel_id)

    # no negative values allowed
    if start < 0:
        raise ValueError("Index starts from 0 being the latest message")

    # user is not a member of the channel
    if not is_member(user["u_id"], channel["channel_id"]):
        raise AccessError("User is not a member of the channel")

    # if the start is greater than the total number of messages
    if start > len(channel["messages"]):
        raise ValueError("start is greater than the total number of messages")

    # set the end
    end = start + 50

    # change end if end is too large
    if end > len(channel["messages"]):
        end = len(channel["messages"])
        return_dict = {"messages": channel["messages"][start:end], "start": start, "end": -1}
    else:
        return_dict = {"messages": channel["messages"][start:end], "start": start, "end": end}

    return_dict["messages"] = get_is_this_user_reacted(user["u_id"], return_dict["messages"])
    # now need to change datetimes to strings
    for message in return_dict["messages"]:
        message["time_created"] = get_serializable_datetime(message["time_created"])

    # print(return_dict)
    return return_dict


def channel_leave(token, channel_id):
    # Check validity of inputs
    check_token(token)
    check_channel_id(channel_id)

    # create a dict of type member
    member_details = get_member(token)

    # Remove user from a channel
    channel = get_channel(channel_id)
    if member_details in channel["all_members"]:
        channel["all_members"].remove(member_details)
        if member_details in channel["owner_members"]:
            channel["owner_members"].remove(member_details)
    save()
    return {}


def channel_join(token, channel_id):
    # check validity of inputs
    check_token(token)
    check_channel_id(channel_id)

    # get data
    user = get_user_from_token(token)
    channel = get_channel(channel_id)

    # create a dict of type member
    member_details = get_member(token)

    # check if user is authorised to join
    if channel["is_public"] is False and user["permission_id"] == 3:
        raise AccessError("Channel is private")

    # check if user is already in the channel
    if member_details in channel["all_members"]:
        return {}

    # Add user to channel
    channel["all_members"].append(member_details)

    # Add user to owner list if they have perms
    if user["permission_id"] != 3:
        channel["owner_members"].append(member_details)
    save()
    return {}


def channel_addowner(token, channel_id, u_id):

    # Check the validity of the inputs
    check_token(token)
    check_channel_id(channel_id)
    check_u_id(u_id)

    # Check that the user is not an owner of the specified channel
    if is_owner(u_id, channel_id) is True:
        raise ValueError("User is already an owner of the channel")

    # Check that the user is authorised to add the owner
    auth_user = get_user_from_token(token)["u_id"]
    if is_owner(auth_user, channel_id) is False:
        raise AccessError("Authorised user is not an owner of slackr, or an owner of the channel")

    # Get user info
    user = get_user_from_id(u_id)

    # Create a dict of type member
    member_details = {info: user[info] for info in ["u_id", "name_first", "name_last"]}

    # Add user to channel
    get_channel(channel_id)["owner_members"].append(member_details)

    save()
    return {}


def channel_removeowner(token, channel_id, u_id):
    # check validity of inputs
    check_token(token)
    check_channel_id(channel_id)
    check_u_id(u_id)

    # check that the target is an owner of the specified channel
    if is_owner(u_id, channel_id) is False:
        raise ValueError("User is not an owner of the channel")

    # check that the user is authorised to remove the owner
    auth_user = get_user_from_token(token)["u_id"]
    if is_owner(auth_user, channel_id) is False:
        raise AccessError

    # Check that the target is not a owner or admin
    if get_user_from_id(u_id)["permission_id"] != 3:
        raise AccessError("Cannot remove admin/slackr owner from channel owners")

    # since all values are correct, remove the owner of the channel
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            for owner in channel["owner_members"]:
                if owner["u_id"] == u_id:
                    channel["owner_members"].remove(owner)
                    break
    save()
    return {}


def channels_list(token):
    # check that token is valid
    check_token(token)

    channels = []
    u_id = get_user_from_token(token)["u_id"]

    for channel in data["channels"]:
        if is_member(u_id, channel["channel_id"]) is True:
            channels.append({
                "channel_id": channel["channel_id"],
                "name": channel["name"],
                })
    return {
        "channels": channels,
    }


def channels_listall(token):
    # check validity of token
    check_token(token)

    # get the data
    user = get_user_from_token(token)

    # if the user is only a member he/she can only see all channels that is public
    # or he/she is part of
    channels = []
    if user["permission_id"] == 3:
        for channel in data["channels"]:
            if channel["is_public"] or is_member(user["u_id"], channel["channel_id"]):
                # append to the channels
                channels.append({
                    "channel_id": channel["channel_id"],
                    "name": channel["name"],
                })
    else:  # if user is owner/admin
        for channel in data["channels"]:
            channels.append({
                "channel_id": channel["channel_id"],
                "name": channel["name"],
            })
    # return channels
    return {"channels": channels}


def channels_create(token, name, is_public):
    # Validate values
    check_token(token)
    check_channel_name(name)

    # Create a dict of type member
    member_details = get_member(token)

    # Create a new channel
    new_channel = {
        "channel_id": len(data["channels"]) + 1,
        "name": name,
        "is_public": is_public,
        "owner_members": [member_details],
        "all_members": [member_details],
        "messages": [],
        "future_messages": [],
        "standup_message": None,
        "active_standup": False
    }

    data["channels"].append(new_channel)
    save()
    return {"channel_id": new_channel["channel_id"]}


def message_sendlater(token, channel_id, message, time_sent):
    # Check validity of inputs
    check_token(token)
    check_channel_id(channel_id)

    # Check that message is less than 1000 characters
    if len(message) > 1000:
        raise ValueError("Message can't be more than 1000 characters")

    # Check that the time sent is not the past
    time_now = datetime.utcnow()
    if time_sent < time_now:
        raise ValueError("Invalid time set")

    # Get channel
    channel = get_channel(channel_id)

    # Raise an access error if user not in channel
    if get_member(token) not in channel["all_members"]:
        raise AccessError("User is not a member of the channel.")

    # Send a message from authorised_user to a specific channel at a specified time in the future

    # Grab the user data
    user = get_user_from_token(token)

    # Set the message dictionary up
    message = {
        "message_id": data["n_messages"] + 1,
        "u_id": user["u_id"],
        "message": message,
        "time_created": time_sent,
        "reacts": [{"react_id": 0, "u_ids": []},
                   {"react_id": 1, "u_ids": []},
                   {"react_id": 2, "u_ids": []}],
        "is_pinned": False
    }
    # Reserving the unique message id. this message id is not valid until message is sent,
    # but the message id will be usable after it is sent
    data["n_messages"] += 1

    future_messages = channel["future_messages"]
    future_messages.append(message)

    # sort the list by timestamp(Source:
    # https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary)
    future_messages = sorted(future_messages, key=lambda k: k["time_created"])

    # save the sorted list
    channel["future_messages"] = future_messages

    save()
    return {"message_id": message["message_id"]}


def message_send(token, channel_id, message):
    # Check validity of inputs
    check_token(token)
    check_channel_id(channel_id)

    # Check if any future messages or standup messages need to be sent
    check_future(channel_id)
    check_standup(channel_id)

    # Invalid name
    if len(message) > 1000:
        raise ValueError("Message can't be more than 1000 characters")

    # grab the user data from token
    user = get_user_from_token(token)

    # Get channel
    channel = get_channel(channel_id)

    # Check if the user has joined the channel
    if is_member(user["u_id"], channel_id) is False:
        raise AccessError("User is not a member of the channel.")

    message = {
        "message_id": data["n_messages"] + 1,
        "u_id": user["u_id"],
        "message": message,
        "time_created": datetime.utcnow(),
        "reacts": [{"react_id": 0, "u_ids": []},
                   {"react_id": 1, "u_ids": []},
                   {"react_id": 2, "u_ids": []}],
        "is_pinned": False
    }

    channel["messages"].insert(0, message)
    data["n_messages"] += 1
    save()
    return {"message_id": message["message_id"]}


def message_remove(token, message_id):
    # check that token is valid
    check_token(token)

    # get info about user and message
    channel_id = get_channel_id_from_message(message_id)
    message_info = get_info_about_message(message_id)
    u_id = get_user_from_token(token)["u_id"]

    # check that message_id is valid
    if channel_id is None:
        raise ValueError("Invalid message")

    # check that the authorised user is the one who sent the message
    # or is an admin/owner of the channel or slackr
    if message_info["u_id"] != u_id:
        if is_owner(u_id, channel_id) is False or get_user_from_id(u_id)["permission_id"] == 3:
            raise AccessError("User is not authorised to remove this message")

    # since all values are correct, remove the message
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            for message in channel["messages"]:
                if message["message_id"] == message_info["message_id"]:
                    channel["messages"].remove(message)
                    break
    save()
    return {}


def message_edit(token, message_id, message):
    # check that token is valid
    check_token(token)

    # check that message is valid
    if len(message) > 1000:
        raise ValueError("Message can't be more than 1000 characters")

    # get info about user and message
    channel_id = get_channel_id_from_message(message_id)
    message_info = get_info_about_message(message_id)
    u_id = get_user_from_token(token)["u_id"]

    # check that message_id is valid
    if channel_id is None:
        raise ValueError("Invalid message")

    # check that the authorised user is the one who sent the message
    # or is an admin/owner of the channel or slackr
    if message_info["u_id"] != u_id:
        if is_owner(u_id, channel_id) is False or get_user_from_id(u_id)["permission_id"] == 3:
            raise AccessError("User is not authorised to remove this message")

    # check if the message is empty string remove the message
    if message == "":
        message_remove(token, message_id)

    # since all values are correct, edit the message
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            for msg in channel["messages"]:
                if msg["message_id"] == message_info["message_id"]:
                    msg["message"] = message
                    break
    save()
    return {}


def message_react(token, message_id, react_id):
    # check validity of inputs
    check_token(token)
    check_react_id(react_id)

    # get the channel id & check if message is valid
    channel_id = get_channel_id_from_message(message_id)
    if channel_id is None:
        raise ValueError("Invalid message")

    # get the user id & check if the user is in the channel
    u_id = get_user_from_token(token)["u_id"]
    if not is_member(u_id, channel_id):
        raise ValueError("User is not part of the channel")

    # get the msg
    msg = get_info_about_message(message_id)
    for reacts in msg["reacts"]:
        # find the react id
        if reacts["react_id"] == react_id:
            # check if the user did the same reacts already
            for user_id in reacts["u_ids"]:
                if user_id == u_id:
                    raise ValueError("User already reacted to the message with the same react")
            reacts["u_ids"].append(u_id)
            save()
            break
    return {}


def message_unreact(token, message_id, react_id):
    # check validity of inputs
    check_token(token)
    check_react_id(react_id)

    # get the channel id & check if message is valid
    channel_id = get_channel_id_from_message(message_id)
    if channel_id is None:
        raise ValueError("Invalid message")

    # get the user id & check if the user is in the channel
    u_id = get_user_from_token(token)["u_id"]
    if not is_member(u_id, channel_id):
        raise ValueError("User is not part of the channel")

    # get the msg
    msg = get_info_about_message(message_id)
    for reacts in msg["reacts"]:
        # find the react id
        if reacts["react_id"] == react_id:
            # have to do it this way because we redefined ValueError
            if u_id in reacts["u_ids"]:
                reacts["u_ids"].remove(u_id)
                save()
            else:
                raise ValueError("User has not reacted to the message")
    return {}


def message_pin(token, message_id):
    """
    Given a message within a channel, mark it as "pinned" to be given special display treatment
    by the frontend.
    """
    # Check that token is valid
    check_token(token)

    # Check that the message is valid
    channel_id = get_channel_id_from_message(message_id)
    if channel_id is None:
        raise ValueError("Invalid message")

    # Check the user permissions
    user = get_user_from_token(token)
    if user["permission_id"] == 3:
        raise ValueError("User does not have the required permissions")

    # Check if the messages is already pinned
    message = get_info_about_message(message_id)
    if message["is_pinned"]:
        raise ValueError("Message is already pinned")

    # Check if the user is inside the channel
    if is_member(user["u_id"], channel_id) is False:
        raise AccessError("User is not a member of the channel")

    # pin the message
    message["is_pinned"] = True
    save()
    return {}


def message_unpin(token, message_id):
    """
    Given a message within a channel, mark it as "pinned" to be given special display treatment
    by the frontend.
    """
    # Check that token is valid
    check_token(token)

    # Check that the message is valid
    channel_id = get_channel_id_from_message(message_id)
    if channel_id is None:
        raise ValueError("Invalid message")

    # Check the user permissions
    user = get_user_from_token(token)
    if user["permission_id"] == 3:
        raise ValueError("The authorised user is not an admin")

    # Check if the messages is not pinned
    message = get_info_about_message(message_id)
    if message["is_pinned"] is False:
        raise ValueError("Message with ID message_id is already unpinned")

    # Check if the user is inside the channel
    if is_member(user["u_id"], channel_id) is False:
        raise AccessError("User is not a member of the channel")

    # unpin the message
    message["is_pinned"] = False
    save()
    return {}


def user_profile(token, u_id):
    """
    For a valid user, returns information about their email, first name, last name, and handle
    """
    # check validity of inputs
    check_token(token)
    check_u_id(u_id)

    # get user info
    info = get_user_from_id(u_id)
    return {
        "u_id": u_id,
        "email": info["email"],
        "name_first": info["name_first"],
        "name_last": info["name_last"],
        "handle_str": info["handle_str"],
        "profile_img_url": get_host_from_path(info["profile_img_url"])
        }


def user_profile_setname(token, name_first, name_last):
    # check validity of token
    check_token(token)

    # Invalid first name
    if is_invalid_name(name_first):
        raise ValueError("First name has to be between 1 and 50 english characters")

    # Invalid last name
    if is_invalid_name(name_last):
        raise ValueError("Last name has to be between 1 and 50 english characters")

    # get the user based on the token
    user = get_user_from_token(token)

    # update the name
    user["name_first"] = name_first
    user["name_last"] = name_last

    # update name in any channels they are in
    for channel in data["channels"]:
        for member in channel["all_members"]:
            if member["u_id"] == user["u_id"]:
                member["name_first"] = name_first
                member["name_last"] = name_last
                # if they are a member of the channel they might also be an owner
                for owner in channel["owner_members"]:
                    if owner["u_id"] == user["u_id"]:
                        owner["name_first"] = name_first
                        owner["name_last"] = name_last

    save()
    return {}


def user_profile_setemail(token, email):
    # check validity of token
    check_token(token)

    # check for valid email
    if is_invalid_email(email):
        raise ValueError("Invalid email")

    # check if the email is being used
    for user in data["users"]:
        if user["email"] == email:
            raise ValueError("Email address is being used")

    # get the user based on the token
    user = get_user_from_token(token)

    # update the email
    user["email"] = email
    save()
    return {}


def user_profile_sethandle(token, handle_str):
    """
    Update the authorised user's handle (i.e. display name)
    """
    # Check that token is valid
    check_token(token)

    # Check for valid length
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise ValueError("Handle must be between 3 and 20 characters")

    # Check if handle has been used
    if is_handle_in_data(handle_str, data):
        raise ValueError("Handle is already used by another user")

    # Update handle
    user = get_user_from_token(token)
    user["handle_str"] = handle_str
    save()
    return {}


def user_profiles_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):

    # Check that token is valid
    if is_valid_token(token) is False:
        raise AccessError("Invalid token")

    # Check that the img_url does not return a HTTP status other than 200.
    try:
        # Note: will not work if website blocks urllib.request
        local_filename, headers = urllib.request.urlretrieve(img_url)
    except urllib.error.HTTPError:
        raise ValueError("img_url returns a HTTP status other than 200.")

    # Get the file type and check if it is a jpg
    if headers["Content-Type"] not in ["image/jpeg", "image/jpg"]:
        raise ValueError("Image uploaded is not a JPG")

    # Check the dimensions and raise an error if they are out of bounds
    image = Image.open(local_filename)
    width, height = image.size
    if x_start < 0 or y_start < 0 or x_start > width or y_start > height:
        raise ValueError("Index not within the dimensions of the image")
    if x_end > width or y_end > width or x_end < x_start or y_end < y_start:
        raise ValueError("Index not within the dimensions of the image")

    # Crop image using .crop() with the respective dimensions
    cropped = image.crop((x_start, y_start, x_end, y_end))

    # save image to the static folder
    random = generate_reset_code()
    cropped.save("static/" + random + ".jpg")

    # create a link to the image and add photo to users database. this will be something like "/static/yourimagefilename.jpg"
    get_user_from_token(token)["profile_img_url"] = "/static/" + random + ".jpg"

    # Update photo in the member dicts
    user = get_user_from_token(token)
    for channel in data["channels"]:
        for member in channel["all_members"]:
            if member["u_id"] == user["u_id"]:
                member["profile_img_url"] = "/static/" + random + ".jpg"
                # if they are a member of the channel they might also be an owner
                for owner in channel["owner_members"]:
                    if owner["u_id"] == user["u_id"]:
                        owner["profile_img_url"] = "/static/" + random + ".jpg"

    return {}


def users_all(token):
    # Check that token is valid
    check_token(token)

    users = []
    for user in data["users"]:
        new = {
            "u_id": user["u_id"],
            "email": user["email"],
            "name_first": user["name_first"],
            "name_last": user["name_last"],
            "handle_str": user["handle_str"],
            "profile_img_url": get_host_from_path(user["profile_img_url"])
        }
        users.append(new)

    return {"users": users}


def standup_start(token, channel_id, length):

    # Check validity of inputs
    check_token(token)
    check_channel_id(channel_id)

    # Get the user id from token
    u_id = get_user_from_token(token)["u_id"]

    # Access error if user is not in the channel
    if is_member(u_id, channel_id) is False:
        raise AccessError("Member not in channel")

    # Check if a standup is already running
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id and channel["active_standup"]:
            raise ValueError("Standup is already running")

    # Turn on standup
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id and (channel["active_standup"] is False):
            channel["active_standup"] = True

    # create temp standup message dictionary
    standup_message = {}

    # Find standup time and standup finish
    # Due to changes in iteration 3, the standup interval will be a given
    # variable input in seconds called 'length'

    time_finish = datetime.utcnow() + timedelta(seconds=length)

    # create temp standup message dictionary
    standup_message = {
        "message_id": data["n_messages"] + 1,
        "u_id": u_id,
        "message": "",
        "time_created": time_finish,
        "reacts": [{"react_id": 0, "u_ids": []},
                   {"react_id": 1, "u_ids": []},
                   {"react_id": 2, "u_ids": []}],
        "is_pinned": False
    }

    # reserve the message_id
    data["n_messages"] += 1

    # add the standup message to the channel
    get_channel(channel_id)["standup_message"] = standup_message

    save()
    return {
        "time_finish": get_serializable_datetime(time_finish)}


def standup_active(token, channel_id):
    # Check validity of inputs
    check_token(token)
    check_channel_id(channel_id)

    channel = get_channel(channel_id)

    if channel["active_standup"]:
        time_finish = get_serializable_datetime(channel["standup_message"]["time_created"])
        return {"is_active": True, "time_finish": time_finish}

    return {"is_active": False, "time_finish": None}


def standup_send(token, channel_id, message):

    # Check validity of inputs
    check_token(token)
    check_channel_id(channel_id)

    # Check the message is less than 1000 characters
    if len(message) > 1000:
        raise ValueError("Message can't be more than 1000 characters")

    # get the channel from channel_id
    channel = get_channel(channel_id)

    # Access error if user is not in the channel
    if get_member(token) not in get_channel(channel_id)["all_members"]:
        raise AccessError("User is not part of the channel")

    # Check if a standup is already running
    if channel["active_standup"] is False:
        raise ValueError("Standup is not running")

    # get the handle from token
    user = get_user_from_token(token)
    handle = user["handle_str"]

    # add handle to message
    string = handle + ": " + message.strip() + "\n"

    # add string to the standup message
    channel["standup_message"]["message"] += string

    save()
    return {}


def search(token, query_str):

    # update messages
    for channel in data["channels"]:
        channel_id = channel["channel_id"]
        check_future(channel_id)
        check_standup(channel_id)

    # check that token is valid
    check_token(token)

    results = []

    channels = channels_list(token)["channels"]
    for channel in channels:
        for message in get_channel(channel["channel_id"])["messages"]:
            if query_str.lower() in message["message"].lower():
                results.append(message)
    u_id = get_user_from_token(token)["u_id"]

    # need to add is_this_user_reacted
    results = get_is_this_user_reacted(u_id, results)

    # now need to change datetimes to strings
    for message in results:
        message["time_created"] = get_serializable_datetime(message["time_created"])

    return {"messages": results}


def admin_userpermission_change(token, u_id, permission_id):

    # check if the token is valid
    check_token(token)

    # check if the permission id is valid
    if not 1 <= permission_id <= 3:
        raise ValueError("Invalid permission_id")

    # get the admin based on the token
    admin = get_user_from_token(token)

    # check if user is admin/owner
    if admin["permission_id"] == 3:
        raise AccessError("User is not admin or owner")

    # this function raise ValueError if the u_id is invalid
    user = get_user_from_id(u_id)

    # update the permission
    user["permission_id"] = permission_id
    save()
    return {}
