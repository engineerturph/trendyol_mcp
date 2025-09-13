from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


def get_product_reviews(product_name):
    print(f"Searching for product: {product_name}")
    url = f"https://www.trendyol.com/sr?q={product_name}"
    print(f"URL: {url}")

    options = Options()
    # Remove headless mode to avoid detection
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    )

    try:
        print("Installing ChromeDriver...")
        # Initialize the WebDriver with webdriver-manager
        service = Service(ChromeDriverManager().install())
        print("Creating Chrome driver...")
        driver = webdriver.Chrome(service=service, options=options)

        # Add stealth settings
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        print("Navigating to search URL...")
        driver.get(url)
        print("Page loaded, waiting...")

        print("Looking for product containers...")

        # Try to find product containers
        container_selectors = [
            ".p-card-wrppr",
            "[class*='product-item']",
            "[class*='product-card']",
            ".product-down",
            "[data-test-id*='product']",
        ]

        first_product_found = False

        for container_selector in container_selectors:
            print(f"Trying container selector: {container_selector}")
            containers = driver.find_elements(By.CSS_SELECTOR, container_selector)
            print(
                f"Found {len(containers)} containers with selector '{container_selector}'"
            )

            if len(containers) > 0:
                first_product_found = True
                first_container = containers[0]

                # Look for clickable link within the first container
                link_selectors = [
                    "a[href*='/p/']",  # Trendyol product links contain '/p/'
                    "a",
                    "[href*='product']",
                    ".p-card-wrppr a",
                ]

                product_link = None
                for link_sel in link_selectors:
                    try:
                        product_link = first_container.find_element(
                            By.CSS_SELECTOR, link_sel
                        )
                        href = product_link.get_attribute("href")
                        if href and ("/p/" in href or "product" in href.lower()):
                            print(f"Found product link: {href}")
                            break
                    except:
                        continue

                if not product_link:
                    print("No specific product link found, clicking container")
                    product_link = first_container

                print("Clicking on the first product...")
                # Store current window handle
                main_window = driver.current_window_handle

                # Scroll to element first
                driver.execute_script(
                    "arguments[0].scrollIntoView(true);", product_link
                )
                # Click using JavaScript to avoid interception
                driver.execute_script("arguments[0].click();", product_link)

                # Switch to the new tab (product page)
                all_windows = driver.window_handles
                if len(all_windows) > 1:
                    # Switch to the new tab
                    for window in all_windows:
                        if window != main_window:
                            driver.switch_to.window(window)
                            break
                    print("Switched to product page tab")
                else:
                    print("No new tab opened, staying on current page")

                print("Product page loaded, scrolling to find reviews section...")

                # Scroll down smoothly to load all content and find the reviews section
                driver.execute_script(
                    """
                    window.scrollTo({
                        top: document.body.scrollHeight,
                        behavior: 'smooth'
                    });
                """
                )

                print("Looking for reviews...")

                # Look for the reviews button and click it
                reviews_found = click_reviews_button(driver)

                if reviews_found:
                    # Extract reviews from the reviews page
                    reviews = extract_product_reviews(driver)
                    print_product_reviews(reviews)
                else:
                    print("Could not find or access product reviews")

                break

        if not first_product_found:
            print("No products found in search results")

        driver.quit()
        print("Script completed successfully!")

    except Exception as e:
        print(f"Error occurred: {e}")
        if "driver" in locals():
            driver.quit()


def click_reviews_button(driver):
    """Click the button to go to reviews page"""
    try:
        print("Looking for reviews button...")

        # Try different approaches to find the reviews button
        print("Searching for buttons with text 'TÜM YORUMLARI GÖSTER'...")

        # First try: Look for any button or clickable element containing the text
        all_buttons = driver.find_elements(
            By.XPATH, "//*[contains(text(), 'TÜM YORUMLARI GÖSTERRR')]"
        )
        if all_buttons:
            print(f"Found {len(all_buttons)} elements with reviews text")
            reviews_button = all_buttons[0]
        else:
            # Second try: Look for specific class patterns
            button_selectors = [
                ".show-more-button-show-more-button",
                "[class*='show-more-button']",
                "[class*='review']",
                "[class*='comment']",
                "button",
                ".btn",
            ]

            reviews_button = None
            while reviews_button is None:
                time.sleep(1)
                for selector in button_selectors:
                    try:
                        buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                        print(
                            f"Found {len(buttons)} buttons with selector '{selector}'"
                        )
                        for button in buttons:
                            button_text = button.text.strip()
                            if "YORUM" in button_text and "TÜM" in button_text:
                                print(
                                    f"Found potential reviews button with text: '{button_text}'"
                                )
                                reviews_button = button
                                break
                        if reviews_button:
                            break
                    except:
                        continue

        if reviews_button:
            # Scroll to the button and click it
            driver.execute_script("arguments[0].scrollIntoView(true);", reviews_button)
            driver.execute_script("arguments[0].click();", reviews_button)
            print("Clicked reviews button, waiting for reviews page to load...")
            return True
        else:
            print("Reviews button not found, checking current page for reviews...")
            # Maybe reviews are already on the current page
            review_containers = driver.find_elements(By.CSS_SELECTOR, ".comment-text")
            if review_containers:
                print(f"Found {len(review_containers)} reviews on current page")
                return True
            else:
                print("No reviews found on current page either")
                return False

    except Exception as e:
        print(f"Error clicking reviews button: {e}")
        return False


def extract_product_reviews(driver):
    """Extract reviews from the reviews page"""
    reviews = []

    try:
        print("Extracting reviews...")

        # Find all review containers

        limit_review_attempts = 5
        review_containers = []
        while len(review_containers) == 0 and limit_review_attempts > 0:
            print(review_containers)
            time.sleep(1)
            review_containers = driver.find_elements(By.CSS_SELECTOR, ".comment-text")
            limit_review_attempts -= 1
        print(f"Found {len(review_containers)} review containers")

        for i, container in enumerate(review_containers[:20]):  # Get first 20 reviews
            try:
                # Extract text from <p> elements inside the comment-text div
                review_paragraphs = container.find_elements(By.TAG_NAME, "p")
                review_text_parts = []

                for p in review_paragraphs:
                    p_text = p.text.strip()
                    if p_text:
                        review_text_parts.append(p_text)

                if review_text_parts:
                    full_review = " ".join(review_text_parts)
                    reviews.append({"id": i + 1, "text": full_review})

            except Exception as e:
                print(f"Error extracting review {i+1}: {e}")
                continue

        print(f"Successfully extracted {len(reviews)} reviews")

    except Exception as e:
        print(f"Error extracting reviews: {e}")

    return reviews


def print_product_reviews(reviews):
    """Print the extracted reviews in a formatted way"""
    print("\n" + "=" * 80)
    print("PRODUCT REVIEWS")
    print("=" * 80)

    if not reviews:
        print("No reviews found")
        return

    for review in reviews:
        print(f"\n--- Review {review['id']} ---")
        print(f"{review['text']}")
        print("-" * 50)

    print(f"\nTotal Reviews: {len(reviews)}")
    print("=" * 80)


if __name__ == "__main__":
    get_product_reviews("laptop")
