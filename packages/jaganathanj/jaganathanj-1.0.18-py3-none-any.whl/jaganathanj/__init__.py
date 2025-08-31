# jaganathanj/__init__.py
"""
Jaganathan J - Personal Brand as a Python Package
==================================================

A unique way to share my professional story, achievements, and contact information.
Because why settle for a boring resume when you can pip install a person details?

Usage:
    import jaganathanj
    jaganathanj.about()     # Detailed story and background
    jaganathanj.resume()    # Quick resume summary
    jaganathanj.cv()        # Full detailed CV
    jaganathanj.contact()   # All contact information
    jaganathanj.linkedin()  # Open LinkedIn profile
"""

import webbrowser
import sys
import os
import platform
from typing import NoReturn

__version__ = "1.0.18"
__author__ = "Jaganathan J"
__email__ = "jaganathanjjds@gmail.com"

# Enhanced color detection with better Windows support
def _supports_color():
    """
    Detect if the terminal supports ANSI color codes.
    Returns True if colors are supported, False otherwise.
    """
    # Check environment variables first
    if os.getenv('NO_COLOR') or os.getenv('TERM') == 'dumb':
        return False
    
    if os.getenv('FORCE_COLOR') or os.getenv('COLORTERM'):
        return True
    
    # Check if we're in a known terminal that supports colors
    term = os.getenv('TERM', '').lower()
    colorterm = os.getenv('COLORTERM', '').lower()
    
    if colorterm in ('truecolor', '24bit', 'yes'):
        return True
    
    if term in ('xterm', 'xterm-color', 'xterm-256color', 'screen', 'screen-256color', 
                'tmux', 'tmux-256color', 'ansi', 'linux'):
        return True
    
    # Windows-specific checks with enhanced detection
    if platform.system() == 'Windows':
        # Windows Terminal and modern terminals
        if os.getenv('WT_SESSION') or os.getenv('WT_PROFILE_ID'):
            return True
        
        # Check for other modern Windows terminals
        if any(os.getenv(var) for var in ['ConEmuPID', 'CMDER_ROOT', 'TERM_PROGRAM']):
            return True
        
        # Check for Windows 10+ ANSI support
        try:
            import ctypes
            from ctypes import wintypes
            
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            
            if handle == -1:
                return False
                
            mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                if mode.value & 0x0004:
                    return True
                    
                # Try to enable VT processing
                new_mode = mode.value | 0x0004
                if kernel32.SetConsoleMode(handle, new_mode):
                    return True
        except (ImportError, OSError, AttributeError):
            pass
        
        # Fallback: assume modern Windows supports colors
        try:
            version = platform.version()
            if version and float(version.split('.')[0]) >= 10:
                return True
        except:
            pass
            
        return False
    
    # For Unix-like systems, check if stdout is a TTY
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

# Initialize color support
_COLOR_SUPPORTED = _supports_color()

# Professional Matrix/Hacker-inspired color scheme
class Colors:
    if _COLOR_SUPPORTED:
        # Matrix/Cyber theme colors
        MATRIX_GREEN = '\033[38;5;40m'      # Bright matrix green
        CYBER_BLUE = '\033[38;5;51m'        # Electric blue
        NEON_CYAN = '\033[38;5;87m'         # Bright cyan
        HACK_ORANGE = '\033[38;5;208m'      # Warning orange
        BLOOD_RED = '\033[38;5;196m'        # Alert red
        GOLD = '\033[38;5;220m'             # Achievement gold
        SILVER = '\033[38;5;250m'           # Secondary text
        WHITE = '\033[38;5;255m'            # Primary text
        DIM_GREEN = '\033[38;5;28m'         # Subdued green
        PURPLE = '\033[38;5;141m'           # Accent purple
        
        # Text formatting
        BOLD = '\033[1m'
        DIM = '\033[2m'
        ITALIC = '\033[3m'
        UNDERLINE = '\033[4m'
        BLINK = '\033[5m'
        REVERSE = '\033[7m'
        STRIKE = '\033[9m'
        
        # Reset
        RESET = '\033[0m'
        
        # Compound styles for specific uses
        HEADER = BOLD + MATRIX_GREEN
        TITLE = BOLD + CYBER_BLUE
        SECTION = BOLD + NEON_CYAN
        WARNING = BOLD + HACK_ORANGE
        ERROR = BOLD + BLOOD_RED
        SUCCESS = BOLD + MATRIX_GREEN
        INFO = CYBER_BLUE
        MUTED = DIM + SILVER
        ACCENT = PURPLE
        HIGHLIGHT = BOLD + GOLD
    else:
        # No color fallback - all empty strings
        MATRIX_GREEN = CYBER_BLUE = NEON_CYAN = HACK_ORANGE = BLOOD_RED = ''
        GOLD = SILVER = WHITE = DIM_GREEN = PURPLE = ''
        BOLD = DIM = ITALIC = UNDERLINE = BLINK = REVERSE = STRIKE = ''
        RESET = HEADER = TITLE = SECTION = WARNING = ERROR = ''
        SUCCESS = INFO = MUTED = ACCENT = HIGHLIGHT = ''

