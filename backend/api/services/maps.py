import requests

class MapsService:
    GEOCODE_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    DIRECTIONS_API_URL = 'https://maps.googleapis.com/maps/api/directions/json'
    API_KEY = 'AIzaSyC47oj2tI6UtG7ZVuM498c2iZNGMBcKW4E'

    @staticmethod
    def get_location(address):
        response = requests.get(
            MapsService.GEOCODE_API_URL,
            params={'address': address, 'key': MapsService.API_KEY}
        )
        return response.json()

    @staticmethod
    def get_directions(origin, destination):
        response = requests.get(
            MapsService.DIRECTIONS_API_URL,
            params={
                'origin': origin,
                'destination': destination,
                'key': MapsService.API_KEY
            }
        )
        return response.json()