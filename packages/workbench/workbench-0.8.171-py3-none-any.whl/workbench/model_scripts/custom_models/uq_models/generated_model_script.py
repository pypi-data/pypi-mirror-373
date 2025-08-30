# Model: NGBoost Regressor with Distribution output
from ngboost import NGBRegressor
from xgboost import XGBRegressor  # Base Estimator
from sklearn.model_selection import train_test_split

# Model Performance Scores
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error
)

from io import StringIO
import json
import argparse
import joblib
import os
import numpy as np
import pandas as pd
from typing import List, Tuple

# Local Imports
from proximity import Proximity



# Template Placeholders
TEMPLATE_PARAMS = {
    "id_column": "udm_mol_bat_id",
    "target": "udm_asy_res_intrinsic_clearance_ul_per_min_per_mg_protein",
    "features": ['bcut2d_logplow', 'numradicalelectrons', 'smr_vsa5', 'fr_lactam', 'fr_morpholine', 'fr_aldehyde', 'slogp_vsa1', 'fr_amidine', 'bpol', 'fr_ester', 'fr_azo', 'kappa3', 'peoe_vsa5', 'fr_ketone_topliss', 'vsa_estate9', 'estate_vsa9', 'bcut2d_mrhi', 'fr_ndealkylation1', 'numrotatablebonds', 'minestateindex', 'fr_quatn', 'peoe_vsa3', 'fr_epoxide', 'fr_aniline', 'minpartialcharge', 'fr_nitroso', 'fpdensitymorgan2', 'fr_oxime', 'fr_sulfone', 'smr_vsa1', 'kappa1', 'fr_pyridine', 'numaromaticrings', 'vsa_estate6', 'molmr', 'estate_vsa1', 'fr_dihydropyridine', 'vsa_estate10', 'fr_alkyl_halide', 'chi2n', 'fr_thiocyan', 'fpdensitymorgan1', 'fr_unbrch_alkane', 'slogp_vsa9', 'chi4n', 'fr_nitro_arom', 'fr_al_oh', 'fr_furan', 'fr_c_s', 'peoe_vsa8', 'peoe_vsa14', 'numheteroatoms', 'fr_ndealkylation2', 'maxabspartialcharge', 'vsa_estate2', 'peoe_vsa7', 'apol', 'numhacceptors', 'fr_tetrazole', 'vsa_estate1', 'peoe_vsa9', 'naromatom', 'bcut2d_chghi', 'fr_sh', 'fr_halogen', 'slogp_vsa4', 'fr_benzodiazepine', 'molwt', 'fr_isocyan', 'fr_prisulfonamd', 'maxabsestateindex', 'minabsestateindex', 'peoe_vsa11', 'slogp_vsa12', 'estate_vsa5', 'numaliphaticcarbocycles', 'bcut2d_mwlow', 'slogp_vsa7', 'fr_allylic_oxid', 'fr_methoxy', 'fr_nh0', 'fr_coo2', 'fr_phenol', 'nacid', 'nbase', 'chi3v', 'fr_ar_nh', 'fr_nitrile', 'fr_imidazole', 'fr_urea', 'bcut2d_mrlow', 'chi1', 'smr_vsa6', 'fr_aryl_methyl', 'narombond', 'fr_alkyl_carbamate', 'fr_piperzine', 'exactmolwt', 'qed', 'chi0n', 'fr_sulfonamd', 'fr_thiazole', 'numvalenceelectrons', 'fr_phos_acid', 'peoe_vsa12', 'fr_nh1', 'fr_hdrzine', 'fr_c_o_nocoo', 'fr_lactone', 'estate_vsa6', 'bcut2d_logphi', 'vsa_estate7', 'peoe_vsa13', 'numsaturatedcarbocycles', 'fr_nitro', 'fr_phenol_noorthohbond', 'rotratio', 'fr_barbitur', 'fr_isothiocyan', 'balabanj', 'fr_arn', 'fr_imine', 'maxpartialcharge', 'fr_sulfide', 'slogp_vsa11', 'fr_hoccn', 'fr_n_o', 'peoe_vsa1', 'slogp_vsa6', 'heavyatommolwt', 'fractioncsp3', 'estate_vsa8', 'peoe_vsa10', 'numaliphaticrings', 'fr_thiophene', 'maxestateindex', 'smr_vsa10', 'labuteasa', 'smr_vsa2', 'fpdensitymorgan3', 'smr_vsa9', 'slogp_vsa10', 'numaromaticheterocycles', 'fr_nh2', 'fr_diazo', 'chi3n', 'fr_ar_coo', 'slogp_vsa5', 'fr_bicyclic', 'fr_amide', 'estate_vsa10', 'fr_guanido', 'chi1n', 'numsaturatedrings', 'fr_piperdine', 'fr_term_acetylene', 'estate_vsa4', 'slogp_vsa3', 'fr_coo', 'fr_ether', 'estate_vsa7', 'bcut2d_chglo', 'fr_oxazole', 'peoe_vsa6', 'hallkieralpha', 'peoe_vsa2', 'chi2v', 'nocount', 'vsa_estate5', 'fr_nhpyrrole', 'fr_al_coo', 'bertzct', 'estate_vsa11', 'minabspartialcharge', 'slogp_vsa8', 'fr_imide', 'kappa2', 'numaliphaticheterocycles', 'numsaturatedheterocycles', 'fr_hdrzone', 'smr_vsa4', 'fr_ar_n', 'nrot', 'smr_vsa8', 'slogp_vsa2', 'chi4v', 'fr_phos_ester', 'fr_para_hydroxylation', 'smr_vsa3', 'nhohcount', 'estate_vsa2', 'mollogp', 'tpsa', 'fr_azide', 'peoe_vsa4', 'numhdonors', 'fr_al_oh_notert', 'fr_c_o', 'chi0', 'fr_nitro_arom_nonortho', 'vsa_estate3', 'fr_benzene', 'fr_ketone', 'vsa_estate8', 'smr_vsa7', 'fr_ar_oh', 'fr_priamide', 'ringcount', 'estate_vsa3', 'numaromaticcarbocycles', 'bcut2d_mwhi', 'chi1v', 'heavyatomcount', 'vsa_estate4', 'chi0v'],
    "compressed_features": [],
    "train_all_data": False,
    "track_columns": ['udm_asy_res_intrinsic_clearance_ul_per_min_per_mg_protein']
}


