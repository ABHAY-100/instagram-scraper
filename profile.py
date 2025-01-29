import os, json, uuid, re
from instaloader import Instaloader, Profile

def extract_urls(text):
    if not text: return []
    urls = re.findall(r'https?://(?:[-\w\.]+)(?:[-\w\._~:/?#\[\]@!$&\'\(\)\*\+,;=])*', text)
    return [url.rstrip('.,)') for url in urls]

def get_latest_posts(profile, num_posts=3):
    posts = []
    try:
        for idx, post in enumerate(profile.get_posts()):
            if idx >= num_posts: break
            post_data = {
                'shortcode': post.shortcode,
                'caption': post.caption or "",
                'date': post.date_local.strftime("%Y-%m-%d %H:%M:%S"),
                'likes': post.likes,
                'comments': post.comments,
                'is_video': post.is_video,
                'url': post.url,
                'media_urls': [post.url],
                'hashtags': list(post.caption_hashtags),
                'mentions': list(post.caption_mentions),
                'location': post.location
            }
            if post.is_video:
                post_data.update({'video_url': post.video_url, 'view_count': post.video_view_count})
            if post.mediacount > 1:
                post_data['media_urls'].extend([n.display_url for n in post.get_sidecar_nodes()])
                post_data['media_urls'] = list(set(post_data['media_urls']))
            posts.append(post_data)
    except Exception as e: print(f"Error fetching posts: {e}")
    return posts

def get_profile_details(username, include_posts=True, num_posts=3):
    try:
        profile = Profile.from_username(Instaloader().context, username)
        all_urls = []
        
        if profile.external_url:
            all_urls.append(profile.external_url)
            all_urls.extend(extract_urls(profile.external_url))
        if profile.biography:
            all_urls.extend(extract_urls(profile.biography))
            
        final_urls = []
        for url in all_urls:
            url = ('http://' + url) if 'apple.co' in url and not url.startswith('http') else url
            final_urls.append(url.rstrip('/.,:;'))
            
        profile_info = {
            'username': profile.username,
            'full_name': profile.full_name,
            'biography': profile.biography,
            'profile_pic_url': profile.profile_pic_url,
            'external_urls': list(dict.fromkeys(final_urls)),
            'is_private': profile.is_private,
            'is_verified': profile.is_verified,
            'followers': profile.followers,
            'following': profile.followees,
            'posts_count': profile.mediacount,
        }
        
        if include_posts:
            profile_info['latest_posts'] = get_latest_posts(profile, num_posts)
        return profile_info
    except Exception as e: 
        print(f"Error: {e}")
        return None

def save_to_json(data, username, folder='data'):
    if not os.path.exists(folder): os.makedirs(folder)
    file_path = os.path.join(folder, f"{username}_profile_details_{uuid.uuid4()}.json")
    with open(file_path, 'w') as f: json.dump(data, f, indent=4)

if __name__ == "__main__":
    username = input("Enter the Instagram username: ")
    num_posts = int(input("Enter number of latest posts to fetch (default 3): ") or 3)
    if result := get_profile_details(username, True, num_posts):
        save_to_json(result, username)