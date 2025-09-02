import cloudscraper
from bs4 import BeautifulSoup
import time
import re
import os
import pandas as pd
import signal
import sys
import json
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime
import html
import unicodedata
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import logging

# MongoDB connection
MONGO_URI = "mongodb+srv://quokkalabs:quokkalabs@cluster0.tuksmdq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.clutch_scraper
companies_collection = db.companies

def setup_mongodb():
    """Setup MongoDB indexes"""
    try:
        # Create unique index on company_url
        companies_collection.create_index("company_url", unique=True)
        print("✅ MongoDB connected and indexes created")
        return True
    except Exception as e:
        print(f"❌ MongoDB setup failed: {e}")
        return False

def is_company_already_scraped(company_url):
    """Check if company already exists in MongoDB"""
    try:
        result = companies_collection.find_one(
            {"company_url": company_url}, 
            {"_id": 1}  # Only return _id for faster query
        )
        return result is not None
    except Exception as e:
        print(f"Error checking company in DB: {e}")
        return False

def save_company_to_mongodb(company_data):
    """Save company data to MongoDB"""
    try:
        document = {
            "company_url": company_data['company_url'],
            "company_name": company_data['company_name'],
            "scraped_at": datetime.now(),
            "contacts": company_data['reviews'],  # Your contact data
            "total_contacts": len(company_data['reviews'])
        }
        
        result = companies_collection.insert_one(document)
        print(f"    💾 Saved to MongoDB with ID: {result.inserted_id}")
        return True
        
    except DuplicateKeyError:
        print(f"    ⚠️  Company already exists in database")
        return False
    except Exception as e:
        print(f"    ❌ Error saving to MongoDB: {e}")
        return False
    
    
def clean_text(text):
    """Clean text from encoding issues and HTML entities"""
    if not text:
        return text
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Fix common encoding issues
    text = text.replace('Ã§', 'ç').replace('Ã¡', 'á').replace('Ã©', 'é')
    text = text.replace('Ã­', 'í').replace('Ã³', 'ó').replace('Ãº', 'ú')
    text = text.replace('Ã¼', 'ü').replace('Ã', 'à').replace('Ã±', 'ñ')
    
    return text.strip()

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self._kill_handler)
        signal.signal(signal.SIGTERM, self._kill_handler)

    def _kill_handler(self, signum, frame):
        print("\n⚠️  Stopping scraper gracefully... Please wait.")
        self.kill_now = True

