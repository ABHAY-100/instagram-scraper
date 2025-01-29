import os
import json
import uuid
from datetime import datetime
from instaloader import Instaloader, Profile
from post import extract_hashtags

def instagram_login():
    """Handle Instagram login"""
    L = Instaloader()
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    
    try:
        print("Logging in to Instagram...")
        L.login(username, password)
        print("Login successful!")
        return L
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return None

def get_homepage_posts(username, max_posts=10):
    """
    Fetch recent posts from a user's Instagram homepage
    max_posts: Maximum number of posts to fetch (default: 10)
    """
    try:
        L = instagram_login()  # Get authenticated instance
        if not L:
            return None
            
        profile = Profile.from_username(L.context, username)
        
        print(f"Fetching recent posts from {username}'s homepage...")
        
        posts_data = []
        post_count = 0
        
        for post in profile.get_posts():
            if post_count >= max_posts:
                break
                
            post_info = {
                'shortcode': post.shortcode,
                'caption': post.caption,
                'date': post.date_local.strftime("%Y-%m-%d %H:%M:%S"),
                'likes': post.likes,
                'comments': post.comments,
                'location': post.location,
                'is_video': post.is_video,
                'media_urls': [post.url],
                'hashtags': extract_hashtags(post.caption),
                'mentions': list(post.caption_mentions),
                'accessibility_caption': post.accessibility_caption
            }
            
            if post.is_video:
                post_info['video_url'] = post.video_url
                post_info['view_count'] = post.video_view_count
                
            if post.mediacount > 1:
                post_info['media_urls'].extend([node.display_url for node in post.get_sidecar_nodes()])
                post_info['media_urls'] = list(set(post_info['media_urls']))
            
            posts_data.append(post_info)
            post_count += 1
            print(f"Processed post {post_count}/{max_posts}")
            
        return posts_data
        
    except Exception as e:
        print(f"Error fetching homepage posts: {str(e)}")
        return None

def get_my_homepage_posts(max_posts=10):
    """Fetch posts from your own homepage after login"""
    try:
        L = instagram_login()
        if not L:
            return None
            
        # Get logged in user's profile
        username = L.context.username
        profile = Profile.from_username(L.context, username)
        
        print(f"Successfully logged in as {username}")
        print(f"Fetching your recent posts...")
        
        posts_data = []
        post_count = 0
        
        for post in profile.get_posts():
            if post_count >= max_posts:
                break
                
            print(f"Fetching post {post_count + 1}/{max_posts}")
            
            # Get post details including media
            post_info = {
                'shortcode': post.shortcode,
                'caption': post.caption,
                'date': post.date_local.strftime("%Y-%m-%d %H:%M:%S"),
                'likes': post.likes,
                'comments': post.comments,
                'location': post.location,
                'is_video': post.is_video,
                'media_urls': [post.url],
                'hashtags': extract_hashtags(post.caption),
                'mentions': list(post.caption_mentions)
            }
            
            if post.is_video:
                post_info['video_url'] = post.video_url
                post_info['view_count'] = post.video_view_count
                
            posts_data.append(post_info)
            post_count += 1
            
        return posts_data, username
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None

def get_public_profile_posts(username, max_posts=10):
    """Fetch posts from a public Instagram profile without login"""
    try:
        L = Instaloader()
        print(f"Fetching public posts from {username}'s profile...")
        
        try:
            profile = Profile.from_username(L.context, username)
        except Exception as e:
            print(f"Error: Could not find profile '{username}' or profile is private")
            return None
            
        if profile.is_private:
            print(f"Error: {username}'s profile is private. Cannot fetch posts.")
            return None
            
        posts_data = []
        post_count = 0
        
        for post in profile.get_posts():
            if post_count >= max_posts:
                break
                
            print(f"Fetching post {post_count + 1}/{max_posts}")
            
            post_info = {
                'shortcode': post.shortcode,
                'caption': post.caption if post.caption else "",
                'date': post.date_local.strftime("%Y-%m-%d %H:%M:%S"),
                'likes': post.likes,
                'comments': post.comments,
                'media_urls': [post.url],
                'hashtags': extract_hashtags(post.caption),
                'is_video': post.is_video
            }
            
            posts_data.append(post_info)
            post_count += 1
            
        return posts_data
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def save_homepage_data(data, username, folder='data'):
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{username}_homepage_posts_{timestamp}.json"
    file_path = os.path.join(folder, unique_filename)
    
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Homepage data saved to {file_path}")

if __name__ == "__main__":
    username = input("Enter the Instagram username to scrape: ")
    max_posts = int(input("Enter number of posts to fetch (default 10): ") or 10)
    
    posts_data = get_public_profile_posts(username, max_posts)
    if posts_data:
        save_homepage_data(posts_data, username)
