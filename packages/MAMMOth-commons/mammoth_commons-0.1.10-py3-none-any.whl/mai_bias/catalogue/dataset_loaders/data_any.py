from mammoth_commons.datasets import CSV
from mammoth_commons.integration import loader, Options
import pandas as pd


def data_local(raw_data: pd.DataFrame, target: str = None) -> CSV:
    numeric = [
        col
        for col in raw_data
        if pd.api.types.is_any_real_numeric_dtype(raw_data[col])
        and len(set(raw_data[col])) > 10
    ]
    numeric_set = set(numeric)
    categorical = [col for col in raw_data if col not in numeric_set]
    if len(categorical) < 1:
        raise Exception("At least one categorical column is required.")
    if target is None:
        if "class" in categorical:
            target = "class"
        elif "Class" in categorical:
            target = "Class"
        elif "Y" in categorical:
            target = "Y"
        elif "y" in categorical:
            target = "y"
        else:
            target = categorical[-1]
    if target in categorical:
        categorical.remove(target)
    elif target in numeric:
        numeric.remove(target)
    label = raw_data[target].copy()
    raw_data = raw_data.drop(columns=[target])
    return CSV(raw_data, num=numeric, cat=categorical, labels=label)


@loader(
    namespace="mammotheu",
    version="v0048",
    python="3.13",
    packages=("pandas",),
)
def data_read_any(
    dataset_path: str = None,
    target: str = None,
) -> CSV:
    """
    <img src="https://raw.githubusercontent.com/arjunroyihrpa/MMM_fair/main/images/mmm-fair.png" alt="Based on MMM-Fair" style="float: left; margin-right: 5px; margin-bottom: 5px; height: 80px;"/>

    Loads a dataset for analysis from either a pre-loaded pandas DataFrame or a file in one of the supported formats:
    `.csv`, `.xls`, `.xlsx`, `.xlsm`, `.xlsb`, `.odf`, `.ods`, `.json`, `.html`, or `.htm`.
    The module accepts either a raw DataFrame or a file path (local or URL). If a file path is provided, the data is
    automatically loaded using the appropriate pandas function based on the file extension. Basic preprocessing is applied
    to infer column types, and the specified target column is treated as the predictive label.

    To customize the loading process (e.g., load a subset of columns, handle missing values, or change column type inference),
    additional parameters or a custom loader function may be provided.
    The Data loader module is recommended to load and process local data also while training models which are intended to be tested
    using the ONNXEnsemble module.

    Args:
        dataset_path: Path or URL to the dataset file. Must have one of the supported extensions.
        target: The name of the column to treat as the predictive label.
    """
    try:
        if dataset_path.endswith(".csv"):
            df = pd.read_csv(dataset_path)
        elif dataset_path.endswith(".xls", ".xlsx", ".xlsm", ".xlsb", ".odf", ".ods"):
            df = pd.read_excel(dataset_path)
        elif dataset_path.endswith(".json"):
            df = pd.read_json(dataset_path)
        elif dataset_path.endswith(".html", ".htm"):
            df = pd.read_html(dataset_path)
        return data_local(df, target)
    except:
        raise ValueError("Could not read data. Unsupported or invalid format.")
