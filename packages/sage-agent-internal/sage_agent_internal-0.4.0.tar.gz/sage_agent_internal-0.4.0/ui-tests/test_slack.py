#!/usr/bin/env python3
"""
Slack bot for posting UI test results to Slack channels.
This script posts test results and PR links to Slack.
"""

import os
import sys
import time
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
def get_pr_info():
    """Get PR information from environment variables set by GitHub Actions."""
    pr_number = os.environ.get("GITHUB_PR_NUMBER", "")
    pr_url = os.environ.get("GITHUB_PR_URL", "")
    repo_name = os.environ.get("GITHUB_REPOSITORY", "")
    return pr_number, pr_url, repo_name

def get_test_results_content():
    """Read the test summary content that would be posted to GitHub."""
    summary_path = "./test-summary.md"
    
    try:
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "❌ **Test Summary Not Available**\n\nTest summary file was not generated."
    except Exception as e:
        print(f"Error reading test summary: {e}")
        return f"❌ **Error Reading Test Summary**\n\nFailed to read test summary file: {str(e)}"

def format_slack_message(pr_number, pr_url, repo_name, test_content):
    """Format the message for Slack with PR info and test results."""
    if pr_number and pr_url:
        header = f"🔄 *UI Test Results for PR #{pr_number}*\n"
        header += f"📋 *Repository:* {repo_name}\n"
        header += f"🔗 *PR Link:* <{pr_url}|View Pull Request>\n\n"
    else:
        header = f"🔄 *UI Test Results*\n"
        header += f"📋 *Repository:* {repo_name}\n\n"
    
    # Convert markdown to Slack-friendly format
    slack_content = test_content
    # Convert markdown headers to bold text
    slack_content = slack_content.replace("## ", "*").replace("#", "*")
    # Convert markdown bold to Slack bold
    slack_content = slack_content.replace("**", "*")
    # Convert markdown links to Slack format where possible
    # Note: This is a basic conversion, more complex regex might be needed
    
    message = header + slack_content
    
    # Slack has a 4000 character limit for messages
    max_length = 3900  # Leave some buffer
    if len(message) > max_length:
        message = message[:max_length] + "\n\n⚠️ *Message truncated due to length limit.*"
    
    return message

def get_accessible_channels(client):
    """Get channels where the bot can actually post messages."""
    print("🔍 Finding accessible channels...")
    accessible_channels = []
    
    try:
        # Get all public channels where the bot is a member
        response = client.conversations_list(types="public_channel", limit=1000)
        all_channels = response.get("channels", [])
        
        print(f"Found {len(all_channels)} public channels. Testing access...")
        
        for channel in all_channels:
            channel_id = channel["id"]
            channel_name = channel["name"]
            
            # Check if bot is a member
            try:
                info_response = client.conversations_info(channel=channel_id)
                channel_info = info_response["channel"]
                is_member = channel_info.get("is_member", False)
                
                if is_member:
                    print(f"  ✅ Bot is member of #{channel_name}")
                    accessible_channels.append(channel)
                    
            except SlackApiError as e:
                if e.response["error"] != "channel_not_found":
                    print(f"  ❌ Error accessing #{channel_name}: {e.response['error']}")
    
    except SlackApiError as e:
        print(f"❌ Error getting public channels: {e.response['error']}")
    
    print(f"Found {len(accessible_channels)} accessible channels")
    return accessible_channels

def upload_video_file(client, channel_id, video_path):
    """Upload video file to Slack channel using the new upload API."""
    try:
        if os.path.exists(video_path):
            print(f"📹 Uploading video: {os.path.basename(video_path)}")
            
            # Get file size
            file_size = os.path.getsize(video_path)
            filename = os.path.basename(video_path)
            
            # Step 1: Get upload URL
            upload_response = client.files_getUploadURLExternal(
                filename=filename,
                length=file_size
            )
            
            upload_url = upload_response["upload_url"]
            file_id = upload_response["file_id"]
            
            # Step 2: Upload file to the URL
            import requests
            with open(video_path, 'rb') as file_data:
                upload_result = requests.post(upload_url, files={"file": file_data})
                
            if upload_result.status_code != 200:
                print(f"❌ Error uploading file data: HTTP {upload_result.status_code}")
                return False
            
            # Step 3: Complete the upload
            complete_response = client.files_completeUploadExternal(
                files=[{
                    "id": file_id,
                    "title": "SP500 Test Final Video"
                }],
                channel_id=channel_id,
                initial_comment="📹 UI Test Video Results"
            )
            
            print(f"✅ Video uploaded successfully")
            return True
        else:
            print(f"⚠️  Video file not found: {video_path}")
            return False
    except SlackApiError as e:
        print(f"❌ Error uploading video: {e.response['error']}")
        return False
    except Exception as e:
        print(f"❌ Error uploading video: {str(e)}")
        return False

