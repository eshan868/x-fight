import secrets
import uuid

from django.core.cache import cache


CALL_TIMEOUT = 3600


def create_call(
    caller_id,
    receiver_id,
    gamemate_id,
    chatroom_name,
    call_type="video",
):
    call_id = uuid.uuid4().hex

    room_id = (
        f"gamearena_{secrets.token_urlsafe(18)}"
    )

    call_data = {
        "call_id": call_id,
        "caller_id": int(caller_id),
        "receiver_id": int(receiver_id),
        "gamemate_id": int(gamemate_id),
        "chatroom_name": chatroom_name,
        "room_id": room_id,
        "call_type": call_type,
        "status": "ringing",
    }

    cache.set(
        f"call:{call_id}",
        call_data,
        timeout=CALL_TIMEOUT,
    )

    return call_data


def get_call(call_id):
    return cache.get(f"call:{call_id}")


def update_call(call_id, **updates):
    call_data = get_call(call_id)

    if not call_data:
        return None

    call_data.update(updates)

    cache.set(
        f"call:{call_id}",
        call_data,
        timeout=CALL_TIMEOUT,
    )

    return call_data


def delete_call(call_id):
    cache.delete(f"call:{call_id}")