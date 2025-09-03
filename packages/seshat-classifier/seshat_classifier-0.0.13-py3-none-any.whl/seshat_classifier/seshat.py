from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pandas as pd
import xgboost as xgb
import numpy as np
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
    "training_set.csv": "https://bcrompvoets.github.io/files/seshat/training_set.csv",
    "training_set_cosmological.csv": "https://bcrompvoets.github.io/files/seshat/training_set_cosmological.csv",
    "training_set_AGB.csv": "https://bcrompvoets.github.io/files/seshat/training_set_AGB.csv",
}

# Load a small CSV packaged with the code
def _load_small_csv(name):
    with resources.files("seshat_classifier").joinpath("data",name).open("rb") as f:
        return pd.read_csv(f)

# Download/cache a large CSV with ETag-based refresh
def _load_big_csv(name):
    url = CSV_URLS[name]
    path = CACHE_DIR / name
    etag_path = CACHE_DIR / f"{name}.etag"

    # Check for ETag changes
    if path.exists() and etag_path.exists():
        try:
            head = requests.head(url, timeout=5)
            if head.status_code == 200:
                remote_etag = head.headers.get("ETag")
                local_etag = etag_path.read_text().strip()
                if remote_etag and remote_etag == local_etag:
                    return pd.read_csv(path)
        except requests.RequestException:
            return pd.read_csv(path)  # Use cached if check fails

    # Download new or updated file
    print(f"[seshat_classifier] Downloading {name}...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    path.write_bytes(r.content)

    # Save new ETag
    etag = r.headers.get("ETag")
    if etag:
        etag_path.write_text(etag)

    print(f"[seshat_classifier] Saved to {path}")
    return pd.read_csv(path)

def ml_test(real, label=True, cosmological=False,
            classes=["YSOs", "FS", "Galaxies", "Brown Dwarfs", "White Dwarfs"],
            return_test=True):

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


    inp_df.loc[(inp_df.label == 5) | (inp_df.label == 6), 'label'] = 4  # Collapse CHeB blue/red
        


    # Define canonical classes in dataset
    possible_classes = ["YSOs", "MS", "SGB", "RGB", "CHeB", "CHEB-blue", "CHeB-red", "EAGB", "TPAGB", "Post-AGB", "Galaxies", "Brown Dwarfs", "White Dwarfs"]

    # Group definitions
    fs_components = ["MS", "SGB", "RGB", "CHeB", "EAGB", "TPAGB", "Post-AGB"]
    agb_components = ["TPAGB"]

    # Expand "AGB" into components
    has_agb = "AGB" in classes
    if has_agb:
        classes = list(set(classes) - {"AGB"}) + agb_components

    # Expand "FS" into components (possibly excluding AGB if AGB is also selected)
    if "FS" in classes:
        if has_agb:
            fs_effective = [c for c in fs_components if c not in agb_components]
        else:
            fs_effective = fs_components
    else:
        fs_effective = []

    # Build class-to-group mapping (e.g., MS → FS, EAGB → AGB)
    class_label_map = {}
    new_classes = []

    for cls in classes:
        if cls == "FS":
            for subcls in fs_effective:
                class_label_map[subcls] = "FS"
            if "FS" not in new_classes:
                new_classes.append("FS")
        elif cls in agb_components:
            class_label_map[cls] = "AGB"
            if "AGB" not in new_classes:
                new_classes.append("AGB")
        else:
            class_label_map[cls] = cls
            if cls not in new_classes:
                new_classes.append(cls)

    # Index-to-class mapping from file
    label_to_class = {i: c for i, c in enumerate(possible_classes)}

    # Keep only relevant rows
    valid_labels = [i for i, c in label_to_class.items() if c in class_label_map]
    inp_df = inp_df[inp_df.label.isin(valid_labels)]
    inp_df["class_name"] = inp_df.label.map(label_to_class).map(class_label_map)

    # Map class names to numeric training labels
    class_encoding = {name: i for i, name in enumerate(new_classes)}
    # print(class_encoding,label_to_class,class_label_map)
    inp_df["label"] = inp_df["class_name"].map(class_encoding)

    if label:
        real = real[real.label.isin(valid_labels)]
        real["class_name"] = real.label.map(label_to_class).map(class_label_map)
        real["label"] = real["class_name"].map(class_encoding)

    # Determine filters to use
    filters = [f for f in real.columns if f in veg_jy.keys()]
    

    # Split data
    inp_df, test_df = train_test_split(inp_df, train_size=0.75, random_state=700)
    val_df, test_df = train_test_split(test_df, train_size=0.5, random_state=700)

    # Add noise and null values to training and validation sets
    # inp_df = add_noise(filters, inp_df, real)
    # inp_df = add_null(inp_df, filters, n=50)
    val_df = add_noise(filters, val_df, real)
    val_df = add_null(val_df, filters, n=500)

    # Prep XGBoost matrices
    dtrain, dval, dte, dreal = prep_all_dat(inp_df, val_df, test_df, real, filters, label)

    inp = pd.DataFrame(dtrain.get_data().toarray(), columns=dtrain.feature_names)
    inp["label"] = dtrain.get_label()
    
    # Train XGBoost model
    evallist = [(dtrain, "train"),  (dte, "test"), (dval, "eval")]
    metric = ["mlogloss","merror"]
    param_final = {
        "nthread": 6,
        "gamma": 15,
        "subsample": 0.3,
        "max_depth": 1,
        "eta": 0.01,
        "objective": "multi:softprob",
        "num_class": len(np.unique(dtrain.get_label())),
        "eval_metric": metric,
    }

    num_trees = 10000
    xgb_cls = xgb.train(param_final, dtrain, num_trees, evallist, early_stopping_rounds=100, verbose_eval=False)
    best_iter = xgb_cls.best_iteration + 1
    print(best_iter)

    # Get predictions
    real = get_preds(xgb_cls.predict(dreal, iteration_range=(0, best_iter)), real, new_classes)
    test = get_preds(xgb_cls.predict(dte, iteration_range=(0, best_iter)), test_df, new_classes)

    if table:
        real = Table.from_pandas(real)

    return (real, test, new_classes) if return_test else real


def get_preds(probs, df,display_labels):
    df['pred'] = np.argmax(probs,axis=1)
    for i, l in enumerate(display_labels):
        df['Prob '+l] = np.transpose(probs)[i]
    return df


def add_pca(df_train, df_val, df_test, df_real, features, n_comp=5,label_use = 'label'):
    # Copy to avoid modifying original data
    df_train = df_train.copy().reset_index(drop=True)
    df_val = df_val.copy().reset_index(drop=True)
    df_test = df_test.copy().reset_index(drop=True)
    df_real = df_real.copy().reset_index(drop=True)

    # Drop rows with NaNs for PCA training
    df_train_pca = df_train.dropna(subset=features).copy()
    df_val_pca = df_val.dropna(subset=features).copy()
    df_test_pca = df_test.dropna(subset=features).copy()
    df_real_pca = df_real.dropna(subset=features).copy()

    # Fit scaler and PCA only on valid training data
    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(df_train_pca[features])
    scaled_val = scaler.transform(df_val_pca[features])
    scaled_test = scaler.transform(df_test_pca[features])
    scaled_real = scaler.transform(df_real_pca[features])

    pca = PCA(n_components=n_comp)
    train_pca_components = pca.fit_transform(scaled_train,df_train_pca[label_use])
    val_pca_components = pca.transform(scaled_val)
    test_pca_components = pca.transform(scaled_test)
    real_pca_components = pca.transform(scaled_real)

    # Add PCA columns to original dataframes (initialized with NaNs)
    for i in range(n_comp):
        colname = f'PCA_{i+1}'
        df_train[colname] = np.nan
        df_val[colname] = np.nan
        df_test[colname] = np.nan
        df_real[colname] = np.nan

        df_train.loc[df_train_pca.index, colname] = train_pca_components[:, i]
        df_val.loc[df_val_pca.index, colname] = val_pca_components[:, i]
        df_test.loc[df_test_pca.index, colname] = test_pca_components[:, i]
        df_real.loc[df_real_pca.index, colname] = real_pca_components[:, i]

    return df_train, df_val, df_test, df_real,

    
    

def add_noise(filters, df,df_real):
    """ Add noise based on the wavelength, with decreasing noise with increasing wavelength. """
    df = df.copy()
    df = df.replace([np.inf, -np.inf], np.nan)
    df_tmp = df.copy()
    
    for f in filters:
        noise = np.random.normal(np.nanmean(df_real['e_'+f]),np.nanstd(df_real['e_'+f]),len(df_tmp))
        df_tmp[f] = df[f] + noise*np.random.choice([1,-1],len(df_tmp))#/wvs[f]
    try:
        df_new = pd.concat([df_tmp,df_new])
    except:
        df_new = pd.concat([df.copy(),df_tmp])
    df_new = df_new.sample(frac=1).reset_index(drop=True)
    return df_new


def add_null(df,filters, n = 1000):
    max_ind = len(df)
    for f in filters:
        rand_vals = np.random.randint(0,max_ind,n)
        df_f = df.iloc[rand_vals].reset_index(drop=True)
        df_f[f] = np.nan # Set that filter to be null
        df = pd.concat([df,df_f])
        df.reset_index(drop=True,inplace=True)
    miss_one_ind = len(df)
    for f in filters:
        rand_vals = np.random.randint(max_ind,miss_one_ind,int(n/2))
        df_f = df.iloc[rand_vals].reset_index(drop=True)
        df_f[f] = np.nan # Set that filter to be null
        df = pd.concat([df,df_f])
        df.reset_index(drop=True,inplace=True)
    return df



def oversample(df, n = 25000):
    for label in np.unique(df.Label):
        # print(label)
        df_l = df[df.Label==label].copy()
        df_l.reset_index(drop=True,inplace=True)
        df_l = pd.concat([df_l]*int(np.ceil(n/len(df_l))),ignore_index=True).reset_index(drop=True)
        if len(np.unique(df.Label)) == 3:
            rand_samp = random.sample(range(0,len(df_l[df_l.Label==label])),n)
        elif (label == 2) | (label == 3):
            rand_samp = random.sample(range(0,len(df_l[df_l.Label==label])),int(n/2))
        else:
            rand_samp = random.sample(range(0,len(df_l[df_l.Label==label])),n)
        try:
            df_new = pd.concat([df_l.loc[rand_samp].copy(),df_new])
        except:
            df_new = df_l.loc[rand_samp].copy()
    df_new = df_new.sample(frac=1).reset_index(drop=True)
    return df_new
        
def prep_all_dat(df_train, df_val, df_test, df_real, filters, label=True):
    # Get colours/other features
    df_train_new = add_fc(df_train.copy(),filters,train=True)
    df_val_new = add_fc(df_val.copy(),filters,train=False)
    df_test_new = add_fc(df_test.copy(),filters,train=False)
    df_real_new = add_fc(df_real.copy(),filters,train=False)
    df_train_new = df_train_new.replace([np.inf, -np.inf], np.nan)
    df_val_new = df_val_new.replace([np.inf, -np.inf], np.nan)
    df_test_new = df_test_new.replace([np.inf, -np.inf], np.nan)
    df_real_new = df_real_new.replace([np.inf, -np.inf], np.nan)

    # Apply PCA on all features that aren't mags
    fcd_columns = [c for c in df_train_new.columns if ('-' in c) | ('/' in c)]
    df_train_new, df_val_new, df_test_new, df_real_new = add_pca(df_train_new, df_val_new, df_test_new, df_real_new, fcd_columns,n_comp=2)
    

    # Oversample training set and finish prepping
    df_train_new = oversample(df_train_new)
    
    # fcd_columns = [c for c in df_train_new.columns if c.startswith('PCA_')]
    fcd_columns = [c for c in df_train_new.columns if ('-' in c) | ('/' in c) | c.startswith('PCA_')]
    df_train_new = df_train_new.replace([np.inf, -np.inf], np.nan)
    df_val_new = df_val_new.replace([np.inf, -np.inf], np.nan)
    df_test_new = df_test_new.replace([np.inf, -np.inf], np.nan)
    df_real_new = df_real_new.replace([np.inf, -np.inf], np.nan)
    
    # Transform to dmatrices
    dmatrix_tr_df = xgb.DMatrix(df_train_new[fcd_columns], label=df_train_new['label'], missing=np.NaN)
    inp = pd.DataFrame(dmatrix_tr_df.get_data().toarray(),columns=dmatrix_tr_df.feature_names)
    
    dmatrix_va_df = xgb.DMatrix(df_val_new[fcd_columns], label=df_val_new['label'], missing=np.NaN)
    dmatrix_te_df = xgb.DMatrix(df_test_new[fcd_columns], label=df_test_new['label'], missing=np.NaN)
    if label:
        dmatrix_re_df = xgb.DMatrix(df_real_new[fcd_columns], label=df_real_new['label'], missing=np.NaN)
    else:
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
            # col_sq = filt+"-"+filt2+'sq'
            # dao_fcd[col_sq] = dao_fcd[col]**2
            # col_rt = filt+"-"+filt2+'root'
            # dao_fcd[col_rt] = 1/dao_fcd[col_sq]
            # col_exp = 'flux-ratio_'+ filt+"/"+filt2
            # dao_fcd[col_exp] = 10**(0.4*dao_fcd[col])
            # col = filt+"/"+filt2
            # dao_fcd[col] = dao_fcd[filt]/dao_fcd[filt2]
            
    return dao_fcd


import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['font.family'] = 'serif'

def cm_custom(y_true, y_pred, display_labels=None, ax=None, cmap='Greys', integers=True):
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
        fig, ax = plt.subplots(figsize=(7, 6))

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