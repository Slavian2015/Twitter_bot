FROM python:3.8

RUN mkdir -p /usr/local/WB
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y --no-install-recommends

RUN pip install instapy
RUN pip install Flask flask_cors

COPY docker-entrypoint.sh /usr/local/bin/
RUN ln -s /usr/local/bin/docker-entrypoint.sh /entrypoint.sh # backwards compat
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN pip install gunicorn
RUN apt install nano
RUN pip install cython
RUN pip install pandas
RUN pip install requests
RUN pip install requests_oauthlib

ENTRYPOINT ["docker-entrypoint.sh"]