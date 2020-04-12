"""Flask server"""
import sys
from flask_cors import CORS
from json import dumps
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.exceptions import HTTPException
from flask_mail import Mail, Message
import server.stub as stub
from datetime import datetime
import pickle


def default_handler(err):
    response = err.get_response()
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


# Load data from file
try:
    with open("database.p", "rb") as fp:
        stub.data = pickle.load(fp)
except Exception as e:
    print(e)

APP = Flask(__name__, static_url_path='/static/')
APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, default_handler)
CORS(APP)

APP.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = "peppapigisok@gmail.com",
    MAIL_PASSWORD = "peppapig1"
)

@APP.route('/echo/get', methods=['GET'])
def echo1():
    """ returns what is given by GET request """
    return dumps({
        'echo': request.args.get('echo'),
    })


@APP.route('/echo/post', methods=['POST'])
def echo2():
    """ returns what is given by POST """
    return dumps({
        'echo': request.form.get('echo'),
    })


# Interface


@APP.route('/auth/login', methods=['POST'])
def auth_login():
    """ uses stub.py interface function to login a user """
    return dumps(stub.auth_login(request.form.get('email'), request.form.get('password')))


@APP.route('/auth/logout', methods=['POST'])
def auth_logout():
    """ uses stub.py interface function to logout a user """
    return dumps(stub.auth_logout(request.form.get('token')))


@APP.route('/auth/register', methods=['POST'])
def auth_register():
    """ uses stub.py interface function to register a new user """
    return dumps(
        stub.auth_register(request.form.get('email'),
                           request.form.get('password'),
                           request.form.get('name_first'),
                           request.form.get('name_last')))


@APP.route('/auth/passwordreset/request', methods=['POST'])
def auth_passwordreset_request():
    """ sends an email with a reset code unless email is not in data """
    email = request.form.get('email')
    # get code from stub interface function
    code = stub.auth_passwordreset_request(email)["code"]
    if code is None:
        return dumps({})
    else:
        mail = Mail(APP)
        try:
            msg = Message("Slackr Password Reset Code",
                sender="peppapigisok@gmail.com",
                recipients=[email])
            msg.body = "Your password reset code is: " + code
            mail.send(msg)
            return dumps({})
        except Exception as e:
            return (str(e))


@APP.route('/auth/passwordreset/reset', methods=['POST'])
def auth_passwordreset_reset():
    """ uses stub.py interface function to reset a password """
    return dumps(stub.auth_passwordreset_reset(request.form.get('reset_code'),
                                               request.form.get('new_password')))


@APP.route('/channel/invite', methods=['POST'])
def channel_invite():
    """ uses stub.py interface function to invite a user to a channel """
    return dumps(
        stub.channel_invite(request.form.get('token'), int(request.form.get('channel_id')),
                            int(request.form.get('u_id'))))


@APP.route('/channel/details', methods=['GET'])
def channel_details():
    """ uses stub.py interface function to get details about a channel """
    return dumps(stub.channel_details(request.args.get('token'),
                                      int(request.args.get('channel_id'))))


@APP.route('/channel/messages', methods=['GET'])
def channel_messages():
    """ uses stub.py interface function to get messages from a channel """
    return dumps(
        stub.channel_messages(request.args.get('token'),
                              int(request.args.get('channel_id')),
                              int(request.args.get('start'))))


@APP.route('/channel/leave', methods=['POST'])
def channel_leave():
    """ uses stub.py interface function to remove a user from a channel """
    return dumps(stub.channel_leave(request.form.get('token'),
                                    int(request.form.get('channel_id'))))


@APP.route('/channel/join', methods=['POST'])
def channel_join():
    """ uses stub.py interface function to add a user to a channel """
    return dumps(stub.channel_join(request.form.get('token'),
                                   int(request.form.get('channel_id'))))


@APP.route('/channel/addowner', methods=['POST'])
def channel_addowner():
    """ uses stub.py interface function to add a user as an owner of a channel """
    return dumps(
        stub.channel_addowner(request.form.get('token'),
                              int(request.form.get('channel_id')),
                              int(request.form.get('u_id'))))


@APP.route('/channel/removeowner', methods=['POST'])
def channel_removeowner():
    """ uses stub.py interface function to remove a user as an owner of a channel """
    return dumps(
        stub.channel_removeowner(request.form.get('token'),
                                 int(request.form.get('channel_id')),
                                 int(request.form.get('u_id'))))


@APP.route('/channels/list', methods=['GET'])
def channels_list():
    """ uses stub.py interface function to get a list of the channels a user is in """
    return dumps(stub.channels_list(request.args.get('token')))


@APP.route('/channels/listall', methods=['GET'])
def channels_listall():
    """ uses stub.py interface function to get a list of all channels a user can join """
    return dumps(stub.channels_listall(request.args.get('token')))


@APP.route('/channels/create', methods=['POST'])
def channels_create():
    """ uses stub.py interface function to create a channel """
    # print(request.form.get('is_public'))
    # print(request.form.get('is_public') == "true")
    if request.form.get('is_public') == "false":
        is_public = False
    else: 
        is_public = True
    
    return dumps(
        stub.channels_create(request.form.get('token'),
                             request.form.get('name'),
                             is_public))


