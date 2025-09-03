from seshat_classifier import seshat
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

cosmos = pd.read_csv("~/Documents/Star_Formation/YSO+Classification/Synthetic_Data/Data/COSMOSWeb_Labeled.csv")
cosmos['Class'] = 'Gal'
cosmos.loc[cosmos.Label==3,'label'] = 'BD'
display_labels = np.unique(cosmos.Class.values)
cosmos = seshat.classify(cosmos,cosmological=True,classes=display_labels,return_test=False)

ax = seshat.cm_custom(cosmos.label.values,cosmos.pred,cmap='Greys',display_labels=display_labels)
plt.tight_layout()
plt.savefig("cosmos_cm_test.png")