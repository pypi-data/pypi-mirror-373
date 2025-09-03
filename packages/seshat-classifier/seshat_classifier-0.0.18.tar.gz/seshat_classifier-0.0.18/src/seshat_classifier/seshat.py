from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pandas as pd
import xgboost as xgb
import numpy as np
import random
from astropy.table import Table
import pandas as pd
import importlib.resources as resources
import pathlib
import requests
from astropy.table import Table

# Cache directory for large CSVs
CACHE_DIR = pathlib.Path.home() / ".seshat_classifier" / "data"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# URLs for hosted large CSVs
CSV_URLS = {
    "training_set.csv": "https://bcrompvoets.github.io/assets/files/seshat/training_set.csv",
    "training_set_cosmological.csv": "https://bcrompvoets.github.io/assets/files/seshat/training_set_cosmological.csv",
    "training_set_AGB.csv": "https://bcrompvoets.github.io/assets/files/seshat/training_set_AGB.csv",
}


# Load a small CSV packaged with the code
def _load_small_csv(name):
    with resources.files("seshat_classifier").joinpath("data",name).open("rb") as f:
        return pd.read_csv(f)
def _load_big_csv(name):
    url = CSV_URLS[name]
    path = CACHE_DIR / name
    etag_path = CACHE_DIR / f"{name}.etag"

    # Try to use cache if it exists
    if path.exists():
        try:
            head = requests.head(url, timeout=5)
            if head.status_code == 200:
                remote_etag = head.headers.get("ETag")
                local_etag = etag_path.read_text().strip() if etag_path.exists() else None
                if remote_etag and remote_etag == local_etag:
                    return pd.read_csv(path)
        except requests.RequestException:
            print(f"[seshat_classifier] Offline — using cached {name}")
            return pd.read_csv(path)

    # If we get here, we either have no file or need to update it
    try:
        print(f"[seshat_classifier] Downloading {name}...")
        r = requests.get(url, stream=True, timeout=10)
        r.raise_for_status()
        path.write_bytes(r.content)

        # Save ETag
        etag = r.headers.get("ETag")
        if etag:
            etag_path.write_text(etag)

        print(f"[seshat_classifier] Saved to {path}")
        return pd.read_csv(path)

    except requests.RequestException as e:
        if path.exists():
            print(f"[seshat_classifier] Warning: Could not update {name} ({e}), using cached file")
            return pd.read_csv(path)
        else:
            raise FileNotFoundError(
                f"Could not download {name} and no cached copy exists. "
                "Please connect to the internet and try again."
            )

def relabel_training_classes(keep_class,inp_df,real=None):
    """ This function relabels the classes in terms of numbers, assigned at runtime. """
    possible_classes = ["YSO", "FS", "WD", "BD", "Gal"]

    # Make new dataframe with just the classes requested
    inp_new = inp_df[inp_df["Class"].isin(keep_class)].copy()

    # If contaminant class is requested, make new class of everything not otherwise requested
    if "Contaminant" in keep_class:
        inp_new.loc[~inp_new["Class"].isin(keep_class), "Class"] = "Contaminant"

    # Make an ordered list of what the requested classes are
    keep_class_new = [p for p in possible_classes if p in keep_class]
    if 'Contaminant' in keep_class:
        keep_class_new.append('Contaminant')

    # Write a new label that gives an integer value for each class.
    inp_new["Class_Label"] = pd.Categorical(inp_new["Class"], categories=keep_class_new).codes
    
    # Relabel the real set as well.
    if real is not None:
        real["Class_Label"] = pd.Categorical(real["Class"], categories=keep_class_new).codes
        return inp_new, real, keep_class_new

    return inp_new, keep_class_new