def _print_styled(text: str, style: str = '', end: str = '\n') -> None:
    """Print text with style formatting, ensuring proper reset"""
    if style:
        print(f"{style}{text}{Colors.RESET}", end=end)
    else:
        print(text, end=end)

def _create_banner(text: str, width: int = 80, char: str = '═') -> str:
    """Create a professional banner with specified character"""
    if len(text) >= width - 4:
        return f"{char * width}"
    
    padding = (width - len(text) - 2) // 2
    return f"{char * padding} {text} {char * (width - padding - len(text) - 2)}"

def _create_box(lines: list, width: int = 80) -> str:
    """Create a bordered box containing the given lines"""
    top = f"╔{'═' * (width - 2)}╗"
    bottom = f"╚{'═' * (width - 2)}╝"
    
    boxed_lines = [top]
    for line in lines:
        # Handle long lines by truncating or wrapping
        if len(line) > width - 4:
            line = line[:width - 7] + "..."
        padding = width - len(line) - 4
        boxed_lines.append(f"║ {line}{' ' * padding} ║")
    boxed_lines.append(bottom)
    
    return '\n'.join(boxed_lines)

def _welcome_message() -> None:
    """Display enhanced welcome message when package is used as CLI"""
    welcome_lines = [
        "",
        f"{Colors.HEADER} JAGANATHANJ DIGITAL IDENTITY INTERFACE {Colors.RESET}",
        "",
        f"{Colors.SUCCESS}>_ PERSONAL PACKAGE READY{Colors.RESET}",
        f"{Colors.INFO}>_ TERMINAL INTERFACE ACTIVE{Colors.RESET}",
        f"{Colors.MUTED}>_ VERSION {__version__} | PYTHON {sys.version.split()[0]}{Colors.RESET}",
        "",
        f"{Colors.SECTION}AVAILABLE COMMANDS:{Colors.RESET}",
        f"  {Colors.HIGHLIGHT}jaganathanj help{Colors.RESET}      {Colors.MUTED}→ Show all available commands{Colors.RESET}",
        f"  {Colors.HIGHLIGHT}jaganathanj about{Colors.RESET}     {Colors.MUTED}→ Deep dive into my journey{Colors.RESET}",
        f"  {Colors.HIGHLIGHT}jaganathanj resume{Colors.RESET}    {Colors.MUTED}→ Professional summary{Colors.RESET}",
        f"  {Colors.HIGHLIGHT}jaganathanj cv{Colors.RESET}        {Colors.MUTED}→ Complete curriculum vitae{Colors.RESET}",
        f"  {Colors.HIGHLIGHT}jaganathanj contact{Colors.RESET}   {Colors.MUTED}→ Connection protocols{Colors.RESET}",
        "",
        f"{Colors.WARNING}SYSTEM REQUIREMENTS: Python 3.6+ | ANSI Terminal{Colors.RESET}",
        "",
        f"{Colors.SUCCESS}Tip: Run 'jaganathanj help' to explore all commands!{Colors.RESET}",
        "",
        f"{Colors.ACCENT} Coming Soon: Local AI integration {Colors.RESET}",
        f"{Colors.MUTED}   → Offline chat, code review, and reasoning modules{Colors.RESET}",
        ""
    ]
    
    banner = _create_banner("DIGITAL IDENTITY INTERFACE", char='═')
    _print_styled(f"\n{banner}", Colors.HEADER)
    
    for line in welcome_lines:
        print(line)
    
    _print_styled(_create_banner("", char='═'), Colors.HEADER)

