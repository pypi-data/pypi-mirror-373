import json
import sqlite3
import urllib.parse
from bs4 import BeautifulSoup  
import requests
from flask import jsonify
import time

def duckduckgo_search(query, max_results=5):
    """
    Perform a web search using DuckDuckGo.
    """
    search_url = f"https://www.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = safe_request(search_url, headers)
    if not response:
        print("Failed to fetch search results.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    search_results = []

    for result in soup.select(".result__title a")[:max_results]:
        raw_link = result["href"]

        # Extract actual URL from DuckDuckGo redirect
        parsed_link = urllib.parse.parse_qs(urllib.parse.urlparse(raw_link).query).get("uddg")
        if parsed_link:
            actual_url = parsed_link[0]  # Extract first element from list
            title = result.get_text()
            search_results.append((title, actual_url))

    return search_results


def extract_article_text(url):
    """
    Extract meaningful text from a web article.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = safe_request(url, headers)

    if not response:
        print(f"Failed to fetch content from {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Try multiple content selectors
    content_selectors = [
        ("div", "article-content"),
        ("article", None),
        ("div", "content"),
        ("div", "main-content"),
        ("div", "entry-content"),
        ("div", "post-content"),
        ("div", "article-body"),
        ("section", "content-section"),
        ("div", "story-body"),
        ("div", "news-content"),
        ("div", "news-article"),
        ("div", "article"),
        ("section", "article-body"),
        ("div", "article-text"),
        ("div", "story"),
        ("div", "news-body"),
        ("body", None)  # Last resort (entire page)
    ]

    unwanted_keywords = [
        "Sign in", "Log into your account", "Forgot your password?", "Recover your password",
        "Subscribe", "Get help", "Navigation", "Menu", "Search", "Welcome!", "Watch & Bet",
        "Follow us on", "Trending", "Latest news", "Social media", "Facebook", "Twitter", "Instagram", "Youtube"
    ]

    for tag, class_name in content_selectors:
        content_block = soup.find(tag, class_=class_name) if class_name else soup.find(tag)
        if content_block:
            extracted_text = content_block.get_text("\n", strip=True)

            # Remove lines containing unwanted keywords
            extracted_lines = [line for line in extracted_text.split("\n") if
                               not any(keyword in line for keyword in unwanted_keywords)]
            cleaned_text = "\n".join(extracted_lines)

            # Check if extracted content is meaningful (not just a few words)
            if len(cleaned_text.split()) > 50:  # Only return text if it's longer than 50 words
                return cleaned_text

    print("Could not find meaningful article content.")
    return None

def web_search(query_string: str, num_results: int) -> str:
    """
    Perform a web search using DuckDuckGo and cache results in SQLite.
    Returns formatted search results as a string.
    """
    conn = sqlite3.connect('context_database.db')
    cursor = conn.cursor()
    
    try:
        # Check if we have cached results
        cursor.execute('SELECT results FROM web_search_results WHERE query = ? AND timestamp > datetime("now", "-1 day")', (query_string,))
        cached_result = cursor.fetchone()
        
        if cached_result:
            conn.close()
            return cached_result[0]
        
        search_results = duckduckgo_search(query_string, max_results=num_results)

        if not search_results:
            return json.dumps({"error": "No search results found."})

        extracted_articles = []
        
        for title, link in search_results:
            article_text = extract_article_text(link)
            
            if article_text:
                extracted_articles.append({
                    "title": title,
                    "link": link,
                    "text": article_text # Limit to first 1000 characters to avoid excessive length
                })
        
        if not extracted_articles:
            return jsonify({"error": "Failed to extract relevant article content from search results."})

        # Convert results to JSON string before storing
        results_json = json.dumps({
            "source": "live_search",
            "search_results": extracted_articles
        })
        
        # Store the results in the database
        cursor.execute('''
            INSERT INTO web_search_results (query, results) 
            VALUES (?, ?)
        ''', (query_string, results_json))
        conn.commit()
        
        return results_json
    
    except Exception as e:
        print(f"Error in web_search: {e}")
        return json.dumps({"error": str(e)})  # Return error as JSON string
    
    finally:
        conn.close()

def safe_request(url, headers=None, max_retries=3, timeout=10):
    """
    Safely fetch a URL with retries and exponential backoff.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
            if attempt < max_retries - 1:  # Don't wait after the last attempt
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Failed to fetch {url} after multiple retries.")
                return None
