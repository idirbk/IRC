#!/bin/bash

# Start the Python server
echo "Starting the server..."
python3 server.py 7984 &
SERVER_PID=$!
sleep 2  # Gives the server time to start up

# Start two instances of the Python client
echo "Starting the first client..."
python3 userInterface.py 7984 idir&
#echo "Starting the second client..."
#python3 userInterface.py 8380 farid&

# Wait for the user to press any key to terminate the clients and the server
read -n 1 -s -r -p "Press any key to stop the server and clients"

# Kill the server and clients
echo "Stopping the clients and server..."
kill $SERVER_PID
pkill -P $$ python

echo "All processes stopped."
