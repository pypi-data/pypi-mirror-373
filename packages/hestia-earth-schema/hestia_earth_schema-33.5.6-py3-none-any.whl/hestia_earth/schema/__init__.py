# auto-generated content
from collections import OrderedDict
from enum import Enum
from pkgutil import extend_path


__path__ = extend_path(__path__, __name__)
SCHEMA_VERSION = '33.5.6'
NESTED_SEARCHABLE_KEYS = [
    'inputs',
    'practices',
    'otherSites',
    'animals',
    'products',
    'transformations',
    'emissions',
    'emissionsResourceUse',
    'impacts',
    'endpoints',
    'measurements',
    'management',
    'metaAnalyses',
    'subClassOf',
    'defaultProperties'
]


class NodeType(Enum):
    ACTOR = 'Actor'
    CYCLE = 'Cycle'
    IMPACTASSESSMENT = 'ImpactAssessment'
    ORGANISATION = 'Organisation'
    SITE = 'Site'
    SOURCE = 'Source'
    TERM = 'Term'


class SchemaType(Enum):
    ACTOR = 'Actor'
    ANIMAL = 'Animal'
    BIBLIOGRAPHY = 'Bibliography'
    COMPLETENESS = 'Completeness'
    CYCLE = 'Cycle'
    EMISSION = 'Emission'
    IMPACTASSESSMENT = 'ImpactAssessment'
    INDICATOR = 'Indicator'
    INFRASTRUCTURE = 'Infrastructure'
    INPUT = 'Input'
    MANAGEMENT = 'Management'
    MEASUREMENT = 'Measurement'
    ORGANISATION = 'Organisation'
    PRACTICE = 'Practice'
    PRODUCT = 'Product'
    PROPERTY = 'Property'
    SITE = 'Site'
    SOURCE = 'Source'
    TERM = 'Term'
    TRANSFORMATION = 'Transformation'
    TRANSPORT = 'Transport'


NODE_TYPES = [e.value for e in NodeType]
SCHEMA_TYPES = [e.value for e in SchemaType]


def is_node_type(type: str): return type in NODE_TYPES


def is_type_valid(type: str): return type in SCHEMA_TYPES


def is_schema_type(type: str): return is_type_valid(type) and not is_node_type(type)


