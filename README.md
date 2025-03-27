# TP0: Docker + Comunicaciones + Concurrencia

En el presente repositorio se provee un esqueleto básico de cliente/servidor, en donde todas las dependencias del mismo se encuentran encapsuladas en containers. Los alumnos deberán resolver una guía de ejercicios incrementales, teniendo en cuenta las condiciones de entrega descritas al final de este enunciado.

 El cliente (Golang) y el servidor (Python) fueron desarrollados en diferentes lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden convivir en el mismo proyecto con la ayuda de containers, en este caso utilizando [Docker Compose](https://docs.docker.com/compose/).

## Instrucciones de uso
El repositorio cuenta con un **Makefile** que incluye distintos comandos en forma de targets. Los targets se ejecutan mediante la invocación de:  **make \<target\>**. Los target imprescindibles para iniciar y detener el sistema son **docker-compose-up** y **docker-compose-down**, siendo los restantes targets de utilidad para el proceso de depuración.

Los targets disponibles son:

| target  | accion  |
|---|---|
|  `docker-compose-up`  | Inicializa el ambiente de desarrollo. Construye las imágenes del cliente y el servidor, inicializa los recursos a utilizar (volúmenes, redes, etc) e inicia los propios containers. |
| `docker-compose-down`  | Ejecuta `docker-compose stop` para detener los containers asociados al compose y luego  `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene de versiones de desarrollo y recursos sin liberar. |
|  `docker-compose-logs` | Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose. |
| `docker-image`  | Construye las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para probar nuevos cambios en las imágenes antes de arrancar el proyecto. |
| `build` | Compila la aplicación cliente para ejecución en el _host_ en lugar de en Docker. De este modo la compilación es mucho más veloz, pero requiere contar con todo el entorno de Golang y Python instalados en la máquina _host_. |

### Servidor

Se trata de un "echo server", en donde los mensajes recibidos por el cliente se responden inmediatamente y sin alterar. 

Se ejecutan en bucle las siguientes etapas:

1. Servidor acepta una nueva conexión.
2. Servidor recibe mensaje del cliente y procede a responder el mismo.
3. Servidor desconecta al cliente.
4. Servidor retorna al paso 1.


### Cliente
 se conecta reiteradas veces al servidor y envía mensajes de la siguiente forma:
 
1. Cliente se conecta al servidor.
2. Cliente genera mensaje incremental.
3. Cliente envía mensaje al servidor y espera mensaje de respuesta.
4. Servidor responde al mensaje.
5. Servidor desconecta al cliente.
6. Cliente verifica si aún debe enviar un mensaje y si es así, vuelve al paso 2.

### Ejemplo

Al ejecutar el comando `make docker-compose-up`  y luego  `make docker-compose-logs`, se observan los siguientes logs:

```
client1  | 2024-08-21 22:11:15 INFO     action: config | result: success | client_id: 1 | server_address: server:12345 | loop_amount: 5 | loop_period: 5s | log_level: DEBUG
client1  | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:14 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2024-08-21 22:11:14 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°3
client1  | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°3
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°5
client1  | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°5
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:40 INFO     action: loop_finished | result: success | client_id: 1
client1 exited with code 0
```


## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°1:
Definir un script de bash `generar-compose.sh` que permita crear una definición de Docker Compose con una cantidad configurable de clientes.  El nombre de los containers deberá seguir el formato propuesto: client1, client2, client3, etc. 

El script deberá ubicarse en la raíz del proyecto y recibirá por parámetro el nombre del archivo de salida y la cantidad de clientes esperados:

`./generar-compose.sh docker-compose-dev.yaml 5`

Considerar que en el contenido del script pueden invocar un subscript de Go o Python:

```
#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
python3 mi-generador.py $1 $2
```

En el archivo de Docker Compose de salida se pueden definir volúmenes, variables de entorno y redes con libertad, pero recordar actualizar este script cuando se modifiquen tales definiciones en los sucesivos ejercicios.

### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera reconstruír las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida por fuera de la imagen (hint: `docker volumes`).


### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). `


### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.



#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).


### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). 
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento.

La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los archivos deberán ser inyectados en los containers correspondientes y persistido por fuera de la imagen (hint: `docker volumes`), manteniendo la convencion de que el cliente N utilizara el archivo de apuestas `.data/agency-{N}.csv` .

En el servidor, si todas las apuestas del *batch* fueron procesadas correctamente, imprimir por log: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}`. En caso de detectar un error con alguna de las apuestas, debe responder con un código de error a elección e imprimir: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD_DE_APUESTAS}`.

