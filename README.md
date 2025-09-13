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

### Claude Desktop Configuration

For Claude Desktop, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "trendyol-search": {
      "command": "python",
      "args": ["/path/to/trendyol_mcp_server.py"]
    }
  }
}
```

## License

This project is for educational and research purposes. Please respect Trendyol's terms of service and robots.txt when using this tool.

## Support

For issues and questions:

- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---

**Note:** This tool is designed for educational and research purposes. Always comply with Trendyol's terms of service and applicable laws when using web scraping tools.