def display_categories():
    """Display available categories for user selection"""
    categories = {
        1: ("Advertising & Marketing", {
            1: ("Advertising", "agencies"),
            2: ("Full Service Digital", "agencies/digital"),
            3: ("Digital Strategy", "agencies/digital-strategy"),
            4: ("Digital Marketing", "agencies/digital-marketing"),
            5: ("Social Media Marketing", "agencies/social-media-marketing"),
            6: ("Content Marketing", "agencies/content-marketing"),
            7: ("Email Marketing", "agencies/email"),
            8: ("Inbound Marketing", "agencies/inbound-marketing"),
            9: ("Direct Marketing", "agencies/direct-marketing"),
            10: ("Mobile & App Marketing", "agencies/app-marketing"),
            11: ("Event Marketing", "agencies/event"),
            12: ("Experiential Marketing", "agencies/experiential"),
            13: ("Creative", "agencies/creative"),
            14: ("Public Relations", "pr-firms"),
            15: ("Video Production", "agencies/video-production"),
            16: ("Branding", "agencies/branding"),
            17: ("Naming", "agencies/naming"),
            18: ("PPC", "agencies/ppc"),
            19: ("SEO", "seo-firms"),
            20: ("SEM", "agencies/sem"),
            21: ("Conversion Optimization", "agencies/conversion-optimization"),
            22: ("Market Research", "agencies/market-research"),
            23: ("Media Planning and Buying", "agencies/media-buying"),
            24: ("Marketing Automation", "it-services/marketing-automation"),
        }),
        2: ("Development", {
            1: ("Web Developers", "web-developers"),
            2: ("Software Developers", "developers"),
            3: ("Mobile App Development", "app-developers"),
            4: ("iPhone App Development", "app-developers/iphone"),
            5: ("Android App Development", "app-developers/android"),
            6: ("eCommerce", "developers/ecommerce"),
            7: ("Artificial Intelligence", "developers/artificial-intelligence"),
            8: ("Blockchain", "developers/blockchain"),
            9: ("AR/VR", "developers/virtual-reality"),
            10: ("IoT", "developers/internet-of-things"),
            11: ("Ruby on Rails", "developers/ruby-rails"),
            12: ("Shopify", "developers/shopify"),
            13: ("WordPress Developers", "developers/wordpress"),
            14: ("Drupal", "developers/drupal"),
            15: ("Magento", "developers/magento"),
            16: (".NET", "developers/dot-net"),
            17: ("PHP", "web-developers/php"),
            18: ("Wearables", "app-developers/wearables"),
            19: ("Software Testing", "developers/testing"),
        }),
        3: ("Design & Production", {
            1: ("Design", "agencies/design"),
            2: ("Digital Design", "agencies/digital-design"),
            3: ("Web Design", "web-designers"),
            4: ("User Experience (UX/UI)", "agencies/ui-ux"),
            5: ("Packaging Design", "agencies/packaging-design"),
            6: ("Print Design", "agencies/print-design"),
            7: ("Graphic Design", "agencies/graphic-designers"),
            8: ("Logo Design", "agencies/logo-designers"),
            9: ("Product Design", "agencies/logo-designers"),
            10: ("Interior Design", "agencies/design/interior"),
        }),
        4: ("IT Services", {
            1: ("IT Services", "it-services"),
            2: ("BI & Big Data", "it-services/analytics"),
            3: ("Staff Augmentation", "it-services/staff-augmentation"),
            4: ("Cybersecurity", "it-services/cybersecurity"),
            5: ("Cloud Consulting", "it-services/cloud"),
            6: ("Managed Service Providers", "it-services/msp"),
        }),
        5: ("Business Services", {
            1: ("BPO", "bpo"),
            2: ("Human Resources", "hr"),
            3: ("Consulting", "consulting"),
            4: ("Accounting", "accounting"),
            5: ("Payroll Processing", "accounting/payroll"),
            6: ("Call Centers", "call-centers"),
            7: ("Answering Services", "call-centers/answering-services"),
            8: ("Telemarketing", "call-centers/telemarketing"),
            9: ("Transcription", "transcription"),
            10: ("Translation", "translation"),
            11: ("Real Estate", "real-estate"),
            12: ("Logistics & Supply Chain Consulting", "logistics/supply-chain-management"),
            13: ("Contract Manufacturing", "logistics/manufacturing-companies"),
            14: ("Customs Brokerage", "logistics/customs-brokers"),
            15: ("Warehousing & Distribution", "logistics/distribution-companies"),
            16: ("Fulfillment", "logistics/fulfillment-services"),
            17: ("Freight Forwarding", "logistics/freight-forwarders"),
            18: ("Rail Freight", "logistics/rail-freight-companies"),
            19: ("Airfreight", "logistics/air-freight-companies"),
            20: ("Trucking", "logistics/trucking-companies"),
            21: ("Ocean Freight", "logistics/container-shipping-companies"),
            22: ("3PL", "logistics/3pls"),
            23: ("Shipping", "logistics/shipping-companie"),
            24: ("Legal", "law"),
            25: ("Executive Search", "hr/executive-search"),
            26: ("HR Staffing", "hr/staffing"),
            27: ("HR Recruiting", "hr/recruiting"),
            28: ("HR Consulting", "hr/consultants"),
            29: ("PEO", "hr/peo"),
            30: ("HR Outsourcing", "hr/outsourcing"),
        }),
    }
    return categories


def get_user_category_selection():
    """Get category selection from user"""
    categories = display_categories()
    
    print("\n" + "="*50)
    print("CLUTCH.CO COMPANY & REVIEWS SCRAPER")
    print("="*50)
    
    # Display main categories
    print("\nSelect a main category:")
    for key, (name, subcats) in categories.items():
        print(f"{key}. {name}")
    
    try:
        main_choice = int(input("\nEnter category number: "))
        if main_choice not in categories:
            print("Invalid selection!")
            return None
            
        main_category, subcategories = categories[main_choice]
        
        # Display subcategories
        print(f"\nSelect from {main_category}:")
        for key, (name, url_slug) in subcategories.items():
            print(f"{key}. {name}")
        
        sub_choice = int(input("\nEnter subcategory number: "))
        if sub_choice not in subcategories:
            print("Invalid selection!")
            return None
            
        selected_name, selected_slug = subcategories[sub_choice]
        return selected_name, selected_slug
        
    except ValueError:
        print("Please enter a valid number!")
        return None

