import socket, ssl, struct, time, base64, re
import gzip
from io import BytesIO
from tp_http_request_response_parser import TP_HTTP_REQUEST_PARSER, TP_HTTP_RESPONSE_PARSER

class TP_HTTP_REQUEST:
	def __init__(self, rawRequest, Coding="utf-8", separator="||", parse_index="$", dupSign_start="{{{", dupSign_end="}}}", ordered_dict=False, skipDuplicated=True, _isDebug_=False):
		self.__version = "2025.8.30"
		self.Coding = Coding
		self.separator = separator
		self.parse_index = parse_index
		self.dupSign_start = dupSign_start
		self.dupSign_end = dupSign_end
		self.ordered_dict = ordered_dict
		self.skipDuplicated = skipDuplicated
		self._isDebug_ = _isDebug_

		self.RequestParser = TP_HTTP_REQUEST_PARSER(rawRequest, separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)

		if self.RequestParser.request_headers.get("User-Agent", case_insensitive=True)["value"] == "JSON_DUPLICATE_KEYS_ERROR":
			self.RequestParser.request_headers.set("User-Agent", "TP-Requests (http/TP_HTTP_REQUEST "+self.__version+")")
		if self.RequestParser.request_headers.get("Connection", case_insensitive=True)["value"] == "JSON_DUPLICATE_KEYS_ERROR":
			self.RequestParser.request_headers.set("Connection", "close")


	def socks4_handshake(self, sock, Host, Port, username=""):
		ip_bytes = socket.inet_aton(socket.gethostbyname(Host))
		port_bytes = struct.pack(">H", Port)
		userid = username.encode() if username else b""
		packet = b"\x04\x01" + port_bytes + ip_bytes + userid + b"\x00"
		sock.sendall(packet)
		resp = sock.recv(8)

		if self._isDebug_: print(resp)

		if resp[1] != 0x5A:
			raise Exception("SOCKS4 connection failed with code: {}".format(resp[1]))


	def socks5_handshake(self, sock, Host, Port, username=None, password=None):
		if username and password:
			# Send: version 5, 1 method (username/password = 0x02)
			sock.sendall(b"\x05\x01\x02")
		else:
			# No auth
			sock.sendall(b"\x05\x01\x00")

		resp = sock.recv(2)

		if self._isDebug_: print(resp)

		if resp[0] != 0x05:
			raise Exception("Invalid SOCKS5 response")

		if resp[1] == 0x02 and username and password:
			# Username/password auth
			u = username.encode()
			p = password.encode()
			sock.sendall(b"\x01" + bytes([len(u)]) + u + bytes([len(p)]) + p)
			auth_resp = sock.recv(2)
			if auth_resp[1] != 0x00:
				raise Exception("SOCKS5 auth failed")
		elif resp[1] != 0x00:
			raise Exception("SOCKS5 method not supported")

		addr = Host.encode()
		req = b"\x05\x01\x00\x03" + bytes([len(addr)]) + addr + struct.pack(">H", Port)
		sock.sendall(req)
		resp = sock.recv(10)
		if resp[1] != 0x00:
			raise Exception("SOCKS5 connect failed: {}".format(resp[1]))


	def sendRequest(self, Host, Port, Scheme, ReqTimeout=60, update_content_length=True, proxy_server=None):
		rawRequest = self.RequestParser.unparse(update_content_length=update_content_length)
		rawResponse = b""
		request_timestamp = response_timestamp = 0

		try:
			# Create a socket connection
			client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client_socket.settimeout(ReqTimeout)

			# Connect to the proxy/ server
			if isinstance(proxy_server, dict):
				client_socket.connect((proxy_server["host"], proxy_server["port"]))
				proxy_type = proxy_server.get("type", "").upper()
				proxy_user = proxy_server.get("username")
				proxy_pass = proxy_server.get("password")

				if proxy_type == "SOCKS4":
					self.socks4_handshake(client_socket, Host, Port, proxy_user)
				elif proxy_type == "SOCKS5":
					self.socks5_handshake(client_socket, Host, Port, proxy_user, proxy_pass)
				elif proxy_type in ["HTTP", "HTTPS"]:
					# Basic CONNECT for HTTP proxy if needed
					connect_req = "CONNECT {Host}:{Port} HTTP/1.1\r\nHost: {Host}:{Port}\r\n".format(Host=Host, Port=Port)
					if proxy_user and proxy_pass:
						auth = base64.b64encode("{proxy_user}:{proxy_pass}".format(proxy_user=proxy_user, proxy_pass=proxy_pass).encode()).decode()
						connect_req += "Proxy-Authorization: Basic {}\r\n".format(auth)
					connect_req += "\r\n"
					client_socket.sendall(connect_req.encode(self.Coding))
					resp = client_socket.recv(4096)

					if self._isDebug_: print(resp)

					if b"200 Connection established" not in resp:
						raise Exception("HTTP CONNECT failed")
				else:
					raise Exception("Unsupported proxy type: {}".format(proxy_type))
			else:
				client_socket.connect((Host, Port))

			# Perform SSL/TLS handshake with the target server
			if Scheme == "https":
				context = ssl.create_default_context()
				context.check_hostname = False
				context.verify_mode = ssl.CERT_NONE
				client_socket = context.wrap_socket(client_socket, server_side=False, server_hostname=Host)

			request_timestamp = int(time.time()*1000)

			# Send the HTTP request
			client_socket.sendall(rawRequest.encode(self.Coding))

			# Receive and process the server's response
			startReceivedResponse = True
			while True:
				chunk = client_socket.recv(4096)
				if startReceivedResponse: response_timestamp = int(time.time()*1000)
				if not chunk:
					break
				rawResponse += chunk
				startReceivedResponse = False

			# Close the connections
			client_socket.close()
		except Exception as e:
			if self._isDebug_: print(e)

		# Handle gzip decomptression response body if needed
		if len(rawResponse) > 0:
			responseBody = re.split(b"\r\n\r\n", rawResponse, 1)[1] if len(re.split(b"\r\n\r\n", rawResponse, 1)) == 2 else ""
			if responseBody:
				if re.search(b"^[a-fA-F0-9]+\r\n", responseBody, re.MULTILINE) and re.search(b"\r\n0\r\n\r\n$", responseBody, re.MULTILINE):
					chunked_body = re.sub(b"\r\n0\r\n\r\n$", b"", re.sub(b"^[a-fA-F0-9]+\r\n", b"", responseBody))
					try:
						with gzip.GzipFile(fileobj=BytesIO(chunked_body)) as f:
							decompressed_responseBody = f.read()
							rawResponse = re.split(b"\r\n\r\n", rawResponse, 1)[0] + b"\r\n\r\n" + decompressed_responseBody
					except Exception as e:
						rawResponse = re.split(b"\r\n\r\n", rawResponse, 1)[0] + b"\r\n\r\n" + chunked_body

		rawResponse = TP_HTTP_RESPONSE_PARSER(rawResponse, separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated).unparse(update_content_length=True) if len(rawResponse) > 0 else ""

		return {
			"Host": Host,
			"Port": Port,
			"Scheme": Scheme,
			"rawRequest": rawRequest,
			"rawResponse": rawResponse,
			"RequestTime": response_timestamp - request_timestamp
		}