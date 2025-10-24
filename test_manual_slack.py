"""Manual Slack integration test - monitor bot response to user messages"""

import time
from pathlib import Path


def monitor_bot_logs():
    """Monitor bot logs for YouTube download activity"""

    print("=" * 60)
    print("Manual Slack Integration Test")
    print("=" * 60)
    print()
    print("📱 Please send a YouTube link to #ask channel in Slack")
    print("   Example: https://www.youtube.com/watch?v=jNQXAC9IVRw")
    print()
    print("🔍 Monitoring logs for bot activity...")
    print()

    log_file = Path("logs/app.log")

    if not log_file.exists():
        print("❌ Log file not found: logs/app.log")
        return False

    # Get current log position
    initial_size = log_file.stat().st_size

    # Monitor for 60 seconds
    start_time = time.time()
    last_activity = None

    while time.time() - start_time < 60:
        time.sleep(2)

        # Read new log entries
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(initial_size)
            new_logs = f.read()

        if not new_logs:
            continue

        # Parse log lines
        for line in new_logs.split('\n'):
            if not line.strip():
                continue

            # Check for message received
            if "Received message in channel" in line:
                print(f"📩 {line.split(' - ')[-1]}")
                last_activity = "received"

            # Check for processing started
            elif "Processing message from" in line:
                print(f"⚙️  {line.split(' - ')[-1]}")
                last_activity = "processing"

            # Check for URL extraction
            elif "Extracting URLs from message" in line:
                print(f"🔗 Extracting URLs...")
                last_activity = "extracting"

            # Check for download started
            elif "Starting download:" in line:
                url = line.split("Starting download:")[-1].strip()
                print(f"⬇️  Starting download: {url}")
                last_activity = "downloading"

            # Check for video title
            elif "Video title:" in line:
                title = line.split("Video title:")[-1].strip()
                print(f"📹 Video: {title}")

            # Check for success
            elif "successfully downloaded" in line.lower() or "Download successful" in line:
                print(f"✅ {line.split(' - ')[-1]}")
                last_activity = "success"

            # Check for completion
            elif "Agent completed:" in line:
                result = line.split("Agent completed:")[-1].strip()
                print(f"🏁 {result}")
                if "1/1" in result or "successful" in result.lower():
                    return True

            # Check for errors
            elif "Download failed:" in line or "ERROR" in line:
                print(f"❌ {line.split(' - ')[-1]}")
                last_activity = "failed"
                return False

        # Update initial size for next iteration
        current_size = log_file.stat().st_size
        if current_size > initial_size:
            initial_size = current_size

    # Timeout
    if last_activity:
        print()
        print(f"⏱️  Timeout after 60s (last activity: {last_activity})")
        return False
    else:
        print()
        print("⏱️  Timeout: No bot activity detected")
        print("   Make sure you sent a message to #ask channel")
        return False


if __name__ == "__main__":
    print()
    success = monitor_bot_logs()

    print()
    print("=" * 60)
    if success:
        print("✅ TEST PASSED: Bot successfully processed YouTube download")
    else:
        print("❌ TEST FAILED: Check output above for details")
    print("=" * 60)
    print()

    exit(0 if success else 1)
