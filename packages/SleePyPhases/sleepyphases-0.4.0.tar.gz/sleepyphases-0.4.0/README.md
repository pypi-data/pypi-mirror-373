# Arousal Detector

Machine learning based arousal detection during sleep. This project uses [pyPhases](https://pypi.org/project/pyPhases/).

# Setup

## Dataset

You need to download a valid dataset for example [SHHS](https://sleepdata.org/datasets/shhs) or [MESA](https://sleepdata.org/datasets/mesa).

Supported dataset and their identifiers:

- [SHHS](https://sleepdata.org/datasets/shhs): `shhs` (SHHS1)
- [MESA](https://sleepdata.org/datasets/mesa): `mesa`
- [MrOS](https://sleepdata.org/datasets/mros/): `mros`
- TSM: `tsm` (local dataset from [Universitätsklinikum Carl Gustav Carus Dresden](https://www.uniklinikum-dresden.de/de))

## Setup dataset path

Depending on the dataset following config Values need to be specified: `shhs-path`, `mros-path`, `mesa-path`, `tsm-path`

It is recommended to set up a file `userconfigs/local.yml` with following configuration values:

```yaml
Extract:
  useMultiThreading: True  # "True" default value
  validatDataset: True  # "True" default value
BuildDataset:
  useMultiThreading: True  # "True" default value

shhs-path: D:/datasets/SHHS/
mros-path: D:/datasets/MrOs/mros/
mesa-path: D:/datasets/MESA/
tsm-path: D:/datasets/TSM/records
```

## Local execution
### Requirements

- Python >= `3.5`
- [PyTorch](https://pytorch.org/get-started/locally/)
- packages in `requirements.txt`: `pip install -r requirements.txt`

### Train a Model

There are default Configs in the folder `configs/datasets` for each dataset. The file `configs/datasets/[dataset identifier]/init.yaml` loads the default values to execute further commands.

To test the Training process, you can execute the training only using few recordings:

`phases run -c userconfigs/local.yaml,configs/datasets/shhs/init.yaml,configs/datasets/shhs/version-debug.yaml Training`

If `phases` is not installed in your path you can use `python -m phases ...` instead.

This command starts the extraction of the dataset and the training process.

## Docker

## Docker compose

```yaml
version: "3.7"

services:
  apptorch:
    image: registry.gitlab.com/tud.ibmt.public/pyphases/arousaldetector/torch
    entrypoint: python -m phases
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      # you can use this to reference your local datasets
      - ./datasets/:/app/datasets
      # just a placeholder for your custom configs
      - ./userconfigs:/app/userconfigs
    # required for gpu execution using a nvidia gpu
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: [ '0' ]
              capabilities: [ gpu ]
```
Create a local config file in `userconfigs/local.yml` and add the following content:

```yaml
useLoader: shhs
shhs-path: /app/datasets/SHHS1
```

Now you can test the project using docker compose:

`docker compose run apptorch -c userconfigs/local.yml run Training`

Run the complete Training:

`docker compose run apptorch -c userconfigs/local.yml,configs/shhs.predefined.yaml run Training`

# Usage

## Create Dataset

### Create a new Dataset using

```yaml
# config.yml
# setup shhs

shhs-path: ./datasets/shhs
useLoader: shhs

dataversion:
  version: All
  groupBy: Null
  recordIds: Null

# export specification
export:
  annotations:
    - apnea
    - arousal
    - limb
    - sleepStage
    - light
  channels:
    - [EEG]
    - [EEG Ch2]
    - [EOG(L), EOG LOC-A2, E1-M2, "E1:M2"]
    - [EOG(R), EOG ROC-A1, "E2:M1"]
    - [EMG, EMG Chin, Chin1-Chin2, Chin]
    - [POSITION, Body]
    - [THOR RES, Effort THO, CHEST, RIP Thora]
    - [ABDO RES, Effort ABD, ABD, RIP Abdom]
    - [SaO2, SpO2]
    - [FLOW]

```

### single record

`phases run --set recordId=shhs1-200001 -c config.yml Export`

### full dataset

`phases run -c config.yml Export`

## Define Custom Data Loading




# Development

## Change dataset

make sure the right paths are set in `project.yaml` to use the dataset.

`phases run -c configs/datasets/[DATASET]/init.yml run Training`

for example:

`phases run -c configs/datasets/mesa/init.yml run Training`


## Change Model

## Add new metric to scoring

Adding a new metric for the validation/evaluation you register a new metric using the Scorer class from `pyPhasesML`.

```python
from pyPhasesML import Scorer
# ...
class Setup(Phase):
    def prepareConfig(self):
        # ...

        def scoreRecord(truth, prediction):
            # calculate the score for single record
            return 1.0

        def scoreAllSamples(truth, prediction):
            # calculate the score for all samples
            return 1.0

        Scorer.registerMetric("score1", scoreRecord, scoreAllSamples)
```

Update config:

```yaml
# add metric to training validation

trainingParameter:
  validationMetrics:
    - accuracy
    - score1
# add metric to evaluation

eval:
  metrics:
  - kappa
  - score1
```

## Run Tests

`phases test test`

Using docker: `docker compose run --rm phases-test test test -v`

## Create debug docker container

`docker compose run --rm --entrypoint bash phases-test`

## pyPhase structure
| Complete                           | Training with pyPhases                               |
|------------------------------------|------------------------------------------------------|
| ![Structure](assets/structure.svg) | ![PyPhases-Structure](assets/structure-pyPhases.svg) |


## Apnea

Use all channels: `configs/datasets/shhs/channels.yaml`
Change Classification: `configs/aasm-apnea.yaml`
Use Hotencoding for model inputs: `configs/hotEncode.yaml`
Change Model: `configs/models/apneaunet.yaml`

Training: `phases run -c userconfigs/local.yml,configs/datasets/shhs/init.yaml,configs/datasets/shhs/version-debug.yaml,configs/datasets/shhs/channels.yaml,configs/aasm-apnea.yaml,configs/hotEncode.yaml,configs/models/apneaunet.yaml Training`