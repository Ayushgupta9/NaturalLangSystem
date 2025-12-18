import requests

WEATHER_API = "https://api.responsible-nlp.net/weather.php"

def get_weather(place):
    response = requests.post(
        WEATHER_API,
        data={"place": place},
        timeout=10
    )

    if response.status_code != 200:
        raise RuntimeError("Weather API request failed")

    return response.json()


if __name__ == "__main__":
    data = get_weather("Marburg")
    print(data)
