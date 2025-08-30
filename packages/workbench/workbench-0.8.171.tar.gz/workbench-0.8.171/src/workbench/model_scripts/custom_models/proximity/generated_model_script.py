# Model: feature_space_proximity
#
# Description: The feature_space_proximity model computes nearest neighbors for the given feature space
#

# Template Placeholders
TEMPLATE_PARAMS = {
    "id_column": "udm_mol_bat_id",
    "features": ['bcut2d_logplow', 'numradicalelectrons', 'smr_vsa5', 'fr_lactam', 'fr_morpholine', 'fr_aldehyde', 'slogp_vsa1', 'fr_amidine', 'bpol', 'fr_ester', 'fr_azo', 'kappa3', 'peoe_vsa5', 'fr_ketone_topliss', 'vsa_estate9', 'estate_vsa9', 'bcut2d_mrhi', 'fr_ndealkylation1', 'numrotatablebonds', 'minestateindex', 'fr_quatn', 'peoe_vsa3', 'fr_epoxide', 'fr_aniline', 'minpartialcharge', 'fr_nitroso', 'fpdensitymorgan2', 'fr_oxime', 'fr_sulfone', 'smr_vsa1', 'kappa1', 'fr_pyridine', 'numaromaticrings', 'vsa_estate6', 'molmr', 'estate_vsa1', 'fr_dihydropyridine', 'vsa_estate10', 'fr_alkyl_halide', 'chi2n', 'fr_thiocyan', 'fpdensitymorgan1', 'fr_unbrch_alkane', 'slogp_vsa9', 'chi4n', 'fr_nitro_arom', 'fr_al_oh', 'fr_furan', 'fr_c_s', 'peoe_vsa8', 'peoe_vsa14', 'numheteroatoms', 'fr_ndealkylation2', 'maxabspartialcharge', 'vsa_estate2', 'peoe_vsa7', 'apol', 'numhacceptors', 'fr_tetrazole', 'vsa_estate1', 'peoe_vsa9', 'naromatom', 'bcut2d_chghi', 'fr_sh', 'fr_halogen', 'slogp_vsa4', 'fr_benzodiazepine', 'molwt', 'fr_isocyan', 'fr_prisulfonamd', 'maxabsestateindex', 'minabsestateindex', 'peoe_vsa11', 'slogp_vsa12', 'estate_vsa5', 'numaliphaticcarbocycles', 'bcut2d_mwlow', 'slogp_vsa7', 'fr_allylic_oxid', 'fr_methoxy', 'fr_nh0', 'fr_coo2', 'fr_phenol', 'nacid', 'nbase', 'chi3v', 'fr_ar_nh', 'fr_nitrile', 'fr_imidazole', 'fr_urea', 'bcut2d_mrlow', 'chi1', 'smr_vsa6', 'fr_aryl_methyl', 'narombond', 'fr_alkyl_carbamate', 'fr_piperzine', 'exactmolwt', 'qed', 'chi0n', 'fr_sulfonamd', 'fr_thiazole', 'numvalenceelectrons', 'fr_phos_acid', 'peoe_vsa12', 'fr_nh1', 'fr_hdrzine', 'fr_c_o_nocoo', 'fr_lactone', 'estate_vsa6', 'bcut2d_logphi', 'vsa_estate7', 'peoe_vsa13', 'numsaturatedcarbocycles', 'fr_nitro', 'fr_phenol_noorthohbond', 'rotratio', 'fr_barbitur', 'fr_isothiocyan', 'balabanj', 'fr_arn', 'fr_imine', 'maxpartialcharge', 'fr_sulfide', 'slogp_vsa11', 'fr_hoccn', 'fr_n_o', 'peoe_vsa1', 'slogp_vsa6', 'heavyatommolwt', 'fractioncsp3', 'estate_vsa8', 'peoe_vsa10', 'numaliphaticrings', 'fr_thiophene', 'maxestateindex', 'smr_vsa10', 'labuteasa', 'smr_vsa2', 'fpdensitymorgan3', 'smr_vsa9', 'slogp_vsa10', 'numaromaticheterocycles', 'fr_nh2', 'fr_diazo', 'chi3n', 'fr_ar_coo', 'slogp_vsa5', 'fr_bicyclic', 'fr_amide', 'estate_vsa10', 'fr_guanido', 'chi1n', 'numsaturatedrings', 'fr_piperdine', 'fr_term_acetylene', 'estate_vsa4', 'slogp_vsa3', 'fr_coo', 'fr_ether', 'estate_vsa7', 'bcut2d_chglo', 'fr_oxazole', 'peoe_vsa6', 'hallkieralpha', 'peoe_vsa2', 'chi2v', 'nocount', 'vsa_estate5', 'fr_nhpyrrole', 'fr_al_coo', 'bertzct', 'estate_vsa11', 'minabspartialcharge', 'slogp_vsa8', 'fr_imide', 'kappa2', 'numaliphaticheterocycles', 'numsaturatedheterocycles', 'fr_hdrzone', 'smr_vsa4', 'fr_ar_n', 'nrot', 'smr_vsa8', 'slogp_vsa2', 'chi4v', 'fr_phos_ester', 'fr_para_hydroxylation', 'smr_vsa3', 'nhohcount', 'estate_vsa2', 'mollogp', 'tpsa', 'fr_azide', 'peoe_vsa4', 'numhdonors', 'fr_al_oh_notert', 'fr_c_o', 'chi0', 'fr_nitro_arom_nonortho', 'vsa_estate3', 'fr_benzene', 'fr_ketone', 'vsa_estate8', 'smr_vsa7', 'fr_ar_oh', 'fr_priamide', 'ringcount', 'estate_vsa3', 'numaromaticcarbocycles', 'bcut2d_mwhi', 'chi1v', 'heavyatomcount', 'vsa_estate4', 'chi0v'],
    "target": "udm_asy_res_value",
    "track_columns": None
}

