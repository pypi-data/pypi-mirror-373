# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import json
import sys

from enum import Enum
from typing import Iterator, List, Mapping, Optional, Sequence, Text, Type

from intersperse import intersperse
from textcompat import text_to_filesystem_str

# open() with encoding support in Py2/Py3
if sys.version_info < (3,):
    import codecs

    open_with_encoding = codecs.open
else:
    open_with_encoding = open

# urllib differences
if sys.version_info < (3,):
    from urllib2 import Request, urlopen, URLError


    def post_request_instance(url, data, headers):
        """Create POST request for Python 2.

        Args:
            url: The target URL for the request
            data: The data to be sent in the request body
            headers: Dictionary of HTTP headers

        Returns:
            Request: A configured POST request object
        """
        return Request(url, data=data, headers=headers)
else:
    from urllib.request import Request, urlopen
    from urllib.error import URLError


    def post_request_instance(url, data, headers):
        """Create POST request for Python 3.

        Args:
            url: The target URL for the request
            data: The data to be sent in the request body
            headers: Dictionary of HTTP headers

        Returns:
            Request: A configured POST request object
        """
        return Request(url, data=data, headers=headers, method=u'POST')


class Message(object):
    """Abstract base class representing a message in a conversation.

    All message types should inherit from this class and implement
    the to_json method.
    """

    def to_json(self):
        """Convert the message to JSON format.

        Returns:
            dict: A dictionary representation of the message

        Raises:
            NotImplementedError: If the method is not implemented by subclass
        """
        raise NotImplementedError


class AssistantMessage(Message):
    """Represents a message from the AI assistant.

    Attributes:
        text (Text): The content of the assistant's message
    """
    __slots__ = ('text',)

    def __new__(cls, text):
        # type: (Type[AssistantMessage], Text) -> AssistantMessage
        """Create a new AssistantMessage instance.

        Args:
            text: The text content of the assistant's message

        Returns:
            AssistantMessage: A new instance with the provided text
        """
        self = super(AssistantMessage, cls).__new__(cls)
        self.text = text
        return self

    def to_json(self):
        """Convert the assistant message to JSON format.

        Returns:
            dict: Dictionary with 'role' as 'assistant' and 'content' as the text
        """
        return {u'role': u'assistant', u'content': self.text}


class UserMessage(Message):
    """Represents a text-only message from the user.

    Attributes:
        text (Text): The content of the user's message
    """
    __slots__ = ('text',)

    def __new__(cls, text):
        # type: (Type[UserMessage], Text) -> UserMessage
        """Create a new UserMessage instance.

        Args:
            text: The text content of the user's message

        Returns:
            UserMessage: A new instance with the provided text
        """
        self = super(UserMessage, cls).__new__(cls)
        self.text = text
        return self

    def to_json(self):
        """Convert the user message to JSON format.

        Returns:
            dict: Dictionary with 'role' as 'user' and 'content' as the text
        """
        return {u'role': u'user', u'content': self.text}


class UserMessageWithImage(UserMessage):
    """Represents a user message that includes both text and an image.

    Attributes:
        text (Text): The text content of the message
        image_url (Text): URL pointing to the associated image
    """
    __slots__ = ('image_url',)

    def __new__(cls, text, url):
        # type: (Type[UserMessageWithImage], Text, Text) -> UserMessageWithImage
        """Create a new UserMessageWithImage instance.

        Args:
            text: The text content of the message
            url: URL pointing to the image

        Returns:
            UserMessageWithImage: A new instance with text and image URL
        """
        self = super(UserMessageWithImage, cls).__new__(cls, text)
        self.image_url = url
        return self

    def to_json(self):
        """Convert the message with image to JSON format.

        Returns:
            dict: Dictionary with 'role' as 'user' and 'content' as a list
                  containing both text and image_url objects
        """
        return {
            u'role': u'user',
            u'content': [
                {u'type': u'text', u'text': self.text},
                {u'type': u'image_url', u'image_url': {u'url': self.image_url}}
            ]
        }


class ExtractedFromUserMessageContentSequence(object):
    """Base class for elements extracted from user message content sequences."""
    pass


