# ReplicatedLogV1

Command to launch app

- docker build -t replicated_log:v1 .
- docker-compose up



## APP Description
The Replicated Log should have the following deployment architecture: one Master and any number of Secondaries.
Master expose a simple HTTP server with: 
- POST method - appends a message into the in-memory list
- GET method - returns all messages from the in-memory list

Secondary should expose a simple  HTTP server(or alternative service with a similar API)  with:
- GET method - returns all replicated messages from the in-memory list

Properties and assumptions:
- after each POST request, the message should be replicated on every Secondary server
  - Implemented in replication_on_secondary function
- Master should ensure that Secondaries have received a message via ACK
  - In replication_on_secondary raise an Exception in case when responce doesn't have ACK
  - Exception handle in handle_request_exception route
- Master’s POST request should be finished only after receiving ACKs from all Secondaries (blocking replication approach)
  - Only after succeed in replication_on_secondary message will be save in master
- to test that the replication is blocking, introduce the delay/sleep on the Secondary
  - In Docker you could stop any secondary server and try to sent a new message to Master
  - It raise requests.RequestException and send info about mistake
- at this stage assume that the communication channel is a perfect link (no failures and messages lost)
- any RPC framework can be used for Master-Secondary communication (Sockets, language-specific RPC, HTTP, Rest, gRPC, …)
  - This code implement Client-Server communication by Flask Framework 
- your implementation should support logging
  - Support, but not implemented as I get it right
- Master and Secondaries should run in Docker
  - Repo has DockerFile and docker-compose.yml to run it into Docker
