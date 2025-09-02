import numpy as np
import orbdot.models.theory as m

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
    E_tra = (2 * np.arctan(np.sqrt((1 - e_comp) / (1 + e_comp)) * np.tan(f_tra / 2))) % TWOPI
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
        t_ecl = t0 + P0 * E + P0/2 + 2*P0/np.pi * e0 * np.cos(w0)

        for comp in C:
            ltt_corr -= ltt(comp, M_s, t_ecl) / 86400

        return t_ecl + ltt_corr

def ltt_ttv_decay(t0, P0, PdE, e0, w0, E, C, M_s, primary=True):

    ltt_corr = 0

    if primary:
        t_tra = t0 + P0 * E + 0.5 * (E ** 2) * PdE

        for comp in C:
            ltt_corr -= ltt(comp, M_s, t_tra) / 86400

        return t_tra + ltt_corr

    else:

        t_ecl = t0 + P0 * E + 0.5 * (E ** 2) * PdE + P0/2 + 2*P0/np.pi * e0 * np.cos(w0)

        for comp in C:
            ltt_corr -= ltt(comp, M_s, t_ecl) / 86400

        return t_ecl + ltt_corr

