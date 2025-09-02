from typing import Tuple, Optional

import numpy as np
from pyCFS.data.util import TimeRecord, array_memory_usage


def vkp_spectrum(
    K: np.ndarray, nu: float, urms: np.ndarray, epsilon: np.ndarray, ke: np.ndarray, kmin=0.0, kmax=1e6
) -> np.ndarray:
    # Reshape arrays
    urms = urms[:, np.newaxis]
    epsilon = epsilon[:, np.newaxis]
    ke = ke[:, np.newaxis]

    # computed from input to satisfy homogeneous turbulence properties
    Kappae = np.sqrt(5.0 / 12.0) * ke
    Alpha = 1.452762113
    KappaEta = pow(epsilon, 0.25) * pow(nu, -3.0 / 4.0)
    r1 = K / Kappae
    r2 = K / KappaEta
    espec = Alpha * urms * urms / Kappae * pow(r1, 4) / pow(1.0 + r1 * r1, 17.0 / 6.0) * np.exp(-2.0 * r2 * r2)
    return espec


def eval_stochastic_input(
    dof_ids_process: np.ndarray,
    kin_viscosity: float,
    length_scale_factor: float,
    tke: np.ndarray,
    tdr: np.ndarray,
    max_wave_number_percentage: float,
    min_wave_number_percentage: float,
    num_modes: int,
    urms: np.ndarray,
    C_mu=0.09,
    vkp_scaling_const=1.452762113,
    eps_orthogonal=1e-9,
    rn_gen=np.random.default_rng(),
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # calcLengthScale (2.68)
    turb_length_scale = length_scale_factor * C_mu * tke[dof_ids_process] ** (3 / 2) / tdr[dof_ids_process]  # l
    # calcMostEnergeticWaveNumber (2.70)
    K_e = 9 * np.pi / 55 * vkp_scaling_const / turb_length_scale
    del turb_length_scale
    # (4.9)
    K_N = max_wave_number_percentage * K_e
    # (4.8)
    K_1 = min_wave_number_percentage * K_e
    # assembleWaveNumbers (2.72)
    DK_lin = ((K_N - K_1) / (num_modes - 1)).reshape(dof_ids_process.size, 1)
    K = np.linspace(start=K_1, stop=K_N, num=num_modes, axis=1)
    del K_1, K_N

    # evalEnergy (2.61)
    E = vkp_spectrum(K, kin_viscosity, urms[dof_ids_process], tdr[dof_ids_process], K_e)
    del K_e, kin_viscosity, tdr

    # calcModeAmplitude (2.60)
    u_tilde = np.sqrt(E * DK_lin)
    del DK_lin, E

    # angular frequency (2.67)
    omega = rn_gen.normal(
        loc=urms[dof_ids_process, np.newaxis] * K,
        scale=urms[dof_ids_process, np.newaxis] * K,
        size=(dof_ids_process.size, num_modes),
    )
    del urms

    # randomly draw alpha
    alpha = rn_gen.uniform(low=0.0, high=2 * np.pi, size=(dof_ids_process.size, num_modes))
    # randomly draw phi
    phi = rn_gen.uniform(low=0.0, high=2 * np.pi, size=(dof_ids_process.size, num_modes))
    # randomly draw psi
    psi = rn_gen.uniform(low=0.0, high=2 * np.pi, size=(dof_ids_process.size, num_modes))
    # randomly draw theta (4.2) - (4.4)
    theta = np.arccos(1 - 2 * rn_gen.uniform(low=0.0, high=1.0, size=(dof_ids_process.size, num_modes)))
    # assemble wave vector
    wave_vec = np.stack([K * np.cos(theta) * np.cos(phi), K * np.sin(phi), -K * np.sin(theta) * np.cos(phi)], axis=2)
    # assemble mode direction
    sigma_vec = np.stack(
        [
            -np.sin(phi) * np.cos(alpha) * np.cos(theta) + np.sin(alpha) * np.sin(theta),
            np.cos(phi) * np.cos(alpha),
            np.sin(phi) * np.cos(alpha) * np.sin(theta) + np.sin(alpha) * np.cos(theta),
        ],
        axis=2,
    )

    # check if wave vector and mode direction are orthogonal
    wave_div = np.einsum("ijk,ijk->ij", wave_vec, sigma_vec)

    if np.any(wave_div > eps_orthogonal):
        print(f"Orthogonality check failed. Maximum divergence in wave space: {wave_div.max()}")

    return u_tilde, omega, psi, wave_vec, sigma_vec


def eval_fluct_velocity(
    i: int,
    timesteps: np.ndarray,
    u_tilde: np.ndarray,
    wave_vec: np.ndarray,
    coords: np.ndarray,
    mean_velocity: np.ndarray,
    dof_ids_process: np.ndarray,
    psi: np.ndarray,
    omega: np.ndarray,
    sigma_vec: np.ndarray,
) -> np.ndarray:
    num_dofs_process = len(dof_ids_process)

    u_prime_step = np.zeros((num_dofs_process, 3))
    t = timesteps[i]
    for n in range(u_tilde.shape[1]):
        # compute turbulent velocity fluctuations (2.66)
        u_prime_mode_contribution = (
            2
            * u_tilde[:, n]
            * np.cos(
                (wave_vec[:, n, :] * (coords[dof_ids_process, :] - t * mean_velocity[dof_ids_process, :])).sum(1)
                + psi[:, n]
                + omega[:, n] * t
            )
        )
        u_prime_step += u_prime_mode_contribution.reshape(num_dofs_process, 1) * sigma_vec[:, n, :]

    return u_prime_step


def eval_fluct_velocity_vectorized(
    timesteps: np.ndarray,
    u_tilde: np.ndarray,
    wave_vec: np.ndarray,
    coords: np.ndarray,
    mean_velocity: np.ndarray,
    dof_ids_process: np.ndarray,
    psi: np.ndarray,
    omega: np.ndarray,
    sigma_vec: np.ndarray,
) -> np.ndarray:

    # compute turbulent velocity fluctuations (2.66)
    tmp = (
        2
        * u_tilde[np.newaxis, :, :]
        * np.cos(
            (
                wave_vec[np.newaxis, :, :, :]
                * (
                    coords[np.newaxis, dof_ids_process, np.newaxis, :]
                    - timesteps[:, np.newaxis, np.newaxis, np.newaxis]
                    * mean_velocity[np.newaxis, dof_ids_process, np.newaxis, :]
                )
            ).sum(3)
            + psi[np.newaxis, :, :]
            + omega[np.newaxis, :, :] * timesteps[:, np.newaxis, np.newaxis]
        )
    )

    return (tmp[..., np.newaxis] * sigma_vec[np.newaxis, :, :, :]).sum(2)


def compute_fourier_coefficients(
    omega: np.ndarray,
    wave_vec: np.ndarray,
    mean_velocity: np.ndarray,
    dof_ids_process: np.ndarray,
    coords: np.ndarray,
    u_tilde: np.ndarray,
    psi: np.ndarray,
    sigma_vec: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:

    omega_effective = omega - (wave_vec * (mean_velocity[dof_ids_process, np.newaxis, :])).sum(2)
    del omega

    # Scalar term
    grad_u_prime_scalar_fourier_1 = (
        1j
        * np.sqrt(2 * np.pi)
        * u_tilde
        * np.exp(-1j * ((wave_vec * coords[dof_ids_process, np.newaxis, :]).sum(2) + psi))
    )

    # Multiply with wave vector
    tmp_1 = grad_u_prime_scalar_fourier_1[:, :, np.newaxis] * wave_vec

    # Vectorized outer product
    grad_u_prime_fourier_1 = tmp_1[..., np.newaxis] * sigma_vec[:, :, np.newaxis, :]

    del grad_u_prime_scalar_fourier_1, tmp_1

    grad_u_prime_scalar_fourier_2 = (
        1j
        * np.sqrt(2 * np.pi)
        * u_tilde
        * np.exp(1j * ((wave_vec * coords[dof_ids_process, np.newaxis, :]).sum(2) + psi))
    )
    tmp_2 = grad_u_prime_scalar_fourier_2[:, :, np.newaxis] * wave_vec
    grad_u_prime_fourier_2 = tmp_2[..., np.newaxis] * sigma_vec[:, :, np.newaxis, :]

    return omega_effective, grad_u_prime_fourier_1, grad_u_prime_fourier_2


def compute_lighthill_rhs(
    *,
    f_steps: np.ndarray,
    omega_effective: np.ndarray,
    grad_u_prime_fourier_1: np.ndarray,
    grad_u_prime_fourier_2: np.ndarray,
    density: float,
) -> np.ndarray:
    num_dofs_process = omega_effective.shape[0]
    delta_f = f_steps[1] - f_steps[0]

    grad_u_prime_process = np.zeros((f_steps.size, num_dofs_process, 3, 3), dtype=complex)

    f_interval = np.array((f_steps - 0.5 * delta_f, f_steps + 0.5 * delta_f))

    idx_contribution_1 = np.nonzero(
        (omega_effective[np.newaxis, ...] >= (2 * np.pi * f_interval[0, :, np.newaxis, np.newaxis]))
        * (omega_effective[np.newaxis, ...] < (2 * np.pi * f_interval[1, :, np.newaxis, np.newaxis]))
    )

    for k in range(f_steps.size):
        idx_process = idx_contribution_1[0] == k
        grad_u_prime_process[k, idx_contribution_1[1][idx_process], ...] += grad_u_prime_fourier_1[
            idx_contribution_1[1][idx_process], idx_contribution_1[2][idx_process], :
        ]

    del idx_contribution_1

    idx_contribution_2 = np.nonzero(
        (-omega_effective[np.newaxis, ...] >= (2 * np.pi * f_interval[0, :, np.newaxis, np.newaxis]))
        * (-omega_effective[np.newaxis, ...] < (2 * np.pi * f_interval[1, :, np.newaxis, np.newaxis]))
    )

    for k in range(f_steps.size):
        idx_process = idx_contribution_2[0] == k
        grad_u_prime_process[k, idx_contribution_2[1][idx_process], ...] += grad_u_prime_fourier_2[
            idx_contribution_2[1][idx_process], idx_contribution_2[2][idx_process], :
        ]

    return density * np.einsum("ijkl,ijkl->ij", grad_u_prime_process, grad_u_prime_process)


def compute_stochastic_velocity_fluctuations(
    coords: np.ndarray,
    mean_velocity: np.ndarray,
    tke: np.ndarray,
    tdr: np.ndarray,
    kin_viscosity: float,
    crit_tke_percentage: float,
    max_wave_number_percentage: float,
    min_wave_number_percentage: float,
    num_modes: int,
    num_steps: int,
    delta_t: float,
    length_scale_factor: float = 1.0,
    C_mu=0.09,
    vkp_scaling_const=1.452762113,
    eps_orthogonal: float = 1e-9,
    rn_gen=np.random.default_rng(),
    max_memory_usage: Optional[float] = None,  # in GB
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute stochastic velocity fluctuations using the SNGR (stochastic noise generation and radiation) method.

    Parameters
    ----------
    coords: np.ndarray
        Coordinates of the DOFs in the mesh, shape (num_dofs, 3).
    mean_velocity: np.ndarray
        Mean velocity of the stationary flow field, shape (num_dofs, 3).
    tke: np.ndarray
        Turbulent kinetic energy of the stationary flow field, shape (num_dofs,).
    tdr: np.ndarray
        Turbulent dissipation rate of the stationary flow field, shape (num_dofs,).
    kin_viscosity: float
        Kinematic viscosity of the fluid.
    crit_tke_percentage: float
        Percentage of the maximum turbulent kinetic energy, processing only values above the threshold, default is 0.01.
    max_wave_number_percentage: float
        Percentage of the most energetic wave number
    min_wave_number_percentage: float
        Percentage of the minimum wave number
    num_modes: int
        Number of modes to be used in the fourier series expansion of the velocity fluctuations.
    num_steps: int
        Number of time steps to generate the fluctuating velocity field.
    delta_t: float
        Time step size
    length_scale_factor: float
        Factor to adjust the length scale of the turbulence, default is 1.0. [2, Eq. (2.68)]
    C_mu: float, optional
        Closure coefficient for the turbulence model, default is 0.09. [2, Eq. (2.69)]
    vkp_scaling_const: float, optional
        Energy spectrum scaling constant, default is 1.452762113. [2, Eq. (2.62)]
    eps_orthogonal: float, optional
        Threshold for orthogonality check of wave vector and mode direction, default is 1e-9.
    rn_gen: np.random.Generator, optional
        Random number generator, default is np.random.default_rng().
    max_memory_usage: float, optional
        Maximum memory usage in GB for the computation of the Lighthill source density. If None, no limit is set.

    Returns
    -------
    u_prime: np.ndarray
        fluctuating velocity field of the stationary flow field, shape (num_steps, num_dofs, 3).
    timesteps: np.ndarray
        Timesteps for the fluctuating velocity field, shape (num_steps,).

    References
    ----------
    [1] Wurzinger, A., Schoder, S., Mayr-Mittermüller, B., Kaltenbacher, M. and Sima, H., 2025. Hydrodynamic and
    flow-acoustic simulation of a two-chamber piston hydraulic system prone to whistling. Results in Engineering, p.105220.
    [2] Weitz, M., 2019. An Approach to Compute Cavity Noise Using Stochastic Noise Generation and Radiation (Master’s Thesis). TU Wien, Vienna.
    """

    # TODO: add reference to dissertation
    num_dofs = coords.shape[0]

    k_max = max(tke)
    k_min = crit_tke_percentage * k_max

    # Compute the root mean square of the turbulent velocity fluctuations
    urms = np.sqrt(2.0 / 3.0 * tke)

    # Create time steps
    timesteps = delta_t * np.arange(num_steps)

    # Initialize fluctuating velocity field
    u_prime = np.zeros((num_steps, num_dofs, 3))

    # get tke threshold
    dof_ids_threshold = np.where(tke > k_min)[0]

    if max_memory_usage is None:
        num_dofs_process = len(dof_ids_threshold)
    else:
        # RAM usage estimate
        mem_base = coords.nbytes + mean_velocity.nbytes + tke.nbytes + tdr.nbytes + urms.nbytes + u_prime.nbytes
        if max_memory_usage * 1e9 < mem_base:
            raise ValueError(
                f"Specified maximum memory usage {max_memory_usage} GB is too low for the base memory usage of {mem_base / 1e9:.2f} GB."
            )

        # Stochastic input memory usage
        mem_per_dof_stochastic = (
            array_memory_usage((1, num_modes), float)  # u_tilde
            + array_memory_usage((1, num_modes), float)  # omega
            + array_memory_usage((1, num_modes), float)  # u_tilde
            + array_memory_usage((1, num_modes), float)  # alpha
            + array_memory_usage((1, num_modes), float)  # phi
            + array_memory_usage((1, num_modes), float)  # psi
            + array_memory_usage((1, num_modes), float)  # theta
            + array_memory_usage((1, num_modes, 3), float)  # wave_vec
            + array_memory_usage((1, num_modes, 3), float)  # sigma_vec
        )

        # Velocity memory usage
        mem_per_dof_velocity = (
            array_memory_usage((num_steps, 1, num_modes), float)  # tmp
            + array_memory_usage((num_steps, 1, 3), float)  # u_prime_process
            + array_memory_usage((1, num_modes), float)  # omega
            + array_memory_usage((1, num_modes), float)  # u_tilde
            + array_memory_usage((1, num_modes), float)  # psi
            + array_memory_usage((1, num_modes, 3), float)  # wave_vec
            + array_memory_usage((1, num_modes, 3), float)  # sigma_vec
        )

        mem_per_dof = max(mem_per_dof_stochastic, mem_per_dof_velocity)

        # Calculate the maximum number of DOFs that can be processed without exceeding the memory limit
        num_dofs_process = int((max_memory_usage * 1e9 - mem_base) / mem_per_dof)

    num_process_blocks = int(np.ceil(len(dof_ids_threshold) / num_dofs_process))

    for idx_block in range(num_process_blocks):

        if num_process_blocks > 1:
            print(f"- Processing block {idx_block + 1}/{num_process_blocks}")

        dof_ids_process = dof_ids_threshold[
            idx_block * num_dofs_process : min(dof_ids_threshold.size, (idx_block + 1) * num_dofs_process)
        ]

        eval_stochastic_input_args = {
            "dof_ids_process": dof_ids_process,
            "kin_viscosity": kin_viscosity,
            "length_scale_factor": length_scale_factor,
            "tke": tke,
            "tdr": tdr,
            "max_wave_number_percentage": max_wave_number_percentage,
            "min_wave_number_percentage": min_wave_number_percentage,
            "num_modes": num_modes,
            "urms": urms,
            "C_mu": C_mu,
            "vkp_scaling_const": vkp_scaling_const,
            "eps_orthogonal": eps_orthogonal,
            "rn_gen": rn_gen,
        }

        with TimeRecord(message="Draw stochastic quantities"):
            u_tilde, omega, psi, wave_vec, sigma_vec = eval_stochastic_input(**eval_stochastic_input_args)

        eval_fluct_velocity_args = {
            "timesteps": timesteps,
            "u_tilde": u_tilde,
            "wave_vec": wave_vec,
            "coords": coords,
            "mean_velocity": mean_velocity,
            "dof_ids_process": dof_ids_process,
            "psi": psi,
            "omega": omega,
            "sigma_vec": sigma_vec,
        }
        with TimeRecord(message="Compute turbulent velocity fluctuations"):
            u_prime_process = eval_fluct_velocity_vectorized(**eval_fluct_velocity_args)

        u_prime[:, dof_ids_process, :] = u_prime_process

    return u_prime, timesteps


def compute_stochastic_harmonic_lighthill_rhs(
    coords: np.ndarray,
    mean_velocity: np.ndarray,
    tke: np.ndarray,
    tdr: np.ndarray,
    kin_viscosity: float,
    density: float,
    crit_tke_percentage: float,
    max_wave_number_percentage: float,
    min_wave_number_percentage: float,
    num_modes: int,
    num_steps: int,
    f_min: float,
    f_max: float,
    length_scale_factor: float = 1.0,
    C_mu=0.09,
    vkp_scaling_const=1.452762113,
    eps_orthogonal: float = 1e-9,
    rn_gen=np.random.default_rng(),
    max_memory_usage: Optional[float] = None,  # in GB
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute stochastic velocity fluctuations using the SNGR (stochastic noise generation and radiation) method.

    Parameters
    ----------
    coords: np.ndarray
        Coordinates of the DOFs in the mesh, shape (num_dofs, 3).
    mean_velocity: np.ndarray
        Mean velocity of the stationary flow field, shape (num_dofs, 3).
    tke: np.ndarray
        Turbulent kinetic energy of the stationary flow field, shape (num_dofs,).
    tdr: np.ndarray
        Turbulent dissipation rate of the stationary flow field, shape (num_dofs,).
    kin_viscosity: float
        Kinematic viscosity of the fluid.
    density: float
        Fluid density.
    crit_tke_percentage: float
        Percentage of the maximum turbulent kinetic energy, processing only values above the threshold, default is 0.01.
    max_wave_number_percentage: float
        Percentage of the most energetic wave number
    min_wave_number_percentage: float
        Percentage of the minimum wave number
    num_modes: int
        Number of modes to be used in the fourier series expansion of the velocity fluctuations.
    num_steps: int
        Number of time steps to generate the fluctuating velocity field.
    f_min: float
        Minimum frequency for the linear frequency sampling, in Hz.
    f_max: float
        Maximum frequency for the linear frequency sampling, in Hz.
    length_scale_factor: float, optional
        Factor to adjust the length scale of the turbulence, default is 1.0. [2, Eq. (2.68)]
    C_mu: float, optional
        Closure coefficient for the turbulence model, default is 0.09. [2, Eq. (2.69)]
    vkp_scaling_const: float, optional
        Energy spectrum scaling constant, default is 1.452762113. [2, Eq. (2.62)]
    eps_orthogonal: float, optional
        Threshold for orthogonality check of wave vector and mode direction, default is 1e-9.
    rn_gen: np.random.Generator, optional
        Random number generator, default is np.random.default_rng().
    max_memory_usage: float, optional
        Maximum memory usage in GB for the computation of the Lighthill source density. If None, no limit is set.

    Returns
    -------
    lighthill_rhs: np.ndarray
        Lighthill source density, shape (num_steps, num_dofs,).
    f_steps: np.ndarray
        Frequency step values for the harmonic Lighthill source density, shape (num_steps,).

    References
    ----------
    [1] Wurzinger, A., Schoder, S., Mayr-Mittermüller, B., Kaltenbacher, M. and Sima, H., 2025. Hydrodynamic and
    flow-acoustic simulation of a two-chamber piston hydraulic system prone to whistling. Results in Engineering, p.105220.
    [2] Weitz, M., 2019. An Approach to Compute Cavity Noise Using Stochastic Noise Generation and Radiation (Master’s Thesis). TU Wien, Vienna.
    """
    # TODO: add reference to dissertation
    num_dofs = coords.shape[0]

    k_max = max(tke)
    k_min = crit_tke_percentage * k_max

    # Compute the root mean square of the turbulent velocity fluctuations
    urms = np.sqrt(2.0 / 3.0 * tke)

    # Create frequency steps for the harmonic data
    delta_f = (f_max - f_min) / (num_steps - 1)
    f_steps = np.arange(start=f_min, stop=f_max + delta_f, step=delta_f)

    # Initialize Lighthill source density
    lighthill_rhs = np.zeros((num_steps, num_dofs), dtype=complex)

    # get tke threshold
    dof_ids_threshold = np.where(tke > k_min)[0]

    if max_memory_usage is None:
        num_dofs_process = len(dof_ids_threshold)
    else:
        # RAM usage estimate
        mem_base = coords.nbytes + mean_velocity.nbytes + tke.nbytes + tdr.nbytes + urms.nbytes + lighthill_rhs.nbytes
        if max_memory_usage * 1e9 < mem_base:
            raise ValueError(
                f"Specified maximum memory usage {max_memory_usage} GB is too low for the base memory usage of {mem_base / 1e9:.2f} GB."
            )

        # Stochastic input memory usage
        mem_per_dof_stochastic = (
            array_memory_usage((1, num_modes), float)  # u_tilde
            + array_memory_usage((1, num_modes), float)  # omega
            + array_memory_usage((1, num_modes), float)  # u_tilde
            + array_memory_usage((1, num_modes), float)  # alpha
            + array_memory_usage((1, num_modes), float)  # phi
            + array_memory_usage((1, num_modes), float)  # psi
            + array_memory_usage((1, num_modes), float)  # theta
            + array_memory_usage((1, num_modes, 3), float)  # wave_vec
            + array_memory_usage((1, num_modes, 3), float)  # sigma_vec
        )

        # Fourier coefficients memory usage
        mem_per_dof_fourier = (
            array_memory_usage((1, num_modes, 3, 3), complex)  # grad_u_prime_fourier_1
            + array_memory_usage((1, num_modes, 3, 3), complex)  # grad_u_prime_fourier_2
            + array_memory_usage((1, num_modes), complex)  # grad_u_prime_scalar_fourier_2
            + array_memory_usage((1, num_modes, 3), complex)  # tmp_2
            + array_memory_usage((1, num_modes), float)  # omega_effective
            + array_memory_usage((1, num_modes), float)  # u_tilde
            + array_memory_usage((1, num_modes), float)  # psi
            + array_memory_usage((1, num_modes, 3), float)  # wave_vec
            + array_memory_usage((1, num_modes, 3), float)  # sigma_vec
        )

        # Lighthill source density memory usage
        mem_per_dof_lighthill = (
            array_memory_usage((1, num_modes, 3, 3), complex)  # f_grad_u_prime_scalar_fourier_1
            + array_memory_usage((1, num_modes, 3, 3), complex)  # f_grad_u_prime_scalar_fourier_2
            + array_memory_usage((num_steps, 1, 3, 3), complex)  # grad_u_prime_process
            + array_memory_usage((num_steps, 1), complex)  # lighthill_rhs_process
        )

        mem_per_dof = max(mem_per_dof_stochastic, mem_per_dof_fourier, mem_per_dof_lighthill)

        # Calculate the maximum number of DOFs that can be processed without exceeding the memory limit
        num_dofs_process = int((max_memory_usage * 1e9 - mem_base) / mem_per_dof)

    num_process_blocks = int(np.ceil(len(dof_ids_threshold) / num_dofs_process))

    for idx_block in range(num_process_blocks):

        if num_process_blocks > 1:
            print(f"- Processing block {idx_block + 1}/{num_process_blocks}")

        dof_ids_process = dof_ids_threshold[
            idx_block * num_dofs_process : min(dof_ids_threshold.size, (idx_block + 1) * num_dofs_process)
        ]

        eval_stochastic_input_args = {
            "dof_ids_process": dof_ids_process,
            "kin_viscosity": kin_viscosity,
            "length_scale_factor": length_scale_factor,
            "tke": tke,
            "tdr": tdr,
            "max_wave_number_percentage": max_wave_number_percentage,
            "min_wave_number_percentage": min_wave_number_percentage,
            "num_modes": num_modes,
            "urms": urms,
            "C_mu": C_mu,
            "vkp_scaling_const": vkp_scaling_const,
            "eps_orthogonal": eps_orthogonal,
            "rn_gen": rn_gen,
        }

        with TimeRecord(message="Draw stochastic quantities"):
            u_tilde, omega, psi, wave_vec, sigma_vec = eval_stochastic_input(**eval_stochastic_input_args)

        # Compute effective angular frequencies
        compute_fourier_coefficients_args = {
            "omega": omega,
            "wave_vec": wave_vec,
            "mean_velocity": mean_velocity,
            "dof_ids_process": dof_ids_process,
            "coords": coords,
            "u_tilde": u_tilde,
            "psi": psi,
            "sigma_vec": sigma_vec,
        }

        with TimeRecord(message="Compute fourier coefficients"):
            omega_effective, grad_u_prime_fourier_1, grad_u_prime_fourier_2 = compute_fourier_coefficients(
                **compute_fourier_coefficients_args
            )

        # Compute Lighthill source density
        with TimeRecord(message="Compute lighthill source density"):
            lighthill_rhs_process = compute_lighthill_rhs(
                f_steps=f_steps,
                omega_effective=omega_effective,
                grad_u_prime_fourier_1=grad_u_prime_fourier_1,
                grad_u_prime_fourier_2=grad_u_prime_fourier_2,
                density=density,
            )

        lighthill_rhs[:, dof_ids_process] = lighthill_rhs_process

    return lighthill_rhs, f_steps
