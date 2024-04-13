# ska_ost_sim_low_station_beam

A python package to simulate the station beam response of an SKA Low station.
Station beam responses can be simulated for both full stations (with all 256 LFAA elements)
or for substations (with a subset of the LFAA elements in a station).

Note that this package is still being developed and it can't simulate station beam
responses just yet. 

A detailed description of the various functionalities available in this package can be
found in the `docs/examples.ipynb` notebook. 

Installation
------------

We use [poetry](https://python-poetry.org/docs/basic-usage/) to manage dependencies in this project. 
You can install `ska_ost_sim_low_station_beam` with

```bash
git clone https://gitlab.com/ska-telescope/ost/ska_ost_sim_low_station_beam.git
cd ska_ost_sim_low_station_beam
poetry install
```

Alternately, you can also install using traditional methods with
```bash
pip install ska_ost_sim_low_station_beam --extra-index-url https://artefact.skao.int/repository/pypi-internal/simple
```


This package has been tested against `python-3.9`, `python-3.10`, and `python-3.11`.

Contributing
------------

If you wish to add more features to this package, feel free to issue a merge request.