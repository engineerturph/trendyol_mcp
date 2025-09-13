from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import requests
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO


def get_product_image(product_name):
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

                # Extract product image from the product page
                image_url = extract_and_display_product_image(driver)

                # Download and display the image if URL is found
                if image_url:
                    download_and_show_image(image_url)

                break

        driver.quit()

    except Exception as e:
        if "driver" in locals():
            driver.quit()


def extract_and_display_product_image(driver):
    """Extract and display product image from the product-image-gallery-carousel element"""
    main_image_url = None

    try:
        # First try to find the specific carousel element
        try:
            carousel_element = driver.find_element(
                By.CSS_SELECTOR, ".product-image-gallery-carousel"
            )

            # Look for img elements within the carousel
            img_elements = carousel_element.find_elements(By.TAG_NAME, "img")

            if img_elements:
                # Display all images found in the carousel
                for i, img in enumerate(img_elements):
                    img_src = img.get_attribute("src")
                    img_alt = img.get_attribute("alt")
                    img_class = img.get_attribute("class")

                    if img_src:
                        print(f"\nImage {i+1}:")
                        print(f"  Source: {img_src}")
                        print(f"  Alt Text: {img_alt or 'No alt text'}")
                        print(f"  Class: {img_class or 'No class'}")
                        print(
                            f"  HTML: <img src='{img_src}' alt='{img_alt or ''}' class='{img_class or ''}' />"
                        )

                # Get the main/first image details
                main_img = img_elements[0]
                main_src = main_img.get_attribute("src")
                main_alt = main_img.get_attribute("alt")
                main_image_url = main_src

                print(f"\n" + "=" * 80)
                print("MAIN PRODUCT IMAGE")
                print("=" * 80)
                print(f"Main Image URL: {main_src}")
                print(f"Main Image Alt: {main_alt or 'Product Image'}")
                print(f"Total Images in Gallery: {len(img_elements)}")
                print(
                    f"Main Image Element: <img src='{main_src}' alt='{main_alt or 'Product Image'}' />"
                )
                print("=" * 80)

        except Exception as e:
            # Fallback selectors if the main carousel isn't found
            fallback_selectors = [
                "[class*='image-gallery']",
                "[class*='product-image']",
                ".product-photos",
                "img[class*='product']",
                "main img",
            ]

            image_found = False
            for selector in fallback_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # If it's a container, look for images inside
                        if elements[0].tag_name != "img":
                            img_elements = elements[0].find_elements(By.TAG_NAME, "img")
                        else:
                            img_elements = elements

                        if img_elements:
                            img_src = img_elements[0].get_attribute("src")
                            img_alt = img_elements[0].get_attribute("alt")
                            main_image_url = img_src

                            print("\n" + "=" * 80)
                            print("PRODUCT IMAGE (FALLBACK)")
                            print("=" * 80)
                            print(f"Image URL: {img_src}")
                            print(f"Image Alt: {img_alt or 'Product Image'}")
                            print(f"Found using selector: {selector}")
                            print(
                                f"Image Element: <img src='{img_src}' alt='{img_alt or 'Product Image'}' />"
                            )
                            print("=" * 80)

                            image_found = True
                            break
                except:
                    continue

    except Exception as e:
        pass

    return main_image_url


def download_and_show_image(image_url):
    """Download image from URL and display it using matplotlib"""
    try:
        # Set headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

        # Download the image
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Open the image using PIL
        image = Image.open(BytesIO(response.content))

        # Create a matplotlib figure
        plt.figure(figsize=(10, 12))
        plt.imshow(image)
        plt.axis("off")  # Hide axes
        plt.title("Product Image from Trendyol", fontsize=16, fontweight="bold")

        # Show the image
        plt.tight_layout()
        plt.show()

        # Print image info
        print(f"\nImage Information:")
        print(f"Format: {image.format}")
        print(f"Size: {image.size}")
        print(f"Mode: {image.mode}")

    except requests.exceptions.RequestException as e:
        pass
    except Exception as e:
        pass


if __name__ == "__main__":
    get_product_image("laptop")
