import csv
import os

import numpy as np
from orbdot.star_planet import StarPlanet

# import orbdot.models.ltt_models as ltt
import orbdot.tools.plots as pl
import orbdot.tools.stats as stat
import orbdot.tools.utilities as utl


def ltt_amplitude(dist, i0_comp, M_comp, M_s):

    # unit conversions
    i0_comp *= np.pi / 180  # degrees to radians
    M_comp *= m.M_earth  # earth masses to m
    M_s *= m.M_sun  # solar masses to m

    return (M_comp / M_s) * (dist / m.c) * np.sin(i0_comp)


def ltt(C, M_interior, time):

    t0_comp, P_comp, e_comp, w_comp, i_comp, O0_c, M_comp = C

    # determine the epoch of the most recent transit
    epoch = (time - t0_comp) / P_comp
    epoch = np.array([int(x) for x in epoch])

    # define the mean motion
    TWOPI = 2 * np.pi
    nu_comp = TWOPI / P_comp

    # calculate true, eccentric, and mean anomalies during transit
    f_tra = (np.pi / 2 - w_comp) % TWOPI
    E_tra = (
        2 * np.arctan(np.sqrt((1 - e_comp) / (1 + e_comp)) * np.tan(f_tra / 2))
    ) % TWOPI
    M_tra = E_tra - e_comp * np.sin(E_tra)

    # calculate the most recent transit center time
    t_tra = t0_comp + P_comp * epoch

    # calculate the time of pericenter passage
    t_p = t_tra - (1 / nu_comp) * M_tra

    # calculate the true anomaly of the planet at the given time
    f_comp = true_anomaly(time, t_p, nu_comp, e_comp)

    # calculate TTV amplitude in seconds
    a_comp = m.get_semi_major_axis_from_period(P_comp, M_interior)  # m
    Q = a_comp * (1 + e_comp)
    amplitude = ltt_amplitude(Q, i_comp, M_comp, M_interior)

    return amplitude * (np.cos(w_comp + f_comp) + e_comp * np.cos(w_comp))


def ltt_ttv_constant(t0, P0, e0, w0, E, C, M_s, primary=True):

    ltt_corr = 0

    if primary:
        t_tra = t0 + P0 * E

        for comp in C:
            ltt_corr -= ltt(comp, M_s, t_tra) / 86400

        return t_tra + ltt_corr

    else:
        t_ecl = t0 + P0 * E + P0 / 2 + 2 * P0 / np.pi * e0 * np.cos(w0)

        for comp in C:
            ltt_corr -= ltt(comp, M_s, t_ecl) / 86400

        return t_ecl + ltt_corr


def ltt_ttv_decay(t0, P0, PdE, e0, w0, E, C, M_s, primary=True):

    ltt_corr = 0

    if primary:
        t_tra = t0 + P0 * E + 0.5 * (E**2) * PdE

        for comp in C:
            ltt_corr -= ltt(comp, M_s, t_tra) / 86400

        return t_tra + ltt_corr

    else:

        t_ecl = (
            t0 + P0 * E + 0.5 * (E**2) * PdE + P0 / 2 + 2 * P0 / np.pi * e0 * np.cos(w0)
        )

        for comp in C:
            ltt_corr -= ltt(comp, M_s, t_ecl) / 86400

        return t_ecl + ltt_corr


def ltt_ttv_precession(t0, P0, PdE, e0, w0, wdE, E, C, M_s, primary=True):
    pass

    ltt_corr = 0

    if primary:
        t_tra = t0 + P0 * E + 0.5 * (E**2) * PdE

        for comp in C:
            ltt_corr -= ltt(comp, M_s, t_tra) / 86400

        return t_tra + ltt_corr

    else:

        t_ecl = (
            t0 + P0 * E + 0.5 * (E**2) * PdE + P0 / 2 + 2 * P0 / np.pi * e0 * np.cos(w0)
        )

        for comp in C:
            ltt_corr -= ltt(comp, M_s, t_ecl) / 86400

        return t_ecl + ltt_corr


