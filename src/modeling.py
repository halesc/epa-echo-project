"""
This module is used to train and test the model. The model is trained using the BaggingRegressor algorithm. This module will also param tune the model. The model is saved to the lib folder.
"""
import os
import pickle
import datetime
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import BaggingRegressor, RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# TODO: Add the ability to select which features to use.
# TODO: Add in automated param tuning. Maybe a button for this in main.py.

DT = datetime.datetime.now()
print("Start Training and Testing the Model...", flush=True)
READ_PATH = os.path.join(os.path.dirname(os.path.abspath("")[:-3]), "../epa-echo-project/lib/processed/")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath("")), "../epa-echo-project/lib/models/")
case_details_demographics = pd.read_csv(READ_PATH + "tidy_data.csv")
case_details_demographics.columns

# Remove outliers.
percentile_10 = case_details_demographics["fed_penalty_assessed_amt"].quantile(0.05)
percentile_90 = case_details_demographics["fed_penalty_assessed_amt"].quantile(0.95)
# Create a new DataFrame without the top and bottom 10% of values
case_details_demographics = case_details_demographics[(case_details_demographics["fed_penalty_assessed_amt"] >= percentile_10) & (case_details_demographics["fed_penalty_assessed_amt"] <= percentile_90)]
case_details_demographics = case_details_demographics[case_details_demographics["county"] != "Oakland"]

label_encoder = LabelEncoder()
case_details_demographics['State'] = label_encoder.fit_transform(case_details_demographics['state'])

case_details_demographics_subset = case_details_demographics.sample(frac=0.1, random_state=42)


encoded_to_original = dict(zip(case_details_demographics_subset['State'], case_details_demographics_subset['state']))
original_to_encoded = {v: k for k, v in encoded_to_original.items()}

X = case_details_demographics_subset[['black_population_ratio', 'white_population_ratio', "hispanic_population_ratio", 'asian_population_ratio', 'american_indian_population_ratio', 'low_income_ratio', 'State']]
y = case_details_demographics_subset["fed_penalty_assessed_amt"]

columns = X.columns
# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create the base estimator - RandomForestRegressor
base_estimator = RandomForestRegressor(n_estimators=200, max_depth=2, max_features=0.6, min_samples_leaf=5, min_samples_split=10, bootstrap=True, random_state=45)

# Create the BaggingRegressor using the base estimator
bagging_model = BaggingRegressor(estimator=base_estimator, n_estimators=10, random_state=45)

# Fit the BaggingRegressor to the training data
bagging_model.fit(X_train, y_train)

# Make predictions on the test set using the BaggingRegressor
bagging_y_pred = bagging_model.predict(X_test)

# Evaluate the model using mean squared error
mse_bagging = mean_squared_error(y_test, bagging_y_pred)

# Calculate R-squared (Coefficient of Determination)
r2_bagging = r2_score(y_test, bagging_y_pred)

# Calculate Mean Absolute Error (MAE)
mae_bagging = mean_absolute_error(y_test, bagging_y_pred)

pickle.dump(bagging_model, open(MODEL_PATH + "rf_model.pkl", "wb"))
pickle.dump(bagging_model, open(MODEL_PATH + f"rf_model_{DT.year}{DT.month}{DT.day}.pkl", "wb"))

# Load the trained model
loaded_model = pickle.load(open(MODEL_PATH + "rf_model.pkl", "rb"))

# Make predictions using the loaded model for each record in the results table
case_details_demographics.columns

result = case_details_demographics

result['predicted_value'] = loaded_model.predict(result[['black_population_ratio', 'white_population_ratio', "hispanic_population_ratio", 'asian_population_ratio', 'american_indian_population_ratio', 'low_income_ratio', 'State']])

# Save the updated DataFrame to a new CSV file
result.to_csv(MODEL_PATH + "tidy_data_with_predictions.csv", index=False)

print("Completed Training: Model Applied to Results Table and Saved to lib/models", flush=True)
print("Completed Training: Model Saved to lib/models/", flush=True)
