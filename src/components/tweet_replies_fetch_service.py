import requests
import json
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv(dotenv_path='.env.prod')

class TweetRepliesFetchService:
    def __init__(self):
        self.api_url = os.getenv("TWITTER_API_URL")
        self.headers = {"X-API-Key": os.getenv("TWITTER_API_KEY")}
        self.replies = []  # List to store all reply tweets

    def get_tweet_replies(self, tweet_id: str, max_replies: int = 100):
        """
        Fetch replies for a specific tweet ID.
        Args:
            tweet_id (str): The ID of the tweet to fetch replies for
            max_replies (int): Maximum number of replies to fetch (default: 100)
        Returns:
            list: List of reply tweets with their details
        """
        logging.info(f"Starting to fetch replies for tweet ID: {tweet_id}")
        self.replies.clear()

        try:
            # Make the request directly to get replies
            response = requests.request(
                "GET",
                self.api_url,
                headers=self.headers,
                params={"tweetId": tweet_id},
                timeout=10
            )
            logging.info(f"Response status: {response.status_code}")
            logging.info(f"Response content: {response.text}")
            
            replies_data = response.json()
            
            if "tweets" in replies_data and isinstance(replies_data["tweets"], list):
                for reply in replies_data["tweets"]:
                    reply_info = {
                        "reply_id": reply["id"],
                        "author_id": reply.get("author_id"),
                        "author_username": reply.get("author", {}).get("username"),
                        "text": reply["text"],
                        "created_at": reply.get("created_at"),
                        "metrics": {
                            "likes": reply.get("likes_count", 0),
                            "retweets": reply.get("retweets_count", 0),
                            "replies": reply.get("replies_count", 0)
                        }
                    }
                    self.replies.append(reply_info)
                
                logging.info(f"Successfully fetched {len(self.replies)} replies for tweet {tweet_id}")
            else:
                logging.info(f"No replies found for tweet ID: {tweet_id}")

        except requests.RequestException as req_err:
            logging.error(f"API request failed for tweet {tweet_id}: {req_err}", exc_info=True)
            return []

        return self.replies

    def get_replies_with_metadata(self, tweet_id: str, max_replies: int = 100):
        """
        Get replies along with metadata about the fetch operation.
        """
        replies = self.get_tweet_replies(tweet_id, max_replies)
        return {
            "tweet_id": tweet_id,
            "total_replies_fetched": len(replies),
            "fetch_timestamp": datetime.now().isoformat(),
            "replies": replies
        }

    def save_replies_to_file(self, tweet_id: str, filename: str = None, max_replies: int = 100):
        """
        Fetch replies and save them to a JSON file.
        """
        if filename is None:
            filename = f"replies_to_{tweet_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        final_output = self.get_replies_with_metadata(tweet_id, max_replies)
        
        with open(filename, "w") as f:
            json.dump(final_output, f, indent=4)
        
        logging.info(f"Replies saved to file: {filename}")
        return filename


def test_tweet_replies_fetch():
    # Initialize the service
    service = TweetRepliesFetchService()
    
    # Example tweet ID to fetch replies for
    tweet_id = "1902962796993843331"  # Replace with an actual tweet ID
    
    try:
        # Test getting replies
        print("\nTesting get_tweet_replies...")
        replies = service.get_tweet_replies(tweet_id, max_replies=5)
        print(f"Fetched {len(replies)} replies")
        
        # Test getting replies with metadata
        print("\nTesting get_replies_with_metadata...")
        replies_with_metadata = service.get_replies_with_metadata(tweet_id, max_replies=5)
        print(f"Metadata: {json.dumps(replies_with_metadata, indent=2)}")
        
        # Test saving to file
        print("\nTesting save_replies_to_file...")
        output_file = service.save_replies_to_file(tweet_id, max_replies=5)
        print(f"Saved replies to: {output_file}")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")


if __name__ == "__main__":
    test_tweet_replies_fetch()