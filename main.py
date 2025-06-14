import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import hashlib
import json
from dataclasses import dataclass
from typing import List, Optional, Dict
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# ==================== CONFIG ====================
st.set_page_config(
    page_title="UAE Innovate Hub - KIC",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==================== DATABASE ====================
class Database:
    def __init__(self, db_path="innovate_hub_enhanced.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Enhanced database schema with new social features"""
        cursor = self.conn.cursor()

        # Enhanced users table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           email TEXT UNIQUE NOT NULL,
                           password_hash TEXT NOT NULL,
                           name TEXT NOT NULL,
                           user_type TEXT NOT NULL,
                           organization TEXT,
                           bio TEXT,
                           location TEXT,
                           profile_image TEXT,
                           linkedin_url TEXT,
                           website_url TEXT,
                           kic_balance INTEGER DEFAULT 1000,
                           total_projects_completed INTEGER DEFAULT 0,
                           reputation_score INTEGER DEFAULT 0,
                           is_verified BOOLEAN DEFAULT FALSE,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       )''')

        # Companies table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS companies
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           description TEXT,
                           industry TEXT,
                           size TEXT,
                           location TEXT,
                           website TEXT,
                           logo_url TEXT,
                           founded_year INTEGER,
                           kic_balance INTEGER DEFAULT 5000,
                           total_projects_posted INTEGER DEFAULT 0,
                           rating REAL DEFAULT 0,
                           is_verified BOOLEAN DEFAULT FALSE,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       )''')

        # Enhanced labs table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS labs
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           university TEXT NOT NULL,
                           location TEXT NOT NULL,
                           specialty TEXT NOT NULL,
                           available_from DATE,
                           equipment TEXT,
                           description TEXT,
                           contact TEXT,
                           price_per_day INTEGER,
                           kic_price_per_day INTEGER,
                           rating REAL DEFAULT 0,
                           image_url TEXT,
                           capacity INTEGER,
                           amenities TEXT,
                           total_bookings INTEGER DEFAULT 0,
                           is_featured BOOLEAN DEFAULT FALSE
                       )''')

        # Enhanced talents table with social features
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS talents
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER,
                           title TEXT NOT NULL,
                           location TEXT NOT NULL,
                           experience TEXT,
                           education TEXT,
                           skills TEXT,
                           availability TEXT,
                           bio TEXT,
                           hourly_rate INTEGER,
                           kic_hourly_rate INTEGER,
                           portfolio_url TEXT,
                           linkedin_url TEXT,
                           rating REAL DEFAULT 0,
                           total_projects INTEGER DEFAULT 0,
                           total_earnings INTEGER DEFAULT 0,
                           specializations TEXT,
                           certifications TEXT,
                           languages TEXT,
                           is_featured BOOLEAN DEFAULT FALSE,
                           FOREIGN KEY (user_id) REFERENCES users (id)
                       )''')

        # Enhanced projects table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS projects
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           title TEXT NOT NULL,
                           organization TEXT NOT NULL,
                           company_id INTEGER,
                           location TEXT NOT NULL,
                           deadline DATE,
                           posted DATE DEFAULT CURRENT_DATE,
                           description TEXT,
                           requirements TEXT,
                           tags TEXT,
                           budget_min INTEGER,
                           budget_max INTEGER,
                           kic_budget_min INTEGER,
                           kic_budget_max INTEGER,
                           status TEXT DEFAULT 'Active',
                           contact TEXT,
                           views INTEGER DEFAULT 0,
                           applications INTEGER DEFAULT 0,
                           project_type TEXT DEFAULT 'Research',
                           urgency TEXT DEFAULT 'Medium',
                           remote_possible BOOLEAN DEFAULT FALSE,
                           FOREIGN KEY (company_id) REFERENCES companies (id)
                       )''')

        # Messages table for chat system
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS messages
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           sender_id INTEGER NOT NULL,
                           receiver_id INTEGER NOT NULL,
                           message TEXT NOT NULL,
                           message_type TEXT DEFAULT 'text',
                           is_read BOOLEAN DEFAULT FALSE,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (sender_id) REFERENCES users (id),
                           FOREIGN KEY (receiver_id) REFERENCES users (id)
                       )''')

        # Connections table (like LinkedIn connections)
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS connections
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           requester_id INTEGER NOT NULL,
                           addressee_id INTEGER NOT NULL,
                           status TEXT DEFAULT 'pending',
                           message TEXT,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           accepted_at TIMESTAMP,
                           FOREIGN KEY (requester_id) REFERENCES users (id),
                           FOREIGN KEY (addressee_id) REFERENCES users (id)
                       )''')

        # Activity feed table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS activities
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER NOT NULL,
                           activity_type TEXT NOT NULL,
                           title TEXT NOT NULL,
                           description TEXT,
                           related_id INTEGER,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (user_id) REFERENCES users (id)
                       )''')

        # KIC transactions table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS kic_transactions
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER NOT NULL,
                           transaction_type TEXT NOT NULL,
                           amount INTEGER NOT NULL,
                           description TEXT,
                           related_id INTEGER,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (user_id) REFERENCES users (id)
                       )''')

        # Existing tables with minimal changes...
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS bookings
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER,
                           lab_id INTEGER,
                           start_date DATE,
                           end_date DATE,
                           purpose TEXT,
                           status TEXT DEFAULT 'Pending',
                           total_cost INTEGER,
                           kic_cost INTEGER,
                           payment_method TEXT DEFAULT 'AED',
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (user_id) REFERENCES users (id),
                           FOREIGN KEY (lab_id) REFERENCES labs (id)
                       )''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS reviews
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER,
                           item_type TEXT,
                           item_id INTEGER,
                           rating INTEGER,
                           comment TEXT,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (user_id) REFERENCES users (id)
                       )''')

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS notifications
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER,
                           title TEXT,
                           message TEXT,
                           type TEXT,
                           is_read BOOLEAN DEFAULT FALSE,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY (user_id) REFERENCES users (id)
                       )''')

        self.conn.commit()

    def seed_enhanced_data(self):
        """Enhanced data seeding with new features"""
        cursor = self.conn.cursor()

        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM companies")
        if cursor.fetchone()[0] > 0:
            return

        # Seed companies
        companies_data = [
            ("Dubai Future Foundation", "Leading government organization driving future innovation in UAE", 
             "Government", "Large", "Dubai", "https://dubaifuture.gov.ae", None, 2016, 50000, 15, 4.8, True),
            ("Mubadala Investment Company", "Strategic investment company creating lasting value", 
             "Investment", "Large", "Abu Dhabi", "https://mubadala.com", None, 2002, 75000, 22, 4.9, True),
            ("ADNOC", "Leading energy and petrochemicals company", 
             "Energy", "Large", "Abu Dhabi", "https://adnoc.ae", None, 1971, 60000, 18, 4.7, True),
            ("Noon", "E-commerce platform and technology company", 
             "Technology", "Large", "Dubai", "https://noon.com", None, 2016, 40000, 12, 4.6, True),
            ("Emaar Properties", "Leading real estate development company", 
             "Real Estate", "Large", "Dubai", "https://emaar.com", None, 1997, 45000, 20, 4.5, True),
        ]

        cursor.executemany('''
                           INSERT INTO companies (name, description, industry, size, location, website, 
                                                  logo_url, founded_year, kic_balance, total_projects_posted, 
                                                  rating, is_verified)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ''', companies_data)

        # Enhanced users with social features
        enhanced_users = [
            ("ahmed.mansouri@example.com", hashlib.sha256("password123".encode()).hexdigest(),
             "Ahmed Al Mansouri", "talent", "Tech Innovations LLC", 
             "Robotics Engineer specializing in AI-driven automation systems. 5+ years experience in industrial robotics.",
             "Abu Dhabi", None, "https://linkedin.com/in/ahmed-mansouri", "https://robotics-portfolio.ae", 
             1500, 15, 450, True),
            ("fatima.zaabi@example.com", hashlib.sha256("password123".encode()).hexdigest(),
             "Dr. Fatima Al Zaabi", "talent", "Analytics Solutions",
             "Data Scientist and Machine Learning expert with focus on healthcare applications.",
             "Dubai", None, "https://linkedin.com/in/fatima-zaabi", "https://ml-portfolio.ae",
             2200, 25, 780, True),
            ("sara.hassan@example.com", hashlib.sha256("password123".encode()).hexdigest(),
             "Sara Hassan", "company", "Dubai Future Foundation",
             "Innovation Manager at Dubai Future Foundation, leading emerging technology initiatives.",
             "Dubai", None, "https://linkedin.com/in/sara-hassan", None,
             5000, 8, 320, True),
        ]

        for user_data in enhanced_users:
            cursor.execute('''
                           INSERT INTO users (email, password_hash, name, user_type, organization,
                                              bio, location, profile_image, linkedin_url, website_url,
                                              kic_balance, total_projects_completed, reputation_score, is_verified)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ''', user_data)

        # Enhanced projects with KIC integration
        enhanced_projects = [
            ("AI-Powered Smart City Infrastructure", "Dubai Future Foundation", 1, "Dubai",
             "2024-08-15", "2024-02-01",
             "Develop AI systems for smart traffic management, energy optimization, and citizen services integration.",
             "AI/ML expertise, smart city experience, IoT knowledge, Arabic language preferred",
             "AI,Smart City,IoT,Machine Learning,Arabic", 80000, 120000, 4000, 6000, "Active",
             "projects@dubaifuture.gov.ae", 234, 18, "Innovation", "High", True),
            
            ("Blockchain Supply Chain Transparency", "Mubadala Investment Company", 2, "Abu Dhabi",
             "2024-07-30", "2024-02-05",
             "Create blockchain solution for supply chain transparency in healthcare and pharmaceuticals.",
             "Blockchain development, smart contracts, healthcare domain knowledge",
             "Blockchain,Healthcare,Supply Chain,Smart Contracts", 60000, 90000, 3000, 4500, "Active",
             "blockchain@mubadala.ae", 156, 12, "Research", "Medium", False),
        ]

        cursor.executemany('''
                           INSERT INTO projects (title, organization, company_id, location, deadline, posted,
                                                 description, requirements, tags, budget_min, budget_max,
                                                 kic_budget_min, kic_budget_max, status, contact, views, 
                                                 applications, project_type, urgency, remote_possible)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ''', enhanced_projects)

        # Sample activities for feed
        activities_data = [
            (1, "project_completed", "Completed Robotics Automation Project", 
             "Successfully delivered industrial automation solution for manufacturing company", 1),
            (2, "skill_certified", "Earned AI/ML Certification", 
             "Completed advanced certification in Machine Learning from Stanford Online", None),
            (1, "connection_made", "Connected with Dr. Fatima Al Zaabi", 
             "New professional connection in Data Science field", 2),
            (2, "project_started", "Started Healthcare Analytics Project", 
             "Beginning new project on predictive analytics for patient outcomes", 2),
        ]

        cursor.executemany('''
                           INSERT INTO activities (user_id, activity_type, title, description, related_id)
                           VALUES (?, ?, ?, ?, ?)
                           ''', activities_data)

        # Sample KIC transactions
        kic_transactions = [
            (1, "project_payment", 2500, "Payment for completed robotics project", 1),
            (2, "lab_booking", -800, "Paid for AI lab booking using KIC", 1),
            (1, "bonus", 500, "Performance bonus for high-rated project delivery", None),
            (2, "talent_fee", 1200, "Received payment for consulting work", 2),
        ]

        cursor.executemany('''
                           INSERT INTO kic_transactions (user_id, transaction_type, amount, description, related_id)
                           VALUES (?, ?, ?, ?, ?)
                           ''', kic_transactions)

        self.conn.commit()


# ==================== ENHANCED STYLES ====================
def load_enhanced_css():
    st.markdown("""
    <style>
        /* Modern LinkedIn-inspired light theme */
        .main {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            color: #1e293b;
        }

        /* Enhanced gradient text */
        .gradient-text {
            background: linear-gradient(-45deg, #0077b5, #00a0dc, #0073e6, #005582);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Modern card design */
        .modern-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            border: 1px solid rgba(0, 119, 181, 0.1);
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 119, 181, 0.1);
        }

        .modern-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 119, 181, 0.15);
            border: 1px solid rgba(0, 119, 181, 0.2);
        }

        /* Professional navigation */
        .nav-container {
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(0, 119, 181, 0.1);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0, 119, 181, 0.05);
        }

        /* Profile card styling */
        .profile-card {
            background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%);
            color: white;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1rem;
        }

        .profile-avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            margin: 0 auto 1rem auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            font-weight: bold;
        }

        /* KIC Balance styling */
        .kic-balance {
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }

        /* Message bubble styling */
        .message-bubble {
            background: #f1f5f9;
            border-radius: 15px;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            max-width: 70%;
        }

        .message-bubble.sent {
            background: #0077b5;
            color: white;
            margin-left: auto;
        }

        .message-bubble.received {
            background: #f1f5f9;
            color: #1e293b;
        }

        /* Activity feed styling */
        .activity-item {
            background: white;
            border-left: 4px solid #0077b5;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 4px rgba(0, 119, 181, 0.1);
        }

        /* Status badges - LinkedIn style */
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }

        .status-online {
            background: rgba(34, 197, 94, 0.1);
            color: #16a34a;
            border: 1px solid #16a34a;
        }

        .status-verified {
            background: rgba(59, 130, 246, 0.1);
            color: #2563eb;
            border: 1px solid #2563eb;
        }

        .status-featured {
            background: rgba(251, 191, 36, 0.1);
            color: #d97706;
            border: 1px solid #d97706;
        }

        /* Professional skill tags */
        .skill-tag {
            background: rgba(0, 119, 181, 0.1);
            color: #0077b5;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            margin: 0.2rem;
            display: inline-block;
            border: 1px solid rgba(0, 119, 181, 0.2);
            font-weight: 500;
        }

        /* Connection button */
        .connect-btn {
            background: #0077b5;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 20px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .connect-btn:hover {
            background: #005582;
            transform: translateY(-1px);
        }

        /* Company card styling */
        .company-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(0, 119, 181, 0.1);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }

        .company-card:hover {
            box-shadow: 0 8px 25px rgba(0, 119, 181, 0.15);
            transform: translateY(-2px);
        }

        /* Enhanced metrics */
        .metric-card {
            background: linear-gradient(135deg, rgba(0, 119, 181, 0.05) 0%, rgba(0, 160, 220, 0.05) 100%);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(0, 119, 181, 0.1);
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 119, 181, 0.1);
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Chat interface */
        .chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid rgba(0, 119, 181, 0.1);
            border-radius: 8px;
            padding: 1rem;
            background: #f8fafc;
        }

        /* Project urgency indicators */
        .urgency-high {
            color: #dc2626;
            font-weight: bold;
        }

        .urgency-medium {
            color: #d97706;
            font-weight: bold;
        }

        .urgency-low {
            color: #16a34a;
            font-weight: bold;
        }

        /* Professional buttons */
        .professional-btn {
            background: linear-gradient(135deg, #0077b5 0%, #005582 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
        }

        .professional-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 119, 181, 0.3);
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f5f9;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #005582 0%, #0077b5 100%);
        }
    </style>
    """, unsafe_allow_html=True)


# ==================== ENHANCED COMPONENTS ====================
class EnhancedAuthManager:
    """Enhanced authentication with social features"""

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def login(email: str, password: str, db: Database) -> Optional[Dict]:
        cursor = db.conn.cursor()
        cursor.execute("""
                       SELECT id, email, name, user_type, organization, bio, location,
                              kic_balance, total_projects_completed, reputation_score, is_verified
                       FROM users
                       WHERE email = ? AND password_hash = ?
                       """, (email, EnhancedAuthManager.hash_password(password)))

        user = cursor.fetchone()
        if user:
            return dict(user)
        return None

    @staticmethod
    def register(email: str, password: str, name: str, user_type: str,
                 organization: str, location: str, db: Database) -> bool:
        try:
            cursor = db.conn.cursor()
            cursor.execute("""
                           INSERT INTO users (email, password_hash, name, user_type, 
                                              organization, location, kic_balance)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           """, (email, EnhancedAuthManager.hash_password(password), 
                                 name, user_type, organization, location, 1000))
            db.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


class SocialManager:
    """Manage social features like connections, messages, activity feed"""

    @staticmethod
    def send_connection_request(requester_id: int, addressee_id: int, message: str, db: Database):
        cursor = db.conn.cursor()
        cursor.execute("""
                       INSERT INTO connections (requester_id, addressee_id, message)
                       VALUES (?, ?, ?)
                       """, (requester_id, addressee_id, message))
        db.conn.commit()

    @staticmethod
    def accept_connection(connection_id: int, db: Database):
        cursor = db.conn.cursor()
        cursor.execute("""
                       UPDATE connections 
                       SET status = 'accepted', accepted_at = CURRENT_TIMESTAMP
                       WHERE id = ?
                       """, (connection_id,))
        db.conn.commit()

    @staticmethod
    def send_message(sender_id: int, receiver_id: int, message: str, db: Database):
        cursor = db.conn.cursor()
        cursor.execute("""
                       INSERT INTO messages (sender_id, receiver_id, message)
                       VALUES (?, ?, ?)
                       """, (sender_id, receiver_id, message))
        db.conn.commit()

    @staticmethod
    def get_conversations(user_id: int, db: Database):
        cursor = db.conn.cursor()
        cursor.execute("""
                       SELECT DISTINCT 
                           CASE 
                               WHEN sender_id = ? THEN receiver_id 
                               ELSE sender_id 
                           END AS other_user_id,
                           u.name, u.user_type, 
                           MAX(m.created_at) as last_message_time
                       FROM messages m
                       JOIN users u ON u.id = CASE 
                           WHEN m.sender_id = ? THEN m.receiver_id 
                           ELSE m.sender_id 
                       END
                       WHERE ? IN (sender_id, receiver_id)
                       GROUP BY other_user_id, u.name, u.user_type
                       ORDER BY last_message_time DESC
                       """, (user_id, user_id, user_id))
        return cursor.fetchall()

    @staticmethod
    def get_messages(user1_id: int, user2_id: int, db: Database):
        cursor = db.conn.cursor()
        cursor.execute("""
                       SELECT m.*, u.name as sender_name
                       FROM messages m
                       JOIN users u ON m.sender_id = u.id
                       WHERE (sender_id = ? AND receiver_id = ?) 
                          OR (sender_id = ? AND receiver_id = ?)
                       ORDER BY created_at ASC
                       """, (user1_id, user2_id, user2_id, user1_id))
        return cursor.fetchall()


class KICManager:
    """Manage KIC (Knowledge and Innovation Connected) currency"""

    @staticmethod
    def transfer_kic(from_user_id: int, to_user_id: int, amount: int, 
                     description: str, db: Database) -> bool:
        cursor = db.conn.cursor()
        
        # Check balance
        cursor.execute("SELECT kic_balance FROM users WHERE id = ?", (from_user_id,))
        balance = cursor.fetchone()[0]
        
        if balance >= amount:
            # Deduct from sender
            cursor.execute("""
                           UPDATE users SET kic_balance = kic_balance - ? WHERE id = ?
                           """, (amount, from_user_id))
            
            # Add to receiver
            cursor.execute("""
                           UPDATE users SET kic_balance = kic_balance + ? WHERE id = ?
                           """, (amount, to_user_id))
            
            # Record transactions
            cursor.execute("""
                           INSERT INTO kic_transactions (user_id, transaction_type, amount, description)
                           VALUES (?, 'sent', ?, ?)
                           """, (from_user_id, -amount, description))
            
            cursor.execute("""
                           INSERT INTO kic_transactions (user_id, transaction_type, amount, description)
                           VALUES (?, 'received', ?, ?)
                           """, (to_user_id, amount, description))
            
            db.conn.commit()
            return True
        return False

    @staticmethod
    def get_kic_balance(user_id: int, db: Database) -> int:
        cursor = db.conn.cursor()
        cursor.execute("SELECT kic_balance FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()[0]

    @staticmethod
    def get_kic_transactions(user_id: int, db: Database, limit: int = 10):
        cursor = db.conn.cursor()
        cursor.execute("""
                       SELECT * FROM kic_transactions 
                       WHERE user_id = ? 
                       ORDER BY created_at DESC 
                       LIMIT ?
                       """, (user_id, limit))
        return cursor.fetchall()


# ==================== ENHANCED PAGES ====================
def show_enhanced_login_page(db: Database):
    """Enhanced login page with professional styling"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('''
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 class="gradient-text" style="font-size: 3rem; margin-bottom: 0.5rem;">
                🔬 UAE Innovate Hub
            </h1>
            <p style="font-size: 1.2rem; color: #64748b; margin-bottom: 0.5rem;">
                Knowledge & Innovation Connected
            </p>
            <p style="color: #94a3b8;">
                Connect with top talent • Collaborate on breakthrough projects • Access cutting-edge labs
            </p>
        </div>
        ''', unsafe_allow_html=True)

        # Professional login/register tabs
        tab1, tab2 = st.tabs(["🔑 Sign In", "🚀 Join the Network"])

        with tab1:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            with st.form("login_form"):
                email = st.text_input("Work Email", placeholder="your.name@company.com")
                password = st.text_input("Password", type="password")
                
                col1, col2 = st.columns(2)
                with col1:
                    remember_me = st.checkbox("Keep me signed in")
                with col2:
                    st.markdown('<a href="#" style="float: right; color: #0077b5;">Forgot password?</a>', 
                               unsafe_allow_html=True)

                if st.form_submit_button("Sign In", use_container_width=True):
                    user = EnhancedAuthManager.login(email, password, db)
                    if user:
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['name']}! 🎉")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Full Name *")
                    email = st.text_input("Work Email *")
                    location = st.selectbox("Location", 
                                           ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"])
                with col2:
                    password = st.text_input("Password *", type="password")
                    confirm_password = st.text_input("Confirm Password *", type="password")
                    user_type = st.selectbox("I'm joining as", ["Talent", "Company Representative", "Researcher"])

                organization = st.text_input("Organization/University *")
                
                st.markdown("#### Why are you joining? (Optional)")
                join_reason = st.multiselect("Select all that apply:",
                                           ["Find talented professionals", "Discover research opportunities", 
                                            "Access testing facilities", "Collaborate on projects", 
                                            "Share knowledge", "Build professional network"])

                terms = st.checkbox("I agree to the Terms of Service and Privacy Policy *")

                if st.form_submit_button("Create Professional Account", use_container_width=True):
                    if password != confirm_password:
                        st.error("Passwords don't match")
                    elif not terms:
                        st.error("Please accept the terms")
                    elif not all([name, email, password, organization]):
                        st.error("Please fill in all required fields")
                    else:
                        success = EnhancedAuthManager.register(email, password, name,
                                                             user_type.lower(), organization, location, db)
                        if success:
                            st.success("🎉 Welcome to UAE Innovate Hub! Please sign in with your new account.")
                            st.balloons()
                        else:
                            st.error("Email already exists. Please try signing in instead.")
            st.markdown('</div>', unsafe_allow_html=True)


def show_enhanced_dashboard(db: Database):
    """Enhanced dashboard with social media features"""
    
    user = st.session_state.user
    
    st.markdown(f'''
    <div style="margin-bottom: 2rem;">
        <h1 class="gradient-text">Welcome back, {user['name']}! 👋</h1>
        <p style="font-size: 1.1rem; color: #64748b;">
            Your innovation network awaits • {user['total_projects_completed']} projects completed • 
            <span class="kic-balance">💰 {user['kic_balance']} KIC</span>
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # Professional metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    cursor = db.conn.cursor()
    
    with col1:
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'talent'")
        talent_count = cursor.fetchone()[0]
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{talent_count}+</div>
            <div style="color: #64748b; font-weight: 600;">Talents</div>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        cursor.execute("SELECT COUNT(*) FROM companies")
        company_count = cursor.fetchone()[0]
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{company_count}+</div>
            <div style="color: #64748b; font-weight: 600;">Companies</div>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'Active'")
        active_projects = cursor.fetchone()[0]
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{active_projects}</div>
            <div style="color: #64748b; font-weight: 600;">Active Projects</div>
        </div>
        ''', unsafe_allow_html=True)

    with col4:
        cursor.execute("SELECT COUNT(*) FROM labs")
        lab_count = cursor.fetchone()[0]
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{lab_count}+</div>
            <div style="color: #64748b; font-weight: 600;">Testing Labs</div>
        </div>
        ''', unsafe_allow_html=True)

    with col5:
        # Personal network size
        cursor.execute("""
                       SELECT COUNT(*) FROM connections 
                       WHERE (requester_id = ? OR addressee_id = ?) AND status = 'accepted'
                       """, (user['id'], user['id']))
        network_size = cursor.fetchone()[0]
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{network_size}</div>
            <div style="color: #64748b; font-weight: 600;">My Network</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")

    # Main dashboard content
    col1, col2 = st.columns([2, 1])

    with col1:
        # Activity Feed
        st.markdown("### 📈 Network Activity")
        
        cursor.execute("""
                       SELECT a.*, u.name, u.user_type 
                       FROM activities a
                       JOIN users u ON a.user_id = u.id
                       ORDER BY a.created_at DESC
                       LIMIT 10
                       """)
        activities = cursor.fetchall()

        for activity in activities:
            icon_map = {
                "project_completed": "✅",
                "skill_certified": "🎓",
                "connection_made": "🤝",
                "project_started": "🚀",
                "lab_booked": "🔬",
                "review_received": "⭐"
            }
            
            icon = icon_map.get(activity['activity_type'], "📋")
            
            st.markdown(f'''
            <div class="activity-item">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 1.5rem;">{icon}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #1e293b;">{activity['name']}</div>
                        <div style="color: #0077b5; font-weight: 500;">{activity['title']}</div>
                        <div style="color: #64748b; font-size: 0.9rem;">{activity['description']}</div>
                    </div>
                    <div style="color: #94a3b8; font-size: 0.8rem;">
                        {activity['created_at'][:10]}
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        # Trending Projects
        st.markdown("### 🔥 Trending Projects")
        cursor.execute("""
                       SELECT * FROM projects 
                       WHERE status = 'Active'
                       ORDER BY views DESC, applications DESC
                       LIMIT 3
                       """)
        trending_projects = cursor.fetchall()

        for project in trending_projects:
            urgency_class = f"urgency-{project['urgency'].lower()}"
            
            st.markdown(f'''
            <div class="modern-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="margin-bottom: 0.5rem;">{project['title']}</h4>
                        <div style="color: #0077b5; font-weight: 600; margin-bottom: 0.5rem;">
                            {project['organization']}
                        </div>
                        <div style="color: #64748b; margin-bottom: 1rem;">
                            📍 {project['location']} • 
                            <span class="{urgency_class}">⚡ {project['urgency']} Priority</span> •
                            👁️ {project['views']} views
                        </div>
                        <div style="color: #475569;">
                            {project['description'][:120]}...
                        </div>
                    </div>
                    <div style="text-align: right; margin-left: 1rem;">
                        <div style="color: #16a34a; font-weight: bold; font-size: 1.1rem;">
                            💰 {project['kic_budget_min']:,} - {project['kic_budget_max']:,} KIC
                        </div>
                        <div style="color: #64748b; font-size: 0.9rem;">
                            AED {project['budget_min']:,} - {project['budget_max']:,}
                        </div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    with col2:
        # Personal Profile Card
        st.markdown(f'''
        <div class="profile-card">
            <div class="profile-avatar">{user['name'][0].upper()}</div>
            <h3 style="margin-bottom: 0.5rem;">{user['name']}</h3>
            <div style="opacity: 0.9; margin-bottom: 1rem;">{user['organization']}</div>
            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; margin-bottom: 1rem;">
                <div style="font-size: 0.9rem; opacity: 0.8;">Reputation Score</div>
                <div style="font-size: 1.5rem; font-weight: bold;">{user['reputation_score']}</div>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px;">
                <div style="font-size: 0.9rem; opacity: 0.8;">Projects Completed</div>
                <div style="font-size: 1.5rem; font-weight: bold;">{user['total_projects_completed']}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # KIC Balance and Recent Transactions
        st.markdown("### 💰 KIC Wallet")
        
        kic_transactions = KICManager.get_kic_transactions(user['id'], db, 5)
        
        st.markdown(f'''
        <div class="modern-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 2rem; font-weight: bold; color: #f59e0b;">
                    {user['kic_balance']} KIC
                </div>
                <div style="color: #64748b;">Available Balance</div>
            </div>
        ''', unsafe_allow_html=True)

        if kic_transactions:
            st.markdown("**Recent Transactions:**")
            for txn in kic_transactions:
                color = "#16a34a" if txn['amount'] > 0 else "#dc2626"
                sign = "+" if txn['amount'] > 0 else ""
                
                st.markdown(f'''
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0;">
                    <div>
                        <div style="font-size: 0.9rem; font-weight: 500;">{txn['transaction_type'].title()}</div>
                        <div style="font-size: 0.8rem; color: #64748b;">{txn['description']}</div>
                    </div>
                    <div style="color: {color}; font-weight: bold;">
                        {sign}{txn['amount']} KIC
                    </div>
                </div>
                ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("💬 Messages", use_container_width=True):
            st.session_state.current_page = "Messages"
            st.rerun()
            
        if st.button("🔍 Find Talent", use_container_width=True):
            st.session_state.current_page = "Talents"
            st.rerun()
            
        if st.button("📋 Browse Projects", use_container_width=True):
            st.session_state.current_page = "Projects"
            st.rerun()
            
        if st.button("🏢 Explore Labs", use_container_width=True):
            st.session_state.current_page = "Labs"
            st.rerun()


def show_enhanced_talents_page(db: Database):
    """Enhanced talents page with social features"""
    
    st.markdown('<h1 class="gradient-text">Talent Network</h1>', unsafe_allow_html=True)
    st.markdown("Connect with UAE's top innovators, researchers, and industry experts")

    # Search and filters
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search talents...", 
                                   placeholder="Search by name, skills, title, or expertise")

    with col2:
        sort_option = st.selectbox("Sort by", 
                                 ["Best Match", "Reputation Score", "Project Count", 
                                  "Rating", "Recently Active"])

    with col3:
        view_mode = st.radio("View", ["Professional", "Compact"], horizontal=True)

    # Advanced filters
    with st.expander("🔧 Advanced Filters", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cursor = db.conn.cursor()
            cursor.execute("SELECT DISTINCT location FROM talents")
            locations = [row[0] for row in cursor.fetchall()]
            selected_locations = st.multiselect("Locations", locations)
            
        with col2:
            availability_options = ["Full-time", "Part-time", "Contract", "Remote"]
            selected_availability = st.multiselect("Availability", availability_options)
            
        with col3:
            rate_range = st.slider("Hourly rate (AED)", 0, 500, (0, 500))
            
        with col4:
            min_projects = st.slider("Min. projects completed", 0, 50, 0)

    # Fetch and filter talents
    query = """
            SELECT t.*, u.name, u.email, u.location as user_location, u.is_verified,
                   u.reputation_score, u.total_projects_completed
            FROM talents t
            JOIN users u ON t.user_id = u.id
            WHERE 1=1
            """
    params = []

    if search_query:
        query += " AND (u.name LIKE ? OR t.title LIKE ? OR t.skills LIKE ? OR t.bio LIKE ?)"
        search_param = f"%{search_query}%"
        params.extend([search_param] * 4)

    if selected_locations:
        query += f" AND t.location IN ({','.join(['?'] * len(selected_locations))})"
        params.extend(selected_locations)

    if selected_availability:
        query += f" AND t.availability IN ({','.join(['?'] * len(selected_availability))})"
        params.extend(selected_availability)

    query += " AND t.hourly_rate BETWEEN ? AND ?"
    params.extend([rate_range[0], rate_range[1]])

    query += " AND u.total_projects_completed >= ?"
    params.append(min_projects)

    # Sorting
    if sort_option == "Reputation Score":
        query += " ORDER BY u.reputation_score DESC"
    elif sort_option == "Project Count":
        query += " ORDER BY u.total_projects_completed DESC"
    elif sort_option == "Rating":
        query += " ORDER BY t.rating DESC"
    else:
        query += " ORDER BY u.is_verified DESC, u.reputation_score DESC"

    cursor.execute(query, params)
    talents = cursor.fetchall()

    st.markdown(f"### Found {len(talents)} talented professionals")

    # Display talents
    if view_mode == "Professional":
        for talent in talents:
            st.markdown(f'''
            <div class="modern-card">
                <div style="display: flex; gap: 1.5rem;">
                    <div style="flex-shrink: 0;">
                        <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #0077b5, #00a0dc); 
                                    border-radius: 50%; display: flex; align-items: center; justify-content: center;
                                    color: white; font-size: 1.8rem; font-weight: bold;">
                            {talent['name'][0].upper()}
                        </div>
                    </div>
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                            <h3 style="margin: 0;">{talent['name']}</h3>
                            {f'<span class="status-badge status-verified">✓ Verified</span>' if talent['is_verified'] else ''}
                            <span class="status-badge status-online">🟢 Active</span>
                        </div>
                        <div style="color: #0077b5; font-weight: 600; margin-bottom: 0.5rem;">
                            {talent['title']}
                        </div>
                        <div style="color: #64748b; margin-bottom: 1rem;">
                            📍 {talent['location']} • 💼 {talent['experience']} • 
                            🎓 {talent['education']} • 
                            📊 {talent['reputation_score']} reputation • 
                            ✅ {talent['total_projects_completed']} projects completed
                        </div>
                        <div style="color: #475569; margin-bottom: 1rem;">
                            {talent['bio'][:200]}{'...' if len(talent['bio']) > 200 else ''}
                        </div>
                        <div style="margin-bottom: 1rem;">
                            {' '.join([f'<span class="skill-tag">{skill.strip()}</span>' 
                                     for skill in talent['skills'].split(',')[:6]])}
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="color: #16a34a; font-weight: bold; font-size: 1.1rem;">
                                    💰 {talent['kic_hourly_rate']} KIC/hr
                                </span>
                                <span style="color: #64748b; margin-left: 1rem;">
                                    AED {talent['hourly_rate']}/hr
                                </span>
                            </div>
                            <div style="display: flex; gap: 0.5rem;">
                                <span class="status-badge status-featured">{talent['availability']}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("👤 View Profile", key=f"view_{talent['id']}"):
                    st.session_state.selected_talent_id = talent['id']
                    st.rerun()
            with col2:
                if st.button("🤝 Connect", key=f"connect_{talent['id']}"):
                    st.session_state.connect_talent_id = talent['id']
                    st.rerun()
            with col3:
                if st.button("💬 Message", key=f"message_{talent['id']}"):
                    st.session_state.message_talent_id = talent['id']
                    st.rerun()
            with col4:
                if st.button("💼 Hire", key=f"hire_{talent['id']}"):
                    st.session_state.hire_talent_id = talent['id']
                    st.rerun()

    else:  # Compact view
        for talent in talents:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
            
            with col1:
                verified_badge = "✓" if talent['is_verified'] else ""
                st.markdown(f"**{talent['name']} {verified_badge}**  \n{talent['title']}")
            with col2:
                st.markdown(f"{talent['location']} • {talent['availability']}")
            with col3:
                st.markdown(f"**{talent['total_projects_completed']}** projects")
            with col4:
                st.markdown(f"**{talent['kic_hourly_rate']} KIC**/hr")
            with col5:
                if st.button("→", key=f"compact_{talent['id']}"):
                    st.session_state.selected_talent_id = talent['id']
                    st.rerun()


def show_enhanced_companies_page(db: Database):
    """New companies page"""
    
    st.markdown('<h1 class="gradient-text">Partner Companies</h1>', unsafe_allow_html=True)
    st.markdown("Discover innovative companies driving UAE's future")

    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM companies ORDER BY rating DESC, total_projects_posted DESC")
    companies = cursor.fetchall()

    # Company metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{len(companies)}</div>
            <div style="color: #64748b; font-weight: 600;">Partner Companies</div>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        total_projects = sum(company['total_projects_posted'] for company in companies)
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{total_projects}</div>
            <div style="color: #64748b; font-weight: 600;">Projects Posted</div>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        verified_companies = sum(1 for company in companies if company['is_verified'])
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{verified_companies}</div>
            <div style="color: #64748b; font-weight: 600;">Verified</div>
        </div>
        ''', unsafe_allow_html=True)

    with col4:
        avg_rating = sum(company['rating'] for company in companies) / len(companies) if companies else 0
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{avg_rating:.1f}⭐</div>
            <div style="color: #64748b; font-weight: 600;">Avg. Rating</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")

    # Industry filter
    industries = list(set(company['industry'] for company in companies))
    selected_industry = st.selectbox("Filter by Industry", ["All Industries"] + industries)

    # Display companies
    filtered_companies = companies
    if selected_industry != "All Industries":
        filtered_companies = [c for c in companies if c['industry'] == selected_industry]

    for company in filtered_companies:
        st.markdown(f'''
        <div class="company-card">
            <div style="display: flex; gap: 1.5rem;">
                <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #0077b5, #00a0dc); 
                            border-radius: 12px; display: flex; align-items: center; justify-content: center;
                            color: white; font-size: 1.5rem; font-weight: bold;">
                    {company['name'][:2].upper()}
                </div>
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                        <h3 style="margin: 0;">{company['name']}</h3>
                        {f'<span class="status-badge status-verified">✓ Verified</span>' if company['is_verified'] else ''}
                        <span class="status-badge status-featured">{company['industry']}</span>
                    </div>
                    <div style="color: #64748b; margin-bottom: 1rem;">
                        📍 {company['location']} • 
                        👥 {company['size']} • 
                        📅 Founded {company['founded_year']} • 
                        ⭐ {company['rating']:.1f} rating • 
                        📋 {company['total_projects_posted']} projects posted
                    </div>
                    <div style="color: #475569; margin-bottom: 1rem;">
                        {company['description']}
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #16a34a; font-weight: bold;">
                                💰 {company['kic_balance']:,} KIC Available
                            </span>
                        </div>
                        <div>
                            <a href="{company['website']}" target="_blank" style="color: #0077b5;">
                                🌐 Visit Website
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 View Projects", key=f"projects_{company['id']}"):
                st.session_state.company_projects_id = company['id']
                st.rerun()
        with col2:
            if st.button("💬 Contact", key=f"contact_{company['id']}"):
                st.session_state.contact_company_id = company['id']
                st.rerun()
        with col3:
            if st.button("🤝 Follow", key=f"follow_{company['id']}"):
                st.success("Now following!")


def show_enhanced_messages_page(db: Database):
    """New messaging system"""
    
    user = st.session_state.user
    
    st.markdown('<h1 class="gradient-text">💬 Messages</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Conversations")
        
        conversations = SocialManager.get_conversations(user['id'], db)
        
        if conversations:
            for conv in conversations:
                with st.container():
                    if st.button(f"👤 {conv['name']}", 
                               key=f"conv_{conv['other_user_id']}",
                               use_container_width=True):
                        st.session_state.active_conversation = conv['other_user_id']
                        st.rerun()
                    
                    st.markdown(f"<small>{conv['user_type']} • {conv['last_message_time'][:16]}</small>", 
                               unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info("No conversations yet. Connect with talents to start messaging!")

        # Start new conversation
        st.markdown("### Start New Conversation")
        cursor = db.conn.cursor()
        cursor.execute("""
                       SELECT u.id, u.name, u.user_type 
                       FROM users u 
                       WHERE u.id != ? 
                       ORDER BY u.name
                       """, (user['id'],))
        all_users = cursor.fetchall()
        
        selected_user = st.selectbox("Select user", 
                                   [(u['id'], f"{u['name']} ({u['user_type']})") for u in all_users],
                                   format_func=lambda x: x[1])
        
        if st.button("Start Conversation"):
            st.session_state.active_conversation = selected_user[0]
            st.rerun()

    with col2:
        if 'active_conversation' in st.session_state:
            other_user_id = st.session_state.active_conversation
            
            # Get other user info
            cursor = db.conn.cursor()
            cursor.execute("SELECT name, user_type FROM users WHERE id = ?", (other_user_id,))
            other_user = cursor.fetchone()
            
            st.markdown(f"### 💬 Chat with {other_user['name']}")
            
            # Message history
            messages = SocialManager.get_messages(user['id'], other_user_id, db)
            
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            for message in messages:
                bubble_class = "sent" if message['sender_id'] == user['id'] else "received"
                
                st.markdown(f'''
                <div class="message-bubble {bubble_class}">
                    <div style="font-size: 0.9rem;">{message['message']}</div>
                    <div style="font-size: 0.7rem; opacity: 0.7; margin-top: 0.25rem;">
                        {message['created_at'][11:16]}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Send new message
            with st.form("send_message", clear_on_submit=True):
                message_text = st.text_input("Type your message...", key="message_input")
                if st.form_submit_button("Send 📤"):
                    if message_text.strip():
                        SocialManager.send_message(user['id'], other_user_id, message_text, db)
                        st.rerun()
        else:
            st.markdown('''
            <div style="text-align: center; padding: 4rem; color: #64748b;">
                <h3>👋 Select a conversation to start messaging</h3>
                <p>Connect with talented professionals and start collaborating!</p>
            </div>
            ''', unsafe_allow_html=True)


# ==================== MAIN APPLICATION ====================
def main():
    # Load enhanced styles
    load_enhanced_css()

    # Initialize enhanced database
    db = Database()
    db.seed_enhanced_data()

    # Check authentication
    if 'user' not in st.session_state:
        show_enhanced_login_page(db)
        return

    # Enhanced navigation
    st.markdown('''
    <div class="nav-container">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 1rem;">
            <div style="display: flex; align-items: center; gap: 2rem;">
                <h2 class="gradient-text" style="margin: 0;">🔬 UAE Innovate Hub</h2>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span class="kic-balance">💰 {}</span>
                <span style="color: #64748b;">Welcome, {} 👋</span>
            </div>
        </div>
    </div>
    '''.format(st.session_state.user['kic_balance'], st.session_state.user['name']), 
               unsafe_allow_html=True)

    # Enhanced navigation menu
    pages = {
        "Home": "🏠",
        "Talents": "👥", 
        "Companies": "🏢",
        "Projects": "📋",
        "Labs": "🔬",
        "KIC Hub": "💰",
        "Messages": "💬",
        "Profile": "👤"
    }

    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"

    cols = st.columns(len(pages))

    for idx, (page, icon) in enumerate(pages.items()):
        with cols[idx]:
            if st.button(f"{icon} {page}", key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()

    # Display selected page
    if st.session_state.current_page == "Home":
        show_enhanced_dashboard(db)
    elif st.session_state.current_page == "Talents":
        show_enhanced_talents_page(db)
    elif st.session_state.current_page == "Companies":
        show_enhanced_companies_page(db)
    elif st.session_state.current_page == "Messages":
        show_enhanced_messages_page(db)
    elif st.session_state.current_page == "KIC Hub":
        show_kic_hub_page(db)
    elif st.session_state.current_page == "Projects":
        show_enhanced_projects_page(db)
    elif st.session_state.current_page == "Labs":
        show_enhanced_labs_page(db)
    elif st.session_state.current_page == "Profile":
        show_enhanced_profile_page(db)


def show_kic_hub_page(db: Database):
    """KIC (Knowledge and Innovation Connected) Hub page"""
    
    user = st.session_state.user
    
    st.markdown('<h1 class="gradient-text">💰 KIC Hub</h1>', unsafe_allow_html=True)
    st.markdown("**Knowledge and Innovation Connected** - The future of innovation economy")

    # KIC Balance Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div class="profile-card">
            <h2 style="margin-bottom: 1rem;">Your KIC Wallet</h2>
            <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">
                {user['kic_balance']}
            </div>
            <div style="font-size: 1.2rem; opacity: 0.8;">KIC Available</div>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        cursor = db.conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM kic_transactions WHERE user_id = ? AND amount > 0", (user['id'],))
        total_earned = cursor.fetchone()[0] or 0
        
        st.markdown(f'''
        <div class="modern-card" style="text-align: center; padding: 2rem;">
            <h3>Total Earned</h3>
            <div style="font-size: 2rem; font-weight: bold; color: #16a34a;">
                +{total_earned} KIC
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        cursor.execute("SELECT SUM(amount) FROM kic_transactions WHERE user_id = ? AND amount < 0", (user['id'],))
        total_spent = abs(cursor.fetchone()[0] or 0)
        
        st.markdown(f'''
        <div class="modern-card" style="text-align: center; padding: 2rem;">
            <h3>Total Spent</h3>
            <div style="font-size: 2rem; font-weight: bold; color: #dc2626;">
                -{total_spent} KIC
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")

    # KIC Features
    tab1, tab2, tab3, tab4 = st.tabs(["💳 Transactions", "📊 Analytics", "🔄 Transfer", "🎁 Earn More"])

    with tab1:
        st.markdown("### Recent Transactions")
        
        transactions = KICManager.get_kic_transactions(user['id'], db, 20)
        
        if transactions:
            for txn in transactions:
                color = "#16a34a" if txn['amount'] > 0 else "#dc2626"
                sign = "+" if txn['amount'] > 0 else ""
                icon = "📈" if txn['amount'] > 0 else "📉"
                
                st.markdown(f'''
                <div class="modern-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <span style="font-size: 1.5rem;">{icon}</span>
                            <div>
                                <div style="font-weight: 600;">{txn['transaction_type'].title()}</div>
                                <div style="color: #64748b; font-size: 0.9rem;">{txn['description']}</div>
                                <div style="color: #94a3b8; font-size: 0.8rem;">{txn['created_at']}</div>
                            </div>
                        </div>
                        <div style="color: {color}; font-weight: bold; font-size: 1.2rem;">
                            {sign}{txn['amount']} KIC
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No transactions yet. Start earning KIC by completing projects!")

    with tab2:
        st.markdown("### KIC Analytics")
        
        # Monthly earning chart
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        earnings = [50 + i*5 + (i%7)*20 for i in range(30)]
        
        fig = px.line(x=dates, y=earnings, 
                     title="Daily KIC Earnings",
                     labels={'x': 'Date', 'y': 'KIC Earned'})
        fig.update_traces(line_color='#f59e0b', line_width=3)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("### Transfer KIC")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Send KIC")
            with st.form("send_kic"):
                cursor = db.conn.cursor()
                cursor.execute("SELECT id, name FROM users WHERE id != ?", (user['id'],))
                other_users = cursor.fetchall()
                
                recipient = st.selectbox("Send to", 
                                        [(u['id'], u['name']) for u in other_users],
                                        format_func=lambda x: x[1])
                
                amount = st.number_input("Amount (KIC)", min_value=1, max_value=user['kic_balance'], value=100)
                description = st.text_input("Description", value="KIC Transfer")
                
                if st.form_submit_button("Send KIC 💸"):
                    success = KICManager.transfer_kic(user['id'], recipient[0], amount, description, db)
                    if success:
                        st.success(f"Successfully sent {amount} KIC to {recipient[1]}!")
                        st.session_state.user['kic_balance'] -= amount
                        st.rerun()
                    else:
                        st.error("Insufficient KIC balance!")

        with col2:
            st.markdown("#### Request KIC")
            with st.form("request_kic"):
                requester = st.selectbox("Request from", 
                                       [(u['id'], u['name']) for u in other_users],
                                       format_func=lambda x: x[1])
                
                req_amount = st.number_input("Amount (KIC)", min_value=1, value=100)
                req_reason = st.text_input("Reason", value="Payment for services")
                
                if st.form_submit_button("Send Request 📧"):
                    st.success(f"KIC request sent to {requester[1]}!")

    with tab4:
        st.markdown("### Earn More KIC")
        
        earning_opportunities = [
            {
                "title": "Complete Profile",
                "description": "Add skills, portfolio, and certifications",
                "reward": 100,
                "icon": "👤"
            },
            {
                "title": "First Project Completion",
                "description": "Successfully complete your first project",
                "reward": 500,
                "icon": "🎯"
            },
            {
                "title": "5-Star Rating",
                "description": "Receive a 5-star rating from a client",
                "reward": 200,
                "icon": "⭐"
            },
            {
                "title": "Referral Bonus",
                "description": "Invite a friend to join the platform",
                "reward": 300,
                "icon": "🤝"
            },
            {
                "title": "Lab Booking",
                "description": "Book and complete a lab session",
                "reward": 150,
                "icon": "🔬"
            }
        ]

        for opportunity in earning_opportunities:
            st.markdown(f'''
            <div class="modern-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span style="font-size: 2rem;">{opportunity['icon']}</span>
                        <div>
                            <div style="font-weight: 600; font-size: 1.1rem;">{opportunity['title']}</div>
                            <div style="color: #64748b;">{opportunity['description']}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #16a34a; font-weight: bold; font-size: 1.2rem;">
                            +{opportunity['reward']} KIC
                        </div>
                        <button class="professional-btn" style="font-size: 0.9rem; padding: 0.5rem 1rem;">
                            Start Now
                        </button>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)


def show_enhanced_projects_page(db: Database):
    """Enhanced projects page with KIC integration"""
    
    st.markdown('<h1 class="gradient-text">🚀 Innovation Projects</h1>', unsafe_allow_html=True)
    st.markdown("Discover cutting-edge projects and collaboration opportunities")

    # Project metrics
    col1, col2, col3, col4 = st.columns(4)
    
    cursor = db.conn.cursor()
    
    with col1:
        cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'Active'")
        active_count = cursor.fetchone()[0]
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{active_count}</div>
            <div style="color: #64748b; font-weight: 600;">Active Projects</div>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        cursor.execute("SELECT SUM(kic_budget_max) FROM projects WHERE status = 'Active'")
        total_kic = cursor.fetchone()[0] or 0
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{total_kic:,}</div>
            <div style="color: #64748b; font-weight: 600;">Total KIC Available</div>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        cursor.execute("SELECT COUNT(DISTINCT organization) FROM projects")
        org_count = cursor.fetchone()[0]
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{org_count}</div>
            <div style="color: #64748b; font-weight: 600;">Partner Organizations</div>
        </div>
        ''', unsafe_allow_html=True)

    with col4:
        cursor.execute("SELECT AVG(applications) FROM projects WHERE status = 'Active'")
        avg_applications = cursor.fetchone()[0] or 0
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{avg_applications:.1f}</div>
            <div style="color: #64748b; font-weight: 600;">Avg. Applications</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")

    # Enhanced project tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Active Projects", "⚡ Urgent", "💰 High Value", "🎯 My Applications"])

    with tab1:
        show_enhanced_projects_by_status(db, "Active")

    with tab2:
        show_enhanced_projects_by_urgency(db, "High")

    with tab3:
        show_enhanced_high_value_projects(db)

    with tab4:
        show_my_applications(db)


def show_enhanced_projects_by_status(db: Database, status: str):
    """Enhanced project display with KIC integration"""
    
    cursor = db.conn.cursor()
    cursor.execute("""
                   SELECT p.*, c.name as company_name, c.industry, c.is_verified as company_verified,
                          julianday(deadline) - julianday('now') as days_left
                   FROM projects p
                   LEFT JOIN companies c ON p.company_id = c.id
                   WHERE p.status = ?
                   ORDER BY p.views DESC, p.created_at DESC
                   """, (status,))
    projects = cursor.fetchall()

    if not projects:
        st.info(f"No {status.lower()} projects at the moment.")
        return

    for project in projects:
        days_left = int(project['days_left']) if project['days_left'] else 0
        urgency_class = f"urgency-{project['urgency'].lower()}"
        
        st.markdown(f'''
        <div class="modern-card">
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin-bottom: 0.5rem;">{project['title']}</h3>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span style="color: #0077b5; font-weight: 600;">{project['organization']}</span>
                        {f'<span class="status-badge status-verified">✓ Verified</span>' if project.get('company_verified') else ''}
                        <span class="status-badge status-featured">{project.get('industry', 'Technology')}</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #16a34a; font-weight: bold; font-size: 1.3rem;">
                        💰 {project['kic_budget_min']:,} - {project['kic_budget_max']:,} KIC
                    </div>
                    <div style="color: #64748b;">
                        AED {project['budget_min']:,} - {project['budget_max']:,}
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <span>📍 {project['location']}</span> • 
                <span class="{urgency_class}">⚡ {project['urgency']} Priority</span> • 
                <span>⏰ {days_left} days left</span> • 
                <span>👁️ {project['views']} views</span> • 
                <span>📝 {project['applications']} applications</span>
                {f" • 🌐 Remote OK" if project['remote_possible'] else ""}
            </div>
            
            <div style="color: #475569; margin-bottom: 1.5rem; line-height: 1.6;">
                {project['description']}
            </div>
            
            <div style="margin-bottom: 1rem;">
                <strong style="color: #1e293b;">Requirements:</strong>
                <div style="color: #64748b; margin-top: 0.5rem;">{project['requirements']}</div>
            </div>
            
            <div style="margin-bottom: 1rem;">
                {' '.join([f'<span class="skill-tag">{tag.strip()}</span>' for tag in project['tags'].split(',')])}
            </div>
        </div>
        ''', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📋 View Details", key=f"view_proj_{project['id']}"):
                # Increment view count
                cursor.execute("UPDATE projects SET views = views + 1 WHERE id = ?", (project['id'],))
                db.conn.commit()
                st.session_state.selected_project_id = project['id']
                st.rerun()
        
        with col2:
            if st.button("🚀 Apply Now", key=f"apply_proj_{project['id']}"):
                st.session_state.apply_project_id = project['id']
                st.rerun()
        
        with col3:
            if st.button("💬 Ask Question", key=f"question_proj_{project['id']}"):
                st.session_state.question_project_id = project['id']
                st.rerun()
        
        with col4:
            if st.button("⭐ Save", key=f"save_proj_{project['id']}"):
                st.success("Project saved!")


def show_enhanced_projects_by_urgency(db: Database, urgency: str):
    """Show projects by urgency level"""
    
    cursor = db.conn.cursor()
    cursor.execute("""
                   SELECT p.*, c.name as company_name, c.industry,
                          julianday(deadline) - julianday('now') as days_left
                   FROM projects p
                   LEFT JOIN companies c ON p.company_id = c.id
                   WHERE p.urgency = ? AND p.status = 'Active'
                   ORDER BY p.deadline ASC
                   """, (urgency,))
    
    urgent_projects = cursor.fetchall()
    
    if urgent_projects:
        st.markdown(f"### ⚡ {urgency} Priority Projects - Act Fast!")
        
        for project in urgent_projects:
            days_left = int(project['days_left']) if project['days_left'] else 0
            
            st.markdown(f'''
            <div class="modern-card" style="border-left: 4px solid #dc2626;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: #dc2626; margin-bottom: 0.5rem;">
                            🚨 {project['title']}
                        </h4>
                        <div style="color: #64748b;">
                            {project['organization']} • {project['location']} • ⏰ {days_left} days left
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #16a34a; font-weight: bold;">
                            💰 {project['kic_budget_max']:,} KIC
                        </div>
                        <button class="professional-btn" style="font-size: 0.9rem;">
                            Apply Now ⚡
                        </button>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info(f"No {urgency.lower()} priority projects at the moment.")


def show_enhanced_high_value_projects(db: Database):
    """Show high-value projects"""
    
    cursor = db.conn.cursor()
    cursor.execute("""
                   SELECT p.*, c.name as company_name, c.industry
                   FROM projects p
                   LEFT JOIN companies c ON p.company_id = c.id
                   WHERE p.kic_budget_max >= 3000 AND p.status = 'Active'
                   ORDER BY p.kic_budget_max DESC
                   """)
    
    high_value_projects = cursor.fetchall()
    
    st.markdown("### 💎 Premium Projects - High Value Opportunities")
    
    for project in high_value_projects:
        st.markdown(f'''
        <div class="modern-card" style="border: 2px solid #f59e0b; background: linear-gradient(135deg, rgba(251, 191, 36, 0.05), rgba(245, 158, 11, 0.05));">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <span style="font-size: 2rem;">💎</span>
                <div>
                    <h3 style="margin: 0; color: #d97706;">{project['title']}</h3>
                    <div style="color: #0077b5; font-weight: 600;">{project['organization']}</div>
                </div>
                <div style="margin-left: auto; text-align: right;">
                    <div style="background: #f59e0b; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                        💰 {project['kic_budget_max']:,} KIC
                    </div>
                </div>
            </div>
            <div style="color: #475569; margin-bottom: 1rem;">
                {project['description'][:200]}...
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    📍 {project['location']} • 👁️ {project['views']} views
                </div>
                <button class="professional-btn">
                    Apply for Premium Project 💎
                </button>
            </div>
        </div>
        ''', unsafe_allow_html=True)


def show_my_applications(db: Database):
    """Show user's project applications"""
    
    st.markdown("### 📋 My Project Applications")
    st.info("Application tracking feature coming soon! You'll be able to see all your submitted applications here.")
    
    # Placeholder for applications
    sample_applications = [
        {
            "project": "AI-Powered Smart City Infrastructure",
            "company": "Dubai Future Foundation",
            "status": "Under Review",
            "applied_date": "2024-02-15",
            "kic_amount": "6000 KIC"
        },
        {
            "project": "Blockchain Supply Chain Transparency", 
            "company": "Mubadala Investment Company",
            "status": "Accepted",
            "applied_date": "2024-02-10",
            "kic_amount": "4500 KIC"
        }
    ]
    
    for app in sample_applications:
        status_color = "#16a34a" if app['status'] == "Accepted" else "#f59e0b"
        
        st.markdown(f'''
        <div class="modern-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin-bottom: 0.5rem;">{app['project']}</h4>
                    <div style="color: #64748b;">
                        {app['company']} • Applied on {app['applied_date']}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="color: {status_color}; font-weight: bold; margin-bottom: 0.5rem;">
                        {app['status']}
                    </div>
                    <div style="color: #16a34a; font-weight: bold;">
                        💰 {app['kic_amount']}
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)


def show_enhanced_labs_page(db: Database):
    """Enhanced labs page with KIC payments"""
    
    st.markdown('<h1 class="gradient-text">🔬 Innovation Labs</h1>', unsafe_allow_html=True)
    st.markdown("Access cutting-edge research facilities across the UAE")

    # Lab metrics
    col1, col2, col3, col4 = st.columns(4)
    
    cursor = db.conn.cursor()
    
    with col1:
        cursor.execute("SELECT COUNT(*) FROM labs")
        total_labs = cursor.fetchone()[0]
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{total_labs}</div>
            <div style="color: #64748b; font-weight: 600;">Available Labs</div>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        cursor.execute("SELECT AVG(rating) FROM labs")
        avg_rating = cursor.fetchone()[0] or 0
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{avg_rating:.1f}⭐</div>
            <div style="color: #64748b; font-weight: 600;">Average Rating</div>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        cursor.execute("SELECT COUNT(DISTINCT specialty) FROM labs")
        specialties = cursor.fetchone()[0]
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{specialties}</div>
            <div style="color: #64748b; font-weight: 600;">Specializations</div>
        </div>
        ''', unsafe_allow_html=True)

    with col4:
        cursor.execute("SELECT SUM(total_bookings) FROM labs")
        total_bookings = cursor.fetchone()[0] or 0
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{total_bookings}</div>
            <div style="color: #64748b; font-weight: 600;">Total Bookings</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")

    # Search and filters
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search labs...", 
                                   placeholder="Search by name, equipment, or specialty")

    with col2:
        sort_by = st.selectbox("Sort by", ["Rating", "Price", "KIC Price", "Availability"])

    with col3:
        payment_method = st.radio("Payment", ["Both", "AED", "KIC"], horizontal=True)

    # Enhanced filters
    with st.expander("🔧 Advanced Filters", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cursor.execute("SELECT DISTINCT specialty FROM labs")
            specialties = [row[0] for row in cursor.fetchall()]
            selected_specialties = st.multiselect("Specialties", specialties)
            
        with col2:
            cursor.execute("SELECT DISTINCT location FROM labs")
            locations = [row[0] for row in cursor.fetchall()]
            selected_locations = st.multiselect("Locations", locations)
            
        with col3:
            if payment_method in ["Both", "AED"]:
                aed_range = st.slider("AED Price per day", 0, 3000, (0, 3000))
            else:
                aed_range = (0, 10000)
                
        with col4:
            if payment_method in ["Both", "KIC"]:
                kic_range = st.slider("KIC Price per day", 0, 1500, (0, 1500))
            else:
                kic_range = (0, 5000)

    # Build query
    query = "SELECT * FROM labs WHERE 1=1"
    params = []

    if search_query:
        query += " AND (name LIKE ? OR description LIKE ? OR equipment LIKE ? OR specialty LIKE ?)"
        search_param = f"%{search_query}%"
        params.extend([search_param] * 4)

    if selected_specialties:
        query += f" AND specialty IN ({','.join(['?'] * len(selected_specialties))})"
        params.extend(selected_specialties)

    if selected_locations:
        query += f" AND location IN ({','.join(['?'] * len(selected_locations))})"
        params.extend(selected_locations)

    query += " AND price_per_day BETWEEN ? AND ?"
    params.extend([aed_range[0], aed_range[1]])

    query += " AND kic_price_per_day BETWEEN ? AND ?"
    params.extend([kic_range[0], kic_range[1]])

    # Sorting
    if sort_by == "Rating":
        query += " ORDER BY rating DESC"
    elif sort_by == "Price":
        query += " ORDER BY price_per_day ASC"
    elif sort_by == "KIC Price":
        query += " ORDER BY kic_price_per_day ASC"
    else:
        query += " ORDER BY available_from ASC"

    cursor.execute(query, params)
    labs = cursor.fetchall()

    st.markdown(f"### Found {len(labs)} laboratories")

    # Display labs
    for lab in labs:
        st.markdown(f'''
        <div class="modern-card">
            <div style="display: flex; gap: 1.5rem;">
                <div style="flex-shrink: 0;">
                    <div style="width: 100px; height: 100px; background: linear-gradient(135deg, #0077b5, #00a0dc); 
                                border-radius: 12px; display: flex; align-items: center; justify-content: center;
                                color: white; font-size: 2rem;">
                        🔬
                    </div>
                </div>
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 0.5rem;">
                        <div style="flex: 1;">
                            <h3 style="margin-bottom: 0.5rem;">{lab['name']}</h3>
                            <div style="color: #0077b5; font-weight: 600; margin-bottom: 0.5rem;">
                                {lab['university']}
                            </div>
                            <div style="color: #64748b; margin-bottom: 1rem;">
                                📍 {lab['location']} • 
                                🧪 {lab['specialty']} • 
                                👥 Capacity: {lab['capacity']} • 
                                ⭐ {lab['rating']:.1f} rating • 
                                📅 {lab['total_bookings']} bookings
                            </div>
                            <div style="color: #475569; margin-bottom: 1rem; line-height: 1.6;">
                                {lab['description']}
                            </div>
                            <div style="margin-bottom: 1rem;">
                                <strong>Equipment:</strong>
                                <div style="margin-top: 0.5rem;">
                                    {' '.join([f'<span class="skill-tag">{eq.strip()}</span>' 
                                             for eq in lab['equipment'].split(',')[:4]])}
                                </div>
                            </div>
                            <div style="margin-bottom: 1rem;">
                                <strong>Amenities:</strong>
                                <div style="margin-top: 0.5rem;">
                                    {' '.join([f'<span class="skill-tag">{amenity.strip()}</span>' 
                                             for amenity in lab['amenities'].split(',')[:3]])}
                                </div>
                            </div>
                        </div>
                        <div style="text-align: right; margin-left: 2rem;">
                            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                                <div style="margin-bottom: 1rem;">
                                    <div style="color: #16a34a; font-weight: bold; font-size: 1.3rem;">
                                        💰 {lab['kic_price_per_day']} KIC/day
                                    </div>
                                    <div style="color: #64748b; font-size: 0.9rem;">
                                        or AED {lab['price_per_day']}/day
                                    </div>
                                </div>
                                <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 1rem;">
                                    Available from: {lab['available_from']}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📋 View Details", key=f"view_lab_{lab['id']}"):
                st.session_state.selected_lab_id = lab['id']
                st.rerun()
        with col2:
            if st.button("💰 Book with KIC", key=f"book_kic_{lab['id']}"):
                st.session_state.book_lab_kic_id = lab['id']
                st.rerun()
        with col3:
            if st.button("💳 Book with AED", key=f"book_aed_{lab['id']}"):
                st.session_state.book_lab_aed_id = lab['id']
                st.rerun()
        with col4:
            if st.button("📞 Contact Lab", key=f"contact_lab_{lab['id']}"):
                st.session_state.contact_lab_id = lab['id']
                st.rerun()


def show_enhanced_profile_page(db: Database):
    """Enhanced profile page with social features"""
    
    user = st.session_state.user
    
    st.markdown(f'''
    <div style="margin-bottom: 2rem;">
        <h1 class="gradient-text">My Professional Profile</h1>
        <p style="color: #64748b;">Manage your professional presence on UAE Innovate Hub</p>
    </div>
    ''', unsafe_allow_html=True)

    # Profile tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Profile", "🤝 Network", "💼 Activity", "💰 Wallet", "⚙️ Settings"])

    with tab1:
        col1, col2 = st.columns([1, 2])

        with col1:
            # Enhanced profile card
            st.markdown(f'''
            <div class="profile-card">
                <div class="profile-avatar">{user['name'][0].upper()}</div>
                <h3 style="margin-bottom: 0.5rem;">{user['name']}</h3>
                {f'<span class="status-badge status-verified">✓ Verified</span>' if user['is_verified'] else ''}
                <div style="opacity: 0.9; margin: 1rem 0;">{user['organization']}</div>
                <div style="opacity: 0.8; margin-bottom: 1rem;">📍 {user.get('location', 'UAE')}</div>
                
                <div style="display: flex; justify-content: space-around; margin: 1.5rem 0;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold;">{user['total_projects_completed']}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">Projects</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold;">{user['reputation_score']}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">Reputation</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold;">{user['kic_balance']}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">KIC</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            # Quick stats
            cursor = db.conn.cursor()
            cursor.execute("""
                           SELECT COUNT(*) FROM connections 
                           WHERE (requester_id = ? OR addressee_id = ?) AND status = 'accepted'
                           """, (user['id'], user['id']))
            network_size = cursor.fetchone()[0]

            st.markdown(f'''
            <div class="modern-card">
                <h4>Professional Stats</h4>
                <div style="margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                        <span>Network Size:</span>
                        <strong>{network_size} connections</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                        <span>Profile Views:</span>
                        <strong>127 this month</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                        <span>KIC Earned:</span>
                        <strong>2,450 total</strong>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        with col2:
            st.markdown("### Edit Profile Information")

            with st.form("edit_profile"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    name = st.text_input("Full Name", value=user['name'])
                    organization = st.text_input("Organization", value=user['organization'])
                    location = st.selectbox("Location", 
                                           ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"],
                                           index=0 if not user.get('location') else 
                                           ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"].index(user.get('location', 'Abu Dhabi')))
                    
                with col_b:
                    linkedin_url = st.text_input("LinkedIn Profile", value=user.get('linkedin_url', ''))
                    website_url = st.text_input("Website/Portfolio", value=user.get('website_url', ''))
                    phone = st.text_input("Phone Number", placeholder="+971 50 123 4567")

                bio = st.text_area("Professional Bio", 
                                 value=user.get('bio', ''),
                                 placeholder="Tell the community about your expertise, interests, and goals...")
                
                # Professional details for talents
                if user['user_type'] == 'talent':
                    st.markdown("#### Talent-Specific Information")
                    
                    col_c, col_d = st.columns(2)
                    with col_c:
                        title = st.text_input("Professional Title", placeholder="e.g., Senior Data Scientist")
                        experience = st.selectbox("Years of Experience", 
                                                ["0-1 years", "2-3 years", "4-5 years", "6-10 years", "10+ years"])
                        
                    with col_d:
                        availability = st.selectbox("Availability", 
                                                  ["Full-time", "Part-time", "Contract", "Remote"])
                        hourly_rate = st.number_input("Hourly Rate (AED)", min_value=0, value=150)
                    
                    skills = st.text_input("Skills", 
                                         placeholder="Python, Machine Learning, Data Analysis, etc.")
                    certifications = st.text_input("Certifications", 
                                                  placeholder="AWS Certified, PMP, etc.")

                if st.form_submit_button("Save Profile Changes", use_container_width=True):
                    cursor = db.conn.cursor()
                    cursor.execute("""
                                   UPDATE users 
                                   SET name = ?, organization = ?, bio = ?, location = ?
                                   WHERE id = ?
                                   """, (name, organization, bio, location, user['id']))
                    db.conn.commit()
                    
                    st.success("✅ Profile updated successfully!")
                    st.session_state.user.update({
                        'name': name,
                        'organization': organization,
                        'bio': bio,
                        'location': location
                    })
                    st.rerun()

    with tab2:
        st.markdown("### 🤝 Professional Network")
        
        # Network statistics
        col1, col2, col3 = st.columns(3)
        
        cursor = db.conn.cursor()
        
        with col1:
            cursor.execute("""
                           SELECT COUNT(*) FROM connections 
                           WHERE (requester_id = ? OR addressee_id = ?) AND status = 'accepted'
                           """, (user['id'], user['id']))
            connections_count = cursor.fetchone()[0]
            
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{connections_count}</div>
                <div style="color: #64748b; font-weight: 600;">Connections</div>
            </div>
            ''', unsafe_allow_html=True)

        with col2:
            cursor.execute("""
                           SELECT COUNT(*) FROM connections 
                           WHERE addressee_id = ? AND status = 'pending'
                           """, (user['id'],))
            pending_requests = cursor.fetchone()[0]
            
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{pending_requests}</div>
                <div style="color: #64748b; font-weight: 600;">Pending Requests</div>
            </div>
            ''', unsafe_allow_html=True)

        with col3:
            # Calculate network growth (mock data)
            network_growth = "+12%"
            
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{network_growth}</div>
                <div style="color: #64748b; font-weight: 600;">This Month</div>
            </div>
            ''', unsafe_allow_html=True)

        # Show connections
        cursor.execute("""
                       SELECT u.id, u.name, u.user_type, u.organization, u.is_verified
                       FROM connections c
                       JOIN users u ON (
                           CASE WHEN c.requester_id = ? THEN c.addressee_id ELSE c.requester_id END = u.id
                       )
                       WHERE (c.requester_id = ? OR c.addressee_id = ?) AND c.status = 'accepted'
                       ORDER BY c.accepted_at DESC
                       """, (user['id'], user['id'], user['id']))
        
        connections = cursor.fetchall()
        
        if connections:
            st.markdown("#### Your Professional Network")
            
            for connection in connections:
                st.markdown(f'''
                <div class="modern-card">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #0077b5, #00a0dc); 
                                    border-radius: 50%; display: flex; align-items: center; justify-content: center;
                                    color: white; font-weight: bold;">
                            {connection['name'][0].upper()}
                        </div>
                        <div style="flex: 1;">
                            <div style="font-weight: 600;">{connection['name']}</div>
                            <div style="color: #64748b;">{connection['organization']}</div>
                            <div style="color: #0077b5; font-size: 0.9rem;">{connection['user_type'].title()}</div>
                        </div>
                        <div>
                            {f'<span class="status-badge status-verified">✓</span>' if connection['is_verified'] else ''}
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

        # Connection requests
        if pending_requests > 0:
            st.markdown("#### Pending Connection Requests")
            
            cursor.execute("""
                           SELECT c.id, u.name, u.user_type, u.organization, c.message
                           FROM connections c
                           JOIN users u ON c.requester_id = u.id
                           WHERE c.addressee_id = ? AND c.status = 'pending'
                           """, (user['id'],))
            
            requests = cursor.fetchall()
            
            for request in requests:
                st.markdown(f'''
                <div class="modern-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600;">{request['name']}</div>
                            <div style="color: #64748b;">{request['organization']}</div>
                            <div style="color: #475569; font-size: 0.9rem; margin-top: 0.5rem;">
                                "{request['message']}"
                            </div>
                        </div>
                        <div style="display: flex; gap: 0.5rem;">
                            <button class="professional-btn" style="font-size: 0.9rem; padding: 0.5rem 1rem;">
                                Accept
                            </button>
                            <button class="professional-btn" style="background: #64748b; font-size: 0.9rem; padding: 0.5rem 1rem;">
                                Decline
                            </button>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

    with tab3:
        st.markdown("### 💼 Professional Activity")
        
        # Activity metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('''
            <div class="metric-card">
                <div class="metric-value">15</div>
                <div style="color: #64748b; font-weight: 600;">Activities This Month</div>
            </div>
            ''', unsafe_allow_html=True)

        with col2:
            st.markdown('''
            <div class="metric-card">
                <div class="metric-value">3</div>
                <div style="color: #64748b; font-weight: 600;">Projects Started</div>
            </div>
            ''', unsafe_allow_html=True)

        with col3:
            st.markdown('''
            <div class="metric-card">
                <div class="metric-value">127</div>
                <div style="color: #64748b; font-weight: 600;">Profile Views</div>
            </div>
            ''', unsafe_allow_html=True)

        # Recent activity
        cursor.execute("""
                       SELECT * FROM activities 
                       WHERE user_id = ? 
                       ORDER BY created_at DESC 
                       LIMIT 10
                       """, (user['id'],))
        
        activities = cursor.fetchall()
        
        if activities:
            st.markdown("#### Recent Activity")
            
            for activity in activities:
                icon_map = {
                    "project_completed": "✅",
                    "skill_certified": "🎓", 
                    "connection_made": "🤝",
                    "project_started": "🚀",
                    "lab_booked": "🔬",
                    "review_received": "⭐"
                }
                
                icon = icon_map.get(activity['activity_type'], "📋")
                
                st.markdown(f'''
                <div class="activity-item">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span style="font-size: 1.5rem;">{icon}</span>
                        <div style="flex: 1;">
                            <div style="font-weight: 600;">{activity['title']}</div>
                            <div style="color: #64748b; font-size: 0.9rem;">{activity['description']}</div>
                        </div>
                        <div style="color: #94a3b8; font-size: 0.8rem;">
                            {activity['created_at'][:10]}
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No recent activity. Start connecting and working on projects to build your activity history!")

    with tab4:
        st.markdown("### 💰 KIC Wallet Management")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # KIC balance overview
            st.markdown(f'''
            <div class="profile-card">
                <h3>Current KIC Balance</h3>
                <div style="font-size: 3rem; font-weight: bold; margin: 1rem 0;">
                    {user['kic_balance']} KIC
                </div>
                <div style="opacity: 0.8;">Knowledge & Innovation Connected Currency</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Recent transactions
            st.markdown("#### Recent KIC Transactions")
            
            transactions = KICManager.get_kic_transactions(user['id'], db, 10)
            
            if transactions:
                for txn in transactions:
                    color = "#16a34a" if txn['amount'] > 0 else "#dc2626"
                    sign = "+" if txn['amount'] > 0 else ""
                    icon = "📈" if txn['amount'] > 0 else "📉"
                    
                    st.markdown(f'''
                    <div class="modern-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <span style="font-size: 1.5rem;">{icon}</span>
                                <div>
                                    <div style="font-weight: 600;">{txn['transaction_type'].title()}</div>
                                    <div style="color: #64748b; font-size: 0.9rem;">{txn['description']}</div>
                                    <div style="color: #94a3b8; font-size: 0.8rem;">{txn['created_at'][:16]}</div>
                                </div>
                            </div>
                            <div style="color: {color}; font-weight: bold; font-size: 1.2rem;">
                                {sign}{txn['amount']} KIC
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.info("No KIC transactions yet.")

        with col2:
            # Quick actions
            st.markdown("#### Quick Actions")
            
            if st.button("💸 Send KIC", use_container_width=True):
                st.session_state.show_send_kic = True
                st.rerun()
                
            if st.button("📊 View Analytics", use_container_width=True):
                st.session_state.current_page = "KIC Hub"
                st.rerun()
                
            if st.button("🎁 Earn More KIC", use_container_width=True):
                st.session_state.current_page = "KIC Hub"
                st.rerun()
            
            # KIC earning tips
            st.markdown('''
            <div class="modern-card">
                <h4>💡 Earning Tips</h4>
                <div style="font-size: 0.9rem; line-height: 1.6;">
                    • Complete projects successfully<br>
                    • Maintain high ratings<br>
                    • Refer new talents<br>
                    • Use labs regularly<br>
                    • Stay active in community
                </div>
            </div>
            ''', unsafe_allow_html=True)

    with tab5:
        st.markdown("### ⚙️ Account Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Account Security")
            
            with st.form("change_password"):
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Update Password"):
                    if new_password != confirm_password:
                        st.error("Passwords don't match")
                    elif len(new_password) < 8:
                        st.error("Password must be at least 8 characters")
                    else:
                        # Verify current password
                        cursor = db.conn.cursor()
                        cursor.execute("""
                                       SELECT id FROM users 
                                       WHERE id = ? AND password_hash = ?
                                       """, (user['id'], EnhancedAuthManager.hash_password(current_password)))
                        
                        if cursor.fetchone():
                            cursor.execute("""
                                           UPDATE users SET password_hash = ? WHERE id = ?
                                           """, (EnhancedAuthManager.hash_password(new_password), user['id']))
                            db.conn.commit()
                            st.success("✅ Password updated successfully!")
                        else:
                            st.error("Current password is incorrect")

        with col2:
            st.markdown("#### Notification Preferences")
            
            notification_settings = {
                "Email notifications for new projects": True,
                "Email notifications for messages": True,
                "Email notifications for bookings": True,
                "Weekly activity summary": False,
                "KIC transaction alerts": True,
                "Connection requests": True
            }
            
            for setting, default_value in notification_settings.items():
                st.checkbox(setting, value=default_value)
            
            if st.button("Save Notification Settings"):
                st.success("✅ Notification preferences saved!")

        st.markdown("---")
        
        # Account actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Export My Data", use_container_width=True):
                st.info("Data export will be sent to your email within 24 hours.")
                
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
                
        with col3:
            if st.button("🗑️ Delete Account", type="secondary", use_container_width=True):
                st.warning("⚠️ This action cannot be undone!")
                if st.checkbox("I understand this will permanently delete my account"):
                    st.error("Account deletion is not available in this demo.")


if __name__ == "__main__":
    main()
