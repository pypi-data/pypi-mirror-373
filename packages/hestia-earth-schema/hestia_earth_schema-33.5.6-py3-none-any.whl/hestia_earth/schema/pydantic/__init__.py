from pydantic import AliasChoices

from hestia_earth.schema import SchemaType

import datetime

from typing import Annotated

from typing import Annotated

from pydantic import PlainSerializer

from pydantic import BeforeValidator, PlainSerializer

from decimal import Decimal

DecimalValue = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used='json')]

DateYear = Annotated[datetime.date, BeforeValidator(lambda x: datetime.datetime.strptime(x, '%Y')), PlainSerializer(lambda x: x.strftime('%Y'))]





import datetime

from pydantic import BeforeValidator, PlainSerializer

from typing import Annotated

from decimal import Decimal

from pydantic import PlainSerializer

from __future__ import annotations

from enum import Enum

from typing import List, Optional

from pydantic import BaseModel, Extra, Field, confloat, constr

class Type(Enum):
    Bibliography = 'Bibliography'

class FieldType(Enum):
    Bibliography = 'Bibliography'

class Bibliography1(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    name: str = Field(..., description='An automatically generated citation in the format: lastName (year) for a single author or institution, lastName & lastName (year) for two authors or institutions, or lastName et al (year) for more than two authors or institutions.', examples=['Poore & Nemecek (2018)'])
    documentDOI: Optional[constr(regex='^10.(\\d)+\\/(\\S)+$')] = Field(None, description='A unique number made up of a prefix and a suffix separated by a forward slash, e.g. 10.1000/182.', examples=['10.1126/science.aaq0216'])
    title: str = Field(..., description='The title of the document or database.', examples=["Reducing food's environmental impacts through producers and consumers"])
    arxivID: Optional[str] = Field(None, description='The arXiv ID.', examples=[])
    scopus: Optional[str] = Field(None, description='The Scopus ID.', examples=['2-s2.0-85048197694'])
    mendeleyID: Optional[str] = Field(None, description='The Mendeley ID.', examples=['9ecd6598-d3c7-36a3-965b-821be771b328'])
    authors: List[Actor] = Field(..., description='The authors of the document or database.', examples=[[{'@id': 'avvs577', '@type': 'Actor', 'name': 'J. Poore, Univerity of Oxford'}, {'@id': 'gyys7s9', '@type': 'Actor', 'name': 'T. Nemecek, Agroscope'}]])
    outlet: str = Field(..., description='Where the document or database was published (can be "unpublished").', examples=['Science'])
    year: confloat(ge=0.0) = Field(..., description='The year the document or database was published, or the year this version of the database was released.', examples=[2018])
    volume: Optional[confloat(ge=0.0)] = Field(None, description='The volume holding the document.', examples=[])
    issue: Optional[str] = Field(None, description='The issue holding the document.', examples=[])
    chapter: Optional[str] = Field(None, description='The chapter.', examples=[])
    pages: Optional[str] = Field(None, description='The range of pages the document covers, e.g., 4-8.', examples=[])
    publisher: Optional[str] = Field(None, description='The publisher of the document or database.', examples=[])
    city: Optional[str] = Field(None, description='The city of the publisher.', examples=[])
    editors: Optional[List[Actor]] = Field(None, description='The editors of the document or database.', examples=[])
    institutionPub: Optional[List[Actor]] = Field(None, description='The institutions who published the document or database.', examples=[])
    websites: Optional[List[str]] = Field(None, description='Websites where the document or database was accessed from.', examples=[])
    articlePdf: Optional[str] = Field(None, description='A link to a freely available pdf version of this article.', examples=[])
    dateAccessed: Optional[List[str]] = Field(None, description='A corresponding list of dates the webpages were accessed in ISO 8601 format (YYYY-MM-DD).', examples=[])
    abstract: Optional[str] = Field(None, description='A brief summary of the document or database.', examples=["Food's environmental impacts are created by millions of diverse producers. To identify solutions that are effective under this heterogeneity, we consolidated data covering five environmental indicators; 38,700 farms; and 1600 processors, packaging types, and retailers. Impact can vary 50-fold among producers of the same product, creating substantial mitigation opportunities. However, mitigation is complicated by trade-offs, multiple ways for producers to achieve low impacts, and interactions throughout the supply chain. Producers have limits on how far they can reduce impacts. Most strikingly, impacts of the lowest-impact animal products typically exceed those of vegetable substitutes, providing new evidence for the importance of dietary change. Cumulatively, our findings support an approach where producers monitor their own impacts, flexibly meet environmental targets by choosing from multiple practices, and communicate their impacts to consumers."])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])

class Bibliography(BaseModel):

    class Config:
        extra = Extra.forbid
    __root__: Bibliography1 = Field(..., description='Information uniquely describing the document or database.', title='Bibliography')

from pydantic import BaseModel, Extra, Field, PositiveFloat

class OwnershipStatus(Enum):
    owned = 'owned'
    rented = 'rented'
    borrowed = 'borrowed'

class MethodClassification(Enum):
    physical_measurement = 'physical measurement'
    verified_survey_data = 'verified survey data'
    non_verified_survey_data = 'non-verified survey data'
    modelled = 'modelled'
    estimated_with_assumptions = 'estimated with assumptions'
    consistent_external_sources = 'consistent external sources'
    inconsistent_external_sources = 'inconsistent external sources'
    expert_opinion = 'expert opinion'
    unsourced_assumption = 'unsourced assumption'

