from .core import multiply, insta_recovery

__version__ = "0.1.0"

banner = f"""
📘 pyloch v{__version__}
=======================
مرحبًا بك في مكتبة *pyloch* 🎉
مكتبة تجريبية للرياضيات + أمثلة HTTP.

🔢 الدوال المتوفرة:
- multiply(a, b): ضرب رقمين
- insta_recovery(username): محاكاة طلب استرجاع إنستغرام

مثال سريع:
>>> from pyloch import multiply, insta_recovery
>>> multiply(6, 7)
42
>>> insta_recovery("example_user")
"Send Email : e***@gmail.com"
"""

print(banner)