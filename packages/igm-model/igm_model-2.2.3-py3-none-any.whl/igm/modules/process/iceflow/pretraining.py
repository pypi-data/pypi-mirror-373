#!/usr/bin/env python3

# Copyright (C) 2021-2023 Guillaume Jouvet <guillaume.jouvet@unil.ch>
# Published under the GNU GPL (Version 3), check at the LICENSE file

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import datetime
import os
import xarray
import sys
 
from igm.modules.utils import *
from .utils import *
from .emulate import *
from .solve import *
from .energy_iceflow import *
from .diagnostic import *
 
def pretraining(params, state):
    state.direct_name = (
        "pinnbp"
        + "_"
        + str(params.iflo_Nz)
        + "_"
        + str(int(params.iflo_vert_spacing))
        + "_"
    )
    state.direct_name += (
        params.iflo_network
        + "_"
        + str(params.iflo_nb_layers)
        + "_"
        + str(params.iflo_nb_out_filter)
        + "_"
    )
    state.direct_name += (
        str(params.iflo_dim_arrhenius) + "_" + str(int(params.iflo_new_friction_param))
    )

    os.makedirs( state.direct_name, exist_ok=True)

    os.system(
        "echo rm -r "
        + state.direct_name
        + " >> clean.sh"
    )

    subdatasetname_train, subdatasetpath_train = _findsubdata(
        os.path.join(params.data_dir, "train")
    )

    subdatasetname_test, subdatasetpath_test = _findsubdata(
        os.path.join(params.data_dir, "test")
    )

    for p in subdatasetpath_test:
        state.PAR = []
        it = 3
        midva2 = 0.50 * params.min_arrhenius + 0.50 * params.max_arrhenius
        midvs2 = 0.50 * params.min_slidingco + 0.50 * params.max_slidingco
        state.PAR.append([p, it, midva2, midvs2, params.min_coarsen])
        if params.min_arrhenius < params.max_arrhenius:
            midva1 = 0.25 * params.min_arrhenius + 0.75 * params.max_arrhenius
            midva3 = 0.75 * params.min_arrhenius + 0.25 * params.max_arrhenius
            state.PAR.append([p, it, midva1, midvs2, params.min_coarsen])
            state.PAR.append([p, it, midva3, midvs2, params.min_coarsen])
        if params.min_slidingco < params.max_slidingco:
            midvs1 = 0.25 * params.min_slidingco + 0.75 * params.max_slidingco
            midvs3 = 0.75 * params.min_slidingco + 0.25 * params.max_slidingco
            state.PAR.append([p, it, midva2, midvs1, params.min_coarsen])
            state.PAR.append([p, it, midva2, midvs3, params.min_coarsen])
        if params.min_coarsen < params.max_coarsen:
            state.PAR.append([p, it, midva2, midvs2, params.min_coarsen + 1])

    compute_solutions(params, state)

    train_iceflow_emulator(params, state, subdatasetpath_train)

    print("pretraining done, the code stop here, as the emulator is trained")
    print("pretraining can not be followed with a run now.")

    sys.exit()


 
######################################
 
