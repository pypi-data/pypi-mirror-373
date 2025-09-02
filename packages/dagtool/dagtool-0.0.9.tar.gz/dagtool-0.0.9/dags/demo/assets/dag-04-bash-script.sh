echo "$AIRFLOW_ENV";
echo "$PROJECT_ID";
echo "$BUCKET_ID";
echo "{{ data_interval_start | tz('Asia/Bangkok') | fmt('%Y-%m-%d %H:00:00%z') }}";
echo "${NEW_ENV}";
echo "{{ vars('project_id') }}";
