# LIA-Projekt-STI-26

## Data Pipeline

The data pipeline currently has a new readme inside the folder. Look there for more information about running and using the pipeline

## IMPORTANT NOTE

DO NOT PUSH THESE CHANGES TO THE RASPBERRY PI AS IT WILL OVERWRITE MANUAL COMPATABILITY FIXES!!!

Before pushing anything to the raspberry first do these steps:

    1: Push the current raspberry project to a new branch, for example "raspberry"
    2: Merge any changes you want to implement to the raspberry with the raspberry branch
    3: Solve any conflicts in the merge with a focus on keeping any raspberry compatability changes
    4: Pull the raspberry branch to the raspberry pi and test changes
    5a: If the pipeline works the branch can be merged to main with a title of raspberry patch 'X' to differentiate it from other patches. 
    5b: If it does not work you need to troubleshoot the code. Use the previous working patch as a help. When it is working again push it to the raspberry branch and do 5a.