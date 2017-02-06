
from datetime import datetime

from django_socketio.channels import CHANNELS
from django_socketio.clients import CLIENTS


class NoSocket(Exception):
    """
    Raised when no clients are available to broadcast to.
    """


def send(session_id, message):
    """
    Send a message to the socket for the given session ID.
    """
    try:
        socket = CLIENTS[session_id][1]
    except KeyError:
        raise NoSocket("There is no socket with the session ID: " + session_id)
    socket.send(message)


def broadcast(message):
    """
    Find the first socket and use it to broadcast to all sockets
    including the socket itself.
    """
    try:
        socket = CLIENTS.values()[0][1]
    except IndexError:
        raise NoSocket("There are no clients.")
    socket.send_and_broadcast(message)


def broadcast_channel(message, channel):
    """
    Find the first socket for the given channel, and use it to
    broadcast to the channel, including the socket itself.
    """
    try:
        session_ids = []
        socket = None
        for session_id in CHANNELS.get(channel, []):
            if session_id not in CLIENTS:
                session_ids.append(session_id)
                CHANNELS[channel].remove(session_id)
            else:
                socket = CLIENTS[session_id][1]
    except IndexError, KeyError:
        raise NoSocket("There are no clients on the channel: " + channel)
    if socket:
        socket.send_and_broadcast_channel(message, channel)
    else:
        raise NoSocket("There are no sessionids:[{}] on the channel:{} ".format(','.join(session_ids), channel))


def format_log(request, message_type, message):
    """
    Formats a log message similar to gevent's pywsgi request logging.
    """
    from django_socketio.settings import MESSAGE_LOG_FORMAT
    if MESSAGE_LOG_FORMAT is None:
        return None
    now = datetime.now().replace(microsecond=0)
    args = dict(request.META, TYPE=message_type, MESSAGE=message, TIME=now)
    return (MESSAGE_LOG_FORMAT % args) + "\n"
