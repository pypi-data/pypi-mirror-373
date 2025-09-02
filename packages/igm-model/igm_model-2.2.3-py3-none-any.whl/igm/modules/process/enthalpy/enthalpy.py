#!/usr/bin/env python3

# Copyright (C) 2021-2023 Guillaume Jouvet <guillaume.jouvet@unil.ch>
# Published under the GNU GPL (Version 3), check at the LICENSE file

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import time

from igm.modules.utils import *


def params(parser):
    parser.add_argument(
        "--enth_water_density",
        type=float,
        default=1000,
        help="Constant of the Water density [kg m-3]",
    )
    parser.add_argument(
        "--enth_spy",
        type=float,
        default=31556926,
        help="Number of seconds per years [s y-1]",
    )
    parser.add_argument(
        "--enth_ki",
        type=float,
        default=2.1,
        help="Conductivity of cold ice [W m-1 K-1] (Aschwanden and al, JOG, 2012)",
    )
    parser.add_argument(
        "--enth_ci",
        type=float,
        default=2009,
        help="Specific heat capacity of ice [W s kg-1 K-1] (Aschwanden and al, JOG, 2012)",
    )
    parser.add_argument(
        "--enth_Lh",
        type=float,
        default=3.34 * 10 ** (5),
        help="latent heat of fusion [W s kg-1] = [E] (Aschwanden and al, JOG, 2012)",
    )
    parser.add_argument(
        "--enth_KtdivKc",
        type=float,
        default=10 ** (-1),
        help="Ratio of temp vs cold ice diffusivity Kt / Kc [no unit] (Aschwanden and al, JOG, 2012)",
    )
    parser.add_argument(
        "--enth_claus_clape",
        type=float,
        default=7.9 * 10 ** (-8),
        help="Clausius-Clapeyron constant [K Pa-1] (Aschwanden and al, JOG, 2012)",
    )
    parser.add_argument(
        "--enth_melt_temp",
        type=float,
        default=273.15,
        help="Melting point at standart pressure [K] (Aschwanden and al, JOG, 2012)",
    )
    parser.add_argument(
        "--enth_ref_temp",
        type=float,
        default=223.15,
        help="Reference temperature [K] (Aschwanden and al, JOG, 2012)",
    )
    parser.add_argument(
        "--enth_till_friction_angle",
        type=float,
        default=30,
        help="Till friction angle in the Mohr-Coulomb friction law [deg]",
    )

    parser.add_argument(
        "--enth_till_friction_angle_bed_min",
        type=float,
        default=None,
        help="enth_till_friction_angle_bed_min",
    )
    parser.add_argument(
        "--enth_till_friction_angle_bed_max",
        type=float,
        default=None,
        help="enth_till_friction_angle_bed_max",
    )
    parser.add_argument(
        "--enth_till_friction_angle_phi_min",
        type=float,
        default=15,
        help="enth_till_friction_angle_phi_min",
    )
    parser.add_argument(
        "--enth_till_friction_angle_phi_max",
        type=float,
        default=45,
        help="enth_till_friction_angle_phi_max",
    )
    
    parser.add_argument(
        "--enth_uthreshold", type=float, default=100, help="uthreshold [m/y]"
    )
    parser.add_argument(
        "--enth_drain_rate",
        type=float,
        default=0.001,
        help="Drain rate at 1 mm/y  [m y-1] (Bueler and Pelt, GMD, 2015)",
    )
    parser.add_argument(
        "--enth_till_wat_max",
        type=float,
        default=2,
        help="Maximum water till tickness [m] (Bueler and Pelt, GMD, 2015)",
    )
    parser.add_argument(
        "--enth_drain_ice_column",
        type=str2bool,
        default=True,
        help="Transform the water content beyond a thr=0.01 into water, drain it, and add it to basal melt rate",
    )

    parser.add_argument(
        "--enth_default_bheatflx",
        type=float,
        default=0.065,
        help="Geothermal heat flux [W m-2]",
    )
    
    parser.add_argument(
        "--temperature_offset_air_to_ice",
        type=float,
        default=0.0,
        help="This is the offset between the air temperature and the ice temperature as records show \
              [e.g., Reeh 1991] shows that the mean temperature at the ice surface is about X°C colder \
              than the temperature of ice to be given as boundary upper condition to the Enthlapy model"
    )
    
    parser.add_argument(
        "--enth_tauc_min",
        type=float,
        default=10**5,
        help="lower bound for tauc [Pa]"
    )
    parser.add_argument(
        "--enth_tauc_max",
        type=float,
        default=10**10,
        help="lower bound for tauc [Pa]"
    )
 
