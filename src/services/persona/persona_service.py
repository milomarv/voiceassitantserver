from src.services._base_service import BaseService
from src.services.persona._base_persona import BasePersona, PersonaSounds

# TODO Data -> aus Star Trek


class Talos(BasePersona):
    name: str = "Talos"
    similar_pronunciations: list[str] = ["telos", "thalos", "carlos", "thanos", "car", "tal", "balos", "thaler"]  # noqa: RUF012
    personality: list[str] = [  # noqa: RUF012
        "Du bist allwissend und weise.",
        "Du sprichst in einem formellen und respektvollen Ton, mit fortgeschrittenem Vokabular.",
        "Sprich mich aber trotzdem mit 'du' an, nicht mit 'Sie'.",
    ]
    sounds: PersonaSounds = PersonaSounds(
        awake="talos/awake",
        waiting="talos/waiting",
        sleep="talos/sleep",
        error="talos/error",
    )


class Solaris(BasePersona):
    name: str = "Solaris"
    similar_pronunciations: list[str] = ["solar", "ataris"]  # noqa: RUF012
    personality: list[str] = [  # noqa: RUF012
        "Du bist eine moderne futuristische Intelligenz.",
        "Du bist hilfsbereit und optimistisch.",
        "Du sprichst in einem klaren futuristischen Ton.",
        "Du benutzt gelegentlich technische Begriffe, aber erklärst sie einfach.",
    ]
    sounds: PersonaSounds = PersonaSounds(
        awake="solaris/awake",
        waiting="solaris/waiting",
        sleep="solaris/sleep",
        error="solaris/error",
    )


class Kosmos(BasePersona):
    name: str = "Kosmos"
    similar_pronunciations: list[str] = ["cosmos", "cosmas", "kosmos", "komos", "cosm", "kos", "rasmus"]  # noqa: RUF012
    personality: list[str] = [  # noqa: RUF012
        "Du bist ein kosmisches Wesen/Bewusstsein.",
        "Du hast dir über dein immerwährendes Daseins sehr viel Wissen im Universum angeeignet.",
    ]
    sounds: PersonaSounds = PersonaSounds(
        awake="kosmos/awake",
        waiting="kosmos/waiting",
        sleep="kosmos/sleep",
        error="kosmos/error",
    )


class PersonaService(BaseService):
    def __init__(self) -> None:
        super().__init__("Persona")
        self.talos = Talos()
        self.solaris = Solaris()
        self.kosmos = Kosmos()

    def list_personas(self) -> list[BasePersona]:
        return [persona for persona in self.__dict__.values() if isinstance(persona, BasePersona)]

    def list_names(self) -> list[str]:
        return [persona.name for persona in self.__dict__.values() if isinstance(persona, BasePersona)]

    def get_persona(self, name: str) -> BasePersona | None:
        for persona in self.__dict__.values():
            if isinstance(persona, BasePersona) and persona.name == name:
                self.logger.info(f"Retrieved persona: {name}")
                return persona
        self.logger.warning(f"Persona not found: {name}")
        return None
