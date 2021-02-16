# Main script

import numpy as np


def dat_parser(filename: str) -> list:
    return np.loadtxt(filename)


if __name__ == "__main__":
    insp1_time = dat_parser("data_files/servinsp1.dat")
    insp2_time = dat_parser("data_files/servinsp22.dat")
    insp3_time = dat_parser("data_files/servinsp23.dat")
    ws1_time = dat_parser("data_files/ws1.dat")
    ws2_time = dat_parser("data_files/ws2.dat")
    ws3_time = dat_parser("data_files/ws3.dat")
