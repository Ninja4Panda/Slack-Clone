# Tests for all interface functions

# pylint: disable=missing-docstring

# line 1 Too many comments but they are needed to explain pylint ignores
# pylint: disable=too-many-lines

# Some functions return a dictionary and it can't be shortened.
# pylint: disable=line-too-long

# line 878 the dictionaries are indented so they are easily readiable
# pylint: disable=bad-continuation

# line 994 Unused variable however, the new user is needed to check list changes
# pylint: disable=unused-variable

from datetime import datetime, timedelta
from random import random
import time
import pytest

import server.stub as stub
import server.helper as helper
import server.validation_helper as validation_helper
import server.get_info_helper as get_info_helper


def test_auth_login():
    helper.reset_data()
    # Create users for testing
    user1 = stub.auth_register("test123@email.com", "123456", "first", "user")
    user1_token = user1["token"]
    user1_id = user1["u_id"]

    # Invalid email
    with pytest.raises(validation_helper.ValueError):
        stub.auth_login("hi", "123456")

    # Email doesn't belong to a user
    with pytest.raises(validation_helper.ValueError):
        stub.auth_login("hi@email.com", "123456")

    # Invalid password
    with pytest.raises(validation_helper.ValueError):
        stub.auth_login("test123@email.com", "hi")

    # Empty string
    with pytest.raises(validation_helper.ValueError):
        stub.auth_login("", "")

    # Successfully login
    stub.auth_logout(user1_token)
    assert stub.auth_login("test123@email.com", "123456")["u_id"] == user1_id


def test_auth_logout():
    helper.reset_data()
    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.auth_logout("fake token")

    # Create user for testing
    user = stub.auth_register("test123@email.com", "123456", "first", "user")
    # Successfully logout
    assert stub.auth_logout(user["token"]) == {"is_success": True}

    # Check that the token is no longer valid
    with pytest.raises(validation_helper.AccessError):
        stub.auth_logout(user["token"])


def test_auth_register():
    helper.reset_data()
    # Successful register
    user1 = stub.auth_register("test123@email.com", "123456", "first", "user")
    user2 = stub.auth_register("test1234@email.com", "123456", "second", "user")

    # Check that valid token has been created
    assert stub.channels_list(user1["token"]) == {"channels": []}
    assert stub.channels_list(user2["token"]) == {"channels": []}

    # Check that user1 is the owner of the slackr since they are the first user
    # But user2 is not
    # Do this by trying user permission change
    with pytest.raises(validation_helper.AccessError):
        stub.admin_userpermission_change(user2["token"], user1["u_id"], 3)
    stub.admin_userpermission_change(user1["token"], user2["u_id"], 2)

    # Invalid email
    with pytest.raises(validation_helper.ValueError):
        stub.auth_register("87", "123456", "first", "user")   # Invalid email

    # Email taken (by successful call)
    with pytest.raises(validation_helper.ValueError):
        stub.auth_register("test123@email.com", "123456", "first", "user")

    # Invalid password
    with pytest.raises(validation_helper.ValueError):
        stub.auth_register("test1234@email.com", "1", "first", "user")

    # Invalid firstname
    with pytest.raises(validation_helper.ValueError):
        stub.auth_register("test1234@email.com", "123456", "f"*51, "user")

    # Invalid lastname
    with pytest.raises(validation_helper.ValueError):
        stub.auth_register("test1234@email.com", "123456", "first", "u"*51)

    # Empty string
    with pytest.raises(validation_helper.ValueError):
        stub.auth_register("", "", "", "")


def test_auth_passwordreset_request():
    # commented this out since we have to test this using the flask server

    # helper.reset_data()
    # # Create users for testing
    # stub.auth_register("test123@email.com", "123456", "first", "user")

    # # Test for valid request
    # assert stub.auth_passwordreset_request("test123@email.com") == {}
    pass


def test_auth_passwordreset_reset():
    # note: commented most tests out since we have to test this using the flask server
    # can only check that error is raised if code is not in data
    helper.reset_data()
    # Create users for testing
   # user1 = stub.auth_register("test123@email.com", "123456", "first", "user")

    # # Send a password reset request
    # stub.auth_passwordreset_request("test123@email.com")

    # # Invalid password
    # with pytest.raises(validation_helper.ValueError):
    #     stub.auth_passwordreset_reset(user1["reset_code"], "1")

    # Invalid reset_code
    with pytest.raises(validation_helper.ValueError):
        stub.auth_passwordreset_reset("fake code", "123456")

    # # Changed password & successfully logged in
    # stub.auth_passwordreset_reset(user1["reset_code"], "1234567")
    # assert stub.auth_login("test123@email.com", "1234567") == {user1_id, user1_token}


