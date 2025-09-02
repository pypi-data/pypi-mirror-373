# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""A {{glossary("microgrid")}} is a local electrical grid that connects a set of
electrical components together.  They are often built around a passive power consumer,
to supplement the electricity consumed from the {{glossary("grid", "public grid")}} with
on-site power generation or storage systems.

Microgrids can also function in {{glossary("island", "island-mode")}}, without a grid
connection, or without a local power consumer, but they have to have at least one of the
two, to be meaningful.

## Frequenz SDK Microgrid Model

The SDK aims to provide an abstract model of the microgrid that enables high-level
interactions with {{glossary("component", "microgrid components")}}, without having to
worry about (or even be aware of) location-specific details such as:

- where the {{glossary("meter", "meters")}} are placed,
- how many {{glossary("battery", "batteries")}},
- whether there's a grid connection or a passive consumer,
- what models the {{glossary("inverter", "inverters")}} are, etc.
- whether components are having downtimes, because {{glossary("metric", "metrics")}} and
  limits get adjusted automatically when components are having downtimes.

Users of the SDK can develop applications around this interface once and deploy
anywhere, and the SDK will take care of translating the requests and instructions to
correspond to the specific microgrid configurations.

``` mermaid
flowchart LR

subgraph Left[Measurements only]
direction LR
  grid["Grid Connection"]
  consumer["Consumer"]
  pv["PV Arrays"]
  chp["CHP"]
end

junction(( ))

subgraph Right[Measurements and control]
direction LR
  bat["Batteries"]
  ev["EV Chargers"]
end

grid --- junction
consumer --- junction
pv --- junction
chp --- junction

junction --- bat
junction --- ev
```

## Grid

This refers to a microgrid's connection to the external Grid.  The power flowing through
this connection can be streamed through
[`grid_power`][frequenz.sdk.timeseries.grid.Grid.power].

In locations without a grid connection, this method remains accessible, and streams zero
values.

## Consumer

This is the main power consumer at the site of a microgrid, and often the
{{glossary("load")}} the microgrid is built to support.  The power drawn by the consumer
is available through [`consumer_power`][frequenz.sdk.timeseries.consumer.Consumer.power]

In locations without a consumer, this method streams zero values.

## Producers: PV Arrays, CHP

The total CHP production in a site can be streamed through
[`chp_power`][frequenz.sdk.timeseries.logical_meter.LogicalMeter.chp_power].  PV Power
is available through the PV pool described below.  And total producer power is available
through [`microgrid.producer().power`][frequenz.sdk.timeseries.producer.Producer.power].

As is the case with the other methods, if PV Arrays or CHPs are not available in a
microgrid, the corresponding methods stream zero values.

## PV Arrays

The total PV power production is available through
[`pv_pool`][frequenz.sdk.microgrid.new_pv_pool]'s
[`power`][frequenz.sdk.timeseries.pv_pool.PVPool.power].  The PV pool by default uses
all PV inverters available at a location, but PV pool instances can be created for
subsets of PV inverters if necessary, by specifying the inverter ids.

The `pv_pool` also provides available power bounds through the
[`power_status`][frequenz.sdk.timeseries.pv_pool.PVPool.power_status] method.

The `pv_pool` also provides a control method
[`propose_power`][frequenz.sdk.timeseries.pv_pool.PVPool.propose_power], which accepts
values in the {{glossary("psc", "Passive Sign Convention")}} and supports only
production.


## Batteries

The total Battery power is available through the
[`battery_pool`][frequenz.sdk.microgrid.new_battery_pool]'s
[`power`][frequenz.sdk.timeseries.battery_pool.BatteryPool.power].  The battery pool by
default uses all batteries available at a location, but battery pool instances can be
created for subsets of batteries if necessary, by specifying the battery ids.

