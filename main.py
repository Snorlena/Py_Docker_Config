import configparser
import os
import sys

config = configparser.ConfigParser()
config.read("config.ini")

# Removes all files that is created by the script.
def resetBuild():
    os.remove("nginx-proxy/nginx.conf")
    os.removedirs("nginx-proxy")
    os.remove("docker-compose.yml")
    os.remove("Dockerfile")

# A config for nginx. This one needs a overhaul.
def nginx_conf():
    if not os.path.exists("nginx-proxy"):
        os.mkdir("nginx-proxy")
    nginx_config = open("nginx-proxy/nginx.conf", "w")
    nginx_config.write("upstream backend {\n    server webserver1;\n    server webserver2;\n  }\n")
    nginx_config.write("  server {\n    listen 80;\n    location / {\n      proxy_pass http://backend;\n    }\n}")
    nginx_config.close()

# Takes information from [dockerfile] in the config and writes it to a Dockerfile
def nginx_dockerfile():
    if os.path.exists("Dockerfile"):
        os.remove("Dockerfile")
    data = dict(config.items('dockerfile'))
    dockerfile = open("Dockerfile","a")
    for keys, value in data.items():
        add_to_file = str(keys.upper()+ " "+ value+ "\n")
        dockerfile.write(add_to_file)
    dockerfile.close()

# Takes information from the config.ini and writes a docker-compose file.
def docker_compose():
    services = []

    # Takes lines in config.ini and puts them without brackets in a list.
    with open ("config.ini", "r") as cnf:
        for line in cnf:
            if "[" in line[0]:
                services.append(line.strip("\n\[]"))

    dockercompose = open("docker-compose.yml", "w")
    dockercompose.write("version: \"3.0\"\n")
    dockercompose.write("services:\n")

    # Takes the services from the servicelist and adds them to the docker-compose.
    for i in services:
        tab = "  "
        if i != "networks" and i != "dockerfile":
            data = dict(config.items(i))
            dockercompose = open("docker-compose.yml","a")
            dockercompose.write(tab + i + ":\n")
            for keys, value in data.items():
                if value != "":
                    if keys == "ports" or keys == "volumes":
                        add_to_file = str(tab*2 + keys + ":\n" + tab*2 + "- " + value + "\n")
                        dockercompose.write(add_to_file)
                    elif keys == "networks":
                        add_to_file = str(tab*2 + keys + ":\n"+ tab*3 + value + ":\n")
                        dockercompose.write(add_to_file)
                    elif keys == "ipv4_address":
                        add_to_file = str(tab*4 + keys + ": "+ value + "\n")
                        dockercompose.write(add_to_file)
                    else:
                        add_to_file = str(tab*2 + keys + ": "+ value + "\n")
                        dockercompose.write(add_to_file)
            dockercompose.write("\n")

        # Special part to add a network to the compose file.
        elif i == "networks":
            dockercompose.write(i + ":\n")
            dockercompose.write(tab + config.get(i, "network") + ":\n")
            dockercompose.write(tab*2 + "name: " + config.get(i, "name") + "\n")
            dockercompose.write(tab*2 + "driver: " + config.get(i, "driver") + "\n")
            dockercompose.write(tab*2 + "ipam:\n")
            dockercompose.write(tab*3 + "config:\n")
            dockercompose.write(tab*4 + "- subnet: " + config.get(i, "subnet") + "\n")
            dockercompose.write(tab*5 + "gateway: " + config.get(i, "gateway") + "\n")

    dockercompose.close()

if __name__ == '__main__':

    # Check for remove argument.
    if len(sys.argv) == 2:
        remove = sys.argv[1]
        if remove.lower() == "remove":
            resetBuild()
    # Build the files if no arguments.
    else:
        nginx_conf()
        docker_compose()
        nginx_dockerfile()