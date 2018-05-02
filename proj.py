#!/usr/bin/env python3

####################################################################
# FILE DESCRIPTION
####################################################################
# CSCI 7000 Final Project
# Authors: Brian Lubars, Josh Ladd
#  4/30/2018
# ------------------------------------------------------------------
# DELEGABILITY CLASSIFIER

####################################################################
#  IMPORTS
####################################################################
from math import log, exp
from collections import OrderedDict
import csv
import random
from html.parser import HTMLParser
import queue
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.preprocessing import StandardScaler, LabelBinarizer
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn import tree
from sklearn.metrics import accuracy_score

import graphviz

####################################################################
# VARIABLES AND CONSTANTS
####################################################################
random.seed(12)

FILE_PATH = "./data/data-may-1-18.csv"
OUTFILE_PATH = "./data/cleaned-may-1-18.csv"

####################################################################
#  FUNCTION DEFINITIONS
####################################################################

delegability_map = {
    3 : 'No Delegation',
    2 : 'Human Control, Machine Advice',
    1 : 'Complete Delegation'
}

question_map = {
    'factors' : 'Q8',
    'delegate' : 'Q10',
    'why-delegate' : 'Q11',
    'why-not-delegate' : 'Q12',
    'trust-delegate' : 'Q13'
}

factor_list = [
    'importance',
    'difficulty',
    'self-efficacy',
    'intrinsic-motivation',
    'accountability',
    'goal-mastery-orientation'
]

task_list = [
    'Writing a short story for fun.',
    'Finding and choosing a new roomate.',
    'Buying art for your home.',
    'Paying your bills.',
    'Voting in a federal election.',
    'Writing a birthday card to one of your parents.',
    "Chatting with a local in a foreign country where you don't speak the language.",
    'Picking a movie to watch with a group of friends.',
    'Writing your wedding vows.',
    'Drawing or painting something meaningful to you.',
    'Deciding what people to invite to a party.',
    'Driving to work.',
    'Buying a house.',
    'Driving a family member to the hospital during a medical emergency.',
    'Finding and scheduling events for you to attend in your free time.',
    'Planning a holiday party at work.',
    'Creating a personal nutrition plan and tracking your diet.',
    'Breaking up with your romantic partner.',
    'Finding and picking a new roommate.',
    "Diagnosing and repairing your car's engine problems.",
    'Doing your taxes.',
    'Managing all your finances and investments.',
    'Planning and booking a weekend vacation: destination, travel, accommodations, events.',
    'Deciding and ordering food for dinner.',
    'Texting a joke to a friend.',
    'Cleaning your house.',
    'Filling out and submitting a job application.',
    'Serving on jury duty and deciding if a defendant is guilty.',
    'Reading a novel.',
    'Answering emails from customers at your job.'
]

task_map = OrderedDict()
for i, task in enumerate(task_list):
    task_map[task] = i + 1
factor_map = OrderedDict()
for i, factor in enumerate(factor_list):
    factor_map[factor] = i + 1

#inv_task_map = invert_map(task_map)

def invert_map(d):
    newd = {}
    for k,v in d.items():
        newd[v] = k
    return newd

class HTMLStripper(HTMLParser):
    def __init__(self, queue):
        super().__init__()
        self.q = queue

    def handle_data(self, data):
        self.q.put(data)

