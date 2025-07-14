from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/terms", response_class=HTMLResponse)
def get_terms():
    return """
    <html>
        <head>
            <title>Terms of Service - Vibe</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #333; }
                h2 { color: #666; margin-top: 30px; }
                p { margin-bottom: 15px; }
            </style>
        </head>
        <body>
            <h1>Terms of Service</h1>
            <p>Last updated: January 2025</p>
            
            <h2>1. Acceptance of Terms</h2>
            <p>By accessing and using Vibe, you accept and agree to be bound by the terms and provision of this agreement.</p>
            
            <h2>2. Use License</h2>
            <p>Permission is granted to temporarily use Vibe for personal, non-commercial transitory viewing only.</p>
            
            <h2>3. Disclaimer</h2>
            <p>The materials on Vibe are provided on an 'as is' basis. Vibe makes no warranties, expressed or implied.</p>
            
            <h2>4. Limitations</h2>
            <p>In no event shall Vibe or its suppliers be liable for any damages arising out of the use or inability to use the materials on Vibe.</p>
            
            <h2>5. Contact Information</h2>
            <p>If you have any questions about these Terms of Service, please contact us.</p>
        </body>
    </html>
    """

@router.get("/privacy", response_class=HTMLResponse)
def get_privacy():
    return """
    <html>
        <head>
            <title>Privacy Policy - Vibe</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #333; }
                h2 { color: #666; margin-top: 30px; }
                p { margin-bottom: 15px; }
            </style>
        </head>
        <body>
            <h1>Privacy Policy</h1>
            <p>Last updated: January 2025</p>
            
            <h2>1. Information We Collect</h2>
            <p>We collect information you provide directly to us, such as when you create an account, post content, or contact us.</p>
            
            <h2>2. How We Use Your Information</h2>
            <p>We use the information we collect to provide, maintain, and improve our services.</p>
            
            <h2>3. Information Sharing</h2>
            <p>We do not sell, trade, or otherwise transfer your personal information to third parties without your consent.</p>
            
            <h2>4. Data Security</h2>
            <p>We implement appropriate security measures to protect your personal information.</p>
            
            <h2>5. Your Rights</h2>
            <p>You have the right to access, update, or delete your personal information at any time.</p>
            
            <h2>6. Contact Us</h2>
            <p>If you have any questions about this Privacy Policy, please contact us.</p>
        </body>
    </html>
    """