def initialize(params, state):
    Ny, Nx = state.thk.shape

    state.basalMeltRate = tf.Variable(tf.zeros_like(state.thk),trainable=False)
    state.T = tf.Variable(tf.ones((params.iflo_Nz, Ny, Nx)) * params.enth_melt_temp,trainable=False)
    state.omega = tf.Variable(tf.zeros_like(state.T),trainable=False)
    state.E = tf.Variable(
        tf.ones_like(state.T)
        * (params.enth_ci * (params.enth_melt_temp - params.enth_ref_temp)),
        trainable=False
    )
    state.tillwat = 0.0 * tf.Variable(tf.ones_like(state.thk),trainable=False)

    if not hasattr(state, "bheatflx"):
        state.bheatflx = tf.Variable(
            tf.ones_like(state.thk) * params.enth_default_bheatflx, trainable=False
        )

    state.phi = compute_phi(params,state)

    # update the sliding coefficient
    state.tauc,state.slidingco = compute_slidingco_tf(
        state.thk,
        state.tillwat,
        params.iflo_ice_density,
        params.iflo_gravity_cst,
        params.enth_till_wat_max,
        state.phi,
        params.iflo_exp_weertman,
        params.enth_uthreshold,
        params.iflo_new_friction_param,
        params.enth_tauc_min,
        params.enth_tauc_max
    )

    state.tcomp_enthalpy = []

    # arrhenius must be 3D for the Enthlapy to work
    assert params.iflo_dim_arrhenius == 3


def update(params, state):
    if hasattr(state, "logger"):
        state.logger.info("Update ENTHALPY at time : " + str(state.t.numpy()))

    state.tcomp_enthalpy.append(time.time())

    # compute the surface temperature taken the negative part of the mean air temperature
    surftemp = (
        tf.minimum(tf.math.reduce_mean(state.air_temp + params.temperature_offset_air_to_ice, axis=0), 0)
        + params.enth_melt_temp
    )  # [K]

    # get the vertical discretization
    depth, dz = vertically_discretize_tf(
        state.thk, params.iflo_Nz, params.iflo_vert_spacing
    )

    # compute temperature and enthalpy at the pressure melting point
    Tpmp, Epmp = TpmpEpmp_from_depth_tf(
        depth,
        params.iflo_gravity_cst,
        params.iflo_ice_density,
        params.enth_claus_clape,
        params.enth_melt_temp,
        params.enth_ci,
        params.enth_ref_temp,
    )

    # get the temperature from the enthalpy
    state.T, state.omega = temperature_from_enthalpy_tf(
        state.E,
        Tpmp,
        Epmp,
        params.enth_ci,
        params.enth_ref_temp,
        params.enth_Lh,
    )
    
    # pressure adjusted temperature
    state.Tpa = state.T + params.enth_claus_clape * params.iflo_ice_density * params.iflo_gravity_cst * depth
    
    state.temppabase = state.Tpa[0]
    state.temppasurf = state.Tpa[-1]

    # get the arrhenius factor from temperature and and enthalpy
    state.arrhenius = arrhenius_from_temp_tf(
        state.Tpa,
        state.omega
    ) * params.iflo_enhancement_factor
 
    if hasattr(state, "W"):
        # correct vertical velocity corrected (therefore Wc) from melting rate
        Wc = state.W - tf.expand_dims(state.basalMeltRate, axis=0)
    else:
        # if the vertical velocity is not given, we assume it is zero
        Wc = tf.zeros_like(state.U) - tf.expand_dims(state.basalMeltRate, axis=0)
        
    # compute the strainheat is in [W m-3]
    state.strainheat = compute_strainheat_tf(
        state.U / params.enth_spy,
        state.V / params.enth_spy,
        state.arrhenius,
        state.dx,
        dz,
        params.iflo_exp_glen,
        params.iflo_thr_ice_thk,
    )

    # compute the frictheat is in [W m-2]
    state.frictheat = compute_frictheat_tf(
        state.U / params.enth_spy,
        state.V / params.enth_spy,
        state.slidingco,
        state.topg,
        state.dx,
        params.iflo_exp_weertman,
        params.iflo_new_friction_param,
    )

    # compute the surface enthalpy
    surfenth = surf_enthalpy_from_temperature_tf(
        surftemp, params.enth_melt_temp, params.enth_ci, params.enth_ref_temp
    )

    # one explicit step for the horizonal advection
    state.E = state.E - state.dt * compute_upwind_tf(
        state.U, state.V, state.E, state.dx
    )

    # update the enthalpy and the basal melt rate (implicit scheme)
    state.E, state.basalMeltRate = compute_enthalpy_basalmeltrate(
        state.E,
        Epmp,
        state.dt * params.enth_spy,
        dz,
        Wc / params.enth_spy,
        surfenth,
        state.bheatflx,
        state.strainheat,
        state.frictheat,
        state.tillwat,
        params.iflo_thr_ice_thk,
        params.enth_ki,
        params.iflo_ice_density,
        params.enth_water_density,
        params.enth_ci,
        params.enth_ref_temp,
        params.enth_Lh,
        params.enth_spy,
        params.enth_KtdivKc,
        params.enth_drain_ice_column,
    )

    state.basalMeltRate = tf.clip_by_value(state.basalMeltRate, 0.0, 10.0**10)

    # update the till water content
    state.tillwat = state.tillwat + state.dt * (
        state.basalMeltRate - params.enth_drain_rate
    )
    state.tillwat = tf.clip_by_value(state.tillwat, 0.0, params.enth_till_wat_max)
    state.tillwat = tf.where(state.thk > 0, state.tillwat, 0.0)
    
    state.phi = compute_phi(params,state)

    # update the sliding coefficient
    state.tauc,state.slidingco = compute_slidingco_tf(
        state.thk,
        state.tillwat,
        params.iflo_ice_density,
        params.iflo_gravity_cst,
        params.enth_till_wat_max,
        state.phi,
        params.iflo_exp_weertman,
        params.enth_uthreshold,
        params.iflo_new_friction_param,
        params.enth_tauc_min,
        params.enth_tauc_max
    )
    
    state.hardav = tf.reduce_sum(state.arrhenius**(-1/3) * state.vert_weight, axis=0) \
                 * 1e+6 * (365.25*24*3600)**(1/3)  # unit is Pa s**(1/3)
                 
    state.arrheniusav = tf.reduce_sum(state.arrhenius * state.vert_weight, axis=0)
    
    state.tcomp_enthalpy[-1] -= time.time()
    state.tcomp_enthalpy[-1] *= -1


