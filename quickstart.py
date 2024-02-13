import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def master_func(begin,end):
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time

    # begin=input("Enter the start date for fetching holidays:")
    # end=input("Enter the date upto which holidays are to be fetched:")

    #print("Fetching the Holidays between Start and End date:")
    events_result = (
        service.events()
        .list(
            calendarId="en.indian.official#holiday@group.v.calendar.google.com",
            timeMin=begin,
            timeMax=end,
            #timeMin=now,
            #maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    temp=[]
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      temp.append((start, event["summary"]))
    return temp

  except HttpError as error:
    return (f"An error occurred: {error}") #print

# import gradio as gr
# demo = gr.Interface(fn=master, inputs=["text","text"], outputs="text")
# demo.launch()  

from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def form():
  return render_template("index.html")  # Render the HTML form

@app.route("/calculate", methods=["POST"])
def calculate():
  begin = request.form["begin"]
  end = request.form["end"]
  result = master_func(begin, end)  # Call the Python function
  return render_template("result.html", result=result)  # Render result page

if __name__ == "__main__":
  app.run(debug=True)  # Start the Flask development server



# if __name__ == "__main__":
  #main()