class DataLoader:
    def __init__(self, fpath):
        self.fpath = fpath
        self.q = queue.Queue()
        self.html = HTMLStripper(self.q)
        return

    def group_by_task(self, data, task):
        ''' average info across task '''
        # TODO: do statstical analysis by task?
        # group data by task instead of by subject
        task_data = []
        for subject in data:
            for task_answer in subject:
                if task_answer["task"] == task:
                    task_data.append(task_answer)
        return task_data

    def vectorize_item(self, item):
        # vectorize a single subject-task data item
        a = []
        for factor in factor_map.keys():
            a.append(int(item[factor]))
        # last element is delegability
        a.append(int(item['delegate']))
        a.append(int(item['trust-delegate']))
        return a

    def vectorize(self, data):
        ''' turn data array into a feature vector, organized
            by task (each row is a task)  '''
        # first element of X is the task ID (task-map)
        num_features = len(factor_map)
        num_examples = len(task_map)
        X = []
        y = []
        metadata = []
        trust = []
        # group by task, then collapse factors across task
        # such that we have one feature vector per class
        for i, task in enumerate(task_map.keys()):
            task_id = task_map[task]
            task_data = self.group_by_task(data, task)
            a = []
            for j, item in enumerate(task_data):
                a.append(self.vectorize_item(item))
            if len(a) == 0:
                # no data for this task??
                print("No data for '{}'".format(task))
                continue
            # summarize task data
            avg_task_data = np.mean(np.array(a), axis=0)
            X.append(avg_task_data[0:num_features])
            y.append(avg_task_data[num_features])
            metadata.append({'task_id': task_id, 'num_resp': len(a)})
            trust.append(avg_task_data[num_features + 1])
        return np.array(X), np.array(y), metadata

    def read_csv(self):
        data = []
        with open(self.fpath) as csvfile:
            reader = csv.DictReader(csvfile)
            for i,row in enumerate(reader):
                if i <= 1:
                    continue
                row_data = self.parse_row(row)
                data.append(row_data)
        return data

    def parse_row(self, row):
        tasks = []
        for ti in range(7):
            task_dict = self.parse_task(row, ti)
            tasks.append(task_dict)
        return tasks

    def get_cell_id(self, question, task=None, factor=None):
        # get number for task:
        tag = ""
        q = question_map[question]
        if question == 'factors':
            t = task_map[task]
            f = factor_map[factor]
            tag = str(t) + '_' + q + '_' + str(f)
        elif 'delegate' in question:
            tag = str(task) + '_' + q
        if tag == "":
            print("ERROR: bad cell id")
        return tag

    def parse_task(self, row, task_num):
        d = {}
        # task text
        self.html.feed(row['task' + str(task_num)])
        task = self.q.get(block=True)
        d['task'] = task.strip()
        # task factors:
        for factor in factor_map.keys():
            tag = self.get_cell_id('factors', task, factor)
            d[factor] = row[tag]
        for q in ['delegate', 'why-delegate', 'why-not-delegate', 'trust-delegate']:
            tag = self.get_cell_id(q, task_num+1)
            d[q] = row[tag]
        return d

    def write_csv(self, data):
        with open(OUTFILE_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Subject", "Task", "Task id", "Delegability", "Trust", 
                             'Importance', 'Difficulty', 'Self-efficacy', 'Intrinsic-motivation', 
                             'Accountability', 'Goal-mastery-orientation', 'Why delegate?', 'Why not delegate?'])
            for subj_id, subj in enumerate(data):
                for task in subj:
                    info = [
                        subj_id, task['task'], task_map[task['task']], 
                        task['delegate'], task['trust-delegate'], 
                        task['importance'], task['difficulty'], task['self-efficacy'],
                        task['intrinsic-motivation'], task['accountability'], task['goal-mastery-orientation'],
                        task['why-delegate'], task['why-not-delegate']
                    ]
                    writer.writerow(info)


class TaskPlotter:
    def __init__(self, DataLoader):
        self.dl = DataLoader

    def plot_task(self):
        return

def graph_vis(model, feature_names, class_names):
    dot_data = tree.export_graphviz(model, out_file=None, 
                             feature_names=feature_names,
                             class_names=class_names,
                             filled=True, rounded=True,  
                             special_characters=True)  
    graph = graphviz.Source(dot_data)  
    graph.render("tree")

