#!/usr/bin/env python3
"""
Unified Post Parser for HTML and JSON inputs (image/video posts)
Normalizes fields from both sources into a consistent JSON structure.
"""

import json
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup


def parse_html_post(html_content: str) -> Dict[str, Any]:
    """
    Parse HTML post content and extract normalized fields.
    Specifically designed for imginn.com Instagram post pages.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract post URL (from canonical link)
    post_url = None
    canonical = soup.find('link', {'rel': 'canonical'})
    if canonical and canonical.get('href'):
        post_url = canonical['href']

    # Extract images - only from main post swiper-slide data-src attributes (high quality)
    # Do NOT fallback to other img tags to avoid extracting user avatars, arrows, etc.
    images = []

    # Primary method: get data-src from swiper-slide divs within the main .show container
    # This avoids picking up images from the "More posts" recommendation section
    show_div = soup.find('div', class_='show')
    if show_div:
        swiper_container = show_div.find('div', class_='swiper-container')
        if swiper_container:
            swiper_slides = swiper_container.find_all('div', class_='swiper-slide')
            for slide in swiper_slides:
                data_src = slide.get('data-src')
                if data_src and 'base64' not in str(data_src):
                    # Clean up the URL (remove HTML entities)
                    clean_url = data_src.replace('&#38;', '&')
                    images.append(clean_url)

    # For video posts, there might be no images in swiper-slides, so we don't add any fallback
    # This prevents extracting user avatars, arrow icons, and other unrelated images

    # Extract video - look for video tags (though imginn seems to be image-only)
    video_url = None
    video_tag = soup.find('video')
    if video_tag:
        video_url = video_tag.get('src') or video_tag.get('data-src')
        if video_url:
            if video_url.startswith('//'):
                video_url = 'https:' + video_url
            elif video_url.startswith('/') and post_url:
                from urllib.parse import urljoin
                video_url = urljoin(post_url, video_url)

    # Extract likes and comments from post-stats div
    likes = 0
    comments = 0

    # Look for the post-stats div which contains likes-count and comments-count
    post_stats = soup.find('div', class_='post-stats')
    if post_stats:
        # Extract likes
        likes_elem = post_stats.find('div', class_='likes-count')
        if likes_elem:
            likes_span = likes_elem.find('span')
            if likes_span:
                try:
                    likes = int(likes_span.get_text().replace(',', ''))
                except (ValueError, AttributeError):
                    pass

        # Extract comments
        comments_elem = post_stats.find('div', class_='comments-count')
        if comments_elem:
            comments_span = comments_elem.find('span')
            if comments_span:
                try:
                    comments = int(comments_span.get_text().replace(',', ''))
                except (ValueError, AttributeError):
                    pass

    # If post-stats not found, try data-comment-count attribute on page-post div
    if comments == 0:
        page_post = soup.find('div', class_='page-post')
        if page_post:
            comment_count = page_post.get('data-comment-count')
            if comment_count:
                try:
                    comments = int(comment_count)
                except ValueError:
                    pass

    # Extract user info
    user_info = {}
    username_elem = soup.find('div', class_='username')
    if username_elem:
        user_info['username'] = username_elem.get_text().strip().replace('@', '')

    fullname_elem = soup.find('div', class_='fullname')
    if fullname_elem:
        user_info['fullname'] = fullname_elem.get_text().strip()

    # User profile URL
    user_link = soup.find('a', href=re.compile(r'^/[^/]+/$'))
    if user_link and user_link.get('href'):
        user_profile_url = f"https://imginn.com{user_link['href']}"
        user_info['profile_url'] = user_profile_url

    # Extract post content/caption
    post_content = ""
    desc_div = soup.find('div', class_='desc')
    if desc_div:
        # Get all text content, excluding share links
        share_to = desc_div.find('ul', class_='share-to')
        if share_to:
            share_to.decompose()
        post_content = desc_div.get_text().strip()

    # Extract timestamp
    timestamp = None
    post_time_div = soup.find('div', class_='post-time')
    if post_time_div:
        timestamp = post_time_div.get_text().replace('Posted On: ', '').strip()

    return {
        "post_url": post_url,
        "images": images,
        "video_url": video_url,
        "likes": likes,
        "comments": comments,
        "user_info": user_info,
        "post_content": post_content,
        "timestamp": timestamp,
        "post_type": "video" if video_url else "image" if images else "unknown"
    }


def parse_json_post(json_content: str) -> Dict[str, Any]:
    """
    Parse JSON post content and extract normalized fields.
    Assumes JSON structure varies but contains similar information.
    """
    try:
        data = json.loads(json_content)
    except json.JSONDecodeError:
        # If it's not valid JSON, try to extract JSON from within
        # Sometimes JSON is embedded in HTML or has extra characters
        json_match = re.search(r'\{.*\}', json_content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON content")
        else:
            raise ValueError("Invalid JSON content")

    def safe_get(obj, *keys, default=None):
        """Safely get nested dictionary values"""
        for key in keys:
            if isinstance(obj, dict) and key in obj:
                obj = obj[key]
            else:
                return default
        return obj

    # Extract post URL
    post_url = safe_get(data, 'post_url') or safe_get(data, 'url') or safe_get(data, 'link')

    # Extract images
    images = []
    # Common image field names
    image_fields = ['images', 'image_urls', 'photos', 'media', 'attachments']
    for field in image_fields:
        imgs = safe_get(data, field)
        if imgs:
            if isinstance(imgs, list):
                if all(isinstance(img, str) for img in imgs):
                    images.extend(imgs)
                elif all(isinstance(img, dict) for img in imgs):
                    # Extract URL from image objects
                    for img in imgs:
                        url = safe_get(img, 'url') or safe_get(img, 'src') or safe_get(img, 'link')
                        if url:
                            images.append(url)
            elif isinstance(imgs, dict):
                url = safe_get(imgs, 'url') or safe_get(imgs, 'src')
                if url:
                    images.append(url)
            elif isinstance(imgs, str):
                images.append(imgs)

    # Extract video
    video_url = None
    video_fields = ['video_url', 'video', 'video_link', 'media_url']
    for field in video_fields:
        video_url = safe_get(data, field)
        if video_url:
            break
    if not video_url:
        # Check if media array contains video
        media = safe_get(data, 'media') or safe_get(data, 'attachments')
        if isinstance(media, list):
            for item in media:
                if isinstance(item, dict):
                    media_type = safe_get(item, 'type', default='').lower()
                    if 'video' in media_type:
                        video_url = safe_get(item, 'url') or safe_get(item, 'src')
                        if video_url:
                            break

    # Extract likes and comments
    likes = safe_get(data, 'likes') or safe_get(data, 'like_count') or safe_get(data, 'reactions', 'like') or 0
    comments = safe_get(data, 'comments') or safe_get(data, 'comment_count') or safe_get(data, 'comments_count') or 0

    # Ensure numeric values
    try:
        likes = int(likes)
    except (ValueError, TypeError):
        likes = 0
    try:
        comments = int(comments)
    except (ValueError, TypeError):
        comments = 0

    # Extract user info
    user_info = {}
    user_data = safe_get(data, 'user') or safe_get(data, 'author') or safe_get(data, 'creator')
    if user_data:
        if isinstance(user_data, dict):
            user_info['username'] = safe_get(user_data, 'username') or safe_get(user_data, 'name') or safe_get(
                user_data, 'display_name')
            user_info['fullname'] = safe_get(user_data, 'fullname') or safe_get(user_data, 'full_name')
            user_info['profile_url'] = safe_get(user_data, 'profile_url') or safe_get(user_data, 'url')
        else:
            user_info['username'] = str(user_data)

    # Extract post content
    post_content = safe_get(data, 'content') or safe_get(data, 'caption') or safe_get(data, 'text') or safe_get(data,
                                                                                                                'description')

    # Extract timestamp
    timestamp = safe_get(data, 'timestamp') or safe_get(data, 'created_at') or safe_get(data, 'date')

    return {
        "post_url": post_url,
        "images": images,
        "video_url": video_url,
        "likes": likes,
        "comments": comments,
        "user_info": user_info,
        "post_content": post_content,
        "timestamp": timestamp,
        "post_type": "video" if video_url else "image" if images else "unknown"
    }


def normalize_post_data(input_content: str, input_type: str = "auto") -> Dict[str, Any]:
    """
    Main function to parse and normalize post data.

    Args:
        input_content: The HTML or JSON content to parse
        input_type: "html", "json", or "auto" (default)

    Returns:
        Normalized dictionary with consistent fields
    """
    if input_type == "auto":
        # Try to detect format
        stripped = input_content.strip()
        if stripped.startswith('{') and stripped.endswith('}'):
            input_type = "json"
        elif '<' in stripped and '>' in stripped:
            input_type = "html"
        else:
            # Default to JSON if ambiguous, but this might fail
            input_type = "json"

    if input_type == "json":
        return parse_json_post(input_content)
    else:
        return parse_html_post(input_content)


# Example usage and testing
if __name__ == "__main__":
    # Test with sample HTML file
    try:
        with open('post.html', 'r', encoding='utf-8') as f:
            html_content = f.read()

        result = normalize_post_data(html_content, "html")
        print("HTML Parse Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except FileNotFoundError:
        print("post.html not found for testing")