from io import StringIO
import json
import argparse
import os
import pandas as pd

# Local Imports
from proximity import Proximity


# Function to check if dataframe is empty
def check_dataframe(df: pd.DataFrame, df_name: str) -> None:
    """Check if the DataFrame is empty and raise an error if so."""
    if df.empty:
        msg = f"*** The training data {df_name} has 0 rows! ***STOPPING***"
        print(msg)
        raise ValueError(msg)


# Function to match DataFrame columns to model features (case-insensitive)
def match_features_case_insensitive(df: pd.DataFrame, model_features: list) -> pd.DataFrame:
    """Match and rename DataFrame columns to match the model's features, case-insensitively."""
    # Create a set of exact matches from the DataFrame columns
    exact_match_set = set(df.columns)

    # Create a case-insensitive map of DataFrame columns
    column_map = {col.lower(): col for col in df.columns}
    rename_dict = {}

    # Build a dictionary for renaming columns based on case-insensitive matching
    for feature in model_features:
        if feature in exact_match_set:
            rename_dict[feature] = feature
        elif feature.lower() in column_map:
            rename_dict[column_map[feature.lower()]] = feature

    # Rename columns in the DataFrame to match model features
    return df.rename(columns=rename_dict)


# TRAINING SECTION
#
# This section (__main__) is where SageMaker will execute the training job
# and save the model artifacts to the model directory.
#
if __name__ == "__main__":
    # Template Parameters
    id_column = TEMPLATE_PARAMS["id_column"]
    features = TEMPLATE_PARAMS["features"]
    target = TEMPLATE_PARAMS["target"]  # Can be None for unsupervised models
    track_columns = TEMPLATE_PARAMS["track_columns"]  # Can be None

    # Script arguments for input/output directories
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train"))
    parser.add_argument(
        "--output-data-dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/output/data")
    )
    args = parser.parse_args()

    # Load training data from the specified directory
    training_files = [
        os.path.join(args.train, file)
        for file in os.listdir(args.train) if file.endswith(".csv")
    ]
    all_df = pd.concat([pd.read_csv(file, engine="python") for file in training_files])

    # Check if the DataFrame is empty
    check_dataframe(all_df, "training_df")

    # Create the Proximity model
    model = Proximity(all_df, id_column, features, target, track_columns=track_columns)

    # Now serialize the model
    model.serialize(args.model_dir)

# Model loading and prediction functions
def model_fn(model_dir):

    # Deserialize the model
    model = Proximity.deserialize(model_dir)
    return model


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
    use_explicit_na = False
    if "text/csv" in accept_type:
        if use_explicit_na:
            csv_output = output_df.fillna("N/A").to_csv(index=False)  # CSV with N/A for missing values
        else:
            csv_output = output_df.to_csv(index=False)
        return csv_output, "text/csv"
    elif "application/json" in accept_type:
        return output_df.to_json(orient="records"), "application/json"  # JSON array of records (NaNs -> null)
    else:
        raise RuntimeError(f"{accept_type} accept type is not supported by this script.")


# Prediction function
def predict_fn(df, model):
    # Match column names before prediction if needed
    df = match_features_case_insensitive(df, model.features + [model.id_column])

    # Compute Nearest neighbors
    df = model.neighbors(df)
    return df
