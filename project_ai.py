# -*- coding: utf-8 -*-
"""Project_AI

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Lfik-0lMUPDyvicVov68hRZUvFR5hcPg

Last Updated: 11/15/2023

TODO: add in error checking

TODO: change a_factor calc

TODO: add in default equipment values

TODO: add in standard scaler (?)

Implementation

* ask for BMI calculation
* ask for equipment available
* ask for experience level

Generate gym split based on criteria above
"""

import requests
import json
import csv
import pandas as pd
import sklearn

"""# Collecting Data From API
* collecting and cleaning ( through pandas )
"""

# Define the API URL
base_url = 'https://api.api-ninjas.com/v1/exercises'

api_key = 'b+5JS9PpABz0ysJEdtrRsQ==dJ7AslezF3lZbWAw'

# Create a list to store all the exercise data
all_exercises = []

# Set the initial offset to 0
offset = 0

while True:
    # Define the parameters for the request
    params = {
        'offset': offset
    }

    # Set the API key in the headers
    headers = {
        'X-Api-Key': api_key
    }

    # Send a GET request to the API
    response = requests.get(base_url, params=params, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()

        if data:
          for i in data:
            all_exercises.append(i)
        else:
          break

        # Increment the offset to fetch the next page
        offset += len(data)
    else:
        print("Failed to retrieve data from the API. Status code:", response.status_code)
        break

print(f"Total exercises retrieved: {len(all_exercises)}")

# Importing all of the data into a CSV File
import csv

csv_file = 'exercises.csv'

with open(csv_file, 'w', newline='') as csvfile:
    fieldnames = all_exercises[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(all_exercises)

"""**Cleaning Data**
* using pandas dataframe
"""

#converting the data into a dataframe
exercise_data = pd.read_csv('exercises.csv')

# cleaning up leading and trailing white space in instructions
exercise_data['instructions'] = exercise_data['instructions'].str.strip()

# filling in missing values with 0
exercise_data.fillna(0, inplace=True)

cleaned_data = exercise_data.copy()

"""#User Profile

* TODO: add in user.goal (lose, maintain, gain)
"""

class User:

  def __init__(self, name, age, weight, activity_level, height, sex, exp_level, equipment):
    self.name = name
    self.sex = sex
    self.age = age

    self.activity_level = activity_level
    self.ac_factor = self.activity_factor(activity_level)

    self.weight = self.weight_conv(weight)
    self.height = self.height_conv(height)

    self.exp_level = exp_level

    self.equipment = equipment.replace(" ", "").split(',')

    self.goal = 0 # default value

  def weight_conv(self, weight):
    return weight * 0.453592

  def height_conv(self, height):
    feet, inches = map(int, height.split(','))
    total_inches = feet * 12 + inches
    return total_inches * 2.54

  def activity_factor(self, activity_level):
    activity_factors = {
      1: 1.2,
      2: 1.375,
      3: 1.55,
      4: 1.725,
      5: 1.9
    }

    # getting activity factor
    a_factor = [val for key, val in activity_factors.items() if activity_level == key]
    a_factor = a_factor[0]

    return a_factor

  def set_goal(self, new_goal):
    self.goal = new_goal

name = input('Please enter your name: ')
age = int(input('Please enter your age: '))
weight = float(input('Please enter your weight in lbs: '))
height = input('Please enter your height in feet,inches (EX: 5\'2" = 5,2 ): ' )
sex = input('Enter your gender (M or F):').lower()
exp_level = int(input('Please enter your experience level: (1. Beginner, 2. Intermediate, 3. Experienced)'))
equipment = input('Please enter the equipment available to you: ')

print('\nGUIDE\n1. Sedentary\n2. Lightly Active\n3. Moderately Active\n4. Very Active\n5. Super Active')
activity_level = int(input('Enter your activity level (# corresponding to your level): '))

MyUser = User(name, age, weight, activity_level, height, sex, exp_level, equipment)

"""# TDEE & BMI Calculation"""

def tdee_calculation(weight_kg, height, age, a_factor, sex):

  # calculating based on gender
  if sex == 'm':
    bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height) - (5.677 * age)
    #bmr = (10 * weight_kg) + (6.25 * height) - (5 * age) + 5
  elif sex == 'f':
    bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height) - (4.330 * age)


  return bmr * a_factor

def tdee_results(w, h, a, a_l, s):

  tdee = tdee_calculation(w, h, a, a_l, s)

  print('TDEE RESULTS')
  print(f'  Maintain Weight:\t{tdee:.2f} calories/day')
  print(f'  Mild Weight Loss:\t{(tdee*0.9):.2f} calories/day')
  print(f'  Weight Loss:\t\t{(tdee*0.8):.2f} calories/day')
  print(f'  Extreme Weight Loss:\t{(tdee*0.6):.2f} calories/day\n\n')

