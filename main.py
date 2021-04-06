# Main script

import matplotlib.pyplot as plt
import numpy as np
import simpy
from statistics import stdev
from scipy import stats

from classes import Product, Component, Workstation, Inspector

SIZE = 1000
RUNS = 50
MAX_MINUTES = 3300
DELETION_POINT = 300
default = False
debug = False
plot = False
sensitivity = False
alternate = False


def dat_parser(filename: str) -> list:
    """
    Converts .dat file to numpy array
    :param filename: the .dat file to be opened
    :return:
    """
    return list(np.loadtxt(filename))


def generate_input(mean: int) -> list:
    """
    Generate a random exponential distribution
    :param mean: mean of the distribution
    :return: a list of numbers
    """
    return list(np.random.exponential(mean, SIZE))


def generate_confidence(lst: list):
    """
    Used to generate the confidence intervals
    :param lst: the data to be passed in
    :return: the confidence interval
    """
    confidence = 0.95
    v = RUNS - 1
    mean, error = np.mean(lst), stats.sem(lst)
    h = error * stats.t.ppf((1 + confidence) / 2, v)
    return mean - h, mean + h


# Main Script
if __name__ == "__main__":
    print("Starting Simulation ")

    insp1_wait = []
    insp2_wait = []

    ws1_wait = []
    ws2_wait = []
    ws3_wait = []

    ws1_products = []
    ws2_products = []
    ws3_products = []

    if sensitivity:
        MEANS = {"insp1_time": 10.35791, "insp22_time": 15.53690333, "insp23_time": 20.63275667,
                 "ws1_time": 4.604416667, "ws2_time": 11.09260667, "ws3_time": 8.79558}
        steps = 101
        deviation = 0.5  # vary each input value by +-50%
        changes = np.linspace(-deviation * 100, deviation * 100, steps)
        MEAS_TIME = MAX_MINUTES - DELETION_POINT  # time after deletion point over which data is measured
        for m in MEANS:
            newMEANS = dict(MEANS)
            insp1_wait_rate = []
            insp2_wait_rate = []
            ws1_throughput = []
            ws2_throughput = []
            ws3_throughput = []
            ws1_util = []
            ws2_util = []
            ws3_util = []
            for n in range(steps):
                newMEANS[m] = MEANS[m] * ((n / (steps - 1)) + deviation)
                insp1_time = generate_input(newMEANS["insp1_time"])
                insp22_time = generate_input(newMEANS["insp22_time"])
                insp23_time = generate_input(newMEANS["insp23_time"])
                ws1_time = generate_input(newMEANS["ws1_time"])
                ws2_time = generate_input(newMEANS["ws2_time"])
                ws3_time = generate_input(newMEANS["ws3_time"])

                env = simpy.Environment()

                component1 = Component("Component 1")
                component2 = Component("Component 2")
                component3 = Component("Component 3")

                product1 = Product("Product 1", [component1])
                product2 = Product("Product 2", [component1, component2])
                product3 = Product("Product 3", [component1, component3])

                workstation1 = Workstation(env, "Workstation 1", product1, ws1_time, debug, DELETION_POINT)
                workstation2 = Workstation(env, "Workstation 2", product2, ws2_time, debug, DELETION_POINT)
                workstation3 = Workstation(env, "Workstation 3", product3, ws3_time, debug, DELETION_POINT)

                inspector1 = Inspector(env, "Inspector 1", [component1], [insp1_time],
                                       [workstation1, workstation2, workstation3], debug, DELETION_POINT, alternate)
                inspector2 = Inspector(env, "Inspector 2", [component2, component3], [insp22_time, insp23_time],
                                       [workstation2, workstation3], debug, DELETION_POINT, alternate)

                env.run(until=MAX_MINUTES)

                insp1_wait_rate.append(inspector1.blocked_time / MEAS_TIME)
                insp2_wait_rate.append(inspector2.blocked_time / MEAS_TIME)

                ws1_util.append((MEAS_TIME - workstation1.wait_time) / MEAS_TIME)
                ws2_util.append((MEAS_TIME - workstation2.wait_time) / MEAS_TIME)
                ws3_util.append((MEAS_TIME - workstation3.wait_time) / MEAS_TIME)

                ws1_throughput.append(workstation1.products_made / MEAS_TIME)
                ws2_throughput.append(workstation2.products_made / MEAS_TIME)
                ws3_throughput.append(workstation3.products_made / MEAS_TIME)
            plt.plot(changes, insp1_wait_rate)
            plt.plot(changes, insp2_wait_rate)
            plt.xlabel("% Change in " + m)
            plt.ylabel("% Time Idle")
            plt.xticks([-50, -25, 0, 25, 50])
            plt.title("Sensitivity of Inspector Idle Time")
            plt.legend(["Inspector 1", "Inspector 2"])
            plt.show()

            plt.plot(changes, ws1_util)
            plt.plot(changes, ws2_util)
            plt.plot(changes, ws3_util)
            plt.xlabel("% Change in " + m)
            plt.ylabel("Utilization (%)")
            plt.xticks([-50, -25, 0, 25, 50])
            plt.title("Sensitivity of Workstation Utilization")
            plt.legend(["Workstation 1", "Workstation 2", "Workstation 3"])
            plt.show()

            plt.plot(changes, ws1_throughput)
            plt.plot(changes, ws2_throughput)
            plt.plot(changes, ws3_throughput)
            plt.xlabel("% Change in " + m)
            plt.ylabel("Throughput (products/minute)")
            plt.xticks([-50, -25, 0, 25, 50])
            plt.title("Sensitivity of Workstation Throughput")
            plt.legend(["Workstation 1", "Workstation 2", "Workstation 3"])
            plt.show()

    else:
        for i in range(RUNS):

            if default:
                insp1_time = dat_parser("data_files/servinsp1.dat")
                insp22_time = dat_parser("data_files/servinsp22.dat")
                insp23_time = dat_parser("data_files/servinsp23.dat")
                ws1_time = dat_parser("data_files/ws1.dat")
                ws2_time = dat_parser("data_files/ws2.dat")
                ws3_time = dat_parser("data_files/ws3.dat")
            #        elif debug:
            #            insp1_time = [5] * SIZE  # make every time 5 minutes to see if clock is working
            #            insp22_time = [5] * SIZE
            #            insp23_time = [5] * SIZE
            #            ws1_time = [5] * SIZE
            #            ws2_time = [5] * SIZE
            #            ws3_time = [5] * SIZE
            #            MAX_MINUTES = 250
            else:
                MEANS = {"insp1_time": 10.35791, "insp22_time": 15.53690333, "insp23_time": 20.63275667,
                         "ws1_time": 4.604416667, "ws2_time": 11.09260667, "ws3_time": 8.79558}
                insp1_time = generate_input(MEANS["insp1_time"])
                insp22_time = generate_input(MEANS["insp22_time"])
                insp23_time = generate_input(MEANS["insp23_time"])
                ws1_time = generate_input(MEANS["ws1_time"])
                ws2_time = generate_input(MEANS["ws2_time"])
                ws3_time = generate_input(MEANS["ws3_time"])

            env = simpy.Environment()

            component1 = Component("Component 1")
            component2 = Component("Component 2")
            component3 = Component("Component 3")

            product1 = Product("Product 1", [component1])
            product2 = Product("Product 2", [component1, component2])
            product3 = Product("Product 3", [component1, component3])

            workstation1 = Workstation(env, "Workstation 1", product1, ws1_time, debug, DELETION_POINT)
            workstation2 = Workstation(env, "Workstation 2", product2, ws2_time, debug, DELETION_POINT)
            workstation3 = Workstation(env, "Workstation 3", product3, ws3_time, debug, DELETION_POINT)

            inspector1 = Inspector(env, "Inspector 1", [component1], [insp1_time],
                                   [workstation1, workstation2, workstation3], debug, DELETION_POINT, alternate)
            inspector2 = Inspector(env, "Inspector 2", [component2, component3], [insp22_time, insp23_time],
                                   [workstation2, workstation3], debug, DELETION_POINT, alternate)

            env.run(until=MAX_MINUTES)
            print("Finished Run", i + 1)

            insp1_wait.append(inspector1.blocked_time)
            insp2_wait.append(inspector2.blocked_time)

            ws1_wait.append(workstation1.wait_time)
            ws2_wait.append(workstation2.wait_time)
            ws3_wait.append(workstation3.wait_time)

            ws1_products.append(workstation1.products_made)
            ws2_products.append(workstation2.products_made)
            ws3_products.append(workstation3.products_made)

        print("")
        MAX_MINUTES = MAX_MINUTES - DELETION_POINT
        avg_insp1_wait = sum(insp1_wait) / len(insp1_wait)
        avg_insp2_wait = sum(insp2_wait) / len(insp2_wait)

        avg_ws1_wait = sum(ws1_wait) / len(ws1_wait)
        avg_ws2_wait = sum(ws2_wait) / len(ws2_wait)
        avg_ws3_wait = sum(ws3_wait) / len(ws3_wait)

        avg_ws1_prods = sum(ws1_products) / len(ws1_products)
        avg_ws2_prods = sum(ws2_products) / len(ws2_products)
        avg_ws3_prods = sum(ws3_products) / len(ws3_products)

        insp1_wait_conf = generate_confidence(insp1_wait)
        insp2_wait_conf = generate_confidence(insp2_wait)
        ws1_wait_conf = generate_confidence(ws1_wait)
        ws2_wait_conf = generate_confidence(ws2_wait)
        ws3_wait_conf = generate_confidence(ws3_wait)
        ws1_prods_conf = generate_confidence(ws1_products)
        ws2_prods_conf = generate_confidence(ws2_products)
        ws3_prods_conf = generate_confidence(ws3_products)

        std_insp1_wait = stdev(insp1_wait)
        std_insp2_wait = stdev(insp2_wait)

        std_ws1_wait = stdev(ws1_wait)
        std_ws2_wait = stdev(ws2_wait)
        std_ws3_wait = stdev(ws3_wait)

        std_ws1_prods = stdev(ws1_products)
        std_ws2_prods = stdev(ws2_products)
        std_ws3_prods = stdev(ws3_products)

        print(inspector1.name, " wait time: ", avg_insp1_wait)
        print(inspector1.name, " wait time confidence intervals: ", insp1_wait_conf[:2])
        print(inspector2.name, " wait time: ", avg_insp2_wait)
        print(inspector2.name, " wait time confidence intervals: ", insp2_wait_conf[:2])
        print("")
        print(inspector1.name, " wait time percent: ", avg_insp1_wait / MAX_MINUTES)
        print(inspector2.name, " wait time percent: ", avg_insp2_wait / MAX_MINUTES)
        print("")
        print(inspector1.name, " wait time standard deviation: ", std_insp1_wait)
        print(inspector2.name, " wait time standard deviation: ", std_insp2_wait)
        print("")
        if debug:
            for i in [inspector1, inspector2]:
                print("DEBUG: ", i.name, " inspected:")
                for c in i.components_inspected:
                    print("\t", c, ": ", i.components_inspected[c])
            print("")
        print(workstation1.name, " wait time: ", avg_ws1_wait)
        print(workstation1.name, " wait time confidence intervals: ", ws1_wait_conf[:2])
        print(workstation1.name, " wait time: ", avg_ws2_wait)
        print(workstation2.name, " wait time confidence intervals: ", ws2_wait_conf[:2])
        print(workstation3.name, " wait time: ", avg_ws3_wait)
        print(workstation3.name, " wait time confidence intervals: ", ws3_wait_conf[:2])
        print("")
        print(workstation1.name, " wait time standard deviation: ", std_ws1_wait)
        print(workstation2.name, " wait time standard deviation: ", std_ws2_wait)
        print(workstation3.name, " wait time standard deviation: ", std_ws3_wait)
        print("")

        if debug:
            for w in [workstation1, workstation2, workstation3]:
                print("DEBUG: ", w.name, " used:")
                for c in w.components_used:
                    print("\t", c, ": ", w.components_used[c])
            components_inspected = {component1.name: 0, component2.name: 0, component3.name: 0}
            components_buffered = {component1.name: 0, component2.name: 0, component3.name: 0}
            components_used = {component1.name: 0, component2.name: 0, component3.name: 0}
            components_held = {component1.name: 0, component2.name: 0, component3.name: 0}
            for i in [inspector1, inspector2]:
                for c in i.components_inspected:
                    components_inspected[c] += i.components_inspected[c]
            for w in [workstation1, workstation2, workstation3]:
                for c in w.buffers.keys():
                    components_buffered[c.name] += w.buffers[c].level
                for c in w.components_used:
                    components_used[c] += w.components_used[c]
                for c in w.components_held:
                    components_held[c] += w.components_held[c]
            component1_conserved = components_inspected[component1.name] == components_buffered[component1.name] \
                                   + components_used[component1.name]
            component2_conserved = components_inspected[component2.name] == components_buffered[component2.name] \
                                   + components_used[component2.name]
            component3_conserved = components_inspected[component3.name] == components_buffered[component3.name] \
                                   + components_used[component3.name]
            print("DEBUG: ", component1.name, " conserved: ", component1_conserved)
            print("DEBUG: ", component2.name, " conserved: ", component2_conserved)
            print("DEBUG: ", component3.name, " conserved: ", component3_conserved)
            print("")
        print("Workstation 1 Products Made: ", avg_ws1_prods)
        print("Workstation 1 Products Made Confidence interval: ", ws1_prods_conf[:2])
        print("Workstation 2 Products Made: ", avg_ws2_prods)
        print("Workstation 2 Products Made Confidence interval: ", ws2_prods_conf[:2])
        print("Workstation 3 Products Made: ", avg_ws3_prods)
        print("Workstation 3 Products Made Confidence interval: ", ws3_prods_conf[:2])
        print("")
        print(workstation1.name, " products made time standard deviation: ", std_ws1_prods)
        print(workstation2.name, " products made time standard deviation: ", std_ws2_prods)
        print(workstation3.name, " products made time standard deviation: ", std_ws3_prods)
        print("")
        print("Workstation 1 Throughput: ", avg_ws1_prods / MAX_MINUTES)
        print("Workstation 2 Throughput: ", avg_ws2_prods / MAX_MINUTES)
        print("Workstation 3 Throughput: ", avg_ws3_prods / MAX_MINUTES)
        print("")
        print("Workstation 1 Utilization: ", (MAX_MINUTES - avg_ws1_wait) / MAX_MINUTES)
        print("Workstation 2 Utilization: ", (MAX_MINUTES - avg_ws2_wait) / MAX_MINUTES)
        print("Workstation 3 Utilization: ", (MAX_MINUTES - avg_ws3_wait) / MAX_MINUTES)
        print("")
        print("Workstation 1 Mean service time: ", (MAX_MINUTES - avg_ws1_wait) / avg_ws1_prods)
        print("Workstation 2 Mean service time: ", (MAX_MINUTES - avg_ws2_wait) / avg_ws2_prods)
        print("Workstation 3 Mean service time: ", (MAX_MINUTES - avg_ws3_wait) / avg_ws3_prods)

        if plot:
            plt.plot(workstation1.products_time)
            plt.title("Products made by Workstation 1 by Minute")
            plt.xlabel("Minutes")
            plt.xticks(np.arange(0, MAX_MINUTES + 1, 250))
            plt.ylabel("Products Made")
            plt.show()
            plt.plot(workstation2.products_time)
            plt.title("Products made by Workstation 2 by Minute")
            plt.xlabel("Minutes")
            plt.xticks(np.arange(0, MAX_MINUTES + 1, 250))
            plt.ylabel("Products Made")
            plt.show()
            plt.plot(workstation3.products_time)
            plt.title("Products made by Workstation 3 by Minute")
            plt.xlabel("Minutes")
            plt.xticks(np.arange(0, MAX_MINUTES + 1, 250))
            plt.ylabel("Products Made")
            plt.show()
