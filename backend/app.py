from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import pytz
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import openai
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['meeting_scheduler']
users_collection = db['users']
chats_collection = db['chats']
meetings_collection = db['meetings']

# OpenAI Configuration
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-openai-api-key')

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key')
genai.configure(api_key=GEMINI_API_KEY)

# Personal Email Configuration - Update these with your personal email
PERSONAL_EMAIL_HOST = os.getenv('PERSONAL_EMAIL_HOST', 'smtp.gmail.com')
PERSONAL_EMAIL_PORT = int(os.getenv('PERSONAL_EMAIL_PORT', '587'))
PERSONAL_EMAIL_USER = os.getenv('PERSONAL_EMAIL_USER', 'your-personal-email@gmail.com')
PERSONAL_EMAIL_PASSWORD = os.getenv('PERSONAL_EMAIL_PASSWORD', 'your-personal-app-password')

class MeetingScheduler:
    def __init__(self):
        try:
            self.openai_client = openai.OpenAI(api_key=openai.api_key)
        except Exception as e:
            print(f"Warning: OpenAI client initialization failed: {e}")
            self.openai_client = None
        
        # Initialize Gemini model
        try:
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini API initialized successfully")
        except Exception as e:
            print(f"Warning: Gemini API initialization failed: {e}")
            self.gemini_model = None
    
 

    def analyze_chat_intent(self, chat_history):
        """Analyze chat to detect meeting intent and extract availability using Gemini AI"""
        try:
        # Get all unique participants from chat history
            pipeline = [
            {"$group": {"_id": "$user_email", "name": {"$first": "$user_name"}}}
        ]
            participants = list(chats_collection.aggregate(pipeline))
        
            real_participants = [
            {"name": p["name"], "email": p["_id"]} 
            for p in participants 
            if p["_id"] and p["name"]
        ]
        
        # Get chat messages for analysis
            chat_messages = list(chats_collection.find({}, {"message": 1, "user_name": 1}).sort("timestamp", 1))
        
            if not chat_messages or not real_participants:
                return {
                "has_meeting_intent": False,
                "participants": real_participants,
                "availability_mentions": [],
                "suggested_times": [],
                "missing_info": [],
                "follow_up_questions": []
            }
        
        # Use Gemini AI for intelligent analysis
            if self.gemini_model:
                try:
                # Prepare chat text for analysis
                    chat_text = "\n".join([f"{msg['user_name']}: {msg['message']}" for msg in chat_messages])

                # Use tomorrow's date for dynamic time suggestions
                    tomorrow = datetime.now() + timedelta(days=1)
                    date_str = tomorrow.strftime('%Y-%m-%d')
                
                    prompt = f"""
                Analyze this group chat conversation for meeting scheduling intent and extract availability information.
                
                Chat Conversation:
                {chat_text}
                
                Please analyze and return a JSON response with:
                {{
                    "has_meeting_intent": boolean,
                    "participants": [{{"name": "string", "email": "string"}}],
                    "availability_mentions": [
                        {{
                            "person": "string",
                            "availability": "string",
                            "time_mentions": ["string"]
                        }}
                    ],
                    "suggested_times": ["string"],
                    "missing_info": ["string"],
                    "follow_up_questions": ["string"]
                }}
                
                CRITICAL INSTRUCTIONS:
                1. Extract EXACT times mentioned in the chat (9 AM, 2 PM, 6 PM, etc.)
                2. If multiple times are mentioned, prioritize the time that most people agree on
                3. If someone says "9 AM works for me", suggest "{date_str} 09:00 AM"
                4. If someone says "2 PM is perfect", suggest "{date_str} 02:00 PM"
                5. If someone says "6 PM works", suggest "{date_str} 06:00 PM"
                6. If there's a consensus time (like everyone agreeing on 6 PM), make that the FIRST suggestion
                7. Use today's date plus one day, which is {date_str}, for all suggestions.
                8. Be very specific about the times mentioned in the chat
                
                Example: If chat mentions "9 AM", "2 PM", and "6 PM", and everyone agrees on "6 PM", 
                then suggested_times should be: ["{date_str} 06:00 PM", "{date_str} 09:00 AM", "{date_str} 02:00 PM"]
                """
                
                    response = self.gemini_model.generate_content(prompt)
                
                # *** The new logic is here ***
                    raw_response = response.text
                    print(f"Gemini API Raw Response: {raw_response}")
                
                # Clean the string by removing the markdown code block tags
                    cleaned_response = raw_response.strip().removeprefix('```json').removesuffix('```')

                    try:
                        result = json.loads(cleaned_response)
                    except json.JSONDecodeError:
                        print(f"Error: Gemini API returned a non-JSON response. Raw response: {raw_response}")
                        return self._basic_analysis(chat_messages, real_participants)
                
                # Ensure we have the required fields
                    result.setdefault("has_meeting_intent", False)
                    result.setdefault("participants", real_participants)
                    result.setdefault("availability_mentions", [])
                    result.setdefault("suggested_times", [])
                    result.setdefault("missing_info", [])
                    result.setdefault("follow_up_questions", [])
                
                    print(f"✅ Gemini AI Analysis: {result}")
                    return result
                
                except Exception as e:
                    print(f"Error with Gemini AI analysis: {e}")
                    return self._basic_analysis(chat_messages, real_participants)
            else:
             return self._basic_analysis(chat_messages, real_participants)
            
        except Exception as e:
            print(f"Error in analyze_chat_intent: {e}")
            return {
            "has_meeting_intent": False,
            "participants": [],
            "availability_mentions": [],
            "suggested_times": [],
            "missing_info": [],
            "follow_up_questions": []
        }
    def _basic_analysis(self, chat_messages, real_participants):
        """Basic analysis fallback when AI is not available"""
        chat_text = " ".join([msg["message"] for msg in chat_messages])
        
        # Simple keyword analysis
        meeting_keywords = ["meeting", "schedule", "call", "discuss", "meet", "appointment", "conference"]
        has_meeting_intent = any(keyword in chat_text.lower() for keyword in meeting_keywords)
        
        # Extract availability mentions and time preferences
        availability_mentions = []
        time_preferences = []
        
        for msg in chat_messages:
            message_lower = msg["message"].lower()
            if any(word in message_lower for word in ["available", "free", "can", "will", "time", "when"]):
                availability_mentions.append({
                    "person": msg["user_name"],
                    "availability": msg["message"],
                    "time_mentions": []
                })
            
            # Extract specific time mentions
            if "9 am" in message_lower or "9am" in message_lower:
                time_preferences.append("09:00 AM")
            elif "10 am" in message_lower or "10am" in message_lower:
                time_preferences.append("10:00 AM")
            elif "11 am" in message_lower or "11am" in message_lower:
                time_preferences.append("11:00 AM")
            elif "2 pm" in message_lower or "2pm" in message_lower:
                time_preferences.append("02:00 PM")
            elif "3 pm" in message_lower or "3pm" in message_lower:
                time_preferences.append("03:00 PM")
            elif "4 pm" in message_lower or "4pm" in message_lower:
                time_preferences.append("04:00 PM")
            elif "5 pm" in message_lower or "5pm" in message_lower:
                time_preferences.append("05:00 PM")
            elif "6 pm" in message_lower or "6pm" in message_lower:
                time_preferences.append("06:00 PM")
            elif "7 pm" in message_lower or "7pm" in message_lower:
                time_preferences.append("07:00 PM")
            elif "8 pm" in message_lower or "8pm" in message_lower:
                time_preferences.append("08:00 PM")
        
        # Generate time suggestions based on extracted preferences
        suggested_times = []
        if has_meeting_intent:
            from datetime import datetime, timedelta
            tomorrow = datetime.now() + timedelta(days=1)
            date_str = tomorrow.strftime('%Y-%m-%d')
            
            # Use extracted time preferences if available
            if time_preferences:
                # Remove duplicates and take first 3
                unique_times = list(dict.fromkeys(time_preferences))[:3]
                suggested_times = [f"{date_str} {time}" for time in unique_times]
            else:
                # Fallback to default times
                suggested_times = [
                    f"{date_str} 10:00 AM",
                    f"{date_str} 03:00 PM",
                    f"{date_str} 05:00 PM"
                ]
        
        return {
            "has_meeting_intent": has_meeting_intent,
            "participants": real_participants,
            "availability_mentions": availability_mentions,
            "suggested_times": suggested_times,
            "missing_info": ["Specific time preferences", "Meeting duration"] if has_meeting_intent else [],
            "follow_up_questions": ["What time works best for everyone?", "How long should the meeting be?"] if has_meeting_intent else []
        }
        
        try:
            system_prompt = """
            You are an AI assistant that analyzes group chat conversations to detect meeting scheduling intent and extract availability information.
            
            Analyze the chat and return a JSON response with:
            {
                "has_meeting_intent": boolean,
                "participants": [{"name": "string", "email": "string"}],
                "availability_mentions": [
                    {
                        "person": "string",
                        "availability": "string",
                        "time_mentions": ["string"]
                    }
                ],
                "suggested_times": ["string"],
                "missing_info": ["string"],
                "follow_up_questions": ["string"]
            }
            
            Focus on:
            - Detecting if users want to schedule a meeting
            - Extracting mentioned availability times
            - Identifying participants
            - Finding common time slots
            - Identifying missing information
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this chat conversation:\n\n{chat_history}"}
                ],
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error analyzing chat: {e}")
            return {
                "has_meeting_intent": False,
                "participants": [],
                "availability_mentions": [],
                "suggested_times": [],
                "missing_info": [],
                "follow_up_questions": []
            }
    
    def propose_meeting_time(self, availability_data):
        """Propose a meeting time based on availability and Gemini analysis."""
        # Use the suggested_times from the Gemini analysis directly
        suggested_times = availability_data.get("suggested_times")
        participants = [p['name'] for p in availability_data.get("participants", [])]
        
        if suggested_times:
            # Use the first suggested time from the Gemini analysis
            proposed_time_str = suggested_times[0]
            reasoning = "Based on the most agreed-upon time from the group chat conversation."
            
            # Use tomorrow's date if no date is in the suggested time (Gemini should provide one)
            try:
                from datetime import datetime
                datetime.strptime(proposed_time_str, '%Y-%m-%d %H:%M %p')
            except ValueError:
                # Fallback in case Gemini doesn't provide a full date
                from datetime import datetime, timedelta
                tomorrow = datetime.now() + timedelta(days=1)
                date_str = tomorrow.strftime('%Y-%m-%d')
                time_part = proposed_time_str.split(' ')[-2:]
                proposed_time_str = f"{date_str} {' '.join(time_part)}"
                reasoning = "Based on a suggested time from the chat, scheduled for tomorrow."
            
            return {
                "proposed_time": proposed_time_str,
                "timezone": "UTC",  # Assuming UTC for simplicity
                "duration": "60 minutes",
                "participants": participants,
                "reasoning": reasoning
            }
        
        # Fallback if no specific times were suggested by the AI
        else:
            print("⚠️ No specific times suggested by Gemini. Falling back to a default proposal.")
            from datetime import datetime, timedelta
            tomorrow = datetime.now() + timedelta(days=1)
            proposed_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
            
            return {
                "proposed_time": proposed_time.strftime("%Y-%m-%d %H:%M"),
                "timezone": "UTC",
                "duration": "60 minutes",
                "participants": participants,
                "reasoning": "Scheduled for tomorrow afternoon based on typical business hours, as no specific times were mentioned."
            }


scheduler = MeetingScheduler()

def send_personal_email(to_email, subject, body):
    """Send email using personal email configuration"""
    try:
        msg = MIMEMultipart()
        msg['From'] = PERSONAL_EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(PERSONAL_EMAIL_HOST, PERSONAL_EMAIL_PORT)
        server.starttls()
        server.login(PERSONAL_EMAIL_USER, PERSONAL_EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(PERSONAL_EMAIL_USER, to_email, text)
        server.quit()
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        return False

def get_all_chat_participants():
    """Get all unique participants from chat history"""
    try:
        # Get all unique users from chat messages
        pipeline = [
            {"$group": {"_id": "$user_email", "name": {"$first": "$user_name"}}}
        ]
        participants = list(chats_collection.aggregate(pipeline))
        
        return [
            {"name": p["name"], "email": p["_id"]} 
            for p in participants 
            if p["_id"] and p["name"]
        ]
    except Exception as e:
        print(f"Error getting chat participants: {e}")
        return []

# API Routes

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = list(users_collection.find({}, {'_id': 0}))
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.json
        user = {
            'name': data['name'],
            'email': data['email'],
            'created_at': datetime.now().isoformat()
        }
        users_collection.insert_one(user)
        user.pop('_id', None)
        print(f"✅ New user created: {user['name']} ({user['email']})")
        return jsonify(user), 201
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chats', methods=['GET'])
def get_chats():
    """Get all chat messages"""
    try:
        chats = list(chats_collection.find({}, {'_id': 0}).sort('timestamp', 1))
        return jsonify(chats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chats', methods=['POST'])
def create_message():
    """Create a new chat message"""
    try:
        data = request.json
        message = {
            'user_name': data['user_name'],
            'user_email': data['user_email'],
            'message': data['message'],
            'timestamp': datetime.now().isoformat()
        }
        chats_collection.insert_one(message)
        message.pop('_id', None)
        return jsonify(message), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-chat', methods=['POST'])
def analyze_chat():
    """Analyze chat for meeting intent"""
    try:
        # Get all chat messages
        chats = list(chats_collection.find({}, {'_id': 0}).sort('timestamp', 1))
        chat_history = "\n".join([f"{chat['user_name']}: {chat['message']}" for chat in chats])
        
        # Analyze with AI
        analysis = scheduler.analyze_chat_intent(chat_history)
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/schedule-meeting', methods=['POST'])
def schedule_meeting():
    """Schedule a meeting based on chat analysis"""
    try:
        data = request.json
        
        # Get all chat messages
        chats = list(chats_collection.find({}, {'_id': 0}).sort('timestamp', 1))
        chat_history = "\n".join([f"{chat['user_name']}: {chat['message']}" for chat in chats])
        
        # Analyze with Gemini
        analysis = scheduler.analyze_chat_intent(chat_history)
        
        if not analysis['has_meeting_intent']:
            return jsonify({'error': 'No meeting intent detected'}), 400
        
        # Propose meeting time using the analysis from Gemini
        meeting_proposal = scheduler.propose_meeting_time(analysis)
        
        if not meeting_proposal:
            return jsonify({'error': 'Could not propose meeting time'}), 500
        
        # Store meeting details
        meeting = {
            'title': data.get('title', 'Group Meeting'),
            'proposed_time': meeting_proposal['proposed_time'],
            'timezone': meeting_proposal['timezone'],
            'duration': meeting_proposal['duration'],
            'participants': meeting_proposal['participants'],
            'reasoning': meeting_proposal['reasoning'],
            'status': 'proposed',
            'created_at': datetime.now().isoformat()
        }
        
        meetings_collection.insert_one(meeting)
        meeting.pop('_id', None)
        
        # Get all chat participants to send emails
        all_participants = get_all_chat_participants()
        
        # Send confirmation emails
        email_sent_count = 0
        for participant in all_participants:
            email_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: #f9f9f9;">
                    <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #667eea; margin-bottom: 20px;">🤖 Meeting Scheduled!</h2>
                        
                        <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                            <h3 style="margin-top: 0; color: #2d5a2d;">{meeting['title']}</h3>
                            <p><strong>📅 Time:</strong> {meeting['proposed_time']} ({meeting['timezone']})</p>
                            <p><strong>⏱️ Duration:</strong> {meeting['duration']}</p>
                            <p><strong>👥 Participants:</strong> {', '.join(meeting['participants'])}</p>
                            <p><strong>💡 Reasoning:</strong> {meeting['reasoning']}</p>
                        </div>
                        
                        <p style="color: #666; font-size: 14px;">
                            This meeting was automatically scheduled based on your group chat conversation 
                            using AI-powered analysis.
                        </p>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                            <p style="font-size: 12px; color: #999;">
                                Sent by AI Meeting Scheduler • Powered by Gemini AI
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            if send_personal_email(participant['email'], f"Meeting Scheduled: {meeting['title']}", email_body):
                email_sent_count += 1
        
        print(f"📧 Sent {email_sent_count} emails to chat participants")
        
        return jsonify({
            **meeting,
            'emails_sent': email_sent_count,
            'total_participants': len(all_participants)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/meetings', methods=['GET'])
def get_meetings():
    """Get all scheduled meetings"""
    try:
        meetings = list(meetings_collection.find({}, {'_id': 0}).sort('created_at', -1))
        return jsonify(meetings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/confirm-meeting/<meeting_id>', methods=['POST'])
def confirm_meeting(meeting_id):
    """Confirm a proposed meeting"""
    try:
        meeting = meetings_collection.find_one({'_id': meeting_id})
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        # Update meeting status
        meetings_collection.update_one(
            {'_id': meeting_id},
            {'$set': {'status': 'confirmed'}}
        )
        
        return jsonify({'message': 'Meeting confirmed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-all-data', methods=['DELETE'])
def clear_all_data():
    """Clear all data from database"""
    try:
        users_collection.delete_many({})
        chats_collection.delete_many({})
        meetings_collection.delete_many({})
        print("✅ All data cleared from database")
        return jsonify({'message': 'All data cleared successfully'})
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/email-config', methods=['GET'])
def get_email_config():
    """Get current email configuration (without sensitive data)"""
    return jsonify({
        'email_host': PERSONAL_EMAIL_HOST,
        'email_user': PERSONAL_EMAIL_USER,
        'configured': bool(PERSONAL_EMAIL_USER and PERSONAL_EMAIL_USER != 'your-personal-email@gmail.com')
    })

if __name__ == '__main__':
    print("🤖 AI Meeting Scheduler Backend Starting...")
    print(f"📧 Email Configuration: {PERSONAL_EMAIL_USER}")
    print(f"🗄️  MongoDB: Connected to localhost:27017")
    print(f"🔗 API Server: http://localhost:5001")
    app.run(debug=True, port=5001) 
    print("Using email user:", PERSONAL_EMAIL_USER)
    print("Using password length:", len(PERSONAL_EMAIL_PASSWORD))