def test_channel_invite():
    helper.reset_data()

    # Create users for testing
    user1 = helper.token_account_1()
    user2 = helper.token_account_2()

    # create a new channel for testing
    channel_id = helper.channelid_public(user1["token"])

    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.channel_invite("fake token", channel_id, user1["u_id"])

    # Invalid channel_id
    with pytest.raises(validation_helper.ValueError):
        stub.channel_invite(user1["token"], -1, user2["u_id"])

    # Invalid u_id
    with pytest.raises(validation_helper.ValueError):
        stub.channel_invite(user1["token"], channel_id, -1)

    # valid call
    assert stub.channel_invite(user1["token"], channel_id, user2["u_id"]) == {}

    # Test that the user is in the channel
    message_id = stub.message_send(user2["token"], channel_id, "Hi")["message_id"]

    # check that nothing happens if the user is already in the channel
    stub.channel_invite(user1["token"], channel_id, user1["u_id"])

    # check that if an admin/owner of the slackr is invited, they become an owner
    stub.channel_leave(user1["token"], channel_id)
    stub.channel_invite(user2["token"], channel_id, user1["u_id"])
    stub.message_remove(user1["token"], message_id)  # can do this since they should be an owner


def test_channel_details():
    helper.reset_data()
    # Create users for testing
    user1 = helper.token_account_1()
    user1_token = user1["token"]
    user1_id = user1["u_id"]
    user2 = helper.token_account_2()
    user2_token = user2["token"]

    # Create a new channel for testing
    channel_id = helper.channelid_public(user1_token)

    # this is to test things
    channel_name = "Public Channel"
    channel_owner_members = [{"name_first": "Mommy",
                              "name_last": "Pig",
                              "u_id": user1_id,
                              "profile_img_url": "/static/default.jpg"}]
    channel_all_members = [{"name_first": "Mommy",
                            "name_last": "Pig",
                            "u_id": user1_id,
                            "profile_img_url": "/static/default.jpg"}]

    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.channel_details("fake token", channel_id)

    # Channel doesn't exist
    with pytest.raises(validation_helper.ValueError):
        stub.channel_details(user1_token, -1)

    # user2 is not a member
    with pytest.raises(validation_helper.AccessError):
        stub.channel_details(user2_token, channel_id)

    # Valid call
    assert stub.channel_details(user1_token, channel_id) == {"name": channel_name,
                                                             "owner_members": channel_owner_members,
                                                             "all_members": channel_all_members}


def test_channel_messages():
    helper.reset_data()

    # Create users for testing
    user1 = helper.token_account_1()
    user1_token = user1["token"]
    user2 = helper.token_account_2()
    user2_token = user2["token"]

    # Create a new channel for testing
    channel_id = helper.channelid_public(user1_token)

    # Leave the channel in case user2 is in the new channel
    stub.channel_leave(user2_token, channel_id)

    # Setting the start & end
    start = 0

    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.channel_messages("fake token", channel_id, start)

    # Start is a invalid number
    with pytest.raises(validation_helper.ValueError):
        stub.channel_messages(user1_token, channel_id, -1)

    # Channel doesn't exist
    with pytest.raises(validation_helper.ValueError):
        stub.channel_messages(user1_token, -1, start)

    # Index of start greater then messages in channel
    with pytest.raises(validation_helper.ValueError):
        stub.channel_messages(user1_token, channel_id, 1000)

    # user2 is not a member
    with pytest.raises(validation_helper.AccessError):
        stub.channel_messages(user2_token, channel_id, start)

    # valid call
    message_id = helper.get_valid_message(user1_token, channel_id)
    message = get_info_helper.get_info_about_message(message_id)
    assert stub.channel_messages(user1_token, channel_id, start) == {"messages": [message],
                                                                     "start": 0,
                                                                     "end": -1}

    # now test it with >50 messages sent in the channel
    i = 0
    while i < 70:
        stub.message_send(user1_token, channel_id, "Hello")
        i += 1
    messages = stub.channel_messages(user1_token, channel_id, 10)
    assert messages["start"] == 10
    assert messages["end"] == 60
    assert len(messages["messages"]) == 50


def test_channel_leave():
    helper.reset_data()
    # SETUP START
    user = helper.token_admin()
    new_channel_id = helper.channelid_public(user["token"])
    # SETUP END

    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.channel_leave("fake token", new_channel_id)

    with pytest.raises(validation_helper.ValueError):
        # check that validation_helper.ValueError is raised if channel does not exist
        # Assumption: channel_id cannot be negative
        stub.channel_leave(user["token"], -1)

    # check that call is successful if channel exists and user is a member of it
    stub.channel_leave(user["token"], new_channel_id)
    assert validation_helper.is_member(user["u_id"], new_channel_id) is not True

    # check that nothing happens if user is not in the channel (assumption)
    stub.channel_leave(user["token"], new_channel_id)  # should raise no errors