The `battery_pool` also provides
[`soc`][frequenz.sdk.timeseries.battery_pool.BatteryPool.soc],
[`capacity`][frequenz.sdk.timeseries.battery_pool.BatteryPool.capacity],
[`temperature`][frequenz.sdk.timeseries.battery_pool.BatteryPool.temperature] and
available power bounds through the
[`power_status`][frequenz.sdk.timeseries.battery_pool.BatteryPool.power_status] method.

The `battery_pool` also provides control methods
[`propose_power`][frequenz.sdk.timeseries.battery_pool.BatteryPool.propose_power] (which
accepts values in the {{glossary("psc", "Passive Sign Convention")}} and supports both
charging and discharging), or through
[`propose_charge`][frequenz.sdk.timeseries.battery_pool.BatteryPool.propose_charge], or
[`propose_discharge`][frequenz.sdk.timeseries.battery_pool.BatteryPool.propose_discharge].

## EV Chargers

The [`ev_charger_pool`][frequenz.sdk.microgrid.new_ev_charger_pool] offers a
[`power`][frequenz.sdk.timeseries.ev_charger_pool.EVChargerPool.power] method that
streams the total power measured for all the {{glossary("ev-charger", "EV Chargers")}}
at a site.

The `ev_charger_pool` also provides available power bounds through the
[`power_status`][frequenz.sdk.timeseries.ev_charger_pool.EVChargerPool.power_status]
method.


The `ev_charger_pool` also provides a control method
[`propose_power`][frequenz.sdk.timeseries.ev_charger_pool.EVChargerPool.propose_power],
which accepts values in the {{glossary("psc", "Passive Sign Convention")}} and supports
only charging.

# Component pools

The SDK provides a unified interface for interacting with sets of Batteries, EV
chargers and PV arrays, through their corresponding `Pool`s.

* [Battery pool][frequenz.sdk.microgrid.new_battery_pool]
* [EV charger pool][frequenz.sdk.microgrid.new_ev_charger_pool]
* [PV pool][frequenz.sdk.microgrid.new_pv_pool]

All of them provide support for streaming aggregated data and for setting the
power values of the components.

## Streaming component data

All pools have a `power` property, which is a
[`FormulaEngine`][frequenz.sdk.timeseries.formula_engine.FormulaEngine] that can

- provide a stream of resampled power values, which correspond to the sum of the
power measured from all the components in the pool together.

- be composed with other power streams to for composite formulas.

In addition, the battery pool has some additional properties that can be used as
streams for metrics specific to batteries:
[`soc`][frequenz.sdk.timeseries.battery_pool.BatteryPool.soc],
[`capacity`][frequenz.sdk.timeseries.battery_pool.BatteryPool.capacity] and
[`temperature`][frequenz.sdk.timeseries.battery_pool.BatteryPool.temperature].

## Setting power

All pools provide a `propose_power` method for setting power for the pool.  This
would then be distributed to the individual components in the pool, using an
algorithm that's suitable for the category of the components.  For example, when
controlling batteries, power could be distributed based on the `SoC` of the
individual batteries, to keep the batteries in balance.

### How to work with other actors

If multiple actors are trying to control (by proposing power values) the same
set of components, the power manager will aggregate their desired power values,
while considering the priority of the actors and the bounds they set, to
calculate the target power for the components.

The final target power can be accessed using the receiver returned from the
[`power_status`][frequenz.sdk.timeseries.battery_pool.BatteryPool.power_status]
method available for all pools, which also streams the bounds that an actor
should comply with, based on its priority.

#### Adding the power proposals of individual actors

When an actor A calls the `propose_power` method with a power, the proposed
power of the lower priority actor will get added to actor A's power.  This works
as follows:

 - the lower priority actor would see bounds shifted by the power proposed by
   actor A.
 - After lower priority actor B sets a power in its shifted bounds, it will get
   shifted back by the power set by actor A.

This has the effect of adding the powers set by actors A and B.

*Example 1*: Battery bounds available for use: -100kW to 100kW

