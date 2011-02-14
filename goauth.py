

class OAuthReturnHandler:
	def __init__(oself):
		oself.httpd_access_token_callback = None
		
		import BaseHTTPServer
		import SocketServer

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

		oself.httpd = BaseHTTPServer.HTTPServer(("", 0), Handler)
		_,oself.port = oself.httpd.server_address
		oself.oauth_callback_url = "http://localhost:%d/get_access_token" % oself.port

	def wait_callback_response(self):
		while self.httpd_access_token_callback == None:
			self.httpd.handle_request()
		return self.httpd_access_token_callback
