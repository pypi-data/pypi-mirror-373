from fastmcp import FastMCP

def run():
    app = FastMCP("insee-server")

    @app.tool()
    async def add_numbers(a: int, b: int) -> int:
        """Additionne deux entiers et retourne le résultat"""
        return a + b

    # Lancement du serveur avec transport streamable-http
    app.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")

if __name__ == "__main__":
    run()
