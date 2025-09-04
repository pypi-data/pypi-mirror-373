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
                #  *** ID  ***
                #print(f"D...  {task['title']}  ...  {item.get('id')} ")
                tasks_remote[v].append(task)
        except HttpError as err:
            print("X...", err)
    return tasks_remote


# ================================================================================
#                           like IMPORT
# --------------------------------------------------------------------------------

def dict2org(tasks_dict):
    """
    Converts nested dict {tasklist: [tasks]} to org-mode lines.   LIKE IMPORT
    """
    lines = ["* GOOGLE TASKS"]
    for tasklist, tasks in tasks_dict.items():
        lines.append("")
        lines.append(f"** {tasklist}")
        for t in tasks:
            lines.append("")
            # -------- ------------------------------- SCHEDULED has TODO if not else   (import)
            #print(f"{tasklist:25s}@@@{t['title'].strip()}@I@")

            if t['title'].strip().find("DOING") == 0:
                lines.append(f"*** {t['title']}")
            elif t['title'].strip().find("WAITING") == 0:
                lines.append(f"*** {t['title']}")
            elif t['title'].strip().find("TODO") == 0:
                lines.append(f"*** {t['title']}")
            elif t['title'].strip().find("DELEGATED") == 0:
                lines.append(f"*** {t['title']}")
            elif t['title'].strip().find("POSTPONED") == 0:
                lines.append(f"*** {t['title']}")
            elif t['title'].strip().find("DONE") == 0:
                lines.append(f"*** {t['title']}")
            elif t['title'].strip().find("CANCELED") == 0:
                lines.append(f"*** {t['title']}")
            elif t.get("due"):
                lines.append(f"*** TODO {t['title']}")
            else:
                lines.append(f"*** {t['title']}")
            #------------------------

            if t.get("due"):
                due_org = dt_to_org(t["due"])
                lines.append(f"SCHEDULED: <{due_org}>")
            if t.get("updated"):
                #updated_org = dt_to_org(t["updated"])
                #lines.append(f"UPDATED: [{updated_org}]")
                notsoISO = t['updated']
                notsoISO = notsoISO.replace("T", " ") # remove T for org
                lines.append(f"UPDATED: [{notsoISO}]")  # store full ISO timestamp
            if t.get("status") and t["status"] != "needsAction":
                lines.append(f"            - STAT: {t['status']}")
            if t.get("notes"):
                if t['notes'].find("\n") >= 0:
                    res = t['notes'].strip().split("\n")
                    for i in res:
                        lines.append(f" {i}")
                else:
                    lines.append(f"            - NOTES: {t['notes']}")
    return lines

# ================================================================================
#            like EXPORT
# --------------------------------------------------------------------------------

def org2dict(org_lines):
    """
    convert due to the T Z format  ----- like EXPORT
    """
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
        elif line.startswith("*** "): # ------------------------------- exporting items
            # ---------  TODO is bound to Schedule, I will skip it here
            mytitle = line.replace("*** ", "") # ALWAYS REMOVE ***  line[9:].strip()
            mytitle = mytitle.replace("TODO", "") # dont propagate TODO - it is <-> scheduled
            mytitle = mytitle.strip(" ")
        #elif line.startswith("*** TODO ") or line.startswith("*** DOING "):
            # Save previous task before starting new one
            #if line.startswith("*** DOING "):
            #else:
            #    mytitle = line[8:].strip()
            ## ------ ----------------------- formulate task
            if current_task and current_tasklist:
                tasks_dict[current_tasklist].append(current_task) # Like Finish The Previous Task and GO ON
            # -- initiate
            #print(f"{current_tasklist:25s}@@@{mytitle}@E@")
            current_task = {"title": mytitle, "due": None, "updated": None, "status": "needsAction", "notes": ""}
        elif line.startswith("SCHEDULED: <") and current_task:
            current_task["due"] = line[len("SCHEDULED: <"):-1]
            current_task["due"] = current_task["due"].split()[0] + "T00:00:00.000Z"
        #elif line.startswith("DEADLINE: <") and current_task:
        #    current_task["due"] = line[len("DEADLINE: <"):-1]
        elif line.startswith("UPDATED: [") and current_task:
            current_task["updated"] = line[len("UPDATED: ["):-1]
        elif line.strip().startswith("- STAT:") and current_task:
            current_task["status"] = line.split(":")[1].strip()
        elif line.strip().startswith("- NOTES:") and current_task:
            current_task["notes"] = line.split(":")[1].strip()
        elif current_task:
            if "notes" in current_task:
                if line != "":
                    current_task["notes"] = f'{current_task["notes"]}\n{line}'
            else:
                if line != "":
                    current_task["notes"] = line
    # Add last task if any
    if current_task and current_tasklist:
        tasks_dict[current_tasklist].append(current_task)
    return tasks_dict