def finalize(params, state):
    pass


#######################################################################################

# thk in [m]
# E in [W s kg-1]
# T in [K]
# omeag dimensionless
# dt in [y]
# dz in [m]
# surftemp in [K]
# bheatflx in [W m-2]
# frictheat in [W m-2]
# tillwat in [m]
# strainheat in [W m-3]


@tf.function()
def vertically_discretize_tf(thk, Nz, vert_spacing):
    zeta = tf.cast(tf.range(Nz) / (Nz - 1), "float32")
    levels = (zeta / vert_spacing) * (1.0 + (vert_spacing - 1.0) * zeta)
    ddz = levels[1:] - levels[:-1]

    dz = tf.expand_dims(thk, 0) * tf.expand_dims(tf.expand_dims(ddz, -1), -1)

    D = tf.concat([dz, tf.zeros((1, dz.shape[1], dz.shape[2]))], axis=0)

    depth = tf.math.cumsum(D, axis=0, reverse=True)

    return depth, dz


@tf.function()
def temperature_from_enthalpy_tf(E, Tpmp, Epmp, ci, ref_temp, Lh):
    # Units: T [K], omega [], E [W s kg-1]

    T = tf.where(E >= Epmp, Tpmp, E / ci + ref_temp)
    omega = tf.where(E >= Epmp, (E - Epmp) / Lh, 0.0)

    return T, omega


@tf.function()
def arrhenius_from_temp_tf(Tpa, omega):
    # Budd Paterson Law adapted for (T,omega), return result in MPa^{-3} y^{-1}
    # (Aschwanden and al, JOG, 2012) & (Paterson 1994)

    A = tf.where(Tpa < 263.15, 3.985 * 10 ** (-13), 1.916 * 10**3)  # s^{-1} Pa^{-3}
    Q = tf.where(Tpa < 263.15, 60000.0, 139000.0)  # J mol-1

    chunit = (10**18) * 31556926  # change unit from Pa^{-3} s^{-1} to MPa^{-3} y^{-1}

    return (
        (1.0 + 181.25 * tf.minimum(omega, 0.01))
        * A
        * chunit
        * tf.math.exp(-Q / (8.314 * Tpa))
    )


