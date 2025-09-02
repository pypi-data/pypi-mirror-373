#!/usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser, REMAINDER
import os
from contextlib import closing
from getpass import getuser
import platform
import random
import re
import socket
import subprocess
import sys
import webbrowser
import donodo
import json

__version__ = "9.2"

on_linux = platform.system() == "Linux"

pat_tag = re.compile(r"\d{4}-\d{2}-\d{2}")

persistent_volume = "colomoto-{}".format(getuser())
persistent_dir = "persistent"

official_image = "colomoto/colomoto-docker"
official_alt = [
    "ghcr.io/colomoto/colomoto-docker:{tag}",
]

def error(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def info(msg):
    print(msg, file=sys.stderr)

def check_cmd(argv):
    DEVNULL = subprocess.DEVNULL if hasattr(subprocess, "DEVNULL") \
                else open(os.devnull, 'w')
    try:
        subprocess.call(argv, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
        return True
    except:
        return False

def check_sudo():
    return check_cmd(["sudo", "true"])

def docker_call():
    direct_docker = ["docker"]
    sudo_docker = ["sudo", "docker"]
    if on_linux:
        import grp
        try:
            docker_grp = grp.getgrnam("docker")
            if docker_grp.gr_gid in os.getgroups():
                return direct_docker
        except KeyError:
            raise
        if not check_sudo():
            error("""Error: 'sudo' is not installed and you are not in the 'docker' group.
Either install sudo, or add your user to the docker group by doing
   su -c "usermod -aG docker $USER" """)
        return sudo_docker
    return direct_docker

def check_docker():
    if not check_cmd(["docker", "version"]):
        if not on_linux:
            error("""Error: Docker not found.
If you are using Docker Toolbox, make sure you are running 'colomoto-docker'
within the 'Docker quickstart Terminal'.""")
        else:
            error("Error: Docker not found.")
    docker_argv = docker_call()
    if subprocess.call(docker_argv + ["version"], stdout=2):
        error("Error: cannot connect to Docker. Make sure it is running.")
    return docker_argv

def pull_image_from_doi(doi, docker_argv):
    """
    Download the Docker image referred by doi on Zenoto repository.
    Before pulling the image, the function first checks if the image already
    exists locally using the 'notes' metadata of the record.

    :param doi: the DOI of the image stored on Zenodo
    :param docker_argv: docker command as return by check_docker
    :return: The image name with its tag in case of success and None in case of error.
    """

    try:
        doi_record = donodo.doi_record(doi)
    except Exception as err:
        error(f"Error: {err}")
        return None

    if doi_record.notes is None:
        error("Error: docker image references are missing in Zenodo image record.")
        return None
    refs = json.loads(doi_record.notes)
    docker_image_name = refs.get("docker-image-name", None)
    if docker_image_name is None:
        error("Error: can't find docker-image-name in Zenodo image record.")
        return None

    need_pull = True
    docker_id = refs.get("docker-id", None)
    if docker_id is not None:
        docker_argv = docker_argv + ["inspect", "--type", "image", docker_id]
        try:
            output = subprocess.check_output(docker_argv)
            output = output.decode()
            if not output:
                need_pull = True
            else:
                imgspec = json.loads(output)[0]
                need_pull = (imgspec["Id"] != docker_id or
                             docker_image_name not in imgspec["RepoTags"])
        except subprocess.CalledProcessError:
            need_pull = True
    if need_pull:
        if donodo.pull(doi, doi_record) != 0:
            return None
    else:
        info(f'{docker_image_name} already exists; no need to pull it.')
    return f"{refs['docker-image-name']}"

def main():
    parser = ArgumentParser()
    parser.add_argument("--bind", default=None, type=str,
        help="Bind specified path to the docker working directory")
    parser.add_argument("--no-selinux", default=False, action="store_true",
        help="Disable SElinux for this container")
    parser.add_argument("-w", "--workdir", default="/notebook", type=str,
        help="Workdir within the docker image")
    parser.add_argument("-V", "--version", type=str, default="same",
        help="""Version of docker image ('latest' to fetch the latest tag;
        'same' for most recently fetched image)""")
    parser.add_argument("--forward-jupyter-port", default=False, action="store_true",
        help="Forward Jupyter listening port even if in shell or command mode")
    parser.add_argument("--port", default=0, type=int,
        help="Local port")
    parser.add_argument("--image", default=official_image,
        help="Docker image")
    parser.add_argument("--doi", default=None,
        help="DOI of a docker image on Zenodo")
    parser.add_argument("--no-browser", default=False, action="store_true",
        help="Do not start the browser")
    parser.add_argument("--unsafe-ssl", default=False, action="store_true",
        help="Do not check for SSL certificates")
    parser.add_argument("--no-update", default=False, action="store_true",
        help="Do not check for image update")
    parser.add_argument("--cleanup", default=False, action="store_true",
        help="Cleanup old images")

    group = parser.add_argument_group("choice of interface")
    x = group.add_mutually_exclusive_group()
    x.add_argument('--lab', action="store_true", help="Use jupyter lab interface")
    x.add_argument('--notebook', action="store_true", help="Use jupyter notebook interface")
    x.add_argument("--shell", action="store_true", help="Start interactive shell instead of notebook service")

    parser.add_argument("--for-colab", default=False, action="store_true",
        help="Default options for connecting Google Colab")

    group = parser.add_argument_group("docker run options")
    group.add_argument("-e", "--env", action="append",
        help="Set environment variables")
    group.add_argument("--name", help="Name of the container")
    group.add_argument("-v", "--volume", action="append",
        help="Bind mount a volume")
    group.add_argument("--network", type=str,
        help="Network access")
    group.add_argument("--ulimit", type=str,
        help="Resource limit")
    docker_run_opts = ["env", "volume", "network", "ulimit"]

    parser.add_argument("command", nargs=REMAINDER, help="Command to run in place of web interface")
    args = parser.parse_args()

    info(f"colomoto-docker {__version__}")

    docker_argv = check_docker()

    if args.doi is not None:
        docker_image_name = pull_image_from_doi(args.doi, docker_argv)
        if docker_image_name is None:
            print(f"fail to download image {args.doi}", file=sys.stderr)
            sys.exit(1)
        docker_image_name = docker_image_name.split(":")
        args.image = docker_image_name[0]
        args.version = docker_image_name[1]

    image_tag = args.version
    if args.version == "same":
        output = subprocess.check_output(docker_argv+[ "images", "-f",
                                    "reference=colomoto/colomoto-docker",
                                    "--format", "{{.Tag}}"])
        output = output.decode()
        if not output:
            args.version = "latest"
        else:
            image_tag = output.split("\n")[0]


    if args.version == "latest" and not args.no_update:
        import json
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        if args.unsafe_ssl or not on_linux:
            # disable SSL verification...
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context

        info("# querying for latest tag of {}...".format(args.image))
        url_api = "https://registry.hub.docker.com/v2/repositories/{}/tags".format(args.image)
        namespace, repository = args.image.split("/")
        url_api = f"https://hub.docker.com/v2/namespaces/{namespace}/repositories/{repository}/tags"
        tags = []
        q = urlopen(url_api)
        data = q.read().decode("utf-8")
        r = json.loads(data)
        q.close()
        r = r["results"]
        tags = [t["name"] for t in r if pat_tag.match(t["name"])]
        if not tags:
            info("# ... none found! use 'latest'")
            image_tag = "latest"
        else:
            image_tag = max(tags)

    image = "%s:%s" % (args.image, image_tag)
    info("# using {}".format(image))

    if not args.no_update \
        and (image_tag.startswith("next") \
            or not subprocess.check_output(docker_argv + ["images", "-q", image])):
        if args.image == official_image:
            pull = subprocess.run(docker_argv + ["pull", image])
            if pull.returncode != 0:
                info(f"The image {image} does not exists on hub.docker.com, falling back to mirrors..")
                for ref in official_alt:
                    altimage = ref.format(tag=image_tag)
                    pull = subprocess.run(docker_argv + ["pull", altimage])
                    if pull.returncode == 0:
                        info(f".. using {altimage}")
                        subprocess.check_call(docker_argv + ["tag", altimage, image])
                        subprocess.check_call(docker_argv + ["rmi", altimage])
                        break
                raise Exception("Docker image not found, maybe wrong version?")
        else:
            subprocess.check_call(docker_argv + ["pull", image])

    if args.cleanup:
        output = subprocess.check_output(docker_argv + ["images", "-f",
                                    "reference=colomoto/colomoto-docker",
                                    "--format", "{{.Tag}} {{.ID}}"])
        todel = []
        for line in output.decode().split("\n"):
            if not line:
                continue
            tag, iid = line.split()
            if tag == image_tag:
                continue
            if tag == "<none>":
                todel.append(iid)
            else:
                todel.append("{}:{}".format(args.image, tag))
        if todel:
            argv = docker_argv + ["rmi"] + todel
            info("# {}".format(" ".join(argv)))
            subprocess.call(argv)

    argv = docker_argv + ["run", "-it",  "--rm"]
    if args.no_selinux:
        argv += ["--security-opt", "label:disable"]

    if args.bind:
        argv += ["--volume", "%s:%s" % (os.path.abspath(args.bind), args.workdir)]
    else:
        persistent_mount = "%s/%s" % (args.workdir, persistent_dir)
        argv += ["--volume", "%s:%s" % (persistent_volume, persistent_mount)]

    argv += ["-w", args.workdir]
    if args.forward_jupyter_port or (not args.shell and not args.command):
        container_ip = "127.0.0.1"
        docker_machine = os.getenv("DOCKER_MACHINE_NAME")
        if docker_machine:
            container_ip = subprocess.check_output(["docker-machine", "ip", docker_machine])
            container_ip = container_ip.decode().strip().split("%")[0]
        if args.port == 0:
            # find next available
            for port in range(8888, 65535):
                with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                    dest_addr = (container_ip, port)
                    if s.connect_ex(dest_addr):
                        break
        else:
            port = args.port

        argv += ["-p", "%s:8888" % port]


    # forward proxy configuration
    for env in ["HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY", "NO_PROXY"]:
        if env in os.environ:
            argv += ["-e", env]

    name = args.name or f"colomoto{random.randint(0,100)}"
    argv += ["--name", name]

    def easy_volume(val):
        orig, dest = val.split(":")
        if dest[0] != "/":
            dest = os.path.abspath(os.path.join(args.workdir, dest))
        if orig[0] != "/" and os.path.isdir(orig):
            orig = os.path.abspath(orig)
        return "%s:%s" % (orig, dest)

    for opt in docker_run_opts:
        if getattr(args, opt) is not None:
            val = getattr(args, opt)
            if isinstance(val, list):
                for v in val:
                    if opt == "volume":
                        v = easy_volume(v)
                    argv += ["--%s"%opt, v]
            else:
                argv += ["--%s" % opt, val]

    argv += [image]

    _args_jupyter = ["--no-browser", "--port", "8888",
                        "--ip", "0.0.0.0"]
    token = ""
    if args.for_colab:
        import uuid
        token = "token=%s" % uuid.uuid4()
        _args_jupyter += [
            "--NotebookApp.%s" % token,
            "--NotebookApp.allow_origin='https://colab.research.google.com'",
            "--NotebookApp.port_retries=0"]
    else:
        _args_jupyter.append("--NotebookApp.token=")

    _args_jupyter += os.environ.get("JUPYTER_OPTS", "").split(" ")

    if args.notebook or args.for_colab:
        argv += ["jupyter-notebook"] + _args_jupyter
    elif args.shell:
        argv += ["bash"]
    elif args.lab:
        argv += ["jupyter-lab"] + _args_jupyter
    elif args.command:
        argv += args.command

    info("# %s" % " ".join(argv))

    if args.forward_jupyter_port or (not args.shell and not args.command and
                                     not args.no_browser):
        url = "http://%s:%s/?%s" % (container_ip, port, token)
        if os.fork() == 0:
            import threading
            import time
            def start_browser():
                try:
                    return webbrowser.open(url)
                except:
                    time.sleep(4)
                    info("""
Please open your web-browser to the following address:

    %s

""" % url)
            started = False
            nb_tries = 10
            while not started and nb_tries:
                nb_tries -= 1
                time.sleep(2)
                info("colomoto-docker: attaching to logs")
                with subprocess.Popen(docker_argv + ["logs", "-f", name],
                                       stdout=subprocess.PIPE) as p:
                    while line := p.stdout.readline():
                        if "is running at" in line.decode(errors="ignore"):
                            started = True
                            info("colomoto-docker: launching browser")
                            ret = start_browser()
                            info(f"colomoto-docker: launching browser returned {ret}")
                            if ret and args.for_colab:
                                time.sleep(4)
                                info("\n\n")
                                info("""==> Google Colab connect point: %s""" % url)
                            p.terminate()
                            break
                    ret = p.wait()
                    info(f"colomoto-docker: docker logs ended with retcode {ret}")
            sys.exit(0)
    os.execvp(argv[0], argv)

if __name__ == "__main__":
    main()
