import os
import time
from typing import Optional
import serpapi
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool

class HotelsInput(BaseModel):
    q: Optional[str] = Field(default="Paris", description='Location of the hotel')
    check_in_date: Optional[str] = Field(default="2025-11-10", description='Check-in date. The format is YYYY-MM-DD. e.g. 2024-06-22')
    check_out_date: Optional[str] = Field(default="2025-11-15", description='Check-out date. The format is YYYY-MM-DD. e.g. 2024-06-28')
    sort_by: Optional[str] = Field(default="8", description='Parameter is used for sorting the results. Default is sort by highest rating')
    adults: Optional[int] = Field(default=1, description='Number of adults. Default to 1.')
    children: Optional[int] = Field(default=0, description='Number of children. Default to 0.')
    rooms: Optional[int] = Field(default=1, description='Number of rooms. Default to 1.')
    hotel_class: Optional[str] = Field(default=None, description='Parameter defines to include only certain hotel class in the results. for example- 2,3,4')

class HotelsInputSchema(BaseModel):
    params: HotelsInput

@tool(args_schema=HotelsInputSchema)
def hotels_finder(params: HotelsInput):
    '''
    Find hotels using the Google Hotels engine.
    Returns:
        dict: Hotel search results with images.
    '''
    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_hotels',
        'hl': 'en',
        'gl': 'us',
        'q': params.q or "Paris",
        'check_in_date': params.check_in_date or "2025-11-10",
        'check_out_date': params.check_out_date or "2025-11-15",
        'currency': 'USD',
        'adults': params.adults or 1,
        'children': params.children or 0,
        'rooms': params.rooms or 1,
        'sort_by': params.sort_by or "8",
        'hotel_class': params.hotel_class
    }
    start_time = time.time()
    try:
        search = serpapi.search(params)
        results = search.data
        properties = results.get('properties', [])[:5]
        for prop in properties:
            prop['image_url'] = prop.get('thumbnail') or prop.get('image') or "https://via.placeholder.com/150"
            print(f"Hotel image URL: {prop['image_url']}")
        print(f"Hotels API took {time.time() - start_time} seconds")
        return properties
    except Exception as e:
        print(f"Hotels API error: {e}")
        return f"Error: {str(e)}"