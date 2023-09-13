from __future__ import annotations
import enum


class Geography(enum.Enum):
    US = "us"
    REGION = "region"
    DIVISION = "division"
    STATE = "state"
    COUNTY = "county"
    COUNTY_SUBDIVISION = "county subdivision"
    PLACE = "place"
    ALASKA_NATIVE_REGIONAL_CORPORATION = "alaska native regional corporation"
    CONGRESSIONAL_DISTRICT = "congressional district"
    PUBLIC_USE_MICRODATA_AREA = "public use microdata area"
    SCHOOL_DISTRICT_ELEMENTARY = "school district (elementary)"
    SCHOOL_DISTRICT_SECONDARY = "school district (secondary)"
    SCHOOL_DISTRICT_UNIFIED = "school district (unified)"
    AMERICAN_INDIAN_ALASKA_NATIVE_HAWIIAN = "american indian area/alaska native area/hawaiian home land"
    METROPOLITAN_MICROPOLITAN_STATISTICAL_AREA = "metropolitan statistical area/micropolitan statistical area"
    STATE_OR_PART = "state (or part)"
    PRINCIPAL_CITY_OR_PART = "principal city (or part)"
    METROPOLITAN_DIVISION = "metropolitan division"
    COMBINED_STATISTICAL_AREA = "combined statistical area"
    COMBINED_NEW_ENGLAND_CITY_AND_TOWN_AREA = "combined new england city and town area"
    NEW_ENGLAND_CITY_AND_TOWN_AREA = "new england city and town area"
    PRINCIPAL_CITY = "principal city"
    NECTA_DIVISION = "necta division"
    URBAN_AREA = "urban area"



    # """Geographies, meaning districts or regions, referencing both census and election data definitions, prioritizing census definitions"""
    #
    # TRACT = "tract"
    # CD = "congressional district"
    # COUNTY = "county"
    # STATE = "state"
    # ZCTA = "zip code tabulation area"
    # BLOCK = "block"
    # BLOCKGROUP = "block group"
    # # NEW:
    # SL = "state legislative district (lower)"
    # UL = "state legislative district (upper)"
    # PRECINCT = "precinct"
    #
    #
    # def __init__(self, geo_type, id: str, name: str, shape=None):
    #     self.geo_type = geo_type
    #     self.id = id
    #     self.name = name
    #     self.shape = shape
    #
    #
    #
    # def find_intersections(self, other_geography):
    #     """
    #     Returns bool if self intersects with other_geography
    #
    #     If "shape" is not defined for this geographi
    #     """
    #     return None