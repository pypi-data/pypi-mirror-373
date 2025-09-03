import csv
from pathlib import Path

from pyPhases.util.Logger import classLogger


@classLogger
class DominoErgLoader:
    txtEncoding = "utf-16"

    def getTimeValue(self, timeValue, unit="m"):
        # in minutes to make it compatible with Alice
        h, m, s = timeValue.split(":")
        value = int(s) + int(m) * 60 + int(h) * 60 * 60
        if unit == "m":
            value /= 60
        elif unit == "h":
            value /= 60
        elif unit == "s":
            pass
        else:
            raise Exception("not a valid time unit")
        return value

    def calculateMetaData(self, allValues):
        # default
        supineSleepDuration = (self.getTimeValue(allValues["SUPINE_SLEEP_DURATION"]))
        nonSupineSleepDuration = self.getTimeValue(allValues["PRONE_SLEEP_DURATION"]) + self.getTimeValue(allValues["LEFT_SLEEP_DURATION"]) +self.getTimeValue(allValues["RIGHT_SLEEP_DURATION"])
        tibDuration = self.getTimeValue(allValues["TIB_DURATION"])
        remDuration = self.getTimeValue(allValues["REM_DURATION"])
        nonRemDuration = self.getTimeValue(allValues["NONREM_DURATION"])
        apneaHyponea =float(allValues["APNOEA_SLEEP_NUMBER"])+                    float(allValues["HYPOPNOEA_SLEEP_NUMBER"])
        data = {
            "ahiRuecken": ((float(allValues["APNOEA_SUPINE_NUMBER"]) + float(allValues["HYPOPNOEA_SUPINE_NUMBER"])) / supineSleepDuration) if supineSleepDuration > 0 else 0,
            "ahiKeinRuecken": ((
                    float(allValues["APNOEA_PRONE_NUMBER"]) + 
                    float(allValues["APNOEA_LEFT_NUMBER"]) + 
                    float(allValues["APNOEA_RIGHT_NUMBER"]) + 
                    float(allValues["HYPOPNOEA_PRONE_NUMBER"]) +
                    float(allValues["HYPOPNOEA_LEFT_NUMBER"]) +
                    float(allValues["HYPOPNOEA_RIGHT_NUMBER"])
                ) / nonSupineSleepDuration) if nonSupineSleepDuration > 0 else 0,
            "ahiRem": ((
                float(allValues["APNOEA_REM_NUMBER"]) + 
                float(allValues["HYPOPNOEA_REM_NUMBER"])
                ) / remDuration) if remDuration > 0 else 0,
            "ahiNrem": ((
                float(allValues["APNOEA_NONREM_NUMBER"]) + 
                float(allValues["HYPOPNOEA_NONREM_NUMBER"])
                ) / nonRemDuration) if nonRemDuration > 0 else 0,
            "percentageApneaCentral":
                (float(allValues["CENTRALE_SLEEP_NUMBER"]) / 
                apneaHyponea * 100) if apneaHyponea > 0 else 0,
            "rdiRuecken": ((
                float(allValues["APNOEA_SUPINE_NUMBER"]) + 
                float(allValues["HYPOPNOEA_SUPINE_NUMBER"]) +
                float(allValues["RERA_SUPINE_NUMBER"])
                ) / supineSleepDuration) if supineSleepDuration > 0 else 0,
            "rdiKeinRuecken": ((
                float(allValues["APNOEA_PRONE_NUMBER"]) + 
                float(allValues["APNOEA_LEFT_NUMBER"]) +
                float(allValues["APNOEA_RIGHT_NUMBER"]) +
                float(allValues["HYPOPNOEA_PRONE_NUMBER"]) +
                float(allValues["HYPOPNOEA_LEFT_NUMBER"]) +
                float(allValues["HYPOPNOEA_RIGHT_NUMBER"]) +
                float(allValues["RERA_PRONE_NUMBER"]) +
                float(allValues["RERA_LEFT_NUMBER"]) +
                float(allValues["RERA_RIGHT_NUMBER"])
                ) / nonSupineSleepDuration) if nonSupineSleepDuration > 0 else 0,
            "rdiRem": ((
                float(allValues["APNOEA_REM_NUMBER"]) + 
                float(allValues["HYPOPNOEA_REM_NUMBER"]) +
                float(allValues["RERA_REM_NUMBER"])
                ) / remDuration) if remDuration > 0 else 0,
            "rdiNrem": ((
                float(allValues["APNOEA_NONREM_NUMBER"]) + 
                float(allValues["HYPOPNOEA_NONREM_NUMBER"]) +
                float(allValues["RERA_NONREM_NUMBER"])
                ) / nonRemDuration) if nonRemDuration > 0 else 0,
            # "percentageSpO2Lower80": ((
            #     self.getTimeValue(allValues["TIME_90_SPO2"], unit="m") + 
            #     self.getTimeValue(allValues["TIME_90_SPO2_WAKE"], unit="m")
            #     ) / tibDuration) if tibDuration > 0 else 0,
        }
        data.update({
            "ratioAhiRuecken": (data["ahiRuecken"] / data["ahiKeinRuecken"]) if data["ahiKeinRuecken"] > 0 else 0,
            "ratioAhiRem": (data["ahiRem"] / data["ahiNrem"]) if data["ahiNrem"] > 0 else 0,
            "ratioRdiRuecken": (data["rdiRuecken"] / data["rdiKeinRuecken"]) if data["rdiKeinRuecken"] > 0 else 0,
            "ratioRdiRem": (data["rdiRem"] / data["rdiNrem"]) if data["rdiNrem"] > 0 else 0,
        })
        return data
    
    def getMetaDataFromFile(self, reportfile, rowIds):
        data = {}
        extracedIds = []
        with open(reportfile, newline="", encoding=DominoErgLoader.txtEncoding) as csvfile:
            rows = csv.reader(csvfile, delimiter="=")
            allData = {}
            for row in rows:
                # row = row.
                if len(row) < 2:
                    continue
                id, value = row[0:2]
                value = value.split(";")[-1]
                allData[id] = value
                if id in rowIds:
                    extracedIds.append(id)
                    if value != "":
                        nameId = rowIds[id]
                        if rowIds[id] == "":
                            nameId = "domino%s" % (id)

                        # check for duration
                        if ":" in value:
                            value = self.getTimeValue(value)
                        try:
                            if isinstance(value, str) and ("pid" in value or id == "PATIENTDATA_MONTAGE_NAME"):
                                data[nameId] = value
                            # data.append((nameId, float(value), ""))
                            else:
                                data[nameId] = float(value)
                        except Exception as ex:
                            self.logWarning("Failed to convert folling Line to float %s:%s value: %s: %s" % (reportfile, id, value, ex))
        notFound = set(rowIds) - set(extracedIds)
        if len(notFound) > 0:
            self.logWarning("export of following ids not found: %s" % notFound)
        data.update(self.calculateMetaData(allData))
        return data

    # relevant rows where exported from the report files
    relevantRows = {
        "SLEEP_DURATION": "tst",
        "TIB_DURATION": "tib",
        "SLEEP_PERIODE_TOTAL": "spt",
        "SLEEPLATENCY": "sLatency",
        "REM_LATENCY": "rLatency",
        "WAKE_AFTER_SLEEP_ON": "waso",
        "SLEEP_EFFICIENCY": "sEfficiency",
        "WAKE_PERCENTAGE": "percentageW",
        "STAGE1_PERCENTAGE": "percentageN1",
        "STAGE2_PERCENTAGE": "percentageN2",
        "STAGE3_PERCENTAGE": "percentageN3",
        "REM_PERCENTAGE": "percentageR",
        "MA_TOTAL_SLEEP_NUMBER": "countArousal",
        "MA_TOTAL_SLEEP_INDEX": "indexArousal",
        "AVERAGE_HF": "meanHrSleep",
        "MAX_HF": "maxHrSleep",
        "MIN_HF": "minHrSleep",
        "PLM_SLEEP_NUMBER": "countPlms",
        "MA_PLM_SLEEP_NUMBER": "countPlmsArousal",
        "PLM_SLEEP_INDEX": "indexPlms",
        "MA_PLM_SLEEP_INDEX": "indexPlmsArousal",
        "OBSTRUCTIVE_SLEEP_NUMBER": "countApneaObstructive",
        "MIXED_SLEEP_NUMBER": "countApneaMixed",
        "CENTRALE_SLEEP_NUMBER": "countApneaCentral",
        "HYPOPNOEA_SLEEP_NUMBER": "countHypopnea",
        "APNOEA_SLEEP_INDEX": "indexApnea",
        "HYPOPNOEA_SLEEP_INDEX": "indexHypopnea",
        "AHI_SLEEP": "ahi",
        "RERA_SLEEP_NUMBER": "countRera",
        "RERA_SLEEP_INDEX": "indexRera",
        "RDI_SLEEP": "rdi",
        "NUMBER_DESAT": "countOxyDesat",
        "DESAT_INDEX": "indexOxyDesat",
        "AVERAGE_SPO2": "meanSpO2",
        "MIN_SPO2": "minSpO2",
        "AVERAGE_SPO2_REM": "meanSpO2Rem",
        "AVERAGE_SPO2_NONREM": "meanSpO2Nrem",
        "SNORE_TOTAL_EPISOD": "percentageSnore",
        "PATIENTDATA_ID": "patient",
        "PATIENTDATA_CASE_ID": "case",
        "PATIENTDATA_BMI": "bmi",
        "PATIENTDATA_MONTAGE_NAME": "psg_setup",
        "SLEEP_PROFILE_MANUALLY_SCORED": "manualScored",
    }