def post_test_results(client, channel_id, channel_name, message, video_path=None):
    """Post test results message to a specific channel with optional video upload."""
    try:
        # First, upload the video if provided and exists
        if video_path and os.path.exists(video_path):
            upload_video_file(client, channel_id, video_path)
            time.sleep(2)  # Wait a bit between video upload and message post
        
        response = client.chat_postMessage(
            channel=channel_id,
            text=message,
            mrkdwn=True  # Enable Slack markdown formatting
        )
        print(f"✅ Test results posted successfully to #{channel_name}")
        return True
    except SlackApiError as e:
        print(f"❌ Error posting to #{channel_name}: {e.response['error']}")
        return False

def main():
    """Main function to post test results to Slack channels."""
    
    # Check if bot token is set
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    if not bot_token:
        print("❌ Error: SLACK_BOT_TOKEN environment variable not set!")
        print("This script requires a Slack bot token to function.")
        sys.exit(1)
    
    # Initialize the Slack client
    client = WebClient(token=bot_token)
    
    # Test the connection
    try:
        auth_response = client.auth_test()
        bot_name = auth_response["user"]
        bot_id = auth_response["user_id"]
        team_name = auth_response.get("team", "Unknown Team")
        print(f"🤖 Connected as bot: {bot_name} (ID: {bot_id}) in team: {team_name}")
        
    except SlackApiError as e:
        print(f"❌ Error connecting to Slack: {e.response['error']}")
        sys.exit(1)
    
    # Get PR information
    pr_number, pr_url, repo_name = get_pr_info()
    print(f"📋 PR Info - Number: {pr_number}, Repository: {repo_name}")
    if pr_url:
        print(f"🔗 PR URL: {pr_url}")
    
    # Get test results content
    print("📖 Reading test results...")
    test_content = get_test_results_content()
    
    # Set video file path
    video_path = os.path.join(os.path.dirname(__file__), "screenshots", "sp500_test_final.mp4")
    print(f"📹 Video file path: {video_path}")
    
    # Check if video file exists
    if os.path.exists(video_path):
        print(f"✅ Video file found: {os.path.basename(video_path)}")
    else:
        print(f"⚠️  Video file not found at: {video_path}")
        video_path = None
    
    # Format message for Slack
    slack_message = format_slack_message(pr_number, pr_url, repo_name, test_content)
    
    # Get channels the bot can access
    bot_channels = get_accessible_channels(client)
    
    if not bot_channels:
        print("❌ Bot is not a member of any accessible channels!")
        print("Make sure to invite the bot to at least one channel.")
        sys.exit(1)
    
    print(f"📢 Found {len(bot_channels)} channels to post to:")
    for channel in bot_channels:
        print(f"  - #{channel['name']}")
    
    # Post to each accessible channel
    print(f"\n🚀 Posting test results...")
    success_count = 0
    
    for channel in bot_channels:
        print(f"\n📤 Posting to #{channel['name']}...")
        if post_test_results(client, channel["id"], channel["name"], slack_message, video_path):
            success_count += 1
        time.sleep(2)  # Rate limiting - wait 2 seconds between posts to allow for video upload
    
    print(f"\n✅ Completed! Successfully posted to {success_count}/{len(bot_channels)} channels.")
    
    if success_count == 0:
        print("⚠️  No messages were posted successfully.")
        sys.exit(1)

if __name__ == "__main__":
    main()