class Actor:
    def __init__(self):
        self.required = [
            'lastName',
            'dataPrivate'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = NodeType.ACTOR.value
        self.fields['name'] = ''
        self.fields['firstName'] = ''
        self.fields['lastName'] = ''
        self.fields['orcid'] = ''
        self.fields['scopusID'] = ''
        self.fields['primaryInstitution'] = ''
        self.fields['city'] = ''
        self.fields['country'] = None
        self.fields['email'] = ''
        self.fields['website'] = None
        self.fields['dataPrivate'] = False
        self.fields['originalId'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class AnimalReferencePeriod(Enum):
    AVERAGE = 'average'
    END_OF_CYCLE = 'end of Cycle'
    START_OF_CYCLE = 'start of Cycle'


class AnimalStatsDefinition(Enum):
    ANIMALS = 'animals'
    CYCLES = 'cycles'
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SITES = 'sites'
    SPATIAL = 'spatial'
    TIME = 'time'


class AnimalMethodClassification(Enum):
    CONSISTENT_EXTERNAL_SOURCES = 'consistent external sources'
    ESTIMATED_WITH_ASSUMPTIONS = 'estimated with assumptions'
    EXPERT_OPINION = 'expert opinion'
    INCONSISTENT_EXTERNAL_SOURCES = 'inconsistent external sources'
    MODELLED = 'modelled'
    NON_VERIFIED_SURVEY_DATA = 'non-verified survey data'
    PHYSICAL_MEASUREMENT = 'physical measurement'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'
    VERIFIED_SURVEY_DATA = 'verified survey data'


class Animal:
    def __init__(self):
        self.required = [
            'animalId',
            'term',
            'referencePeriod'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.ANIMAL.value
        self.fields['animalId'] = ''
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['referencePeriod'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['price'] = None
        self.fields['currency'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['inputs'] = []
        self.fields['practices'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class Bibliography:
    def __init__(self):
        self.required = [
            'name',
            'title',
            'authors',
            'outlet',
            'year'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.BIBLIOGRAPHY.value
        self.fields['name'] = ''
        self.fields['documentDOI'] = ''
        self.fields['title'] = ''
        self.fields['arxivID'] = ''
        self.fields['scopus'] = ''
        self.fields['mendeleyID'] = ''
        self.fields['authors'] = []
        self.fields['outlet'] = ''
        self.fields['year'] = None
        self.fields['volume'] = None
        self.fields['issue'] = ''
        self.fields['chapter'] = ''
        self.fields['pages'] = ''
        self.fields['publisher'] = ''
        self.fields['city'] = ''
        self.fields['editors'] = []
        self.fields['institutionPub'] = []
        self.fields['websites'] = None
        self.fields['articlePdf'] = ''
        self.fields['dateAccessed'] = None
        self.fields['abstract'] = ''
        self.fields['schemaVersion'] = ''

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class Completeness:
    def __init__(self):
        self.required = [
            'animalFeed',
            'animalPopulation',
            'cropResidue',
            'electricityFuel',
            'excreta',
            'fertiliser',
            'freshForage',
            'ingredient',
            'liveAnimalInput',
            'material',
            'operation',
            'otherChemical',
            'pesticideVeterinaryDrug',
            'product',
            'seed',
            'soilAmendment',
            'transport',
            'waste',
            'water'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.COMPLETENESS.value
        self.fields['animalFeed'] = False
        self.fields['animalPopulation'] = False
        self.fields['cropResidue'] = False
        self.fields['electricityFuel'] = False
        self.fields['excreta'] = False
        self.fields['fertiliser'] = False
        self.fields['freshForage'] = False
        self.fields['ingredient'] = False
        self.fields['liveAnimalInput'] = False
        self.fields['material'] = False
        self.fields['operation'] = False
        self.fields['otherChemical'] = False
        self.fields['pesticideVeterinaryDrug'] = False
        self.fields['product'] = False
        self.fields['seed'] = False
        self.fields['soilAmendment'] = False
        self.fields['transport'] = False
        self.fields['waste'] = False
        self.fields['water'] = False
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class CycleFunctionalUnit(Enum):
    _1_HA = '1 ha'
    RELATIVE = 'relative'


class CycleStartDateDefinition(Enum):
    FIRST_BEARING_YEAR = 'first bearing year'
    HARVEST_OF_PREVIOUS_CROP = 'harvest of previous crop'
    ONE_YEAR_PRIOR = 'one year prior'
    ORCHARD_OR_VINEYARD_ESTABLISHMENT_DATE = 'orchard or vineyard establishment date'
    SOIL_PREPARATION_DATE = 'soil preparation date'
    SOWING_DATE = 'sowing date'
    START_OF_ANIMAL_LIFE = 'start of animal life'
    START_OF_WILD_HARVEST_PERIOD = 'start of wild harvest period'
    START_OF_YEAR = 'start of year'
    STOCKING_DATE = 'stocking date'
    TRANSPLANTING_DATE = 'transplanting date'


class CycleDefaultMethodClassification(Enum):
    CONSISTENT_EXTERNAL_SOURCES = 'consistent external sources'
    ESTIMATED_WITH_ASSUMPTIONS = 'estimated with assumptions'
    EXPERT_OPINION = 'expert opinion'
    INCONSISTENT_EXTERNAL_SOURCES = 'inconsistent external sources'
    MODELLED = 'modelled'
    NON_VERIFIED_SURVEY_DATA = 'non-verified survey data'
    PHYSICAL_MEASUREMENT = 'physical measurement'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'
    VERIFIED_SURVEY_DATA = 'verified survey data'


class Cycle:
    def __init__(self):
        self.required = [
            'functionalUnit',
            'endDate',
            'site',
            'defaultMethodClassification',
            'defaultMethodClassificationDescription',
            'completeness',
            'dataPrivate'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = NodeType.CYCLE.value
        self.fields['name'] = ''
        self.fields['description'] = ''
        self.fields['functionalUnit'] = ''
        self.fields['functionalUnitDetails'] = ''
        self.fields['endDate'] = ''
        self.fields['startDate'] = ''
        self.fields['startDateDefinition'] = ''
        self.fields['cycleDuration'] = None
        self.fields['site'] = None
        self.fields['otherSites'] = []
        self.fields['siteDuration'] = None
        self.fields['otherSitesDuration'] = None
        self.fields['siteUnusedDuration'] = None
        self.fields['otherSitesUnusedDuration'] = None
        self.fields['siteArea'] = None
        self.fields['otherSitesArea'] = None
        self.fields['harvestedArea'] = None
        self.fields['numberOfCycles'] = None
        self.fields['treatment'] = ''
        self.fields['commercialPracticeTreatment'] = False
        self.fields['numberOfReplications'] = None
        self.fields['sampleWeight'] = None
        self.fields['defaultMethodClassification'] = ''
        self.fields['defaultMethodClassificationDescription'] = ''
        self.fields['defaultSource'] = None
        self.fields['completeness'] = None
        self.fields['practices'] = []
        self.fields['animals'] = []
        self.fields['inputs'] = []
        self.fields['products'] = []
        self.fields['transformations'] = []
        self.fields['emissions'] = []
        self.fields['dataPrivate'] = False
        self.fields['originalId'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = False
        self.fields['aggregatedDataValidated'] = False
        self.fields['aggregatedVersion'] = ''
        self.fields['aggregatedQualityScore'] = None
        self.fields['aggregatedQualityScoreMax'] = None
        self.fields['aggregatedCycles'] = []
        self.fields['aggregatedSources'] = []
        self.fields['covarianceMatrixIds'] = None
        self.fields['covarianceMatrix'] = None
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class EmissionStatsDefinition(Enum):
    ANIMALS = 'animals'
    CYCLES = 'cycles'
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SITES = 'sites'
    SPATIAL = 'spatial'
    TIME = 'time'


class EmissionMethodTier(Enum):
    BACKGROUND = 'background'
    MEASURED = 'measured'
    NOT_RELEVANT = 'not relevant'
    TIER_1 = 'tier 1'
    TIER_2 = 'tier 2'
    TIER_3 = 'tier 3'


class Emission:
    def __init__(self):
        self.required = [
            'term',
            'value',
            'methodTier',
            'methodModel'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.EMISSION.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['key'] = None
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['dates'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['emissionDuration'] = None
        self.fields['depth'] = None
        self.fields['methodTier'] = ''
        self.fields['methodModel'] = None
        self.fields['methodModelDescription'] = ''
        self.fields['properties'] = []
        self.fields['inputs'] = []
        self.fields['animals'] = []
        self.fields['transport'] = []
        self.fields['operation'] = None
        self.fields['transformation'] = None
        self.fields['site'] = None
        self.fields['country'] = None
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None
        self.fields['deleted'] = False

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class ImpactAssessmentAllocationMethod(Enum):
    BIOPHYSICAL = 'biophysical'
    ECONOMIC = 'economic'
    ENERGY = 'energy'
    MASS = 'mass'
    NONE = 'none'
    NONE_REQUIRED = 'none required'
    SYSTEM_EXPANSION = 'system expansion'


class ImpactAssessment:
    def __init__(self):
        self.required = [
            'product',
            'functionalUnitQuantity',
            'allocationMethod',
            'endDate',
            'country',
            'dataPrivate'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = NodeType.IMPACTASSESSMENT.value
        self.fields['name'] = ''
        self.fields['version'] = ''
        self.fields['versionDetails'] = ''
        self.fields['cycle'] = None
        self.fields['product'] = None
        self.fields['functionalUnitQuantity'] = 1
        self.fields['allocationMethod'] = ''
        self.fields['endDate'] = ''
        self.fields['startDate'] = ''
        self.fields['site'] = None
        self.fields['country'] = None
        self.fields['region'] = None
        self.fields['organisation'] = None
        self.fields['source'] = None
        self.fields['emissionsResourceUse'] = []
        self.fields['impacts'] = []
        self.fields['endpoints'] = []
        self.fields['dataPrivate'] = False
        self.fields['organic'] = False
        self.fields['irrigated'] = False
        self.fields['autoGenerated'] = False
        self.fields['originalId'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = False
        self.fields['aggregatedDataValidated'] = False
        self.fields['aggregatedVersion'] = ''
        self.fields['aggregatedQualityScore'] = None
        self.fields['aggregatedQualityScoreMax'] = None
        self.fields['aggregatedImpactAssessments'] = []
        self.fields['aggregatedSources'] = []
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class IndicatorStatsDefinition(Enum):
    ANIMALS = 'animals'
    CYCLES = 'cycles'
    IMPACTASSESSMENTS = 'impactAssessments'
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SITES = 'sites'
    SPATIAL = 'spatial'
    TIME = 'time'


class IndicatorMethodTier(Enum):
    BACKGROUND = 'background'
    MEASURED = 'measured'
    NOT_RELEVANT = 'not relevant'
    TIER_1 = 'tier 1'
    TIER_2 = 'tier 2'
    TIER_3 = 'tier 3'


class Indicator:
    def __init__(self):
        self.required = [
            'term',
            'value',
            'methodModel'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.INDICATOR.value
        self.fields['term'] = None
        self.fields['key'] = None
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['methodTier'] = ''
        self.fields['methodModel'] = None
        self.fields['methodModelDescription'] = ''
        self.fields['inputs'] = []
        self.fields['animals'] = []
        self.fields['country'] = None
        self.fields['operation'] = None
        self.fields['landCover'] = None
        self.fields['previousLandCover'] = None
        self.fields['transformation'] = None
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class InfrastructureOwnershipStatus(Enum):
    BORROWED = 'borrowed'
    OWNED = 'owned'
    RENTED = 'rented'


class InfrastructureMethodClassification(Enum):
    CONSISTENT_EXTERNAL_SOURCES = 'consistent external sources'
    ESTIMATED_WITH_ASSUMPTIONS = 'estimated with assumptions'
    EXPERT_OPINION = 'expert opinion'
    INCONSISTENT_EXTERNAL_SOURCES = 'inconsistent external sources'
    MODELLED = 'modelled'
    NON_VERIFIED_SURVEY_DATA = 'non-verified survey data'
    PHYSICAL_MEASUREMENT = 'physical measurement'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'
    VERIFIED_SURVEY_DATA = 'verified survey data'


class Infrastructure:
    def __init__(self):
        self.required = [
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.INFRASTRUCTURE.value
        self.fields['term'] = None
        self.fields['name'] = ''
        self.fields['description'] = ''
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['defaultLifespan'] = None
        self.fields['defaultLifespanHours'] = None
        self.fields['mass'] = None
        self.fields['area'] = None
        self.fields['ownershipStatus'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['source'] = None
        self.fields['impactAssessment'] = None
        self.fields['inputs'] = []
        self.fields['transport'] = []
        self.fields['schemaVersion'] = ''

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class InputStatsDefinition(Enum):
    ANIMALS = 'animals'
    CYCLES = 'cycles'
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SITES = 'sites'
    SPATIAL = 'spatial'
    TIME = 'time'


class InputMethodClassification(Enum):
    CONSISTENT_EXTERNAL_SOURCES = 'consistent external sources'
    ESTIMATED_WITH_ASSUMPTIONS = 'estimated with assumptions'
    EXPERT_OPINION = 'expert opinion'
    INCONSISTENT_EXTERNAL_SOURCES = 'inconsistent external sources'
    MODELLED = 'modelled'
    NON_VERIFIED_SURVEY_DATA = 'non-verified survey data'
    PHYSICAL_MEASUREMENT = 'physical measurement'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'
    VERIFIED_SURVEY_DATA = 'verified survey data'


class InputPriceStatsDefinition(Enum):
    CYCLES = 'cycles'
    CYCLES_AND_TIME = 'cycles and time'
    TIME = 'time'


class InputCostStatsDefinition(Enum):
    CYCLES = 'cycles'
    CYCLES_AND_TIME = 'cycles and time'
    TIME = 'time'


class Input:
    def __init__(self):
        self.required = [
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.INPUT.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['dates'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['inputDuration'] = None
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['model'] = None
        self.fields['modelDescription'] = ''
        self.fields['isAnimalFeed'] = False
        self.fields['fromCycle'] = False
        self.fields['producedInCycle'] = False
        self.fields['price'] = None
        self.fields['priceSd'] = None
        self.fields['priceMin'] = None
        self.fields['priceMax'] = None
        self.fields['priceStatsDefinition'] = ''
        self.fields['cost'] = None
        self.fields['costSd'] = None
        self.fields['costMin'] = None
        self.fields['costMax'] = None
        self.fields['costStatsDefinition'] = ''
        self.fields['currency'] = ''
        self.fields['lifespan'] = None
        self.fields['operation'] = None
        self.fields['country'] = None
        self.fields['region'] = None
        self.fields['impactAssessment'] = None
        self.fields['impactAssessmentIsProxy'] = False
        self.fields['site'] = None
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['transport'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class ManagementStatsDefinition(Enum):
    ANIMALS = 'animals'
    CYCLES = 'cycles'
    IMPACTASSESSMENTS = 'impactAssessments'
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SITES = 'sites'
    SPATIAL = 'spatial'
    TIME = 'time'


class ManagementMethodClassification(Enum):
    CONSISTENT_EXTERNAL_SOURCES = 'consistent external sources'
    ESTIMATED_WITH_ASSUMPTIONS = 'estimated with assumptions'
    EXPERT_OPINION = 'expert opinion'
    INCONSISTENT_EXTERNAL_SOURCES = 'inconsistent external sources'
    MODELLED = 'modelled'
    NON_VERIFIED_SURVEY_DATA = 'non-verified survey data'
    PHYSICAL_MEASUREMENT = 'physical measurement'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'
    VERIFIED_SURVEY_DATA = 'verified survey data'


class Management:
    def __init__(self):
        self.required = [
            'term',
            'endDate'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.MANAGEMENT.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['model'] = None
        self.fields['modelDescription'] = ''
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class MeasurementStatsDefinition(Enum):
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SITES = 'sites'
    SPATIAL = 'spatial'
    TIME = 'time'


class MeasurementMethodClassification(Enum):
    COUNTRY_LEVEL_STATISTICAL_DATA = 'country-level statistical data'
    EXPERT_OPINION = 'expert opinion'
    GEOSPATIAL_DATASET = 'geospatial dataset'
    MODELLED_USING_OTHER_MEASUREMENTS = 'modelled using other measurements'
    ON_SITE_PHYSICAL_MEASUREMENT = 'on-site physical measurement'
    PHYSICAL_MEASUREMENT_ON_NEARBY_SITE = 'physical measurement on nearby site'
    REGIONAL_STATISTICAL_DATA = 'regional statistical data'
    TIER_1_MODEL = 'tier 1 model'
    TIER_2_MODEL = 'tier 2 model'
    TIER_3_MODEL = 'tier 3 model'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'


class Measurement:
    def __init__(self):
        self.required = [
            'term',
            'methodClassification'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.MEASUREMENT.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['dates'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['measurementDuration'] = None
        self.fields['depthUpper'] = None
        self.fields['depthLower'] = None
        self.fields['latitude'] = None
        self.fields['longitude'] = None
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['method'] = None
        self.fields['methodDescription'] = ''
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class Organisation:
    def __init__(self):
        self.required = [
            'country',
            'dataPrivate',
            'uploadBy'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = NodeType.ORGANISATION.value
        self.fields['name'] = ''
        self.fields['description'] = ''
        self.fields['boundary'] = None
        self.fields['boundaryArea'] = None
        self.fields['area'] = None
        self.fields['latitude'] = None
        self.fields['longitude'] = None
        self.fields['streetAddress'] = ''
        self.fields['city'] = ''
        self.fields['region'] = None
        self.fields['country'] = None
        self.fields['postOfficeBoxNumber'] = ''
        self.fields['postalCode'] = ''
        self.fields['website'] = None
        self.fields['glnNumber'] = ''
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['infrastructure'] = []
        self.fields['dataPrivate'] = False
        self.fields['originalId'] = ''
        self.fields['uploadBy'] = None
        self.fields['schemaVersion'] = ''
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class PracticeStatsDefinition(Enum):
    ANIMALS = 'animals'
    CYCLES = 'cycles'
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SITES = 'sites'
    SPATIAL = 'spatial'
    TIME = 'time'


class PracticeMethodClassification(Enum):
    CONSISTENT_EXTERNAL_SOURCES = 'consistent external sources'
    ESTIMATED_WITH_ASSUMPTIONS = 'estimated with assumptions'
    EXPERT_OPINION = 'expert opinion'
    INCONSISTENT_EXTERNAL_SOURCES = 'inconsistent external sources'
    MODELLED = 'modelled'
    NON_VERIFIED_SURVEY_DATA = 'non-verified survey data'
    PHYSICAL_MEASUREMENT = 'physical measurement'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'
    VERIFIED_SURVEY_DATA = 'verified survey data'


class PracticePriceStatsDefinition(Enum):
    CYCLES = 'cycles'
    CYCLES_AND_TIME = 'cycles and time'
    TIME = 'time'


class PracticeCostStatsDefinition(Enum):
    CYCLES = 'cycles'
    CYCLES_AND_TIME = 'cycles and time'
    TIME = 'time'


class PracticeOwnershipStatus(Enum):
    BORROWED = 'borrowed'
    OWNED = 'owned'
    RENTED = 'rented'


class Practice:
    def __init__(self):
        self.required = [
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.PRACTICE.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['variety'] = ''
        self.fields['key'] = None
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['dates'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['model'] = None
        self.fields['modelDescription'] = ''
        self.fields['areaPercent'] = None
        self.fields['price'] = None
        self.fields['priceSd'] = None
        self.fields['priceMin'] = None
        self.fields['priceMax'] = None
        self.fields['priceStatsDefinition'] = ''
        self.fields['cost'] = None
        self.fields['costSd'] = None
        self.fields['costMin'] = None
        self.fields['costMax'] = None
        self.fields['costStatsDefinition'] = ''
        self.fields['currency'] = ''
        self.fields['ownershipStatus'] = ''
        self.fields['primaryPercent'] = None
        self.fields['site'] = None
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class ProductStatsDefinition(Enum):
    ANIMALS = 'animals'
    CYCLES = 'cycles'
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SITES = 'sites'
    SPATIAL = 'spatial'
    TIME = 'time'


class ProductMethodClassification(Enum):
    CONSISTENT_EXTERNAL_SOURCES = 'consistent external sources'
    ESTIMATED_WITH_ASSUMPTIONS = 'estimated with assumptions'
    EXPERT_OPINION = 'expert opinion'
    INCONSISTENT_EXTERNAL_SOURCES = 'inconsistent external sources'
    MODELLED = 'modelled'
    NON_VERIFIED_SURVEY_DATA = 'non-verified survey data'
    PHYSICAL_MEASUREMENT = 'physical measurement'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'
    VERIFIED_SURVEY_DATA = 'verified survey data'


class ProductFate(Enum):
    ANAEROBIC_DIGESTION = 'anaerobic digestion'
    BEDDING = 'bedding'
    BREEDING = 'breeding'
    BURNT = 'burnt'
    BURNT_FOR_FUEL = 'burnt for fuel'
    COMPOSTED = 'composted'
    FODDER = 'fodder'
    HOME_CONSUMPTION = 'home consumption'
    PROCESSING = 'processing'
    SAVED_FOR_SEEDS = 'saved for seeds'
    SOLD = 'sold'
    SOLD_FOR_BREEDING = 'sold for breeding'
    SOLD_FOR_FATTENING = 'sold for fattening'
    SOLD_FOR_SLAUGHTER = 'sold for slaughter'
    SOLD_TO_DOMESTIC_MARKET = 'sold to domestic market'
    SOLD_TO_EXPORT_MARKET = 'sold to export market'
    USED_AS_FERTILISER = 'used as fertiliser'
    USED_AS_MULCH = 'used as mulch'
    USED_AS_SOIL_AMENDMENT = 'used as soil amendment'


class ProductPriceStatsDefinition(Enum):
    CYCLES = 'cycles'
    CYCLES_AND_TIME = 'cycles and time'
    TIME = 'time'


class ProductRevenueStatsDefinition(Enum):
    CYCLES = 'cycles'
    CYCLES_AND_TIME = 'cycles and time'
    TIME = 'time'


class Product:
    def __init__(self):
        self.required = [
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.PRODUCT.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['variety'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['dates'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['model'] = None
        self.fields['modelDescription'] = ''
        self.fields['fate'] = ''
        self.fields['price'] = None
        self.fields['priceSd'] = None
        self.fields['priceMin'] = None
        self.fields['priceMax'] = None
        self.fields['priceStatsDefinition'] = ''
        self.fields['revenue'] = None
        self.fields['revenueSd'] = None
        self.fields['revenueMin'] = None
        self.fields['revenueMax'] = None
        self.fields['revenueStatsDefinition'] = ''
        self.fields['currency'] = ''
        self.fields['economicValueShare'] = None
        self.fields['primary'] = False
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['transport'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class PropertyStatsDefinition(Enum):
    CYCLES = 'cycles'
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SITES = 'sites'
    SPATIAL = 'spatial'
    TIME = 'time'


class PropertyMethodClassification(Enum):
    CONSISTENT_EXTERNAL_SOURCES = 'consistent external sources'
    ESTIMATED_WITH_ASSUMPTIONS = 'estimated with assumptions'
    EXPERT_OPINION = 'expert opinion'
    INCONSISTENT_EXTERNAL_SOURCES = 'inconsistent external sources'
    MODELLED = 'modelled'
    NON_VERIFIED_SURVEY_DATA = 'non-verified survey data'
    PHYSICAL_MEASUREMENT = 'physical measurement'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'
    VERIFIED_SURVEY_DATA = 'verified survey data'


class PropertyDataState(Enum):
    COMPLETE = 'complete'
    MISSING = 'missing'
    NOT_REQUIRED = 'not required'
    REQUIRES_VALIDATION = 'requires validation'
    UNASSIGNED = 'unassigned'


class Property:
    def __init__(self):
        self.required = [
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.PROPERTY.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['key'] = None
        self.fields['value'] = None
        self.fields['share'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['date'] = ''
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['methodModel'] = None
        self.fields['methodModelDescription'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['source'] = None
        self.fields['dataState'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class SiteSiteType(Enum):
    AGRI_FOOD_PROCESSOR = 'agri-food processor'
    ANIMAL_HOUSING = 'animal housing'
    CROPLAND = 'cropland'
    FOOD_RETAILER = 'food retailer'
    FOREST = 'forest'
    GLASS_OR_HIGH_ACCESSIBLE_COVER = 'glass or high accessible cover'
    LAKE = 'lake'
    OTHER_NATURAL_VEGETATION = 'other natural vegetation'
    PERMANENT_PASTURE = 'permanent pasture'
    POND = 'pond'
    RIVER_OR_STREAM = 'river or stream'
    SEA_OR_OCEAN = 'sea or ocean'


class SiteTenure(Enum):
    FARMING_ON_COMMON_LAND = 'farming on common land'
    FARMING_ON_OWNED_LAND = 'farming on owned land'
    FARMING_ON_RENTED_LAND = 'farming on rented land'
    OTHER_TENURE_MODEL = 'other tenure model'
    SHARE_FARMING = 'share farming'


class SiteDefaultMethodClassification(Enum):
    CONSISTENT_EXTERNAL_SOURCES = 'consistent external sources'
    ESTIMATED_WITH_ASSUMPTIONS = 'estimated with assumptions'
    EXPERT_OPINION = 'expert opinion'
    INCONSISTENT_EXTERNAL_SOURCES = 'inconsistent external sources'
    MODELLED = 'modelled'
    NON_VERIFIED_SURVEY_DATA = 'non-verified survey data'
    PHYSICAL_MEASUREMENT = 'physical measurement'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'
    VERIFIED_SURVEY_DATA = 'verified survey data'


class Site:
    def __init__(self):
        self.required = [
            'siteType',
            'country',
            'dataPrivate'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = NodeType.SITE.value
        self.fields['name'] = ''
        self.fields['description'] = ''
        self.fields['organisation'] = None
        self.fields['siteType'] = ''
        self.fields['tenure'] = ''
        self.fields['numberOfSites'] = None
        self.fields['boundary'] = None
        self.fields['area'] = None
        self.fields['areaSd'] = None
        self.fields['areaMin'] = None
        self.fields['areaMax'] = None
        self.fields['latitude'] = None
        self.fields['longitude'] = None
        self.fields['country'] = None
        self.fields['region'] = None
        self.fields['glnNumber'] = ''
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['defaultMethodClassification'] = ''
        self.fields['defaultMethodClassificationDescription'] = ''
        self.fields['defaultSource'] = None
        self.fields['measurements'] = []
        self.fields['management'] = []
        self.fields['infrastructure'] = []
        self.fields['dataPrivate'] = False
        self.fields['boundaryArea'] = None
        self.fields['ecoregion'] = ''
        self.fields['awareWaterBasinId'] = ''
        self.fields['originalId'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = False
        self.fields['aggregatedDataValidated'] = False
        self.fields['aggregatedVersion'] = ''
        self.fields['aggregatedSites'] = []
        self.fields['aggregatedSources'] = []
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class SourceOriginalLicense(Enum):
    CC_BY = 'CC-BY'
    CC_BY_NC = 'CC-BY-NC'
    CC_BY_NC_ND = 'CC-BY-NC-ND'
    CC_BY_NC_SA = 'CC-BY-NC-SA'
    CC_BY_ND = 'CC-BY-ND'
    CC_BY_SA = 'CC-BY-SA'
    CC0 = 'CC0'
    GNU_FDL = 'GNU-FDL'
    NO_PUBLIC_LICENSE = 'no public license'
    OTHER_PUBLIC_LICENSE = 'other public license'


class Source:
    def __init__(self):
        self.required = [
            'name',
            'bibliography',
            'uploadBy',
            'dataPrivate'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = NodeType.SOURCE.value
        self.fields['name'] = ''
        self.fields['bibliography'] = None
        self.fields['metaAnalyses'] = []
        self.fields['uploadBy'] = None
        self.fields['uploadNotes'] = ''
        self.fields['validationDate'] = None
        self.fields['validationBy'] = []
        self.fields['intendedApplication'] = ''
        self.fields['studyReasons'] = ''
        self.fields['intendedAudience'] = ''
        self.fields['comparativeAssertions'] = False
        self.fields['sampleDesign'] = None
        self.fields['weightingMethod'] = ''
        self.fields['experimentDesign'] = None
        self.fields['originalLicense'] = ''
        self.fields['dataPrivate'] = False
        self.fields['originalId'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class TermTermType(Enum):
    ANIMALBREED = 'animalBreed'
    ANIMALMANAGEMENT = 'animalManagement'
    ANIMALPRODUCT = 'animalProduct'
    AQUACULTUREMANAGEMENT = 'aquacultureManagement'
    BIOCHAR = 'biochar'
    BIOLOGICALCONTROLAGENT = 'biologicalControlAgent'
    BUILDING = 'building'
    CHARACTERISEDINDICATOR = 'characterisedIndicator'
    CROP = 'crop'
    CROPESTABLISHMENT = 'cropEstablishment'
    CROPRESIDUE = 'cropResidue'
    CROPRESIDUEMANAGEMENT = 'cropResidueManagement'
    CROPSUPPORT = 'cropSupport'
    ELECTRICITY = 'electricity'
    EMISSION = 'emission'
    ENDPOINTINDICATOR = 'endpointIndicator'
    EXCRETA = 'excreta'
    EXCRETAMANAGEMENT = 'excretaManagement'
    EXPERIMENTDESIGN = 'experimentDesign'
    FEEDFOODADDITIVE = 'feedFoodAdditive'
    FERTILISERBRANDNAME = 'fertiliserBrandName'
    FORAGE = 'forage'
    FUEL = 'fuel'
    INORGANICFERTILISER = 'inorganicFertiliser'
    IRRIGATION = 'irrigation'
    LANDCOVER = 'landCover'
    LANDUSEMANAGEMENT = 'landUseManagement'
    LIVEANIMAL = 'liveAnimal'
    LIVEAQUATICSPECIES = 'liveAquaticSpecies'
    MACHINERY = 'machinery'
    MATERIAL = 'material'
    MEASUREMENT = 'measurement'
    METHODEMISSIONRESOURCEUSE = 'methodEmissionResourceUse'
    METHODMEASUREMENT = 'methodMeasurement'
    MODEL = 'model'
    OPERATION = 'operation'
    ORGANICFERTILISER = 'organicFertiliser'
    OTHERINORGANICCHEMICAL = 'otherInorganicChemical'
    OTHERORGANICCHEMICAL = 'otherOrganicChemical'
    PASTUREMANAGEMENT = 'pastureManagement'
    PESTICIDEAI = 'pesticideAI'
    PESTICIDEBRANDNAME = 'pesticideBrandName'
    PROCESSEDFOOD = 'processedFood'
    PROCESSINGAID = 'processingAid'
    PROPERTY = 'property'
    REGION = 'region'
    RESOURCEUSE = 'resourceUse'
    SAMPLEDESIGN = 'sampleDesign'
    SEED = 'seed'
    SOILAMENDMENT = 'soilAmendment'
    SOILTEXTURE = 'soilTexture'
    SOILTYPE = 'soilType'
    STANDARDSLABELS = 'standardsLabels'
    SUBSTRATE = 'substrate'
    SYSTEM = 'system'
    TILLAGE = 'tillage'
    TRANSPORT = 'transport'
    USDASOILTYPE = 'usdaSoilType'
    VETERINARYDRUG = 'veterinaryDrug'
    WASTE = 'waste'
    WASTEMANAGEMENT = 'wasteManagement'
    WATER = 'water'
    WATERREGIME = 'waterRegime'


class Term:
    def __init__(self):
        self.required = [
            'name',
            'termType'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = NodeType.TERM.value
        self.fields['name'] = ''
        self.fields['synonyms'] = None
        self.fields['definition'] = ''
        self.fields['description'] = ''
        self.fields['units'] = ''
        self.fields['unitsDescription'] = ''
        self.fields['subClassOf'] = []
        self.fields['defaultProperties'] = []
        self.fields['casNumber'] = ''
        self.fields['ecoinventReferenceProductId'] = None
        self.fields['fishstatName'] = ''
        self.fields['hsCode'] = ''
        self.fields['iccCode'] = None
        self.fields['iso31662Code'] = ''
        self.fields['gadmFullName'] = ''
        self.fields['gadmId'] = ''
        self.fields['gadmLevel'] = None
        self.fields['gadmName'] = ''
        self.fields['gadmCountry'] = ''
        self.fields['gtin'] = ''
        self.fields['canonicalSmiles'] = ''
        self.fields['latitude'] = None
        self.fields['longitude'] = None
        self.fields['area'] = None
        self.fields['openLCAId'] = ''
        self.fields['scientificName'] = ''
        self.fields['website'] = None
        self.fields['agrovoc'] = None
        self.fields['aquastatSpeciesFactSheet'] = None
        self.fields['cornellBiologicalControl'] = None
        self.fields['ecolabelIndex'] = None
        self.fields['feedipedia'] = None
        self.fields['fishbase'] = None
        self.fields['pubchem'] = None
        self.fields['wikipedia'] = None
        self.fields['termType'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class Transformation:
    def __init__(self):
        self.required = [
            'transformationId',
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.TRANSFORMATION.value
        self.fields['transformationId'] = ''
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['transformationDuration'] = None
        self.fields['previousTransformationId'] = ''
        self.fields['transformedShare'] = None
        self.fields['site'] = None
        self.fields['inputs'] = []
        self.fields['emissions'] = []
        self.fields['products'] = []
        self.fields['practices'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class TransportStatsDefinition(Enum):
    CYCLES = 'cycles'
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SPATIAL = 'spatial'


class TransportDistanceStatsDefinition(Enum):
    CYCLES = 'cycles'
    MODELLED = 'modelled'
    OTHER_OBSERVATIONS = 'other observations'
    REGIONS = 'regions'
    REPLICATIONS = 'replications'
    SIMULATED = 'simulated'
    SPATIAL = 'spatial'
    TIME = 'time'


class TransportMethodClassification(Enum):
    CONSISTENT_EXTERNAL_SOURCES = 'consistent external sources'
    ESTIMATED_WITH_ASSUMPTIONS = 'estimated with assumptions'
    EXPERT_OPINION = 'expert opinion'
    INCONSISTENT_EXTERNAL_SOURCES = 'inconsistent external sources'
    MODELLED = 'modelled'
    NON_VERIFIED_SURVEY_DATA = 'non-verified survey data'
    PHYSICAL_MEASUREMENT = 'physical measurement'
    UNSOURCED_ASSUMPTION = 'unsourced assumption'
    VERIFIED_SURVEY_DATA = 'verified survey data'


class Transport:
    def __init__(self):
        self.required = [
            'term',
            'returnLegIncluded'
        ]
        self.fields = OrderedDict()
        self.fields['type'] = SchemaType.TRANSPORT.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['distance'] = None
        self.fields['distanceSd'] = None
        self.fields['distanceMin'] = None
        self.fields['distanceMax'] = None
        self.fields['distanceStatsDefinition'] = ''
        self.fields['distanceObservations'] = None
        self.fields['returnLegIncluded'] = False
        self.fields['methodModel'] = None
        self.fields['methodModelDescription'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['inputs'] = []
        self.fields['practices'] = []
        self.fields['emissions'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class ActorJSONLD:
    def __init__(self):
        self.required = [
            'lastName',
            'dataPrivate'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = NodeType.ACTOR.value
        self.fields['@id'] = ''
        self.fields['name'] = ''
        self.fields['firstName'] = ''
        self.fields['lastName'] = ''
        self.fields['orcid'] = ''
        self.fields['scopusID'] = ''
        self.fields['primaryInstitution'] = ''
        self.fields['city'] = ''
        self.fields['country'] = None
        self.fields['email'] = ''
        self.fields['website'] = None
        self.fields['dataPrivate'] = False
        self.fields['originalId'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class AnimalJSONLD:
    def __init__(self):
        self.required = [
            'animalId',
            'term',
            'referencePeriod'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.ANIMAL.value
        self.fields['animalId'] = ''
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['referencePeriod'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['price'] = None
        self.fields['currency'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['inputs'] = []
        self.fields['practices'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class BibliographyJSONLD:
    def __init__(self):
        self.required = [
            'name',
            'title',
            'authors',
            'outlet',
            'year'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.BIBLIOGRAPHY.value
        self.fields['name'] = ''
        self.fields['documentDOI'] = ''
        self.fields['title'] = ''
        self.fields['arxivID'] = ''
        self.fields['scopus'] = ''
        self.fields['mendeleyID'] = ''
        self.fields['authors'] = []
        self.fields['outlet'] = ''
        self.fields['year'] = None
        self.fields['volume'] = None
        self.fields['issue'] = ''
        self.fields['chapter'] = ''
        self.fields['pages'] = ''
        self.fields['publisher'] = ''
        self.fields['city'] = ''
        self.fields['editors'] = []
        self.fields['institutionPub'] = []
        self.fields['websites'] = None
        self.fields['articlePdf'] = ''
        self.fields['dateAccessed'] = None
        self.fields['abstract'] = ''
        self.fields['schemaVersion'] = ''

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class CompletenessJSONLD:
    def __init__(self):
        self.required = [
            'animalFeed',
            'animalPopulation',
            'cropResidue',
            'electricityFuel',
            'excreta',
            'fertiliser',
            'freshForage',
            'ingredient',
            'liveAnimalInput',
            'material',
            'operation',
            'otherChemical',
            'pesticideVeterinaryDrug',
            'product',
            'seed',
            'soilAmendment',
            'transport',
            'waste',
            'water'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.COMPLETENESS.value
        self.fields['animalFeed'] = False
        self.fields['animalPopulation'] = False
        self.fields['cropResidue'] = False
        self.fields['electricityFuel'] = False
        self.fields['excreta'] = False
        self.fields['fertiliser'] = False
        self.fields['freshForage'] = False
        self.fields['ingredient'] = False
        self.fields['liveAnimalInput'] = False
        self.fields['material'] = False
        self.fields['operation'] = False
        self.fields['otherChemical'] = False
        self.fields['pesticideVeterinaryDrug'] = False
        self.fields['product'] = False
        self.fields['seed'] = False
        self.fields['soilAmendment'] = False
        self.fields['transport'] = False
        self.fields['waste'] = False
        self.fields['water'] = False
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class CycleJSONLD:
    def __init__(self):
        self.required = [
            'functionalUnit',
            'endDate',
            'site',
            'defaultMethodClassification',
            'defaultMethodClassificationDescription',
            'completeness',
            'dataPrivate'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = NodeType.CYCLE.value
        self.fields['@id'] = ''
        self.fields['name'] = ''
        self.fields['description'] = ''
        self.fields['functionalUnit'] = ''
        self.fields['functionalUnitDetails'] = ''
        self.fields['endDate'] = ''
        self.fields['startDate'] = ''
        self.fields['startDateDefinition'] = ''
        self.fields['cycleDuration'] = None
        self.fields['site'] = None
        self.fields['otherSites'] = []
        self.fields['siteDuration'] = None
        self.fields['otherSitesDuration'] = None
        self.fields['siteUnusedDuration'] = None
        self.fields['otherSitesUnusedDuration'] = None
        self.fields['siteArea'] = None
        self.fields['otherSitesArea'] = None
        self.fields['harvestedArea'] = None
        self.fields['numberOfCycles'] = None
        self.fields['treatment'] = ''
        self.fields['commercialPracticeTreatment'] = False
        self.fields['numberOfReplications'] = None
        self.fields['sampleWeight'] = None
        self.fields['defaultMethodClassification'] = ''
        self.fields['defaultMethodClassificationDescription'] = ''
        self.fields['defaultSource'] = None
        self.fields['completeness'] = None
        self.fields['practices'] = []
        self.fields['animals'] = []
        self.fields['inputs'] = []
        self.fields['products'] = []
        self.fields['transformations'] = []
        self.fields['emissions'] = []
        self.fields['dataPrivate'] = False
        self.fields['originalId'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = False
        self.fields['aggregatedDataValidated'] = False
        self.fields['aggregatedVersion'] = ''
        self.fields['aggregatedQualityScore'] = None
        self.fields['aggregatedQualityScoreMax'] = None
        self.fields['aggregatedCycles'] = []
        self.fields['aggregatedSources'] = []
        self.fields['covarianceMatrixIds'] = None
        self.fields['covarianceMatrix'] = None
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class EmissionJSONLD:
    def __init__(self):
        self.required = [
            'term',
            'value',
            'methodTier',
            'methodModel'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.EMISSION.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['key'] = None
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['dates'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['emissionDuration'] = None
        self.fields['depth'] = None
        self.fields['methodTier'] = ''
        self.fields['methodModel'] = None
        self.fields['methodModelDescription'] = ''
        self.fields['properties'] = []
        self.fields['inputs'] = []
        self.fields['animals'] = []
        self.fields['transport'] = []
        self.fields['operation'] = None
        self.fields['transformation'] = None
        self.fields['site'] = None
        self.fields['country'] = None
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None
        self.fields['deleted'] = False

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class ImpactAssessmentJSONLD:
    def __init__(self):
        self.required = [
            'product',
            'functionalUnitQuantity',
            'allocationMethod',
            'endDate',
            'country',
            'dataPrivate'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = NodeType.IMPACTASSESSMENT.value
        self.fields['@id'] = ''
        self.fields['name'] = ''
        self.fields['version'] = ''
        self.fields['versionDetails'] = ''
        self.fields['cycle'] = None
        self.fields['product'] = None
        self.fields['functionalUnitQuantity'] = 1
        self.fields['allocationMethod'] = ''
        self.fields['endDate'] = ''
        self.fields['startDate'] = ''
        self.fields['site'] = None
        self.fields['country'] = None
        self.fields['region'] = None
        self.fields['organisation'] = None
        self.fields['source'] = None
        self.fields['emissionsResourceUse'] = []
        self.fields['impacts'] = []
        self.fields['endpoints'] = []
        self.fields['dataPrivate'] = False
        self.fields['organic'] = False
        self.fields['irrigated'] = False
        self.fields['autoGenerated'] = False
        self.fields['originalId'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = False
        self.fields['aggregatedDataValidated'] = False
        self.fields['aggregatedVersion'] = ''
        self.fields['aggregatedQualityScore'] = None
        self.fields['aggregatedQualityScoreMax'] = None
        self.fields['aggregatedImpactAssessments'] = []
        self.fields['aggregatedSources'] = []
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class IndicatorJSONLD:
    def __init__(self):
        self.required = [
            'term',
            'value',
            'methodModel'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.INDICATOR.value
        self.fields['term'] = None
        self.fields['key'] = None
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['methodTier'] = ''
        self.fields['methodModel'] = None
        self.fields['methodModelDescription'] = ''
        self.fields['inputs'] = []
        self.fields['animals'] = []
        self.fields['country'] = None
        self.fields['operation'] = None
        self.fields['landCover'] = None
        self.fields['previousLandCover'] = None
        self.fields['transformation'] = None
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class InfrastructureJSONLD:
    def __init__(self):
        self.required = [
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.INFRASTRUCTURE.value
        self.fields['term'] = None
        self.fields['name'] = ''
        self.fields['description'] = ''
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['defaultLifespan'] = None
        self.fields['defaultLifespanHours'] = None
        self.fields['mass'] = None
        self.fields['area'] = None
        self.fields['ownershipStatus'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['source'] = None
        self.fields['impactAssessment'] = None
        self.fields['inputs'] = []
        self.fields['transport'] = []
        self.fields['schemaVersion'] = ''

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class InputJSONLD:
    def __init__(self):
        self.required = [
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.INPUT.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['dates'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['inputDuration'] = None
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['model'] = None
        self.fields['modelDescription'] = ''
        self.fields['isAnimalFeed'] = False
        self.fields['fromCycle'] = False
        self.fields['producedInCycle'] = False
        self.fields['price'] = None
        self.fields['priceSd'] = None
        self.fields['priceMin'] = None
        self.fields['priceMax'] = None
        self.fields['priceStatsDefinition'] = ''
        self.fields['cost'] = None
        self.fields['costSd'] = None
        self.fields['costMin'] = None
        self.fields['costMax'] = None
        self.fields['costStatsDefinition'] = ''
        self.fields['currency'] = ''
        self.fields['lifespan'] = None
        self.fields['operation'] = None
        self.fields['country'] = None
        self.fields['region'] = None
        self.fields['impactAssessment'] = None
        self.fields['impactAssessmentIsProxy'] = False
        self.fields['site'] = None
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['transport'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class ManagementJSONLD:
    def __init__(self):
        self.required = [
            'term',
            'endDate'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.MANAGEMENT.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['model'] = None
        self.fields['modelDescription'] = ''
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class MeasurementJSONLD:
    def __init__(self):
        self.required = [
            'term',
            'methodClassification'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.MEASUREMENT.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['dates'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['measurementDuration'] = None
        self.fields['depthUpper'] = None
        self.fields['depthLower'] = None
        self.fields['latitude'] = None
        self.fields['longitude'] = None
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['method'] = None
        self.fields['methodDescription'] = ''
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class OrganisationJSONLD:
    def __init__(self):
        self.required = [
            'country',
            'dataPrivate',
            'uploadBy'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = NodeType.ORGANISATION.value
        self.fields['@id'] = ''
        self.fields['name'] = ''
        self.fields['description'] = ''
        self.fields['boundary'] = None
        self.fields['boundaryArea'] = None
        self.fields['area'] = None
        self.fields['latitude'] = None
        self.fields['longitude'] = None
        self.fields['streetAddress'] = ''
        self.fields['city'] = ''
        self.fields['region'] = None
        self.fields['country'] = None
        self.fields['postOfficeBoxNumber'] = ''
        self.fields['postalCode'] = ''
        self.fields['website'] = None
        self.fields['glnNumber'] = ''
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['infrastructure'] = []
        self.fields['dataPrivate'] = False
        self.fields['originalId'] = ''
        self.fields['uploadBy'] = None
        self.fields['schemaVersion'] = ''
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class PracticeJSONLD:
    def __init__(self):
        self.required = [
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.PRACTICE.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['variety'] = ''
        self.fields['key'] = None
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['dates'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['model'] = None
        self.fields['modelDescription'] = ''
        self.fields['areaPercent'] = None
        self.fields['price'] = None
        self.fields['priceSd'] = None
        self.fields['priceMin'] = None
        self.fields['priceMax'] = None
        self.fields['priceStatsDefinition'] = ''
        self.fields['cost'] = None
        self.fields['costSd'] = None
        self.fields['costMin'] = None
        self.fields['costMax'] = None
        self.fields['costStatsDefinition'] = ''
        self.fields['currency'] = ''
        self.fields['ownershipStatus'] = ''
        self.fields['primaryPercent'] = None
        self.fields['site'] = None
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class ProductJSONLD:
    def __init__(self):
        self.required = [
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.PRODUCT.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['variety'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['dates'] = None
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['model'] = None
        self.fields['modelDescription'] = ''
        self.fields['fate'] = ''
        self.fields['price'] = None
        self.fields['priceSd'] = None
        self.fields['priceMin'] = None
        self.fields['priceMax'] = None
        self.fields['priceStatsDefinition'] = ''
        self.fields['revenue'] = None
        self.fields['revenueSd'] = None
        self.fields['revenueMin'] = None
        self.fields['revenueMax'] = None
        self.fields['revenueStatsDefinition'] = ''
        self.fields['currency'] = ''
        self.fields['economicValueShare'] = None
        self.fields['primary'] = False
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['properties'] = []
        self.fields['transport'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class PropertyJSONLD:
    def __init__(self):
        self.required = [
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.PROPERTY.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['key'] = None
        self.fields['value'] = None
        self.fields['share'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['date'] = ''
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['methodModel'] = None
        self.fields['methodModelDescription'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['source'] = None
        self.fields['dataState'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class SiteJSONLD:
    def __init__(self):
        self.required = [
            'siteType',
            'country',
            'dataPrivate'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = NodeType.SITE.value
        self.fields['@id'] = ''
        self.fields['name'] = ''
        self.fields['description'] = ''
        self.fields['organisation'] = None
        self.fields['siteType'] = ''
        self.fields['tenure'] = ''
        self.fields['numberOfSites'] = None
        self.fields['boundary'] = None
        self.fields['area'] = None
        self.fields['areaSd'] = None
        self.fields['areaMin'] = None
        self.fields['areaMax'] = None
        self.fields['latitude'] = None
        self.fields['longitude'] = None
        self.fields['country'] = None
        self.fields['region'] = None
        self.fields['glnNumber'] = ''
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['defaultMethodClassification'] = ''
        self.fields['defaultMethodClassificationDescription'] = ''
        self.fields['defaultSource'] = None
        self.fields['measurements'] = []
        self.fields['management'] = []
        self.fields['infrastructure'] = []
        self.fields['dataPrivate'] = False
        self.fields['boundaryArea'] = None
        self.fields['ecoregion'] = ''
        self.fields['awareWaterBasinId'] = ''
        self.fields['originalId'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = False
        self.fields['aggregatedDataValidated'] = False
        self.fields['aggregatedVersion'] = ''
        self.fields['aggregatedSites'] = []
        self.fields['aggregatedSources'] = []
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class SourceJSONLD:
    def __init__(self):
        self.required = [
            'name',
            'bibliography',
            'uploadBy',
            'dataPrivate'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = NodeType.SOURCE.value
        self.fields['@id'] = ''
        self.fields['name'] = ''
        self.fields['bibliography'] = None
        self.fields['metaAnalyses'] = []
        self.fields['uploadBy'] = None
        self.fields['uploadNotes'] = ''
        self.fields['validationDate'] = None
        self.fields['validationBy'] = []
        self.fields['intendedApplication'] = ''
        self.fields['studyReasons'] = ''
        self.fields['intendedAudience'] = ''
        self.fields['comparativeAssertions'] = False
        self.fields['sampleDesign'] = None
        self.fields['weightingMethod'] = ''
        self.fields['experimentDesign'] = None
        self.fields['originalLicense'] = ''
        self.fields['dataPrivate'] = False
        self.fields['originalId'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class TermJSONLD:
    def __init__(self):
        self.required = [
            'name',
            'termType'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = NodeType.TERM.value
        self.fields['@id'] = ''
        self.fields['name'] = ''
        self.fields['synonyms'] = None
        self.fields['definition'] = ''
        self.fields['description'] = ''
        self.fields['units'] = ''
        self.fields['unitsDescription'] = ''
        self.fields['subClassOf'] = []
        self.fields['defaultProperties'] = []
        self.fields['casNumber'] = ''
        self.fields['ecoinventReferenceProductId'] = None
        self.fields['fishstatName'] = ''
        self.fields['hsCode'] = ''
        self.fields['iccCode'] = None
        self.fields['iso31662Code'] = ''
        self.fields['gadmFullName'] = ''
        self.fields['gadmId'] = ''
        self.fields['gadmLevel'] = None
        self.fields['gadmName'] = ''
        self.fields['gadmCountry'] = ''
        self.fields['gtin'] = ''
        self.fields['canonicalSmiles'] = ''
        self.fields['latitude'] = None
        self.fields['longitude'] = None
        self.fields['area'] = None
        self.fields['openLCAId'] = ''
        self.fields['scientificName'] = ''
        self.fields['website'] = None
        self.fields['agrovoc'] = None
        self.fields['aquastatSpeciesFactSheet'] = None
        self.fields['cornellBiologicalControl'] = None
        self.fields['ecolabelIndex'] = None
        self.fields['feedipedia'] = None
        self.fields['fishbase'] = None
        self.fields['pubchem'] = None
        self.fields['wikipedia'] = None
        self.fields['termType'] = ''
        self.fields['schemaVersion'] = ''
        self.fields['createdAt'] = None
        self.fields['updatedAt'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class TransformationJSONLD:
    def __init__(self):
        self.required = [
            'transformationId',
            'term'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.TRANSFORMATION.value
        self.fields['transformationId'] = ''
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['startDate'] = ''
        self.fields['endDate'] = ''
        self.fields['transformationDuration'] = None
        self.fields['previousTransformationId'] = ''
        self.fields['transformedShare'] = None
        self.fields['site'] = None
        self.fields['inputs'] = []
        self.fields['emissions'] = []
        self.fields['products'] = []
        self.fields['practices'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


class TransportJSONLD:
    def __init__(self):
        self.required = [
            'term',
            'returnLegIncluded'
        ]
        self.fields = OrderedDict()
        self.fields['@type'] = SchemaType.TRANSPORT.value
        self.fields['term'] = None
        self.fields['description'] = ''
        self.fields['value'] = None
        self.fields['distribution'] = None
        self.fields['sd'] = None
        self.fields['min'] = None
        self.fields['max'] = None
        self.fields['statsDefinition'] = ''
        self.fields['observations'] = None
        self.fields['distance'] = None
        self.fields['distanceSd'] = None
        self.fields['distanceMin'] = None
        self.fields['distanceMax'] = None
        self.fields['distanceStatsDefinition'] = ''
        self.fields['distanceObservations'] = None
        self.fields['returnLegIncluded'] = False
        self.fields['methodModel'] = None
        self.fields['methodModelDescription'] = ''
        self.fields['methodClassification'] = ''
        self.fields['methodClassificationDescription'] = ''
        self.fields['source'] = None
        self.fields['otherSources'] = []
        self.fields['inputs'] = []
        self.fields['practices'] = []
        self.fields['emissions'] = []
        self.fields['schemaVersion'] = ''
        self.fields['added'] = None
        self.fields['addedVersion'] = None
        self.fields['updated'] = None
        self.fields['updatedVersion'] = None
        self.fields['aggregated'] = None
        self.fields['aggregatedVersion'] = None

    def to_dict(self):
        values = OrderedDict()
        for key, value in self.fields.items():
            if (value is not None and value != '' and value != []) or key in self.required:
                values[key] = value
        return values


ACTOR_COUNTRY = [
    TermTermType.REGION
]


ANIMAL_TERM = [
    TermTermType.LIVEANIMAL,
    TermTermType.LIVEAQUATICSPECIES
]


EMISSION_TERM = [
    TermTermType.EMISSION
]


EMISSION_INPUTS = [
    TermTermType.BIOLOGICALCONTROLAGENT,
    TermTermType.ELECTRICITY,
    TermTermType.FEEDFOODADDITIVE,
    TermTermType.FUEL,
    TermTermType.MATERIAL,
    TermTermType.INORGANICFERTILISER,
    TermTermType.ORGANICFERTILISER,
    TermTermType.BIOCHAR,
    TermTermType.FERTILISERBRANDNAME,
    TermTermType.PESTICIDEAI,
    TermTermType.PESTICIDEBRANDNAME,
    TermTermType.SEED,
    TermTermType.SOILAMENDMENT,
    TermTermType.SUBSTRATE,
    TermTermType.VETERINARYDRUG,
    TermTermType.WATER,
    TermTermType.TRANSPORT,
    TermTermType.ANIMALPRODUCT,
    TermTermType.CROP,
    TermTermType.FORAGE,
    TermTermType.CROPRESIDUE,
    TermTermType.LIVEANIMAL,
    TermTermType.LIVEAQUATICSPECIES,
    TermTermType.PROCESSEDFOOD,
    TermTermType.EXCRETAMANAGEMENT,
    TermTermType.WASTEMANAGEMENT,
    TermTermType.OPERATION,
    TermTermType.OTHERORGANICCHEMICAL,
    TermTermType.OTHERINORGANICCHEMICAL
]


EMISSION_ANIMALS = [
    TermTermType.LIVEANIMAL,
    TermTermType.LIVEAQUATICSPECIES
]


EMISSION_METHODMODEL = [
    TermTermType.MODEL,
    TermTermType.METHODEMISSIONRESOURCEUSE
]


EMISSION_COUNTRY = [
    TermTermType.REGION
]


EMISSION_KEY = [
    TermTermType.FUEL,
    TermTermType.MATERIAL,
    TermTermType.WASTE,
    TermTermType.INORGANICFERTILISER,
    TermTermType.OTHERINORGANICCHEMICAL,
    TermTermType.OTHERORGANICCHEMICAL,
    TermTermType.PESTICIDEAI,
    TermTermType.SOILAMENDMENT,
    TermTermType.VETERINARYDRUG
]


IMPACTASSESSMENT_COUNTRY = [
    TermTermType.REGION
]


IMPACTASSESSMENT_REGION = [
    TermTermType.REGION
]


IMPACTASSESSMENT_EMISSIONSRESOURCEUSETERM = [
    TermTermType.EMISSION,
    TermTermType.RESOURCEUSE
]


IMPACTASSESSMENT_IMPACTSTERM = [
    TermTermType.CHARACTERISEDINDICATOR
]


IMPACTASSESSMENT_ENDPOINTSTERM = [
    TermTermType.ENDPOINTINDICATOR
]


INDICATOR_TERM = [
    TermTermType.EMISSION,
    TermTermType.ENDPOINTINDICATOR,
    TermTermType.CHARACTERISEDINDICATOR,
    TermTermType.RESOURCEUSE
]


INDICATOR_METHODMODEL = [
    TermTermType.MODEL,
    TermTermType.METHODEMISSIONRESOURCEUSE
]


INDICATOR_OPERATION = [
    TermTermType.OPERATION
]


INDICATOR_LANDCOVER = [
    TermTermType.LANDCOVER
]


INDICATOR_PREVIOUSLANDCOVER = [
    TermTermType.LANDCOVER
]


INDICATOR_COUNTRY = [
    TermTermType.REGION
]


INDICATOR_KEY = [
    TermTermType.FUEL,
    TermTermType.MATERIAL,
    TermTermType.WASTE,
    TermTermType.INORGANICFERTILISER,
    TermTermType.OTHERINORGANICCHEMICAL,
    TermTermType.OTHERORGANICCHEMICAL,
    TermTermType.PESTICIDEAI,
    TermTermType.SOILAMENDMENT,
    TermTermType.VETERINARYDRUG
]


INDICATOR_INPUTS = [
    TermTermType.BIOLOGICALCONTROLAGENT,
    TermTermType.ELECTRICITY,
    TermTermType.FEEDFOODADDITIVE,
    TermTermType.FUEL,
    TermTermType.MATERIAL,
    TermTermType.INORGANICFERTILISER,
    TermTermType.ORGANICFERTILISER,
    TermTermType.BIOCHAR,
    TermTermType.FERTILISERBRANDNAME,
    TermTermType.PESTICIDEAI,
    TermTermType.PESTICIDEBRANDNAME,
    TermTermType.SEED,
    TermTermType.SOILAMENDMENT,
    TermTermType.SUBSTRATE,
    TermTermType.VETERINARYDRUG,
    TermTermType.WATER,
    TermTermType.TRANSPORT,
    TermTermType.ANIMALPRODUCT,
    TermTermType.CROP,
    TermTermType.FORAGE,
    TermTermType.CROPRESIDUE,
    TermTermType.LIVEANIMAL,
    TermTermType.LIVEAQUATICSPECIES,
    TermTermType.PROCESSEDFOOD,
    TermTermType.EXCRETAMANAGEMENT,
    TermTermType.WASTEMANAGEMENT,
    TermTermType.OPERATION,
    TermTermType.OTHERORGANICCHEMICAL,
    TermTermType.OTHERINORGANICCHEMICAL
]


INDICATOR_ANIMALS = [
    TermTermType.LIVEANIMAL,
    TermTermType.LIVEAQUATICSPECIES
]


INFRASTRUCTURE_TERM = [
    TermTermType.BUILDING,
    TermTermType.CROPSUPPORT,
    TermTermType.IRRIGATION,
    TermTermType.MACHINERY
]


INFRASTRUCTURE_INPUTSTERM = [
    TermTermType.ELECTRICITY,
    TermTermType.FUEL,
    TermTermType.MATERIAL,
    TermTermType.SEED,
    TermTermType.TRANSPORT,
    TermTermType.WATER
]


INPUT_TERM = [
    TermTermType.BIOLOGICALCONTROLAGENT,
    TermTermType.ELECTRICITY,
    TermTermType.FEEDFOODADDITIVE,
    TermTermType.FUEL,
    TermTermType.MATERIAL,
    TermTermType.INORGANICFERTILISER,
    TermTermType.ORGANICFERTILISER,
    TermTermType.FERTILISERBRANDNAME,
    TermTermType.BIOCHAR,
    TermTermType.PESTICIDEAI,
    TermTermType.PESTICIDEBRANDNAME,
    TermTermType.PROCESSINGAID,
    TermTermType.SEED,
    TermTermType.OTHERORGANICCHEMICAL,
    TermTermType.OTHERINORGANICCHEMICAL,
    TermTermType.SOILAMENDMENT,
    TermTermType.SUBSTRATE,
    TermTermType.WATER,
    TermTermType.ANIMALPRODUCT,
    TermTermType.CROP,
    TermTermType.FORAGE,
    TermTermType.LIVEANIMAL,
    TermTermType.LIVEAQUATICSPECIES,
    TermTermType.EXCRETA,
    TermTermType.PROCESSEDFOOD,
    TermTermType.VETERINARYDRUG,
    TermTermType.WASTE
]


INPUT_MODEL = [
    TermTermType.MODEL
]


INPUT_OPERATION = [
    TermTermType.OPERATION
]


INPUT_COUNTRY = [
    TermTermType.REGION
]


INPUT_REGION = [
    TermTermType.REGION
]


MANAGEMENT_TERM = [
    TermTermType.CROPRESIDUEMANAGEMENT,
    TermTermType.LANDCOVER,
    TermTermType.LANDUSEMANAGEMENT,
    TermTermType.PASTUREMANAGEMENT,
    TermTermType.STANDARDSLABELS,
    TermTermType.SYSTEM,
    TermTermType.TILLAGE,
    TermTermType.WATERREGIME
]


MEASUREMENT_TERM = [
    TermTermType.MEASUREMENT,
    TermTermType.SOILTEXTURE,
    TermTermType.SOILTYPE,
    TermTermType.USDASOILTYPE
]


MEASUREMENT_METHOD = [
    TermTermType.METHODMEASUREMENT,
    TermTermType.MODEL
]


ORGANISATION_COUNTRY = [
    TermTermType.REGION
]


ORGANISATION_REGION = [
    TermTermType.REGION
]


PRACTICE_TERM = [
    TermTermType.ANIMALBREED,
    TermTermType.ANIMALMANAGEMENT,
    TermTermType.AQUACULTUREMANAGEMENT,
    TermTermType.CROPESTABLISHMENT,
    TermTermType.CROPRESIDUEMANAGEMENT,
    TermTermType.EXCRETAMANAGEMENT,
    TermTermType.LANDCOVER,
    TermTermType.LANDUSEMANAGEMENT,
    TermTermType.PASTUREMANAGEMENT,
    TermTermType.STANDARDSLABELS,
    TermTermType.SYSTEM,
    TermTermType.TILLAGE,
    TermTermType.WATERREGIME,
    TermTermType.WASTEMANAGEMENT,
    TermTermType.OPERATION
]


PRACTICE_KEY = [
    TermTermType.CROP,
    TermTermType.FORAGE,
    TermTermType.BIOLOGICALCONTROLAGENT,
    TermTermType.INORGANICFERTILISER,
    TermTermType.ORGANICFERTILISER,
    TermTermType.BIOCHAR,
    TermTermType.OTHERINORGANICCHEMICAL,
    TermTermType.OTHERORGANICCHEMICAL,
    TermTermType.PESTICIDEAI,
    TermTermType.SOILAMENDMENT,
    TermTermType.LANDCOVER
]


PRACTICE_MODEL = [
    TermTermType.MODEL
]


PRODUCT_TERM = [
    TermTermType.ANIMALPRODUCT,
    TermTermType.CROP,
    TermTermType.CROPRESIDUE,
    TermTermType.ELECTRICITY,
    TermTermType.FEEDFOODADDITIVE,
    TermTermType.FORAGE,
    TermTermType.FUEL,
    TermTermType.LIVEANIMAL,
    TermTermType.LIVEAQUATICSPECIES,
    TermTermType.EXCRETA,
    TermTermType.ORGANICFERTILISER,
    TermTermType.INORGANICFERTILISER,
    TermTermType.BIOCHAR,
    TermTermType.OTHERORGANICCHEMICAL,
    TermTermType.OTHERINORGANICCHEMICAL,
    TermTermType.PROCESSINGAID,
    TermTermType.PROCESSEDFOOD,
    TermTermType.SEED,
    TermTermType.SOILAMENDMENT,
    TermTermType.SUBSTRATE,
    TermTermType.MATERIAL,
    TermTermType.WASTE
]


PRODUCT_MODEL = [
    TermTermType.MODEL
]


PROPERTY_TERM = [
    TermTermType.PROPERTY
]


PROPERTY_METHODMODEL = [
    TermTermType.MODEL,
    TermTermType.METHODMEASUREMENT
]


SITE_COUNTRY = [
    TermTermType.REGION
]


SITE_REGION = [
    TermTermType.REGION
]


SOURCE_SAMPLEDESIGN = [
    TermTermType.SAMPLEDESIGN
]


SOURCE_EXPERIMENTDESIGN = [
    TermTermType.EXPERIMENTDESIGN
]


TRANSFORMATION_TERM = [
    TermTermType.EXCRETAMANAGEMENT,
    TermTermType.WASTEMANAGEMENT,
    TermTermType.OPERATION
]


TRANSPORT_TERM = [
    TermTermType.TRANSPORT
]


TRANSPORT_METHODMODEL = [
    TermTermType.MODEL
]


TRANSPORT_PRACTICESTERM = [
    TermTermType.OPERATION
]


class CompletenessField(Enum):
    ANIMALFEED = 'animalFeed'
    ANIMALPOPULATION = 'animalPopulation'
    CROPRESIDUE = 'cropResidue'
    ELECTRICITYFUEL = 'electricityFuel'
    EXCRETA = 'excreta'
    FERTILISER = 'fertiliser'
    FRESHFORAGE = 'freshForage'
    INGREDIENT = 'ingredient'
    LIVEANIMALINPUT = 'liveAnimalInput'
    MATERIAL = 'material'
    OPERATION = 'operation'
    OTHERCHEMICAL = 'otherChemical'
    PESTICIDEVETERINARYDRUG = 'pesticideVeterinaryDrug'
    PRODUCT = 'product'
    SEED = 'seed'
    SOILAMENDMENT = 'soilAmendment'
    TRANSPORT = 'transport'
    WASTE = 'waste'
    WATER = 'water'
    SCHEMAVERSION = 'schemaVersion'
    ADDED = 'added'
    ADDEDVERSION = 'addedVersion'
    UPDATED = 'updated'
    UPDATEDVERSION = 'updatedVersion'


COMPLETENESS_MAPPING = {
  "Input": {
    "animalProduct": "ingredient",
    "crop": "ingredient",
    "processedFood": "ingredient",
    "electricity": "electricityFuel",
    "fuel": "electricityFuel",
    "fertiliseBrandName": "fertiliser",
    "inorganicFertiliser": "fertiliser",
    "organicFertiliser": "fertiliser",
    "forage": "freshForage",
    "feedFoodAdditive": "ingredient",
    "liveAnimal": "liveAnimalInput",
    "liveAquaticSpecies": "liveAnimalInput",
    "material": "material",
    "substrate": "material",
    "otherInorganicChemical": "otherChemical",
    "otherOrganicChemical": "otherChemical",
    "processingAid": "otherChemical",
    "biologicalControlAgent": "pesticideVeterinaryDrug",
    "pesticideAI": "pesticideVeterinaryDrug",
    "pesticideBrandName": "pesticideVeterinaryDrug",
    "veterinaryDrug": "pesticideVeterinaryDrug",
    "seed": "seed",
    "soilAmendment": "soilAmendment",
    "biochar": "soilAmendment",
    "waste": "waste",
    "water": "water"
  },
  "Animal": {
    "liveAnimal": "animalPopulation",
    "liveAquaticSpecies": "animalPopulation"
  },
  "Product": {
    "cropResidue": "cropResidue",
    "excreta": "excreta",
    "animalProduct": "product",
    "crop": "product",
    "electricity": "product",
    "feedFoodAdditive": "product",
    "forage": "product",
    "fuel": "product",
    "landCover": "product",
    "liveAnimal": "product",
    "liveAquaticSpecies": "product",
    "organicFertiliser": "product",
    "inorganicFertiliser": "product",
    "biochar": "product",
    "processingAid": "product",
    "processedFood": "product",
    "seed": "product",
    "soilAmendment": "product",
    "substrate": "product",
    "material": "product",
    "waste": "waste"
  },
  "Practice": {
    "cropResidueManagement": "cropResidue",
    "excretaManagement": "excreta",
    "operation": "operation",
    "wasteManagement": "waste"
  },
  "Transformation": {
    "excretaManagement": "excreta",
    "wasteManagement": "waste"
  },
  "Transport": {
    "transport": "transport"
  }
}


UNIQUENESS_FIELDS = {
    'Animal': {
        'properties': [
            'term.@id',
            'key.@id',
            'date',
            'startDate',
            'endDate'
        ],
        'inputs': [
            'term.@id',
            'dates',
            'startDate',
            'endDate',
            'isAnimalFeed',
            'producedInCycle',
            'transport.term.@id',
            'operation.@id',
            'country.@id',
            'region.@id',
            'impactAssessment.id'
        ],
        'practices': [
            'term.@id',
            'key.@id',
            'dates',
            'startDate',
            'endDate',
            'areaPercent',
            'ownershipStatus'
        ]
    },
    'Cycle': {
        'practices': [
            'term.@id',
            'key.@id',
            'dates',
            'startDate',
            'endDate',
            'areaPercent',
            'ownershipStatus',
            'variety',
            'site.id'
        ],
        'animals': [
            'animalId'
        ],
        'inputs': [
            'term.@id',
            'dates',
            'startDate',
            'endDate',
            'isAnimalFeed',
            'producedInCycle',
            'transport.term.@id',
            'operation.@id',
            'country.@id',
            'region.@id',
            'impactAssessment.id',
            'site.id'
        ],
        'products': [
            'term.@id',
            'dates',
            'startDate',
            'endDate',
            'variety',
            'fate'
        ],
        'transformations': [
            'transformationId'
        ],
        'emissions': [
            'term.@id',
            'key.@id',
            'dates',
            'startDate',
            'endDate',
            'depth',
            'inputs.@id',
            'animals.@id',
            'transport.@id',
            'operation.@id',
            'transformation.@id',
            'site.id',
            'country.@id'
        ]
    },
    'Emission': {
        'properties': [
            'term.@id',
            'key.@id',
            'date',
            'startDate',
            'endDate'
        ],
        'inputs': [
            '@id'
        ],
        'animals': [
            '@id'
        ],
        'transport': [
            '@id'
        ]
    },
    'ImpactAssessment': {
        'emissionsResourceUse': [
            'term.@id',
            'key.@id',
            'inputs.@id',
            'animals.@id',
            'country.@id',
            'operation.@id',
            'methodModel.@id',
            'transformation.@id',
            'landCover.@id',
            'previousLandCover.@id'
        ],
        'impacts': [
            'term.@id',
            'inputs.@id',
            'methodModel.@id'
        ],
        'endpoints': [
            'term.@id',
            'inputs.@id',
            'methodModel.@id'
        ]
    },
    'Indicator': {
        'inputs': [
            '@id'
        ],
        'animals': [
            '@id'
        ]
    },
    'Infrastructure': {
        'inputs': [
            'term.@id',
            'transport.term.@id',
            'operation.@id',
            'country.@id'
        ],
        'transport': [
            'term.@id',
            'value',
            'distance'
        ]
    },
    'Input': {
        'properties': [
            'term.@id',
            'key.@id',
            'value',
            'share',
            'date',
            'startDate',
            'endDate'
        ],
        'transport': [
            'term.@id',
            'value',
            'distance'
        ]
    },
    'Management': {
        'properties': [
            'term.@id',
            'key.@id',
            'date',
            'startDate',
            'endDate'
        ]
    },
    'Measurement': {
        'properties': [
            'term.@id',
            'key.@id',
            'date',
            'startDate',
            'endDate'
        ]
    },
    'Organisation': {
        'infrastructure': [
            'term.@id'
        ]
    },
    'Practice': {
        'properties': [
            'term.@id',
            'key.@id',
            'date',
            'startDate',
            'endDate'
        ]
    },
    'Product': {
        'properties': [
            'term.@id',
            'key.@id',
            'value',
            'share',
            'date',
            'startDate',
            'endDate'
        ],
        'transport': [
            'term.@id',
            'value',
            'distance'
        ]
    },
    'Site': {
        'measurements': [
            'term.@id',
            'dates',
            'startDate',
            'endDate',
            'measurementDuration',
            'depthUpper',
            'depthLower',
            'method.@id',
            'methodDescription',
            'methodClassification'
        ],
        'management': [
            'term.@id',
            'startDate',
            'endDate'
        ],
        'infrastructure': [
            'term.@id',
            'defaultLifespan',
            'defaultLifespanHours',
            'ownershipStatus'
        ]
    },
    'Term': {
        'subClassOf': [
            '@id'
        ],
        'defaultProperties': [
            'term.@id',
            'key.@id'
        ]
    },
    'Transformation': {
        'inputs': [
            'term.@id',
            'dates',
            'startDate',
            'endDate',
            'fromCycle',
            'transport.term.@id',
            'operation.@id',
            'country.@id',
            'region.@id',
            'impactAssessment.id'
        ],
        'emissions': [
            'term.@id',
            'dates',
            'startDate',
            'endDate',
            'depth',
            'inputs.@id',
            'transport.@id',
            'operation.@id'
        ],
        'products': [
            'term.@id',
            'dates',
            'startDate',
            'endDate',
            'variety',
            'fate'
        ],
        'practices': [
            'term.@id',
            'key.@id',
            'dates',
            'startDate',
            'endDate',
            'areaPercent',
            'ownershipStatus'
        ]
    },
    'Transport': {
        'inputs': [
            'term.@id',
            'dates',
            'startDate',
            'endDate',
            'operation.@id',
            'country.@id'
        ],
        'practices': [
            'term.@id',
            'description',
            'key.@id',
            'dates',
            'startDate',
            'endDate',
            'areaPercent',
            'ownershipStatus'
        ],
        'emissions': [
            'term.@id',
            'dates',
            'startDate',
            'endDate',
            'depth',
            'inputs.@id'
        ]
    }
}


AGGREGATED_QUALITY_SCORE_FIELDS = {
    'Completeness': {
        'crop': [
            'animalFeed',
            'cropResidue',
            'electricityFuel',
            'excreta',
            'fertiliser',
            'freshForage',
            'ingredient',
            'liveAnimalInput',
            'otherChemical',
            'pesticideVeterinaryDrug',
            'product',
            'seed',
            'water'
        ],
        'animalProduct': [
            'animalFeed',
            'cropResidue',
            'electricityFuel',
            'excreta',
            'fertiliser',
            'freshForage',
            'ingredient',
            'liveAnimalInput',
            'otherChemical',
            'pesticideVeterinaryDrug',
            'product',
            'seed',
            'water'
        ],
        'liveAnimal': [
            'animalFeed',
            'cropResidue',
            'electricityFuel',
            'excreta',
            'fertiliser',
            'freshForage',
            'ingredient',
            'liveAnimalInput',
            'otherChemical',
            'pesticideVeterinaryDrug',
            'product',
            'seed',
            'water'
        ],
        'liveAquaticSpecies': [
            'animalFeed',
            'cropResidue',
            'electricityFuel',
            'excreta',
            'fertiliser',
            'freshForage',
            'ingredient',
            'liveAnimalInput',
            'otherChemical',
            'pesticideVeterinaryDrug',
            'product',
            'seed',
            'water'
        ],
        'processedFood': [
            'electricityFuel',
            'ingredient',
            'product',
            'water'
        ]
    }
}