# Function to check if dataframe is empty
def check_dataframe(df: pd.DataFrame, df_name: str) -> None:
    """
    Check if the provided dataframe is empty and raise an exception if it is.

    Args:
        df (pd.DataFrame): DataFrame to check
        df_name (str): Name of the DataFrame
    """
    if df.empty:
        msg = f"*** The training data {df_name} has 0 rows! ***STOPPING***"
        print(msg)
        raise ValueError(msg)


def match_features_case_insensitive(df: pd.DataFrame, model_features: list) -> pd.DataFrame:
    """
    Matches and renames DataFrame columns to match model feature names (case-insensitive).
    Prioritizes exact matches, then case-insensitive matches.

    Raises ValueError if any model features cannot be matched.
    """
    df_columns_lower = {col.lower(): col for col in df.columns}
    rename_dict = {}
    missing = []
    for feature in model_features:
        if feature in df.columns:
            continue  # Exact match
        elif feature.lower() in df_columns_lower:
            rename_dict[df_columns_lower[feature.lower()]] = feature
        else:
            missing.append(feature)

    if missing:
        raise ValueError(f"Features not found: {missing}")

    # Rename the DataFrame columns to match the model features
    return df.rename(columns=rename_dict)


def convert_categorical_types(df: pd.DataFrame, features: list, category_mappings={}) -> tuple:
    """
    Converts appropriate columns to categorical type with consistent mappings.

    Args:
        df (pd.DataFrame): The DataFrame to process.
        features (list): List of feature names to consider for conversion.
        category_mappings (dict, optional): Existing category mappings. If empty dict, we're in
                                            training mode. If populated, we're in inference mode.

    Returns:
        tuple: (processed DataFrame, category mappings dictionary)
    """
    # Training mode
    if category_mappings == {}:
        for col in df.select_dtypes(include=["object", "string"]):
            if col in features and df[col].nunique() < 20:
                print(f"Training mode: Converting {col} to category")
                df[col] = df[col].astype("category")
                category_mappings[col] = df[col].cat.categories.tolist()  # Store category mappings

    # Inference mode
    else:
        for col, categories in category_mappings.items():
            if col in df.columns:
                print(f"Inference mode: Applying categorical mapping for {col}")
                df[col] = pd.Categorical(df[col], categories=categories)  # Apply consistent categorical mapping

    return df, category_mappings


