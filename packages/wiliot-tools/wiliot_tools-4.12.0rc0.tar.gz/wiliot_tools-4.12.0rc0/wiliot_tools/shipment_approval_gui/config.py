col_width = {
    "requestId": 15,
    "externalIdPrefix": 18,
    "processStatus": 33,
    "failedPpAndShipmentTags": 19,
    "totalTestedTags": 12,
    "passedTags": 9,
    "failedOfflineTags": 13,
    "yield": 10,
    "First Tag": 10,
    "Last Tag": 9,
    "tagId": 31,
    "comment": 43,
    "status": 11,
    'serializationStatus': 20,
    'corruptedStatus': 18,
    'duplicationsStatus': 18,
    'sampleTestStatus': 18,
    'reelName': 18,
    "otherIssuesStatus": 18,
    "tadbikApproval": 18,
    "customerApproval": 18,
    "yieldStatus": 18
}

FULL_COLUMNS = ['requestId', 'processStatus', 'externalIdPrefix', 'reelName', 'customerApproval', 'tadbikApproval', 'totalTestedTags', 'passedTags',
                      'failedOfflineTags', 'yield', 'yieldStatus', 'failedPpAndShipmentTags', 'failedSerializationQty', 'serializationStatus',
                      'corruptedTagsQty', 'corruptedStatus', 'duplicationsQty', 'duplicationsStatus', "otherIssuesQty", 'otherIssuesStatus', 'numOfCommonRunNames', 'commonRunNames',
                      'firstExternalId', 'lastExternalId', 'sampleTestCommonRunName', 'sampleTestTesterStationName', 'sampleTestTestedTags',
                        'sampleTestPassedTags', 'sampleTestRespondedTags', 'sampleTestFailBinStr', 'sampleTestTbpAvg', 'sampleTestStatus', 'serializationTags',
                      'corruptedTags', 'duplicationTags', 'otherIssuesTags', 'uploadedAt']

DISPLAY_COLS = ['requestId', 'externalIdPrefix', 'processStatus', 'yield', 'customerApproval', 'tadbikApproval', 'yieldStatus', 'serializationStatus', 'corruptedStatus', 'duplicationsStatus', 'otherIssuesStatus', 'sampleTestStatus']