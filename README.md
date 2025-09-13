# Trendyol MCP Server

A Model Context Protocol (MCP) server that provides comprehensive product search and analysis functionality for Trendyol, Turkey's leading e-commerce platform.

## Overview

This MCP server enables AI assistants and applications to search, analyze, and extract detailed information from Trendyol products using automated web scraping. It provides four main tools for interacting with Trendyol's product catalog.

## Features

### 🔍 **Product Search**

- Search for products with customizable result counts
- Extract product names, descriptions, and prices
- Scroll through multiple pages automatically
- Handle dynamic content loading

### 📊 **Product Details**

- Get comprehensive product information including:
  - Title and brand
  - Price and rating
  - Detailed description
  - Product features and specifications
  - Stock status

### 🖼️ **Product Images**

- Extract product images from gallery carousels
- Display images using matplotlib
- Fallback image extraction for different page layouts
- Image metadata and format information

### 💬 **Product Reviews**

- Extract customer reviews and comments
- Navigate to dedicated reviews pages
- Parse review text from multiple sources
- Support for up to 20 reviews per product

## Installation

### Prerequisites

- Python 3.8+
- Chrome browser (for Selenium WebDriver)

### Setup

1. **Clone the repository:**

```bash
git clone https://github.com/engineerturph/trendyol_mcp.git
cd trendyol_mcp
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Make the run script executable:**

```bash
chmod +x run_mcp_server.sh
```

## Usage

### Starting the MCP Server

```bash
python trendyol_mcp_server.py
```

Or using the provided script:

```bash
./run_mcp_server.sh
```

### Available Tools

#### 1. `search_trendyol`

Search for products on Trendyol with detailed information.

**Parameters:**

- `query` (string, required): Search term or product name
- `target_count` (integer, optional): Number of products to retrieve (1-100, default: 100)

**Example:**

```json
{
  "query": "laptop",
  "target_count": 50
}
```

#### 2. `get_product_details`

Get comprehensive details about a specific product.

**Parameters:**

- `product_name` (string, required): Product name to search for

**Example:**

```json
{
  "product_name": "MacBook Pro"
}
```

#### 3. `get_product_image`

Extract and display product images from the gallery.

**Parameters:**

- `product_name` (string, required): Product name to search for

**Example:**

```json
{
  "product_name": "iPhone 15"
}
```

#### 4. `get_product_reviews`

Extract customer reviews for a specific product.

**Parameters:**

- `product_name` (string, required): Product name to search for

**Example:**

```json
{
  "product_name": "Samsung Galaxy S24"
}
```

## Configuration

### MCP Client Configuration

Add this server to your MCP client configuration:

```json
{
  "mcpServers": {
    "trendyol-search": {
      "command": "python",
      "args": ["/path/to/trendyol_mcp_server.py"],
      "env": {}
    }
  }
}
```

### Claude Desktop Configuration

For Claude Desktop, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "trendyol-search": {
      "command": "python",
      "args": ["/Users/your-username/path/to/trendyol_mcp_server.py"]
    }
  }
}
```

## Dependencies

- **selenium**: Web automation and scraping
- **webdriver-manager**: Automatic Chrome WebDriver management
- **mcp**: Model Context Protocol framework
- **requests**: HTTP requests for image downloading
- **matplotlib**: Image display and visualization
- **pillow**: Image processing and manipulation

## Technical Details

### Web Scraping Approach

- Uses Selenium WebDriver with Chrome for JavaScript-heavy content
- Implements stealth techniques to avoid detection
- Handles dynamic loading with intelligent waiting mechanisms
- Robust error handling and fallback selectors

### Performance Optimizations

- Efficient element selection with multiple fallback strategies
- Optimized scrolling for loading additional products
- Smart retry logic for missing product details
- Minimal debugging output for production use

### Browser Configuration

- Headless mode disabled to avoid bot detection
- Custom user agent for authenticity
- Disabled automation flags
- GPU and sandbox optimizations for stability

## Error Handling

The server includes comprehensive error handling:

- Invalid parameter validation
- Network connectivity issues
- Element not found scenarios
- Browser automation failures
- Graceful degradation for missing content

## Limitations

- Requires Chrome browser installation
- May be affected by Trendyol's anti-bot measures
- Performance depends on network speed and page load times
- Limited to publicly available product information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect Trendyol's terms of service and robots.txt when using this tool.

## Troubleshooting

### Common Issues

**Chrome WebDriver Issues:**

- Ensure Chrome browser is installed
- WebDriver is automatically managed by webdriver-manager

**Connection Problems:**

- Check internet connectivity
- Verify Trendyol website accessibility
- Consider VPN if regional restrictions apply

**Performance Issues:**

- Reduce `target_count` for faster searches
- Lower `max_scroll_attempts` to limit waiting time
- Close other browser instances to free resources

## Support

For issues and questions:

- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---

**Note:** This tool is designed for educational and research purposes. Always comply with Trendyol's terms of service and applicable laws when using web scraping tools.
