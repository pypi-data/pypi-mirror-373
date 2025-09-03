from seshat_classifier import seshat
import numpy as np
import matplotlib.pyplot as plt

# Specify filters to test
filters = ['f090w', 'f200w', 'f356w', 'f480m', 'f770w', 'f1500w']
# Specify classes to search for
classes = ['YSO', 'FS', 'Gal']

# Specify the limiting and saturating magnitudes of your observations
limiting_mags = {'f090w':22, 'f200w':23, 'f356w':24, 'f480m':25, 'f770w':22, 'f1500w':24}
saturating_mags = {'f090w':14, 'f200w':13, 'f356w':12, 'f480m':11, 'f770w':15, 'f1500w':14}

# Specify the expected distribution of errors
sig = 0.02
mean = 0.1
errs = [np.random.normal(mean, sig, size=100) for f in filters] # Choose a suitably large size to capture shape of distribution

# Get the performance
test_results = seshat.test_filters(filters = filters, classes=classes, limiting_mags = limiting_mags, saturating_mags = saturating_mags, errs=errs, threads = 8)

# Plot performance
ax = seshat.cm_custom(test_results.Class,test_results.Predicted_Class,cmap='Greys',display_labels=classes)
plt.tight_layout()
plt.savefig("tests/test_filters_cm_test.png")