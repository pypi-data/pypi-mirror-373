from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from ocpi_pydantic.v221.enum import OcpiImageCategoryEnum



class OcpiImage(BaseModel):
    '''
    OCPI 8.4.15. Image class

    This class references an image related to an EVSE in terms of a file name or url. According to the roaming connection between one
    EVSE Operator and one or more Navigation Service Providers, the hosting or file exchange of image payload data has to be
    defined. The exchange of this content data is out of scope of OCPI. However, the recommended setup is a public available web
    server hosted and updated by the EVSE Operator. Per charge point an unlimited number of images of each type is allowed.
    Recommended are at least two images where one is a network or provider logo and the second is a station photo. If two images of
    the same type are defined, not only one should be selected but both should be displayed together.

    Photo Dimensions: The recommended dimensions for all photos is a minimum width of 800 pixels and a minimum height of 600
    pixels. Thumbnail should always have the same orientation as the original photo with a size of 200 by 200 pixels.
    
    Logo Dimensions: The recommended dimensions for logos are exactly 512 pixels in width height. Thumbnail representations of
    logos should be exactly 128 pixels in width and height. If not squared, thumbnails should have the same orientation as the original.
    '''
    url: HttpUrl = Field(description='URL from where the image data can be fetched through a web browser.')
    thumbnail: Annotated[HttpUrl | None, Field(description='URL from where a thumbnail of the image can be fetched through a webbrowser.')] = None
    category: OcpiImageCategoryEnum = Field(description='Describes what the image is used for.')
    type: str = Field(description='Image type like: gif, jpeg, png, svg.')
    width: int | None = Field(None, description='Width of the full scale image.', gt=0, le=99999)
    height: int | None = Field(None, description='Height of the full scale image.', gt=0, le=99999)

    _example: ClassVar[dict] = {
        'url': 'https://wnc.com.tw/wp-content/uploads/2022/07/logo_banner_blue.png',
        'category': 'OPERATOR',
        'type': 'png',
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiBusinessDetails(BaseModel):
    '''
    OCPI 8.4.2. BusinessDetails class
    '''
    name: str = Field(max_length=100, description='Name of the operator.')
    website: HttpUrl | None = Field(None, description='Link to the operator’s website.')
    logo: OcpiImage | None = Field(None, description='Image link to the operator’s logo.')

    _example: ClassVar[dict] = {
        'name': 'WNC',
        'website': 'https://www.wnc.com.tw',
        # 'logo': OcpiImage._example,
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiGeoLocation(BaseModel):
    '''
    OCPI 8.4.13. GeoLoation class

    - WGS 84 坐標系。
    '''
    latitude: str = Field(description='Latitude of the point in decimal degree.', max_length=10)
    longitude: str = Field(description='Longitude of the point in decimal degree.', max_length=11)

    _example: ClassVar[dict] = {"latitude": "51.047599", "longitude": "3.729944"}
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})


