import requests
from requests.auth import HTTPBasicAuth
import json
import os
from dotenv import find_dotenv, load_dotenv
from datetime import datetime
from typing import  List
from dataclasses import dataclass

JIRA_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
JIRA_DATE_FORMAT_D = "%Y-%m-%d"

@dataclass
class JiraComment:
    Commenter : str
    CommentDate: datetime
    Comment : str

@dataclass
class JiraWorkLog:
   id: int
   Logger : str
   LogDate : datetime
   LogHour : float

@dataclass
class JiraIssue:
    key : str
    summary: str
    description: str
    fields: dict
    Comments : List[JiraComment]
    Worklogs : List[JiraWorkLog]


load_dotenv(find_dotenv())

# Support either JIRA_TOKEN or JIRA_PAT_TOKEN for backwards compatibility
JIRA_TOKEN = os.getenv("JIRA_TOKEN") or os.getenv("JIRA_PAT_TOKEN")
JIRA_USER = os.getenv("JIRA_USER")

# Only create the auth object if credentials are available
auth = HTTPBasicAuth(JIRA_USER, JIRA_TOKEN) if JIRA_USER and JIRA_TOKEN else None

#How to get comments for a single jira issue

def searchJiraIssues(jql:str, fields:str="key,summary,description", loadComments = False) -> List[JiraIssue]:
   url = "https://pointr.atlassian.net/rest/api/3/search"
 
   headers = {
  	   "Accept": "application/json"
   }
   
   loadWorkLogs = False
   listoffields = fields.split(",")
   if "key" not in listoffields:
      fields += ",key"
   if "description" not in listoffields:
      fields += ",description"
   if "summary" not in listoffields:
      fields += ",summary"
   if "worklog" in listoffields:
      loadWorkLogs = True

   maxResult = 100
   fetchedRecords = 0 
   selectedIssues: List[JiraIssue]= []
   currentRecord = 0
   while True:
      query = {
         'jql': jql,
         'fields': fields,
         'maxResults': maxResult,
         'startAt' : fetchedRecords
      }
      
      response = requests.request(
         "GET",
         url,
         headers=headers,
         params=query,
         auth=auth
      )
     
      data = json.loads(response.text)
      #print(data)
      totalIssueCount = data["total"]
      #print(totalIssueCount)
      fetchedRecords = fetchedRecords +  data["maxResults"]

      #Get all issues and put them into an array
      for issue in data['issues']:
            currentRecord = currentRecord +1
            # print(f"{currentRecord}/{totalIssueCount}")
            jIssue = JiraIssue(key=issue["key"], summary=issue["fields"]["summary"], description=issue["fields"]["description"], fields= issue["fields"], Comments=None, Worklogs=None)
            if loadComments:
               jIssue.Comments = getJiraComments(issue["key"])
            if loadWorkLogs:
               jIssue.Worklogs = getJiraWorklogs(issue)

            selectedIssues.append(jIssue)
            

      if totalIssueCount <= fetchedRecords:
         break;

   return selectedIssues

def extract_text_from_json(json_obj):
    text = ""
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if not (key == 'type' and value in ('text','paragraph','doc','inlineCard')):
               text += extract_text_from_json(value)
    elif isinstance(json_obj, list):
        for item in json_obj:
            text += extract_text_from_json(item)
    elif isinstance(json_obj, str):
         text += json_obj + " "
    return text

def createJiraFiles(issues: List[JiraIssue]):
   folder_path = "./data/jiraIssues"
   if not os.path.exists(folder_path):
      # If it doesn't exist, create the folder
      os.makedirs(folder_path)
      print(f"Folder '{folder_path}' has been created.")

   for issue in issues:
      fileName = f"{folder_path}/{issue.key}.txt"
      with open(fileName, 'w', encoding="utf-8") as f:
         f.writelines(f"Key : {issue.key}\n")
         f.writelines(f"Summary : {issue.summary}\n")
         f.writelines(f"Description \n")
         description = extract_text_from_json(issue.description)
         f.writelines(description.strip())
         f.writelines("\n")
         f.writelines("Comments:\n")
         for comment in issue.Comments:
            f.writelines(f"Date: {comment.CommentDate}\n")
            f.writelines(f"Author: {comment.Commenter}\n")
            f.writelines(f"Comment: {comment.Comment}\n")      
         f.writelines("__________")

def getJiraWorklogs(issue) -> List[JiraWorkLog]:
   worklogs:List[JiraWorkLog]=[]
   if issue["fields"]["worklog"] is not None :
      workLogMaxResults = issue["fields"]["worklog"]["maxResults"]
      workLogTotalCount = issue["fields"]["worklog"]["total"]
      if workLogTotalCount <= workLogMaxResults:
         for workLog in issue["fields"]["worklog"]["worklogs"]:
            id = workLog["id"]
            author = workLog["author"]["displayName"]
            timeSpent = workLog["timeSpentSeconds"]/60/60
            logDateOrj = str(workLog["started"])
            logDate = datetime.strptime(logDateOrj[:10], JIRA_DATE_FORMAT_D )
            cm = JiraWorkLog(id, author, logDate, timeSpent)
            worklogs.append(cm)  
      else:   
         maxResult = 5000
         fetchedRecords = 0 
         currentRecord = 0
         jiraKey = issue["key"]
         url = f"https://pointr.atlassian.net/rest/api/2/issue/{jiraKey}/worklog/"

         headers = {
         "Accept": "application/json"
         }

         while True:
            query = {
               'maxResults': maxResult,
               'startAt' : fetchedRecords
            }
            
            response = requests.request(
            "GET",
            url,
            headers=headers,
            params=query,
            auth=auth
            )
      
            data = json.loads(response.text)
            totalIssueCount = data["total"]  
            fetchedRecords = fetchedRecords +  data["maxResults"]
            for workLog in data["worklogs"]:
               currentRecord = currentRecord +1
               id =  workLog["id"]
               author = workLog["author"]["displayName"]
               timeSpent = workLog["timeSpentSeconds"]/60/60
               logDateOrj = str(workLog["started"])
               logDate = datetime.strptime(logDateOrj[:10], JIRA_DATE_FORMAT_D )
               cm = JiraWorkLog(id,author, logDate, timeSpent)
               worklogs.append(cm)  

            if totalIssueCount <= fetchedRecords:
               break;

   return worklogs




def getJiraComments(key:str) -> List[JiraComment]:
   url = f"https://pointr.atlassian.net/rest/api/2/issue/{key}"
   
   headers = {
  	"Accept": "application/json"
   }
 
   query = {
   'fields': "comment"
   }
 
   response = requests.request(
  	"GET",
  	url,
  	headers=headers,
  	params=query,
  	auth=auth
   )
 
   data = json.loads(response.text)
   #print(response.text)
   comments:List[JiraComment]=[]
   #Get all issues and put them into an array
   for comment in data['fields']['comment']['comments']:
      author = comment["author"]["displayName"]
      message = comment["body"]
      commentDate = datetime.strptime(comment["updated"], JIRA_DATE_FORMAT ) 
      cm = JiraComment(author, commentDate, message)
      comments.append(cm)
   return comments


