import os.path
#
# https://googleapis.github.io/google-api-python-client/docs/dyn/tasks_v1.tasks.html
#
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from console import fg, bg
import datetime as dt
import click
import sys

# If modifying these scopes, delete the file token.json.
#SCOPES = ["https://www.googleapis.com/auth/tasks.readonly"]
SCOPES = ["https://www.googleapis.com/auth/tasks"]
# --- token will happen on the PC if it doesnt yet exist
TOKEN = "~/.google_tasks_api.token"
TOKEN = os.path.expanduser(TOKEN)

# --- this is credential given by google
CRED = "~/.credentials_google0.json"
CRED =    os.path.expanduser(CRED)


def to_rfc3339(date_str):
    # Convert date like '2025-07-12 Sat 00:00' or ISO to RFC3339
    try:
        dt_obj = dt.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        dt_obj = dt.datetime.strptime(date_str, "%Y-%m-%d %a %H:%M")
    return dt_obj.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def dt_to_org(datim):
    """
    Convert date string to org-mode format.
    Supports ISO format with 'T' and 'Z' or 'YYYY-MM-DD Ddd HH:MM'.
    """
    try:
        due_date = dt.datetime.strptime(datim, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    except ValueError:
        try:
            due_date = dt.datetime.strptime(datim, "%Y-%m-%d %a %H:%M").date()
        except ValueError:
            # fallback: return input as is
            return datim
    return due_date.strftime("%Y-%m-%d %a %H:%M")

# def dt_to_org(datim):
#     """
#     from T Z to <2025-06-30 Mon 00:00>
#     """
#     due_str = datim # item['due']    # e.g. '2025-07-01T00:00:00.000Z'
#     due_date = dt.datetime.strptime(due_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()  # compare to today etc..
#     p_date =  due_date.strftime("%Y-%m-%d")
#     p_time =  due_date.strftime("%H:%M:%S")
#     p_wday =  due_date.strftime("%F")
#     #
#     result = due_date.strftime("%Y-%m-%d %a %H:%M")
#     return result
#     #
#     due_str = due_str.split("T")[0]
#     # plain date
#     today = dt.datetime.now(dt.timezone.utc).date()
#     tomorrow = today + dt.timedelta(days=1)


# ================================================================================
#
# --------------------------------------------------------------------------------

def tasks_read_remote(service, TASKLIST1):
    """

    """
    tasks_remote = {}
    for k, v in TASKLIST1.items():
        tasks_remote[v] = []
        try:
            results = service.tasks().list(tasklist=k).execute()
            items = results.get("items", [])
            for item in items:
                if item.get('status') == "completed":
                    continue
                task = {
                    "title": item.get("title"),
                    "due": item.get("due"),
                    "updated": item.get("updated"),
                    "status": item.get("status", "needsAction"),
                    "notes": item.get("notes", ""),
                }
                tasks_remote[v].append(task)
        except HttpError as err:
            print("X...", err)
    return tasks_remote
    # TASKS_REMOTE = []
    # #print("D... ============================== Parsing tasklists ===")
    # TASKS_REMOTE.append("* GOOGLE TASKS")
    # for k, v in TASKLIST1.items():
    #     TASKS_REMOTE.append(f"** {v}" )
    #     try:
    #         #service = build("tasks", "v1", credentials=creds)
    #         # Call the Tasks API
    #         results = service.tasks().list(tasklist=k).execute()
    #         items = results.get("items", [])

    #         #print()
    #         for item in items:

    #             if 'status' in item:
    #                 if item['status'] == "completed":
    #                     #print(f"{fg.slategray}     - {item['title']} : STAT: {item['status']}    {fg.default}")
    #                     continue

    #             TASKS_REMOTE.append(f"*** TODO {item['title']}")
    #             if 'due' in item:
    #                 s_scheduled = dt_to_org(item['due'])
    #                 TASKS_REMOTE.append(f"SCHEDULED: <{s_scheduled}>")
    #             s_updated = dt_to_org(item['updated'])
    #             TASKS_REMOTE.append(f"UPDATED: [{s_updated}]") # inactive timestamp
    #             if 'status' in item:
    #                 if item['status'] != "needsAction":
    #                     TASKS_REMOTE.append(f"            - STAT: {item['status']}    ")
    #             if 'due' in item:
    #                 s_scheduled = dt_to_org(item['due'])
    #                 due_str = item['due']    # e.g. '2025-07-01T00:00:00.000Z'
    #                 due_date = dt.datetime.strptime(due_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    #                 #due_str = due_str.split("T")[0]
    #                 today = dt.datetime.now(dt.timezone.utc).date()
    #                 tomorrow = today + dt.timedelta(days=1)
    #                 if due_date == today:
    #                     TASKS_REMOTE.append(f"             -  Due today     ") # The allow day only via API
    #                 elif due_date == tomorrow:
    #                     TASKS_REMOTE.append(f"             -  Due tomorrow  ") # They let day only
    #                 elif due_date < today:
    #                     TASKS_REMOTE.append(f"             -  Due in the PAST    {due_str}") # They let day only
    #                 else:
    #                     #print("Due on", due_date)
    #                     TASKS_REMOTE.append(f"             - DUE : {due_str}   ")
    #             if 'notes' in item:
    #                 TASKS_REMOTE.append(f"             - NOTES: {item['notes']}    ")
    #             #results = service.tasks().get(tasklist=k, task=item['id'])
    #     except HttpError as err:
    #         print("X...", err)
    # return TASKS_REMOTE

def dict2org(tasks_dict):
    """
    Converts nested dict {tasklist: [tasks]} to org-mode lines.
    """
    lines = ["* GOOGLE TASKS"]
    for tasklist, tasks in tasks_dict.items():
        lines.append(f"** {tasklist}")
        for t in tasks:
            lines.append(f"*** TODO {t['title']}")
            if t.get("due"):
                due_org = dt_to_org(t["due"])
                lines.append(f"SCHEDULED: <{due_org}>")
            if t.get("updated"):
                #updated_org = dt_to_org(t["updated"])
                #lines.append(f"UPDATED: [{updated_org}]")
                lines.append(f"UPDATED: [{t['updated']}]")  # store full ISO timestamp
            if t.get("status") and t["status"] != "needsAction":
                lines.append(f"            - STAT: {t['status']}")
            if t.get("notes"):
                lines.append(f"            - NOTES: {t['notes']}")
    return lines

# ================================================================================
#
# --------------------------------------------------------------------------------

def org2dict(org_lines):
    tasks_dict = {}
    current_tasklist = None
    current_task = None
    for line in org_lines:
        line = line.strip()
        if line.startswith("* GOOGLE TASKS"):
            continue
        elif line.startswith("** "):
            # Save previous task before switching tasklist
            if current_task and current_tasklist:
                tasks_dict[current_tasklist].append(current_task)
                current_task = None
            current_tasklist = line[3:]
            tasks_dict.setdefault(current_tasklist, [])
        elif line.startswith("*** TODO "):
            # Save previous task before starting new one
            if current_task and current_tasklist:
                tasks_dict[current_tasklist].append(current_task)
            current_task = {"title": line[8:].strip(), "due": None, "updated": None, "status": "needsAction", "notes": ""}
        elif line.startswith("SCHEDULED: <") and current_task:
            current_task["due"] = line[len("SCHEDULED: <"):-1]
        elif line.startswith("UPDATED: [") and current_task:
            current_task["updated"] = line[len("UPDATED: ["):-1]
        elif line.strip().startswith("- STAT:") and current_task:
            current_task["status"] = line.split(":")[1].strip()
        elif line.strip().startswith("- NOTES:") and current_task:
            current_task["notes"] = line.split(":")[1].strip()
    # Add last task if any
    if current_task and current_tasklist:
        tasks_dict[current_tasklist].append(current_task)
    return tasks_dict
    # """
    # Parses org-mode lines into nested dict {tasklist: [tasks]}.
    # """
    # tasks_dict = {}
    # current_tasklist = None
    # current_task = None
    # for line in org_lines:
    #     line = line.strip()
    #     if line.startswith("* GOOGLE TASKS"):
    #         continue
    #     elif line.startswith("** "):
    #         current_tasklist = line[3:]
    #         tasks_dict[current_tasklist] = []
    #     elif line.startswith("*** TODO "):
    #         if current_task:
    #             tasks_dict[current_tasklist].append(current_task)
    #         current_task = {"title": line[8:], "due": None, "updated": None, "status": "needsAction", "notes": ""}
    #     elif line.startswith("SCHEDULED: <") and current_task:
    #         current_task["due"] = line[len("SCHEDULED: <"):-1]
    #     elif line.startswith("UPDATED: [") and current_task:
    #         current_task["updated"] = line[len("UPDATED: ["):-1]  # read full ISO timestamp
    #         # current_task["updated"] = line[len("UPDATED: ["):-1]
    #     elif line.strip().startswith("- STAT:") and current_task:
    #         current_task["status"] = line.split(":")[1].strip()
    #     elif line.strip().startswith("- NOTES:") and current_task:
    #         current_task["notes"] = line.split(":")[1].strip()
    # if current_task and current_tasklist:
    #     tasks_dict[current_tasklist].append(current_task)
    # return tasks_dict

def tasks_read_file(filepath="tasks_local.org"):
    with open(filepath, "r") as f:
        lines = f.readlines()
    return org2dict(lines)


# def tasks_read_file(filepath="tasks_local.org"):
#     """
#     Reads local tasks from an org-mode formatted file.
#     Returns a list of task dicts with keys: title, due, updated, status, notes.
#     """
#     if not os.path.exists(filepath):
#         print(f"X... NO FILE {filepath}")
#         sys.exit(0)
#     tasks = []
#     current_task = None
#     with open(filepath, "r") as f:
#         for line in f:
#             line = line.strip()
#             if line.startswith("*** TODO "):
#                 if current_task:
#                     tasks.append(current_task)
#                 current_task = {"title": line[8:], "due": None, "updated": None, "status": "needsAction", "notes": None}
#             elif line.startswith("SCHEDULED: <") and current_task:
#                 # parse date inside <>
#                 current_task["due"] = line[len("SCHEDULED: <"):-1]
#             elif line.startswith("UPDATED: [") and current_task:
#                 current_task["updated"] = line[len("UPDATED: ["):-1]
#             elif line.strip().startswith("- STAT:") and current_task:
#                 current_task["status"] = line.split(":")[1].strip()
#             elif line.strip().startswith("- NOTES:") and current_task:
#                 current_task["notes"] = line.split(":")[1].strip()
#         if current_task:
#             tasks.append(current_task)
#     return tasks


# ================================================================================
#
# --------------------------------------------------------------------------------

def tasks_compare_rl(remote_dict, local_dict):
    """
    Compare remote and local nested dicts
    """
    # drop_remote = {} # NO DROP REMOTE
    to_update = []
    to_push_new = []

    for tasklist, remote_tasks in remote_dict.items():
        if tasklist in local_dict:
            local_tasks = local_dict[tasklist]
            for ri in remote_tasks:
                present = False
                needsupdate = True
                #print(f"/{ri['title']}/")
                for li in local_tasks:
                    #print(f"         /{li['title']}/")
                    if (ri['title'] == li['title']):
                        present = True
                        if ri['updated'] == li['updated']:
                        #print(ri['title'], "ok")
                            needsupdate = False
                if not present:
                    print(f"r2l... @ {tasklist:20s}   #   {ri['title']}")
                elif needsupdate:
                    print(f"r2l... @ {tasklist:20s}   U   {ri['title']}")
        else:
            print("X... no tasklist {tasklist} in local")
    print("_" * 60)

    for tasklist, local_tasks in local_dict.items():
        if tasklist in remote_dict:
            remote_tasks = remote_dict[tasklist]
            for li in local_tasks:
                present = False
                needsupdate = True
                #print(f"/{ri['title']}/")
                for ri in remote_tasks:
                    #print(f"         /{li['title']}/")
                    if (ri['title'] == li['title']):
                        present = True
                        if ri['updated'] == li['updated']:
                            needsupdate = False
                        #print(ri['title'], "ok")
                if not present:
                    print(f"l2r... @ {tasklist:20s}   #   {li['title']}")
                    to_push_new.append( (tasklist, li['title']) )
                elif needsupdate:
                    print(f"l2r... @ {tasklist:20s}   U   {li['title']}")
                    to_update.append( (tasklist, li['title']) )
        else:
            print("X... no tasklist {tasklist} in remote")


    return to_push_new, to_update



# ================================================================================
#
# --------------------------------------------------------------------------------

def add_tasks_to_remote(service, TASKLIST1, local_dict, tasks_to_add):
    """
    Adds local tasks specified by (tasklist, title) tuples to remote Google Tasks.
    service: Google Tasks API service object.
    TASKLIST1: dict mapping tasklist IDs to titles.
    local_dict: nested dict {tasklist_title: [tasks]}.
    tasks_to_add: list of (tasklist_title, task_title) tuples.
    """
    # Reverse TASKLIST1 to map title -> id
    title_to_id = {v: k for k, v in TASKLIST1.items()}

    for tasklist_title, task_title in tasks_to_add:
        tasklist_id = title_to_id.get(tasklist_title)
        if not tasklist_id:
            print(f"Tasklist '{tasklist_title}' not found in remote.")
            continue
        local_tasks = local_dict.get(tasklist_title, [])
        task = next((t for t in local_tasks if t["title"] == task_title), None)
        if not task:
            print(f"Task '{task_title}' not found locally in '{tasklist_title}'.")
            continue

        body = {
            "title": task["title"],
            "status": task.get("status", "needsAction"),
        }
        if task.get("due"):
            #body["due"] = task["due"]
            body["due"] = to_rfc3339(task["due"])
        if task.get("notes"):
            body["notes"] = task["notes"]

        print(f"D... task '{task_title}' to remote tasklist '{tasklist_title}'.")
        input("Add the task? > ")
        try:
            service.tasks().insert(tasklist=tasklist_id, body=body).execute()
            print(f"Added task '{task_title}' to remote tasklist '{tasklist_title}'.")
        except HttpError as err:
            print(f"Failed to add task '{task_title}': {err}")




# ================================================================================
#
# --------------------------------------------------------------------------------

@click.command()
@click.option("--command", "-c", default="rprint", help="rprint  lprint  rlcomp")
def main(command):
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        print(f"D...  TOKEN: {TOKEN}")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    CRED, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN, "w") as token:
            token.write(creds.to_json())

    TASKLIST = {}
    try:
        service = build("tasks", "v1", credentials=creds)

        # Call the Tasks API
        results = service.tasklists().list(maxResults=10).execute()
        items = results.get("items", [])

        if not items:
            print("No task lists found.")
            return

        #print("D... ===============================Task lists:")
        for item in items:
            #print(f"D...   * {item['title']} ({item['id']})")
            TASKLIST[item['id']] = item['title']
    except HttpError as err:
        print(err)

    # ===========================================================   command section ============
    if command == "rprint" or command == "r": # I NEED THIS TO CREATE ORGMODE AGENDA
        tarem = tasks_read_remote(service, TASKLIST)
        #print(tarem)
        print()
        for i in dict2org(tarem): print(i)
    # elif command == "lprint" or command == "l": # I dont need it really
    #     taloc = tasks_read_file()
    #     #print(taloc)
    #     print()
    #     for i in dict2org(taloc): print(i)
    # elif command == "rlcomp" or command == "rl":
    #     tarem = tasks_read_remote(service, TASKLIST)
    #     taloc = tasks_read_file()
    #     to_push_new, to_update = tasks_compare_rl(tarem, taloc)
    #     print("TO PUSH NEW")
    #     print(to_push_new)
    #     add_tasks_to_remote(service, TASKLIST, taloc, to_push_new)
    #     #
    #     print("TO UPDATE")
    #     print(to_update)
    #     #print("CHANGE")
    #     #print(res['to_update'])
    # else:
    #     print("X... unknown command ")

if __name__ == "__main__":
    main()
