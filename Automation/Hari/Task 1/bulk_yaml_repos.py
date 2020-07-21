import os, json, requests, yaml
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#------------------------------------------------------------------------
username = os.environ.get("GITHUB_USERNAME")
token = os.environ.get("GITHUB_TOKEN")
license_template = os.environ.get("LICENSE")
t_owner = os.environ.get("T_OWNER")
t_repo = os.environ.get("T_REPO")
wh_url = os.environ.get("WH_URL")
organization = os.environ.get("ORGANIZATION")
wh_events = json.loads(os.environ.get("WH_EVENTS"))
#------------------------------------------------------------------------

url = "https://api.github.com/"
headers = {
    'Authorization': 'token ' + token,
    'Accept': 'application/vnd.github.baptiste-preview+json'
}

params = {}
for (category, repositories) in yaml.safe_load(open("details.yaml")).items():
    for repository in repositories:
        params['name'] = repository
        for key in repositories[params['name']]:
            params[key] = repositories[params['name']][key]

        headers['Accept'] =  "application/vnd.github.baptiste-preview+json"
        p = requests.post(url + 'repos/' + t_owner + '/' + t_repo + '/generate', data=json.dumps(params), headers=headers)
        if p.status_code != 201:
            print("Error! Repository {} could not be created.".format(repository))
            print("Error Code:",p.status_code)
            continue
        headers.pop("Accept")
        whpar = {}
        config = {}
        whpar['events'] = wh_events
        config['url'] = wh_url
        whpar['config'] = config
        p = requests.post(url + 'repos/' + username + '/' + repository + '/hooks', data=json.dumps(whpar), headers=headers)
        if p.status_code != 201:
            print("Error! Webhook could not be created.")
            print("Error Code:",p.status_code)
        tfrparams = {}
        tfrparams['new_owner'] = organization
        p = requests.post(url + 'repos/' + username + '/' + repository + '/transfer', data=json.dumps(tfrparams), headers=headers)
        if p.status_code != 202:
            print("Error! Repository could not be transferred to the organization.")
            print("Error Code:",p.status_code)
        print("Success! {} has been created successfully.".format(repository))