def decompress_features(df: pd.DataFrame, features: List[str], compressed_features: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """Prepare features for the XGBoost model

    Args:
        df (pd.DataFrame): The features DataFrame
        features (List[str]): Full list of feature names
        compressed_features (List[str]): List of feature names to decompress (bitstrings)

    Returns:
        pd.DataFrame: DataFrame with the decompressed features
        List[str]: Updated list of feature names after decompression

    Raises:
        ValueError: If any missing values are found in the specified features
    """

    # Check for any missing values in the required features
    missing_counts = df[features].isna().sum()
    if missing_counts.any():
        missing_features = missing_counts[missing_counts > 0]
        print(
            f"WARNING: Found missing values in features: {missing_features.to_dict()}. "
            "WARNING: You might want to remove/replace all NaN values before processing."
        )

    # Decompress the specified compressed features
    decompressed_features = features
    for feature in compressed_features:
        if (feature not in df.columns) or (feature not in features):
            print(f"Feature '{feature}' not in the features list, skipping decompression.")
            continue

        # Remove the feature from the list of features to avoid duplication
        decompressed_features.remove(feature)

        # Handle all compressed features as bitstrings
        bit_matrix = np.array([list(bitstring) for bitstring in df[feature]], dtype=np.uint8)
        prefix = feature[:3]

        # Create all new columns at once - avoids fragmentation
        new_col_names = [f"{prefix}_{i}" for i in range(bit_matrix.shape[1])]
        new_df = pd.DataFrame(bit_matrix, columns=new_col_names, index=df.index)

        # Add to features list
        decompressed_features.extend(new_col_names)

        # Drop original column and concatenate new ones
        df = df.drop(columns=[feature])
        df = pd.concat([df, new_df], axis=1)

    return df, decompressed_features


if __name__ == "__main__":
    # Template Parameters
    id_column = TEMPLATE_PARAMS["id_column"]
    target = TEMPLATE_PARAMS["target"]
    features = TEMPLATE_PARAMS["features"]
    orig_features = features.copy()
    compressed_features = TEMPLATE_PARAMS["compressed_features"]
    train_all_data = TEMPLATE_PARAMS["train_all_data"]
    track_columns = TEMPLATE_PARAMS["track_columns"]  # Can be None
    validation_split = 0.2

    # Script arguments for input/output directories
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train"))
    parser.add_argument(
        "--output-data-dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/output/data")
    )
    args = parser.parse_args()

    # Read the training data into DataFrames
    training_files = [
        os.path.join(args.train, file)
        for file in os.listdir(args.train)
        if file.endswith(".csv")
    ]
    print(f"Training Files: {training_files}")

    # Combine files and read them all into a single pandas dataframe
    all_df = pd.concat([pd.read_csv(file, engine="python") for file in training_files])

    # Check if the dataframe is empty
    check_dataframe(all_df, "training_df")

    # Features/Target output
    print(f"Target: {target}")
    print(f"Features: {str(features)}")

    # Convert any features that might be categorical to 'category' type
    all_df, category_mappings = convert_categorical_types(all_df, features)

    # If we have compressed features, decompress them
    if compressed_features:
        print(f"Decompressing features {compressed_features}...")
        all_df, features = decompress_features(all_df, features, compressed_features)

    # Do we want to train on all the data?
    if train_all_data:
        print("Training on ALL of the data")
        df_train = all_df.copy()
        df_val = all_df.copy()

    # Does the dataframe have a training column?
    elif "training" in all_df.columns:
        print("Found training column, splitting data based on training column")
        df_train = all_df[all_df["training"]]
        df_val = all_df[~all_df["training"]]
    else:
        # Just do a random training Split
        print("WARNING: No training column found, splitting data with random state=42")
        df_train, df_val = train_test_split(
            all_df, test_size=validation_split, random_state=42
        )
    print(f"FIT/TRAIN: {df_train.shape}")
    print(f"VALIDATION: {df_val.shape}")

    # We're using XGBoost for point predictions and NGBoost for uncertainty quantification
    xgb_model = XGBRegressor()
    ngb_model = NGBRegressor()

    # Prepare features and targets for training
    X_train = df_train[features]
    X_validate = df_val[features]
    y_train = df_train[target]
    y_validate = df_val[target]

    # Train both models using the training data
    xgb_model.fit(X_train, y_train)
    ngb_model.fit(X_train, y_train, X_val=X_validate, Y_val=y_validate)

    # Make Predictions on the Validation Set
    print(f"Making Predictions on Validation Set...")
    preds = xgb_model.predict(X_validate)

    # Calculate various model performance metrics (regression)
    rmse = root_mean_squared_error(y_validate, preds)
    mae = mean_absolute_error(y_validate, preds)
    r2 = r2_score(y_validate, preds)
    print(f"RMSE: {rmse:.3f}")
    print(f"MAE: {mae:.3f}")
    print(f"R2: {r2:.3f}")
    print(f"NumRows: {len(df_val)}")

    # Save the trained XGBoost model
    xgb_model.save_model(os.path.join(args.model_dir, "xgb_model.json"))

    # Save the trained NGBoost model
    joblib.dump(ngb_model, os.path.join(args.model_dir, "ngb_model.joblib"))

    # Save the features (this will validate input during predictions)
    with open(os.path.join(args.model_dir, "feature_columns.json"), "w") as fp:
        json.dump(orig_features, fp)  # We save the original features, not the decompressed ones

    # Now the Proximity model
    model = Proximity(df_train, id_column, features, target, track_columns=track_columns)

    # Now serialize the model
    model.serialize(args.model_dir)


