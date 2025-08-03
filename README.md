# 🤖 AI-Powered Meeting Scheduler

An intelligent web application that analyzes group chat conversations to automatically detect meeting intent, extract availability information, and schedule meetings with email confirmations sent from your personal email.

## 🚀 Features

### Core Features
- **Personal User Management**: Add your own users with the "New User" button
- **Group Chat Management**: Multi-user chat interface with real-time messaging
- **AI-Powered Analysis**: Intelligent detection of meeting intent and availability extraction
- **Automatic Meeting Scheduling**: Proposes optimal meeting times based on chat analysis
- **Personal Email Notifications**: Sends confirmation emails from YOUR personal email to all chat participants
- **Modern UI**: Beautiful, responsive interface with real-time updates

### Technical Features
- **Backend**: Python Flask API with MongoDB integration
- **Frontend**: React with modern UI components
- **AI Integration**: OpenAI GPT for intelligent chat analysis
- **Database**: MongoDB for storing users, chats, and meetings
- **Personal Email Service**: SMTP integration using your personal email

## 🛠️ Technology Stack

### Backend
- **Python 3.x** with Flask framework
- **MongoDB** for data persistence
- **OpenAI API** for AI-powered analysis
- **Personal SMTP** for email notifications

### Frontend
- **React 18** with modern hooks
- **Axios** for API communication
- **Lucide React** for icons
- **CSS3** with modern styling

## 📋 Prerequisites

- Python 3.x
- Node.js 16+
- MongoDB (running locally)
- OpenAI API key
- Personal Gmail account with app password

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Navigate to project directory
cd "data scinece"

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd frontend
npm install
```

### 2. Personal Email Configuration
Create a `.env` file in the root directory with your personal email:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Personal Email Configuration (YOUR personal email)
PERSONAL_EMAIL_HOST=smtp.gmail.com
PERSONAL_EMAIL_PORT=587
PERSONAL_EMAIL_USER=your-personal-email@gmail.com
PERSONAL_EMAIL_PASSWORD=your-personal-app-password

# MongoDB Configuration (default local)
MONGODB_URI=mongodb://localhost:27017/
```

#### Setting up Gmail App Password:
1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password for "Mail"
4. Use this app password in your `.env` file

### 3. Start MongoDB
```bash
# On macOS with Homebrew
brew services start mongodb-community

# Or start manually
mongod
```

### 4. Run the Application

#### Start Backend Server
```bash
cd backend
python app.py
```
Backend will run on: http://localhost:5001

#### Start Frontend Server
```bash
cd frontend
npm start
```
Frontend will run on: http://localhost:3000

## 🎯 How It Works

### 1. Add Personal Users
- Click the "New User" button in the Group Chat tab
- Enter name and email for your personal users
- Users are stored in MongoDB and available for chat

### 2. Group Chat
- Users can participate in a group chat
- Messages are stored in MongoDB
- Real-time chat interface with user selection

### 3. AI Analysis
- Click "Analyze Chat" to process conversation
- AI detects meeting intent and extracts availability
- Identifies participants and suggested meeting times

### 4. Meeting Scheduling
- AI proposes optimal meeting time based on availability
- Automatically schedules meeting if majority agrees
- Sends confirmation emails from YOUR personal email to ALL chat participants

### 5. Meeting Management
- View all scheduled meetings
- Track meeting status and details
- See email delivery status

## 📊 API Endpoints

### Users
- `GET /api/users` - Get all users
- `POST /api/users` - Create new user

### Chat
- `GET /api/chats` - Get all chat messages
- `POST /api/chats` - Create new message

### Analysis
- `POST /api/analyze-chat` - Analyze chat for meeting intent

### Meetings
- `GET /api/meetings` - Get all scheduled meetings
- `POST /api/schedule-meeting` - Schedule new meeting
- `POST /api/confirm-meeting/<id>` - Confirm meeting

### Email Configuration
- `GET /api/email-config` - Get email configuration status

## 🗄️ Database Schema

### Users Collection
```json
{
  "name": "string",
  "email": "string",
  "created_at": "datetime"
}
```

### Chats Collection
```json
{
  "user_name": "string",
  "user_email": "string",
  "message": "string",
  "timestamp": "datetime"
}
```

### Meetings Collection
```json
{
  "title": "string",
  "proposed_time": "datetime",
  "timezone": "string",
  "duration": "string",
  "participants": ["string"],
  "reasoning": "string",
  "status": "string",
  "created_at": "datetime",
  "emails_sent": "number",
  "total_participants": "number"
}
```

## 🎨 UI Features

### Modern Design
- Gradient backgrounds and smooth animations
- Responsive layout for all devices
- Intuitive tab-based navigation

### Interactive Elements
- **New User Button**: Add personal users with name and email
- Real-time chat interface
- User selection dropdown
- Loading spinners and status indicators
- Success/error notifications
- Email configuration status indicator

### Tab Navigation
- **Group Chat**: Real-time messaging interface with user management
- **AI Analysis**: Chat analysis and meeting detection
- **Meetings**: View scheduled meetings with email status

## 🔧 Configuration

### OpenAI API
1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to `.env` file
3. AI will analyze chat conversations for meeting intent

### Personal Email Configuration
1. **Enable 2-factor authentication** on your Gmail account
2. **Generate app password** for "Mail" in Google Account settings
3. **Add your personal email credentials** to `.env` file:
   ```env
   PERSONAL_EMAIL_USER=your-personal-email@gmail.com
   PERSONAL_EMAIL_PASSWORD=your-app-password
   ```
4. **Meeting confirmations** will be sent from YOUR email to all chat participants

### MongoDB
- Default: `mongodb://localhost:27017/`
- Database: `meeting_scheduler`
- Collections: `users`, `chats`, `meetings`

## 🧪 Clean Application

The application starts completely clean with no demo data:
- **No pre-loaded users** - Add your own users with the "New User" button
- **No pre-loaded chat** - Start fresh conversations
- **Real AI analysis** - Only analyzes your actual chat data
- **Personal meetings** - Schedule meetings with your real participants

## 🚀 Success Criteria Met

✅ **Personal User Management**: Add your own users with the "New User" button  
✅ **Clean Start**: No demo data - completely fresh application  
✅ **Real-time Interaction**: Users can send messages and switch between users  
✅ **AI Analysis**: Agent extracts availability and computes meeting time  
✅ **Meeting Scheduling**: Automatically schedules when majority agrees  
✅ **Personal Email Confirmations**: Sends emails from YOUR personal email to all participants  
✅ **Database Integration**: MongoDB stores all user and meeting data  
✅ **Modern UI**: Beautiful, responsive interface with smooth animations

## 🔮 Future Enhancements

- Real-time WebSocket connections for live chat
- Calendar integration (Google Calendar, Outlook)
- Video conferencing links (Zoom, Teams)
- Advanced AI features (sentiment analysis, conflict resolution)
- Mobile app development
- Multi-language support
- Email templates customization

## 📝 License

This project is created for the PropVivo AI/ML Coding Assessment.

---

**🎉 The application is now running!**
- Frontend: http://localhost:3000
- Backend: http://localhost:5001
- MongoDB: Running locally

**📧 Personal Email Setup:**
1. Update `.env` file with your personal Gmail credentials
2. Enable 2FA and generate app password
3. Emails will be sent from your personal email to all chat participants

Open your browser and start exploring the AI-powered meeting scheduler with personal user management and email notifications! # prop
