#!/usr/bin/env python3
"""
Setup script for Construction Project Management Chatbot
"""
import os
import subprocess
import sys
import shutil

def run_command(command, cwd=None):
    """Run a shell command."""
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        'logs',
        'database',
        'chatbot',
        'frontend/src'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_python_environment():
    """Set up Python virtual environment and install dependencies."""
    print("\n🐍 Setting up Python environment...")
    
    # Create virtual environment
    if not os.path.exists('venv'):
        run_command('python -m venv venv')
        print("✓ Created virtual environment")
    
    # Activate and install requirements
    if sys.platform == 'win32':
        activate_script = r'venv\Scripts\activate'
        pip_command = r'venv\Scripts\pip'
    else:
        activate_script = 'source venv/bin/activate'
        pip_command = 'venv/bin/pip'
    
    # Install requirements
    if os.path.exists('requirements.txt'):
        run_command(f"{pip_command} install -r requirements.txt")
        print("✓ Installed Python dependencies")

def setup_frontend():
    """Set up React frontend."""
    print("\n⚛️  Setting up React frontend...")
    
    if not os.path.exists('frontend/package.json'):
        print("Creating React app...")
        run_command('npx create-react-app frontend')
        
        # Install additional dependencies
        run_command('npm install marked bootstrap-icons', cwd='frontend')
        print("✓ Installed frontend dependencies")
    
    # Copy our custom files
    if os.path.exists('frontend/src/Home.jsx'):
        print("✓ Custom React components already in place")

def create_env_file():
    """Create .env file from template."""
    print("\n⚙️  Setting up environment variables...")
    
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✓ Created .env file from template")
            print("⚠️  Please edit .env file with your actual values:")
            print("   - GEMINI_API_KEY")
            print("   - Database credentials")
        else:
            print("❌ .env.example not found")
    else:
        print("✓ .env file already exists")

def verify_setup():
    """Verify the setup is complete."""
    print("\n✅ Verifying setup...")
    
    checks = [
        ('Python dependencies', 'venv' in os.listdir('.')),
        ('Frontend dependencies', 'frontend/node_modules' in os.listdir('frontend') if os.path.exists('frontend') else False),
        ('Environment file', os.path.exists('.env')),
        ('Database module', os.path.exists('database/__init__.py')),
        ('Chatbot module', os.path.exists('chatbot/__init__.py')),
    ]
    
    all_good = True
    for check_name, check_result in checks:
        status = "✓" if check_result else "❌"
        print(f"  {status} {check_name}")
        if not check_result:
            all_good = False
    
    return all_good

def main():
    """Main setup function."""
    print("🚀 Setting up Construction Project Management Chatbot\n")
    
    # Create directory structure
    create_directories()
    
    # Set up Python environment
    setup_python_environment()
    
    # Set up frontend
    setup_frontend()
    
    # Create environment file
    create_env_file()
    
    # Verify setup
    if verify_setup():
        print("\n🎉 Setup complete! Next steps:")
        print("1. Edit .env file with your API keys and database credentials")
        print("2. Start the backend: python app.py")
        print("3. Start the frontend: cd frontend && npm start")
        print("\nFor database setup, ensure PostgreSQL is running and create a database named 'construction_db'")
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")

if __name__ == '__main__':
    main()