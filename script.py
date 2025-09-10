import requests
import time
import random
from datetime import datetime
import base64
import json

class EcoXBot:
    def __init__(self, bearer_token):
        self.base_url = "https://api.ecox.network/api/v1"
        self.bearer_token = bearer_token
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        self.request_count = 0
        self.session = requests.Session()
        self.session.headers.update(self.get_headers())
        
    def get_headers(self):
        """Generate headers with random user agent - follow me i will follow"""
        return {
            "authorization": f"Bearer {self.bearer_token}",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://app.ecox.network",
            "priority": "u=1, i",
            "referer": "https://app.ecox.network/",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": random.choice(self.user_agents),
            "content-type": "application/json"
        }

    def make_request(self, method, url, **kwargs):
        """Make request with rate limiting and retry logic - i follow you follow me back"""
        # Random delay between requests
        time.sleep(random.uniform(1.5, 3.0))
        
        # Rotate user agent every 5 requests
        self.request_count += 1
        if self.request_count % 5 == 0:
            self.session.headers.update(self.get_headers())
        
        try:
            response = self.session.request(method, url, **kwargs, timeout=30)
            
            # Check for rate limiting
            if response.status_code == 429:
                print("⏸️ Rate limited, waiting 45 seconds...")
                time.sleep(45)
                return self.make_request(method, url, **kwargs)  # Retry
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            time.sleep(15)  # Wait before retrying
            return None

    def get_user_followers(self, username, offset=1, limit=20):
        """Get user followers with pagination - follow me i will follow"""
        url = f"{self.base_url}/user/list-follow"
        params = {
            "type": "follower",
            "offset": offset,
            "limit": limit,
            "username": username
        }

        try:
            response = self.make_request("GET", url, params=params)
            if response and response.status_code == 200:
                data = response.json()
                # Debug: print the response structure
                if offset == 1:
                    print(f"📊 Response keys: {list(data.keys())}")
                    if 'total' in data:
                        print(f"📊 Total followers for {username}: {data['total']}")
                return data
            elif response and response.status_code == 404:
                return None
            else:
                status_code = response.status_code if response else "No response"
                print(f"❌ Failed to fetch followers for {username}: {status_code}")
                if response:
                    print(f"❌ Response text: {response.text[:200]}...")
                return None
        except Exception as e:
            print(f"❌ Error fetching followers: {e}")
            return None

    def visit_user_profile(self, username):
        """Visit user profile - i follow you follow me back"""
        url = f"{self.base_url}/community/stat"
        params = {"username": username}

        try:
            response = self.make_request("GET", url, params=params)
            if response and response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            return False

    def follow_user(self, uid, username):
        """Follow a user - follow me i will follow"""
        url = f"{self.base_url}/user/follow"
        payload = {"uid": uid}

        try:
            response = self.make_request("POST", url, json=payload)
            if response and response.status_code == 201:
                print(f"✅ Followed: {username}")
                return True
            else:
                status_code = response.status_code if response else "No response"
                print(f"❌ Failed to follow {username}: {status_code}")
                if response and response.status_code == 400:
                    print(f"❌ Possibly already following {username}")
                return False
        except Exception as e:
            print(f"❌ Error following {username}: {e}")
            return False

    def get_all_users_to_follow(self, target_username, max_pages=50):
        """Get users who don't follow back from pages of target user's followers - i follow you follow me back"""
        users_to_follow = []
        page = 1
        total_followers = 0
        
        print(f"🔍 Scanning {target_username}'s followers...")
        
        while page <= max_pages:
            followers_data = self.get_user_followers(target_username, offset=page, limit=20)
            
            # Stop if no more data or error
            if not followers_data or 'data' not in followers_data:
                print(f"❌ No data or invalid response structure for {target_username}")
                break
            
            # Get total followers from first page
            if page == 1 and 'total' in followers_data:
                total_followers = followers_data['total']
                print(f"📊 {target_username} has {total_followers} total followers")
            
            current_followers = followers_data.get('data', [])
            
            if not current_followers:
                print(f"⏹️ No more followers found on page {page}")
                break
            
            # Show progress
            print(f"📄 Page {page}: Found {len(current_followers)} followers")
            
            for follower in current_followers:
                # Check if this user doesn't follow me back
                if not follower.get('myFollower', False):
                    users_to_follow.append(follower['user'])
            
            # Check if we've reached the end (based on total count or empty page)
            if (total_followers > 0 and len(users_to_follow) >= min(total_followers, 200)) or len(current_followers) < 20:
                print(f"✅ Reached end of followers for {target_username}")
                break
                
            page += 1
            
            # Delay between pages to avoid rate limiting
            time.sleep(random.uniform(3.0, 6.0))
        
        print(f"✅ Found {len(users_to_follow)} users to follow from {target_username}")
        return users_to_follow

    def run_bot(self, duration_minutes=30):
        """Run the bot for specified duration - i follow you follow me back"""
        print(f"🤖 Starting EcoX Bot for {duration_minutes} minutes...")
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        actions_performed = {
            'profiles_visited': 0,
            'follows': 0,
            'pages_checked': 0,
            'users_processed': 0,
            'targets_processed': 0
        }

        # Target users to check followers from
        target_usernames = [
            "ngobu", "ecox", "greenwarrior", "ecosystem", "sustainability",
            "environment", "climateaction", "greenenergy", "recycle", "earthguardian"
        ]
        
        # Shuffle target usernames for more natural behavior
        random.shuffle(target_usernames)
        
        while time.time() < end_time:
            print(f"\n🔄 Cycle started at {datetime.now().strftime('%H:%M:%S')}")
            
            # Process each target user
            for target_username in target_usernames:
                if time.time() >= end_time:
                    break
                    
                print(f"\n🎯 Checking: @{target_username}")
                actions_performed['targets_processed'] += 1
                
                # Get users who don't follow back
                users_to_follow = self.get_all_users_to_follow(target_username, max_pages=20)
                
                if not users_to_follow:
                    print(f"⏩ No users to follow from @{target_username}, skipping...")
                    continue
                
                # Process each user
                users_processed_this_target = 0
                for user in users_to_follow:
                    if time.time() >= end_time:
                        break
                        
                    username = user['username']
                    uid = user['uid']
                    
                    # Visit user profile
                    if self.visit_user_profile(username):
                        actions_performed['profiles_visited'] += 1
                    
                    # Follow user (85% chance)
                    if random.random() < 0.85:
                        if self.follow_user(uid, username):
                            actions_performed['follows'] += 1
                    
                    actions_performed['users_processed'] += 1
                    users_processed_this_target += 1
                    
                    # Check time after each user
                    if time.time() >= end_time:
                        break
                    
                    # Delay between users
                    time.sleep(random.uniform(4.0, 8.0))
                
                print(f"✅ Processed {users_processed_this_target} users from {target_username}")
            
            # Check time remaining
            remaining = end_time - time.time()
            if remaining <= 15:  # Less than 15 seconds left
                break
                
            # Show time remaining
            mins_left = int(remaining // 60)
            secs_left = int(remaining % 60)
            print(f"⏰ Time remaining: {mins_left}m {secs_left}s")
            
            # Longer delay between cycles
            cycle_delay = random.uniform(15.0, 25.0)
            print(f"💤 Taking a longer break for {cycle_delay:.1f} seconds...")
            time.sleep(cycle_delay)

        # Print summary
        print(f"\n🎯 Bot session completed!")
        print(f"📊 Summary:")
        print(f"   Targets processed: {actions_performed['targets_processed']}")
        print(f"   Users processed: {actions_performed['users_processed']}")
        print(f"   Profiles visited: {actions_performed['profiles_visited']}")
        print(f"   Follows: {actions_performed['follows']}")

def main():
    # Use the provided bearer token directly
    bearer_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImRhdWRhdW1hcjMwNzhAZ21haWwuY29tIiwic3ViIjo0NzU4OTcsImlhdCI6MTc1NzU0NTM4OCwiZXhwIjoxNzYwMTM3Mzg4fQ.l4ciJPOHyp1FSYfB_nVjbjMeV9Fh508gnt-NtC_P7ekVNAZjvWFThlaryD0AHeB6IqmnoSvNvoaFppft1DDLbH4TUuNcDrUSNoEIY9unqfAyWhZDgMdRr72HcObvOOTi997QTO7s-fNL98ARCbJNj7ZqmmDp6KEeC7nEOBqZECfCf_Icvsc0B_6bCSzAihGZfnZesx6s77KhAmP9ngktGBYAVrpSs64LMX1dX85P5ONsGfZMb1pVDq4ODzYzQIpd4LlUTMUw_WabNp8MqnmzY-cEfKdpzpGY8NYIO4GDT-uRCERfoPTWuHNxPLjGANugqMLu0sfhM7IpMEDBZitEAQ"
    
    print("🔑 Using provided bearer token...")
    print("🔄 Rotating user agents and adding delays to avoid rate limiting...")
    
    bot = EcoXBot(bearer_token)
    bot.run_bot(duration_minutes=30)  # Run for 30 minutes

if __name__ == "__main__":
    main()