@tf.function()
def compute_slidingco_tf(
    thk,
    tillwat,
    ice_density,
    gravity_cst,
    tillwatmax,
    phi,
    exp_weertman,
    uthreshold,
    new_friction_param,
    tauc_min,
    tauc_max
):
    # return the sliding coefficient in [m MPa^{-3} y^{-1}]

    e0 = 0.69  # void ratio at reference
    Cc = 0.12  # till compressibility coefficient
    delta = 0.02
    N0 = 1000  # [Pa] reference effective pressure

    s = tillwat / tillwatmax  # []

    P = ice_density * gravity_cst * thk  # [Pa]

    effpress = tf.minimum(
        P, N0 * ((delta * P / N0) ** s) * 10 ** (e0 * (1 - s) / Cc)
    )  # [Pa]

    tauc = effpress * tf.math.tan(phi * np.math.pi / 180)  # [Pa]

    tauc = tf.where(thk > 0, tauc, 10**6)  # high value if ice-fre

    tauc = tf.clip_by_value(tauc, tauc_min, tauc_max)

    if new_friction_param:
        slidingco = (tauc * 10 ** (-6)) * uthreshold ** (
            -1.0 / exp_weertman
        )  # Mpa m^(-1/3) y^(1/3)
    else:
        slidingco = (tauc * 10 ** (-6)) ** (-exp_weertman) * uthreshold  # Mpa^-3 m y^-1

    return tauc,slidingco

def compute_phi(params,state):

    if params.enth_till_friction_angle_bed_min == None:
        return params.enth_till_friction_angle * tf.ones_like(state.thk)
    else:
        return tf.where(
            state.topg <= params.enth_till_friction_angle_bed_min,
            params.enth_till_friction_angle_phi_min,
            tf.where(
                state.topg >= params.enth_till_friction_angle_bed_max,
                params.enth_till_friction_angle_phi_max,
                params.enth_till_friction_angle_phi_min
                + (params.enth_till_friction_angle_phi_max - params.enth_till_friction_angle_phi_min)
                * (state.topg                              - params.enth_till_friction_angle_bed_min)
                / (params.enth_till_friction_angle_bed_max - params.enth_till_friction_angle_bed_min),
            ),
        )

@tf.function()
def compute_strainheat_tf(U, V, arrhenius, dx, dz, exp_glen, thr):
    # input U [m s^{-1} ]
    # input arrhenius [MPa^{-3} y^{-1} ]
    # return strainheat in [W m^{-3}]

    Ui = tf.pad(U[:, :, :], [[0, 0], [0, 0], [1, 1]], "SYMMETRIC")
    Uj = tf.pad(U[:, :, :], [[0, 0], [1, 1], [0, 0]], "SYMMETRIC")
    Uk = tf.pad(U[:, :, :], [[1, 1], [0, 0], [0, 0]], "SYMMETRIC")

    Vi = tf.pad(V[:, :, :], [[0, 0], [0, 0], [1, 1]], "SYMMETRIC")
    Vj = tf.pad(V[:, :, :], [[0, 0], [1, 1], [0, 0]], "SYMMETRIC")
    Vk = tf.pad(V[:, :, :], [[1, 1], [0, 0], [0, 0]], "SYMMETRIC")

    DZ2 = tf.concat([dz[0:1], dz[:-1] + dz[1:], dz[-1:]], axis=0)

    Exx = (Ui[:, :, 2:] - Ui[:, :, :-2]) / (2 * dx)
    Eyy = (Vj[:, 2:, :] - Vj[:, :-2, :]) / (2 * dx)
    Ezz = -Exx - Eyy

    Exy = 0.5 * (Vi[:, :, 2:] - Vi[:, :, :-2]) / (2 * dx) + 0.5 * (
        Uj[:, 2:, :] - Uj[:, :-2, :]
    ) / (2 * dx)
    Exz = 0.5 * (Uk[2:, :, :] - Uk[:-2, :, :]) / tf.maximum(DZ2, thr)
    Eyz = 0.5 * (Vk[2:, :, :] - Vk[:-2, :, :]) / tf.maximum(DZ2, thr)

    strainrate = (
        0.5
        * (
            Exx**2
            + Exy**2
            + Exz**2
            + Exy**2
            + Eyy**2
            + Eyz**2
            + Exz**2
            + Eyz**2
            + Ezz**2
        )
    ) ** 0.5

    strainrate = tf.where(DZ2 > 1, strainrate, 0.0)

    # here one put back arrhenius in unit  Pa^{-3} s^{-1}
    # [Pa y^1/3 y^(-4/3)] = [Pa s^{-1}] = [W m^{-3}]
    return (arrhenius / ((10**18) * 31556926)) ** (-1.0 / exp_glen) * (
        strainrate ** (1.0 + 1.0 / exp_glen)
    )


