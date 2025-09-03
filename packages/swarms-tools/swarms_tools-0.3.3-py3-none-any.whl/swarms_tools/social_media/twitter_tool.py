import os
import subprocess
import time
from typing import Any, Callable, Dict, List, Optional

try:
    import tweepy
except ImportError:
    print(
        "Tweepy is not installed. Please install it using 'pip install tweepy'."
    )
    subprocess.run(["pip", "install", "tweepy"])
    raise


class TwitterTool:
    """
    A plugin that interacts with Twitter to perform various actions such as posting, replying, quoting, and liking tweets, as well as fetching metrics.
    """

    def __init__(self, options: Dict[str, Any]) -> None:
        """
        Initializes the TwitterTool with the provided options.

        Args:
            options (Dict[str, Any]): A dictionary containing plugin configuration options.
        """
        self.id: str = options.get("id", "twitter_plugin")
        self.name: str = options.get("name", "Twitter Plugin")
        self.description: str = options.get(
            "description",
            "A plugin that executes tasks within Twitter, capable of posting, replying, quoting, and liking tweets, and getting metrics.",
        )
        # Ensure credentials are provided
        credentials: Optional[Dict[str, str]] = options.get(
            "credentials"
        )
        if not credentials:
            raise ValueError("Twitter API credentials are required.")

        self.twitter_client: tweepy.Client = tweepy.Client(
            consumer_key=credentials.get("apiKey"),
            consumer_secret=credentials.get("apiSecretKey"),
            access_token=credentials.get("accessToken"),
            access_token_secret=credentials.get("accessTokenSecret"),
        )
        # Define internal function mappings
        self._functions: Dict[str, Callable[..., Any]] = {
            "get_metrics": self._get_metrics,
            "reply_tweet": self._reply_tweet,
            "post_tweet": self._post_tweet,
            "like_tweet": self._like_tweet,
            "quote_tweet": self._quote_tweet,
        }

    @property
    def available_functions(self) -> List[str]:
        """
        Get list of available function names.

        Returns:
            List[str]: A list of available function names.
        """
        return list(self._functions.keys())

    def get_function(self, fn_name: str) -> Callable:
        """
        Get a specific function by name.

        Args:
            fn_name (str): Name of the function to retrieve

        Raises:
            ValueError: If function name is not found

        Returns:
            Function object
        """
        if fn_name not in self._functions:
            raise ValueError(
                f"Function '{fn_name}' not found. Available functions: {', '.join(self.available_functions)}"
            )
        return self._functions[fn_name]

    def _get_metrics(self) -> Dict[str, int]:
        """
        Fetches user metrics such as followers, following, and tweets count.

        Returns:
            Dict[str, int]: A dictionary containing user metrics.
        """
        try:
            user = self.twitter_client.get_me(
                user_fields=["public_metrics"]
            )
            if not user or not user.data:
                print("Failed to fetch user metrics.")
                return {}
            public_metrics = user.data.public_metrics
            return {
                "followers": public_metrics.get("followers_count", 0),
                "following": public_metrics.get("following_count", 0),
                "tweets": public_metrics.get("tweet_count", 0),
            }
        except tweepy.TweepyException as e:
            print(f"Failed to fetch metrics: {e}")
            return {}

    def _reply_tweet(self, tweet_id: int, reply: str) -> None:
        """
        Replies to a tweet with the given reply text.

        Args:
            tweet_id (int): The ID of the tweet to reply to.
            reply (str): The text of the reply.
        """
        try:
            self.twitter_client.create_tweet(
                in_reply_to_tweet_id=tweet_id, text=reply
            )
            print(f"Successfully replied to tweet {tweet_id}.")
        except tweepy.TweepyException as e:
            print(f"Failed to reply to tweet {tweet_id}: {e}")

    def _post_tweet(self, tweet: str) -> Dict[str, Any]:
        """
        Posts a new tweet with the given text.

        Args:
            tweet (str): The text of the tweet to post.

        Returns:
            Dict[str, Any]: The response from Twitter.
        """
        try:
            self.twitter_client.create_tweet(text=tweet)
            print("Tweet posted successfully.")
        except tweepy.TweepyException as e:
            print(f"Failed to post tweet: {e}")

    def _like_tweet(self, tweet_id: int) -> None:
        """
        Likes a tweet with the given ID.

        Args:
            tweet_id (int): The ID of the tweet to like.
        """
        try:
            self.twitter_client.like(tweet_id)
            print(f"Tweet {tweet_id} liked successfully.")
        except tweepy.TweepyException as e:
            print(f"Failed to like tweet {tweet_id}: {e}")

    def _quote_tweet(self, tweet_id: int, quote: str) -> None:
        """
        Quotes a tweet with the given ID and adds a quote text.

        Args:
            tweet_id (int): The ID of the tweet to quote.
            quote (str): The text of the quote.
        """
        try:
            self.twitter_client.create_tweet(
                quote_tweet_id=tweet_id, text=quote
            )
            print(f"Successfully quoted tweet {tweet_id}.")
        except tweepy.TweepyException as e:
            print(f"Failed to quote tweet {tweet_id}: {e}")

        # Add to the TwitterPlugin class

    def _fetch_mentions(self) -> List[Dict[str, Any]]:
        try:
            # Fetch the authenticated user's ID
            user = self.twitter_client.get_me()
            user_id = user.data.id

            # Fetch mentions
            response = self.twitter_client.get_users_mentions(
                id=user_id,
                tweet_fields=[
                    "id",
                    "text",
                    "author_id",
                    "created_at",
                ],
            )

            # Log rate limit information
            headers = response.headers
            print(f"Rate Limit: {headers.get('x-rate-limit-limit')}")
            print(
                f"Remaining: {headers.get('x-rate-limit-remaining')}"
            )
            print(f"Reset Time: {headers.get('x-rate-limit-reset')}")

            if response.data:
                print(f"Fetched {len(response.data)} mentions.")
                return response.data
            else:
                print("No new mentions found.")
            return []
        except tweepy.TooManyRequests as e:
            print(
                f"Rate limit exceeded: {e.response.headers.get('x-rate-limit-reset')} seconds until reset."
            )
            time.sleep(
                int(e.response.headers.get("x-rate-limit-reset", 60))
            )
            return []
        except tweepy.TweepyException as e:
            print(f"Error fetching mentions: {e}")
            return []

    def reply_to_mentions_with_agent(self, agent: Any) -> None:
        print("Starting real-time mention monitoring...")
        replied_tweets = set()

        while True:
            try:
                mentions = self._fetch_mentions()
                for mention in mentions:
                    tweet_id = mention["id"]
                    tweet_text = mention["text"]

                    if tweet_id not in replied_tweets:
                        try:
                            response = agent(tweet_text)
                            self._reply_tweet(tweet_id, response)
                            print(
                                f"Replied to tweet {tweet_id}: {response}"
                            )
                            replied_tweets.add(tweet_id)
                        except tweepy.TweepyException as e:
                            print(
                                f"Error replying to tweet {tweet_id}: {e}"
                            )

                # Dynamic backoff based on remaining requests
                headers = self.twitter_client.last_response.headers
                remaining = int(
                    headers.get("x-rate-limit-remaining", 0)
                )
                reset_time = int(
                    headers.get("x-rate-limit-reset", 60)
                )

                if remaining <= 5:  # If close to the limit
                    sleep_time = reset_time - int(time.time()) + 1
                    print(
                        f"Approaching rate limit. Sleeping for {sleep_time} seconds."
                    )
                    time.sleep(max(sleep_time, 1))
                else:
                    time.sleep(60)  # Default sleep time

            except tweepy.TooManyRequests:
                print("Rate limit exceeded. Sleeping...")
                time.sleep(300)  # Fallback sleep for 5 minutes