def classify(real, 
            cosmological=False,
            classes=["YSO", "FS", "BD", "WD", "Gal"],
            return_test=True,
            threads=1):
    """ This function is the main function of SESHAT. It takes a real dataset and classifies it into the provided classes, with probabilities.
    
    Inputs:
    real (DataFrame or Table): The input catalog, either a FITS table or a apandas DataFrame, with columns as described in the README.
    cosmological (bool): Whether the catalog is of a cosmological field
    classes (list): The classes to be assigned, can be "YSO", "FS", "BD", "WD", "Gal, or "Contaminant" (the latter is still under development, use at own risk)
    return_test (bool): Whether to return the test set original and predicted classifications, and predicted probabilities
    threads (int): The number of threads to use when classifying.

    Returns:
    real (DataFrame or Table): A copy of the input catalog, now with classifications and probabilities
    (optional) test (DataFrame): A pandas DataFrame containing the following columns: the true class, the predicted class, and a column each for each class specified in the input classes list.
    """

    # Load small packaged CSV
    veg_jy = {f: v for (f, v) in _load_small_csv("veg_zps_spitzer_2mass_jwst.csv").values}

    # Convert Table to pandas if needed
    if isinstance(real, Table):
        real = real.to_pandas()
        table = True
    else:
        table = False

    # Load appropriate large input data CSV
    if cosmological:
        inp_df = _load_big_csv("training_set_cosmological.csv")
    else:
        inp_df = _load_big_csv("training_set.csv")

    if "AGB" in classes:
        inp_df = _load_big_csv("training_set_AGB.csv")
        

    inp_df, new_classes = relabel_training_classes(classes,inp_df)

    # Determine filters to use
    filters = [f for f in real.columns if f in veg_jy.keys()]

    # Prep XGBoost matrices
    dtrain, dval, dte, dreal = prep_all_dat(inp_df, real, filters)
    
    # Train XGBoost model
    evallist = [(dtrain, "train"),  (dte, "test"), (dval, "eval")]
    metric = ["mlogloss"]
    params = {
        "nthread": threads,
        "gamma": 15,
        "subsample": 0.3,
        "max_depth": 1,
        "eta": 0.01,
        "objective": "multi:softprob",
        "num_class": len(np.unique(dtrain.get_label())),
        "eval_metric": metric,
    }
    
    num_trees = 10000
    evals_result = {}
    xgb_cls = xgb.train(params, dtrain, num_trees, evallist, early_stopping_rounds=50, evals_result=evals_result, verbose_eval=False)
    best_iter = xgb_cls.best_iteration + 1

    
    # Get predictions
    real = get_preds(xgb_cls.predict(dreal, iteration_range=(0, best_iter)), real, new_classes)
    if table:
        real = Table.from_pandas(real)
    
    if return_test:
        classes= np.array(new_classes)[np.array(dte.get_label().astype(int))]
        test_df = pd.DataFrame({"Class":classes})
        test = get_preds(xgb_cls.predict(dte, iteration_range=(0, best_iter)), test_df, new_classes)
        return (real, test) 

    return real



def get_preds(probs, df,display_labels):
    """ Get a column for each label with the probability for each object. Also get a column with the assigned label based on the greatest probability."""
    classes = np.array(display_labels)[np.array(probs.argmax(axis=1))]
    df = df.assign(Predicted_Class=classes).join(pd.DataFrame(probs, columns=[f"Prob {l}" for l in display_labels], index=df.index))
    return df

    

def add_noise(filters, df,df_real):
    """ Add noise based on the wavelength as determined from real data. """

    # Make sure no infinite datapoints
    df = df.replace([np.inf, -np.inf], np.nan)

    # Compute means and stds of error for all filters
    means = df_real[['e_'+f for f in filters]].mean(skipna=True).to_numpy()
    stds  = df_real[['e_'+f for f in filters]].std(skipna=True).to_numpy()
    # Randomly add or subtract error (i.e. +/- noise)
    noise = np.random.choice([1, -1], size=(len(df), len(filters)))*np.random.normal(loc=means, scale=stds, size=(len(df), len(filters)))

    df_tmp = df.copy()
    df_tmp[filters] = df[filters].to_numpy() + noise
    df_new = pd.concat([df, df_tmp], ignore_index=True)

    return df_new

