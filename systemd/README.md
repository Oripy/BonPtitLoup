# Systemd Timer Setup for Closing Expired Votes

This directory contains systemd service and timer files to automatically close expired vote groups daily.

## Files

- `bonptitloup-close-votes.service` - The systemd service that runs the Django management command
- `bonptitloup-close-votes.timer` - The systemd timer that schedules when to run the service

## Installation

### 1. Edit the Service File

Before installing, you need to update the paths in `bonptitloup-close-votes.service`:

```bash
# Replace these placeholders with your actual paths:
# - /path/to/BonPtitLoup → Your project directory (e.g., /home/user/BonPtitLoup)
# - www-data → Your web server user (e.g., www-data, nginx, apache, or your username)
```

Example:
```ini
WorkingDirectory=/home/user/BonPtitLoup
Environment="PATH=/home/user/BonPtitLoup/venv/bin"
ExecStart=/home/user/BonPtitLoup/venv/bin/python /home/user/BonPtitLoup/manage.py close_expired_votes
User=www-data
Group=www-data
```

### 2. Copy Files to Systemd Directory

```bash
# Copy service file
sudo cp systemd/bonptitloup-close-votes.service /etc/systemd/system/

# Copy timer file
sudo cp systemd/bonptitloup-close-votes.timer /etc/systemd/system/
```

### 3. Reload Systemd

```bash
sudo systemctl daemon-reload
```

### 4. Enable and Start the Timer

```bash
# Enable the timer (so it starts on boot)
sudo systemctl enable bonptitloup-close-votes.timer

# Start the timer
sudo systemctl start bonptitloup-close-votes.timer
```

### 5. Verify Installation

```bash
# Check timer status
sudo systemctl status bonptitloup-close-votes.timer

# List all timers to see when it will run next
systemctl list-timers bonptitloup-close-votes.timer

# Check service logs
sudo journalctl -u bonptitloup-close-votes.service -f
```

## Manual Testing

You can test the service manually without waiting for the timer:

```bash
# Run the service manually
sudo systemctl start bonptitloup-close-votes.service

# Check the output
sudo journalctl -u bonptitloup-close-votes.service -n 50
```

## Timer Schedule

The timer is configured to run:
- **Daily at midnight (00:00:00)**
- With a randomized delay of 0-300 seconds to avoid system load spikes
- If the system was off, it will run immediately when it comes back online (Persistent=true)

## Customizing the Schedule

To change when the timer runs, edit `/etc/systemd/system/bonptitloup-close-votes.timer`:

```ini
# Examples:

# Run every hour
OnCalendar=hourly

# Run every day at 2 AM
OnCalendar=*-*-* 02:00:00

# Run every Monday at 9 AM
OnCalendar=Mon *-*-* 09:00:00

# Run twice daily (midnight and noon)
OnCalendar=*-*-* 00:00:00
OnCalendar=*-*-* 12:00:00
```

After editing, reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart bonptitloup-close-votes.timer
```

## Troubleshooting

### Check if the timer is active:
```bash
sudo systemctl is-active bonptitloup-close-votes.timer
```

### Check when it will run next:
```bash
systemctl list-timers bonptitloup-close-votes.timer
```

### View service logs:
```bash
sudo journalctl -u bonptitloup-close-votes.service
```

### View timer logs:
```bash
sudo journalctl -u bonptitloup-close-votes.timer
```

### Disable the timer:
```bash
sudo systemctl stop bonptitloup-close-votes.timer
sudo systemctl disable bonptitloup-close-votes.timer
```

## Notes

- The service runs as a one-shot service (Type=oneshot), meaning it runs once and exits
- Logs are sent to the systemd journal, which you can view with `journalctl`
- Make sure the user specified in the service file has read/write access to the Django project directory and database

