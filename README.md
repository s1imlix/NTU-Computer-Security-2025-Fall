# NTU Computer Security 計算機安全 (交大程式安全) 2025 Fall

## Info
This is an archive of the course Computer Security Fall 2025 by Hsu-Chun Hsiao 蕭旭君 @ CSIE NTU Taiwan, including my own solutions. **Disclaimer: I do not own the source code to the homework problems nor the labs.** 
- [Course website (NTU VPN required)](https://edu-ctf.csie.org/)

### Lecturer
- Crypto: maple3142
- Reverse: TwinkleStar03
- Pwn: nella17
- Web: lebronli1986
### Public resources
- [How-to-Hack-Websites](https://github.com/splitline/How-to-Hack-Websites)
### Environment
Most challenge can be brought up/down with `docker-compose`.

```sh
docker compose up -d
docker compose down
```

For Pwn challenges, [`nella17/docker-vm`](https://github.com/nella17/docker-vm) is very useful in setting up a local environment for testing your exploit.
## Homework/Lab
For the homework part, all problem except `[Pwn] todolist` are solved. 
Refer to the directories `hw[0-5]/`. All of them has similar directory structure:

```
hw0
├── problem_name
│   ├── solve.py
│   └── src
└── hw0.pdf
```

where problem solution scripts are under `problem_name/` and sources are in `problem_name/src`. `hw[0-5].pdf` are the write-up for the corresponding homework.

As for the labs, only Pwn labs (except `orw`, `Double Free`) are available, they are under `lab/pwn_labs`. 
### Crypto

| Name                                   | Topics                                     |
| -------------------------------------- | ------------------------------------------ |
| [[hw0] crypto](hw0/crypto)             | `Probability Theory`                       |
| [[hw1] cbc-revenge](hw1/cbc-revenge)   | `CBC padding oracle`                       |
| [[hw1] rng](hw1/rng)                   | `LFSR`, `PyRandom Cracking`                |
| [[hw5] Cosmic Ray](hw5/cosmic_ray)     | `Franklin-Reiter related message`          |
| [[hw5] Hidden Curve](hw5/hidden_curve) | `Singular Curve`, `Anomalous Curve`, `CRT` |
| [[hw5] One Key](hw5/one_key)           | `LLL`                                      |
| [[hw5] Not Random](hw5/not_random)     | `LLL`, `Hidden Number Problem`             |
### Pwn
| Name                                                    | Topics                             |
| ------------------------------------------------------- | ---------------------------------- |
| [[hw0] pwn](hw0/pwn)                                    | `Buffer overflow`                  |
| [[hw1] sc++](hw1/sc++)                                  | `Canary Leak`, `ret2win`           |
| [[hw1] STAR machine (pwn)](hw1/starvm-pwn)              | `VM Reverse`, `ROP`, `ret2win`     |
| [[hw4] GoGoGo](hw4/gogogo)                              | `GOT Overwrite`, `ret2main`        |
| [[hw4] uptime](hw4/uptime)                              | `Heap overflow`, `fmtstr`          |
| [[hw4] todolist easy](hw4/todolist_easy)                | `fastbin dup`, `Hook overwrite`    |
| [[hw4] todolist](hw4/todolist)                          |                                    |
| [[lab] Shellcode](lab/pwn_labs/shellcode)               | `Shellcode`                        |
| [[lab] BoF](lab/pwn_labs/bof)                           | `Buffer overflow`                  |
| [[lab] GOT](lab/pwn_labs/got)                           | `GOT Overwrite`                    |
| [[lab] ROP](lab/pwn_labs/rop)                           | `ROPGadget`                        |
| [[lab] StackPivot](lab/pwn_labs/shellcode)              | `Shellcode`                        |
| [[lab] orw](lab/pwn_labs/orw)                           |                                    |
| [[lab] ret2plt](lab/pwn_labs/ret2plt)                   | `ret2plt`                          |
| [[lab] fmt](lab/pwn_labs/fmt)                           | `fmtstr`                           |
| [[lab] heapmath](lab/pwn_labs/heapmath)                 | `ptalloc heap`                     |
| [[lab] Double Free](lab/pwn_labs/double-free)           |                                    |
| [[lab] Double Free Easy](lab/pwn_labs/double-free-easy) | `UAF`, `tcache Poisoning`          |
| [[lab] UAF Easy](lab/pwn_labs/uaf-easy)                 | `tcache Poisoning`, `Safe Linking` |
| [[lab] UAF](lab/pwn_labs/uaf)                           | `tcache Poisoning`                 |

### Web
| Name                                                         | Topics                            |
| ------------------------------------------------------------ | --------------------------------- |
| [[hw0] web](hw0/web)                                         | `Basics`                          |
| [[hw1] Ping as a Service](hw1/paas)                          | `WAF bypass`, `Command injection` |
| [[hw1] SurrealQL Injection](hw1/surrealql)                   | `SQLi`                            |
| [[hw3] Flag Vault - FLAG1](hw3/flag-vault)                   | `SSTI`, `Session Forgery`         |
| [[hw3] Flag Vault - FLAG2](hw3/flag-vault)                   | `Self XSS`, `CSRF`                |
| [[hw3] Private Wayback Machine](hw3/private-wayback-machine) | `gopher:// SSRF`, `POP Chain`     |
### Reverse
| Name                                            | Topics               |
| ----------------------------------------------- | -------------------- |
| [[hw0] reverse](hw0/reverse)                    | `Basics`             |
| [[hw1] checker](hw1/checker)                    | `IDA Basics`         |
| [[hw1] STAR machine (rev)](hw2/rev)             | `VM Reverse`         |
| [[hw2] tro - Preflight Check](hw2/tro)          | `Windows PE Reverse` |
| [[hw2] tro - Payload Decryption v1/v2](hw2/tro) | `Windows PE Reverse` |
| [[hw2] tro - Stolen Data](hw2/tro)              | `Windows PE Reverse` |
## Final CTF
The finals for this year's course is AIS3 EOF 2026 Qual. Our team `f4k3_b413n` ended up in 5th place with a total of 2863 points. My own write-up for the problems I contributed to is included at `final/final.pdf`.

## Other CTF
For other participation, I participated in [niteCTF 2025](https://ctftime.org/event/2851/) and [V1t CTF 2025](https://ctftime.org/event/2920). The write-up can also be found at `other/other.pdf`.




