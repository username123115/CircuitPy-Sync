
I want to sync stuff to circuitpython but web is slow and crappy and my device doesn't show up as a boot drive, so I wrote a crappier (but maybe less slow) way to sync files over usb cable


Client:

# Commands:

| Name               | Function                            | Code                    |
| ------------------ | ----------------------------------- | ----------------------- |
| Quit               | Client exit                         | `q`                     |
| Enter              | Enter a directory or return failure | `cd <dir>`              |
| List               | List files                          | `ls <file>`             |
| Checksum           | Get checksum of file                | `chksum <file>`         |
| Transfer Write<br> | Begin write                         | `tw <file> <n>`         |
| Transfer Read      | Begin read                          | `tr <file> <bl = 1024>` |

# User utils (do later)

| Name   | Function    | Code                   |
| ------ | ----------- | ---------------------- |
| Read   | Read file   | `cat <file>`           |
| Write  | Write File  | `wn <file> <contents>` |
| Append | Append File | `wa [file] <contents>` |

# Transfer commands
| Name              | Function   | Code         |
| ----------------- | ---------- | ------------ |
| Transfer          | Send bytes | `tr <bytes>` |
| Transfer verified |            |              |

