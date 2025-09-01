"""
Steering dynamics identification using first-order inertia model with delay.
u -- steering command
y -- steering angle
y' = (K * u - y) / tc
y(T + 1) = y(T) + (K * u - y(t)) * (1 - exp(-t / tc)
y(T + 1) = y(T) + (K * u - y(t)) * (t / tc)  when t << tc
"""
import math
from numpy.typing import NDArray
from scipy.optimize import least_squares, curve_fit, differential_evolution, OptimizeResult
import matplotlib.pyplot as plt
from typing import cast
import questionary
from .utils import *

def foi_update(
        y_prev: float,
        u: float,
        k: float,
        t: float,
        tc: float,
        use_approximation: bool,
):
    if tc <= 1e-9:
        raise ValueError('tc must be positive')
    if use_approximation:
        return y_prev + (k * u - y_prev) * min(t / tc, 1.0)
    else:
        return y_prev + (k * u - y_prev) * (1 - np.exp(-t / tc))

def delay(u: NDArray[np.float64], delay_steps: int):
    if delay_steps < 0:
        raise ValueError('delay_steps must be non-negative')
    if delay_steps == 0:
        return np.copy(u)
    u_delayed = np.roll(u, delay_steps)
    u_delayed[:delay_steps] = u[0]
    return u_delayed

def simulate(
        y0: float,
        u: NDArray[np.float64],
        k: float,
        t: float,
        tc: float,
        delay_steps: int,
        use_approximation: bool,
):
    y_predicted = np.zeros_like(u)
    y_predicted[0] = y0
    u_delayed = delay(u, delay_steps)
    for i in range(len(u) - 1):
        y_prev = cast(float, y_predicted[i])
        u_prev = cast(float, u_delayed[i])
        y_predicted[i + 1] = foi_update(y_prev, u_prev, k, t, tc, use_approximation)
    return y_predicted

def global_search(
        y: NDArray[np.float64],
        u: NDArray[np.float64],
        t: float,
        delay_steps: int,
        use_approximation: bool,
        k_bounds: tuple[float, float],
        tc_bounds: tuple[float, float],
) -> OptimizeResult:
    def sse(params):
        k, tc = params
        y0 = cast(float, y[0])
        y_predicted = simulate(y0, u, k, t, tc, delay_steps, use_approximation)
        return np.sum((y - y_predicted) ** 2)
    return differential_evolution(sse, [k_bounds, tc_bounds])

def local_search(
        y: NDArray[np.float64],
        u: NDArray[np.float64],
        t: float,
        delay_steps: int,
        use_approximation: bool,
        k_bounds: tuple[float, float],
        tc_bounds: tuple[float, float],
        initial_guess: tuple[float, float],
):
    def model(t_axis, k, tc):
        y0 = cast(float, y[0])
        return simulate(y0, u, k, t, tc, delay_steps, use_approximation)
    popt, pcov = curve_fit(
        f=model,
        xdata=np.arange(len(y)) * t,
        ydata=y,
        p0=initial_guess,
        bounds=[list(b) for b in zip(*[k_bounds, tc_bounds])]
    )
    return popt, pcov

def identify(
        control_k: NDArray[np.float64],
        state_k: NDArray[np.float64],
        t: float,
        use_approximation: bool,
        k_bounds: tuple[float, float],
        tc_bounds: tuple[float, float],
        delay_steps_range: tuple[int, int],
):
    # print('Starting identification...')
    results = []
    for delay_steps in range(delay_steps_range[0], delay_steps_range[1] + 1):
        # print()
        # print(f'Trying delay steps: {delay_steps}')
        # print('Starting global optimization...')
        global_result: OptimizeResult = global_search(state_k, control_k, t, delay_steps, use_approximation, k_bounds, tc_bounds)
        if not global_result.success:
            print(f'Global optimization failed for delay steps {delay_steps}: {global_result.message}')
            continue
        global_optimum = global_result.x
        # print(f'Global optimization result: K={global_optimum[0]}, tc={global_optimum[1]}, SSE={global_result.fun:.3e}')
        # print('Starting local optimization with global optimum as initial guess...')
        try:
            popt, pcov = local_search(state_k, control_k, t, delay_steps, use_approximation, k_bounds, tc_bounds, global_optimum)
        except RuntimeError as e:
            print(f'Local optimization failed for delay steps {delay_steps}: {e}')
            continue
        y0 = cast(float, state_k[0])
        k_opt, tc_opt = popt
        state_k_fit = simulate(y0, control_k, k_opt, t, tc_opt, delay_steps, use_approximation)
        residual = state_k - state_k_fit
        sse = np.sum(residual ** 2)
        rmse = math.sqrt(sse / len(state_k))
        result = {
            'delay_steps': delay_steps,
            'global_result': global_result,
            'popt': popt,
            'pcov': pcov,
            'state_k_fit': state_k_fit,
            'residual': residual,
            'sse': sse,
            'rmse': rmse,
        }
        results.append(result)
    return results

