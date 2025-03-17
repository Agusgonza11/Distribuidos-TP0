#!/bin/bash
SERVER_NAME="server"
SERVER_PORT=12345
NETWORK_NAME="tp0_testing_net"
MESSAGE="Hola mundo"

RESPONSE=$(docker run --rm --network="$NETWORK_NAME" busybox sh -c "echo '$MESSAGE' | nc $SERVER_NAME $SERVER_PORT")
echo "$RESPONSE"

if [ "$RESPONSE" = "$MESSAGE" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi