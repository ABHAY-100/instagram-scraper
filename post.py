import os
import json
import uuid
from instaloader import Instaloader, Post
from urllib.parse import urlparse
import re
from datetime import datetime

def extract_hashtags(caption):
    """Extract hashtags from the caption text."""
    if caption:
        return re.findall(r'#\w+', caption)
    return []

def get_post_details(post_url):
    try:
        L = Instaloader()
        
        path = urlparse(post_url).path
        shortcode_match = re.search(r'/p/([^/]+)|/reel/([^/]+)', path)
        
        if not shortcode_match:
            return "Error: Invalid Instagram post or reel URL."
        
        shortcode = shortcode_match.group(1) or shortcode_match.group(2)
        
        post = Post.from_shortcode(L.context, shortcode)
        
        media_urls = [post.url]
        
        if post.is_video:
            media_urls.append(post.video_url)
        
        if post.mediacount > 1:
            media_urls.extend([node.display_url for node in post.get_sidecar_nodes()])
        
        media_urls = list(set(media_urls))
        
        post_info = {
            'shortcode': post.shortcode,
            'caption': post.caption,
            'date': post.date_local.strftime("%Y-%m-%d %H:%M:%S"),
            'likes': post.likes,
            'comments': post.comments,
            'location': post.location,
            'author': post.owner_username,
            'media_urls': media_urls,
            'tagged_users': list(post.tagged_users),
            'hashtags': extract_hashtags(post.caption),
            'mentions': list(post.caption_mentions),
            'accessibility_caption': post.accessibility_caption,
            'view_count': post.video_view_count if post.is_video else None,
            'media_count': post.mediacount if hasattr(post, 'mediacount') else 1
        }
        
        return post_info
        
    except Exception as e:
        return f"Error fetching post details: {str(e)}"

def save_to_json(data, folder='data'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    unique_filename = f"post_details_{uuid.uuid4()}.json"
    file_path = os.path.join(folder, unique_filename)
    
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    post_url = input("Enter the public Instagram post URL: ")
    
    result = get_post_details(post_url)
    save_to_json(result)
