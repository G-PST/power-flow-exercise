import pypowsybl as pp


def write_output(network, dir_path):
    output_flows(network).to_csv(dir_path + "flow.csv", index=False)
    output_buses(network).to_csv(dir_path + "bus.csv", index=False)


def output_flows(network):
    flows = network.get_lines()[['bus1_id', 'bus2_id', 'p1', 'q1', 'p2', 'q2']].round(
        2)
    flows['branch_n'] = [str(i) + ".0" for i in range(1, len(flows)+1)]
    extract_bus_id(flows, 'bus1_id', 'bus1')
    extract_bus_id(flows, 'bus2_id', 'bus2')
    return flows[['branch_n', 'bus1', 'bus2', 'p1', 'q1', 'p2', 'q2']]


def output_buses(network):
    buses = network.get_buses()[['v_mag', 'v_angle']].round(3)
    ids = range(len(buses))
    buses['bus'] = buses.index
    extract_bus_id(buses, 'bus', 'bus')
    buses['ids'] = ids
    buses.set_index('ids', inplace=True)
    return buses[['bus', 'v_mag', 'v_angle']]


def extract_bus_id(df, name_in, name_out):
    df[name_out] = df[name_in].str.extract(r'(\d{3})') + ".0"
