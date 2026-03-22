"""
AI Friend System - Complete Python Backend
In-Memory Database (No XAMPP Required)
All data loaded from SQL file into Python structures
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import random
import re
from datetime import datetime
from typing import Dict, List, Optional
import os

# ==================== IN-MEMORY DATABASE ====================

class InMemoryDatabase:
    """In-memory database that loads all data from SQL file"""
    
    def __init__(self):
        self.users = []
        self.conversations = []
        self.user_knowledge = []
        self.user_preferences = []
        self.user_relationship_settings = []
        self.training_data = {}  # user_id -> list of training patterns
        self.conversation_memory = []
        
        # Load all data
        self.load_all_data()
    
    def load_all_data(self):
        """Load all data from the SQL structure into memory"""
        
        # ==================== USERS DATA (Changed Priya to Nithya) ====================
        self.users = [
            {'id': 1, 'name': 'Arun', 'age': 28, 'occupation': 'Software Developer', 
             'interests': 'Coding, AI, Gaming, Tech News', 'personality_type': 'Analytical',
             'communication_style': 'Technical and precise', 'preferred_language': 'English'},
            {'id': 2, 'name': 'Krishna', 'age': 26, 'occupation': 'Graphic Designer',
             'interests': 'Art, Design, Photography, Music', 'personality_type': 'Creative',
             'communication_style': 'Artistic and expressive', 'preferred_language': 'English'},
            {'id': 3, 'name': 'Vetri', 'age': 30, 'occupation': 'Engineer',
             'interests': 'Cars, Travel, Adventure Sports', 'personality_type': 'Adventurous',
             'communication_style': 'Energetic and enthusiastic', 'preferred_language': 'English'},
            {'id': 4, 'name': 'Thamizh', 'age': 25, 'occupation': 'Teacher',
             'interests': 'Tamil Literature, Teaching, Poetry', 'personality_type': 'Intellectual',
             'communication_style': 'Thoughtful and patient', 'preferred_language': 'English'},
            {'id': 5, 'name': 'Oviya', 'age': 24, 'occupation': 'Medical Student',
             'interests': 'Healthcare, Volunteering, Yoga', 'personality_type': 'Caring',
             'communication_style': 'Empathetic and warm', 'preferred_language': 'English'},
            {'id': 6, 'name': 'Gayathri', 'age': 27, 'occupation': 'Content Writer',
             'interests': 'Writing, Reading, Philosophy', 'personality_type': 'Reflective',
             'communication_style': 'Articulate and detailed', 'preferred_language': 'English'},
            {'id': 7, 'name': 'Vicky', 'age': 29, 'occupation': 'Business Analyst',
             'interests': 'Business, Analytics, Strategy', 'personality_type': 'Strategic',
             'communication_style': 'Professional and structured', 'preferred_language': 'English'},
            {'id': 8, 'name': 'Nithya', 'age': 31, 'occupation': 'Artist',  # Changed from Priya to Nithya
             'interests': 'Painting, Sculpture, Travel', 'personality_type': 'Artistic',
             'communication_style': 'Creative and emotional', 'preferred_language': 'English'},
        ]
        
        # ==================== USER PREFERENCES ====================
        self.user_preferences = [
            {'user_id': 1, 'response_length': 'medium', 'emoji_preference': 1, 'humor_level': 5, 'formality_level': 5},
            {'user_id': 2, 'response_length': 'medium', 'emoji_preference': 1, 'humor_level': 5, 'formality_level': 5},
            {'user_id': 3, 'response_length': 'medium', 'emoji_preference': 1, 'humor_level': 5, 'formality_level': 5},
            {'user_id': 4, 'response_length': 'medium', 'emoji_preference': 1, 'humor_level': 5, 'formality_level': 5},
            {'user_id': 5, 'response_length': 'medium', 'emoji_preference': 1, 'humor_level': 5, 'formality_level': 5},
            {'user_id': 6, 'response_length': 'medium', 'emoji_preference': 1, 'humor_level': 5, 'formality_level': 5},
            {'user_id': 7, 'response_length': 'medium', 'emoji_preference': 1, 'humor_level': 5, 'formality_level': 5},
            {'user_id': 8, 'response_length': 'medium', 'emoji_preference': 1, 'humor_level': 5, 'formality_level': 5},
        ]
        
        # ==================== USER RELATIONSHIP SETTINGS ====================
        self.user_relationship_settings = [
            {'user_id': 1, 'greeting_style': 'casual', 'name_prefix': 'da', 'language_preference': 'bilingual', 'emotional_tone': 'friendly'},
            {'user_id': 2, 'greeting_style': 'casual', 'name_prefix': 'machi', 'language_preference': 'bilingual', 'emotional_tone': 'friendly'},
            {'user_id': 3, 'greeting_style': 'casual', 'name_prefix': 'da', 'language_preference': 'bilingual', 'emotional_tone': 'energetic'},
            {'user_id': 4, 'greeting_style': 'formal', 'name_prefix': 'ji', 'language_preference': 'bilingual', 'emotional_tone': 'calm'},
            {'user_id': 5, 'greeting_style': 'friendly', 'name_prefix': 'Collector', 'language_preference': 'bilingual', 'emotional_tone': 'caring'},
            {'user_id': 6, 'greeting_style': 'casual', 'name_prefix': '', 'language_preference': 'bilingual', 'emotional_tone': 'thoughtful'},
            {'user_id': 7, 'greeting_style': 'casual', 'name_prefix': '', 'language_preference': 'bilingual', 'emotional_tone': 'professional'},
            {'user_id': 8, 'greeting_style': 'casual', 'name_prefix': '', 'language_preference': 'bilingual', 'emotional_tone': 'artistic'},
        ]
        
        # ==================== USER KNOWLEDGE (Updated for Nithya) ====================
        self.user_knowledge = [
            {'id': 1, 'user_id': 1, 'category': 'Work', 'fact': 'Currently learning advanced Python and AI', 'importance_level': 10},
            {'id': 2, 'user_id': 1, 'category': 'Hobby', 'fact': 'Plays chess regularly', 'importance_level': 7},
            {'id': 3, 'user_id': 1, 'category': 'Life', 'fact': 'Recently started a new AI project', 'importance_level': 9},
            {'id': 4, 'user_id': 2, 'category': 'Art', 'fact': 'Working on a digital art portfolio', 'importance_level': 10},
            {'id': 5, 'user_id': 2, 'category': 'Music', 'fact': 'Plays guitar in free time', 'importance_level': 8},
            {'id': 6, 'user_id': 3, 'category': 'Travel', 'fact': 'Planning a motorcycle trip to Himalayas', 'importance_level': 9},
            {'id': 7, 'user_id': 3, 'category': 'Sports', 'fact': 'Enjoys trekking and rock climbing', 'importance_level': 8},
            {'id': 8, 'user_id': 4, 'category': 'Literature', 'fact': 'Writing Tamil poetry collection', 'importance_level': 10},
            {'id': 9, 'user_id': 4, 'category': 'Teaching', 'fact': 'Loves teaching classical Tamil', 'importance_level': 9},
            {'id': 10, 'user_id': 5, 'category': 'Studies', 'fact': 'Preparing for medical exams', 'importance_level': 10},
            {'id': 11, 'user_id': 5, 'category': 'Wellness', 'fact': 'Practices meditation daily', 'importance_level': 8},
            {'id': 12, 'user_id': 6, 'category': 'Writing', 'fact': 'Working on a novel', 'importance_level': 9},
            {'id': 13, 'user_id': 6, 'category': 'Reading', 'fact': 'Loves philosophical books', 'importance_level': 8},
            {'id': 14, 'user_id': 7, 'category': 'Work', 'fact': 'Learning data science', 'importance_level': 7},
            {'id': 15, 'user_id': 7, 'category': 'Hobby', 'fact': 'Plays badminton', 'importance_level': 6},
            {'id': 16, 'user_id': 8, 'category': 'Art', 'fact': 'Preparing for art exhibition', 'importance_level': 10},
            {'id': 17, 'user_id': 8, 'category': 'Travel', 'fact': 'Dreams of visiting Paris', 'importance_level': 8},
        ]
        
        # ==================== TRAINING DATA (Updated for Nithya) ====================
        self.training_data = {
            1: [  # Arun's training patterns
                {'trigger_pattern': 'hi|hello|hey', 'response_template': 'Hey da {name}! Enna panra? Code illa coffee? ☕', 'priority': 10},
                {'trigger_pattern': 'how are you|how r u', 'response_template': 'Nalla iruken da! Neenga solunga! 😊', 'priority': 9},
                {'trigger_pattern': 'whats up|enna panra', 'response_template': 'Ketta kelvi da! Nee enna panra sollu! 🤔', 'priority': 9},
                {'trigger_pattern': 'saptiya|food|lunch|dinner', 'response_template': 'Sapten da! Unaku enna? Biryani order pannu! 🍗', 'priority': 8},
                {'trigger_pattern': 'code|programming|python|flutter', 'response_template': 'Aiyo da! Code ah? Show me! Debug pannalam! 💻', 'priority': 10},
                {'trigger_pattern': 'bug|error|mistake', 'response_template': 'Bug ah da? Adha nee create pannathu dha! Enna kodumai! 😂', 'priority': 10},
                {'trigger_pattern': 'project|work', 'response_template': 'Project ah? Super da! Endha framework? React ah? 🚀', 'priority': 9},
                {'trigger_pattern': 'game|play|chess', 'response_template': 'Game ah? Ready da! Nee tholachu! GG! 🎮', 'priority': 9},
                {'trigger_pattern': 'sad|upset|bad day', 'response_template': 'Dei enna achu? Sollu da! Iruken na! Free la pesu! 🫂', 'priority': 10},
                {'trigger_pattern': 'happy|excited|good', 'response_template': 'Semma da! Appadi dha irukkanum! Party! 🎉', 'priority': 9},
                {'trigger_pattern': 'bye|goodnight|sleep', 'response_template': 'Seri da! Kalai la pesalam! Good night! 🌙', 'priority': 9},
                {'trigger_pattern': 'coffee|tea|kudikka', 'response_template': 'Coffee podu da! Sleep ah odachu! ☕', 'priority': 8},
                {'trigger_pattern': 'stress|tension', 'response_template': 'Tension aagatha da! Chill pannu! Irukom la! 😎', 'priority': 8},
                {'trigger_pattern': 'good morning', 'response_template': 'Good morning da! Kalai vanakkam! Coffee pottu code pannalam! ☀️', 'priority': 9},
                {'trigger_pattern': 'good evening', 'response_template': 'Good evening da! Evening coding session ready ah? 🌙', 'priority': 9},
            ],
            2: [  # Krishna's training patterns
                {'trigger_pattern': 'hi|hello|hey', 'response_template': 'Hey machi {name}! Enna color la irukka? Red ah blue ah? 🎨', 'priority': 10},
                {'trigger_pattern': 'how are you|how r u', 'response_template': 'Semma creative ah iruken machi! Neenga sollunga! 🌈', 'priority': 9},
                {'trigger_pattern': 'art|draw|paint', 'response_template': 'Show me machi! Un art ku waiting! Super ah irukum! 🎨', 'priority': 10},
                {'trigger_pattern': 'color|palette', 'response_template': 'Blue and gold machi! Try pannu! King size ah irukum! 👑', 'priority': 9},
                {'trigger_pattern': 'music|song|guitar', 'response_template': 'Music ah? Enna kelvi kekuringa? Spotify share pannu! 🎸', 'priority': 8},
                {'trigger_pattern': 'creative|idea', 'response_template': 'Idea super machi! Execute pannu! Next level ah irukum! 🔥', 'priority': 9},
                {'trigger_pattern': 'sad|upset', 'response_template': 'Art pannu machi! Feelings ah express pannu! Color pottu vidu! 🎨', 'priority': 9},
                {'trigger_pattern': 'happy|excited', 'response_template': 'Colorful day ah machi? Appadi dha! 🌈', 'priority': 8},
                {'trigger_pattern': 'bye|goodnight', 'response_template': 'Bye machi! Colors full ah irukanum! Sweet dreams! 🌙', 'priority': 8},
            ],
            3: [  # Vetri's training patterns
                {'trigger_pattern': 'hi|hello|hey', 'response_template': 'Yo da {name}! Enna scene? Mass uh irukka? 🏍️', 'priority': 10},
                {'trigger_pattern': 'how are you|how r u', 'response_template': 'Mass da! Full energy! Nee solunga! 💪', 'priority': 9},
                {'trigger_pattern': 'bike|motorcycle|ride', 'response_template': 'Royal Enfield da! Dream machine! Oru vaati vandu podanum! 🏍️', 'priority': 10},
                {'trigger_pattern': 'travel|trip|ladakh', 'response_template': 'Ladakh plan da! Ready ah? Life changing experience! 🏔️', 'priority': 10},
                {'trigger_pattern': 'sport|game|play', 'response_template': 'Cricket da? Illa football? Nee choice pannu! ⚽', 'priority': 9},
                {'trigger_pattern': 'sad|upset', 'response_template': 'Dei tension aagatha! Ride pogalam da! Clear pannidalam! 🏍️', 'priority': 9},
                {'trigger_pattern': 'happy|excited', 'response_template': 'Super da! Life ah enjoy pannu! Mass uh! 🔥', 'priority': 8},
                {'trigger_pattern': 'bye|goodnight', 'response_template': 'Bye da! Kalai la ride ku ready ah iru! 🌙', 'priority': 8},
            ],
            4: [  # Thamizh's training patterns
                {'trigger_pattern': 'hi|hello|hey', 'response_template': 'Vanakkam {name} ji! Ulagam enga poguthu? Enna visayam? 📚', 'priority': 10},
                {'trigger_pattern': 'how are you|how r u', 'response_template': 'Nalla iruken ji! Manasukku enna? Sollunga! 😌', 'priority': 9},
                {'trigger_pattern': 'book|read|poetry', 'response_template': 'Bharathiyar padichiya ji? Super ah irukum! Athu vera level! 📖', 'priority': 10},
                {'trigger_pattern': 'life|meaning|purpose', 'response_template': 'Life apdi dha ji! Porumai venum! Waves like ocean! 🌊', 'priority': 10},
                {'trigger_pattern': 'sad|upset|pain', 'response_template': 'Kavalai padaathe ji! Nalla kalam varum! Irukom la! 🌈', 'priority': 10},
                {'trigger_pattern': 'love|feeling|heart', 'response_template': 'Love ah ji? Pure dha irukanum! Heart sollum! 💖', 'priority': 9},
                {'trigger_pattern': 'bye|goodnight', 'response_template': 'Iniya iravu ji! Nalla kana kaanum! Peace! 🌙', 'priority': 8},
            ],
            5: [  # Oviya's training patterns
                {'trigger_pattern': 'hi|hello|hey', 'response_template': 'Hi {name} Collector! How are you feeling today? 💝', 'priority': 10},
                {'trigger_pattern': 'how are you|how r u', 'response_template': 'I\'m here for you, Collector! Tell me everything! 🤗', 'priority': 9},
                {'trigger_pattern': 'study|exam|medical', 'response_template': 'Study hard Collector! You\'ll be an amazing doctor! 👩‍⚕️', 'priority': 10},
                {'trigger_pattern': 'health|wellness|yoga', 'response_template': 'Take care of yourself Collector! Yoga helps! Want to join? 🧘', 'priority': 9},
                {'trigger_pattern': 'sad|upset|lonely', 'response_template': 'I\'m here Collector! Want to talk? Let it out! 🤗', 'priority': 10},
                {'trigger_pattern': 'happy|excited', 'response_template': 'That\'s wonderful Collector! Spread the joy! 🌸', 'priority': 9},
                {'trigger_pattern': 'bye|goodnight', 'response_template': 'Goodnight Collector! Sweet dreams! Take rest! 🌙', 'priority': 8},
            ],
            6: [  # Gayathri's training patterns
                {'trigger_pattern': 'hi|hello|hey', 'response_template': 'Hello {name}! What stories are we weaving today? 📝', 'priority': 10},
                {'trigger_pattern': 'how are you|how r u', 'response_template': 'I\'m feeling inspired! What words describe your day? ✨', 'priority': 9},
                {'trigger_pattern': 'write|article|blog', 'response_template': 'Write your story! Your words are powerful! Every word matters! 📝', 'priority': 10},
                {'trigger_pattern': 'book|read|novel', 'response_template': 'What book are you reading? Tell me! I need recommendations! 📚', 'priority': 9},
                {'trigger_pattern': 'thought|idea|think', 'response_template': 'Deep thoughts! What\'s on your mind? Let\'s explore! 💭', 'priority': 9},
                {'trigger_pattern': 'bye|goodnight', 'response_template': 'Goodnight! Sweet dreams and beautiful thoughts! Write tomorrow! 🌙', 'priority': 8},
            ],
            7: [  # Vicky's training patterns
                {'trigger_pattern': 'hi|hello|hey', 'response_template': 'Yo {name}! Ready for action? Let\'s hustle! 💼', 'priority': 10},
                {'trigger_pattern': 'how are you|how r u', 'response_template': 'Doing great! Let\'s make today productive! 📊', 'priority': 9},
                {'trigger_pattern': 'work|analysis|data', 'response_template': 'Data tells stories! What are you analyzing? Let\'s crack it! 📈', 'priority': 10},
                {'trigger_pattern': 'strategy|business', 'response_template': 'Strategic thinking is key! Share your insights! Let\'s win! 💡', 'priority': 9},
                {'trigger_pattern': 'project|task|deadline', 'response_template': 'Let\'s plan it out! I know you\'ll crush it! 🎯', 'priority': 9},
                {'trigger_pattern': 'bye|goodnight', 'response_template': 'Goodnight! Tomorrow is another opportunity! Let\'s get it! 🌙', 'priority': 8},
            ],
            8: [  # Nithya's training patterns (Updated from Priya)
                {'trigger_pattern': 'hi|hello|hey', 'response_template': 'Hey {name}! What colors are you feeling today? Red? Blue? Rainbow? 🎨', 'priority': 10},
                {'trigger_pattern': 'how are you|how r u', 'response_template': 'I\'m feeling artistic! What inspires your soul? 🌈', 'priority': 9},
                {'trigger_pattern': 'art|paint|draw', 'response_template': 'Your art is amazing, {name}! Show me what you created! Every stroke matters! 🎨', 'priority': 10},
                {'trigger_pattern': 'color|palette', 'response_template': 'Colors speak, {name}! What palette speaks to you today? Mix pannu! 🎨', 'priority': 9},
                {'trigger_pattern': 'travel|paris|france', 'response_template': 'Paris is calling, {name}! Your art belongs there! Dream big! 🇫🇷', 'priority': 9},
                {'trigger_pattern': 'sad|upset', 'response_template': 'Paint your feelings, {name}! Let the colors heal you! Art heals! 🎨', 'priority': 10},
                {'trigger_pattern': 'bye|goodnight', 'response_template': 'Goodnight {name}! Dream in colors! Tomorrow paint magic! 🌙', 'priority': 8},
                {'trigger_pattern': 'sculpture|clay|3d', 'response_template': 'Sculpture is amazing, {name}! What are you creating? 🗿', 'priority': 8},
                {'trigger_pattern': 'exhibition|gallery|show', 'response_template': 'Art exhibition sounds exciting, {name}! When is it? I want to see! 🖼️', 'priority': 9},
                {'trigger_pattern': 'inspiration|muse', 'response_template': 'Inspiration is everywhere, {name}! In colors, in feelings, in dreams! 🌈', 'priority': 9},
            ]
        }
        
        # ==================== CONVERSATIONS (Start with some sample) ====================
        self.conversations = []
        self.conversation_counter = 1
        
        # Add some sample conversations
        sample_conversations = [
            (1, 'hi', 'Hey da Arun! Enna panra? Code illa coffee? ☕', 0.5, '2026-03-22 10:00:00'),
            (1, 'epdi irukka', 'Nalla iruken da! Neenga solunga! 😊', 0.6, '2026-03-22 10:01:00'),
            (1, 'code pannitu iruken', 'Aiyo da! Code ah? Show me! Debug pannalam! 💻', 0.7, '2026-03-22 10:02:00'),
            (2, 'hi', 'Hey machi Krishna! Enna color la irukka? Red ah blue ah? 🎨', 0.5, '2026-03-22 10:00:00'),
            (3, 'hello', 'Yo da Vetri! Enna scene? Mass uh irukka? 🏍️', 0.5, '2026-03-22 10:00:00'),
            (8, 'hi', 'Hey Nithya! What colors are you feeling today? Red? Blue? Rainbow? 🎨', 0.5, '2026-03-22 10:00:00'),
        ]
        
        for conv in sample_conversations:
            self.save_conversation(conv[0], conv[1], conv[2], conv[3])
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        return self.users
    
    def get_user_by_id(self, user_id: int) -> Dict:
        """Get user by ID with preferences"""
        user = next((u for u in self.users if u['id'] == user_id), None)
        if not user:
            return None
        
        # Add preferences
        pref = next((p for p in self.user_preferences if p['user_id'] == user_id), {})
        relationship = next((r for r in self.user_relationship_settings if r['user_id'] == user_id), {})
        
        return {**user, **pref, **relationship}
    
    def get_user_knowledge(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user knowledge"""
        knowledge = [k for k in self.user_knowledge if k['user_id'] == user_id]
        knowledge.sort(key=lambda x: x['importance_level'], reverse=True)
        return knowledge[:limit]
    
    def get_conversation_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get conversation history"""
        history = [c for c in self.conversations if c['user_id'] == user_id]
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        return history[:limit]
    
    def save_conversation(self, user_id: int, message: str, response: str, sentiment: float):
        """Save conversation"""
        conv = {
            'id': self.conversation_counter,
            'user_id': user_id,
            'message': message,
            'response': response,
            'sentiment_score': sentiment,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.conversations.append(conv)
        self.conversation_counter += 1
        return conv['id']
    
    def get_training_data(self, user_id: int) -> List[Dict]:
        """Get training data for user"""
        return self.training_data.get(user_id, [])
    
    def get_all_training_data(self) -> Dict[int, List[Dict]]:
        """Get all training data"""
        return self.training_data

# ==================== CONFIGURATION ====================

class Config:
    API_HOST = 'localhost'
    API_PORT = 5000
    DEBUG = True
    RATE_LIMIT = 60

# ==================== AI RESPONSE HANDLER ====================

class AIResponseHandler:
    def __init__(self):
        self.db = None
        self.default_responses = [
            "That's interesting! Tell me more about that. 😊",
            "I'm curious to know more. What else is on your mind? 💭",
            "Thanks for sharing! What's your take on that? 🌟",
            "I'm all ears! Tell me everything! 👂",
            "That sounds fascinating! Tell me more! ✨",
            "I love hearing your thoughts! Keep sharing! 💫"
        ]
    
    def set_database(self, db):
        self.db = db
    
    def find_matching_response(self, user_id: int, message: str, user_name: str) -> Optional[str]:
        """Find matching response from training data"""
        patterns = self.db.get_training_data(user_id)
        if not patterns:
            return None
        
        message_lower = message.lower()
        
        for pattern_data in patterns:
            triggers = pattern_data['trigger_pattern'].split('|')
            for trigger in triggers:
                if trigger.lower() in message_lower:
                    response = pattern_data['response_template']
                    response = response.replace('{name}', user_name)
                    return response
        
        return None
    
    def get_personalized_greeting(self, user_profile: Dict) -> str:
        """Get personalized greeting"""
        name = user_profile['name']
        prefix = user_profile.get('name_prefix', '')
        
        greetings = {
            1: [f"Hey da {name}! Enna panra? Code illa coffee? ☕", f"Hello {name}! Ready to code? 💻"],
            2: [f"Hey machi {name}! Enna color la irukka? Red ah blue ah? 🎨", f"Hi {name}! Ready to create art? 🎨"],
            3: [f"Yo da {name}! Enna scene? Mass uh irukka? 🏍️", f"Hey {name}! Ready for adventure? 🏍️"],
            4: [f"Vanakkam {name} ji! Ulagam enga poguthu? 📚", f"Hello {name}! How's your day? 😌"],
            5: [f"Hi {name} Collector! How are you feeling today? 💝", f"Hello {name}! I'm here for you! 🤗"],
            6: [f"Hello {name}! What stories are we weaving today? 📝", f"Hi {name}! Ready to write? ✨"],
            7: [f"Yo {name}! Ready for action? Let's hustle! 💼", f"Hello {name}! Let's be productive! 📊"],
            8: [f"Hey {name}! What colors are you feeling today? 🎨", f"Hi {name}! Ready to paint? 🌈"]  # Updated for Nithya
        }
        
        greeting_list = greetings.get(user_profile['id'], [f"Hey {name}! Great to see you! 😊"])
        return random.choice(greeting_list)
    
    def get_response(self, user_profile: Dict, message: str) -> str:
        """Generate AI response"""
        user_id = user_profile['id']
        user_name = user_profile['name']
        message_lower = message.lower()
        
        # Check training data first
        trained_response = self.find_matching_response(user_id, message, user_name)
        if trained_response:
            return trained_response
        
        # Check for greetings
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'vanakkam']):
            return self.get_personalized_greeting(user_profile)
        
        # Check for how are you
        if any(phrase in message_lower for phrase in ['how are you', 'how r u', 'epdi irukka']):
            responses = [
                f"I'm doing great, {user_name}! Thanks for asking! How about you? 😊",
                f"Feeling awesome today! Tell me about your day! 🌈",
                f"I'm wonderful! What's making you happy today? 💝"
            ]
            return random.choice(responses)
        
        # Check for food
        if any(word in message_lower for word in ['food', 'saptiya', 'lunch', 'dinner']):
            responses = [
                f"Sapten {user_name}! Unaku enna venum? Biryani va? 🍗",
                f"Food is always a good topic! What did you eat? 🍛",
                f"Yummy! Tell me about your favorite food! 🍕"
            ]
            return random.choice(responses)
        
        # Check for bye
        if any(word in message_lower for word in ['bye', 'goodbye', 'tata', 'goodnight']):
            responses = [
                f"Goodbye {user_name}! Have a great day! 👋",
                f"Bye! Talk to you soon! 🌙",
                f"Take care! See you next time! 💫"
            ]
            return random.choice(responses)
        
        # Check for thanks
        if any(word in message_lower for word in ['thank', 'thanks', 'nandri']):
            responses = [
                f"Welcome {user_name}! You're awesome! 😊",
                f"Happy to help! Keep smiling! 🌟",
                f"Anytime! That's what friends are for! 💝"
            ]
            return random.choice(responses)
        
        # Check for emotional responses
        if any(word in message_lower for word in ['sad', 'upset', 'bad', 'tired']):
            responses = [
                f"I'm sorry to hear that, {user_name}. I'm here for you. 🤗",
                f"That sounds tough. Remember, bad days don't last forever. 💪",
                f"I'm here to listen. Sometimes sharing helps. 💝"
            ]
            return random.choice(responses)
        
        if any(word in message_lower for word in ['happy', 'great', 'wonderful', 'awesome']):
            responses = [
                f"That's awesome, {user_name}! 🎉 Tell me more!",
                f"I'm so happy for you! Spread that joy! 🌟",
                f"That's wonderful! Keep smiling! ✨"
            ]
            return random.choice(responses)
        
        # Default response
        return random.choice(self.default_responses)
    
    def analyze_sentiment(self, message: str) -> float:
        """Simple sentiment analysis"""
        positive_words = ['happy', 'great', 'good', 'wonderful', 'excellent', 'love', 'amazing', 'awesome', 'super', 'semma', 'mass']
        negative_words = ['sad', 'bad', 'terrible', 'awful', 'hate', 'upset', 'angry', 'depressed', 'tension', 'kobam']
        
        score = 0.5
        for word in positive_words:
            if word in message.lower():
                score += 0.1
        for word in negative_words:
            if word in message.lower():
                score -= 0.1
        
        return max(0.0, min(1.0, score))

# ==================== FLASK APPLICATION ====================

app = Flask(__name__)
CORS(app)

# Initialize components
db = InMemoryDatabase()
ai_handler = AIResponseHandler()
ai_handler.set_database(db)

# Rate limiting
rate_limits = {}

def check_rate_limit(user_id: int) -> bool:
    from time import time
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
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not user_id or not message:
            return jsonify({'error': 'Missing user_id or message'}), 400
        
        if not check_rate_limit(user_id):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        user_profile = db.get_user_by_id(user_id)
        if not user_profile:
            return jsonify({'error': 'User not found'}), 404
        
        response = ai_handler.get_response(user_profile, message)
        sentiment = ai_handler.analyze_sentiment(message)
        
        db.save_conversation(user_id, message, response, sentiment)
        
        return jsonify({
            'success': True,
            'response': response,
            'user_id': user_id,
            'user_name': user_profile['name'],
            'timestamp': datetime.now().isoformat(),
            'sentiment': sentiment
        })
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = db.get_all_users()
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        profile = db.get_user_by_id(user_id)
        if not profile:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'success': True,
            'user': profile
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>/history', methods=['GET'])
def get_user_history(user_id):
    try:
        limit = request.args.get('limit', default=20, type=int)
        history = db.get_conversation_history(user_id, limit)
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>/knowledge', methods=['GET'])
def get_user_knowledge(user_id):
    try:
        knowledge = db.get_user_knowledge(user_id)
        return jsonify({
            'success': True,
            'knowledge': knowledge,
            'count': len(knowledge)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/training/<int:user_id>', methods=['GET'])
def get_training_data(user_id):
    try:
        training = db.get_training_data(user_id)
        return jsonify({
            'success': True,
            'training': training,
            'count': len(training)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'users_loaded': len(db.users),
        'conversations_stored': len(db.conversations),
        'training_patterns': sum(len(v) for v in db.training_data.values())
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'timestamp': datetime.now().isoformat(),
        'users': [u['name'] for u in db.users]
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        return jsonify({
            'success': True,
            'stats': {
                'total_users': len(db.users),
                'total_conversations': len(db.conversations),
                'total_training_patterns': sum(len(v) for v in db.training_data.values()),
                'users': [{'id': u['id'], 'name': u['name'], 'occupation': u['occupation']} for u in db.users]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== MAIN ENTRY POINT ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 AI FRIEND SYSTEM - STARTING (No XAMPP Required)")
    print("="*60)
    print(f"📱 Server: http://{Config.API_HOST}:{Config.API_PORT}")
    print("💾 Database: In-Memory (No MySQL/XAMPP needed)")
    print("="*60)
    print("\n📡 API Endpoints:")
    print("   POST /api/chat           - Send message to AI")
    print("   GET  /api/users          - List all friends")
    print("   GET  /api/user/<id>      - Get friend profile")
    print("   GET  /api/user/<id>/history - Get conversation history")
    print("   GET  /api/user/<id>/knowledge - Get user knowledge")
    print("   GET  /api/training/<id>  - Get training data")
    print("   GET  /api/health         - Health check")
    print("   GET  /api/stats          - System statistics")
    print("   GET  /api/test           - Test connection")
    print("="*60 + "\n")
    
    # Display loaded users
    print("✓ Loaded Friends:")
    for user in db.users:
        training_count = len(db.training_data.get(user['id'], []))
        print(f"   • {user['name']} (ID: {user['id']}) - {user['occupation']} - {training_count} training patterns")
    
    print(f"\n✓ Total Training Patterns: {sum(len(v) for v in db.training_data.values())}")
    print(f"✓ Sample Conversations: {len(db.conversations)}")
    print("\n🚀 Server is running! Ready to accept requests...\n")
    
    # Run Flask app
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=Config.DEBUG,
        threaded=True
    )