def compute_solutions(params, state):
    state.solutions = []
    state.solutions_cost = []

    if int(tf.__version__.split(".")[1]) <= 10:
        state.optimizer = tf.keras.optimizers.Adam(
            learning_rate=params.iflo_solve_step_size
        )
    else:
        state.optimizer = tf.keras.optimizers.legacy.Adam(
            learning_rate=params.iflo_solve_step_size
        )

    for par in state.PAR:
        p, it, val_A, val_C, val_R = par
        co = int(2**val_R)

        ds = xarray.open_dataset(os.path.join(p, "ex.nc"), engine="netcdf4")
        rec = ds.dims["time"]

        thk = tf.convert_to_tensor(ds["thk"])[it, ::co, ::co]
        usurf = tf.convert_to_tensor(ds["usurf"])[it, ::co, ::co]
        x = tf.convert_to_tensor(ds["x"])
        resol = float((x[1] - x[0]) * co)
        dX = tf.ones_like(thk) * resol

        if params.iflo_dim_arrhenius == 3:
            arrhenius = tf.ones((params.iflo_Nz, thk.shape[0], thk.shape[1])) * val_A
        else:
            arrhenius = tf.ones_like(thk) * val_A

        slidingco = tf.ones_like(thk) * val_C

        for f in params.iflo_fieldin:
            vars(state)[f] = vars()[f]

        fieldin = [thk, usurf, arrhenius, slidingco, dX]

        X = fieldin_to_X(params, fieldin)

        U = tf.Variable(
            tf.zeros((params.iflo_Nz, state.thk.shape[0], state.thk.shape[1]))
        )
        V = tf.Variable(
            tf.zeros((params.iflo_Nz, state.thk.shape[0], state.thk.shape[1]))
        )

        U, V, MISFIT = solve_iceflow(params, state, U, V)

        Y = UV_to_Y(params, U, V)

        code = (
            p.split("/")[-1]
            + "_"
            + str(it)
            + "_A"
            + str(int(val_A))
            + "_C"
            + str(int(val_C * 100) / 100)
            + "_R"
            + str(int(val_R))
        )

        # define path
        path = os.path.join(state.direct_name, code)
        os.makedirs(path, exist_ok=True)

        fig = plt.figure(figsize=(10, 10))
        plt.plot(MISFIT, "--k", label="COST")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(path, "MISFIT-STOKES.png"), pad_inches=0)
        plt.close("all")

        np.savetxt(
            os.path.join(path, "costs-stokes.dat"),
            np.stack(MISFIT),
            fmt="%.5f",
        )

        #        np.save(os.path.join(path, 'X-stokes.npy'),X.numpy())
        #        np.save(os.path.join(path, 'Y-stokes.npy'),Y.numpy())

        _plot_one_Glen(params, X, Y, path)

        state.solutions.append([X, Y])

        state.solutions_cost.append(MISFIT[-1])


