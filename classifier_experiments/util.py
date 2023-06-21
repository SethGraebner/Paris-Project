'''
General utility file to box up some common functions. Could probably move more things here.
'''

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

def provide_confusion_matrix(y_te, y_pred):
    # Create confusion matrix
    cm = confusion_matrix(y_te, y_pred)

    # Calculate percentages
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    # Set up figure
    fig, ax = plt.subplots(figsize=(8, 6))

    # Create heatmap
    sns.heatmap(cm_norm, annot=True, cmap='Blues', fmt='.2%', cbar=False)

    # Set axis labels
    ax.set_xlabel('Predicted label')
    ax.set_ylabel('True label')

    # Set title
    ax.set_title('Confusion Matrix')

    # label 0 -> good, 1 -> bad
    ax.xaxis.set_ticklabels(['good', 'bad'])
    ax.yaxis.set_ticklabels(['good', 'bad'])

    # Show plot
    plt.show()