from fastmcp import FastMCP
from scripts.sirene import search_sirene_company
import os
import pynsee
from pynsee import init_conn
from pynsee.utils import clear_all_cache

clear_all_cache()

def run():
    clear_all_cache()
    app = FastMCP("insee-server")
    @app.tool()
    async def search_company(
        company_name: str = None,
        siren: str = None,
        siret: str = None,
        fuzzy: bool = True
    ):
        """
        Recherche une entreprise dans la base SIRENE selon SIREN, SIRET ou nom.

        Args:
            company_name (str, optional): Nom de l'entreprise.
            siren (str, optional): Code SIREN.
            siret (str, optional): Code SIRET.
            fuzzy (bool): Active la recherche approximative si nom partiel.

        Returns:
            dict: Informations clés sur l'entreprise.
        """
        print("API KEY inside server:", os.getenv("API_KEY"))
        init_conn(sirene_key=os.getenv("API_KEY"))
        return search_sirene_company(company_name, siren, siret, fuzzy)

    # Lancement du serveur avec transport stdio
    # app.run(transport="stdio", host="127.0.0.1", port=8000, path="/mcp")
    app.run(transport="stdio")

if __name__ == "__main__":
    run()
