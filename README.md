# teiko-technical
Solution repository for Teiko take home coding assignment

## Relevant links

- [Google form](https://docs.google.com/forms/d/e/1FAIpQLSerNlUUw5B-rqD83aw2U72BLaDP8XTS7AryR_mV1g8VNbupHw/viewform?pli=1)
- [Provided data](https://drive.google.com/file/d/1eMfLCQBIqChy8FVej5yE-9h9UL7oTvVy/view)
- [Ashby HQ link](https://you.ashbyhq.com/teiko/assignment/9075659b-723a-4eaf-9366-43957734f81a)

# Submission Requirements
Please submit your solution as a GitHub repository link.

Your project should include:

- Your Python program with all accompanying files
- Any input or output files generated
- A README.md with:
    - Any instructions needed to run your code and reproduce the outputs (We will run your code using GitHub Codespaces).
    - An explanation of the schema used for the relational database, with rationale for the design and how this would scale if there were hundreds of projects, thousands of samples and various types of analytics you’d want to perform.
    - A brief overview of your code structure and an explanation of why you designed it the way you did.
    - A link to the dashboard.
- A Makefile in the root directory. We will use this to automatically grade your submission using GitHub Codespaces. Your Makefile must implement the following three targets exactly as named:
    - `make setup`: Installs all necessary dependencies for your project (e.g., from a requirements.txt, environment.yml, or pyproject.toml).
    - `make pipeline`: Executes your entire data pipeline sequentially from start to finish without any manual intervention. When our grader runs this command, it should initialize the database, load the data (Part 1), and generate all required output tables and plots (Parts 2-4). (Note: You may use pure Python, bash scripts, Snakemake, or any other orchestration tool, as long as make pipeline triggers the complete execution).
    - `make dashboard`: Starts the local server for your interactive dashboard.
