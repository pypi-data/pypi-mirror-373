# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Interactions with pools of EV Chargers."""


import asyncio
import uuid
from collections import abc

from frequenz.client.common.microgrid.components import ComponentId
from frequenz.quantities import Current, Power

from ..._internal._channels import MappingReceiverFetcher, ReceiverFetcher
from ...microgrid import _power_distributing, _power_managing
from ...timeseries import Bounds
from .._base_types import SystemBounds
from ..formula_engine import FormulaEngine, FormulaEngine3Phase
from ..formula_engine._formula_generators import (
    EVChargerCurrentFormula,
    EVChargerPowerFormula,
    FormulaGeneratorConfig,
)
from ._ev_charger_pool_reference_store import EVChargerPoolReferenceStore
from ._result_types import EVChargerPoolReport


class EVChargerPoolError(Exception):
    """An error that occurred in any of the EVChargerPool methods."""


class EVChargerPool:
    """An interface for interaction with pools of EV Chargers.

    Provides:
      - Aggregate [`power`][frequenz.sdk.timeseries.ev_charger_pool.EVChargerPool.power]
        and
        [`current_per_phase`][frequenz.sdk.timeseries.ev_charger_pool.EVChargerPool.current_per_phase]
        measurements of the EV Chargers in the pool.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        pool_ref_store: EVChargerPoolReferenceStore,
        name: str | None,
        priority: int,
    ) -> None:
        """Create an `EVChargerPool` instance.

        !!! note

            `EVChargerPool` instances are not meant to be created directly by users. Use
            the
            [`microgrid.new_ev_charger_pool`][frequenz.sdk.microgrid.new_ev_charger_pool]
            method for creating `EVChargerPool` instances.

        Args:
            pool_ref_store: The EV charger pool reference store instance.
            name: An optional name used to identify this instance of the pool or a
                corresponding actor in the logs.
            priority: The priority of the actor using this wrapper.
        """
        self._pool_ref_store = pool_ref_store
        unique_id = str(uuid.uuid4())
        self._source_id = unique_id if name is None else f"{name}-{unique_id}"
        self._priority = priority

    async def propose_power(
        self,
        power: Power | None,
        *,
        bounds: Bounds[Power | None] = Bounds(None, None),
    ) -> None:
        """Send a proposal to the power manager for the pool's set of EV chargers.

        This proposal is for the maximum power that can be set for the EV chargers in
        the pool.  The actual consumption might be lower based on the number of phases
        an EV is drawing power from, and its current state of charge.

        Details on how the power manager handles proposals can be found in the
        [Microgrid][frequenz.sdk.microgrid--setting-power] documentation.

        Args:
            power: The power to propose for the EV chargers in the pool.  If `None`,
                this proposal will not have any effect on the target power, unless
                bounds are specified.  When specified without bounds, bounds for lower
                priority actors will be shifted by this power.  If both are `None`, it
                is equivalent to not having a proposal or withdrawing a previous one.
            bounds: The power bounds for the proposal. When specified, these bounds will
                limit the bounds for lower priority actors.

        Raises:
            EVChargerPoolError: If a discharge power for EV chargers is requested.
        """
        if power is not None and power < Power.zero():
            raise EVChargerPoolError(
                "Discharging from EV chargers is currently not supported."
            )
        await self._pool_ref_store.power_manager_requests_sender.send(
            _power_managing.Proposal(
                source_id=self._source_id,
                preferred_power=power,
                bounds=bounds,
                component_ids=self._pool_ref_store.component_ids,
                priority=self._priority,
                creation_time=asyncio.get_running_loop().time(),
            )
        )

    @property
    def component_ids(self) -> abc.Set[ComponentId]:
        """Return component IDs of all EV Chargers managed by this EVChargerPool.

        Returns:
            Set of managed component IDs.
        """
        return self._pool_ref_store.component_ids

    @property
    def current_per_phase(self) -> FormulaEngine3Phase[Current]:
        """Fetch the total current for the EV Chargers in the pool.

        This formula produces values that are in the Passive Sign Convention (PSC).

        If a formula engine to calculate EV Charger current is not already running, it
        will be started.

        A receiver from the formula engine can be created using the `new_receiver`
        method.

        Returns:
            A FormulaEngine that will calculate and stream the total current of all EV
                Chargers.
        """
        engine = (
            self._pool_ref_store.formula_pool.from_3_phase_current_formula_generator(
                "ev_charger_total_current",
                EVChargerCurrentFormula,
                FormulaGeneratorConfig(
                    component_ids=self._pool_ref_store.component_ids
                ),
            )
        )
        assert isinstance(engine, FormulaEngine3Phase)
        return engine

    @property
    def power(self) -> FormulaEngine[Power]:
        """Fetch the total power for the EV Chargers in the pool.

        This formula produces values that are in the Passive Sign Convention (PSC).

        If a formula engine to calculate EV Charger power is not already running, it
        will be started.

        A receiver from the formula engine can be created using the `new_receiver`
        method.

        Returns:
            A FormulaEngine that will calculate and stream the total power of all EV
                Chargers.
        """
        engine = self._pool_ref_store.formula_pool.from_power_formula_generator(
            "ev_charger_power",
            EVChargerPowerFormula,
            FormulaGeneratorConfig(
                component_ids=self._pool_ref_store.component_ids,
            ),
        )
        assert isinstance(engine, FormulaEngine)
        return engine

    @property
    def power_status(self) -> ReceiverFetcher[EVChargerPoolReport]:
        """Get a receiver to receive new power status reports when they change.

        These include
          - the current inclusion/exclusion bounds available for the pool's priority,
          - the current target power for the pool's set of batteries,
          - the result of the last distribution request for the pool's set of batteries.

        Returns:
            A receiver that will stream power status reports for the pool's priority.
        """
        sub = _power_managing.ReportRequest(
            source_id=self._source_id,
            priority=self._priority,
            component_ids=self._pool_ref_store.component_ids,
        )
        self._pool_ref_store.power_bounds_subs[sub.get_channel_name()] = (
            asyncio.create_task(
                self._pool_ref_store.power_manager_bounds_subs_sender.send(sub)
            )
        )
        channel = self._pool_ref_store.channel_registry.get_or_create(
            _power_managing._Report,  # pylint: disable=protected-access
            sub.get_channel_name(),
        )
        channel.resend_latest = True

        return channel

    @property
    def power_distribution_results(self) -> ReceiverFetcher[_power_distributing.Result]:
        """Get a receiver to receive power distribution results.

        Returns:
            A receiver that will stream power distribution results for the pool's set of
            EV chargers.
        """
        return MappingReceiverFetcher(
            self._pool_ref_store.power_distribution_results_fetcher,
            lambda recv: recv.filter(
                lambda x: x.request.component_ids == self._pool_ref_store.component_ids
            ),
        )

    async def stop(self) -> None:
        """Stop all tasks and channels owned by the EVChargerPool."""
        # This was closing the pool_ref_store, which is not correct, because those are
        # shared.
        #
        # This method will do until we have a mechanism to track the resources created
        # through it.  It can also eventually cleanup the pool_ref_store, when it is
        # holding the last reference to it.

    @property
    def _system_power_bounds(self) -> ReceiverFetcher[SystemBounds]:
        """Return a receiver fetcher for the system power bounds."""
        return self._pool_ref_store.bounds_channel
