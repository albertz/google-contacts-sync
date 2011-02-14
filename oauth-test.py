#!/usr/bin/python

import gdata.gauth
import gdata.contacts.client

CONSUMER_KEY = 'anonymous'
CONSUMER_SECRET = 'anonymous'
SCOPES = [ "http://www.google.com/m8/feeds/" ] # contacts

client = gdata.contacts.client.ContactsClient(source='Test app')

import BaseHTTPServer
import SocketServer

httpd_access_token_callback = None
class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.startswith("/get_access_token?"):
			global httpd_access_token_callback
			httpd_access_token_callback = self.path

			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write("""
				<html><head><title>OAuth return</title></head>
				<body onload="onLoad()">
				<script type="text/javascript">
				function onLoad() {
					ww = window.open(window.location, "_self");
					ww.close();
				}
				</script>
				</body></html>""")
		else:
			self.send_response(404)
			self.end_headers()

	def log_message(self, format, *args): pass
httpd = BaseHTTPServer.HTTPServer(("", 0), Handler)
_,port = httpd.server_address

oauth_callback_url = 'http://localhost:%d/get_access_token' % port
request_token = client.GetOAuthToken(
    SCOPES, oauth_callback_url, CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)

# When using HMAC-SHA1, you need to persist the request_token in some way.
# You'll need the token secret when upgrading to an access token later on.
# In Google App Engine, you can use the AeSave helper:
# gdata.gauth.AeSave(request_token, 'myKey')

loginurl = request_token.generate_authorization_url()
loginurl = str(loginurl)
print "* open oauth login page"
import webbrowser; webbrowser.open(loginurl)

print "* waiting for redirect callback ...",
while httpd_access_token_callback == None:
	httpd.handle_request()

print "done"


request_token = gdata.gauth.AuthorizeRequestToken(request_token, httpd_access_token_callback)

# Upgrade the token and save in the user's datastore
access_token = client.GetAccessToken(request_token)
client.auth_token = access_token


def PrintFeed(feed):
  for i, entry in enumerate(feed.entry):
    print "entry", i, ":"
    if entry.name:
	  print entry.name.full_name.text
    if entry.content:
      print '    %s' % (entry.content.text)
    # Display the primary email address for the contact.
    for email in entry.email:
      if email.primary and email.primary == 'true':
        print '    %s' % (email.address)
    # Show the contact groups that this contact is a member of.
    for group in entry.group_membership_info:
      print '    Member of group: %s' % (group.href)
    # Display extended properties.
    for extended_property in entry.extended_property:
      if extended_property.value:
        value = extended_property.value
      else:
        value = extended_property.GetXmlBlob()
      print '    Extended Property - %s: %s' % (extended_property.name, value)
feed = client.GetContacts()
PrintFeed(feed)
