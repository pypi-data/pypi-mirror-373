#cython: language_level=3, boundscheck=False, wraparound=False
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Group iSP and contributors

import numpy as np

cdef extern from "math.h":
    long double expl(long double) nogil
    long double logl(long double) nogil
    long double log1pl(long double) nogil
    int isinf(long double) nogil
    long double fabsl(long double) nogil
    const float INFINITY

ctypedef double dtype_t

cdef inline int _argmax(dtype_t[:] X) nogil:
    cdef dtype_t X_max = -INFINITY
    cdef int pos = 0
    cdef int i
    for i in range(X.shape[0]):
        if X[i] > X_max:
            X_max = X[i]
            pos = i
    return pos


cdef inline dtype_t _max(dtype_t[:] X) nogil:
    return X[_argmax(X)]


cdef inline dtype_t _logsumexp(dtype_t[:] X) nogil:
    cdef dtype_t X_max = _max(X)
    if isinf(X_max):
        return -INFINITY

    cdef dtype_t acc = 0
    for i in range(X.shape[0]):
        acc += expl(X[i] - X_max)
    return logl(acc) + X_max


cdef inline dtype_t _logaddexp(dtype_t a, dtype_t b) nogil:
    if isinf(a) and a < 0:
        return b
    elif isinf(b) and b < 0:
        return a
    else:
        return max(a, b) + log1pl(expl(-fabsl(a - b)))

def _u_only(int n_samples, int n_states, int n_durations,
            dtype_t[:, :] log_obsprob, dtype_t[:, :, :] u):
    cdef int t, j, d

    with nogil:
        for t in range(n_samples):
            for j in range(n_states):
                for d in range(n_durations):
                    if t < 1 or d < 1:
                        u[t, j, d] = log_obsprob[t, j]
                    else:
                        u[t, j, d] = u[t - 1, j, d - 1] + log_obsprob[t, j]


# evaluate current u_t(j, d). extends to t - d < 0 and t > n_samples - 1.
cdef inline dtype_t _curr_u(int n_samples, dtype_t[:, :, :] u, int t, int j, int d) nogil:
    if t - d >= 0 and t < n_samples:
        return u[t, j, d]
    elif t - d < 0:
        return u[t, j, t]
    elif d >= t - (n_samples - 1):
        return u[n_samples - 1, j, (n_samples - 1) + d - t]
    else:
        return 0.0


def _smoothed(int n_samples, int n_states, int n_durations,
              dtype_t[:, :] beta, dtype_t[:, :] betastar,
              int right_censor,
              dtype_t[:, :, :] eta, dtype_t[:, :, :] xi, dtype_t[:, :] gamma):
    cdef int t, j, d, i, h

    with nogil:
        for t in range(n_samples - 1, -1, -1):
            for i in range(n_states):
                # eta computation
                # note: if with right censor, then eta[t, :, :] for t >= n_samples will only
                # be used for gamma computation. since beta[t, :] = 0 for t >= n_samples, hence
                # no modifications to eta at t >= n_samples.
                for d in range(n_durations):
                    eta[t, i, d] = eta[t, i, d] + beta[t, i]
                # xi computation
                # note: at t == n_samples - 1, it is decided that xi[t, :, :] should be log(0),
                # either with right censor or without, because there is no more next data.
                for j in range(n_states):
                    if t == n_samples - 1:
                        xi[t, i, j] = -INFINITY
                    else:
                        xi[t, i, j] = xi[t, i, j] + betastar[t + 1, j]
                # gamma computation
                # note: this is the slow "original" method. the paper provides a faster
                # recursive method (using xi), but it requires subtraction and produced
                # numerical inaccuracies from our initial tests.
                gamma[t, i] = -INFINITY
                for d in range(n_durations):
                    for h in range(n_durations):
                        if h >= d and (t + d < n_samples or right_censor != 0):
                            gamma[t, i] = _logaddexp(gamma[t, i], eta[t + d, i, h])


def _viterbi(int n_samples, int n_states, int n_durations,
             dtype_t[:] log_startprob,
             dtype_t[:, :] log_transmat,
             dtype_t[:, :] log_duration,
             int left_censor, int right_censor,
             dtype_t[:, :, :] u):
    cdef int t_iter, t, j, d, i, j_dur, back_state, back_dur, back_t
    cdef dtype_t state_logl
    # set number of iterations for t
    if right_censor != 0:
        t_iter = n_samples + n_durations - 1
    else:
        t_iter = n_samples
    cdef dtype_t[:, ::1] delta = np.empty((t_iter, n_states))
    cdef int[:, :, ::1] psi = np.empty((t_iter, n_states, 2), dtype=np.int32)
    cdef dtype_t[::1] buffer0 = np.empty(n_states)
    cdef dtype_t[::1] buffer1 = np.empty(n_durations)
    cdef int[::1] buffer1_state = np.empty(n_durations, dtype=np.int32)
    cdef int[::1] state_sequence = np.empty(n_samples, dtype=np.int32)

    with nogil:
        # forward pass
        for t in range(t_iter):
            for j in range(n_states):
                for d in range(n_durations):
                    if t - d == 0 or (t - d < 0 and left_censor != 0):   # beginning
                        buffer1[d] = log_startprob[j] + log_duration[j, d] + _curr_u(n_samples, u, t, j, d)
                        buffer1_state[d] = -1   # place-holder only
                    elif t - d > 0:   # ongoing
                        for i in range(n_states):
                            if i != j:
                                buffer0[i] = delta[t - d - 1, i] + log_transmat[i, j] + _curr_u(n_samples, u, t, j, d)
                            else:
                                buffer0[i] = -INFINITY
                        buffer1[d] = _max(buffer0) + log_duration[j, d]
                        buffer1_state[d] = _argmax(buffer0)
                    else:   # this should not be chosen
                        buffer1[d] = -INFINITY
                delta[t, j] = _max(buffer1)
                j_dur = _argmax(buffer1)
                psi[t, j, 0] = j_dur   # psi[:, j, 0] is the duration of j
                psi[t, j, 1] = buffer1_state[j_dur]   # psi[:, j, 1] is the state leading to j
        # getting the last state and maximum log-likelihood
        if right_censor != 0:
            for d in range(n_durations):
                buffer1[d] = _max(delta[n_samples + d - 1])
                buffer1_state[d] = _argmax(delta[n_samples + d - 1])
            state_logl = _max(buffer1)
            j_dur = _argmax(buffer1)
            back_state = buffer1_state[j_dur]
            back_dur = psi[n_samples + j_dur - 1, back_state, 0] - j_dur
        else:
            state_logl = _max(delta[n_samples - 1])
            back_state = _argmax(delta[n_samples - 1])
            back_dur = psi[n_samples - 1, back_state, 0]
        # backward pass
        back_t = n_samples - 1
        for t in range(n_samples - 1, -1, -1):
            if back_dur < 0:
                back_state = psi[back_t, back_state, 1]
                back_dur = psi[t, back_state, 0]
                back_t = t
            state_sequence[t] = back_state
            back_dur -= 1

    return state_sequence, state_logl