def add_null(df, filters, n=1000):
    """ Add nulls to the synthetic data"""
    max_ind = len(df)
    df_list = []

    # First pass
    for f in filters:
        rand_vals = np.random.randint(0, max_ind, n)
        df_f = df.iloc[rand_vals].copy()
        df_f[f] = np.nan
        df_list.append(df_f)

    # Build base once for second pass sampling
    base = pd.concat([df] + df_list, ignore_index=True)
    miss_one_ind = len(base)

    # Second pass
    for f in filters:
        rand_vals = np.random.randint(max_ind, miss_one_ind, n // 2)
        df_f = base.iloc[rand_vals].copy()
        df_f[f] = np.nan
        df_list.append(df_f)

    return pd.concat([df] + df_list, ignore_index=True)




def oversample(df, n = 25000):
    """A simple function for oversampling all the classes in a dataframe to the same degree. 
    Takes as input a dataframe and returns a new dataframe with oversampled classes.
    NOTE: do not use prior to splitting data into training and validation as this will
    result in copies of the same rows."""
    for label in np.unique(df.Class):
        df_l = df[df.Class==label].copy()
        df_l.reset_index(drop=True,inplace=True)
        df_l = pd.concat([df_l]*int(np.ceil(n/len(df_l))),ignore_index=True).reset_index(drop=True)
        
        # Intentionally do not oversample the brown and white dwarfs to keep these classes imbalanced.
        if (label == "WD") | (label == "BD"):
            rand_samp = random.sample(range(0,len(df_l[df_l.Class==label])),int(n/2))
        else:
            rand_samp = random.sample(range(0,len(df_l[df_l.Class==label])),n)

        try:
            df_new = pd.concat([df_l.loc[rand_samp].copy(),df_new])
        except:
            df_new = df_l.loc[rand_samp].copy()
    df_new = df_new.sample(frac=1).reset_index(drop=True)
    return df_new
        
def prep_all_dat(df_train, df_real, filters):
    """Prepare the data with PCA columns included. Takes as input the training, validation, test,
      and real data to be transformed according to PCA, as well as the filters for creating colours,
      and whether or not the real input catalog has labels already associated with it."""


    # Get colours/other features
    df_train_new = add_fc(df_train.copy(),filters,train=True)
    df_real_new = add_fc(df_real.copy(),filters,train=False)
    df_train_new = df_train_new.replace([np.inf, -np.inf], np.nan)
    df_real_new = df_real_new.replace([np.inf, -np.inf], np.nan)

    # Apply PCA on all features that aren't mags
    fcd_columns = [c for c in df_train_new.columns if ('-' in c) | ('/' in c)]


    # Split data
    df_train_new, df_val_new = train_test_split(df_train_new, train_size=0.75, random_state=700)
    df_val_new, df_test_new = train_test_split(df_val_new, train_size=0.5, random_state=700)

    # Add noise and null values to training and validation sets
    # inp_df = add_noise(filters, inp_df, real)
    # inp_df = add_null(inp_df, filters, n=50)
    df_val_new = add_noise(filters, df_val_new, df_real_new)
    df_val_new = add_null(df_val_new, filters, n=500)

    # Oversample training set and finish prepping
    df_train_new = oversample(df_train_new)
    fcd_columns = [c for c in df_train_new.columns if ('-' in c) | ('/' in c) | c.startswith('PCA_')]
    df_train_new = df_train_new.replace([np.inf, -np.inf], np.nan)
    df_val_new = df_val_new.replace([np.inf, -np.inf], np.nan)
    df_test_new = df_test_new.replace([np.inf, -np.inf], np.nan)
    df_real_new = df_real_new.replace([np.inf, -np.inf], np.nan)
    
    # Transform to dmatrices
    dmatrix_tr_df = xgb.DMatrix(df_train_new[fcd_columns], label=df_train_new['Class_Label'], missing=np.NaN)
    dmatrix_va_df = xgb.DMatrix(df_val_new[fcd_columns], label=df_val_new['Class_Label'], missing=np.NaN)
    dmatrix_te_df = xgb.DMatrix(df_test_new[fcd_columns], label=df_test_new['Class_Label'], missing=np.NaN)
    
    dmatrix_re_df = xgb.DMatrix(df_real_new[fcd_columns], missing=np.NaN)
    return dmatrix_tr_df, dmatrix_va_df, dmatrix_te_df, dmatrix_re_df



def add_fc(dao_fcd,filters,train=False):
    """Function for adding in colours for the specified filters. All filter combinations
    are returned."""
    if train:
        dao_fcd = dao_fcd.sample(frac=1).reset_index(drop=True)
    
    for f, filt in enumerate(filters):
        if train == True:
            dao_fcd = add_null(dao_fcd,filters)
        for filt2 in filters[f+1:]:
            col = filt+"-"+filt2
            dao_fcd[col] = dao_fcd[filt] - dao_fcd[filt2]
            
    return dao_fcd


import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['font.family'] = 'serif'

def cm_custom(y_true, y_pred, display_labels=None, ax=None, cmap='Greys'):
    # Get confusion matrix
    if (len(display_labels) <= 3) & ('FS' in display_labels):
        print(display_labels=='FS',display_labels[display_labels.index('FS')])
        display_labels[display_labels.index('FS')] = 'Field Stars'
    if (len(display_labels) > 3) & ('Brown Dwarfs' in display_labels): 
        display_labels[display_labels.index('Brown Dwarfs')] = 'BDs'
    if (len(display_labels) > 3) & ('White Dwarfs' in display_labels): 
        display_labels[display_labels.index('White Dwarfs')] = 'WDs'
    if (len(display_labels) > 3) & ('Galaxies' in display_labels): 
        display_labels[display_labels.index('Galaxies')] = 'Gals'
    cm = confusion_matrix(y_true, y_pred, labels=range(len(display_labels)))
    cm_norm = cm.astype('float') / cm.sum(axis=1, keepdims=True)

    # Create custom annotations: normalized (first line), counts (second line)
    annot = np.empty_like(cm).astype(str)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            norm_val = f"{cm_norm[i, j]:.2f}"
            count_val = f"{cm[i, j]}"
            annot[i, j] = f"{norm_val}\n{count_val}"

    # If no axis is given, create one
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 6))

    # Draw heatmap with custom annotations
    sns.heatmap(
        cm_norm,
        annot=annot,
        fmt='',
        cmap=cmap,
        vmin=0,
        vmax=1,
        square=True,
        xticklabels=display_labels,
        yticklabels=display_labels,
        ax=ax,
        cbar_kws={'label': 'Normalized value'}
    )

    ax.set_xlabel('Predicted label')
    ax.set_ylabel('True label')

    return ax





def test_filters(filters, classes, err_mu = 0.1, err_sig = 0.02, threads=1):
    """ This function is for testing filter choices for JWST proposals. Specifically, it is used to determine
    what the best performance of SESHAT will be with those filters. Optionally, one can input the assumed error
    for these observations. By default, a normal distribution with mean 0.1 and standard deviation 0.02 is assumed.
    
    Inputs:
    filters (list): The filters to be tested.
    classes (list): The classes to be identified.
    err_mu (float): Mean for the normal distribution of assumed error. Default 0.1 mag.
    err_sig (float): Standard deviation for the normal distribution of assumed error. Default 0.02 mag.
    threads (int): The number of threads to use when classifying.

    Returns:
    test (DataFrame): A pandas DataFrame containing the true classes, the predicted classes, as well as the predicted probabilities for the test set.
    """
    
    df_tmp = pd.DataFrame({f:[99]*100 for f in filters})
    for f in filters:
        df_tmp['e_'+f] = np.random.normal(err_mu, err_sig, 100)

    _, test = classify(real=df_tmp,classes=classes,threads=threads)
    return test