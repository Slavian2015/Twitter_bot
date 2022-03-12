from requests_oauthlib import OAuth1Session


def new_tweet(consumer_key=None, consumer_secret=None, access_token=None, access_token_secret=None, new_text=None):
    print("-----  NEW TWEET ---------")
    payload = {"text": new_text}

    if all([consumer_key, consumer_secret, access_token, access_token_secret]):
        try:
            oauth = OAuth1Session(
                consumer_key,
                client_secret=consumer_secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret)
        except:
            pass

        try:
            response = oauth.post(
                "https://api.twitter.com/2/tweets",
                json=payload)
        except:
            pass

    return


