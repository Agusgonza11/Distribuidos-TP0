import sys 
import yaml


def generar_yaml(cantidad_clientes):
    yaml = {
        "name": "tp0",
        "services": {
            "server": {
                "container_name": "server",
                "image": "server:latest",
                "entrypoint": "python3 /main.py",
                "environment": [
                    "PYTHONUNBUFFERED=1",
                    "LOGGING_LEVEL=DEBUG"
                ],
                "networks": ["testing_net"]
            }
        },
        "networks": {
            "testing_net": {
                "ipam": {
                    "driver": "default",
                    "config": [{"subnet": "172.25.125.0/24"}]
                }
            }
        }
    }

    for i in range(1, int(cantidad_clientes) + 1):
        yaml["services"][f"client{i}"] = {
            "container_name": f"client{i}",
            "image": "client:latest",
            "entrypoint": "/client",
            "environment": [
                f"CLI_ID={i}",
                "CLI_LOG_LEVEL=DEBUG"
            ],
            "networks": ["testing_net"],
            "depends_on": ["server"]
        }

    return yaml
   


def generar_docker_compose(nombre_archivo, cantidad_clientes):
    with open(nombre_archivo, "w") as archivo:
        yaml.dump(generar_yaml(cantidad_clientes), archivo)



if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)
    generar_docker_compose(sys.argv[1], sys.argv[2])