# Week 6 Meeting Notes

### 1. Call to Order
A meeting was held at 33 Charles St East on 15 October 2022.

### 2. Attendees
* Regan
* Riley
* Jared

### 3. Open Issues
* New format for meeting notes (Regan)
* Determine progress on data cleaning (Riley)
* Determine progress on data visualization (Riley)
* Determine initial machine learning pipeline (Regan)
* Automating docker build and push using github actions (Jared)
* Further discuss changes to user interface (All)

    **1. Data cleaning and visualization**
    * <b>PROGRESS:</b> Completed and will be reviewed by Regan after this meeting to ensure that it is suitable for machine learning algorithms.
    * <b>HIGHLIGHTS:</b> The dataset has to be processed properly, such as handling null values and removing duplicates. As the feature set is small, more features need to be engineered and transformed into sensible features (eg. using one-hot encoding).
    Plotting the feature distributions allows us to identify skewness and outliers. Appropriate techniques (eg. robust scale transformation) can then be used to resolve them.
    Riley presented some of his findings to the team with the visualized data.

    **2. Machine learning pipeline**
    * <b>PROGRESS:</b> In progress
    * <b>HIGHLIGHTS:</b> Regan presented to the team his idea of the machine learning pipeline.
        * Feature selection to remove unnecessary features using a selected machine learning model
        * With the filtered features, determine another regressor to produce the appropriate output
        * Apply an appropriate cross validation algorithm to optimize the features input into this entire pipeline

    **3. Automating docker build and push using github actions**
    * <b>PROGRESS:</b> In progress
    * <b>HIGHLIGHTS:</b> Jared created the github workflow to automate the process of building and pushing the docker images into Docker Hub, triggered by every push on the main branch 

    **4.Review on Features to be implemented (TO DO LIST)**<br />
    <b>Priority Levels</b>
    - I: Top priority, has to be done by the next meeting (should have only one top priority tasks per meeting)
    - II: 