#!/usr/bin/env python3
"""
Initialize Vault with OpenWeatherMap API key
Simple script to securely store your API key
"""

import sys
from pathlib import Path
from vault_local import get_vault

def main():
    print("🔐 Initialiser le vault local pour Weather API")
    print("=" * 50)
    print()
    
    # Get the API key from user
    api_key = input("📝 Entrez votre clé API OpenWeatherMap: ").strip()
    
    if not api_key:
        print("❌ Erreur: La clé API ne peut pas être vide")
        sys.exit(1)
    
    # Validate basic format (OpenWeather keys are typically 32 hex characters)
    if len(api_key) < 10:
        print("⚠️  Attention: Votre clé API semble courte")
        confirm = input("Continuer quand même? (y/n): ").strip().lower()
        if confirm != 'y':
            sys.exit(1)
    
    try:
        # Store in vault
        vault = get_vault()
        vault.set_secret('weather/openweather', 'api_key', api_key)
        
        print()
        print("✅ Succès!")
        print("📋 Votre clé API est stockée dans: .vault_secrets.json")
        print("🔒 Ce fichier contient les secrets - NE PAS le committer dans Git!")
        print()
        print("Vous pouvez maintenant lancer votre application:")
        print("   python weather.py")
        print()
        
    except Exception as e:
        print(f"❌ Erreur lors du stockage du secret: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
