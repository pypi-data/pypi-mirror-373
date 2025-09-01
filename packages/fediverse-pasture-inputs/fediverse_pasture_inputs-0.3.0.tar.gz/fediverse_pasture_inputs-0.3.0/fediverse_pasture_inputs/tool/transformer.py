"""
Helper class to create object and activity from examples
"""

from unittest.mock import AsyncMock, MagicMock
from bovine.testing import actor

from fediverse_pasture.runner import ActivitySender


def activity_sender():
    aactor = MagicMock()
    aactor.id = actor["id"]
    aactor.build = MagicMock(return_value=actor)
    bovine_actor = AsyncMock()
    bovine_actor.get = AsyncMock(return_value={"inbox": "inbox"})
    sender = ActivitySender.for_actor(bovine_actor, aactor)
    sender.sleep_after_getting_inbox = False
    return sender


class ExampleTransformer:
    """Class to create objects and activities from
    examples"""

    def __init__(self):
        self.sender = activity_sender()

    async def init_sender_for_example(self, example):
        self.sender.init_create_note(lambda x: {**x, **example})
        await self.sender.send("http://remote.example/")

    async def create_object(self, example):
        """Creates the sample object

        ```pycon
        >>> import asyncio
        >>> et = ExampleTransformer()
        >>> asyncio.run(et.create_object({"content": "moo"}))
        {'type': 'Note',
            'attributedTo': 'http://actor.example',
            'to': ['https://www.w3.org/ns/activitystreams#Public'],
            'id': 'http://actor.example/...',
            'published': '...',
            'content': 'moo',
            '@context': ['https://www.w3.org/ns/activitystreams',
                {'Hashtag': 'as:Hashtag', 'sensitive': 'as:sensitive'}]}

        ```
        """
        await self.init_sender_for_example(example)
        obj = self.sender.note

        if obj is None:
            raise Exception("Failed ot created note")

        if "@context" not in obj:
            obj["@context"] = [
                "https://www.w3.org/ns/activitystreams",
                {"Hashtag": "as:Hashtag", "sensitive": "as:sensitive"},
            ]
        return obj

    async def create_activity(self, example):
        """Creates the sample activity

        ```pycon
        >>> import asyncio
        >>> et = ExampleTransformer()
        >>> asyncio.run(et.create_activity({"content": "moo"}))
        {'@context': ['https://www.w3.org/ns/activitystreams',
            {'Hashtag': 'as:Hashtag', 'sensitive': 'as:sensitive'}],
            'type': 'Create',
            'actor': 'http://actor.example',
            'to': [...],
            'id': 'http://actor.example/...',
            'published': '...',
            'object': {'type': 'Note',
                'attributedTo': 'http://actor.example',
                'to': ['https://www.w3.org/ns/activitystreams#Public', 'http://remote.example/'],
                'id': 'http://actor.example/...',
                'published': '...',
                'content': 'moo'}}

        ```
        """
        await self.init_sender_for_example(example)
        return self.sender.activity
