# A Cli tool for Grepsr Developers

## Installation
```
$ pip install grepsr-cli
```


## Usage
### passing parameters to `amazon_com` service.
```bash
gcli crawler test -s amazon_com -p '{"urls":["https://amazon.com/VVUH4HJ","https://amazon.com/FV4434"]}'
```

### if JSON is complex, use file instead
```
# contents of /tmp/amazon_params.json
{"urls": ["https://amazon.com/VV%20UH4HJ"], "strip": ["'", "\"", "\\"]}

gcli crawler test -s amazon_com --params-file '/tmp/amazon_params.json'
```

#### Hacks Used.
> If the json parameter has a space, it might break parameter parsing.
> If the json parameter has a dash `-` and any character after it has a space, it will break parameter parsing.
Cause: no double quoting around $@ in `run_service.php:5:49` [here](https://bitbucket.org/grepsr/vortex-backend/src/09c263fb0bb538003db01e1d6742a43ae6ebc61a/deploy/vortex-backend/scripts/run_service.sh#lines-5)
> This is fixed hackily by replacing string with its unicode \u0020 sequence. This works beacause $@ does not split on \u0020.

### inject custom command.
Say, for example you wanted to a inject a php function so that it could be called from inside you service_code when testing locally.
Note: All these files should only be created inside `~/.grepsr/tmp`. Creating it outside will not work.

1. Create a file called `inject.php` inside `~/.grepsr/tmp/`
2. Implement your function inside `~/.grepsr/tmp/inject.php`
```php
function addRowLocal($arr) {
    ...
    ...
}
```
3. Create a file called `inject.sh` inside `~/.grepsr/tmp/`
4. inside inject.sh add:
```
alias php='php -d auto_prepend_file=/tmp/inject.php'
```
Note: the file location is `/tmp/inject.php` instead of `~/.grepsr/tmp/inject.php`.
This is because, the local path `~/.grepsr/tmp` gets mapped to `/tmp` in the docker container.
And `inject.sh` runs inside docker, instead of the local filesystem.
5. Add an entry in `~/.grepst/config.yml` like so:
```yml
    php:
        ...
        sdk_image: ...
        pre_entry_run_file: inject.sh      # relative and limited to the tmp/ dir
```
6. Now you can use `addRowLocal()` in your any of your files.
```php
public function main($params) {
    ...
    $arr = $this->dataSet->getEmptyRow();
    addRowLocal($arr); // won't throw error
    ...
}
```
## Development
> Be sure to uninstall gcli first, with
`pip uninstall grepsr-cli`

```bash
git clone git@bitbucket.org:zznixt07/gcli.git grepsrcli
cd grepsrcli
pip install -e .
```

## Features Added
- drop stash after pushed successully. Before this, all stashes were always kept.
- run a custom shell file before running your crawler. This allows possiblity like always injecting a php function in all your crawlers.
- auto add `Dependencies: ...` that your crawler class extends (dependecies that are not extended by crawler classes but used elsewhere is upcoming)


# TODO:
- Experiment with git rebase on deploy fail. `git rebase origin/master --autostash && git push`
- Handle Prioritization of same plugin name across multiple repo more deterministically. (maybe prioritize cwd path?)
- node only run crawler if npm install is successfull. (add && between npm install and npm start)
- run `tsc` before deploying `vortex-ts-registry` packages
- add option to force update dependecies to latest version for all/specific `vortex-ts-registry` dependencies
- handle ctrl+c during node package install on docker. (currently it continues running in BG)
- add new baseclass typescript package and do not include SOP, (do not normalize - to _) change `npm start` to `tsc` and test runs. Also generate .d.ts file in tsconfig.json