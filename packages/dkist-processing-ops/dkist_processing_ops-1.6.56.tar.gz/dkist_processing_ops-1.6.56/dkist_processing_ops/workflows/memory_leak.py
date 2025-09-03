from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TrialTeardown
from dkist_processing_core import ResourceQueue
from dkist_processing_core import Workflow

from dkist_processing_ops.tasks.read_memory_leak import FitsDataRead

ops_investigation = Workflow(
    input_data="ops",
    output_data="common",
    category="investigation",
    workflow_package=__package__,
)
ops_investigation.add_node(
    task=TransferL0Data, upstreams=None, resource_queue=ResourceQueue.DEFAULT
)
ops_investigation.add_node(
    task=FitsDataRead, upstreams=TransferL0Data, resource_queue=ResourceQueue.DEFAULT
)
ops_investigation.add_node(
    task=TrialTeardown, upstreams=FitsDataRead, resource_queue=ResourceQueue.DEFAULT
)
