"""
This is a file which contains helper functions to determine if values are valid
"""
# pylint: disable=missing-docstring

# \ is needed in regex and can't be removed
# pylint: disable=anomalous-backslash-in-string

# Can't change value error name to anything else in line 19
# pylint: disable=redefined-builtin

# Imports won't work when we try to avoid this error :/
# pylint: disable=cyclic-import

import hashlib
import re
from werkzeug.exceptions import HTTPException

from server.get_info_helper import get_data


class ValueError(HTTPException):
    code = 400
    message = 'No message specified'


class AccessError(HTTPException):
    code = 400
    message = 'No message specified'


def is_member(user_id, channel_id):
    """
    This function returns a boolean indicating whether a user is a member of a channel
    usage: pass in a valid token, a user_id, and a channel_id

    Important: This helper function will only work when the following functions are complete:
    auth_login
    channel_details
    """
    data = get_data()
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            for member in channel["all_members"]:
                if member["u_id"] == user_id:
                    return True

    return False


def is_owner(user_id, channel_id):
    """
    This function returns a boolean indicating whether a user is an owner of a channel
    usage: pass in a valid token, a user_id, and a channel_id

    Important: This helper function will only work when the following functions are complete:
    auth_login
    channel_details
    """
    data = get_data()
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            for owner in channel["owner_members"]:
                if owner["u_id"] == user_id:
                    return True

    return False


def is_valid_token(token):
    """
    A helper function used for TESTING and SERVER FUNCTIONS
    :param token: a string encoded with jwt received from auth_login or auth_register
    :return: boolean of whether the token has or hasn't been tampered with
    """
    data = get_data()

    for user in data["users"]:
        if token in user["valid_tokens"]:
            return True
    return False


def is_valid_channel(channel_id):
    """
    Given a channel_id, returns whether it is a valid channel.
    """
    data = get_data()
    for channel in data["channels"]:
        if channel["channel_id"] == channel_id:
            return True

    return False


def is_invalid_email(email):
    """
    This function returns true if the email is invalid & false if the email is valid
    usage: pass in a email
    Source: https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    """
    # Make a regular expression
    # for validating an Email
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    # pass the regualar expression
    # and the string in search() method
    if re.search(regex, email):
        return False
    return True


def is_valid_password(u_id, password):
    """
    Given a password determine whether it is a valid password for the u_id.
    """
    data = get_data()
    for user in data["users"]:
        for valid_u_id in user["u_id"]:
            if valid_u_id == u_id:
                if user["password"] == password:
                    return True
    return False


def is_valid_uid(u_id):
    """
    Given a u_id, returns whether it is a valid u_id.
    """
    data = get_data()
    for user in data["users"]:
        if user["u_id"] == u_id:
            return True
    return False


def is_invalid_name(name):
    """
    This function returns true if the name is invalid & false if the name is valid
    usage: pass in a name
    :param name: string
    :return: Boolean
    """
    # Check if the name contain all spaces
    if name.isspace():
        return True

    # Check if the name is only english
    if not name.isalpha():
        return True

    # If the name is between 1 and 50 characters
    if 1 <= len(name) <= 50:
        return False
    return True


def is_handle_in_data(handle, data):
    """
    This function loops through the data
    returns true if the handle is in data & false if otherwise
    usage: pass in a handle and data
    :return:
    """
    # find if the handle is inside the data
    for user in data["users"]:
        if user["handle_str"] == handle:
            return True
    return False


def is_invalid_channel_name(name):
    """
    Given a channel name checks it fits the naming criteria.
    This function returns true if the name is invalid & false if the name
    is valid.
    """

    if len(name) > 20 or name == "":
        return True

    return False


# Functions that raise exceptions
def check_token(token):
    if is_valid_token(token) is False:
        raise AccessError("Invalid token")


def check_u_id(u_id):
    if is_valid_uid(u_id) is False:
        raise ValueError("Invalid user")


def check_channel_id(channel_id):
    if is_valid_channel(channel_id) is False:
        raise ValueError("Invalid channel")


def check_react_id(react_id):
    if not 0 <= react_id <= 2:
        raise ValueError("Invalid react")


def check_channel_name(name):
    if is_invalid_channel_name(name) is True:
        raise ValueError("Channel name must be between 1 and 20 english characters")


def check_email(email):
    """
    Given an email determines whether it belongs to a user u_id.
    The function returns true if the email doesn't belong to a user
    and false if it does.
    """
    data = get_data()
    counter = 0
    # Check the email belongs to a user
    for user in data["users"]:
        if user["email"] == email:
            counter = 1
    if counter < 1:
        return True

    return False


def check_password(u_id, password):
    """
    Given a password determines whether it belongs to the correct user u_id.
    The function returns true if the password does not belong to the user and
    false if it does.
    """
    data = get_data()

    counter = 0
    # Check that the password belongs to the correct user
    for user in data["users"]:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user["u_id"] == u_id and user["password"] == hashed_password:
            counter = 1
    if counter < 1:
        return True
    return False