def about() -> None:
    """Display detailed about me story with enhanced formatting"""
    # Header
    _print_styled(_create_banner("JAGANATHAN J :: DIGITAL BIOGRAPHY", char='█'), Colors.HEADER)
    print()
    
    # Introduction with style
    _print_styled(">>> INITIALIZING PERSONAL NARRATIVE...", Colors.INFO)
    _print_styled(">>> LOADING PROFESSIONAL MATRIX...", Colors.INFO)
    _print_styled(">>> STATUS: READY", Colors.SUCCESS)
    print()
    
    sections = [
        {
            "title": "THE ANOMALY",
            "content": """Hey there! You just imported me as a Python package. That's not normal, and neither am I.

Most people put their story on LinkedIn. I built mine into code you can pip install.
Why? Because everything I do reflects how I think differently about problems.

At the time of creating this package, I'm in my final year of Computer Science and 
Engineering at SRM Easwari Engineering College, Chennai, with a CGPA of 8.89/10. 
I've served as the class representative for three consecutive semesters — a role I 
stepped into after volunteering and was entrusted with by faculty."""
        },
        {
            "title": "CRITICAL SYSTEM INTERVENTION",
            "content": """The weekend before the Computer Networks exam? 60+ classmates panicking about
12 Cisco Packet Tracer experiments they couldn't grasp. RIP protocols, DHCP configs,
static routing - technical nightmares that make or break your semester.

I had one week. I self-mastered every single experiment. Then I did something that
defined who I am: I called a 6-hour Google Meet session. Real-time doubt clearing.
Live problem-solving. No slides, just pure technical knowledge transfer.

RESULT: 100% pass rate. Every single person passed the next day.

That's when I realized - my superpower isn't just solving problems. It's scaling
solutions to lift entire communities."""
        },
        {
            "title": "INNOVATION PROTOCOLS",
            "content": """I don't just code. I patent ideas. Filed "202441089112 A" for a SARIMA-based GPS
alternative using machine learning time series prediction. When GPS fails, temporal
mapping takes over. Infrastructure independence through intelligent prediction.

I don't just learn. I teach. My YouTube channel "Tech CrafterX" hit 667% subscriber
growth in 15 days. Created 33-minute cloud computing tutorials that 150+ students
across multiple sections now use. Not because I'm chasing fame - because knowledge
should elevate everyone."""
        },
        {
            "title": "SYSTEM ARCHITECTURE",
            "content": """I don't just build projects. I build experiences. Architected a real-time Firebase
note taking app as the sole developer among 60 students. While others built Udemy clones,
I delivered a live demo where the entire class interacted with disappearing messages
in real-time. Perfect score. Faculty recognition. Production deployment.

During my 6th semester, I noticed that our mini-project documentation was fragmented 
and unclear. So, I redesigned it — structure, formatting, clarity — and proposed a cleaner 
format. It was approved by every project guide and adopted across the department. 
Hundreds of students and faculty now use it."""
        },
        {
            "title": "CONTINUOUS INTEGRATION",
            "content": """Do I solve coding problems regularly? Absolutely. Sometimes it's LeetCode. Other 
times it's system design, data structures, or whatever sparks my curiosity that week. 
The topics and intensity vary — but the habit stays.

I don't follow a strict #100DaysOfCode routine. For me, problem-solving is less about 
streaks and more about staying mentally sharp, building real intuition, and applying 
what I learn in meaningful ways."""
        },
        {
            "title": "ORIGIN STORY",
            "content": """It started early. In 6th grade, I built a racing robot from scratch using a 12V battery, 
IR sensors, motors, and more — and won my first competition. That experience wired 
something permanent into me: the thrill of building, solving, and improving.

I've been committed to fitness since 6th grade — building physical strength as a 
foundation for mental resilience. You need both when you're debugging at 2 AM or guiding 
70 classmates through TCP/IP right before an exam with no margin for error."""
        },
        {
            "title": "ERROR HANDLING & RECOVERY",
            "content": """Setbacks? I've had them. A gaming addiction during school nearly knocked me off course. 
But I turned that phase into fuel for a comeback. Through focus and discipline, 
I scored 191/200 in my Higher Secondary exams and topped my school in Mathematics with 99%.

College came with its own challenges — but I stayed sharp. Every stumble has been a step 
forward. Growth, for me, has always been intentional — mentally, physically, and technically."""
        },
        {
            "title": "ACHIEVEMENTS UNLOCKED",
            "content": """• NPTEL Gold Medal in Cloud Computing (90% with 2 days prep)
• IIT Madras Shaastra 2025 Hackathon Finalist
• MongoDB Certified Student Developer
• Winner of Pitch Perfect Competition

When professors face cryptic errors in legacy C programs, they reach out to me.  
When classmates can't rely on the manual or faculty, they rely on my explanation.  
When precision and last-minute fixes are the only option — I show up."""
        },
        {
            "title": "FUTURE DEPLOYMENT",
            "content": """I'm not just looking for a job. I'm building a career in LLM, Data Science, AI/ML 
Engineering, or Full-Stack Development where I can create scalable impact. Where my 
obsession with understanding systems deeply can solve real problems for real people.

I want to work with teams that appreciate someone who learns fast, teaches others,
and sees opportunities where others see obstacles. Someone who files patents, builds
viral educational content, and turns academic crises into learning victories."""
        }
    ]
    
    for section in sections:
        _print_styled(f"\n[{section['title']}]", Colors.SECTION)
        _print_styled("─" * 50, Colors.MUTED)
        print(section['content'])
    
    # Contact footer
    print()
    _print_styled("CONTACT_PROTOCOLS:", Colors.SECTION)
    _print_styled("├─ PRIMARY: jaganathanjjds@gmail.com", Colors.INFO)
    _print_styled("├─ GITHUB: https://github.com/J-Jaganathan", Colors.INFO)
    _print_styled("├─ LINKEDIN: https://linkedin.com/in/jaganathan-jn", Colors.INFO)
    _print_styled("├─ YOUTUBE: https://youtube.com/@Tech_CrafterX", Colors.INFO)
    _print_styled("└─ PORTFOLIO: https://jaganathan-j-portfolio.vercel.app/", Colors.INFO)
    
    print()
    _print_styled("Even this format - packaging myself as importable code - reflects how I approach", Colors.MUTED)
    _print_styled("everything. Unconventional, functional, and memorable.", Colors.MUTED)
    print()
    _print_styled("Welcome to my story. Thanks for pip installing me.", Colors.SUCCESS)
    _print_styled("- Jaganathan J", Colors.HIGHLIGHT)
    
    _print_styled(_create_banner("END_OF_TRANSMISSION", char='█'), Colors.HEADER)

