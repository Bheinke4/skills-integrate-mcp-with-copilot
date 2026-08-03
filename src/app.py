"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import os
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(Path(__file__).parent, "static")),
    name="static",
)

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
}

# In-memory student account database
students = {
    "emma@mergington.edu": {
        "password": "emma123",
        "branch": "Computer Science",
    },
    "john@mergington.edu": {
        "password": "john123",
        "branch": "Physical Education",
    },
    "olivia@mergington.edu": {
        "password": "olivia123",
        "branch": "Arts",
    },
    "michael@mergington.edu": {
        "password": "michael123",
        "branch": "History",
    },
}

sessions = {}


def get_current_user(request: Request) -> dict:
    session_token = request.cookies.get("session_token")
    if not session_token or session_token not in sessions:
        raise HTTPException(status_code=401, detail="Authentication required")

    email = sessions[session_token]
    student = students.get(email)
    if not student:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {"email": email, "branch": student["branch"]}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/login")
async def login(request: Request, response: Response):
    payload = await request.json()
    if not payload:
        raise HTTPException(status_code=400, detail="Email and password are required")

    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    student = students.get(email)
    if not student or student["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    session_token = str(uuid.uuid4())
    sessions[session_token] = email
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        samesite="lax",
    )

    return {"email": email, "branch": student["branch"]}


@app.post("/logout")
def logout(response: Response, request: Request):
    session_token = request.cookies.get("session_token")
    if session_token and session_token in sessions:
        sessions.pop(session_token, None)

    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}


@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, current_user: dict = Depends(get_current_user)):
    """Sign up the current student for an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    email = current_user["email"]

    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="No spots left")

    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, current_user: dict = Depends(get_current_user)):
    """Unregister the current student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    email = current_user["email"]

    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
