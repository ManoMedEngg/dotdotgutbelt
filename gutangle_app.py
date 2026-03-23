"""
GutAngle — GutBelt Companion App
Full PyQt6 desktop application for posture + EGG monitoring.

Dependencies:
    pip install PyQt6 pyqtgraph bleak numpy

Run:
    python gutangle_app.py
"""

import sys
import math
import random
import asyncio
import threading
import time
from datetime import datetime, timedelta
from collections import deque

import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTabWidget, QFrame, QScrollArea,
    QSlider, QCheckBox, QGroupBox, QSizePolicy, QSpacerItem,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QPoint, QSize, QObject, pyqtProperty,
    QParallelAnimationGroup, QSequentialAnimationGroup
)
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QFontDatabase, QPen, QBrush,
    QLinearGradient, QRadialGradient, QPainterPath, QPixmap,
    QIcon, QPalette, QCursor, QConicalGradient
)

try:
    import pyqtgraph as pg
    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False

try:
    from bleak import BleakScanner, BleakClient
    HAS_BLEAK = True
except ImportError:
    HAS_BLEAK = False


# ─────────────────────────────────────────────
#  THEME & PALETTE
# ─────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg":          "#0A0F1E",
        "bg2":         "#111827",
        "surface":     "#1C2333",
        "surface2":    "#252D3D",
        "border":      "#2E3A50",
        "accent":      "#00D4AA",
        "accent2":     "#0099FF",
        "accent3":     "#FF6B6B",
        "text":        "#E8EDF5",
        "text2":       "#8B95A8",
        "text3":       "#4A5568",
        "success":     "#22C55E",
        "warning":     "#F59E0B",
        "danger":      "#EF4444",
        "ripple":      "#00D4AA",
        "graph_egg":   "#00D4AA",
        "graph_pos":   "#0099FF",
        "graph_grid":  "#1C2333",
    },
    "light": {
        "bg":          "#F0F4F8",
        "bg2":         "#FFFFFF",
        "surface":     "#FFFFFF",
        "surface2":    "#EBF0F7",
        "border":      "#D1DBE8",
        "accent":      "#008B70",
        "accent2":     "#0066CC",
        "accent3":     "#CC3333",
        "text":        "#0F172A",
        "text2":       "#475569",
        "text3":       "#94A3B8",
        "success":     "#16A34A",
        "warning":     "#D97706",
        "danger":      "#DC2626",
        "ripple":      "#008B70",
        "graph_egg":   "#008B70",
        "graph_pos":   "#0066CC",
        "graph_grid":  "#EBF0F7",
    }
}

current_theme = "dark"

def T(key):
    return THEMES[current_theme][key]