def test_channel_join():
    helper.reset_data()
    # SETUP START
    user1 = helper.token_admin()
    user2 = helper.token_account_1()

    public_channel_id = helper.channelid_public(user1["token"])
    private_channel_id = helper.channelid_private(user1["token"])
    # SETUP END

    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.channel_join("fake token", public_channel_id)

    # Check that error is raised if an invalid channel_id is passed in
    with pytest.raises(validation_helper.ValueError):
        stub.channel_join(user1["token"], -1)

    with pytest.raises(validation_helper.ValueError):
        # check that validation_helper.ValueError is raised if channel does not exist
        # Assumption: channel_id cannot be negative
        stub.channel_join(user1["token"], -1)

    # check that nothing happens if user is already a member of the channel (assumption)
    stub.channel_join(user1["token"], public_channel_id)  # should raise no errors

    # check that channel_join is successful when channel is public
    stub.channel_join(user2["token"], public_channel_id)
    assert validation_helper.is_member(user2["u_id"], public_channel_id)

    with pytest.raises(validation_helper.AccessError):
        # check that validation_helper.AccessError is raised if channel
        # is private and user is not an admin
        stub.channel_join(user2["token"], private_channel_id)

    # check that channel_join is successful when channel is private and user is an admin
    stub.admin_userpermission_change(user1["token"], user2["u_id"], 2)
    stub.channel_join(user2["token"], private_channel_id)
    assert validation_helper.is_member(user2["u_id"], private_channel_id)


def test_channel_addowner():
    helper.reset_data()
    # SETUP START
    user1 = helper.token_admin()
    user2 = helper.token_account_1()

    new_channel_id = helper.channelid_public(user1["token"])
    # SETUP END

    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.channel_addowner("fake token", new_channel_id, user1["u_id"])

    # Check that error is raised if an invalid u_id is passed in
    with pytest.raises(validation_helper.ValueError):
        stub.channel_addowner(user1["token"], new_channel_id, -1)

    with pytest.raises(validation_helper.ValueError):
        # Check ValueError raised if channel does not exist
        # Assumption: channel_id cannot be negative
        stub.channel_addowner(user1["token"], -1, user1["u_id"])

    with pytest.raises(validation_helper.ValueError):
        # Check valueError raised if target user is already an owner
        stub.channel_addowner(user1["token"], new_channel_id, user1["u_id"])

    with pytest.raises(validation_helper.AccessError):
        # Check accessError raised if user is not an owner
        stub.channel_addowner(user2["token"], new_channel_id, user2["u_id"])

    # check that call is successful if all inputs are valid
    stub.channel_addowner(user1["token"], new_channel_id, user2["u_id"])
    assert validation_helper.is_owner(user2["u_id"], new_channel_id)


def test_channel_removeowner():
    helper.reset_data()
    # SETUP START
    user1 = helper.token_admin()
    user2 = helper.token_account_1()

    new_channel_id = helper.channelid_public(user1["token"])
    # SETUP END

    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.channel_removeowner("fake token", new_channel_id, user1["u_id"])

    with pytest.raises(validation_helper.ValueError):
        # check that validation_helper.ValueError is raised if channel does not exist
        # Assumption: channel_id cannot be negative
        stub.channel_removeowner(user1["token"], -1, user1["u_id"])

    with pytest.raises(validation_helper.ValueError):
        # Check ValueError raised if target user is not an owner
        stub.channel_removeowner(user1["token"], new_channel_id, user2["u_id"])

    with pytest.raises(validation_helper.AccessError):
        # Check accessError raised if user not an owner
        stub.channel_removeowner(user2["token"], new_channel_id, user1["u_id"])

    with pytest.raises(validation_helper.AccessError):
        # Check accessError raised if target is an owner
        stub.channel_removeowner(user1["token"], new_channel_id, user1["u_id"])

    # Check that call is successful if all inputs are valid
    stub.channel_addowner(user1["token"], new_channel_id, user2["u_id"])
    stub.channel_removeowner(user1["token"], new_channel_id, user2["u_id"])
    assert validation_helper.is_owner(user2["u_id"], new_channel_id) is not True


def test_channels_list():
    helper.reset_data()
    # SETUP START
    user1 = helper.token_admin()
    user2 = helper.token_account_1()

    channel1_id = helper.channelid_public(user1["token"])
    channel2_id = helper.channelid_private(user1["token"])
    # SETUP END

    assert stub.channels_list(user1["token"]) == {
        "channels": [
            {"channel_id": channel1_id, "name": "Public Channel"},
            {"channel_id": channel2_id, "name": "Private Channel"}
        ]
    }

    # Invalid token
    with pytest.raises(validation_helper.AccessError):
        stub.channels_list("fake token")

    # check that no channels are returned if user is not in any channel
    assert stub.channels_list(user2["token"]) == {"channels": []}

    stub.channel_join(user2["token"], channel1_id)

    # check that output changes once a user joins a channel
    assert stub.channels_list(user2["token"]) == {"channels": [{"channel_id": channel1_id, "name": "Public Channel"}]}

    # check that output changes once a user leaves a channel
    stub.channel_leave(user1["token"], channel1_id)
    assert stub.channels_list(user1["token"]) == {"channels": [{"channel_id": channel2_id, "name": "Private Channel"}]}


