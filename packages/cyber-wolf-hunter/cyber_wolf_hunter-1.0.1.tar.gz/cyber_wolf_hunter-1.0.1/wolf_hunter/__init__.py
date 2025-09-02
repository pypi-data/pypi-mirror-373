"""
Cyber Wolf Hunter - Comprehensive Website Vulnerability Scanner
Developed by: S.Tamilselvan
Portfolio: https://tamilselvan-portfolio-s.web.app/
Email: tamilselvanreacher@gmail.com
GitHub: https://github.com/Tamilselvan-S-Cyber-Security
"""

from .core import WolfHunter

__version__ = "1.0.1"
__author__ = "S.Tamilselvan"
__email__ = "tamilselvanreacher@gmail.com"
__description__ = "Comprehensive website vulnerability scanner with multi-threading and HTML reporting"

# Main interface function
def wolfhunter(target_url, thread=10):
    """
    Create a new Wolf Hunter instance for vulnerability scanning
    
    Args:
        target_url (str): Target website URL to scan
        thread (int): Number of threads to use for scanning (default: 10)
    
    Returns:
        WolfHunter: Scanner instance ready for vulnerability assessment
    
    Example:
        wolf = wolfhunter("example.com", thread=100)
        results = wolf.scan()
        wolf.generate_report("report.html")
    """
    return WolfHunter(target_url, threads=thread)

# Export main classes and functions
__all__ = ['wolfhunter', 'WolfHunter']