| Actor | Priority | System Bounds   | Requested Bounds | Requested | Adjusted     | Aggregate |
|       |          |                 |                  | Power     | Power        | Power     |
|-------|----------|-----------------|------------------|-----------|--------------|-----------|
| A     | 3        | -100kW .. 100kW | None             | 20kW      | 20kW         | 20kW      |
| B     | 2        | -120kW .. 80kW  | None             | 50kW      | 50kW         | 70kW      |
| C     | 1        | -170kW .. 30kW  | None             | 50kW      | 30kW         | 100kW     |
|       |          |                 |                  |           | target power | 100kW     |

Actor A proposes a power of `20kW`, but no bounds.  In this case, actor B sees
bounds shifted by A's proposal.  Actor B proposes a power of `50kW` on this
shifted range, and if this is applied on to the original bounds (aka shift the
bounds back to the original range), it would be `20kW + 50kW = 70kW`.

So Actor C sees bounds shifted by `70kW` from the original bounds, and sets
`50kW` on this shifted range, but it can't exceed `30kW`, so its request gets
limited to 30kW.  Shifting this back by `70kW`, the target power is calculated
to be `100kW`.

Irrespective of what any actor sets, the final power won't exceed the available
battery bounds.

*Example 2*:

| Actor | Priority | System Bounds   | Requested Bounds | Requested | Adjusted     | Aggregate |
|       |          |                 |                  | Power     | Power        | Power     |
|-------|----------|-----------------|------------------|-----------|--------------|-----------|
| A     | 3        | -100kW .. 100kW | None             | 20kW      | 20kW         | 20kW      |
| B     | 2        | -120kW .. 80kW  | None             | -20kW     | -20kW        | 0kW       |
|       |          |                 |                  |           | target power | 0kW       |

Actors with exactly opposite requests cancel each other out.

#### Limiting bounds for lower priority actors

When an actor A calls the `propose_power` method with bounds (either both lower
and upper bounds or at least one of them), lower priority actors will see their
(shifted) bounds restricted and can only propose power values within that range.

*Example 1*: Battery bounds available for use: -100kW to 100kW

| Actor | Priority | System Bounds   | Requested Bounds | Requested | Adjusted     | Aggregate |
|       |          |                 |                  | Power     | Power        | Power     |
|-------|----------|-----------------|------------------|-----------|--------------|-----------|
| A     | 3        | -100kW .. 100kW | -20kW .. 100kW   | 50kW      | 40kW         | 50kW      |
| B     | 2        | -70kW .. 50kW   | -90kW .. 0kW     | -10kW     | -10kW        | 40kW      |
| C     | 1        | -60kW .. 10kW   | None             | -20kW     | -20kW        | 20kW      |
|       |          |                 |                  |           | target power | 20kW      |

Actor A with the highest priority has the entire battery bounds available to it.
It sets limited bounds of -20kW .. 100kW, and proposes a power of 50kW.

Actor B sees Actor A's limit of -20kW..100kW shifted by 50kW as -70kW..50kW, and
can only propose powers within this range, which will get added (shifted back)
to Actor A's proposed power.

Actor B tries to limit the bounds of actor C to -90kW .. 0kW, but it can only
operate in the -70kW .. 50kW range because of bounds set by actor A, so its
requested bounds get restricted to -70kW .. 0kW.

Actor C sees this as -60kW .. 10kW, because it gets shifted by Actor B's
proposed power of -10kW.

Actor C proposes a power within its bounds and the proposals of all the actors
are added to get the target power.

*Example 2*:

| Actor | Priority | System Bounds   | Requested Bounds | Requested | Adjusted     | Aggregate |
|       |          |                 |                  | Power     | Power        | Power     |
|-------|----------|-----------------|------------------|-----------|--------------|-----------|
| A     | 3        | -100kW .. 100kW | -20kW .. 100kW   | 50kW      | 50kW         | 50kW      |
| B     | 2        | -70kW .. 50kW   | -90kW .. 0kW     | -90kW     | -70kW        | -20kW     |
|       |          |                 |                  |           | target power | -20kW     |