def get_total_companies(scraper, category_url):
    """Get total number of companies in a category"""
    try:
        print(f"\nChecking total companies for: {category_url}")
        response = scraper.get(category_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find total companies count
        companies_count_element = soup.select_one(".facets__companies-amount")
        if companies_count_element:
            count_text = companies_count_element.get_text(strip=True)
            # Extract number from text like "90,154 Companies"
            match = re.search(r'([\d,]+)', count_text)
            if match:
                total_companies = int(match.group(1).replace(',', ''))
                return total_companies, soup
        
        return 0, soup
        
    except Exception as e:
        print(f"Error getting total companies: {e}")
        return 0, None

def scrape_companies_from_page(scraper, page_url):
    """Scrape company information from a single listing page"""
    try:
        print(f"  Scraping companies from: {page_url}")
        response = scraper.get(page_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        companies = []
        
        # Find all company cards
        providers_list = soup.select_one("#providers__list")
        if not providers_list:
            print("    No providers list found")
            return companies
            
        # Look for different types of company listings
        
        # Method 1: Try regular company listings first (non-featured)
        regular_companies = soup.select('.provider-row .provider__title-link[href*="/profile/"]')
        print(f"    Found {len(regular_companies)} regular company profile links")
        
        for link in regular_companies:
            company_name = link.get_text(strip=True)
            company_url = link.get('href')
            
            if company_url.startswith('/'):
                company_url = f"https://clutch.co{company_url}"
            
            companies.append({
                'name': company_name,
                'url': company_url
            })
            print(f"      Found: {company_name}")
        
        # Method 2: If no regular companies found, try alternative selectors
        if not companies:
            print("    No regular listings found, trying alternative selectors...")
            
            # Try different patterns for company profile links
            alternative_selectors = [
                'a[href*="/profile/"]',
                '.provider__title a[href*="/profile/"]',
                '.provider-card a[href*="/profile/"]',
                'h3 a[href*="/profile/"]'
            ]
            
            for selector in alternative_selectors:
                profile_links = soup.select(selector)
                print(f"    Trying selector '{selector}': found {len(profile_links)} links")
                
                for link in profile_links:
                    company_name = link.get_text(strip=True)
                    company_url = link.get('href')
                    
                    if company_url.startswith('/'):
                        company_url = f"https://clutch.co{company_url}"
                    
                    # Avoid duplicates
                    if not any(c['url'] == company_url for c in companies):
                        companies.append({
                            'name': company_name,
                            'url': company_url
                        })
                        print(f"      Found: {company_name}")
                
                if companies:  # If we found some, stop trying other selectors
                    break
        
        # Method 3: Debug - show what company cards we actually have
        if not companies:
            print("    No profile links found. Debugging...")
            all_cards = soup.select('div[id^="provider-"]')
            print(f"    Total provider cards: {len(all_cards)}")
            
            if all_cards:
                first_card = all_cards[0]
                print("    First card HTML snippet:")
                print(f"    {str(first_card)[:500]}...")
                
                # Check all links in first card
                all_links = first_card.select('a')
                print(f"    Links in first card: {len(all_links)}")
                for i, link in enumerate(all_links):
                    href = link.get('href', 'No href')
                    text = link.get_text(strip=True)[:50]
                    print(f"      Link {i+1}: {text} -> {href}")
        
        return companies
        
    except Exception as e:
        print(f"  Error scraping page {page_url}: {e}")
        return []

def save_company_reviews_to_csv(company_data, output_dir):
    """Save company reviews to individual CSV file"""
    company_name = company_data['company_name']
    safe_name = re.sub(r'[^\w\s-]', '', company_name).strip()
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    
    csv_file = output_dir / f"{safe_name}_reviews.csv"
    
    if company_data['reviews']:
        df = pd.DataFrame(company_data['reviews'])
        df['scrape_timestamp'] = pd.Timestamp.now()
        
        # Reorder columns
        cols = ['FirstName', 'LastName', 'Email', 'Designation', 'City', 'Country',
                'ProfileLink', 'Source', 'PhoneNumber', 'OrganisationName', 
                'Industry', 'Purpose', 'WebsiteLink']
        df = df[cols]
        
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"    ✅ Saved {len(df)} reviews to {csv_file.name}")
    else:
        # Create empty CSV with headers for companies with no reviews
        df = pd.DataFrame(columns=['FirstName', 'LastName', 'Email', 'Designation', 'City', 'Country',
                              'ProfileLink', 'Source', 'PhoneNumber', 'OrganisationName', 
                              'Industry', 'Purpose', 'WebsiteLink'])
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"    ⚠️  No reviews found - created empty CSV: {csv_file.name}")