def train_iceflow_emulator(params, state, trainingset, augmentation=True):
    """
    train_iceflow_emulator
    """

    import random

    nb_inputs = len(params.iflo_fieldin) + (params.iflo_dim_arrhenius == 3) * (
        params.iflo_Nz - 1
    )
    nb_outputs = 2 * params.iflo_Nz

    if os.path.exists("model0.h5"):
        state.iceflow_model = tf.keras.models.load_model("model0.h5", compile=False)
    else:
        if params.iflo_network=='cnn':
            state.iceflow_model = cnn(params, nb_inputs, nb_outputs)
        elif params.iflo_network=='unet':
            state.iceflow_model = unet(params, nb_inputs, nb_outputs)

    state.iceflow_model.summary(line_length=130)

    # fix change in TF btw version <=10 and version >=11
    if int(tf.__version__.split(".")[1]) <= 10:
        optimizer = tf.keras.optimizers.Adam(
            learning_rate=params.iflo_retrain_emulator_lr
        )
    else:
        optimizer = tf.keras.optimizers.legacy.Adam(
            learning_rate=params.iflo_retrain_emulator_lr
        )

    state.MISFIT = []
    state.MISFIT_CO = []

    define_vertical_weight(params, state)

    for epoch in range(params.epochs):
        nsub = list(trainingset)
        random.shuffle(nsub)

        for p in nsub:
            ds = xarray.open_dataset(os.path.join(p, "ex.nc"), engine="netcdf4")

            rec = ds.dims["time"]

            bs = params.batch_size

            st = rec // bs

            it = np.random.randint(0, st)

            if augmentation:
                ri = tf.constant(
                    [
                        np.random.randint(0, 4),
                        np.random.randint(0, 2),
                        np.random.randint(0, 2),
                        np.random.randint(0, 2),
                    ]
                )
            else:
                ri = tf.constant([0, 0, 0, 0])

            if (params.soft_begining > 0) & (params.soft_begining < epoch):
                co = int(
                    2
                    ** tf.random.uniform(
                        shape=[1],
                        minval=params.min_coarsen,
                        maxval=params.max_coarsen,
                        dtype=tf.int32,
                    )
                )
                val_A = tf.random.uniform(
                    shape=[1], minval=params.min_arrhenius, maxval=params.max_arrhenius
                )
                val_C = tf.random.uniform(
                    shape=[1], minval=params.min_slidingco, maxval=params.max_slidingco
                )
            else:
                co = int(2**params.min_coarsen)
                val_A = (params.min_arrhenius + params.max_arrhenius) / 2
                val_C = (params.min_slidingco + params.max_slidingco) / 2

            thk = _aug(
                tf.expand_dims(
                    tf.convert_to_tensor(ds["thk"])[it::st, ::co, ::co], axis=-1
                ),
                ri,
            )[:bs, :, :, 0]
            usurf = _aug(
                tf.expand_dims(
                    tf.convert_to_tensor(ds["usurf"])[it::st, ::co, ::co], axis=-1
                ),
                ri,
            )[:bs, :, :, 0]

            x = tf.convert_to_tensor(ds["x"])
            dX = tf.ones_like(thk) * (x[1] - x[0]) * co

            nn, ny, nx = thk.shape
            
            PAD = compute_PAD(params,nx,ny)

            if params.iflo_dim_arrhenius == 3:
                arrhenius = tf.ones((1, params.iflo_Nz, ny, nx)) * val_A
            else:
                arrhenius = tf.ones_like(thk) * val_A

            slidingco = tf.ones_like(thk) * val_C

            fieldin = [thk[0], usurf[0], arrhenius[0], slidingco[0], dX[0]]

            X = fieldin_to_X(params, fieldin)

            with tf.GradientTape() as t:
                t.watch(state.iceflow_model.trainable_variables)
                
                X = tf.pad(X, PAD, "CONSTANT")

                Y = state.iceflow_model(X)
                
                X = X[:,:ny,:nx,:]
                Y = Y[:,:ny,:nx,:]

                C_shear, C_slid, C_grav, C_float = iceflow_energy_XY(params, X, Y)
 
                COST = tf.reduce_mean(C_shear) + tf.reduce_mean(C_slid) \
                       + tf.reduce_mean(C_grav)  + tf.reduce_mean(C_float)

            grads = t.gradient(COST, state.iceflow_model.trainable_variables)

            optimizer.apply_gradients(
                zip(grads, state.iceflow_model.trainable_variables)
            )

            ds.close()

        if params.train_iceflow_emulator_restart_lr > 0:
            optimizer.lr = params.iflo_retrain_emulator_lr * (
                0.9 ** ((epoch % params.train_iceflow_emulator_restart_lr) / 100)
            )
        else:
            optimizer.lr = params.iflo_retrain_emulator_lr * (0.9 ** (epoch / 100))

        if epoch % (params.epochs // 5) == 0:
            pp = os.path.join( state.direct_name, "model-" + str(epoch) + ".h5" )
            state.iceflow_model.save(pp)

        if epoch % params.freq_test == 0:
            # Run a validation loop at the end of each epoch.

            MIS = []
            MIS_CO = []

            for par, sol, sol_co in zip(
                state.PAR, state.solutions, state.solutions_cost
            ):
                p = par[0]
                X = sol[0]
                Y = sol[1]

                code = (
                    p.split("/")[-1]
                    + "_"
                    + str(par[1])
                    + "_A"
                    + str(int(par[2]))
                    + "_C"
                    + str(int(par[3] * 100) / 100)
                    + "_R"
                    + str(int(par[4]))
                )

                path = os.path.join(state.direct_name, code)                

                Ny = X.shape[1]
                Nx = X.shape[2]

                PAD = compute_PAD(params,Nx,Ny)
                
                X = tf.pad(X, PAD, "CONSTANT")

                YP = state.iceflow_model(X)
                
                X  =  X[:,:Ny,:Nx,:]
                YP = YP[:,:Ny,:Nx,:]

                C_shear, C_slid, C_grav, C_float = iceflow_energy_XY(params, X, YP)
 
                COST = tf.reduce_mean(C_shear) + tf.reduce_mean(C_slid) \
                     + tf.reduce_mean(C_grav)  + tf.reduce_mean(C_float)
                
                nl1, nl2, nbarl1, nbarl1a = _computemisfitall(params, state, X, Y, YP)

                if epoch % (params.epochs // 20) == 0:
                    _plot_iceflow_Glen(
                        params, state, X, Y, YP, str(epoch).zfill(5), path
                    )
                    np.save(os.path.join(path, "Y-pinn.npy"), YP.numpy())

                MIS.append(nbarl1)

                MIS_CO.append((COST - sol_co).numpy())

                print(
                    datetime.datetime.now().strftime("%H:%M:%S"),
                    " TEST :",
                    epoch,
                    code,
                    nl1,
                    nl2,
                    nbarl1,
                    nbarl1a,
                    MIS_CO[-1],
                    optimizer.lr.numpy(),
                )

                fid = open(os.path.join(path, "misfit-pinn.dat"), "a")
                fid.write(
                    "%.0f %.4f %.4f %.4f %.4f %.4f \n"
                    % (epoch, nl1, nl2, nbarl1, nbarl1a, MIS_CO[-1])
                )
                fid.close()

            state.MISFIT.append(MIS)
            state.MISFIT_CO.append(MIS_CO)

    state.MISFIT = np.stack(state.MISFIT)
    state.MISFIT_CO = np.stack(state.MISFIT_CO)

    fig = plt.figure(figsize=(10, 10))
    for l, par in enumerate(state.PAR):
        p = par[0]
        code = (
            p.split("/")[-1]
            + "_"
            + str(par[1])
            + "_A"
            + str(int(par[2]))
            + "_C"
            + str(int(par[3] * 100) / 100)
            + "_R"
            + str(int(par[4]))
        )
        plt.plot(
            params.freq_test * np.arange(state.MISFIT.shape[0]),
            state.MISFIT[:, l],
            label="MISFIT " + code,
        )
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        os.path.join(state.direct_name, "MISFIT.png"), pad_inches=0
    )
    plt.close("all")

    fig = plt.figure(figsize=(10, 10))
    for l, par in enumerate(state.PAR):
        p = par[0]
        code = (
            p.split("/")[-1]
            + "_"
            + str(par[1])
            + "_A"
            + str(int(par[2]))
            + "_C"
            + str(int(par[3] * 100) / 100)
            + "_R"
            + str(int(par[4]))
        )
        plt.plot(
            params.freq_test * np.arange(state.MISFIT_CO.shape[0]),
            state.MISFIT_CO[:, l],
            label="MISFIT " + code,
        )
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        os.path.join(state.direct_name, "MISFIT_CO.png"),
        pad_inches=0,
    )
    plt.close("all")

    state.iceflow_model.save(
        os.path.join(state.direct_name, "model.h5")
    )