When an actor requests a power that's outside its available bounds, the closest
available power is used.

#### Comprehensive example

Battery bounds available for use: -100kW to 100kW

| Priority | System Bounds     | Requested Bounds | Requested | Adjusted     | Aggregate |
|          |                   |                  | Power     | Power        | Power     |
|----------|-------------------|------------------|-----------|--------------|-----------|
| 7        | -100 kW .. 100 kW | None             | 10 kW     | 10 kW        | 10 kW     |
| 6        | -110 kW .. 90 kW  | -110 kW .. 80 kW | 10 kW     | 10 kW        | 20 kW     |
| 5        | -120 kW .. 70 kW  | -100 kW .. 80 kW | 80 kW     | 70 kW        | 90 kW     |
| 4        | -170 kW .. 0 kW   | None             | -120 kW   | -120 kW      | -30 kW    |
| 3        | -50 kW .. 120 kW  | None             | 60 kW     | 60 kW        | 30 kW     |
| 2        | -110 kW .. 60 kW  | -40 kW .. 30 kW  | 20 kW     | 20 kW        | 50 kW     |
| 1        | -60 kW .. 10 kW   | -50 kW .. 40 kW  | 25 kW     | 10 kW        | 60 kW     |
| 0        | -60 kW .. 0 kW    | None             | 12 kW     | 0 kW         | 60 kW     |
| -1       | -60 kW .. 0 kW    | -40 kW .. -10 kW | -10 kW    | -10 kW       | 50 kW     |
|          |                   |                  |           | Target Power | 50 kW     |

## Withdrawing power proposals

An actor can withdraw its power proposal by calling `propose_power` with `None`
target_power and `None` bounds (which are the default anyway).  As soon as an actor
calls `pool.propose_power(None)`, its proposal is dropped and the target power is
recalculated and the component powers are updated.

When all the proposals for a pool are withdrawn, the components get reset to their
default powers immediately.  These are:

| component category | default power (according to Passive Sign Convention) |
|--------------------|------------------------------------------------------|
| Batteries          | Zero                                                 |
| PV                 | Max production (Min power according to PSC)          |
| EV Chargers        | Max consumption (Max power according to PSC)         |
"""  # noqa: D205, D400

from datetime import timedelta

from ..timeseries._resampling._config import ResamplerConfig
from . import _data_pipeline, connection_manager
from ._data_pipeline import (
    consumer,
    frequency,
    grid,
    logical_meter,
    new_battery_pool,
    new_ev_charger_pool,
    new_pv_pool,
    producer,
    voltage_per_phase,
)


async def initialize(
    server_url: str,
    resampler_config: ResamplerConfig,
    *,
    api_power_request_timeout: timedelta = timedelta(seconds=5.0),
) -> None:
    """Initialize the microgrid connection manager and the data pipeline.

    Args:
        server_url: The location of the microgrid API server in the form of a URL.
            The following format is expected: `grpc://hostname{:port}{?ssl=ssl}`,
            where the port should be an int between `0` and `65535` (defaulting to
            `9090`) and ssl should be a boolean (defaulting to false). For example:
            `grpc://localhost:1090?ssl=true`.
        resampler_config: Configuration for the resampling actor.
        api_power_request_timeout: Timeout to use when making power requests to
            the microgrid API.  When requests to components timeout, they will
            be marked as blocked for a short duration, during which time they
            will be unavailable from the corresponding component pools.
    """
    await connection_manager.initialize(server_url)
    await _data_pipeline.initialize(
        resampler_config,
        api_power_request_timeout=api_power_request_timeout,
    )


__all__ = [
    "initialize",
    "consumer",
    "grid",
    "frequency",
    "logical_meter",
    "new_battery_pool",
    "new_ev_charger_pool",
    "new_pv_pool",
    "producer",
    "voltage_per_phase",
]
