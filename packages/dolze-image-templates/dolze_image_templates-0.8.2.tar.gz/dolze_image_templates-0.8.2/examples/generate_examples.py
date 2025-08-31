"""
Example script demonstrating how to use the Dolze Templates library.

This script shows how to:
1. Load templates from JSON files
2. Render templates with different data
3. Save the generated images
"""

from cgitb import text
import os
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path so we can import the package
import sys

sys.path.append(str(Path(__file__).parent.parent))

from dolze_image_templates import (
    get_template_registry,
    configure,
    get_font_manager,
)

# Initialize font manager to scan for fonts
font_manager = get_font_manager()
print("Font manager initialized. Available fonts:", font_manager.list_fonts())

# Configure the library
configure(
    templates_dir=os.path.join(
        os.path.dirname(__file__), "..", "dolze_image_templates", "templates"
    ),
    output_dir=os.path.join(os.path.dirname(__file__), "output"),
)


def generate_business_template(templateName: str):
    """Generate a business template post."""
    # Get the template registry
    registry = get_template_registry()
    template_data = {
        "cta_text": "LEARN MORE",
        "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg",
        "image_url": "https://images.pexels.com/photos/235986/pexels-photo-235986.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "cta_image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d",
        "heading": "plan your day in a snap",
        "subheading": "Driving success",
        "contact_email": "contact@business.com",
        "contact_phone": "+1-800-555-1234",
        "website_url": "dolze.ai /download",
        "quote": "The only way to do great work is to love what you do.",
        "theme_color": "#44EC9D",
        "user_avatar": "https://img.freepik.com/free-vector/blue-circle-with-white-user_78370-4707.jpg?ga=GA1.1.1623013982.1744968336&semt=ais_hybrid&w=740",
        "user_name": "Alex Johnson",
        "user_title": "Marketing Director, TechCorp",
        "testimonial_text": "This product has completely transformed how we works. The intuitive interface and powerful features have saved us countless hours.",
    }
    # Template data mapping
    if templateName == "calendar_app_promo":
        template_data = {
            "cta_text": "LEARN MORE",
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg",
            "image_url": "https://www.calendar.com/wp-content/uploads/2019/09/CalendarAndroidApp.png.webp",
            "cta_image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d",
            "heading": "streamline your business with Dolze",
            "subheading": "Your AI-powered business assistant",
            "contact_email": "contact@dolze.ai",
            "contact_phone": "+1-800-555-1234",
            "website_url": "dolze.ai/download",
            "quote": "Simplify your business, amplify your success.",
            "theme_color": "#ffc524",
            "user_avatar": "https://img.freepik.com/free-vector/blue-circle-with-white-user_78370-4707.jpg?ga=GA1.1.1623013982.1744968336&semt=ais_hybrid&w=740",
            "user_name": "Maya Patel",
            "user_title": "Founder, Artisan Gems",
            "testimonial_text": "Dolze transformed how I manage my jewelry store. The AI team handles marketing and customer care seamlessly.",
        }
    elif templateName == "testimonials_template":
        template_data = {
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/download",
            "user_avatar": "https://img.freepik.com/free-vector/isolated-young-handsome-man-different-poses-white-background-illustration_632498-859.jpg?ga=GA1.1.1623013982.1744968336&semt=ais_hybrid&w=740",
            "user_name": "Maya Patel",
            "user_title": "Jewelry Store Owner",
            "testimonial_text": "Dolze’s AI managers helped me grow my online sales and freed up my time to focus on crafting.",
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg",
        }
    elif templateName == "blog_post" or templateName == "blog_post_2":
        template_data = {
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/blog",
            "title": "How Dolze simplifies digital marketing for small businesses",
            "author": "@dolze_ai",
            "read_time": "4",
            "publish_date": "2025-06-22",
            "excerpt": "Discover how Dolze’s AI managers help small business owners streamline marketing and customer engagement.",
            "image_url": "https://img.freepik.com/free-vector/underwater-ocean-reef-coral-background_107791-1853.jpg",
            "logo_url": "https://img.freepik.com/free-vector/gradient-s-letter-logo_343694-1365.jpg",
        }
    elif templateName == "qa_template" or templateName == "qa_template_2":
        template_data = {
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg",
            "question": "How does Dolze help small businesses?",
            "answer": "Dolze automates marketing, customer care, and operations using AI, saving time and boosting sales.",
            "username": "@dolze_ai",
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/blog",
        }
    elif templateName == "quote_template_2":
        template_data = {
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg",
            "quote1": "Simplify your business,",
            "quote2": "amplify your success.",
            "username": "@dolze_ai",
            "website_url": "dolze.ai",
            "theme_color": "#ffc524",
        }
    elif templateName == "education_info" or templateName == "education_info_2":
        template_data = {
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/blog",
            "product_name": "Dolze AI Managers",
            "product_info": "AI-powered assistants that automate marketing, customer care, and operations for small businesses.",
            "author": "@dolze_ai",
            "read_time": "4",
            "image_url": "https://img.freepik.com/free-photo/portrait-young-businesswoman-holding-eyeglasses-hand-against-gray-backdrop_23-2148029483.jpg?ga=GA1.1.1623013982.1744968336&semt=ais_hybrid&w=740",
            "logo_url": "https://img.freepik.com/free-vector/gradient-s-letter-logo_343694-1365.jpg",
        }
    elif templateName == "product_promotion_2":
        template_data = {
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg?w=200&h=200&white=true",
            "image_url": "https://media.licdn.com/dms/image/v2/D4D12AQGnbgq78a4LMg/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1677634984855?e=1755734400&v=beta&t=PS0JBTOx91C-z1Tb4Ky4NOnQeRosuW-7i1GIDUj088o",
            "quote1": "Manage your business",
            "quote2": "with Dolze’s AI team",
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/download",
        }
    elif templateName == "product_promotion":
        template_data = {
            "image_url": "https://media.licdn.com/dms/image/v2/D4D12AQGnbgq78a4LMg/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1677634984855?e=1755734400&v=beta&t=PS0JBTOx91C-z1Tb4Ky4NOnQeRosuW-7i1GIDUj088o",
            "heading": "Dolze AI Managers",
            "subheading": "Your digital business team made simple witn Dolze ai. Your digital business team made simple witn Dolze ai.Your digital business team made simple witn Dolze ai.",
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg?w=200&h=200&white=true",
            "cta_text": "LEARN MORE",
            "website_url": "dolze.ai/download",
            "theme_color": "#ffc524",
        }
    elif templateName == "product_showcase" or templateName == "product_showcase_2":
        template_data = {
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg?w=200&h=200&white=true",
            "product_image": "https://media.istockphoto.com/id/171384959/photo/executive-office-chair.jpg?s=612x612&w=0&k=20&c=5vRz91x_JdXHGrzWoDxtj7xEYvI35ls3pDfysHgd57M=",
            "product_name": "Dolze AI Manager",
            "product_price": "$52",
            "product_description": "AI assistant that automates your marketing and customer care tasks.",
            "theme_color": "#ffc524",
            "badge_text": "Top Rated",
        }
    elif templateName == "coming_soon_page":
        template_data = {
            "header_text": "Dolze is Coming",
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/download",
            "contact_email": "contact@dolze.ai",
        }
    elif templateName == "coming_soon_post_2":
        template_data = {
            "text": "3 days left until Dolze launches to simplify your business!",
            "cta_text": "STAY TUNEDSTAY TUNEDSTAY TUNEDSTAY TUNED",
            "website_url": "dolze.ai/download",
        }
    elif templateName == "hiring_post":
        template_data = {
            "theme_color": "#ffc524",
            "heading": "Join Our Team",
            "subheading": "Passionate about AI and business? We want you!",
            "job_title": "Social Media Lead",
            "website_url": "dolze.ai/careers",
            "company_name": "Dolze",
            "cta_text": "Apply Now!",
        }
    elif templateName == "product_sale":
        template_data = {
            "cta_text": "Shop Now",
            "sale_end_text": "December 31, 2023",
            "product_name": "Laptop Comparison Hub",
            "product_description": "Discover the ultimate laptop guide with comprehensive reviews ",
            "sale_heading": "Expert Insights",
            "sale_text": "Limited Time Offer",
            "background_image_url": "Generate a prompt for an attractive laptop image on a clean background with a comparison chart overlay",
            "theme_color": "#4A90E2",
            "product_image": "https://t4.ftcdn.net/jpg/14/68/86/23/360_F_1468862392_uFV91fk0dgIrSUpRhYUqw7OcikgXpelA.webp",
            "logo_url": "https://img.freepik.com/free-vector/gradient-s-letter-logo_343694-1365.jpg",
        }
    elif templateName == "product_marketing":
        template_data = {
            "social_handle": "@dolze.ai",
            "heading": "Unlock AI-Driven Growth",
            "description": "Transform your marketing with Dolze.ai—an AI-powered SaaS that analyzes data, crafts high-performing campaigns, and scales your reach effortlessly.",
            "background_image_url": "https://img.freepik.com/free-photo/open-laptop-with-glowing-screen-notepad-table-night_169016-53665.jpg?t=st=1752265269~exp=1752268869~hmac=ffb2b5be8ce1b9130640bfeb4d11ec00d46974ad6c576e0857b3b6bbdffb7e65&w=2000",
        }

        # https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/mbcEtwwJKCf7jn4GnfzFm1thlhC3/6829afe6925fb5ef8c087942/business_assets/BlackRedGeometricBusinessMarketingInstagramPost.png

        # {
        #     "product_name": "Dolze AI Subscription",
        #     "sale_text": "Flat 15% OFF",
        #     "product_description": "Automate your business with Dolze’s AI managers.",
        #     "cta_text": "BUY NOW",
        #     "sale_end_text": "Ends 10th July at midnight",
        #     "sale_heading": "Flash Sale!"
        # }
    elif templateName == "summer_sale_promotion":
        template_data = {
            "background_image_url": "https://ideogram.ai/api/images/ephemeral/pxydLJjkTWaOReUD7p6h6w.png?exp=1751984498&sig=f0603e9215d75bcc2603d93f7114c23761c9f84aca28c651ac71f16c05deb9b0",
            "theme_color": "#ffc524",
            "brand_name": "Dolze AI",
            "sale_heading": "Summer Sale!",
            "sale_description": "Refresh your business with Dolze’s AI solutions. Don’t miss out! or similar in under 10 words",
            "discount_text": "Up to 50% Off",
            "social_handle": "@dolze_ai",
            "contact_number": "+123-456-7890",
        }
    elif templateName == "product_showcase_3":
        template_data = {
            "product_name": "Dolze AI Assistant",
            "product_description": "Start automating your business today for just $15.99/month.",
            "cta_text": "Get Started",
            "product_image": "https://media-public.canva.com/A6MI4/MAGbaAA6MI4/1/s3.png",
            "website_url": "dolze.ai/shop",
        }
    elif templateName == "quote_template":
        template_data = {
            "quote": "The only way to do your best work is to love what you do and let Dolze handle the rest.",
            "social_handle": "@dolze_ai",
        }
    elif templateName == "product_service_minimal":
        template_data = {
            "text": "Simplify your business with Dolze’s AI-powered services.",
            "website_url": "dolze.ai/shop",
            "product_image": "https://img.freepik.com/free-photo/furniture-background-clean-wall-wood_1253-666.jpg?t=st=1751691647~exp=1751695247~hmac=d5a191ec06d19843dcb271039a8e46a0374789e5a09714f0335e34139da25e43&w=1380",
        }
    elif templateName == "product_showcase_4":
        template_data = {
            "offer_text": "Only with Dolze",
            "product_image": "https://media-public.canva.com/A6MI4/MAGbaAA6MI4/1/s3.png",
            "website_url": "dolze.ai/shop",
            "theme_color": "#ffc524",
        }
    elif templateName == "coming_soon":
        template_data = {
            "background_image_url": "https://img.freepik.com/free-photo/close-up-meat-with-baked-potatoes-eggplant-tomato-pepper-decorated-with-pomegranate-wooden-bark_176474-2443.jpg?t=st=1751704275~exp=1751707875~hmac=1bb3b262f6a44e5898fcf5f70fb1be071981253d1b1db308ac972cf7f0e9e0ab&w=1380",
            "text": "COMING SOON",
            "website_url": "dolze.ai",
            "business_name": "Dolze AI",
            "logo_url": "https://img.freepik.com/free-vector/detailed-chef-logo-template_23-2148987940.jpg?t=st=1751704940~exp=1751708540~hmac=d327a7d9b9b689564d411580764d3308e521d60ea9b470ce9ed0c75b978d29d7&w=1380",
        }
    elif templateName == "event_day":
        template_data = {
            "celebration_text": "SPECIAL OFFER",
            "celebration_name": "Launch Day",
            "celebration_description": "Celebrate Dolze’s launch with exclusive offers for your business!",
            "celebration_image": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/9b130834-14ac-4624-b794-2287749ef906.png",
            "sale_info": "Get 10% off your first subscription",
        }
    elif templateName == "product_showcase_5":
        template_data = {
            "heading": "Healthy living happy living",
            "subheading": "Healthy eating is about choosing fresh, balanced meals to nourish your body and mind. Start small, and enjoy the benefits every day!",
            "cta_text": "Book Now",
            "contact_number": "+09876543211",
            "website_url": "dolze.ai",
            "product_image": "https://rukminim2.flixcart.com/image/100/100/xif0q/mobile/k/l/l/-original-imagtc5fz9spysyk.jpeg?q=90",
        }
    elif templateName == "brand_info":
        template_data = {
            "product_image": "https://plus.unsplash.com/premium_photo-1677087121676-2acaaae5b3c8?w=1200&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8b2ZmaWNlfGVufDB8MnwwfHx8MA%3D%3D",
            "heading": "build a brand in 10 days",
            "subheading": "build a brand in under 10 days if not return the money to usif not return the money to usif not return the money to us",
            "cta_text": "Book Now Today",
            "website_url": "dolze.ai",
            "theme_color": "#214aff",
        }
    elif templateName == "brand_info_2":
        template_data = {
            "service_hook": "Require a brand new",
            "service_name": "Website ?",
            "content": "our team of expert devlopers will make sure you will get the best website available in the market",
            "contact_number": "+123-456-7890",
            "website_url": "www.dolze.ai/careers",
            "product_image": "https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            "contact_email": "contact@dolze.ai",
        }
    elif templateName == "product_sale_2":
        template_data = {
            "theme_color": "#fffdf7",
            "product_image": "https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            "heading": "Digital planner",
            "usp1": "Undated Planner",
            "usp2": "Hyperlinked Pages",
            "cta_text": "Book Now",
            "product_highlights": "300+ pages",
            "social_handle": "@dolze_ai",
            "business_name": "Dolze AI",
        }
    elif templateName == "product_feature":
        template_data = {
            "product_image": "https://media-public.canva.com/cOgj8/MAGczGcOgj8/1/s2.png",
            "feature1": "This nasal drop is good",
            "feature2": "This nasal drop is really great product",
            "feature3": "Clears nose with ease",
            "feature4": "This nasal drop is really great product",
            "feature_title": "Features",
            "product_name": "Nasal Drops",
        }
    elif templateName == "event_alert":
        template_data = {
            "company_name": "Dolze AI",
            "event_type": "FREE WEBINAR",
            "event_date": "July 16",
            "event_time": "10:00 AM - 12:00 PM",
            "event_venue": "Online",
            "event_highlight": "How Dolze saves time for you to make your business successful",
            "register_details": "Registration Link in bio",
            "product_image": "https://media-public.canva.com/A6MI4/MAGbaAA6MI4/1/s3.png",
        }
    elif templateName == "sale_alert":
        template_data = {
            "sale_heading": "Technology Sale",
            "sale_description": "Special Sale Only in August",
            "cta_text": "Shop Now!",
            "website_url": "www.dolze.ai",
            "sale_text": "30% off",
            "product_image": "https://static.vecteezy.com/system/resources/previews/055/473/101/large_2x/cute-cartoon-teddy-bear-sitting-perfect-for-children-s-products-free-png.png",
        }
    elif templateName == "testimonials":
        template_data = {
            "product_image": "https://img.freepik.com/free-photo/portrait-white-man-isolated_53876-40306.jpg?t=st=1752413811~exp=1752417411~hmac=afeea5e512a3cef81bfab9b893856637b99d6b4a617883396766b8ced0981805&w=2000",
            "name": "Sagar Giri",
            "greeting": "Meet our developers",
            "designation": '" I have had a passion for coding since I was a kid. I have developed in the field of software and now with Rimberio I help our customers solve their digital product problems. "',
            "social_handle": "@dolze_ai",
        }
    elif templateName == "event_announcement":
        template_data = {
            "event_image": "https://img.freepik.com/free-photo/business-people-office_144627-3800.jpg",
            "event_name": "Tech Conference 2024",
            "event_description": "Join us for the biggest tech event of the year featuring industry leaders and innovative solutions.",
            "company_name": "Dolze AI",
        }
    elif templateName == "event_announcement":
        template_data = {
            "event_image": "https://plus.unsplash.com/premium_photo-1664392147011-2a720f214e01?q=80&w=578&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            "event_name": "Sale Alert",
            "company_name": "Dolze AI",
            "event_description": "Sale starting on our grocery store for all users on all platforms",
        }

    elif templateName == "testing_template":
        template_data = {
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/blog",
            "excerpt": "The best PLG founders, startups, strategists, metrics and community.",
            "text_bold": "Evey week",
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
            "background_image_url": "https://i.postimg.cc/L82YpK4b/Frame-1244832595.png",
        }

    elif templateName == "orchid_baby_post":
        template_data = {
            "theme_color": "#ffc524",
            "website_url": "dolze.ai/blog",
            "button_text": "Learn more today",
            "excerpt": "Average baby\nor super baby?",
            "text_subtext": "The choice is yours",
            "logo_url": "https://i.postimg.cc/d3qQry0D/Frame-1244832596.png",
            "background_image_url": "https://i.postimg.cc/wvmG6fcd/image-10.png",
            "baby_image": "https://i.postimg.cc/vZ78mhhf/image-11.png",
            "gradient_bg": "https://i.postimg.cc/cJgPk4zh/Frame-1244832597.png",
        }

    elif templateName == "super_king_burgers_template":
        template_data = {
            "background_image_url": "https://i.postimg.cc/bJzN2BL1/jhunelle-francis-sardido-PPtcyr-AB5-UQ-unsplash.jpg",
            "badge_number": "Super Burgers",
            "subtitle": "CULINARY EXPLORATIONS",
            "main_title": "Super King Burgers",
            "description": "Discover the most unique flavors and try new food experiences. Limited spots available!",
            "button_text": "ORDER NOW",
            "theme_color": "#FFD700",
            "gradient_bg": "https://i.postimg.cc/WbfFcT8C/Frame-1244832597.png",
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
        }

    elif templateName == "shelf_engine_template":
        template_data = {
            "logo_url": "https://i.postimg.cc/d3qQry0D/Frame-1244832596.png",
            "headline": "14% of fresh juice spoils",
            "subtitle": "Accurate demand forecasting for perishable foods.",
            "cta_text": "Free Profit Analysis",
            "background_image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=800&fit=crop",
            "bottles_image": "https://i.postimg.cc/BvHr6WwQ/image-13.png",
            "theme_color": "#20B2AA",
        }

    elif templateName == "cookie_poster":
        template_data = {
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
            "headline": "GET 25% OFF",
            "subtitle": "Healthy Snacking Made Easy!",
            "cta_text": "BESTEL NU",
            "background_image_url": "https://i.postimg.cc/ht54k7XW/cookiebg.png",
            "cookie_image_url": "https://i.postimg.cc/NM1g2JpB/cookie.png",
            "theme_color": "#F7A824",
        }

    elif templateName == "juice_poster":
        template_data = {
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
            "headline": "GET 25% OFF",
            "subtitle": "Healthy Snacking Made Easy!",
            "cta_text": "BESTEL NU",
            "background_image_url": "https://i.postimg.cc/cCN5RtSB/image-24.png",
            "juice_image_url": "https://i.postimg.cc/9MPBjx6y/Frame-1244832601.png",
            "theme_color": "#383838",
        }

    elif templateName == "healthy_food_template":
        template_data = {
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
            "salad_image_url": "https://i.postimg.cc/rwt33QRy/image-26.png",
            "background_url": "https://i.postimg.cc/yxp9mh72/image-27.png",
            "arrow_url": "https://i.postimg.cc/SN75LJ9V/Layer-1.png",
            "headline": "Delicious",
            "subtitle": "HEALTHY FOOD",
            "price": "$17",
            "price_note": "ONLY",
            "footer_text_left": "@USERNAME",
            "footer_text_right": "9876 6543 3210",
            "theme_color": "#62A851",
        }

    elif templateName == "grilled_chicken_template":
        template_data = {
            "background_image": "https://i.postimg.cc/ydBhzwjk/image-29.png",
            "logo_url": "https://i.postimg.cc/d3qQry0D/Frame-1244832596.png",
            "chicken_image_url": "https://i.postimg.cc/PfZqsPcV/image-31.png",
            "headline_top": "DELICIOUS",
            "headline_bottom": "GRILLED CHICKEN",
            "price": "$14",
            "price_note": "ONLY",
            "contact_number": "987 6543 3210",
            "address_line1": "123 STREET, AREA NAME",
            "address_line2": "YOUR CITY, STATE",
            "username": "@username",
            "theme_color": "#F4A300",
        }

    elif templateName == "juice_poster_gif":
        template_data = {
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
            "headline": "FRESH JUICE",
            "subtitle": "100% Natural, No Added Sugar",
            "cta_text": "ORDER NOW",
            "background_image_url": "https://i.postimg.cc/cCN5RtSB/image-24.png",
            "juice_image_url": "https://i.postimg.cc/9MPBjx6y/Frame-1244832601.png",
            "theme_color": "#383838",
        }

    elif templateName == "learn_gif_template":
        template_data = {
            "headline": "Learn Something New",
            "feature1": "Interactive courses",
            "feature2": "Expert instructors",
            "feature3": "Flexible schedule",
            "feature4": "Certificate on completion",
            "background_color": "#6200EA",
            "cta_color": "#FF5722",
            "cta_text": "Enroll Now",
            "cta_text_color": "#FFFFFF",
        }

    elif templateName == "shoe_ad_template":
        template_data = {
            "product_image": "https://i.postimg.cc/PfZqsPcV/image-31.png",
            "product_name": "UltraBoost Running Shoes",
            "product_description": "Lightweight and responsive running shoes with superior cushioning for maximum comfort",
            "price": "$129.99",
            "cta_text": "Shop Now",
            "theme_color": "#00BCD4",
            "shoe_image_url": "https://i.postimg.cc/PfZqsPcV/image-31.png",
        }

    elif templateName == "stamped_loyalty_template":
        template_data = {
            "logo_url": "https://i.postimg.cc/R0t3BS5K/logo.png",
            "heading": "Loyalty Rewards",
            "subheading": "Earn points with every purchase",
            "points": "250",
            "theme_color": "#795548",
            "cta_text": "Redeem Now",
        }

    elif templateName == "status_indicator":
        template_data = {
            "status_text": "In Progress",
            "status_color": "#FFC107",
            "description": "Your order is being processed and will be shipped soon",
        }

    elif templateName == "super_king_burgers_template":
        template_data = {
            "product_image": "https://i.postimg.cc/L8nHzQs3/burger.png",
            "product_name": "Super King Burger",
            "product_description": "Triple patty burger with cheese, bacon, and our special sauce",
            "price": "$12.99",
            "theme_color": "#D84315",
        }

    # Render the template with the data
    output_path = os.path.join("output", f"{templateName}.png")
    rendered_image = registry.render_template(
        templateName,
        template_data,
        output_path=output_path,
    )

    print(f"Template saved to {os.path.abspath(output_path)}")
    return rendered_image