class ExtractedText(ExtractedFromUserMessageContentSequence):
    """Represents extracted text content from a user message.

    Attributes:
        text (Text): The extracted text content
    """
    __slots__ = ('text',)

    def __new__(cls, text):
        # type: (Type[ExtractedText], Text) -> ExtractedText
        """Create a new ExtractedText instance.

        Args:
            text: The extracted text content

        Returns:
            ExtractedText: A new instance with the extracted text
        """
        self = super(ExtractedText, cls).__new__(cls)
        self.text = text
        return self


class ExtractedImageURL(ExtractedFromUserMessageContentSequence):
    """Represents an extracted image URL from a user message.

    Attributes:
        image_url (Text): The extracted image URL
    """
    __slots__ = ('image_url',)

    def __new__(cls, image_url):
        # type: (Type[ExtractedImageURL], Text) -> ExtractedImageURL
        """Create a new ExtractedImageURL instance.

        Args:
            image_url: The extracted image URL

        Returns:
            ExtractedImageURL: A new instance with the image URL
        """
        self = super(ExtractedImageURL, cls).__new__(cls)
        self.image_url = image_url
        return self


class Invalid(ExtractedFromUserMessageContentSequence):
    """Represents invalid or unrecognized content in a user message."""
    pass


def extract_from_user_message_content_sequence(user_message_content_sequence):
    # type: (Sequence) -> Iterator[ExtractedFromUserMessageContentSequence]
    """Extract structured content from a user message content sequence.

    Parses a sequence of content elements from a user message and yields
    appropriate Extracted* objects for valid content types.

    Args:
        user_message_content_sequence: A sequence of content elements from a user message

    Yields:
        ExtractedFromUserMessageContentSequence: Objects representing the extracted content
        (ExtractedText, ExtractedImageURL, or Invalid for unrecognized types)
    """
    for element in user_message_content_sequence:
        if isinstance(element, Mapping):
            element_type = element.get(u'type', None)
            element_text = element.get(u'text', None)
            element_image_url = element.get(u'image_url', None)
        else:
            element_type = None
            element_text = None
            element_image_url = None

        if isinstance(element_image_url, Mapping):
            element_image_url_url = element_image_url.get(u'url', None)
        else:
            element_image_url_url = None

        if element_type == u'text':
            yield ExtractedText(element_text)
        elif element_type == u'image_url':
            yield ExtractedImageURL(element_image_url_url)
        else:
            yield Invalid()


class UserMessageContentSequenceParseState(Enum):
    """Enum representing the parsing state for user message content sequences.

    Used to track the state during parsing of complex user message content.
    """
    AFTER_USER_MESSAGE = 1
    AFTER_TEXT_CONTENT = 2


class ParseState(object):
    """Base class representing the result of parsing messages."""
    pass


class SuccessfulParse(ParseState):
    """Represents a successful parsing operation.

    Attributes:
        parsed_messages (list): List of successfully parsed Message objects
    """
    __slots__ = ('parsed_messages',)

    def __new__(cls, parsed_messages):
        """Create a new SuccessfulParse instance.

        Args:
            parsed_messages: List of successfully parsed Message objects

        Returns:
            SuccessfulParse: A new instance containing parsing results
        """
        self = super(SuccessfulParse, cls).__new__(cls)
        self.parsed_messages = list(parsed_messages)
        return self


class UnsuccessfulParse(ParseState):
    """Represents a failed parsing operation.

    Attributes:
        failed_object: The object that caused the parsing failure
    """
    __slots__ = ('failed_object',)

    def __new__(cls, failed_object):
        """Create a new UnsuccessfulParse instance.

        Args:
            failed_object: The object that could not be parsed

        Returns:
            UnsuccessfulParse: A new instance containing the failed object
        """
        self = super(UnsuccessfulParse, cls).__new__(cls)
        self.failed_object = failed_object
        return self