# ─────────────────────────────────────────────
#  LOCALIZATION
# ─────────────────────────────────────────────
LANGUAGES = {
    "English": {
        "app_name": "GutAngle",
        "tagline": "Posture & Gut Health Monitor",
        "sign_in": "Sign In",
        "sign_up": "Sign Up",
        "username": "Username / Email",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "full_name": "Full Name",
        "forgot_password": "Forgot Password?",
        "reset_password": "Reset Password",
        "email_hint": "Enter your email to reset",
        "login_btn": "Login",
        "register_btn": "Create Account",
        "send_reset": "Send Reset Link",
        "back": "Back",
        "bluetooth": "Bluetooth",
        "scan": "Scan for Devices",
        "scanning": "Scanning...",
        "connected": "Connected",
        "disconnected": "Disconnected",
        "device_name": "GutBelt",
        "dashboard": "Dashboard",
        "egg_signals": "EGG Signals",
        "posture": "Posture",
        "history": "History",
        "settings": "Settings",
        "battery": "Battery",
        "posture_good": "Posture: Good",
        "posture_fair": "Posture: Fair",
        "posture_poor": "Posture: Poor",
        "digestion_normal": "Digestion: Normal",
        "digestion_active": "Digestion: Active",
        "digestion_low": "Digestion: Low",
        "theme": "Theme",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode",
        "language": "Language",
        "change_password": "Change Password",
        "current_password": "Current Password",
        "new_password": "New Password",
        "save": "Save Changes",
        "week": "Week",
        "month": "Month",
        "no_data": "No data available",
        "connect_device": "Connect GutBelt",
        "device_info": "Device Information",
        "firmware": "Firmware v2.1.3",
        "signal_strength": "Signal",
        "logout": "Logout",
    },
    "Tamil": {
        "app_name": "GutAngle",
        "tagline": "தோரணை & குடல் ஆரோக்கிய கண்காணிப்பு",
        "sign_in": "உள்நுழைவு",
        "sign_up": "பதிவு செய்",
        "username": "பயனர்பெயர் / மின்னஞ்சல்",
        "password": "கடவுச்சொல்",
        "confirm_password": "கடவுச்சொல்லை உறுதிப்படுத்து",
        "full_name": "முழு பெயர்",
        "forgot_password": "கடவுச்சொல் மறந்துவிட்டதா?",
        "reset_password": "கடவுச்சொல்லை மீட்டமை",
        "email_hint": "மீட்டமைக்க மின்னஞ்சல் உள்ளிடவும்",
        "login_btn": "உள்நுழை",
        "register_btn": "கணக்கை உருவாக்கு",
        "send_reset": "மீட்டமை இணைப்பை அனுப்பு",
        "back": "பின்",
        "bluetooth": "புளூடூத்",
        "scan": "சாதனங்களை தேடு",
        "scanning": "தேடுகிறது...",
        "connected": "இணைக்கப்பட்டது",
        "disconnected": "இணைப்பு துண்டிக்கப்பட்டது",
        "device_name": "குட்பெல்ட்",
        "dashboard": "டாஷ்போர்டு",
        "egg_signals": "EGG சிக்னல்கள்",
        "posture": "தோரணை",
        "history": "வரலாறு",
        "settings": "அமைப்புகள்",
        "battery": "பேட்டரி",
        "posture_good": "தோரணை: நல்லது",
        "posture_fair": "தோரணை: சரியானது",
        "posture_poor": "தோரணை: மோசம்",
        "digestion_normal": "செரிமானம்: சாதாரணம்",
        "digestion_active": "செரிமானம்: செயலில்",
        "digestion_low": "செரிமானம்: குறைவு",
        "theme": "தீம்",
        "dark_mode": "இரவு பயன்முறை",
        "light_mode": "பகல் பயன்முறை",
        "language": "மொழி",
        "change_password": "கடவுச்சொல் மாற்று",
        "current_password": "தற்போதைய கடவுச்சொல்",
        "new_password": "புதிய கடவுச்சொல்",
        "save": "மாற்றங்களை சேமி",
        "week": "வாரம்",
        "month": "மாதம்",
        "no_data": "தரவு இல்லை",
        "connect_device": "குட்பெல்ட் இணை",
        "device_info": "சாதன தகவல்",
        "firmware": "Firmware v2.1.3",
        "signal_strength": "சிக்னல்",
        "logout": "வெளியேறு",
    },
    "Hindi": {
        "app_name": "GutAngle",
        "tagline": "मुद्रा और आंत स्वास्थ्य मॉनिटर",
        "sign_in": "साइन इन",
        "sign_up": "साइन अप",
        "username": "उपयोगकर्ता नाम / ईमेल",
        "password": "पासवर्ड",
        "confirm_password": "पासवर्ड की पुष्टि करें",
        "full_name": "पूरा नाम",
        "forgot_password": "पासवर्ड भूल गए?",
        "reset_password": "पासवर्ड रीसेट करें",
        "email_hint": "रीसेट के लिए ईमेल दर्ज करें",
        "login_btn": "लॉगिन",
        "register_btn": "खाता बनाएं",
        "send_reset": "रीसेट लिंक भेजें",
        "back": "वापस",
        "bluetooth": "ब्लूटूथ",
        "scan": "डिवाइस खोजें",
        "scanning": "खोज रहा है...",
        "connected": "जुड़ा हुआ",
        "disconnected": "डिस्कनेक्ट",
        "device_name": "GutBelt",
        "dashboard": "डैशबोर्ड",
        "egg_signals": "EGG सिग्नल",
        "posture": "मुद्रा",
        "history": "इतिहास",
        "settings": "सेटिंग्स",
        "battery": "बैटरी",
        "posture_good": "मुद्रा: अच्छी",
        "posture_fair": "मुद्रा: ठीक",
        "posture_poor": "मुद्रा: खराब",
        "digestion_normal": "पाचन: सामान्य",
        "digestion_active": "पाचन: सक्रिय",
        "digestion_low": "पाचन: कम",
        "theme": "थीम",
        "dark_mode": "डार्क मोड",
        "light_mode": "लाइट मोड",
        "language": "भाषा",
        "change_password": "पासवर्ड बदलें",
        "current_password": "वर्तमान पासवर्ड",
        "new_password": "नया पासवर्ड",
        "save": "परिवर्तन सहेजें",
        "week": "सप्ताह",
        "month": "महीना",
        "no_data": "कोई डेटा नहीं",
        "connect_device": "GutBelt जोड़ें",
        "device_info": "डिवाइस जानकारी",
        "firmware": "Firmware v2.1.3",
        "signal_strength": "सिग्नल",
        "logout": "लॉग आउट",
    },
    "Telugu": {
        "app_name": "GutAngle", "tagline": "భంగిమ & పేగు ఆరోగ్య మానిటర్",
        "sign_in": "సైన్ ఇన్", "sign_up": "సైన్ అప్",
        "username": "వినియోగదారు పేరు / ఇమెయిల్", "password": "పాస్‌వర్డ్",
        "confirm_password": "పాస్‌వర్డ్ నిర్ధారించు", "full_name": "పూర్తి పేరు",
        "forgot_password": "పాస్‌వర్డ్ మర్చిపోయారా?", "reset_password": "పాస్‌వర్డ్ రీసెట్",
        "email_hint": "రీసెట్ కోసం ఇమెయిల్ నమోదు చేయండి", "login_btn": "లాగిన్",
        "register_btn": "ఖాతా సృష్టించు", "send_reset": "రీసెట్ లింక్ పంపు",
        "back": "వెనుకకు", "bluetooth": "బ్లూటూత్", "scan": "పరికరాలు వెతుకు",
        "scanning": "వెతుకుతోంది...", "connected": "అనుసంధానించబడింది",
        "disconnected": "డిస్‌కనెక్ట్", "device_name": "GutBelt",
        "dashboard": "డాష్‌బోర్డ్", "egg_signals": "EGG సిగ్నల్స్",
        "posture": "భంగిమ", "history": "చరిత్ర", "settings": "సెట్టింగులు",
        "battery": "బ్యాటరీ", "posture_good": "భంగిమ: మంచిది",
        "posture_fair": "భంగిమ: సరైనది", "posture_poor": "భంగిమ: చెడు",
        "digestion_normal": "జీర్ణక్రియ: సాధారణం", "digestion_active": "జీర్ణక్రియ: చురుకైన",
        "digestion_low": "జీర్ణక్రియ: తక్కువ", "theme": "థీమ్",
        "dark_mode": "డార్క్ మోడ్", "light_mode": "లైట్ మోడ్",
        "language": "భాష", "change_password": "పాస్‌వర్డ్ మార్చు",
        "current_password": "ప్రస్తుత పాస్‌వర్డ్", "new_password": "కొత్త పాస్‌వర్డ్",
        "save": "మార్పులు సేవ్ చేయి", "week": "వారం", "month": "నెల",
        "no_data": "డేటా లేదు", "connect_device": "GutBelt కనెక్ట్",
        "device_info": "పరికర సమాచారం", "firmware": "Firmware v2.1.3",
        "signal_strength": "సిగ్నల్", "logout": "లాగ్ అవుట్",
    },
    "Kannada": {
        "app_name": "GutAngle", "tagline": "ಭಂಗಿ ಮತ್ತು ಕರುಳಿನ ಆರೋಗ್ಯ ಮಾನಿಟರ್",
        "sign_in": "ಸೈನ್ ಇನ್", "sign_up": "ಸೈನ್ ಅಪ್",
        "username": "ಬಳಕೆದಾರ ಹೆಸರು / ಇಮೇಲ್", "password": "ಪಾಸ್‌ವರ್ಡ್",
        "confirm_password": "ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ", "full_name": "ಪೂರ್ಣ ಹೆಸರು",
        "forgot_password": "ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿದ್ದೀರಾ?", "reset_password": "ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸಿ",
        "email_hint": "ಮರುಹೊಂದಿಕೆಗಾಗಿ ಇಮೇಲ್ ನಮೂದಿಸಿ", "login_btn": "ಲಾಗಿನ್",
        "register_btn": "ಖಾತೆ ರಚಿಸಿ", "send_reset": "ಮರುಹೊಂದಿಕೆ ಲಿಂಕ್ ಕಳುಹಿಸಿ",
        "back": "ಹಿಂದೆ", "bluetooth": "ಬ್ಲೂಟೂತ್", "scan": "ಸಾಧನಗಳನ್ನು ಹುಡುಕಿ",
        "scanning": "ಹುಡುಕುತ್ತಿದೆ...", "connected": "ಸಂಪರ್ಕಿಸಲಾಗಿದೆ",
        "disconnected": "ಸಂಪರ್ಕ ತಡೆಯಲಾಗಿದೆ", "device_name": "GutBelt",
        "dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್", "egg_signals": "EGG ಸಿಗ್ನಲ್‌ಗಳು",
        "posture": "ಭಂಗಿ", "history": "ಇತಿಹಾಸ", "settings": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
        "battery": "ಬ್ಯಾಟರಿ", "posture_good": "ಭಂಗಿ: ಉತ್ತಮ",
        "posture_fair": "ಭಂಗಿ: ಸರಿಯಾಗಿದೆ", "posture_poor": "ಭಂಗಿ: ಕೆಟ್ಟ",
        "digestion_normal": "ಜೀರ್ಣಕ್ರಿಯೆ: ಸಾಮಾನ್ಯ", "digestion_active": "ಜೀರ್ಣಕ್ರಿಯೆ: ಸಕ್ರಿಯ",
        "digestion_low": "ಜೀರ್ಣಕ್ರಿಯೆ: ಕಡಿಮೆ", "theme": "ಥೀಮ್",
        "dark_mode": "ಡಾರ್ಕ್ ಮೋಡ್", "light_mode": "ಲೈಟ್ ಮೋಡ್",
        "language": "ಭಾಷೆ", "change_password": "ಪಾಸ್‌ವರ್ಡ್ ಬದಲಾಯಿಸಿ",
        "current_password": "ಪ್ರಸ್ತುತ ಪಾಸ್‌ವರ್ಡ್", "new_password": "ಹೊಸ ಪಾಸ್‌ವರ್ಡ್",
        "save": "ಬದಲಾವಣೆಗಳನ್ನು ಉಳಿಸಿ", "week": "ವಾರ", "month": "ತಿಂಗಳು",
        "no_data": "ಡೇಟಾ ಇಲ್ಲ", "connect_device": "GutBelt ಸಂಪರ್ಕಿಸಿ",
        "device_info": "ಸಾಧನ ಮಾಹಿತಿ", "firmware": "Firmware v2.1.3",
        "signal_strength": "ಸಿಗ್ನಲ್", "logout": "ಲಾಗ್ ಔಟ್",
    },
    "Malayalam": {
        "app_name": "GutAngle", "tagline": "ഭാവം & കുടൽ ആരോഗ്യ നിരീക്ഷണം",
        "sign_in": "സൈൻ ഇൻ", "sign_up": "സൈൻ അപ്",
        "username": "ഉപയോക്തൃ നാമം / ഇമെയിൽ", "password": "പാസ്‌വേഡ്",
        "confirm_password": "പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക", "full_name": "പൂർണ്ണ നാമം",
        "forgot_password": "പാസ്‌വേഡ് മറന്നോ?", "reset_password": "പാസ്‌വേഡ് പുനഃസജ്ജീകരിക്കുക",
        "email_hint": "പുനഃസജ്ജീകരണത്തിന് ഇമെയിൽ നൽകുക", "login_btn": "ലോഗിൻ",
        "register_btn": "അക്കൗണ്ട് ഉണ്ടാക്കുക", "send_reset": "റീസെറ്റ് ലിങ്ക് അയയ്ക്കുക",
        "back": "പിന്നോക്കം", "bluetooth": "ബ്ലൂടൂത്ത്", "scan": "ഉപകരണങ്ങൾ തിരയുക",
        "scanning": "തിരയുന്നു...", "connected": "ബന്ധിപ്പിച്ചു",
        "disconnected": "വിച്ഛേദിച്ചു", "device_name": "GutBelt",
        "dashboard": "ഡാഷ്‌ബോർഡ്", "egg_signals": "EGG സിഗ്നലുകൾ",
        "posture": "ഭാവം", "history": "ചരിത്രം", "settings": "ക്രമീകരണങ്ങൾ",
        "battery": "ബാറ്ററി", "posture_good": "ഭാവം: നല്ലത്",
        "posture_fair": "ഭാവം: ശരി", "posture_poor": "ഭാവം: മോശം",
        "digestion_normal": "ദഹനം: സാധാരണ", "digestion_active": "ദഹനം: സജീവം",
        "digestion_low": "ദഹനം: കുറഞ്ഞ", "theme": "തീം",
        "dark_mode": "ഡാർക്ക് മോഡ്", "light_mode": "ലൈറ്റ് മോഡ്",
        "language": "ഭാഷ", "change_password": "പാസ്‌വേഡ് മാറ്റുക",
        "current_password": "നിലവിലെ പാസ്‌വേഡ്", "new_password": "പുതിയ പാസ്‌വേഡ്",
        "save": "മാറ്റങ്ങൾ സംരക്ഷിക്കുക", "week": "ആഴ്ച", "month": "മാസം",
        "no_data": "ഡാറ്റ ഇല്ല", "connect_device": "GutBelt ബന്ധിപ്പിക്കുക",
        "device_info": "ഉപകരണ വിവരങ്ങൾ", "firmware": "Firmware v2.1.3",
        "signal_strength": "സിഗ്നൽ", "logout": "ലോഗ് ഔട്ട്",
    },
    "Bengali": {
        "app_name": "GutAngle", "tagline": "ভঙ্গি ও অন্ত্র স্বাস্থ্য মনিটর",
        "sign_in": "সাইন ইন", "sign_up": "সাইন আপ",
        "username": "ব্যবহারকারীর নাম / ইমেইল", "password": "পাসওয়ার্ড",
        "confirm_password": "পাসওয়ার্ড নিশ্চিত করুন", "full_name": "পূর্ণ নাম",
        "forgot_password": "পাসওয়ার্ড ভুলে গেছেন?", "reset_password": "পাসওয়ার্ড রিসেট",
        "email_hint": "রিসেটের জন্য ইমেইল দিন", "login_btn": "লগইন",
        "register_btn": "অ্যাকাউন্ট তৈরি করুন", "send_reset": "রিসেট লিঙ্ক পাঠান",
        "back": "ফিরে যান", "bluetooth": "ব্লুটুথ", "scan": "ডিভাইস খুঁজুন",
        "scanning": "খুঁজছে...", "connected": "সংযুক্ত",
        "disconnected": "সংযোগ বিচ্ছিন্ন", "device_name": "GutBelt",
        "dashboard": "ড্যাশবোর্ড", "egg_signals": "EGG সংকেত",
        "posture": "ভঙ্গি", "history": "ইতিহাস", "settings": "সেটিংস",
        "battery": "ব্যাটারি", "posture_good": "ভঙ্গি: ভালো",
        "posture_fair": "ভঙ্গি: মোটামুটি", "posture_poor": "ভঙ্গি: খারাপ",
        "digestion_normal": "হজম: স্বাভাবিক", "digestion_active": "হজম: সক্রিয়",
        "digestion_low": "হজম: কম", "theme": "থিম",
        "dark_mode": "ডার্ক মোড", "light_mode": "লাইট মোড",
        "language": "ভাষা", "change_password": "পাসওয়ার্ড পরিবর্তন",
        "current_password": "বর্তমান পাসওয়ার্ড", "new_password": "নতুন পাসওয়ার্ড",
        "save": "পরিবর্তন সংরক্ষণ", "week": "সপ্তাহ", "month": "মাস",
        "no_data": "কোনো ডেটা নেই", "connect_device": "GutBelt সংযুক্ত করুন",
        "device_info": "ডিভাইস তথ্য", "firmware": "Firmware v2.1.3",
        "signal_strength": "সংকেত", "logout": "লগ আউট",
    },
    "Marathi": {
        "app_name": "GutAngle", "tagline": "आसन आणि आतड्याचे आरोग्य मॉनिटर",
        "sign_in": "साइन इन", "sign_up": "साइन अप",
        "username": "वापरकर्ता नाव / ईमेल", "password": "पासवर्ड",
        "confirm_password": "पासवर्ड पुष्टी करा", "full_name": "पूर्ण नाव",
        "forgot_password": "पासवर्ड विसरलात?", "reset_password": "पासवर्ड रीसेट करा",
        "email_hint": "रीसेटसाठी ईमेल प्रविष्ट करा", "login_btn": "लॉगिन",
        "register_btn": "खाते तयार करा", "send_reset": "रीसेट लिंक पाठवा",
        "back": "मागे", "bluetooth": "ब्लूटूथ", "scan": "उपकरणे शोधा",
        "scanning": "शोधत आहे...", "connected": "जोडलेले",
        "disconnected": "डिस्कनेक्ट", "device_name": "GutBelt",
        "dashboard": "डॅशबोर्ड", "egg_signals": "EGG सिग्नल",
        "posture": "आसन", "history": "इतिहास", "settings": "सेटिंग्ज",
        "battery": "बॅटरी", "posture_good": "आसन: चांगले",
        "posture_fair": "आसन: ठीक", "posture_poor": "आसन: वाईट",
        "digestion_normal": "पचन: सामान्य", "digestion_active": "पचन: सक्रिय",
        "digestion_low": "पचन: कमी", "theme": "थीम",
        "dark_mode": "डार्क मोड", "light_mode": "लाइट मोड",
        "language": "भाषा", "change_password": "पासवर्ड बदला",
        "current_password": "सध्याचा पासवर्ड", "new_password": "नवीन पासवर्ड",
        "save": "बदल जतन करा", "week": "आठवडा", "month": "महिना",
        "no_data": "डेटा उपलब्ध नाही", "connect_device": "GutBelt जोडा",
        "device_info": "उपकरण माहिती", "firmware": "Firmware v2.1.3",
        "signal_strength": "सिग्नल", "logout": "लॉग आउट",
    },
    "Odia": {
        "app_name": "GutAngle", "tagline": "ଭଙ୍ଗୀ ଓ ପେଟ ସ୍ୱାସ୍ଥ୍ୟ ନଜର",
        "sign_in": "ସାଇନ ଇନ", "sign_up": "ସାଇନ ଅପ",
        "username": "ବ୍ୟବହାରକାରୀ ନାମ / ଇମେଲ", "password": "ପାସୱାର୍ଡ",
        "confirm_password": "ପାସୱାର୍ଡ ନିଶ୍ଚିତ କରନ୍ତୁ", "full_name": "ପୂର୍ଣ ନାମ",
        "forgot_password": "ପାସୱାର୍ଡ ଭୁଲିଯାଇଛନ୍ତି?", "reset_password": "ପାସୱାର୍ଡ ରିସେଟ",
        "email_hint": "ରିସେଟ ପାଇଁ ଇମେଲ ଦିଅନ୍ତୁ", "login_btn": "ଲଗଇନ",
        "register_btn": "ଆକାଉଣ୍ଟ ତୈଆର କରନ୍ତୁ", "send_reset": "ରିସେଟ ଲିଙ୍କ ପଠାନ୍ତୁ",
        "back": "ପଛକୁ", "bluetooth": "ବ୍ଲୁଟୁଥ", "scan": "ଡିଭାଇସ ଖୋଜନ୍ତୁ",
        "scanning": "ଖୋଜୁଛି...", "connected": "ସଂଯୁକ୍ତ",
        "disconnected": "ସଂଯୋଗ ବିଚ୍ଛିନ୍ନ", "device_name": "GutBelt",
        "dashboard": "ଡ୍ୟାଶବୋର୍ଡ", "egg_signals": "EGG ସଙ୍କେତ",
        "posture": "ଭଙ୍ଗୀ", "history": "ଇତିହାସ", "settings": "ସେଟିଂ",
        "battery": "ବ୍ୟାଟେରୀ", "posture_good": "ଭଙ୍ଗୀ: ଭଲ",
        "posture_fair": "ଭଙ୍ଗୀ: ଠିକ", "posture_poor": "ଭଙ୍ଗୀ: ଖରାପ",
        "digestion_normal": "ହଜମ: ସ୍ୱାଭାବିକ", "digestion_active": "ହଜମ: ସକ୍ରିୟ",
        "digestion_low": "ହଜମ: କମ", "theme": "ଥିମ",
        "dark_mode": "ଡାର୍କ ମୋଡ", "light_mode": "ଲାଇଟ ମୋଡ",
        "language": "ଭାଷା", "change_password": "ପାସୱାର୍ଡ ବଦଳାନ୍ତୁ",
        "current_password": "ବର୍ତ୍ତମାନ ପାସୱାର୍ଡ", "new_password": "ନୂଆ ପାସୱାର୍ଡ",
        "save": "ପରିବର୍ତ୍ତନ ସଞ୍ଚୟ କରନ୍ତୁ", "week": "ସପ୍ତାହ", "month": "ମାସ",
        "no_data": "ତଥ୍ୟ ନାହିଁ", "connect_device": "GutBelt ସଂଯୁକ୍ତ",
        "device_info": "ଡିଭାଇସ ସୂଚନା", "firmware": "Firmware v2.1.3",
        "signal_strength": "ସଙ୍କେତ", "logout": "ଲଗ ଆଉଟ",
    },
    "Urdu": {
        "app_name": "GutAngle", "tagline": "کرنسی اور آنت کی صحت کی نگرانی",
        "sign_in": "سائن ان", "sign_up": "سائن اپ",
        "username": "صارف نام / ای میل", "password": "پاس ورڈ",
        "confirm_password": "پاس ورڈ کی تصدیق", "full_name": "پورا نام",
        "forgot_password": "پاس ورڈ بھول گئے؟", "reset_password": "پاس ورڈ ری سیٹ",
        "email_hint": "ری سیٹ کے لیے ای میل درج کریں", "login_btn": "لاگ ان",
        "register_btn": "اکاؤنٹ بنائیں", "send_reset": "ری سیٹ لنک بھیجیں",
        "back": "واپس", "bluetooth": "بلوٹوتھ", "scan": "آلات تلاش کریں",
        "scanning": "تلاش ہو رہی ہے...", "connected": "منسلک",
        "disconnected": "غیر منسلک", "device_name": "GutBelt",
        "dashboard": "ڈیش بورڈ", "egg_signals": "EGG سگنلز",
        "posture": "کرنسی", "history": "تاریخ", "settings": "ترتیبات",
        "battery": "بیٹری", "posture_good": "کرنسی: اچھی",
        "posture_fair": "کرنسی: ٹھیک", "posture_poor": "کرنسی: خراب",
        "digestion_normal": "ہاضمہ: معمول", "digestion_active": "ہاضمہ: فعال",
        "digestion_low": "ہاضمہ: کم", "theme": "تھیم",
        "dark_mode": "ڈارک موڈ", "light_mode": "لائٹ موڈ",
        "language": "زبان", "change_password": "پاس ورڈ تبدیل کریں",
        "current_password": "موجودہ پاس ورڈ", "new_password": "نیا پاس ورڈ",
        "save": "تبدیلیاں محفوظ کریں", "week": "ہفتہ", "month": "مہینہ",
        "no_data": "کوئی ڈیٹا نہیں", "connect_device": "GutBelt منسلک کریں",
        "device_info": "آلے کی معلومات", "firmware": "Firmware v2.1.3",
        "signal_strength": "سگنل", "logout": "لاگ آؤٹ",
    },
}

