#!/usr/bin/python

# Here for more:
# http://code.google.com/intl/de/apis/contacts/docs/3.0/developers_guide_python.html
# http://gdata-python-client.googlecode.com/svn/trunk/pydocs/gdata.contacts.client.html#ContactsClient

import gdata.contacts.client
client = gdata.contacts.client.ContactsClient(source='Test app')

import goauth
goauth.authorize(client)


def PrintEntry(entry):
	if entry.name and entry.name.full_name:
		print "   name:", entry.name.full_name.text
	elif entry.name: print "   name:", entry.name
	else: print "   no name"
	if entry.content:
		print "   content:", entry.content.text

	# Display the primary email address for the contact.
	for email in entry.email:
		if email.primary and email.primary == 'true':
			print "   primary mail:", email.address
		else:
			print "   mail:", email.address

	# Show the contact groups that this contact is a member of.
	for group in entry.group_membership_info:
		print "   Member of group:", group.href

	# Display extended properties.
	for extended_property in entry.extended_property:
		if extended_property.value:
			value = extended_property.value
		else:
			value = extended_property.GetXmlBlob()
			print "   Extended Property - %s: %s" % (extended_property.name, value)

def all_contacts():
	feed = client.GetContacts()
	while len(feed.entry) > 0:
		for entry in feed.entry: yield entry
		try: feed = client.GetNext(feed)
		except: break

for i, entry in enumerate(all_contacts()):
	print "entry", i, ":", entry.title.text
	PrintEntry(entry)

