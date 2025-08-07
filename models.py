from datetime import datetime
from app import db
from sqlalchemy import JSON

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api_key = db.Column(db.String(256), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    blockchain = db.Column(db.String(32), nullable=False)
    private_key_encrypted = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('wallets', lazy=True))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    tx_hash = db.Column(db.String(256), unique=True, nullable=False)
    blockchain = db.Column(db.String(32), nullable=False)
    operation_type = db.Column(db.String(64), nullable=False)  # swap, lend, farm, etc.
    protocol = db.Column(db.String(64), nullable=True)
    amount = db.Column(db.String(64), nullable=True)
    token_in = db.Column(db.String(64), nullable=True)
    token_out = db.Column(db.String(64), nullable=True)
    gas_used = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(32), default='pending')  # pending, confirmed, failed
    tx_metadata = db.Column(JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    wallet = db.relationship('Wallet', backref=db.backref('transactions', lazy=True))

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    token_address = db.Column(db.String(256), nullable=False)
    token_symbol = db.Column(db.String(32), nullable=False)
    balance = db.Column(db.String(64), nullable=False)
    usd_value = db.Column(db.Float, nullable=True)
    blockchain = db.Column(db.String(32), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('portfolio', lazy=True))
    wallet = db.relationship('Wallet', backref=db.backref('portfolio', lazy=True))

class ProtocolPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    protocol = db.Column(db.String(64), nullable=False)
    position_type = db.Column(db.String(32), nullable=False)  # lending, farming, staking
    token_address = db.Column(db.String(256), nullable=False)
    token_symbol = db.Column(db.String(32), nullable=False)
    amount = db.Column(db.String(64), nullable=False)
    apy = db.Column(db.Float, nullable=True)
    rewards_earned = db.Column(db.String(64), default='0')
    blockchain = db.Column(db.String(32), nullable=False)
    position_metadata = db.Column(JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('positions', lazy=True))
    wallet = db.relationship('Wallet', backref=db.backref('positions', lazy=True))