def resume() -> None:
    """Display quick resume summary with professional formatting"""
    _print_styled(_create_banner("JAGANATHAN J :: EXECUTIVE_SUMMARY", char='▓'), Colors.TITLE)
    print()
    
    sections = [
        (" EDUCATION", [
            "B.Tech Computer Science & Engineering | SRM Easwari Engineering College",
            "CGPA: 8.89/10 | Expected Graduation: June 2026",
            "Class Representative (3 consecutive semesters)"
        ]),
        (" EXPERIENCE", [
            " Content Creator & Technical Instructor – YouTube (Tech_CrafterX)",
            "   → 667%_ subscriber growth | 500+ views | 150+ student adoption",
            "",
            " Data Science Intern – Personifwy (Nov–Dec 2024, Remote)",
            "   → ML model development | 15%_ accuracy improvement",
            "",
            " Data Science Intern – Adverk Technologies (June–July 2023)",
            "   → Biomedical ML | Stroke & breast cancer prediction models",
            "",
            " Technical Mentor – Computer Networks Lab",
            "   → 70+ students trained | 100% pass rate achieved"
        ]),
        (" KEY_PROJECTS", [
            "• Real-time Chat Application (Firebase, JavaScript) - Perfect score",
            "• Network Communication System (Java, Socket Programming)",
            "• Voice-Controlled Notes App (JavaScript, Web Speech API) - 95%_ accuracy",
            "• Patent Filed: GPS Alternative using SARIMA Model (App. No. 202441089112 A)"
        ]),
        (" ACHIEVEMENTS", [
            "• IIT Madras Shaastra 2025 Hackathon Finalist",
            "• NPTEL Gold Medal - Cloud Computing (90%)",
            "• MongoDB Certified Student Developer",
            "• Winner - Pitch Perfect Competition"
        ]),
        (" TECH_STACK", [
            "Languages: Python, Java, JavaScript, C++, HTML/CSS",
            "Cloud: AWS, Firebase, MongoDB, SQL",
            "Tools: VS Code, GitHub, Android Studio",
            "Specialties: Machine Learning, NLP, System Architecture"
        ])
    ]
    
    for title, items in sections:
        _print_styled(f"\n{title}", Colors.SECTION)
        _print_styled("─" * 40, Colors.MUTED)
        for item in items:
            if item.startswith("   →"):
                _print_styled(item, Colors.INFO)
            elif item.startswith("•"):
                _print_styled(item, Colors.SUCCESS)
            else:
                print(item)
    
    print()
    _print_styled(" CONTACT: jaganathanjjds@gmail.com", Colors.HIGHLIGHT)
    _print_styled(" PORTFOLIO: https://jaganathan-j-portfolio.vercel.app/", Colors.INFO)
    
    print()
    _print_styled("Run jaganathanj.about() for the complete narrative!", Colors.WARNING)
    _print_styled(_create_banner("", char='▓'), Colors.TITLE)

