from dataclasses import dataclass, field
from typing import Self
from uuid import UUID

from .schema import workflow_api
from .sdk_entity import SDKEntity

ALL_INSTRUMENTS = "ALL"


@dataclass(kw_only=True, slots=True)
class Instrument(SDKEntity[workflow_api.WorkcellInstrumentInput, workflow_api.WorkcellInstrument]):
    """Describes an instrument in a workcell."""

    id: str
    """Instrument ID (must be unique for the entire workflow)."""

    name: str
    """Instrument name."""

    type: str
    """Instrument type. Currently arbitrary."""

    bench: str
    """Id of the instrument's bench."""

    driver: str
    """Name of the instrument driver."""

    capacity: int = 1
    """Instrument labware capacity."""

    is_slotless_container: bool = False
    """Set to true for instruments like bins, which have capacity for many pieces of labware not distinct slots."""

    config: dict[str, workflow_api.JsonSerializable] = field(default_factory=dict)
    """Configuration options for the instrument driver. Use the driver CLI to get valid values for each driver."""

    mappings: list[str] = field(default_factory=lambda: [ALL_INSTRUMENTS])
    """Mappings this instrument is assigned to, used when a task can pick from several instruments."""

    def to_api_input(self) -> workflow_api.WorkcellInstrumentInput:
        return workflow_api.WorkcellInstrumentInput(
            id=self.id,
            name=self.name,
            type=self.type,
            bench=self.bench,
            driver=self.driver,
            capacity=self.capacity,
            is_slotless_container=self.is_slotless_container,
            config=self.config,
            mappings=self.mappings,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.WorkcellInstrument) -> Self:
        return cls(
            id=api_output.id,
            name=api_output.name,
            type=api_output.type,
            bench=api_output.bench,
            driver=api_output.driver,
            capacity=api_output.capacity,
            is_slotless_container=api_output.is_slotless_container,
            config=api_output.config,
            mappings=api_output.mappings,
        )


@dataclass(kw_only=True, slots=True)
class TransportPath(SDKEntity[workflow_api.TransportPathInput, workflow_api.TransportPath]):
    """Describes the estimated time to transport labware from an instrument on one bench to another.

    Note: For benches with multiple instruments, this assumes it takes roughly the same amount of time
    to transfer labware from any instrument on the bench to the transport layer and vice versa.
    """

    source: str
    """The source bench."""

    destination: str
    """The destination bench."""

    time: int
    """Estimated transport time from source to destination."""

    def to_api_input(self) -> workflow_api.TransportPathInput:
        return workflow_api.TransportPathInput(source=self.source, destination=self.destination, time=self.time)

    @classmethod
    def from_api_output(cls, api_output: workflow_api.TransportPath) -> Self:
        return cls(source=api_output.source, destination=api_output.destination, time=api_output.time)


@dataclass(kw_only=True, slots=True)
class TransportMatrix(SDKEntity[workflow_api.TransportMatrixInput, workflow_api.TransportMatrix]):
    """The transport matrix contains all estimates for transport times between benches."""

    default_transport_time: int
    """Default transport time if no specific estimate for a path is given."""

    paths: list[TransportPath]
    """List of paths describing the time to transport labware from one bench to another."""

    def to_api_input(self) -> workflow_api.TransportMatrixInput:
        return workflow_api.TransportMatrixInput(
            default=self.default_transport_time,
            paths=[path.to_api_input() for path in self.paths],
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.TransportMatrix) -> Self:
        return cls(
            default_transport_time=api_output.default,
            paths=[TransportPath.from_api_output(path) for path in api_output.paths],
        )


@dataclass(kw_only=True, slots=True)
class Workcell(SDKEntity[workflow_api.WorkcellInput, workflow_api.Workcell]):
    """Represents a workcell."""

    workcell_id: UUID | None = field(default=None)
    """The identifier of the workcell."""

    instruments: list[Instrument]
    """The list of instruments present in the workcell."""

    transport_matrix: TransportMatrix
    """Describes transport times between benches in the workcell."""

    def to_api_input(self) -> workflow_api.WorkcellInput:
        return workflow_api.WorkcellInput(
            workcell_id=self.workcell_id,
            instruments=[instrument.to_api_input() for instrument in self.instruments],
            transport_matrix=self.transport_matrix.to_api_input(),
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.Workcell) -> Self:
        return cls(
            workcell_id=api_output.workcell_id,
            instruments=[Instrument.from_api_output(instrument) for instrument in api_output.instruments],
            transport_matrix=TransportMatrix.from_api_output(api_output.transport_matrix),
        )

    def get_instrument(self, instrument_id: str) -> Instrument:
        """
        Fetches the instrument with the given `instrument_id` from the list of instruments.

        :param str instrument_id: The unique identifier of the instrument.
        :raise KeyError: If no instrument with the specified ID is found in the workcell.
        :return: The instrument with the matching ID.
        :rtype: Instrument
        """
        for instrument in self.instruments:
            if instrument.id == instrument_id:
                return instrument
        raise KeyError(f"Workcell has no instrument with id {instrument_id}")
