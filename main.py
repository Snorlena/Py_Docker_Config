import configparser
import os
import sys

config = configparser.ConfigParser()
config.read("config.ini")

def resetBuild():
    os.remove("nginx-proxy/nginx.conf")
    os.removedirs("nginx-proxy")
    os.remove("docker-compose.yml")
    os.remove("Dockerfile")

def nginx_conf():
    if not os.path.exists("nginx-proxy"):
        os.mkdir("nginx-proxy")
    nginx_config = open("nginx-proxy/nginx.conf", "w")
    nginx_config.write("upstream backend {\n    server webserver1;\n    server webserver2;\n  }\n")
    nginx_config.write("  server {\n    listen 80;\n    location / {\n      proxy_pass http://backend;\n    }\n}")

def nginx_dockerfile():
    if os.path.exists("Dockerfile"):
        os.remove("Dockerfile")
    data = dict(config.items('dockerfile'))
    dockerfile = open("Dockerfile","a")
    for keys, value in data.items():
        add_to_file = str(keys.upper()+ " "+ value+ "\n")
        dockerfile.write(add_to_file)

def docker_compose():
    services = []

    with open ("config.ini", "r") as cnf:
        for line in cnf:
            if "[" in line[0]:
                services.append(line.strip("\n\[]"))

    dockercompose = open("docker-compose.yml", "w")
    dockercompose.write("version: \"3.0\"\n")
    dockercompose.write("services:\n")

    for i in services:
        if i != "networks" and i != "dockerfile":
            data = dict(config.items(i))
            dockercompose = open("docker-compose.yml","a")
            dockercompose.write("  " + i + ":\n")
            for keys, value in data.items():
                if value != "":
                    if keys == "ports" or keys == "volumes":
                        add_to_file = str("    " + keys + ":\n    - "+ value+ "\n")
                        dockercompose.write(add_to_file)
                    elif keys == "networks":
                        add_to_file = str("    " + keys + ":\n      "+ value + ":\n")
                        dockercompose.write(add_to_file)
                    elif keys == "ipv4_address":
                        add_to_file = str("        " + keys + ": "+ value + "\n")
                        dockercompose.write(add_to_file)
                    else:
                        add_to_file = str("    " + keys + ": "+ value + "\n")
                        dockercompose.write(add_to_file)
            dockercompose.write("\n")

        elif i == "networks":
            dockercompose.write(i + ":\n")
            dockercompose.write("  " + config.get(i, "network") + ":\n")
            dockercompose.write("    name: " + config.get(i, "name") + "\n")
            dockercompose.write("    driver: " + config.get(i, "driver") + "\n")
            dockercompose.write("    ipam:\n")
            dockercompose.write("      config:\n")
            dockercompose.write("        - subnet: " + config.get(i, "subnet") + "\n")
            dockercompose.write("          gateway: " + config.get(i, "gateway") + "\n")

if __name__ == '__main__':

    if len(sys.argv) > 1:
        remove = sys.argv[1]
        if remove.lower() == "remove":
            resetBuild()
    else:
        nginx_conf()
        docker_compose()
        nginx_dockerfile()

        
