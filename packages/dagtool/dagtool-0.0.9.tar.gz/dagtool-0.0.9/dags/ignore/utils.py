from airflow.models import Pool

sequence_pool = Pool.create_or_update_pool(
    "sequence_pool",
    slots=1,
    description="Limit to 1 run of MySelf workload.",
    include_deferred=False,
)
