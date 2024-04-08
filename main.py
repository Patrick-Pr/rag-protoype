import typer
from dotenv import load_dotenv

from database.database import add_to_database

load_dotenv()

app = typer.Typer()


@app.command()
def add(src_directory: str):
    add_to_database(src_directory)


if __name__ == "__main__":
    app()
