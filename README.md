# Dynamic Ambulance Allocation System

A Python implementation of a dynamic ambulance dispatch and routing system for emergency response optimization, developed for Design and Analysis of Algorithms (DAA).

## Overview

The system allocates available ambulances to incoming emergency calls across a road network graph. It minimizes response times using Dijkstra's algorithm while prioritizing emergencies by medical severity.

## Key Features

- **Shortest Path Routing**: Uses Dijkstra's algorithm (min-heap) to compute minimum travel times and routes.
- **Priority-Based Dispatch**: Sorts emergencies by severity (`Critical` > `Serious` > `Moderate`) and dispatches the closest available unit.
- **Dynamic Reallocation & Queue**: Places emergencies into a priority waiting queue when all ambulances are busy, automatically reassigning ambulances as calls complete.
- **Interactive CLI & Simulation**: Prompts for emergency inputs and simulates step-by-step dispatch, completion, and queue updates.

## Network & Fleet Configuration

- **Road Graph**: 5 nodes (`N1` to `N5`) with bidirectional weighted travel times (minutes).
- **Fleet**: Ambulances `A1` (starts at `N1`), `A2` (starts at `N4`), and `A3` (starts at `N2`).

- **Severity Levels**:
  - `Critical` (Priority 3)
  - `Serious` (Priority 2)
  - `Moderate` (Priority 1)

## How to Run

Requires Python 3 (uses standard library `heapq`, no external dependencies).

```bash
python main.py
```

Follow the terminal prompts to specify the number of emergencies, location node for each (`N1`–`N5`), and severity level (`1`–`3`).