def parse_messages(loaded):
    # type: (object) -> ParseState
    """Parse a loaded JSON object into Message objects.

    Converts a JSON structure into a sequence of Message objects, handling
    both simple text messages and complex content sequences with images.

    Args:
        loaded: A JSON-loaded object (typically a list of message dictionaries)

    Returns:
        ParseState: SuccessfulParse with parsed messages and user message count,
                   or UnsuccessfulParse with the problematic object
    """
    parsed_messages = []
    if isinstance(loaded, Sequence):
        for element in loaded:
            if isinstance(element, dict):
                role = element.get(u'role', None)
            else:
                return UnsuccessfulParse(element)

            if role == u'user':
                content = element.get(u'content', None)

                if isinstance(content, Text):
                    parsed_messages.append(UserMessage(content))
                elif isinstance(content, Sequence):
                    parse_state = UserMessageContentSequenceParseState.AFTER_USER_MESSAGE
                    cached_text = u''  # type: Text

                    for extracted in extract_from_user_message_content_sequence(content):
                        if parse_state == UserMessageContentSequenceParseState.AFTER_USER_MESSAGE:
                            if isinstance(extracted, ExtractedText):
                                parse_state = UserMessageContentSequenceParseState.AFTER_TEXT_CONTENT
                                cached_text = extracted.text

                                continue
                            elif isinstance(extracted, ExtractedImageURL):
                                parsed_messages.append(UserMessageWithImage(cached_text, extracted.image_url))

                                parse_state = UserMessageContentSequenceParseState.AFTER_USER_MESSAGE
                                cached_text = u''

                                continue
                            else:
                                return UnsuccessfulParse(element)
                        else:
                            if isinstance(extracted, ExtractedText):
                                parsed_messages.append(UserMessage(cached_text))

                                parse_state = UserMessageContentSequenceParseState.AFTER_TEXT_CONTENT
                                cached_text = extracted.text

                                continue
                            elif isinstance(extracted, ExtractedImageURL):
                                parsed_messages.append(UserMessageWithImage(cached_text, extracted.image_url))

                                parse_state = UserMessageContentSequenceParseState.AFTER_USER_MESSAGE
                                cached_text = u''

                                continue
                            else:
                                return UnsuccessfulParse(element)

                    if parse_state != UserMessageContentSequenceParseState.AFTER_USER_MESSAGE:
                        parsed_messages.append(UserMessage(cached_text))

                        parse_state = UserMessageContentSequenceParseState.AFTER_USER_MESSAGE
                        cached_text = u''
                else:
                    return UnsuccessfulParse(element)
            elif role == u'assistant':
                # Extract content
                content = element.get(u'content', None)

                if isinstance(content, Text):
                    parsed_messages.append(AssistantMessage(content))
                else:
                    return UnsuccessfulParse(element)
            else:
                return UnsuccessfulParse(element)

        return SuccessfulParse(parsed_messages)
    else:
        return UnsuccessfulParse(loaded)


