import rich

from egse.hexapod.symetrie.puna import PunaProxy
from egse.registry.client import RegistryClient


def test_puna_cs_with_proxy():
    with RegistryClient() as reg:
        rich.print(reg.list_services())

    puna = PunaProxy()
    puna.connect()
