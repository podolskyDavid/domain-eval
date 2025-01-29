from fastapi import FastAPI, Request, HTTPException
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import os
import hmac
import hashlib
import time
import logging
import requests
from pathlib import Path
from parser.pitch_deck_parsing import parse_pitch_deck

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize the Bolt app with your bot token
bolt_app = App(token=os.getenv("SLACK_BOT_TOKEN"))
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

# Test the connection
try:
    auth_test = client.auth_test()
    logger.info(f"Successfully connected to Slack with bot user: {auth_test['user']}")
except SlackApiError as e:
    logger.error(f"Error testing Slack connection: {e.response['error']}")
    raise Exception("Failed to connect to Slack")

# Message event handler
@bolt_app.message("hello")
def handle_message(message, say):
    logger.info(f"Received message: {message}")
    user = message.get("user")
    say(f"Hey there <@{user}>! 👋")

# App mention handler
@bolt_app.event("app_mention")
def handle_mention(event, say):
    logger.info(f"Received mention: {event}")
    user = event.get("user")
    say(f"Thanks for mentioning me, <@{user}>! How can I help?")

# File upload handler
@bolt_app.event("message")
def handle_file_share(body, say, client):
    # Get the event from the body
    event = body["event"]
    
    # Check if it's a file share
    if event.get("subtype") != "file_share":
        return

    try:
        # Get file info from the event
        files = event.get("files", [])
        if not files:
            return

        file = files[0]  # Process the first file if multiple are shared
        
        # Check if it's a PDF
        if not file.get("mimetype") == "application/pdf":
            say("Sorry, I can only process PDF files! 📄")
            return

        try:
            # Get the file URL and download it
            file_url = file.get("url_private_download")
            headers = {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN')}"}
            response = requests.get(file_url, headers=headers)
            
            if response.status_code != 200:
                say("Sorry, I couldn't download the file! 😕")
                return

            # Save temporarily
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            temp_file = temp_dir / f"{file['id']}.pdf"
            
            with open(temp_file, "wb") as f:
                f.write(response.content)

            # Process the PDF
            try:
                markdown_content = parse_pitch_deck(str(temp_file))
                
                # Split message if too long (Slack has a 40k character limit)
                max_length = 39000
                if len(markdown_content) > max_length:
                    chunks = [markdown_content[i:i + max_length] 
                             for i in range(0, len(markdown_content), max_length)]
                    
                    say("Here's your processed pitch deck (split into multiple messages):")
                    for chunk in chunks:
                        say(f"```{chunk}```")
                else:
                    say(f"Here's your processed pitch deck:\n```{markdown_content}```")
                    
            except Exception as e:
                logger.error(f"Error processing PDF: {str(e)}")
                say("Sorry, I had trouble processing the PDF! 😕")
                
            finally:
                # Cleanup
                temp_file.unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Error handling file: {str(e)}")
            say("Sorry, I had trouble accessing the file! 😕")
            
    except Exception as e:
        logger.error(f"Error handling file: {str(e)}")
        say("Sorry, something went wrong! 😕")

# FastAPI app for health checks
app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    from threading import Thread
    
    logger.info("Starting server...")
    
    # Start the Socket Mode handler in a separate thread
    handler = SocketModeHandler(
        app_token=os.getenv("SLACK_APP_TOKEN"),  # xapp-... token
        app=bolt_app
    )
    socket_mode_thread = Thread(target=handler.start)
    socket_mode_thread.daemon = True
    socket_mode_thread.start()
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 3000)))