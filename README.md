# epa-echo-project
A repo containing a webapp that analyzes the epa echo dataset.

### Setup through Github
1. Clone the repo or download the zip file. Download and install Docker Desktop from https://www.docker.com/products/docker-desktop
![imageAlt text](./lib/images/1_repo.png)

2. Unzip the application into a folder. Navigate there in command prompt / terminal. Then build the application folder aka run the below command in the folder that contains the DockerFile.
```
docker build -t epa-echo-project .

```
![imageAlt text](./lib/images/2_cmd_line.png)

3. Run the image to start the container. Click on the run button on docker desktop.
![imageAlt text](./lib/images/3_image.png)

4. Input the proper optional settings.
![imageAlt text](./lib/images/4_image_setup.png)

5. Run the container. Click at port to open in web browser.
![imageAlt text](./lib/images/5_run_container.png)

And just like that you have the application up and running in a contained environment.

#### Demographic Analysis Description:
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

#### Utilities Description:
There are three buttons here.

The first button is 'Extract Data'. It links to the EPA ECHO website. This is the website where the data was pulled from. This will begin downloading the most up to date data into the /raw/ directory.

The second button is 'Transform Data'. This processes the data so that the models in the application can use it to model. This will create a new file in the /processed/ directory.

Finally there is a button to retrain the demographic model. Note this is usually retrained when the application is opened for the first time. This will create a new file in the /models/ directory.