def initialize_twitter_tool() -> TwitterTool:
    # Define your options with the necessary credentials
    id = os.getenv("TWITTER_ID") or "twitter_plugin"
    name = os.getenv("TWITTER_NAME") or "Twitter Plugin"
    description = (
        os.getenv("TWITTER_DESCRIPTION")
        or "A plugin that executes tasks within Twitter, capable of posting, replying, quoting, and liking tweets, and getting metrics."
    )

    options = {
        "id": id,
        "name": name,
        "description": description,
        "credentials": {
            "apiKey": os.getenv("TWITTER_API_KEY"),
            "apiSecretKey": os.getenv("TWITTER_API_SECRET_KEY"),
            "accessToken": os.getenv("TWITTER_ACCESS_TOKEN"),
            "accessTokenSecret": os.getenv(
                "TWITTER_ACCESS_TOKEN_SECRET"
            ),
        },
    }

    # Initialize the TwitterTool with your options
    twitter_plugin = TwitterTool(options)
    return twitter_plugin


def post_tweet(tweet: str) -> None:
    """
    Posts a tweet with the given text.

    Args:
        tweet (str): The text of the tweet to post.

    Raises:
        tweepy.TweepyException: If there's an error posting the tweet.
    """
    try:
        twitter_plugin = initialize_twitter_tool()
        twitter_plugin.post_tweet(tweet)
        print(f"Tweet posted successfully: {tweet}")
    except tweepy.TweepyException as e:
        print(f"Failed to post tweet: {e}")