# class LightTravelTime:
#     """This class utilizes the capabilities of the :class:`~orbdot.nested_sampling.NestedSampling`
#     class to facilitate model fitting of transit and eclipse mid-times.
#     """
#
#     def __init__(self, ttv_settings, system_info):
#         """Initializes the TransitTiming class.
#
#         Parameters
#         ----------
#         ttv_settings : dict
#             A dictionary specifying directories and settings for the nested sampling analysis.
#
#         """
#         self.M_s = system_info["M_s [M_sun]"]  # star mass in solar masses
#         self.COMP = ((t_c1, P_c1, e_c1, 0.0, i_c1, 0.0, M_c1),
#                      (t_c2, P_c2, e_c2, 0.0, i_c2, 0.0, M_c2),
#                      (t_c3, P_c3, e_c3, 0.0, i_c3, 0.0, M_c3),
#                      (t_c4, P_c4, e_c4, 0.0, i_c4, 0.0, M_c4))
#
#         # directory for saving the output files
#         self.ttv_save_dir = ttv_settings["save_dir"]
#
#         # the requested sampler ('nestle' or 'multinest')
#         self.ttv_sampler = ttv_settings["sampler"]
#
#         # the number of live points for the nested sampling analysis
#         self.ttv_n_points = ttv_settings["n_live_points"]
#
#         # the evidence tolerance for the nested sampling analysis
#         self.ttv_tol = ttv_settings["evidence_tolerance"]
#
#         # create a save directory if not found
#         parent_dir = os.path.abspath(os.getcwd()) + "/"
#
#         try:
#             os.makedirs(os.path.join(parent_dir, ttv_settings["save_dir"]))
#
#         except FileExistsError:
#             pass
#
#     def ltt_loglike_constant(self, theta):
#         """Calculates the log-likelihood for the constant-period timing model.
#
#         This function returns the log-likelihood for the constant-period timing model using the
#         :meth:`~orbdot.models.ttv_models.ttv_constant` method.
#
#         Parameters
#         ----------
#         theta : array_like
#             An array containing parameter values, passed from the sampling algorithm.
#
#         Returns
#         -------
#         float
#             The log-likelihood value.
#
#         """
#         # extract orbital elements
#         orbit, timedp, rvel = self.get_vals(theta)
#         tc, pp, ee, ww, ii, om = orbit
#
#         # check if eccentricity exceeds physical limits
#         if ee >= 1.0:
#             return -1e10  # return a very low likelihood if eccentricity is invalid
#
#         # calculate log-likelihood with transit timing data
#         mod_tr = ltt_ttv_constant(tc, pp, ee, ww, self.ttv_data["epoch"],
#                                       self.COMP, self.M_s)
#         ll = stat.calc_chi2(self.ttv_data["bjd"], mod_tr, self.ttv_data["err"])
#
#         # calculate log-likelihood with eclipse timing data (if available)
#         try:
#             mod_ecl = ltt_ttv_constant(tc, pp, ee, ww, self.ttv_data["epoch"],
#                                            self.COMP, self.M_s, primary=False)
#             ll += stat.calc_chi2(self.ttv_data["bjd_ecl"], mod_ecl, self.ttv_data["err_ecl"])
#
#         except KeyError:
#             pass  # no eclipse timing data available
#
#         return ll
#
#     def ltt_loglike_decay(self, theta):
#         """Calculates the log-likelihood for the orbital decay timing model.
#
#         This function returns the log-likelihood for the orbital decay timing model using the
#         :meth:`~orbdot.models.ttv_models.ttv_decay` method.
#
#         Parameters
#         ----------
#         theta : array_like
#             An array containing parameter values, passed from the sampling algorithm.
#
#         Returns
#         -------
#         float
#             The log-likelihood value.
#
#         """
#         # extract orbital elements and time-dependent variables
#         orbit, timedp, rvel = self.get_vals(theta)
#         tc, pp, ee, ww, ii, om = orbit
#         dp, dw, de, di, do = timedp
#
#         # check if eccentricity exceeds physical limits
#         if ee >= 1.0:
#             return -1e10  # return a very low likelihood if eccentricity is invalid
#
#         # calculate log-likelihood with transit timing data
#         mod_tr = ltt_ttv_decay(tc, pp, dp, ee, ww, self.ttv_data["epoch"], self.COMP, self.M_s)
#         ll = stat.calc_chi2(self.ttv_data["bjd"], mod_tr, self.ttv_data["err"])
#
#         # calculate log-likelihood with eclipse timing data (if available)
#         try:
#             mod_ecl = ltt_ttv_decay(tc, pp, dp, ee, ww, self.ttv_data["epoch"],
#                                         self.COMP, self.M_s, primary=False)
#             ll += stat.calc_chi2(
#                 self.ttv_data["bjd_ecl"], mod_ecl, self.ttv_data["err_ecl"]
#             )
#
#         except KeyError:
#             pass  # no eclipse timing data available
#
#         return ll
#
#     def run_ttv_fit(self, free_params, model="constant", file_suffix="", make_plot=True,
#                     sigma_clip=False, clip_model="linear",):
#
#         if model == "constant":
#             res = self.run_ltt_constant(
#                 free_params, file_suffix, make_plot, sigma_clip, clip_model, save=True
#             )
#
#         elif model == "decay":
#             res = self.run_ltt_decay(
#                 free_params, file_suffix, make_plot, sigma_clip, clip_model, save=True
#             )
#
#         elif model == "precession":
#             res = self.run_ltt_precession(
#                 free_params, file_suffix, make_plot, sigma_clip, clip_model, save=True
#             )
#
#         else:
#             raise ValueError(
#                 f"The string '{model}' does not represent a valid TTV model. Options "
#                 "are: 'constant', 'decay', or 'precession'."
#             )
#
#         return res
#
#     def run_ltt_constant(self, free_params, suffix, plot, clip, clip_method, save):
#         """Run a fit of the constant-period ltt model.
#         """
#         free_params = np.array(free_params, dtype="<U16")
#
#         try:
#             self.ttv_data
#
#         except AttributeError:
#             raise Exception(
#                 "\n\nNo transit and/or eclipse mid-time data was detected. Please give "
#                 "a valid\npath name in the settings file before running the TTV fit."
#             )
#
#         # define parameters that are not in the model
#         illegal_params = [
#             "i0",
#             "O0",
#             "PdE",
#             "wdE",
#             "idE",
#             "edE",
#             "OdE",
#             "K",
#             "v0",
#             "jit",
#             "dvdt",
#             "ddvdt",
#             "K_tide",
#         ]
#
#         # raise an exception if the free parameter(s) are not valid
#         utl.raise_not_valid_param_error(free_params, self.legal_params, illegal_params)
#
#         self.plot_settings["TTV_PLOT"]["data_file" + suffix] = self.ttv_data_filename
#
#         if clip:
#             print("-" * 100)
#             print("Running sigma-clipping routine on transit mid-times")
#             print("-" * 100)
#
#             cleaned_filename = self.ttv_save_dir + "mid_times_cleaned" + suffix + ".txt"
#             clipped_filename = self.ttv_save_dir + "mid_times_clipped" + suffix + ".txt"
#
#             self.clip(cleaned_filename, clipped_filename, method=clip_method)
#
#             self.plot_settings["TTV_PLOT"]["data_file"] = cleaned_filename
#             self.plot_settings["TTV_PLOT"]["clipped_data_file"] = clipped_filename
#
#         if save:
#             print("-" * 100)
#             print(
#                 f"Running constant-period TTV fit with free parameters: {free_params}"
#             )
#             print("-" * 100)
#
#         # specify a prefix for output file names
#         prefix = self.ttv_save_dir + "ltt_ttv_constant"
#
#         # if selected, run the Nestle sampling algorithm
#         if self.ttv_sampler == "nestle":
#             res, samples, random_samples = self.run_nestle(
#                 self.ltt_loglike_constant,
#                 free_params,
#                 "multi",
#                 self.ttv_n_points,
#                 self.ttv_tol,
#             )
#
#         # if selected, run the MultiNest sampling algorithm
#         elif self.ttv_sampler == "multinest":
#             res, samples, random_samples = self.run_multinest(
#                 self.ltt_loglike_constant,
#                 free_params,
#                 self.ttv_n_points,
#                 self.ttv_tol,
#                 prefix + suffix,
#             )
#         else:
#             raise ValueError("Unrecognized sampler, specify 'nestle' or 'multinest'")
#
#         if save:
#
#             rf = prefix + "_results" + suffix + ".json"
#             sf = prefix + "_random_samples" + suffix + ".txt"
#
#             res["model"] = "ltt_ttv_constant"
#             res["suffix"] = suffix
#             res["results_filename"] = rf
#             res["samples_filename"] = sf
#
#             self.save_results(
#                 random_samples,
#                 samples,
#                 res,
#                 free_params,
#                 self.ttv_sampler,
#                 suffix,
#                 prefix,
#                 illegal_params,
#             )
#
#             # generate a TTV ("O-C") plot
#             self.plot_settings["TTV_PLOT"]["ltt_ttv_constant_results_file" + suffix] = rf
#             self.plot_settings["TTV_PLOT"]["ltt_ttv_constant_samples_file" + suffix] = sf
#
#             if plot:
#                 plot_filename = prefix + "_plot" + suffix
#                 self.make_ttv_plot(self.plot_settings, plot_filename, suffix=suffix)
#
#         return res
#
#
#     def make_ltt_plot(self, plot_settings, outfile, suffix=""):
#         """Generates a transit timing variation (TTV) plot.
#
#         Parameters
#         ----------
#         plot_settings : dict
#             A dictionary containing plot settings.
#         outfile : str
#             The file path for saving the plot.
#         suffix : str, optional
#             Optional string for matching model fit results.
#
#         Returns
#         -------
#         None
#
#         """
#         print("-" * 100)
#         print("Generating LTT plot...")
#         print("-" * 100)
#
#         # load plot settings
#         plt.rcParams.update(plot_settings["TTV_PLOT"]["rcParams"])
#
#         data_colors = plot_settings["TTV_PLOT"]["data_colors"]
#         dfmt = plot_settings["TTV_PLOT"]["data_fmt"]
#         dms = plot_settings["TTV_PLOT"]["data_markersize"]
#         delw = plot_settings["TTV_PLOT"]["data_err_linewidth"]
#         decap = plot_settings["TTV_PLOT"]["data_err_capsize"]
#
#         s_alpha = plot_settings["TTV_PLOT"]["samples_alpha"]
#         s_lw = plot_settings["TTV_PLOT"]["samples_linewidth"]
#         m_alpha = plot_settings["TTV_PLOT"]["model_alpha"]
#         m_lw = plot_settings["TTV_PLOT"]["model_linewidth"]
#
#         bbox = plot_settings["TTV_PLOT"]["bbox_inches"]
#         dpi = plot_settings["TTV_PLOT"]["dpi"]
#         pad_inches = plot_settings["TTV_PLOT"]["pad_inches"]
#
#         # load full dataset
#         data_file = plot_settings["TTV_PLOT"]["data_file" + suffix]
#         data = utl.read_ttv_data(data_file)
#
#         try:
#             # load constant-period fit results
#             with open(
#                 plot_settings["TTV_PLOT"]["ltt_ttv_constant_results_file" + suffix]
#             ) as jf:
#                 rf_c = json.load(jf)
#                 res_c = rf_c["params"]
#
#             # load constant-period samples
#             s_orb_c, s_tdp_c, s_rv_c = read_random_samples(
#                 plot_settings["TTV_PLOT"]["ltt_ttv_constant_samples_file" + suffix]
#             )
#
#         except KeyError:
#             print(
#                 f"ERROR: Missing '*_results{suffix}.json' file for constant-period TTV fit. The O-C plot "
#                 "cannot be generated without first fitting the constant-period TTV model.\n\n"
#             )
#             return
#
#         transits = False
#         eclipses = False
#
#         if data["epoch"].size > 0 and data["epoch_ecl"].size > 0:
#             transits = True
#             eclipses = True
#
#         elif data["epoch"].size > 0:
#             transits = True
#
#         elif data["epoch_ecl"].size > 0:
#             eclipses = True
#
#         if transits and eclipses:
#             fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=True)
#         else:
#             fig, ax1 = plt.subplots(1, 1)
#
#         # define a full range of epochs
#         preE = plot_settings["TTV_PLOT"]["num_epochs_pre_data"]
#         postE = plot_settings["TTV_PLOT"]["num_epochs_post_data"]
#
#         if transits:
#             epochs_full = np.arange(
#                 min(data["epoch"]) - preE, max(data["epoch"]) + postE, 1
#             )
#
#         else:
#             epochs_full = np.arange(
#                 min(data["epoch_ecl"]) - preE, max(data["epoch_ecl"]) + postE, 1
#             )
#
#         if transits and eclipses:
#             # generate best-fit constant period model (transits) over full epoch range
#             cmod_full = ltt_ttv_constant(
#                 res_c["t0"][0],
#                 res_c["P0"][0],
#                 res_c["e0"][0],
#                 res_c["w0"][0],
#                 epochs_full, self.COMP, self.M_s,
#                 primary=True,
#             )
#
#             # plot best-fit constant period model (transits) over full epoch range
#             ax1.plot(
#                 epochs_full,
#                 np.array(cmod_full - cmod_full) * 1440,
#                 color="darkgrey",
#                 label="_",
#                 linewidth=m_lw,
#                 alpha=m_alpha,
#             )
#
#             # generate best-fit constant-period model (eclipses) over full epoch range
#             cmod_full_ecl = ltt_ttv_constant(
#                 res_c["t0"][0],
#                 res_c["P0"][0],
#                 res_c["e0"][0],
#                 res_c["w0"][0],
#                 epochs_full, self.COMP, self.M_s,
#                 primary=False,
#             )
#
#             # plot best-fit constant period model (eclipses) over full epoch range
#             ax2.plot(
#                 epochs_full,
#                 np.array(cmod_full_ecl - cmod_full_ecl) * 1440,
#                 color="darkgrey",
#                 label="Constant Period",
#                 linewidth=m_lw,
#                 alpha=1,
#             )
#
#         elif transits and not eclipses:
#             # generate best-fit constant period model (transits) over full epoch range
#             cmod_full = ltt_ttv_constant(
#                 res_c["t0"][0],
#                 res_c["P0"][0],
#                 res_c["e0"][0],
#                 res_c["w0"][0],
#                 epochs_full, self.COMP, self.M_s,
#                 primary=True,
#             )
#
#             # plot best-fit constant period model (transits) over full epoch range
#             ax1.plot(
#                 epochs_full,
#                 np.array(cmod_full - cmod_full) * 1440,
#                 color="darkgrey",
#                 label="Constant Period",
#                 linewidth=m_lw,
#                 alpha=m_alpha,
#             )
#
#         elif eclipses and not transits:
#             # generate best-fit constant-period model (eclipses) over full epoch range
#             cmod_full_ecl = ltt_ttv_constant(
#                 res_c["t0"][0],
#                 res_c["P0"][0],
#                 res_c["e0"][0],
#                 res_c["w0"][0],
#                 epochs_full, self.COMP, self.M_s,
#                 primary=False,
#             )
#
#             # plot best-fit constant period model (eclipses) over full epoch range
#             ax1.plot(
#                 epochs_full,
#                 np.array(cmod_full_ecl - cmod_full_ecl) * 1440,
#                 color="darkgrey",
#                 label="Constant Period",
#                 linewidth=m_lw,
#                 alpha=1,
#             )
#
#         # plot 300 random samples from constant-period model fit
#         for i in range(np.shape(s_orb_c)[0]):
#
#             if transits and eclipses:
#
#                 # generate constant-period model (transits)
#                 smod_c = ltt_ttv_constant(
#                     s_orb_c[i][0],
#                     s_orb_c[i][1],
#                     s_orb_c[i][2],
#                     s_orb_c[i][3],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=True,
#                 )
#
#                 # plot constant-period model (transits)
#                 ax1.plot(
#                     epochs_full,
#                     np.array(smod_c - cmod_full) * 1440,
#                     color="darkgrey",
#                     label="_",
#                     linewidth=s_lw,
#                     alpha=s_alpha,
#                 )
#
#                 # generate constant-period model (eclipses)
#                 smod_c_ecl = ltt_ttv_constant(
#                     s_orb_c[i][0],
#                     s_orb_c[i][1],
#                     s_orb_c[i][2],
#                     s_orb_c[i][3],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=False,
#                 )
#
#                 # plot constant-period model (eclipses)
#                 ax2.plot(
#                     epochs_full,
#                     np.array(smod_c_ecl - cmod_full_ecl) * 1440,
#                     color="darkgrey",
#                     label="_",
#                     linewidth=s_lw,
#                     alpha=s_alpha,
#                 )
#
#             elif transits and not eclipses:
#                 # generate constant-period model (transits)
#                 smod_c = ltt_ttv_constant(
#                     s_orb_c[i][0],
#                     s_orb_c[i][1],
#                     s_orb_c[i][2],
#                     s_orb_c[i][3],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=True,
#                 )
#
#                 # plot constant-period model (transits)
#                 ax1.plot(
#                     epochs_full,
#                     np.array(smod_c - cmod_full) * 1440,
#                     color="darkgrey",
#                     label="_",
#                     linewidth=s_lw,
#                     alpha=s_alpha,
#                 )
#
#             elif eclipses and not transits:
#                 # generate constant-period model (eclipses)
#                 smod_c_ecl = ltt_ttv_constant(
#                     s_orb_c[i][0],
#                     s_orb_c[i][1],
#                     s_orb_c[i][2],
#                     s_orb_c[i][3],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=False,
#                 )
#
#                 # plot constant-period model (eclipses)
#                 ax1.plot(
#                     epochs_full,
#                     np.array(smod_c_ecl - cmod_full_ecl) * 1440,
#                     color="darkgrey",
#                     label="_",
#                     linewidth=s_lw,
#                     alpha=s_alpha,
#                 )
#
#         try:
#
#             # load orbital decay fit results
#             with open(plot_settings["TTV_PLOT"]["ltt_ttv_decay_results_file" + suffix]) as jf:
#                 rf_d = json.load(jf)
#                 res_d = rf_d["params"]
#
#             # load orbital decay samples
#             s_orb_d, s_tdp_d, s_rv_d = read_random_samples(
#                 plot_settings["TTV_PLOT"]["ltt_ttv_decay_samples_file" + suffix]
#             )
#
#             if transits and eclipses:
#                 # generate best-fit orbital decay model (transits) over full epoch range
#                 dmod_full = ltt_ttv_decay(
#                     res_d["t0"][0],
#                     res_d["P0"][0],
#                     res_d["PdE"][0],
#                     res_d["e0"][0],
#                     res_d["w0"][0],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=True,
#                 )
#
#                 # plot best-fit orbital decay model (transits) over full epoch range
#                 ax1.plot(
#                     epochs_full,
#                     np.array(dmod_full - cmod_full) * 1440,
#                     color="#9c3535",
#                     label="_",
#                     linewidth=m_lw,
#                     alpha=m_alpha,
#                 )
#
#                 # generate best-fit orbital decay model (eclipses) over full epoch range
#                 dmod_full_ecl = ltt_ttv_decay(
#                     res_d["t0"][0],
#                     res_d["P0"][0],
#                     res_d["PdE"][0],
#                     res_d["e0"][0],
#                     res_d["w0"][0],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=False,
#                 )
#
#                 # plot best-fit orbital decay model (eclipses) over full epoch range
#                 ax2.plot(
#                     epochs_full,
#                     np.array(dmod_full_ecl - cmod_full_ecl) * 1440,
#                     color="#9c3535",
#                     label="Orbital Decay",
#                     linewidth=m_lw,
#                     alpha=m_alpha,
#                 )
#
#             elif transits and not eclipses:
#
#                 # generate best-fit orbital decay model (transits) over full epoch range
#                 dmod_full = ltt_ttv_decay(
#                     res_d["t0"][0],
#                     res_d["P0"][0],
#                     res_d["PdE"][0],
#                     res_d["e0"][0],
#                     res_d["w0"][0],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=True,
#                 )
#
#                 # plot best-fit orbital decay model (transits) over full epoch range
#                 ax1.plot(
#                     epochs_full,
#                     np.array(dmod_full - cmod_full) * 1440,
#                     color="#9c3535",
#                     label="Orbital Decay",
#                     linewidth=m_lw,
#                     alpha=m_alpha,
#                 )
#
#             elif eclipses and not transits:
#                 # generate best-fit orbital decay model (eclipses) over full epoch range
#                 dmod_full_ecl = ltt_ttv_decay(
#                     res_d["t0"][0],
#                     res_d["P0"][0],
#                     res_d["PdE"][0],
#                     res_d["e0"][0],
#                     res_d["w0"][0],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=False,
#                 )
#
#                 # plot best-fit orbital decay model (eclipses) over full epoch range
#                 ax1.plot(
#                     epochs_full,
#                     np.array(dmod_full_ecl - cmod_full_ecl) * 1440,
#                     color="#9c3535",
#                     label="Orbital Decay",
#                     linewidth=m_lw,
#                     alpha=m_alpha,
#                 )
#
#             # plot 300 random samples orbital decay model fit
#             for i in range(np.shape(s_orb_d)[0]):
#
#                 if transits and eclipses:
#
#                     # generate orbital decay model (transits)
#                     smod_d = ltt_ttv_decay(
#                         s_orb_d[i][0],
#                         s_orb_d[i][1],
#                         s_tdp_d[i][0],
#                         s_orb_d[i][2],
#                         s_orb_d[i][3],
#                         epochs_full, self.COMP, self.M_s,
#                         primary=True,
#                     )
#
#                     # generate orbital decay model (transits)
#                     ax1.plot(
#                         epochs_full,
#                         np.array(smod_d - cmod_full) * 1440,
#                         color="#9c3535",
#                         label="_",
#                         linewidth=s_lw,
#                         alpha=s_alpha,
#                     )
#
#                     # generate orbital decay model (eclipses)
#                     smod_d_ecl = ltt_ttv_decay(
#                         s_orb_d[i][0],
#                         s_orb_d[i][1],
#                         s_tdp_d[i][0],
#                         s_orb_d[i][2],
#                         s_orb_d[i][3],
#                         epochs_full, self.COMP, self.M_s,
#                         primary=False,
#                     )
#
#                     # generate orbital decay model (eclipses)
#                     ax2.plot(
#                         epochs_full,
#                         np.array(smod_d_ecl - cmod_full_ecl) * 1440,
#                         color="#9c3535",
#                         label="_",
#                         linewidth=s_lw,
#                         alpha=s_alpha,
#                     )
#
#                 elif transits and not eclipses:
#                     # generate orbital decay model (transits)
#                     smod_d = ltt_ttv_decay(
#                         s_orb_d[i][0],
#                         s_orb_d[i][1],
#                         s_tdp_d[i][0],
#                         s_orb_d[i][2],
#                         s_orb_d[i][3],
#                         epochs_full, self.COMP, self.M_s,
#                         primary=True,
#                     )
#
#                     # generate orbital decay model (transits)
#                     ax1.plot(
#                         epochs_full,
#                         np.array(smod_d - cmod_full) * 1440,
#                         color="#9c3535",
#                         label="_",
#                         linewidth=s_lw,
#                         alpha=s_alpha,
#                     )
#
#                 elif eclipses and not transits:
#
#                     # generate orbital decay model (eclipses)
#                     smod_d_ecl = ltt_ttv_decay(
#                         s_orb_d[i][0],
#                         s_orb_d[i][1],
#                         s_tdp_d[i][0],
#                         s_orb_d[i][2],
#                         s_orb_d[i][3],
#                         epochs_full, self.COMP, self.M_s,
#                         primary=False,
#                     )
#
#                     # generate orbital decay model (eclipses)
#                     ax1.plot(
#                         epochs_full,
#                         np.array(smod_d_ecl - cmod_full_ecl) * 1440,
#                         color="#9c3535",
#                         label="_",
#                         linewidth=s_lw,
#                         alpha=s_alpha,
#                     )
#
#         except KeyError:
#             print(" --> No orbital decay fit results detected.")
#
#         try:
#
#             # load apsidal precession fit results
#             with open(
#                 plot_settings["TTV_PLOT"]["ltt_ttv_precession_results_file" + suffix]
#             ) as jf:
#                 rf_p = json.load(jf)
#                 res_p = rf_p["params"]
#
#             # load apsidal precession samples
#             s_orb_p, s_tdp_p, s_rv_p = read_random_samples(
#                 plot_settings["TTV_PLOT"]["ltt_ttv_precession_samples_file" + suffix]
#             )
#
#             if transits and eclipses:
#
#                 # generate best-fit apsidal precession model (transits) over full epoch range
#                 pmod_full = ltt_ttv_precession(
#                     res_p["t0"][0],
#                     res_p["P0"][0],
#                     res_p["e0"][0],
#                     res_p["w0"][0],
#                     res_p["wdE"][0],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=True,
#                 )
#
#                 # plot best-fit apsidal precession model (transits) over full epoch range
#                 ax1.plot(
#                     epochs_full,
#                     np.array(pmod_full - cmod_full) * 1440,
#                     color="cadetblue",
#                     label="_",
#                     linewidth=m_lw,
#                     alpha=m_alpha,
#                 )
#
#                 # generate best-fit apsidal precession model (eclipses) over full epoch range
#                 pmod_full_ecl = ltt_ttv_precession(
#                     res_p["t0"][0],
#                     res_p["P0"][0],
#                     res_p["e0"][0],
#                     res_p["w0"][0],
#                     res_p["wdE"][0],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=False,
#                 )
#
#                 # plot best-fit apsidal precession model (eclipses) over full epoch range
#                 ax2.plot(
#                     epochs_full,
#                     np.array(pmod_full_ecl - cmod_full_ecl) * 1440,
#                     color="cadetblue",
#                     label="Apsidal Precession",
#                     linewidth=m_lw,
#                     alpha=m_alpha,
#                 )
#
#             elif transits and not eclipses:
#                 # generate best-fit apsidal precession model (transits) over full epoch range
#                 pmod_full = ltt_ttv_precession(
#                     res_p["t0"][0],
#                     res_p["P0"][0],
#                     res_p["e0"][0],
#                     res_p["w0"][0],
#                     res_p["wdE"][0],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=True,
#                 )
#
#                 # plot best-fit apsidal precession model (transits) over full epoch range
#                 ax1.plot(
#                     epochs_full,
#                     np.array(pmod_full - cmod_full) * 1440,
#                     color="cadetblue",
#                     label="Apsidal Precession",
#                     linewidth=m_lw,
#                     alpha=m_alpha,
#                 )
#
#             elif eclipses and not transits:
#                 # generate best-fit apsidal precession model (eclipses) over full epoch range
#                 pmod_full_ecl = ltt_ttv_precession(
#                     res_p["t0"][0],
#                     res_p["P0"][0],
#                     res_p["e0"][0],
#                     res_p["w0"][0],
#                     res_p["wdE"][0],
#                     epochs_full, self.COMP, self.M_s,
#                     primary=False,
#                 )
#
#                 # plot best-fit apsidal precession model (eclipses) over full epoch range
#                 ax1.plot(
#                     epochs_full,
#                     np.array(pmod_full_ecl - cmod_full_ecl) * 1440,
#                     color="cadetblue",
#                     label="Apsidal Precession",
#                     linewidth=m_lw,
#                     alpha=m_alpha,
#                 )
#
#             # plot 300 random samples apsidal precession model fit
#             for i in range(np.shape(s_orb_p)[0]):
#
#                 if transits and eclipses:
#                     # generate apsidal precession model (transits)
#                     smod_p = ltt_ttv_precession(
#                         s_orb_p[i][0],
#                         s_orb_p[i][1],
#                         s_orb_p[i][2],
#                         s_orb_p[i][3],
#                         s_tdp_p[i][1],
#                         epochs_full, self.COMP, self.M_s,
#                         primary=True,
#                     )
#
#                     # plot apsidal precession model (transits)
#                     ax1.plot(
#                         epochs_full,
#                         np.array(smod_p - cmod_full) * 1440,
#                         color="cadetblue",
#                         label="_",
#                         linewidth=s_lw,
#                         alpha=s_alpha,
#                     )
#
#                     # generate apsidal precession model (eclipses)
#                     smod_p_ecl = ltt_ttv_precession(
#                         s_orb_p[i][0],
#                         s_orb_p[i][1],
#                         s_orb_p[i][2],
#                         s_orb_p[i][3],
#                         s_tdp_p[i][1],
#                         epochs_full, self.COMP, self.M_s,
#                         primary=False,
#                     )
#
#                     # plot apsidal precession model (eclipses)
#                     ax2.plot(
#                         epochs_full,
#                         np.array(smod_p_ecl - cmod_full_ecl) * 1440,
#                         color="cadetblue",
#                         label="_",
#                         linewidth=s_lw,
#                         alpha=s_alpha,
#                     )
#
#                 elif transits and not eclipses:
#                     # generate apsidal precession model (transits)
#                     smod_p = ltt_ttv_precession(
#                         s_orb_p[i][0],
#                         s_orb_p[i][1],
#                         s_orb_p[i][2],
#                         s_orb_p[i][3],
#                         s_tdp_p[i][1],
#                         epochs_full, self.COMP, self.M_s,
#                         primary=True,
#                     )
#
#                     # plot apsidal precession model (transits)
#                     ax1.plot(
#                         epochs_full,
#                         np.array(smod_p - cmod_full) * 1440,
#                         color="cadetblue",
#                         label="_",
#                         linewidth=s_lw,
#                         alpha=s_alpha,
#                     )
#
#                 elif eclipses and not transits:
#                     # generate apsidal precession model (eclipses)
#                     smod_p_ecl = ltt_ttv_precession(
#                         s_orb_p[i][0],
#                         s_orb_p[i][1],
#                         s_orb_p[i][2],
#                         s_orb_p[i][3],
#                         s_tdp_p[i][1],
#                         epochs_full, self.COMP, self.M_s,
#                         primary=False,
#                     )
#
#                     # plot apsidal precession model (eclipses)
#                     ax1.plot(
#                         epochs_full,
#                         np.array(smod_p_ecl - cmod_full_ecl) * 1440,
#                         color="cadetblue",
#                         label="_",
#                         linewidth=s_lw,
#                         alpha=s_alpha,
#                     )
#
#         except KeyError:
#             print(" --> No apsidal precession fit results detected.\n")
#
#         if transits and eclipses:
#             # generate best-fit constant-period model (transits)
#             cmod_obs = ltt_ttv_constant(
#                 res_c["t0"][0],
#                 res_c["P0"][0],
#                 res_c["e0"][0],
#                 res_c["w0"][0],
#                 data["epoch"], self.COMP, self.M_s,
#                 primary=True,
#             )
#
#             # calculate O-C values for transit data
#             oc = data["bjd"] - cmod_obs
#
#             # generate best-fit constant-period model (eclipses)
#             cmod_obs_ecl = ltt_ttv_constant(
#                 res_c["t0"][0],
#                 res_c["P0"][0],
#                 res_c["e0"][0],
#                 res_c["w0"][0],
#                 data["epoch_ecl"], self.COMP, self.M_s,
#                 primary=False,
#             )
#
#             # calculate O-C values for eclipse data
#             oc_ecl = data["bjd_ecl"] - cmod_obs_ecl
#
#         elif transits and not eclipses:
#             # generate best-fit constant-period model (transits)
#             cmod_obs = ltt_ttv_constant(
#                 res_c["t0"][0],
#                 res_c["P0"][0],
#                 res_c["e0"][0],
#                 res_c["w0"][0],
#                 data["epoch"], self.COMP, self.M_s,
#                 primary=True,
#             )
#
#             # calculate O-C values for transit data
#             oc = data["bjd"] - cmod_obs
#
#         elif eclipses and not transits:
#             # generate best-fit constant-period model (eclipses)
#             cmod_obs_ecl = ltt_ttv_constant(
#                 res_c["t0"][0],
#                 res_c["P0"][0],
#                 res_c["e0"][0],
#                 res_c["w0"][0],
#                 data["epoch_ecl"], self.COMP, self.M_s,
#                 primary=False,
#             )
#
#             # calculate O-C values for eclipse data
#             oc_ecl = data["bjd_ecl"] - cmod_obs_ecl
#
#         # plot data, separating sources into different colours and labels
#         sources_unique = np.unique(list(data["src"]) + list(data["src_ecl"]))
#         num_sources = len(sources_unique)
#
#         if transits and eclipses:
#
#             # iterate through transit data sources
#             for i in range(num_sources):
#                 # plot transit data
#                 indx = np.where(data["src"] == sources_unique[i])[0]
#                 ax1.errorbar(
#                     np.take(data["epoch"], indx),
#                     np.array(np.take(oc, indx)) * 1440,
#                     yerr=np.take(data["err"], indx) * 1440,
#                     label=sources_unique[i],
#                     color=data_colors[i],
#                     ecolor=data_colors[i],
#                     fmt=dfmt,
#                     markersize=dms,
#                     elinewidth=delw,
#                     capsize=decap,
#                 )
#
#             # iterate through eclipse data sources
#             for i in range(num_sources):
#                 # plot eclipse data
#                 indx = np.where(data["src_ecl"] == sources_unique[i])[0]
#                 ax2.errorbar(
#                     np.take(data["epoch_ecl"], indx),
#                     np.array(np.take(oc_ecl, indx)) * 1440,
#                     yerr=np.take(data["err_ecl"], indx) * 1440,
#                     label="_",
#                     color=data_colors[i],
#                     ecolor=data_colors[i],
#                     fmt=dfmt,
#                     markersize=dms,
#                     elinewidth=delw,
#                     capsize=decap,
#                 )
#
#         elif transits and not eclipses:
#             # iterate through transit data sources
#             for i in range(num_sources):
#                 # plot transit data
#                 indx = np.where(data["src"] == sources_unique[i])[0]
#                 ax1.errorbar(
#                     np.take(data["epoch"], indx),
#                     np.array(np.take(oc, indx)) * 1440,
#                     yerr=np.take(data["err"], indx) * 1440,
#                     label=sources_unique[i],
#                     color=data_colors[i],
#                     ecolor=data_colors[i],
#                     fmt=dfmt,
#                     markersize=dms,
#                     elinewidth=delw,
#                     capsize=decap,
#                 )
#
#         elif eclipses and not transits:
#             # iterate through eclipse data sources
#             for i in range(num_sources):
#                 # plot eclipse data
#                 indx = np.where(data["src_ecl"] == sources_unique[i])[0]
#                 ax1.errorbar(
#                     np.take(data["epoch_ecl"], indx),
#                     np.array(np.take(oc_ecl, indx)) * 1440,
#                     yerr=np.take(data["err_ecl"], indx) * 1440,
#                     label="_",
#                     color=data_colors[i],
#                     ecolor=data_colors[i],
#                     fmt=dfmt,
#                     markersize=dms,
#                     elinewidth=delw,
#                     capsize=decap,
#                 )
#
#         # plot data removed in sigma clipping process
#         try:
#             clipped_data = utl.read_ttv_data(plot_settings["TTV_PLOT"]["clipped_data_file"])
#
#             # generate best-fit constant-period model for clipped epochs (transits)
#             cmod_obs_clipped = ltt_ttv_constant(
#                 res_c["t0"][0],
#                 res_c["P0"][0],
#                 res_c["e0"],
#                 res_c["w0"],
#                 clipped_data["epoch"], self.COMP, self.M_s,
#             )
#
#             # calculate O-C values for clipped transit data
#             clipped_OCs = clipped_data["bjd"] - cmod_obs_clipped
#
#             # plot clipped data O-C
#             ax1.errorbar(
#                 clipped_data["epoch"],
#                 np.array(clipped_OCs) * 1440,
#                 yerr=clipped_data["err"] * 1440,
#                 label="Excluded",
#                 fmt="x",
#                 markersize="5",
#                 ecolor="r",
#                 elinewidth=0.8,
#                 color="r",
#             )
#
#         except KeyError:
#             pass
#
#         # plot vertical lines for reference dates
#         trans = transforms.blended_transform_factory(ax1.transData, ax1.transAxes)
#
#         date_refs = plot_settings["TTV_PLOT"]["reference_dates"]
#         t_ref = Time(date_refs, format="iso", in_subfmt="date")
#         dates_jd = t_ref.to_value("jd", subfmt="float")
#         dates_e = utl.calculate_epochs(
#             res_c["t0"][0], res_c["P0"][0], dates_jd, primary=True
#         )
#
#         t_t0 = Time([str(res_c["t0"][0])], format="jd", scale="tdb")  # add t0
#         date_refs = list(date_refs)
#         date_refs.append(t_t0.to_value("iso", subfmt="date")[0])
#         dates_e.append(0)
#
#         # remove month and day
#         dates_year = [s.split("-")[0] for s in date_refs]
#         for i, date in enumerate(dates_e):
#
#             ax1.axvline(x=date, linewidth=0.5, linestyle="-", color="grey")
#             ax1.text(
#                 date,
#                 0.05,
#                 dates_year[i],
#                 rotation=90,
#                 fontsize=12,
#                 ha="right",
#                 va="bottom",
#                 transform=trans,
#             )
#
#             try:
#                 ax2.axvline(x=date, linewidth=0.5, linestyle="-", color="grey", label="_")
#
#             except UnboundLocalError:
#                 pass
#
#         # finish plot
#         plt.xlabel("Epoch")
#         ax1.set_ylabel("Timing Deviation (min)")
#
#         plt.xlim(epochs_full[0], epochs_full[-1])
#         plt.ylim(
#             plot_settings["TTV_PLOT"]["y_axis_limits"][0],
#             plot_settings["TTV_PLOT"]["y_axis_limits"][1],
#         )
#
#         if eclipses and not transits:
#             ax1.set_title("{}".format(plot_settings["TTV_PLOT"]["title"] + " Eclipses"))
#
#         elif transits:
#             ax1.set_title("{}".format(plot_settings["TTV_PLOT"]["title"] + " Transits"))
#
#         ax1.legend()
#         legend1 = ax1.legend()
#         for line in legend1.get_lines():
#             line.set_linewidth(6)
#             line.set_alpha(1)
#
#         try:
#             ax2.set_title("{}".format(plot_settings["TTV_PLOT"]["title"]) + " Eclipses")
#             ax2.set_ylabel("Timing Deviation (min)")
#             legend2 = ax2.legend()
#             for line in legend2.get_lines():
#                 line.set_linewidth(6)
#                 line.set_alpha(1)
#         except UnboundLocalError:
#             pass
#
#         plt.savefig(outfile, bbox_inches=bbox, dpi=dpi, pad_inches=pad_inches)
#         plt.close()
#
#         print("Done!\n")


