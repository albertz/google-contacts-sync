#!/usr/bin/python

import gdata.contacts.client

client = gdata.contacts.client.ContactsClient(source='Test app')

import goauth

SCOPES = [ "http://www.google.com/m8/feeds/" ] # contacts
goauth.authorize(SCOPES, client)

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
