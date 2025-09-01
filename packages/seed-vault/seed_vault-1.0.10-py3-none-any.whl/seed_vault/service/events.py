"""
The events service should get the events based on a selection (filter) settings.
UI should generate the selection and pass it here. We need a single function
here that gets the selection and runs Rob's script.

We should also be able to support multi-select areas.

@TODO: For now, dummy scripts are used. @Yunlong to fix.
"""

import pandas as pd
import streamlit as st
import requests

from obspy.core.event import Catalog

from seed_vault.models.config import SeismoLoaderSettings
from seed_vault.service.seismoloader import get_events


# @st.cache_data
# def get_event_data(settings_json_str: str):

#     settings = SeismoLoaderSettings.model_validate_json(settings_json_str)
#     return get_events(settings)


def remove_duplicate_events(events):
    unique_resource_ids = set()
    unique_events = Catalog()

    for event in events:
        resource_id = event.resource_id.id #the .id makes it a string
        if resource_id not in unique_resource_ids:
            unique_resource_ids.add(resource_id)
            unique_events.append(event)

    return unique_events

# @st.cache_data
def get_event_data(settings: SeismoLoaderSettings):
    return remove_duplicate_events(get_events(settings))

def event_response_to_df(data):
    """
    @TODO: base on response from FSDN, below should be re-written
    """
    records = []
    for event in data:
        # Extract the preferred origin (location info)
        origin = event.preferred_origin() or event.origins[0]
        magnitude = event.preferred_magnitude() or event.magnitudes[0]
        
        # Extract location (longitude, latitude, depth)
        longitude = origin.longitude
        latitude = origin.latitude
        depth = origin.depth / 1000 if origin.depth is not None else 0.99999  # Convert depth to kilometers

        # Extract the time and place
        time = origin.time.datetime
        place = event.event_descriptions[0].text if event.event_descriptions else "Unknown place"

        # Extract the magnitude
        mag = magnitude.mag if magnitude.mag is not None else 0.99999
        mag_type = magnitude.magnitude_type if magnitude.magnitude_type is not None else "[-]"
        # Create the record dictionary
        record = {
            'place': place,
            'magnitude': mag,
            'magnitude type': mag_type,
            'time': pd.to_datetime(time),  # Convert to pandas datetime
            'longitude': longitude,
            'latitude': latitude,
            'depth (km)': depth,  # in kilometers
        }

        records.append(record)
    return pd.DataFrame(records)