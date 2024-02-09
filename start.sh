################################################
#             Start the servers                #
################################################ 

echo "Starting the servers..."
python3 server.py 4084 &
SERVER1_PID=$!
sleep 1
python3 server.py 4085 4084&
SERVER2_PID=$!
sleep 1
python3 server.py 4086 4085&
SERVER3_PID=$!
sleep 1
################################################
#             Start the the clients            #
################################################ 
echo "Starting the clients..."
python3 userInterface.py 4084 jeff&

python3 userInterface.py 4085 linus&
python3 userInterface.py 4085 ken&

python3 userInterface.py 4086 bjarne&

read -n 1 -s -r -p "Press any key to stop the server and clients"

# Kill the server and clients
echo "Stopping the clients and server..."
kill $SERVER_PID
pkill -P $$ python

echo "All processes stopped."!
