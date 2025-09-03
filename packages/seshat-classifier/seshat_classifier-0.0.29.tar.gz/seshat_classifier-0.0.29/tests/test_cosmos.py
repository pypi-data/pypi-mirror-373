from seshat_classifier import seshat
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

cosmos = pd.read_csv("~/Documents/Star_Formation/YSO+Classification/Synthetic_Data/Data/COSMOSWeb_Labeled.csv")
cosmos['Class'] = 'Gal'
cosmos.loc[cosmos.Label==3,'Class'] = 'BD'
display_labels = list(np.unique(cosmos.Class.values))
cosmos = seshat.classify(cosmos,cosmological=False,classes=display_labels,return_test=False)

ax = seshat.cm_custom(cosmos.Class,cosmos.Predicted_Class,cmap='Greys',display_labels=display_labels)
plt.tight_layout()
plt.savefig("tests/cosmos_cm_test.png")