def tasks_read_file(filepath):
    with open(filepath, "r") as f:
        lines = f.readlines()
    return org2dict(lines)




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

    # ---- this part I dont care.....
    print(fg.darkslateblue)
    print("_" * 60, " no action with these:")
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
                        if (ri['notes'].replace(" ", "") == li['notes'].replace(" ", "") ) and (ri['due'] == li['due']) :
                        #print(ri['title'], "ok")
                            needsupdate = False
                if not present:
                    print(f"r2l... @ {tasklist:20s}   #   {ri['title']}")
                elif needsupdate:
                    print(f"r2l... @ {tasklist:20s}   U   {ri['title']}")
        else:
            print("X... no tasklist {tasklist} in local")


    print(fg.default)
    print("_" * 15, "L", "_" * 20, "R", "_" * 15," action on local->remote:")

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
                        if (  ri['notes'].replace(" ", "") == li['notes'].replace(" ", "")) and (ri['due'] == li['due']) :
                            needsupdate = False
                        #print(ri['title'], "ok")
                # ------------------- PRINT ALL INTENTIONS ------------
                if not present:
                    print(f"l2r... @ {tasklist:20s}   >   {li['title']}")
                    to_push_new.append( (tasklist, li['title']) )
                elif needsupdate:
                    print(f"l2r... @ {tasklist:20s}   U   {li['title']}")
                    if  li['notes'].replace(" ", "") != "":
                        print(f".           {li['notes']}")
                    if  ri['notes'].replace(" ", "") != "":
                        print(f".                                  {ri['notes']}")
                    if li['due'] is not None:
                        print(f",           {li['due']}")
                    if ri['due'] is not None:
                        print(f",                                  {ri['due']}")
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
        #input("Add the task? > ")
        try:
            service.tasks().insert(tasklist=tasklist_id, body=body).execute()
            print(f"Added task '{task_title}' to remote tasklist '{tasklist_title}'.")
        except HttpError as err:
            print(f"Failed to add task '{task_title}': {err}")


# ================================================================================
#  UPDATE REMOTE
# --------------------------------------------------------------------------------

