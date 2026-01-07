import re
from datetime import date, datetime, timedelta

DEBUG = True  # Set to False to silence debug logs

WEEKDAYS = [
    "monday", "tuesday", "wednesday",
    "thursday", "friday", "saturday", "sunday"
]

FUZZY_ORDINALS = {
    "first": 1, "1st": 1,
    "second": 2, "2nd": 2, "sacond": 2, "sagand": 2, "mileage": 2, "much": 2,
    "third": 3, "3rd": 3, "therd": 3,
    "fourth": 4, "4th": 4,
    "fifth": 5, "5th": 5, "fit": 5,
    "sixth": 6, "6th": 6,
    "seventh": 7, "7th": 7,
    "eighth": 8, "8th": 8,
    "ninth": 9, "9th": 9,
    "tenth": 10, "10th": 10,
    "eleventh": 11, "11th": 11,
    "twelfth": 12, "12th": 12, "twelth": 12, "twelf": 12,
    "thirteenth": 13, "13th": 13,
    "fourteenth": 14, "14th": 14,
    "fifteenth": 15, "15th": 15,
    "sixteenth": 16, "16th": 16,
    "seventeenth": 17, "17th": 17,
    "eighteenth": 18, "18th": 18,
    "nineteenth": 19, "19th": 19,
    "twentieth": 20, "20th": 20, "twenty": 20,
    "twenty first": 21, "21st": 21,
    "twenty second": 22, "22nd": 22,
    "twenty third": 23, "23rd": 23,
    "twenty fourth": 24, "24th": 24,
}

FUZZY_MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3, "much": 3, "marge": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

KNOWN_PLACES = [
    "marburg", "frankfurt", "berlin", "hamburg", "munich",
    "kassel", "giessen", "gießen", "cologne", "stuttgart", "leipzig"
]


def dprint(*args):
    if DEBUG:
        print("[NLU]", *args)


def parse_intent(text, state):
    text = text.lower().strip()
    dprint("RAW TEXT:", text)

def parse_intent(text, state):
    text = text.lower().strip()
    dprint("RAW:", text)

    # GREETINGS
    if any(w in text for w in ["hello", "hi", "hey", "good morning", "good evening"]):
        return {"intent": "greeting"}

    if any(w in text for w in ["how are you", "how are you doing"]):
        return {"intent": "how_are_you"}

    # WEATHER
    if any(w in text for w in ["weather", "temperature", "forecast", "whether", "rain"]):
        place = extract_place(text, state)
        day = extract_day(text, state)

        if "rain" in text:
            return {"intent": "check_rain", "place": place, "day": day}

        return {"intent": "get_weather", "place": place, "day": day}


    # ---------- DELETE (PRIORITY over create) ----------
    if any(w in text for w in ["delete", "remove", "cancel"]):
        # explicit "this appointment"
        if "this appointment" in text or "this event" in text:
            return {"intent": "delete_this_event"}
        # "previously created appointment"
        if "previous" in text or "previously" in text:
            return {"intent": "delete_last_event"}
        # generic "delete the appointment", "delete my appointment"
        return {"intent": "delete_last_event"}

    # CREATE APPOINTMENT
    if ("add" in text or "create" in text or "and an appointment" in text):
        if "appointment" in text or "meeting" in text or "event" in text:
            title = extract_title(text)
            day = extract_day(text, state)
            return {"intent": "create_event", "title": title, "date": day}

    # NEXT APPOINTMENT
    if "next appointment" in text or "my next appointment" in text:
        return {"intent": "get_next_event"}

    # UPDATE LOCATION
    if "change" in text or "update" in text:
        if "location" in text or "place" in text:
            new_loc = extract_new_location(text)
            if "this" in text:
                return {"intent": "update_this_event_location", "location": new_loc}
            day = extract_day(text, state)
            return {"intent": "update_event_location_for_day", "day": day, "location": new_loc}

    return {"intent": "unknown"}


def extract_place(text, state):
    m = re.search(r"in ([a-zA-Zäöüß]+)", text)
    if m:
        candidate = m.group(1)
        if candidate in KNOWN_PLACES:
            return candidate

    for city in KNOWN_PLACES:
        if city in text:
            return city

    return state.get("last_place")


def extract_title(text):
    if "doctor" in text:
        return "doctor"
    if "dentist" in text:
        return "dentist"

    m = re.search(r"appointment titled ([a-zA-Z0-9 ]+)", text)
    if m:
        return m.group(1).strip()

    m = re.search(r"appointment for ([a-zA-Z0-9 ]+)", text)
    if m:
        return m.group(1).strip()

    return "Untitled appointment"


def extract_new_location(text):
    m = re.search(r"to ([a-zA-Z0-9 ]+)$", text)
    if m:
        loc = m.group(1).strip()
        loc = loc.replace("appointment", "").replace("location", "").strip()
        return loc
    return None


def extract_day(text, state):
    today = date.today()
    text = text.lower()

    if "today" in text:
        return today
    if "tomorrow" in text:
        return today + timedelta(days=1)

    for i, name in enumerate(WEEKDAYS):
        if name in text:
            return next_weekday(today, i)

    words = text.split()

    for w in words:
        if w in FUZZY_ORDINALS:
            day_num = FUZZY_ORDINALS[w]
            for m in words:
                if m in FUZZY_MONTHS:
                    month_num = FUZZY_MONTHS[m]
                    year = today.year
                    try:
                        d = date(year, month_num, day_num)
                        if d < today:
                            d = date(year + 1, month_num, day_num)
                        return d
                    except:
                        pass

    m = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december) (\d+)", text)
    if m:
        month = FUZZY_MONTHS[m.group(1)]
        day_num = int(m.group(2))
        d = date(today.year, month, day_num)
        if d < today:
            d = date(today.year + 1, month, day_num)
        return d

    return state.get("last_day")


def next_weekday(start_date, weekday_index):
    days_ahead = weekday_index - start_date.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)
