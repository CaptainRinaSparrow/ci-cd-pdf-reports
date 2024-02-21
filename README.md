# CI-CD PDF REPORTS
#### Video Demo:  [YouTube](https://youtu.be/RrvWv6hOK_w)
#### Description:
I've developed an automation tool for CI/CD pipeline documentation, initially for the CS50P Harvard course. This tool retrieves the latest deployment data, including Salesforce CLI deployment results, ensures the process was successful, and compiles logs and job details into a streamlined PDF report. Aimed at improving the clarity of deployment artifacts for audits and leveraging my Python abilities in automation and data analysis, this versatile application can generate various reports, such as failed deployments, validation outcomes, and Apex test results. While currently demonstrated with GitLab, the tool is designed with the flexibility to adapt to other platforms.

#### Components:
My project includes the following key components:
- `README.md`: The introductory guide to the project.
- `project.py`: Central script for data retrieval, processing, and report creation.
- `test_project.py`: Contains tests to ensure functionality.
- `requirements.txt`: Lists required Python packages.
- `build.env`: Config file for essential project variables.
- `DejaVuSansCondensed.ttf` & `DejaVuSansCondensed-Bold.ttf`: Fonts selected for readability in reports.
- `cs50p.png`: Demonstrates FPDF capabilities with an image in reports[^1].

This tool is demonstrated using my GitLab.com public test project [learning/cs50p-project](https://gitlab.com/learning4050104/cs50p-project).

#### Running project.py:
To see the results, execute `python3 project.py` in your terminal:
1. **Environment Setup**: Loads environment variables from `build.env` for GitLab authentication and project identification.
2. **Timezone Configuration**: Sets the timezone to Asia/Yerevan for consistent report timestamps, adjustable via the `time_zone` variable.
3. **Initial API Call**: Sends a request to GitLab's API for the latest pipeline data of the specified project, using `ci_project_id`.
4. **Pipeline Status Check**: Analyzes the pipeline's status, ID, and source from the JSON response. If unsuccessful, prompts a deployment check.
5. **Fetching Job Data**: Retrieves job IDs for a successful pipeline to proceed with log collection.
6. **Retrieving Logs**: Obtains job logs for detailed execution data.
7. **PDF Report Generation**: Uses the `FLTReport` class to create a custom PDF report with logs, source branch, and timestamp.
8. **Data Processing for PDF**: Prepares log data for the report, filtering and formatting according to predefined headings.
9. **Final Output**: Saves the report as 'deployment_report.pdf', showcasing deployment logs in a structured format.
10. **Error Handling**: Manages exceptions, ensuring robust processing and clear error reporting.

#### Reflections and Next Steps:
This project has been a significant learning experience, enhancing my Python skills in automation and data management and improving the quality of our deployment documentation. I am considering expanding its capabilities to include various data types and a user-friendly interface for broader accessibility.

I look forward to engaging with the community on this tool, and inviting feedback and contributions. Whether you aim to refine your CI/CD workflows, delve into Python automation, or explore PDF report generation, I hope this project serves as a valuable resource.

[^1]: Basically, it's a slightly cropped CS50P image from GitHub. The image is taken from [https://github.com/realTristan/CS50P](https://user-images.githubusercontent.com/75189508/194149777-f63aa3eb-0455-4982-8b18-199bc6e6c156.png) page.