def test_channels_listall():
    helper.reset_data()
    # SETUP START
    user1 = helper.token_admin()
    user2 = helper.token_account_1()
    # SETUP END

    # check that no channels are returned when none exist
    assert stub.channels_list(user2["token"]) == {"channels": []}

    # MORE SETUP
    public_channel_id = helper.channelid_public(user1["token"])
    private_channel_id = helper.channelid_private(user1["token"])

    # check that both private and public channels are returned
    assert stub.channels_listall(user1["token"]) == {
        "channels": [
            {"channel_id": public_channel_id, "name": "Public Channel"},
            {"channel_id": private_channel_id, "name": "Private Channel"},
        ]
    }

    # check that all public channels are returned even if the user is not in them
    # Assumption: private channels are not listed if the user is not in them and not an admin
    assert stub.channels_listall(user2["token"]) == {
        "channels": [{"channel_id": public_channel_id, "name": "Public Channel"}],
    }

    # check that private channels are returned even if the user is not in them,
    # provided that the user is an admin
    stub.channel_leave(user1["token"], private_channel_id)
    assert stub.channels_listall(user1["token"]) == {
        "channels": [
            {"channel_id": public_channel_id, "name": "Public Channel"},
            {"channel_id": private_channel_id, "name": "Private Channel"},
        ]
    }


def test_channels_create():
    helper.reset_data()
    user = helper.token_admin()

    # Invalid token
    with pytest.raises(validation_helper.AccessError):
        stub.channels_create("fake token", "name", True)

    with pytest.raises(validation_helper.ValueError):
        # check that validation_helper.ValueError is raised if name is more than 20 characters long
        stub.channels_create(user["token"], "123456789012345678901", True)

    with pytest.raises(validation_helper.ValueError):
        # check that validation_helper.ValueError is raised if name is an empty string (assumption)
        stub.channels_create(user["token"], "", True)

    # check that call is successful otherwise
    public_channel_id = stub.channels_create(user["token"], "Public Channel", True)["channel_id"]
    private_channel_id = stub.channels_create(user["token"], "Private Channel", False)["channel_id"]

    assert stub.channels_listall(user["token"]) == {
        "channels": [
            {"channel_id": public_channel_id, "name": "Public Channel"},
            {"channel_id": private_channel_id, "name": "Private Channel"}
        ]
    }

    # note: haven't tested whether private_channel is actually private
    # because this is basically tested in test_channel_join
    # however there may be another way to test this later


def test_message_sendlater():
    helper.reset_data()

    # Valid parameters
    token = helper.token_account_1()["token"]
    channel_id = helper.get_valid_channel(token)
    message = "Testing the function message_sendlater."
    time_sent = helper.in_one_second()

    # Invalid parameters
    unauthorised_token = helper.token_account_2()["token"]
    invalid_channel_id = -00000
    invalid_message = message*3000
    invalid_time_sent = datetime(2018, 12, 12)
    stub.channel_leave(unauthorised_token, channel_id)

    # Test that it raises a error if the channel does not exist
    with pytest.raises(validation_helper.ValueError):
        stub.message_sendlater(token, invalid_channel_id, message, time_sent)

    # Test that it raises an error if the message is >1000 characters
    with pytest.raises(validation_helper.ValueError):
        stub.message_sendlater(token, channel_id, invalid_message, time_sent)

    # Test that it raises an error if the time sent is a time in the past
    with pytest.raises(validation_helper.ValueError):
        stub.message_sendlater(token, channel_id, message, invalid_time_sent)

    # Test that it raises an access error if the token is not an authorised user
    with pytest.raises(validation_helper.AccessError):
        stub.message_sendlater(unauthorised_token, channel_id, message, time_sent)

    # Test that the function successfully completes with valid parameters
    # (this may require manual verification)
    message_id = stub.message_sendlater(token, channel_id, message, time_sent)["message_id"]
    assert message_id > -1


