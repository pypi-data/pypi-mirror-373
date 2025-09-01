
from typing import List, Union
import numpy as np
from seed_vault.ui.components.map import normalize_circle, normalize_bounds
import streamlit as st
import os
import jinja2

from obspy.geodetics import kilometer2degrees

from seed_vault.models.common import RectangleArea, CircleArea
from seed_vault.enums.common import GeometryType
from seed_vault.models.config import SeismoLoaderSettings, GeometryConstraint


current_directory = os.path.dirname(os.path.abspath(__file__))
target_file = os.path.join(current_directory, '../../../service/config.cfg')
target_file = os.path.abspath(target_file)

target_file_direct = os.path.join(current_directory, '../../../service/config_direct.cfg')
target_file_direct = os.path.abspath(target_file_direct)


def empty_settings_geo_constraints(settings: SeismoLoaderSettings):
    """
    TODO: a function that reads the latest app settings
    """
    if(settings.event):
        settings.event.geo_constraint = []
    if(settings.station):
        settings.station.geo_constraint = []        
    return settings


def get_app_settings(create_new: bool = True, empty_geo: bool = True):
    if "app_settings" not in st.session_state:
        settings = SeismoLoaderSettings.from_cfg_file(target_file)
        settings.client_url_mapping.load()
        st.session_state.app_settings = settings
    else:
        if create_new:
            settings = SeismoLoaderSettings.from_cfg_file(target_file)
            settings.client_url_mapping.load()
            st.session_state.app_settings = settings
    
    if empty_geo:
        st.session_state.app_settings = empty_settings_geo_constraints(st.session_state.app_settings)

    return st.session_state.app_settings


def set_app_settings(settings: SeismoLoaderSettings):
    st.session_state.app_settings = settings


def get_direct_settings(create_new: bool = True, empty_geo: bool = True):
    if "direct_settings" not in st.session_state:
        settings = SeismoLoaderSettings.from_cfg_file(target_file_direct)
        settings.client_url_mapping.load()
        st.session_state.direct_settings = settings          
    else:
        if create_new:
            settings = SeismoLoaderSettings.from_cfg_file(target_file_direct)
            settings.client_url_mapping.load()
            st.session_state.direct_settings = settings
   
    if empty_geo:
        st.session_state.direct_settings = empty_settings_geo_constraints(st.session_state.direct_settings)

    return st.session_state.direct_settings


def set_direct_settings(settings: SeismoLoaderSettings):
    st.session_state.direct_settings = settings


def save_filter(settings:  SeismoLoaderSettings):
    set_app_settings(settings)
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(current_directory, '../../../service')
    target_file = os.path.abspath(target_file)
    
    template_loader = jinja2.FileSystemLoader(searchpath=target_file)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("config_template.cfg")
    config_dict = get_app_settings(create_new=False, empty_geo=False).add_to_config()
    config_str = template.render(**config_dict)
    
    save_path = os.path.join(target_file, "config" + ".cfg")
    with open(save_path, "w") as f:
        f.write(config_str)
    
    return save_path

def reset_config():
    return SeismoLoaderSettings.create_default()
        
def handle_polygon(geo) -> GeometryConstraint:
    coords_arr = np.array(geo.get("geometry").get("coordinates")[0])
    max_vals   = coords_arr.max(axis=0)
    min_vals   = coords_arr.min(axis=0)

    return GeometryConstraint(
            coords = RectangleArea(
            min_lat = min_vals[1],
            min_lon = min_vals[0],
            max_lat = max_vals[1],
            max_lon = max_vals[0],
        )
    )


def handle_circle(geo) -> GeometryConstraint:
    coords = geo.get("geometry").get("coordinates")
    # min_radius = geo.get("properties").get("min_radius")
    # max_radius = geo.get("properties").get("max_radius")
    radius = geo.get("properties").get("radius") #this is in "meters"

    if radius is None:
        raise ValueError("Radius is missing in the geo properties")    

    return GeometryConstraint(
            coords = CircleArea(
            lat = coords[1],
            lon = coords[0],
            min_radius = 0,
            max_radius = kilometer2degrees(radius/1000)
        )
    )


def get_selected_areas(map_output) -> List[Union[RectangleArea, CircleArea]]:
    lst_locs = []
    k = "all_drawings"
    
    if map_output.get(k):
        for geo in map_output.get(k):
            geom_type = geo.get("geometry").get('type')
            
            if geom_type == GeometryType.POLYGON:
                geometry_constraint = handle_polygon(geo)                
                split_constraints = normalize_bounds(geometry_constraint)
                for constraint in split_constraints:
                    lst_locs.append(constraint)
                continue

            if geom_type == GeometryType.POINT:
                geometry_constraint = handle_circle(geo)                
                split_constraints = normalize_circle(geometry_constraint)
                for constraint in split_constraints:
                    lst_locs.append(constraint)
                continue                

            raise ValueError(f"Geometry Type {geom_type} not supported!")
        
    return lst_locs
