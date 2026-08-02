"""
============================================================
FILE NAME
travel_request.py

PURPOSE
Master travel inquiry object used everywhere.

INPUT
Raw customer request

OUTPUT
Structured travel request

USED BY
Universal Parser
Language Engine
Itinerary Engine
Costing Engine
CRM
Email Automation

DEPENDENCIES
dataclasses

LAST UPDATED
2026-06-04
============================================================
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class TravelRequest:

    inquiry_id:str=""
    source_type:str=""
    source_file:str=""

    customer_name:str=""
    customer_email:str=""
    customer_phone:str=""
    customer_country:str=""

    language:str="en"
    original_language:str="en"

    raw_text:str=""
    translated_text:str=""

    destinations:List[str]=field(default_factory=list)
    cities:List[str]=field(default_factory=list)
    hotels:List[str]=field(default_factory=list)
    activities:List[str]=field(default_factory=list)
    meals:List[str]=field(default_factory=list)
    transport:List[str]=field(default_factory=list)

    pax:int=0
    adults:int=0
    children:int=0
    infants:int=0

    nights:int=0
    days:int=0

    arrival_date:str=""
    departure_date:str=""

    budget:float=0
    currency:str="USD"

    hotel_category:str=""
    travel_style:str=""

    quotation_language:str="en"

    notes:str=""

    metadata:Dict[str,Any]=field(default_factory=dict)
