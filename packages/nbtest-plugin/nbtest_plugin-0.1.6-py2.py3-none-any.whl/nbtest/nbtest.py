from time import time
import os
import atexit
import unittest
import pandas as pd
import glob
import numpy as np
import pickle
import matplotlib.pyplot as plt
from matplotlib.testing.compare import compare_images

output_dir = os.environ.get('NBTEST_OUTPUT_DIR', '.')

collect_flag = False
notebook_fname = None
tracked_pairs = set()

tc = unittest.TestCase()

if os.environ.get('COLLECT_VARS') and os.environ['COLLECT_VARS'] == '1':
    collect_flag = True

def assert_equal(a, b, err_msg='', type='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        np.testing.assert_equal(a, b, err_msg=err_msg)

def assert_allclose(a, b, rtol=1e-07, atol=0, err_msg='', type='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        np.testing.assert_allclose(a, b, rtol=rtol, atol=atol, err_msg=err_msg)

def assert_true(a, err_msg=None, type='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        tc.assertTrue(a, msg=err_msg)

def assert_false(a, err_msg=None, type='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        tc.assertFalse(a, msg=err_msg)

def assert_df_var(a, b, rtol=1e-07, atol=0, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        np.testing.assert_allclose(np.nanvar(a.select_dtypes(include=['number']).to_numpy()), b, rtol=rtol, atol=atol, err_msg=err_msg)

def assert_df_mean(a, b, rtol=1e-07, atol=0, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        np.testing.assert_allclose(np.nanmean(a.select_dtypes(include=['number']).to_numpy()), b, rtol=rtol, atol=atol, err_msg=err_msg)

def assert_column_types(a, b, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        if isinstance(b, list):
            np.testing.assert_equal([str(a[i].dtype) for i in sorted(a.columns)], b, err_msg=err_msg)
        elif isinstance(b, dict):
            for col, dtype in b.items():
                np.testing.assert_equal(str(a[col].dtype), dtype, err_msg=err_msg)
        else:
            raise ValueError("Invalid type for b")

def assert_column_names(a, b, strict=False, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        if strict:
            np.testing.assert_equal(sorted(a.columns), sorted(b), err_msg=err_msg)
        else:
            tc.assertTrue(set(b).issubset(set(a.columns)))

def assert_shape(a, b, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        np.testing.assert_equal(a.shape, b, err_msg=err_msg)

def assert_sklearn_model(a, b, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        with open(b, 'rb') as f:
            b_dict = pickle.load(f)
            a_dict = {
                k: v for k, v in a.get_params().items()
                if k != 'random_state'
                and not (hasattr(v, '__module__') and v.__module__.startswith('sklearn'))
            }
            np.testing.assert_equal(a_dict, b_dict, err_msg=err_msg)

def assert_nn_model(a, b, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        layer_info_list = []

        for layer in a.layers:
            # Get the layer type (class name)
            layer_type = layer.__class__.__name__

            output_shape = layer.output_shape

            # Get the number of trainable parameters for the layer
            num_params = layer.count_params()

            # Append the information as a tuple to our list
            layer_info_list.append((layer_type, output_shape, num_params))

        np.testing.assert_equal(layer_info_list, b, err_msg=err_msg)

def assert_in(a, b, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        tc.assertIn(a, b, msg=err_msg)

def assert_df_leakage(train, test, df_id='index', validation=None, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        if df_id == 'index':
            np.testing.assert_equal(len(set(train.index).intersection(set(test.index))), 0, err_msg=err_msg)
        else:
            np.testing.assert_equal(len(set(train[df_id].unique()).intersection(set(test[df_id].unique()))), 0, err_msg=err_msg)

        if validation:
            if df_id == 'index':
                np.testing.assert_equal(len(set(train.index).intersection(set(validation.index))), 0, err_msg=err_msg)
                np.testing.assert_equal(len(set(test.index).intersection(set(validation.index))), 0, err_msg=err_msg)
            else:
                np.testing.assert_equal(len(set(train[df_id].unique()).intersection(set(validation[df_id].unique()))), 0, err_msg=err_msg)
                np.testing.assert_equal(len(set(test[df_id].unique()).intersection(set(validation[df_id].unique()))), 0, err_msg=err_msg)

def assert_df_normalised(df, lower_bound=0.0, upper_bound=1.0, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        numerical_df = df.select_dtypes(include=np.number)

        np.testing.assert_equal(numerical_df.isnull().any().any(), False)

        for col in numerical_df.columns:
            tc.assertLessEqual(lower_bound, numerical_df[col].min(), msg=err_msg)
            tc.assertLessEqual(numerical_df[col].max(), upper_bound, msg=err_msg)

def assert_no_class_imbalance(y, threshold=0.9, err_msg='', test_id = ''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        if hasattr(y, "value_counts"):  # pandas Series
            counts = y.value_counts(normalize=True)
            max_ratio = counts.max()
        elif hasattr(y, "numpy"):  # tf.Tensor
            y = y.numpy()
            _, counts = np.unique(y, return_counts=True)
            max_ratio = counts.max() / counts.sum()
        elif hasattr(y, "detach"):  # torch.Tensor
            y = y.detach().cpu().numpy()
            _, counts = np.unique(y, return_counts=True)
            max_ratio = counts.max() / counts.sum()
        else:  # assume numpy array
            _, counts = np.unique(y, return_counts=True)
            max_ratio = counts.max() / counts.sum()

        tc.assertLess(max_ratio, threshold, msg=err_msg)

def assert_plot_equal(fig, reference_image_path, tol=0, err_msg='', test_id=''):
    if os.environ.get('NBTEST_RUN_ASSERTS', '0') == '0':
        pass
    else:
        test_image_path = os.path.join(output_dir, f'test_plot_{time()}.png')

        try:
            if isinstance(fig, plt.Figure):
                fig.savefig(test_image_path)
            elif isinstance(fig, str) and os.path.exists(fig):
                test_image_path = fig
            else:
                raise TypeError("Argument 'fig' is neither a matplolib figure or a valid file path")

            result = compare_images(reference_image_path, test_image_path, tol=tol)

            if result is not None:
                tc.fail(f"Images are not equal: {result}")

            if os.path.exists(test_image_path):
                os.remove(test_image_path)

        except RuntimeError as e:
            raise RuntimeError(f"An error occurred while comparing images:\n{e}")

vars = []

# List of sklearn module names
sklearn_modules = ["sklearn.ensemble", "sklearn.linear_model", "sklearn.tree", "sklearn.svm", "sklearn.cluster",
                    "sklearn.neural_network", "sklearn.pipeline", "sklearn.semi_supervised", "sklearn.naive_bayes", "sklearn.neighbors",
                    "sklearn.discriminant_analysis", "sklearn.kernel_ridge", "sklearn.multiclass", "sklearn.multioutput", "xgboost.sklearn",
                    "lightgbm.sklearn", "catboost.core"
                    ]


def check_val_type(instrument_value):
    if isinstance(instrument_value, pd.DataFrame):
        value_type = "DataFrame"
    elif isinstance(instrument_value, pd.Series):
        value_type = "Series"
    elif isinstance(instrument_value, list):
        value_type = "list"
    elif isinstance(instrument_value, dict):
        value_type = "dict"
    elif isinstance(instrument_value, (int, float, np.number)):
        value_type = "numeric"
    elif isinstance(instrument_value, str):
        value_type = "string"
    elif isinstance(instrument_value, tuple):
        value_type = "tuple"
    elif isinstance(instrument_value, bool):
        value_type = f"bool"
    # TODO: Edit model type
    elif (
        "keras.src.engine.sequential.Sequential" in str(type(instrument_value)) or
        "keras.src.models.sequential.Sequential" in str(type(instrument_value)) or
        "tensorflow.keras.models" in str(type(instrument_value)) or
        "tensorflow.keras.layers" in str(type(instrument_value)) or
        "torch.nn" in str(type(instrument_value))
    ):
        value_type = "model"

    elif any(module in str(type(instrument_value)) for module in sklearn_modules):
        value_type = "sklearn_model"
    elif "matplotlib.figure.Figure" in str(type(instrument_value)):
        value_type = "plot"
    else:
        value_type = "unknown"

    return value_type

def check_api(api_name, value_type):
    if api_name == "evaluate" and value_type == "list":
        value_type = "evaluate_list"

    return value_type

def get_instrument_dict(value_type, value, cell_no, line_no):
    instrument_value_dict = {"isNone": True}
    try:
        if value_type == "DataFrame":
            instrument_value_dict = {
                "isNone": False,
                "assert_var.shape": value.shape,
                "sorted(assert_var.columns)": sorted(value.columns),
                "[str(assert_var[i].dtype) for i in sorted(assert_var.columns)]": [
                    str(value[i].dtype) for i in sorted(value.columns)
                ]
            }
            numeric_data = value.select_dtypes(include=["number"])
            if not numeric_data.empty:
                mean_value = np.nanmean(numeric_data.to_numpy())
                var_value = np.nanvar(numeric_data.to_numpy())

                instrument_value_dict["np.nanmean(assert_var.select_dtypes(include=['number']).to_numpy())"] = mean_value
                instrument_value_dict["np.nanvar(assert_var.select_dtypes(include=['number']).to_numpy())"] = var_value

        elif value_type == "Series":
            instrument_value_dict = {
                "isNone": False,
                "assert_var.sum()":value.sum()}
        elif value_type == "list":
            instrument_value_dict = {
                "isNone": False,
                "assert_var":value}
        elif value_type == "dict":
            instrument_value_dict = {
                "isNone": False,
                "len(assert_var)":len(value)}
        elif value_type == "numeric":
            instrument_value_dict = {
                "isNone": False,
                "assert_var":value}
        elif value_type == "string":
            instrument_value_dict = {
                "isNone": False,
                "assert_var":str(value)}
        elif value_type == "tuple":
            instrument_value_dict = {
                "isNone": False,
                "assert_var":value}
        elif value_type == "bool":
            instrument_value_dict = {
                "isNone": False,
                "assert_var":value}
        elif value_type == "model":
            instrument_value_dict = {
                "isNone": False,
                "[(layer.__class__.__name__, layer.output_shape, layer.count_params()) for layer in value.layers]": [
                    (layer.__class__.__name__, layer.output_shape, layer.count_params())
                    for layer in value.layers
                ]}
        elif value_type == "sklearn_model":
            instrument_value_dict = {
                "isNone": False,
                "{k: v for k, v in assert_var.get_params().items() if k != 'random_state' and not (hasattr(v, '__module__') and v.__module__.startswith('sklearn'))}": {k: v for k, v in value.get_params().items() if k != 'random_state' and not (hasattr(v, '__module__') and v.__module__.startswith('sklearn'))}
            }
        elif value_type == "evaluate_list":
            instrument_value_dict = {
                "isNone": False,
                "assert_var[0]": value[0],
                "assert_var[1]": value[1]
            }
        elif value_type == "plot":
            tmpdir = os.path.join(output_dir, "tmp_imgs/")
            os.makedirs(tmpdir, exist_ok=True)
            file_path = os.path.join(tmpdir, f"assert_plot_{cell_no}_{line_no}_{int(time())}.png")
            value.savefig(file_path)
            instrument_value_dict = {
                "isNone": False,
                "img_path": file_path  # save image path instead of object
            }
        # TODO
        # elif value_type == 'pipeline_model':
        #     instrument_value_dict = {
        #         "isNone": False,
        #         "[(name, type(obj).__name__) for name, obj in assert_var.steps]": [(name, type(obj).__name__) for name, obj in value.steps]
        #     }
    except:
        instrument_value_dict = {"isNone": True}

    return instrument_value_dict

def instrument(value, cell_no, line_no, notebook_fname_pass, var_name, **kwargs):
    global tracked_pairs

    if collect_flag:
        value_type = check_val_type(value)

        if kwargs.get("api"):
            api_name = kwargs.get("api")
            value_type = check_api(api_name, value_type)

        global notebook_fname
        notebook_fname = notebook_fname_pass
        instrument_value_dict = get_instrument_dict(value_type, value, cell_no, line_no)

        instrument_value_dict["cell_no"] = cell_no
        instrument_value_dict["line_no"] = line_no

        for item in vars:
            if var_name in item:
                existing_data = item[var_name]
                if (existing_data.get("cell_no") == cell_no and
                    existing_data.get("line_no") == line_no):
                    tracked_pairs.add((var_name, cell_no, line_no))
                    return  # Avoid instrumentation in loops

        vars.append({var_name: instrument_value_dict})

def exit_handler():
    global notebook_fname
    global vars
    global tracked_pairs

    # Clean loop variables
    vars = [item for item in vars if not any(
        var_name in item and
        item[var_name].get("cell_no") == cell_no and
        item[var_name].get("line_no") == line_no
        for var_name, cell_no, line_no in tracked_pairs
    )]

    if collect_flag and len(vars):
        output_dir = os.environ.get('NBTEST_OUTPUT_DIR', '.')

        for i, var in enumerate(vars):
            try:
                pickle.dumps(var)
            except Exception as e:
                vars[i] = None  # Replace unserializable variable with None


        # Find previous iterations
        prev_ite = 0
        for file in sorted(glob.glob(os.path.join(output_dir, f"{notebook_fname}_instrumentation_*.pkl"))):
            num = int(file.split("_")[-1].replace(".pkl", ""))
            prev_ite = max(prev_ite, num)

        current_ite = prev_ite + 1
        instrumentation_pkl = os.path.join(output_dir, f"{notebook_fname}_instrumentation_{current_ite}.pkl")

        with open(instrumentation_pkl, "wb") as file:
            pickle.dump(vars, file)

atexit.register(exit_handler)