def reply_tweet(tweet_id: int, reply: str) -> None:
    """
    Replies to a tweet with the given ID and reply text.

    Args:
        tweet_id (int): The ID of the tweet to reply to.
        reply (str): The text of the reply.

    Raises:
        tweepy.TweepyException: If there's an error replying to the tweet.
    """
    try:
        twitter_plugin = initialize_twitter_tool()
        twitter_plugin.reply_tweet(tweet_id, reply)
        print(f"Successfully replied to tweet {tweet_id}.")
    except tweepy.TweepyException as e:
        print(f"Failed to reply to tweet {tweet_id}: {e}")


def like_tweet(tweet_id: int) -> None:
    """
    Likes a tweet with the given ID.

    Args:
        tweet_id (int): The ID of the tweet to like.

    Raises:
        tweepy.TweepyException: If there's an error liking the tweet.
    """
    try:
        twitter_plugin = initialize_twitter_tool()
        twitter_plugin.like_tweet(tweet_id)
        print(f"Tweet {tweet_id} liked successfully.")
    except tweepy.TweepyException as e:
        print(f"Failed to like tweet {tweet_id}: {e}")


def quote_tweet(tweet_id: int, quote: str) -> None:
    """
    Quotes a tweet with the given ID and adds a quote text.

    Args:
        tweet_id (int): The ID of the tweet to quote.
        quote (str): The text of the quote.

    Raises:
        tweepy.TweepyException: If there's an error quoting the tweet.
    """
    try:
        twitter_plugin = initialize_twitter_tool()
        twitter_plugin.quote_tweet(tweet_id, quote)
        print(f"Successfully quoted tweet {tweet_id}.")
    except tweepy.TweepyException as e:
        print(f"Failed to quote tweet {tweet_id}: {e}")


def get_metrics() -> Dict[str, int]:
    """
    Retrieves metrics from the Twitter plugin.

    Returns:
        Dict[str, int]: A dictionary containing metrics.

    Raises:
        tweepy.TweepyException: If there's an error fetching metrics.
    """
    try:
        twitter_plugin = initialize_twitter_tool()
        metrics = twitter_plugin.get_metrics()
        return metrics
    except tweepy.TweepyException as e:
        print(f"Failed to fetch metrics: {e}")
        return {}


def reply_to_mentions_with_agent(
    agent: Any, interval: int = 10
) -> None:
    """
    Replies to mentions on Twitter using the provided agent and interval.

    Args:
        agent (Any): The agent to use for replying to mentions.
        interval (int, optional): The time interval in seconds between replies. Defaults to 10.

    Raises:
        tweepy.TweepyException: If there's an error replying to mentions.
    """
    try:
        twitter_plugin = initialize_twitter_tool()
        twitter_plugin.reply_to_mentions_with_agent(agent)
    except tweepy.TweepyException as e:
        print(f"Failed to reply to mentions: {e}")