@tf.function()
def compute_frictheat_tf(U, V, slidingco, topg, dx, exp_weertman, new_friction_param):
    # input U [m s^{-1} ]
    # input slidingo [m MPa^{-3} y^{-1} ]
    # return frictheat in [W m^{-2}]

    sloptopgx, sloptopgy = compute_gradient_tf(topg, dx, dx)
    wvelbase = U[0] * sloptopgx + V[0] * sloptopgy
    ub = (U[0, :, :] ** 2 + V[0, :, :] ** 2 + wvelbase**2) ** 0.5

    if new_friction_param:
        # slidingco is in Mpa m^{-1/3} y^{1/3}
        # [Pa m^{-1/3} y^{1/3} s^{1/3} y^{-1/3} m^{4/3} s^{-4/3}] = [Pa m s^{-1}] = [W m^{-2}]
        return (
            (slidingco * 10**6)
            * (31556926) ** (1.0 / exp_weertman)
            * ub ** ((1.0 / exp_weertman) + 1)
        )
    else:
        # slidingco is in Mpa^-3 m y-1
        # [Pa s^{1/3} m^{-1/3} m^{4/3} s^{-4/3}] = [Pa m s^{-1}] = [W m^{-2}]
        return ((slidingco / ((10**18) * 31556926)) + 10 ** (-12)) ** -(
            1.0 / exp_weertman
        ) * ub ** ((1.0 / exp_weertman) + 1)


@tf.function()
def TpmpEpmp_from_depth_tf(
    depth, gravity_cst, ice_density, claus_clape_cst, melt_temp, ci, ref_temp
):
    # Tmp is the pressure melting point Temperature
    # Tmp is the pressure melting point Enthalpy
    p = ice_density * gravity_cst * depth  #  [Pa]
    Tpmp = melt_temp - claus_clape_cst * p  #  [K]
    Epmp = ci * (Tpmp - ref_temp)  #  [W s Kg-1]

    return Tpmp, Epmp


@tf.function()
def surf_enthalpy_from_temperature_tf(T, melt_temp, ci, ref_temp):
    # Enthalpy is expressed in W s kg-1
    # T must be expressed in K
    # p must be expressed in Pa
    # omega is dimnesionless

    return tf.where(T < melt_temp, ci * (T - ref_temp), ci * (melt_temp - ref_temp))


@tf.function()
def drainageFunc(omega):
    # References: Greve (1997, application), Aschwanden (2012): p450
    # omega is dimensionless, eturn  [y-1]

    A = omega <= 0.01
    B = (omega > 0.01) & (omega <= 0.02)
    C = (omega > 0.02) & (omega <= 0.03)
    D = omega > 0.03

    return tf.where(
        A,
        0.0 * omega,
        tf.where(B, 0.5 * omega - 0.005, tf.where(C, 4.5 * omega - 0.085, 0.05)),
    )


@tf.function()
def compute_upwind_tf(U, V, E, dx):
    #  upwind computation of u dE/dx + v dE/dy, unit are [E s^{-1}]

    # Extend E with constant value at the domain boundaries
    Ex = tf.pad(E, [[0, 0], [0, 0], [1, 1]], "SYMMETRIC")  # has shape (nz,ny,nx+2)
    Ey = tf.pad(E, [[0, 0], [1, 1], [0, 0]], "SYMMETRIC")  # has shape (nz,ny+2,nx)

    ## Compute the product selcting the upwind quantities  :-2, 1:-1 , 2:
    Rx = U * tf.where(
        U > 0,
        (Ex[:, :, 1:-1] - Ex[:, :, :-2]) / dx,
        (Ex[:, :, 2:] - Ex[:, :, 1:-1]) / dx,
    )  # has shape (nz,ny,nx+1)
    Ry = V * tf.where(
        V > 0,
        (Ey[:, 1:-1:, :] - Ey[:, :-2, :]) / dx,
        (Ey[:, 2:, :] - Ey[:, 1:-1, :]) / dx,
    )  # has shape (nz,ny+1,nx)

    ##  Final shape is (nz,ny,nx)
    return Rx + Ry
 

