"""
SEH - Safe Ethical Hacking Library
A Python library for learning penetration testing, network analysis,
web scraping, and ethical hacking in a safe and educational environment.

Includes tools for:
- Web vulnerability testing (XSS, SQLi, CSRF, LFI, SSRF, Open Redirect, etc.)
- API security testing and fuzzing
- Network analysis, sniffing, MITM simulations
- Web scraping and analysis
- Authentication and session testing
- Utility tools for passwords, user agents, and mock databases
All tools are async and safe for educational purposes.
"""

# ----- Network & Packet Analysis -----
from .network import NetworkSimulator, PacketAnalyzer, TrafficPatternAnalyzer, PacketInjectionSimulator, VPNDetection, ARPSpoofSimulator, DNSSpoofSimulator

# ----- Attacks & Exploits -----
from .attacks import (
    BruteForce, SQLInjection, XSS, CSRF, DirectoryTraversal, LFI,
    CommandInjection, RemoteFileUpload, SSRF, OpenRedirect, HTTPParameterPollution,
    BlindSQLi, TimeBasedSQLi, UnionSQLi, BooleanSQLi, NoSQLInjection,
    OAuthMisconfiguration, JWTChecker, PasswordResetTester
)

# ----- Web Security & Scraping -----
from .web import (
    WebScraper, HeaderAnalyzer, FormAnalyzer, LoginTester,
    APIEndpointTester, RateLimitTester, JSONResponseAnalyzer, WAFDetector,
    CORSTester, SubdomainTakeoverDetector, BrokenAuthTester,
    SecurityHeadersChecker, OpenRedirectAdvanced, XXETester, GraphQLAnalyzer
)

# ----- Sniffing & MITM -----
from .sniffing import PacketSniffer, MITMSimulator

# ----- PenTest & Network Tools -----
from .pentest_tools import PortScanner, SubdomainFinder, APIFuzzer, CookieAnalyzer, RateLimitBypassTester, APIKeyExposureChecker

# ----- Reporting -----
from .reporting import Report

# ----- Utilities -----
from .utils import PasswordGenerator, RandomUserAgent, CAPTCHASimulator, TwoFactorAuthTester, TLSChecker, RateLimiterBypass, DOMHijackingDetector, ReferrerPolicyAnalyzer

# ----- Databases -----
from .databases import MockDatabase
