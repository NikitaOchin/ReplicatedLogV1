# ReplicatedLog
Command to launch app

- docker build -t replicated_log:v2 .
- docker-compose up


## ReplicatedLogV2

### Logs for four running with different delays
Here is given, that since of delay, older message could be written on secondary after newest
```angular2html
master_1      | [2023-11-24 10:12:36,447] DEBUG in master: New message is correct
master_1      | [2023-11-24 10:12:36,456] DEBUG in master: Start replication for http://secondary1:5000
master_1      | [2023-11-24 10:12:36,456] DEBUG in master: Replication for master was ended
master_1      | [2023-11-24 10:12:36,457] DEBUG in CountDownLatch: awaiter with 2
master_1      | [2023-11-24 10:12:36,458] DEBUG in master: Start replication for http://secondary2:5000
secondary2_1  | [2023-11-24 10:12:36,470] INFO in secondary: New message is [1, 'Hello, World 212312322222!'] with delay 6
secondary1_1  | [2023-11-24 10:12:36,471] INFO in secondary: New message is [1, 'Hello, World 212312322222!'] with delay 6
master_1      | [2023-11-24 10:12:37,922] DEBUG in master: New message is correct
master_1      | [2023-11-24 10:12:37,926] DEBUG in master: Start replication for http://secondary1:5000
master_1      | [2023-11-24 10:12:37,927] DEBUG in master: Replication for master was ended
master_1      | [2023-11-24 10:12:37,928] DEBUG in CountDownLatch: awaiter with 0
master_1      | [2023-11-24 10:12:37,928] INFO in master: Replication was ended
master_1      | [2023-11-24 10:12:37,929] DEBUG in master: Start replication for http://secondary2:5000
master_1      | 172.22.0.1 - - [24/Nov/2023 10:12:37] "POST /append HTTP/1.1" 201 -
secondary2_1  | [2023-11-24 10:12:37,941] INFO in secondary: New message is [2, 'Hello, World 212312322222!'] with delay 9
secondary1_1  | [2023-11-24 10:12:37,943] INFO in secondary: New message is [2, 'Hello, World 212312322222!'] with delay 7
master_1      | [2023-11-24 10:12:39,051] DEBUG in master: New message is correct
master_1      | [2023-11-24 10:12:39,054] DEBUG in master: Start replication for http://secondary1:5000
master_1      | [2023-11-24 10:12:39,054] DEBUG in master: Replication for master was ended
master_1      | [2023-11-24 10:12:39,055] DEBUG in CountDownLatch: awaiter with 1
master_1      | [2023-11-24 10:12:39,056] DEBUG in master: Start replication for http://secondary2:5000
secondary1_1  | [2023-11-24 10:12:39,062] INFO in secondary: New message is [3, 'Hello, World 212312322222!'] with delay 6
secondary2_1  | [2023-11-24 10:12:39,064] INFO in secondary: New message is [3, 'Hello, World 212312322222!'] with delay 9
master_1      | [2023-11-24 10:12:40,369] DEBUG in master: New message is correct
master_1      | [2023-11-24 10:12:40,373] DEBUG in master: Replication for master was ended
master_1      | [2023-11-24 10:12:40,374] DEBUG in CountDownLatch: awaiter with 2
master_1      | [2023-11-24 10:12:40,374] DEBUG in master: Start replication for http://secondary1:5000
master_1      | [2023-11-24 10:12:40,375] DEBUG in master: Start replication for http://secondary2:5000
secondary1_1  | [2023-11-24 10:12:40,385] INFO in secondary: New message is [4, 'Hello, World 212312322222!'] with delay 12
secondary2_1  | [2023-11-24 10:12:40,386] INFO in secondary: New message is [4, 'Hello, World 212312322222!'] with delay 7
secondary2_1  | [2023-11-24 10:12:42,485] INFO in secondary: End replicate message [1, 'Hello, World 212312322222!']
secondary1_1  | [2023-11-24 10:12:42,484] INFO in secondary: End replicate message [1, 'Hello, World 212312322222!']
secondary2_1  | 172.22.0.4 - - [24/Nov/2023 10:12:42] "POST /append HTTP/1.1" 201 -
secondary1_1  | 172.22.0.4 - - [24/Nov/2023 10:12:42] "POST /append HTTP/1.1" 201 -
master_1      | [2023-11-24 10:12:42,488] DEBUG in master: Replication for http://secondary1:5000 was ended
master_1      | [2023-11-24 10:12:42,488] DEBUG in master: Replication for http://secondary2:5000 was ended
master_1      | [2023-11-24 10:12:42,489] DEBUG in CountDownLatch: count_down with 2
master_1      | [2023-11-24 10:12:42,489] DEBUG in CountDownLatch: count_down with 2
master_1      | [2023-11-24 10:12:42,489] INFO in master: Replication was ended
master_1      | 172.22.0.1 - - [24/Nov/2023 10:12:42] "POST /append HTTP/1.1" 201 -
secondary1_1  | [2023-11-24 10:12:45,069] INFO in secondary: End replicate message [3, 'Hello, World 212312322222!']
secondary1_1  | 172.22.0.4 - - [24/Nov/2023 10:12:45] "POST /append HTTP/1.1" 201 -
master_1      | [2023-11-24 10:12:45,072] DEBUG in master: Replication for http://secondary1:5000 was ended
master_1      | [2023-11-24 10:12:45,073] DEBUG in CountDownLatch: count_down with 1
master_1      | [2023-11-24 10:12:45,073] INFO in master: Replication was ended
master_1      | 172.22.0.1 - - [24/Nov/2023 10:12:45] "POST /append HTTP/1.1" 201 -
secondary1_1  | [2023-11-24 10:12:45,154] INFO in secondary: End replicate message [2, 'Hello, World 212312322222!']
secondary1_1  | 172.22.0.4 - - [24/Nov/2023 10:12:45] "POST /append HTTP/1.1" 201 -
master_1      | [2023-11-24 10:12:45,157] DEBUG in master: Replication for http://secondary1:5000 was ended
master_1      | [2023-11-24 10:12:45,158] DEBUG in CountDownLatch: count_down with 0
secondary2_1  | [2023-11-24 10:12:46,946] INFO in secondary: End replicate message [2, 'Hello, World 212312322222!']
secondary2_1  | 172.22.0.4 - - [24/Nov/2023 10:12:46] "POST /append HTTP/1.1" 201 -
master_1      | [2023-11-24 10:12:46,949] DEBUG in master: Replication for http://secondary2:5000 was ended
master_1      | [2023-11-24 10:12:46,949] DEBUG in CountDownLatch: count_down with -1
secondary2_1  | [2023-11-24 10:12:47,406] INFO in secondary: End replicate message [4, 'Hello, World 212312322222!']
secondary2_1  | 172.22.0.4 - - [24/Nov/2023 10:12:47] "POST /append HTTP/1.1" 201 -
master_1      | [2023-11-24 10:12:47,409] DEBUG in master: Replication for http://secondary2:5000 was ended
master_1      | [2023-11-24 10:12:47,410] DEBUG in CountDownLatch: count_down with 2
secondary2_1  | [2023-11-24 10:12:48,085] INFO in secondary: End replicate message [3, 'Hello, World 212312322222!']
secondary2_1  | 172.22.0.4 - - [24/Nov/2023 10:12:48] "POST /append HTTP/1.1" 201 -
master_1      | [2023-11-24 10:12:48,088] DEBUG in master: Replication for http://secondary2:5000 was ended
master_1      | [2023-11-24 10:12:48,088] DEBUG in CountDownLatch: count_down with -2
secondary1_1  | [2023-11-24 10:12:52,402] INFO in secondary: End replicate message [4, 'Hello, World 212312322222!']
secondary1_1  | 172.22.0.4 - - [24/Nov/2023 10:12:52] "POST /append HTTP/1.1" 201 -
master_1      | [2023-11-24 10:12:52,404] DEBUG in master: Replication for http://secondary1:5000 was ended
master_1      | [2023-11-24 10:12:52,404] DEBUG in CountDownLatch: count_down with 1
master_1      | [2023-11-24 10:12:52,405] INFO in master: Replication was ended
master_1      | 172.22.0.1 - - [24/Nov/2023 10:12:52] "POST /append HTTP/1.1" 201 -

```