@APP.route('/message/sendlater', methods=['POST'])
def message_sendlater():
    """ uses stub.py interface function to create a message that is sent later """
    # so the time sent is given in a unix timestamp string
    ts = int(request.form.get('time_sent'))/1000
    print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
    return dumps(
        stub.message_sendlater(request.form.get('token'),
                               int(request.form.get('channel_id')),
                               request.form.get('message'),
                               datetime.utcfromtimestamp(ts)))


@APP.route('/message/send', methods=['POST'])
def message_send():
    """ uses stub.py interface function to send a message immediately """
    return dumps(
        stub.message_send(request.form.get('token'),
                          int(request.form.get('channel_id')),
                          request.form.get('message')))


@APP.route('/message/remove', methods=['DELETE'])
def message_remove():
    """ uses stub.py interface function to remove a message """
    return dumps(stub.message_remove(request.form.get('token'),
                                     int(request.form.get('message_id'))))


@APP.route('/message/edit', methods=['PUT'])
def message_edit():
    """ uses stub.py interface function to edit a message """
    return dumps(
        stub.message_edit(request.form.get('token'),
                          int(request.form.get('message_id')),
                          request.form.get('message')))


@APP.route('/message/react', methods=['POST'])
def message_react():
    """ uses stub.py interface function to add a react to a message """
    return dumps(
        stub.message_react(request.form.get('token'),
                           int(request.form.get('message_id')),
                           int(request.form.get('react_id'))))


@APP.route('/message/unreact', methods=['POST'])
def message_unreact():
    """ uses stub.py interface function to remove a react from a message """
    return dumps(
        stub.message_unreact(request.form.get('token'),
                             int(request.form.get('message_id')),
                             int(request.form.get('react_id'))))


@APP.route('/message/pin', methods=['POST'])
def message_pin():
    """ uses stub.py interface function to pin a message """
    return dumps(stub.message_pin(request.form.get('token'),
                                  int(request.form.get('message_id'))))


@APP.route('/message/unpin', methods=['POST'])
def message_unpin():
    """ uses stub.py interface function to unpin a message """
    return dumps(stub.message_unpin(request.form.get('token'),
                                    int(request.form.get('message_id'))))


@APP.route('/user/profile', methods=['GET'])
def user_profile():
    """ uses stub.py interface function to get a user's profile info """
    return dumps(stub.user_profile(request.args.get('token'),
                                   int(request.args.get('u_id'))))


@APP.route('/user/profile/setname', methods=['PUT'])
def user_profile_setname():
    """ uses stub.py interface function to change a user's name """
    return dumps(stub.user_profile_setname(request.form.get('token'),
                                           request.form.get('name_first'),
                                           request.form.get('name_last')))


@APP.route('/user/profile/setemail', methods=['PUT'])
def user_profile_setemail():
    """ uses stub.py interface function to change a user's email """
    return dumps(stub.user_profile_setemail(request.form.get('token'),
                                            request.form.get('email')))


@APP.route('/user/profile/sethandle', methods=['PUT'])
def user_profile_sethandle():
    """ uses stub.py interface function to change a user's handle """
    return dumps(stub.user_profile_sethandle(request.form.get('token'),
                                             request.form.get('handle_str')))


@APP.route('/user/profiles/uploadphoto', methods=['POST'])
def user_profile_uploadphoto():
    """ uses stub.py interface function to upload a photo """
    return dumps(stub.user_profiles_uploadphoto(request.form.get('token'),
                                                request.form.get('img_url'),
                                                int(request.form.get('x_start')),
                                                int(request.form.get('y_start')),
                                                int(request.form.get('x_end')),
                                                int(request.form.get('y_end'))))

@APP.route('/users/all', methods=['GET'])
def users_all():
    """ uses stub.py interface function to get a list of all users """
    return dumps(stub.users_all(request.args.get('token')))


@APP.route('/standup/start', methods=['POST'])
def standup_start():
    """ uses stub.py interface function to start a standup """
    return dumps(stub.standup_start(request.form.get('token'),
                                    int(request.form.get('channel_id')),
                                    int(request.form.get('length'))))

@APP.route('/standup/active', methods=['GET'])
def standup_active():
    """ uses stub.py interface function to check if a standup is active """
    return dumps(stub.standup_active(request.args.get('token'),
                                    int(request.args.get('channel_id'))))


@APP.route('/standup/send', methods=['POST'])
def standup_send():
    """ uses stub.py interface function to send a message to a standup """
    return dumps(
        stub.standup_send(request.form.get('token'),
                          int(request.form.get('channel_id')),
                          request.form.get('message')))


@APP.route('/search', methods=['GET'])
def search():
    """ uses stub.py interface function to find all messages matching a query """
    return dumps(stub.search(request.args.get('token'),
                             request.args.get('query_str')))


@APP.route('/admin/userpermission/change', methods=['POST'])
def admin_userpermission_change():
    """ uses stub.py interface function to change a user's permissions """
    return dumps(stub.admin_userpermission_change(request.form.get('token'),
                                                  int(request.form.get('u_id')),
                                                  int(request.form.get('permission_id'))))

@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('', path)


if __name__ == '__main__':
    APP.run(port=(sys.argv[1] if len(sys.argv) > 1 else 5000))
