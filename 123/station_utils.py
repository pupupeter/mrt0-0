from difflib import get_close_matches
from cc import station_data

def fuzzy_search_station(query):
    all_stations = list(station_data.keys())
    return get_close_matches(query, all_stations, n=3, cutoff=0.6)

def parse_route_response(route_text):
    return [step.strip() for step in route_text.replace("。", ".").split(".") if step.strip()]
