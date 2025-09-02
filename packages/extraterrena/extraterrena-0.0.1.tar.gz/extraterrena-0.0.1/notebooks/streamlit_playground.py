from nullaterra import arrays, constants, simulation
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import importlib

importlib.reload(arrays)
importlib.reload(constants)
importlib.reload(simulation)

st.set_page_config(
    page_title="Signal Playground",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Signal Playground")
st.sidebar.header("Configs...")

num_antenna = st.sidebar.slider("num antennas", 1, 1000, 100)
antenna_spacing = st.sidebar.slider("antenna_spacing (wvs)", 0.25, 10.0, 0.5)

center_freq_ghz = 1.0
mid_freq = 1e9 * center_freq_ghz
bandwidth_mhz = 2

num_interferers = st.sidebar.slider("num interferers", 0, 10, 1)
num_eigenvectors_to_null = st.sidebar.slider("eigenvecs to null", 0, 50, 1)
interferers = []

with st.sidebar.expander("Source Parameters", expanded=True):
    source_f_center = st.slider(
        "source center frequency (GHz)",
        float(center_freq_ghz - bandwidth_mhz / 1000),
        float(center_freq_ghz + bandwidth_mhz / 1000),
        float(center_freq_ghz),
        step=bandwidth_mhz / (10 * 1000),
        format="%0.4f",
    )
    source_f_bandwidth = st.slider(
        "source frequency bandwidth (MHz)", 0.1, float(bandwidth_mhz), 1.0, step=0.1
    )
    source_power = st.slider("source power", 0.1, 100.0, 1.0)
    source_theta_signal_deg = st.slider("source DoA degrees", 0, 90, 40)
    source_f_low = 1e9 * (source_f_center - 0.5 * source_f_bandwidth / 1_000)
    source_f_high = 1e9 * (source_f_center + 0.5 * source_f_bandwidth / 1_000)

with st.sidebar.expander(
    f"Interferer Parameters ({num_interferers} total)", expanded=True
):
    for i in range(num_interferers):
        st.markdown(f"**Interferer {i + 1}**")

        # Create unique keys for each slider to avoid conflicts
        freq_center = st.slider(
            f"Frequency_Center {i + 1} (GHz)",
            min_value=center_freq_ghz - bandwidth_mhz / 1_000,
            max_value=center_freq_ghz + bandwidth_mhz / 1_000,
            value=center_freq_ghz - i * 0.001,  # Default values that vary slightly
            step=0.0001,
            key=f"freq_center_{i}",
            format="%0.4f",
        )

        freq_bandwidth = st.slider(
            f"Frequency_Bandwidth {i + 1} (MHz)",
            min_value=0.1,
            max_value=float(bandwidth_mhz),
            value=1.0 + i * 1.0,  # Default values that vary slightly
            step=0.1,
            key=f"freq_bandwidth_{i}",
        )
        power = st.slider(
            f"Power {i + 1}",
            min_value=1.0,
            max_value=1000.0,
            value=10 - i * 0.1,  # Decreasing amplitude by default
            step=1.0,
            key=f"power_{i}",
        )

        direction = st.slider(
            f"Direction {i + 1} (degrees)",
            min_value=0,
            max_value=360,
            value=i * (360 // max(num_interferers, 1)),  # Spread evenly
            step=1,
            key=f"dir_{i}",
        )

        # Add to interferers list
        interferers.append(
            {
                "frequency_low": 1e9 * (freq_center - 0.5 * freq_bandwidth / 1_000),
                "frequency_high": 1e9 * (freq_center + 0.5 * freq_bandwidth / 1_000),
                "power": power,
                "direction": direction,
            }
        )

        # Add separator except for last interferer
        if i < num_interferers - 1:
            st.markdown("---")
interferer_f_low = [inter["frequency_low"] for inter in interferers]
interferer_f_high = [inter["frequency_high"] for inter in interferers]
interferer_theta_signal_deg = [inter["direction"] for inter in interferers]
interferer_power = [inter["power"] for inter in interferers]
sigma = st.sidebar.slider("noise sigma", 0.0, 5.0, 0.5)
lambda_ridge = st.sidebar.slider("ridge lambda", 0.0, 5.0, 0.0, step=0.1)
wv = [constants.c / mid_freq]
d = wv[0] * antenna_spacing
array = arrays.UniformLinearArray(num_antenna, d)

fs = 2 * bandwidth_mhz * 1e6

t = np.linspace(0, 1001 / fs, 1_000)
X_true = np.array(
    [
        simulation.simulate(
            array,
            source_f_low,
            source_f_high,
            [],
            [],
            source_theta_signal_deg,
            [],
            source_power,
            [],
            t,
            sigma=sigma,
            sampling_frequency=fs,
            center_freq=mid_freq,
        )
    ]
)
X = np.array(
    [
        simulation.simulate(
            array,
            source_f_low,
            source_f_high,
            interferer_f_low,
            interferer_f_high,
            source_theta_signal_deg,
            interferer_theta_signal_deg,
            source_power,
            interferer_power,
            t,
            sigma=sigma,
            sampling_frequency=fs,
            center_freq=mid_freq,
        )
    ]
)
channel = 0
acm = X[channel, :, :] @ X[channel, :, :].conj().T
evals, evecs = np.linalg.eigh(acm)


A = evecs[:, -(num_eigenvectors_to_null):]
AH = A.conj().T
orth_proj = np.identity(A.shape[0]) - A @ np.linalg.inv(AH @ A) @ AH
theta_rad = np.deg2rad(source_theta_signal_deg)
w = array.steering_vector(theta_rad, np.array([constants.c / mid_freq]))

oblique_proj = w @ np.linalg.inv(w.conj().T @ orth_proj @ w) @ w.conj().T @ orth_proj
w = array.steering_vector(
    theta_rad,
    constants.c / np.array([mid_freq]),
)
Pw = (
    np.identity(A.shape[0])
    - w
    @ np.linalg.inv(w.conj().T @ w + lambda_ridge * np.identity(w.shape[1]))
    @ w.conj().T
)
PwA = Pw @ A
new_proj = (
    np.identity(PwA.shape[0])
    - PwA
    @ np.linalg.inv(PwA.conj().T @ PwA + lambda_ridge * np.identity(PwA.shape[1]))
    @ PwA.conj().T
)


def plot_spectrum(signals, labels, fs, f_carrier, true_signal):
    fig, axes = plt.subplots(2, len(labels), figsize=(20, 10))

    true_fft_vals = np.fft.fftshift(np.fft.fft(true_signal))
    true_power_spectrum = np.abs(true_fft_vals) ** 2
    true_power_db = 10 * np.log10(
        true_power_spectrum + 1e-12
    )  # Adding small number to avoid log(0)
    true_power_db -= true_power_db.max()

    for i, (signal, label) in enumerate(zip(signals, labels)):
        # FFT along time axis
        fft_vals = np.fft.fftshift(np.fft.fft(signal))
        fft_freq = np.fft.fftshift(np.fft.fftfreq(len(signal), d=1 / fs))
        power_spectrum = np.abs(fft_vals) ** 2
        power_db = 10 * np.log10(
            power_spectrum + 1e-12
        )  # Adding small number to avoid log(0)
        power_db -= np.max(power_db)
        axes[0, i].plot(fft_freq, power_db, label=label)
        axes[0, i].set_xlabel("Frequency (Hz)")
        axes[0, i].set_ylabel("Power (dB)")
        axes[0, i].set_title(f"Power Spectrum {label}")
        axes[0, i].grid(True)
        # axes[0, i].axvline(
        #    f_carrier,
        #    color="red",
        #    linestyle="--",
        #    label=f"Carrier: {f_carrier / 1e3:.1f} kHz",
        # )

        axes[1, i].plot(fft_freq, power_db - true_power_db, label=label)
        axes[1, i].grid(True)
        axes[1, i].set_title(f"Diff from true power spectrum {label}")
        axes[1, i].legend()

    plt.tight_layout()
    plt.legend()

    # Print some diagnostics
    print(f"Sampling frequency: {fs:.1f} Hz")
    print(f"Frequency resolution: {fs / len(signal):.3f} Hz")
    print(f"Nyquist frequency: {fs / 2:.1f} Hz")
    print(f"Carrier frequency: {f_carrier / 1e3:.1f} kHz")
    print(f"Beamformed signal shape: {signal.shape}")
    print(f"Signal power: {np.mean(np.abs(signal) ** 2):.2e}")

    return fig


fig = plot_spectrum(
    [
        ((w.conj().T) @ (X))[0].flatten(),
        ((w.conj().T) @ (orth_proj @ X))[0].flatten(),
        ((w.conj().T) @ (oblique_proj @ X))[0].flatten(),
    ],
    ["w/ int", "orth", "oblique"],
    fs,
    (source_f_low + 0.5 * (source_f_high - source_f_low)),
    ((w.conj().T) @ (X_true))[0].flatten(),
)
st.header("Frequency plots...")
st.pyplot(fig)

st.header("Known Direction plots...")


A_known = np.hstack(
    [
        array.steering_vector(
            np.deg2rad(direction),
            np.array([constants.c / (freq_low + 0.5 * (freq_high - freq_low))]),
        )
        for direction, freq_high, freq_low in zip(
            interferer_theta_signal_deg, interferer_f_high, interferer_f_low
        )
    ],
)

proj_known = (
    np.identity(num_antenna)
    - A_known @ np.linalg.pinv(A_known.conj().T @ A_known) @ A_known.conj().T
)

fig = plot_spectrum(
    [
        ((w.conj().T) @ (proj_known @ X))[0].flatten(),
        ((w.conj().T) @ (X))[0].flatten(),
    ],
    ["known", "w/ int"],
    len(t) / t[-1],
    source_f_low + 0.5 * (source_f_high - source_f_low),
    ((w.conj().T) @ (X_true))[0].flatten(),
)
st.pyplot(fig)

st.header("DoA Plots...")

theta_scan = np.linspace(-1 * np.pi, np.pi, 1000)
results = []
for theta_i in theta_scan:
    w = array.steering_vector(theta_i, np.array([constants.c / mid_freq]))
    X_weighted = w.conj().T @ X
    results.append(10 * np.log10(np.var(X_weighted)))
results -= np.max(results)

fig, ax = plt.subplots(1, 1)
ax.plot(theta_scan * 180 / np.pi, results)  # lets plot angle in degrees
ax.set_xlabel("Theta [Degrees]")
ax.set_ylabel("DOA Metric")
ax.grid()
for int_theta in interferer_theta_signal_deg:
    ax.axvline(int_theta, color="red", linestyle="--", linewidth=0.9, alpha=0.5)
ax.axvline(
    source_theta_signal_deg,
    color="black",
    linestyle="--",
    linewidth=0.9,
    alpha=1,
)
st.pyplot(fig)


fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
ax.plot(theta_scan, results)  # MAKE SURE TO USE RADIAN FOR POLAR
ax.set_theta_zero_location("N")  # make 0 degrees point up
ax.set_theta_direction(-1)  # increase clockwise
ax.set_rlabel_position(55)  # Move grid labels away from other labels
st.pyplot(fig)

st.header("Beam Pattern")
N_fft = 512
theta_degrees = source_theta_signal_deg
theta = np.deg2rad(theta_degrees)

projectors = {
    "identity": np.identity(num_antenna),
    "orthogonal": orth_proj,
    "oblique": oblique_proj,
}

w = array.steering_vector(theta, constants.c / mid_freq)
fig, ax = plt.subplots(
    len(projectors), 2, figsize=(20, 17), subplot_kw={"projection": "polar"}
)

theta_bins = np.linspace(-np.pi, np.pi, 2_000)
for i, (label, proj) in enumerate(projectors.items()):
    response = [
        np.abs(w.conj().T @ proj @ array.steering_vector(theta, constants.c / mid_freq))
        ** 2
        for theta in theta_bins
    ]
    response_dB = 10 * np.log10(response)
    response_dB -= np.max(response_dB)
    # find max so we can add it to plot
    theta_max = theta_bins[np.argmax(response_dB)]

    ax[i, 0].plot(theta_bins, response_dB)  # MAKE SURE TO USE RADIAN FOR POLAR
    ax[i, 0].plot([theta_max], [np.max(response_dB)], "ro")
    ax[i, 0].text(
        theta_max - 0.1, np.max(response_dB) - 4, np.round(theta_max * 180 / np.pi)
    )
    ax[i, 0].set_theta_zero_location("N")  # make 0 degrees point up
    ax[i, 0].set_theta_direction(-1)  # increase clockwise
    ax[i, 0].set_rlabel_position(55)  # Move grid labels away from other labels
    ax[i, 0].set_thetamin(-90)  # only show top half
    ax[i, 0].set_thetamax(90)
    ax[i, 0].set_ylim([-30, 1])  # because there's no noise, only go down 30 dB
    ax[i, 0].set_title(label)

    ax[i, 1].remove()
    ax[i, 1] = fig.add_subplot(
        len(projectors),
        2,
        2 * i + 2,
    )
    ax[i, 1].plot([np.rad2deg(theta_i) for theta_i in theta_bins], response_dB)
    for int_theta in interferer_theta_signal_deg:
        ax[i, 1].axvline(
            int_theta, color="red", linestyle="--", linewidth=0.9, alpha=0.5
        )
    ax[i, 1].axvline(
        source_theta_signal_deg,
        color="black",
        linestyle="--",
        linewidth=0.9,
        alpha=1,
    )
plt.tight_layout()
st.pyplot(fig)

st.header("Beam Statistics")

data = []

data.append(
    {
        "Title": "HPBW (rad)",
        "Val": 0.9
        / (num_antenna * antenna_spacing * np.cos(np.deg2rad(source_theta_signal_deg))),
    }
)
data.append({"Title": "FNBW (rad)", "Val": 2 / (num_antenna * antenna_spacing)})
data = pd.DataFrame(data)

st.table(data)


st.header("Eigenvalue analysis")

fig, ax = plt.subplots(1, 1)
ax.plot(evals)

st.text(f"Last {num_interferers + 1} eigenvalues...")
st.text(evals[-(num_interferers + 1) :])


theta_degrees = source_theta_signal_deg
theta = np.deg2rad(theta_degrees)

w = array.steering_vector(
    theta, constants.c / (source_f_low + 0.5 * (source_f_high - source_f_low))
)
int1_steer = array.steering_vector(
    np.deg2rad(interferer_theta_signal_deg[0]),
    constants.c
    / (interferer_f_low[0] + 0.5 * (interferer_f_high[0] - interferer_f_low[0])),
)

relevant_evals = evals[-(num_interferers + 10) :]
relevant_evecs = evecs[:, -(num_interferers + 10) :]
direction_correlations = pd.DataFrame(
    [
        {
            "Evec": i,
            "eval": relevant_evals[i],
            "dot_prod_w_steering": np.abs(np.dot(w.conj(), relevant_evecs[:, i]))
            / (np.linalg.norm(w.conj())),
            "dot_prod_w_int_1": np.abs(np.dot(int1_steer.conj(), relevant_evecs[:, i]))
            / (np.linalg.norm(int1_steer.conj())),
        }
        for i in range(num_interferers + 10)
    ]
)
st.table(direction_correlations)
st.pyplot(fig)


st.header("Interference / Signal Correlations")

int_signal_correlations = pd.DataFrame(
    [
        {
            "Interferer": i,
            "Corr to Signal": np.abs(
                np.dot(
                    w.conj(),
                    array.steering_vector(
                        np.deg2rad(direction_deg),
                        constants.c
                        / (
                            interferer_f_low[i]
                            + 0.5 * (interferer_f_high[i] - interferer_f_low[i])
                        ),
                    ),
                )
            )
            / (
                np.linalg.norm(w.conj())
                * np.linalg.norm(
                    array.steering_vector(
                        np.deg2rad(direction_deg),
                        constants.c
                        / (
                            interferer_f_low[i]
                            + 0.5 * (interferer_f_high[i] - interferer_f_low[i])
                        ),
                    )
                )
            ),
        }
        for i, direction_deg in enumerate(interferer_theta_signal_deg)
    ]
)
st.table(int_signal_correlations)
