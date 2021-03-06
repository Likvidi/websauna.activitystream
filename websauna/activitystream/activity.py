from uuid import UUID

from sqlalchemy.orm import Session

from websauna.system.http import Request
from websauna.system.user.models import User
from websauna.utils.time import now

from .events import ActivityCreated
from .models import Activity
from .models import Stream


def create_activity(request: Request, activity_type: str, msg_context: dict, object_id: UUID, user: User):
    """Creates a new activity.

    The caller is responsible for firing events.

    :param request:
    :param msg_id:
    :param msg_context:
    :param object_id:
    :param user:
    :return:
    """
    dbsession = Session.object_session(user)

    stream = Stream.get_or_create_user_stream(user)

    a = Activity()
    a.object_id = object_id
    a.activity_type = activity_type
    a.msg_context = msg_context

    stream.activities.append(a)
    dbsession.flush()

    return a


def get_last_unseen(stream: Stream, limit=5):
    return stream.activities.filter(Activity.seen_at == None)[0:5]


def get_unread_activity_count(stream: Stream):
    """Get number of unseen activities"""
    return stream.activities.filter(Activity.seen_at == None).count()


def mark_seen(stream: Stream, object_id: UUID, activity_type=None):
    """Mark notifications seen bt user.

    Call this in the context of target page view function.

    :param activity_type: Optional type if the same object can have several activities of different types.
    """
    unread = stream.activities.filter(Activity.object_id==object_id, Activity.seen_at==None)

    if activity_type:
        unread.filter(Activity.activity_type==activity_type)

    unread.update(values=dict(seen_at=now()))


def mark_seen_by_user(user: User, object_id: UUID, activity_type=None):
    stream = Stream.get_or_create_user_stream(user)
    mark_seen(stream, object_id, activity_type)


def mark_all_seen_by_user(user: User):
    stream = Stream.get_or_create_user_stream(user)
    unread = stream.activities.filter(Activity.seen_at == None)
    unread.update(values=dict(seen_at=now()))


def get_all_activities(stream: Stream):
    return stream.activities.all()
