import pytz
import requests
from os import getenv
from fpdf import FPDF
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

dotenv_path = Path('build.env').resolve()
load_dotenv(dotenv_path=dotenv_path, override=True)
access_token = getenv('ACCESS_TOKEN')
ci_project_id = getenv('CI_PROJECT_ID')
time_zone = getenv('TIME_ZONE')
tz = pytz.timezone(time_zone)
date_time = datetime.now(tz).strftime('%Y.%m.%d %H:%M %Z (UTC%z)')


def main():
    response = send_request(url = f'https://gitlab.com/api/v4/projects/{ci_project_id}/pipelines/latest')
    status, pipeline_id, source = get_pipeline_parameters(response)
    if status:
        response = send_request(url = f'https://gitlab.com/api/v4/projects/{ci_project_id}/pipelines/{pipeline_id}/jobs')
        job_id = get_job_parameters(response)
        response = send_request(url = f'https://gitlab.com/api/v4/projects/{ci_project_id}/jobs/{job_id}/artifacts/log.log')
        logs = get_logs(response)
        generate_deployment_report(source, 'gitlabci.cs50p', logs, date_time)
    else:
        print('Please check your latest deployment!')


def send_request(url):
    """
    Sends a HTTPS request.

    """
    headers = {'PRIVATE-TOKEN': access_token}
    response = requests.get(url, headers=headers)
    # print(f"{response.text} \n")
    return response


def get_pipeline_parameters(response) -> tuple[bool, int, str]:
    """
    Gets GitLab response parameters for a pipeline.

    """
    try:
        json_data = response.json()
        status = json_data['status']
        pipeline_id = json_data['id']
        source = json_data['ref']
    except Exception as err:
        raise ValueError(f"Error parsing pipeline parameters: {err}")
    # print(type(status), status, type(pipeline_id), pipeline_id, type(source), source)
    return True if status == 'success' else False, pipeline_id, source


def get_job_parameters(response) -> int:
    """
    Gets GitLab response parameters for a job.

    """
    try:
        json_data = response.json()
        job_id = json_data[0]['id']
    except Exception as err:
        raise ValueError(f"Error parsing job parameters: {err}")
    # print(type(job_id), job_id)
    return job_id


def get_logs(response) -> str:
    """
    Gets GitLab logs for a job.

    """
    try:
        logs = response.text
    except Exception as err:
        raise ValueError(f"Error parsing logs: {err}")
    # print(type(logs), logs)
    return logs


class FLTReport(FPDF):
    def __init__(self, source, target, date_time=None):
        super().__init__(orientation='L')
        self.logo_path = Path(__file__).resolve().parent / 'cs50p.png'
        self.source = source
        self.target = target
        self.date_time = date_time

    def header(self):
        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf')
        self.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf')
        self.set_font('DejaVu', '', 10)

        self.image(self.logo_path, 10, 5, 80, 0, '', 'https://cs50.harvard.edu/python/2022/')
        info_str = f"Source: {self.source}\nTarget: {self.target}\nTime: {self.date_time}"
        self.set_y(40)
        self.multi_cell(75, 5, info_str)
        self.ln(5)


default_table_heading = ['State', 'Name', 'Type', 'Path']
default_table_len = len(default_table_heading)


def generate_pdf_report(source, target, data, data_type='default', date_time=None):
    """
    Generates a PDF report. Can be versatile and use different table data for deployment, validations, test results, etc.

    """
    pdf = FLTReport(source, target, date_time)
    pdf.add_page()

    if data_type.lower() == 'table':
        pdf.set_font('DejaVu', '', 12)
        with pdf.table(cell_fill_color=237, cell_fill_mode='ROWS') as table:
            for data_row in data:
                row = table.row()
                for data_cell in data_row:
                    row.cell(data_cell)
    else:
        pdf.multi_cell(0, 10, data)

    filename = 'deployment_report.pdf'
    pdf.output(filename)
    return filename


def parse_deployment_data(raw_data):
    """
    Parses deployment data from Salesforce CLI execution results.

    """
    data = [default_table_heading]
    # print(f'raw_data: {raw_data}')
    processed_data = raw_data.split('\n')[7:-2]  # Simplify data preprocessing
    # print(f'processed_data: {processed_data}')
    for element in processed_data:
        if '|' in element and '─' not in element:
            # print(f'element: {element}')
            parts = element.split(' ')[1:]
            meta_to_log = [part.strip() for part in parts if part.strip()]
            # print(f'meta_to_log: {meta_to_log}')
            parsed_columns = len(meta_to_log)
            if parsed_columns == default_table_len:
                data.append(meta_to_log)
                # print(f'data: {data}')
            else:
                raise ValueError(f'A line {meta_to_log} was not added to pdf report due to wrong formatting.')
    # print(f'data: {data}')
    return data


def generate_deployment_report(source, target, raw_data, date_time=None):
    """
    Pre-generates a report based on deployemnt data from parse_deployment_data().

    """
    try:
        data = parse_deployment_data(raw_data)
        if len(data) > 1:
            return generate_pdf_report(source, target, data, 'table', date_time)
        else:
            raise ValueError('Insufficient data for report.')
    except Exception as err:
        raise Exception(f'Error generating report: {err}')


if __name__ == '__main__':
    main()
