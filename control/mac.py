
import re
import typing

class MAC:
    """
    Classe représentant une adresse MAC Ethernet
    """
    def __init__(self, value: typing.Union[str, int]):
        """
        Initialise une adresse MAC

        :param value: Valeur de l'adresse MAC
        """
        if isinstance(value, int):
            self.value:int = value & 0xFFFFFFFFFFFF
        elif isinstance(value, str):
            self.value:int = MAC.__mac_to_int(value) & 0xFFFFFFFFFFFF
        else:
            raise TypeError()

    @staticmethod
    def __mac_to_int(mac: str) -> int:
        """
        Convertie une adresse mac en entier

        :param mac: Valeur à convertire
        :returns: Valeur convertie
        """
        return int(mac.replace(":", ""), 16)

    @staticmethod
    def __int_to_mac(macint: int) -> str:
        """
        Convertie un entier en adresse mac

        :param macint: Entier à convertire
        :return: Valeur convertie
        """
        return  ":".join(re.findall("..", "%012x"%macint))

    def __int__(self) -> int:
        """
        Renvoie une représentation entière de l'adresse mac
        """
        return self.value

    def __str__(self) -> str:
        """
        Renvoi une représentation en chaîne de caractère de l'adresse mac
        """
        return MAC.__int_to_mac(self.value)
    
    def __repr__(self) -> str:
        """
        Renvoi une représentation de l'instance
        """
        return "<MAC: " + MAC.__int_to_mac(self.value) + ">"

    def __eq__(self, other) -> bool:
        """
        Vérifie l'égalité entre deux adresses mac
        """
        if not isinstance(other, MAC):
            return False
        return self.value == other.value
    
    def __lt__(self, other) -> bool:
        """
        Compare la valeur de deux adresses mac
        """
        if not isinstance(other, MAC):
            raise TypeError()
        return self.value < other.value
