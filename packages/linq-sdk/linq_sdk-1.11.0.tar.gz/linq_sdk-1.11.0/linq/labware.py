import logging
from dataclasses import dataclass, field
from typing import Self

from .schema import workflow_api
from .sdk_entity import SDKEntity
from .workcell import Instrument

logger = logging.getLogger(__name__)


@dataclass(kw_only=True, slots=True)
class LabwareDimensions(SDKEntity[workflow_api.LabwareDimensionsInput, workflow_api.LabwareDimensions]):
    """Physical dimensions of a piece of labware."""

    length: float
    """Length in mm."""

    width: float
    """Width in mm."""

    height: float
    """Height in mm."""

    def to_api_input(self) -> workflow_api.LabwareDimensionsInput:
        return workflow_api.LabwareDimensionsInput(
            length=self.length,
            width=self.width,
            height=self.height,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.LabwareDimensions) -> Self:
        return cls(length=api_output.length, width=api_output.width, height=api_output.height)


@dataclass(kw_only=True, slots=True)
class LabwareOffset(SDKEntity[workflow_api.LabwareOffsetsInput, workflow_api.LabwareOffsets]):
    """Physical dimensions of a piece of labware."""

    height: float | None = None

    def to_api_input(self) -> workflow_api.LabwareOffsetsInput:
        return workflow_api.LabwareOffsetsInput(
            height=self.height,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.LabwareOffsets) -> Self:
        return cls(height=api_output.height)


@dataclass(kw_only=True, slots=True)
class GrippingWidth(SDKEntity[workflow_api.GrippingWidthInput, workflow_api.GrippingWidth]):
    gripped: float | None = None
    released: float | None = None

    def to_api_input(self) -> workflow_api.GrippingWidthInput:
        data = {}
        if self.gripped is not None:
            data["gripped"] = self.gripped
        if self.released is not None:
            data["released"] = self.released
        return workflow_api.GrippingWidthInput(gripped=self.gripped, released=self.released)

    @classmethod
    def from_api_output(cls, api_output: workflow_api.GrippingWidth) -> Self:
        return cls(gripped=api_output.gripped, released=api_output.released)


@dataclass(kw_only=True, slots=True)
class GrippingWidths(SDKEntity[workflow_api.GrippingWidthsInput, workflow_api.GrippingWidths]):
    portrait: GrippingWidth | None = None
    landscape: GrippingWidth | None = None

    def to_api_input(self) -> workflow_api.GrippingWidthsInput:
        data = {}
        if self.portrait is not None:
            data["portrait"] = self.portrait.to_api_input()
        if self.landscape is not None:
            data["landscape"] = self.landscape.to_api_input()
        return workflow_api.GrippingWidthsInput(
            portrait=data.get("portrait"),
            landscape=data.get("landscape"),
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.GrippingWidths) -> Self:
        return cls(
            portrait=GrippingWidth.from_api_output(api_output.portrait) if api_output.portrait is not None else None,
            landscape=GrippingWidth.from_api_output(api_output.landscape) if api_output.landscape is not None else None,
        )


@dataclass(kw_only=True, slots=True)
class GrippingOffset(SDKEntity[workflow_api.GrippingOffsetInput, workflow_api.GrippingOffset]):
    portrait: float | None = None
    landscape: float | None = None

    def to_api_input(self) -> workflow_api.GrippingOffsetInput:
        return workflow_api.GrippingOffsetInput(
            portrait=self.portrait,
            landscape=self.landscape,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.GrippingOffset) -> Self:
        return cls(
            portrait=api_output.portrait,
            landscape=api_output.landscape,
        )


@dataclass(kw_only=True, slots=True)
class LabwareType(SDKEntity[workflow_api.LabwareTypeInput, workflow_api.LabwareType]):
    """A specific type of labware, specifying the dimensions of all labware of this type."""

    id: str
    """Unique ID for this labware type."""

    dimensions: LabwareDimensions | None = None
    """Labware type dimensions -- DEPRECATED, will be removed in February 2025 release"""

    labware_dimension_offset: LabwareOffset = field(default_factory=LabwareOffset)
    """Dimensional offsets for labware type."""

    max_idle_time: int | None = None

    gripping_widths: GrippingWidths | None = None
    """Gripping widths along the X-axis for portrait and landscape orientations, including both gripped and released states."""

    gripping_depth_offset: GrippingOffset | None = None
    """Offsets along the Y-axis for the tool, applicable to both portrait and landscape orientations."""

    gripping_height_offset: float | GrippingOffset | None = None
    """Z-axis offsets for gripping, either as a single value or specified per orientation."""

    scara_motion_profile: str | None = None
    """Custom motion profile for SCARA robot."""

    scara_speed_multiplier: float | None = None
    """Speed multiplier for SCARA robot."""

    def to_api_input(self) -> workflow_api.LabwareTypeInput:
        return workflow_api.LabwareTypeInput(
            id=self.id,
            dimensions=self.dimensions.to_api_input() if self.dimensions is not None else None,
            labware_dimension_offset=self.labware_dimension_offset.to_api_input(),
            max_idle_time=self.max_idle_time,
            gripping_widths=self.gripping_widths.to_api_input() if self.gripping_widths is not None else None,
            gripping_depth_offset=self.gripping_depth_offset.to_api_input()
            if self.gripping_depth_offset is not None
            else None,
            gripping_height_offset=(
                self.gripping_height_offset.to_api_input()
                if isinstance(self.gripping_height_offset, GrippingOffset)
                else self.gripping_height_offset
            )
            if self.gripping_height_offset is not None
            else None,
            scara_motion_profile=self.scara_motion_profile,
            scara_speed_multiplier=self.scara_speed_multiplier,
        )

    @classmethod
    def from_api_output(cls, api_output: workflow_api.LabwareType) -> Self:
        return cls(
            id=api_output.id,
            dimensions=LabwareDimensions.from_api_output(api_output.dimensions)
            if api_output.dimensions is not None
            else None,
            labware_dimension_offset=LabwareOffset.from_api_output(api_output.labware_dimension_offset),
            gripping_widths=GrippingWidths.from_api_output(api_output.gripping_widths)
            if api_output.gripping_widths is not None
            else None,
            gripping_depth_offset=GrippingOffset.from_api_output(api_output.gripping_depth_offset)
            if api_output.gripping_depth_offset is not None
            else None,
            gripping_height_offset=(
                GrippingOffset.from_api_output(api_output.gripping_height_offset)
                if isinstance(api_output.gripping_height_offset, workflow_api.GrippingOffset)
                else api_output.gripping_height_offset
            )
            if api_output.gripping_height_offset is not None
            else None,
            scara_motion_profile=api_output.scara_motion_profile,
            scara_speed_multiplier=api_output.scara_speed_multiplier,
        )