def _computenormp(dz, u, v, p):
    temp = tf.reduce_sum(dz * (tf.abs(u) ** p + tf.abs(v) ** p), axis=0)

    return (tf.reduce_sum(temp)) ** (1 / p)


def _computemisfitall(params, state, X, Y, YP):
    N = params.iflo_Nz
    thk = X[0, :, :, 0]

    # Vertical discretization
    zeta = np.arange(params.iflo_Nz) / (params.iflo_Nz - 1)
    temp = (zeta / params.iflo_vert_spacing) * (
        1.0 + (params.iflo_vert_spacing - 1.0) * zeta
    )
    temp = temp[1:] - temp[:-1]
    dz = tf.stack([thk * z for z in temp])

    ut, vt = Y_to_UV(params, Y)
    ut = ut[0]
    vt = vt[0]
    up, vp = Y_to_UV(params, YP)
    up = up[0]
    vp = vp[0]

    nl1bardiff, nl2bardiff = computemisfit(state, thk, ut - up, vt - vp)

    ut = 0.5 * (ut[1:, :, :] + ut[:-1, :, :])
    up = 0.5 * (up[1:, :, :] + up[:-1, :, :])
    vt = 0.5 * (vt[1:, :, :] + vt[:-1, :, :])
    vp = 0.5 * (vp[1:, :, :] + vp[:-1, :, :])

    nl1diff = _computenormp(dz, ut - up, vt - vp, 1.0).numpy()
    nl1abso = _computenormp(dz, ut, vt, 1.0).numpy()

    nl2diff = _computenormp(dz, ut - up, vt - vp, 2.0).numpy()
    nl2abso = _computenormp(dz, ut, vt, 2.0).numpy()

    return (nl1diff / nl1abso), (nl2diff / nl2abso), nl1bardiff, nl1bardiff


# find the directory of 'test' and 'train' folder, to reference data
def _findsubdata(folder):
    subdatasetpath = [f.path for f in os.scandir(folder) if f.is_dir()]

    subdatasetpath.sort(key=lambda x: (os.path.isdir(x), x))  # sort alphabtically

    subdatasetname = [f.split("/")[-1] for f in subdatasetpath]

    return subdatasetname, subdatasetpath


# this function is for data augmentation
def _aug(M, ri):
    for l in range(ri[0]):
        M = tf.image.rot90(M)
    if ri[1] == 1:
        M = tf.image.flip_left_right(M)
    if ri[2] == 1:
        M = tf.image.flip_up_down(M)
    if ri[3] == 1:
        M = tf.image.transpose(M)
    return M