@tf.function()
def solve_TDMA_new(L, M, U, R):
    # Tridiagonal Matrix Algorithm (TDMA) or Thomas Algorithm
    # https://en.wikipedia.org/wiki/Tridiagonal_matrix_algorithm
    # Here L = Lower Diag, M = Main Diag, U = Upper Diag, R = Right Hand Side

    nz = tf.shape(M)[0]

    w = tf.TensorArray(dtype=tf.float32, size=nz-1)
    g = tf.TensorArray(dtype=tf.float32, size=nz)
    p = tf.TensorArray(dtype=tf.float32, size=nz)

    # Forward sweep
    w = w.write(0, U[0] / M[0])
    g = g.write(0, R[0] / M[0])

    for i in tf.range(1, nz-1):
        w = w.write(i, U[i] / (M[i] - L[i-1] * w.read(i-1)))

    for i in tf.range(1, nz):
        g = g.write(i, (R[i] - L[i-1] * g.read(i-1)) / (M[i] - L[i-1] * w.read(i-1)))

    # Backward substitution
    p = p.write(nz-1, g.read(nz-1))

    for i in tf.range(nz-2, -1, -1):
        p = p.write(i, g.read(i) - w.read(i) * p.read(i+1))

    return p.stack() 

@tf.function()
def solve_TDMA(L, M, U, R):
    # Tridiagonal Matrix Algorithm (TDMA) or Thomas Algorithm
    # https://en.wikipedia.org/wiki/Tridiagonal_matrix_algorithm
    # Here L = Lower Diag, M = Main Diag, U = Upper Diag, R = Right Hand Side

    nz = M.shape[0]

    w = []
    g = []
    p = []

    w.append(U[0] / M[0])
    g.append(R[0] / M[0])

    for i in range(1, nz - 1):
        w.append(U[i] / (M[i] - L[i - 1] * w[i - 1]))

    for i in range(1, nz):
        g.append((R[i] - L[i - 1] * g[i - 1]) / (M[i] - L[i - 1] * w[i - 1]))

    p.append(g[nz - 1])

    for i in range(nz - 1, 0, -1):
        p.append(g[i - 1] - w[i - 1] * p[nz - 1 - i])

    p.reverse()

    return tf.stack(p)


@tf.function()
def assembly_diffusion_advection_tf(E, dt, dz, w, K, f, BCB, VB, VS, L, M, U, R):
    # dE/dt  + w * dE/dz = K * ( d^2 E / d^2 z ) + f
    # This is a FD scheme , which is equi. to FE with mass lumping
    # Neuman  BC: E'(0) = VB    OR    Dirichlet BC: E(0) = VB
    # Dirichlet BC: E(H)  = VS
     # E, w and f is P1 (have shape (nz,ny,nx)). K and dz are P0 (have shape (nz-1,ny,nx)). BCB, VB and VS are scalar (have shape (ny,nx)).

    nz = E.shape[0]

    s = dt * K / (dz * dz)  # this is a P0 quantity

    # Assembly the matrix and the RHS
    M.assign(M + 1.0)
    M[1:nz].assign(M[1:nz] + s)
    M[0 : nz - 1].assign(M[0 : nz - 1] + s)
    L.assign(L - s)
    U.assign(U - s)
    R.assign(R + E + dt * f)

    # BOTTOM BC (BCB is either 'neumann' (1) or 'dirichlet' (0))
    M[0].assign(tf.where(BCB == 1, -tf.ones_like(BCB), tf.ones_like(BCB)))
    U[0].assign(tf.where(BCB == 1, tf.ones_like(BCB), tf.zeros_like(BCB)))
    R[0].assign(tf.where(BCB == 1, VB * dz[0], VB))

    # SURFACE BC
    M[-1].assign(tf.ones_like(BCB))
    L[-1].assign(tf.zeros_like(BCB))
    R[-1].assign(VS)

    # UPWIND SCHEME FOR THE ADVECTION TERM (TREATED IMPLICITLY)
    wdivdz = dt * (w[1:] + w[:-1]) / (2.0 * dz)  # this is a P0 quantity
    L[:-1].assign(L[:-1] + tf.where(w[1:-1] > 0, -wdivdz[:-1], 0))
    M[1:-1].assign(M[1:-1] + tf.where(w[1:-1] > 0, wdivdz[:-1], -wdivdz[1:]))
    U[1:].assign(U[1:] + tf.where(w[1:-1] <= 0, wdivdz[1:], 0))

    return L, M, U, R


