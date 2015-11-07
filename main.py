import os
import logging
import webapp2
from google.appengine.api import memcache, urlfetch

class ApiHandler(webapp2.RequestHandler):
    def get(self):
        url = self.request.get('url')
        if not url:
            self.error(400)
            self.response.out.write('url is required.')
            return

        final_url = url
        try:
            # has cache?
            url_from_cache = memcache.get(url)
            if url_from_cache is not None:
                logging.info("cache hit: " + url)
                final_url = url_from_cache

            else:
                # fetch
                logging.info("fetch: " + url)
                response = urlfetch.fetch(url = url, method = urlfetch.HEAD, follow_redirects = False, deadline = 10)
                if 'location' in response.headers:
                    final_url = response.headers['location'] 
                    memcache.add(url, final_url, time = 86400)
                else:
                    final_url = url

        except urlfetch.Error, error: # urlfetch.Error ???
            logging.warn(error.args)

        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(final_url)

app = webapp2.WSGIApplication([
    ('/api', ApiHandler),
], debug=True)