def _plot_one_Glen(params, X, Y, path):

    from mpl_toolkits.axes_grid1 import make_axes_locatable

    #    N    = params.iflo_Nz
    #    ut   = Y[0,:,:,N-1] ; #tf.reduce_mean( Y[0,:,:,:N] , axis=-1)
    #    vt   = Y[0,:,:,2*N-1]  ; #tf.reduce_mean( Y[0,:,:,N:] , axis=-1)

    U, V = Y_to_UV(params, Y)
    ut = U[0, -1]
    vt = V[0, -1]

    thk = X[0, :, :, 0]

    velbar_magt = tf.norm(
        tf.concat([tf.expand_dims(ut, axis=-1), tf.expand_dims(vt, axis=-1)], axis=2),
        axis=2,
    )

    minvar = np.min(velbar_magt)
    maxvar = np.max(velbar_magt)

    fig, ax1 = plt.subplots(1, 1, figsize=(6, 6), dpi=200)

    #        ax1.set_title("STOKES " + tit)
    im1 = ax1.imshow(
        velbar_magt,
        origin="lower",
        vmin=minvar,
        vmax=maxvar,
        cmap="viridis",
    )
    divider = make_axes_locatable(ax1)
    cax1 = divider.append_axes("right", size="5%", pad=0.05)
    cbar1 = plt.colorbar(im1, format="%.0f", cax=cax1, orientation="vertical")
    ax1.axis("off")

    plt.tight_layout()
    plt.savefig(os.path.join(path, "STOKES.png"), pad_inches=0)
    plt.close("all")


def _plot_iceflow_Glen(params, state, X, Y, YP, tit, path):

    from mpl_toolkits.axes_grid1 import make_axes_locatable

    #    N    = params.iflo_Nz

    #    ut   = Y[0,:,:,N-1] ; #tf.reduce_mean( Y[0,:,:,:N] , axis=-1)
    #    vt   = Y[0,:,:,2*N-1]  ; #tf.reduce_mean( Y[0,:,:,N:] , axis=-1)

    #    up   = YP[0,:,:,N-1] ; #up   = tf.reduce_mean( YP[0,:,:,:N] , axis=-1)
    #    vp   = YP[0,:,:,2*N-1] ; #vp   = tf.reduce_mean( YP[0,:,:,N:] , axis=-1)

    U, V = Y_to_UV(params, Y)
    ut = U[0, -1]
    vt = V[0, -1]
    UP, VP = Y_to_UV(params, YP)
    up = UP[0, -1]
    vp = VP[0, -1]

    thk = X[0, :, :, 0]

    velbar_magt = tf.norm(
        tf.concat([tf.expand_dims(ut, axis=-1), tf.expand_dims(vt, axis=-1)], axis=2),
        axis=2,
    )
    velbar_magp = tf.norm(
        tf.concat([tf.expand_dims(up, axis=-1), tf.expand_dims(vp, axis=-1)], axis=2),
        axis=2,
    )

    minvar = np.min(velbar_magt)
    maxvar = np.max(velbar_magt)

    minvardiff = -maxvar / 10
    maxvardiff = maxvar / 10

    nl1, nl2, nbarl1, nbarl1a = _computemisfitall(params, state, X, Y, YP)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 6), dpi=200)

    ax1.set_title("STOKES ")
    im1 = ax1.imshow(
        velbar_magt,
        origin="lower",
        vmin=minvar,
        vmax=maxvar,
        cmap="viridis",
    )
    divider = make_axes_locatable(ax1)
    cax1 = divider.append_axes("right", size="5%", pad=0.05)
    cbar1 = plt.colorbar(im1, format="%.0f", cax=cax1, orientation="vertical")
    ax1.axis("off")

    ax2.set_title("PINN ")
    im2 = ax2.imshow(
        velbar_magp,
        origin="lower",
        vmin=minvar,
        vmax=maxvar,
        cmap="viridis",
    )
    divider = make_axes_locatable(ax2)
    cax2 = divider.append_axes("right", size="5%", pad=0.05)
    cbar2 = plt.colorbar(im2, format="%.0f", cax=cax2, orientation="vertical")
    ax2.axis("off")

    ax3.set_title("Misfit : " + str(int(100 * nbarl1)) + " %")
    im3 = ax3.imshow(
        velbar_magp - velbar_magt,
        origin="lower",
        vmin=minvardiff,
        vmax=maxvardiff,
        cmap="RdBu",
    )
    divider = make_axes_locatable(ax3)
    cax3 = divider.append_axes("right", size="5%", pad=0.05)
    cbar3 = plt.colorbar(im3, format="%.0f", cax=cax3, orientation="vertical")
    ax3.axis("off")

    plt.tight_layout()
    plt.savefig(os.path.join(path, "DIFF_" + tit + ".png"), pad_inches=0)
    plt.close("all")
