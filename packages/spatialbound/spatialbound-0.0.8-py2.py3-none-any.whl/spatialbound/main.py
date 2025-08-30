# main.py
import os
from spatialbound import Spatialbound

# Use environment variable or placeholder for API key
api_key = os.getenv("SPATIALBOUND_API_KEY", "your-api-key-here")
spatialbound = Spatialbound(api_key)

# Show login response
print(spatialbound.login_response)

# Example of calculating a route with coordinates (points)
coordinates = [
    [51.5360, -0.1406],  # Camden Town lat, lon
    [51.5155, -0.1420]   # Soho lat, lon
]

points_route = spatialbound.navigate(
    route_type="points",
    origin=coordinates[0],
    destinations=coordinates[1:],
    optimisation_type="shortest_path",
    mode_of_travel="walk"
)

print("Points-based route:", points_route)



# Example of calculating a route with addresses
origin_address = "10 Downing Street, London"
destination_addresses = [
    "The British Museum, London"
]

address_route = spatialbound.navigate(
    route_type="address",
    origin=origin_address,
    destinations=destination_addresses,
    optimisation_type="shortest_path",
    mode_of_travel="walk"
)

print("Address-based route:", address_route)






# main.py/  of calculating a route with postcodes
origin_postcode = "SW1A 2AA" 
destination_postcodes = [
    "W2 4QR" 
]

postcode_route = spatialbound.navigate(
    route_type="postcode",
    origin=origin_postcode,
    destinations=destination_postcodes,
    optimisation_type="shortest_path",
    mode_of_travel="drive"
)

print("Postcode-based route:", postcode_route)



# Example of analysing a location
location_analysis = spatialbound.analyse_location(
    location_type="residential",
    address="221B Baker Street, London",
    transaction_type="buy"
)
print(location_analysis)