planet = StarPlanet("input_files/HAT-P-7_settings.json")

epochs = np.array(planet.ttv_data["epoch"])
midtimes = np.array(planet.ttv_data["bjd"])
errors = np.array(planet.ttv_data["err"])

folder = "results/HAT-P-7/ttv_fits/"
file_c = folder + "ttv_constant_results_eccentric.json"
file_d = folder + "ttv_decay_results_eccentric.json"
file_p = folder + "ttv_precession_results.json"

# load fit results
with open(file_c) as jf:
    res_c = json.load(jf)
with open(file_d) as jf:
    res_d = json.load(jf)
with open(file_p) as jf:
    res_p = json.load(jf)

ac = Analyzer(planet, res_c)
ad = Analyzer(planet, res_d)
ap = Analyzer(planet, res_p)

COMP = (
    (t_c1, P_c1, e_c1, 0.0, i_c1, 0.0, M_c1),
    (t_c2, P_c2, e_c2, 0.0, i_c2, 0.0, M_c2),
    (t_c3, P_c3, e_c3, 0.0, i_c3, 0.0, M_c3),
    (t_c4, P_c4, e_c4, 0.0, i_c4, 0.0, M_c4),
)

model_d_ltt = ltt_ttv_decay(ad.t0, ad.P0, ad.PdE, ad.e0, ad.w0, epochs, COMP, ad.M_s)
model_c_ltt = ltt_ttv_constant(ac.t0, ac.P0, ac.e0, ac.w0, epochs, COMP, ac.M_s)


model_c = ttv.ttv_constant(ac.t0, ac.P0, ac.e0, ac.w0, epochs)
model_d = ttv.ttv_decay(ad.t0, ad.P0, ad.PdE, ad.e0, ad.w0, epochs)
model_p = ttv.ttv_precession(ap.t0, ap.P0, ap.e0, ap.w0, ap.wdE, epochs)
oc_c = midtimes - model_c
oc_d = midtimes - model_d
oc_p = midtimes - model_p

oc_d_ltt = midtimes - model_d_ltt
oc_c_ltt = midtimes - model_c_ltt

# plt.scatter(epochs, oc_c)
plt.plot(epochs, model_c_ltt - model_c)
plt.show()

epochs_full = np.arange(min(epochs) - 100, max(epochs) + 100, 1)

plt.scatter(epochs, oc_c)
plt.plot(epochs_full, model_c_ltt - model_c)
# plt.plot(epochs_full, model_p - model_c)
# plt.plot(epochs_full, model_d - model_c)
plt.show()
