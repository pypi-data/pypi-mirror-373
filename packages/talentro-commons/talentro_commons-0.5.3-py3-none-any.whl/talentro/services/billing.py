import json
from datetime import datetime
from functools import wraps
from http import HTTPStatus

from ..event import Message, Queue, Event
from ..services.rabbitmq import QueueContext
from ..constants import ErrorCode, DisplayMessage, SKU
from ..exceptions import APIException


def billable_event(sku: SKU, meta_data=None):

    if meta_data is None:
        meta_data = {}

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not kwargs.get("x_organization_id"):
                raise APIException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    message="No organization provided",
                    error_code=ErrorCode.BAD_REQUEST,
                    display_message=DisplayMessage.BAD_REQUEST,
                )

            result = func(*args, **kwargs)

            organization_id = kwargs.get("x_organization_id")

            await send_billing_event(sku, organization_id, 1, meta_data)
            return result

        return wrapper

    return decorator


async def send_billing_event(sku: SKU, organization_id: str, count: int = 1, meta_data=None):
    # Send message to billing queue
    context: QueueContext = QueueContext()

    event = Event(
        event_type='billing.event',
        payload={
            "sku": sku,
            "count": count,
            "organization_id": organization_id,
            "meta_data": json.dumps(meta_data),
        },
        created_on=datetime.now(),
    )

    message = Message(
        queue=Queue.billing,
        event=event
    )

    await context.send_message(message)
    print(f"[Billing] Billed event with sku: '{sku}' x {count} usages.")
