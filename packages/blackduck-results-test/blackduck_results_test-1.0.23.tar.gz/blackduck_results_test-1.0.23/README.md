# blackduck-results

Recursively collate library findings on a BlackDuck project and subprojects and return in a format suitable for integration with other tools such as Slack and JIRA.

## Quick Start

Create a ```.restconfig.json``` This is necessary for the blackduck REST API. DO NOT add this to any repository. The format is: 

```
        {
        "baseurl": "https://yourbd.com",
        "api_token": "YOUR_TOKEN_HERE",
        "insecure": false,
        "debug": false
        }
```

install the package

```
pip install blackduck-results
```

The package installation process left an executable ```bd-results``` which you can use directly to get the offending components in any project and version:


```
$bd-results project_name version_name
```


# Formats and cutoff points

```bd-results``` supports several options for formatting. The default is a short list of name and version of offending libraries, probably most useful for scripting and integration with slack, others are CSV, JSON, and PANDAS which gives a nice tabulation to stdout for quick manual checks.

Together with the cutoff parameter, one can inspect/integrate reports about offending projects in a variety of scenarios.e.g.

```
$ bd-results --cutoff high --format PANDAS sample_project Master 
                                 Component             Version  Critical Security Risk  High Security Risk  Total
54                         Apache ActiveMQ             5.15.12                       1                   1      2
279                               elliptic              v6.5.3                       0                   1      1
345                                 Gradle              4.10.3                       1                   2      3
986                                   y18n               4.0.0                       1                   0      1
```

# Tree

```bd-results``` allows you to see the recursive progress through subprojects as the results are being collected. e.g.

```
$bd-results --cutoff high --tree XX-YYY-XX-POC Latest
XX-YUY-XG-XRXC-Dynamo
	foo-dynamodb-backup
	foo-dynamodb-restore
	foo-library-ui-components
XX-YYY-XX-POC-entitlements
	infra-subscriptions
XX-YYY-XX-POC-UI
	XXC-foo-web-app-support 
	foo-library-ui-components
	foo-web-app-landing
Lodash 4.17.20
node-ini 1.3.5
Socket.IO Parser 3.3.1
axios v0.21.0
Lodash 4.17.19

```

# General Help

```
bd-results --help
usage: bd-results [-h] [-c {medium,high,critical,low}] [-f {SHORT,PANDAS,CSV,JSON}] [--tree] project_name version_name

Report the offending libraries from a given project+version in a short format suitable for jira/slack notifications. Note
blackduck connection depends on a .restconfig.json file which must be present in the current directory. It's format is: {
"baseurl": "https://foo.blackduck.xyz.com", "api_token": "YOUR_TOKEN_HERE", "insecure": true, "debug": false }

positional arguments: 
  project_name
  version_name

optional arguments:
  -h, --help            show this help message and exit
  -c {medium,high,critical,low}, --cutoff {medium,high,critical,low}
                        Minimum level of risk to report
  -f {SHORT,PANDAS,CSV,JSON}, --format {SHORT,PANDAS,CSV,JSON}
                        Report format
  --tree                Print tree of subprojects as stats are being gathered
  
Standard POSIX exit codes for OK, DATAERR, CONFIG
```

# Development

```make install_local``` will allow you to install the package locally and therefore see changes as you make edits to the code.

make sure you are using a new virtual environment so as to not confuse your package manager with a previously installed version.

```
# Use this if you are doing local development
install_source:
	python setup.py sdist bdist
	pip install -e .
```
# Deploying

The command ```make deploy``` is invoked from github workflow. At the moment and until jfrog edge is enabled the package is published to pipy.