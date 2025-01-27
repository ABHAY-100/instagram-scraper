import os
import json
import uuid
try:
    from instaloader import Instaloader, Profile
except ImportError:
    print("Error: Required module 'instaloader' not found.")
    print("Please install it using: pip install instaloader")
    exit(1)

def get_profile_details(username):
    try:
        L = Instaloader()
        profile = Profile.from_username(L.context, username)

        print(f"Fetching details for {username}...")  # Logging

        profile_info = {
            'username': profile.username,
            'full_name': profile.full_name,
            'biography': profile.biography,
            'profile_pic_url': profile.profile_pic_url,
            'external_url': profile.external_url,
            'is_private': profile.is_private,
            'is_verified': profile.is_verified,
            'followers': profile.followers,
            'following': profile.followees,
            'posts_count': profile.mediacount,
        }

        print(f"Successfully fetched details for {username}.")  # Logging
        return profile_info

    except Exception as e:
        print(f"Error fetching profile details: {str(e)}")  # Logging
        return None

def save_to_json(data, username, folder='data'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    unique_filename = f"{username}_profile_details_{uuid.uuid4()}.json"
    file_path = os.path.join(folder, unique_filename)

    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    username = input("Enter the Instagram username: ")

    result = get_profile_details(username)
    save_to_json(result, username)