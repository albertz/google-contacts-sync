#!/usr/bin/python

import gdata.gauth
import gdata.contacts.client

CONSUMER_KEY = 'anonymous'
CONSUMER_SECRET = 'anonymous'
SCOPES = [ "http://www.google.com/m8/feeds/" ] # contacts

client = gdata.contacts.client.ContactsClient(source='Test app')

import goauth
oauthreturnhandler = goauth.OAuthReturnHandler()
request_token = client.GetOAuthToken(
    SCOPES, oauthreturnhandler.oauth_callback_url, CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)

# When using HMAC-SHA1, you need to persist the request_token in some way.
# You'll need the token secret when upgrading to an access token later on.
# In Google App Engine, you can use the AeSave helper:
# gdata.gauth.AeSave(request_token, 'myKey')

loginurl = request_token.generate_authorization_url()
loginurl = str(loginurl)
print "* open oauth login page"
import webbrowser; webbrowser.open(loginurl)

print "* waiting for redirect callback ...",
httpd_access_token_callback = oauthreturnhandler.wait_callback_response()
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
