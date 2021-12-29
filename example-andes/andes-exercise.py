import time
import numpy as np

import andes
import pandas as pd


andes.main.config_logger(stream_level=40)


def load_case(path, ntimes=1):
    """
    Load the matpower case and return ``andes.System`` and load time.

    Parameters
    ----------
    path : str
        path to the test case
    ntimes : int
        repeat the test case ntimes

    Returns
    -------
    andes.System, tload : andes.System, float
        the system and the time to load the case
    """

    # Load the RTS-GMLC case
    t0 = time.time()

    for _ in range(ntimes):
        ss = andes.load(path)

    tload = time.time() - t0

    return ss, (tload / ntimes)


def solve_case(system, ntimes=1):
    """
    Solve the system for n times.

    Parameters
    ----------
    system : andes.System
        the system to solve
    ntimes : int
        repeat the solve ntimes

    Returns
    -------
    t : float
        the time to solve the system
    """

    # setup the system
    system.setup()

    # temporarily disable report writing
    system.files.no_output = True

    # Solve the system
    t0 = time.time()

    for _ in range(ntimes):
        system.PFlow.init()
        system.PFlow.run()

    t = time.time() - t0

    return t / ntimes


def save_report(system, ntimes=1):
    """
    Time the output IO.

    Parameters
    ----------
    system : andes.System
        test system
    """

    # enable outputs
    system.files.no_output = False

    t0 = time.time()
    for _ in range(ntimes):
        system.PFlow.report()

    t = time.time() - t0

    return t / ntimes


def stats(system, mpc_bus, mpc_flow):
    """
    Calculate solution statistics compared with MATPOWER.

    Parameters
    ----------
    system : andes.System
        ANDES system object
    mpc_bus : str
        path to matpower bus results in csv
    mpc_flow : str
        path to matpower line flow in csv
    """

    bus_ref = pd.read_csv("../reference-matpower/results/bus.csv")

    andes_v = ss.dae.y[ss.Bus.v.a]
    andes_a = np.degrees(ss.dae.y[ss.Bus.a.a])

    v_diff = np.abs(andes_v - bus_ref['v_mag'])
    a_diff = np.abs(andes_a - bus_ref['v_ang'])

    df_diff = pd.DataFrame(a_diff, bus_ref.index, ['v_ang'])
    df_diff['v_mag'] = v_diff

    print(df_diff.describe())


if __name__ == '__main__':
    NTIMES = 100
    ss, load_time = load_case('../reference-matpower/RTS_GMLC.m', ntimes = NTIMES)
    solve_time = solve_case(ss, ntimes = NTIMES)
    report_time = save_report(ss, ntimes = NTIMES)
    stats(ss,
          '../reference-matpower//results/bus.csv',
          '../reference-matpower/results/flow.csv')


    print('Power flow exercise with ANDES')
    print('Using RTS-GMLC')
    print('MATPOWER .m case load time: {:.3f} ms'.format(load_time * 1000))
    print('Solve time: {:.3f} ms'.format(solve_time * 1000))
    print('Output report time: {:.3f} ms'.format(report_time * 1000))
