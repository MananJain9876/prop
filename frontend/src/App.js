import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Send, Plus } from 'lucide-react';

function App() {
  const [users, setUsers] = useState([]);
  const [chats, setChats] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [currentUser, setCurrentUser] = useState({ name: '', email: '' });
  const [newMessage, setNewMessage] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [showNewUserForm, setShowNewUserForm] = useState(false);
  const [newUserData, setNewUserData] = useState({ name: '', email: '' });
  const [emailConfig, setEmailConfig] = useState(null);

  useEffect(() => {
    // Load users from backend
    loadUsers();
    // Load email configuration
    loadEmailConfig();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await axios.get('/api/users');
      const backendUsers = response.data;
      
      if (backendUsers.length > 0) {
        setUsers(backendUsers);
        setCurrentUser(backendUsers[0]);
      } else {
        setUsers([]);
        setCurrentUser({ name: '', email: '' });
      }
    } catch (error) {
      console.error('Error loading users:', error);
      setUsers([]);
      setCurrentUser({ name: '', email: '' });
    }
  };

  const loadEmailConfig = async () => {
    try {
      const response = await axios.get('/api/email-config');
      setEmailConfig(response.data);
    } catch (error) {
      console.error('Error loading email config:', error);
      setEmailConfig({ configured: false });
    }
  };

  const addNewUser = async () => {
    if (!newUserData.name.trim() || !newUserData.email.trim()) {
      alert('Please fill in both name and email');
      return;
    }

    try {
      const response = await axios.post('/api/users', newUserData);
      const newUser = response.data;
      
      // Add to local state
      setUsers(prevUsers => [...prevUsers, newUser]);
      setCurrentUser(newUser);
      setNewUserData({ name: '', email: '' });
      setShowNewUserForm(false);
      
      alert(`✅ User "${newUser.name}" added successfully!`);
    } catch (error) {
      console.error('Error adding user:', error);
      alert('❌ Error adding user. Please try again.');
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !currentUser.name) {
      alert('Please select a user and enter a message');
      return;
    }

    const message = {
      user_name: currentUser.name,
      user_email: currentUser.email,
      message: newMessage
    };

    try {
      const response = await axios.post('/api/chats', message);
      setChats(prevChats => [...prevChats, response.data]);
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
      // Add to local state if backend fails
      setChats(prevChats => [...prevChats, { ...message, timestamp: new Date().toISOString() }]);
      setNewMessage('');
    }
  };

  const analyzeChat = async () => {
    if (chats.length === 0) {
      alert('No chat messages to analyze. Please send some messages first.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/analyze-chat');
      setAnalysis(response.data);
    } catch (error) {
      console.error('Error analyzing chat:', error);
      alert('❌ Error analyzing chat. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const scheduleMeeting = async () => {
    if (!analysis || !analysis.has_meeting_intent) {
      alert('Please analyze the chat first to detect meeting intent.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/schedule-meeting', {
        title: 'Group Meeting'
      });
      setMeetings(prevMeetings => [...prevMeetings, response.data]);
      
      const emailStatus = emailConfig?.configured ? 
        `✅ Meeting scheduled! Emails sent to ${response.data.emails_sent} participants from your personal email.` :
        `⚠️ Meeting scheduled! Email configuration not set up - no emails sent.`;
      
      alert(emailStatus);
    } catch (error) {
      console.error('Error scheduling meeting:', error);
      alert('❌ Error scheduling meeting. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🤖 Meeting Scheduler AI</h1>
        <p>AI-powered meeting scheduling based on group chat analysis</p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <button 
            className={`btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
            style={{ flex: 1 }}
          >
            💬 Group Chat
          </button>
          <button 
            className={`btn ${activeTab === 'analysis' ? 'active' : ''}`}
            onClick={() => setActiveTab('analysis')}
            style={{ flex: 1 }}
          >
            🔍 AI Analysis
          </button>
          <button 
            className={`btn ${activeTab === 'meetings' ? 'active' : ''}`}
            onClick={() => setActiveTab('meetings')}
            style={{ flex: 1 }}
          >
            📅 Meetings
          </button>
        </div>

        {activeTab === 'chat' && (
          <div>
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h3>👤 Current User</h3>
                <button 
                  className="btn" 
                  onClick={() => setShowNewUserForm(true)}
                  style={{ padding: '8px 16px', fontSize: '14px' }}
                >
                  <Plus size={16} /> New User
                </button>
              </div>
              
              {showNewUserForm ? (
                <div style={{ 
                  padding: '15px', 
                  border: '2px solid #667eea', 
                  borderRadius: '8px', 
                  marginBottom: '15px',
                  background: '#f8f9fa'
                }}>
                  <h4>➕ Add New User</h4>
                  <div style={{ marginBottom: '10px' }}>
                    <input
                      type="text"
                      className="input"
                      placeholder="Enter name..."
                      value={newUserData.name}
                      onChange={(e) => setNewUserData({...newUserData, name: e.target.value})}
                    />
                  </div>
                  <div style={{ marginBottom: '15px' }}>
                    <input
                      type="email"
                      className="input"
                      placeholder="Enter email..."
                      value={newUserData.email}
                      onChange={(e) => setNewUserData({...newUserData, email: e.target.value})}
                    />
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button className="btn" onClick={addNewUser}>
                      Add User
                    </button>
                    <button 
                      className="btn" 
                      onClick={() => setShowNewUserForm(false)}
                      style={{ background: '#6c757d' }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  {users.length === 0 ? (
                    <div style={{ 
                      padding: '15px', 
                      background: '#fff3cd', 
                      border: '1px solid #ffc107',
                      borderRadius: '8px',
                      textAlign: 'center'
                    }}>
                      <p>No users available. Click "New User" to add your first user.</p>
                    </div>
                  ) : (
                    <select 
                      className="input"
                      value={currentUser.name}
                      onChange={(e) => {
                        const user = users.find(u => u.name === e.target.value);
                        setCurrentUser(user);
                      }}
                    >
                      {users.map(user => (
                        <option key={user.email} value={user.name}>
                          {user.name} ({user.email})
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}
            </div>

            <div className="card">
              <h3>💬 Group Chat</h3>
              {chats.length === 0 ? (
                <div style={{ 
                  padding: '20px', 
                  textAlign: 'center',
                  color: '#666',
                  background: '#f8f9fa',
                  borderRadius: '8px'
                }}>
                  <p>No messages yet. Start the conversation!</p>
                </div>
              ) : (
                <div className="chat-container">
                  {chats.map((chat, index) => (
                    <div 
                      key={index} 
                      className={`message ${chat.user_name === currentUser.name ? 'sent' : 'received'}`}
                    >
                      <div className="message-header">
                        {chat.user_name} • {new Date(chat.timestamp).toLocaleString()}
                      </div>
                      {chat.message}
                    </div>
                  ))}
                </div>
              )}
              
              <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <input
                  type="text"
                  className="input"
                  placeholder="Type your message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={!currentUser.name}
                />
                <button className="btn" onClick={sendMessage} disabled={!currentUser.name}>
                  <Send size={20} />
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="grid">
            <div className="card">
              <h3>🔍 AI Analysis</h3>
              <button className="btn" onClick={analyzeChat} disabled={loading || chats.length === 0}>
                {loading ? 'Analyzing...' : 'Analyze Chat'}
              </button>
              
              {chats.length === 0 && (
                <div style={{ 
                  marginTop: '15px', 
                  padding: '15px', 
                  background: '#fff3cd', 
                  borderRadius: '8px',
                  border: '1px solid #ffc107'
                }}>
                  <p>No chat messages to analyze. Go to the Group Chat tab and send some messages first.</p>
                </div>
              )}
              
              {loading && (
                <div className="loading">
                  <div className="spinner"></div>
                </div>
              )}
              
              {analysis && (
                <div style={{ marginTop: '20px' }}>
                  <h4>Analysis Results:</h4>
                  <p><strong>Meeting Intent:</strong> {analysis.has_meeting_intent ? '✅ Yes' : '❌ No'}</p>
                  
                  {analysis.participants.length > 0 && (
                    <div>
                      <h4>👥 Participants:</h4>
                      <ul>
                        {analysis.participants.map((participant, index) => (
                          <li key={index}>{participant.name} ({participant.email})</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysis.availability_mentions.length > 0 && (
                    <div>
                      <h4>⏰ Availability Mentions:</h4>
                      {analysis.availability_mentions.map((mention, index) => (
                        <div key={index} style={{ marginBottom: '10px', padding: '10px', background: '#f8f9fa', borderRadius: '8px' }}>
                          <strong>{mention.person}:</strong> {mention.availability}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {analysis.suggested_times.length > 0 && (
                    <div>
                      <h4>📅 Suggested Times:</h4>
                      <ul>
                        {analysis.suggested_times.map((time, index) => (
                          <li key={index}>{time}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {analysis.missing_info.length > 0 && (
                    <div>
                      <h4>❓ Missing Information:</h4>
                      <ul>
                        {analysis.missing_info.map((info, index) => (
                          <li key={index}>{info}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            <div className="card">
              <h3>📅 Schedule Meeting</h3>
              <p>Based on the AI analysis, we can automatically schedule a meeting for the group.</p>
              
              {/* Email Configuration Status */}
              <div style={{ 
                marginBottom: '15px', 
                padding: '10px', 
                borderRadius: '8px',
                background: emailConfig?.configured ? '#e8f5e8' : '#fff3cd',
                border: `1px solid ${emailConfig?.configured ? '#28a745' : '#ffc107'}`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '16px' }}>📧</span>
                  <strong>Email Configuration:</strong>
                  {emailConfig?.configured ? (
                    <span style={{ color: '#28a745' }}>✅ Configured ({emailConfig.email_user})</span>
                  ) : (
                    <span style={{ color: '#856404' }}>⚠️ Not configured - Update .env file</span>
                  )}
                </div>
              </div>
              
              <button 
                className="btn" 
                onClick={scheduleMeeting} 
                disabled={loading || !analysis?.has_meeting_intent}
                style={{ marginTop: '10px' }}
              >
                {loading ? 'Scheduling...' : 'Schedule Meeting'}
              </button>
              
              {analysis && analysis.has_meeting_intent && (
                <div style={{ marginTop: '20px', padding: '15px', background: '#e8f5e8', borderRadius: '8px' }}>
                  <h4>✅ Meeting Intent Detected!</h4>
                  <p>The AI has detected meeting scheduling intent in your conversation. Click the button above to schedule the meeting.</p>
                  {emailConfig?.configured && (
                    <p style={{ marginTop: '10px', fontSize: '14px', color: '#28a745' }}>
                      📧 Emails will be sent to all chat participants from your personal email.
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'meetings' && (
          <div className="card">
            <h3>📅 Scheduled Meetings</h3>
            {meetings.length === 0 ? (
              <div style={{ 
                padding: '20px', 
                textAlign: 'center',
                color: '#666',
                background: '#f8f9fa',
                borderRadius: '8px'
              }}>
                <p>No meetings scheduled yet. Use the AI Analysis tab to schedule a meeting based on your chat.</p>
              </div>
            ) : (
              <div>
                {meetings.map((meeting, index) => (
                  <div key={index} style={{ 
                    padding: '15px', 
                    border: '1px solid #e1e5e9', 
                    borderRadius: '8px', 
                    marginBottom: '15px',
                    background: '#f8f9fa'
                  }}>
                    <h4>{meeting.title}</h4>
                    <p><strong>Time:</strong> {meeting.proposed_time} ({meeting.timezone})</p>
                    <p><strong>Duration:</strong> {meeting.duration}</p>
                    <p><strong>Participants:</strong> {meeting.participants.join(', ')}</p>
                    <p><strong>Status:</strong> {meeting.status}</p>
                    <p><strong>Reasoning:</strong> {meeting.reasoning}</p>
                    {meeting.emails_sent && (
                      <p style={{ color: '#28a745', fontWeight: 'bold' }}>
                        📧 Emails sent: {meeting.emails_sent}/{meeting.total_participants} participants
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 