def test_message_send():
    helper.reset_data()

    # Valid parameters
    token = helper.token_account_1()["token"]
    channel_id = helper.get_valid_channel(token)
    message = "Testing the function message_send."

    # Invalid parameters
    invalid_channel_id = -00000
    invalid_message = message*3000
    unauthorised_token = helper.token_account_2()["token"]

    # Test that it raises an erorr if the channel does not exist
    with pytest.raises(validation_helper.ValueError):
        stub.message_send(token, invalid_channel_id, message)

    # Test that it raises an erorr if the message is >1000 characters
    with pytest.raises(validation_helper.ValueError):
        stub.message_send(token, channel_id, invalid_message)

    # Test that it raises an access erorr if the token is not an authorised user.
    # Note: we assume the second account is not part of the channel. This will fail if the second
    # account is in the channel
    with pytest.raises(validation_helper.AccessError):
        stub.channel_leave(unauthorised_token, channel_id)
        stub.message_send(unauthorised_token, channel_id, message)

    # Test that the function successfully completes with valid parameters
    # (this may require manual verification)
    assert stub.message_send(token, channel_id, message)["message_id"] > -1


def test_message_remove():
    helper.reset_data()

    # Valid parameters
    token = helper.token_account_1()["token"]
    channel_id = helper.get_valid_channel(token)
    message_id = helper.get_valid_message(token, channel_id)
    message = "This message was produced by the get_valid_message function."

    # Invalid parameters
    unauthorised_token = helper.token_account_2()["token"]
    stub.channel_leave(unauthorised_token, channel_id)

    # Test that it raises an access erorr if the user is not in the channel
    # to remove a message
    with pytest.raises(validation_helper.AccessError):
        stub.message_remove(unauthorised_token, message_id)

    # Test that it raises an access erorr if the user does not have the proper
    # authority to remove a message
    with pytest.raises(validation_helper.AccessError):
        stub.channel_join(unauthorised_token, channel_id)
        stub.message_remove(unauthorised_token, message_id)

    # Attempt to successfully remove a message
    assert stub.message_remove(token, message_id) == {}

    # Test that it raises an error if trying to remove a already removed message
    with pytest.raises(validation_helper.ValueError):
        stub.message_remove(token, message_id)

    # Test that the message disappears from search
    assert message_id not in stub.search(token, message)


def test_message_edit():
    helper.reset_data()

    # Valid parameters
    token = helper.token_account_1()["token"]
    channel_id = helper.get_valid_channel(token)
    message_id = helper.get_valid_message(token, channel_id)
    message = "This message was edited by the message_edit function."

    # Invalid parameters
    invalid_message = message*3000
    invalid_message_id = -1
    unauthorised_token = helper.token_account_2()["token"]

    # Test that it raises an error if a user edits a message that is not theirs.
    with pytest.raises(validation_helper.AccessError):
        stub.channel_join(unauthorised_token, channel_id)
        stub.message_edit(unauthorised_token, message_id, message)
    stub.channel_leave(unauthorised_token, channel_id)

    # Test that it raises an error if invalid message_id
    with pytest.raises(validation_helper.ValueError):
        stub.message_edit(token, invalid_message_id, message)

    # Test that it raises an error if it is a invalid message being edited
    with pytest.raises(validation_helper.ValueError):
        stub.message_edit(token, message_id, invalid_message)

    # Attempt to successfully edit a message
    assert stub.message_edit(token, message_id, message) == {}

    # Test that the message is edited in search
    assert stub.search(token, message)["messages"] != []

    # Test that message is deleted if edited with an empty string
    stub.message_edit(token, message_id, "")
    assert stub.channel_messages(token, channel_id, 0)["messages"] == []


def test_message_react():
    helper.reset_data()

    # Valid parameters
    token = helper.token_account_1()["token"]
    react_id = 1  # We do not have any way of obtaining a valid react_id atm
    channel_id = helper.get_valid_channel(token)
    message_id = helper.get_valid_message(token, channel_id)

    # Invalid parameters
    invalid_react_id = -1
    invalid_message_id = -1

    # message_id is not a valid message within a channel that the authorised user has joined
    with pytest.raises(validation_helper.ValueError):
        stub.message_react(token, invalid_message_id, react_id)

    # react_id is not a valid React ID
    with pytest.raises(validation_helper.ValueError):
        stub.message_react(token, message_id, invalid_react_id)

    # Successfully react a message
    assert stub.message_react(token, message_id, react_id) == {}

    # Message with ID message_id already contains an active React with ID react_id
    with pytest.raises(validation_helper.ValueError):
        stub.message_react(token, message_id, react_id)


def test_message_unreact():
    helper.reset_data()

    # Set up valid parameters
    token = helper.token_account_1()["token"]
    react_id = 1  # We do not have any way of obtaining a valid react_id atm
    channel_id = helper.get_valid_channel(token)
    message_id = helper.get_valid_message(token, channel_id)
    stub.message_react(token, message_id, react_id)

    # Set up invalid parameters
    invalid_react_id = -1
    invalid_message_id = -1

    # message_id is invalid
    with pytest.raises(validation_helper.ValueError):
        stub.message_unreact(token, invalid_message_id, react_id)

    # react_id is not a valid React ID
    with pytest.raises(validation_helper.ValueError):
        stub.message_unreact(token, invalid_message_id, invalid_react_id)

    # successfully unreact a message
    assert stub.message_unreact(token, message_id, react_id) == {}

    # unreact something you already unreacted
    with pytest.raises(validation_helper.ValueError):
        stub.message_unreact(token, message_id, react_id)


