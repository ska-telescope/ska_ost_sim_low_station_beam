FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Ubuntu installations
RUN apt-get update \
&& apt-get --yes install --no-install-recommends \
  build-essential \
  cmake \
  git \
  libhdf5-dev \
  python3-dev \
  python3-pip \
  python3-setuptools \
  wget \
&& rm -rf /var/lib/apt/lists/*

# Install OSKAR
OSKAR_VERSION=2.9.4
RUN cd / \
&& git clone https://github.com/OxfordSKA/OSKAR.git \
&& cd OSKAR && git checkout $OSKAR_VERSION \
&& mkdir build && cd build \
&& cmake ../ && make && make install \
&& cd / && rm -r OSKAR

# Install Python packages
RUN pip3 install -U pip
RUN pip3 install 'git+https://github.com/OxfordSKA/OSKAR.git@${OSKAR_VERSION}#egg=oskarpy&subdirectory=python'
RUN pip3 install ska-ost-sim-low-station-beam --extra-index-url https://artefact.skao.int/repository/pypi-internal/simple
RUN pip3 install -U ipython jupyter