La cantidad máxima de apuestas dentro de cada _batch_ debe ser configurable desde config.yaml. Respetar la clave `batch: maxAmount`, pero modificar el valor por defecto de modo tal que los paquetes no excedan los 8kB. 

Por su parte, el servidor deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

## Parte 3: Repaso de Concurrencia
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

## Condiciones de Entrega
Se espera que los alumnos realicen un _fork_ del presente repositorio para el desarrollo de los ejercicios y que aprovechen el esqueleto provisto tanto (o tan poco) como consideren necesario.

Cada ejercicio deberá resolverse en una rama independiente con nombres siguiendo el formato `ej${Nro de ejercicio}`. Se permite agregar commits en cualquier órden, así como crear una rama a partir de otra, pero al momento de la entrega deberán existir 8 ramas llamadas: ej1, ej2, ..., ej7, ej8.
 (hint: verificar listado de ramas y últimos commits con `git ls-remote`)

Se espera que se redacte una sección del README en donde se indique cómo ejecutar cada ejercicio y se detallen los aspectos más importantes de la solución provista, como ser el protocolo de comunicación implementado (Parte 2) y los mecanismos de sincronización utilizados (Parte 3).

Se proveen [pruebas automáticas](https://github.com/7574-sistemas-distribuidos/tp0-tests) de caja negra. Se exige que la resolución de los ejercicios pase tales pruebas, o en su defecto que las discrepancias sean justificadas y discutidas con los docentes antes del día de la entrega. El incumplimiento de las pruebas es condición de desaprobación, pero su cumplimiento no es suficiente para la aprobación. Respetar las entradas de log planteadas en los ejercicios, pues son las que se chequean en cada uno de los tests.

La corrección personal tendrá en cuenta la calidad del código entregado y casos de error posibles, se manifiesten o no durante la ejecución del trabajo práctico. Se pide a los alumnos leer atentamente y **tener en cuenta** los criterios de corrección informados  [en el campus](https://campusgrado.fi.uba.ar/mod/page/view.php?id=73393).


# Explicación de Resolución

### Instalación de dependencias

Se recomienda instalar `pyyaml` para manejar la generación del archivo `docker-compose-dev.yaml` desde el script Bash:

```bash
python3 -m pip install pyyaml
```

## Ejercicio 1

Para resolver este ejercicio, se utilizó el mismo script de Bash (`generar-compose.sh`) sugerido en la consigna, el cual invoca un script en Python (`mi-generador.py`).

En `mi-generador.py`, se emplea la librería `yaml` para generar dinámicamente un archivo `docker-compose-dev.yaml`. Para lograr esto, se creo un diccionario en Python que replica la estructura original del `docker-compose-dev.yaml`, modificando solo la cantidad de clientes de acuerdo con el parametro recibido. Esto garantiza una generación de YAML estructurada y sin errores de indentación.

### Ejecución
El script se ejecuta con el siguiente comando:
```bash
./generar-compose.sh <nombre archivo salida> <cantidad clientes>
```

## Ejercicio 2
Se agregó una sección de volúmenes en `mi-generador.py` para inyectar los archivos de configuración en los contenedores del servidor y los clientes. Esto permite modificar la configuración sin necesidad de reconstruir las imagenes de Docker.

Los volumenes montan `config.ini` en el servidor y `config.yaml` en los clientes.

## Ejercicio 3
Se creó un script de Bash (`validar-echo-server.sh`) que utiliza `netcat` para verificar el correcto funcionamiento del servidor echo. Utilizando el network name `tp0_testing_net`. Se envía un mensaje al servidor y se compara la respuesta con el mensaje original.

### Ejecución
```sh
./validar-echo-server.sh
```

Si la respuesta coincide con el mensaje enviado, imprime:
```sh
action: test_echo_server | result: success
```
De lo contrario:
```sh
action: test_echo_server | result: fail
```

## Ejercicio 4
Se modifico tanto el server en su funcion `run`, como al cliente en su funcion `StartClientLoop` para que capturen la señal `SIGTERM`.  
El cliente simplemente captura la señal y cierra su socket.  
El server ademas cierra todas sus conexiones al recibir la señal, esto se logra ya que se agrego una lista con todos los sockets cada vez que se genera una conexion con un nuevo cliente.

### Ejecución
Primero ejecutar `make docker-compose-up` en una terminal, luego en otra terminal `make docker-compose-logs`, finalmente utilizar la primera para cerrar los contenedores con `make docker-compose-down`.  
Lo que se vera seran los logs indicando los cierres exitosos tanto de los clientes como del server.  
Del lado del cliente:  
```sh
"Client <id>: Received SIGTERM. Closing connection"
client<id> exited with code 0
```
Del lado del server:  
```sh
"Server: Recibida señal SIGTERM. Cerrando conexiones"
server exited with code 0
```
Para cada uno de sus clientes:
```sh
action: closing_socket | result: success
```

## Ejercicio 5
Se creó un archivo `clientes.yaml` que contiene una lista con los datos de los clientes en el siguiente formato:

```yaml
clientes:
  - NOMBRE: "Santiago"
    APELLIDO: "Lorca"
    DOCUMENTO: "30904465"
    NACIMIENTO: "1999-03-17"
    NUMERO: "7574"
  - NOMBRE: "Maria"
    APELLIDO: "Gomez"
    DOCUMENTO: "40123456"
    NACIMIENTO: "2000-05-22"
    NUMERO: "1234"
```
Se modificó el script `my-generador.py` para que estos datos sean utilizados y pasados como variables de entorno a los contenedores de los clientes.

#### Cliente
- Se implementó la función `ManageBet`, encargada de serializar la apuesta del cliente y enviarla al servidor.
- Se modificó `StartClientLoop` para abrir una nueva conexión en cada iteración y enviar la apuesta correspondiente.

#### Servidor
- Se modificó `__handle_client_connection` para recibir y procesar las apuestas de los clientes.

## Protocolo de Comunicación
1. **El cliente envía un `uint32`** con el tamaño del mensaje.
2. **El cliente envía el mensaje**, que es un string con el siguiente formato:
   ```
   id|nombre|apellido|dni|nacimiento|numero
   ```
3. **El servidor recibe el `uint32`**, lo interpreta como el tamaño del mensaje.
4. **El servidor recibe el mensaje**, lo parsea y lo almacena utilizando `store_bets`.
5. **El servidor registra la apuesta en los logs** y envía al cliente un byte:
   - `1` si la apuesta se procesó con éxito.
   - `0` si ocurrió un error.
6. **El cliente recibe el byte de respuesta** e imprime en los logs si la apuesta fue `success` o `fail`.

### Ejecución
Generar el archivo `docker-compose-dev.yaml`:
   ```sh
   ./generar-compose.sh docker-compose-dev.yaml 5
   ```
Levantar los contenedores:
   ```sh
   make docker-compose-up
   ```
Observar los logs en otra terminal:
   ```sh
   make docker-compose-logs
   ```
Se podra observar:
#### Cliente
```sh
action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}
```

#### Servidor
```sh
action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}
```


## Ejercicio 6

#### Cliente

- Se reemplazó el uso de variables de entorno individuales por un archivo CSV que se monta como volumen en el contenedor. Ejemplo en `docker-compose-dev.yaml`:
- Se implementó un **parser** que lee el archivo CSV y las divide en **batches** según las restricciones definidas en `config.yaml`:
  - Cada batch contiene un número limitado de apuestas, evitando que se supere el tamaño máximo permitido.
  - Dentro de un batch, cada apuesta está representada como una cadena de texto con los campos separados por `|`, y las apuestas dentro del batch están separadas por `;`.
  - Este enfoque es más eficiente, ya que evita instanciar objetos innecesarios en memoria y simplifica la serialización de los datos antes de enviarlos al servidor.

#### Servidor

- Se introdujo un diccionario `sockets_id` para asignar un **ID único** a cada cliente basado en su dirección de socket. Esto evita que el cliente deba enviar su ID en cada mensaje y permite que el servidor gestione esta información internamente.

### Protocolo de comunicación

1. **El cliente envía un ****`uint32`**** (size)** indicando el tamaño del batch.
2. **El cliente envía un ****`uint32`**** (bets\_length)** con la cantidad de apuestas en el batch.
3. **El cliente envía el batch como un string**, con las apuestas separadas por `;` y los campos de cada apuesta separados por `|`.
   ```
   nombre|apellido|dni|nacimiento|numero
   ```
4. **El servidor recibe los datos y los procesa**:
   - Separa las apuestas y las almacena en una lista.
   - Valida que la cantidad de apuestas recibidas coincida con `bets_length`.
   - Si hay una diferencia, la reporta en los logs.
5. **El servidor responde con un byte**:
   - `0x00` si las apuestas se procesaron correctamente.
   - `0x01` si ocurrió un error.
   - `0x02` si solo alguna de las apuestas son incorrectas.

6. **El cliente recibe la respuesta y la registra en los logs.**

#### Finalización de la conexión

- Una vez que el cliente ha enviado todos sus batches, envía un `uint32` con valor `0`.
- El servidor interpreta este valor como un indicador de finalización y cierra la conexión con el cliente.

### Ejecución
   ```sh
   ./generar-compose.sh docker-compose-dev.yaml {cantidad clientez}
   ```
Levantar los contenedores:
   ```sh
   make docker-compose-up
   ```
Observar los logs en otra terminal:
   ```sh
   make docker-compose-logs
   ```
Se podra observar:

```sh
action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}
```

## Ejercicio 7

#### Cliente

- Ahora, una vez que los clientes envían sus **batches**, solicitan a los ganadores al servidor.
- Se mantiene el formato del archivo CSV para la carga de apuestas.
- Se agregó lógica para solicitar ganadores en caso de que el sorteo haya finalizado o reintentar si aún no ha ocurrido.

#### Servidor

- Se introdujo un diccionario `sockets_id` donde, para cada ID de cliente recibido, se asigna un **ID incremental** para vincularlo a una agencia. Esto se debe a que los IDs de agencia se asignan por orden de llegada, por lo que, por ejemplo, `client5` podría tener `id: 0`.
- Ahora el servidor conoce cuántos clientes debe esperar gracias al archivo de configuración (`config.yaml`).
- Cada cliente, al finalizar el envío de apuestas, informa al servidor con un **byte de finalización**. El servidor mantiene un registro (`agency_finish`) de qué clientes ya terminaron.
- Una vez que todos los clientes han informado su finalización, el servidor marca el sorteo como **finalizado** y lo reporta en los logs:
  ```sh
  action: sorteo | result: success
  ```
- Cuando un cliente solicita los ganadores, el servidor utiliza la función `get_winners()`, que internamente llama a `load_bets()` y `has_won()` para obtener los ganadores por agencia.

---

### Protocolo de comunicación

#### Envío de apuestas (`B` - Bets)

1. **El cliente envía un byte con el carácter `'B'`** indicando que enviará apuestas por **batches**.
2. **El servidor recibe los datos en el siguiente orden:**
   - `4 bytes (uint32)`: tamaño del mensaje.
   - `4 bytes (uint32)`: cantidad de apuestas en el batch.
   - `4 bytes (uint32)`: ID del cliente (se reintrodujo porque ahora los clientes abren y cierran conexiones, no era conveniente seguir vinculando los ids de agencias a los peer names).
   - **Batch de apuestas**: un string donde las apuestas están separadas por `;` y los campos dentro de cada apuesta por `|`.
3. **El servidor procesa los datos:**
   - Separa las apuestas y las almacena en una lista.
   - Valida que la cantidad de apuestas recibidas coincida con `bets_length`.
   - Si hay diferencias, lo registra en los logs.
4. **El servidor responde con un byte:**
   - `0x00`: si las apuestas se procesaron correctamente.
   - `0x01`: si ocurrió un error.
   - `0x02`: si algunas apuestas fueron incorrectas.
5. **El cliente recibe la respuesta y la registra en los logs.**
6. **Finalización:**
   - Una vez que el cliente ha enviado todos sus **batches**, envía un `uint32` con valor `0`.
   - El servidor interpreta esto como una señal de finalización y cierra la conexión con el cliente.

#### Solicitud de ganadores (`W` - Winners)

1. **El cliente envía un byte con el carácter `'W'`** indicando que solicita los ganadores del sorteo.
2. **El servidor puede responder de dos maneras:**
   - **Si el sorteo aún no ha finalizado:**
     - Envía un byte `'R'` (**Retry**) indicando que el cliente debe volver a intentarlo más tarde.
     - Ambos cierran la conexión.
     - El cliente espera un tiempo (`LoopPeriod` del archivo de configuración) y reintenta la solicitud.
   - **Si el sorteo ha finalizado:**
     - El servidor envía un byte `'S'` (**Sending**) indicando que enviará los datos.
     - El cliente le envia al servidor su id para que identifique que agencia le solicita sus ganadores.  
     - Luego, obtiene los ganadores para la agencia correspondiente al cliente.
     - Envía los **DNI de los ganadores** como un string separados por `;`.
     - El cliente separa la información y reporta la cantidad de ganadores en los logs.
     - Ambos cierran la conexión.

---

### Ejecución

Generar el archivo `docker-compose-dev.yaml` con el archivo de configuración de clientes:
```sh
./generar-compose.sh docker-compose-dev.yaml 5
```

Levantar los contenedores:
```sh
make docker-compose-up
```

Observar los logs en otra terminal:
```sh
make docker-compose-logs
```

Se podrá observar:
```sh
action: sorteo | result: success
```
```sh
action: consulta_ganadores | result: success | cant_ganadores: ${CANT}
```


## Ejercicio 8

En esta versión, se ha introducido la concurrencia para mejorar la eficiencia y el manejo de conexiones. Ahora, cada vez que un cliente se conecta, se lanza un proceso en paralelo para gestionar su comunicación con el servidor. Estos procesos se almacenan y se cierran junto a los sockets cuando el servidor recibe una señal `SIGTERM`.

Se han implementado tres instancias de exclusión mutua (`Lock`) para garantizar el acceso seguro a los recursos compartidos:
1. **`get_winners`**: Asegura un acceso seguro al archivo CSV de apuestas cuando se consultan los ganadores.
2. **`save_bets`**: Protege la escritura en el archivo CSV cuando se almacenan nuevas apuestas.
3. **`clients_agency`**: Administra la asignación de IDs de clientes de manera segura.

Otro cambio fundamental es que los clientes ahora mantienen una única conexión abierta durante toda la ejecución. Esto optimiza el uso de memoria y simplifica la gestión de conexiones, ya que los clientes no necesitan cerrar y reabrir sockets para solicitar los ganadores. En consecuencia, los IDs de los clientes vuelven a ser administrados exclusivamente por el servidor, vinculándolos con su `peer name`.

---

### Protocolo de comunicación - Version definitiva

#### Envío de apuestas (`B` - Bets)

1. **El cliente envía un byte con el carácter `'B'`** indicando que enviará apuestas por **batches**.
2. **El servidor recibe los datos en el siguiente orden:**
   - `4 bytes (uint32)`: tamaño del mensaje.
   - `4 bytes (uint32)`: cantidad de apuestas en el batch.
   - **Batch de apuestas**: un string donde las apuestas están separadas por `;` y los campos dentro de cada apuesta por `|`.
   ```
   nombre|apellido|dni|nacimiento|numero
   ```
3. **El servidor procesa los datos:**
   - Separa las apuestas y las almacena en una lista.
   - Valida que la cantidad de apuestas recibidas coincida con `bets_length`.
   - Si hay diferencias, lo registra en los logs.
4. **El servidor responde con un byte:**
   - `0x00`: si las apuestas se procesaron correctamente.
   - `0x01`: si ocurrió un error.
   - `0x02`: si algunas apuestas fueron incorrectas.
5. **El cliente recibe la respuesta y la registra en los logs.**
6. **Finalización:**
   - El cliente envía un byte con valor `0` en el tamaño del mensaje, lo que indica el fin del envío de apuestas.

#### Solicitud de ganadores (`W` - Winners)

1. **El cliente envía un byte con el carácter `'W'`** indicando que solicita los ganadores del sorteo.
2. **El servidor puede responder de dos maneras:**
   - **Si el sorteo aún no ha finalizado:**
     - Envía un byte `'R'` (**Retry**) indicando que el cliente debe volver a intentarlo más tarde.
     - El cliente espera un tiempo (`LoopPeriod` del archivo de configuración) y reintenta la solicitud.
   - **Si el sorteo ha finalizado:**
     - El servidor envía un byte `'S'` (**Sending**) indicando que enviará los datos.
     - El servidor obtiene los ganadores para la agencia correspondiente al cliente.
     - Envía los **DNI de los ganadores** como un string separados por `;`.
     - El cliente separa la información y reporta la cantidad de ganadores en los logs.
     - Ambos cierran la conexión.

---

### Ejecución

Generar el archivo `docker-compose-dev.yaml` con el archivo de configuración de clientes:
```sh
./generar-compose.sh docker-compose-dev.yaml 5
```

Levantar los contenedores:
```sh
make docker-compose-up
```

Observar los logs en otra terminal:
```sh
make docker-compose-logs
```

Se podrá observar:
```sh
action: sorteo | result: success
```
```sh
action: consulta_ganadores | result: success | cant_ganadores: ${CANT}
```