@tf.function()
def assembly_diffusion_advection_tf_new(E, dt, dz, w, K, f, BCB, VB, VS):
    # dE/dt  + w * dE/dz = K * ( d^2 E / d^2 z ) + f
    # This is a FD scheme , which is equi. to FE with mass lumping
    # Neuman  BC: E'(0) = VB    OR    Dirichlet BC: E(0) = VB
    # Dirichlet BC: E(H)  = VS
    # E, w and f is P1 (have shape (nz,ny,nx)). K and dz are P0 (have shape (nz-1,ny,nx)). BCB, VB and VS are scalar (have shape (ny,nx)).
  
    nz, ny, nx = E.shape
    s = dt * K / (dz * dz)  # P0 quantity, shape (nz-1, ny, nx)

    # Initialize L, M, U, R tensors
    L = tf.zeros((nz - 1, ny, nx))
    M = tf.ones((nz, ny, nx))
    U = tf.zeros((nz - 1, ny, nx))
    R = E + dt * f

    # Assembly the matrix and the RHS
    M = M + tf.concat([s, tf.zeros((1, ny, nx))], axis=0)
    M = M + tf.concat([tf.zeros((1, ny, nx)), s], axis=0)
    L = L - s
    U = U - s

    # BOTTOM BC (BCB is either 'neumann' (1) or 'dirichlet' (0))
    M = tf.concat([tf.where(BCB == 1, -tf.ones_like(BCB), tf.ones_like(BCB))[None, :, :], M[1:]], axis=0)
    U = tf.concat([tf.where(BCB == 1, tf.ones_like(BCB), tf.zeros_like(BCB))[None, :, :], U[1:]], axis=0)
    R = tf.concat([tf.where(BCB == 1, VB * dz[0], VB)[None, :, :], R[1:]], axis=0)

    # SURFACE BC
    M = tf.concat([M[:-1], tf.ones_like(BCB)[None, :, :]], axis=0)
    L = tf.concat([L[:-1], tf.zeros_like(BCB)[None, :, :]], axis=0)
    R = tf.concat([R[:-1], VS[None, :, :]], axis=0)

    # UPWIND SCHEME FOR THE ADVECTION TERM (TREATED IMPLICITLY)
    wdivdz = dt * (w[1:] + w[:-1]) / (2.0 * dz)  # P0 quantity, shape (nz-1, ny, nx)
    L = tf.concat([L[:-1] + tf.where(w[1:-1] > 0, -wdivdz[:-1], 0), L[-1:]], axis=0)
    M = tf.concat([M[:1], M[1:-1] + tf.where(w[1:-1] > 0, wdivdz[:-1], -wdivdz[1:]), M[-1:]], axis=0)
    U = tf.concat([U[:1], U[1:] + tf.where(w[1:-1] <= 0, wdivdz[1:], 0)], axis=0)

    return L, M, U, R