def bmi_calculation(weight, height):
  height = height / 100
  height_calc = pow(height, 2)
  return weight / height_calc

def bmi_results(weight, height):

  bmi = bmi_calculation(weight, height)

  print(f'BMI RESULTS\n  bmi: {bmi:.2f}\t', end='')
  if bmi < 18.5:
      print('Underweight')
  elif 18.5 <= bmi < 24.9:
      print('Normal (Healthy) Weight')
  elif 25.0 <= bmi < 29.9:
      print('Overweight')
  elif bmi >= 30.0:
      print('Obese')

tdee_results(MyUser.weight, MyUser.height, MyUser.age, MyUser.ac_factor, MyUser.sex)
bmi_results(MyUser.weight, MyUser.height)

goal = int(input('Based on the above results, what is your goal? (1. Lose, 2. Maintain, 3. Gain) '))
MyUser.set_goal(goal)

"""#RandomForestClassifier/Regressor

* classifier: predicts whether workout reccommended (1: yes 0: no)

* regressor: predicts # of days user should train
"""

# assigning numerical representation for difficulty  levels:
# adding new column called 'Difficulty Mapping'

difficulty_mapping = {'beginner':1, 'intermediate':2, 'expert':3}
diff_numbered = cleaned_data['difficulty'].map(difficulty_mapping)
cleaned_data['Difficulty Mapping'] = diff_numbered


# creating subsets for each experience level
beginner_data = cleaned_data[cleaned_data['Difficulty Mapping'] == 1]
intermediate_data = cleaned_data[cleaned_data['Difficulty Mapping'] == 2]
advanced_data = cleaned_data[cleaned_data['Difficulty Mapping'] == 3]

'''
Testing with User
 with following equipment and experience level

EXPERIENCE: 2
EQUIPMENT: dumbbell, body_only, none, exercise_ball, None, other

'''

def is_recommended(row):

  if row['equipment'] in MyUser.equipment and row['Difficulty Mapping'] <= MyUser.exp_level:
    return 1
  else:
    return 0

cleaned_data['Recommended'] = cleaned_data.apply(is_recommended, axis=1)

"""Prediction: Specific Workout Based on User Input"""

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

#data_encoded = pd.get_dummies(cleaned_data[['type', 'muscle', 'equipment', 'difficulty']])
data_encoded = pd.get_dummies(cleaned_data[['type', 'equipment', 'difficulty']])
df_final = pd.concat([cleaned_data[['name']], data_encoded], axis=1)

# Recommended = target variable
df_final['Recommended'] = cleaned_data['Recommended']


# splitting dataset into training and testing sets