#
# Inference Section
#
def model_fn(model_dir) -> dict:
    """Load and return XGBoost, NGBoost, and Prox Model from model directory."""

    # Load XGBoost regressor
    xgb_path = os.path.join(model_dir, "xgb_model.json")
    xgb_model = XGBRegressor(enable_categorical=True)
    xgb_model.load_model(xgb_path)

    # Load NGBoost regressor
    ngb_model = joblib.load(os.path.join(model_dir, "ngb_model.joblib"))

    # Deserialize the proximity model
    prox_model = Proximity.deserialize(model_dir)

    return {
        "xgboost": xgb_model,
        "ngboost": ngb_model,
        "proximity": prox_model
    }


def input_fn(input_data, content_type):
    """Parse input data and return a DataFrame."""
    if not input_data:
        raise ValueError("Empty input data is not supported!")

    # Decode bytes to string if necessary
    if isinstance(input_data, bytes):
        input_data = input_data.decode("utf-8")

    if "text/csv" in content_type:
        return pd.read_csv(StringIO(input_data))
    elif "application/json" in content_type:
        return pd.DataFrame(json.loads(input_data))  # Assumes JSON array of records
    else:
        raise ValueError(f"{content_type} not supported!")


def output_fn(output_df, accept_type):
    """Supports both CSV and JSON output formats."""
    if "text/csv" in accept_type:
        csv_output = output_df.fillna("N/A").to_csv(index=False)  # CSV with N/A for missing values
        return csv_output, "text/csv"
    elif "application/json" in accept_type:
        return output_df.to_json(orient="records"), "application/json"  # JSON array of records (NaNs -> null)
    else:
        raise RuntimeError(f"{accept_type} accept type is not supported by this script.")


def predict_fn(df, models) -> pd.DataFrame:
    """Make Predictions with our XGB Quantile Regression Model

    Args:
        df (pd.DataFrame): The input DataFrame
        models (dict): The dictionary of models to use for predictions

    Returns:
        pd.DataFrame: The DataFrame with the predictions added
    """

    # Grab our feature columns (from training)
    model_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
    with open(os.path.join(model_dir, "feature_columns.json")) as fp:
        model_features = json.load(fp)

    # Match features in a case-insensitive manner
    matched_df = match_features_case_insensitive(df, model_features)

    # Use XGBoost for point predictions
    df["prediction"] = models["xgboost"].predict(matched_df[model_features])

    # NGBoost predict returns distribution objects
    y_dists = models["ngboost"].pred_dist(matched_df[model_features])

    # Extract parameters from distribution
    dist_params = y_dists.params

    # Extract mean and std from distribution parameters
    df["prediction_uq"] = dist_params['loc']  # mean
    df["prediction_std"] = dist_params['scale']  # standard deviation

    # Add 95% prediction intervals using ppf (percent point function)
    # Note: Our hybrid model uses XGB point prediction and NGBoost UQ
    #  so we need to adjust the bounds to include the point prediction
    df["q_025"] = np.minimum(y_dists.ppf(0.025), df["prediction"])
    df["q_975"] = np.maximum(y_dists.ppf(0.975), df["prediction"])

    # Add 90% prediction intervals
    df["q_05"] = y_dists.ppf(0.05)  # 5th percentile
    df["q_95"] = y_dists.ppf(0.95)  # 95th percentile

    # Add 80% prediction intervals
    df["q_10"] = y_dists.ppf(0.10)  # 10th percentile
    df["q_90"] = y_dists.ppf(0.90)  # 90th percentile

    # Add 50% prediction intervals
    df["q_25"] = y_dists.ppf(0.25)  # 25th percentile
    df["q_75"] = y_dists.ppf(0.75)  # 75th percentile

    # Reorder the quantile columns for easier reading
    quantile_cols = ["q_025", "q_05", "q_10", "q_25", "q_75", "q_90", "q_95", "q_975"]
    other_cols = [col for col in df.columns if col not in quantile_cols]
    df = df[other_cols + quantile_cols]

    # Compute Nearest neighbors with Proximity model
    models["proximity"].neighbors(df)

    # Return the modified DataFrame
    return df
