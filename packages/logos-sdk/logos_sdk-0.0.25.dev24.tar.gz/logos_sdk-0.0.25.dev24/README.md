# Logos Software Development Kit  
  
Logos Software Development Kit (Logos SDK) is a private library encapsulating functionality shared by Logos Scripts - configurable scripts running as Cloud Functions, triggered by Cloud Scheduler, which are controlled and monitored via the Logos UI, as a part of the Logos Ecosystem.  
  
# Functionality modules  
  
## Logging  
Cloud Function Scripts within the Logos ecosystem have special requirements for logging. Apart from simple JSON messages, the logs need to also carry information on:  
  
- trace (used for tracking runs of Cloud Functions)  
- labels (fields used for internal Logos filtering)  
- logger name  
  
The standard Python `logging` library does not offer the possibility of capturing a combination of these values in a format parsable by Google Cloud Logging - this is only possible through the `google-cloud-logging` library. On the other hand, `google-cloud-logging` transmits all logs to Google Cloud Logging even when a script is run on the local machine (with the exception of running it within the `functions-framework` environment), which is something to be avoided when developing locally or testing on Bitbucket, as we do not want to waste our resources. 

This module serves as a wrapper over the standard Python `logging` and `google-cloud-logging` libraries, with the default being set to  `google-cloud-logging`. The switch is based on the presence of environment variables `DEVELOPMENT` or `TESTING`: if either of these is set within the venv environment,  `logging` library is used instead.
If deploying to development instance in Cloud, we want the logs to be logged into Cloud, but not to clash with the production instance, therefore setting the environment variable `CLOUD_DEVELOPMENT` ensures that the logs are logged under name `logos-logging-development` instead of the standard `logos-logging`.

```bash  
export DEVELOPMENT=True  
#or 
export TESTING=True  
#or
export CLOUD_DEVELOPMENT=True
```  
  
### Usage  
  
To set up the Logger, one can use the parsing function `setup_from_request`, which expects a Cloud Function Script trigger request in a usual format:
  
```python  
import functions_framework  
import logos_sdk.logging as logos_logging  
  
@functions_framework.http  
def run(request):  
	logger, labels, settings, secrets = logos_logging.setup_from_request(request, "logos-logging")
```
```
EXPECTED_REQUEST_JSON_BODY = {  
	"settings": {},  
	"id": "",  
	"author": "",  
	"script": "",  
	"client": "",  
	"accesses": [  
		{  
			"account": {"id": "", "account_platform_id": ""},  
			"secret": {"id": "", "name": ""},  
			"platform": {"id": "", "short_name": ""}  
		},  
		...  
	],  
}  
```  
  
The trigger request can be also processed separately, in which case the logger is instantiated from the class itself:  

```python
LogosLogger(name="logos-logging", labels={}, trace="")`
```
  
### Output  
When the standard Python `logging` library is used, the output logs have the following structure:  
  
```python  
Lowest possible severity: INFO  
  
String output: SEVERITY:logger-name:message  
  
LogEntry output:  
	LogEntry.name = "logos-logging"  
	LogEntry.msg = {"message": ""}  
	LogEntry.level = 40 | ...  
	LogEntry.levelname = INFO | ERROR | ...  
	LogEntry.json_fields = {  
	"logging.googleapis.com/trace": trace,  
	"logging.googleapis.com/labels": {  
	    "log_type": RESULT | NOTIFICATION | DEBUG,  
	    **labels,  
	},  
}  
```  
  
With `google-cloud-logging`, the output logs should have the following structure: 
  
```python  
Lowest possible severity: INFO  
{  
	"logName": "projects/logos-382010/logs/logos-logging",  
	"trace": "projects/logos-382010/traces/some-trace",  
	"severity": INFO | ERROR | ...,  
	"jsonPayload": { "message": "", ... },  
	"labels": {  
		"log_type": RESULT | NOTIFICATION | DEBUG,  
		"id": "Logos id of the job",  
		"author": "Logos id of the job author",   
		"client": "Logos id of the client",  
		"script": "Logos id of the script",
		**platform_accounts,  
	}  
}  
```  
   
Depending on the `platform_accounts` the Cloud Function Script accesses during its run, `labels` might also contain Logos platform `short_name` field as a key and Logo `account_platform_id` as a value, for example:  
  
```python  
{  
	"merchant-center": "xxxxxxx",  
	"google-ads": "xxx-xxx-xxxx",  
}  
```  
  
To sum it up, an example of the complete labels contents would be:  
  
```python  
{  
	"labels": {  
		"log_type": "result",  
		"id": "0",  
		"author": "0",  
		"client": "0",  
		"script": "0",  
		"merchant-center": "0000000",  
		"google-ads": "000-000-0000"  
	}  
}  
```  
  
## Services  
This module serves as a wrapper over communicating with Logos Services. When `DEVELOPMENT`, `TESTING` or `CLOUD_DEVELOPMENT` environment variable is set  
  
```bash  
export DEVELOPMENT=True 
#or 
export TESTING=True  
#or
export CLOUD_DEVELOPMENT=True
```  
  
the URLs of development services (bound to the development branches in BitBucket) are used. On the other hand, if none of these is set, production URLs are called (used in the Cloud production environment).  
  
# Installation as a dependency to Logos Scripts  
  
## Local environment  
  
This library is hosted as on Pypi.  

logos-sdk=[desired version]/latest
```  
2. Then in your terminal with the venv active, run following:  
```bash
pip3 install -r requirements.txt  
export DEVELOPMENT=True  
```  
  
