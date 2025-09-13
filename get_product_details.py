from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


def get_product_details(product_name):
    url = f"https://www.trendyol.com/sr?q={product_name}"

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
        # Initialize the WebDriver with webdriver-manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Add stealth settings
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        driver.get(url)

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
            containers = driver.find_elements(By.CSS_SELECTOR, container_selector)

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
                            break
                    except:
                        continue

                if not product_link:
                    product_link = first_container

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

                # Extract product details from the product page with retry logic
                product_details = {}
                limit_attempts = 5
                expected_elements = [
                    "title",
                    "price",
                    "description",
                    "features",
                    "rating",
                    "brand",
                    "stock",
                ]

                while limit_attempts > 0:
                    product_details = extract_product_page_details(driver)

                    # Check which elements are missing
                    missing_elements = []
                    for element in expected_elements:
                        if (
                            element not in product_details
                            or not product_details[element]
                        ):
                            missing_elements.append(element)

                    if not missing_elements:
                        break

                    limit_attempts -= 1
                    time.sleep(1)

                print_product_details(product_details)

                break

        driver.quit()

    except Exception as e:
        if "driver" in locals():
            driver.quit()


def extract_product_page_details(driver):
    """Extract detailed product information from the product page"""
    details = {}

    try:
        # Product title
        title_selectors = [".product-title"]

        for selector in title_selectors:
            try:
                title_element = driver.find_element(By.CSS_SELECTOR, selector)
                details["title"] = title_element.text.strip()
                break
            except:
                continue

        # Product price
        price_selectors = [
            ".prc-box-dscntd",
            ".prc-box-sllng",
            "[class*='price']",
            ".price-current",
            "[data-test-id='price-current-price']",
        ]

        for selector in price_selectors:
            try:
                price_element = driver.find_element(By.CSS_SELECTOR, selector)
                details["price"] = price_element.text.strip()
                break
            except:
                continue

        # Product description
        description_selectors = [".content-description-container"]

        for selector in description_selectors:
            try:
                desc_element = driver.find_element(By.CSS_SELECTOR, selector)
                # If it's the content-description-container, get all child elements text
                if "content-description-container" in selector:
                    # Get all text content from child elements
                    child_elements = desc_element.find_elements(By.CSS_SELECTOR, "*")
                    description_parts = []
                    for child in child_elements:
                        child_text = child.text.strip()
                        if child_text and child_text not in description_parts:
                            description_parts.append(child_text)
                    if description_parts:
                        details["description"] = "\n".join(description_parts)
                    else:
                        details["description"] = desc_element.text.strip()
                else:
                    details["description"] = desc_element.text.strip()
                break
            except:
                continue

        # Product features/specifications
        try:
            features_elements = driver.find_elements(
                By.CSS_SELECTOR,
                ".attribute-item, .detail-attr li, .product-features li, [class*='feature'] li",
            )
            if features_elements:
                features = []
                for feature in features_elements[:15]:  # Get first 15 features
                    feature_text = feature.text.strip()
                    if feature_text:
                        # For attribute-item divs, the text might contain both key and value
                        # Clean up the text to make it more readable
                        if "attribute-item" in feature.get_attribute("class"):
                            # Split by common separators and clean up
                            if ":" in feature_text:
                                feature_text = feature_text.replace(":", ": ")
                            elif "\n" in feature_text:
                                feature_text = feature_text.replace("\n", ": ")

                        if feature_text not in features:
                            features.append(feature_text)
                details["features"] = features
        except:
            pass

        # Product rating
        rating_selectors = [
            ".rating-score",
            "[class*='rating']",
            ".star-rating",
            "[data-test-id='rating']",
        ]

        for selector in rating_selectors:
            try:
                rating_element = driver.find_element(By.CSS_SELECTOR, selector)
                details["rating"] = rating_element.text.strip()
                break
            except:
                continue

        # Brand
        brand_selectors = ["a.product-title-brand-name-anchor"]

        for selector in brand_selectors:
            try:
                brand_element = driver.find_element(By.CSS_SELECTOR, selector)
                details["brand"] = brand_element.text.strip()
                break
            except:
                continue

        # Stock status
        stock_selectors = [
            ".stock-info",
            "[class*='stock']",
            ".availability",
            "[data-test-id*='stock']",
        ]

        for selector in stock_selectors:
            try:
                stock_element = driver.find_element(By.CSS_SELECTOR, selector)
                details["stock"] = stock_element.text.strip()
                break
            except:
                continue

    except:
        pass

    return details


def print_product_details(details):
    """Print the extracted product details in a formatted way"""
    print("\n" + "=" * 60)
    print("PRODUCT DETAILS")
    print("=" * 60)

    if "title" in details:
        print(f"Title: {details['title']}")

    if "brand" in details:
        print(f"Brand: {details['brand']}")

    if "price" in details:
        print(f"Price: {details['price']}")

    if "rating" in details:
        print(f"Rating: {details['rating']}")

    if "stock" in details:
        print(f"Stock: {details['stock']}")

    if "description" in details:
        print(f"\nDescription:")
        print(f"{details['description']}")

    if "features" in details and details["features"]:
        print(f"\nFeatures:")
        for i, feature in enumerate(details["features"], 1):
            print(f"  {i}. {feature}")

    print("=" * 60)


if __name__ == "__main__":
    get_product_details("laptop")
