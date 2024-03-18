# Schedule Main

This is a time management system designed for the terminal, aimed at quickly recording your life's events with a clear and simple method and analyzing your time and activities. 

Currently, it supports logging life events, with plans to gradually enhance the analysis of events and time.

## Installation

```shell
git clone https://github.com/yixiaoer/schedule-main.git
cd schedule-main
python3.11 -m venv venv
. venv/bin/activate
pip install tabulate
pip install .
```

## Usage

Schedule Main categorizes events into two types: *Timed events* (events with a start and end time) and *Instant events* (events occurring at a specific moment, also referred to as *Tidspunkt*). 

Events are further classified into three statuses: 'ongoing' (for Timed events that have started but not ended), 'ended' (for Timed events that have both start and end times recorded), and 'tidspunkt' (for Instant events).

### Adding events

* For *Timed events*, to start an event:

```shell
schedule-main -i|--include -n|--name '<EVENT_NAME>' -t|--time <TIME>
```

Example: `schedule-main -i -n 'Bilibili' -t now` marks the start of the 'Bilibili' event at the current time.

* For *Instant events*, to log an event happening at a specific moment:

```shell
schedule-main -p|--tidspunkt -n|--name "<EVENT_NAME>" -t|--time <TIME>
```

Example: `schedule-main -p -n "Baldur's Gate 3" -t now` logs a tidspunkt at the current time.

### Updating the end time of Timed events

To conclude 'ongoing' *Timed events* or update the finish time of 'ended' *Timed events*:

```shell
schedule-main -c|--conclude <EVENT_ID|LAST|LAST-1|..> -t|--time <TIME>
```

Example: `schedule-main -c LAST -t now` updates the status of the most recent event to 'ended' or modifies its end time.

### Modifying Events

For *Timed events*, to adjust the start time or name; for *Instant events*, to modify the occurrence time or name：

```shell
schedule-main -a|--amend <EVENT_ID|LAST|LAST-1|..> [-t|--time <NEW_TIME>]
```

You can opt to modify either or both attributes.

Example: `schedule-main -a LAST -n 'Divinity: Original Sin II'` to adjust the name of the last event.

### Deleting Events

To remove an event：

```shell
schedule-main -r|--remove <EVENT_ID|LAST|LAST-1|..>
```

Example: `schedule-main --remove 0` to delete the event with id 0.

### Listing Events

To display the event table：

```shell
schedule-main -l|--list
```

Schedule Main is your go-to for managing time and events efficiently in the terminal. 

Get started today and streamline your event logging and analysis!
