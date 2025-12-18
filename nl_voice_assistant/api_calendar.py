import requests

CALENDER_ID = "TEAM_NLS_Project"
BASE_URL = "https://api.responsible-nlp.net/calendar.php"

def calendar_url():
    return f"{BASE_URL}?calenderid={CALENDER_ID}"

# CREATE
def create_event(title, description, start_time, end_time, location):
    payload = {
        "title": title,
        "description": description,
        "start_time": start_time,
        "end_time": end_time,
        "location": location
    }
    r = requests.post(calendar_url(), json=payload, timeout=10)
    return r.json()

# LIST
def list_events():
    r = requests.get(calendar_url(), timeout=10)
    return r.json()

# DELETE
def delete_event(event_id):
    r = requests.delete(f"{calendar_url()}&id={event_id}", timeout=10)
    return r.json()


if __name__ == "__main__":
    print("Creating event...")
    create_event(
        "Test Meeting",
        "Milestone 2 test",
        "2025-11-03T09:00",
        "2025-11-03T10:00",
        "Room 12"
    )

    print("\nListing events...")
    events = list_events()
    print(events)

    if events:
        print("\nDeleting first event...")
        delete_event(events[0]["id"])