def test_message_pin():
    helper.reset_data()

    # Set up valid parameters
    token = helper.token_admin()["token"]
    not_admin = helper.token_account_1()["token"]
    channel_id = helper.get_valid_channel(not_admin)
    message_id = helper.get_valid_message(not_admin, channel_id)
    stub.channel_join(token, channel_id)

    # Set up invalid parameters
    invalid_message_id = -1

    # message_id is not a valid message
    with pytest.raises(validation_helper.ValueError):
        stub.message_pin(token, invalid_message_id)

    # Error when the authorised user is not an admin
    with pytest.raises(validation_helper.ValueError):
        stub.message_pin(not_admin, message_id)

    # Error when the admin is not a member of the channel that the message is within
    with pytest.raises(validation_helper.AccessError):
        stub.channel_leave(token, channel_id)
        stub.message_pin(channel_id, message_id)
    stub.channel_join(token, channel_id)

    # successfully pin a message
    assert stub.message_pin(token, message_id) == {}

    # try and pin a message again
    with pytest.raises(validation_helper.ValueError):
        stub.message_pin(token, message_id)


def test_message_unpin():
    helper.reset_data()

    # Set up valid parameters
    token = helper.token_admin()["token"]
    not_admin = helper.token_account_1()["token"]
    channel_id = helper.get_valid_channel(not_admin)
    message_id = helper.get_valid_message(not_admin, channel_id)
    stub.channel_join(token, channel_id)
    stub.message_pin(token, message_id)

    # Set up invalid parameters
    invalid_message_id = -1

    # message_id is not a valid message
    with pytest.raises(validation_helper.ValueError):
        stub.message_unpin(token, invalid_message_id)

    # Error when the authorised user is not an admin
    with pytest.raises(validation_helper.ValueError):
        stub.message_unpin(not_admin, message_id)

    # Error when the admin is not a member of the channel that the message is within
    with pytest.raises(validation_helper.AccessError):
        stub.channel_leave(token, channel_id)
        stub.message_unpin(channel_id, message_id)
    stub.channel_join(token, channel_id)

    # successfully unpin a message
    assert stub.message_unpin(token, message_id) == {}

    # try and unpin a message again
    with pytest.raises(validation_helper.ValueError):
        stub.message_unpin(token, message_id)


def test_user_profile():
    helper.reset_data()
    # SETUP START
    admin = helper.token_admin()
    user = helper.token_account_1()
    # Invalid User
    invalid_token = "invalidTest"
    invalid_user = -1
    # SETUP END

    # Checks that an error is raised for invalid token
    with pytest.raises(validation_helper.AccessError):
        stub.user_profile(invalid_token, user["u_id"])

    # Checks that an error is raised for invalid user
    with pytest.raises(validation_helper.ValueError):
        stub.user_profile(admin["token"], invalid_user)

    # Checks that the correct user profile is returned
    assert stub.user_profile(admin["token"], admin["u_id"]) == {"u_id": admin["u_id"],
                                                                "email": "admin@email.com",
                                                                "name_first": "Daddy",
                                                                "name_last": "Pig",
                                                                "handle_str": "daddypig",
                                                                "profile_img_url": "/static/default.jpg",
                                                                }

    assert stub.user_profile(user["token"], user["u_id"]) == {"u_id": user["u_id"],
                                                              "email": "test1@email.com",
                                                              "name_first": "Mommy",
                                                              "name_last": "Pig",
                                                              "handle_str": "mommypig",
                                                              "profile_img_url": "/static/default.jpg",
                                                              }


