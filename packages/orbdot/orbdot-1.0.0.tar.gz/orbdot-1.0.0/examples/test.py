
from orbdot.star_planet import StarPlanet
from orbdot.analysis import Analyzer


from orbdot.star_planet import StarPlanet
from orbdot.analysis import Analyzer


wasp12 = StarPlanet('settings_files/WASP-12_test.json')
print(wasp12.sys_info)

"""
Model Fitting
"""
# run the constant-period TTV model fit
fit_c = wasp12.run_ttv_fit(['t0', 'P0'], model='constant')

# run the orbital decay TTV model fit
fit_d = wasp12.run_ttv_fit(['t0', 'P0', 'PdE'], model='decay')

# # run the apsidal precession TTV model fit
# fit_p = wasp12.run_ttv_fit(['t0', 'P0', 'e0', 'w0', 'wdE'], model='precession')

"""
Interpretation
"""
# create an ``Analyzer`` instance for the orbital decay results
analyzer = Analyzer(wasp12, fit_d)
analyzer.unknown_companion()
analyzer.orbital_decay_fit()
analyzer.orbital_decay_predicted()
analyzer.apsidal_precession_fit()
analyzer.apsidal_precession_predicted()
analyzer.proper_motion()
analyzer.resolved_binary(2)

# from matplotlib import pyplot as plt
# import orbdot.models.tdv_models as m
# import numpy as np
# P0 = 1.091409179803604
# e0 = 0.00013665726814669036
# w0 = 2.051583488001029
# i0 = 81.22943402052505
# wdE = 0.0504372575437024
# M_s = 1.17
# R_s = 1.749
#
# epochs = wasp12.tdv_data['epoch']
# # = np.arange(-1000, 10000, 1)
# durations_p = m.tdv_precession(P0, e0, w0, i0, wdE, epochs, M_s, R_s)
#
# P0 = 1.091477572826386
# e0 = 0.09773467005608191
# w0 = 1.513870719816205
# i0 = 83.47676664547097
# PdE = -4.180971324765935e-10
# durations_d = m.tdv_decay(P0, e0, w0, i0, PdE, epochs, M_s, R_s)
#
# P0 = 1.0914261703137607
# e0 = 0.11579714389463619
# w0 = 5.43830474209931
# i0 = 84.2080675563851
# durations_c = m.tdv_constant(P0, e0, w0, i0, epochs, M_s, R_s)
#
# tdvs_decay = durations_d - durations_c
# tdvs_precession =  durations_p - durations_c
# tdvs_data = wasp12.tdv_data['dur'] - durations_c
#
# plt.plot(epochs, tdvs_decay)
# plt.plot(epochs, tdvs_precession)
# plt.scatter(epochs, tdvs_data)
#
# plt.ylabel('TDV (minutes)')
# plt.xlabel('Epoch')
# plt.show()