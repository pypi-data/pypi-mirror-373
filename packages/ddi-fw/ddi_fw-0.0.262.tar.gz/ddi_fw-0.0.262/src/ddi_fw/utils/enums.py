from enum import Enum


class UMLSCodeTypes(Enum):
    TUI = 'tui',
    CUI = 'cui',
    ENTITIES = 'entities',


class DrugBankTextDataTypes(Enum):
    DESCRIPTION = 'description',
    INDICATION = 'indication',
    SYNTHESIS_REFERENCE = 'synthesis_reference',
    PHARMACODYNAMICS = 'pharmacodynamics',
    MECHANISM_OF_ACTION = 'mechanism_of_action',
    TOXICITY = 'toxicity',
    METABOLISM = 'metabolism',
    ABSORPTION = 'absorption',
    HALF_LIFE = 'half_life',
    PROTEIN_BINDING = 'protein_binding',
    ROUTE_OF_ELIMINATION = 'route_of_elimination',
    VOLUME_OF_DISTRIBUTION = 'volume_of_distribution',
    CLEARANCE = 'clearance',
