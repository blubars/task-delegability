#!/usr/bin/env python3

#---------------------------------------------------------
# FILE DESCRIPTION:
#---------------------------------------------------------
# Run statistical analysis on results from survey

#---------------------------------------------------------
# IMPORTS
#---------------------------------------------------------
import sys
import os.path
import csv
import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np
import seaborn as sns
#import matplotlib.pyplot as plt

#---------------------------------------------------------
# GLOBALS
#---------------------------------------------------------
CSV_FILE_IN = None

gender_categories = ["male", "female", "other", "blank"]
age_categories = ["18-25", "26-35", "36-45", "46-55", "56-65", "66-75", "76 or older", "blank"]

#---------------------------------------------------------
# SCRIPT 
#---------------------------------------------------------

def plot_cat_hist(series, title):
    #df['gender'].value_counts().plot(kind='bar')
    sns.countplot(series, color='gray')
    plt.savefig(title)
    #plt.close(fig)
    
def plot_hist(title):
    bins = np.arange(0,5)
    plt.xlabel('time')
    plt.ylabel(count)
    plt.title(title)
    plt.savefig('hist1')

def main():
    if CSV_FILE_IN is None:
        print("Error: Need to pass in a CSV file to process")
        return
        
    gender_cat_type = CategoricalDtype(categories=gender_categories, ordered=True)
    age_cat_type = CategoricalDtype(categories=age_categories, ordered=True)

    df = pd.read_csv(CSV_FILE_IN)
    
    df['gender'] = df['gender'].astype(gender_cat_type)
    df['age'] = df['age'].astype(age_cat_type)
    gp = df.groupby('HIT id')
    plot_cat_hist(df['age'], "age")
    for name, group in gp:
        # produce little report for each task
        task = group['Annotation'][0]
        print(name)
        print(task)

        #print(group)
        

if __name__ == "__main__":
    main()