class ChatCompletionsConversation(object):
    """
    Minimalist conversation manager for LLMs providing an OpenAI Chat Completions-compatible API.

    Designed to respect model randomness and prevent engineering illusions.
    No system prompts, no parameter control.
    Just raw conversation and manual correction when needed.

    Attributes:
        api_key: API authentication key
        base_url: API endpoint base URL
        model: Model identifier
        messages: Raw conversation history
    """
    __slots__ = (
        'api_key',
        'base_url',
        'model',
        'messages'
    )

    def __init__(self, api_key, base_url, model):
        # type: (Text, Text, Text) -> None
        """
        Initialize conversation with model API details.

        Args:
            api_key: API authentication key
            base_url: API endpoint URL
            model: Model name
        """
        self.api_key = api_key  # type: Text
        self.base_url = base_url  # type: Text
        self.model = model  # type: Text
        self.messages = []  # type: List[Message]

    def to_json(self):
        json_object = []
        for message in self.messages:
            json_object.append(message.to_json())
        return json_object

    def load_from_json_file(self, json_file_path):
        # type: (Text) -> None
        """
        Load conversation from a JSON file.
        Only user and assistant roles supported. No system prompts allowed.
        """
        with open_with_encoding(text_to_filesystem_str(json_file_path), 'r', encoding='utf-8') as f:
            loaded_json_object = json.load(f)
            parse_result = parse_messages(loaded_json_object)
            if isinstance(parse_result, SuccessfulParse):
                self.messages = parse_result.parsed_messages
            else:
                raise ValueError(
                    u'Invalid JSON schema: '
                    u'Expected a list of dictionaries '
                    u'with keys "role" (value "user" or "assistant") '
                    u'and "content" (value either "<text>" or [{"type": "text", "text": "<text>"}, {"type": "image_url", "image_url": {"url": "<text>"}}]). '
                    u'Got: %r' % loaded_json_object
                )

    def save_to_json_file(self, json_file_path):
        # type: (Text) -> None
        """Save conversation to a JSON file."""
        with open_with_encoding(text_to_filesystem_str(json_file_path), 'w', encoding='utf-8') as f:
            json.dump(
                self.to_json(),
                f,
                indent=2,
                ensure_ascii=False
            )

    def export_to_text(self):
        # type: () -> Text
        """
        Export conversation to readable text.

        Returns:
            Formatted conversation with message numbers
        """
        lines = []
        user_message_counter = 0

        for message in self.messages:
            if isinstance(message, AssistantMessage):
                lines += [u'%s [%i]:' % (u'Assistant', user_message_counter), message.text]
            else:
                user_message_counter += 1

                lines += [u'%s [%i]:' % (u'User', user_message_counter)]

                if message.text:
                    lines += [message.text]

                if isinstance(message, UserMessageWithImage):
                    lines += [u"<img src='%s' />" % (message.image_url,)]

        return u'\n'.join(intersperse(lines, u''))

    def create_user_message(self, text, image_url=None):
        # type: (Text, Optional[Text]) -> None
        """Create a user message and add to the model's message list without obtaining a response."""
        if image_url is not None:
            message = UserMessageWithImage(text, image_url)
        else:
            message = UserMessage(text)

        self.messages.append(message)

    def create_user_message_and_stream_response(self, text, image_url=None):
        # type: (Text, Optional[Text]) -> Iterator[Text]
        """
        Create a user message, add to the model's message list, send conversation to model, and stream response as it emerges.

        Yields:
            Response chunks as generated by the model
        """
        if image_url is not None:
            message = UserMessageWithImage(text, image_url)
        else:
            message = UserMessage(text)

        self.messages.append(message)

        exception_occurred = False
        try:
            url = u'%s/chat/completions' % self.base_url
            headers = {
                u'Content-Type': u'application/json',
                u'Authorization': u'Bearer %s' % self.api_key
            }
            data = json.dumps({u'model': self.model, u'messages': self.to_json(), u'stream': True}).encode('utf-8')
            req = post_request_instance(url, data=data, headers=headers)
            response = urlopen(req)

            contents = []
            for line in response:
                if line.startswith(b'data: '):
                    chunk_data = line[6:].decode('utf-8').strip()  # Remove "data: " prefix
                    if chunk_data == u'[DONE]':
                        break

                    chunk = json.loads(chunk_data)
                    content = chunk.get(u'choices', [{}])[0].get(u'delta', {}).get(u'content', u'') or u''
                    contents.append(content)
                    yield content

            self.messages.append(AssistantMessage(u''.join(contents)))
        except Exception:
            exception_occurred = True
            raise
        finally:
            if exception_occurred:
                self.messages.pop()

    def create_user_message_and_obtain_response(self, text, image_url=None):
        # type: (Text, Optional[Text]) -> Text
        """
        Create a user message, add to the model's message list, send conversation to model, and obtain response.
        """
        chunks = []
        for chunk in self.create_user_message_and_stream_response(text, image_url):
            chunks.append(chunk)
        return u''.join(chunks)

    def correct_last_response(self, corrected_response):
        # type: (Text) -> bool
        """
        Correct the last assistant response manually.

        Returns:
            True if correction successful, False if no assistant response to correct
        """
        if self.messages:
            original_last_message = self.messages[-1]
            if isinstance(original_last_message, AssistantMessage):
                self.messages[-1] = AssistantMessage(corrected_response)
                return True
        return False
