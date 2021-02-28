# Main script

import numpy as np
import simpy
from classes import Product, Component, Workstation, Inspector


def dat_parser(filename: str) -> list:
    """
    Converts .dat file to numpy array
    :param filename: the .dat file to be opened
    :return:
    """
    return list(np.loadtxt(filename))


# Main Script
if __name__ == "__main__":
    insp1_time = dat_parser("data_files/servinsp1.dat")
    insp22_time = dat_parser("data_files/servinsp22.dat")
    insp23_time = dat_parser("data_files/servinsp23.dat")
    ws1_time = dat_parser("data_files/ws1.dat")
    ws2_time = dat_parser("data_files/ws2.dat")
    ws3_time = dat_parser("data_files/ws3.dat")

    env = simpy.Environment()

    component1 = Component("Component 1")
    component2 = Component("Component 2")
    component3 = Component("Component 3")

    product1 = Product("Product 1", [component1])
    product2 = Product("Product 2", [component1, component2])
    product3 = Product("Product 3", [component1, component3])

    workstation1 = Workstation(env, "Workstation 1", product1, ws1_time)
    workstation2 = Workstation(env, "Workstation 2", product2, ws2_time)
    workstation3 = Workstation(env, "Workstation 3", product3, ws3_time)

    inspector1 = Inspector(env, "Inspector 1", [component1], [insp1_time], [workstation1, workstation2, workstation3])
    inspector2 = Inspector(env, "Inspector 2", [component2, component3], [insp22_time, insp23_time],
                           [workstation2, workstation3])
    env.run(until=2500)

    print("")
    print(inspector1.name, " wait time: ", inspector1.blocked_time)
    print(inspector2.name, " wait time: ", inspector2.blocked_time)
    print("")
    print(inspector1.name, " wait time percent: ", inspector1.blocked_time / 2500)
    print(inspector2.name, " wait time percent: ", inspector2.blocked_time / 2500)
    print("")
    print(workstation1.name, " wait time: ", workstation1.wait_time)
    print(workstation2.name, " wait time: ", workstation2.wait_time)
    print(workstation3.name, " wait time: ", workstation3.wait_time)
    print("")
    print("Workstation 1 Products Made: ", workstation1.products_made)
    print("Workstation 2 Products Made: ", workstation2.products_made)
    print("Workstation 3 Products Made: ", workstation3.products_made)
    print("")
    print("Workstation 1 Throughput: ", workstation1.products_made / 2500)
    print("Workstation 2 Throughput: ", workstation2.products_made / 2500)
    print("Workstation 3 Throughput: ", workstation3.products_made / 2500)
    print("")
    print("Workstation 1 Utilization: ", (2500 - workstation1.wait_time) / 2500)
    print("Workstation 2 Utilization: ", (2500 - workstation2.wait_time) / 2500)
    print("Workstation 3 Utilization: ", (2500 - workstation3.wait_time) / 2500)
    print("")
    print("Workstation 1 Mean service time: ", (2500 - workstation1.wait_time) / workstation1.products_made)
    print("Workstation 2 Mean service time: ", (2500 - workstation2.wait_time) / workstation2.products_made)
    print("Workstation 3 Mean service time: ", (2500 - workstation3.wait_time) / workstation3.products_made)
