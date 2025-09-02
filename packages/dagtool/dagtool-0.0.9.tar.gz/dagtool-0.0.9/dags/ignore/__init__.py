"""# Ignore DAGs

The ignored DAGs that generate from template config file.
"""

from dagtool import Factory
from dagtool.utils import days_ago

factory = Factory(name="ignore", path=__file__, docs=__doc__)
factory.build_airflow_dags_to_globals(
    gb=globals(),
    default_args={"start_date": days_ago(2)},
)
