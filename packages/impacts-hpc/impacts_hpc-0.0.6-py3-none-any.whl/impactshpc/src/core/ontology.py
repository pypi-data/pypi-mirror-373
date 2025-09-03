from dataclasses import dataclass
from logging import config
from typing import Any


@dataclass
class Ontology:
    term: str
    link: str

    @staticmethod
    def from_config(configEntry: dict[str, Any] | None):
        if configEntry is None:
            return None

        return Ontology(term=configEntry["term"], link=configEntry["link"])


EMBODIED_IMPACTS = Ontology(
    term="Embodied impacts", link="TODO : REPLACE WITH A LINK TO THE ONTOLOGY OF EMBODIED IMPACT"
)
USAGE_IMPACTS = Ontology(term="Usage impacts", link="TODO : REPLACE WITH A LINK TO THE ONTOLOGY OF EMBODIED IMPACT")
EMBEDDED_IMPACTS = Ontology(term="Usage impacts", link="TODO : REPLACE WITH A LINK TO THE ONTOLOGY OF EMBODIED IMPACT")
ELECTRIC_POWER = Ontology(term="Electric power", link="TODO : REPLACE WITH A LINK TO THE ONTOLOGY OF ELECTRIC POWER")
PEAK_POWER = Ontology(term="Peak power", link="TODO : REPLACE WITH A LINK TO THE ONTOLOGY OF PEAK POWER")
IDLE_POWER = Ontology(term="Idle power", link="TODO : REPLACE WITH A LINK TO THE ONTOLOGY OF IDLE POWER")
BATTERY_CAPACITY = Ontology(term="Battery Capacity", link="TODO : REPLACE WITH ONTOLOGY OF BATTERY CAPACITY")
BATTERY_WEIGHT = Ontology(term="Battery weight", link="TODO : REPLACE WITH ONTOLOGY OF BATTERY WEIGHT")
EXTRAPOLATION_FACTOR = Ontology(
    term="Extrapolation factor", link="TODO : REPLACE WITH ONTOLOGY OF EXTRAPOLATION FACTOR"
)
