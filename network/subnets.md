# Subnet allocation for 10.20.0.0/16

Method: allocate from the largest requirement to the smallest, starting at 10.20.0.0, each subnet placed right after
the previous one, using the smallest prefix p with 2^(32-p) - 2 >= hosts needed.

| Subnet | Hosts needed | Prefix chosen (why) | Network | Usable range | Broadcast | Usable hosts |
|---|---|---|---|---|---|---|
| app | 1000 | /22 (2^10-2 = 1022) | 10.20.0.0/22 | 10.20.0.1 - 10.20.3.254 | 10.20.3.255 | 1022 |
| public | 250 | /24 (2^8-2 = 254) | 10.20.4.0/24 | 10.20.4.1 - 10.20.4.254 | 10.20.4.255 | 254 |
| data | 100 | /25 (2^7-2 = 126) | 10.20.5.0/25 | 10.20.5.1 - 10.20.5.126 | 10.20.5.127 | 126 |
| management | 20 | /27 (2^5-2 = 30) | 10.20.5.128/27 | 10.20.5.129 - 10.20.5.158 | 10.20.5.159 | 30 |

Working: /23 gives 2^9-2 = 510 < 1000; /22 gives 2^10-2 = 1022 >= 1000. /24 gives 254 >= 250 (/25 gives only 126).
/25 gives 126 >= 100 (/26 gives 62). /27 gives 30 >= 20 (/28 gives 14).
