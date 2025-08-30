import yaml
import fmot
from pathlib import Path
from fmot.test.utm.get_utms import ALL_UTMS
import tqdm
from typing import *

TOL_PATH = Path(fmot.__file__).parent / "test" / "utm" / "quantization_tolerance.yaml"


def load_tolerances() -> dict:
    with open(TOL_PATH, "r") as f:
        tolerances = yaml.safe_load(f)

    return tolerances


def write_tolerances(tolerances):
    with open(TOL_PATH, "w") as f:
        yaml.dump(tolerances, f)


def run_measurement(name, utm):
    err_dbl = utm.get_quantization_nrmse(bw_conf="double")
    err_std = utm.get_quantization_nrmse(bw_conf="standard")
    err_eig = utm.get_quantization_nrmse(bw_conf="eights")
    return name, (err_dbl, err_std, err_eig)


def measure_errors():
    measurements = {}

    for name, utm in tqdm.tqdm(ALL_UTMS.items()):
        try:
            err_dbl = utm.get_quantization_nrmse(bw_conf="double")
            measurements[f"{name}-double"] = err_dbl
        except:
            pass

        try:
            err_std = utm.get_quantization_nrmse(bw_conf="standard")
            measurements[f"{name}-standard"] = err_std
        except:
            pass

        try:
            err_eig = utm.get_quantization_nrmse(bw_conf="eights")
            measurements[f"{name}-eights"] = err_eig
        except:
            pass
    return measurements


def ask_to_continue(message=None) -> bool:
    yes = {"yes", "y", ""}
    no = {"no", "n"}

    if message is not None:
        print(message)
    choice = input("Continue [Y](es)/n(o)?  ").lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        print("Please respond with 'y', 'yes', '', 'n', or 'no'")
        return ask_to_continue()


def set_tolerances(
    mode: Literal["overwrite", "max", "min"], alpha: float = 1.5, force=False
):
    print(f'Setting new quantization error tolerances in "{mode}" mode')

    print(
        f"Measuring quantization errors..., new tolerances values will be {alpha:.2f} x current errors"
    )
    # set new tolerances to alpha * measured error
    new_tols = measure_errors()
    for k, v in new_tols.items():
        new_tols[k] = alpha * v

    curr_tols = load_tolerances()

    if mode == "overwrite":
        print(
            "WARNING: if you continue, all quantization tolerances will be set to new values"
        )
        if force or ask_to_continue():
            write_tolerances(new_tols)
        else:
            print("ABORTING")

    # raise bounds on errors
    elif mode == "max":
        print("Setting new tolerances as the max of current and new tolerances")
        for name, newval in new_tols.items():
            curval = curr_tols.get(name, None)
            if curval is not None:
                if newval > curval and (
                    force
                    or ask_to_continue(
                        f"Raise tolerance of {name} from {curval:.3E} to {newval:.3E}?"
                    )
                ):
                    pass

                else:
                    new_tols[name] = curval
        write_tolerances(new_tols)

    elif mode == "min":
        print("Setting new tolerances as the min of current and new tolerances")
        for name, newval in new_tols.items():
            curval = curr_tols.get(name, None)

            if curval is not None:
                if newval < curval and (
                    force
                    or ask_to_continue(
                        f"Lower tolerance of {name} from {curval:.3E} to {newval:.3E}?"
                    )
                ):
                    pass
                else:
                    new_tols[name] = curval
        write_tolerances(new_tols)


if __name__ == "__main__":
    set_tolerances("min", 2, False)
