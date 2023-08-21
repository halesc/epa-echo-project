"""
This module is used to train and test the model. The model is trained using the BaggingRegressor algorithm. This module will also param tune the model. The model is saved to the lib folder.
TODO: Add the ability to select which features to use.
"""

import os
import pickle
import datetime
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import BaggingRegressor, RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


DT = datetime.datetime.now()
print("Start Training and Testing the Model...", flush=True)
READ_PATH = os.path.join(os.path.dirname(os.path.abspath("")[:-3]), "app/lib/processed/")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath("")), "app/lib/models/")
case_details_demographics = pd.read_csv(READ_PATH + "tidy_data.csv")

# Remove known outliers from the dataset.
case_details_demographics = case_details_demographics[case_details_demographics["state"] != "MI"]
case_details_demographics = case_details_demographics[case_details_demographics["fed_penalty_assessed_amt"] < 1000000]

case_details_demographics_subset = case_details_demographics
# TODO: Possibly remove this subset.
case_details_demographics_subset = case_details_demographics.sample(frac=0.1, random_state=42)
label_encoder = LabelEncoder()

case_details_demographics_subset["state"] = label_encoder.fit_transform(case_details_demographics_subset["state"])
encoded_to_original = dict(zip(case_details_demographics_subset["state"], case_details_demographics_subset["state"]))
original_to_encoded = {v: k for k, v in encoded_to_original.items()}

X = case_details_demographics_subset[["black_population_ratio", "white_population_ratio", "hispanic_population_ratio", "asian_population_ratio", "american_indian_population_ratio", "low_income_ratio", "state"]]
y = case_details_demographics_subset["fed_penalty_assessed_amt"]
columns = X.columns

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create base estimator. This is the model that will be used to train the BaggingRegressor.
base_estimator = RandomForestRegressor(n_estimators=10, random_state=42)

# TODO: Add param tuning of base estimator.

# Create the BaggingRegressor using the base estimator
bagging_model = BaggingRegressor(estimator=base_estimator, n_estimators=10, random_state=42)

# Fit the BaggingRegressor to the training data
bagging_model.fit(X_train, y_train)

# Make predictions on the test set using the BaggingRegressor
bagging_y_pred = bagging_model.predict(X_test)

# Evaluate the model using mean squared error
mse_bagging = mean_squared_error(y_test, bagging_y_pred)
print(f"Mean Squared Error (Bagging): {mse_bagging}", flush=True)

# Calculate R-squared (Coefficient of Determination)
r2_bagging = r2_score(y_test, bagging_y_pred)
print(f"R-squared (Coefficient of Determination): {r2_bagging}", flush=True)

# Calculate Mean Absolute Error (MAE)
mae_bagging = mean_absolute_error(y_test, bagging_y_pred)
print(f"Mean Absolute Error (Bagging): {mae_bagging}", flush=True)

# TODO: Add versioning of models.
pickle.dump(bagging_model, open(MODEL_PATH + "rf_model.pkl", "wb"))
pickle.dump(bagging_model, open(MODEL_PATH + f"rf_model_{DT.year}{DT.month}{DT.day}.pkl", "wb"))
print("Completed Training: Model Saved to lib/models/", flush=True)
