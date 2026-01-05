from datetime import datetime, date, timedelta

from asr_tts import listen_once, speak
from api_weather import get_weather
from api_calendar import create_event, list_events, delete_event, update_event
from nlu import parse_intent

# ======================================================
# Conversation state
# ======================================================
conversation_state = {
    "last_place": None,
    "last_day": None,
    "last_created_event_id": None,
    "last_referenced_event_id": None
}

def set_reference(event_id):
    if event_id:
        conversation_state["last_referenced_event_id"] = event_id


# ======================================================
# Main intent handler
# ======================================================
def handle_intent(intent, state):
    if not intent or "intent" not in intent:
        return "Sorry, I did not understand that."

    name = intent["intent"]

    # WEATHER INTENTS
    if name in ["get_weather", "check_rain"]:
        return handle_weather(intent, state)

    # CALENDAR INTENTS
    if name == "create_event":
        return handle_create_event(intent, state)
    if name == "delete_last_event":
        return handle_delete_last_event(intent, state)
    if name == "delete_this_event":
        return handle_delete_this_event(intent, state)
    if name == "get_next_event":
        return handle_get_next_event(intent, state)
    if name == "update_event_location_for_day":
        return handle_update_event_location_for_day(intent, state)
    if name == "update_this_event_location":
        return handle_update_this_event_location(intent, state)

    return "Sorry, I did not understand that."


# ======================================================
# WEATHER HANDLERS
# ======================================================
def handle_weather(intent, state):
    place = intent.get("place") or state.get("last_place")
    day = intent.get("day") or date.today()

    if not place:
        return "I am not sure which place you mean."

    state["last_place"] = place
    state["last_day"] = day

    data = get_weather(place)
    if data.get("error"):
        return "Sorry, I could not reach the weather service."

    forecast = data.get("forecast", [])
    target = day.strftime("%A").lower()

    for entry in forecast:
        if entry.get("day", "").lower() == target:
            weather = entry.get("weather", "unknown")
            temp = entry.get("temperature", {})
            if intent["intent"] == "check_rain":
                if "rain" in weather.lower() or "shower" in weather.lower():
                    return f"Yes, it will rain in {place} on {day.strftime('%A')}."
                else:
                    return f"No, it will not rain in {place} on {day.strftime('%A')}."
            else:
                return (
                    f"The weather in {place} on {day.strftime('%A')} will be "
                    f"{weather}, between {temp.get('min', '?')} and {temp.get('max', '?')} degrees."
                )

    return f"I could not find a forecast for {place} on {day.strftime('%A')}."


# ======================================================
# CALENDAR HANDLERS
# ======================================================
def handle_create_event(intent, state):
    title = intent.get("title", "Untitled")
    event_date = intent.get("date", date.today())

    start_time = datetime.combine(event_date, datetime.min.time()).replace(hour=9, minute=0)
    end_time = start_time + timedelta(hours=1)

    created = create_event(
        title=title,
        description=title,
        start_time=start_time.isoformat(timespec="minutes"),
        end_time=end_time.isoformat(timespec="minutes"),
        location=intent.get("location", "Office")
    )

    event_id = created.get("id")
    state["last_created_event_id"] = event_id
    set_reference(event_id)

    return (
        f"I have added an appointment titled '{title}' on "
        f"{event_date.strftime('%A, %d %B %Y')} at {start_time.strftime('%H:%M')}."
    )


def handle_delete_last_event(intent, state):
    event_id = state.get("last_created_event_id")
    if not event_id:
        return "I do not know which appointment you want to delete."
    delete_event(event_id)
    state["last_created_event_id"] = None
    return "I have deleted the previously created appointment."


def handle_delete_this_event(intent, state):
    event_id = state.get("last_referenced_event_id")
    if not event_id:
        return "I do not know which appointment you mean."
    delete_event(event_id)
    return "I have deleted this appointment."


def handle_get_next_event(intent, state):
    events = list_events()
    if not events:
        return "You have no appointments."

    now = datetime.now()
    future = []
    for e in events:
        try:
            dt = datetime.fromisoformat(e["start_time"])
            if dt >= now:
                future.append((dt, e))
        except:
            continue

    if not future:
        return "You have no upcoming appointments."

    future.sort(key=lambda x: x[0])
    dt, event = future[0]
    set_reference(event["id"])

    return (
        f"Your next appointment is '{event.get('title', 'Untitled')}' on "
        f"{dt.strftime('%A, %d %B %Y at %H:%M')} in {event.get('location', 'unknown location')}."
    )


def handle_update_event_location_for_day(intent, state):
    event_date = intent.get("day")
    new_location = intent.get("location")
    if not event_date:
        return "I did not understand which day the appointment is on."
    if not new_location:
        return "I did not understand the new location."

    events = list_events()
    for e in events:
        try:
            dt = datetime.fromisoformat(e["start_time"])
            if dt.date() == event_date:
                update_event(e["id"], location=new_location)
                set_reference(e["id"])
                return (
                    f"I have changed the location of your appointment on "
                    f"{event_date.strftime('%A, %d %B %Y')} to {new_location}."
                )
        except:
            continue

    return f"I could not find an appointment on {event_date.strftime('%A, %d %B %Y')}."


def handle_update_this_event_location(intent, state):
    event_id = state.get("last_referenced_event_id")
    new_location = intent.get("location")
    if not event_id:
        return "I do not know which appointment you mean."
    if not new_location:
        return "I did not understand the new location."

    update_event(event_id, location=new_location)
    return f"I have updated the location of this appointment to {new_location}"


# ======================================================
# MAIN LOOP (for testing only)
# ======================================================
if __name__ == "__main__":
    speak("Assistant module loaded successfully.")