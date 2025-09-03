import sys

from linq.client import Linq
from linq.hooks import (
    Filters,
    HookParameters,
    LabwareMovementHook,
    NewPlanHook,
    RunStateChangeHook,
    SafetyStateChangeHook,
    TaskStateChangeHook,
)
from linq.labware import GrippingOffset, GrippingWidth, GrippingWidths, LabwareLocation
from linq.parameters import ParameterReference
from linq.task import ActionTask, Inputs, LabwareOutput, StoredLabware
from linq.utils import get_latest_scheduler_version
from linq.workcell import Instrument, TransportMatrix, TransportPath, Workcell
from linq.workflow import ActionTask, Labware, LabwareType, RunInstruction, Workflow

# Define instruments and workcell
hotel = Instrument(
    id="hotel_1",
    name="Hotel 1",
    type="hotel",
    bench="robotA",
    driver="hotel_driver_v1",
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
tubes_type = LabwareType(
    id="tubes",
    gripping_widths=GrippingWidths(portrait=GrippingWidth(gripped=10.0), landscape=GrippingWidth(released=12.0)),
    gripping_depth_offset=GrippingOffset(portrait=2.0, landscape=3.0),
    gripping_height_offset=5.0,
    scara_motion_profile="some_motion_profile",
    scara_speed_multiplier=1.5,
)
microplate_type = LabwareType(id="microplate_96")

tubes = Labware(
    id="sample_tubes",
    labware_type=tubes_type,
    starting_location=LabwareLocation(instrument=hotel, slot=1),
    batch=1,
)

microplate = Labware(
    id="sample_microplate",
    labware_type=microplate_type,
    starting_location=LabwareLocation(instrument=hotel, slot=10),
    batch=1,
)

# Define tasks

# Prepare Tubes:
unload_tubes_from_hotel = ActionTask(
    id="unload_tubes_from_hotel",
    description="Unload tubes from hotel",
    instrument_type=hotel.type,
    action="unload",
    inputs=Inputs(slot=1),
    time_estimate=30,
    # The labware is already stored in the hotel
    labware_sources=[StoredLabware(tubes, slot=1)],
    labware_outputs=[
        LabwareOutput(
            tubes,
            slot=0,  # Slot 0 is the loading/parking bay of the hotel
        ),
    ],
)

centrifuge_tubes = ActionTask(
    id="centrifuge_tubes",
    description="Centrifuge tubes",
    instrument_type=centrifuge.type,
    action="centrifuge",
    time_estimate=60,
    labware_sources=[
        # Sources can be specified directly, as
        # LabwareSource(tubes, destination_slot=1, source_task=unload_tubes_from_hotel),
        # or labware can be sourced by referencing a labware output by a previous task
        unload_tubes_from_hotel.forward(
            labware=tubes,
            destination_slot=1,  # Optional, the default is 1
        )
    ],
    # labware_outputs is optional - if left out, it will default to mirroring the labware sources.
    # here, this is equivalent to:
    # labware_outputs=[LabwareOutput(tubes, slot=1)],
    # Dependencies can be added explicitly, but in this case they are already implied by the labware sources
    # dependencies=[unload_tubes_from_hotel],
)

uncap_tubes = ActionTask(
    id="uncap_tubes",
    description="Uncap tubes",
    instrument_type=uncapper.type,
    action="uncap",
    time_estimate=30,
    labware_sources=[centrifuge_tubes.forward(labware=tubes)],
    labware_outputs=[LabwareOutput(tubes)],
)

tubes_prep_tasks = [
    unload_tubes_from_hotel,
    centrifuge_tubes,
    uncap_tubes,
]

# Prepare microplate

unload_microplate_from_hotel = ActionTask(
    id="unload_microplate_from_hotel",
    description="Unload microplate from hotel",
    instrument_type=hotel.type,
    action="unload",
    inputs=Inputs(slot=1),
    time_estimate=30,
    labware_sources=[StoredLabware(microplate, slot=10)],
    labware_outputs=[LabwareOutput(microplate, slot=0)],
)

peel_microplate = ActionTask(
    id="peel_microplate",
    description="Peel microplate",
    instrument_type=peeler.type,
    action="peel",
    time_estimate=30,
    labware_sources=[unload_microplate_from_hotel.forward(labware=microplate)],
    labware_outputs=[LabwareOutput(microplate)],
)

microplate_prep_tasks = [
    unload_microplate_from_hotel,
    peel_microplate,
]

# Run assay

run_hamilton = ActionTask(
    id="run_hamilton",
    description="Run Hamilton",
    instrument_type=hamilton.type,
    action="run",
    time_estimate=120,
    labware_sources=[
        uncap_tubes.forward(labware=tubes, destination_slot=0),
        peel_microplate.forward(labware=microplate, destination_slot=1),
    ],
    labware_outputs=[
        LabwareOutput(tubes, slot=0),
        LabwareOutput(microplate, slot=1),
    ],
)

seal_microplate = ActionTask(
    id="seal_microplate",
    description="Seal microplate",
    instrument_type=sealer.type,
    action="seal",
    time_estimate=30,
    labware_sources=[run_hamilton.forward(labware=microplate)],
    labware_outputs=[LabwareOutput(microplate)],
)

load_microplate_to_hotel = ActionTask(
    id="load_microplate_to_hotel",
    description="Load microplate to hotel",
    instrument_type=hotel.type,
    action="load",
    inputs=Inputs(slot=1),
    labware_sources=[seal_microplate.forward(labware=microplate)],
    # This task stores labware in the hotel
    # If another task required this labware, it would first have to be unloaded
    labware_outputs=[StoredLabware(microplate, slot=1)],
    time_estimate=30,
)

assay_tasks = [
    run_hamilton,
    seal_microplate,
    load_microplate_to_hotel,
]

prep_hotel_instruction = RunInstruction(description="Ensure there is sufficient space in the hotel", phase="pre")
prep_hamilton_instruction = RunInstruction(description="Ensure plate is in hamilton", phase="pre")
post_run_instruction = RunInstruction(description="Ensure plate has reached hotel", phase="post")

run_instructions = [prep_hotel_instruction, prep_hamilton_instruction, post_run_instruction]

hooks = [
    RunStateChangeHook(
        parameters=HookParameters(
            url="http://example.com",
        ),
        filter=Filters.ON_RUN_STATE_CHANGE,
    ),
    TaskStateChangeHook(
        parameters=HookParameters(
            url="http://example.com",
        ),
        filter=Filters.ON_TASK_STATE_CHANGE,
        task_ids=[run_hamilton.id],
    ),
    LabwareMovementHook(
        parameters=HookParameters(
            url="http://example.com",
        ),
        filter=Filters.ON_LABWARE_MOVEMENT,
        labware_ids=[],
        trigger_on="both",
    ),
    SafetyStateChangeHook(
        parameters=HookParameters(
            url="http://example.com",
        ),
        filter=Filters.ON_SAFETY_STATE_CHANGE,
    ),
    NewPlanHook(
        parameters=HookParameters(
            url="http://example.com",
        ),
        filter=Filters.ON_NEW_PLAN,
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
    run_instructions=run_instructions,
    hooks=hooks,
    parameter_definitions=[],
)

if __name__ == "__main__":
    linq = Linq()
    print("Validating workflow...")
    result = linq.validate_workflow(workflow)
    if result.is_valid:
        print("Workflow is valid")
    else:
        print("Workflow is invalid")
        sys.exit(1)

    # Print the JSON representation of the workflow
    # print("\nWorkflow JSON:\n")
    # print(workflow.to_api_input().model_dump(exclude_none=True, mode="json"))
    # print("\nPlanning workflow...")
    # TODO: Uncomment when workflow crud is implemented
    # workflow_id = linq.create_workflow(workflow)
    # plan = linq.plan_workflow(workflow)
    # if isinstance(plan, workflow_api.WorkflowPlanResult):
    #     print("Planning successful.")
    #     print(
    #         "\nPlanning visualisations - note: these pre-rendered visualisations are temporary "
    #         "and will be replaced with creating visualisations locally."
    #     )

    #     # TODO: Replace with local visualisation rendering
    #     # print("\nInstrument View ")
    #     # print(plan.instrument_visualization_url)
    #     # print("\nLabware View")
    #     # print(plan.labware_visualization_url)
    # else:
    #     print("An error occurred during planning.")
