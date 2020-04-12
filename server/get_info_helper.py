"""
This is a file which contains helper functions to get info
"""
# pylint: disable=missing-docstring

# line 186 said to use isinstance instead of type
# pylint: disable=unidiomatic-typecheck

# line 210 don't know what else to raise
# pylint: disable=bare-except

from datetime import datetime, timezone
import random
import pickle
from flask import request

import server.stub as stub
import server.validation_helper as validation_helper


def get_data():
    return stub.data


def save():
    with open("database.p", "wb") as file_pointer:
        pickle.dump(stub.data, file_pointer, protocol=pickle.HIGHEST_PROTOCOL)


def get_user_from_id(u_id):
    """
    Given a u_id, returns the user's user info.
    If user cannot be found, raises a ValueError.
    """
    data = get_data()
    for user in data["users"]:
        if user["u_id"] == u_id:
            return user

    raise validation_helper.ValueError("Invalid user")


def get_channel_id_from_message(message_id):
    """
    Given a message_id, returns the channel containing that message and
    returns its channel_id. If message is not found, returns None.
    """
    data = get_data()
    for channel in data["channels"]:
        for message in channel["messages"]:
            if message["message_id"] == message_id:
                return channel["channel_id"]

    return None


def get_info_about_message(message_id):
    """
    Given a message_id, returns the whole dictionary about that message.
    If message is not found, returns None.
    """
    data = get_data()
    for channel in data["channels"]:
        for message in channel["messages"]:
            if message["message_id"] == message_id:
                return message

    return None


def get_member(token):
    """
    Given a token, returns the dictionary of type member given by the token
    :param token: encoded string
    :return: dictionary of type member
    """
    user = get_user_from_token(token)
    return {info: user[info] for info in ["u_id", "name_first", "name_last", "profile_img_url"]}


def get_user_from_token(token):
    """
    Given a token, returns the dictionary of type user given by the token
    :param token: encoded string
    :return: dictionary of type user
    """
    data = get_data()
    for user in data["users"]:
        if token in user["valid_tokens"]:
            return user

    raise validation_helper.AccessError("Invalid token")


def get_channel(channel_id):
    """
    Given a channel, returns a pointer to dictionary of type channel
    :param channel_id: int
    :return: dict of type channel
    """
    data = get_data()
    for channel in data["channels"]:
        if channel_id == channel["channel_id"]:
            return channel

    raise validation_helper.ValueError("Invalid channel")


def generate_handle(name_first, name_last, data):
    """
    This funciton returns a valid the handle name
    usage: pass in first name, last name and the data
    """
    # change it to lower case
    lower_first = name_first.lower()
    lower_last = name_last.lower()
    # concat the two names & make it within 20 characters long
    concat_string = lower_first+lower_last
    concat_string = concat_string[0:20]

    # search through the dictionary to check if handle is taken
    while validation_helper.is_handle_in_data(concat_string, data):
        # make a random string as a handle name
        # source: https://pynative.com/python-generate-random-string/
        letters = "abcdefghijklmnopqrstuvwxyz"
        concat_string = ''.join(random.choice(letters) for i in range(len(concat_string)))
    # return the valid handle name
    return concat_string


def generate_reset_code():
    """
    This function generates a random reset code
    """
    data = get_data()
    code = ""
    letters = "abcdefghijklmnopqrstuvwxyz"
    active_codes = []
    for requests in data["reset_requests"]:
        active_codes.append(requests["reset_code"])

    i = 0
    while i < 3:
        code = code + random.choice(letters)
        code = code + str(random.randint(0, 9))
        i += 1

    # keep adding more stuff until it is unique
    while code in active_codes:
        code = code + random.choice(letters)
        code = code + str(random.randint(0, 9))

    return code


def get_is_this_user_reacted(u_id, messages):
    """
    Function to add is_this_user_reacted key to every react
    """
    for message in messages:
        for react in message["reacts"]:
            if u_id in react["u_ids"]:
                react["is_this_user_reacted"] = True
            else:
                react["is_this_user_reacted"] = False

    return messages


def check_future(channel_id):

    channel = get_channel(channel_id)
    if channel["future_messages"] != []:
        # first message in future messages which is sorted by timestamps
        current_message = channel["future_messages"][0]
        while current_message["time_created"] <= datetime.utcnow():
            channel["messages"].insert(0, current_message)
            channel["future_messages"].remove(current_message)
            if channel["future_messages"] != []:
                current_message = channel["future_messages"][0]
            else:
                break
    save()


def get_serializable_datetime(time):
    if type(time) is datetime:
        return time.replace(tzinfo=timezone.utc).timestamp()
    return time


def check_standup(channel_id):
    channel = get_channel(channel_id)

    # Situation 1: no active standup. In this case, do nothing.
    if channel["active_standup"] is False:
        return

    # Situation 2: active standup but not yet finished
    if channel["standup_message"]["time_created"] > datetime.utcnow():
        return

    # Situation 3: active standup that has just finished recently
    channel["active_standup"] = False
    channel["messages"].insert(0, channel["standup_message"])
    channel["standup_message"] = None


def get_host_from_path(pathname):
    try:
        # flask server
        host = str(request.host)
        return "http://" + host + pathname
    except:
        # pytest so server won't be up
        return pathname


def get_u_id(email):
    data = get_data()
    for user in data["users"]:
        if user["email"] == email:
            u_id = user["u_id"]

    return u_id