def print_results(results, sorted_by):
    if not results or len(results) == 0:
        print('No valid results found.')
        return
    def print_result(r):
        delay_steps = r['delay_steps']
        k_opt, tc_opt = r['popt']
        rmse = r['rmse']
        residual_max = np.max(np.abs(r['residual']))
        print(f'Delay Steps: {delay_steps:02}, K: {k_opt:.6f}, tc: {tc_opt:.6f}, RMSE: {rmse:.6f}, Max Residual: {residual_max:.6f}')

    if sorted_by == 'max residual':
        for r in sorted(results, key=lambda r: np.max(np.abs(r['residual']))):
            print_result(r)
        return
    for r in sorted(results, key=lambda r: r[sorted_by]):
        print_result(r)

def plot_results(results, timestamps, control_k, state_k, max_rmse=math.inf, max_residual=math.inf):
    if not results or len(results) == 0:
        print('No valid results found.')
        return
    filtered_results = [r for r in results if r['rmse'] <= max_rmse and np.max(np.abs(r['residual'])) <= max_residual]
    plt.figure()
    plt.xlabel('Time (s)')
    plt.ylabel('k')
    plt.plot(timestamps, control_k, label='Control')
    plt.plot(timestamps, state_k, label='State')
    for r in filtered_results:
        plt.plot(timestamps, r['state_k_fit'], label=f'Fit delay_steps={r["delay_steps"]}')
    plt.legend()
    plt.grid()

    plt.figure()
    plt.subplot(4, 1, 1)
    plt.xlabel('Delay steps')
    plt.ylabel('Max residual')
    plt.plot([r['delay_steps'] for r in filtered_results], [np.max(np.abs(r['residual'])) for r in filtered_results], marker='o')
    plt.grid()

    plt.subplot(4, 1, 2)
    plt.xlabel('Delay steps')
    plt.ylabel('RMSE')
    plt.plot([r['delay_steps'] for r in filtered_results], [r['rmse'] for r in filtered_results], marker='o')
    plt.grid()

    plt.subplot(4, 1, 3)
    plt.xlabel('Delay steps')
    plt.ylabel('k_opt')
    plt.plot([r['delay_steps'] for r in filtered_results], [r['popt'][0] for r in filtered_results], marker='o')
    plt.grid()

    plt.subplot(4, 1, 4)
    plt.xlabel('Delay steps')
    plt.ylabel('tc_opt')
    plt.plot([r['delay_steps'] for r in filtered_results], [r['popt'][1] for r in filtered_results], marker='o')
    plt.grid()

    plt.tight_layout()
    plt.show()
    plt.close()

def run(
        bag: Path,
        interval: float,
        use_approximation: bool,
        k_min: float,
        k_max: float,
        tc_min: float,
        tc_max: float,
        delay_steps_min: int,
        delay_steps_max: int,
):
    matched = get_matched_control_vehicle_state(bag)
    print(f'Found {len(matched)} matched control and vehicle state messages')
    control_k, state_k, timestamps = get_matched_k(matched)
    if interval is None:
        if len(timestamps) >= 2:
            interval = float(np.median(np.diff(timestamps)))
            print(f'Inferred interval: {interval:.4f} seconds')
        else:
            raise ValueError('Not enough data to infer interval. Please provide interval explicitly.')
    results = identify(
        control_k=control_k,
        state_k=state_k,
        t=interval,
        use_approximation=use_approximation,
        k_bounds=(k_min, k_max),
        tc_bounds=(tc_min, tc_max),
        delay_steps_range=(delay_steps_min, delay_steps_max),
    )
    class Choice:
        class Print:
            delay_steps = 'Show results sorted by delay steps'
            rmse = 'Show results sorted by RMSE'
            max_residual = 'Show results sorted by max residual'
        plot_with_filter = 'Plot results with filter'
        Exit = 'Exit'
    def plot_with_filter():
        max_rmse = questionary.text('Maximum RMSE (leave empty for no limit):', default='').ask()
        max_residual = questionary.text('Maximum max residual (leave empty for no limit):', default='').ask()
        try:
            max_rmse_val = float(max_rmse) if max_rmse else math.inf
            max_residual_val = float(max_residual) if max_residual else math.inf
        except ValueError:
            print('Invalid input. Please enter numeric values.')
            return
        plot_results(results, timestamps, control_k, state_k, max_rmse=max_rmse_val, max_residual=max_residual_val)
    while True:
        answer = questionary.select(
            'What do you want to do?',
            choices=[
                Choice.Print.delay_steps,
                Choice.Print.rmse,
                Choice.Print.max_residual,
                Choice.plot_with_filter,
                Choice.Exit,
            ]).ask()
        match answer:
            case Choice.Print.delay_steps:
                print_results(results, 'delay_steps')
            case Choice.Print.rmse:
                print_results(results, 'rmse')
            case Choice.Print.max_residual:
                print_results(results, 'max residual')
            case Choice.plot_with_filter:
                plot_with_filter()
            case Choice.Exit:
                break
