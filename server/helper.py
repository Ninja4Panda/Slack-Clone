"""
This is a file which contains helper functions to assist with writing tests and server functions
"""
# pylint: disable=missing-docstring
from datetime import datetime
from datetime import timedelta
import server.stub as stub
# import jwt


def token_admin():
    """
    A helper function used for TESTING only
    :return: token for an administrative account (use this first with multiple users)
    """
    return stub.auth_register("admin@email.com", "adminPassword", "Daddy", "Pig")


def token_account_1():
    """
    A helper function used for TESTING only
    :return: token for a normal account
    """
    return stub.auth_register("test1@email.com", "12345Password", "Mommy", "Pig")


def token_account_2():
    """
    A helper function used for TESTING only
    :return: token for a second normal account
    """
    return stub.auth_register("test2@email.com", "12345Password", "Peppa", "Pig")


# Creating channels for tests
def channelid_public(token):
    """
    A helper function used for TESTING only
    :return: channel_id for a public channel
    """
    return stub.channels_create(token, "Public Channel", True)["channel_id"]


def channelid_private(token):
    """
    A helper function used for TESTING only
    :return: channel_id for a private channel
    """
    return stub.channels_create(token, "Private Channel", False)["channel_id"]


def get_valid_channel(token):
    """
    This function returns a valid channel_id for the provided token. The token would be
    guaranteed to be in that channel.
    usage: pass in a valid token

    Notes: It will try and find a valid channel to join, else it will create one and return that.
    This is to prevent creating more unnecessesary channels

    This makes sure the channel_id is valid for the user.
    """
    # token = token_account_1()

    # No channels exist
    if stub.channels_listall(token)["channels"] == []:

        # Create a new channel
        channel_id = stub.channels_create(token, "test_channel", True)["channel_id"]

    # There is at least 1 channel so we will join the first one we find
    else:
        channel_id = stub.channels_listall(token)["channels"][0]["channel_id"]
        stub.channel_join(token, channel_id)

    return channel_id


def in_one_second():
    """
    in_one_seconds returns the time it would be in 1 minute in datetime format.
    Source:
    https://stackoverflow.com/questions/4541629/how-to-create-a-datetime-equal-to-15-minutes-ago
    actually it's in_one_second now
    """
    return datetime.now() + timedelta(seconds=1)


def get_valid_message(token, channel_id):
    """
    This function returns a valid message_id sent from the provided token.
    It is expected that the user is a part of the channel it is posting messages to.
    usage: pass in a valid token, and the channel in which you want to send your message

    Notes: It will try and find a valid channel to join, else it will create one and return that.
    This is to prevent creating more unnecessesary channels

    This makes sure the channel_id is valid for the user.
    """
    # send a message
    message = "This message was produced by the get_valid_message function."
    stub.message_send(token, channel_id, message)

    # Get a list of messages in the channel
    start = 0
    messages = stub.channel_messages(token, channel_id, start)["messages"]

    # Grab the most recent message
    # We assume our message is the first one.
    # assert messages[0]["message"] == message
    message_id = messages[0]["message_id"]

    return message_id


def reset_data():
    stub.data = {
        "users": [],
        "channels": [],
        "reset_requests": [],  # Contains reset code and u_id.
        "valid_token": [],
        "n_messages": 0,
        "n_channels": 0,
    }