####################################################################
#  MAIN
###################################################################
if __name__ == "__main__":
    dl = DataLoader(FILE_PATH)
    raw_data = dl.read_csv()
    X, Y, metadata = dl.vectorize(raw_data)
    #print(X)
    #print(Y)
    #for d in metadata:
    #    print(d)
    #dl.write_csv(raw_data)

    # round the labels to discrete values
    discrete_y = np.around(Y)

    if 0:
        labels = [delegability_map[label] for label in discrete_y]
        # scatterplot matrix
        import pandas as pd
        import seaborn as sns
        sns.set(style="ticks")
        df1 = pd.DataFrame(X, columns=factor_list)
        df2 = pd.DataFrame(labels, columns=["labels"])
        df = pd.concat([df1, df2], axis=1)
        print(df)
        graph = sns.pairplot(df, hue="labels") #kind="reg", 
        plt.show()


    # plot the data
    if 0:
        if 0:
            # run PCA/dim reduction
            pca = PCA(n_components=2)
            X = StandardScaler().fit_transform(X)
            X_r = pca.fit_transform(X)
            print("Explained variance ratio (1st 2 components): {}".format(pca.explained_variance_ratio_))
        elif 0:
            lda = LinearDiscriminantAnalysis(n_components=2)
            X = StandardScaler().fit_transform(X,)
            X_r = lda.fit_transform(X, discrete_y)
        else:
            X_r = np.zeros((X.shape[0], 2))
            X_r[:,0] = X[:,0]
            X_r[:,1] = X[:,3]
            plt.title("Delegability: Importance vs Intrinsic Motivation")
            plt.xlabel("Importance")
            plt.ylabel("Intrinsic Motivation")
        colors = ['b', 'g', 'r']
        for i, label in delegability_map.items():
            #print("{}, {}".format(i, label))
            c = colors[i-1]
            plt.scatter(X_r[discrete_y == i, 0], X_r[discrete_y == i, 1], color=c, alpha=0.8, label=label)
        plt.legend()


        #for m, x, y in zip(metadata, X_r[:, 0], X_r[:, 1]):
        #    text = task_list[m['task_id'] - 1]
            #text = str(m['task_id'])
        #    plt.annotate(text, xy=(x, y), xytext=(-50, 10), textcoords='offset points')

        plt.show()
        #labels = [delegability_map]

    if 0:
        deleg_y = np.copy(discrete_y)
        for i,v in enumerate(deleg_y):
            #if v == 3: # NO delegation == 3
            if v == 1: # delegation == 1
                deleg_y[i] = 1
            else:
                deleg_y[i] = 0

        # tree for DELEGATING
        X_train, X_test, y_train, y_test, m_train, m_test = train_test_split(X, deleg_y, metadata, test_size=0.4, random_state=0)
        print("Train:")
        print(y_train)
        print("Test:")
        print(y_test)
        m1 = tree.DecisionTreeClassifier(max_depth=6, class_weight="balanced")
        m1.fit(X_train, y_train)
        y_pred1 = m1.predict(X_test)
        print("Pred:")
        print(y_pred1)
        print("Accuracy, Dec Tree Depth {}: {}".format(3, accuracy_score(y_test, y_pred1)))
        for x,yt,yp,meta in zip(X_test, y_test, y_pred1, m_test):
            print("Task[{}]: {}: Prediction: {} Actual: {}, Features:{}".format(meta['task_id'], task_list[meta['task_id'] - 1], yp, yt, x))
            print(m1.decision_path([x]))

        print("FEATURE IMPORTANCES:")
        print(m1.feature_importances_)
        print("TREE:")
        graph_vis(m1, factor_list, ["Full/Partial Automation", "Human Only"])
        # print decision tree:

    if 0:
        #for i,v in enumerate(discrete_y):
        #    if v != 1:
        #        discrete_y[i] = 0

        lb = LabelBinarizer()
        bin_y = lb.fit_transform(discrete_y)
        X_train, X_test, y_train, y_test = train_test_split(X, bin_y, test_size=0.4, random_state=0)

        print("Train:")
        print(y_train)
        print("Test:")
        print(y_test)
        m1 = tree.DecisionTreeClassifier(max_depth=2)
        m2 = tree.DecisionTreeClassifier(max_depth=3)
        m1.fit(X_train, y_train)
        m2.fit(X_train, y_train)
        y_pred1 = m1.predict(X_test)
        y_pred2 = m2.predict(X_test)
        print("Pred, depth 2:")
        print(y_pred1)
        print("Pred, depth 3:")
        print(y_pred2)
        print("Accuracy, Dec Tree Depth {}: {}".format(2, accuracy_score(y_test, y_pred1)))
        print("Accuracy, Dec Tree Depth {}: {}".format(3, accuracy_score(y_test, y_pred2)))

    if 1:
        from sklearn.svm import SVC
        #for i,v in enumerate(discrete_y):
        #    if v != 1:
        #        discrete_y[i] = 0

        #lb = LabelBinarizer()
        #bin_y = lb.fit_transform(discrete_y)
        X_train, X_test, y_train, y_test = train_test_split(X, discrete_y, test_size=0.4, random_state=0)

        print("Train:")
        print(y_train)
        print("Test:")
        print(y_test)
        m1 = SVC()
        m1.fit(X_train, y_train)
        y_pred = m1.predict(X_test)
        print("Pred, depth 2:")
        print(y_pred)
        print("Accuracy, SVM: {}".format(accuracy_score(y_test, y_pred)))




