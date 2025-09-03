"""Workflows to test task submission and spin up"""

from dkist_processing_common.tasks import TrialTeardown
from dkist_processing_core import ResourceQueue
from dkist_processing_core import Workflow

from dkist_processing_ops.tasks import WaitTask

smoke_default = Workflow(
    input_data="ops",
    output_data="common",
    category="smoke",
    detail="default",
    workflow_package=__package__,
)
smoke_default.add_node(task=WaitTask, upstreams=None, resource_queue=ResourceQueue.DEFAULT)
smoke_default.add_node(task=TrialTeardown, upstreams=WaitTask)


smoke_high_mem = Workflow(
    input_data="ops",
    output_data="common",
    category="smoke",
    detail="high-mem",
    workflow_package=__package__,
)
smoke_high_mem.add_node(task=WaitTask, upstreams=None, resource_queue=ResourceQueue.HIGH_MEMORY)
smoke_high_mem.add_node(task=TrialTeardown, upstreams=WaitTask)
