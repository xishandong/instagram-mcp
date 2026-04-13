import re
from typing import Dict, Any

from bs4 import BeautifulSoup


def parse_html_post(html_content: str) -> Dict[str, Any]:
    """
    Parse HTML post content and extract normalized fields.
    Specifically designed for imginn.com Instagram post pages.
    Supports carousel posts with mixed images and videos.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract post URL (from canonical link)
    post_url = None
    canonical = soup.find('link', {'rel': 'canonical'})
    if canonical and canonical.get('href'):
        post_url = canonical['href']

    # Extract images and videos from all slides
    images = []
    videos = []

    show_div = soup.find('div', class_='show')
    if show_div:
        # Check for swiper-container (carousel/multi-media post)
        swiper_container = show_div.find('div', class_='swiper-container')
        if swiper_container:
            # Multi-media carousel post
            swiper_slides = swiper_container.find_all('div', class_='swiper-slide')
            for slide in swiper_slides:
                # Check if this slide contains a video
                media_wrap = slide.find('div', class_='media-wrap')
                if not media_wrap:
                    continue

                # Check for video tag
                video_tag = media_wrap.find('video')
                if video_tag:
                    # This is a video slide
                    video_src = video_tag.get('src')
                    if video_src:
                        if video_src.startswith('//'):
                            video_src = 'https:' + video_src
                        elif video_src.startswith('/') and post_url:
                            from urllib.parse import urljoin
                            video_src = urljoin(post_url, video_src)
                        videos.append(video_src)
                else:
                    # This is an image slide
                    img_tag = media_wrap.find('img')
                    if img_tag:
                        # Try data-src first (lazy loaded), then src
                        src = img_tag.get('data-src') or img_tag.get('src')
                        if src and 'base64' not in str(src) and 'lazy.jpg' not in src:
                            images.append(src)
        else:
            # Single media post (image or video)
            video_tag = show_div.find('video')
            if video_tag:
                # Single video post
                video_src = video_tag.get('src') or video_tag.get('data-src')
                if video_src:
                    if video_src.startswith('//'):
                        video_src = 'https:' + video_src
                    elif video_src.startswith('/') and post_url:
                        from urllib.parse import urljoin
                        video_src = urljoin(post_url, video_src)
                    videos.append(video_src)
            else:
                # Single image post
                media_wrap = show_div.find('div', class_='media-wrap')
                if media_wrap:
                    img_tag = media_wrap.find('img')
                    if img_tag:
                        src = img_tag.get('data-src') or img_tag.get('src')
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
        "videos": videos,
        "likes": likes,
        "comments": comments,
        "user_info": user_info,
        "tagged_users": tagged_users,
        "post_content": post_content,
        "timestamp": timestamp,
        "post_type": "carousel" if (images and videos) else "video" if videos else "image" if images else "unknown"
    }

