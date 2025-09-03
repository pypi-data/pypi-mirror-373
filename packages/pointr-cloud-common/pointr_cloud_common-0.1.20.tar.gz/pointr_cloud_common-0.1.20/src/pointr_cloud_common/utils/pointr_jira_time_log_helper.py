from dotenv import load_dotenv
from typing import List
from .pointr_jira_helper import searchJiraIssues
from datetime import datetime
from typing import List
from dataclasses import dataclass
import re

load_dotenv()


@dataclass(frozen=False)
class TimeSheet:
    id: int
    status: str
    summary: str
    jiraKey: str
    mapJobId: str
    floorPlanId: str
    loggingDate: datetime
    loggedHours: float = 0.0
    isUpdateJob: bool = False
    sector: str = None
    client: str = None
    areaSqFeet: float = None
    logger: str = None
    loggerEmail: str = None
    jiraProject: str = None
    activityType: str = None
    jiraUrl: str = None
    doneBy: str = "Pointr"
    issueType: str = None
    complexity: int = 0


jira_url = "https://pointr.atlassian.net/browse/{0}"


def extract_client_fromJiraSummary(title, jiraProject):
    """
    Extracts the substring between 'Digitize' and 'maps through' from the given text.

    Parameters:
    text (str): The input string containing the text.

    Returns:
    str: The extracted substring, or None if no match is found.
    """
    if jiraProject["key"] == "IMM":
        # Regular expression to capture the text between "Digitize" and "maps through"
        pattern = r'Digitize\s+(.*?)\s+maps through'

        # Search for the pattern in the text
        match = re.search(pattern, title)

        # Check if a match is found and extract it
        if match:
            return match.group(1)
        else:
            return jiraProject["name"]
    else:
        return jiraProject["name"]


def generate_timelog_report(jql, columns, employeeList):
    id_to_displayName = {team_member['id']: team_member['displayName'] for team_member in employeeList}
    issues = searchJiraIssues(jql, columns)

    field_names_map = {
        "areaField": "customfield_10691",
        "floorPlanId": "customfield_10690",
        "mapJobId": "customfield_10689",
        "sector": "customfield_10687",
        "isMapScaleOutputUsed": "customfield_10686",
        "isUpdate": "customfield_10696",
        "taskDoneBy": "customfield_10730",
        "complexity": "customfield_10747",
        "activityType": "customfield_10822"
    }

    timesheetList: List[TimeSheet] = []
    for i in issues:
        area = 0
        if field_names_map["areaField"] in i.fields:
            area = i.fields[field_names_map["areaField"]]
            if area is None:
                area = 0

        taskDoneBy = "Pointr"
        if field_names_map["taskDoneBy"] in i.fields:
            if i.fields[field_names_map["taskDoneBy"]] is not None:
                taskDoneBy = i.fields[field_names_map["taskDoneBy"]]["value"]

        floorPlanIdObj = None
        if field_names_map["floorPlanId"] in i.fields:
            floorPlanIdObj = i.fields[field_names_map["floorPlanId"]]

        floorPlanId = None
        if floorPlanIdObj is not None:
            floorPlanId = floorPlanIdObj
        else:
            floorPlanId = None

        mapJobId = None
        if field_names_map["mapJobId"] in i.fields:
            mapJobIdObj = i.fields[field_names_map["mapJobId"]]
            if mapJobIdObj is not None:
                mapJobId = mapJobIdObj
            else:
                mapJobId = None

        sector = None
        if field_names_map["sector"] in i.fields:
            sectorObj = i.fields[field_names_map["sector"]]
            if sectorObj is not None and "value" in sectorObj:
                sector = sectorObj["value"]
            else:
                sector = None

        activityType = None
        if field_names_map["activityType"] in i.fields:
            if i.fields[field_names_map["activityType"]] is not None:
                activityType = i.fields[field_names_map["activityType"]]["value"]

        isMapScaleOutputUsed = None
        if field_names_map["isMapScaleOutputUsed"] in i.fields:
            isMapScaleOutputUsedObj = i.fields[field_names_map["isMapScaleOutputUsed"]]
            if isMapScaleOutputUsedObj is not None and "value" in isMapScaleOutputUsedObj:
                if isMapScaleOutputUsedObj["value"] == "Yes":
                    isMapScaleOutputUsed = True
                elif isMapScaleOutputUsedObj["value"] == "No":
                    isMapScaleOutputUsed = False
            else:
                isMapScaleOutputUsed = None

        isUpdate = False
        if field_names_map["isUpdate"] in i.fields:
            isUpdateObj = i.fields[field_names_map["isUpdate"]]
            if isUpdateObj is not None and "value" in isUpdateObj:
                if isUpdateObj["value"] == "Yes":
                    isUpdate = True
                elif isUpdateObj["value"] == "No":
                    isUpdate = False
            else:
                isUpdate = False

        for l in i.Worklogs:  # .fields["worklog"]["worklogs"]:
            hoursSpent = 0 if l.LogHour is None else l.LogHour  # ['timeSpentSeconds']/60/60
            dateLogged = l.LogDate  # convertJiraDateToGMTTimeZone(l['started'], "%Y-%m-%dT%H:%M:%S.%f%z")

            ts = TimeSheet(
                id=l.id,
                status=i.fields["status"]["name"],
                summary=i.fields["summary"],
                jiraKey=i.key,
                mapJobId=mapJobId,
                floorPlanId=floorPlanId,
                loggingDate=dateLogged,
                loggedHours=hoursSpent,
                isUpdateJob=isUpdate,
                sector=sector,
                client=extract_client_fromJiraSummary(i.fields["summary"], i.fields["project"]),
                areaSqFeet=area,
                logger=id_to_displayName.get(l.Logger, f'Jira user {l.Logger} not found in database'),
                jiraUrl=jira_url.replace("{0}", i.key),
                doneBy=taskDoneBy,
                jiraProject=i.fields["project"]["name"],
                issueType=i.fields.get('issuetype', {}).get('name', None),
                complexity=i.fields.get(field_names_map["complexity"], None),
                activityType=activityType
            )
            timesheetList.append(ts)

    return timesheetList 