from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


def search_trendyol(query, target_count=100, max_scroll_attempts=15):
    url = f"https://www.trendyol.com/sr?q={query}"

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

        # Try to find product containers first, then extract name and price from each container
        container_selectors = [
            ".p-card-wrppr",
            "[class*='product-item']",
            "[class*='product-card']",
            ".product-down",
            "[data-test-id*='product']",
        ]

        found_containers = False

        for container_selector in container_selectors:
            containers = driver.find_elements(By.CSS_SELECTOR, container_selector)

            if len(containers) > 0:
                found_containers = True
                print(f"\n=== Product Results ===")

                # If we don't have enough containers, try scrolling to load more
                scroll_attempts = 0
                no_new_products_count = 0

                while (
                    len(containers) < target_count
                    and scroll_attempts < max_scroll_attempts
                ):
                    current_count = len(containers)

                    # Simply scroll to 80% of the page to load new products
                    driver.execute_script(
                        """
                            window.scrollTo({
                            top: 0,
                            behavior: 'smooth'
                            });
                        """
                    )
                    time.sleep(1)
                    driver.execute_script(
                        """
                            window.scrollTo({
                            top: document.body.scrollHeight,
                            behavior: 'smooth'
                            });
                        """
                    )
                    time.sleep(1)

                    # Re-check for containers
                    new_containers = driver.find_elements(
                        By.CSS_SELECTOR, container_selector
                    )
                    if len(new_containers) > current_count:
                        containers = new_containers
                        no_new_products_count = 0  # Reset counter
                    else:
                        no_new_products_count += 1

                        # If we haven't found new products for 10 consecutive attempts, stop
                        if no_new_products_count >= 10:
                            break

                    scroll_attempts += 1

                # Show up to 100 products (or however many we found)
                products_to_show = min(len(containers), target_count)

                for i, container in enumerate(containers[:products_to_show]):
                    try:
                        # Look for name within this container
                        name_element = None
                        name_selectors_in_container = [
                            "span.prdct-desc-cntnr-name",
                            ".name",
                            "span[class*='name']",
                            "[class*='title']",
                        ]

                        for name_sel in name_selectors_in_container:
                            try:
                                name_element = container.find_element(
                                    By.CSS_SELECTOR, name_sel
                                )
                                break
                            except:
                                continue

                        # Look for description within this container
                        description_element = None
                        description_selectors_in_container = [
                            ".product-desc-sub-text",
                            "div[class*='desc']",
                            "[class*='description']",
                            ".prdct-desc-cntnr-ttl",
                            "div[title]",
                        ]

                        for desc_sel in description_selectors_in_container:
                            try:
                                description_element = container.find_element(
                                    By.CSS_SELECTOR, desc_sel
                                )
                                break
                            except:
                                continue

                        # Look for price within this container
                        price_element = None
                        price_selectors_in_container = [
                            ".prc-box-dscntd",
                            ".prc-box-sllng",
                            "[class*='price']",
                            ".price",
                            "span[class*='prc']",
                        ]

                        for price_sel in price_selectors_in_container:
                            try:
                                price_element = container.find_element(
                                    By.CSS_SELECTOR, price_sel
                                )
                                break
                            except:
                                continue

                        name_text = (
                            name_element.text.strip()
                            if name_element
                            else "Name not found"
                        )
                        description_text = (
                            description_element.text.strip()
                            if description_element
                            else "Description not found"
                        )
                        price_text = (
                            price_element.text.strip()
                            if price_element
                            else "Price not found"
                        )

                        # If description is empty, try to get it from title attribute
                        if (
                            description_text == "Description not found"
                            and description_element
                        ):
                            try:
                                title_attr = description_element.get_attribute("title")
                                if title_attr:
                                    description_text = title_attr.strip()
                            except:
                                pass

                        # Clean up price text - extract only the main price
                        if price_text and price_text != "Price not found":
                            # Split by newlines and take the first line that contains "TL"
                            price_lines = price_text.split("\n")
                            for line in price_lines:
                                if "TL" in line and any(
                                    char.isdigit() for char in line
                                ):
                                    price_text = line.strip()
                                    break

                        if name_text and name_text != "Name not found":
                            print(f"{i+1}. Product: {name_text} | {description_text}")
                            print(f"    Price: {price_text}")
                            print()

                    except Exception as e:
                        continue

                break

        driver.quit()

    except Exception as e:
        if "driver" in locals():
            driver.quit()


if __name__ == "__main__":
    # Example usage
    search_trendyol("laptop", target_count=100, max_scroll_attempts=10)
