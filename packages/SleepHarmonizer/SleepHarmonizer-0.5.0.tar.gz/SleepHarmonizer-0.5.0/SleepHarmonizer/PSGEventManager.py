from pyPhasesRecordloader import EventManager


class PSGEventManager(EventManager):
    """
    Harmonized event names for PSG data.
    """
    INDEX_WAKE = 2
    INDEX_NREM1 = 4
    INDEX_NREM2 = 8
    INDEX_NREM3 = 16
    INDEX_REM = 32

    INDEX_APNEA_OBSTRUCTIVE = 2
    INDEX_APNEA_HYPO = 4
    INDEX_APNEA_CENTRAL = 8
    INDEX_APNEA_MIXED = 16
    INDEX_APNEA_PARTIALOBSTRUCTIVE = 32
    INDEX_APNEA_HYPOVENTILATION = 64
    INDEX_APNEA_CHEYNESTOKESBREATH = 128

    INDEX_AROUSAL_RERA = 2
    INDEX_AROUSAL_SPONTANEOUS = 4
    INDEX_AROUSAL_PLM = 8
    INDEX_AROUSAL_SNORE = 16
    INDEX_AROUSAL_BRUXISM = 32
    INDEX_AROUSAL_NOISE = 64
    INDEX_AROUSAL = 128
    INDEX_AROUSAL_ASDA = 256
    INDEX_AROUSAL_CHIN = 512
    INDEX_AROUSAL_LIMB = 8

    INDEX_LEGMOVEMENT = 8
    INDEX_LEGMOVEMENT_LEFT = 2
    INDEX_LEGMOVEMENT_RIGHT = 4

    def __init__(self):
        eventGroups = {
            "sleepStage": ["undefined", "W", "N1", "N2", "N3", "R"],
            "bodyposition": [
                "undefinedBodyPosition",
                "Up",
                "Supine",
                "Left",
                "Prone",
                "Right",
            ],
            "apnea": [
                "noneApnea",
                "resp_obstructiveapnea",
                "resp_hypopnea",
                "resp_centralapnea",
                "resp_mixedapnea",
                "resp_partialobstructive",
                "resp_hypoventilation",
                "resp_cheynestokesbreath",
                "resp_hypopnea_obstructive",
                "resp_hypopnea_central",
            ],
            "arousal": [
                "noneArousal",
                "arousal_rera",
                "arousal_spontaneous",
                "arousal_plm",
                "arousal_snore",
                "arousal_bruxism",
                "arousal_noise",
                "arousal",
                "arousal_asda",  # shhs/mros: American Sleep Disorders Association
                "arousal_chin",  # shhs
                "arousal_limb",
            ],
            "grapho": [
                "no-grapho",
                "AlphaActivity-eeg",
                "RapidEyeMovement",
                "SlowEyeMovement",
                "Spindle-eeg",
            ],
            "fail": [  # maximal 32 for 32bit integer
                "workingSignal",
                "fail-channel0",
                "fail-channel1",
                "fail-channel2",
                "fail-channel3",
                "fail-channel4",
                "fail-channel5",
                "fail-channel6",
                "fail-channel7",
                "fail-channel8",
                "fail-channel9",
                "fail-channel10",
                "fail-channel11",
                "fail-channel12",
                "fail-channel13",
                "fail-channel14",
                "fail-channel15",
                "fail-channel16",
                "fail-channel17",
                "fail-channel18",
                "fail-channel19",
                "fail-channel20",
                "fail-channel21",
                "fail-channel22",
                "fail-channel23",
                "fail-channel24",
                "fail-channel25",
                "fail-channel26",
                "fail-channel27",
                "fail-channel28",
                "fail-channel29",
                "fail-channel30",
            ],
            "limb": ["noneLegmovement", "LegMovement-Left", "LegMovement-Right", "LegMovement"],
            "spo2": [
                "spo2_desaturation",
                "spo2_meanPerEpoch",
                "spo2_minPerEpoch",
                "spo2_Lower90",
                "spo2_Lower80",
            ],
            "cardiac": [
                "hr_rise",
                "sinus_tachycardia",
            ],
            "light": [
                "lightOff",
                "lightOn",
            ],
        }
        super().__init__(eventGroups)