def cv() -> None:
    """Display full detailed CV with enhanced professional formatting"""
    _print_styled(_create_banner("JAGANATHAN J :: CURRICULUM_VITAE", char='▓'), Colors.TITLE)
    print()
    
    # Personal Info Box
    personal_info = [
        "Name: Jaganathan J",
        "Email: jaganathanjjds@gmail.com",
        "Portfolio: https://jaganathan-j-portfolio.vercel.app/",
        "GitHub: https://github.com/J-Jaganathan",
        "LinkedIn: https://linkedin.com/in/jaganathan-jn",
        "YouTube: https://youtube.com/@Tech_CrafterX"
    ]
    
    _print_styled("PERSONAL_INFORMATION", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    for info in personal_info:
        _print_styled(f"  {info}", Colors.INFO)
    
    # Executive Summary
    _print_styled("\nEXECUTIVE_SUMMARY", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    print("""Self-directed computer science engineer with patent-pending innovation, 500+ educational
video views, and a track record of 100% peer success rates in critical technical
interventions. Demonstrated ability to master complex systems independently, scale
educational impact across 150+ students, and build production-ready applications.""")
    
    # Education
    _print_styled("\nEDUCATION", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    _print_styled("Bachelor of Engineering - Computer Science & Engineering (2022-2026)", Colors.SUCCESS)
    print("SRM Easwari Engineering College, Chennai")
    _print_styled("CGPA: 8.89/10", Colors.HIGHLIGHT)
    print("• Class Representative (3 consecutive semesters)")
    print("• Patent Application Filed: GPS Alternative System (App. No. 202441089112 A)")
    print("• Perfect Academic Record: Zero failures from grades 1-12")
    
    # Professional Experience
    _print_styled("\nPROFESSIONAL_EXPERIENCE", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    
    experiences = [
        {
            "title": "Content Creator & Technical Instructor (Sep 2024 – Present)",
            "company": "YouTube Channel - Tech CrafterX | Remote",
            "details": [
                "• Achieved 667%_ subscriber growth in 15 days with 500+ views through AWS tutorials",
                "• Produced 3+ comprehensive tutorials on Cloud Computing and Hadoop",
                "• Created content adopted by 150+ students across multiple sections"
            ]
        },
        {
            "title": "Data Science Intern (Nov 2024 – Dec 2024)",
            "company": "Personifwy | Remote, Bengaluru",
            "details": [
                "• Applied Python, ML, and statistical analysis to real-world projects",
                "• Improved model accuracy by 15% through advanced preprocessing techniques"
            ]
        },
        {
            "title": "Technical Mentor (Nov 2024)",
            "company": "Computer Networks Lab, SRM Easwari Engineering College",
            "details": [
                "• Conducted intensive crisis session for 70+ students before critical exam",
                "• Achieved 100%_ class pass rate through real-time doubt clearing sessions"
            ]
        },
        {
            "title": "Data Science Intern (Jun 2023 – Jul 2023)",
            "company": "Adverk Technologies | Remote, Bengaluru",
            "details": [
                "• Built foundational ML pipelines for Breast Cancer and Stroke Prediction",
                "• Explored data preprocessing and binary classification using health datasets"
            ]
        }
    ]
    
    for exp in experiences:
        _print_styled(f"\n{exp['title']}", Colors.SUCCESS)
        _print_styled(exp['company'], Colors.INFO)
        for detail in exp['details']:
            print(detail)
    
    # Technical Projects
    _print_styled("\nTECHNICAL_PROJECTS", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    
    projects = [
        "Grocery Helper Application | Firebase, JavaScript, HTML/CSS",
        "• Real-time note-taking system as sole developer among 60 students",
        "• Perfect score with faculty recognition",
        "",
        "Network Communication System | Java, ServerSocket Programming", 
        "• Custom laptop-to-laptop communication protocol",
        "• Self-taught Java for project requirements",
        "",
        "Voice-Controlled Notes Application | Java, Web Speech API",
        "• 95% voice-to-text accuracy with accessibility features",
        "",
        "NLP Expression Evaluator | Prolog",
        "• Intelligent text parser for arithmetic expressions"
    ]
    
    for project in projects:
        if project.startswith("•"):
            _print_styled(project, Colors.INFO)
        elif project and not project.startswith(" "):
            _print_styled(project, Colors.SUCCESS)
        else:
            print(project)
    
    # Research & IP
    _print_styled("\nRESEARCH & INTELLECTUAL_PROPERTY", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    _print_styled("Patent Application - Temporal Mapping Technology (Nov 2024)", Colors.HIGHLIGHT)
    _print_styled("Application No.: 202441089112 A", Colors.INFO)
    print("• Developed SARIMA-based GPS alternative using ML time-series prediction")
    print("• Addresses critical infrastructure dependency in location services")
    print("• Prototype development in progress for backup navigation systems")
    
    # Certifications
    _print_styled("\nCERTIFICATIONS & ACHIEVEMENTS", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    achievements = [
        "• NPTEL Cloud Computing: 90% (Gold Medal) - 2024",
        "• NPTEL Industry 4.0 & IIoT: 80% (Silver Medal) - 2023",
        "• MongoDB Student Developer Course - Certified (Jul 2024)",
        "• Winner - Pitch Perfect Competition (Nov 2023)",
        "• Finalist - IIT Madras Shaastra 2025 Hackathon (Jan 2025)"
    ]
    
    for achievement in achievements:
        _print_styled(achievement, Colors.SUCCESS)
    
    # Technical Expertise
    _print_styled("\nTECHNICAL_EXPERTISE", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    tech_skills = [
        "Programming Languages: Python, Java, JavaScript, C++, HTML/CSS, C, MATLAB",
        "Cloud & Databases: AWS, Firebase, MongoDB, MySQL",
        "Development Tools: Git, VS Code, Android Studio, Cisco Packet Tracer",
        "Data Science: NumPy, Pandas, Matplotlib, Scikit-learn",
        "Network Protocols: TCP/IP, RIP, OSPF, DHCP, Static/Dynamic Routing",
        "Specialties: Machine Learning, NLP, System Architecture, Socket Programming"
    ]
    
    for skill in tech_skills:
        _print_styled(f"  {skill}", Colors.INFO)
    
    _print_styled(f"\n{_create_banner('', char='▓')}", Colors.TITLE)

def contact() -> None:
    """Display all contact information with professional styling"""
    _print_styled(_create_banner("JAGANATHAN J :: CONTACT_PROTOCOLS", char='▓'), Colors.TITLE)
    print()
    
    # Contact sections with icons and styling
    contact_sections = [
        (" PRIMARY_COMMUNICATION", [
            "jaganathanjjds@gmail.com",
            "310622104064@eec.srmrmp.edu.in"
        ]),
        (" PROFESSIONAL_NETWORKS", [
            "LinkedIn: https://linkedin.com/in/jaganathan-jn",
            "GitHub: https://github.com/J-Jaganathan",
            "Portfolio: https://jaganathan-j-portfolio.vercel.app/"
        ]),
        (" CONTENT_CHANNELS", [
            "YouTube: https://youtube.com/@Tech_CrafterX",
            "Focus: Cloud Computing, Data Science tutorials"
        ]),
        (" AVAILABILITY_STATUS", [
            "Status: Final year B.Tech student (Graduating June 2026)",
            "Seeking: Full-time roles, internships, research collaborations",
            "Interests: Data Science, AI/ML Engineering, Full-Stack Development"
        ]),
        (" COLLABORATION_TARGETS", [
            "• Teams that value rapid learning and knowledge sharing",
            "• Projects involving scalable system architecture",
            "• Opportunities to create educational and social impact",
            "• Roles where I can solve complex technical challenges"
        ])
    ]
    
    for title, items in contact_sections:
        _print_styled(f"\n{title}", Colors.SECTION)
        _print_styled("─" * 50, Colors.MUTED)
        for item in items:
            if item.startswith("•"):
                _print_styled(f"  {item}", Colors.SUCCESS)
            elif ":" in item and not item.startswith("Status:"):
                parts = item.split(": ", 1)
                _print_styled(f"  {parts[0]}: ", Colors.INFO, end="")
                _print_styled(parts[1], Colors.HIGHLIGHT)
            else:
                _print_styled(f"  {item}", Colors.INFO)
    
    print()
    _print_styled(" RESPONSE_TIME: Usually within 24 hours", Colors.WARNING)
    print()
    _print_styled("Feel free to reach out for collaborations, opportunities, or tech discussions!", Colors.SUCCESS)
    
    _print_styled(f"\n{_create_banner('', char='▓')}", Colors.TITLE)

def linkedin() -> None:
    """Open LinkedIn profile in browser with styled output"""
    linkedin_url = "https://linkedin.com/in/jaganathan-jn"
    try:
        webbrowser.open(linkedin_url)
        _print_styled("\n LAUNCHING PROFESSIONAL PROFILE...", Colors.INFO)
        _print_styled(f"   URL: {linkedin_url}", Colors.HIGHLIGHT)
        _print_styled("   STATUS: Browser launched successfully", Colors.SUCCESS)
        _print_styled("   If browser didn't open, copy the URL above.", Colors.MUTED)
    except Exception as e:
        _print_styled(f"\n BROWSER_ERROR: Could not launch browser", Colors.ERROR)
        _print_styled(f"   Please visit: {linkedin_url}", Colors.WARNING)

def portfolio() -> None:
    """Open portfolio website in browser with styled output"""
    portfolio_url = "https://jaganathan-j-portfolio.vercel.app/"
    try:
        webbrowser.open(portfolio_url)
        _print_styled("\n LAUNCHING DIGITAL PORTFOLIO...", Colors.INFO)
        _print_styled(f"   URL: {portfolio_url}", Colors.HIGHLIGHT)
        _print_styled("   STATUS: Portfolio interface loaded", Colors.SUCCESS)
        _print_styled("   Explore my projects and achievements!", Colors.MUTED)
    except Exception as e:
        _print_styled(f"\n BROWSER_ERROR: Could not launch browser", Colors.ERROR)
        _print_styled(f"   Please visit: {portfolio_url}", Colors.WARNING)

def youtube() -> None:
    """Open YouTube channel in browser with styled output"""
    youtube_url = "https://youtube.com/@Tech_CrafterX"
    try:
        webbrowser.open(youtube_url)
        _print_styled("\n LAUNCHING CONTENT CHANNEL...", Colors.INFO)
        _print_styled(f"   URL: {youtube_url}", Colors.HIGHLIGHT)
        _print_styled("   STATUS: Channel access established", Colors.SUCCESS)
        _print_styled("   Subscribe for Cloud Computing, and Data Science tutorials!", Colors.WARNING)
    except Exception as e:
        _print_styled(f"\n BROWSER_ERROR: Could not launch browser", Colors.ERROR)
        _print_styled(f"   Please visit: {youtube_url}", Colors.WARNING)

def help() -> None:
    """Display help information with enhanced styling"""
    _print_styled(_create_banner("JAGANATHANJ :: SYSTEM_HELP", char='▓'), Colors.TITLE)
    print()
    
    # Highlight Help first
    _print_styled("CORE COMMANDS:", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    core_commands = [
        ("jaganathanj help",    "Show this help interface"),
        ("jaganathanj about",   "Detailed personal story and journey"),
        ("jaganathanj resume",  "Quick professional summary"), 
        ("jaganathanj cv",      "Full detailed curriculum vitae"),
        ("jaganathanj contact", "Complete contact information"),
    ]
    for cmd, desc in core_commands:
        _print_styled(f"  {cmd:<20}", Colors.HIGHLIGHT, end="")
        _print_styled(f"→ {desc}", Colors.MUTED)

    # External links
    print()
    _print_styled("EXTERNAL LINKS:", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    external_commands = [
        ("jaganathanj linkedin",  "Open LinkedIn profile in your default browser"),
        ("jaganathanj github",    "Open GitHub profile in your default browser"),
        ("jaganathanj portfolio", "Open portfolio website in your default browser"),
        ("jaganathanj youtube",   "Open YouTube channel in your default browser"),
    ]
    for cmd, desc in external_commands:
        _print_styled(f"  {cmd:<20}", Colors.HIGHLIGHT, end="")
        _print_styled(f"→ {desc}", Colors.MUTED)

    # Future AI section (teaser)
    print()
    _print_styled("COMING SOON – AI FEATURES:", Colors.SECTION)
    _print_styled("─" * 50, Colors.MUTED)
    ai_teasers = [
        ("jaganathanj -ai enable",     "Activate local AI assistant"),
        ("private-ai-j",     "Launch offline AI chat & code review UI"),
    ]
    for cmd, desc in ai_teasers:
        _print_styled(f"  {cmd:<20}", Colors.ACCENT, end="")
        _print_styled(f"→ {desc}", Colors.MUTED)

    # Package info
    print()
    _print_styled("PACKAGE_INFO:", Colors.SECTION)
    _print_styled("─" * 20, Colors.MUTED)
    _print_styled(f"  Version: {__version__}", Colors.INFO)
    _print_styled(f"  Author: {__author__}", Colors.INFO)
    _print_styled(f"  Email: {__email__}", Colors.INFO)
    _print_styled(f"  Python: {sys.version.split()[0]}", Colors.INFO)
    
    print()
    _print_styled("GETTING_STARTED:", Colors.WARNING)
    _print_styled("1. Try 'jaganathanj about' to begin exploration", Colors.SUCCESS)
    _print_styled("2. Watch for AI features in upcoming releases ", Colors.ACCENT)
    
    _print_styled(f"\n{_create_banner('', char='▓')}", Colors.TITLE)


def github() -> None:
    """Open GitHub profile in browser with styled output"""
    github_url = "https://github.com/J-Jaganathan"
    try:
        webbrowser.open(github_url)
        _print_styled("\n LAUNCHING CODE REPOSITORY...", Colors.INFO)
        _print_styled(f"   URL: {github_url}", Colors.HIGHLIGHT)
        _print_styled("   STATUS: Repository access granted", Colors.SUCCESS)
        _print_styled("   Check out my repositories and contributions!", Colors.MUTED)
    except Exception as e:
        _print_styled(f"\n BROWSER_ERROR: Could not launch browser", Colors.ERROR)
        _print_styled(f"   Please visit: {github_url}", Colors.WARNING)
        
# Make functions available at package level
__all__ = [
    'about', 'resume', 'cv', 'contact', 'linkedin', 
    'github', 'portfolio', 'youtube', 'help'
]
