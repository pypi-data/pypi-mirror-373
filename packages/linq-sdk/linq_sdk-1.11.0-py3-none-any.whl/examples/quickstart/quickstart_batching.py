from linq.labware import LabwareLocation, SlotRange
from linq.parameters import FloatParameterDefinition, IntegerParameterDefinition, ParameterReference
from linq.task import ActionTask, Inputs, LabwareSource, SlotFillingRule
from linq.utils import get_latest_scheduler_version
from linq.workcell import Instrument, TransportMatrix, TransportPath, Workcell
from linq.workflow import ActionTask, Labware, LabwareType, Workflow

# Define instruments and workcell
hotel = Instrument(
    id="hotel_1",
    name="Hotel 1",
    type="hotel",
    bench="robotA",
    driver="liconic_lpx110_v1",
    capacity=100,
    mappings=["A"],
    config={},
)

peeler = Instrument(
    id="peeler_1",
    name="Peeler 1",
    type="peeler",
    bench="robotA",
    driver="peeler_driver_v1",
    capacity=1,
    mappings=["A"],
    config={},
)

sealer = Instrument(
    id="sealer_1",
    name="Sealer 1",
    type="sealer",
    bench="robotA",
    driver="sealer_driver_v1",
    capacity=1,
    mappings=["A"],
    config={},
)

uncapper = Instrument(
    id="uncapper_1",
    name="Uncapper 1",
    type="uncapper",
    bench="robotA",
    driver="uncapper_driver_v1",
    capacity=1,
    mappings=["A"],
    config={},
)

centrifuge = Instrument(
    id="centrifuge_1",
    name="Centrifuge 1",
    type="centrifuge",
    bench="robotA",
    driver="centrifuge_driver_v1",
    capacity=1,
    mappings=["A"],
    config={},
)

hamilton = Instrument(
    id="hamilton_1",
    name="Hamilton 1",
    type="hamilton",
    bench="robotA",
    driver="hamilton_driver_v1",
    capacity=2,
    mappings=["A", "B"],
    config={},
)

transport_instrument = Instrument(
    id="transport",
    name="Transport",
    type="transport",
    bench="robotA",
    driver="automata_transport_v1",
    mappings=["A"],
)

workcell = Workcell(
    instruments=[hotel, peeler, sealer, uncapper, centrifuge, hamilton, transport_instrument],
    transport_matrix=TransportMatrix(
        default_transport_time=5,
        paths=[
            TransportPath(source="robotA", destination="robotA", time=15),
        ],
    ),
)

# Define labware
tubes_type = LabwareType(id="tubes")
microplate_type = LabwareType(id="microplate_96")

tubes = Labware(
    id="sample_tubes",
    labware_type=tubes_type,
    starting_location=LabwareLocation(instrument=hotel, slot=SlotRange(start_slot=1, end_slot=50)),
    total_units=3,
)

microplate = Labware(
    id="sample_microplate",
    labware_type=microplate_type,
    starting_location=LabwareLocation(instrument=hotel, slot=SlotRange(start_slot=51, end_slot=100)),
)

# Define tasks

# Prepare Tubes:

centrifuge_tubes = ActionTask(
    id="centrifuge_tubes",
    description="Centrifuge tubes",
    instrument_type=centrifuge.type,
    action="centrifuge",
    time_estimate=60,
    labware_sources=[LabwareSource(labware=tubes)],
)

uncap_tubes = ActionTask(
    id="uncap_tubes",
    description="Uncap tubes",
    instrument_type=uncapper.type,
    action="uncap",
    time_estimate=30,
    labware_sources=[centrifuge_tubes.forward(labware=tubes)],
)

tubes_prep_tasks = [
    centrifuge_tubes,
    uncap_tubes,
]

# Prepare microplate


peel_microplate = ActionTask(
    id="peel_microplate",
    description="Peel microplate",
    instrument_type=peeler.type,
    action="peel",
    time_estimate=30,
    labware_sources=[LabwareSource(labware=microplate)],
)

microplate_prep_tasks = [
    peel_microplate,
]