class Infrastructure(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    term: Term = Field(..., description='A reference to the Term describing the Infrastructure.', examples=[{'@id': 'dripIrrigationEquipment', '@type': 'Term', 'name': 'Drip irrigation equipment', 'termType': 'irrigation'}])
    name: Optional[str] = Field(None, description='A name for the Infrastructure, if not described by a Term.', examples=[])
    description: Optional[str] = Field(None, description='A short description of the Infrastructure. Use this to specify the machinery brand name or manufacturer name (e.g., "Valtra BM 100" or "John Deere 5090E").', examples=[])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The date when the Infrastructure was built ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=['1988-01-01'])
    endDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The (expected) date when the Infrastructure was (will be) dismantled ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    defaultLifespan: Optional[PositiveFloat] = Field(None, description='The (expected) lifespan of all Inputs required to create the Infrastructure, expressed in decimal years. Equal to endDate - startDate. If each Input has a different lifespan (e.g., the greenhouse glass lasts for 5 years while the metal frame lasts for 20 years) this should be specified for each Input.', examples=[25])
    defaultLifespanHours: Optional[PositiveFloat] = Field(None, description='The (expected) lifespan, expressed in hours.', examples=[])
    mass: Optional[PositiveFloat] = Field(None, description='The mass of the Infrastructure, expressed in kilograms.', examples=[])
    area: Optional[PositiveFloat] = Field(None, description='The area of the Infrastructure, expressed in hectares.', examples=[])
    ownershipStatus: Optional[OwnershipStatus] = Field(None, description='The ownership status of the Infrastructure.', examples=[])
    methodClassification: Optional[MethodClassification] = Field(None, description='A classification of the method used to acquire or estimate the term and value. Overrides the defaultMethodClassification specified in the Site.    physical measurement means the amount is quantified using weighing,\n    volume measurement, metering, chemical methods, or other physical approaches.\n\n    verified survey data means the data are initially collected through\n    surveys; all or a subset of the data are verified using physical methods; and\n    erroneous survey data are discarded or corrected.\n\n    non-verified survey data means the data are collected through\n    surveys that have not been subjected to verification.\n\n    modelled means a previously calibrated model is used to estimate\n    this data point from other data points describing this Cycle.\n\n    estimated with assumptions means a documented assumption is used\n    to estimate this data point from other data points describing this Cycle.\n\n    consistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using the same technology (defined as the same\n        System or the same key Practices\n        as those specified in the Cycle);\n\n        At the same date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        and\n\n        In the same region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    inconsistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using a different technology (defined as a different\n        System or using different key\n        Practices to those specified in the Cycle);\n\n        At a different date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        or\n\n        In a different region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    expert opinion means the data have been estimated by experts in\n    the field.\n\n    unsourced assumption means the data do not have a clear source\n    and/or are based on assumptions only.\n', examples=[])
    methodClassificationDescription: Optional[str] = Field(None, description='A justification of the methodClassification used. If the data were estimated with assumptions this field should also describe the assumptions. This is a required field if methodClassification is specified.', examples=[])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data, if different from the Source of the Site.', examples=[{'@id': 's66765d', '@type': 'Source', 'name': 'Gigou (1990)'}])
    impactAssessment: Optional[ImpactAssessment] = Field(None, description='A reference to the node containing environmental impact data related to producing this Infrastructure.', examples=[])
    inputs: Optional[List[Input]] = Field(None, description='The Inputs required to create the Infrastructure.', examples=[[{'@type': 'Input', 'term': {'@id': 'polyvinylChloride', '@type': 'Term', 'name': 'Polyvinyl Chloride', 'units': 'kg', 'termType': 'material'}, 'value': [1100]}]])
    transport: Optional[List[Transport]] = Field(None, description='A list of Transport stages to bring this Product to the Cycle.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])

from datetime import date

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra, Field, PositiveFloat, confloat, constr

class SiteType(Enum):
    forest = 'forest'
    other_natural_vegetation = 'other natural vegetation'
    cropland = 'cropland'
    glass_or_high_accessible_cover = 'glass or high accessible cover'
    permanent_pasture = 'permanent pasture'
    animal_housing = 'animal housing'
    pond = 'pond'
    river_or_stream = 'river or stream'
    lake = 'lake'
    sea_or_ocean = 'sea or ocean'
    agri_food_processor = 'agri-food processor'
    food_retailer = 'food retailer'

class Tenure(Enum):
    farming_on_owned_land = 'farming on owned land'
    farming_on_rented_land = 'farming on rented land'
    farming_on_common_land = 'farming on common land'
    share_farming = 'share farming'
    other_tenure_model = 'other tenure model'

class DefaultMethodClassification(Enum):
    physical_measurement = 'physical measurement'
    verified_survey_data = 'verified survey data'
    non_verified_survey_data = 'non-verified survey data'
    modelled = 'modelled'
    estimated_with_assumptions = 'estimated with assumptions'
    consistent_external_sources = 'consistent external sources'
    inconsistent_external_sources = 'inconsistent external sources'
    expert_opinion = 'expert opinion'
    unsourced_assumption = 'unsourced assumption'

class Site(BaseModel):

    class Config:
        extra = Extra.forbid
    id: str = Field(validation_alias=AliasChoices('@id', 'id'), serialization_alias='@id', description='Unique id assigned by HESTIA')
    
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    name: Optional[str] = Field(None, description='An automatically generated name for the Site composed of: siteType, "-", organisation.name, "-", region "," country, "-", description.', examples=['Field 1', 'Land use change example'])
    description: Optional[str] = Field(None, description='A description of the Site, including information that cannot be captured with other fields.', examples=[])
    organisation: Optional[Organisation] = Field(None, description='A reference to the Organisation this Site is managed by.', examples=[{'@id': 'orhaa1', '@type': 'Organisation', 'name': 'La Ferme du Grand Roc'}])
    siteType: SiteType = Field(..., description='The type of the Site. Definitions for agricultural land follow FAOSTAT, where cropland here means arable land and permanent crops. The additional term "glass or high accessible cover" is defined by EUROSTAT.', examples=['cropland', 'cropland'])
    tenure: Optional[Tenure] = Field(None, description='The ownership status of the Site following EUROSTAT terminology.', examples=[])
    numberOfSites: Optional[confloat(ge=1.0)] = Field(None, description='If data on multiple Sites are aggregated and represented as a single Site, the number of Sites.', examples=[])
    boundary: Optional[Dict[str, Any]] = Field(None, description="A nested GeoJSON object for the Site boundary of type 'FeatureCollection', 'Feature' or 'GeometryCollection' in the WGS84 datum. For cropland the boundary should represent area under cultivation (also called sown area).", examples=[{'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Polygon', 'coordinates': [[[6.9052934646606445, 49.16690366996946], [6.903340816497803, 49.16568302182135], [6.900680065155029, 49.16423784775604], [6.9001007080078125, 49.16369063491694], [6.8998003005981445, 49.163255666551734], [6.900315284729004, 49.16308729067498], [6.901495456695557, 49.16392916433382], [6.903705596923828, 49.165023578693386], [6.903920173645019, 49.1649534246523], [6.906323432922362, 49.16608990788086], [6.9052934646606445, 49.16690366996946]]]}}]}])
    area: Optional[PositiveFloat] = Field(None, description='The area of the Site in hectares. For cropland, this must be area under cultivation, also called sown area. Harvested area, which can be less than sown area, can be defined for each Cycle using the field harvestedArea. If data from more than one Site has been averaged (numberOfSites is greater than one) the area must also be the mean area across Sites and not the sum of areas. If the Site is a country or region, the area must be the area represented by the Cycle data (e.g., the area of the sampled farms or the area of maize production in a country).', examples=[4.465786])
    areaSd: Optional[PositiveFloat] = Field(None, description='The standard deviation of area, if there are multiple Sites.', examples=[])
    areaMin: Optional[PositiveFloat] = Field(None, description='The minimum of area, if there are multiple Sites.', examples=[])
    areaMax: Optional[PositiveFloat] = Field(None, description='The maximum of area, if there are multiple Sites.', examples=[])
    latitude: Optional[confloat(ge=-90.0, le=90.0)] = Field(None, description='The latitude of the centroid of the Site (-90 to 90, WGS84 datum). Latitude should be provided with at least five decimal place precision (which roughly corresponds to 1 meter precision at the equator).', examples=[])
    longitude: Optional[confloat(ge=-180.0, le=180.0)] = Field(None, description='The longitude of the centroid of the Site (-180 to 180, WGS84 datum). Longitude should be provided with at least five decimal place precision.', examples=[])
    country: Term = Field(..., description='The country from the Glossary.', examples=[{'@id': 'GADM-FRA', '@type': 'Term', 'name': 'France', 'termType': 'region'}, {'@id': 'GADM-BRA', '@type': 'Term', 'name': 'Brazil', 'termType': 'region'}])
    region: Optional[Term] = Field(None, description='The most specific geographical region from the Glossary.', examples=[{'@id': 'GADM-FRA.6.9.3_1', '@type': 'Term', 'name': 'Forbach (Districts), Moselle (Department), Grand Est (Region), France', 'termType': 'region'}])
    glnNumber: Optional[constr(regex='^\\d{13}$')] = Field(None, description='The Global Location Number.', examples=[])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The date in which the Site in its current form was established in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    endDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The date in which the Site in its current form ceased to exist in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    defaultMethodClassification: Optional[DefaultMethodClassification] = Field(None, description='The default classification of the method used to acquire or estimate all Infrastructure and Management data in the Cycle. Only required if the Site contains data on Infrastructure and Management. It can be overridden by specifying a methodClassification for each Infrastructure item or Management data item.    physical measurement means the amount is quantified using weighing,\n    volume measurement, metering, chemical methods, or other physical approaches.\n\n    verified survey data means the data are initially collected through\n    surveys; all or a subset of the data are verified using physical methods; and\n    erroneous survey data are discarded or corrected.\n\n    non-verified survey data means the data are collected through\n    surveys that have not been subjected to verification.\n\n    modelled means a previously calibrated model is used to estimate\n    this data point from other data points describing this Cycle.\n\n    estimated with assumptions means a documented assumption is used\n    to estimate this data point from other data points describing this Cycle.\n\n    consistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using the same technology (defined as the same\n        System or the same key Practices\n        as those specified in the Cycle);\n\n        At the same date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        and\n\n        In the same region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    inconsistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using a different technology (defined as a different\n        System or using different key\n        Practices to those specified in the Cycle);\n\n        At a different date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        or\n\n        In a different region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    expert opinion means the data have been estimated by experts in\n    the field.\n\n    unsourced assumption means the data do not have a clear source\n    and/or are based on assumptions only.\n', examples=['physical measurement', 'verified survey data'])
    defaultMethodClassificationDescription: Optional[str] = Field(None, description='A justification of the defaultMethodClassification used. If the data were estimated with assumptions this field should also describe the assumptions.', examples=['Specifications regarding site infrastructure were provided by the manufacturer.', 'Data from site visits and historical maps'])
    defaultSource: Optional[Source] = Field(None, description='The default Source for all data in the Site which can be overridden by specifying a source for each Measurement or item of Infrastructure. Not required (but recommended) for public uploads (i.e., where dataPrivate is false).', examples=[{'@id': 's66765d', '@type': 'Source', 'name': 'Gigou (1990)'}, {'@id': 'adsi899', '@type': 'Source', 'name': 'Cordoba (2024)'}])
    measurements: Optional[List[Measurement]] = Field(None, description='The Measurements taken on the Site.', examples=[[{'@type': 'Measurement', 'term': {'@id': 'soilPh', '@type': 'Term', 'name': 'Soil pH', 'termType': 'measurement'}, 'method': {'@id': 'cacl2MethodSoilPh', '@type': 'Term', 'name': 'CaCl2 method, soil pH', 'termType': 'methodMeasurement'}, 'methodClassification': 'on-site physical measurement', 'dates': ['1989-01-01'], 'value': [7.6]}, {'@type': 'Measurement', 'term': {'@id': 'organicCarbonPerKgSoil', '@type': 'Term', 'name': 'Organic carbon (per kg soil)', 'units': 'g C / kg soil', 'termType': 'measurement'}, 'method': {'@id': 'chromicAcidWetOxidation', '@type': 'Term', 'name': 'Chromic acid wet oxidation', 'termType': 'methodMeasurement'}, 'methodClassification': 'on-site physical measurement', 'dates': ['1989-01', '1989-01-01', '1989-01-01T20:20:39'], 'value': [0.1, 0.36, 0.4], 'depthUpper': 0, 'depthLower': 30}]])
    management: Optional[List[Management]] = Field(None, description='The Management of the Site.', examples=[[{'@type': 'Management', 'term': {'@id': 'forest', '@type': 'Term', 'name': 'Forest', 'termType': 'landCover'}, 'value': 5.9, 'startDate': '1990-01-01', 'endDate': '1990-12-31'}, {'@type': 'Management', 'term': {'@id': 'annualCropland', '@type': 'Term', 'name': 'Annual cropland', 'termType': 'landCover'}, 'value': 94.15, 'startDate': '1990-01-01', 'endDate': '1990-12-31'}, {'@type': 'Management', 'term': {'@id': 'permanentCropland', '@type': 'Term', 'name': 'Permanent cropland', 'termType': 'landCover'}, 'value': 0, 'startDate': '1990-01-01', 'endDate': '1990-12-31'}, {'@type': 'Management', 'term': {'@id': 'permanentPasture', '@type': 'Term', 'name': 'Permanent pasture', 'termType': 'landCover'}, 'value': 0, 'startDate': '1990-01-01', 'endDate': '1990-12-31'}, {'@type': 'Management', 'term': {'@id': 'maizePlant', '@type': 'Term', 'name': 'Maize plant', 'termType': 'landCover'}, 'value': 100, 'startDate': '2010-01-01', 'endDate': '2010-12-31'}]])
    infrastructure: Optional[List[Infrastructure]] = Field(None, description='The Infrastructure on the Site.', examples=[[{'@type': 'Infrastructure', 'term': {'@id': 'dripIrrigationEquipment', '@type': 'Term', 'name': 'Drip irrigation equipment', 'termType': 'irrigation'}, 'startDate': '1988-01-01', 'defaultLifespan': 25, 'source': {'@id': 's66765d', '@type': 'Source', 'name': 'Gigou (1990)'}, 'inputs': [{'@type': 'Input', 'term': {'@id': 'polyvinylChloride', '@type': 'Term', 'name': 'Polyvinyl Chloride', 'units': 'kg', 'termType': 'material'}, 'value': [1100]}]}]])
    dataPrivate: bool = Field(..., description='If these data are private. Private means that HESTIA administrators can access these data and you can grant access to other platform users, but these data will not be made available to any other users of the platform or distributed to third parties.', examples=[])
    boundaryArea: Optional[confloat(ge=0.0)] = Field(None, description='The area in km2 of the boundary, used for validation and gap filling. This field is automatically calculated when boundary is provided.', examples=[])
    ecoregion: Optional[str] = Field(None, description='The WWF Terrestrial Ecoregion name.', examples=['Western European broadleaf forests'])
    awareWaterBasinId: Optional[str] = Field(None, description='The AWARE water basin identifier.', examples=[])
    originalId: Optional[str] = Field(None, description='The identifier for these data in the source database.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[bool] = Field(None, description="If this Site has been 'aggregated' using data from multiple Sites.", examples=[])
    aggregatedDataValidated: Optional[bool] = Field(None, description='If this aggregated Site has been validated by the HESTIA team.', examples=[])
    aggregatedVersion: Optional[str] = Field(None, description='A version of the aggregation engine corresponding to this Site.', examples=[])
    aggregatedSites: Optional[List[Site]] = Field(None, description='Sites used to aggregated this Site.', examples=[])
    aggregatedSources: Optional[List[Source]] = Field(None, description='Sources used to aggregated this Site.', examples=[])
    createdAt: Optional[date] = Field(None, description='Date created on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])
    updatedAt: Optional[date] = Field(None, description='Last update date on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])

from pydantic import BaseModel, Extra, Field, PositiveFloat, confloat, conint, constr

class FunctionalUnit(Enum):
    field_1_ha = '1 ha'
    relative = 'relative'

class StartDateDefinition(Enum):
    harvest_of_previous_crop = 'harvest of previous crop'
    soil_preparation_date = 'soil preparation date'
    sowing_date = 'sowing date'
    transplanting_date = 'transplanting date'
    orchard_or_vineyard_establishment_date = 'orchard or vineyard establishment date'
    first_bearing_year = 'first bearing year'
    stocking_date = 'stocking date'
    start_of_animal_life = 'start of animal life'
    start_of_year = 'start of year'
    one_year_prior = 'one year prior'
    start_of_wild_harvest_period = 'start of wild harvest period'

class Cycle(BaseModel):

    class Config:
        extra = Extra.forbid
    id: str = Field(validation_alias=AliasChoices('@id', 'id'), serialization_alias='@id', description='Unique id assigned by HESTIA')
    
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    name: Optional[str] = Field(None, description='An automatically generated name for the Cycle composed of: primary product name, "-", site.region "," site.country, "-", endDate, "-", treatment, and/or description.', examples=['Wheat, grain - Forbach, France - 1989', 'Cattle (beef) - Rondônia, Brazil - 2013', "African aubergine, fruit - Côte d'Ivoire - 2010-2025"])
    description: Optional[str] = Field(None, description='A description of the Cycle, including information that cannot be captured with other fields.', examples=['50N treatment'])
    functionalUnit: FunctionalUnit = Field(..., description="The units that the inputs, emissions, products, and transformations are expressed 'per'. Can either be: 1 ha (one hectare) or relative (meaning that the quantities of Inputs and Emissions correspond to the quantities of Products). If the primary product is a crop or forage, the functional unit must be 1 ha.", examples=['1 ha', 'relative', '1 ha'])
    functionalUnitDetails: Optional[str] = Field(None, description="Further information on the functional unit (e.g., 'one batch').", examples=[])
    endDate: Union[datetime.date, DateYear] = Field(..., description='The end date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY). If startDate is specified to month or day precision, endDate must be too. For crops, endDate must be the harvest date. For continually harvested crops, it should be the end of the year.', examples=['1989-12-31', '2013', '2025'])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The start date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY). It is calculated as endDate - cycleDuration. For temporary crops, the start date should be the date of harvest of the previous crop for consistency with FAOSTAT (where a long fallow period is counted as a crop). For permanent crops it should be the start of the year. However other start dates can be used, such as the sowing date or soil preparation date. While the schema allows only one startDate, use terms from the glossary to record further information (e.g., with terms like Cropping duration).', examples=['1989-06-01', '2010'])
    startDateDefinition: Optional[StartDateDefinition] = Field(None, description='A definition of what the start date is. This is a required field if startDate or cycleDuration are provided.', examples=['harvest of previous crop', 'one year prior', 'start of year'])
    cycleDuration: Optional[confloat(ge=0.0, le=3650.0)] = Field(None, description='The duration of the Cycle in days, equal to endDate - startDate. For crop production Cycles, this should generally be 365 days or less, but to account for short fallows before the main production Cycle it can be longer, but must be 730 days or less.', examples=[213, 365])
    site: Site = Field(..., description='A reference to the Site where this Cycle occurred.', examples=[{'@id': 'bbscc9', '@type': 'Site', 'name': 'Field 1', 'siteType': 'cropland', 'country': {'@id': 'GADM-FRA', '@type': 'Term', 'name': 'France', 'termType': 'region'}}, {'@id': 'nixxrdw', '@type': 'Site', 'name': 'Pasture - Brazil'}, {'@id': 'africanAubergineFruit-cote-divoire-2010-2025-20250427', '@type': 'Site'}])
    otherSites: Optional[List[Site]] = Field(None, description='If the Cycle occurred on multiple Sites, a list of the other Sites.', examples=[[{'@id': '7aalbii', '@type': 'Site', 'name': 'Animal Housing - Brazil'}]])
    siteDuration: Optional[confloat(ge=0.0)] = Field(None, description='The duration the Site is used for this Cycle in days. For temporary crops, the use period is defined as including the short fallow period and is therefore the period from harvest of the previous crop to harvest of the current crop (siteDuration = cycleDuration when startDateDefinition = harvest of previous crop). For permanent crops, the use period is equal to the cycleDuration. For animal production Cycles, this should be the time the animals are physically present on the Site and siteUnusedDuration should be used to record periods where the Site is un-grazed, fallow, or unused.', examples=[213, 300])
    otherSitesDuration: Optional[List[Optional[confloat(ge=0.0)]]] = Field(None, description='If a Cycle occurred on multiple Sites, a corresponding array to otherSites with the number of days on each Site.', examples=[[65]], ge=0)
    siteUnusedDuration: Optional[confloat(ge=0.0)] = Field(None, description='During a Cycle, or over a number of Cycles, Sites are often unused for production for a period of time (e.g., the long fallow duration in crop production systems or periods when animals have been rotated to a different field). The unused duration is included in land occupation calculations. For cropping Cycles, siteUnusedDuration is calculated as the long fallow duration divided by the rotation duration multiplied by the siteDuration. It is therefore a time weighted allocation of the long fallow period to each Cycle in the crop rotation. For animal production Cycles, it is the period when animals are not present on the Site (e.g., if animals spend half the year in housing and half the year on pasture) it would be calculated 365/2 days. For animal production Cycles, if there are no other uses of a Site, it can simply be calculated as cycleDuration - siteDuration for each Site. For aquaculture production Cycles, it is the time between previous harvest and the current stocking (see Fallow period (aquaculture)).', examples=[65])
    otherSitesUnusedDuration: Optional[List[Optional[confloat(ge=0.0)]]] = Field(None, description='If a Cycle occurred on multiple Sites, a corresponding array to otherSites with the number of days the Site was unused for.', examples=[[300]], ge=0)
    siteArea: Optional[confloat(ge=0.0)] = Field(None, description='The area of the site in hectares per functionalUnit. If the functionalUnit is 1 ha, this will default to 1. If the functionalUnit is relative this is the area of site required to produce the products from this Cycle. For cropland, this must be area under cultivation, also called sown area. Harvested area, which can be less than sown area, can be defined using the field harvestedArea.', examples=[1, 33.12])
    otherSitesArea: Optional[List[Optional[confloat(ge=0.0)]]] = Field(None, description='If a Cycle occurred on multiple Sites, a corresponding array to otherSites with the area of each of each of the other Sites, in hectares, required to produce the products from this Cycle.', examples=[[0.28]], ge=0)
    harvestedArea: Optional[PositiveFloat] = Field(None, description='For crops, the area harvested per functionalUnit of this Cycle in hectares. Area harvested is the same as area under cultivation if the entire cultivated area is harvested, but less if crops fail or are not harvested for economic or other reasons.', examples=[])
    numberOfCycles: Optional[conint(ge=1)] = Field(None, description='If data on multiple Cycles are aggregated and represented as a single Cycle, the number of Cycles. For example, Cycles occurred on the same Site in multiple growing seasons might be represented as a single Cycle with standard deviations across Cycles.', examples=[])
    treatment: Optional[str] = Field(None, description='A description of the treatment administered by researchers to the experimental unit. Use the numberOfReplications field to specify the number of replicates for each treatment.', examples=[])
    commercialPracticeTreatment: Optional[bool] = Field(None, description='Whether this treatment is representative of typical commercial practice. Required if treatment is specified.', examples=[])
    numberOfReplications: Optional[conint(ge=1)] = Field(None, description='In experimental studies, the number of replicates for the treatment.', examples=[])
    sampleWeight: Optional[conint(ge=0, le=100)] = Field(None, description='In surveys, the sample weight for this Cycle relative to all other Cycles included in the Source.', examples=[])
    defaultMethodClassification: DefaultMethodClassification = Field(..., description='The default classification of the method used to acquire or estimate all Input, Product, Practice, and Transport data in the Cycle. It can be overridden by specifying a methodClassification for each Input, Product, Practice, or Transport stage.    physical measurement means the amount is quantified using weighing,\n    volume measurement, metering, chemical methods, or other physical approaches.\n\n    verified survey data means the data are initially collected through\n    surveys; all or a subset of the data are verified using physical methods; and\n    erroneous survey data are discarded or corrected.\n\n    non-verified survey data means the data are collected through\n    surveys that have not been subjected to verification.\n\n    modelled means a previously calibrated model is used to estimate\n    this data point from other data points describing this Cycle.\n\n    estimated with assumptions means a documented assumption is used\n    to estimate this data point from other data points describing this Cycle.\n\n    consistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using the same technology (defined as the same\n        System or the same key Practices\n        as those specified in the Cycle);\n\n        At the same date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        and\n\n        In the same region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    inconsistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using a different technology (defined as a different\n        System or using different key\n        Practices to those specified in the Cycle);\n\n        At a different date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        or\n\n        In a different region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    expert opinion means the data have been estimated by experts in\n    the field.\n\n    unsourced assumption means the data do not have a clear source\n    and/or are based on assumptions only.\n', examples=['verified survey data', 'non-verified survey data', 'modelled'])
    defaultMethodClassificationDescription: str = Field(..., description='A justification of the defaultMethodClassification used. If the data were estimated with assumptions this field should also describe the assumptions.', examples=['Data from a postal survey of 200 farms where researchers followed up with on-site visits to validate the data.', 'A telephone survey of 50 farms.', 'aggregated data'])
    defaultSource: Optional[Source] = Field(None, description='The default Source for all data in the Cycle which can be overridden by specifying a source for each Input, Emission, Product, or Practice. Required for public uploads (i.e., where dataPrivate is false).', examples=[{'@id': 's66765d', '@type': 'Source', 'name': 'Gigou (1990)'}, {'@id': 's6nl6jn', '@type': 'Source', 'name': 'Alvarez et al (2021)'}, {'@type': 'Source', 'name': 'HESTIA Team (2023)', '@id': 'pu2wmwp8yfv7'}])
    completeness: Completeness = Field(..., description='A specification of how complete the inputs and products data are. If an area of activity data is marked as complete, then the associated Inputs and Products represent a complete description of the Cycle.', examples=[{'@type': 'Completeness', 'animalPopulation': True, 'freshForage': True, 'ingredient': True, 'otherChemical': True, 'operation': False, 'electricityFuel': False, 'material': True, 'transport': True, 'fertiliser': True, 'soilAmendment': True, 'pesticideVeterinaryDrug': True, 'water': True, 'animalFeed': True, 'liveAnimalInput': True, 'seed': False, 'product': True, 'cropResidue': False, 'excreta': True, 'waste': False}, {'@type': 'Completeness', 'animalPopulation': True, 'freshForage': False, 'otherChemical': True, 'ingredient': True, 'operation': False, 'electricityFuel': False, 'material': False, 'transport': False, 'fertiliser': True, 'soilAmendment': True, 'pesticideVeterinaryDrug': True, 'water': True, 'animalFeed': True, 'liveAnimalInput': True, 'seed': True, 'product': True, 'cropResidue': False, 'excreta': True, 'waste': False}, {'animalFeed': True, 'animalPopulation': True, 'cropResidue': False, 'electricityFuel': True, 'excreta': True, 'fertiliser': True, 'freshForage': True, 'ingredient': True, 'liveAnimalInput': True, 'material': True, 'operation': False, 'otherChemical': True, 'pesticideVeterinaryDrug': True, 'product': True, 'seed': True, 'soilAmendment': True, 'transport': False, 'waste': False, 'water': True, '@type': 'Completeness'}])
    practices: Optional[List[Practice]] = Field(None, description='The Practices used.', examples=[[{'@type': 'Practice', 'term': {'@id': 'croppingDuration', '@type': 'Term', 'name': 'Cropping duration', 'units': 'days', 'termType': 'landUseManagement'}, 'value': [163]}, {'@type': 'Practice', 'term': {'@id': 'shortFallowDuration', '@type': 'Term', 'name': 'Short fallow duration', 'units': 'days', 'termType': 'landUseManagement'}, 'value': [50]}, {'@type': 'Practice', 'term': {'@id': 'seedTreated', '@type': 'Term', 'name': 'Seed treated', 'termType': 'cropEstablishment'}}], [{'term': {'@type': 'Term', 'name': 'Cropping intensity', 'termType': 'landUseManagement', '@id': 'croppingIntensity', 'units': 'ratio'}, 'value': [0.26170096], '@type': 'Practice'}, {'term': {'@type': 'Term', 'name': 'Long fallow ratio', 'termType': 'landUseManagement', '@id': 'longFallowRatio', 'units': 'ratio'}, 'value': [1.14453049], '@type': 'Practice'}]])
    animals: Optional[List[Animal]] = Field(None, description='The types of Animal present.', examples=[[{'@type': 'Animal', 'animalId': 'young beef cattle heifer', 'term': {'@id': 'beefCattleHeifer', '@type': 'Term', 'name': 'Beef cattle, heifer', 'units': 'number', 'termType': 'liveAnimal'}, 'value': 15, 'referencePeriod': 'average', 'properties': [{'@type': 'Property', 'term': {'@id': 'age', '@type': 'Term', 'name': 'Age', 'units': 'days', 'termType': 'property'}, 'value': 730}, {'@type': 'Property', 'term': {'@id': 'liveweightPerHead', '@type': 'Term', 'name': 'Liveweight per head', 'units': 'kg liveweight / head', 'termType': 'property'}, 'value': 200}]}, {'@type': 'Animal', 'animalId': 'mature beef cattle heifer', 'term': {'@id': 'beefCattleHeifer', '@type': 'Term', 'name': 'Beef cattle, heifer', 'units': 'number', 'termType': 'liveAnimal'}, 'value': 10, 'referencePeriod': 'average', 'properties': [{'@type': 'Property', 'term': {'@id': 'age', '@type': 'Term', 'name': 'Age', 'units': 'days', 'termType': 'property'}, 'value': 1095}, {'@type': 'Property', 'term': {'@id': 'liveweightPerHead', '@type': 'Term', 'name': 'Liveweight per head', 'units': 'kg liveweight / head', 'termType': 'property'}, 'value': 250}]}, {'@type': 'Animal', 'animalId': 'beef cattle cow', 'term': {'@id': 'beefCattleCow', '@type': 'Term', 'name': 'Beef cattle (cow)', 'units': 'number', 'termType': 'liveAnimal'}, 'value': 20, 'referencePeriod': 'average', 'properties': [{'@type': 'Property', 'term': {'@id': 'liveweightPerHead', '@type': 'Term', 'name': 'Liveweight per head', 'units': 'kg liveweight / head', 'termType': 'property'}, 'value': 430}]}, {'@type': 'Animal', 'animalId': 'beef cattle bull', 'term': {'@id': 'beefCattleBull', '@type': 'Term', 'name': 'Beef cattle, bull', 'units': 'number', 'termType': 'liveAnimal'}, 'value': 1, 'referencePeriod': 'average', 'properties': [{'@type': 'Property', 'term': {'@id': 'liveweightPerHead', '@type': 'Term', 'name': 'Liveweight per head', 'units': 'kg liveweight / head', 'termType': 'property'}, 'value': 500}]}]])
    inputs: Optional[List[Input]] = Field(None, description='The Inputs used.', examples=[[{'@type': 'Input', 'term': {'@id': 'CAS-34494-04-7', '@type': 'Term', 'name': 'Glyphosate', 'units': 'g active ingredient', 'termType': 'pesticideAI'}, 'value': [400], 'sd': [180], 'statsDefinition': 'replications', 'observations': [10]}, {'@type': 'Input', 'term': {'@id': 'ureaKgN', '@type': 'Term', 'name': 'Urea (kg N)', 'units': 'kg N', 'termType': 'inorganicFertiliser'}, 'value': [40], 'transport': [{'@type': 'Transport', 'term': {'@id': 'freightLorry32MetricTon', '@type': 'Term', 'name': 'Freight, lorry, >32 metric ton', 'units': 'tkm', 'termType': 'transport'}, 'value': 8, 'returnLegIncluded': False, 'methodClassification': 'estimated with assumptions', 'methodClassificationDescription': 'Distance estimated using approximate road distance to likely supplier, assuming 100% load factor.', 'emissions': [{'@type': 'Emission', 'term': {'@id': 'co2ToAirFuelCombustion', '@type': 'Term', 'name': 'CO2, to air, fuel combustion', 'units': 'kg CO2', 'termType': 'emission'}, 'value': [0.7], 'methodModel': {'@id': 'emepEea2019', '@type': 'Term', 'name': 'EMEA-EEA (2019)', 'termType': 'model'}, 'methodTier': 'tier 1'}]}]}, {'@type': 'Input', 'term': {'@id': 'electricityGridMarketMix', '@type': 'Term', 'name': 'Electricity, grid, market mix', 'units': 'kWh', 'termType': 'electricity'}, 'value': [600]}, {'@type': 'Input', 'term': {'@id': 'fixedNitrogenFromPreviousCropKgN', '@type': 'Term', 'name': 'Fixed nitrogen, from previous crop (kg N)', 'units': 'kg N', 'termType': 'organicFertiliser'}, 'value': [40], 'methodClassification': 'modelled', 'methodClassificationDescription': 'Modelled using a simple model which links nitrogen fixation to nitrogen fertiliser input (Jensen, 1987, Plant and Soil).'}], [{'@type': 'Input', 'term': {'@id': 'lime', '@type': 'Term', 'name': 'Lime', 'units': 'kg CaCO3', 'termType': 'soilAmendment'}, 'value': [250]}, {'@type': 'Input', 'term': {'@id': 'beefCattleCalfWeaned', '@type': 'Term', 'name': 'Beef cattle, calf (weaned)', 'units': 'number', 'termType': 'liveAnimal'}, 'value': [4]}]])
    products: Optional[List[Product]] = Field(None, description='The Products created.', examples=[[{'@type': 'Product', 'term': {'@id': 'wheatGrain', '@type': 'Term', 'name': 'Wheat, grain', 'units': 'kg', 'termType': 'crop'}, 'value': [7282], 'primary': True, 'economicValueShare': 94.8, 'properties': [{'@type': 'Property', 'term': {'@id': 'dryMatter', '@type': 'Term', 'name': 'Dry matter', 'units': '%', 'termType': 'property'}, 'value': 80}]}, {'@type': 'Product', 'term': {'@id': 'wheatStraw', '@type': 'Term', 'name': 'Wheat, straw', 'units': 'kg', 'termType': 'crop'}, 'value': [40], 'economicValueShare': 5.2}], [{'@type': 'Product', 'term': {'@id': 'beefCattle', '@type': 'Term', 'name': 'Beef cattle', 'units': 'number', 'termType': 'liveAnimal'}, 'value': [10], 'properties': [{'@type': 'Property', 'term': {'@id': 'processingConversionLiveweightToColdDressedCarcassWeight', '@type': 'Term', 'name': 'Processing conversion, liveweight to cold dressed carcass weight', 'units': '%', 'termType': 'property'}, 'value': 48}]}, {'@type': 'Product', 'term': {'@id': 'excretaBeefCattleExceptFeedlotFedKgMass', '@type': 'Term', 'name': 'Excreta, beef cattle, except feedlot fed (kg mass)', 'units': 'kg', 'termType': 'excreta'}, 'value': [1050]}], [{'term': {'@type': 'Term', 'termType': 'crop', 'name': 'African aubergine, fruit', 'units': 'kg', '@id': 'africanAubergineFruit'}, 'value': [16923], 'economicValueShare': 99.98, 'primary': True, '@type': 'Product'}]])
    transformations: Optional[List[Transformation]] = Field(None, description='The Transformations applied to products generated from this Cycle.', examples=[[{'@type': 'Transformation', 'transformationId': 'excreta-on-pasture', 'term': {'@id': 'pastureRangePaddockExcretaManagement', '@type': 'Term', 'name': 'Pasture/Range/Paddock (excreta management)', 'termType': 'excretaManagement'}, 'inputs': [{'@type': 'Input', 'term': {'@id': 'excretaBeefCattleExceptFeedlotFedKgMass', '@type': 'Term', 'name': 'Excreta, beef cattle, except feedlot fed (kg mass)', 'units': 'kg', 'termType': 'excreta'}, 'value': [840], 'fromCycle': False}], 'transformedShare': 80}, {'@type': 'Transformation', 'transformationId': 'pit-storage', 'term': {'@id': 'pitStorageBelowAnimalConfinements', '@type': 'Term', 'name': 'Pit storage below animal confinements', 'termType': 'excretaManagement'}, 'inputs': [{'@type': 'Input', 'term': {'@id': 'excretaBeefCattleExceptFeedlotFedKgMass', '@type': 'Term', 'name': 'Excreta, beef cattle, except feedlot fed (kg mass)', 'units': 'kg', 'termType': 'excreta'}, 'value': [210], 'fromCycle': False}], 'transformedShare': 20}, {'@type': 'Transformation', 'transformationId': 'lagoon', 'term': {'@id': 'liquidSlurry', '@type': 'Term', 'name': 'Liquid/Slurry', 'termType': 'excretaManagement'}, 'inputs': [{'@type': 'Input', 'term': {'@id': 'excretaBeefCattleExceptFeedlotFedKgMass', '@type': 'Term', 'name': 'Excreta, beef cattle, except feedlot fed (kg mass)', 'units': 'kg', 'termType': 'excreta'}, 'fromCycle': False}], 'transformedShare': 100, 'previousTransformationId': 'pit-storage'}]])
    emissions: Optional[List[Emission]] = Field(None, description='The Emissions created.', examples=[[{'@type': 'Emission', 'term': {'@id': 'no3ToGroundwaterSoilFlux', '@type': 'Term', 'name': 'NO3, to groundwater, soil flux', 'units': 'kg NO3', 'termType': 'emission'}, 'value': [60.75, 70.5], 'dates': ['1989-06-16', '1989-08-01'], 'methodModel': {'@id': 'percolationLysimeter', '@type': 'Term', 'name': 'Percolation lysimeter', 'termType': 'methodEmissionResourceUse'}, 'methodTier': 'measured', 'source': {'@id': 'source-8v5', '@type': 'Source', 'name': 'Murwira (1993)'}}, {'@type': 'Emission', 'term': {'@id': 'n2OToAirInorganicFertiliserDirect', '@type': 'Term', 'name': 'N2O, to air, inorganic fertiliser, direct', 'units': 'kg N2O', 'termType': 'emission'}, 'value': [0.628], 'methodModel': {'@id': 'ipcc2006', '@type': 'Term', 'name': 'IPCC (2006)', 'termType': 'model'}, 'methodTier': 'tier 1'}, {'@type': 'Emission', 'term': {'@id': 'so2ToAirInputsProduction', '@type': 'Term', 'name': 'SO2, to air, inputs production', 'units': 'kg SO2', 'termType': 'emission'}, 'value': [2.11], 'methodModel': {'@id': 'ecoinventV3', '@type': 'Term', 'name': 'ecoinvent v3', 'termType': 'model'}, 'methodTier': 'background', 'inputs': [{'@id': 'electricityGridMarketMix', '@type': 'Term', 'name': 'Electricity, grid, market mix', 'termType': 'electricity'}]}], [{'term': {'@type': 'Term', 'name': 'NOx, to air, inputs production', 'termType': 'emission', '@id': 'noxToAirInputsProduction', 'units': 'kg NOx'}, 'value': [0.124], 'methodTier': 'not relevant', 'methodModel': {'@type': 'Term', 'name': 'Aggregated models', 'termType': 'model', '@id': 'aggregatedModels'}, '@type': 'Emission'}, {'term': {'@type': 'Term', 'name': 'CO2, to air, organic soil cultivation', 'termType': 'emission', '@id': 'co2ToAirOrganicSoilCultivation', 'units': 'kg CO2'}, 'value': [509], 'methodTier': 'not relevant', 'methodModel': {'@type': 'Term', 'name': 'Aggregated models', 'termType': 'model', '@id': 'aggregatedModels'}, '@type': 'Emission'}, {'term': {'@type': 'Term', 'name': 'NO3, to groundwater, crop residue decomposition', 'termType': 'emission', '@id': 'no3ToGroundwaterCropResidueDecomposition', 'units': 'kg NO3'}, 'value': [3.18], 'methodTier': 'not relevant', 'methodModel': {'@type': 'Term', 'name': 'Aggregated models', 'termType': 'model', '@id': 'aggregatedModels'}, '@type': 'Emission'}]])
    dataPrivate: bool = Field(..., description='If these data are private. Private means that HESTIA administrators can access these data and you can grant access to other platform users, but these data will not be made available to any other users of the platform or distributed to third parties.', examples=[])
    originalId: Optional[str] = Field(None, description='The identifier for these data in the source database (e.g., if the data were converted from openLCA or ecoinvent, the id field from that database).', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[bool] = Field(None, description="If this Cycle has been 'aggregated' using data from multiple Cycles.", examples=[True])
    aggregatedDataValidated: Optional[bool] = Field(None, description='If this aggregated Cycle has been validated by the HESTIA team.', examples=[])
    aggregatedVersion: Optional[str] = Field(None, description='A version of the aggregation engine corresponding to this Cycle.', examples=[])
    aggregatedQualityScore: Optional[conint(ge=0)] = Field(None, description='A data quality score for aggregated data. The points depend on the primary Product of the aggregation. One point is awarded for each of the categories satisfied, according to the table below. For global aggregations, an additional point is awarded for both farm-stage and processing aggregations if the aggregation includes countries representing over 75% of production of the farm-gate product. The global aggregation is then scored out of 4 or 5 for processing and crop respectively.\n        Primary Product\n        Emissions\n        Number of Cycles\n        Yield\n        Completeness\n\n        Crop\n        No emissions included in the system boundary are missing\n        Over 50 Cycles\n        Within +/- 20% of FAOSTAT yield for the primary Product\n        True for all priority areas (animalFeed, cropResidue, electricityFuel, excreta, fertiliser, freshForage, ingredient, liveAnimalInput, otherChemical, pesticdieVetinaryDrug, product, seed, water)\n\n        Processed food\n        No emissions included in the system boundary are missing\n        Over 10 Cycles\n        -\n        True for all priority areas True for all priority areas (electricityFuel, ingredient, product, water)\n', examples=[1])
    aggregatedQualityScoreMax: Optional[conint(ge=3)] = Field(None, description='The maximum value for the aggregated quality score.', examples=[4])
    aggregatedCycles: Optional[List[Cycle]] = Field(None, description='Cycles used to aggregated this Cycle.', examples=[])
    aggregatedSources: Optional[List[Source]] = Field(None, description='Sources used to aggregated this Cycle.', examples=[])
    covarianceMatrixIds: Optional[List[str]] = Field(None, description='An array of strings which are the column column/row headers of the covarianceMatrix.', examples=[['practices.croppingIntensity', 'practices.longFallowRatio', 'products.africanAubergineFruit', 'emissions.noxToAirInputsProduction', 'emissions.co2ToAirOrganicSoilCultivation', 'emissions.no3ToGroundwaterCropResidueDecomposition']])
    covarianceMatrix: Optional[List[List[Optional[float]]]] = Field(None, description='For aggregated cycles only, a covariance matrix, represented using the lower triangle only. The covariance matrix describes the covariance between all data items in the Cycle. It is used to generate the distributions of Impact Assessment Indicators. E.g., it contains the covariance between one emission and another. It controls for the fact that data items in the Cycle often covary with another. This covariance generally reduces the variability in the distributions of Indicators.', examples=[[[20, 0, 0, 0, 0, 0], [30, 40, 0, 0, 0, 0], [10, 60, 90, 0, 0, 0], [4, -25, -88, 10, 0, 0], [0.6, -10, -90, 11, 30, 0], [75, 20, -15, -70, 2, 35]]])
    createdAt: Optional[date] = Field(None, description='Date created on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])
    updatedAt: Optional[date] = Field(None, description='Last update date on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])

from typing import Any, List, Optional, Union

class StatsDefinition(Enum):
    sites = 'sites'
    cycles = 'cycles'
    replications = 'replications'
    animals = 'animals'
    other_observations = 'other observations'
    time = 'time'
    spatial = 'spatial'
    regions = 'regions'
    simulated = 'simulated'
    modelled = 'modelled'

class PriceStatsDefinition(Enum):
    cycles = 'cycles'
    time = 'time'
    cycles_and_time = 'cycles and time'

class CostStatsDefinition(Enum):
    cycles = 'cycles'
    time = 'time'
    cycles_and_time = 'cycles and time'

class Practice(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    term: Term = Field(..., description="A reference to the Term describing the Practice. This can be replaced by a description instead if the Term isn't available in the Glossary.", examples=[{'@id': 'croppingDuration', '@type': 'Term', 'name': 'Cropping Duration', 'units': 'days', 'termType': 'landUseManagement'}, {'@id': 'soilAssociationOrganicStandard', '@type': 'Term', 'name': 'Soil Association Organic Standard', 'termType': 'standardsLabels'}, {'@id': 'cloverPlant', '@type': 'Term', 'name': 'Clover plant', 'termType': 'landCover'}])
    description: Optional[str] = Field(None, description='A description of the Practice. This is a required field if term is not provided.', examples=[])
    variety: Optional[str] = Field(None, description='For Land cover terms only, the variety (cultivar) of a crop. Standardised variety names are defined in external glossaries, such as the OECD, GEVES, PLUTO, or CPVO glossaries.', examples=['Small leafed clover'])
    key: Optional[Term] = Field(None, description='If the data associated with the Practice are in key:value form, the key.', examples=[])
    value: Optional[List[Optional[Union[str, float, bool]]]] = Field(None, description='The value associated with the Practice. If an average, it should always be the mean.', examples=[[163], [100]])
    distribution: Optional[List[Union[float, List[Any]]]] = Field(None, description='An array of up to 1000 random samples from the posterior distribution of valuedates field.', examples=[], max_items=1000)
    sd: Optional[List[Optional[confloat(ge=0.0)]]] = Field(None, description='The standard deviation of value.', examples=[], ge=0)
    min: Optional[List[Optional[float]]] = Field(None, description='The minimum of value.', examples=[])
    max: Optional[List[Optional[float]]] = Field(None, description='The maximum of value.', examples=[])
    statsDefinition: Optional[StatsDefinition] = Field(None, description='What the descriptive statistics (sd, min, max, and value) are calculated across, or whether they are simulated or the output of a model. spatial refers to descriptive statistics calculated across spatial units (e.g., pixels) within a region or country. time refers to descriptive statistics calculated across units of time (e.g., hours).', examples=[])
    observations: Optional[List[Optional[confloat(ge=1.0)]]] = Field(None, description='The number of observations the descriptive statistics are calculated over.', examples=[], ge=1)
    dates: Optional[List[Union[datetime.date, DateYear]]] = Field(None, description='A corresponding array to value, representing the dates of the Practice in ISO 8601 format (YYYY-MM-DD, YYYY-MM, YYYY, --MM-DD, --MM, or YYYY-MM-DDTHH:mm:ssZ).', examples=[])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The start date of the Practice if different from the start date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY). The start date is the first date the practice is carried out. The practice will continue without stopping until the end date is reached. Alternatively, use the dates term to specify practices which occur on a number of different dates.', examples=['1996-01-01', '1996-01-01'])
    endDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The end date of the Practice if different from the end date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY). The end date is the last date the practice is carried out. The practice will continue without stopping until the end date is reached. Alternatively, use the dates term to specify practices which occur on a number of different dates.', examples=['1996-01-01'])
    methodClassification: Optional[MethodClassification] = Field(None, description='A classification of the method used to acquire or estimate the term and value. Overrides the defaultMethodClassification specified in the Cycle. methodClassification should be specified separately for properties (see Property).    physical measurement means the amount is quantified using weighing,\n    volume measurement, metering, chemical methods, or other physical approaches.\n\n    verified survey data means the data are initially collected through\n    surveys; all or a subset of the data are verified using physical methods; and\n    erroneous survey data are discarded or corrected.\n\n    non-verified survey data means the data are collected through\n    surveys that have not been subjected to verification.\n\n    modelled means a previously calibrated model is used to estimate\n    this data point from other data points describing this Cycle.\n\n    estimated with assumptions means a documented assumption is used\n    to estimate this data point from other data points describing this Cycle.\n\n    consistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using the same technology (defined as the same\n        System or the same key Practices\n        as those specified in the Cycle);\n\n        At the same date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        and\n\n        In the same region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    inconsistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using a different technology (defined as a different\n        System or using different key\n        Practices to those specified in the Cycle);\n\n        At a different date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        or\n\n        In a different region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    expert opinion means the data have been estimated by experts in\n    the field.\n\n    unsourced assumption means the data do not have a clear source\n    and/or are based on assumptions only.\n', examples=[])
    methodClassificationDescription: Optional[str] = Field(None, description='A justification of the methodClassification used. If the data were estimated with assumptions this field should also describe the assumptions. This is a required field if methodClassification is specified.', examples=[])
    model: Optional[Term] = Field(None, description='A reference to the Term describing the model used to estimate these data.', examples=[])
    modelDescription: Optional[str] = Field(None, description='A free text field, describing the model used to estimate these data.', examples=[])
    areaPercent: Optional[confloat(ge=0.0)] = Field(None, description='The area of the Site that Practice occurred on, specified as a percentage of Site area. If the units of the term are already in % area, do not use this field and use value instead to record these data.', examples=[])
    price: Optional[confloat(ge=0.0)] = Field(None, description='The price paid for this Practice. The price should be expressed per the units defined in the term. The currency must be specified. The price of the inputs associated with this practice should be included in the inputs rather than here.', examples=[])
    priceSd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of price.', examples=[])
    priceMin: Optional[confloat(ge=0.0)] = Field(None, description='The minimum of price.', examples=[])
    priceMax: Optional[confloat(ge=0.0)] = Field(None, description='The maximum of price.', examples=[])
    priceStatsDefinition: Optional[PriceStatsDefinition] = Field(None, description='What the descriptive statistics for price are calculated across.', examples=[])
    cost: Optional[confloat(ge=0.0)] = Field(None, description='The total cost of this Practice (price x quantity), expressed as a positive value. The currency must be specified. The cost of the inputs associated with this practice should be included in the inputs rather than here.', examples=[])
    costSd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of cost.', examples=[])
    costMin: Optional[confloat(ge=0.0)] = Field(None, description='The minimum of cost.', examples=[])
    costMax: Optional[confloat(ge=0.0)] = Field(None, description='The maximum of cost.', examples=[])
    costStatsDefinition: Optional[CostStatsDefinition] = Field(None, description='What the descriptive statistics for cost are calculated across.', examples=[])
    currency: Optional[constr(regex='^[A-Z]{3}$')] = Field(None, description='The three letter currency code in ISO 4217 format.', examples=[])
    ownershipStatus: Optional[OwnershipStatus] = Field(None, description='For operations, the ownership status of the equipment used to perform the operation.', examples=[])
    primaryPercent: Optional[confloat(ge=0.0, le=100.0)] = Field(None, description='For primary processing operations in food processing Cycles, the percent of primary Product produced with the operation. For example, if the Cycle represents Oil palm, oil (crude) produced only with the operation Pressing, with screw press, the primaryPercent would be 100.', examples=[])
    site: Optional[Site] = Field(None, description='If the Cycle occurred on multiple Sites, the Site where this Practice was used.', examples=[])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data, if different from the defaultSource of the Cycle or Site.', examples=[])
    otherSources: Optional[List[Source]] = Field(None, description='A list of references to any other sources of these data.', examples=[])
    properties: Optional[List[Property]] = Field(None, description='A list of Properties of the Practice, which would override any default properties specified in the term.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[List[str]] = Field(None, description="A list of fields that have been 'aggregated' using data from multiple Cycles.", examples=[])
    aggregatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the aggregation engine corresponding to each aggregated field.', examples=[])

class Fate(Enum):
    sold = 'sold'
    sold_to_export_market = 'sold to export market'
    sold_to_domestic_market = 'sold to domestic market'
    sold_for_breeding = 'sold for breeding'
    sold_for_fattening = 'sold for fattening'
    sold_for_slaughter = 'sold for slaughter'
    home_consumption = 'home consumption'
    fodder = 'fodder'
    bedding = 'bedding'
    breeding = 'breeding'
    saved_for_seeds = 'saved for seeds'
    processing = 'processing'
    burnt_for_fuel = 'burnt for fuel'
    burnt = 'burnt'
    anaerobic_digestion = 'anaerobic digestion'
    composted = 'composted'
    used_as_fertiliser = 'used as fertiliser'
    used_as_soil_amendment = 'used as soil amendment'
    used_as_mulch = 'used as mulch'

class RevenueStatsDefinition(Enum):
    cycles = 'cycles'
    time = 'time'
    cycles_and_time = 'cycles and time'

class Product(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    term: Term = Field(..., description='A reference to the Term describing the Product.', examples=[{'@id': 'wheatGrain', '@type': 'Term', 'name': 'Wheat, grain', 'units': 'kg', 'termType': 'crop'}])
    description: Optional[str] = Field(None, description='A short description of the Product.', examples=[])
    variety: Optional[str] = Field(None, description='The variety (cultivar) of a crop or breed of animal. Standardised variety names are defined in external glossaries, such as the OECD, GEVES, PLUTO, or CPVO glossaries.', examples=[])
    value: Optional[List[Optional[confloat(ge=0.0)]]] = Field(None, description='The quantity of the Product. If an average, it should always be the mean. Can be a single number (array of length one) or an array of numbers with associated dates (e.g., for multiple harvests in one Cycle]). The units are always specified in the [Term. For crops, value should always be per harvest or per year, following FAOSTAT conventions.', examples=[[7282]], ge=0)
    distribution: Optional[List[Union[float, List[Any]]]] = Field(None, description='An array of up to 1000 random samples from the posterior distribution of valuedates field.', examples=[], max_items=1000)
    sd: Optional[List[Optional[confloat(ge=0.0)]]] = Field(None, description='The standard deviation of value.', examples=[], ge=0)
    min: Optional[List[Optional[float]]] = Field(None, description='The minimum of value.', examples=[])
    max: Optional[List[Optional[float]]] = Field(None, description='The maximum of value.', examples=[])
    statsDefinition: Optional[StatsDefinition] = Field(None, description='What the descriptive statistics (sd, min, max, and value) are calculated across, or whether they are simulated or the output of a model. spatial refers to descriptive statistics calculated across spatial units (e.g., pixels) within a region or country. time refers to descriptive statistics calculated across units of time (e.g., hours).', examples=[])
    observations: Optional[List[Optional[confloat(ge=1.0)]]] = Field(None, description='The number of observations the descriptive statistics are calculated over.', examples=[], ge=1)
    dates: Optional[List[Union[datetime.date, DateYear]]] = Field(None, description='A corresponding array to value, representing the dates of the Products in ISO 8601 format (YYYY-MM-DD, YYYY-MM, YYYY, --MM-DD, --MM, or YYYY-MM-DDTHH:mm:ssZ).', examples=[])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='For Products created over periods, the start date of the Product if different from the start date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    endDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='For Products created over periods, the end date of the Product if different from the end date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    methodClassification: Optional[MethodClassification] = Field(None, description='A classification of the method used to acquire or estimate the term and value. Overrides the defaultMethodClassification specified in the Cycle. methodClassification should be specified separately for properties (see Property) and transport (see Transport).    physical measurement means the amount is quantified using weighing,\n    volume measurement, metering, chemical methods, or other physical approaches.\n\n    verified survey data means the data are initially collected through\n    surveys; all or a subset of the data are verified using physical methods; and\n    erroneous survey data are discarded or corrected.\n\n    non-verified survey data means the data are collected through\n    surveys that have not been subjected to verification.\n\n    modelled means a previously calibrated model is used to estimate\n    this data point from other data points describing this Cycle.\n\n    estimated with assumptions means a documented assumption is used\n    to estimate this data point from other data points describing this Cycle.\n\n    consistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using the same technology (defined as the same\n        System or the same key Practices\n        as those specified in the Cycle);\n\n        At the same date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        and\n\n        In the same region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    inconsistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using a different technology (defined as a different\n        System or using different key\n        Practices to those specified in the Cycle);\n\n        At a different date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        or\n\n        In a different region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    expert opinion means the data have been estimated by experts in\n    the field.\n\n    unsourced assumption means the data do not have a clear source\n    and/or are based on assumptions only.\n', examples=[])
    methodClassificationDescription: Optional[str] = Field(None, description='A justification of the methodClassification used. If the data were estimated with assumptions this field should also describe the assumptions. This is a required field if methodClassification is specified.', examples=[])
    model: Optional[Term] = Field(None, description='A reference to the Term describing the model used to estimate these data.', examples=[])
    modelDescription: Optional[str] = Field(None, description='A free text field, describing the model used to estimate these data.', examples=[])
    fate: Optional[Fate] = Field(None, description='The fate of the Product. Use Transformations where possible to represent the conversion of one Product into another.', examples=[])
    price: Optional[confloat(ge=0.0)] = Field(None, description='The sale price of this Product. The price should be expressed per the units defined in the term, for example per "kg liveweight". The currency must be specified.', examples=[])
    priceSd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of price.', examples=[])
    priceMin: Optional[confloat(ge=0.0)] = Field(None, description='The minimum of price.', examples=[])
    priceMax: Optional[confloat(ge=0.0)] = Field(None, description='The maximum of price.', examples=[])
    priceStatsDefinition: Optional[PriceStatsDefinition] = Field(None, description='What the descriptive statistics for price are calculated across.', examples=[])
    revenue: Optional[confloat(ge=0.0)] = Field(None, description='The total revenue (price x quantity) of this Product. The currency must be specified.', examples=[])
    revenueSd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of revenue.', examples=[])
    revenueMin: Optional[confloat(ge=0.0)] = Field(None, description='The minimum of revenue.', examples=[])
    revenueMax: Optional[confloat(ge=0.0)] = Field(None, description='The maximum of revenue.', examples=[])
    revenueStatsDefinition: Optional[RevenueStatsDefinition] = Field(None, description='What the descriptive statistics for revenue are calculated across.', examples=[])
    currency: Optional[constr(regex='^[A-Z]{3}$')] = Field(None, description='The three letter currency code in ISO 4217 format.', examples=[])
    economicValueShare: Optional[confloat(ge=0.0, le=100.0)] = Field(None, description='The economic value (typically revenue) of this Product, divided by the total economic value of all Products, expressed as a percentage.', examples=[94.8])
    primary: Optional[bool] = Field(None, description='Where the are multiple products, whether this product is the primary product. Defaults to true if there is only one product or if economicValueShare > 50.', examples=[])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data, if different from the defaultSource of the Cycle.', examples=[])
    otherSources: Optional[List[Source]] = Field(None, description='A list of references to any other sources of these data.', examples=[])
    properties: Optional[List[Property]] = Field(None, description='A list of Properties of the Product, which would override any default properties specified in the term. For crops, dry matter is a default property of the Term and can be changed by adding dry matter here.', examples=[[{'@type': 'Property', 'term': {'@id': 'dryMatter', '@type': 'Term', 'name': 'Dry matter', 'units': '%', 'termType': 'property'}, 'value': 80}]])
    transport: Optional[List[Transport]] = Field(None, description='A list of Transport stages to take this Product to the final location within the Site. For example, the Transport required to take harvested crops from the field to the barn where they are stored before being sold.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[List[str]] = Field(None, description="A list of fields that have been 'aggregated' using data from multiple Cycles.", examples=[])
    aggregatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the aggregation engine corresponding to each aggregated field.', examples=[])

from typing import Any, List, Optional

from pydantic import BaseModel, Extra, Field, PositiveFloat, confloat

class Transformation1(BaseModel):
    inputs: Optional[List[Any]] = None

class Transformation2(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    transformationId: str = Field(..., description='An identifier for each Transformation which must be unique within the Cycle.', examples=['second-transformation'])
    term: Term = Field(..., description='A reference to the Term describing the process or operation for transforming the Product.', examples=[{'@id': 'compostingInVessel', '@type': 'Term', 'name': 'Composting - In Vessel', 'termType': 'excretaManagement'}])
    description: Optional[str] = Field(None, description='A description of the Transformation process or operation, including information not captured with other fields.', examples=[])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The start date of the Transformation if different from the start date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    endDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The end date of the Transformation if different from the end date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    transformationDuration: Optional[PositiveFloat] = Field(None, description='The duration of the Transformation in days. Defaulting to cycleDuration when not provided.', examples=[300])
    previousTransformationId: Optional[str] = Field(None, description='The transformationId of the previous Transformation. This is used to link Transformations, so that a share of the products from the previous Transformation become the inputs of the current Transformation. If this field is not specified, the inputs of the Transformation come from the Cycle.', examples=['first-transformation'])
    transformedShare: Optional[confloat(ge=0.0, le=100.0)] = Field(None, description='The share of Products from the Cycle or the previous Transformation that enter the current Transformation. This field is useful when the physical quantities of Products being transformed are unknown, but the share transformed is known. For example, if Excreta, dairy cattle (kg mass) is a Product of a Cycle, transformedShare = 50, and Excreta, dairy cattle (kg mass) is an Input into this Transformation, 50% of the excreta is an Input to this Transformation. If there are more than one Product being transformed, transformedShare applies equally to all Products.', examples=[100])
    site: Optional[Site] = Field(None, description='If the Cycle occurred on multiple Sites, the Site where this Transformation occurred. Use transformedShare to apportion the transformed Product across each Site.', examples=[])
    inputs: Optional[List[Input]] = Field(None, description='The Inputs into the Transformation.', examples=[[{'@type': 'Input', 'term': {'@id': 'excretaBeefCattleFeedlotFedKgN', '@type': 'Term', 'name': 'Excreta, beef cattle, feedlot fed (kg N)', 'units': 'kg N', 'termType': 'excreta'}, 'value': [150], 'fromCycle': True}, {'@type': 'Input', 'term': {'@id': 'rapeseedStraw', '@type': 'Term', 'name': 'Rapeseed, straw', 'units': 'kg', 'termType': 'crop'}, 'value': [25], 'fromCycle': False}]])
    emissions: Optional[List[Emission]] = Field(None, description='The Emissions created from the Transformation.', examples=[[{'@type': 'Emission', 'term': {'@id': 'ch4ToAirExcreta', '@type': 'Term', 'name': 'CH4, to air, excreta', 'units': 'kg CH4', 'termType': 'emission'}, 'value': [8.7], 'methodModel': {'@id': 'emepEea2019', '@type': 'Term', 'name': 'EMEA-EEA (2019)', 'termType': 'model'}, 'methodTier': 'tier 2'}]])
    products: Optional[List[Product]] = Field(None, description='The Products created from the Transformation.', examples=[[{'@type': 'Product', 'term': {'@id': 'excretaMixturesKgN', '@type': 'Term', 'name': 'Excreta mixtures (kg N)', 'units': 'kg N', 'termType': 'excreta'}, 'value': [160]}]])
    practices: Optional[List[Practice]] = Field(None, description='The Practices used during the Transformation.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])

class Transformation(BaseModel):
    __root__: Transformation3 = Field(..., description='The Transformation of one [Product](/schema/Product) to a new Product in the same [Cycle](/schema/Cycle). One Transformation can follow another and they can be linked using <code>[transformationId](/schema/Transformation#transformationId)</code>. Environmental impacts created during Transformations are then included in the [Impact Assessment](/schema/ImpactAssessment). This means that Transformations should be used to represent any processes which are required to get the Product to its marketable form or to manage any waste that is created during production. In general, any essential grain drying, crop grading, and animal excreta management should be represented using Transformations.\n', title='Transformation')

class Transformation3(Transformation1, Transformation2):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    transformationId: str = Field(..., description='An identifier for each Transformation which must be unique within the Cycle.', examples=['second-transformation'])
    term: Term = Field(..., description='A reference to the Term describing the process or operation for transforming the Product.', examples=[{'@id': 'compostingInVessel', '@type': 'Term', 'name': 'Composting - In Vessel', 'termType': 'excretaManagement'}])
    description: Optional[str] = Field(None, description='A description of the Transformation process or operation, including information not captured with other fields.', examples=[])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The start date of the Transformation if different from the start date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    endDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The end date of the Transformation if different from the end date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    transformationDuration: Optional[PositiveFloat] = Field(None, description='The duration of the Transformation in days. Defaulting to cycleDuration when not provided.', examples=[300])
    previousTransformationId: Optional[str] = Field(None, description='The transformationId of the previous Transformation. This is used to link Transformations, so that a share of the products from the previous Transformation become the inputs of the current Transformation. If this field is not specified, the inputs of the Transformation come from the Cycle.', examples=['first-transformation'])
    transformedShare: Optional[confloat(ge=0.0, le=100.0)] = Field(None, description='The share of Products from the Cycle or the previous Transformation that enter the current Transformation. This field is useful when the physical quantities of Products being transformed are unknown, but the share transformed is known. For example, if Excreta, dairy cattle (kg mass) is a Product of a Cycle, transformedShare = 50, and Excreta, dairy cattle (kg mass) is an Input into this Transformation, 50% of the excreta is an Input to this Transformation. If there are more than one Product being transformed, transformedShare applies equally to all Products.', examples=[100])
    site: Optional[Site] = Field(None, description='If the Cycle occurred on multiple Sites, the Site where this Transformation occurred. Use transformedShare to apportion the transformed Product across each Site.', examples=[])
    inputs: Optional[List[Input]] = Field(None, description='The Inputs into the Transformation.', examples=[[{'@type': 'Input', 'term': {'@id': 'excretaBeefCattleFeedlotFedKgN', '@type': 'Term', 'name': 'Excreta, beef cattle, feedlot fed (kg N)', 'units': 'kg N', 'termType': 'excreta'}, 'value': [150], 'fromCycle': True}, {'@type': 'Input', 'term': {'@id': 'rapeseedStraw', '@type': 'Term', 'name': 'Rapeseed, straw', 'units': 'kg', 'termType': 'crop'}, 'value': [25], 'fromCycle': False}]])
    emissions: Optional[List[Emission]] = Field(None, description='The Emissions created from the Transformation.', examples=[[{'@type': 'Emission', 'term': {'@id': 'ch4ToAirExcreta', '@type': 'Term', 'name': 'CH4, to air, excreta', 'units': 'kg CH4', 'termType': 'emission'}, 'value': [8.7], 'methodModel': {'@id': 'emepEea2019', '@type': 'Term', 'name': 'EMEA-EEA (2019)', 'termType': 'model'}, 'methodTier': 'tier 2'}]])
    products: Optional[List[Product]] = Field(None, description='The Products created from the Transformation.', examples=[[{'@type': 'Product', 'term': {'@id': 'excretaMixturesKgN', '@type': 'Term', 'name': 'Excreta mixtures (kg N)', 'units': 'kg N', 'termType': 'excreta'}, 'value': [160]}]])
    practices: Optional[List[Practice]] = Field(None, description='The Practices used during the Transformation.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])

from pydantic import BaseModel, Extra, Field, confloat, conint, constr

class EcoinventReferenceProductId(BaseModel):
    field_id: str = Field(..., alias='@id')

class Website(BaseModel):
    field_id: str = Field(..., alias='@id')

class Agrovoc(BaseModel):
    field_id: str = Field(..., alias='@id')

class AquastatSpeciesFactSheet(BaseModel):
    field_id: str = Field(..., alias='@id')

class CornellBiologicalControl(BaseModel):
    field_id: str = Field(..., alias='@id')

class EcolabelIndex(BaseModel):
    field_id: str = Field(..., alias='@id')

class Feedipedia(BaseModel):
    field_id: str = Field(..., alias='@id')

class Fishbase(BaseModel):
    field_id: str = Field(..., alias='@id')

class Pubchem(BaseModel):
    field_id: str = Field(..., alias='@id')

class Wikipedia(BaseModel):
    field_id: str = Field(..., alias='@id')

class TermType(Enum):
    animalBreed = 'animalBreed'
    animalProduct = 'animalProduct'
    animalManagement = 'animalManagement'
    aquacultureManagement = 'aquacultureManagement'
    biochar = 'biochar'
    biologicalControlAgent = 'biologicalControlAgent'
    building = 'building'
    characterisedIndicator = 'characterisedIndicator'
    crop = 'crop'
    cropEstablishment = 'cropEstablishment'
    cropResidue = 'cropResidue'
    cropResidueManagement = 'cropResidueManagement'
    cropSupport = 'cropSupport'
    electricity = 'electricity'
    emission = 'emission'
    endpointIndicator = 'endpointIndicator'
    excreta = 'excreta'
    excretaManagement = 'excretaManagement'
    experimentDesign = 'experimentDesign'
    feedFoodAdditive = 'feedFoodAdditive'
    fertiliserBrandName = 'fertiliserBrandName'
    forage = 'forage'
    fuel = 'fuel'
    inorganicFertiliser = 'inorganicFertiliser'
    irrigation = 'irrigation'
    landCover = 'landCover'
    landUseManagement = 'landUseManagement'
    liveAnimal = 'liveAnimal'
    liveAquaticSpecies = 'liveAquaticSpecies'
    machinery = 'machinery'
    material = 'material'
    measurement = 'measurement'
    methodEmissionResourceUse = 'methodEmissionResourceUse'
    methodMeasurement = 'methodMeasurement'
    model = 'model'
    operation = 'operation'
    organicFertiliser = 'organicFertiliser'
    otherOrganicChemical = 'otherOrganicChemical'
    otherInorganicChemical = 'otherInorganicChemical'
    pastureManagement = 'pastureManagement'
    pesticideAI = 'pesticideAI'
    pesticideBrandName = 'pesticideBrandName'
    processedFood = 'processedFood'
    processingAid = 'processingAid'
    property = 'property'
    region = 'region'
    resourceUse = 'resourceUse'
    sampleDesign = 'sampleDesign'
    seed = 'seed'
    soilAmendment = 'soilAmendment'
    soilTexture = 'soilTexture'
    soilType = 'soilType'
    standardsLabels = 'standardsLabels'
    substrate = 'substrate'
    system = 'system'
    tillage = 'tillage'
    transport = 'transport'
    usdaSoilType = 'usdaSoilType'
    veterinaryDrug = 'veterinaryDrug'
    waste = 'waste'
    wasteManagement = 'wasteManagement'
    water = 'water'
    waterRegime = 'waterRegime'

class Term(BaseModel):

    class Config:
        extra = Extra.forbid
    id: str = Field(validation_alias=AliasChoices('@id', 'id'), serialization_alias='@id', description='Unique id assigned by HESTIA')
    
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    name: str = Field(..., description='The name of the Term.', examples=['Wheat, grain', 'N2O, to air, inorganic fertiliser, direct', 'France'])
    synonyms: Optional[List[str]] = Field(None, description='A list of synonyms for the name of the Term.', examples=[])
    definition: Optional[str] = Field(None, description='A definition of the Term.', examples=['The grain, including outer husk.', 'Nitrous oxide emissions to air from nitrification and denitrification of inorganic fertiliser.'])
    description: Optional[str] = Field(None, description='A more detailed description of the Term, which can include information about the source of these data.', examples=[])
    units: Optional[str] = Field(None, description='The units that the value (quantity) must always be expressed in (e.g., kg).', examples=['kg', 'kg N2O'])
    unitsDescription: Optional[str] = Field(None, description='A description of the units of the term in plain and simple language.', examples=[])
    subClassOf: Optional[List[Term]] = Field(None, description='A list of references to the Terms that are one level above in a hierarchy (see the RDF Vocabulary for more details).', examples=[[{'@id': 'wheatPlants', '@type': 'Term', 'name': 'Wheat plants', 'termType': 'crop'}]])
    defaultProperties: Optional[List[Property]] = Field(None, description='A list of default Properties of the Term (e.g., the dry matter of a crop).', examples=[[{'@type': 'Property', 'term': {'@id': 'dryMatter', '@type': 'Term', 'name': 'Dry matter', 'termType': 'property'}, 'value': 87}]])
    casNumber: Optional[constr(regex='^[\\d\\-]+$')] = Field(None, description='The unique numerical identifier assigned by the Chemical Abstracts Service (CAS) to every chemical substance described in the open scientific literature.', examples=[])
    ecoinventReferenceProductId: Optional[EcoinventReferenceProductId] = Field(None, description='The id of the reference product of the activity in the ecoinvent database.', examples=[])
    fishstatName: Optional[str] = Field(None, description='The name of the species in the FAO FISHSTAT database.', examples=[])
    hsCode: Optional[str] = Field(None, description='The World Customs Organization Harmonized System 2017 code.', examples=['1214.90'])
    iccCode: Optional[conint(ge=0)] = Field(None, description='The Indicative Crop Classification code.', examples=[11])
    iso31662Code: Optional[constr(regex='^[A-Z]{2}-?([A-Za-z\\d]{1,3})?$')] = Field(None, description='The ISO 3166-2 code for sub divisions within countries.', examples=['FR'])
    gadmFullName: Optional[str] = Field(None, description='The full name of the administrative region including all higher level region names in the GADM database.', examples=['France'])
    gadmId: Optional[constr(regex='^[A-Z]{3}[\\.]?([\\d_\\.]*)?$')] = Field(None, description='The unique identifier assigned by GADM database.', examples=['FRA'])
    gadmLevel: Optional[conint(ge=0, le=5)] = Field(None, description='The level of the administrative region in the GADM database.', examples=[])
    gadmName: Optional[str] = Field(None, description='The name of the administrative region in the GADM database.', examples=['France'])
    gadmCountry: Optional[str] = Field(None, description='The name of the country in the GADM database.', examples=[])
    gtin: Optional[constr(regex='^[\\d]{8,14}$')] = Field(None, description='The Global Trade Item Number (GTIN) is an identifier for trade items, developed by GS1.', examples=[])
    canonicalSmiles: Optional[constr(regex='^[^J][A-Za-z0-9@+%\\.\\-\\[\\]\\(\\)\\\\\\/=#$]*$')] = Field(None, description="The simplified molecular-input line-entry system (SMILES) is a specification in is a string of symbols which represents a chemical's three-dimensional structure. A large number of SMILES exist for any particular structure, and canonical SMILES generates a single generic SMILES amongst all possibilities.", examples=[])
    latitude: Optional[confloat(ge=-90.0, le=90.0)] = Field(None, description='The latitude (-90 to 90, WGS84 datum). If a polygon, the centroid.', examples=[46.55891593])
    longitude: Optional[confloat(ge=-180.0, le=180.0)] = Field(None, description='The longitude (-180 to 180, WGS84 datum). If a polygon, the centroid.', examples=[2.553552532])
    area: Optional[confloat(ge=0.0)] = Field(None, description='The area of the region in km2.', examples=[])
    openLCAId: Optional[str] = Field(None, description='The identifier for the activity in the openLCA database.', examples=[])
    scientificName: Optional[str] = Field(None, description='The taxonomic name of an organism that consists of the genus and species.', examples=['Triticum aestivum'])
    website: Optional[Website] = Field(None, description='A website URL.', examples=[])
    agrovoc: Optional[Agrovoc] = Field(None, description='A hyperlink to the FAO AGROVOC multilingual thesaurus entry.', examples=[])
    aquastatSpeciesFactSheet: Optional[AquastatSpeciesFactSheet] = Field(None, description='A hyperlink to the AQUASTAT species fact sheet.', examples=[])
    cornellBiologicalControl: Optional[CornellBiologicalControl] = Field(None, description='A hyperlink to the Cornell University biological control glossary page.', examples=[])
    ecolabelIndex: Optional[EcolabelIndex] = Field(None, description='A hyperlink to the Ecolabel Index page.', examples=[])
    feedipedia: Optional[Feedipedia] = Field(None, description='A hyperlink to the Feedipedia page.', examples=[{'@id': 'https://www.feedipedia.org/node/12754'}])
    fishbase: Optional[Fishbase] = Field(None, description='A hyperlink to the Fishbase page.', examples=[])
    pubchem: Optional[Pubchem] = Field(None, description='A hyperlink to the PubChem page.', examples=[])
    wikipedia: Optional[Wikipedia] = Field(None, description='A hyperlink to the Wikipedia page.', examples=[{'@id': 'https://en.wikipedia.org/wiki/Wheat'}])
    termType: TermType = Field(..., description='The type of term.', examples=['crop', 'model', 'region'])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    createdAt: Optional[date] = Field(None, description='Date created on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])
    updatedAt: Optional[date] = Field(None, description='Last update date on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])

from pydantic import BaseModel, Extra, Field, confloat, conint

class MethodTier(Enum):
    background = 'background'
    measured = 'measured'
    tier_1 = 'tier 1'
    tier_2 = 'tier 2'
    tier_3 = 'tier 3'
    not_relevant = 'not relevant'

class Indicator(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    term: Term = Field(..., description='A reference to the Term describing the emission e.g., CH4, to air, crop residue burning; the resource use e.g., Freshwater withdrawals, during Cycle; or the characterised environmental impact indicator e.g., Terrestrial ecotoxicity potential (1,4-DCBeq).', examples=[{'@id': 'gwp100', '@type': 'Term', 'name': 'GWP100', 'units': 'kg CO2eq', 'termType': 'characterisedIndicator'}, {'@id': 'landOccupationDuringCycle', '@type': 'Term', 'name': 'Land occupation, during Cycle', 'units': 'm2*year', 'termType': 'resourceUse'}])
    key: Optional[Term] = Field(None, description='For certain emissions (Pesticide, to ..., Ionising compounds, to, and Heavy metals, to...) the element or compound that was emitted.', examples=[])
    value: DecimalValue = Field(..., description='The quantity. If an average, it should always be the mean.', examples=[0.1947728, 2.8])
    distribution: Optional[List[float]] = Field(None, description='An array of up to 1000 random samples from the posterior distribution of value</code. This should describe the entire distribution of the dataset and not the distribution of the mean.', examples=[], max_items=1000)
    sd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of value.', examples=[])
    min: Optional[float] = Field(None, description='The minimum of value.', examples=[])
    max: Optional[float] = Field(None, description='The maximum of value.', examples=[])
    statsDefinition: Optional[StatsDefinition] = Field(None, description='What the descriptive statistics (sd, min, max, and value) are calculated across, or whether they are simulated or the output of a model. spatial refers to descriptive statistics calculated across spatial units (e.g., pixels) within a region or country. time refers to descriptive statistics calculated across units of time (e.g., hours).', examples=[])
    observations: Optional[conint(ge=1)] = Field(None, description='The number of observations the descriptive statistics are calculated over.', examples=[])
    methodTier: Optional[MethodTier] = Field(None, description='For emissions only, a field which matches the methodTier in each Cycle Emission.', examples=[])
    methodModel: Term = Field(..., description='A reference to the Term describing the method or model for calculating these data.', examples=[{'@id': 'ipcc2007', '@type': 'Term', 'name': 'IPCC (2007)', 'termType': 'model'}, {'@id': 'landOccupationCalculationIncludingUsedAndUnusedDuration', '@type': 'Term', 'name': 'Land occupation calculation, including used and unused duration', 'termType': 'model'}])
    methodModelDescription: Optional[str] = Field(None, description='A free text field, describing the method or model used for calculating these data. For example, it can be used to specify the version of the method or model, and/or the software used to carry out the assessment.', examples=[])
    inputs: Optional[List[Term]] = Field(None, description='For emissions or resource uses from Inputs production, the Term describing the Input. For characterised indicators or endpoint indicators, if this Indicator represents the quantity of that indicator caused by producing one or more Inputs used by this Cycle, the Term describing the Inputs.', examples=[])
    animals: Optional[List[Term]] = Field(None, description='For background Emissions, the Term(s) describing the Animal(s) they are associated with.', examples=[])
    country: Optional[Term] = Field(None, description='For indicators describing an emission or resource use related to inputs production, the country where the impacts occurred.', examples=[])
    operation: Optional[Term] = Field(None, description='For emissions or resource uses created by an operation, the Term describing the operation.', examples=[])
    landCover: Optional[Term] = Field(None, description='For land occupation and transformation, the term from the land cover glossary that describes the current land cover of the occupied land (e.g., Cropland or Almond tree). This is a required field for land occupation and land transformation resource uses.', examples=[{'@id': 'artichokePlant', '@type': 'Term', 'name': 'Artichoke plant', 'units': '% area', 'termType': 'landCover'}])
    previousLandCover: Optional[Term] = Field(None, description='For land transformation only, the land cover term that describes the previous land cover of the transformed land. The transformation period is defined by the term (e.g., 20 years, 100 years). If the land was transformed from multiple different land covers (e.g., 50% from forest to cropland and 50% from cropland to cropland), create one Indicator for each transformation. This is a required field for land transformation resource uses.', examples=[])
    transformation: Optional[Term] = Field(None, description='For emissions or resource uses created during a Transformation, the Term describing the Transformation.', examples=[])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data.', examples=[])
    otherSources: Optional[List[Source]] = Field(None, description='A list of references to any other sources of these data.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[List[str]] = Field(None, description="A list of fields that have been 'aggregated' using data from multiple Sites and Cycles.", examples=[])
    aggregatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the aggregation engine corresponding to each aggregated field.', examples=[])

class Measurement(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    term: Term = Field(..., description='A reference to the Term describing the Measurement.', examples=[{'@id': 'organicCarbonPerKgSoil', '@type': 'Term', 'name': 'Organic carbon (per kg soil)', 'units': 'g C / kg soil', 'termType': 'measurement'}, {'@id': 'sandSoilTexture', '@type': 'Term', 'name': 'Sand (soil texture)', 'termType': 'soilTexture'}])
    description: Optional[str] = Field(None, description='A short description of the Measurement.', examples=[])
    value: Optional[List[Union[float, bool]]] = Field(None, description='The quantity of the Measurement. If an average, it should always be the mean. Can be a single number (array of length one), an array of numbers with associated dates (e.g., representing multiple Measurements over time) or a boolean (e.g., Heavy winter precipitation can be either true or false).', examples=[[0.1916, 0.197, 0.6794]])
    distribution: Optional[List[Union[float, List[Any]]]] = Field(None, description='An array of up to 1000 random samples from the posterior distribution of valuedates field.', examples=[[[0.039, 0.24, 0.269, 0.342, 0.068], [0.097, 0.654, 0.161, 0.064, 0.009], [0.98, 0.755, 0.923, 0.269, 0.47]]], max_items=1000)
    sd: Optional[List[Optional[confloat(ge=0.0)]]] = Field(None, description='The standard deviation of value.', examples=[], ge=0)
    min: Optional[List[Optional[float]]] = Field(None, description='The minimum of value.', examples=[])
    max: Optional[List[Optional[float]]] = Field(None, description='The maximum of value.', examples=[])
    statsDefinition: Optional[StatsDefinition] = Field(None, description='What the descriptive statistics (sd, min, max, and value) are calculated across, or whether they are simulated or the output of a model. spatial refers to descriptive statistics calculated across spatial units (e.g., pixels) within a region or country. time refers to descriptive statistics calculated across units of time (e.g., hours).', examples=['replications'])
    observations: Optional[List[Optional[confloat(ge=1.0)]]] = Field(None, description='The number of observations the descriptive statistics are calculated over.', examples=[], ge=1)
    dates: Optional[List[Union[datetime.date, DateYear]]] = Field(None, description='A corresponding array to value, representing the dates (and times) of the Measurements in ISO 8601 format (YYYY-MM-DD, YYYY-MM, YYYY, --MM-DD, --MM, or YYYY-MM-DDTHH:mm:ssZ).', examples=[['1989-01', '1989-01-01', '1989-01-01T20:20:39']])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='For period Measurements, the start date of the Measurement in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    endDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='For period Measurements, the end date of the Measurement in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    measurementDuration: Optional[PositiveFloat] = Field(None, description='The duration of the Measurement in days.', examples=[])
    depthUpper: Optional[confloat(ge=0.0, le=9999.0)] = Field(None, description='For soil Measurements, the upper (shallower) depth of the Measurement interval in centimeters, using positive numbers.', examples=[])
    depthLower: Optional[confloat(ge=0.0, le=9999.0)] = Field(None, description='For soil Measurements, the lower (deeper) depth of the Measurement interval in centimeters.', examples=[])
    latitude: Optional[confloat(ge=-90.0, le=90.0)] = Field(None, description='The latitude of the Measurement if different from the centroid of the Site (-90 to 90, WGS84 datum).', examples=[])
    longitude: Optional[confloat(ge=-180.0, le=180.0)] = Field(None, description='The longitude of the Measurement if different from the centroid of the Site (-90 to 90, WGS84 datum).', examples=[])
    methodClassification: MethodClassification = Field(..., description='    An on-site physical measurement is based on weather stations or\n    indoor climate monitoring units on the Site or on soil samples\n    taken from the Site.\n\n    A physical measurement on nearby site is based on data from\n    nearby weather stations or indoor climate monitoring units or on soil samples\n    from nearby Sites which can be assumed to represent the current Site.\n\n    modelled using other measurements means the data\n    are estimated by applying a statistical or process based model, which is\n    associated with some error, to other measurements.\n\n    A tier 1 model quantifies the Measurement using activity data (i.e.,\n    data on Inputs, Practices, etc.) using a\n    simple equation with parameters which are not country or region specific.\n\n    A tier 2 model quantifies the Measurement from activity data using a\n    simple equation, often of the same form as the tier 1 model, but with\n    geographically specific parameters (e.g., other Site Measurements).\n\n    A tier 3 model quantifies the Measurement from activity data but uses\n    equations or algorithms that differ from the tier 1 model and\n    tier 2 model approaches. Tier 3 approaches include process based models\n    and statistical models with various forms.\n\n    A geospatial dataset is data in raster or vector format with\n    sub-regional and sub-national spatial resolution.\n\n    regional statistical data are soil or climate measurements\n    representative of the region.\n\n    country-level statistical data are soil or climate\n    measurements representative of the country.\n\n    expert opinion is a soil or climate measurement estimated by an\n    individual or organisation with context-specific knowledge.\n\n    An unsourced assumption is a soil or climate measurement\n    estimated by pure assumption or provided without any information on its source.\n', examples=['on-site physical measurement', 'geospatial dataset'])
    methodClassificationDescription: Optional[str] = Field(None, description='Further description or justification of the methodClassification.', examples=[])
    method: Optional[Term] = Field(None, description='For physical measurements, a reference to the Term describing the method used to acquire the measurement.', examples=[{'@id': 'chromicAcidWetOxidation', '@type': 'Term', 'name': 'Chromic acid wet oxidation', 'termType': 'methodMeasurement'}])
    methodDescription: Optional[str] = Field(None, description='A free text field describing the method used to acquire the Measurement.', examples=[])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data, if different from the defaultSource of the Site.', examples=[])
    otherSources: Optional[List[Source]] = Field(None, description='A list of references to any other sources of these data.', examples=[])
    properties: Optional[List[Property]] = Field(None, description='A list of Properties of the Measurement, which would override any default properties specified in the term.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='Version of the schema when the data was created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[List[str]] = Field(None, description="A list of fields that have been 'aggregated' using data from multiple Sites.", examples=[])
    aggregatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the aggregation engine corresponding to each aggregated field.', examples=[])

from pydantic import BaseModel, Extra, Field, confloat

class DistanceStatsDefinition(Enum):
    cycles = 'cycles'
    replications = 'replications'
    other_observations = 'other observations'
    time = 'time'
    spatial = 'spatial'
    regions = 'regions'
    simulated = 'simulated'
    modelled = 'modelled'

class Transport(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    term: Term = Field(..., description='A reference to the Term describing the Transport mode.', examples=[{'@id': 'freightLorry32MetricTon', '@type': 'Term', 'name': 'Freight, lorry, >32 metric ton', 'units': 'tkm', 'termType': 'transport'}])
    description: Optional[str] = Field(None, description='A description of the Transport mode.', examples=[])
    value: Optional[confloat(ge=0.0)] = Field(None, description='The distance transported times the number of tonnes transported. E.g., if 40 kg of Urea (kg N) are used during the Cycle, the nitrogen content of Urea is 45.5%, and the urea was transported 91 km, this field is calculated as 40 / 1000 / 45.5% * 91 = 8 tonne kilometers.', examples=[8])
    distribution: Optional[List[float]] = Field(None, description='An array of up to 1000 random samples from the posterior distribution of value</code. This should describe the entire distribution of the dataset and not the distribution of the mean.', examples=[], max_items=1000)
    sd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of value.', examples=[])
    min: Optional[confloat(ge=0.0)] = Field(None, description='The minimum of value.', examples=[])
    max: Optional[confloat(ge=0.0)] = Field(None, description='The maximum of value.', examples=[])
    statsDefinition: Optional[StatsDefinition] = Field(None, description='What the descriptive statistics (sd, min, max, and value) are calculated across, or whether they are simulated or the output of a model. Spatial is descriptive statistics calculated across spatial units (e.g., pixels) within a region or country.', examples=[])
    observations: Optional[List[Optional[confloat(ge=1.0)]]] = Field(None, description='The number of observations the descriptive statistics are calculated over.', examples=[], ge=1)
    distance: Optional[confloat(ge=0.0)] = Field(None, description='The distance transported in kilometers.', examples=[])
    distanceSd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of distance.', examples=[])
    distanceMin: Optional[confloat(ge=0.0)] = Field(None, description='The minimum of distance.', examples=[])
    distanceMax: Optional[confloat(ge=0.0)] = Field(None, description='The maximum of distance.', examples=[])
    distanceStatsDefinition: Optional[DistanceStatsDefinition] = Field(None, description='What the descriptive statistics (distanceSd, distanceMin, distanceMax, and distance) are calculated across, or whether they are simulated or the output of a model. spatial refers to descriptive statistics calculated across spatial units (e.g., pixels) within a region or country. time refers to descriptive statistics calculated across units of time (e.g., hours).', examples=[])
    distanceObservations: Optional[List[Optional[confloat(ge=1.0)]]] = Field(None, description='The number of observations the descriptive statistics for distance are calculated over.', examples=[], ge=1)
    returnLegIncluded: bool = Field(..., description='Whether the return leg is included in value and distance.', examples=[])
    methodModel: Optional[Term] = Field(None, description='A reference to the Term describing the method or model used to acquire or estimate these data.', examples=[])
    methodModelDescription: Optional[str] = Field(None, description='A free text field, describing the method or model used to acquire or estimate these data.', examples=[])
    methodClassification: Optional[MethodClassification] = Field(None, description='A classification of the method used to acquire or estimate the term and value. Overrides the defaultMethodClassification specified in the Cycle. methodClassification should be specified separately for inputs (see Input) and practices (see Practice).    physical measurement means the amount is quantified using weighing,\n    volume measurement, metering, chemical methods, or other physical approaches.\n\n    verified survey data means the data are initially collected through\n    surveys; all or a subset of the data are verified using physical methods; and\n    erroneous survey data are discarded or corrected.\n\n    non-verified survey data means the data are collected through\n    surveys that have not been subjected to verification.\n\n    modelled means a previously calibrated model is used to estimate\n    this data point from other data points describing this Cycle.\n\n    estimated with assumptions means a documented assumption is used\n    to estimate this data point from other data points describing this Cycle.\n\n    consistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using the same technology (defined as the same\n        System or the same key Practices\n        as those specified in the Cycle);\n\n        At the same date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        and\n\n        In the same region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    inconsistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using a different technology (defined as a different\n        System or using different key\n        Practices to those specified in the Cycle);\n\n        At a different date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        or\n\n        In a different region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    expert opinion means the data have been estimated by experts in\n    the field.\n\n    unsourced assumption means the data do not have a clear source\n    and/or are based on assumptions only.\n', examples=['modelled'])
    methodClassificationDescription: Optional[str] = Field(None, description='A justification of the methodClassification used. If the data were estimated with assumptions this field should also describe the assumptions. This is a required field if methodClassification is specified.', examples=['Distance estimated using approximate road distance to likely supplier, assuming 100% load factor.'])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data.', examples=[])
    otherSources: Optional[List[Source]] = Field(None, description='A list of references to any other sources of these data.', examples=[])
    inputs: Optional[List[Input]] = Field(None, description='The Inputs into the Transport process (e.g., diesel).', examples=[])
    practices: Optional[List[Practice]] = Field(None, description='The Practices used.', examples=[])
    emissions: Optional[List[Emission]] = Field(None, description='The Emissions created during Transport.', examples=[[{'@type': 'Emission', 'term': {'@id': 'co2ToAirFuelCombustion', '@type': 'Term', 'name': 'CO2, to air, fuel combustion', 'units': 'kg CO2', 'termType': 'emission'}, 'value': [0.7], 'methodModel': {'@id': 'emepEea2019', '@type': 'Term', 'name': 'EMEA-EEA (2019)', 'termType': 'model'}, 'methodTier': 'tier 1'}]])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[List[str]] = Field(None, description="A list of fields that have been 'aggregated' using data from multiple Sites and Cycles.", examples=[])
    aggregatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the aggregation engine corresponding to each aggregated field.', examples=[])

from typing import Optional

from pydantic import BaseModel, EmailStr, Extra, Field, constr

class Actor(BaseModel):

    class Config:
        extra = Extra.forbid
    id: str = Field(validation_alias=AliasChoices('@id', 'id'), serialization_alias='@id', description='Unique id assigned by HESTIA')
    
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    name: Optional[str] = Field(None, description='An automatically generated field made up of: firstName initial, lastName, primaryInstitution. If the Actor is an institution, the lastName only.', examples=['J. Poore, University of Oxford'])
    firstName: Optional[str] = Field(None, description="The Actor's first name.", examples=['Joseph'])
    lastName: str = Field(..., description="The Actor's last name or the name of the institution.", examples=['Poore'])
    orcid: Optional[str] = Field(None, description="The Actor's ORCiD identifier.", examples=['0000-0002-2527-7466'])
    scopusID: Optional[str] = Field(None, description="The Actor's Scopus identifier.", examples=['6506007033'])
    primaryInstitution: Optional[str] = Field(None, description="The Actor's primary institution.", examples=['University of Oxford'])
    city: Optional[str] = Field(None, description='A city or town.', examples=['Oxford'])
    country: Optional[Term] = Field(None, description='The country from the Glossary, following GADM naming conventions.', examples=[{'@id': 'GADM-GBR', '@type': 'Term', 'name': 'United Kingdom', 'termType': 'region'}])
    email: Optional[EmailStr] = Field(None, description='The email address of the Actor.', examples=['joseph.poore@biology.ox.ac.uk'])
    website: Optional[Website] = Field(None, description='A link to a website describing the Actor.', examples=[{'@id': 'https://www.oxfordmartin.ox.ac.uk/people/joseph-poore/'}])
    dataPrivate: bool = Field(..., description='If these data are private. Private means that HESTIA administrators can access these data and you can grant access to other platform users, but these data will not be made available to any other users of the platform or distributed to third parties.', examples=[])
    originalId: Optional[str] = Field(None, description='The identifier for these data in the source database (e.g., if the data were converted from openLCA or ecoinvent, the id field from that database).', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    createdAt: Optional[date] = Field(None, description='Date created on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])
    updatedAt: Optional[date] = Field(None, description='Last update date on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])

from pydantic import BaseModel, Extra, Field

class Completeness1(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    animalFeed: bool = Field(..., description='\n        The types and quantities of all animal feed\n         used during the Cycle, including hay and silage, are specified.\n         Note that fresh forage has its own completeness field.\n       Set to true\n\n       No animal feed was used during the Cycle.\n       Set to true\n\n       Animal feed was used during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[True])
    animalPopulation: bool = Field(..., description='\n       The types and quantities of all\n         live animals or\n         live aquatic species\n         that were present during the Cycle are specified in the animal node.\n       Set to true\n\n       No live animals were present during Cycle.\n       Set to true\n\n       Live animals were present during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[True])
    cropResidue: bool = Field(..., description='\n      The quantity of above and below ground\n       crop residue created\n       and its management are recorded.\n      Set to true\n\n      No crop residue was created or managed during the Cycle.\n      Set to true\n\n      Crop residue was created during the Cycle,\n        but the quantities and management are not fully recorded.\n      Set to false\n', examples=[])
    electricityFuel: bool = Field(..., description='\n       The types and quantities of all electricity and\n         fuel used during the Cycle,\n         excluding during the transport phase, are recorded.\n       Set to true\n\n       Electricity and fuel were not used during the Cycle.\n       Set to true\n\n       Electricity and/or fuel were used during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[])
    excreta: bool = Field(..., description='\n      The types and quantities of excreta created\n        and its management are specified.\n\n      Set to true\n\n      No excreta was created or managed during the Cycle.\n      Set to true\n\n      Excreta was created during the Cycle,\n        but the quantities and management are not fully recorded.\n      Set to false\n', examples=[True])
    fertiliser: bool = Field(..., description='\n       The types and quantities of all\n         organic fertiliser and\n         inorganic fertiliser,\n         or the quantity of each fertiliser brand name,\n         used during the Cycle are recorded.\n       Set to true\n\n       No fertilisers were used during the Cycle.\n       Set to true\n\n       Fertilisers were used during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[True])
    freshForage: bool = Field(..., description='\n        The types and quantities of all fresh forage\n         fed to, or grazed by, animals during the Cycle are recorded.\n       Set to true\n\n       No fresh forage was consumed during the Cycle.\n       Set to true\n\n       Fresh forage was consumed during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[True])
    ingredient: bool = Field(..., description='\n      For feed or food processing Cycles, the type and quantities of all\n         feed or food ingredients used, such as crop products,\n         animal products,\n         processed foods,\n         and/or feed or food additives are recorded.\n\n      Set to true\n\n      No feed or food ingredients were used during the Cycle.\n      Set to true\n\n      Food or feed ingredients were used during the Cycle,\n         but the types and quantities are not fully recorded.\n      Set to false\n', examples=[True])
    liveAnimalInput: bool = Field(..., description='\n       The types and quantities of all\n         live animals or\n         live aquatic species\n         which were Inputs into the Cycle are specified. For example,\n         piglets might be an Input into a pig\n         fattening Cycle.\n       Set to true\n\n       No live animals were Inputs into the Cycle.\n       Set to true\n\n       Live animals were Inputs into the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[True])
    material: bool = Field(..., description='\n       The types and quantities of all material\n         and substrate Inputs, which includes capital\n         equipment depreciated over the Cycle, are recorded.\n       Set to true\n\n       No material inputs were used during the Cycle.\n       Set to true\n\n       Material inputs were used during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[])
    operation: bool = Field(..., description='\n       The types of all mechanical operation\n         performed during the Cycle and either their duration or\n         the percentage of area they covered are recorded.\n       Set to true\n\n       No mechanical operations were performed during the Cycle.\n       Set to true\n\n       Mechanical operations were performed during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[])
    otherChemical: bool = Field(..., description='\n       The types and quantities of all other chemicals (including\n         processing aids,\n         other inorganic chemicals, and\n         other organic chemicals) used during\n         the Cycle are recorded.\n       Set to true\n\n       No processing aids or other chemicals were used during the Cycle.\n       Set to true\n\n       Processing aids and/or other chemicals were used during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[True])
    pesticideVeterinaryDrug: bool = Field(..., description='\n       The types and quantities of all pesticides (either as\n         active ingredients\n         or brand names) and\n         veterinary drugs used during\n         the Cycle are recorded.\n       Set to true\n\n       No pesticides or veterinary drugs were used during the Cycle.\n       Set to true\n\n       Pesticides and/or veterinary drugs were used during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[True])
    product: bool = Field(..., description='\n      The types and quantities of all\n        crop,\n        live animal,\n        live aquatic species,\n        animal product, and\n        processed food\n        produced during the Cycle are recorded. In the case where\n        Products were intended to be produced but no production occurred (e.g., if crops\n        fail due to disease) the types of products should still be recorded and the\n        quantity set to zero.\n\n      Set to true\n\n      No Products were produced (or intended to be produced) during the Cycle.\n      Set to true\n\n      Products were produced during the Cycle,\n         but the types and quantities are not fully recorded.\n      Set to false\n', examples=[True])
    seed: bool = Field(..., description='\n      The types and quantities of all seed Inputs,\n       such as seed,saplings, or semen are recorded.\n      Set to true\n\n      No seed Inputs were used during the Cycle.\n      Set to true\n\n      Seed Inputs were used during the Cycle,\n         but the types and quantities are not fully recorded.\n      Set to false\n', examples=[])
    soilAmendment: bool = Field(..., description='\n       The types and quantities of all\n         soil amendments and\n         biochar used\n         during the Cycle are recorded.\n       Set to true\n\n       No soil amendments were used during the Cycle.\n       Set to true\n\n       Soil amendments were used during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[True])
    transport: bool = Field(..., description='\n       The transport modes and distances\n         for each Input to the Site are recorded.\n         If Products were also Transported during this Cycle, the distances\n         and modes are specified.\n       Set to true\n\n       No Inputs were transported to the Site and\n         no Products were transported during the Cycle.\n       Set to true\n\n       Inputs and/or Products were transported, but data on the\n       modes and distances are not fully recorded.\n       Set to false\n', examples=[])
    waste: bool = Field(..., description='\n       The types and quantities all waste streams,\n         their and management, and their transport to where\n         they are managed are specified (note that crop residue\n         and excreta waste streams and management have their own\n         completeness fields).\n         Examples of waste streams include dead animals or plastic films for greenhouses.\n         Examples of management include disposal into a water body or bio-digestion.\n         Examples of transport include taking waste to a disposal center.\n\n       Set to true\n\n       No waste streams were created or managed during the Cycle.\n       Set to true\n\n       Waste was created or managed during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[])
    water: bool = Field(..., description='\n       The types and quantities of all water used\n         during the Cycle are recorded.\n       Set to true\n\n       No water was used during the Cycle or only very small quantities\n         were used but not recorded (e.g., water mixed with fertilisers or pesticides\n         for spraying).\n       Set to true\n\n       Water was used during the Cycle,\n         but the types and quantities are not fully recorded.\n       Set to false\n', examples=[True])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])

class Completeness(BaseModel):

    class Config:
        extra = Extra.forbid
    __root__: Completeness1 = Field(..., description='How complete the data describing the [Inputs](/schema/Input), [Products](/schema/Product), [Animals](/schema/Animal), and key [Practices](/schema/Practice) are. Each field in Completeness corresponds to one or more <code>[termTypes](/schema/Term#termType)</code> in the Glossary. If an area is marked complete, this means that the types and quantities of all the items within the <code>termType(s)</code> covered by the Completeness area are recorded and if they are not recorded, this means they were not present. Use of all data in the HESTIA format must therefore be interpreted in light of completeness: if completeness is <code>true</code> for a <code>termType</code>, but no data are provided for a term in that <code>termType</code>, that means the quantity of that item was zero. For quantity, completeness can be marked as <code>true</code> if either the total quantity is provided or both the minimum and maximum are provided.\n', title='Completeness')

class ReferencePeriod(Enum):
    average = 'average'
    start_of_Cycle = 'start of Cycle'
    end_of_Cycle = 'end of Cycle'

class Animal(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    animalId: str = Field(..., description='An identifier for each Animal which must be unique within the Cycle.', examples=['dairy-cattles'])
    term: Term = Field(..., description='A reference to the Term describing the Animal.', examples=[{'@id': 'dairyCattleCowLactating', '@type': 'Term', 'name': 'Dairy cattle, cow (lactating)', 'units': 'number', 'termType': 'liveAnimal'}])
    description: Optional[str] = Field(None, description='A description of the Animal type.', examples=[])
    referencePeriod: ReferencePeriod = Field(..., description='    The data are a time-weighted average over the Cycle. The recommended\n    value.\n\n    The data describe the Animal at the start of Cycle.\n\n    The data describe the Animal at the end of Cycle.\n', examples=['average'])
    value: Optional[float] = Field(None, description='The number of Animals per functionalUnit. If using an average reference period, the number should be a time-weighted average which takes into account transitions between different categories that occur during the Cycle (e.g., female calves becoming heifers) and mortalities.', examples=[30])
    distribution: Optional[List[float]] = Field(None, description='An array of up to 1000 random samples from the posterior distribution of value</code. This should describe the entire distribution of the dataset and not the distribution of the mean.', examples=[], max_items=1000)
    sd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of value.', examples=[])
    min: Optional[float] = Field(None, description='The minimum of value.', examples=[])
    max: Optional[float] = Field(None, description='The maximum of value.', examples=[])
    statsDefinition: Optional[StatsDefinition] = Field(None, description='What the descriptive statistics (sd, min, max, and value) are calculated across, or whether they are simulated or the output of a model. spatial refers to descriptive statistics calculated across spatial units (e.g., pixels) within a region or country. time refers to descriptive statistics calculated across units of time (e.g., hours).', examples=[])
    observations: Optional[confloat(ge=1.0)] = Field(None, description='The number of observations the descriptive statistics are calculated over.', examples=[])
    price: Optional[confloat(ge=0.0)] = Field(None, description='The price of the Animal. The price should be expressed per animal. The currency must be specified.', examples=[])
    currency: Optional[constr(regex='^[A-Z]{3}$')] = Field(None, description='The three letter currency code in ISO 4217 format.', examples=[])
    methodClassification: Optional[MethodClassification] = Field(None, description='A classification of the method used to acquire or estimate the term and value. Overrides the defaultMethodClassification specified in the Cycle. methodClassification should be specified separately for properties (see Property), inputs (see Input) and practices (see Practice).    physical measurement means the amount is quantified using weighing,\n    volume measurement, metering, chemical methods, or other physical approaches.\n\n    verified survey data means the data are initially collected through\n    surveys; all or a subset of the data are verified using physical methods; and\n    erroneous survey data are discarded or corrected.\n\n    non-verified survey data means the data are collected through\n    surveys that have not been subjected to verification.\n\n    modelled means a previously calibrated model is used to estimate\n    this data point from other data points describing this Cycle.\n\n    estimated with assumptions means a documented assumption is used\n    to estimate this data point from other data points describing this Cycle.\n\n    consistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using the same technology (defined as the same\n        System or the same key Practices\n        as those specified in the Cycle);\n\n        At the same date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        and\n\n        In the same region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    inconsistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using a different technology (defined as a different\n        System or using different key\n        Practices to those specified in the Cycle);\n\n        At a different date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        or\n\n        In a different region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    expert opinion means the data have been estimated by experts in\n    the field.\n\n    unsourced assumption means the data do not have a clear source\n    and/or are based on assumptions only.\n', examples=[])
    methodClassificationDescription: Optional[str] = Field(None, description='A justification of the methodClassification used. If the data were estimated with assumptions this field should also describe the assumptions. This is a required field if methodClassification is specified.', examples=[])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data, if different from the defaultSource of the Cycle.', examples=[])
    otherSources: Optional[List[Source]] = Field(None, description='A list of references to any other sources of these data.', examples=[])
    properties: Optional[List[Property]] = Field(None, description='A list of Properties of the Animal type, which would override any default properties specified in the term.', examples=[[{'@type': 'Property', 'term': {'@id': 'liveweightPerHead', '@type': 'Term', 'name': 'Liveweight per head', 'units': 'kg liveweight / head', 'termType': 'property'}, 'value': 300}, {'@type': 'Property', 'term': {'@id': 'mortalityRate', '@type': 'Term', 'name': 'Mortality rate', 'units': '%', 'termType': 'property'}, 'value': 4.5}]])
    inputs: Optional[List[Input]] = Field(None, description='The Inputs (e.g., feed or veterinary drugs). Values for each Input should be a sum over all animals represented by this blank node and not a value per head.', examples=[])
    practices: Optional[List[Practice]] = Field(None, description='The Practices used to describe the system each Animal type is in or to describe management practices specific to each animal type (e.g., the Milk yield per cow (FPCM)).', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[List[str]] = Field(None, description="A list of fields that have been 'aggregated' using data from multiple Cycles.", examples=[])
    aggregatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the aggregation engine corresponding to each aggregated field.', examples=[])

class Input(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    term: Term = Field(..., description='A reference to the Term describing the Input.', examples=[{'@id': 'CAS-34494-04-7', '@type': 'Term', 'name': 'Glyphosate', 'units': 'g active ingredient', 'termType': 'pesticideAI'}])
    description: Optional[str] = Field(None, description='A description of the Input.', examples=[])
    value: Optional[List[Optional[float]]] = Field(None, description='The quantity of the Input. If an average, it should always be the mean. Can be a single number (array of length one) or an array of numbers with associated dates (e.g., representing an application schedule).', examples=[[400]])
    distribution: Optional[List[Union[float, List[Any]]]] = Field(None, description='An array of up to 1000 random samples from the posterior distribution of valuedates field.', examples=[], max_items=1000)
    sd: Optional[List[Optional[confloat(ge=0.0)]]] = Field(None, description='The standard deviation of value.', examples=[[180]], ge=0)
    min: Optional[List[Optional[float]]] = Field(None, description='The minimum of value.', examples=[])
    max: Optional[List[Optional[float]]] = Field(None, description='The maximum of value.', examples=[])
    statsDefinition: Optional[StatsDefinition] = Field(None, description='What the descriptive statistics (sd, min, max, and value) are calculated across, or whether they are simulated or the output of a model. spatial refers to descriptive statistics calculated across spatial units (e.g., pixels) within a region or country. time refers to descriptive statistics calculated across units of time (e.g., hours).', examples=['replications'])
    observations: Optional[List[Optional[confloat(ge=1.0)]]] = Field(None, description='The number of observations the descriptive statistics are calculated over.', examples=[[10]], ge=1)
    dates: Optional[List[Union[datetime.date, DateYear]]] = Field(None, description='A corresponding array to value, representing the dates of the Inputs in ISO 8601 format (YYYY-MM-DD, YYYY-MM, YYYY, --MM-DD, --MM, or YYYY-MM-DDTHH:mm:ssZ).', examples=[])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='For Inputs over periods different to Cycle, the start date of the Input (if different from the start date of the Cycle]) in [ISO 8601 format (YYYY-MM-DD).', examples=[])
    endDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='For Inputs over periods different to Cycle, the end date of the Input (if different from the end date of the Cycle]) in [ISO 8601 format (YYYY-MM-DD).', examples=[])
    inputDuration: Optional[PositiveFloat] = Field(None, description='The duration of the Input in days.', examples=[])
    methodClassification: Optional[MethodClassification] = Field(None, description='A classification of the method used to acquire or estimate the term and value. Overrides the defaultMethodClassification specified in the Cycle. methodClassification should be specified separately for properties (see Property) and transport (see Transport).    physical measurement means the amount is quantified using weighing,\n    volume measurement, metering, chemical methods, or other physical approaches.\n\n    verified survey data means the data are initially collected through\n    surveys; all or a subset of the data are verified using physical methods; and\n    erroneous survey data are discarded or corrected.\n\n    non-verified survey data means the data are collected through\n    surveys that have not been subjected to verification.\n\n    modelled means a previously calibrated model is used to estimate\n    this data point from other data points describing this Cycle.\n\n    estimated with assumptions means a documented assumption is used\n    to estimate this data point from other data points describing this Cycle.\n\n    consistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using the same technology (defined as the same\n        System or the same key Practices\n        as those specified in the Cycle);\n\n        At the same date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        and\n\n        In the same region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    inconsistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using a different technology (defined as a different\n        System or using different key\n        Practices to those specified in the Cycle);\n\n        At a different date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        or\n\n        In a different region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    expert opinion means the data have been estimated by experts in\n    the field.\n\n    unsourced assumption means the data do not have a clear source\n    and/or are based on assumptions only.\n', examples=[])
    methodClassificationDescription: Optional[str] = Field(None, description='A justification of the methodClassification used. If the data were estimated with assumptions this field should also describe the assumptions. This is a required field if methodClassification is specified.', examples=[])
    model: Optional[Term] = Field(None, description='A reference to the Term describing the model used to estimate these data.', examples=[])
    modelDescription: Optional[str] = Field(None, description='A free text field, describing the model used to estimate these data.', examples=[])
    isAnimalFeed: Optional[bool] = Field(None, description='true if this Input is fed to animals. A required field for Inputs which could potentially be animal feed (defined as Inputs of termType = crop, forage, liveAnimal, animalProduct, liveAquaticSpecies, feedFoodAdditive, processedFood, or waste in animal production Cycles).', examples=[])
    fromCycle: Optional[bool] = Field(None, description='A required field for Inputs into Transformations only. true if this Input is a Product from the Cycle. false if this Input was added at the Transformation stage only (e.g., diesel used to power a grain dryer) or false if this Input is a Product from a previous Transformation.', examples=[])
    producedInCycle: Optional[bool] = Field(None, description='Whether an input is produced and used during the Cycle, e.g., true if the forage is grown on the pasture where animals are grazing, false if it is grown elsewhere.', examples=[])
    price: Optional[confloat(ge=0.0)] = Field(None, description='The price paid for this Input. The currency must be specified. The price should be expressed per the units defined in the term, for example per "kg active ingredient". In situations where a term describes one physical item (e.g., "NP Blend" fertiliser) but the glossary uses terms with unit that split the item (e.g., "NP Blend (kg N)" and "NP Blend (kg P2O5)") the price must be divided by the relative mass of each term.', examples=[])
    priceSd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of price.', examples=[])
    priceMin: Optional[confloat(ge=0.0)] = Field(None, description='The minimum of price.', examples=[])
    priceMax: Optional[confloat(ge=0.0)] = Field(None, description='The maximum of price.', examples=[])
    priceStatsDefinition: Optional[PriceStatsDefinition] = Field(None, description='What the descriptive statistics for price are calculated across.', examples=[])
    cost: Optional[confloat(ge=0.0)] = Field(None, description='The total cost of this Input (price x quantity), expressed as a positive value. The currency must be specified.', examples=[])
    costSd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of cost.', examples=[])
    costMin: Optional[confloat(ge=0.0)] = Field(None, description='The minimum of cost.', examples=[])
    costMax: Optional[confloat(ge=0.0)] = Field(None, description='The maximum of cost.', examples=[])
    costStatsDefinition: Optional[CostStatsDefinition] = Field(None, description='What the descriptive statistics for cost are calculated across.', examples=[])
    currency: Optional[constr(regex='^[A-Z]{3}$')] = Field(None, description='The three letter currency code in ISO 4217 format.', examples=[])
    lifespan: Optional[PositiveFloat] = Field(None, description='For Inputs used to create Infrastructure, the lifespan of this Input expressed in decimal years.', examples=[])
    operation: Optional[Term] = Field(None, description='A reference to the Term describing the operation associated with this Input (e.g., for the Input diesel the operation could be Soil decompaction, machine unspecified).', examples=[])
    country: Optional[Term] = Field(None, description='The country where this Input came from.', examples=[])
    region: Optional[Term] = Field(None, description='The region where this Input came from.', examples=[])
    impactAssessment: Optional[ImpactAssessment] = Field(None, description='A reference to the node containing environmental impact data related to producing this product and transporting it to the Site.', examples=[])
    impactAssessmentIsProxy: Optional[bool] = Field(None, description='\n      The impactAssessment\n        referred to represents data from the actual supply chain (e.g., data from\n        the actual supplying farm or the supplying feed mill).\n\n      Set to false\n\n      The impactAssessment\n        referred to is a proxy for the actual supply chain (e.g., global or\n        regional average data).\n\n      Set to true\n\n Required if impactAssessment is specified.\n', examples=[])
    site: Optional[Site] = Field(None, description='If the Cycle occurred on multiple Sites, the Site where this Input was used.', examples=[])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data, if different from the defaultSource of the Cycle.', examples=[])
    otherSources: Optional[List[Source]] = Field(None, description='A list of references to any other sources of these data.', examples=[])
    properties: Optional[List[Property]] = Field(None, description='A list of Properties of the Input, which would override any default properties specified in the term.', examples=[])
    transport: Optional[List[Transport]] = Field(None, description='A list of Transport stages to bring this Input to the Cycle.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[List[str]] = Field(None, description="A list of fields that have been 'aggregated' using data from multiple Cycles.", examples=[])
    aggregatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the aggregation engine corresponding to each aggregated field.', examples=[])

class Organisation(BaseModel):

    class Config:
        extra = Extra.forbid
    id: str = Field(validation_alias=AliasChoices('@id', 'id'), serialization_alias='@id', description='Unique id assigned by HESTIA')
    
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    name: Optional[str] = Field(None, description='The name of the Organisation.', examples=['La Ferme du Grand Roc'])
    description: Optional[str] = Field(None, description='A description of the Organisation.', examples=[])
    boundary: Optional[Dict[str, Any]] = Field(None, description="A nested GeoJSON object for the Organisation boundary of type 'FeatureCollection', 'Feature' or 'GeometryCollection' in the WGS84 datum.", examples=[])
    boundaryArea: Optional[confloat(ge=0.0)] = Field(None, description='The area in km2 of the boundary. This field is automatically calculated when boundary is provided.', examples=[])
    area: Optional[PositiveFloat] = Field(None, description='The area of the Organisation in hectares.', examples=[])
    latitude: Optional[confloat(ge=-90.0, le=90.0)] = Field(None, description='The latitude of the Organisation (-90 to 90).', examples=[49.16472])
    longitude: Optional[confloat(ge=-180.0, le=180.0)] = Field(None, description='The longitude of the Organisation (-180 to 180).', examples=[6.901544])
    streetAddress: Optional[str] = Field(None, description='The street address.', examples=[])
    city: Optional[str] = Field(None, description='The city or town.', examples=['Œting'])
    region: Optional[Term] = Field(None, description='The most specific geographical region from the Glossary.', examples=[{'@id': 'GADM-FRA.6.9_1', '@type': 'Term', 'name': 'Moselle', 'termType': 'region'}])
    country: Term = Field(..., description='The country from the Glossary.', examples=[{'@id': 'GADM-FRA', '@type': 'Term', 'name': 'France', 'termType': 'region'}])
    postOfficeBoxNumber: Optional[str] = Field(None, description='The post office box number.', examples=[])
    postalCode: Optional[str] = Field(None, description='The postal code.', examples=[])
    website: Optional[Website] = Field(None, description='A link to a website describing the Organisation.', examples=[])
    glnNumber: Optional[constr(regex='^\\d{13}$')] = Field(None, description='The Global Location Number.', examples=[])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The start date of the Organisation in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=['1989-06-01'])
    endDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The end date of the Organisation in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    infrastructure: Optional[List[Infrastructure]] = Field(None, description='The Infrastructure on the Site.', examples=[])
    dataPrivate: bool = Field(..., description='If these data are private. Private means that HESTIA administrators can access these data and you can grant access to other platform users, but these data will not be made available to any other users of the platform or distributed to third parties.', examples=[])
    originalId: Optional[str] = Field(None, description='The identifier for these data in the source database.', examples=[])
    uploadBy: Actor = Field(..., description='The user who uploaded these data.', examples=[{'@id': 'actor-577', '@type': 'Actor', 'name': 'J. Poore, University of Oxford'}])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    createdAt: Optional[date] = Field(None, description='Date created on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])
    updatedAt: Optional[date] = Field(None, description='Last update date on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])

from pydantic import BaseModel, Extra, Field, conint, constr

class AllocationMethod(Enum):
    economic = 'economic'
    mass = 'mass'
    energy = 'energy'
    biophysical = 'biophysical'
    none = 'none'
    none_required = 'none required'
    system_expansion = 'system expansion'

class ImpactAssessment(BaseModel):

    class Config:
        extra = Extra.forbid
    id: str = Field(validation_alias=AliasChoices('@id', 'id'), serialization_alias='@id', description='Unique id assigned by HESTIA')
    
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    name: Optional[str] = Field(None, description='The name of the Impact Assessment.', examples=["Impact Assessment for 'Wheat, grain' under treatment '50N' in 1989 in France"])
    version: Optional[str] = Field(None, description='The version of the Impact Assessment.', examples=[])
    versionDetails: Optional[str] = Field(None, description='A text description of the version of the Impact Assessment.', examples=[])
    cycle: Optional[Cycle] = Field(None, description='A reference to the node describing the production Cycle.', examples=[{'@id': 'vc664x8', '@type': 'Cycle', 'name': '50N, Wheat grain, 1989'}])
    product: Product = Field(..., description='The Product produced during the production Cycle, which is the target of this Impact Assessment.', examples=[{'@type': 'Product', 'term': {'@id': 'wheatGrain', '@type': 'Term', 'name': 'Wheat, grain', 'termType': 'crop'}, 'value': [100]}])
    functionalUnitQuantity: DecimalValue = Field(..., const=True, description='The quantity of the product that this Impact Assessment is expressed per. The units are determined by the Term of the product (e.g., 1kg for Wheat, grain, or 1 head for a Pig).', examples=[1])
    allocationMethod: AllocationMethod = Field(..., description='The method used to allocate environmental impacts between Products.', examples=['economic'])
    endDate: Union[datetime.date, DateYear] = Field(..., description='The end date or year of production in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=['1989-12-31'])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='The start date of production in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    site: Optional[Site] = Field(None, description='A reference to the node describing the Site where production occurred.', examples=[])
    country: Term = Field(..., description='The country from the Glossary, following GADM naming conventions.', examples=[{'@id': 'GADM-FRA', '@type': 'Term', 'name': 'France', 'termType': 'region'}])
    region: Optional[Term] = Field(None, description='The lowest level GADM region available following the naming convention used in the Glossary.', examples=[{'@id': 'GADM-FRA.6.9.3_1', '@type': 'Term', 'name': 'Forbach (Districts), Moselle (Department), Grand Est (Region), France', 'termType': 'region'}])
    organisation: Optional[Organisation] = Field(None, description='A reference to the node describing the Organisation that produced the Product.', examples=[])
    source: Optional[Source] = Field(None, description='The Source for the data in the Impact Assessment. Not required (but recommended) for public uploads (i.e., where dataPrivate is false).', examples=[{'@id': 's66765d', '@type': 'Source', 'name': 'Gigou (1990)'}])
    emissionsResourceUse: Optional[List[Indicator]] = Field(None, description='A list of emissions and resource uses.', examples=[[{'@type': 'Indicator', 'term': {'@id': 'no3ToGroundwaterSoilFlux', '@type': 'Term', 'name': 'NO3, to groundwater, soil flux', 'units': 'kg NO3', 'termType': 'emission'}, 'value': 0.01709, 'methodModel': {'@id': 'percolationLysimeter', '@type': 'Term', 'name': 'Percolation lysimeter', 'termType': 'methodEmissionResourceUse'}, 'methodTier': 'tier 2'}]])
    impacts: Optional[List[Indicator]] = Field(None, description='The mid-point environmental impact Indicators. These are calculated from emissions and resourceUse by applying characterisation factors to generate a characterised impact indicator.', examples=[[{'@type': 'Indicator', 'term': {'@id': 'gwp100', '@type': 'Term', 'name': 'GWP100', 'units': 'kg CO2eq', 'termType': 'characterisedIndicator'}, 'methodModel': {'@id': 'ipcc2007', '@type': 'Term', 'name': 'IPCC (2007)', 'units': 'kg CO2eq', 'termType': 'model'}, 'value': 0.1947728}]])
    endpoints: Optional[List[Indicator]] = Field(None, description='The end-point environmental impact Indicators. These are calculated from the mid-point impacts by applying characterisation factors to generate an end-point impact indicator.', examples=[])
    dataPrivate: bool = Field(..., description='If these data are private. Private means that HESTIA administrators can access these data and you can grant access to other platform users, but these data will not be made available to any other users of the platform or distributed to third parties.', examples=[])
    organic: Optional[bool] = Field(False, description='If the Cycle has an organic label. Used by the aggregation engine only.', examples=[])
    irrigated: Optional[bool] = Field(False, description='If the Cycle was irrigated. Used by the aggregation engine only.', examples=[])
    autoGenerated: Optional[bool] = Field(False, description='If this node was autogenerated during upload.', examples=[])
    originalId: Optional[str] = Field(None, description='The identifier for these data in the source database (e.g., if the data were converted from openLCA or ecoinvent, the id field from that database).', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[bool] = Field(None, description="If this Impact Assessment has been 'aggregated' using data from multiple Impact Assessments.", examples=[])
    aggregatedDataValidated: Optional[bool] = Field(None, description='If this aggregated Impact Assessment has been validated by the HESTIA team.', examples=[])
    aggregatedVersion: Optional[str] = Field(None, description='A version of the aggregation engine corresponding to this Impact Assessment.', examples=[])
    aggregatedQualityScore: Optional[conint(ge=0)] = Field(None, description='A data quality score for aggregated data, set equal to the quality score of the linked Cycle.', examples=[])
    aggregatedQualityScoreMax: Optional[conint(ge=3)] = Field(None, description='The maximum value for the aggregated quality score, set equal tothe max quality score of the linked Cycle.', examples=[])
    aggregatedImpactAssessments: Optional[List[ImpactAssessment]] = Field(None, description='Impact Assessments used to aggregated this Impact Assessment.', examples=[])
    aggregatedSources: Optional[List[Source]] = Field(None, description='Sources used to aggregated this Impact Assessment.', examples=[])
    createdAt: Optional[date] = Field(None, description='Date created on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])
    updatedAt: Optional[date] = Field(None, description='Last update date on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])

from typing import List, Optional, Union

class Management(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    term: Term = Field(..., description='A reference to the Term describing the Site Management.', examples=[{'@id': 'fullTillage', '@type': 'Term', 'name': 'Full tillage', 'units': '% area', 'termType': 'tillage'}, {'@id': 'animalManureUsed', '@type': 'Term', 'name': 'Animal manure used', 'units': 'boolean', 'termType': 'landUseManagement'}, {'@id': 'forest', '@type': 'Term', 'name': 'Forest', 'termType': 'landCover'}])
    description: Optional[str] = Field(None, description='A description of the Management.', examples=[])
    value: Optional[Union[float, bool]] = Field(None, description='The value associated with the Management Term.', examples=[42, True, 5.9])
    distribution: Optional[List[float]] = Field(None, description='An array of up to 1000 random samples from the posterior distribution of value</code. This should describe the entire distribution of the dataset and not the distribution of the mean.', examples=[], max_items=1000)
    sd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of value.', examples=[])
    min: Optional[float] = Field(None, description='The minimum of value.', examples=[])
    max: Optional[float] = Field(None, description='The maximum of value.', examples=[])
    statsDefinition: Optional[StatsDefinition] = Field(None, description='What the descriptive statistics (sd, min, max, and value) are calculated across, or whether they are simulated or the output of a model. spatial refers to descriptive statistics calculated across spatial units (e.g., pixels) within a region or country. time refers to descriptive statistics calculated across units of time (e.g., hours).', examples=[])
    observations: Optional[conint(ge=1)] = Field(None, description='The number of observations the descriptive statistics are calculated over.', examples=[])
    startDate: Optional[constr(regex='^[0-9]{4}(-[0-9]{2})?(-[0-9]{2})?$')] = Field(None, description='The start date of this Site Management in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=['1990', '2015', '1990-01-01'])
    endDate: constr(regex='^[0-9]{4}(-[0-9]{2})?(-[0-9]{2})?$') = Field(..., description='The end date of this Site Management in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=['2005', '2022', '1990-12-31'])
    methodClassification: Optional[MethodClassification] = Field(None, description='A classification of the method used to acquire or estimate the term and percentArea. Overrides the defaultMethodClassification specified in the Site.    physical measurement means the amount is quantified using weighing,\n    volume measurement, metering, chemical methods, or other physical approaches.\n\n    verified survey data means the data are initially collected through\n    surveys; all or a subset of the data are verified using physical methods; and\n    erroneous survey data are discarded or corrected.\n\n    non-verified survey data means the data are collected through\n    surveys that have not been subjected to verification.\n\n    modelled means a previously calibrated model is used to estimate\n    this data point from other data points describing this Cycle.\n\n    estimated with assumptions means a documented assumption is used\n    to estimate this data point from other data points describing this Cycle.\n\n    consistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using the same technology (defined as the same\n        System or the same key Practices\n        as those specified in the Cycle);\n\n        At the same date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        and\n\n        In the same region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    inconsistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using a different technology (defined as a different\n        System or using different key\n        Practices to those specified in the Cycle);\n\n        At a different date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        or\n\n        In a different region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    expert opinion means the data have been estimated by experts in\n    the field.\n\n    unsourced assumption means the data do not have a clear source\n    and/or are based on assumptions only.\n', examples=[])
    methodClassificationDescription: Optional[str] = Field(None, description='A justification of the methodClassification used. If the data were estimated with assumptions this field should also describe the assumptions. This is a required field if methodClassification is specified.', examples=[])
    model: Optional[Term] = Field(None, description='A reference to the Term describing the model used to estimate these data.', examples=[])
    modelDescription: Optional[str] = Field(None, description='A free text field, describing the model used to estimate these data.', examples=[])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data, if different from the defaultSource of the Cycle or Site.', examples=[])
    otherSources: Optional[List[Source]] = Field(None, description='A list of references to any other sources of these data.', examples=[])
    properties: Optional[List[Property]] = Field(None, description='A list of Properties which can be assigned to the Management Term.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[List[str]] = Field(None, description="A list of fields that have been 'aggregated' using data from multiple Sites.", examples=[])
    aggregatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the aggregation engine corresponding to each aggregated field.', examples=[])

class DataState(Enum):
    complete = 'complete'
    not_required = 'not required'
    requires_validation = 'requires validation'
    missing = 'missing'
    unassigned = 'unassigned'

class Property(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    term: Term = Field(..., description='A reference to the Term describing the Property.', examples=[{'@id': 'dryMatter', '@type': 'Term', 'name': 'Dry matter', 'termType': 'property'}, {'@id': 'activeIngredient', '@type': 'Term', 'name': 'Active Ingredient', 'units': '%', 'termType': 'property'}])
    description: Optional[str] = Field(None, description='A description of the Property.', examples=[])
    key: Optional[Term] = Field(None, description="If the data associated with the Property are in key:value form, the key. E.g., in a list of pesticide active ingredients in a pesticide brand, the id of the key might be 'CAS-1071-83-6' and the value might be 25 percent.", examples=[{'@id': 'CAS-111-30-8', '@type': 'Term', 'name': 'Pentanedial', 'termType': 'pesticideAI'}])
    value: Optional[Union[float, bool]] = Field(None, description='The value of the Property.', examples=[87, 25])
    share: Optional[confloat(ge=0.0, le=100.0)] = Field(100, description='The percentage of the Product or Input value the Property refers to (e.g., if 70% of the steers sold are 450 days old and the remaining 30% are 900 days old, the term Beef cattle, steer should be recorded once, with two Age properties associated with it: the first one with value 450 and share 70, the second one with value 900 and share 30).', examples=[])
    sd: Optional[confloat(ge=0.0)] = Field(None, description='The standard deviation of value.', examples=[])
    min: Optional[float] = Field(None, description='The minimum of value.', examples=[])
    max: Optional[float] = Field(None, description='The maximum of value.', examples=[])
    statsDefinition: Optional[StatsDefinition] = Field(None, description='What the descriptive statistics (sd, min, max, and value) are calculated across, or whether they are simulated or the output of a model. spatial refers to descriptive statistics calculated across spatial units (e.g., pixels) within a region or country. time refers to descriptive statistics calculated across units of time (e.g., hours).', examples=[])
    observations: Optional[confloat(ge=1.0)] = Field(None, description='The number of observations the descriptive statistics are calculated over.', examples=[])
    date: Optional[Union[datetime.date, DateYear]] = Field(None, description='The date in which the Property was measured in ISO 8601 format (YYYY-MM-DD, YYYY-MM, YYYY, --MM-DD, --MM, or YYYY-MM-DDTHH:mm:ssZ).', examples=[])
    startDate: Optional[constr(regex='^[0-9]{4}(-[0-9]{2})?(-[0-9]{2})?$')] = Field(None, description='For Properties over periods different to Cycle, the start date of the Property (if different from the start date of the Cycle]) in [ISO 8601 format (YYYY-MM-DD).', examples=[])
    endDate: Optional[constr(regex='^[0-9]{4}(-[0-9]{2})?(-[0-9]{2})?$')] = Field(None, description='For Properties over periods different to Cycle, the end date of the Property (if different from the end date of the Cycle]) in [ISO 8601 format (YYYY-MM-DD).', examples=[])
    methodModel: Optional[Term] = Field(None, description='A reference to the Term describing the method or model for acquiring or estimating these data.', examples=[])
    methodModelDescription: Optional[str] = Field(None, description='A free text field, describing the method or model used for acquiring or estimating these data.', examples=[])
    methodClassification: Optional[MethodClassification] = Field(None, description='A classification of the method used to acquire or estimate the term and value. Overrides the defaultMethodClassification specified in the Cycle.    physical measurement means the amount is quantified using weighing,\n    volume measurement, metering, chemical methods, or other physical approaches.\n\n    verified survey data means the data are initially collected through\n    surveys; all or a subset of the data are verified using physical methods; and\n    erroneous survey data are discarded or corrected.\n\n    non-verified survey data means the data are collected through\n    surveys that have not been subjected to verification.\n\n    modelled means a previously calibrated model is used to estimate\n    this data point from other data points describing this Cycle.\n\n    estimated with assumptions means a documented assumption is used\n    to estimate this data point from other data points describing this Cycle.\n\n    consistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using the same technology (defined as the same\n        System or the same key Practices\n        as those specified in the Cycle);\n\n        At the same date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        and\n\n        In the same region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    inconsistent external sources means the data are taken from external\n    datasets referring to different producers/enterprises:\n\n        Using a different technology (defined as a different\n        System or using different key\n        Practices to those specified in the Cycle);\n\n        At a different date (defined as occurring within the\n        startDate and endDate of the Cycle);\n        or\n\n        In a different region or country.\n\n    Modelling or assumptions may have also been used to transform these data.\n\n    expert opinion means the data have been estimated by experts in\n    the field.\n\n    unsourced assumption means the data do not have a clear source\n    and/or are based on assumptions only.\n', examples=[])
    methodClassificationDescription: Optional[str] = Field(None, description='A justification of the methodClassification used. If the data were estimated with assumptions this field should also describe the assumptions. Not required but recommended if methodClassification is specified.', examples=[])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data.', examples=[])
    dataState: Optional[DataState] = Field(None, description='An indicator of the data quality or whether the data are missing.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[List[str]] = Field(None, description="A list of fields that have been 'aggregated' using data from multiple Sites and Cycles.", examples=[])
    aggregatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the aggregation engine corresponding to each aggregated field.', examples=[])

from pydantic import BaseModel, Extra, Field, constr

class OriginalLicense(Enum):
    CC0 = 'CC0'
    CC_BY = 'CC-BY'
    CC_BY_SA = 'CC-BY-SA'
    CC_BY_NC = 'CC-BY-NC'
    CC_BY_NC_SA = 'CC-BY-NC-SA'
    CC_BY_NC_ND = 'CC-BY-NC-ND'
    CC_BY_ND = 'CC-BY-ND'
    GNU_FDL = 'GNU-FDL'
    other_public_license = 'other public license'
    no_public_license = 'no public license'

class Source(BaseModel):

    class Config:
        extra = Extra.forbid
    id: str = Field(validation_alias=AliasChoices('@id', 'id'), serialization_alias='@id', description='Unique id assigned by HESTIA')
    
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    name: str = Field(..., description='The name from bibliography.', examples=['Gigou (1990)'])
    bibliography: Bibliography = Field(..., description='The bibliographic information describing the document or dataset.', examples=[{'@type': 'Bibliography', 'name': 'Gigou (1990)', 'title': 'Bilan des éléments minéraux sous une rotation blé-orge-colza en lysimètres', 'authors': [{'@id': 'avvs577', '@type': 'Actor', 'name': 'J. Gigou'}], 'outlet': "L'Agronomie", 'year': 1990, 'volume': 41, 'issue': '2', 'pages': '149-153'}])
    metaAnalyses: Optional[List[Source]] = Field(None, description='If multiple Sources were consolidated by meta-analysis, a list of sources describing the meta-analysis document or dataset.', examples=[[{'@id': 'xgfr67d', '@type': 'Source', 'name': 'Poore & Nemecek (2018)', 'bibliography': {'@type': 'Bibliography', 'name': 'Poore & Nemecek (2018)', 'documentDOI': '10.1126/science.aaq0216', 'scopus': '2-s2.0-85048197694', 'mendeleyID': '9ecd6598-d3c7-36a3-965b-821be771b328', 'title': "Reducing food's environmental impacts through producers and consumers", 'authors': [{'@id': 'avvs577', '@type': 'Actor', 'name': 'J. Poore, Univerity of Oxford'}, {'@id': 'gyys7s9', '@type': 'Actor', 'name': 'T. Nemecek, Agroscope'}], 'outlet': 'Science', 'year': 2018, 'abstract': "Food's environmental impacts are created by millions of diverse producers. To identify solutions that are effective under this heterogeneity, we consolidated data covering five environmental indicators; 38,700 farms; and 1600 processors, packaging types, and retailers. Impact can vary 50-fold among producers of the same product, creating substantial mitigation opportunities. However, mitigation is complicated by trade-offs, multiple ways for producers to achieve low impacts, and interactions throughout the supply chain. Producers have limits on how far they can reduce impacts. Most strikingly, impacts of the lowest-impact animal products typically exceed those of vegetable substitutes, providing new evidence for the importance of dietary change. Cumulatively, our findings support an approach where producers monitor their own impacts, flexibly meet environmental targets by choosing from multiple practices, and communicate their impacts to consumers."}}]])
    uploadBy: Actor = Field(..., description='The user who uploaded these data.', examples=[{'@id': 'actor-577', '@type': 'Actor', 'name': 'J. Poore, University of Oxford'}])
    uploadNotes: Optional[str] = Field(None, description='A free text field to describe the data upload, including any issues in the original data, assumptions made, or other important points.', examples=[])
    validationDate: Optional[date] = Field(None, description='The date the data was checked by an independent data validator ISO 8601 format (YYYY-MM-DD).', examples=[])
    validationBy: Optional[List[Actor]] = Field(None, description='The people/organizations who/which validated these data.', examples=[])
    intendedApplication: Optional[str] = Field(None, description='The intended application (see ISO 14044:2006).', examples=[])
    studyReasons: Optional[str] = Field(None, description='The reasons for carrying out the study (see ISO 14044:2006).', examples=[])
    intendedAudience: Optional[str] = Field(None, description='The intended audience i.e., to whom the results of the study are intended to be communicated (see ISO 14044:2006).', examples=[])
    comparativeAssertions: Optional[bool] = Field(None, description='Whether the results are intended to be used in comparative assertions (see ISO 14044:2006).', examples=[])
    sampleDesign: Optional[Term] = Field(None, description='The sample design, taken from the Glossary.', examples=[])
    weightingMethod: Optional[str] = Field(None, description='For sample designs involving weights, a description of the weights.', examples=[])
    experimentDesign: Optional[Term] = Field(None, description='The design of the experiment, taken from the Glossary.', examples=[])
    originalLicense: Optional[OriginalLicense] = Field(None, description='The public copyright license that the original version of these data were licensed under. Required for public uploads only.    CC0 is a Creative Commons license\n    that relinquishes copyright and releases the material into the public domain.\n\n    CC-BY is a Creative Commons license\n    allowing reuse as long as credit is given to the author of the material.\n\n    CC-BY-SA is a Creative Commons license\n    allowing reuse as long as credit is given to the author of the material and adaptations\n    of the material are shared under the same license terms.\n\n    CC-BY-NC is a Creative Commons license\n    allowing reuse for non-commercial purposes as long as credit is given to the author of the material.\n\n    CC-BY-NC-SA is a Creative Commons license\n    allowing reuse for non-commercial purposes as long as credit is given to the author of the material\n    and adaptations of the material are shared under the same license terms.\n\n    CC-BY-NC-ND is a Creative Commons license\n    allowing reuse for non-commercial purposes as long as credit is given to the author of the material\n    but preventing derivatives or adaptations of the material being made.\n\n    CC-BY-ND is a Creative Commons license\n    allowing reuse as long as credit is given to the author of the material\n    but preventing derivatives or adaptations of the material being made.\n\n    GNU-FDL is a GNU Project license\n    allowing reuse as long as adaptations of the material are shared under the same license terms.\n\n    other public license means the material is licensed under a license not listed above.\n\n    no public license means the material is under copyright by the original author or\n    publisher with no rights granted for public use beyond the exceptions to copyright in national law.\n', examples=['CC-BY'])
    dataPrivate: bool = Field(..., description='If these data are private. Private means that HESTIA administrators can access these data and you can grant access to other platform users, but these data will not be made available to any other users of the platform or distributed to third parties. If we find the Source on the Mendeley catalogue, the data in the Source node are public and we set this field to false.', examples=[])
    originalId: Optional[str] = Field(None, description='The identifier for these data in the source database (e.g., if the data were converted from openLCA or ecoinvent, the id field from that database).', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    createdAt: Optional[date] = Field(None, description='Date created on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=[])
    updatedAt: Optional[date] = Field(None, description='Last update date on HESTIA in ISO 8601 format (YYYY-MM-DD).', examples=['2020-02-14'])

class Emission(BaseModel):

    class Config:
        extra = Extra.forbid
    type: SchemaType = Field(validation_alias=AliasChoices('@type', 'type'), serialization_alias='@type', description='Type of the Node')
    term: Term = Field(..., description='A reference to the Term describing the Emission.', examples=[{'@id': 'no3ToGroundwaterSoilFlux', '@type': 'Term', 'name': 'NO3, to groundwater, soil flux', 'units': 'kg NO3', 'termType': 'emission'}, {'@id': 'so2ToAirInputsProduction', '@type': 'Term', 'name': 'SO2, to air, inputs production', 'units': 'kg SO2', 'termType': 'emission'}, {'@id': 'co2ToAirUreaHydrolysis', '@type': 'Term', 'name': 'CO2, to air, urea hydrolysis', 'units': 'kg CO2', 'termType': 'emission'}, {'@id': 'pesticideToWaterInputsProduction', '@type': 'Term', 'name': 'Pesticide, to water, inputs productions', 'units': 'kg active ingredient', 'termType': 'emission'}])
    description: Optional[str] = Field(None, description='A description of the Emission.', examples=[])
    key: Optional[Term] = Field(None, description='For certain emissions (Pesticide, to ..., Ionising compounds, to, and Heavy metals, to...) the element or compound that was emitted.', examples=[{'@id': 'CAS-1071-83-6', '@type': 'Term', 'name': 'Glyphosate', 'units': 'kg active ingredient', 'termType': 'pesticideAI'}])
    value: List[Optional[float]] = Field(..., description='The quantity of the Emission. If an average, it should always be the mean. Can be a single number (array of length one) or an array of numbers with associated dates (e.g., representing multiple measurements over time).', examples=[[60.75, 70.5], [2.11], [32], [0.00622]])
    distribution: Optional[List[Union[float, List[Any]]]] = Field(None, description='An array of up to 1000 random samples from the posterior distribution of valuedates field.', examples=[], max_items=1000)
    sd: Optional[List[Optional[confloat(ge=0.0)]]] = Field(None, description='The standard deviation of value.', examples=[], ge=0)
    min: Optional[List[Optional[float]]] = Field(None, description='The minimum of value.', examples=[])
    max: Optional[List[Optional[float]]] = Field(None, description='The maximum of value.', examples=[])
    statsDefinition: Optional[StatsDefinition] = Field(None, description='What the descriptive statistics (sd, min, max, and value) are calculated across, or whether they are simulated or the output of a model. spatial refers to descriptive statistics calculated across spatial units (e.g., pixels) within a region or country. time refers to descriptive statistics calculated across units of time (e.g., hours).', examples=[])
    observations: Optional[List[Optional[confloat(ge=1.0)]]] = Field(None, description='The number of observations the descriptive statistics are calculated over.', examples=[], ge=1)
    dates: Optional[List[Union[datetime.date, DateYear]]] = Field(None, description='A corresponding array to value, representing the dates of the Emissions in ISO 8601 format (YYYY-MM-DD, YYYY-MM, YYYY, --MM-DD, --MM, or YYYY-MM-DDTHH:mm:ssZ).', examples=[['1989-06-16', '1989-08-01']])
    startDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='For Emissions over periods, the start date of the Emission if different from the start date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    endDate: Optional[Union[datetime.date, DateYear]] = Field(None, description='For Emissions over periods, the end date of the Emission if different from the end date of the Cycle in ISO 8601 format (YYYY-MM-DD, YYYY-MM, or YYYY).', examples=[])
    emissionDuration: Optional[PositiveFloat] = Field(None, description='The duration of the Emissions in days, particularly used for measured Emissions.', examples=[])
    depth: Optional[confloat(ge=0.0, le=9999.0)] = Field(None, description='For soil Emissions, the depth at which the Emissions was recorded in centimeters.', examples=[])
    methodTier: MethodTier = Field(..., description='    background data refer to emissions which do not occur in the\n    current Cycle. They are either drawn from external, secondary, and often\n    aggregated datasets such as ecoinvent or are\n    drawn from a linked Impact Assessment.\n\n    measured refers to emissions which are quantified using physical\n    measurement. Terms to describe the measurement technique are contained in the\n    measurement glossary.\n\n    tier 1 models quantify emissions from activity data (i.e., data on\n    Inputs, Practices, etc.) using a simple equation with\n    parameters which are not country or region specific.\n\n    tier 2 models quantify emissions from activity data using a\n    simple equation, often of the same form as the tier 1 model, but with\n    geographically specific parameters.\n\n    tier 3 models quantify emissions from activity data but use\n    equations or algorithms that differ from tier 1 and\n    tier 2 approaches. These approaches include process based models\n    and statistical models with various forms.\n\n    not relevant means this emission is not relevant and in this case\n    value = 0.\n', examples=['measured', 'background', 'tier 1', 'background'])
    methodModel: Term = Field(..., description='A reference to the Term describing the method for measuring the Emission or the model used to calculate it.', examples=[{'@id': 'percolationLysimeter', '@type': 'Term', 'name': 'Percolation lysimeter', 'termType': 'methodEmissionResourceUse'}, {'@id': 'ecoinventV3', '@type': 'Term', 'name': 'ecoinvent v3', 'termType': 'model'}, {'@id': 'ipcc2006', '@type': 'Term', 'name': 'IPCC (2006)', 'termType': 'model'}, {'@id': 'usetoxV2', '@type': 'Term', 'name': 'USEtox v2', 'termType': 'model'}])
    methodModelDescription: Optional[str] = Field(None, description='A free text field, describing the method for measuring the Emission or the model used to calculate it.', examples=['version 3.1.2'])
    properties: Optional[List[Property]] = Field(None, description='A list of Properties of the Emission, which would override any default properties specified in the term.', examples=[])
    inputs: Optional[List[Term]] = Field(None, description='For background Emissions, the Term(s) describing the Inputs they are associated with. This is a required field for background Emissions.', examples=[[{'@id': 'electricityGridMarketMix', '@type': 'Term', 'name': 'Electricity, grid, market mix', 'termType': 'electricity'}], [{'@id': 'rapeseedSeedWhole', '@type': 'Term', 'name': 'Rapeseed, seed (whole)', 'termType': 'crop'}]])
    animals: Optional[List[Term]] = Field(None, description='For background Emissions, the Term(s) describing the Animal(s) they are associated with.', examples=[])
    transport: Optional[List[Term]] = Field(None, description='For Emissions created by transport, the Term(s) describing the transport.', examples=[])
    operation: Optional[Term] = Field(None, description='For Emissions created by an operation, the Term describing the operation.', examples=[])
    transformation: Optional[Term] = Field(None, description='For Emissions created during a Transformation, the Term describing the Transformation.', examples=[])
    site: Optional[Site] = Field(None, description='If the Cycle occurred on multiple Sites, the Site where this Emission occurred.', examples=[])
    country: Optional[Term] = Field(None, description='The country from the Glossary, following GADM naming conventions. This is for background emissions (emissions from inputs production) only.', examples=[{'@id': 'GADM-FRA', '@type': 'Term', 'name': 'France'}])
    source: Optional[Source] = Field(None, description='A reference to the Source of these data, if different from the defaultSource of the Cycle.', examples=[{'@id': 'yyu8v5', '@type': 'Source', 'name': 'Murwira (1993)'}, {'@id': 'yyu8v5', '@type': 'Source', 'name': 'Wernet et al (2016)'}])
    otherSources: Optional[List[Source]] = Field(None, description='A list of references to any other sources of these data.', examples=[])
    schemaVersion: Optional[str] = Field(None, description='The version of the schema when these data were created.', examples=[])
    added: Optional[List[str]] = Field(None, description='A list of fields that have been added to the original dataset.', examples=[])
    addedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to add these fields.', examples=[])
    updated: Optional[List[str]] = Field(None, description='A list of fields that have been updated on the original dataset.', examples=[])
    updatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the model used to update these fields.', examples=[])
    aggregated: Optional[List[str]] = Field(None, description="A list of fields that have been 'aggregated' using data from multiple Cycles.", examples=[])
    aggregatedVersion: Optional[List[str]] = Field(None, description='A list of versions of the aggregation engine corresponding to each aggregated field.', examples=[])
    deleted: Optional[bool] = Field(None, description='Indicates if this emission has been marked as deleted from the original dataset.', examples=[])