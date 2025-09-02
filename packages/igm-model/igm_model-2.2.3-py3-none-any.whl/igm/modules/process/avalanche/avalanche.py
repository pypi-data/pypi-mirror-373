#!/usr/bin/env python3

# Published under the GNU GPL (Version 3), check at the LICENSE file

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import time


def params(parser):
    parser.add_argument(
        "--aval_update_freq",
        type=float,
        default=1,
        help="Update avalanche each X years (1)",
    )

    parser.add_argument(
        "--aval_angleOfRepose",
        type=float,
        default=30,
        help="Angle of repose (30°)",
    )
    
    parser.add_argument(
        "--aval_stop_redistribution_thk",
        type=float,
        default=0.02,
        help="Stop redistribution if the mean thickness is below this value (m) over the whole grid",
    )


def initialize(params, state):
    state.tcomp_avalanche = []
    state.tlast_avalanche = tf.Variable(params.time_start, dtype=tf.float32)


def update(params, state):
    if (state.t - state.tlast_avalanche) >= params.aval_update_freq:
        if hasattr(state, "logger"):
            state.logger.info("Update AVALANCHE at time : " + str(state.t.numpy()))

        state.tcomp_avalanche.append(time.time())

        H = state.thk
        Zb = state.topg
        Zi = Zb + H
        
        # the elevation difference of the cells that is considered to be stable
        dHRepose = state.dx * tf.math.tan(
            params.aval_angleOfRepose * np.pi / 180.0
        )
        Ho = tf.maximum(H, 0)

        count = 0
        # volume redistributed # for documentation if needed
        # volumes = []
        

        while count <=300:
            count += 1
            
            # find out, in which direction is down (instead of doing normal gradients, we do the max of the two directions)

            dZidx_down = tf.pad(
                tf.maximum(Zi[:, 1:] - Zi[:, :-1], 0), [[0, 0], [1, 0]], "CONSTANT"
            )
            dZidx_up = tf.pad(
                tf.maximum(Zi[:, :-1] - Zi[:, 1:], 0), [[0, 0], [0, 1]], "CONSTANT"
            )
            dZidx = tf.maximum(dZidx_down, dZidx_up)

            dZidy_left = tf.pad(
                tf.maximum(Zi[1:, :] - Zi[:-1, :], 0), [[1, 0], [0, 0]], "CONSTANT"
            )
            dZidy_right = tf.pad(
                tf.maximum(Zi[:-1, :] - Zi[1:, :], 0), [[0, 1], [0, 0]], "CONSTANT"
            )
            dZidy = tf.maximum(dZidy_right, dZidy_left)

            grad = tf.math.sqrt(dZidx**2 + dZidy**2)
            gradT = dZidy_left + dZidy_right + dZidx_down + dZidx_up
            gradT = tf.where(gradT == 0, 1, gradT) # avoid devide by zero error. However, could influence the results (not checked) 
            grad = tf.where(Ho < 0.1, 0, grad)

            delH = tf.maximum(0, (grad - dHRepose) / 3.0)

            # ============ ANDREAS ADDED ===========
            # if there is less than a certain thickness to redesitribute, just redistribute the remaining thickness and stop afterwards
            # print(count, np.max(delH), np.sum(delH) / (np.shape(H)[0]*np.shape(H)[1]))
            mean_thickness = np.sum(delH) / (np.shape(H)[0]*np.shape(H)[1])
            
            if mean_thickness < params.aval_stop_redistribution_thk:
                # for a last time, use all the thickness to redistribute and then stop
                delH = tf.maximum(0, grad - dHRepose)
                count = 2000 # set to random high number to exit the loop
                
            # volumes.append(np.sum(delH) / (np.shape(H)[0]*np.shape(H)[1]))                
            # ================================

            Htmp = Ho
            Ho = tf.maximum(0, Htmp - delH)
            delH = Htmp - Ho

            # The thickness that is redistributed to the neighboring cells based on the fraction of if it should be up, down, left or right (dZidx_**/gradT)
            delHup = tf.pad(
                delH[:, :-1] * dZidx_up[:, :-1] / gradT[:, :-1],
                [[0, 0], [1, 0]],
                "CONSTANT",
            )
            delHdn = tf.pad(
                delH[:, 1:] * dZidx_down[:, 1:] / gradT[:, 1:],
                [[0, 0], [0, 1]],
                "CONSTANT",
            )
            delHrt = tf.pad(
                delH[:-1, :] * dZidy_right[:-1, :] / gradT[:-1, :],
                [[1, 0], [0, 0]],
                "CONSTANT",
            )
            delHlt = tf.pad(
                delH[1:, :] * dZidy_left[1:, :] / gradT[1:, :],
                [[0, 1], [0, 0]],
                "CONSTANT",
            )
            
            # calculate new thickness after distribution ensuring that the thickness is always positive
            Ho = tf.maximum(0, Ho + delHdn + delHup + delHlt + delHrt)

            Zi = Zb + Ho


        state.thk = Ho + tf.where(H < 0, H, 0)

        state.usurf = state.topg + state.thk

        state.tlast_avalanche.assign(state.t)

        state.tcomp_avalanche[-1] -= time.time()
        state.tcomp_avalanche[-1] *= -1


def finalize(params, state):
    pass
