

class OAuthReturnHandler:
	def __init__(oself):
		oself.httpd_access_token_callback = None
		
		import BaseHTTPServer
		class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
			def log_message(self, format, *args): pass
			def do_GET(webself):
				if webself.path.startswith("/get_access_token?"):
					oself.httpd_access_token_callback = webself.path

					webself.send_response(200)
					webself.send_header("Content-type", "text/html")
					webself.end_headers()
					webself.wfile.write("""
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
					webself.send_response(404)
					webself.end_headers()

		oself.handler = Handler		
		def tryOrFail(fn):
			try: fn(); return True
			except: return False
		# Try with some default ports first to avoid cluttering the users Google Authorized Access list.
		tryOrFail(lambda: oself.startserver(port = 8123)) or \
		tryOrFail(lambda: oself.startserver(port = 8321)) or \
		oself.startserver(port = 0)

		_,oself.port = oself.httpd.server_address
		oself.oauth_callback_url = "http://localhost:%d/get_access_token" % oself.port

	def startserver(self, port):
		import BaseHTTPServer
		self.httpd = BaseHTTPServer.HTTPServer(("", port), self.handler)

	def wait_callback_response(self):
		while self.httpd_access_token_callback == None:
			self.httpd.handle_request()
		return self.httpd_access_token_callback


# client must be some gdata.client.GDClient with source set to the application name
def authorize(client):
	import os.path
	cfgfilename = os.path.expanduser("~/." + client.source + ".goauth.cfg")

	import gdata.gauth
	CONSUMER_KEY = 'anonymous'
	CONSUMER_SECRET = 'anonymous'

	# Try to use a previously stored auth token.
	try:
		import ast
		token_str, token_secret = ast.literal_eval(open(cfgfilename).read())
		client.auth_token = gdata.gauth.OAuthHmacToken(
			CONSUMER_KEY, CONSUMER_SECRET, token_str,
			token_secret, gdata.gauth.ACCESS_TOKEN)
		
		# Test if this auth_token is valid. This would throw an exception otherwise.
		client.GetFeed(client.GetFeedUri())

		# everything ok, we can use this token
		return
		
	except:
		pass

	# Get a new access token.
	# Read here for details: http://code.google.com/intl/de/apis/gdata/docs/auth/oauth.html

	# There seem to be no better way to set xoauth_displayname.
	# xoauth_displayname is needed to display the application name.
	# See: http://code.google.com/intl/de/apis/accounts/docs/OAuth.html#tokensIdentifying
	import urllib
	req_token_url = gdata.gauth.REQUEST_TOKEN_URL + '?xoauth_displayname=' + urllib.quote(client.source)
	
	oauthreturnhandler = OAuthReturnHandler()
	request_token = client.GetOAuthToken(
		scopes = client.auth_scopes,
		next = oauthreturnhandler.oauth_callback_url,
		consumer_key = CONSUMER_KEY, consumer_secret = CONSUMER_SECRET,
		url = req_token_url)

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
	
	# Store the access token for later use. Don't care if that fails.
	try: open(cfgfilename, "w").write(repr((access_token.token, access_token.token_secret)))
	except: pass
	