def save_progress_file(output_dir, scraped_companies, total_requested, category_name):
    """Save progress file to track scraping status"""
    progress_file = output_dir / "scrape_progress.txt"
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.write(f"Category: {category_name}\n")
        f.write(f"Companies scraped: {scraped_companies}\n")
        f.write(f"Total requested: {total_requested}\n")
        f.write(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def load_tracking_data(tracking_file='scraped_companies.json'):
    """Load tracking data from JSON file"""
    tracking_path = Path(tracking_file)
    if tracking_path.exists():
        try:
            with open(tracking_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load tracking file: {e}")
            return {}
    return {}

def save_tracking_data(tracking_data, tracking_file='scraped_companies.json'):
    """Save tracking data to JSON file"""
    tracking_path = Path(tracking_file)
    try:
        with open(tracking_path, 'w', encoding='utf-8') as f:
            json.dump(tracking_data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Warning: Could not save tracking file: {e}")

def is_company_scraped(company_url, category_slug, tracking_data):
    """Check if a company has already been scraped for this category"""
    if category_slug not in tracking_data:
        return False
    return company_url in tracking_data[category_slug].get('scraped_companies', [])

def add_scraped_company(company_url, category_slug, tracking_data):
    """Add a company to the scraped list for this category"""
    if category_slug not in tracking_data:
        tracking_data[category_slug] = {
            'scraped_companies': [],
            'last_updated': datetime.now().isoformat()
        }
    
    if company_url not in tracking_data[category_slug]['scraped_companies']:
        tracking_data[category_slug]['scraped_companies'].append(company_url)
        tracking_data[category_slug]['last_updated'] = datetime.now().isoformat()

def get_scraped_count(category_slug, tracking_data):
    """Get the number of already scraped companies for a category"""
    if category_slug not in tracking_data:
        return 0
    return len(tracking_data[category_slug].get('scraped_companies', []))

def scrape_reviews_from_company(scraper, company_url, company_name, killer):
    """Scrape all reviews from a single company profile using original logic"""
    print(f"\n  Scraping reviews for: {company_name}")
    
    all_reviews = []
    
    try:
        # Check for graceful shutdown
        if killer.kill_now:
            return []
            
        # First page
        reviews, soup = scrape_reviews_from_page(scraper, company_url)
        all_reviews.extend(reviews)
        print(f"    Page 1: {len(reviews)} reviews")
        
        # Get company name from profile
        company_element = soup.select_one("h1.profile-header__title")
        actual_company_name = company_element.get_text(strip=True) if company_element else company_name
        
        # Pagination: find total reviews and calculate pages
        pagination_info = soup.select_one("#reviews-list > div.profile-reviews--pagination > p")
        total_pages = 1
        total_reviews = len(reviews)
        
        if pagination_info:
            text = pagination_info.get_text(strip=True)
            print(f"    Pagination info: {text}")
            match = re.search(r'of\s+(\d+)', text, re.IGNORECASE)
            if match:
                total_reviews = int(match.group(1))
                total_pages = (total_reviews + 9) // 10  # assume 10 reviews per page
                print(f"    Total reviews: {total_reviews}, Estimated pages: {total_pages}")
        
        # Scrape remaining pages using actual pagination URLs
        pagination_container = soup.select_one(".sg-pagination-v2")
        page_links = []
        
        if pagination_container and total_pages > 1:
            # Extract all pagination links
            links = pagination_container.select("a[data-page]")
            for link in links:
                href = link.get('href')
                page_num = link.get_text(strip=True)
                if href and page_num.isdigit() and int(page_num) > 1:
                    full_url = f"https://clutch.co{href}"
                    page_links.append((int(page_num), full_url))
            
            page_links = sorted(page_links)
            print(f"    Found {len(page_links)} additional pages to scrape")
            
            for page_num, page_url in page_links:
                # Check for graceful shutdown
                if killer.kill_now:
                    print("    Stopping page scraping due to user interrupt...")
                    break
                    
                if len(all_reviews) >= total_reviews:
                    print(f"    Reached expected total of {total_reviews} reviews!")
                    break
                    
                print(f"    Scraping page {page_num}...")
                try:
                    page_reviews, _ = scrape_reviews_from_page(scraper, page_url)
                    if page_reviews:
                        all_reviews.extend(page_reviews)
                        print(f"    Added {len(page_reviews)} reviews from page {page_num}")
                        print(f"    Total so far: {len(all_reviews)}/{total_reviews}")
                    time.sleep(2)
                except Exception as e:
                    print(f"    Error scraping page {page_num}: {e}")
                    continue
        
        print(f"    Final total reviews for {actual_company_name}: {len(all_reviews)}")
        return all_reviews
        
    except Exception as e:
        print(f"  Error scraping reviews for {company_name}: {e}")
        return []

def scrape_reviews_from_page(scraper, url):
    """Scrape reviews from a single page (reusing existing function)"""
    response = scraper.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    reviews = []
    reviews_container_list = soup.select("article.profile-review")
    
    if not reviews_container_list:
        reviews_container_list = soup.select("#reviews-list .profile-review, .review-card, [class*='review'][class*='card']")
    
    if len(reviews_container_list) < 10:
        div_reviews = soup.select("#reviews-list div[id^='review']")
        if div_reviews:
            for div_review in div_reviews:
                if div_review not in reviews_container_list:
                    reviews_container_list.append(div_review)
    
    for review in reviews_container_list:
        # Find this section and update it:
        title_element = review.select_one(".profile-review__quote") or review.select_one("h3[itemprop='name']") or review.select_one("h3")
        title = clean_text(title_element.get_text(strip=True)) if title_element else ""

        text_element = review.select_one(".profile-review__text") or review.select_one("[itemprop='reviewBody']") or review.select_one("p")
        text = clean_text(text_element.get_text(strip=True)) if text_element else ""

        reviewer_name = review.select_one(".reviewer_card--name") or review.select_one("[itemprop='author']")
        reviewer_name = clean_text(reviewer_name.get_text(strip=True)) if reviewer_name else ""

        reviewer_position = review.select_one(".reviewer_card--position") or review.select_one(".reviewer_position")
        reviewer_position = clean_text(reviewer_position.get_text(strip=True)) if reviewer_position else ""

        reviewer_location = review.select_one(
            ".reviewer_card--location, li:nth-child(2) > span.reviewer_list__details-title.sg-text__title"
        )
        reviewer_location = clean_text(reviewer_location.get_text(strip=True)) if reviewer_location else ""

        reviewer_industry = review.select_one(".reviewer_list__details-title.sg-text__title")
        reviewer_industry = clean_text(reviewer_industry.get_text(strip=True)) if reviewer_industry else ""

        # Replace the existing reviews.append() with this:
        if (text and len(text) > 50) and title and title not in ["Overall Review Rating", "No title"]:
            # Split reviewer name into first and last
            name_parts = reviewer_name.split() if reviewer_name else ["Anonymous"]
            first_name = name_parts[0] if name_parts else "Anonymous"
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            # Extract designation and organization from position
            if reviewer_position and "," in reviewer_position:
                position_parts = reviewer_position.split(",", 1)  # Split only on first comma
                designation = position_parts[0].strip()
                organization = position_parts[1].strip()
            else:
                designation = reviewer_position if reviewer_position else "No position"
                organization = ""
            
            # UPDATED: Parse city and country from location
            city = ""
            country = ""
            if reviewer_location and reviewer_location != "No location":
                if "," in reviewer_location:
                    location_parts = reviewer_location.split(",", 1)
                    city = location_parts[0].strip()
                    country = location_parts[1].strip()
                else:
                    country = reviewer_location.strip()  # If no comma, treat as country
            
            reviews.append({
                "FirstName": first_name,
                "LastName": last_name,
                "Email": "",  # null
                "Designation": designation,
                "City": city,  # UPDATED: Now extracts city
                "Country": country,  # UPDATED: Now extracts country
                "ProfileLink": "",  # null
                "Source": "Clutch.co",
                "PhoneNumber": "",  # null
                "OrganisationName": organization,
                "Industry": reviewer_industry if reviewer_industry else "No industry",
                "Purpose": "",  # null
                "WebsiteLink": ""  # null
            })
    
    return reviews, soup

def main():
    """Main function to run the scraper"""
    killer = GracefulKiller()
    scraper = cloudscraper.create_scraper()
    if not setup_mongodb():
        print("Failed to connect to MongoDB. Exiting...")
        return
    
    print("💡 Tip: Press Ctrl+C at any time to stop and save progress")

    # --- Get category selection ---
    selection = get_user_category_selection()
    if not selection:
        print("Invalid selection. Exiting...")
        return

    category_name, category_slug = selection
    category_url = f"https://clutch.co/{category_slug}"

    # --- Setup output folder (timestamped) ---
    # timestamp = time.strftime("%Y%m%d_%H%M%S")
    # safe_category = re.sub(r'[^\w\s-]', '', category_name).strip()
    # safe_category = re.sub(r'[-\s]+', '_', safe_category)
    # output_dir = Path(f"{safe_category}_{timestamp}")
    # output_dir.mkdir(exist_ok=True)

    safe_category = re.sub(r'[^\w\s-]', '', category_name).strip()
    safe_category = re.sub(r'[-\s]+', '_', safe_category)

    # Fixed folder for the category
    output_dir = Path(f"output/{safe_category}")
    output_dir.mkdir(parents=True, exist_ok=True)


    # --- Setup tracking folder & file ---
    tracking_dir = Path("tracking")
    tracking_dir.mkdir(exist_ok=True)
    tracking_file = tracking_dir / f"{safe_category}_scraped.json"

    # --- Load tracking data ---
    tracking_data = load_tracking_data(tracking_file)
    already_scraped = get_scraped_count(category_slug, tracking_data)
    if already_scraped > 0:
        print(f"\n📊 Found {already_scraped} previously scraped companies in this category. These will be skipped.")

    # --- Get total companies ---
    total_companies, soup = get_total_companies(scraper, category_url)
    if total_companies == 0:
        print("Could not find companies in this category. Exiting...")
        return

    print(f"\nCategory: {category_name}")
    print(f"Total companies available: {total_companies:,}")

    # --- Ask how many companies to scrape ---
    try:
        num_companies = int(input(f"\nHow many companies do you want to scrape? (max {total_companies:,}): "))
        if num_companies <= 0 or num_companies > total_companies:
            print(f"Please enter a number between 1 and {total_companies:,}")
            return
    except ValueError:
        print("Please enter a valid number!")
        return

    print(f"\n📁 Output directory: {output_dir}")
    print(f"🚀 Starting to scrape {num_companies} companies and their reviews...")

    scraped_companies = 0
    skipped_companies = 0
    current_page = 0
    companies_to_scrape = num_companies

    try:
        while scraped_companies < companies_to_scrape and not killer.kill_now:
            page_url = category_url if current_page == 0 else f"{category_url}?page={current_page}"
            print(f"\nScraping company listing page {current_page + 1}...")

            page_companies = scrape_companies_from_page(scraper, page_url)
            if not page_companies:
                print(f"No companies found on page {current_page + 1}. Ending scrape.")
                break

            for company in page_companies:
                if scraped_companies >= companies_to_scrape or killer.kill_now:
                    break

                company_name = company['name']
                company_url = company['url']

                # Skip if already scraped
                if is_company_already_scraped(company_url):
                    skipped_companies += 1
                    print(f"\n[SKIPPED] {company_name} - Already in database")
                    continue

                print(f"\n[{scraped_companies + 1}/{companies_to_scrape}] Processing: {company_name}")
                print(f"  (Skipped {skipped_companies} already scraped companies)")

                # Scrape reviews/contacts
                reviews = scrape_reviews_from_company(scraper, company_url, company_name, killer)
                company_data = {
                    'company_name': company_name,
                    'company_url': company_url,
                    'reviews': reviews,
                    'total_reviews': len(reviews)
                }


                # Save CSV
                save_company_reviews_to_csv(company_data, output_dir)

                # --- Update tracking JSON ---
                # add_scraped_company(company_url, category_slug, tracking_data)
                # save_tracking_data(tracking_data, tracking_file)
                save_company_to_mongodb(company_data)

                scraped_companies += 1

                # Save progress file
                save_progress_file(output_dir, scraped_companies, companies_to_scrape, category_name)

                if killer.kill_now:
                    print("Stopping due to user interrupt...")
                    break

                time.sleep(3)

            current_page += 1

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")

    # --- Final summary ---
    print(f"\n{'='*50}")
    if killer.kill_now:
        print("SCRAPING STOPPED BY USER")
    else:
        print("SCRAPING COMPLETED!")
    print(f"Companies processed: {scraped_companies}/{num_companies}")
    print(f"Companies skipped (already scraped): {skipped_companies}")
    print(f"Output directory: {output_dir}")
    print(f"CSV files created: {len(list(output_dir.glob('*_reviews.csv')))}")
    print("="*50)


if __name__ == "__main__":
    main()