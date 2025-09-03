from datetime import datetime,timezone

date_format = "%Y-%m-%dT%H:%M:%S.%fZ"

def convertJiraDateToGMTTimeZone(inputDate:str, dateformat:str= date_format) -> datetime or None:
    if inputDate is not None :
        input_date = datetime.strptime(inputDate, dateformat)
        input_date = input_date.astimezone(timezone.utc)  # Convert to GMT/UTC timezone
        return input_date
    else:
        return None 