# Run assay

# example 1: using 1 microplate with 1 tube on a single task
run_hamilton = ActionTask(
    id="run_hamilton",
    description="Run Hamilton",
    instrument_type=hamilton.type,
    action="run",
    time_estimate=120,
    labware_sources=[
        uncap_tubes.forward(labware=tubes, destination_slot=1),
        peel_microplate.forward(labware=microplate, destination_slot=2),
    ],
)

# example 2: using 3 microplates with 1 tube on a single task
# run_hamilton = ActionTask(
#     id="run_hamilton",
#     description="Run Hamilton",
#     instrument_type=hamilton.type,
#     action="run",
#     time_estimate=120,
#     labware_sources=[
#         uncap_tubes.forward(labware=tubes, destination_slot=1),
#         peel_microplate.forward(
#             labware=microplate,
#             destination_slot=SlotFillingRule(  # up to 3 microplates can be used with one tube
#                 range=SlotRange(start_slot=2, end_slot=8),
#                 max_count=3,
#                 distribution="non_unique",
#             ),
#         ),
#     ],
# )

# # example 3: re-using the tube for 3 microplates, in separate tasks
# run_hamilton = ActionTask(
#     id="run_hamilton",
#     description="Run Hamilton",
#     instrument_type=hamilton.type,
#     action="run",
#     time_estimate=120,
#     labware_sources=[
#         uncap_tubes.forward(labware=tubes, destination_slot=1, units_consumed=1),
#         peel_microplate.forward(labware=microplate, destination_slot=2),
#     ],
# )

seal_microplate = ActionTask(
    id="seal_microplate",
    description="Seal microplate",
    instrument_type=sealer.type,
    action="seal",
    time_estimate=30,
    labware_sources=[run_hamilton.forward(labware=microplate)],
    inputs=Inputs(seal_temperature=ParameterReference(parameter_id="seal_temperature")),
)

store_microplate_on_hotel = ActionTask(
    id="store_microplate_on_hotel",
    description="End position for the labware",
    instrument_type=hotel.type,
    action="store",
    labware_sources=[
        seal_microplate.forward(
            labware=microplate,
            destination_slot=SlotFillingRule(
                range=SlotRange(start_slot=51, end_slot=100), min_count=1, max_count=1, distribution="unique"
            ),
        ),
    ],
    time_estimate=30,
)


recap_tubes = ActionTask(
    id="recap_tubes",
    description="Recap tubes",
    instrument_type=uncapper.type,
    action="recap",
    time_estimate=30,
    labware_sources=[run_hamilton.forward(labware=tubes)],
)

store_tubes_on_hotel = ActionTask(
    id="store_tubes_on_hotel",
    description="End position for the labware",
    instrument_type=hotel.type,
    action="store",
    labware_sources=[
        recap_tubes.forward(
            labware=tubes,
            destination_slot=SlotFillingRule(
                range=SlotRange(start_slot=1, end_slot=50), min_count=1, max_count=1, distribution="unique"
            ),
        ),
    ],
    time_estimate=30,
)


assay_tasks = [
    run_hamilton,
    seal_microplate,
    store_microplate_on_hotel,
    recap_tubes,
    store_tubes_on_hotel,
]

parameter_definitions = [
    IntegerParameterDefinition(id="batch_number", name="Number of batches to run", always_required=True, default=4),
    FloatParameterDefinition(
        id="seal_temperature",
        name="Temperature of sealing plate. This value should not be prompted for when plan.",
        default=150,
    ),
]


# Create workflow
workflow = Workflow(
    workcell=workcell,
    name="Sample Workflow",
    author="John Doe",
    description="A sample workflow",
    version="1.0",
    scheduler_version=get_latest_scheduler_version(),
    labware_types=[tubes_type, microplate_type],
    labware=[tubes, microplate],
    tasks=[*tubes_prep_tasks, *microplate_prep_tasks, *assay_tasks],
    parameter_definitions=parameter_definitions,
    batches=ParameterReference(parameter_id="batch_number"),
)
