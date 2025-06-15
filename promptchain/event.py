
from collections import defaultdict
from typing import List, Callable, Dict, Any, Union
from pydantic import BaseModel, Field
from promptchain.message import Message

from rich.console import Console
console = Console()

# --- Event System ---
# Default value of the dictionary will be a list of Callables
subscribers = defaultdict(list)

def subscribe(event_type: str, fn: Callable[[Dict[str, Any]], None]):
    """
    Subscribes a function to a specific event type.
    The function will receive a dictionary containing 'message' and 'context'.
    """
    subscribers[event_type].append(fn)
    console.print(f"Subscribed function {fn.__name__} to event type: '{event_type}'")

def send_event(event_type: str, data: Dict[str, Any]):
    """
    Sends an event with associated data to all subscribed functions for that event type.
    Data should typically include 'message' and 'context'.
    """
    if not event_type in subscribers:
        # print(f"No subscribers for event type: '{event_type}'")
        return
    for fn in subscribers[event_type]:
        try:
            fn(data)
            # print(f"Sent event '{event_type}' to {fn.__name__}")
        except Exception as e:
            print(f"Error sending event '{event_type}' to {fn.__name__}: {e}")

# --- Event Class as a Chain Node ---
class Event(BaseModel):
    """
    Represents an event node in a chain. When invoked, it sends messages and context
    to its subscribers. Supports conditional triggering.
    """
    event_type: str
    # A condition function that takes message and context, returns True to trigger
    # Default is always True (unconditional trigger)
    condition: Callable[[Message, Dict[str, Any]], bool] = Field(default_factory=lambda: (lambda msg, ctx: True))
    
    class Config:
        arbitrary_types_allowed = True # Allow Callable types

    def invoke(self, message: Message, context: Dict[str, Any]):
        """
        Invokes the event node. It checks the condition and, if met,
        sends the message and current context to all subscribers of its event_type.
        
        Args:
            message (Message): The current message being processed in the chain.
            context (Dict[str, Any]): The current state/context of the chain.
        """
        if self.condition(message, context):
            # print(f"Event '{self.event_type}' condition met. Sending event...")
            send_event(self.event_type, {"message": message.model_dump(), "context": context})
        # else:
            # print(f"Event '{self.event_type}' condition not met. Event not sent.")

    def __str__(self):
        return f"Event(type='{self.event_type}', conditional={'Yes' if self.condition.__name__ != '<lambda>' else 'No'})"

    def __repr__(self):
        return self.__str__()