# ska_ost_sim_low_station_beam

A python package to simulate the station beam response of an SKA Low station.
Station beam responses can be simulated for both full stations (with all 256 LFAA elements)
or for substations (with a subset of the LFAA elements in a station).

Please contact SKA if you have comments/questions.

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
We use `black` and `isort` to format our code. Make sure to check the formatting with
```bash
make python-lint
```