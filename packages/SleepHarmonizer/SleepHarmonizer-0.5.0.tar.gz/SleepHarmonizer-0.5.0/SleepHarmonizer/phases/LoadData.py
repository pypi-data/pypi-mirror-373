import pandas as pd
from pyPhases import Phase
from pyPhasesRecordloader import RecordLoader
from tqdm import tqdm

from pyPhases.Data import DataNotFound

class LoadData(Phase):
    """
    load record ids
    """

    def getMetadata(self, allRecordIds):
        recordLoader = RecordLoader.get()

        # filter non existing annotations
        metaDates = []
        metaDatesChannels = []
        for r in tqdm(allRecordIds):
            metaData = {
                "recordId": r,
                "annotationExist": recordLoader.existAnnotation(r),
                "metaDataExist": True,
            }
            metaDates.append(metaData)
            if metaData["annotationExist"]:
                try:
                    recordMetadata = recordLoader.getMetaData(r)
                except Exception as identifier:
                    metaData["metaDataExist"] = False
                    self.logError(identifier)
                    continue
                if "channels" in recordMetadata:
                    channelsMetadata = recordMetadata["channels"]
                    for cm in channelsMetadata:
                        if "recordId" not in cm:
                            cm["recordId"] = r
                        metaDatesChannels.append(cm)
                    del recordMetadata["channels"]
                metaData.update(recordMetadata)
            else:
                self.logError(f"record id {r} does not exist")

        return metaDates, metaDatesChannels

    def loadRecordIds(self, metadata, channelsMetadata):
        relevant = metadata.query("annotationExist == True")

        filterQuery = self.getConfig("dataversion.filterQuery", False)
        if filterQuery is not False:
            relevant = relevant.query(filterQuery)

        
        channelFilterQuery = self.getConfig("dataversion.channelFilterQuery", False)
        if channelFilterQuery is not False:
            filtered_channels = channelsMetadata.query(channelFilterQuery)
            
            allChannelType = self.getConfig("dataversion.allChannels", False)
            if allChannelType:
                total_type = channelsMetadata.query(f"type == '{allChannelType}'").groupby(level='recordId').size()
                valid_type = filtered_channels.groupby(level='recordId').size()
                valid_type = valid_type.reindex(total_type.index, fill_value=0)
                valid_records = total_type[total_type == valid_type].index
                relevant = relevant[relevant["recordId"].isin(valid_records)]
            else:
                # At least one channel matches (original behavior)
                relevant = relevant[relevant["recordId"].isin(filtered_channels["recordId"])]
        return relevant["recordId"].tolist()

    def generateData(self, dataName, recordId=None):
        recordLoader = RecordLoader.get()

        if dataName in ["metadata", "metadata-channels"]:
            metadataRecords = pd.DataFrame()
            metadataChannels = pd.DataFrame()
            recordLoader.setupRemoteReadOrDownload()
            if recordId is not None:
                allRecordIds = [recordId]
                mR, mC = self.getMetadata(allRecordIds)

                if dataName == "metadata":
                    return pd.DataFrame(mR)
                else:
                    return pd.DataFrame(mC)
            else:
                allRecordIds = recordLoader.getRecordList()
                if len(allRecordIds) == 0:
                    raise Exception("No records found. Check your recordLoader config and your dataversion config.")
                
                if not self.getConfig("dataIsFinal", False):
                    try:
                        metadataRecords = self.getData("metadata-tmp", pd.DataFrame, generate=False)
                        metadataChannels = self.getData("metadata-channels-tmp", pd.DataFrame, generate=False)
                        loadedRecords = metadataRecords["recordId"].to_list()
                        newRecords = [r for r in allRecordIds if r not in loadedRecords]
                        deprecatedRecords = [r for r in loadedRecords if r not in allRecordIds]

                        if len(deprecatedRecords) > 0:
                            metadataRecords = metadataRecords.drop(deprecatedRecords, errors="ignore")
                            metadataChannels = metadataChannels.drop(deprecatedRecords, errors="ignore")
                                                
                        self.logWarning(f"Not finished dataset: {len(deprecatedRecords)} deprecated records, {len(newRecords)} new records")
                        
                        allRecordIds = newRecords
                    except DataNotFound:
                        pass

            mR, mC = self.getMetadata(allRecordIds)

            # append dataframe
            if len(mR) > 0:
                metadataRecords = pd.concat([metadataRecords, pd.DataFrame(mR)]).set_index("recordId", drop=False)
            if len(mC) > 0:
                metadataChannels = pd.concat([metadataChannels, pd.DataFrame(mC)]).set_index("recordId", drop=False)

            self.project.registerData("metadata", metadataRecords, save=self.getConfig("dataIsFinal", False))
            self.project.registerData("metadata-channels", metadataChannels, save=self.getConfig("dataIsFinal", False))
            
            if not self.getConfig("dataIsFinal", False):
                self.project.registerData("metadata-tmp", metadataRecords)
                self.project.registerData("metadata-channels-tmp", metadataChannels)

        elif dataName == "allDBRecordIds":
            datasetConfig = self.getConfig("dataversion")

            if datasetConfig["recordIds"] is not None:
                recordIds = {r: [r] for r in datasetConfig["recordIds"]}
            else:
                metadata = self.getData("metadata", pd.DataFrame)
                metadataChannels = self.getData("metadata-channels", pd.DataFrame)
                recordIdsFlat = self.loadRecordIds(metadata, metadataChannels)
                recordIds = recordLoader.groupBy(datasetConfig["groupBy"], recordIdsFlat, metadata)

            if not bool(recordIds):
                raise Exception("No records found. Check your recordLoader config and your dataversion config.")

            self.project.registerData("allDBRecordIds", recordIds)

    def main(self):
        self.generateData("allDBRecordIds")
