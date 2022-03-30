import os
import inspect

# Add the site_features.csv file to the path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
root = os.path.dirname(current_dir)
site_features_file_path = root + '/publishers/site_features.csv'
