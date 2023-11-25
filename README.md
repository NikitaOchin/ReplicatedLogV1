# ReplicatedLog
Command to launch app

- docker build -t replicated_log:v2 .
- docker-compose up


## ReplicatedLogV2 with condition or Event

### Log for Write Concern equal to 1 
```
master_1      | [2023-11-24 08:10:13,124] DEBUG in master: New message is correct
master_1      | [2023-11-24 08:10:13,124] DEBUG in master: Write concern is 1
master_1      | [2023-11-24 08:10:13,124] DEBUG in master: Replication for master was ended
master_1      | [2023-11-24 08:10:13,125] INFO in master: Replication was ended
master_1      | [2023-11-24 08:10:13,125] DEBUG in master: Start replication for http://secondary1:5000
master_1      | [2023-11-24 08:10:13,126] DEBUG in master: Start replication for http://secondary2:5000
master_1      | 172.22.0.1 - - [24/Nov/2023 08:10:13] "POST /append HTTP/1.1" 201 -
```

Here is given that code didn't send the request to any secondary 
Debug message -- DEBUG in master: Start replication for http://secondary2:5000 -- say, that async function was started, but not continued 

### Log for Write Concern equal to 2
```
master_1      | [2023-11-24 08:10:15,586] DEBUG in master: New message is correct
master_1      | [2023-11-24 08:10:15,586] DEBUG in master: Write concern is 2
master_1      | [2023-11-24 08:10:15,586] DEBUG in master: Replication for master was ended
master_1      | [2023-11-24 08:10:15,586] DEBUG in master: Start replication for http://secondary1:5000
master_1      | [2023-11-24 08:10:15,587] DEBUG in master: Start replication for http://secondary2:5000
secondary1_1  | [2023-11-24 08:10:15,604] INFO in secondary: New message is [2, 'Hello, World 212312322222!'] with delay 7
secondary2_1  | [2023-11-24 08:10:15,606] INFO in secondary: New message is [2, 'Hello, World 212312322222!'] with delay 6
secondary2_1  | [2023-11-24 08:10:21,678] INFO in secondary: End replicate message [2, 'Hello, World 212312322222!']
secondary2_1  | 172.22.0.3 - - [24/Nov/2023 08:10:21] "POST /append HTTP/1.1" 201 -
master_1      | [2023-11-24 08:10:21,681] DEBUG in master: Replication for http://secondary2:5000 was ended
master_1      | [2023-11-24 08:10:21,681] INFO in master: Replication was ended
master_1      | 172.22.0.1 - - [24/Nov/2023 08:10:21] "POST /append HTTP/1.1" 201 -
secondary1_1  | [2023-11-24 08:10:22,617] INFO in secondary: End replicate message [2, 'Hello, World 212312322222!']
secondary1_1  | 172.22.0.3 - - [24/Nov/2023 08:10:22] "POST /append HTTP/1.1" 201 -'
```

Here is given that code didn't send the log from master about finishing replication on 1st secondary 


### Log for Write Concern equal to 3
```
master_1      | [2023-11-24 08:10:27,050] DEBUG in master: New message is correct
master_1      | [2023-11-24 08:10:27,051] DEBUG in master: Write concern is 3
master_1      | [2023-11-24 08:10:27,051] DEBUG in master: Replication for master was ended
master_1      | [2023-11-24 08:10:27,051] DEBUG in master: Start replication for http://secondary1:5000
master_1      | [2023-11-24 08:10:27,052] DEBUG in master: Start replication for http://secondary2:5000
secondary1_1  | [2023-11-24 08:10:27,059] INFO in secondary: New message is [3, 'Hello, World 212312322222!'] with delay 10
secondary2_1  | [2023-11-24 08:10:27,064] INFO in secondary: New message is [3, 'Hello, World 212312322222!'] with delay 4
secondary2_1  | [2023-11-24 08:10:31,075] INFO in secondary: End replicate message [3, 'Hello, World 212312322222!']
secondary2_1  | 172.22.0.3 - - [24/Nov/2023 08:10:31] "POST /append HTTP/1.1" 201 -
master_1      | [2023-11-24 08:10:31,079] DEBUG in master: Replication for http://secondary2:5000 was ended
```

Only here all log was sent
