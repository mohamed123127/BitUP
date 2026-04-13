import kagglehub
import pandas as pd
import numpy as np
import os

# =========================
# 1. LOAD DATASET
# =========================
def download_dataset():
    path = kagglehub.dataset_download(
        "mayank1897/condition-monitoring-of-hydraulic-systems"
    )
    print("Dataset path:", path)
    return path


# =========================
# 2. LOAD SENSOR FILE
# =========================
def load_sensor(path, file):
    return pd.read_csv(os.path.join(path, file), sep="\t", header=None)


# =========================
# 3. LOAD ALL SENSORS
# =========================
def load_all_sensors(path):
    sensors = {
        "ps": [load_sensor(path, f"PS{i}.txt") for i in range(1, 7)],
        "fs": [load_sensor(path, f"FS{i}.txt") for i in range(1, 3)],
        "ts": [load_sensor(path, f"TS{i}.txt") for i in range(1, 5)],
        "vs": load_sensor(path, "VS1.txt"),
        "eps": load_sensor(path, "EPS1.txt"),
        "se": load_sensor(path, "SE.txt"),
        "ce": load_sensor(path, "CE.txt"),
        "cp": load_sensor(path, "CP.txt"),
    }
    return sensors


# =========================
# 4. LOAD LABELS
# =========================
def load_labels(path):
    profile = pd.read_csv(
        os.path.join(path, "profile.txt"),
        sep="\t",
        header=None
    )

    profile.columns = [
        "cooler_condition",
        "valve_condition",
        "pump_leak",
        "accumulator_pressure",
        "stable_flag"
    ]
    return profile


# =========================
# 5. FEATURE HELPERS
# =========================
def extract_stats(df):
    return {
        "mean": df.mean(axis=1),
        "std": df.std(axis=1),
        "max": df.max(axis=1),
        "min": df.min(axis=1),
        "range": df.max(axis=1) - df.min(axis=1)
    }


def trend(df):
    return df.iloc[:, -1] - df.iloc[:, 0]


def spikes(df):
    return df.max(axis=1) - df.mean(axis=1)


# =========================
# 6. FEATURE FUNCTIONS (EACH TYPE)
# =========================
def pressure_features(ps_list):
    ps_all = pd.concat(ps_list, axis=1)
    feat = extract_stats(ps_all)

    return pd.DataFrame({
        "ps_mean": feat["mean"],
        "ps_std": feat["std"],
        "ps_max": feat["max"],
        "ps_min": feat["min"],
        "ps_range": feat["range"],
        "ps_trend": trend(ps_all),
        "ps_instability": spikes(ps_all)
    })


def flow_features(fs_list):
    fs_all = pd.concat(fs_list, axis=1)
    feat = extract_stats(fs_all)

    return pd.DataFrame({
        "flow_mean": feat["mean"],
        "flow_std": feat["std"],
        "flow_max": feat["max"],
        "flow_min": feat["min"],
        "flow_drop": fs_all.min(axis=1),
        "flow_imbalance": feat["range"]
    })


def temperature_features(ts_list):
    ts_all = pd.concat(ts_list, axis=1)
    feat = extract_stats(ts_all)

    return pd.DataFrame({
        "temp_mean": feat["mean"],
        "temp_max": feat["max"],
        "temp_min": feat["min"],
        "temp_std": feat["std"],
        "temp_gradient": trend(ts_all)
    })


def vibration_features(vs):
    feat = extract_stats(vs)

    return pd.DataFrame({
        "vibration_mean": feat["mean"],
        "vibration_std": feat["std"],
        "vibration_max": feat["max"],
        "vibration_spikes": spikes(vs)
    })


def power_features(eps):
    feat = extract_stats(eps)

    return pd.DataFrame({
        "power_mean": feat["mean"],
        "power_std": feat["std"],
        "power_max": feat["max"]
    })


def efficiency_features(se, ce):
    se_feat = extract_stats(se)
    ce_feat = extract_stats(ce)

    return pd.DataFrame({
        "system_efficiency": se_feat["mean"],
        "cooling_efficiency": ce_feat["mean"]
    })


def global_features(ps_feat, fs_feat, ts_feat, vs_feat):
    return pd.DataFrame({
        "system_health_score": (
            ps_feat["mean"] +
            fs_feat["mean"] +
            ts_feat["mean"]
        ) / 3,

        "anomaly_indicator": (
            ps_feat["std"] +
            fs_feat["std"] +
            vs_feat["std"]
        )
    })


# =========================
# 7. MAIN PIPELINE
# =========================
def preprocess_dataset(save_path="./modules/module8/resources/hydraulic_final_dataset.csv"):
    # Load
    path = download_dataset()
    sensors = load_all_sensors(path)
    labels = load_labels(path)

    # Features
    ps_df = pressure_features(sensors["ps"])
    fs_df = flow_features(sensors["fs"])
    ts_df = temperature_features(sensors["ts"])
    vs_df = vibration_features(sensors["vs"])
    power_df = power_features(sensors["eps"])
    eff_df = efficiency_features(sensors["se"], sensors["ce"])

    # reuse stats for global features
    ps_feat = extract_stats(pd.concat(sensors["ps"], axis=1))
    fs_feat = extract_stats(pd.concat(sensors["fs"], axis=1))
    ts_feat = extract_stats(pd.concat(sensors["ts"], axis=1))
    vs_feat = extract_stats(sensors["vs"])

    global_df = global_features(ps_feat, fs_feat, ts_feat, vs_feat)

    # Merge
    X = pd.concat([
        ps_df,
        fs_df,
        ts_df,
        vs_df,
        power_df,
        eff_df,
        global_df
    ], axis=1)

    final_dataset = pd.concat([X, labels], axis=1)

    print("Final dataset shape:", final_dataset.shape)
    print(final_dataset.head())

    # Save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    final_dataset.to_csv(save_path, index=False)

    print("Dataset saved successfully at:", save_path)

    return final_dataset

