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
from analyzer.pitch_deck_analyzer import analyze_pitch_deck

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize the Bolt app with your bot token
bolt_app = App(token=os.getenv("SLACK_BOT_TOKEN"))
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

# Default analysis prompts
DEFAULT_PROMPTS = {
    "problem_statement": "Analyze the problem statement. Is it clear, significant, and well-defined? What pain points are being addressed?",
    "market_opportunity": "Evaluate the market opportunity. What's the TAM/SAM/SOM? Is there clear evidence of market demand?",
    "technical_approach": "Assess the technical approach and AI implementation. Is it innovative and feasible? What are the key technical differentiators?",
    "team": "Evaluate the team's capabilities and experience. Do they have the right mix of skills and background for this venture?",
    "financials": "Analyze the financial projections and metrics. Are they realistic and well-supported? What are the key assumptions?",
    "competition": "Evaluate the competitive landscape. How does the company differentiate itself? What are their sustainable advantages?",
    "roadmap": "Assess the product roadmap and go-to-market strategy. Is it realistic and well-thought-out?"
}

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
    
    # Check if there are files attached
    files = event.get("files", [])
    if files:
        handle_pitch_deck(files[0], say)
    else:
        say(f"Thanks for mentioning me, <@{user}>! Please share a pitch deck PDF and mention me to analyze it.")

def handle_pitch_deck(file, say):
    """Handle pitch deck analysis"""
    # Check if it's a PDF
    if not file.get("mimetype") == "application/pdf":
        say("Sorry, I can only process PDF files! 📄")
        return

    say("Starting to analyze your pitch deck... 🔍")

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

        try:
            # Convert to markdown
            say("I'm parsing the pitch deck. It may take a minute...")
            markdown_content = parse_pitch_deck(str(temp_file))
            say("I parsed the pitch deck!")
            # Analyze the pitch deck
            say("I'm analyzing the pitch deck. It may take a minute...")
            analysis = analyze_pitch_deck(markdown_content, DEFAULT_PROMPTS)
            say("I analyzed the pitch deck!")
            # Send analysis results
            say("🎯 Here's my analysis of your pitch deck:")
            
            for section_name in ["problem_statement", "market_opportunity", "technical_approach", 
                               "team", "financials", "competition", "roadmap"]:
                section = getattr(analysis, section_name)
                if section.analysis:
                    # Format section name
                    formatted_name = section_name.replace("_", " ").title()
                    message = f"*{formatted_name}*\n{section.analysis.content}"
                    
                    # Add citations if available
                    if section.analysis.citations:
                        message += "\n\n*Sources:*\n" + "\n".join(
                            f"• {citation}" for citation in section.analysis.citations
                        )
                    
                    say(message)
                
            say("Analysis complete! 🎉")
                
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            say("Sorry, I had trouble processing the PDF! 😕")
            
        finally:
            # Cleanup
            temp_file.unlink(missing_ok=True)
            
    except Exception as e:
        logger.error(f"Error handling file: {str(e)}")
        say("Sorry, I had trouble accessing the file! 😕")

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
        app_token=os.getenv("SLACK_APP_TOKEN"),
        app=bolt_app
    )
    socket_mode_thread = Thread(target=handler.start)
    socket_mode_thread.daemon = True
    socket_mode_thread.start()
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 3000)))