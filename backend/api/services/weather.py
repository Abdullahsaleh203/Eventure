import requests


class WeatherService:
    API_URL = 'https://api.openweathermap.org/data/2.5/weather'
    API_KEY = 'your_openweathermap_api_key'

    @staticmethod
    def get_weather(location):
        response = requests.get(
            WeatherService.API_URL,
            params={'q': location, 'appid': WeatherService.API_KEY}
        )
        return response.json()
