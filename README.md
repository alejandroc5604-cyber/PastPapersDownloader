# Past Papers Downloader



Downloads past papers in bulk from [PapaCambridge](https://papacambridge.com/)
## Installation
*_You can use any of the following 3_*
1. Use git (type this into powershell or your terminal):
```git
git clone https://github.com/alejandroc5604-cyber/PastPapersDownloader
```
2. Use GitHub CLI (also type this into powershell or your terminal):
```Bash
gh repo clone alejandroc5604-cyber/PastPapersDownloader
```
3. Download directly (you'll have to extract the files):

> <kbd>[**DOWNLOAD ME!**](https://github.com/alejandroc5604-cyber/PastPapersDownloader/archive/refs/heads/main.zip)</kbd>





## Usage

```python
python CLI.py
```
This will open the semi-graphical interface. Use arrow keys to navigate the syllabus:
~~~
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Past Paper Downloader                                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────── Select Option [Use Arrow Keys & Enter] ─────────╮╭──────────────── Downloaders (3 workers) ─────────────────╮
│   Biology                        (0970)                  ││ ╭────────────────────── Worker 0 ──────────────────────╮ │
│   Business Studies               (0450)                  ││ │ Worker Initialized                                   │ │
│   Business Studies               (0986)                  ││ ╰──────────────────────────────────────────────────────╯ │
│   Chemistry                      (0439)                  ││ ╭────────────────────── Worker 1 ──────────────────────╮ │
│  > Chemistry                      (0620)                 ││ │ Worker Initialized                                   │ │
│   Chemistry                      (0971)                  ││ ╰──────────────────────────────────────────────────────╯ │
│   Child Development              (0637)                  ││ ╭────────────────────── Worker 2 ──────────────────────╮ │
│   Chinese                        (0509)                  ││ │ Worker Initialized                                   │ │
│   Chinese                        (0523)                  ││ ╰──────────────────────────────────────────────────────╯ │
│   Chinese                        (0534)                  ││                                                          │
│   Chinese                        (0547)                  ││                                                          │
│   Computer Science               (0478)                  ││                                                          │
│   Computer Science               (0984)                  ││                                                          │
│   Computer Studies               (0420)                  ││                                                          │
│   Computer Studies               (0441)                  ││                                                          │
│   Czech First Language           (0514)                  ││                                                          │
│               ↓   ↓   ↓                                  ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
╰──────────────────────────────────────────────────────────╯╰──────────────────────────────────────────────────────────╯
~~~
>To download the selected, press
```Ctrl + Enter```. This will download the selected line (The selected line is represented by the slightly indented line, with a `>` and will be colored blue. Other lines are a simple white. _Note The example is not colored_ ). For example, if you have selected **Chemistry (0620)**, then pressed ```Ctrl + Enter```, all of **Chemistry (0620)** will be downloaded.
But maybe you do not want to download the entire syllabus, only a session from **Chemistry (0620)**. So you press ```Enter``` and access the sessions:
~~~
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Past Paper Downloader                                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────── Select Option [Use Arrow Keys & Enter] ─────────╮╭──────────────── Downloaders (3 workers) ─────────────────╮
│  > 2025 oct-nov                                          ││ ╭────────────────────── Worker 0 ──────────────────────╮ │
│   2025 may-june                                          ││ │ Worker Initialized                                   │ │
│   2025 march                                             ││ ╰──────────────────────────────────────────────────────╯ │
│   2024 oct-nov                                           ││ ╭────────────────────── Worker 1 ──────────────────────╮ │
│   2025 oct-nov                                           ││ │ Worker Initialized                                   │ │
│   2025 may-june                                          ││ ╰──────────────────────────────────────────────────────╯ │
│   2025 march                                             ││ ╭────────────────────── Worker 2 ──────────────────────╮ │
│   2024 oct-nov                                           ││ │ Worker Initialized                                   │ │
│   2024 may-june                                          ││ ╰──────────────────────────────────────────────────────╯ │
│   2024 march                                             ││                                                          │
│   2023 oct-nov                                           ││                                                          │
│   2023 may-june                                          ││                                                          │
│   2023 march                                             ││                                                          │
│   2022 oct-nov                                           ││                                                          │
│   2022 may-june                                          ││                                                          │
│   2022 feb-march                                         ││                                                          │
│  ↓   ↓   ↓                                               ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
│                                                          ││                                                          │
╰──────────────────────────────────────────────────────────╯╰──────────────────────────────────────────────────────────╯
~~~
Same thing applies;  ```Ctrl + Enter``` to download the entire session, or enter to fine tune the download. 
## How does it work?


This project is an [asynchronous](https://www.datacamp.com/tutorial/python-async-programming) (multiple tasks can be ran at once) terminal-based downloader for CAIE IGCSE past papers from [PapaCambridge](https://papacambridge.com/).

The interface is built with Rich, website data is gathered using 
[Playwright](https://playwright.dev/) and [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/), and downloads are handled using [aiohttp](https://docs.aiohttp.org/en/stable/) and [asyncio](https://realpython.com/async-io-python/).

 
The project consists of three main files:
```CLI.py```
```Utils.py```
```downloader.py```

```CLI.py```

This is the access to the user interface. It provides menus and navigation, subject/session/paper selection
and displaying worker status. This is the graphical part, built with the ```rich``` module. Its uses the ```keyboard``` module for user input`

```Utils.py```

This is mostly random functions which would've cluttered the CLI.py. This mainly handles fetching webpages (the past papers), extracting subjects, extracting sessions, extracting paper links and sorting the papers into their respective folders

```downloader.py```

In short, this has two classes, ``` Downloader``` which is the manager (tells the workers what to do) and the ```worker``` class, which carries out the tasks set by the downloader. The worker downloads directly the the storage, bypassing memeory for efficency.


When the program starts, a number of download workers are created.

```text
Downloader
├── Worker 0
├── Worker 1
└── Worker 2
```

Each worker waits for download jobs from an `asyncio.Queue`, which is controlled by the manager (the `Downloader` object)

When a paper is added the the `Queue`:

1. The next available worker takes the job.
2. The worker downloads the file using `aiohttp`.
3. The file is saved to disk.
4. The worker becomes available for another download.

Because the workers run asynchronously, multiple files can be downloaded at the same time without blocking the user interface.


Downloaded papers are automatically sorted into folders based on subject code, year, and session. To do this, a string is passed into the `utils.sorter` function. This creates the path where the worker is going to save the file it is downloading

Example using the preset string `$COURSE$/$CODE$/$YEAR$/$MONTH$`:

```text
IGCSE/
└── 0620/
    └── 2025/
        └── w25/
            ├── 0620_w25_qp_12.pdf
            └── 0620_w25_ms_12.pdf
```

---
## LICENSE

[MIT](https://choosealicense.com/licenses/mit/)

[MIT Local Copy](LICENSE.md)

In short, you can do anything, from copying, modifying, distributing and using, to all the way to sending it in a rocket to the moon, as long as credit is given. 
