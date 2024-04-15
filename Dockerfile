FROM python:3.10-slim AS build

WORKDIR /

RUN apt-get update -y && apt-get install -y git
RUN git clone --depth 1 --single-branch https://gitlab.com/ska-telescope/ost/ska-ost-sim-low-station-beam --branch ops-252-first-functionalities
RUN pip install --no-cache-dir poetry poetry-plugin-export && \
    cd ska-ost-sim-low-station-beam && \
    poetry export --without-hashes --all-extras -o requirements.txt && \
    poetry build

FROM python:3.10-slim
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OSKAR_VERSION=2.9.4

# Install OSKAR and OSKARPy
RUN apt-get update \
&& apt-get --yes install --no-install-recommends \
  cmake \
  build-essential \
  git \
  libhdf5-dev \
&& rm -rf /var/lib/apt/lists/*
RUN cd / \
&& git clone https://github.com/OxfordSKA/OSKAR.git \
&& cd OSKAR && git checkout $OSKAR_VERSION \
&& mkdir build && cd build \
&& cmake ../ && make -j4 && make install \
&& cd / && rm -r OSKAR

COPY --from=build /ska-ost-sim-low-station-beam/dist/*.whl /ska-ost-sim-low-station-beam/requirements.txt ./
RUN pip install --no-cache-dir --no-compile -r requirements.txt *.whl \
    --extra-index-url https://artefact.skao.int/repository/pypi-all/simple && \
    rm -rf /root/.cache
