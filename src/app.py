from flask import Flask, render_template, request, url_for
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

app = Flask(__name__)

# Load the dataset
wine_data = pd.read_csv('wine_data.csv')

# Data Preprocessing
# Separate categorical and numerical features
categorical_features = ['grape_variety', 'region', 'winery']
numerical_features = [col for col in wine_data.columns if col not in ['price'] + categorical_features]

# One-hot encode categorical features with handle_unknown='ignore'
encoder = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
categorical_data = encoder.fit_transform(wine_data[categorical_features])
categorical_df = pd.DataFrame(categorical_data, columns=encoder.get_feature_names_out(categorical_features))

# Combine numerical and encoded categorical features
X = pd.concat([wine_data[numerical_features], categorical_df], axis=1)
y = wine_data['price']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Model Evaluation
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

if len(y_test) >= 2:
    print("Mean Squared Error:", mse)
    print("R-squared:", r2)
else:
    print("Insufficient data to calculate R-squared. Please ensure you have at least two samples in the testing set.")


# Home page - render the form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_data = {
            'grape_variety': [request.form['grape_variety']],
            'region': [request.form['region']],
            'vintage': [int(request.form['vintage'])],  # Convert to int
            'rating': [float(request.form['rating'])],  # Convert to float
            'winery': [request.form['winery']]
        }

        # One-hot encode the categorical features for the new data
        categorical_data_new = encoder.transform(pd.DataFrame(new_data)[categorical_features])
        categorical_df_new = pd.DataFrame(categorical_data_new, columns=encoder.get_feature_names_out(categorical_features))

        # Combine numerical and encoded categorical features for the new data
        new_data_encoded = pd.concat([pd.DataFrame(new_data)[numerical_features], categorical_df_new], axis=1)

        # Make predictions for the new wine bottle
        predicted_price = model.predict(new_data_encoded)

        # Reshape the predicted_price to get a single value
        predicted_price = predicted_price[0]

        print("Predicted Price:", predicted_price)

        return render_template('index.html', predicted_price=predicted_price)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
