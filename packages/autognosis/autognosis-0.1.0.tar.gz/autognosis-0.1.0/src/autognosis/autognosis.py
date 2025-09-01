import typer
from typing import Annotated
from .steer_dynamics import run
from .utils import *

app = typer.Typer(invoke_without_command=True)

@app.command(name='steer_dynamics')
def steer_dynamics(
        bag: Annotated[Path, typer.Argument(help='Path to the bag file')],
        interval: Annotated[float, typer.Option(help='Interval per step in seconds')] = None,
        use_approximation: Annotated[bool, typer.Option(help='Use approximation method')] = True,
        k_min: Annotated[float, typer.Option(help='Minimum K value')] = 0.9,
        k_max: Annotated[float, typer.Option(help='Maximum K value')] = 1.1,
        tc_min: Annotated[float, typer.Option(help='Minimum time constant (tc)')] = 0.01,
        tc_max: Annotated[float, typer.Option(help='Maximum time constant (tc)')] = 1.0,
        delay_steps_min: Annotated[int, typer.Option(help='Minimum delay steps')] = 0,
        delay_steps_max: Annotated[int, typer.Option(help='Maximum delay steps')] = 30,
):
    run(bag, interval, use_approximation, k_min, k_max, tc_min, tc_max, delay_steps_min, delay_steps_max)

def main():
    try:
        app()
    except Exception as e:
        print(e)
        exit(1)

if __name__ == "__main__":
    main()