# @tf.function()
def compute_enthalpy_basalmeltrate(
    E,  # [E] or [W s kg-1]
    Epmp,  # [E] or [W s kg-1]
    dt,  # [s]
    dz,  # [m]
    w,  # [m s-1]
    surfenth,  # [E] or [W s kg-1]
    bheatflx,  # [W m^{-2}]
    strainheat,  # [W m^{-3}]
    frictheat,  # [W m^{-2}]
    tillwat,  # [m]
    thr,
    ki,
    ice_density,
    water_density,
    ci,
    ref_temp,
    Lh,
    spy,
    KtdivKc,
    drain_ice_column,
):
    nz, ny, nx = E.shape

    PKc = ki / (ice_density * ci)  # [m2 s-1] , same as PKt

    f = strainheat / ice_density  # P1, [W Kg-1] (strainheat is [W m^{-3}])

    K = PKc * tf.ones_like(dz)  # P0, [m2 s-1]

    K = tf.where((E[:-1] + E[1:] / 2.0) >= (Epmp[:-1] + Epmp[1:] / 2.0), K * KtdivKc, K)

    VS = surfenth  # one value [K]

    COLD_BASE = (E[0] < Epmp[0]) | (tillwat <= 0)
    DRY_ICE = tillwat <= 0
    COLD_ICE = E[1] < Epmp[1]

    # we code the BC with 1 for neummann and 0 for dirichlet
    BCB = tf.where(
        COLD_BASE,
        tf.where(DRY_ICE, tf.ones((ny, nx)), tf.zeros((ny, nx))),
        tf.where(COLD_ICE, tf.zeros((ny, nx)), tf.ones((ny, nx))),
    )

    # we code the BC value, either the derivative for neumann or the value for dirichlet
    VB = tf.where(
        COLD_BASE,
        tf.where(DRY_ICE, -(ci / ki) * (bheatflx + frictheat), Epmp[0]),
        tf.where(COLD_ICE, Epmp[0] * tf.ones((ny, nx)), 0.0),
    )

    # initiatlize to zero the FD matrices to solve the boundary value problem
    L = tf.Variable(tf.zeros((nz - 1, ny, nx)),trainable=False)
    M = tf.Variable(tf.zeros((nz, ny, nx)),trainable=False)
    U = tf.Variable(tf.zeros((nz - 1, ny, nx)),trainable=False)
    R = tf.Variable(tf.zeros((nz, ny, nx)),trainable=False)

    # fill the FD matrices to solve the boundary value problem
    # d E / d t  + w * dE /dz = K * ( d^2 E / d^2 z ) + f of unit [E s^{-1}] or [W kg-1]
#    L, M, U, R = assembly_diffusion_advection_tf(
#        E, dt, tf.maximum(dz, thr), w, K, f, BCB, VB, VS, L, M, U, R
#    )

    L, M, U, R = assembly_diffusion_advection_tf_new( E, dt, tf.maximum(dz, thr), w, K, f, BCB, VB, VS )

    # return the results of the solving of the boundary value problem (tridiagonal pb)
#    E = solve_TDMA(L, M, U, R)
    E = solve_TDMA_new(L, M, U, R)

    # lower-bound at T = -30°C
    Emin = ci * (243.15 - ref_temp)
    E = tf.where(E >= Emin, E, Emin)

    # upper-bound at omega = 1
    Emax = Epmp + 1.0 * Lh
    E = tf.where(E <= Emax, E, Emax)

    # compute flux differently for cold ice or not (unit is [W m^{-2}])
    flux = tf.where(
        E[1] < Epmp[1],
        -(ki / ci) * (E[1] - E[0]) / tf.maximum(dz[0], thr),
        -KtdivKc * (ki / ci) * (E[1] - E[0]) / tf.maximum(dz[0], thr),
    )

    # compute basalMeltRate in [m y-1] when the base not cold (bheatflx, frictheat and flux in [W m-2])
    basalMeltRate = tf.where(
        (E[0] < Epmp[0]) & (tillwat <= 0),
        tf.zeros((ny, nx)),
        spy * (bheatflx + frictheat - flux) / (water_density * Lh),
    )

    # Drain along the ice column and update basal melt rate
    if (dt > 0) & drain_ice_column:
        target_water_fraction = 0.01

        DZ = tf.concat([dz[0:1], dz[:-1] + dz[1:], dz[-1:]], axis=0) / 2.0

        omega = tf.maximum((E - Epmp) / Lh, 0)

        CD = omega > target_water_fraction

        fraction_drained = drainageFunc(omega) * dt / spy  # dimensionless qty

        # make sure we don't drain more than the water available
        fraction_drained = tf.minimum(fraction_drained, omega - target_water_fraction)

        # record the drained water
        H_drained = tf.where(CD, fraction_drained * DZ, 0)  # [m]

        # update the enthalpy after removing the drained water
        E = tf.where(CD, E - fraction_drained * Lh, E)  # [E] or [W s kg-1]

        # drain the water along the column
        H_total_drained = tf.reduce_sum(H_drained, axis=0)  # [m]

        # update the basal melt rate with the drained water (basalMeltRate in [m y-1])
        basalMeltRate = (
            basalMeltRate + (spy / dt) * (ice_density / water_density) * H_total_drained
        )

    return E, basalMeltRate