To verify that the library was successfully installed, you can view the installed package information via:  
  
```bash  
pip3 show -f logos-sdk  
```  
  
## BitBucket pipelines environment  
  
Firstly, read the local environment setting. If "been there, done that", the setting for BitBucket pipeline testing is very similar. At first, go to pipeline variables in BitBucket UI and create a variable `GOOGLE_CREDENTIALS`, pasting the contents of the `logos-accessor` service account credentials file into it. Then create `PYPI_CREDENTIALS` and paste this into the secret:
You also need set the `SERVICES_PATH` for each service.
```
[pypi]
username = __token__
password = pypi-[api token]
```

Then your bitbucket-pipelines.yml testing step should look like this:  
  
```  
pipelines:  
	default:  
		- step:  
			name: Test  
			caches:  
				- pip  
			script:  
				- echo $GOOGLE_CREDENTIALS > logos-382010-ee0fd6995649.json
                - echo $PIPY_CREDENTIALS > .pypirc
                - export GOOGLE_APPLICATION_CREDENTIALS=logos-382010-ee0fd6995649.json
                - pip3 install -U setuptools wheel twine
                - python setup.py sdist bdist_wheel
                - twine upload --config-file .pypirc --verbose dist/* 
```  
  
## Google Cloud environment  
Firstly, read the local environment setting. If "been there, done that", your Dockerfile should contain the following steps:  
  
```  
RUN apt-get update && apt-get install -y git  
RUN pip3 install google-auth keyring keyrings.google-artifactregistry-auth  
RUN pip3 install --no-cache-dir -r requirements.txt  
```  
  
In your cloudbuild.yaml file, the build step should contain the `--network=cloudbuild` parameter, as this ensures that the `keyring` auth libraries have access to the necessary credentials directly from the Cloud Build environment (we no longer need to set `GOOGLE_APPLICATION_CREDENTIALS` environment variable):  
  
```  
- name: 'gcr.io/cloud-builders/docker'  
args: [ 'build', '--network=cloudbuild', '-t', 'gcr.io/logos-382010/merchant-control', '.' ]  
```  

If you are deploying a development cloud instance, in Cloud Run settings, `CLOUD_DEVELOPMENT`needs to be set:

```bash  
export CLOUD_DEVELOPMENT=True
``` 

  
# Development & versioning
Development of new features/refactor/debug follow the naming convention of:  
  
```  
"feature/[short name]"  
"refactor/[short name]"  
"debug/[short name]"  
```
  
Pull requests are directed do the current development branch, which always bears the number of the newest version, for example `development-0.0.2`.  After adding a major feature, or a number of less significant refactors and hot-fixes, the current development branch is merged into master and deployed into Google Artifact Registry. The old development branch is then deleted and a new branch with the following version `development-0.0.3` will be created. Version is not controled throught an env variable VERSION.
For fixing minor bugs, dev version is used, e.g 0.0.24.dev1

Manual build, with optional build number
```
export VERSION=x.x.x.dev[x]
python setup.py sdist bdist_wheel --build-number=$BUILD_NUMBER
```

Manual upload to test PyPi, change .pypirc api token to test version, and change header to [pypi]
```
twine upload --repository testpypi --config-file .pypirc --verbose dist/*
```

Manual upload to production PyPi, change .pypirc api token to production version to [testpypi]
```
twine upload --config-file .pypirc --verbose dist/*
```