def main():
    """Generate all example templates."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Generate all templates
        templates = [
            # "calendar_app_promo",
            # "testimonials_template",
            # "blog_post",
            # "education_info",
            # "education_info_2",
            # "calendar_app_promo",
            # "blog_post_2",
            # "education_info",
            # "product_promotion_2",
            # "promotional_banner",
            # "product_promotion",
            # "qa_template",
            # "quote_template",
            # "quote_template_2",
            # "product_showcase",
            # "testimonials_template_2",
            # "product_showcase_2",
            # "product_showcase_3",
            # "qa_template_2",
            # "qa_template",
            # "education_info_2",
            # "coming_soon_page",
            # "coming_soon_post_2",
            # "product_marketing",
            # "brand_info_2",
            # "product_sale_2",
            # "product_feature",
            # "event_alert"
            # "sale_alert",
            # "testimonials",
            # "event_announcement",
            # "hiring_post",
            # "product_sale",
            # "summer_sale_promotion",
            # "testing_template",
            # "product_showcase_5",
            # "brand_info"
            # "qa2",
            # "product_showcase_4",
            # "cafe_post",
            "cookie_poster",
            "juice_poster",
            "juice_poster_gif",
            "grilled_chicken_template",
            "healthy_food_template",
            "learn_gif_template",
            "orchid_baby_post",
            "shelf_engine_template",
            "shoe_ad_template",
            "stamped_loyalty_template",
            "status_indicator",
            "super_king_burgers_template",
            "testing_template",
        ]
        for template in templates:
            generate_business_template(template)

        print("\nAll examples generated successfully!")
    except Exception as e:
        print(f"\nError generating examples: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
