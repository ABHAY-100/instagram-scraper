import os, json, uuid, re
from instaloader import Instaloader, Post
from urllib.parse import urlparse

def extract_hashtags(caption):
    return re.findall(r'#\w+', caption) if caption else []

def get_post_details(post_url):
    try:
        shortcode = re.search(r'/(?:p|reel)/([^/]+)', urlparse(post_url).path).group(1)
        post = Post.from_shortcode(Instaloader().context, shortcode)
        
        media_urls = [post.url]
        if post.is_video:
            media_urls.append(post.video_url)
        if post.mediacount > 1:
            media_urls.extend([n.display_url for n in post.get_sidecar_nodes()])
        
        return {
            'shortcode': post.shortcode,
            'caption': post.caption,
            'date': post.date_local.strftime("%Y-%m-%d %H:%M:%S"),
            'likes': post.likes,
            'comments': post.comments,
            'location': post.location,
            'author': post.owner_username,
            'media_urls': list(set(media_urls)),
            'tagged_users': list(post.tagged_users),
            'hashtags': extract_hashtags(post.caption),
            'mentions': list(post.caption_mentions),
            'accessibility_caption': post.accessibility_caption,
            'view_count': post.video_view_count if post.is_video else None,
            'media_count': getattr(post, 'mediacount', 1)
        }
    except Exception as e: return f"Error: {e}"

def save_to_json(data, folder='data'):
    if not os.path.exists(folder): os.makedirs(folder)
    file_path = os.path.join(folder, f"post_details_{uuid.uuid4()}.json")
    with open(file_path, 'w') as f: json.dump(data, f, indent=4)

if __name__ == "__main__":
    if result := get_post_details(input("Enter the public Instagram post URL: ")):
        save_to_json(result)
