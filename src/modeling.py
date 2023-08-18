"""

"""

import pickle
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder

# Predicting FED_PENALTY
# Assign the independent variables (X) and the dependent variable (y)


case_details_demographics = pd.read_csv('case_details_demographics.csv')
case_details_demographics_subset = case_details_demographics.sample(frac=0.1, random_state=42)
label_encoder = LabelEncoder()

case_details_demographics_subset['state'] = label_encoder.fit_transform(case_details_demographics_subset['state'])
encoded_to_original = dict(zip(case_details_demographics_subset['state'], case_details_demographics_subset['state']))
original_to_encoded = {v: k for k, v in encoded_to_original.items()}

X = case_details_demographics_subset[['black_population_ratio', 'white_population_ratio', "hispanic_population_ratio", 'asian_population_ratio', 'american_indian_population_ratio', 'low_income_ratio', 'state']]
y = case_details_demographics_subset['fed_penalty_assessed_amt']


# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create the random forest regression model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

# Fit the model to the training data
rf_model.fit(X_train, y_train)

# Make predictions on the test set
rf_y_pred = rf_model.predict(X_test)

# Evaluate the model using mean squared error
mse = mean_squared_error(y_test, rf_y_pred)
print('Mean Squared Error:', mse)


my_dict = {
    "black_population_ratio": .1,
    "white_population_ratio": .8,
    "low_income_ratio": .3,
    "state": original_to_encoded.get('WA')
}
df = pd.DataFrame.from_dict([my_dict])
model_rf = pickle.dump(rf_model, open("rf_model.pkl", "wb"))
columns = X.columns
df = pd.get_dummies(df).reindex(columns=columns, fill_value=0)