def test_user_profile_setname():
    helper.reset_data()
    # SETUP START
    admin = helper.token_admin()
    token = admin["token"]
    profile_dict = stub.user_profile(token, admin["u_id"])
    curr_first = profile_dict['name_first']
    curr_last = profile_dict['name_last']
    # Set names to the following
    new_first = "George"
    new_last = "pig"
    # Invalid input with >50 characters
    invalid_name = "a" * 51
    # Invalid input that aren't words
    jibberish = '??[45jibbersh'
    no_input = ' '
    # Channel to be used in last test
    channel_id = helper.channelid_public(token)
    # SETUP END

    # Checks that an error is raised for > 50 characters
    with pytest.raises(validation_helper.ValueError):
        stub.user_profile_setname(token, invalid_name, invalid_name)

    # Checks that an error is raised for no input
    with pytest.raises(validation_helper.ValueError):
        stub.user_profile_setname(token, new_first, no_input)

    # Checks that an error is raised for not valid characters
    with pytest.raises(validation_helper.ValueError):
        stub.user_profile_setname(token, new_first, jibberish)

    # Checks that the name is updated if its <= 50 characters
    stub.user_profile_setname(admin["token"], new_first, new_last)
    assert(curr_first != new_first and curr_last != new_last)
    new_dict = stub.user_profile(admin["token"], admin["u_id"])
    assert new_dict['name_first'] == new_first and new_dict['name_last'] == new_last

    # Checks that name has also been updated in the channel
    assert stub.channel_details(token, channel_id)["all_members"] == [{
                                                                        "u_id": admin["u_id"],
                                                                        "name_first": new_first,
                                                                        "name_last": new_last,
                                                                        "profile_img_url": "/static/default.jpg"
                                                                    }]
    assert stub.channel_details(token, channel_id)["owner_members"] == [{
                                                                        "u_id": admin["u_id"],
                                                                        "name_first": new_first,
                                                                        "name_last": new_last,
                                                                        "profile_img_url": "/static/default.jpg"
                                                                        }]


def test_user_profile_setemail():
    helper.reset_data()
    # SETUP START
    admin = helper.token_admin()
    token = admin["token"]
    profile_dict = stub.user_profile(admin["token"], admin["u_id"])
    curr_email = profile_dict['email']
    # New email
    new_email = "new@gmail.com"
    # Used email
    used_email = "admin@email.com"
    # Invalid email
    invalid_email = "user.com"
    # SETUP END

    # Checks that it raises an error for used emails
    with pytest.raises(validation_helper.ValueError):
        stub.user_profile_setemail(token, used_email)

    # Checks that it raises an error for invalid emails
    with pytest.raises(validation_helper.ValueError):
        stub.user_profile_setemail(token, invalid_email)

    # Checks that the function has successfully changed valid email
    stub.user_profile_setemail(token, new_email)
    assert curr_email != new_email


# assuming tokens don't change as its not tested
def test_user_profile_sethandle():
    helper.reset_data()
    # SETUP START
    admin = helper.token_admin()
    admin_profile_dict = stub.user_profile(admin["token"], admin["u_id"])
    curr_handle = admin_profile_dict["handle_str"]
    new_handle = 'pig_daddy'
    # Invalid handle with >20 characters
    max_handle = 'a' * 21
    # Invalid handle with no valid characters
    invalid_handle = '??'
    # Invalid handle with no input
    no_handle = ' '
    # SETUP END

    # Checks that an error is raised for >20 characters
    with pytest.raises(validation_helper.ValueError):
        stub.user_profile_sethandle(admin["token"], max_handle)

    # Checks that an error is raised for invalid characters
    with pytest.raises(validation_helper.ValueError):
        stub.user_profile_sethandle(admin["token"], invalid_handle)

    # Checks that an error is raised for no characters
    with pytest.raises(validation_helper.ValueError):
        stub.user_profile_sethandle(admin["token"], no_handle)

    # Successfully updated the handle
    stub.user_profile_sethandle(admin["token"], new_handle)
    assert curr_handle != new_handle


def test_user_profiles_uploadphoto():
    helper.reset_data()
    # SETUP START
    admin = helper.token_admin()
    token = admin["token"]
    img_url = "https://data.junkee.com/wp-content/uploads/2018/04/peppapig-680x454.jpg"
    x_start = 0
    y_start = 0
    x_end = 100
    y_end = 100
    # Invalid Inputs
    invalidx_start = -1
    invalidx_end = -1
    largex_start = 1000000
    largex_end = 1000000
    invalid_img = "https://www.peppapig.com/wp-content/uploads/sites/3/2019/02/peppa_pig_splat.png"

    # Checks that it raises an error for invalid bounds
    with pytest.raises(validation_helper.ValueError):
        stub.user_profiles_uploadphoto(token, img_url, invalidx_start, y_start, invalidx_end, y_end)

    # Checks that it raises an error for HTTP other than 200
    with pytest.raises(validation_helper.ValueError):
        stub.user_profiles_uploadphoto(token, invalid_img, x_start, y_start, x_end, y_end)

    # Checks that it raises an error if bounds are not within image dimensions
    with pytest.raises(validation_helper.ValueError):
        stub.user_profiles_uploadphoto(token, img_url, largex_start, y_start, largex_end, y_end)

    # Checks that valid profile photo is updated
    stub.user_profiles_uploadphoto(token, img_url, x_start, y_start, x_end, y_end)


def test_users_all():
    helper.reset_data()
    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.users_all("fake token")

    user1 = helper.token_admin()

    # Check successful call
    users = stub.users_all(user1["token"])["users"]
    assert len(users) == 1
    assert users[0]["email"] == "admin@email.com"
    assert users[0]["name_last"] == "Pig"

    # Check that the list changes when a new person registers
    user2 = helper.token_account_1()
    users = stub.users_all(user1["token"])["users"]
    assert len(users) == 2


