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
    r.raise_for_status()
    return r.json()

# GET SINGLE
def get_event(event_id):
    r = requests.get(f"{calendar_url()}&id={event_id}", timeout=10)
    r.raise_for_status()
    return r.json()

# UPDATE
def update_event(event_id, **fields):
    # Only send fields that should be updated
    payload = {k: v for k, v in fields.items() if v is not None}
    r = requests.put(f"{calendar_url()}&id={event_id}", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

# DELETE
def delete_event(event_id):
    r = requests.delete(f"{calendar_url()}&id={event_id}", timeout=10)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    print("Creating event...")
    created = create_event(
        "Test Meeting",
        "Milestone 2 test",
        "2025-11-03T09:00",
        "2025-11-03T10:00",
        "Room 12"
    )
    print("Created:", created)

    print("\nListing events...")
    events = list_events()
    print(events)

    if events:
        first_id = events[0]["id"]
        print(f"\nGetting first event (id={first_id})...")
        print(get_event(first_id))

        print("\nUpdating first event location...")
        print(update_event(first_id, location="Room 1"))

        print("\nDeleting first event...")
        delete_event(events[0]["id"])
