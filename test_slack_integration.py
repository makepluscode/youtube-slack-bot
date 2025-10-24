"""Integration test: Send YouTube link to Slack and monitor bot response"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()

def test_slack_youtube_download():
    """Send a YouTube link to Slack #ask channel and monitor the bot response"""

    print("=" * 60)
    print("Slack Integration Test")
    print("=" * 60)

    # Initialize Slack client
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not found in .env")
        return False

    client = WebClient(token=bot_token)

    # Use #ask channel (from logs: C097RMSHZU0)
    print("\n1. Using #ask channel...")
    ask_channel = "C097RMSHZU0"
    print(f"   ✅ Channel ID: {ask_channel}")

    # Send test YouTube link (short video)
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    test_message = f"[TEST] {test_url} 테스트 다운로드"

    try:
        print(f"\n2. Sending test message to #ask...")
        print(f"   Message: {test_message}")

        response = client.chat_postMessage(
            channel=ask_channel,
            text=test_message
        )

        message_ts = response["ts"]
        print(f"   ✅ Message sent (ts: {message_ts})")

    except SlackApiError as e:
        print(f"   ❌ Error sending message: {e.response['error']}")
        return False

    # Monitor logs for bot response
    print(f"\n3. Monitoring bot response (waiting 30 seconds)...")
    log_file = Path("logs/app.log")

    if not log_file.exists():
        print("   ❌ Log file not found")
        return False

    # Get current log size
    initial_size = log_file.stat().st_size

    # Wait and check logs
    for i in range(6):
        time.sleep(5)
        print(f"   ... checking ({(i+1)*5}s)")

        # Read new log entries
        with open(log_file, 'r') as f:
            f.seek(initial_size)
            new_logs = f.read()

        if "Download failed" in new_logs:
            print("\n   ❌ Bot reported download failure")
            print("   Log excerpt:")
            for line in new_logs.split('\n')[-10:]:
                if line.strip():
                    print(f"      {line}")
            return False

        if "successfully downloaded" in new_logs.lower() or "✅" in new_logs:
            print("\n   ✅ Bot successfully processed the download!")
            print("   Log excerpt:")
            for line in new_logs.split('\n')[-10:]:
                if line.strip():
                    print(f"      {line}")
            return True

        if "Starting download" in new_logs:
            print("      → Bot started download...")

    print("\n   ⚠️  Timeout: No clear success/failure in logs")
    print("   Recent logs:")
    with open(log_file, 'r') as f:
        f.seek(initial_size)
        for line in f.readlines()[-15:]:
            if line.strip():
                print(f"      {line.rstrip()}")

    return False


if __name__ == "__main__":
    print("\n🤖 Starting Slack YouTube Bot Integration Test\n")
    success = test_slack_youtube_download()

    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: Bot successfully downloaded video from Slack")
    else:
        print("❌ TEST FAILED: Check logs above for details")
    print("=" * 60)

    exit(0 if success else 1)
