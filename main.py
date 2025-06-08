from fastapi import FastAPI, HTTPException
from pydantic import RootModel, BaseModel
from typing import List, Tuple
from datetime import datetime, timedelta
import pytz
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

users_busy_slots = {}
booked_slots = []  

IST = pytz.timezone("Asia/Kolkata")

class BusySlot(RootModel):
    root: List[str]  

class UserSlots(BaseModel):
    id: int
    busy: List[BusySlot]

class SlotsRequest(BaseModel):
    users: List[UserSlots]

class BookSlot(BaseModel):
    start: str
    end: str


def parse_time(time_str: str, base_date: datetime) -> datetime:
    try:
        return datetime.strptime(f"{base_date.date()} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=IST)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {time_str}. Use HH:MM")


def format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def is_within_workday(start: datetime, end: datetime) -> bool:
    workday_start = start.replace(hour=9, minute=0, second=0, microsecond=0)
    workday_end = start.replace(hour=18, minute=0, second=0, microsecond=0)
    return workday_start <= start and end <= workday_end


@app.post("/slots")
async def store_slots(slots: SlotsRequest):
    today = datetime.now(IST)
    for user in slots.users:
        validated_slots = []
        for slot in user.busy:
            if len(slot.root) != 2:
                raise HTTPException(status_code=400, detail=f"Invalid slot for user {user.id}: {slot.root}. Must be [start, end]")
            start_str, end_str = slot.root
            start = parse_time(start_str, today)
            end = parse_time(end_str, today)
            if start >= end:
                raise HTTPException(status_code=400, detail=f"Invalid slot for user {user.id}: start {start_str} must be before end {end_str}")
            if not is_within_workday(start, end):
                raise HTTPException(status_code=400, detail=f"Slot {start_str}-{end_str} for user {user.id} is outside workday (09:00–18:00)")
            validated_slots.append((start, end))
        users_busy_slots[user.id] = validated_slots
    return {"message": "Slots stored successfully"}


@app.get("/suggest")
async def suggest_meeting(duration: int = 30):
    if duration <= 0:
        raise HTTPException(status_code=400, detail="Duration must be positive")
    
    today = datetime.now(IST)
    workday_start = today.replace(hour=9, minute=0, second=0, microsecond=0)
    workday_end = today.replace(hour=18, minute=0, second=0, microsecond=0)
    duration_delta = timedelta(minutes=duration)
    
    # If no users, return empty list
    if not users_busy_slots:
        return []
    
    # Collect all busy times
    all_busy = []
    for user_id, slots in users_busy_slots.items():
        all_busy.extend(slots)
    
    # Sort busy slots by start time
    all_busy.sort(key=lambda x: x[0])
    
    # Find free slots
    free_slots = []
    current_time = workday_start
    for busy_start, busy_end in all_busy:
        if current_time + duration_delta < busy_start and current_time + duration_delta < workday_end:
            free_slots.append((current_time, current_time + duration_delta))
        current_time = max(current_time, busy_end)
    
    # Check for a free slot after the last busy period
    if current_time + duration_delta < workday_end:
        free_slots.append((current_time, current_time + duration_delta))
    
    # Take first three free slots and format as HH:MM-HH:MM
    result = [[format_time(start), format_time(end)] for start, end in free_slots[:3]]
    return result


@app.get("/calendar/{user_id}")
async def get_calendar(user_id: int):
    if user_id not in users_busy_slots:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    busy_slots = [[format_time(start), format_time(end)] for start, end in users_busy_slots[user_id]]
    return {"user_id": user_id, "busy": busy_slots}


@app.post("/book")
async def book_slot(slot: BookSlot):
    today = datetime.now(IST)
    start = parse_time(slot.start, today)
    end = parse_time(slot.end, today)
    if start >= end:
        raise HTTPException(status_code=400, detail=f"Invalid slot: start {slot.start} must be before end {slot.end}")
    if not is_within_workday(start, end):
        raise HTTPException(status_code=400, detail=f"Slot {slot.start}-{slot.end} is outside workday (09:00–18:00), Please choose a time within work hours")
    
    # Check if slot overlaps with any user's busy slots
    for user_id, slots in users_busy_slots.items():
        for busy_start, busy_end in slots:
            if not (end <= busy_start or start >= busy_end):
                raise HTTPException(status_code=400, detail=f"Slot {slot.start}-{slot.end} conflicts with user {user_id}'s schedule")
    
    # Add to booked slots and update all users' busy slots
    booked_slots.append((start, end))
    for user_id in users_busy_slots:
        users_busy_slots[user_id].append((start, end))
        users_busy_slots[user_id].sort(key=lambda x: x[0])
    return {"message": "Slot booked successfully"}