# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 14:09:28 2024

@author: micah
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.optimize import curve_fit

# Define the die diameters in inches
die_diameters = np.array([1/16, 1/8, 3/16, 1/4, 5/16, 3/8, 7/16, 1/2, 9/16, 5/8, 11/16, 3/4, 13/16])

# Function to calculate the area of a circle
def circle_area(diameter):
    radius = diameter / 2
    return np.pi * (radius ** 2)

# Function to calculate the area of a segment
def segment_area(radius, angle_deg):
    angle_rad = np.deg2rad(angle_deg)
    return (radius**2 / 2) * (angle_rad - np.sin(angle_rad))

# Calculate the area of each die
die_areas = circle_area(die_diameters)

# 13/16 inch die information
main_die_diameter = 13/16
main_die_radius = main_die_diameter / 2

# Calculate the minor segment area for each angle from 0 to 180 degrees
angles = np.linspace(0, 180, 181)
minor_segment_areas = [segment_area(main_die_radius, angle) for angle in angles]

# Double the minor segment area to get the oval area
oval_areas = [2 * area for area in minor_segment_areas]

# Data for the final DataFrame
data = {
    'Die Diameter (in)': die_diameters,
    'Die Area (sq in)': die_areas
}

# Compare the die areas with the oval areas and find the indexing
indexing_deg = []
indexing_mm = []
for die_area in die_areas:
    closest_index = np.argmin(np.abs(np.array(oval_areas) - die_area))
    required_angle = angles[closest_index]
    required_distance_mm = main_die_radius * (1 - np.cos(np.deg2rad(required_angle / 2))) * 25.4  # Convert inches to mm
    indexing_deg.append(required_angle)
    indexing_mm.append(required_distance_mm)

data['Indexing for 13/16 Die (deg)'] = indexing_deg
data['Indexing for 13/16 Die (mm)'] = indexing_mm
data['Minor Segment Area (sq in)'] = [minor_segment_areas[np.argmin(np.abs(np.array(oval_areas) - area))] for area in die_areas]
data['Oval Area (sq in)'] = [oval_areas[np.argmin(np.abs(np.array(oval_areas) - area))] for area in die_areas]

# Create the DataFrame
df = pd.DataFrame(data)

# Polynomial regression to find the best fitting polynomial line
X = (die_diameters * 25.4).reshape(-1, 1)  # Convert diameters to mm
y = np.array(indexing_mm)

poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)
model_poly = LinearRegression()
model_poly.fit(X_poly, y)

# Polynomial equation
poly_coefficients = model_poly.coef_
poly_intercept = model_poly.intercept_
poly_equation = f"Indexing (mm) = {poly_coefficients[2]:.4f} * Die Diameter^2 (mm) + {poly_coefficients[1]:.4f} * Die Diameter (mm) + {poly_intercept:.4f}"

# Exponential function
def exp_func(x, a, b, c):
    return a * np.exp(b * x) + c

# Exponential regression to find the best fitting exponential line
params, _ = curve_fit(exp_func, X.flatten(), y)
a, b, c = params
exp_equation = f"Indexing (mm) = {a:.4f} * exp({b:.4f} * Die Diameter (mm)) + {c:.4f}"

# Plot the data and the best fitting lines
plt.figure(figsize=(10, 6))
plt.scatter(X, y, color='blue', label='Data points')

# Plot polynomial regression line
X_fit = np.linspace(min(X), max(X), 100)
y_poly_fit = model_poly.predict(poly.fit_transform(X_fit))
plt.plot(X_fit, y_poly_fit, color='red', label=f'Polynomial fit\n{poly_equation}')

# Plot exponential regression line
y_exp_fit = exp_func(X_fit, a, b, c)
plt.plot(X_fit, y_exp_fit, color='green', label=f'Exponential fit\n{exp_equation}')

plt.xlabel('Die Diameter (mm)')
plt.ylabel('Indexing for 13/16 Die (mm)')
plt.title('Indexing vs Die Diameter')
plt.legend()
plt.grid(True)
plt.show()

# Determine the best fit
# Calculate the R-squared value for polynomial and exponential fits
r2_poly = model_poly.score(X_poly, y)
y_exp_pred = exp_func(X.flatten(), a, b, c)
ss_res_exp = np.sum((y - y_exp_pred) ** 2)
ss_tot_exp = np.sum((y - np.mean(y)) ** 2)
r2_exp = 1 - (ss_res_exp / ss_tot_exp)

best_fit = "Polynomial" if r2_poly > r2_exp else "Exponential"
best_equation = poly_equation if best_fit == "Polynomial" else exp_equation

# Save the Excel file
file_path = r"C:\Users\micah\OneDrive\Documents\Msstate_grad_project\Testing_Information\Die_Info1.xlsx"
key_info = [
    "This sheet contains information about different die sizes and their corresponding areas.",
    "It also provides the indexing values needed to use a 13/16 inch diameter die to achieve equivalent areas as other die sizes.",
    "The indexing values are calculated based on the ratio of the areas of the target die size to the 13/16 inch die.",
    "Additionally, it compares the area of each die with the total area of the oval shape created by cutting one segment from a folded piece of paper.",
    "The 'Indexing for 13/16 Die (mm)' column provides the exact distance in millimeters to move the die from the outer edge towards the center to achieve the equivalent die area using the oval area data.",
    f"The best fitting line equation is: {best_equation}"
]

with pd.ExcelWriter(file_path) as writer:
    df.to_excel(writer, index=False, sheet_name='Die Information')
    pd.DataFrame({'Key': key_info}).to_excel(writer, index=False, sheet_name='Key')














