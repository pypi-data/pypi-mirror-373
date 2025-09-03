
Helper Python script for launching the [CoLoMoTo Docker distribution](https://colomoto.github.io/colomoto-docker).

## Installation

You need [Docker](https://docs.docker.com/get-docker/) and [Python](http://python.org).
We support GNU/Linux, macOS, and Windows.

In a terminal:

    pip install -U colomoto-docker 


In case of trouble, try `python3 -m pip install -U colomoto-docker`

## Usage

    colomoto-docker

After preparing the Docker container, the command should open your webbrowser to the Jupyter Lab interface.

The container can be stopped by pressing <kbd>Ctrl</kbd>+<kbd>C</kbd> keys.

By default, the script will fetch the most recent [colomoto/colomoto-docker tag](https://github.com/colomoto/colomoto-docker/releases). A specific tag can be specified using the `-V` option; or use `-V same` to use the most recently fetched image. For example:

    colomoto-docker                 # uses the most recently fetched image
    colomoto-docker -V latest       # fetches the latest published image
    colomoto-docker -V 2024-04-01   # fetches a specific image

**Warning**: by default, the files within the Docker container are isolated from the running host computer, therefore *files are deleted after stopping the container*, except the files within the `persistent` directory.

To have access to the files of your current directory you can use the `--bind` option:

    colomoto-docker --bind .

If you want to have the tutorial notebooks alongside your local files, you can
do the following:

    mkdir notebooks
    colomoto-docker -v notebooks:local-notebooks

in the Jupyter browser, you will see a `local-notebooks` directory which is
bound to your `notebooks` directory.

### Selecting interface

    colomoto-docker --lab          # laucnh Jupyter Lab interface (default)
    colomoto-docker --notebook     # launch Jupyter Notebook interface
    colomoto-docker --shell        # launch shell
    colomoto-docker command line   # execute command line in place of launching the interface

### Running old images

On some systems, older images may require changing default security options.

    colomoto-docker --ulimit nofile=8096 -V 2018-05-29


### Other options

See

    colomoto-docker --help

for other options.
