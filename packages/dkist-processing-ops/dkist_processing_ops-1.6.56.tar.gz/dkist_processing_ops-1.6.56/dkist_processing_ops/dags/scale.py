"""
DAG to use up workers to support scaling
"""

from os import environ
from pathlib import Path

from dkist_processing_core.build_utils import export_dags


def export_scale_dags(path: Path | str) -> list[Path]:
    """Export all the ops dags"""
    result = []
    dag_prefix = "ops_scale"
    version = environ.get("BUILD_VERSION", "dev")
    scales = [16, 32]
    queues = ["default", "high_memory"]
    sleep_duration_seconds = 60
    for queue in queues:
        for scale in scales:
            dag_name = f"{dag_prefix}_{queue}_{scale}_{version}"
            dag_body = _scale_dag(
                dag_name=dag_name,
                sleep_duration_seconds=sleep_duration_seconds,
                queue=queue,
                concurrent_task_count=scale,
            )
            dag_path = _export_ops_dag(dag_name=dag_name, dag_body=dag_body, path=path)
            result.append(dag_path)
    return result


def _export_ops_dag(dag_name: str, dag_body: str, path: Path | str | None = None) -> Path:
    """Write a file representation of the scaling DAG."""
    path = path or "dags/"
    path = Path(path)
    path.mkdir(exist_ok=True)
    workflow_py = path / f"{dag_name}.py"
    with workflow_py.open(mode="w") as f:
        f.write(dag_body)
    return workflow_py


def _scale_dag(
    dag_name: str,
    sleep_duration_seconds: int = 60,
    queue: str | None = None,
    concurrent_task_count: int = 16,
) -> str:
    queue = queue or "default"

    imports = f"""# Scale {concurrent_task_count} DAG on queue {queue}
from datetime import timedelta
import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
"""
    dag = f"""with DAG(
        dag_id="{dag_name}",
        start_date=pendulum.today("UTC").add(days=-2),
        schedule=None,
        catchup=False,
        tags=["ops", "scale"],
    ) as d:"""
    tasks = []
    for idx in range(concurrent_task_count):
        task = f"""    t{idx} = BashOperator(
            task_id="t{idx}",
            bash_command=f"sleep {sleep_duration_seconds}",
            retries=0,
            retry_delay=timedelta(seconds=60),
            owner="DKIST Data Center",
            queue="{queue}",
        )"""
        tasks.append(task)
    parts = [imports, dag] + tasks
    body = "\n".join(parts)
    return body
