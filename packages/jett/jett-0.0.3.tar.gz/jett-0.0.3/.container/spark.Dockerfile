FROM rockylinux:9.3

RUN dnf install -y \
      gcc \
      java-1.8.0-openjdk-devel \
      wget \
    && dnf clean all

ENV UV_COMPILE_BYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY --from=ghcr.io/astral-sh/uv:0.8.7 /uv /uvx /bin/

ARG AIRFLOW_VERSION=2.9.2
ARG PYTHON_VERSION=3.10

RUN uv venv /opt/venv --python=${PYTHON_VERSION}

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

ARG SPARK_VERSION=3.4.1
ARG SPARK_ARCHIVE=spark-${SPARK_VERSION}-bin-hadoop3

# # NOTE: Install Apache Spark
# RUN wget https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/${SPARK_ARCHIVE}.tgz \
#     && tar -xvf ${SPARK_ARCHIVE}.tgz -C /opt && rm -f ${SPARK_ARCHIVE}.tgz  \
#     && ln -s ${SPARK_ARCHIVE} /opt/spark

# NOTE: Use cache file instead.
COPY ./.cache/spark-3.4.1-bin-hadoop3.tgz spark-3.4.1-bin-hadoop3.tgz
RUN tar -xvf ${SPARK_ARCHIVE}.tgz -C /opt  \
    && rm -f ${SPARK_ARCHIVE}.tgz \
    && ln -s ${SPARK_ARCHIVE} /opt/spark

ENV JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk
ENV SPARK_HOME=/opt/spark
ENV HADOOP_HOME=/opt/spark
ENV PYSPARK_DRIVER_PYTHON=/opt/venv/bin/python

# NOTE: Install Apache Airflow
# WARNING: Install pendulum first because Airflow version 2.7 does not compatible
#   if it more than 3.0.0
RUN uv pip install "pendulum<3.0.0" \
    && uv pip install "apache-airflow[google]==${AIRFLOW_VERSION}" \
       --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# NOTE: Force change version of necessary version of deps package for Jett.
RUN uv pip install \
      "python-dotenv==1.1.1" \
      "click==8.1.8" \
      "ddeutil-io[yaml,toml]==0.2.17" \
      "pyarrow==21.0.0" \
      "pyspark[connect]==3.4.1" \
      "pydantic>=2.9.2" \
      "requests==2.32.4" \
      "duckdb==1.3.2" \
      "polars==1.32.0" \
      "pyiceberg==0.9.1"

COPY ./jett /opt/airflow/plugins/jett

WORKDIR /opt/airflow
