# Sleep Harmonizer

Harmonize polysomnograms and their annotations. Create a new harmonized dataset of [EDF+-Files](https://www.edfplus.info/specs/edfplus.html). Easily extend existing sources such as public datasets and PSG software vendors.

Currently supported:

- [Dataset SHHS](https://sleepdata.org/datasets/shhs)
- [Dataset MESA](https://sleepdata.org/datasets/mesa)
- [Dataset MrOS](https://sleepdata.org/datasets/mros)
<!-- - [Dataset Physionet ](https://physionet.org/content/challenge-2018/1.0.0/) -->
- [Vendor: Philips - Alice 6](https://www.philips.ie/healthcare/product/HC1063315/alice-6-ldx-diagnostic-sleep-system)
- [Vendor: SOMNOmedics - Domino](https://somnomedics.de/en/solutions/sleep_diagnostics/diagnostic_software/domino/)

## Local Setup

Local setup requires the cloned git repository and a python version `>= 3.8` (tested with `3.11.9`)

Run `pip install -r requirements.txt`.

Test local setup with `phases --version` (if the `phases` command is not available, use `python -m phases` instead)

## Docker Setup

To download and test the docker image, run `docker run registry.gitlab.com/sleep-is-all-you-need/sleep-harmonizer --version`.

## Usage

Some configuration is required to use the sleep harmonizer. You can add additional configuration files within the run command like this

`phases run -c file1.yml,configs/file2.yml Export`.

For the next part we assume you have a configuration file called `config.yml` in the root directory.

You can run the examples with `phases run -c config.yml Export` after updating your config file.

### Specify Source: Public Datasets (SHHS)

You need to specify the path and tell the tool that you want to use the correct data loader.

```yaml
shhs-path: ./datasets/shhs
useLoader: shhs
```

### Specify Source: Vendor (Alice 6)

You need to define a new dataloader that uses a specific RecordLoader (e.g. `loader.myLoader.dataset.loadername`) that needs to be registered. See [available recordloaders]()

```yaml
loader:
  my-alice:
    dataBase: myalice
    dataIsFinal: True # there will be no more updates to the data, and the record metadata can be stored
    dataBaseVersion: 0.0.1 # needs to be raised every time new data is added

    filePath: ./datasets/custom/alice/ # path to the directory where the raw data is stored
    dataset:
      loaderName: RecordLoaderAlice # registred recordloader
      filePattern: "*" # valid files that should be considered further
      downloader:
        basePath: ./datasets/custom/alice/ # path to the directory where the raw data is stored
        canReadRemote: True # if the data needs to be copied locally or the downloader.basePath can be used
        type: allFromFolder # a valid downloader type
        listFilter: acq # filters the file-list compatible with str.find(listFilter)
        extensions: [.edf, .rml] # allowed extensions, the first one is used for the id-pattern
        force: False # force download the files
        idPattern: .*/(.*[^-T]).edf # this pattern will be used to extract the record id from the filename

    # the channels that should be extracted from the edf files
    sourceChannels:
      - name: EEG F3-A2
        type: eeg
      # generate a new channel that uses the first occurence of a valid flow channel
      - name: FlowSelect
        generated: True
        requiresOne: [Flow Aux1, Flow Aux2, Flow Aux4, Flow Aux5, Flow Patient]
        type: flow
      # ... add aditional channels here

    combineChannels:
      # generate a new channel that uses the first occurence of a valid flow channel
      - name: FlowSelect
        combineType: select
        type: flow
        channel: [Flow Aux1, Flow Aux2, Flow Aux4, Flow Aux5, Flow Patient]


useLoader: my-alice
```

### Filter the records

You can filter the records by using the `dataversion` config.

**If you allready have a filtered recordlist** 
```yaml
dataversion:
  version: myStudy1 # giving a name is optional, but is easier to navigate the generated files
  recordIds:
    - record1
    - record2
    - record3
    # ...
```

**Filtering the metadata**
```yaml
dataversion:
  version: myStudy2
  minimalSamplingRate:
    eeg: 200 # all eeg channels require to have at least 200 HZ sampling rate
    emg: 200
    mic: 200
  filterQuery: ahi < 15 and tst > 5 # filter by metada query (compatible with pandas.Dataframe query)
```



### Declare available Channels and Annotations

To determine what channels and annotations you want in you edf files you can use the `extract` options:

- `annotations`: The main groups `apnea`, `arousal`, `limb`, `sleepstage` and `ligt` or any subgroup such as `resp_obstructiveapnea` A complete list can be found in `SleepHarmonizer/PSGEventManager.py`.
- `channels`: Each entry is a list of channel names, the final channel name is the first channel specified in the list. The first existing channel will be used for the EDF file

```yaml
export:
  annotations:
    - apnea
    - arousal
    - limb
    - sleepStage
    - light
  channels:
    - [EEG, EEG F3-A2]
    - [EEG Ch2, EEG F4-A1]
    - [EOG(L), EOG LOC-A2, E1-M2, "E1:M2"]
    - [EOG(R), EOG ROC-A1, "E2:M1"]
    - [EMG, EMG Chin, Chin1-Chin2, Chin]
    - [POSITION, Body]
    - [THOR RES, Effort THO, CHEST, RIP Thora]
    - [ABDO RES, Effort ABD, ABD, RIP Abdom]
    - [SaO2, SpO2]
    - [FLOW, FlowSelect]
    - [Leg 1]
    - [Leg 2]
```


### Manipulate the signals

You can apply signal processing using the `preprocessing` config entry. All available steps are defined in `SleepHarmonizer/SignalPreprocessing.py` as methods. You cann also add a new method and use the method-name in the config.

```yaml
preprocessing:
  targetFrequency: 8 # final sampling rate (if some sort of resampling is aplied as step)
  stepsPerType:
    eeg: [resampleFIR] # will execute the resampleFIR method on all eeg channels (defined in SignalPreprocessing.py)
    eog: [resampleFIR]
    emg: [resampleFIR]
    body: [positionAlice, resampleSimple]
    mic: [resampleFIR]
    effort: [resample,]
    sao2: [resampleSimple]
    flow: [resample]
```

### Complete example

```yaml

# folder where to write the edf files
export-path: data/export/

shhs-path: ./datasets/shhs
useLoader: shhs

dataversion:
  groupBy: Null
  recordIds: Null

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

### Execute the Export


Depending on your phases installation execute:

`phases run -c config.yml Export`

Expected output:

```bash
[phases] Phases v1.0.6 with pyPhases v1.2.6 (Log level: LogLevel.INFO)
[Export] RUN phase Export: Export
[Project] Data allDBRecordIdsSHHS1-70d366c5--current was not found, try to find phase to generate it
[Project] Data metadataSHHS1--current was not found, try to find phase to generate it
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:05<00:00,  1.91it/s]
  0%|                                                                                                                                                    | 0/10 [00:00<?, ?it/s]
[RecordLoaderSHHS] Added 14 signals, ignored: []
[Signal] Unkown type of signal 'hr'
[SHHSAnnotationLoader] Load xml file ./datasets/shhs/polysomnography/annotations-events-nsrr/shhs1/shhs1-200004-nsrr.xml
...
[SignalPreprocessing] Signaltype SignalType.FLOW for signal FLOW has no preprocessing steps (defined in preprocessing.stepsPerType.[type])
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:58<00:00,  5.82s/it]
```
And new created edf files in `data/export`.
