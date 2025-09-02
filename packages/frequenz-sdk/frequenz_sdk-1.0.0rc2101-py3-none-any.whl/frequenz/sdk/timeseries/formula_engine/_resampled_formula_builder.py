# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""A builder for creating formula engines that operate on resampled component metrics."""

from __future__ import annotations

from collections.abc import Callable

from frequenz.channels import Receiver, Sender
from frequenz.client.common.microgrid.components import ComponentId
from frequenz.client.microgrid import ComponentMetricId
from frequenz.quantities import Quantity

from ..._internal._channels import ChannelRegistry
from ...microgrid._data_sourcing import ComponentMetricRequest
from .._base_types import QuantityT, Sample
from ._formula_engine import FormulaBuilder, FormulaEngine
from ._formula_steps import FallbackMetricFetcher
from ._tokenizer import Tokenizer, TokenType


class ResampledFormulaBuilder(FormulaBuilder[QuantityT]):
    """Provides a way to build a FormulaEngine from resampled data streams."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        namespace: str,
        formula_name: str,
        channel_registry: ChannelRegistry,
        resampler_subscription_sender: Sender[ComponentMetricRequest],
        metric_id: ComponentMetricId,
        create_method: Callable[[float], QuantityT],
    ) -> None:
        """Create a `ResampledFormulaBuilder` instance.

        Args:
            namespace: The unique namespace to allow reuse of streams in the data
                pipeline.
            formula_name: A name for the formula.
            channel_registry: The channel registry instance shared with the resampling
                and the data sourcing actors.
            resampler_subscription_sender: A sender to send metric requests to the
                resampling actor.
            metric_id: A metric ID to fetch for all components in this formula.
            create_method: A method to generate the output `Sample` value with.  If the
                formula is for generating power values, this would be
                `Power.from_watts`, for example.
        """
        self._channel_registry: ChannelRegistry = channel_registry
        self._resampler_subscription_sender: Sender[ComponentMetricRequest] = (
            resampler_subscription_sender
        )
        self._namespace: str = namespace
        self._metric_id: ComponentMetricId = metric_id
        self._resampler_requests: list[ComponentMetricRequest] = []
        super().__init__(formula_name, create_method)

    def _get_resampled_receiver(
        self, component_id: ComponentId, metric_id: ComponentMetricId
    ) -> Receiver[Sample[QuantityT]]:
        """Get a receiver with the resampled data for the given component id.

        Args:
            component_id: The component id for which to get a resampled data receiver.
            metric_id: A metric ID to fetch for all components in this formula.

        Returns:
            A receiver to stream resampled data for the given component id.
        """
        request = ComponentMetricRequest(self._namespace, component_id, metric_id, None)
        self._resampler_requests.append(request)
        resampled_channel = self._channel_registry.get_or_create(
            Sample[Quantity], request.get_channel_name()
        )
        resampled_receiver = resampled_channel.new_receiver().map(
            lambda sample: Sample(
                sample.timestamp,
                (
                    self._create_method(sample.value.base_value)
                    if sample.value is not None
                    else None
                ),
            )
        )
        return resampled_receiver

    async def subscribe(self) -> None:
        """Subscribe to all resampled component metric streams."""
        for request in self._resampler_requests:
            await self._resampler_subscription_sender.send(request)

    def push_component_metric(
        self,
        component_id: ComponentId,
        *,
        nones_are_zeros: bool,
        fallback: FallbackMetricFetcher[QuantityT] | None = None,
    ) -> None:
        """Push a resampled component metric stream to the formula engine.

        Args:
            component_id: The component id for which to push a metric fetcher.
            nones_are_zeros: Whether to treat None values from the stream as 0s.  If
                False, the returned value will be a None.
            fallback: Metric fetcher to use if primary one start sending
                invalid data (e.g. due to a component stop). If None the data from
                primary metric fetcher will be returned.
        """
        receiver = self._get_resampled_receiver(component_id, self._metric_id)
        self.push_metric(
            f"#{int(component_id)}",
            receiver,
            nones_are_zeros=nones_are_zeros,
            fallback=fallback,
        )

    def from_string(
        self,
        formula: str,
        *,
        nones_are_zeros: bool,
    ) -> FormulaEngine[QuantityT]:
        """Construct a `FormulaEngine` from the given formula string.

        Formulas can have Component IDs that are preceeded by a pound symbol("#"), and
        these operators: +, -, *, /, (, ).

        For example, the input string: "#20 + #5" is a formula for adding metrics from
        two components with ids 20 and 5.

        Args:
            formula: A string formula.
            nones_are_zeros: Whether to treat None values from the stream as 0s.  If
                False, the returned value will be a None.

        Returns:
            A FormulaEngine instance corresponding to the given formula.

        Raises:
            ValueError: when there is an unknown token type.
        """
        tokenizer = Tokenizer(formula)

        for token in tokenizer:
            if token.type == TokenType.COMPONENT_METRIC:
                self.push_component_metric(
                    ComponentId(int(token.value)), nones_are_zeros=nones_are_zeros
                )
            elif token.type == TokenType.OPER:
                self.push_oper(token.value)
            else:
                raise ValueError(f"Unknown token type: {token}")

        return self.build()