current_language = "English"

def L(key):
    lang = LANGUAGES.get(current_language, LANGUAGES["English"])
    return lang.get(key, LANGUAGES["English"].get(key, key))


# ─────────────────────────────────────────────
#  APP STATE
# ─────────────────────────────────────────────
app_state = {
    "bt_connected": False,
    "battery": 78,
    "signal": -65,
    "posture_score": 85,
    "egg_amplitude": 0.5,
}

def generate_history():
    data = {}
    now = datetime.now()
    for i in range(30):
        day = now - timedelta(days=i)
        key = day.strftime("%Y-%m-%d")
        data[key] = {
            "posture_avg": random.randint(55, 95),
            "egg_avg": round(random.uniform(0.3, 0.9), 2),
            "sessions": random.randint(1, 5),
        }
    return data

history_data = generate_history()


# ─────────────────────────────────────────────
#  RIPPLE BUTTON
# ─────────────────────────────────────────────
class RippleButton(QPushButton):
    def __init__(self, text="", parent=None, variant="primary"):
        super().__init__(text, parent)
        self.variant = variant
        self._ripples = []
        self._ripple_timer = QTimer(self)
        self._ripple_timer.setInterval(16)
        self._ripple_timer.timeout.connect(self._update_ripples)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._apply_style()

    def _apply_style(self):
        if self.variant == "primary":
            bg = T("accent"); fg = "#0A0F1E"; hover = T("accent2")
        elif self.variant == "secondary":
            bg = T("surface2"); fg = T("text"); hover = T("border")
        elif self.variant == "ghost":
            bg = "transparent"; fg = T("accent"); hover = T("surface2")
        elif self.variant == "danger":
            bg = T("danger"); fg = "#FFFFFF"; hover = "#C53030"
        else:
            bg = T("accent"); fg = "#0A0F1E"; hover = T("accent2")

        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg}; color: {fg}; border: none;
                border-radius: 10px; padding: 10px 22px;
                font-size: 13px; font-weight: 600;
            }}
            QPushButton:hover {{ background: {hover}; }}
            QPushButton:disabled {{
                background: {T("surface2")}; color: {T("text3")};
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._ripples.append({
                "x": event.position().x(), "y": event.position().y(),
                "radius": 0, "alpha": 160,
            })
            if not self._ripple_timer.isActive():
                self._ripple_timer.start()
        super().mousePressEvent(event)

    def _update_ripples(self):
        alive = []
        for r in self._ripples:
            r["radius"] += 8
            r["alpha"] = max(0, r["alpha"] - 9)
            if r["alpha"] > 0:
                alive.append(r)
        self._ripples = alive
        if not alive:
            self._ripple_timer.stop()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._ripples:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for r in self._ripples:
            c = QColor(T("ripple"))
            c.setAlpha(r["alpha"])
            painter.setBrush(QBrush(c))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                int(r["x"] - r["radius"]), int(r["y"] - r["radius"]),
                int(r["radius"] * 2), int(r["radius"] * 2)
            )
        painter.end()


# ─────────────────────────────────────────────
#  STYLED INPUT
# ─────────────────────────────────────────────
class StyledInput(QLineEdit):
    def __init__(self, placeholder="", is_password=False, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        if is_password:
            self.setEchoMode(QLineEdit.EchoMode.Password)
        self.setFixedHeight(46)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {T("surface")}; color: {T("text")};
                border: 1.5px solid {T("border")}; border-radius: 10px;
                padding: 0 16px; font-size: 14px;
            }}
            QLineEdit:focus {{ border: 1.5px solid {T("accent")}; }}
        """)


# ─────────────────────────────────────────────
#  CARD
# ─────────────────────────────────────────────
class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setStyleSheet(f"""
            QFrame#Card {{
                background: {T("surface")};
                border: 1px solid {T("border")};
                border-radius: 14px;
            }}
        """)


# ─────────────────────────────────────────────
#  LOADING SCREEN
# ─────────────────────────────────────────────
class LoadingScreen(QWidget):
    done = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self._ripple_scale = 0.0
        self._progress = 0

        self.setStyleSheet(f"background:{T('bg')};")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Canvas for animated logo
        self._canvas = QWidget(self)
        self._canvas.setFixedSize(200, 200)
        self._canvas.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(self._canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(16)

        self._logo_lbl = QLabel("GutAngle")
        self._logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo_lbl.setStyleSheet(f"color:{T('accent')}; font-size:30px; font-weight:800; letter-spacing:3px;")
        layout.addWidget(self._logo_lbl)

        self._tagline_lbl = QLabel(L("tagline"))
        self._tagline_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._tagline_lbl.setStyleSheet(f"color:{T('text2')}; font-size:13px; margin-top:2px;")
        layout.addWidget(self._tagline_lbl)

        layout.addSpacing(36)

        self._status_lbl = QLabel("Initializing...")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_lbl.setStyleSheet(f"color:{T('text3')}; font-size:12px;")
        layout.addWidget(self._status_lbl)

        layout.addSpacing(8)

        self._bar = QProgressBar()
        self._bar.setFixedWidth(260)
        self._bar.setFixedHeight(4)
        self._bar.setTextVisible(False)
        self._bar.setRange(0, 100)
        self._bar.setStyleSheet(f"""
            QProgressBar {{ background:{T("surface2")}; border-radius:2px; border:none; }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {T("accent")}, stop:1 {T("accent2")});
                border-radius:2px;
            }}
        """)
        layout.addWidget(self._bar, alignment=Qt.AlignmentFlag.AlignCenter)

        self._spin_timer = QTimer(self)
        self._spin_timer.setInterval(20)
        self._spin_timer.timeout.connect(self._tick)
        self._spin_timer.start()

        self._prog_timer = QTimer(self)
        self._prog_timer.setInterval(45)
        self._prog_timer.timeout.connect(self._tick_progress)
        self._prog_timer.start()

        self._msgs = ["Initializing...", "Checking Bluetooth...",
                      "Loading components...", "Preparing sensors...", "Almost ready..."]
        self._msg_idx = 0
        self._msg_timer = QTimer(self)
        self._msg_timer.setInterval(700)
        self._msg_timer.timeout.connect(self._next_msg)
        self._msg_timer.start()

    def _tick(self):
        self._angle = (self._angle + 3) % 360
        self._ripple_scale = (self._ripple_scale + 0.018) % 1.0
        self.update()

    def _tick_progress(self):
        if self._progress < 100:
            self._progress = min(100, self._progress + random.randint(1, 3))
            self._bar.setValue(self._progress)
        else:
            self._prog_timer.stop()
            self._spin_timer.stop()
            self._msg_timer.stop()
            QTimer.singleShot(400, self.done.emit)

    def _next_msg(self):
        self._msg_idx = (self._msg_idx + 1) % len(self._msgs)
        self._status_lbl.setText(self._msgs[self._msg_idx])

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        canvas_rect = self._canvas.geometry()
        cx = canvas_rect.x() + canvas_rect.width() // 2
        cy = canvas_rect.y() + canvas_rect.height() // 2

        # Ripple rings
        for i in range(3):
            phase = (self._ripple_scale + i * 0.33) % 1.0
            radius = int(55 + 35 * phase)
            alpha = int(110 * (1 - phase))
            c = QColor(T("accent"))
            c.setAlpha(alpha)
            p.setPen(QPen(c, 1.5))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

        # Spinning arc
        grad = QConicalGradient(cx, cy, self._angle)
        grad.setColorAt(0, QColor(T("accent")))
        grad.setColorAt(0.5, QColor(T("accent2")))
        grad.setColorAt(1, QColor(T("accent")))
        p.setPen(QPen(QBrush(grad), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(cx - 50, cy - 50, 100, 100, 0, 270 * 16)

        # Center fill
        cg = QRadialGradient(cx, cy, 34)
        cg.setColorAt(0, QColor(T("accent")))
        cg.setColorAt(1, QColor(T("bg")))
        p.setBrush(QBrush(cg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(cx - 34, cy - 34, 68, 68)

        # Wave icon in center
        wave_pen = QPen(QColor("#0A0F1E"), 2)
        wave_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(wave_pen)
        path = QPainterPath()
        path.moveTo(cx - 18, cy)
        for j in range(37):
            x = cx - 18 + j
            y = cy + 10 * math.sin((j / 36) * 2 * math.pi + self._angle * 0.06)
            path.lineTo(x, y)
        p.drawPath(path)
        p.end()


# ─────────────────────────────────────────────
#  AUTH SCREEN
# ─────────────────────────────────────────────
class AuthScreen(QWidget):
    login_success = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{T('bg')};")
        self._stack = QStackedWidget(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stack)
        self._stack.addWidget(self._build_login())
        self._stack.addWidget(self._build_signup())
        self._stack.addWidget(self._build_forgot())

    def _panel(self):
        outer = QWidget()
        outer.setStyleSheet(f"background:{T('bg')};")
        v = QVBoxLayout(outer)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card = Card()
        card.setFixedWidth(420)
        v.addWidget(card)
        return outer, card

    def _build_login(self):
        outer, card = self._panel()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(38, 36, 38, 36)
        lay.setSpacing(14)

        logo = QLabel("⬡ GutAngle")
        logo.setStyleSheet(f"color:{T('accent')}; font-size:22px; font-weight:800; letter-spacing:2px;")
        lay.addWidget(logo)

        title = QLabel(L("sign_in"))
        title.setStyleSheet(f"color:{T('text')}; font-size:24px; font-weight:800; margin-top:8px;")
        lay.addWidget(title)

        sub = QLabel("Welcome back — your gut is waiting.")
        sub.setStyleSheet(f"color:{T('text2')}; font-size:12px; margin-bottom:8px;")
        lay.addWidget(sub)

        self._login_user = StyledInput(L("username"))
        self._login_pass = StyledInput(L("password"), is_password=True)
        lay.addWidget(self._login_user)
        lay.addWidget(self._login_pass)

        forgot = QPushButton(L("forgot_password"))
        forgot.setStyleSheet(f"color:{T('accent')}; background:transparent; border:none; font-size:12px;")
        forgot.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        forgot.clicked.connect(lambda: self._stack.setCurrentIndex(2))
        lay.addWidget(forgot, alignment=Qt.AlignmentFlag.AlignRight)

        login_btn = RippleButton(L("login_btn"), variant="primary")
        login_btn.setFixedHeight(48)
        login_btn.clicked.connect(self.login_success.emit)
        lay.addWidget(login_btn)

        sep = QLabel("— or —")
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sep.setStyleSheet(f"color:{T('text3')}; font-size:11px;")
        lay.addWidget(sep)

        su_btn = RippleButton(L("sign_up"), variant="ghost")
        su_btn.setFixedHeight(44)
        su_btn.clicked.connect(lambda: self._stack.setCurrentIndex(1))
        lay.addWidget(su_btn)

        return outer

    def _build_signup(self):
        outer, card = self._panel()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(38, 36, 38, 36)
        lay.setSpacing(12)

        title = QLabel(L("sign_up"))
        title.setStyleSheet(f"color:{T('text')}; font-size:24px; font-weight:800;")
        lay.addWidget(title)
        sub = QLabel("Join GutAngle today")
        sub.setStyleSheet(f"color:{T('text2')}; font-size:12px; margin-bottom:6px;")
        lay.addWidget(sub)

        self._su_name = StyledInput(L("full_name"))
        self._su_email = StyledInput(L("username"))
        self._su_pass = StyledInput(L("password"), is_password=True)
        self._su_confirm = StyledInput(L("confirm_password"), is_password=True)
        for w in [self._su_name, self._su_email, self._su_pass, self._su_confirm]:
            lay.addWidget(w)

        reg_btn = RippleButton(L("register_btn"), variant="primary")
        reg_btn.setFixedHeight(48)
        reg_btn.clicked.connect(self._do_register)
        lay.addWidget(reg_btn)

        back_btn = RippleButton(L("back"), variant="ghost")
        back_btn.setFixedHeight(40)
        back_btn.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        lay.addWidget(back_btn)
        return outer

    def _build_forgot(self):
        outer, card = self._panel()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(38, 36, 38, 36)
        lay.setSpacing(14)

        title = QLabel(L("reset_password"))
        title.setStyleSheet(f"color:{T('text')}; font-size:24px; font-weight:800;")
        lay.addWidget(title)
        sub = QLabel(L("email_hint"))
        sub.setStyleSheet(f"color:{T('text2')}; font-size:12px; margin-bottom:8px;")
        lay.addWidget(sub)

        self._forgot_email = StyledInput("Email address")
        lay.addWidget(self._forgot_email)

        send_btn = RippleButton(L("send_reset"), variant="primary")
        send_btn.setFixedHeight(48)
        send_btn.clicked.connect(self._do_forgot)
        lay.addWidget(send_btn)

        back_btn = RippleButton(L("back"), variant="ghost")
        back_btn.setFixedHeight(40)
        back_btn.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        lay.addWidget(back_btn)
        return outer

    def _do_register(self):
        if self._su_pass.text() != self._su_confirm.text():
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        self._stack.setCurrentIndex(0)

    def _do_forgot(self):
        QMessageBox.information(self, "Sent", f"Reset link sent to: {self._forgot_email.text()}")
        self._stack.setCurrentIndex(0)


# ─────────────────────────────────────────────
#  BLUETOOTH SCREEN
# ─────────────────────────────────────────────
class BluetoothWorker(QThread):
    status_update = pyqtSignal(str, str)
    scan_complete = pyqtSignal(bool)

    def run(self):
        self.status_update.emit("Initializing Bluetooth...", "text2")
        time.sleep(0.8)
        self.status_update.emit("Scanning for GutBelt...", "accent2")
        time.sleep(1.5)

        if HAS_BLEAK:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                devices = loop.run_until_complete(BleakScanner.discover(timeout=3.0))
                found = any(d.name and "gutbelt" in d.name.lower() for d in devices)
            except Exception:
                found = False
        else:
            time.sleep(1.0)
            found = random.random() > 0.3

        if found:
            self.status_update.emit("GutBelt found!", "success")
            time.sleep(0.6)
            self.status_update.emit("Connecting to GutBelt...", "accent")
            time.sleep(1.2)
            self.status_update.emit("Connected to GutBelt", "success")
            app_state["bt_connected"] = True
            self.scan_complete.emit(True)
        else:
            self.status_update.emit("GutBelt not found nearby.", "danger")
            self.scan_complete.emit(False)


class BluetoothScreen(QWidget):
    connected = pyqtSignal()
    skip = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{T('bg')};")
        self._scanning = False
        self._angle = 0

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(0)
        lay.setContentsMargins(60, 40, 60, 40)

        title = QLabel(L("bluetooth"))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color:{T('text')}; font-size:26px; font-weight:800; margin-bottom:4px;")
        lay.addWidget(title)

        sub = QLabel("Pair your GutBelt wearable")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color:{T('text2')}; font-size:13px; margin-bottom:20px;")
        lay.addWidget(sub)

        self._canvas = QWidget()
        self._canvas.setFixedSize(190, 190)
        lay.addWidget(self._canvas, alignment=Qt.AlignmentFlag.AlignCenter)

        lay.addSpacing(24)

        self._status_lbl = QLabel("Press scan to find GutBelt")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_lbl.setStyleSheet(f"color:{T('text2')}; font-size:14px; font-weight:500;")
        lay.addWidget(self._status_lbl)

        lay.addSpacing(28)

        self._scan_btn = RippleButton(L("scan"), variant="primary")
        self._scan_btn.setFixedWidth(240)
        self._scan_btn.setFixedHeight(50)
        self._scan_btn.clicked.connect(self._start_scan)
        lay.addWidget(self._scan_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        lay.addSpacing(10)

        skip_btn = RippleButton("Skip for now", variant="ghost")
        skip_btn.setFixedWidth(240)
        skip_btn.clicked.connect(self.skip.emit)
        lay.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._spin_timer = QTimer(self)
        self._spin_timer.setInterval(20)
        self._spin_timer.timeout.connect(self._tick)

    def _tick(self):
        self._angle = (self._angle + 4) % 360
        self.update()

    def _start_scan(self):
        if self._scanning:
            return
        self._scanning = True
        self._scan_btn.setEnabled(False)
        self._spin_timer.start()
        w = BluetoothWorker(self)
        w.status_update.connect(self._on_status)
        w.scan_complete.connect(self._on_complete)
        w.start()

    def _on_status(self, msg, color_key):
        self._status_lbl.setText(msg)
        self._status_lbl.setStyleSheet(f"color:{T(color_key)}; font-size:14px; font-weight:500;")

    def _on_complete(self, success):
        self._spin_timer.stop()
        self._scanning = False
        self._scan_btn.setEnabled(True)
        if success:
            QTimer.singleShot(600, self.connected.emit)
        else:
            self._scan_btn.setText("Retry Scan")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cr = self._canvas.geometry()
        cx = cr.x() + cr.width() // 2
        cy = cr.y() + cr.height() // 2

        if self._scanning:
            for i in range(3):
                phase = ((self._angle / 360) + i * 0.33) % 1.0
                r = int(38 + 38 * phase)
                alpha = int(160 * (1 - phase))
                c = QColor(T("accent")); c.setAlpha(alpha)
                p.setPen(QPen(c, 2)); p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
        else:
            for r in [32, 52, 72]:
                p.setPen(QPen(QColor(T("border")), 1))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        p.setBrush(QBrush(QColor(T("surface"))))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(cx - 28, cy - 28, 56, 56)

        pen = QPen(QColor(T("accent")), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(cx, cy - 16, cx, cy + 16)
        p.drawLine(cx, cy - 16, cx + 10, cy - 7)
        p.drawLine(cx + 10, cy - 7, cx - 7, cy + 7)
        p.drawLine(cx - 7, cy + 7, cx + 10, cy + 7)
        p.drawLine(cx + 10, cy + 7, cx, cy + 16)
        p.end()


# ─────────────────────────────────────────────
#  REALTIME GRAPH
# ─────────────────────────────────────────────
class RealtimeGraph(QWidget):
    def __init__(self, title="Signal", color_key="accent", parent=None):
        super().__init__(parent)
        self.title = title
        self.color_key = color_key
        self._data = deque([0.0] * 200, maxlen=200)
        self.setMinimumHeight(120)
        self.setStyleSheet(f"background:{T('surface')}; border-radius:8px;")

    def push(self, value):
        self._data.append(value)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        pad = 14

        p.fillRect(0, 0, w, h, QColor(T("surface")))

        p.setPen(QPen(QColor(T("border")), 1, Qt.PenStyle.DotLine))
        for i in range(1, 4):
            y = pad + (h - 2 * pad) * i // 4
            p.drawLine(pad, y, w - pad, y)

        p.setPen(QPen(QColor(T("text2"))))
        p.setFont(QFont("", 9, QFont.Weight.Medium))
        p.drawText(pad + 4, pad + 13, self.title)

        data = list(self._data)
        if len(data) < 2:
            p.end()
            return

        mn, mx = min(data), max(data)
        rng = mx - mn if mx != mn else 1.0

        def ys(v):
            return h - pad - int((v - mn) / rng * (h - 2 * pad - 14)) - 6

        x_step = (w - 2 * pad) / (len(data) - 1)
        path = QPainterPath()
        path.moveTo(pad, ys(data[0]))
        for i, v in enumerate(data[1:], 1):
            path.lineTo(pad + i * x_step, ys(v))

        fill = QPainterPath(path)
        fill.lineTo(pad + (len(data) - 1) * x_step, h - pad)
        fill.lineTo(pad, h - pad)
        fill.closeSubpath()

        lc = QColor(T(self.color_key))
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(lc.red(), lc.green(), lc.blue(), 55))
        grad.setColorAt(1, QColor(lc.red(), lc.green(), lc.blue(), 0))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(fill)

        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(lc, 2))
        p.drawPath(path)

        lx = pad + (len(data) - 1) * x_step
        ly = ys(data[-1])
        p.setBrush(QBrush(lc))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(lx) - 4, int(ly) - 4, 8, 8)
        p.end()


# ─────────────────────────────────────────────
#  POSTURE GAUGE
# ─────────────────────────────────────────────
class PostureGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._score = 75
        self.setFixedSize(150, 95)

    def set_score(self, s):
        self._score = max(0, min(100, s))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h - 8
        r = 72

        p.setPen(QPen(QColor(T("border")), 9, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(cx - r, cy - r, r * 2, r * 2, 0, 180 * 16)

        color = QColor(T("danger") if self._score < 50 else T("warning") if self._score < 75 else T("success"))
        p.setPen(QPen(color, 9, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(cx - r, cy - r, r * 2, r * 2, 0, int(self._score / 100 * 180) * 16)

        p.setPen(QPen(QColor(T("text"))))
        p.setFont(QFont("", 22, QFont.Weight.Bold))
        p.drawText(cx - 26, cy - 18, f"{self._score}")
        p.setFont(QFont("", 9))
        p.setPen(QPen(QColor(T("text2"))))
        p.drawText(cx + 4, cy - 18, "%")
        p.end()


# ─────────────────────────────────────────────
#  DATA SIMULATOR
# ─────────────────────────────────────────────
class DataSimulator(QThread):
    new_egg = pyqtSignal(float)
    new_posture = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self._t = 0
        self._running = True

    def run(self):
        while self._running:
            self._t += 0.1
            egg = (0.5 * math.sin(2 * math.pi * 0.05 * self._t) +
                   0.2 * math.sin(2 * math.pi * 0.15 * self._t) +
                   random.gauss(0, 0.04))
            posture = max(0.0, min(1.0,
                0.7 + 0.3 * math.sin(2 * math.pi * 0.005 * self._t) + random.gauss(0, 0.025)))
            app_state["egg_amplitude"] = egg
            app_state["posture_score"] = int(posture * 100)
            self.new_egg.emit(egg)
            self.new_posture.emit(posture)
            time.sleep(0.05)

    def stop(self):
        self._running = False


# ─────────────────────────────────────────────
#  DASHBOARD SCREEN
# ─────────────────────────────────────────────
class DashboardScreen(QWidget):
    go_settings = pyqtSignal()
    go_bluetooth = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._simulator = None
        self._session_secs = 0
        self._build_ui()
        self._status_timer = QTimer(self)
        self._status_timer.setInterval(2000)
        self._status_timer.timeout.connect(self._refresh_status)
        self._status_timer.start()
        self._session_timer = QTimer(self)
        self._session_timer.setInterval(1000)
        self._session_timer.timeout.connect(self._tick_session)
        self._session_timer.start()

    def _tick_session(self):
        self._session_secs += 1
        m, s = divmod(self._session_secs, 60)
        lbl_children = self._card_session.findChildren(QLabel)
        if len(lbl_children) >= 2:
            lbl_children[1].setText(f"{m:02d}:{s:02d}")

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top bar
        topbar = QWidget()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet(f"background:{T('surface')}; border-bottom:1px solid {T('border')};")
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("⬡ GutAngle")
        logo.setStyleSheet(f"color:{T('accent')}; font-size:17px; font-weight:800; letter-spacing:2px;")
        tb.addWidget(logo)
        tb.addStretch()

        self._conn_dot = QLabel("●")
        self._conn_dot.setStyleSheet(f"color:{T('danger')}; font-size:13px;")
        tb.addWidget(self._conn_dot)
        self._conn_lbl = QLabel("  Disconnected")
        self._conn_lbl.setStyleSheet(f"color:{T('text2')}; font-size:12px; margin-right:14px;")
        tb.addWidget(self._conn_lbl)

        self._bat_lbl = QLabel(f"🔋 {app_state['battery']}%")
        self._bat_lbl.setStyleSheet(f"color:{T('text2')}; font-size:12px; margin-right:14px;")
        tb.addWidget(self._bat_lbl)

        cfg_btn = QPushButton("⚙")
        cfg_btn.setFixedSize(34, 34)
        cfg_btn.setStyleSheet(f"""
            QPushButton {{ background:{T('surface2')}; color:{T('text')}; border:none;
                border-radius:8px; font-size:15px; }}
            QPushButton:hover {{ background:{T('border')}; }}
        """)
        cfg_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cfg_btn.clicked.connect(self.go_settings.emit)
        tb.addWidget(cfg_btn)

        root.addWidget(topbar)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border:none; background:{T('bg')}; }}
            QTabBar::tab {{
                background:{T('surface')}; color:{T('text2')};
                border:none; padding:11px 18px; font-size:12px; font-weight:500; min-width:80px;
            }}
            QTabBar::tab:selected {{ color:{T('accent')}; border-bottom:2px solid {T('accent')}; background:{T('bg')}; }}
            QTabBar::tab:hover {{ color:{T('text')}; }}
        """)
        self._tabs.addTab(self._build_overview(), L("dashboard"))
        self._tabs.addTab(self._build_egg_tab(), L("egg_signals"))
        self._tabs.addTab(self._build_posture_tab(), L("posture"))
        self._tabs.addTab(self._build_history_tab(), L("history"))
        root.addWidget(self._tabs)

    def _sw(self, widget):
        s = QScrollArea()
        s.setWidget(widget)
        s.setWidgetResizable(True)
        s.setStyleSheet(f"background:{T('bg')}; border:none;")
        return s

    def _build_overview(self):
        c = QWidget(); c.setStyleSheet(f"background:{T('bg')};")
        lay = QVBoxLayout(c)
        lay.setContentsMargins(18, 18, 18, 18)
        lay.setSpacing(14)

        # Stat cards
        row = QHBoxLayout(); row.setSpacing(10)
        self._card_posture = self._stat_card("Posture Score", "85%", T("success"), "Good")
        self._card_egg = self._stat_card("EGG Activity", "Normal", T("accent"), "3.0 cpm")
        self._card_session = self._stat_card("Session Time", "00:00", T("accent2"), "Active")
        self._card_alerts = self._stat_card("Alerts", "0", T("warning"), "Today")
        for card in [self._card_posture, self._card_egg, self._card_session, self._card_alerts]:
            row.addWidget(card)
        lay.addLayout(row)

        # Graphs
        grow = QHBoxLayout(); grow.setSpacing(10)
        for title, color_key, attr in [
            (L("egg_signals"), "graph_egg", "_egg_ov"),
            (L("posture"), "graph_pos", "_pos_ov")
        ]:
            card = Card()
            cl = QVBoxLayout(card); cl.setContentsMargins(14, 10, 14, 10)
            cl.addWidget(self._clabel(title))
            graph = RealtimeGraph(title, color_key)
            graph.setMinimumHeight(130)
            setattr(self, attr, graph)
            cl.addWidget(graph)
            grow.addWidget(card)
        lay.addLayout(grow)

        # Status bar
        sc = Card()
        sl = QHBoxLayout(sc); sl.setContentsMargins(18, 12, 18, 12)
        self._posture_pill = self._pill(L("posture_good"), T("success"))
        self._digest_pill = self._pill(L("digestion_normal"), T("accent"))
        sl.addWidget(self._clabel("Status:"))
        sl.addWidget(self._posture_pill)
        sl.addWidget(self._digest_pill)
        sl.addStretch()
        cb = RippleButton(L("connect_device"), variant="primary")
        cb.setFixedHeight(36); cb.clicked.connect(self.go_bluetooth.emit)
        sl.addWidget(cb)
        lay.addWidget(sc)
        lay.addStretch()
        return self._sw(c)

    def _clabel(self, text):
        l = QLabel(text)
        l.setStyleSheet(f"color:{T('text2')}; font-size:12px;")
        return l

    def _stat_card(self, label, value, color, sub):
        card = Card(); card.setFixedHeight(96)
        lay = QVBoxLayout(card); lay.setContentsMargins(14, 10, 14, 10); lay.setSpacing(1)
        lay.addWidget(self._mlabel(label, T("text3"), 10))
        lay.addWidget(self._mlabel(value, color, 20, 800))
        lay.addWidget(self._mlabel(sub, T("text3"), 10))
        return card

    def _mlabel(self, text, color, size, weight=400):
        l = QLabel(text)
        l.setStyleSheet(f"color:{color}; font-size:{size}px; font-weight:{weight};")
        return l

    def _pill(self, text, color):
        l = QLabel(text)
        l.setStyleSheet(f"""
            color:{color}; background:rgba(0,212,170,0.08);
            border:1px solid {color}; border-radius:18px;
            padding:3px 12px; font-size:11px; font-weight:600;
        """)
        return l

    def _build_egg_tab(self):
        c = QWidget(); c.setStyleSheet(f"background:{T('bg')};")
        lay = QVBoxLayout(c); lay.setContentsMargins(18, 18, 18, 18); lay.setSpacing(12)

        card = Card()
        cl = QVBoxLayout(card); cl.setContentsMargins(18, 14, 18, 14)
        cl.addWidget(self._mlabel("Electrogastrography (EGG) Signal", T("text"), 14, 700))
        self._egg_full = RealtimeGraph("EGG (mV)", "graph_egg")
        self._egg_full.setMinimumHeight(200)
        cl.addWidget(self._egg_full)

        chips = QHBoxLayout()
        self._chip_freq = self._chip("Dominant Freq", "~3.0 cpm")
        self._chip_amp = self._chip("Amplitude", "0.50 mV")
        self._chip_status = self._chip("Status", "Normal")
        for ch in [self._chip_freq, self._chip_amp, self._chip_status]:
            chips.addWidget(ch)
        chips.addStretch()
        cl.addLayout(chips)
        lay.addWidget(card)

        note = Card()
        nl = QVBoxLayout(note); nl.setContentsMargins(18, 14, 18, 14)
        txt = QLabel("EGG measures the stomach's electrical activity. Normal gastric rhythm is 2–4 cpm. "
                     "Deviations may indicate gastric motility issues or stress-related disruption.")
        txt.setWordWrap(True)
        txt.setStyleSheet(f"color:{T('text2')}; font-size:12px;")
        nl.addWidget(txt)
        lay.addWidget(note)
        lay.addStretch()
        return self._sw(c)

    def _chip(self, label, value):
        frame = Card(); frame.setFixedHeight(58); frame.setMinimumWidth(100)
        fl = QVBoxLayout(frame); fl.setContentsMargins(10, 7, 10, 7); fl.setSpacing(1)
        fl.addWidget(self._mlabel(label, T("text3"), 9))
        fl.addWidget(self._mlabel(value, T("text"), 12, 600))
        return frame

    def _build_posture_tab(self):
        c = QWidget(); c.setStyleSheet(f"background:{T('bg')};")
        lay = QVBoxLayout(c); lay.setContentsMargins(18, 18, 18, 18); lay.setSpacing(12)

        row = QHBoxLayout(); row.setSpacing(12)

        gc = Card(); gc.setFixedWidth(190)
        gl = QVBoxLayout(gc); gl.setContentsMargins(14, 14, 14, 14)
        gl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gl.addWidget(self._mlabel("Posture Score", T("text2"), 11))
        self._gauge = PostureGauge()
        gl.addWidget(self._gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        self._gauge_lbl = QLabel("Good")
        self._gauge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._gauge_lbl.setStyleSheet(f"color:{T('success')}; font-size:13px; font-weight:700;")
        gl.addWidget(self._gauge_lbl)
        row.addWidget(gc)

        pgc = Card()
        pgl = QVBoxLayout(pgc); pgl.setContentsMargins(14, 10, 14, 10)
        pgl.addWidget(self._mlabel("Posture (Session)", T("text"), 13, 600))
        self._pos_full = RealtimeGraph("Score (%)", "graph_pos")
        self._pos_full.setMinimumHeight(150)
        pgl.addWidget(self._pos_full)
        row.addWidget(pgc)
        lay.addLayout(row)

        tips = Card()
        tl = QVBoxLayout(tips); tl.setContentsMargins(18, 14, 18, 14)
        tl.addWidget(self._mlabel("Posture Tips", T("text"), 13, 700))
        for tip in [
            "Keep your back straight and shoulders relaxed.",
            "Screen should be at eye level to reduce neck strain.",
            "Take a posture break every 30 minutes.",
            "Keep feet flat on the floor for lumbar support.",
        ]:
            lbl = QLabel(f"•  {tip}")
            lbl.setStyleSheet(f"color:{T('text2')}; font-size:12px; padding:2px 0;")
            tl.addWidget(lbl)
        lay.addWidget(tips)
        lay.addStretch()
        return self._sw(c)

    def _build_history_tab(self):
        c = QWidget(); c.setStyleSheet(f"background:{T('bg')};")
        lay = QVBoxLayout(c); lay.setContentsMargins(18, 18, 18, 18); lay.setSpacing(12)

        pr = QHBoxLayout()
        self._wk_btn = RippleButton(L("week"), variant="primary"); self._wk_btn.setFixedHeight(34)
        self._mo_btn = RippleButton(L("month"), variant="secondary"); self._mo_btn.setFixedHeight(34)
        self._wk_btn.clicked.connect(lambda: self._load_history(7))
        self._mo_btn.clicked.connect(lambda: self._load_history(30))
        pr.addWidget(self._wk_btn); pr.addWidget(self._mo_btn); pr.addStretch()
        lay.addLayout(pr)

        hc = Card()
        hl = QVBoxLayout(hc); hl.setContentsMargins(14, 10, 14, 10)
        self._hist_title = QLabel("Posture — Last 7 Days")
        self._hist_title.setStyleSheet(f"color:{T('text')}; font-size:13px; font-weight:600;")
        hl.addWidget(self._hist_title)
        self._hist_graph = RealtimeGraph("Posture Avg", "graph_pos")
        self._hist_graph.setMinimumHeight(150)
        hl.addWidget(self._hist_graph)
        lay.addWidget(hc)

        ec = Card()
        el = QVBoxLayout(ec); el.setContentsMargins(14, 10, 14, 10)
        self._egg_hist_title = QLabel("EGG Activity — Last 7 Days")
        self._egg_hist_title.setStyleSheet(f"color:{T('text')}; font-size:13px; font-weight:600;")
        el.addWidget(self._egg_hist_title)
        self._egg_hist_graph = RealtimeGraph("EGG Avg", "graph_egg")
        self._egg_hist_graph.setMinimumHeight(150)
        el.addWidget(self._egg_hist_graph)
        lay.addWidget(ec)

        tc = Card()
        tbl = QVBoxLayout(tc); tbl.setContentsMargins(14, 10, 14, 10)
        tbl.addWidget(self._mlabel("Daily Summary", T("text"), 13, 600))
        self._tbl_area = QVBoxLayout()
        tbl.addLayout(self._tbl_area)
        lay.addWidget(tc)
        lay.addStretch()

        self._load_history(7)
        return self._sw(c)

    def _load_history(self, days):
        keys = sorted(history_data.keys())[-days:]
        for k in keys:
            self._hist_graph.push(history_data[k]["posture_avg"])
            self._egg_hist_graph.push(history_data[k]["egg_avg"])
        self._hist_title.setText(f"Posture — Last {days} Days")
        self._egg_hist_title.setText(f"EGG Activity — Last {days} Days")

        while self._tbl_area.count():
            item = self._tbl_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        hr = QHBoxLayout()
        for h in ["Date", "Posture", "EGG", "Sessions"]:
            hr.addWidget(self._mlabel(h, T("text3"), 10, 600))
        self._tbl_area.addLayout(hr)

        for k in reversed(keys[-7:]):
            r = QHBoxLayout()
            d = history_data[k]
            for v in [k, f"{d['posture_avg']}%", str(d["egg_avg"]), str(d["sessions"])]:
                r.addWidget(self._mlabel(v, T("text"), 12))
            self._tbl_area.addLayout(r)

    def start_simulation(self):
        if self._simulator is None:
            self._simulator = DataSimulator()
            self._simulator.new_egg.connect(self._on_egg)
            self._simulator.new_posture.connect(self._on_posture)
            self._simulator.start()

    def stop_simulation(self):
        if self._simulator:
            self._simulator.stop()
            self._simulator = None

    def _on_egg(self, val):
        self._egg_ov.push(val)
        self._egg_full.push(val)
        amp_children = self._chip_amp.findChildren(QLabel)
        if len(amp_children) >= 2:
            amp_children[1].setText(f"{abs(val):.2f} mV")
        st_children = self._chip_status.findChildren(QLabel)
        if len(st_children) >= 2:
            st_children[1].setText("Active" if abs(val) > 0.6 else "Low" if abs(val) < 0.2 else "Normal")

    def _on_posture(self, val):
        score = int(val * 100)
        self._pos_ov.push(score)
        self._pos_full.push(score)
        self._gauge.set_score(score)
        if score >= 75:
            self._gauge_lbl.setText("Good")
            self._gauge_lbl.setStyleSheet(f"color:{T('success')}; font-size:13px; font-weight:700;")
        elif score >= 50:
            self._gauge_lbl.setText("Fair")
            self._gauge_lbl.setStyleSheet(f"color:{T('warning')}; font-size:13px; font-weight:700;")
        else:
            self._gauge_lbl.setText("Poor")
            self._gauge_lbl.setStyleSheet(f"color:{T('danger')}; font-size:13px; font-weight:700;")
        # Update stat card
        children = self._card_posture.findChildren(QLabel)
        if len(children) >= 2:
            children[1].setText(f"{score}%")

    def _refresh_status(self):
        connected = app_state["bt_connected"]
        self._conn_dot.setStyleSheet(f"color:{T('success' if connected else 'danger')}; font-size:13px;")
        self._conn_lbl.setText("  " + (L("connected") if connected else L("disconnected")))
        bat = app_state["battery"]
        self._bat_lbl.setText(f"{'🔋' if bat > 20 else '🪫'} {bat}%")


# ─────────────────────────────────────────────
#  SETTINGS SCREEN
# ─────────────────────────────────────────────
class SettingsScreen(QWidget):
    theme_changed = pyqtSignal()
    language_changed = pyqtSignal()
    go_back = pyqtSignal()
    logout = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        topbar = QWidget(); topbar.setFixedHeight(60)
        topbar.setStyleSheet(f"background:{T('surface')}; border-bottom:1px solid {T('border')};")
        tb = QHBoxLayout(topbar); tb.setContentsMargins(20, 0, 20, 0)

        back = RippleButton(L("back"), variant="ghost")
        back.clicked.connect(self.go_back.emit)
        tb.addWidget(back)
        tb.addStretch()
        title = QLabel(L("settings"))
        title.setStyleSheet(f"color:{T('text')}; font-size:17px; font-weight:700;")
        tb.addWidget(title)
        tb.addStretch()
        lo = RippleButton(L("logout"), variant="danger")
        lo.clicked.connect(self.logout.emit)
        tb.addWidget(lo)
        root.addWidget(topbar)

        scroll = QScrollArea(); scroll.setStyleSheet(f"background:{T('bg')}; border:none;")
        scroll.setWidgetResizable(True)
        content = QWidget(); content.setStyleSheet(f"background:{T('bg')};")
        scroll.setWidget(content)

        lay = QVBoxLayout(content); lay.setContentsMargins(28, 22, 28, 22); lay.setSpacing(18)

        # Theme
        tc = Card(); tl = QVBoxLayout(tc); tl.setContentsMargins(22, 18, 22, 18); tl.setSpacing(10)
        tl.addWidget(self._tlabel(L("theme")))
        br = QHBoxLayout()
        self._dark_btn = RippleButton(f"  {L('dark_mode')}", variant="primary" if current_theme == "dark" else "secondary")
        self._light_btn = RippleButton(f"  {L('light_mode')}", variant="primary" if current_theme == "light" else "secondary")
        for b in [self._dark_btn, self._light_btn]:
            b.setFixedHeight(42)
        self._dark_btn.clicked.connect(lambda: self._set_theme("dark"))
        self._light_btn.clicked.connect(lambda: self._set_theme("light"))
        br.addWidget(self._dark_btn); br.addWidget(self._light_btn)
        tl.addLayout(br)
        lay.addWidget(tc)

        # Language
        lc = Card(); ll = QVBoxLayout(lc); ll.setContentsMargins(22, 18, 22, 18); ll.setSpacing(10)
        ll.addWidget(self._tlabel(L("language")))
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(sorted(LANGUAGES.keys()))
        self._lang_combo.setCurrentText(current_language)
        self._lang_combo.setFixedHeight(44)
        self._lang_combo.setStyleSheet(f"""
            QComboBox {{ background:{T('surface2')}; color:{T('text')};
                border:1.5px solid {T('border')}; border-radius:10px; padding:0 14px; font-size:13px; }}
            QComboBox::drop-down {{ border:none; width:28px; }}
            QComboBox QAbstractItemView {{ background:{T('surface')}; color:{T('text')};
                border:1px solid {T('border')}; selection-background-color:{T('accent')}; }}
        """)
        self._lang_combo.currentTextChanged.connect(self._set_language)
        ll.addWidget(self._lang_combo)
        lay.addWidget(lc)

        # Change password
        pc = Card(); pl = QVBoxLayout(pc); pl.setContentsMargins(22, 18, 22, 18); pl.setSpacing(10)
        pl.addWidget(self._tlabel(L("change_password")))
        self._curr_pw = StyledInput(L("current_password"), is_password=True)
        self._new_pw = StyledInput(L("new_password"), is_password=True)
        self._conf_pw = StyledInput(L("confirm_password"), is_password=True)
        for w in [self._curr_pw, self._new_pw, self._conf_pw]:
            pl.addWidget(w)
        sb = RippleButton(L("save"), variant="primary"); sb.setFixedHeight(46)
        sb.clicked.connect(self._change_pw)
        pl.addWidget(sb)
        lay.addWidget(pc)

        # Device info
        dc = Card(); dl = QVBoxLayout(dc); dl.setContentsMargins(22, 18, 22, 18); dl.setSpacing(8)
        dl.addWidget(self._tlabel(L("device_info")))
        for k, v in [("Device", "GutBelt v1.0"), ("Firmware", L("firmware")),
                     ("Signal", f"{app_state['signal']} dBm"), ("Battery", f"{app_state['battery']}%")]:
            row = QHBoxLayout()
            row.addWidget(self._slabel(k, T("text2")))
            row.addStretch()
            row.addWidget(self._slabel(v, T("text"), weight=600))
            dl.addLayout(row)
        lay.addWidget(dc)
        lay.addStretch()
        root.addWidget(scroll)

    def _tlabel(self, text):
        l = QLabel(text)
        l.setStyleSheet(f"color:{T('text')}; font-size:14px; font-weight:700;")
        return l

    def _slabel(self, text, color, weight=400):
        l = QLabel(text)
        l.setStyleSheet(f"color:{color}; font-size:12px; font-weight:{weight};")
        return l

    def _set_theme(self, theme):
        global current_theme
        current_theme = theme
        self.theme_changed.emit()

    def _set_language(self, lang):
        global current_language
        current_language = lang
        self.language_changed.emit()

    def _change_pw(self):
        if self._new_pw.text() != self._conf_pw.text():
            QMessageBox.warning(self, "Error", "New passwords do not match.")
            return
        if len(self._new_pw.text()) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
            return
        QMessageBox.information(self, "Success", "Password updated successfully.")
        self._curr_pw.clear(); self._new_pw.clear(); self._conf_pw.clear()


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GutAngle")
        self.setMinimumSize(900, 660)
        self.resize(1080, 700)
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        self._build_screens()
        self._stack.setCurrentWidget(self._loading)

    def _build_screens(self):
        self._loading = LoadingScreen()
        self._auth = AuthScreen()
        self._bt = BluetoothScreen()
        self._dashboard = DashboardScreen()
        self._settings = SettingsScreen()

        for w in [self._loading, self._auth, self._bt, self._dashboard, self._settings]:
            self._stack.addWidget(w)

        self._loading.done.connect(lambda: self._stack.setCurrentWidget(self._auth))
        self._auth.login_success.connect(lambda: self._stack.setCurrentWidget(self._bt))
        self._bt.connected.connect(self._to_dashboard)
        self._bt.skip.connect(self._to_dashboard)
        self._dashboard.go_settings.connect(lambda: self._stack.setCurrentWidget(self._settings))
        self._dashboard.go_bluetooth.connect(lambda: self._stack.setCurrentWidget(self._bt))
        self._settings.go_back.connect(lambda: self._stack.setCurrentWidget(self._dashboard))
        self._settings.logout.connect(self._do_logout)
        self._settings.theme_changed.connect(self._rebuild)
        self._settings.language_changed.connect(self._rebuild)

    def _to_dashboard(self):
        self._stack.setCurrentWidget(self._dashboard)
        self._dashboard.start_simulation()

    def _do_logout(self):
        self._dashboard.stop_simulation()
        self._stack.setCurrentWidget(self._auth)

    def _rebuild(self):
        """Rebuild all screens when theme or language changes."""
        self._dashboard.stop_simulation()
        while self._stack.count():
            self._stack.removeWidget(self._stack.widget(0))
        self._build_screens()
        self.setStyleSheet(f"QMainWindow {{ background:{T('bg')}; }}")
        self._stack.setCurrentWidget(self._settings)
        self._dashboard.start_simulation()

    def closeEvent(self, event):
        self._dashboard.stop_simulation()
        super().closeEvent(event)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GutAngle")
    app.setStyle("Fusion")

    palette = QPalette()
    bg = QColor(THEMES["dark"]["bg"])
    fg = QColor(THEMES["dark"]["text"])
    surf = QColor(THEMES["dark"]["surface"])
    acc = QColor(THEMES["dark"]["accent"])

    palette.setColor(QPalette.ColorRole.Window, bg)
    palette.setColor(QPalette.ColorRole.WindowText, fg)
    palette.setColor(QPalette.ColorRole.Base, surf)
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(THEMES["dark"]["surface2"]))
    palette.setColor(QPalette.ColorRole.Text, fg)
    palette.setColor(QPalette.ColorRole.Button, surf)
    palette.setColor(QPalette.ColorRole.ButtonText, fg)
    palette.setColor(QPalette.ColorRole.Highlight, acc)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, surf)
    palette.setColor(QPalette.ColorRole.ToolTipText, fg)
    app.setPalette(palette)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
