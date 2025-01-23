# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import matplotlib.pyplot as plt
from scipy.stats import norm
import uproot
import awkward as ak
import numpy as np
import pandas as pd
from scipy.stats import binned_statistic
from scipy.optimize import curve_fit
import argparse


def mean(data):
    m = np.mean(data)
    return m


def std(data):
    s = np.std(data)
    return s


fig = plt.figure(figsize=(12, 8))

data = ak.to_dataframe(
    uproot.open(f"g4/data/chart_eloss_iron.root")["reading"].arrays(library="ak")
)

e_init = data["e_init"]
e_final = data["e_final"]
e_loss = data["e_loss"]

# thickness in mm
e_loss = e_loss / 100

bins = 100
e_range = (0.05, 1000)  # in GeV
log_range = (np.log10(e_range[0]), np.log10(e_range[1]))
edges = 10 ** np.linspace(log_range[0], log_range[1], bins)
mean, _, _ = binned_statistic(
    e_init,
    e_loss,
    bins=edges,
    range=log_range,
    statistic=mean,
)
std, _, _ = binned_statistic(
    e_init,
    e_loss,
    bins=edges,
    range=log_range,
    statistic=std,
)
mid = 0.5 * (edges[:-1] + edges[1:])

# plt.hist(e_init, bins=edges, range=log_range, histtype="step")

# plt.errorbar(mid, mean, yerr=std, fmt="o", linestyle="-", label="Geant4")
plt.plot(mid, mean, marker="o", linestyle="", label="Geant4")

acts_eloss = pd.read_csv("acts/data/eloss_iron.csv")
plt.plot(acts_eloss["p"], acts_eloss["total"], label="ACTS")
# plt.plot(acts_eloss["p"], acts_eloss["bethe"], label="ACTS bethe")

plt.gca().set_xscale("log")
plt.gca().set_yscale("log")

plt.xlabel("Initial momentum [GeV]")
plt.ylabel("Energy loss [GeV/mm]")

plt.legend()

plt.show()
