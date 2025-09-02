# F1 Championship Helper

A friendly **command-line tool** to help you track **Formula 1 driver and constructor championship standings** and see if they’re still in contention for the title.  

---

## Features

- Check if a **driver is still in the running** for the World Drivers’ Championship (WDC)  
- Detailed weekend-by-weekend analysis with realistic point scenarios  
- Check if a **constructor can still win** the World Constructors’ Championship (WCC)  
- Fetches **up-to-date F1 season schedules** using FastF1

---

## Installation

You can install directly from GitHub for development:  

```bash
pip install f1-helper
```
After installation, run the CLI globally:
```bash
f1-helper
```
---
## Usage
Once started, you’ll see a simple menu:
```plaintext
--- F1 Championship Helper ---
1. Check Driver WDC Contention (simple)
2. Check Driver WDC Detailed Scenario
3. Check Constructor WCC Contention
4. Exit
```
### Examples
- Simple driver check:
```plaintext
f1-helper
Enter option: 1
Enter Driver Name: Lewis Hamilton
```
- Detailed driver scenario:
```plaintext
f1-helper
Enter option: 2
Enter Driver Name: Max Verstappen
```
- Constructor check:
```plaintext
f1-helper
Enter option: 3
Enter Constructor Name: Ferrari
```
---
## Dependencies
- **fastf1** – for F1 data and race schedules
- **tabulate** – for pretty tables in the terminal
---
## License

MIT License © 2025 Saur Deshmukh.