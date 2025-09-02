import warnings

from pydantic import BaseModel

from bigdata_client import Bigdata


class TraceEvent(BaseModel):
    event_name: str
    properties: dict


def send_trace(bigdata_client: Bigdata, trace: TraceEvent):
    """
    Send a trace to the Bigdata client.
    """
    try:
        bigdata_client._api.send_tracking_event(trace)
    except Exception as e:
        warnings.warn(f"Could not send trace. Reason {e}")