def test_standup_start():
    helper.reset_data()
    # SETUP START
    admin = helper.token_admin()
    token = admin["token"]
    channel_id = helper.channelid_public(token)
    # Invalid channel id
    invalid_channel_id = -111111
    # SETUP END

    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.standup_start("fake token", channel_id, 10)

    # Checks that it raises an error when channel id does not exist
    with pytest.raises(validation_helper.ValueError):
        stub.standup_start(token, invalid_channel_id, 10)

    # Checks that a standup has successfully started
    time_check = get_info_helper.get_serializable_datetime(datetime.now() + timedelta(seconds=6))

    assert stub.standup_start(token, channel_id, 5)["time_finish"] < time_check

    # Checks that it raises an error when the user is not part of the channel
    with pytest.raises(validation_helper.AccessError):
        stub.channel_leave(admin["token"], channel_id)
        stub.standup_start(token, channel_id, 10)


def test_standup_active():
    helper.reset_data()
    # SETUP START
    admin = helper.token_admin()
    channel_id = helper.channelid_public(admin["token"])
    # SETUP END

    # Check that error is raised if an invalid token is passed in
    with pytest.raises(validation_helper.AccessError):
        stub.standup_active("fake token", channel_id)

    # Checks that it raises an error when channel does not exit
    with pytest.raises(validation_helper.ValueError):
        stub.standup_active(admin["token"], -1)

    # Check when there is no standup
    assert stub.standup_active(admin["token"], channel_id) == {"is_active": False, "time_finish": None}

    # Check when there is a standup
    stub.standup_start(admin["token"], channel_id, 3)
    assert stub.standup_active(admin["token"], channel_id)["is_active"] is True


def test_standup_send():
    helper.reset_data()
    # SETUP START
    admin = helper.token_admin()
    token = admin["token"]
    channel_id = helper.channelid_public(token)
    text = "Hi"
    stub.standup_start(token, channel_id, 5)
    # Invalid inputs
    invalid_channel_id = -111111
    invalid_text = 'Hi' * 1001
    # SETUP END

    # Checks that it raises an error when the channel ID does not exit
    with pytest.raises(validation_helper.ValueError):
        stub.standup_send(token, invalid_channel_id, text)

    # Checks that it raises an error for > 1000 characters
    with pytest.raises(validation_helper.ValueError):
        stub.standup_send(token, channel_id, invalid_text)

    # Successfully send a message in a standup
    assert stub.standup_send(token, channel_id, text) == {}

    # Checks that it raises an error when user is not part of the channel
    with pytest.raises(validation_helper.AccessError):
        stub.channel_leave(admin["token"], channel_id)
        stub.standup_send(admin["token"], channel_id, text)

    # Checks that it raises an error if the standup time has stopped
    with pytest.raises(validation_helper.AccessError):
        time.sleep(6)
        stub.standup_send(token, channel_id, text)


def test_search():
    helper.reset_data()
    # SETUP START
    admin = helper.token_admin()
    channel_id = helper.channelid_public(admin["token"])
    keyword = "Hello" + str(random())
    # SETUP END

    # Checks that nothing is returned if the message does not exist
    assert stub.search(admin["token"], "this message does not exist" + str(random())) == {"messages": []}

    # Checks that messages are successfully returned
    stub.message_send(admin["token"], channel_id, keyword)
    assert keyword in stub.search(admin["token"], keyword)["messages"][0]["message"]


def test_admin_userpermission_change():
    helper.reset_data()
    user1 = helper.token_admin()
    user2 = helper.token_account_1()

    # Invalid token
    with pytest.raises(validation_helper.AccessError):
        stub.admin_userpermission_change("fake token", user2["u_id"], 2)

    with pytest.raises(validation_helper.ValueError):
        # check that validation_helper.ValueError is raised if u_id is not valid
        # Assumption: u_ids cannot be negative
        stub.admin_userpermission_change(user1["token"], -1, 2)

    with pytest.raises(validation_helper.ValueError):
        # check that validation_helper.ValueError is raised if permission_id is not valid
        stub.admin_userpermission_change(user1["token"], user1["u_id"], 10)

    # check that function can run if all inputs are valid
    stub.admin_userpermission_change(user1["token"], user2["u_id"], 1)

    # if previous call was successful, user2 should be able to change their own permissions
    # Assumption: users can change their own permissions provided they are currently an admin
    stub.admin_userpermission_change(user2["token"], user2["u_id"], 3)

    with pytest.raises(validation_helper.AccessError):
        # check that validation_helper.AccessError is raised if user is not an admin or owner
        # this should raise an error since user2 has removed their own permissions
        stub.admin_userpermission_change(user2["token"], user1["u_id"], 3)
