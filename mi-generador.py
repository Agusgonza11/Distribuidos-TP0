import sys 
import yaml

def cargar_clientes_desde_archivo():
    """Cargo clientes desde archivo YAML"""
    with open("clientes.yaml", "r") as file:
        data = yaml.safe_load(file)
    return data.get("clientes", [])


def generar_yaml(cantidad_clientes, clientes):
    """Genera un docker-compose.yaml"""
    yaml = {
        "name": "tp0",
        "services": {
            "server": {
                "container_name": "server",
                "image": "server:latest",
                "entrypoint": "python3 /main.py",
                "environment": [
                    "PYTHONUNBUFFERED=1",
                ],
                "networks": ["testing_net"],
                "volumes": [
                    "./server/config.ini:/config.ini"
                    "./bets.csv:/bets.csv"

                ]
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
        cliente = clientes[i - 1] if i - 1 < len(clientes) else {}
        yaml["services"][f"client{i}"] = {
            "container_name": f"client{i}",
            "image": "client:latest",
            "entrypoint": "/client",
            "environment": [
                f"CLI_ID={i}",
            ],
            "networks": ["testing_net"],
            "depends_on": ["server"],
            "volumes": [
                f"./client/config.yaml:/config.yaml",
                f"./.data/dataset/agency-{i}.csv:/agency.csv"
            ]
        }

    return yaml
   


def generar_docker_compose(nombre_archivo, cantidad_clientes):
    clientes = cargar_clientes_desde_archivo()
    with open(nombre_archivo, "w") as archivo:
        yaml.dump(generar_yaml(cantidad_clientes, clientes), archivo)



if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)
    generar_docker_compose(sys.argv[1], sys.argv[2])