@dataclass(kw_only=True, slots=True)
class SlotRange(SDKEntity[workflow_api.SlotRangeInput, workflow_api.SlotRange]):
    """Range of slots in an instrument."""

    start_slot: int
    """Start slot of the range."""

    end_slot: int
    """End slot of the range."""

    def to_api_input(self) -> workflow_api.SlotRangeInput:
        return workflow_api.SlotRangeInput(start_slot=self.start_slot, end_slot=self.end_slot)

    @classmethod
    def from_api_output(cls, api_output: workflow_api.SlotRange) -> Self:
        return cls(start_slot=api_output.start_slot, end_slot=api_output.end_slot)


@dataclass(kw_only=True, slots=True)
class LabwareLocation(
    SDKEntity[
        workflow_api.LocationInput | workflow_api.LocationRangeInput, workflow_api.Location | workflow_api.LocationRange
    ]
):
    """Location of a labware in an instrument."""

    instrument: Instrument
    """Instrument the labware is located in."""

    slot: int | SlotRange
    """Slot within the instrument the labware is located in."""

    def to_api_input(self) -> workflow_api.LocationInput | workflow_api.LocationRangeInput:
        if isinstance(self.slot, SlotRange):
            return workflow_api.LocationRangeInput(
                instrument=self.instrument.id,
                start_slot=self.slot.start_slot,
                end_slot=self.slot.end_slot,
            )
        else:
            return workflow_api.LocationInput(instrument=self.instrument.id, slot=self.slot)

    @classmethod
    def from_api_output(
        cls,
        api_output: workflow_api.Location | workflow_api.LocationRange,
        instruments: dict[str, workflow_api.WorkcellInstrument],
    ) -> Self:
        instrument = Instrument.from_api_output(instruments[api_output.instrument])
        if isinstance(api_output, workflow_api.Location):
            return cls(
                instrument=instrument,
                slot=api_output.slot,
            )
        else:
            return cls(
                instrument=instrument,
                slot=SlotRange(start_slot=api_output.start_slot, end_slot=api_output.end_slot),
            )


@dataclass(kw_only=True, slots=True)
class Labware(SDKEntity[workflow_api.LabwareItemInput, workflow_api.LabwareItem]):
    """A single piece of labware."""

    id: str
    """Unique ID of this piece of labware."""

    labware_type: LabwareType
    """Labware type."""

    starting_location: LabwareLocation | list[LabwareLocation]
    """Location the labware is located in at the start of the workflow. Can be a single location or a list of locations."""

    total_units: int = 1
    """The number of consumable 'units' in a single piece of labware. Does not affect the workflow if 'units_consumed' is not defined on any tasks."""

    batch: int | None = None
    """The batch that this labware belongs to. Leave as None for auto-assignment"""

    description: str | None = None
    """Description."""

    barcode: str | None = None
    """Barcode (or None if labware has no barcode)."""

    def to_api_input(self) -> workflow_api.LabwareItemInput:
        if isinstance(self.starting_location, LabwareLocation):
            location = self.starting_location.to_api_input()
        elif isinstance(self.starting_location, list):
            location = [s.to_api_input() for s in self.starting_location]
        else:
            raise TypeError(
                f"expected starting_location as LabwareLocation or list[LabwareLocation], "
                f"got {type(self.starting_location).__name__}"
            )
        return workflow_api.LabwareItemInput(
            id=self.id,
            type=self.labware_type.id,
            description=self.description,
            location=location,
            batch=self.batch,
            barcode=self.barcode,
            total_units=self.total_units,
        )

    @classmethod
    def from_api_output(
        cls,
        api_output: workflow_api.LabwareItem,
        labware_type: LabwareType,
        instruments: dict[str, workflow_api.WorkcellInstrument],
    ) -> Self:
        starting_location = (
            LabwareLocation.from_api_output(api_output.location, instruments)
            if isinstance(api_output.location, (workflow_api.Location, workflow_api.LocationRange))
            else [LabwareLocation.from_api_output(location, instruments) for location in api_output.location]
        )
        return cls(
            id=api_output.id,
            labware_type=labware_type,
            starting_location=starting_location,
            batch=api_output.batch,
            description=api_output.description,
            barcode=api_output.barcode,
            total_units=api_output.total_units,
        )