def update_remote_task(service, TASKLIST1, local_dict, tasklist_title, task_title):
    """
    Update remote task matching (tasklist_title, task_title) with local due and notes if changed.
    """
    # Map tasklist title to ID
    title_to_id = {v: k for k, v in TASKLIST1.items()}
    tasklist_id = title_to_id.get(tasklist_title)
    if not tasklist_id:
        print(f"Tasklist '{tasklist_title}' not found.")
        return

    # Get local task
    local_tasks = local_dict.get(tasklist_title, [])
    local_task = next((t for t in local_tasks if t["title"] == task_title), None)
    if not local_task:
        print(f"Local task '{task_title}' not found in '{tasklist_title}'.")
        return

    # Find remote task by listing tasks in tasklist
    try:
        results = service.tasks().list(tasklist=tasklist_id).execute()
        remote_tasks = results.get("items", [])
    except HttpError as err:
        print(f"Failed to list remote tasks: {err}")
        return

    remote_task = next((t for t in remote_tasks if t["title"] == task_title), None)
    if not remote_task:
        print(f"Remote task '{task_title}' not found in '{tasklist_title}'.")
        return

    # Prepare update body with changed fields
    body = {}
    changed = False

    # Compare and update 'due'
    local_due = local_task.get("due")
    remote_due = remote_task.get("due")
    if local_due != remote_due:
        # Convert local_due to RFC3339 if needed
        if local_due:
            try:
                dt_obj = dt.datetime.strptime(local_due, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                dt_obj = dt.datetime.strptime(local_due, "%Y-%m-%d %a %H:%M")
            body["due"] = dt_obj.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        else:
            body["due"] = None
        changed = True

    # Compare and update 'notes'
    local_notes = local_task.get("notes", "")
    remote_notes = remote_task.get("notes", "")
    if local_notes.replace(" ", "")!= remote_notes.replace(" ", ""):
        body["notes"] = local_notes
        changed = True

    if not changed:
        print(f"No changes detected for task '{task_title}'.")
        return

    # Include title and status to avoid overwriting
    body["title"] = task_title
    body["status"] = remote_task.get("status", "needsAction")
    body['id'] = remote_task["id"]
    body['notes'] = local_task['notes']

    try:
        #print(tasklist_id, "task=", remote_task["id"])
        service.tasks().update(tasklist=tasklist_id, task=remote_task["id"], body=body).execute()
        print(f"Updated task '{task_title}' in '{tasklist_title}'.")
    except HttpError as err:
        print(f"Failed to update task '{task_title}': {err}")





# ================================================================================
# IMPORT MAIN
# --------------------------------------------------------------------------------

#@click.command()
#@click.argument("command", default="rprint")
#def main_import(command):
def main_import(command="rprint"):
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN):
        #print(f"D...  ....  TOKEN: {TOKEN}")
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    else:
        print("X... NO token")
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        print(f"D...  creds NOT VALID....  ")
        if creds and creds.expired and creds.refresh_token:
            ok = False
            try:
                print(f"D...  refreshing creds  ")
                creds.refresh(Request())
                ok = True
            except Exception as err:
                print(err)
                print("i... try to remove ", TOKEN)
            if not ok:
                print("X... sorry end")
                sys.exit(1)
        else:
            print(f"D...  creds else: ")
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
        print()
        for i in dict2org(tarem): print(i)
    else:
        print(f"X... command not recognized /{command}/")

# ================================================================================
#  EXPORT MAIN
# --------------------------------------------------------------------------------

@click.command()
@click.argument('filename',  required=True)
def main_export(filename):
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    print(filename)
    command = "rlcomp"
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
            #   * ID *****
            # print(f"D...   * {item['title']} ({item['id']})")
            TASKLIST[item['id']] = item['title']
    except HttpError as err:
        print(err)

    # ===========================================================   command section ============

    if command == "rlcomp" or command == "rl":
        tarem = tasks_read_remote(service, TASKLIST)
        if not os.path.exists(filename):
            print(f"X... cannot find org  file {filename}")
            sys.exit(1)
        else:
            print(f"i... going through possible exports ....  {filename}")
        taloc = tasks_read_file(filename)
        #print(taloc)
        to_push_new, to_update = tasks_compare_rl(tarem, taloc)
        print()


        # ----- PUSH NEW -----------------------------------------------------
        if len(to_push_new) == 0:
            print("i... nothing new to push.... ")
        else:
            print("___________________ preparing push new to remote ____________")
            print(f"{fg.orange}{to_push_new}{fg.default}")
            # ** real action ***
            add_tasks_to_remote(service, TASKLIST, taloc, to_push_new)
            print("_____________________ ALL NEW PUSHED __________________")
        print()

        # ----- UPDATE NEW --------------------------------------------------
        if len(to_update) == 0:
            print("i... nothing to update ...")
        else:
            print("__________________ UPDATING EXISTING NOW:____________________")
            print(f"{fg.red}{to_update}{fg.default}")
            for ii in to_update:
                # ** real action ***
                update_remote_task(service, TASKLIST, taloc, ii[0], ii[1])
                pass
            print("_____________________ ALL UPDATED __________________")

        #print("CHANGE")
        #print(res['to_update'])
    # else:
    #     print("X... unknown command ")


# ================================================================================
# MAIN
# --------------------------------------------------------------------------------

# #@click.command()
# #@click.argument('action')
# #@click.argument('filename', default=None)
# def main():
#     #print(action)
#     action = "export"
#     filename ="/tmp/a.org"
#     if action == 'import':
#         #print(action)
#         main_import()
#     else:
#         print("export",  filename)
#         if filename is None:
#             print("X... give me filename")
#         main_export(filename)
#     print("finish")

if __name__ == "__main__":
    main_export()
    #main_import()
