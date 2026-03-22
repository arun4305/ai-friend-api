"""
AI Friend System - Complete Python Backend for Render Deployment
Flask + MySQL + AI Response Handler
Supports 8 Friends: Arun, Krishna, Vetri, Thamizh, Oviya, Gayathri, Vicky, Priya
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import json
import random
import re
from datetime import datetime
import logging
import os
import sys
from typing import Dict, List, Optional
from time import time
import urllib.parse

# ==================== CONFIGURATION ====================

class Config:
    # Database Configuration - Use environment variables for Render
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'ai_friend_system')
    
    # For Render MySQL, we need to handle the full URL format
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    
    # Server Configuration
    API_HOST = '0.0.0.0'
    API_PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # AI Configuration
    USE_LOCAL_AI = True
    MAX_RESPONSE_LENGTH = 200
    
    # Rate Limiting
    RATE_LIMIT = 60

# ==================== DATABASE HANDLER ====================

class DatabaseHandler:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def parse_database_url(self):
        """Parse database URL if provided"""
        if Config.DATABASE_URL:
            # Parse MySQL URL format: mysql://username:password@host:port/database
            parsed = urllib.parse.urlparse(Config.DATABASE_URL)
            return {
                'host': parsed.hostname,
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path[1:] if parsed.path else Config.DB_NAME,
                'port': parsed.port or 3306
            }
        return None
    
    def connect(self):
        """Establish database connection"""
        try:
            # Try to use DATABASE_URL first
            db_config = self.parse_database_url()
            
            if db_config:
                self.connection = mysql.connector.connect(
                    host=db_config['host'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database'],
                    port=db_config['port'],
                    charset='utf8mb4',
                    use_unicode=True,
                    connect_timeout=30
                )
            else:
                # Use individual environment variables
                self.connection = mysql.connector.connect(
                    host=Config.DB_HOST,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    charset='utf8mb4',
                    use_unicode=True,
                    connect_timeout=30
                )
            
            print("✓ Database connected successfully")
            return True
            
        except Error as e:
            print(f"✗ Database connection error: {e}")
            print(f"  Connection details:")
            print(f"  Host: {Config.DB_HOST}")
            print(f"  Database: {Config.DB_NAME}")
            print(f"  User: {Config.DB_USER}")
            
            if Config.DATABASE_URL:
                print("  Using DATABASE_URL connection string")
            
            # Don't raise exception - allow app to continue in development
            if Config.DEBUG:
                print("  Running in debug mode - continuing without database")
                return False
            else:
                raise
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """Execute query and return results"""
        if not self.connection:
            if Config.DEBUG:
                print("Database not connected - returning empty result")
                return [] if query.strip().upper().startswith('SELECT') else True
            return None
            
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                return result
            else:
                self.connection.commit()
                return cursor.lastrowid if cursor.lastrowid else True
                
        except Error as e:
            print(f"Query error: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def get_user_profile(self, user_id: int) -> Dict:
        """Get complete user profile"""
        query = """
            SELECT u.*, up.response_length, up.emoji_preference, 
                   up.humor_level, up.formality_level
            FROM users u
            LEFT JOIN user_preferences up ON u.id = up.user_id
            WHERE u.id = %s
        """
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_user_knowledge(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get important facts about user"""
        query = """
            SELECT * FROM user_knowledge 
            WHERE user_id = %s 
            ORDER BY importance_level DESC, created_at DESC 
            LIMIT %s
        """
        return self.execute_query(query, (user_id, limit)) or []
    
    def get_conversation_history(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get recent conversation history"""
        query = """
            SELECT message, response, timestamp 
            FROM conversations 
            WHERE user_id = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        return self.execute_query(query, (user_id, limit)) or []
    
    def save_conversation(self, user_id: int, message: str, response: str, sentiment: float):
        """Save conversation to database"""
        query = """
            INSERT INTO conversations (user_id, message, response, sentiment_score) 
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_query(query, (user_id, message, response, sentiment))
    
    def add_user_knowledge(self, user_id: int, category: str, fact: str, importance: int = 5):
        """Add new knowledge about user"""
        query = """
            INSERT INTO user_knowledge (user_id, category, fact, importance_level) 
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_query(query, (user_id, category, fact, importance))
    
    def get_all_users(self) -> List[Dict]:
        """Get list of all friends"""
        query = "SELECT id, name, age, occupation, interests FROM users ORDER BY name"
        return self.execute_query(query) or []
    
    def initialize_database(self):
        """Create tables if they don't exist"""
        if not self.connection:
            print("No database connection - skipping table creation")
            return
        
        try:
            # Create users table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    age INT,
                    occupation VARCHAR(100),
                    interests TEXT,
                    personality_type VARCHAR(50),
                    communication_style VARCHAR(50),
                    preferred_language VARCHAR(50) DEFAULT 'English',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create conversations table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    message TEXT,
                    response TEXT,
                    sentiment_score FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create user_knowledge table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS user_knowledge (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    category VARCHAR(100),
                    fact TEXT,
                    importance_level INT DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create user_preferences table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT UNIQUE,
                    response_length VARCHAR(20) DEFAULT 'medium',
                    emoji_preference BOOLEAN DEFAULT TRUE,
                    humor_level INT DEFAULT 5,
                    formality_level INT DEFAULT 5,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create training data table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS ai_training_data (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    trigger_pattern VARCHAR(255),
                    response_template TEXT,
                    context VARCHAR(100),
                    priority INT DEFAULT 5,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create relationship settings table
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS user_relationship_settings (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT UNIQUE,
                    greeting_style VARCHAR(50) DEFAULT 'casual',
                    name_prefix VARCHAR(20),
                    language_preference VARCHAR(20) DEFAULT 'bilingual',
                    emotional_tone VARCHAR(20) DEFAULT 'friendly',
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            print("✓ Database tables created/verified")
            
        except Error as e:
            print(f"Error creating tables: {e}")
            raise

# ==================== AI RESPONSE HANDLER ====================

class AIResponseHandler:
    def __init__(self):
        self.db = None
        self.conversation_templates = self.load_templates()
    
    def set_database(self, db):
        self.db = db
    
    def load_templates(self):
        """Load conversation templates"""
        return {
            'greetings': [
                "Hey {name}! Great to chat with you! 😊",
                "Hello {name}! How's everything going today? 🌟",
                "Hi {name}! Ready for a great conversation? 💫",
                "Hey there {name}! What's new in your world? 🚀"
            ],
            'how_are_you': [
                "I'm doing fantastic! Thanks for asking! How about you? 😊",
                "Feeling great today! Tell me about your day! 🌈",
                "I'm wonderful! What's making you happy today? 💝"
            ],
            'good_day': [
                "That's awesome to hear! 🎉 What made your day so good?",
                "I'm so happy for you! Tell me more about it! 🌟",
                "That's wonderful! Spread that positivity! ✨"
            ],
            'bad_day': [
                "I'm sorry to hear that. I'm here for you. Want to talk about it? 🤗",
                "That sounds tough. Remember, bad days don't last forever. 💪",
                "I'm here to listen. Sometimes sharing helps. 💝"
            ]
        }
    
    def get_ai_response(self, user_profile: Dict, user_knowledge: List[Dict], 
                        conversation_history: List[Dict], message: str) -> str:
        """Generate personalized response"""
        
        name = user_profile['name']
        style = user_profile.get('communication_style', 'Friendly')
        
        # Check training data first
        training_response = self.check_training_data(user_profile['id'], message, name)
        if training_response:
            return training_response
        
        message_lower = message.lower()
        
        # Greetings
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            return random.choice(self.conversation_templates['greetings']).format(name=name)
        
        # How are you
        if 'how are you' in message_lower:
            return random.choice(self.conversation_templates['how_are_you'])
        
        # Emotional responses
        if any(word in message_lower for word in ['happy', 'great', 'wonderful', 'awesome', 'excited']):
            return random.choice(self.conversation_templates['good_day'])
        
        if any(word in message_lower for word in ['sad', 'upset', 'bad', 'terrible', 'depressed', 'tired']):
            return random.choice(self.conversation_templates['bad_day'])
        
        # Work related
        if any(word in message_lower for word in ['work', 'job', 'project', 'office']):
            if 'code' in message_lower or 'programming' in message_lower:
                return f"How's your coding project coming along, {name}? Need any help? 💻"
            return f"How's work treating you, {name}? Anything exciting happening? 💼"
        
        # Coding/Tech
        if any(word in message_lower for word in ['code', 'programming', 'python', 'flutter']):
            responses = [
                f"That's awesome, {name}! What are you building? 💻",
                f"Tech is fascinating! Tell me more about your project! 🚀",
                f"Coding is like magic! What language are you working with? ✨"
            ]
            return random.choice(responses)
        
        # Art/Creative
        if any(word in message_lower for word in ['art', 'draw', 'paint', 'design']):
            responses = [
                f"Art is beautiful, {name}! What are you creating? 🎨",
                f"I love hearing about creative projects! Tell me more! ✨",
                f"That sounds amazing! What's your inspiration? 🌈"
            ]
            return random.choice(responses)
        
        # Travel
        if any(word in message_lower for word in ['travel', 'trip', 'vacation']):
            responses = [
                f"Travel is life-changing, {name}! Where are you planning to go? ✈️",
                f"I love travel stories! Tell me about your adventures! 🌍",
                f"Exploring new places is amazing! Where's your next destination? 🗺️"
            ]
            return random.choice(responses)
        
        # Default responses
        default_responses = [
            f"That's interesting, {name}! Tell me more about that. 😊",
            f"I'm curious to know more. What else is on your mind? 💭",
            f"Thanks for sharing! What's your take on that? 🌟",
            f"I'm all ears! Tell me everything! 👂"
        ]
        
        return random.choice(default_responses)
    
    def check_training_data(self, user_id: int, message: str, name: str) -> str:
        """Check training data for matching patterns"""
        if not self.db:
            return None
        
        message_lower = message.lower()
        
        query = """
            SELECT trigger_pattern, response_template, priority 
            FROM ai_training_data 
            WHERE user_id = %s AND is_active = TRUE 
            ORDER BY priority DESC
        """
        patterns = self.db.execute_query(query, (user_id,))
        
        if not patterns:
            return None
        
        for pattern in patterns:
            triggers = pattern['trigger_pattern'].split('|')
            for trigger in triggers:
                if trigger in message_lower:
                    response = pattern['response_template']
                    response = response.replace('{name}', name)
                    return response
        
        return None
    
    def analyze_sentiment(self, message: str) -> float:
        """Simple sentiment analysis"""
        positive_words = ['happy', 'great', 'good', 'wonderful', 'excellent', 'love', 'amazing', 'awesome']
        negative_words = ['sad', 'bad', 'terrible', 'awful', 'hate', 'upset', 'angry', 'depressed']
        
        score = 0.5
        for word in positive_words:
            if word in message.lower():
                score += 0.1
        for word in negative_words:
            if word in message.lower():
                score -= 0.1
        
        return max(0.0, min(1.0, score))

# ==================== FLASK APPLICATION ====================

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter

# Initialize components
db = DatabaseHandler()
ai_handler = AIResponseHandler()
ai_handler.set_database(db)

# Rate limiting dictionary
rate_limits = {}

def check_rate_limit(user_id: int) -> bool:
    """Check if user has exceeded rate limit"""
    current_time = time()
    if user_id not in rate_limits:
        rate_limits[user_id] = []
    
    rate_limits[user_id] = [t for t in rate_limits[user_id] if current_time - t < 60]
    
    if len(rate_limits[user_id]) >= Config.RATE_LIMIT:
        return False
    
    rate_limits[user_id].append(current_time)
    return True

# ==================== API ENDPOINTS ====================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not user_id or not message:
            return jsonify({'error': 'Missing user_id or message'}), 400
        
        if not check_rate_limit(user_id):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Get user profile
        user_profile = db.get_user_profile(user_id)
        if not user_profile:
            # Return default response if user not found
            return jsonify({
                'response': f"Hello! I'm your AI friend. How can I help you today? 😊",
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'sentiment': 0.5
            })
        
        # Get user knowledge and history
        user_knowledge = db.get_user_knowledge(user_id)
        conversation_history = db.get_conversation_history(user_id)
        
        # Generate AI response
        response = ai_handler.get_ai_response(
            user_profile, user_knowledge, conversation_history, message
        )
        
        # Analyze sentiment
        sentiment = ai_handler.analyze_sentiment(message)
        
        # Save conversation if database is connected
        if db.connection:
            db.save_conversation(user_id, message, response, sentiment)
        
        return jsonify({
            'response': response,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'sentiment': sentiment
        })
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get list of all friends"""
    try:
        users = db.get_all_users()
        return jsonify({
            'users': users,
            'count': len(users)
        })
    except Exception as e:
        print(f"Error getting users: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile"""
    try:
        profile = db.get_user_profile(user_id)
        if not profile:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': profile})
    except Exception as e:
        print(f"Error getting user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>/history', methods=['GET'])
def get_user_history(user_id):
    """Get conversation history"""
    try:
        limit = request.args.get('limit', default=20, type=int)
        history = db.get_conversation_history(user_id, limit)
        return jsonify({
            'history': history,
            'count': len(history)
        })
    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db.connection else 'disconnected'
    })

@app.route('/api/init', methods=['POST'])
def initialize_database():
    """Initialize database with sample data"""
    try:
        if not db.connection:
            return jsonify({'error': 'Database not connected'}), 500
            
        # Create tables
        db.initialize_database()
        
        # Check if users exist
        users = db.get_all_users()
        if not users:
            # Insert friends data
            friends = [
                ('Arun', 28, 'Software Developer', 'Coding, AI, Gaming, Tech News', 'Analytical', 'Technical and precise'),
                ('Krishna', 26, 'Graphic Designer', 'Art, Design, Photography, Music', 'Creative', 'Artistic and expressive'),
                ('Vetri', 30, 'Engineer', 'Cars, Travel, Adventure Sports', 'Adventurous', 'Energetic and enthusiastic'),
                ('Thamizh', 25, 'Teacher', 'Tamil Literature, Teaching, Poetry', 'Intellectual', 'Thoughtful and patient'),
                ('Oviya', 24, 'Medical Student', 'Healthcare, Volunteering, Yoga', 'Caring', 'Empathetic and warm'),
                ('Gayathri', 27, 'Content Writer', 'Writing, Reading, Philosophy', 'Reflective', 'Articulate and detailed'),
                ('Vicky', 29, 'Business Analyst', 'Business, Analytics, Strategy', 'Strategic', 'Professional and structured'),
                ('Priya', 31, 'Artist', 'Painting, Sculpture, Travel', 'Artistic', 'Creative and emotional')
            ]
            
            for friend in friends:
                query = """
                    INSERT INTO users (name, age, occupation, interests, personality_type, communication_style)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                user_id = db.execute_query(query, friend)
                
                if user_id:
                    # Add default preferences
                    pref_query = """
                        INSERT INTO user_preferences (user_id) VALUES (%s)
                    """
                    db.execute_query(pref_query, (user_id,))
                    
                    # Add relationship settings
                    rel_query = """
                        INSERT INTO user_relationship_settings (user_id, greeting_style, name_prefix) 
                        VALUES (%s, %s, %s)
                    """
                    prefix = 'da' if friend[0] == 'Arun' else ''
                    db.execute_query(rel_query, (user_id, 'casual', prefix))
        
        return jsonify({'success': True, 'message': 'Database initialized successfully'})
    except Exception as e:
        print(f"Error initializing database: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/seed', methods=['POST'])
def seed_sample_conversations():
    """Seed sample conversations for testing"""
    try:
        if not db.connection:
            return jsonify({'error': 'Database not connected'}), 500
            
        users = db.get_all_users()
        sample_messages = [
            "Hi, how are you?",
            "What's new?",
            "I'm working on a coding project",
            "I feel great today!",
            "Had a tough day at work"
        ]
        
        sample_responses = [
            "Hey! I'm doing great! How about you?",
            "Not much, just chatting with friends! You?",
            "That's awesome! What are you building?",
            "That's wonderful! Tell me more!",
            "Sorry to hear that. Want to talk about it?"
        ]
        
        for user in users:
            for i in range(3):
                message = random.choice(sample_messages)
                response = random.choice(sample_responses)
                sentiment = ai_handler.analyze_sentiment(message)
                db.save_conversation(user['id'], message, response, sentiment)
        
        return jsonify({'success': True, 'message': 'Sample conversations seeded'})
    except Exception as e:
        print(f"Error seeding conversations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-history/<int:user_id>', methods=['DELETE'])
def clear_user_history(user_id):
    """Clear conversation history for a user"""
    try:
        query = "DELETE FROM conversations WHERE user_id = %s"
        db.execute_query(query, (user_id,))
        return jsonify({'success': True, 'message': 'History cleared'})
    except Exception as e:
        print(f"Error clearing history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training-data/<int:user_id>', methods=['GET'])
def get_training_data(user_id):
    """Get training data for a user"""
    try:
        query = "SELECT * FROM ai_training_data WHERE user_id = %s ORDER BY priority DESC"
        data = db.execute_query(query, (user_id,))
        return jsonify({'training_data': data or []})
    except Exception as e:
        print(f"Error getting training data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training-data', methods=['POST'])
def add_training_data():
    """Add training data for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        trigger_pattern = data.get('trigger_pattern')
        response_template = data.get('response_template')
        context = data.get('context', 'general')
        priority = data.get('priority', 5)
        
        if not all([user_id, trigger_pattern, response_template]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        query = """
            INSERT INTO ai_training_data (user_id, trigger_pattern, response_template, context, priority)
            VALUES (%s, %s, %s, %s, %s)
        """
        db.execute_query(query, (user_id, trigger_pattern, response_template, context, priority))
        
        return jsonify({'success': True, 'message': 'Training data added'})
    except Exception as e:
        print(f"Error adding training data: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== MAIN ENTRY POINT ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 AI FRIEND SYSTEM - STARTING...")
    print("="*60)
    print(f"📱 Server: http://{Config.API_HOST}:{Config.API_PORT}")
    print(f"🗄️  Database: MySQL ({'Connected' if db.connection else 'Disconnected'})")
    print("👥 Friends: Arun, Krishna, Vetri, Thamizh, Oviya, Gayathri, Vicky, Priya")
    print("="*60)
    print("\n📡 API Endpoints:")
    print("   POST   /api/chat            - Send message to AI")
    print("   GET    /api/users           - List all friends")
    print("   GET    /api/user/<id>       - Get friend profile")
    print("   GET    /api/user/<id>/history - Get conversation history")
    print("   POST   /api/init            - Initialize database")
    print("   POST   /api/seed            - Seed sample conversations")
    print("   DELETE /api/clear-history/<id> - Clear user history")
    print("   GET    /api/training-data/<id> - Get training data")
    print("   POST   /api/training-data   - Add training data")
    print("   GET    /api/health          - Health check")
    print("="*60 + "\n")
    
    # Initialize database tables if connected
    if db.connection:
        try:
            db.initialize_database()
            print("✓ Database tables ready")
        except Exception as e:
            print(f"⚠️  Database initialization warning: {e}")
    else:
        print("⚠️  Running without database connection")
    
    # Run Flask app
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=Config.DEBUG
    )
