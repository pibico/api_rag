#!/usr/bin/env python3
"""
Create an admin user for the RAG application
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.models import SessionLocal, User
from app.services.auth import get_password_hash
from getpass import getpass


def create_admin_user():
    """Create an admin user interactively"""
    print("=" * 60)
    print("Create Admin User for RAG Document Chat")
    print("=" * 60)

    # Get user input
    username = input("Enter username: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        return

    email = input("Enter email: ").strip()
    if not email:
        print("Error: Email cannot be empty")
        return

    password = getpass("Enter password: ")
    if not password:
        print("Error: Password cannot be empty")
        return

    password_confirm = getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match")
        return

    # Create database session
    db: Session = SessionLocal()

    try:
        # Check if username exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"Error: Username '{username}' already exists")
            return

        # Check if email exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            print(f"Error: Email '{email}' already exists")
            return

        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_admin=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print("=" * 60)
        print(f"Admin user created successfully!")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"User ID: {user.id}")
        print("=" * 60)

    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
