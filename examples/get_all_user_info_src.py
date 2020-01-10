import requests


def get_user_posts(userid):
    response = requests.get("https://jsonplaceholder.typicode.com/posts?userId=" + str(userid))
    return response.json()


def get_post_comments():
    pass


if __name__ == "__main__":
    print(get_user_posts(1))
