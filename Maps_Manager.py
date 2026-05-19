import googlemaps
import datetime

class MapsManager:
    def __init__(self, api_key, home_address):
        self.gmaps = googlemaps.Client(key=api_key)
        self.home_address = home_address

    def get_transit_time(self, job_location):
        """Calculates public transport commute time from home to job."""
        try:
            # Transit requires a departure time to check the schedules
            now = datetime.datetime.now()
            
            # Requesting the matrix with mode="transit"
            matrix = self.gmaps.distance_matrix(
                origins=self.home_address, 
                destinations=job_location,
                mode="transit",
                departure_time=now
            )
            
            # Check if the API successfully found a route
            if matrix['status'] == 'OK' and matrix['rows'][0]['elements'][0]['status'] == 'OK':
                # Extracting 'duration' instead of 'distance'
                commute_time = matrix['rows'][0]['elements'][0]['duration']['text']
                return commute_time
            else:
                return "No transit route found"
                
        except Exception as e:
            print(f"✗ Maps API error: {e}")
            return "Error"