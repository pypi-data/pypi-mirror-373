FROM rockylinux:9.3

RUN dnf install -y \
      gcc \
    && dnf clean all

ENV UV_COMPILE_BYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY --from=ghcr.io/astral-sh/uv:0.8.7 /uv /uvx /bin/

ARG AIRFLOW_VERSION=3.0.4
ARG PYTHON_VERSION=3.10

RUN uv venv /opt/venv --python=${PYTHON_VERSION}

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN uv pip install "apache-airflow[google]==${AIRFLOW_VERSION}" \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# NOTE: Force change version of necessary version of deps package for DAG Tool.
#   - pydantic: use minimum version for testing on local.
RUN uv pip install \
      "pydantic>=2.9.2"

COPY ./dagtool /opt/airflow/plugins/dagtool

WORKDIR /opt/airflow