x_train, x_test, y_train, y_test = train_test_split(
    df_final.drop(['name', 'Recommended'], axis=1),
    df_final['Recommended'],
    test_size = 0.4,
    random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(x_train, y_train)

predictions = model.predict(x_test)
accuracy = accuracy_score(y_test, predictions)
print(f'Model Accuracy: {accuracy}')



user_data = {'type': 'strength',
             'equipment': MyUser.equipment,
             'difficulty': MyUser.exp_level}

# Create a DataFrame with the user data
user_data_df = pd.DataFrame([user_data])

# Extract the list of equipment
user_equipment_list = user_data_df['equipment'].iloc[0]

# Create binary columns for each unique equipment type
for equipment_type in set(user_equipment_list):
    user_data_df[f'equipment_{equipment_type}'] = user_data_df['equipment'].apply(lambda x: 1 if equipment_type in x else 0)

# Drop the original 'equipment' column
user_data_df = user_data_df.drop('equipment', axis=1)


# Fill NaN values with 0
user_data_df = user_data_df.fillna(0)
user_data_df = user_data_df.reindex(columns=x_train.columns, fill_value=0)
predictions_new = model.predict(user_data_df)

print(f'Recommended Exercises for New User: {predictions_new}')

"""Prediction: # of Days to Train Based on User Data

TODO: add in goal into the prediction model
"""

'''
make a replica of the code above but instead do it for the user profile with the
bmi and tdee and train it on difference users and have it predict that amount of days
they would have to train
'''

import random

def generate_random_user(count):
  age = random.randint(16, 80)
  weight = random.uniform(50, 100)
  activity_levels = [1,2,3,4,5]
  activity_level = random.choice(activity_levels)
  height = random.uniform(150,190)
  sex = random.choice(['m', 'f'])

  activity_factors = {
      1: 1.2,
      2: 1.375,
      3: 1.55,
      4: 1.725,
      5: 1.9
  }

  # getting activity factor
  a_factor = activity_factors.get(activity_level)
  tdee = tdee_calculation(weight, height, age, a_factor, sex)
  bmi = bmi_calculation(weight, height)

  recc = 5 # default recc value
  if age > 50 and bmi >= 25:
    recc = random.choice([3,4,5])
  elif age > 50 and (bmi >= 18.5 and bmi < 25):
    recc = random.choice([4,5])
  elif (age <= 50 and age >= 40) and bmi >= 25:
    recc = random.choice([4,5])
  elif (age <= 50 and age >= 40) and (bmi >= 18.5 and bmi < 25):
    recc = random.choice([5,6])
  elif age < 40 and bmi >= 25:
    recc = random.choice([5, 6])
  elif age < 40 and (bmi >= 18.5 and bmi < 25):
    recc = random.choice([4, 5, 6])


  user = {
      'ID': count,
      'age': age,
      'weight': weight,
      'activity_level': activity_level,
      'activity_factor': a_factor,
      'height': height,
      'sex': sex,
      'tdee': tdee,
      'bmi': bmi,
      'reccomendation': recc
  }

  return user

random_users = {f'Person{i}': generate_random_user(i) for i in range(1, 201)}

# used to check random_user data for correctness
#for person_id, user_data in list(random_users.items())[:20]:
#  print(f'{person_id}: {user_data}')

random_users_df = pd.DataFrame.from_dict(random_users, orient='index')
print(random_users_df.columns)

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


data_encoded_users = pd.get_dummies(random_users_df[['age', 'weight', 'activity_level','activity_factor','height','sex','tdee','bmi']])
df_final_users = pd.concat([random_users_df[['ID']], data_encoded_users], axis=1)

# Recommended = target variable
df_final_users['reccomendation'] = random_users_df['reccomendation']


# splitting dataset into training and testing sets

x_train, x_test, y_train, y_test = train_test_split(
    df_final_users.drop(['ID', 'reccomendation'], axis=1),
    df_final_users['reccomendation'],
    test_size = 0.25,
    random_state=42
)

regressor = RandomForestRegressor(n_estimators=100, random_state=42)
regressor.fit(x_train, y_train)

predictions = regressor.predict(x_test)
mse = mean_squared_error(y_test, predictions)
print(f'Mean Squared Error: {mse}')

new_user_data = {
    'ID': 202,
    'age': MyUser.age,
    'weight': MyUser.weight,
    'activity_level': MyUser.activity_level,
    'activity_factor': MyUser.ac_factor,
    'height': MyUser.height,
    'sex': MyUser.sex,
    'tdee': 2373.63,
    'bmi': 27.46
}

new_user_data_df = pd.DataFrame([new_user_data])
new_user_data_encoded =  pd.get_dummies(new_user_data_df[['age', 'weight', 'activity_level', 'activity_factor', 'height', 'sex', 'tdee', 'bmi']])
missing_columns = set(x_train.columns) - set(new_user_data_encoded.columns)
for column in missing_columns:
    new_user_data_encoded[column] = 0

prediction_new_user = regressor.predict(new_user_data_encoded)
prediction_new_user = round(prediction_new_user[0])
print(f'Predicted Number of Days for New User: {prediction_new_user}')

"""#Workout Generator

Data Preparation
"""

#weekly schedule dict

weekly_schedule = {'Monday': [],
                   'Tuesday': [],
                   'Wednesday': [],
                   'Thursday': [],
                   'Friday':[],
                   'Saturday': [],
                   'Sunday':[] }

# extracing equipment available and difficulty level correlated to user from df

user_specific_df = cleaned_data.loc[
    (cleaned_data['Difficulty Mapping'] == MyUser.exp_level) &
    cleaned_data['equipment'].isin(MyUser.equipment)
]
print(user_specific_df)


# print(cleaned_data['muscle'].unique())

# create dict to map to general areas of body
muscle_mapping = {
    'Lower Body': ['quadriceps', 'abductors', 'hamstrings', 'glutes', 'calves', 'adductors'],
    'Upper Body': ['lats', 'middle_back', 'lower_back', 'shoulders', 'forearms', 'triceps', 'chest', 'biceps', 'traps', 'neck', 'abdominals']
}

def cardio_amount(prediction_new_user, goal):

  # if working out for 1-2 days then do cardio both days
  if prediction_new_user <= 2:
    return prediction_new_user

  # if goal is to lose weight then cardio every day
  if goal == 1:
    return prediction_new_user
  else:
    if prediction_new_user == 3:
      return prediction_new_user - 1
    elif prediction_new_user == 4 or prediction_new_user == 5:
      return prediction_new_user - 2
    elif prediction_new_user == 6:
      return prediction_new_user -3






def workout_generator(prediction_new_user, equipment, exp_level):
  cardio_days = cardio_amount(prediction_new_user, MyUser.goal)