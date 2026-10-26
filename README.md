# OSLab — CPU Scheduling Algorithm Simulator

A desktop Operating Systems project built with Python, Tkinter, and Matplotlib.

## Features

- FCFS (First Come, First Served)
- SJF (non-preemptive)
- SRTF (preemptive)
- Priority scheduling (non-preemptive; lower number = higher priority)
- Round Robin with configurable time quantum
- Gantt chart
- Completion, turnaround, waiting, and response times
- Average waiting, turnaround, and response times
- CPU utilization and throughput
- Compare all five algorithms
- Export results and Gantt segments to CSV

## Requirements

- Python 3.10 or later recommended
- VS Code (optional)
- Matplotlib
- Tkinter (included with most standard Windows Python installations)

## Setup on Windows

1. Extract the ZIP folder.
2. Open the extracted `OSLab_CPU_Scheduling_Simulator` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt instead:

   ```bat
   .venv\Scripts\activate.bat
   ```

5. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

6. Start the application:

   ```powershell
   py main.py
   ```

## Quick start

- Sample processes load automatically.
- Select an algorithm and click **Run Simulation**.
- Click **Compare All Algorithms** to compare the five algorithms.
- Click **Export Results to CSV** to save the currently displayed result.

## Project structure

```text
OSLab_CPU_Scheduling_Simulator/
├── main.py          # Frontend / desktop GUI
├── scheduler.py     # Backend scheduling algorithms and metrics
├── requirements.txt # Python dependency list
└── README.md        # Setup and usage instructions
```

## Scheduling formulas

- Turnaround Time = Completion Time − Arrival Time
- Waiting Time = Turnaround Time − Burst Time
- Response Time = First CPU Start Time − Arrival Time
- CPU Utilization = Busy CPU Time / Elapsed Simulation Time × 100
- Throughput = Number of completed processes / Elapsed Simulation Time

The simulation's elapsed time is measured from the first process arrival until the last completion.

## Notes and assumptions

- Arrival times, burst times, and Round Robin quantum use integer time units.
- Burst times and quantum must be positive.
- Arrival times cannot be negative.
- Process IDs must be unique.
- SJF and Priority are non-preemptive in this version.
- SRTF is preemptive.
- Smaller priority numbers represent higher priority.
- This is a simulator for learning; it does not alter Windows or Linux CPU scheduling.
