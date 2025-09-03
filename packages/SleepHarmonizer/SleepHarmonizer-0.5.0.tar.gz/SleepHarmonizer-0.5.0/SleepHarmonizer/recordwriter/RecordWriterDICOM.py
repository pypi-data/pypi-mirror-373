from datetime import datetime
from typing import List
import os
import numpy as np
import pydicom
from pydicom.dataset import Dataset
from SleepHarmonizer.PSGEventManager import PSGEventManager
from pyPhases.util.Logger import classLogger
from pyPhasesRecordloader import Event, Signal
from pydicom.fileset import FileSet

from SleepHarmonizer.recordwriter.RecordWriter import RecordWriter


@classLogger
class RecordWriterDICOM(RecordWriter):
    def _toDecimalString(self, number):
        return f"{float(number):.10g}"
    def getSubjectId(self):
        pc = self.metaData["patientCode"] if "patientCode" in self.metaData else "unknown"
        return f"sub-{pc}"

    def getSessionId(self):
        pc = self.metaData["sessionId"] if "sessionId" in self.metaData else "1"
        return f"ses-{pc}"

    def getFilePath(self, recordName):
        bids_path = os.path.join(self.filePath, self.getSubjectId(), self.getSessionId())

        return bids_path

    def getTaskFilePath(self, recordName, subject_id, session, sigType):
        basePath = self.getFilePath(recordName)
        file_name = f"{subject_id}_{session}_task-sleep_{sigType}.dcm"

        return f"{basePath}/{file_name}"

    def writeSignals(
        self, recordName, channels, events=None, startTime=None, signalIsDigital=False
    ):
        if events is None:
            events = []

        # Store study UID for SR reference
        self.study_instance_uid = pydicom.uid.generate_uid()

        # Split channels by modality
        channelsByType = {
            "eeg": [],
            "eog": [],
            "emg": [],
            "ecg": [],
            "sao2": [],
            "body": [],
            "effort": [],
            "flow": [],
            "mic": [],
            "resp": [],
        }

        channelMap = {
            "flow": "resp",
            "effort": "resp",
        }

        for ch in channels:
            if ch.typeStr in channelsByType:
                channel = channelMap[ch.typeStr] if ch.typeStr in channelMap else ch.typeStr
                channelsByType[channel].append(ch)

        # SOP Overview: https://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_b.5.html
        sopMap = {
            "eeg": "1.2.840.10008.5.1.4.1.1.9.7.4",
            "eog": "1.2.840.10008.5.1.4.1.1.9.7.3",
            "emg": "1.2.840.10008.5.1.4.1.1.9.7.2",
            "ecg": "1.2.840.10008.5.1.4.1.1.9.1.2",
            "body": "1.2.840.10008.5.1.4.1.1.9.8.1",
            # "effort": "1.2.840.10008.5.1.4.1.1.9.6.1",
            "resp": "1.2.840.10008.5.1.4.1.1.9.6.2",
            "mic": "1.2.840.10008.5.1.4.1.1.9.4.2",
            "sao2": "1.2.840.10008.5.1.4.1.1.9.5.1",
        }

        subject_id = self.getSubjectId()
        session = self.getSessionId()
        fs = FileSet()
        psg_em = PSGEventManager()
        groups = psg_em.getEventGroupMap()
        for sigType, sop in sopMap.items():
            if len(channelsByType[sigType]) == 0:
                continue

            eeg_dataset = self._create_dataset(
                sop_class_uid=sop,
                channels=channelsByType[sigType],
                events=events,
                modality=sigType,
            )
            
            match sigType:
                case "eeg" | "eog":
                    sig_groups = ["sleepStage", "arousal", "grapho"]
                case "emg":
                    sig_groups = ["limb"]
                case "ecg":
                    sig_groups = ["sleepStage", "arousal", "grapho", "limb", "apnea", "spo2"]
                    # sig_groups = ["cardiac"]
                case "effort":
                    sig_groups = ["apnea"]
                case "resp":
                    sig_groups = ["apnea", "spo2"]

            sig_groups.append("light")
            dic_events = [e for e in events if groups[e["name"]] in sig_groups]
            self._add_events_to_dataset(eeg_dataset, dic_events)

            # Get BIDS-compliant file paths (requires patient info)
            file_path = self.getTaskFilePath(recordName, subject_id, session, sigType)
            if not Path(file_path).parent.exists():
                Path(file_path).parent.mkdir(parents=True)
            eeg_dataset.save_as(file_path, write_like_original=False)
            fs.add(file_path)

        # Write SR if events exist
        if events:
            sr_path = self.writeAnnotationSR(recordName, events)
            fs.add(sr_path)

        fs.write(self.getFilePath(recordName) + ".dcm")
    
    def _create_basedataset(self, sop):
        ds = Dataset()
        ds.SOPClassUID = sop
        ds.StudyInstanceUID = self.study_instance_uid
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        ds.SOPInstanceUID = pydicom.uid.generate_uid()
        ds.StudyDate = self.metaData["start"].strftime("%Y%m%d")
        ds.StudyTime = self.metaData["start"].strftime("%H%M%S.%f")
        ds.StudyID = "acq-1"
        ds.AccessionNumber = "123456789"
        ds.SeriesNumber = 1
        ds.ReferringPhysicianName = "Unknown"
        # ds.PerformedProcedureCodeSequence = self._create_code_sequence('LN', '28633-6', ' Polysomnography (sleep) study')

        # when Content was create (after manual scoring)
        ds.ContentDate = self.metaData["start"].strftime("%Y%m%d")
        ds.ContentTime = self.metaData["start"].strftime("%H%M%S.%f")
        ds.InstanceNumber = 1

        # Patient information
        ds.PatientName = self.metaData["patient"] if "patient" in self.metaData else self.metaData["patientName"]
        ds.PatientID = self.metaData["patientCode"]
        ds.PatientBirthDate = self.metaData["birthdate"]
        ds.PatientSex = self.metaData["sex"]

        # Equipment information
        for k, v in self.metaData["dicom"].items():
            setattr(ds, k, v)

        ds.is_little_endian = True
        ds.is_implicit_VR = True
        return ds

    def _create_dataset(self, sop_class_uid, channels, events, modality):
        ds = self._create_basedataset(sop_class_uid)
        
        ds.Modality = modality.upper()

        dateTime = self.metaData["start"]
        ds.AcquisitionDateTime = dateTime
        ds.AcquisitionContextSequence = []

        # Add waveform data
        self._add_channels_to_dataset(ds, channels)

        return ds

    # def _create_sidecar_json(self, dcm_path, channels, startTime):
    #     import json

    #     sidecar = {
    #         "TaskName": "sleep",
    #         "SamplingFrequency": channels[0].frequency,
    #         "RecordingDuration": len(channels[0].signal) / channels[0].frequency,
    #         "RecordingType": "continuous",
    #         "StartTime": startTime.isoformat() if startTime else None,
    #         "Manufacturer": "SleepHarmonizer",
    #         "PowerLineFrequency": 50,
    #         "SoftwareFilters": "n/a",
    #         "HardwareFilters": "n/a",
    #         "ChannelCount": len(channels),
    #         "Channels": {
    #             ch.name: {"sampling_frequency": ch.frequency, "units": ch.dimension, "type": ch.name.split("_")[0]}
    #             for ch in channels
    #         },
    #     }

    #     json_path = dcm_path.replace(".dcm", ".json")
    #     with open(json_path, "w") as f:
    #         json.dump(sidecar, f, indent=4)

    def _add_channels_to_dataset(self, dataset, channels):
        dataset.WaveformSequence = []

        for channel in channels:
            waveform_seq = Dataset()
            waveform_seq.MultiplexGroupLabel = channel.name
            waveform_seq.MultiplexGroupTimeOffset = 0
            waveform_seq.WaveformOriginality = "ORIGINAL"
            waveform_seq.NumberOfWaveformChannels = 1
            waveform_seq.NumberOfWaveformSamples = len(channel.signal)
            waveform_seq.SamplingFrequency = channel.frequency

            # Calculate bits needed
            diff = channel.digitalMax - channel.digitalMin
            required_bits = np.ceil(np.log2(diff))
            digital_center_diff = (channel.digitalMax - channel.digitalMin + 1) / 2 + channel.digitalMin

            # Set bit depth
            if required_bits <= 16:
                bits = 16
                sample_interp = "SS"
            else:
                bits = 32
                sample_interp = "SL"
            # Channel Source Sequence
            chan_src_seq = Dataset()
            chan_src_seq.CodeMeaning = channel.name

            # Channel definition
            chan_def = Dataset()
            chan_def.ChannelLabel = channel.name
            chan_def.WaveformBitsStored = bits
            chan_def.ChannelSourceSequence = [chan_src_seq]

            # Add sensitivity units
            unit_map = {
                "uV": ("μV", "microvolts"),
                "μV": ("μV", "microvolts"),
                "mV": ("mV", "millivolts"),
                "%": ("%", "percent"),
                "cmH2O": ("cm[H2O]", "centimeters of water"),
                "mmHg": ("mm[Hg]", "millimeters of mercury"),
                "BPM": ("/min", "beats per minute"),
                "bpm": ("/min", "beats per minute"),
                "Hz": ("Hz", "hertz"),
                "°C": ("Cel", "degrees Celsius"),
                "celsius": ("Cel", "degrees Celsius"),
                "SpO2": ("%", "oxygen saturation percentage"),
                "L/min": ("L/min", "liters per minute"),
                "mL/min": ("mL/min", "milliliters per minute"),
                "V": ("V", "volts"),
                "A": ("A", "amperes"),
                "Ohm": ("Ohm", "ohms"),
                "g": ("g", "grams"),
                "kg": ("kg", "kilograms")
            }
            
            if channel.dimension in unit_map:
                ucum_code, description = unit_map[channel.dimension]
                chan_def.ChannelSensitivityUnitsSequence = self._create_code_sequence("UCUM", ucum_code, description)

            # Calculate scaling factors
            digital_to_physical = (channel.physicalMax - channel.physicalMin) / (channel.digitalMax - channel.digitalMin)
            baseline = (channel.physicalMax + channel.physicalMin) / 2 + digital_center_diff * digital_to_physical

            # chan_def.ChannelSensitivity = digital_to_physical
            chan_def.ChannelSensitivity =  self._toDecimalString(digital_to_physical)

            chan_def.ChannelBaseline = baseline
            chan_def.ChannelSampleSkew = 0
            chan_def.ChannelSensitivityCorrectionFactor = 1

            waveform_seq.ChannelDefinitionSequence = [chan_def]
            waveform_seq.WaveformBitsAllocated = bits
            waveform_seq.WaveformSampleInterpretation = sample_interp
            waveform_seq.WaveformData = (channel.signal - digital_center_diff).astype(f"int{bits}").reshape(-1, 1).tobytes()

            dataset.WaveformSequence.append(waveform_seq)

    def _add_events_to_dataset(self, dataset, events, mainCodeSeq=None):
        mainCodeSeq = ("DSM", "130860", "Pattern Event") if mainCodeSeq is None else mainCodeSeq
        dataset.WaveformAnnotationSequence = []
        for event in events:
            annotation = Dataset()
            annotation.ReferencedWaveformChannels = [0]
            if event["duration"] == 0:
                annotation.TemporalRangeType = "POINT"
                annotation.ReferencedTimeOffsets = [self._toDecimalString(event["start"])]
            else:
                annotation.TemporalRangeType = "SEGMENT"
                annotation.ReferencedTimeOffsets = [
                    self._toDecimalString(event["start"]), 
                    self._toDecimalString(event["end"])
                ]
            # annotation.ReferencedSamplePositions = [
            #     int(event["start"]), 
            #     int(event["start"] + event["duration"])
            # ]
            # annotation.ReferencedSamplePositions = [
            #     int(event["start"])
            # ]
            # annotation.TemporalRangeType = "POINT"
            # annotation.ReferencedTimeOffsets = [self._toDecimalString(event["start"])]
            # annotation.UnformattedTextValue = event["name"]
            codeSeq = self.getEventCodeSequence(event["name"])
            if codeSeq is None:
                name = event["name"]
                self.logError(f"Codesequence not found for event '{name}'")
                continue
            annotation.ConceptNameCodeSequence = self._create_code_sequence(*codeSeq)
            annotation.ConceptCodeSequence = self._create_code_sequence(*codeSeq)
            # annotation.ConceptCodeSequence = self._create_code_sequence("MDC", "10:256", "P wave")
            dataset.WaveformAnnotationSequence.append(annotation)

    def writeAnnotationSR(self, recordName, events):
        # Create SR dataset
        sr = self._create_basedataset('1.2.840.10008.5.1.4.1.1.88.22')
        
        sr.Modality = 'SR'      
        sr.CompletionFlag = "PARTIAL"
        sr.VerificationFlag = "UNVERIFIED"
        sr.ValueType = "CODE"

        sr.PerformedProcedureCodeSequence = self._create_code_sequence('LN', '28633-6', ' Polysomnography (sleep) study')
        
        sr.ConceptNameCodeSequence = self._create_code_sequence('LN', '28633-6', ' Polysomnography (sleep) study')
        sr.ConceptCodeSequence = self._create_code_sequence('DCM', '130868', ' Neurophysiology Post-hoc Review Annotations')

        # DCM 130868 Neurophysiology Post-hoc Review Annotations


        ref_proc_step = Dataset()
        ref_proc_step.ReferencedSOPClassUID = '1.2.840.10008.5.1.4.1.1.9.7.4'
        ref_proc_step.ReferencedSOPInstanceUID = uid.generate_uid()
        sr.ReferencedPerformedProcedureStepSequence = [ref_proc_step]


        sr.ContentSequence = self.getEvents(events)

        # Save SR document
        sr_path = os.path.join(self.getFilePath(recordName), f"{self.getSubjectId()}_{self.getSessionId()}_annotations.sr.dcm")
        sr.save_as(sr_path, write_like_original=False)
        return sr_path

    def _create_code_sequence(self, scheme_designator, code_value, code_meaning):
        seq = Dataset()
        seq.CodeValue = code_value
        seq.CodingSchemeDesignator = scheme_designator 
        seq.CodeMeaning = code_meaning
        return [seq]
    
    def getEvents(self, events):
        
        items = [self.create_event(e["name"], e["start"], e["duration"], i) for i, e in enumerate(events)]
        items = [item for item in items if item is not None]

        return items
    
    def getEventCodeSequence(self, name):
        cid_mapping = {
            'sleepStage': {
                'W': ('MDC', '2:23672', 'Sleep stage wake'),
                'N1': ('DCM', '130834', 'Sleep stage N1'), 
                'N2': ('DCM', '130835', 'Sleep stage N2'), 
                'N3': ('DCM', '130836', 'Sleep stage N3'), 
                # 'N1': ('MDC', '2:23696', 'Sleep stage N1'), 
                # 'N2': ('MDC', '2:23704', 'Sleep stage N2'),
                # 'N3': ('MDC', '2:23712', 'Sleep stage N3'),
                'R': ('MDC', '2:23680', 'Sleep stage REM')
            },
            'apnea': {
                'resp_obstructiveapnea': ('MDC', '3:3072', 'Apnea (obstructive)'),
                'resp_centralapnea': ('MDC', '3:3072', 'Apnea (central)'),
                'resp_mixedapnea': ('MDC', '3:3072', 'Apnea (mixed)'),
                'resp_hypopnea': ('MDC', '3:3072', 'Hypopnea')
            },
            'arousal': {
                'arousal': ('MDC', '2:23800', ' Sleep arousal'),
                'arousal_rera':  ('MDC', '2:23800', ' Sleep arousal (RERA)'),
                'arousal_plm': ('MDC', '2:23800', ' Sleep arousal (Periodic limb movement)'),
                'arousal_spontaneous': ('MDC', '2:23800', ' Sleep arousal (Spontaneous)'),
                'arousal_respiratory': ('MDC', '2:23800', ' Sleep arousal (Respiratory event)'),
            },
            'limb': {
                'LegMovement-Left': ('MDC', '2:24184', 'Periodic movements of sleep'),
                'LegMovement-Right': ('MDC', '2:24184', 'Periodic movements of sleep'),
                'LegMovement': ('MDC', '2:24184', 'Periodic movements of sleep'),
                #  Periodic movements of sleep with arousals
            },
            'light': {
                'lightOff': ('MDC', 'MDC_EVT_STAT_LIGHTS_IN_ROOM_OFF', 'Lights off'),
                'lightOn': ('MDC', 'MDC_EVT_STAT_LIGHTS_IN_ROOM_ON', 'Lights on'),
            }
        }
        psg_em = PSGEventManager()
        groups = psg_em.getEventGroupMap()
        event_type = groups[name]
        if event_type in cid_mapping and name in cid_mapping[event_type]:
            return cid_mapping[event_type][name]
        
        return None


    def create_event(self, name, start_time, duration, event_number):
        
        code_sequence = self.getEventCodeSequence(name)
        
        if code_sequence is not None:
            event_container = Dataset()
            event_container.ValueType = "CONTAINER"
            event_container.RelationshipType = "CONTAINS"
            
            event_container.ConceptNameCodeSequence = self._create_code_sequence(f"11110{event_number}", "DCM", f"Sleep Apnea Episode {event_number}")
            event_container.ConceptCodeSequence = self._create_code_sequence(f"11110{event_number}", "DCM", f"Sleep Apnea Episode {event_number}")
            event_container.ContentSequence = []

            # Event Type
            event = Dataset()
            event.ValueType = "CODE"
            event.ConceptNameCodeSequence = self._create_code_sequence(code_sequence[0], code_sequence[1], code_sequence[2])
            # event.ConceptCodeSequence = _create_code_sequence(code_sequence[0], code_sequence[1], code_sequence[2])
            event_container.ContentSequence.append(event)

            # Start Time
            start_time_ds = Dataset()
            start_time_ds.ValueType = "NUM"
            start_time_ds.ConceptNameCodeSequence = self._create_code_sequence("111400", "DCM", "Start of Event")
            start_time_ds.MeasuredValueSequence = [Dataset()]
            start_time_ds.MeasuredValueSequence[0].NumericValue = start_time
            start_time_ds.MeasuredValueSequence[0].MeasurementUnitsCodeSequence = [Dataset()]
            start_time_ds.MeasuredValueSequence[0].MeasurementUnitsCodeSequence = self._create_code_sequence("s", "UCUM", "Seconds")
            event_container.ContentSequence.append(start_time_ds)

            # Duration
            duration_ds = Dataset()
            # duration_ds.RelationshipType = "HAS_OBS_CONTEXT"
            duration_ds.ValueType = "NUM"
            duration_ds.ConceptNameCodeSequence = [Dataset()]
            duration_ds.ConceptNameCodeSequence = self._create_code_sequence( "DCM", "111401", "Duration")

            duration_ds.MeasuredValueSequence = [Dataset()]
            duration_ds.MeasuredValueSequence[0].NumericValue = duration
            duration_ds.MeasuredValueSequence[0].MeasurementUnitsCodeSequence = self._create_code_sequence("UCUM", "s", "Seconds")
            event_container.ContentSequence.append(duration_ds)

            # # Referenced Waveform
            # waveform_ref = Dataset()
            # waveform_ref.ValueType = "IMAGE"
            # waveform_ref.ConceptNameCodeSequence = [Dataset()]
            # waveform_ref.ConceptNameCodeSequence[0].CodeValue = "121020"
            # waveform_ref.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
            # waveform_ref.ConceptNameCodeSequence[0].CodeMeaning = "Referenced Waveform"
            # waveform_ref.ReferencedSOPSequence = [Dataset()]
            # waveform_ref.ReferencedSOPSequence[0].ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.9.1"
            # waveform_ref.ReferencedSOPSequence[0].ReferencedSOPInstanceUID = sop_uid
            # event_container.ContentSequence.append(waveform_ref)
        else:
            return None
        
        return event_container