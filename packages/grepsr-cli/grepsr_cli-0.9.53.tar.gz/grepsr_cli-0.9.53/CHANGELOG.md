# Grepsr Cli Change History

## current version


## 0.7.2
{Changes to gcli codebase from last version (0.7.0 [23 Mar 2022])}

README.md
> updated readme highlighting new features, edge cases and development notes

grepsrcli/controllers/crawler.py
> added 3 new command line options -p, -m, and --params-file
> handle JSON decode exception
> refactor
> timeout if > 300 secs when deploying.
> stash untracked files too. fixes bug if deploying new service on a clean repo (which failed on `git stash pop` cuz there was nothing to stash and nothing to pop).
> drop latest stash if successfully deployed.

grepsrcli/core/aws_s3.py
> removed unused code
> add a new method to get login creds from ECR.

grepsrcli/core/sdk_setup.py
> replace shell command with python specific functions for cross platformability.
> replace EXPORTing auth credentials with corresponding API from boto3 python package for docker authentication.
> refactor

grepsrcli/core/test_local.py
> refactor
> implement key new features for this update.

grepsrcli/core/utils.py
> replace linux specific path seperators with platform independent paths
> a new function to get the entrypoint of a docker image.
> throw more helpful error messages

## 0.0.1

Initial release.
