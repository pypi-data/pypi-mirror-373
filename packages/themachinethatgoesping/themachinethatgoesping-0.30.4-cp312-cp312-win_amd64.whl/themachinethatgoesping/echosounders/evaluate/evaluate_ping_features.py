import themachinethatgoesping as theping
from tqdm.auto import tqdm


# evaluate if all specified features can be called without crashing
# also evaluate that all possible features exist (even if the function may throw an exception)
def __eval_all_features_can_be_called__(feature_group, name, verbose, throw_exception):
    for f in feature_group.possible_features():
        try:
            if feature_group.has_feature(f):
                get_feature = f"feature_group.get_{f.name}()"
                if verbose:
                    print("[success]      ", get_feature.replace("feature_group", name))
                try:
                    eval(get_feature)
                except Exception as e:
                    raise RuntimeError(f'Error: {get_feature.replace("feature_group", name)} failed with error: {e}')
            else:
                get_feature = f"feature_group.get_{f.name}()"
                if verbose:
                    print("[not available]", get_feature.replace("feature_group", name))
                if not hasattr(feature_group, f"get_{f.name}"):
                    raise RuntimeError(f'Error: {get_feature.replace("feature_group", name)} function does not exist!')
        except Exception as e:
            if throw_exception:
                raise
            print('ERROR(all_features_can_be_called):', e)

    for f in feature_group.possible_feature_groups():
        try:
            if feature_group.has_feature(f):
                if verbose:
                    print()
                __eval_all_features_can_be_called__(eval(f"feature_group.{f.name}"), f"{name}.{f.name}", verbose=verbose, throw_exception=throw_exception)
            else:
                if verbose:
                    print()
                get_feature = f"feature_group.{f.name}"
                if verbose:
                    print("[not available]", get_feature.replace("feature_group", name))

                try:
                    has_attr = hasattr(feature_group, f"{f.name}")
                except:
                    has_attr = True  # hasattr returns false if the attribute does not exist, but it sometimes throw san exceptions for attributes that to exist

                if not has_attr:
                    raise RuntimeError(f'Error: {get_feature.replace("feature_group", name)} function does not exist!')
        except Exception as e:
            if throw_exception:
                raise
            print('ERROR(all_features_can_be_called):', e)


def __eval_get_and_has_functions_are_features__(feature_group, name, throw_exception=True):
    features = feature_group.feature_string(True).replace(" ", "").split(",")
    features += feature_group.feature_string(False).replace(" ", "").split(",")
    features += feature_group.feature_groups_string(True).replace(" ", "").split(",")
    features += feature_group.feature_groups_string(False).replace(" ", "").split(",")
    # add exceptions
    features += ["any_of_features", "primary_features", "feature", "all_of_features", "features"]

    for method in dir(feature_group):
        try:
            if method.startswith("has_"):
                if not method.replace("has_", "") in features:
                    raise RuntimeError(f"Has method that is not a feature: {name}.{method}")
            if method.startswith("get_"):
                if not method.replace("get_", "") in features:
                    raise RuntimeError(f"Get method that is not a feature: {name}.{method}")
        except Exception as e:
            if throw_exception:
                raise
            print('ERROR(get_and_has_functions_are_features):', e)

    for f in feature_group.possible_feature_groups():
        if feature_group.has_feature(f):
            __eval_get_and_has_functions_are_features__(
                eval(f"feature_group.{f.name}"), f"{name}.{f.name}", throw_exception
            )


def evaluate_ping_features_can_be_called(ping, verbose=False, throw_exception=True):
    if not isinstance(ping, theping.echosounders.filetemplates.I_Ping):
        if hasattr(ping, "__iter__") or hasattr(ping, "__getitem__"):
            items = tqdm(ping, desc="Evaluating pings", unit="ping", leave=True) if verbose else ping
            for item in items:
                evaluate_ping_features_can_be_called(
                    item, verbose=False
                )  # don't be verbose in individual pings when handling lists
        else:
            raise ValueError("ping must be a single I_Ping object or a list of I_Ping objects")
    else:
        __eval_get_and_has_functions_are_features__(ping, name="ping", throw_exception=False)
        __eval_all_features_can_be_called__(ping, name="ping", verbose=verbose, throw_exception=throw_exception)
