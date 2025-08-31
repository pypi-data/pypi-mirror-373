# setup.py
from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys
import platform

class PostInstallCommand(install):
    """Post-installation for installation mode with enhanced styling."""
    def run(self):
        install.run(self)
        
        # Only show install message if not in quiet mode
        if not any(arg in sys.argv for arg in ['-q', '--quiet', '--silent', 'bdist_wheel', 'sdist']):
            self._show_install_message()

    def _show_install_message(self):
        """Show a beautiful welcome message after installation"""
        try:
            # Enhanced color detection for install hook
            def _supports_color_install():
                """Simplified but robust color detection for install hook"""
                # Check explicit environment variables
                if os.getenv('NO_COLOR') or os.getenv('TERM') == 'dumb':
                    return False
                
                if os.getenv('FORCE_COLOR') or os.getenv('COLORTERM'):
                    return True
                
                # Check terminal capabilities
                term = os.getenv('TERM', '').lower()
                if term in ('xterm', 'xterm-color', 'xterm-256color', 'screen', 'tmux', 'ansi'):
                    return True
                
                # Windows specific checks
                if platform.system() == 'Windows':
                    # Check for modern Windows terminals
                    if any(os.getenv(var) for var in ['WT_SESSION', 'ConEmuPID', 'CMDER_ROOT']):
                        return True
                    
                    # Windows 10+ with ANSI support
                    try:
                        import ctypes
                        kernel32 = ctypes.windll.kernel32
                        handle = kernel32.GetStdHandle(-11)
                        if handle != -1:
                            mode = ctypes.c_ulong()
                            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                                return bool(mode.value & 0x0004)
                    except:
                        pass
                    
                    return False
                
                # Unix-like: check if stdout is a TTY
                return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
            
            # Color class for install message
            if _supports_color_install():
                class InstallColors:
                    MATRIX_GREEN = '\033[38;5;40m'
                    CYBER_BLUE = '\033[38;5;51m'
                    NEON_CYAN = '\033[38;5;87m'
                    GOLD = '\033[38;5;220m'
                    WHITE = '\033[38;5;255m'
                    BOLD = '\033[1m'
                    RESET = '\033[0m'
                    
                    # Compound styles
                    HEADER = BOLD + MATRIX_GREEN
                    TITLE = BOLD + CYBER_BLUE
                    HIGHLIGHT = BOLD + GOLD
                    INFO = NEON_CYAN
                    SUCCESS = MATRIX_GREEN
            else:
                class InstallColors:
                    MATRIX_GREEN = CYBER_BLUE = NEON_CYAN = GOLD = WHITE = ''
                    BOLD = RESET = HEADER = TITLE = HIGHLIGHT = INFO = SUCCESS = ''
            
            # Get version
            version = self._get_version()
            
            # Create beautiful install message
            banner_char = '█'
            banner_width = 70
            banner_line = banner_char * banner_width
            
            install_message = f"""
{InstallColors.HEADER}{banner_line}{InstallColors.RESET}
{InstallColors.HEADER}     JAGANATHANJ PACKAGE INSTALLATION COMPLETE {InstallColors.RESET}
{InstallColors.HEADER}{banner_line}{InstallColors.RESET}

{InstallColors.SUCCESS} SYSTEM STATUS: DIGITAL IDENTITY LOADED{InstallColors.RESET}
{InstallColors.INFO} PACKAGE VERSION: {version}{InstallColors.RESET}
{InstallColors.INFO} PYTHON VERSION: {sys.version.split()[0]}{InstallColors.RESET}
{InstallColors.INFO} PLATFORM: {platform.system()} {platform.release()}{InstallColors.RESET}

{InstallColors.TITLE}INITIALIZATION COMMANDS:{InstallColors.RESET}
  {InstallColors.HIGHLIGHT}jaganathanj{InstallColors.RESET}        {InstallColors.INFO}→ Launch main interface{InstallColors.RESET}
  {InstallColors.HIGHLIGHT}jaganathanj about{InstallColors.RESET}  {InstallColors.INFO}→ Explore my story{InstallColors.RESET}
  {InstallColors.HIGHLIGHT}jaganathanj resume{InstallColors.RESET} {InstallColors.INFO}→ View professional summary{InstallColors.RESET}

{InstallColors.TITLE}PYTHON INTEGRATION:{InstallColors.RESET}
  {InstallColors.HIGHLIGHT}import jaganathanj{InstallColors.RESET}
  {InstallColors.HIGHLIGHT}jaganathanj.about(){InstallColors.RESET}

{InstallColors.SUCCESS}>_ Ready to explore my digital identity!{InstallColors.RESET}
{InstallColors.SUCCESS}>_ Thanks for pip installing me! {InstallColors.RESET}

{InstallColors.HEADER}{banner_line}{InstallColors.RESET}
"""
            print(install_message)
            
        except Exception:
            # Fallback message without colors
            fallback_message = """
================================================================================
     JAGANATHANJ PACKAGE INSTALLATION COMPLETE 
================================================================================

 Digital identity package installed successfully!

Quick start:
  jaganathanj        → Launch main interface
  jaganathanj about  → Explore my story
  jaganathanj resume → View professional summary

Python integration:
  import jaganathanj
  jaganathanj.about()

Thanks for pip installing me! 
================================================================================
"""
            print(fallback_message)

    def _get_version(self):
        """Get version from package or fallback"""
        try:
            # Try to read from __init__.py
            init_path = os.path.join(os.path.dirname(__file__), 'jaganathanj', '__init__.py')
            if os.path.exists(init_path):
                with open(init_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('__version__'):
                            return line.split('=')[1].strip().strip('"\'')
        except:
            pass
        return '1.0.18'  # Fallback version

# Read version from package
def get_version():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'jaganathanj', '__init__.py'), 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    except:
        pass
    return '1.0.18'

# Read README for long description
def get_long_description():
    try:
        readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "Personal portfolio and CLI identity package for Jaganathan J - because why settle for a boring resume when you can pip install a person?"

setup(
    name="jaganathanj",
    version=get_version(),
    description="Personal portfolio and CLI identity package for Jaganathan J, instead of countless resumes",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Jaganathan J",
    author_email="jaganathanjjds@gmail.com",
    url="https://jaganathan-j-portfolio.vercel.app/",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'jaganathanj=jaganathanj.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: System Shells",
        "Topic :: Terminals",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    keywords=[
        "resume", "portfolio", "personal-brand", "cv", "developer", "student",
        "cli", "terminal", "identity", "professional", "career"
    ],
    project_urls={
        "Homepage": "https://jaganathan-j-portfolio.vercel.app/",
        "Repository": "https://github.com/J-Jaganathan/jaganathanj-package",
        "Issues": "https://github.com/J-Jaganathan/jaganathanj-package/issues",
        "LinkedIn": "https://linkedin.com/in/jaganathan-jn",
        "YouTube": "https://youtube.com/@Tech_CrafterX",
        "Documentation": "https://github.com/J-Jaganathan/jaganathanj#readme",
    },
    cmdclass={
        'install': PostInstallCommand,
    },
    zip_safe=False,  # Allow for better debugging and development
)