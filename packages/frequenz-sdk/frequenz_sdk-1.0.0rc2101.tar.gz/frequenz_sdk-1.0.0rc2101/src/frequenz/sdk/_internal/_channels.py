# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""General purpose classes for use with channels."""

import abc
import dataclasses
import logging
import traceback
import typing

from frequenz.channels import Broadcast, Receiver

_logger = logging.getLogger(__name__)

T_co = typing.TypeVar("T_co", covariant=True)
U_co = typing.TypeVar("U_co", covariant=True)
T = typing.TypeVar("T")


class ReceiverFetcher(typing.Generic[T_co], typing.Protocol):
    """An interface that just exposes a `new_receiver` method."""

    @abc.abstractmethod
    def new_receiver(self, *, limit: int = 50) -> Receiver[T_co]:
        """Get a receiver from the channel.

        Args:
            limit: The maximum size of the receiver.

        Returns:
            A receiver instance.
        """


class MappingReceiverFetcher(typing.Generic[T_co, U_co]):
    """A receiver fetcher that can manipulate receivers before returning them."""

    def __init__(
        self,
        fetcher: ReceiverFetcher[T_co],
        mapping_function: typing.Callable[[Receiver[T_co]], Receiver[U_co]],
    ) -> None:
        """Initialize this instance.

        Args:
            fetcher: The underlying fetcher to get receivers from.
            mapping_function: The method to be applied on new receivers before returning
                them.
        """
        self._fetcher = fetcher
        self._mapping_function = mapping_function

    def new_receiver(self, *, limit: int = 50) -> Receiver[U_co]:
        """Get a receiver from the channel.

        Args:
            limit: The maximum size of the receiver.

        Returns:
            A receiver instance.
        """
        return self._mapping_function(self._fetcher.new_receiver(limit=limit))


class ChannelRegistry:
    """Dynamically creates, own and provide access to broadcast channels.

    It can be used by actors to dynamically establish a communication channel
    between each other.

    The registry is responsible for creating channels when they are first requested via
    the [`get_or_create()`][frequenz.sdk.actor.ChannelRegistry.get_or_create] method.

    The registry also stores type information to make sure that the same channel is not
    used for different message types.

    Since the registry owns the channels, it is also responsible for closing them when
    they are no longer needed. There is no way to remove a channel without closing it.

    Note:
        This registry stores [`Broadcast`][frequenz.channels.Broadcast] channels.
    """

    def __init__(self, *, name: str) -> None:
        """Initialize this registry.

        Args:
            name: A name to identify the registry in the logs. This name is also used as
                a prefix for the channel names.
        """
        self._name = name
        self._channels: dict[str, _Entry] = {}

    @property
    def name(self) -> str:
        """The name of this registry."""
        return self._name

    def message_type(self, key: str) -> type:
        """Get the message type of the channel for the given key.

        Args:
            key: The key to identify the channel.

        Returns:
            The message type of the channel.

        Raises:
            KeyError: If the channel does not exist.
        """
        entry = self._channels.get(key)
        if entry is None:
            raise KeyError(f"No channel for key {key!r} exists.")
        return entry.message_type

    def __contains__(self, key: str) -> bool:
        """Check whether the channel for the given `key` exists."""
        return key in self._channels

    def get_or_create(self, message_type: type[T], key: str) -> Broadcast[T]:
        """Get or create a channel for the given key.

        If a channel for the given key already exists, the message type of the existing
        channel is checked against the requested message type. If they do not match,
        a `ValueError` is raised.

        Note:
            The types have to match exactly, it doesn't do a subtype check due to
            technical limitations. In the future subtype checks might be supported.

        Args:
            message_type: The type of the message that is sent through the channel.
            key: The key to identify the channel.

        Returns:
            The channel for the given key.

        Raises:
            ValueError: If the channel exists and the message type does not match.
        """
        if key not in self._channels:
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug(
                    "Creating a new channel for key %r with type %s at:\n%s",
                    key,
                    message_type,
                    "".join(traceback.format_stack(limit=10)[:9]),
                )
            self._channels[key] = _Entry(
                message_type, Broadcast(name=f"{self._name}-{key}")
            )

        entry = self._channels[key]
        if entry.message_type is not message_type:
            error_message = (
                f"Type mismatch, a channel for key {key!r} exists and the requested "
                f"message type {message_type} is not the same as the existing "
                f"message type {entry.message_type}."
            )
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug(
                    "%s at:\n%s",
                    error_message,
                    # We skip the last frame because it's this method, and limit the
                    # stack to 9 frames to avoid adding too much noise.
                    "".join(traceback.format_stack(limit=10)[:9]),
                )
            raise ValueError(error_message)

        return typing.cast(Broadcast[T], entry.channel)

    async def close_and_remove(self, key: str) -> None:
        """Remove the channel for the given key.

        Args:
            key: The key to identify the channel.

        Raises:
            KeyError: If the channel does not exist.
        """
        entry = self._channels.pop(key, None)
        if entry is None:
            raise KeyError(f"No channel for key {key!r} exists.")
        await entry.channel.close()


@dataclasses.dataclass(frozen=True)
class _Entry:
    """An entry in a channel registry."""

    message_type: type
    """The type of the message that is sent through the channel in this entry."""

    # We use object instead of Any to minimize the chances of hindering type checking.
    # If for some reason the channel is not casted to the proper underlaying type, when
    # using object at least accessing any member that's not part of the object base
    # class will yield a type error, while if we used Any, it would not and the issue
    # would be much harder to find.
    channel: Broadcast[object]
    """The channel in this entry."""
