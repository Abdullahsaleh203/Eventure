#!/usr/bein/env python3
import requests
"""Google Maps Services"""


class MapsService:
    """
    A class that make requests with GoogleMapApi
    """
    GEOCODE_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    DIRECTIONS_API_URL = 'https://maps.googleapis.com/maps/api/directions/json'
    API_KEY = 'AIzaSyC47oj2tI6UtG7ZVuM498c2iZNGMBcKW4E'

    @staticmethod
    def get_location(address):
        """
        A method that return the location with JSON format

        Args:
            addres (str): the argument that
                    want to get full location info.

        Returns:
            json object
        """
        response = requests.get(
            MapsService.GEOCODE_API_URL,
            params={'address': address, 'key': MapsService.API_KEY}
        )
        return response.json()

    @staticmethod
    def get_directions(origin, destination):
        """
        A method that return directions
        between two places with JSON format

        Args:
            origin (str): the current location.
            destination (str): the destination location.

        Returns:
            json object
        """
        response = requests.get(
            MapsService.DIRECTIONS_API_URL,
            params={
                'origin': origin,
                'destination': destination,
                'key': MapsService.API_KEY
            }
        )
        return response.json()
