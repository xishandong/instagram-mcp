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

    # Extract images and video
    images = []
    video_url = None

    show_div = soup.find('div', class_='show')
    if show_div:
        # Check if it's a video post (has video tag)
        video_tag = show_div.find('video')
        if video_tag:
            video_url = video_tag.get('src') or video_tag.get('data-src')
            if video_url:
                if video_url.startswith('//'):
                    video_url = 'https:' + video_url
                elif video_url.startswith('/') and post_url:
                    from urllib.parse import urljoin
                    video_url = urljoin(post_url, video_url)
        else:
            # It's an image post
            # Case 1: Multi-image post with swiper-container
            swiper_container = show_div.find('div', class_='swiper-container')
            if swiper_container:
                swiper_slides = swiper_container.find_all('div', class_='swiper-slide')
                for slide in swiper_slides:
                    data_src = slide.get('data-src')
                    if data_src and 'base64' not in str(data_src):
                        # Clean up the URL (remove HTML entities)
                        clean_url = data_src.replace('&#38;', '&')
                        images.append(clean_url)
            # Case 2: Single-image post with direct img tag in media-wrap
            else:
                media_wrap = show_div.find('div', class_='media-wrap')
                if media_wrap:
                    img_tag = media_wrap.find('img')
                    if img_tag:
                        src = img_tag.get('src')
                        if src and 'base64' not in str(src) and 'lazy.jpg' not in src:
                            images.append(src)

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
    username_div = soup.find('div', class_='username')
    if username_div:
        h2_elem = username_div.find('h2')
        if h2_elem:
            user_info['username'] = h2_elem.get_text().strip().replace('@', '')

    fullname_div = soup.find('div', class_='fullname')
    if fullname_div:
        h1_elem = fullname_div.find('h1')
        if h1_elem:
            user_info['fullname'] = h1_elem.get_text().strip()

    # User profile URL
    user_link = soup.find('a', href=re.compile(r'^/[^/]+/$'))
    if user_link and user_link.get('href'):
        user_profile_url = f"https://imginn.com{user_link['href']}"
        user_info['profile_url'] = user_profile_url

    # Extract tagged users
    tagged_users = []
    tagged_users_div = soup.find('div', class_='tagged-users')
    if tagged_users_div:
        tagged_user_list = tagged_users_div.find('div', class_='tagged-user-list')
        if tagged_user_list:
            tagged_user_links = tagged_user_list.find_all('a', class_='tagged-user')
            for link in tagged_user_links:
                user_data = {}
                # Extract username from href
                href = link.get('href')
                if href:
                    # Extract username from /username/ format
                    username_match = re.search(r'/([^/]+)/$', href)
                    if username_match:
                        user_data['username'] = username_match.group(1)
                        user_data['profile_url'] = f"https://imginn.com{href}"

                # Extract profile picture
                img_tag = link.find('img')
                if img_tag and img_tag.get('src'):
                    user_data['profile_pic'] = img_tag['src']

                # Extract display name
                name_div = link.find('div', class_='name')
                if name_div:
                    user_data['display_name'] = name_div.get_text().strip()

                if user_data:
                    tagged_users.append(user_data)

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
        "tagged_users": tagged_users,
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

    # Extract tagged users
    tagged_users = []
    tagged_users_data = safe_get(data, 'tagged_users') or safe_get(data, 'taggedUsers') or safe_get(data, 'mentions')
    if isinstance(tagged_users_data, list):
        for user in tagged_users_data:
            if isinstance(user, dict):
                tagged_user = {}
                tagged_user['username'] = safe_get(user, 'username') or safe_get(user, 'name') or safe_get(user,
                                                                                                           'display_name')
                tagged_user['display_name'] = safe_get(user, 'display_name') or safe_get(user,
                                                                                         'full_name') or tagged_user.get(
                    'username', '')
                tagged_user['profile_url'] = safe_get(user, 'profile_url') or safe_get(user, 'url') or safe_get(user,
                                                                                                                'profile_pic')
                tagged_user['profile_pic'] = safe_get(user, 'profile_pic') or safe_get(user, 'avatar') or safe_get(user,
                                                                                                                   'picture')
                if tagged_user.get('username'):
                    tagged_users.append(tagged_user)

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
        "tagged_users": tagged_users,
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
