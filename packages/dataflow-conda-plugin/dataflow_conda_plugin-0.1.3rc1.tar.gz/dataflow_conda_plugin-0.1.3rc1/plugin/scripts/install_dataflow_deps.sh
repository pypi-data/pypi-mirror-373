#!/bin/bash
set -e
conda_env_path=$1

py_version=$(${conda_env_path}/bin/python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
                      
${conda_env_path}/bin/pip install dash==3.0.3 dash-renderer==1.9.1 plotly==6.0.1 typing==3.7.4.3 streamlit==1.45.1 ipython==9.2.0 ipykernel==6.29.5 ipython-sql==0.4.1 jupysql==0.10.14 psycopg2-binary==2.9.10 cryptography==44.0.3 dataflow-core dataflow-dbt

# 3. Install Dataflow Airflow to a separate path in environment 
${conda_env_path}/bin/pip install \
    --force-reinstall --root-user-action ignore \
    --no-warn-conflicts dataflow-airflow \
    --target ${conda_env_path}/bin/airflow-libraries/

files=(
    ${conda_env_path}/lib/python${py_version}/site-packages/dbt/config/profile.py 
    ${conda_env_path}/lib/python${py_version}/site-packages/dbt/task/debug.py
)
for file in ${files[@]}
do      
    awk '{gsub("from dbt.clients.yaml_helper import load_yaml_text", "from dbt.dataflow_config.secrets_manager import load_yaml_text"); print}' $file > temp 
    mv temp $file
done

echo "Environment Creation Successful"