# Botismus - AI-Powered Discord Bot Manager

[English](#english) | [Deutsch](#deutsch)

> ⚠️ **BETA WARNING**: This bot is currently in BETA. Expect potential bugs and features to change. Use with caution in production environments.

## English Documentation

### Introduction
Botismus is an intelligent Discord bot manager that combines AI capabilities with server management features. Using the Ollama AI framework, it provides natural language interactions while managing your Discord server with a unique personality.

### Key Features
The bot offers a comprehensive set of management tools while maintaining a playful personality:

#### Server Management
- **Channel Control**: Create, delete, and organize channels and categories
- **Role Management**: Custom roles with specific permissions and hierarchies
- **Command System**: Create and manage custom commands with automated responses

#### AI Integration
- **Natural Language Processing**: Understands context and provides meaningful responses
- **Personality System**: Dynamic responses with configurable personality traits
- **Multi-language Support**: Primary support for English and German

#### Performance Tracking
- **Score System**: Performance tracking (10 points for success, -5 for errors)
- **Success Rate Monitoring**: Tracks interaction history and success rates
- **Automated Logging**: Comprehensive logging system for debugging

### Installation Guide

#### Prerequisites
Before installing Botismus, ensure your system meets these requirements:

**Hardware Requirements:**
- RAM: 4GB minimum (8GB recommended)
- CPU: 2 cores minimum (4 cores recommended)
- Storage: 10GB free space for AI models
- Network: 5Mbps stable internet connection

**Software Requirements:**
- Python 3.8+
- Ollama AI 0.1.14+
- Discord.py 2.0+
- Git
- Compatible OS:
  - Linux (Ubuntu 20.04+, Debian 11+)
  - macOS (Catalina+)
  - Windows 10/11 with WSL2

#### Setup Process

1. **System Preparation**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip git

   # Install Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Bot Installation**
   ```bash
   # Clone repository
   git clone https://github.com/retrotee/botismus.git
   cd botismus

   # Setup virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate  # Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

### Configuration

#### Discord Bot Setup
1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application
3. Configure bot settings:
   - Enable required intents
   - Set permissions
   - Generate invite URL

#### Environment Configuration
Create a `.env` file in the root directory:
```
DISCORD_TOKEN=your_token_here
OLLAMA_API_URL=http://localhost:11434
```

#### AI Model Setup
```
# Pull the required Ollama model
ollama pull llama3.1
```

Note: This bot is specifically designed to work with the llama3.1 model. Other models or versions may cause unexpected behavior or reduced performance. The llama3.1 model requires:
- Minimum 8GB RAM recommended (16GB for optimal performance)
- At least 4 CPU cores recommended
- Around 8GB storage space for the model
- CUDA-capable GPU recommended but not required

If you experience performance issues, ensure your system meets these requirements and that llama3.1 is properly installed through Ollama.

Important: Make sure you're using the correct model name (llama3.1) as other versions may not provide the same functionality or performance characteristics.

### Usage Guide

#### Basic Commands
The bot responds to various command types:

1. **Channel Commands**
   - Create channels: `/create_channel name type category`
   - Delete channels: `/delete_channel name`
   - Move channels: `/move_channel name category`

2. **Role Commands**
   - Create roles: `/create_role name color permissions`
   - Modify roles: `/modify_role name property value`

3. **Bot Interaction**
   - Custom commands: `/create_command name description response`
   - Message sequences: `/sequence channel message1 message2`

#### Advanced Features

##### Personality Configuration
The bot's personality can be adjusted through:
- Response tone settings
- Sarcasm levels
- Language preferences

##### Logging System
Logs are stored in `bot.log` with configurable detail levels:
- INFO: Standard operation logs
- DEBUG: Detailed debugging information
- ERROR: Error tracking and troubleshooting

### Troubleshooting Guide

#### Common Issues

##### Ollama Connection Problems
**Symptoms:**
- AI responses not working
- Connection timeout errors

**Solutions:**
1. Check Ollama service:
   ```bash
   systemctl status ollama
   ```
2. Verify API connection:
   ```bash
   curl http://localhost:11434/api/tags
   ```
3. Restart Ollama service:
   ```bash
   systemctl restart ollama
   ```

##### Discord Integration Issues
**Symptoms:**
- Bot offline
- Command failures

**Solutions:**
1. Verify token validity
2. Check required permissions
3. Confirm intent settings

##### Performance Optimization
**Symptoms:**
- Slow responses
- High resource usage

**Solutions:**
1. Monitor system resources:
   ```bash
   htop
   ```
2. Check Ollama logs:
   ```bash
   journalctl -u ollama
   ```
3. Adjust model parameters

### License
MIT License - Copyright (c) 2024 retrotee

### Support
For support, please [open an issue](https://github.com/retrotee/botismus/issues) on GitHub.

---

## Deutsche Dokumentation

> ⚠️ **BETA-WARNUNG**: Dieser Bot befindet sich derzeit in der BETA-Phase. Rechne mit möglichen Bugs und Änderungen der Funktionen. Sei vorsichtig beim Einsatz in Produktivumgebungen.

### Einführung
Botismus ist dein KI-gesteuerter Discord-Bot. Er hilft dir dabei, deinen Server zu verwalten und bringt dabei auch noch eine eigene, freche Persönlichkeit mit! Mit der Ollama KI kann er natürlich mit dir reden und macht die Verwaltung deines Servers zum Kinderspiel.

### Was kann der Bot?
Der Bot hat echt viel drauf und ist dabei noch unterhaltsam:

#### Server-Verwaltung
- **Kanäle**: Erstellen, löschen, verschieben - alles easy!
- **Rollen**: Erstell eigene Rollen mit coolen Rechten
- **Befehle**: Bring dem Bot neue Tricks bei

#### KI-Features
- **Clever**: Versteht was du willst und antwortet sinnvoll
- **Persönlichkeit**: Hat eigenen Charakter und kann frech sein
- **Sprachen**: Spricht Deutsch und Englisch

#### Performance
- **Punktesystem**: Sammelt Punkte für gute Aktionen (+10) und verliert welche (-5) für Fehler
- **Erfolgsquote**: Behält im Auge, wie gut er arbeitet
- **Protokolle**: Schreibt auf, was er so macht (falls was schiefgeht)

### Installation

#### Was brauchst du?
Check mal, ob dein System das packt:

**Hardware:**
- RAM: Mindestens 4GB (8GB wären besser)
- CPU: 2 Kerne minimum (4 wären cool)
- Speicher: 10GB frei für die KI
- Internet: Stabile Verbindung (mindestens 5Mbps)

**Software:**
- Python 3.8 oder neuer
- Ollama AI 0.1.14+
- Discord.py 2.0+
- Git
- Eines dieser Betriebssysteme:
  - Linux (Ubuntu 20.04+, Debian 11+)
  - macOS (Catalina+)
  - Windows 10/11 mit WSL2

#### So installierst du den Bot

1. **System vorbereiten**
   ```bash
   # Für Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip git

   # Ollama installieren
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Bot installieren**
   ```bash
   # Repo klonen
   git clone https://github.com/retrotee/botismus.git
   cd botismus

   # Virtuelle Umgebung einrichten
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # oder
   .\venv\Scripts\activate  # Windows

   # Alles Nötige installieren
   pip install -r requirements.txt
   ```

### Einrichtung

#### Discord Bot erstellen
1. Geh zum [Discord Developer Portal](https://discord.com/developers/applications)
2. Klick auf "New Application"
3. Stell deinen Bot ein:
   - Aktivier die Intents
   - Setz die Rechte
   - Hol dir den Einladungslink

#### Umgebung einrichten
Erstell eine `.env`-Datei im Hauptordner:
```
DISCORD_TOKEN=dein_token_hier
OLLAMA_API_URL=http://localhost:11434
```

#### KI-Modell einrichten
```
# Das brauchst du für die KI
ollama pull llama3.1
```

Hey! Der Bot läuft nur mit llama3.1 - andere Modelle machen nur Ärger. Für llama3.1 brauchst du:
- 8GB RAM minimum (16GB wären super)
- Mindestens 4 CPU-Kerne
- Etwa 8GB Speicherplatz
- Eine CUDA-GPU wäre nice, muss aber nicht

### Probleme?
Schau mal hier:

#### Typische Probleme

##### Ollama spinnt?
**Das passiert:**
- KI antwortet nicht
- Verbindung klappt nicht

**Das hilft:**
1. Ollama-Status checken:
   ```bash
   systemctl status ollama
   ```
2. API testen:
   ```bash
   curl http://localhost:11434/api/tags
   ```
3. Ollama neustarten:
   ```bash
   systemctl restart ollama
   ```

##### Discord-Integrationsprobleme
**Symptome:**
- Bot offline
- Befehlsfehler

**Lösungen:**
1. Token-Gültigkeit überprüfen
2. Erforderliche Berechtigungen prüfen
3. Intent-Einstellungen bestätigen

##### Leistungsoptimierung
**Symptome:**
- Langsame Antworten
- Hohe Ressourcennutzung

**Lösungen:**
1. Systemressourcen überwachen:
   ```bash
   htop
   ```
2. Ollama-Protokolle prüfen:
   ```bash
   journalctl -u ollama
   ```
3. Modellparameter anpassen

### License
MIT-Lizenz - Copyright (c) 2024 retrotee

### Support
Probleme? Erstell ein [Issue](https://github.com/retrotee/botismus/issues) auf GitHub!