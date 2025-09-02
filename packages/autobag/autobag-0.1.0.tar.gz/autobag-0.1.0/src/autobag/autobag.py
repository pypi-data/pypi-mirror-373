from pathlib import Path
from typing import Annotated
import matplotlib.pyplot as plt
import typer
from .utils import *

app = typer.Typer(invoke_without_command=True)

@app.command(name='plot_nav', help='Plot navigation path with enu coordinates')
def plot_nav(
        bag: Annotated[Path, typer.Argument(help="Path to bag")],
):
    nav_protos = get_navigation_from_bag(bag)
    enu_list = navigation_list_to_enu(nav_protos)
    plt.gca().set_aspect('equal', adjustable='datalim')
    plt.xlabel('E')
    plt.ylabel('N')
    plt.title('Navigation path with enu coordinates')
    plt.plot(enu_list[:, 0], enu_list[:, 1])
    plt.grid()
    plt.show()

def main():
    try:
        app()
    except RuntimeError as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
