import pytest
from promptchain.message import Message, AIMessage, HumanMessage, SystemMessage, Messages
from pydantic import ValidationError # Import ValidationError for Pydantic-specific errors

# Test cases for individual Message types
def test_message_creation():
    message = Message(role="user", content="write hello world in python")
    assert message.role == "user"
    assert message.content == "write hello world in python"

def test_ai_message_creation():
    ai_message = AIMessage(content="You are a very helpful assistant.")
    assert ai_message.role == "assistant"
    assert ai_message.content == "You are a very helpful assistant."

def test_human_message_creation():
    user_message = HumanMessage(content="Write code to read a CSV file in Python.")
    assert user_message.role == "user"
    assert user_message.content == "Write code to read a CSV file in Python."

def test_system_message_creation():
    system_message = SystemMessage(content="You are a code generation assistant.")
    assert system_message.role == "system"
    assert system_message.content == "You are a code generation assistant."

# Test cases for Messages class
def test_messages_initialization():
    ai_message = AIMessage(content="Hello.")
    user_message = HumanMessage(content="Hi there.")
    messages_initial = Messages(messages=[ai_message, user_message])
    assert len(messages_initial.messages) == 2
    assert messages_initial.messages[0].role == "assistant"
    assert messages_initial.messages[1].role == "user"

def test_add_message_with_message_object():
    messages = Messages()
    system_message = SystemMessage(content="You are a code generation assistant.")
    messages.add_message(system_message)
    assert len(messages.messages) == 1
    assert messages.messages[0].role == "system"
    assert messages.messages[0].content == "You are a code generation assistant."

def test_add_message_with_dictionary_input():
    messages = Messages()
    messages.add_message({"role": "user", "content": "Tell me a joke."})
    messages.add_message({"role": "assistant", "content": "Why don't scientists trust atoms? Because they make up everything!"})
    assert len(messages.messages) == 2
    assert messages.messages[0].role == "user"
    assert messages.messages[1].role == "assistant"

def test_add_operator_with_message_object():
    messages = Messages()
    new_messages = messages + SystemMessage(content="Be concise.")
    assert len(new_messages.messages) == 1
    assert new_messages.messages[0].role == "system"
    # Ensure original messages object is not modified
    assert len(messages.messages) == 0

def test_add_operator_with_dictionary_input():
    messages = Messages()
    new_messages = messages + {"role": "user", "content": "What's the weather like?"}
    assert len(new_messages.messages) == 1
    assert new_messages.messages[0].role == "user"
    assert new_messages.messages[0].content == "What's the weather like?"

def test_add_operator_with_list_of_mixed_inputs():
    messages = Messages()
    new_messages = messages + [
        SystemMessage(content="Act as a friendly chatbot."),
        {"role": "user", "content": "How are you today?"},
        AIMessage(content="I'm doing great, thanks for asking!"),
        {"role": "user", "content": "That's good to hear!"}
    ]
    assert len(new_messages.messages) == 4
    assert new_messages.messages[0].role == "system"
    assert new_messages.messages[1].content == "How are you today?"
    assert new_messages.messages[2].role == "assistant"
    assert new_messages.messages[3].content == "That's good to hear!"

def test_chaining_add_operations():
    chained_messages = Messages() \
        + SystemMessage(content="You are a helpful assistant.") \
        + {"role": "user", "content": "Can you summarize this text?"} \
        + AIMessage(content="Sure, I can help with that.")
    assert len(chained_messages.messages) == 3
    assert chained_messages.messages[0].role == "system"
    assert chained_messages.messages[1].role == "user"
    assert chained_messages.messages[2].role == "assistant"

# Test cases for error handling
def test_add_message_invalid_dictionary_input():
    messages = Messages()
    with pytest.raises(ValueError, match="Invalid dictionary format for Message"):
        messages.add_message({"rol": "user", "contents": "bad input"}) # Typo in role and content

def test_add_operator_invalid_dictionary_role():
    messages = Messages()
    with pytest.raises(ValueError, match="Invalid dictionary format for Message"):
        messages + {"role": "invalid", "content": "wrong role"} # Invalid literal for role

def test_messages_creation_with_invalid_message_list():
    with pytest.raises(ValidationError): # Pydantic will raise ValidationError for list items
        Messages(messages=[{"role": "user", "contents": "invalid"}, "not a message"])

def test_add_message_unsupported_type():
    messages = Messages()
    with pytest.raises(TypeError, match="Unsupported message type"):
        messages.add_message("this is a string, not a message")

def test_add_operator_unsupported_type():
    messages = Messages()
    with pytest.raises(TypeError, match="Unsupported message type"):
        messages + 123 # Adding an integer