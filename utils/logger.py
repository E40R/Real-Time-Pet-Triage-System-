"""
Logging Utilities
Provides consistent logging across the application
"""
from typing import List
from models.schemas import HealthOverview


class Logger:
    """Handles formatted console output"""
    
    @staticmethod
    def user_speech(text: str):
        """Log user speech"""
        print(f"\n👤 You: {text}")
    
    @staticmethod
    def agent_response(text: str):
        """Log agent response"""
        print(f"\n🤖 Agent: {text}")
    
    @staticmethod
    def structured_analysis(analysis: HealthOverview):
        """Log structured analysis"""
        print("\n📊 Structured Analysis:")
        print(f"  Risk Level: {analysis.risk_level}")
        
        symptoms = ', '.join(analysis.symptom_analysis.symptoms_identified)
        print(f"  Symptoms: {symptoms}")
        
        print(f"  Requires Vet: {analysis.requires_vet}")
        
        if analysis.safety_flags:
            flags = ', '.join(analysis.safety_flags)
            print(f"  Safety Flags: {flags}")
    
    @staticmethod
    def info(message: str):
        """Log info message"""
        print(f"ℹ️  {message}")
    
    @staticmethod
    def success(message: str):
        """Log success message"""
        print(f"✅ {message}")
    
    @staticmethod
    def warning(message: str):
        """Log warning message"""
        print(f"⚠️  {message}")
    
    @staticmethod
    def error(message: str):
        """Log error message"""
        print(f"❌ {message}")
    
    @staticmethod
    def section_header(title: str):
        """Print section header"""
        print("\n" + "="*70)
        print(title)
        print("="*70)
    
    @staticmethod
    def banner():
        """Print application banner"""
        Logger.section_header("🐾 Pet Health Voice Consultation Agent")
        print("\nHow this works:")
        print("  • Speak naturally about your pet's symptoms")
        print("  • The AI will analyze and respond with guidance")
        print("  • You can interrupt the AI at any time by speaking")
        print("  • Press Ctrl+C to exit")
        print("\n⚠️  IMPORTANT: This is NOT a replacement for veterinary care!")
        print("="*70)
