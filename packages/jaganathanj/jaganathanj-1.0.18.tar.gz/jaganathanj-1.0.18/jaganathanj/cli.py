# jaganathanj/cli.py

import sys
import os
from typing import List, Optional

def main():
    """Enhanced CLI entry point with better error handling and help"""
    # Import here to avoid circular imports and ensure color detection works
    import jaganathanj
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    # If no arguments, show welcome and help
    if not args:
        jaganathanj._welcome_message()
        return
    
    command = args[0].lower().strip()
    
    # Handle various help requests
    if command in ("help", "--help", "-h", "?"):
        jaganathanj.help()
        return
    
    # Handle version requests
    if command in ("version", "--version", "-v"):
        jaganathanj._print_styled(f"jaganathanj v{jaganathanj.__version__}", jaganathanj.Colors.HIGHLIGHT)
        jaganathanj._print_styled(f"by {jaganathanj.__author__} <{jaganathanj.__email__}>", jaganathanj.Colors.INFO)
        return
    
    # Command mapping for better organization - FIXED: Store function references, not calls
    command_map = {
        "about": jaganathanj.about,
        "story": jaganathanj.about,  # Alias
        "bio": jaganathanj.about,    # Alias
        
        "resume": jaganathanj.resume,
        "summary": jaganathanj.resume,  # Alias
        
        "cv": jaganathanj.cv,
        "curriculum": jaganathanj.cv,   # Alias
        "vitae": jaganathanj.cv,        # Alias
        
        "contact": jaganathanj.contact,
        "contacts": jaganathanj.contact,  # Alias
        "reach": jaganathanj.contact,     # Alias
        
        "linkedin": jaganathanj.linkedin,
        "li": jaganathanj.linkedin,       # Alias
        "professional": jaganathanj.linkedin,  # Alias
        
        "github": jaganathanj.github,
        "gh": jaganathanj.github,         # Alias
        "code": jaganathanj.github,       # Alias
        "repo": jaganathanj.github,       # Alias
        
        "portfolio": jaganathanj.portfolio,
        "port": jaganathanj.portfolio,    # Alias
        "website": jaganathanj.portfolio, # Alias
        "site": jaganathanj.portfolio,    # Alias
        
        "youtube": jaganathanj.youtube,
        "yt": jaganathanj.youtube,        # Alias
        "videos": jaganathanj.youtube,    # Alias
        "channel": jaganathanj.youtube,   # Alias
        
        "help": jaganathanj.help,
    }
    
    # Execute command if it exists
    if command in command_map:
        try:
            # FIXED: Call the function here, not in the dictionary
            command_map[command]()
        except KeyboardInterrupt:
            jaganathanj._print_styled("\n\n  Operation cancelled by user", jaganathanj.Colors.WARNING)
            sys.exit(130)  # Standard exit code for Ctrl+C
        except Exception as e:
            jaganathanj._print_styled(f"\n ERROR: An unexpected error occurred", jaganathanj.Colors.ERROR)
            jaganathanj._print_styled(f"   Details: {str(e)}", jaganathanj.Colors.MUTED)
            jaganathanj._print_styled("   Please report this issue on GitHub", jaganathanj.Colors.INFO)
            sys.exit(1)
    else:
        # Handle unknown commands with suggestions
        handle_unknown_command(command, list(command_map.keys()))

def handle_unknown_command(unknown_command: str, available_commands: List[str]) -> None:
    """Handle unknown commands with helpful suggestions"""
    import jaganathanj
    
    jaganathanj._print_styled(f"\n UNKNOWN_COMMAND: '{unknown_command}'", jaganathanj.Colors.ERROR)
    
    # Try to find similar commands using simple string matching
    suggestions = find_similar_commands(unknown_command, available_commands)
    
    if suggestions:
        jaganathanj._print_styled("\n Did you mean:", jaganathanj.Colors.WARNING)
        for suggestion in suggestions[:3]:  # Show top 3 suggestions
            jaganathanj._print_styled(f"   jaganathanj {suggestion}", jaganathanj.Colors.SUCCESS)
    
    jaganathanj._print_styled("\n Available commands:", jaganathanj.Colors.INFO)
    
    # Group commands by category for better display
    main_commands = ["about", "resume", "cv", "contact"]
    link_commands = ["linkedin", "github", "portfolio", "youtube"]
    
    jaganathanj._print_styled("   Information:", jaganathanj.Colors.SECTION)
    for cmd in main_commands:
        jaganathanj._print_styled(f"     jaganathanj {cmd}", jaganathanj.Colors.HIGHLIGHT)
    
    jaganathanj._print_styled("   Links:", jaganathanj.Colors.SECTION)
    for cmd in link_commands:
        jaganathanj._print_styled(f"     jaganathanj {cmd}", jaganathanj.Colors.HIGHLIGHT)
    
    jaganathanj._print_styled("\nRun 'jaganathanj help' for detailed information", jaganathanj.Colors.MUTED)

def find_similar_commands(target: str, commands: List[str]) -> List[str]:
    """Find commands similar to the target using simple string matching"""
    def similarity_score(cmd: str, target: str) -> float:
        """Calculate a simple similarity score between two strings"""
        # Exact match
        if cmd == target:
            return 1.0
        
        # Starts with target
        if cmd.startswith(target):
            return 0.9
        
        # Contains target
        if target in cmd:
            return 0.7
        
        # Target contains command (for short aliases)
        if cmd in target:
            return 0.6
        
        # Character overlap
        common_chars = set(cmd.lower()) & set(target.lower())
        if common_chars:
            return len(common_chars) / max(len(cmd), len(target)) * 0.5
        
        return 0.0
    
    # Score all commands and return sorted by similarity
    scored_commands = [(cmd, similarity_score(cmd, target)) for cmd in commands]
    scored_commands.sort(key=lambda x: x[1], reverse=True)
    
    # Return commands with score > 0.3
    return [cmd for cmd, score in scored_commands if score > 0.3]

if __name__ == "__main__":
    main()