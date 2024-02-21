import pytest
from project import *
from dotenv import load_dotenv
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException

dotenv_path = Path('build.env').resolve()
load_dotenv(dotenv_path=dotenv_path, override=True)
ci_project_id = getenv('CI_PROJECT_ID')
url = f"https://gitlab.com/api/v4/projects/{ci_project_id}/pipelines/latest"

def test_send_request_success():
    with patch('requests.get') as mock_get:
        mock_response_data = {
            "status": "success",
            "id": 123,
            "ref": "main"
        }
        mock_get.return_value.json.return_value = mock_response_data
        response = send_request(url)
        assert response.json() == mock_response_data


def test_send_request_failure():
    with patch('requests.get', side_effect=RequestException("Network error")):
        with pytest.raises(RequestException) as exception:
            send_request(url)
        assert "Network error" in str(exception.value), "Unexpected exception message"


def test_get_pipeline_parameters_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'id': 123,
        'ref': 'main',
        'status': 'success'
        }
    assert get_pipeline_parameters(mock_response) == (True, 123, "main")


def test_get_pipeline_parameters_failure():
    mock_response = MagicMock()
    mock_response.json.return_value = "any text"

    with pytest.raises(ValueError):
        get_pipeline_parameters(mock_response)


def test_get_job_parameters_success():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            'id': 123,
            'status': 'success',
            'stage': 'deploy',
            'name': 'deploy-positive',
            'ref': 'main'
        }
    ]
    assert get_job_parameters(mock_response) == (123)


def test_get_job_parameters_failure():
    mock_response = MagicMock()
    mock_response.json.return_value = "any text"

    with pytest.raises(ValueError):
        get_job_parameters(mock_response)


def test_get_logs():
    mock_response = MagicMock()
    mock_response.text = "| any text here"

    assert get_logs(mock_response) == "| any text here"


def test_generate_pdf_report_created():
    with patch('project.FPDF.output') as mock_output:
        filename = generate_pdf_report("source", "target", "data", "default")
        mock_output.assert_called_once_with('deployment_report.pdf')

        assert filename == 'deployment_report.pdf'


raw_correct_data = """
Deploy started.
...
Deployed Source
=============================================================================================================================================
| State     Name                      Type           Path
| ───────── ───────────────────────── ────────────── ────────────────────────────────────────────────────────────────────────────────────────
| Unchanged MyApexClass1              ApexClass      .../classes/MyApexClass1.cls
| Unchanged MyApexClass1              ApexClass      .../classes/MyApexClass1.cls-meta.xml
Deploy Finished.
    """

raw_incorrect_data = """
Deploy started.
...
Deployed Source
=============================================================================================================================================
| State     Name                      Type           Path
| ───────── ───────────────────────── ────────────── ────────────────────────────────────────────────────────────────────────────────────────
| Unchanged MyApexClass1              ApexClass      .../classes/MyApexClass1.cls
| Unchanged My Apex Class 1           ApexClass      .../classes/My Apex Class 1.cls-meta.xml
Deploy Finished.
    """

raw_no_data = """
        Deploy started. / Deploy Finished.
    """

exepcted_processed_data = [
    ['State', 'Name', 'Type', 'Path'],
    ['Unchanged', 'MyApexClass1', 'ApexClass', '.../classes/MyApexClass1.cls'],
    ['Unchanged', 'MyApexClass1', 'ApexClass', '.../classes/MyApexClass1.cls-meta.xml']
]


def test_parse_deployment_data_success():
    assert parse_deployment_data(raw_correct_data) == exepcted_processed_data


def test_parse_deployment_data_failure():
    with pytest.raises(ValueError):
        parse_deployment_data(raw_incorrect_data)


def test_generate_deployment_report_success():
    assert generate_deployment_report("main", "test-target", raw_correct_data, date_time=None) == 'deployment_report.pdf'


def test_generate_deployment_report_valueerror():
    with pytest.raises(Exception):
        generate_deployment_report("main", "test-target", raw_no_data, date_time=None)
