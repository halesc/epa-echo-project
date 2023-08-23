# epa-echo-project
A repo containing a webapp that analyzes the epa echo dataset.

#### Description:
The demographic web app is designed to show the impact of the population on penalty amounts and frequencies.
It is broken into 3 separate sections - the first part uses linear modeling to look at the relationship of  penalty amounts and frequencies based on different racial populations. The second section is similar to the first but looks at the ratio of low income households.
Both of these relationships include coefficients to provide the viewer with a better understanding of the trend. The final section is a penalty estimator which is based on a Random Forest model using the State and demographics as features. The user can input values for the location by US State and the demographic distribution to estimate what the EPA federal penalty could be.

#### Images:
Section 1: Penalty Amount and Frequency Relationship by Racial Populations
![image](https://github.com/Mik-dot/epa-echo-project/assets/58948167/9524bfea-2aec-4ed7-8f52-f48cc37e9d63)

Section 2: Penalty Amount and Frequency Relationship by Low Income Households
![image](https://github.com/Mik-dot/epa-echo-project/assets/58948167/c96e9ec9-327c-4d99-be8e-a1ec268a54aa)

Section 3: EPA Penalty Estimator
![image](https://github.com/Mik-dot/epa-echo-project/assets/58948167/bec37049-37aa-4a1f-acc4-4420d866f091)


#### Geographical Analysis Description: 

The geographical analysis web app allows users to visually interpret and interact with geographical, assessed penalty value, penalty count by statue, demographic and income data.  

It is broken into 2 separate sections –  

The first section allows a user to select a state, county and statute to find an average penalty assessed value by statute chosen. It also produces a visual that shows the demographic race data and income data for the county chosen.  

The second section allows the user to view multiple counties by violation count and penalty assessed value. The user selects the number of counties desired to be analyzed, then enter the county names. 

#### Images: 
Section 1: Penalty Assessed Value Heat Map, Demographic and Income Ratio Data 

![image](./lib/images/image.png)

![image](./lib/images/image-1.png)

Section 2: County Violation Count and Penalty Assessed Value Analysis  

![imageAlt text](./lib/images/image-2.png)