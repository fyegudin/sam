### Instructions to run the script:
#### BASH:
#### Initialize a virtual environment and activate it:
python -m venv venv
####
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
#### Install the dependencies:
pip install -r requirements.txt
#### domains.json the file contains domains, the user may add more domains now including:
{
  "domains": ["google.com", "yahoo.com", "youtube.com", "facebook.com", "twitter.com", "instagram.com",
    "baidu.com", "wikipedia.org", "yandex.ru", "whatsapp.com"]
}
#### Arguments:
--concurrency: Number of concurrent requests
####
--domains: Number of domains
####
--timeout: Timeout in seconds
#### Help for script in terminal use the command:
python stress_tool.py -h
##### or 
python stress_tool.py --help
#### Small Run:
python stress_tool.py --concurrency 10 --domains 10 --timeout 60
#### Run the Tool:
python stress_tool.py --concurrency 10 --domains 500 --timeout 300
#### The results saved into csv file:
reputation_stress_results_timestamp.csv
