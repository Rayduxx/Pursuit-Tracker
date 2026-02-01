# Pursuit-Tracker

A simple, lightweight, and always-on-top racing timer application designed for tracking lap times and countdown assessments. Ideal for FiveM racing or any scenario requiring quick time checks.

## Features

- **Stopwatch / Timer**: Toggle start/stop with a global hotkey.
- **Countdown Presets**: Pre-configured countdown timers for tiered assessments:
  - **Tier 1**: Time Assessment (1:45.0)
  - **Tier 2**: Time Assessment (1:43.0), Jump Assessment (2:25.0), Precision Assessment (0:58.0)
  - **Tier 3**: Time Assessment (2:49.0), Jump Assessment (1:45.0), Precision Assessment (1:36.0)
- **Lap History**: Keeps track of the last 5 runs or lap times.
- **Customizable Hotkey**: Easily rebind the start/stop action to any keyboard key or mouse button.
- **Minimalist UI**: Borderless window that stays on top of other applications (perfect for overlaying on games).
- **Draggable Window**: Click and drag anywhere on the timer to reposition it.
- **Audio Feedback**: distinctive beep sounds for start (high pitch) and stop (low pitch).

## Installation & Requirements

1. **Python**: Ensure you have Python installed (3.x recommended).
2. **Dependencies**:
   Install the required Python packages using pip:
   ```bash
   pip install tk keyboard mouse
   ```
   _(Note: The `winsound` module is part of the standard Python library on Windows)._

## Usage

1. **Run the Application**:
   Execute the script using Python:

   ```bash
   python main.py
   ```

2. **Start/Stop Timer**:
   - Press the configured hotkey (default is `F5`) to start or stop the timer.
   - The timer text turns **Green** when running and **Red** when stopped.

3. **Context Menu**:
   Right-click anywhere on the application window to open the menu:
   - **Presets (Countdown)**: Select a specific tier and assessment to switch to countdown mode. The timer will count down from the selected duration. select "None (Count Up)" to return to standard stopwatch mode.
   - **Change Hotkey**: Select this option, then press any key or mouse button to bind it as the new toggle.
   - **Reset Laps**: Clears the history of the last 5 runs.
   - **Exit**: Closes the application completely.

4. **Moving the Window**:
   Left-click and hold anywhere on the window to drag it to your desired position on the screen.

## Configuration

The application saves your hotkey configuration to a `timer_config.json` file automatically. This ensures your preferred keybind is remembered between sessions.
