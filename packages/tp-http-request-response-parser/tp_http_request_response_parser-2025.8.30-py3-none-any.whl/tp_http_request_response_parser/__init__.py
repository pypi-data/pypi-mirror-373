import json_duplicate_keys as jdks
from collections import OrderedDict
import re, platform
import gzip, zlib
from io import BytesIO

try:
	unicode
except NameError:
	unicode = str

if platform.python_version_tuple()[0] == "3":
	from urllib.parse import urlparse, quote as urlencode, unquote as urldecode
else:
	from urlparse import urlparse
	from urllib import quote as urlencode, unquote as urldecode


class TP_HTTP_REQUEST_PARSER:
	def __init__(self, rawRequest, separator="||", parse_index="$", dupSign_start="{{{", dupSign_end="}}}", ordered_dict=False, skipDuplicated=True):
		self.separator = separator
		self.parse_index = parse_index
		self.dupSign_start = dupSign_start
		self.dupSign_end = dupSign_end
		self.ordered_dict = ordered_dict
		self.skipDuplicated = skipDuplicated

		self.urlencode = {
			"HTTPHeaders": {},
			"HTTPCookies": {},
			"RequestBody": {}
		}

		if type(rawRequest) == bytes:
			requestHeader = self.bytes_to_string(re.split(b"\r\n\r\n|\n\n", rawRequest, 1)[0])
			try:
				requestBody = self.bytes_to_string(re.split(b"\r\n\r\n|\n\n", rawRequest, 1)[1])
			except Exception as e:
				requestBody = ""
		elif type(rawRequest) in [unicode, str] :
			requestHeader = re.split("\r\n\r\n|\n\n", rawRequest, 1)[0]
			try:
				requestBody = re.split("\r\n\r\n|\n\n", rawRequest, 1)[1]
			except Exception as e:
				requestBody = ""
		else:
			requestHeader = ""
			requestBody = ""

		## Request Method ##
		try:
			self.request_method = urldecode(re.split("\r\n|\n", requestHeader)[0].split(" ")[0])
		except Exception as e:
			self.request_method = ""
		##

		## Request Path ##
		try:
			self.request_path = urldecode(urlparse(re.split("\r\n|\n", requestHeader)[0].split(" ")[1]).path)
		except Exception as e:
			self.request_path = ""
		##

		## Request Path Param ##
		self.request_pathParams = jdks.loads("{}", ordered_dict=self.ordered_dict)
		if len(self.request_path) > 0:
			for path_split in self.request_path.split("/"):
				if len(path_split) > 0 and re.match("^<(.+?)>$", path_split):
					JDKSObject = jdks.loads(urldecode(path_split[1:-1]), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
					if JDKSObject:
						self.request_pathParams.update(path_split, JDKSObject.getObject(), allow_new_key=True)
					else:
						self.request_pathParams.update(path_split, urldecode(path_split[1:-1]), allow_new_key=True)
		##

		## Request Query ##
		self.request_queryParams = jdks.loads("{}", ordered_dict=self.ordered_dict)
		try:
			parse_query = urlparse(re.split("\r\n|\n", requestHeader)[0].split(" ")[1]).query
			if len(parse_query) > 0:
				for param_query in parse_query.split("&"):
					kv = re.split("=", param_query, 1)
					if len(kv) == 2:
						JDKSObject = jdks.loads(urldecode(kv[1]), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
						if JDKSObject:
							self.request_queryParams.set(urldecode(kv[0]), JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
						else:
							self.request_queryParams.set(urldecode(kv[0]), urldecode(kv[1]), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
					else:
						self.request_queryParams.set(urldecode(kv[0]), "", separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
		except Exception as e:
			pass
		##

		## Request Fragment ##
		try:
			self.request_fragment = urldecode(urlparse(re.split("\r\n|\n", requestHeader)[0].split(" ")[1]).fragment)
		except Exception as e:
			self.request_fragment = ""
		##

		## Request HTTP Version ##
		try:
			self.request_httpVersion = urldecode(re.split("\r\n|\n", requestHeader)[0].split(" ")[2])
		except Exception as e:
			self.request_httpVersion = ""
		##

		## Request Headers ##
		self.request_headers = jdks.loads("{}", ordered_dict=self.ordered_dict)
		try:
			for header in re.split("\r\n|\n", requestHeader)[1:]:
				if re.match("^[^:]+: .*$", header):
					kv = re.findall("^([^:]+): (.*)$", header)[0]
					JDKSObject = jdks.loads(kv[1], dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
					if JDKSObject:
						self.request_headers.set(kv[0], JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
					else:
						JDKSObject = jdks.loads(urldecode(kv[1]), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
						if JDKSObject:
							self.urlencode["HTTPHeaders"][kv[0]] = True
							self.request_headers.set(kv[0], JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
						else:
							self.request_headers.set(kv[0], kv[1], separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
		except Exception as e:
			pass
		##

		## Request Cookies ##
		self.request_cookies = jdks.loads("{}", ordered_dict=self.ordered_dict)
		if self.request_headers.get("Cookie", case_insensitive=True)["value"] != "JSON_DUPLICATE_KEYS_ERROR":
			for cookie in self.request_headers.get("Cookie", case_insensitive=True)["value"].split(";"):
				kv = cookie.split("=", 1)
				if len(kv) == 2:
					JDKSObject = jdks.loads(kv[1].strip(), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
					if JDKSObject:
						self.request_cookies.set(kv[0].strip(), JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
					else:
						JDKSObject = jdks.loads(urldecode(kv[1].strip()), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
						if JDKSObject:
							self.urlencode["HTTPCookies"][kv[0].strip()] = True
							self.request_cookies.set(kv[0].strip(), JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
						else:
							self.request_cookies.set(kv[0].strip(), kv[1].strip(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
				else:
					self.request_cookies.set(kv[0].strip(), "", separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
		##

		## Request Body ##
		try:
			reqBody = requestBody
			if len(reqBody) > 0:
				# JSON Body
				JDKSObject = jdks.loads(reqBody, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
				if JDKSObject:
					self.request_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": "json", "data": JDKSObject.getObject() })
				else:
					JDKSObject = jdks.loads(urldecode(reqBody), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
					if JDKSObject:
						self.urlencode["RequestBody"]["json"] = True
						self.request_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": "json", "data": JDKSObject.getObject() })
					# Multipart Body
					# Line index 0: ------WebKitFormBoundarylSMLylneEk9ZsCHL
					# Line index 1: Content-Disposition: form-data; name="param_name_1"
					# Line index 2: 
					# Line index 3: param_value_1
					# Line index 4: ------WebKitFormBoundarylSMLylneEk9ZsCHL
					# Line index 5: Content-Disposition: form-data; name="param_name_1"; filename="test.txt"
					# Line index 6: Content-Type: text/plain
					# ...
					# Line index -4: 
					# Line index -3: param_value_2
					# Line index -2: ------WebKitFormBoundarylSMLylneEk9ZsCHL--
					# Line index -1: 
					elif re.split("\r\n|\n", reqBody)[-1] == "" and re.split("\r\n|\n", reqBody)[0]+"--"==re.split("\r\n|\n", reqBody)[-2]:
						boundary = re.split("\r\n|\n", reqBody)[0]

						try:
							params = jdks.loads("{}", ordered_dict=self.ordered_dict)

							for multipart_param in re.split("(?:\r?\n)?"+boundary+"(?:--)?\r?\n", reqBody)[1:-1]:
								# name , filename
								if re.match("^Content-Disposition: form-data; name=\".*?\"; filename=\".*?\"$", re.split("\r\n|\n", multipart_param)[0], re.IGNORECASE):
									result = re.findall("^Content-Disposition: form-data; name=\"(.*?)\"; filename=\"(.*?)\"$", re.split("\r\n|\n", multipart_param)[0], re.IGNORECASE)
									name = result[0][0]
									filename = result[0][1]

									params.set(name, {
										"filename": filename,
										"headers": {},
										"value": ""
									}, separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
								# name
								elif re.match("^Content-Disposition: form-data; name=\".*?\"$", re.split("\r\n|\n", multipart_param)[0], re.IGNORECASE):
									result = re.findall("^Content-Disposition: form-data; name=\"(.*?)\"$", re.split("\r\n|\n", multipart_param)[0], re.IGNORECASE)
									name = result[0]

									params.set(name, {
											"headers": {},
											"value": ""
									}, separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
								else:
									continue

								# Headers
								self.urlencode["RequestBody"]["multipart"] = { "headers": {} }
								for h in re.split("\r\n|\n", re.split("\r\n\r\n|\n\n", multipart_param, 1)[0])[1:]:
									if re.match("^[^:]+: .*$", h):
										kv = re.findall("^([^:]+): (.*)$", h)[0]
										JDKSObject = jdks.loads(kv[1], dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
										if JDKSObject:
											params.set(name+self.separator+"headers"+self.separator+kv[0], JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
										else:
											JDKSObject = jdks.loads(urldecode(kv[1]), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
											if JDKSObject:
												self.urlencode["RequestBody"]["multipart"]["headers"][kv[0]] = True
												params.set(name+self.separator+"headers"+self.separator+kv[0], JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
											else:
												params.set(name+self.separator+"headers"+self.separator+kv[0], kv[1], separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)

								# Value
								v = re.split("\r\n\r\n|\n\n", multipart_param, 1)[-1]
								JDKSObject = jdks.loads(v, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
								if JDKSObject:
									params.update(name+self.separator+"value", JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
								else:
									JDKSObject = jdks.loads(urldecode(v), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
									if JDKSObject:
										self.urlencode["RequestBody"]["multipart"]["value"] = True
										params.update(name+self.separator+"value", JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
									else:
										params.update(name+self.separator+"value", v, separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)

							self.request_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": "multipart", "boundary": boundary[2:], "data": params.getObject() })
						except Exception as e:
							self.request_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": "unknown", "data": reqBody })
					elif re.match("^application/x-www-form-urlencoded", self.request_headers.get("Content-Type", case_insensitive=True)["value"]):
						params = jdks.loads("{}", ordered_dict=self.ordered_dict)

						for NameValue in reqBody.split("&"):
							kv = re.split("=", NameValue, 1)
							if len(kv) == 2:
								JDKSObject = jdks.loads(kv[1], dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
								if JDKSObject:
									params.set(kv[0], JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
								else:
									JDKSObject = jdks.loads(urldecode(kv[1]), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
									if JDKSObject:
										self.urlencode["RequestBody"]["form-urlencoded"][kv[0]] = True
										params.set(kv[0], JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
									else:
										params.set(kv[0], kv[1], separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
							else:
								params.set(kv[0], "", separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)

						self.request_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": "form-urlencoded", "data": params.getObject() })
					else:
						self.request_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": "unknown", "data": reqBody })
			else:
				# No body
				self.request_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": None, "data": None })
		except Exception as e:
			# No body, Exception
			self.request_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": None, "data": None })
		##

	def bytes_to_string(self, data):
		# Try plain UTF-8
		try:
			return data.decode("utf-8")
		except UnicodeDecodeError:
			pass

		# Try gzip
		try:
			with gzip.GzipFile(fileobj=BytesIO(data)) as f:
				decompressed = f.read()
				return decompressed.decode("utf-8")
		except Exception:
			pass

		# Try raw deflate (zlib wbits=-15)
		try:
			decompressed = zlib.decompress(data, wbits=-15)
			return decompressed.decode("utf-8")
		except Exception:
			pass

		# Try zlib default (wbits=+zlib format)
		try:
			decompressed = zlib.decompress(data)
			return decompressed.decode("utf-8")
		except Exception:
			pass

		# Try latin1 as a fallback for decoding weird encodings (1:1 byte mapping)
		try:
			return data.decode("latin1")
		except Exception:
			pass

		# Final fallback: replace invalid chars
		return data.decode("utf-8", errors="replace")

	def unparse(self, update_content_length=False):
		method = path = queryParams = fragment = httpVersion = headers = cookies = body = ""

		if type(self.request_method) == str:
			method = urlencode(self.request_method)
		elif type(self.request_method) == unicode:
			method = urlencode(self.request_method.decode("utf-8").encode("utf-8"))
		elif type(self.request_method) == bytes:
			method = urlencode(self.bytes_to_string(self.request_method))
		else:
			method = urlencode(str(self.request_method))

		try:
			if type(self.request_path) in [unicode, str] and (type(self.request_pathParams) == jdks.JSON_DUPLICATE_KEYS or ("__module__" in dir(self.request_pathParams) and self.request_pathParams.__module__ == "json_duplicate_keys")):
				path = self.request_path
				for k in self.request_pathParams.getObject():
					if type(k) in [unicode, str]:
						if type(self.request_pathParams.get(k)["value"]) == str:
							path = path.replace(k, urlencode(self.request_pathParams.get(k)["value"]))
						elif type(self.request_pathParams.get(k)["value"]) == unicode:
							path = path.replace(k, urlencode(self.request_pathParams.get(k)["value"].decode("utf-8").encode("utf-8")))
						elif type(self.request_pathParams.get(k)["value"]) == bytes:
							path = path.replace(k, urlencode(self.bytes_to_string(self.request_pathParams.get(k)["value"])))
						else:
							path = path.replace(k, urlencode(str(self.request_pathParams.get(k)["value"])))
		except Exception as e:
			pass

		try:
			if type(self.request_queryParams) == jdks.JSON_DUPLICATE_KEYS or ("__module__" in dir(self.request_queryParams) and self.request_queryParams.__module__ == "json_duplicate_keys"):
				query = []
				for k in self.request_queryParams.getObject():
					if type(k) in [unicode, str]:
						Jget = self.request_queryParams.get(k)
						if type(Jget["value"]) in [OrderedDict, dict, list]:
							query.append("{key}={value}".format(key=urlencode(jdks.normalize_key(k)), value=urlencode(jdks.JSON_DUPLICATE_KEYS(Jget["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False))))
						elif type(Jget["value"]) == str:
							query.append("{key}={value}".format(key=urlencode(jdks.normalize_key(k)), value=urlencode(Jget["value"])))
						elif type(Jget["value"]) == unicode:
							query.append("{key}={value}".format(key=urlencode(jdks.normalize_key(k)), value=urlencode(Jget["value"].decode("utf-8").encode("utf-8"))))
						elif type(Jget["value"]) == bytes:
							query.append("{key}={value}".format(key=urlencode(jdks.normalize_key(k)), value=urlencode(self.bytes_to_string(Jget["value"]))))
						else:
							query.append("{key}={value}".format(key=urlencode(jdks.normalize_key(k)), value=urlencode(str(Jget["value"]))))
				queryParams = "&".join(query)
		except Exception as e:
			pass
		if len(queryParams) > 0: queryParams = "?"+queryParams

		if len(self.request_fragment) > 0:
			if type(self.request_fragment) == str:
				fragment = "#"+urlencode(self.request_fragment)
			elif type(self.request_fragment) == unicode:
				fragment = "#"+urlencode(self.request_fragment.decode("utf-8").encode("utf-8"))
			elif type(self.request_fragment) == bytes:
				fragment = "#"+urlencode(self.bytes_to_string(self.request_fragment))
			else:
				fragment = "#"+urlencode(str(self.request_fragment))

		if type(self.request_httpVersion) == str:
			httpVersion = urlencode(self.request_httpVersion)
		elif type(self.request_httpVersion) == unicode:
			httpVersion = urlencode(self.request_httpVersion.decode("utf-8").encode("utf-8"))
		elif type(self.request_httpVersion) == bytes:
			httpVersion = urlencode(self.bytes_to_string(self.request_httpVersion))
		else:
			httpVersion = urlencode(str(self.request_httpVersion))

		try:
			if type(self.request_body) == jdks.JSON_DUPLICATE_KEYS or ("__module__" in dir(self.request_body) and self.request_body.__module__ == "json_duplicate_keys"):
				Jget_dataType = self.request_body.get("dataType")
				Jget_data = self.request_body.get("data")
				if Jget_dataType["value"] == "json":
					if "json" in self.urlencode["RequestBody"]:
						body = urlencode(jdks.JSON_DUPLICATE_KEYS(Jget_data["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False))
					else:
						body = jdks.JSON_DUPLICATE_KEYS(Jget_data["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False)
				elif Jget_dataType["value"] == "multipart":
					for paramName in Jget_data["value"]:
						body += "--"+self.request_body.get("boundary")["value"]
						body += '\r\nContent-Disposition: form-data; name="'+paramName+'"'
						if "filename" in Jget_data["value"][paramName].keys():
							body += '; filename="'+Jget_data["value"][paramName]["filename"]+'"'

						for h in Jget_data["value"][paramName]["headers"]:
							if type(h) in [unicode, str]:
								if type(Jget_data["value"][paramName]["headers"][h]) in [OrderedDict, dict, list]:
									if jdks.normalize_key(h) in self.urlencode["RequestBody"]["multipart"]["headers"]:
										body += "\r\n{key}: {value}".format(key=jdks.normalize_key(h), value=urlencode(jdks.JSON_DUPLICATE_KEYS(Jget_data["value"][paramName]["headers"][h]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False)))
									else:
										body += "\r\n{key}: {value}".format(key=jdks.normalize_key(h), value=jdks.JSON_DUPLICATE_KEYS(Jget_data["value"][paramName]["headers"][h]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False))
								elif type(Jget_data["value"][paramName]["headers"][h]) in [unicode, str]:
									body += "\r\n{key}: {value}".format(key=jdks.normalize_key(h), value=Jget_data["value"][paramName]["headers"][h])
								elif type(Jget_data["value"][paramName]["headers"][h]) == bytes:
									body += "\r\n{key}: {value}".format(key=jdks.normalize_key(h), value=self.bytes_to_string(Jget_data["value"][paramName]["headers"][h]))
								else:
									body += "\r\n{key}: {value}".format(key=jdks.normalize_key(h), value=str(Jget_data["value"][paramName]["headers"][h]))

						if type(Jget_data["value"][paramName]["value"]) in [OrderedDict, dict, list]:
							if "value" in self.urlencode["RequestBody"]["multipart"]:
								body += "\r\n\r\n"+urlencode(jdks.JSON_DUPLICATE_KEYS(Jget_data["value"][paramName]["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False))+"\r\n"
							else:
								body += "\r\n\r\n"+jdks.JSON_DUPLICATE_KEYS(Jget_data["value"][paramName]["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False)+"\r\n"
						elif type(Jget_data["value"][paramName]["value"]) in [unicode, str]:
							body += "\r\n\r\n"+Jget_data["value"][paramName]["value"]+"\r\n"
						elif type(Jget_data["value"][paramName]["value"]) == bytes:
							body += "\r\n\r\n"+self.bytes_to_string(Jget_data["value"][paramName]["value"])+"\r\n"
						else:
							body += "\r\n\r\n"+str(Jget_data["value"][paramName]["value"])+"\r\n"

					body += "--"+self.request_body.get("boundary")["value"]+"--\r\n"

					Jget = self.request_headers.get("Content-Type", case_insensitive=True)
					if Jget["value"] == "JSON_DUPLICATE_KEYS_ERROR":
						self.request_headers.set("Content-Type", "multipart/form-data; boundary="+self.request_body.get("boundary")["value"])
					else:
						self.request_headers.update(Jget["name"], "multipart/form-data; boundary="+self.request_body.get("boundary")["value"])
				elif Jget_dataType["value"] == "form-urlencoded":
					body_urlencoded = []
					for k in Jget_data["value"]:
						if type(k) in [unicode, str]:
							if type(Jget_data["value"][k]) in [OrderedDict, dict, list]:
								if jdks.normalize_key(k) in self.urlencode["RequestBody"]["form-urlencoded"]:
									body_urlencoded.append("{key}={value}".format(key=jdks.normalize_key(k), value=urlencode(jdks.JSON_DUPLICATE_KEYS(Jget_data["value"][k]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False))))
								else:
									body_urlencoded.append("{key}={value}".format(key=jdks.normalize_key(k), value=jdks.JSON_DUPLICATE_KEYS(Jget_data["value"][k]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False)))
							elif type(Jget_data["value"][k]) in [unicode, str]:
								body_urlencoded.append("{key}={value}".format(key=jdks.normalize_key(k), value=Jget_data["value"][k]))
							elif type(Jget_data["value"][k]) == bytes:
								body_urlencoded.append("{key}={value}".format(key=jdks.normalize_key(k), value=self.bytes_to_string(Jget_data["value"][k])))
							else:
								body_urlencoded.append("{key}={value}".format(key=jdks.normalize_key(k), value=str(Jget_data["value"][k])))
					body = "&".join(body_urlencoded)
				elif Jget_dataType["value"] == "unknown":
					if type(Jget_data["value"]) == bytes:
						body = self.bytes_to_string(Jget_data["value"])
					else:
						body = str(Jget_data["value"])
		except Exception as e:
			pass

		if update_content_length:
			self.request_headers.update("Content-Length", len(body), allow_new_key=True, case_insensitive=True)

		try:
			if type(self.request_cookies) == jdks.JSON_DUPLICATE_KEYS or ("__module__" in dir(self.request_cookies) and self.request_cookies.__module__ == "json_duplicate_keys"):
				for k in self.request_cookies.getObject():
					if type(k) in [unicode, str]:
						Jget = self.request_cookies.get(k)
						if type(Jget["value"]) in [OrderedDict, dict, list]:
							if jdks.normalize_key(k) in self.urlencode["HTTPCookies"]:
								cookies += "{key}={value}; ".format(key=jdks.normalize_key(k), value=urlencode(jdks.JSON_DUPLICATE_KEYS(Jget["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False)))
							else:
								cookies += "{key}={value}; ".format(key=jdks.normalize_key(k), value=jdks.JSON_DUPLICATE_KEYS(Jget["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False))
						elif type(Jget["value"]) in [unicode, str]:
							cookies += "{key}={value}; ".format(key=jdks.normalize_key(k), value=Jget["value"])
						elif type(Jget["value"]) == bytes:
							cookies += "{key}={value}; ".format(key=jdks.normalize_key(k), value=self.bytes_to_string(Jget["value"]))
						else:
							cookies += "{key}={value}; ".format(key=jdks.normalize_key(k), value=str(Jget["value"]))

				if len(cookies) > 0:
					self.request_headers.update("Cookie", cookies[:-2], allow_new_key=True, case_insensitive=True)
		except Exception as e:
			pass

		try:
			if type(self.request_headers) == jdks.JSON_DUPLICATE_KEYS or ("__module__" in dir(self.request_headers) and self.request_headers.__module__ == "json_duplicate_keys"):
				for k in self.request_headers.getObject():
					if type(k) in [unicode, str]:
						Jget = self.request_headers.get(k)
						if type(Jget["value"]) in [OrderedDict, dict, list]:
							if jdks.normalize_key(k) in self.urlencode["HTTPHeaders"]:
								headers += "\r\n{key}: {value}".format(key=jdks.normalize_key(k), value=urlencode(jdks.JSON_DUPLICATE_KEYS(Jget["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False)))
							else:
								headers += "\r\n{key}: {value}".format(key=jdks.normalize_key(k), value=jdks.JSON_DUPLICATE_KEYS(Jget["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False))
						elif type(Jget["value"]) in [unicode, str]:
							headers += "\r\n{key}: {value}".format(key=jdks.normalize_key(k), value=Jget["value"])
						elif type(Jget["value"]) == bytes:
							headers += "\r\n{key}: {value}".format(key=jdks.normalize_key(k), value=self.bytes_to_string(Jget["value"]))
						else:
							headers += "\r\n{key}: {value}".format(key=jdks.normalize_key(k), value=str(Jget["value"]))
		except Exception as e:
			pass

		return method+" "+path+queryParams+fragment+" "+httpVersion+headers+"\r\n\r\n"+body




class TP_HTTP_RESPONSE_PARSER:
	def __init__(self, rawResponse, separator="||", parse_index="$", dupSign_start="{{{", dupSign_end="}}}", ordered_dict=False, skipDuplicated=True):
		self.separator = separator
		self.parse_index = parse_index
		self.dupSign_start = dupSign_start
		self.dupSign_end = dupSign_end
		self.ordered_dict = ordered_dict
		self.skipDuplicated = skipDuplicated

		self.urlencode = {
			"ResponseHeaders": {},
			"ResponseCookies": {},
			"ResponseBody": {}
		}

		if type(rawResponse) == bytes:
			responseHeader = self.bytes_to_string(re.split(b"\r\n\r\n|\n\n", rawResponse, 1)[0])
			try:
				responseBody = self.bytes_to_string(re.split(b"\r\n\r\n|\n\n", rawResponse, 1)[1])
			except Exception as e:
				responseBody = ""
		elif type(rawResponse) in [unicode, str] :
			responseHeader = re.split("\r\n\r\n|\n\n", rawResponse, 1)[0]
			try:
				responseBody = re.split("\r\n\r\n|\n\n", rawResponse, 1)[1]
			except Exception as e:
				responseBody = ""
		else:
			responseHeader = ""
			responseBody = ""

		## Response HTTP Version ##
		try:
			self.response_httpVersion = re.split("\r\n|\n", responseHeader)[0].split(" ")[0]
		except Exception as e:
			self.response_httpVersion = ""
		##

		## Response Status Code ##
		try:
			self.response_statusCode = int(re.split("\r\n|\n", responseHeader)[0].split(" ")[1])
		except Exception as e:
			self.response_statusCode = ""
		##

		## Response Status Text ##
		try:
			self.response_statusText = " ".join(re.split("\r\n|\n", responseHeader)[0].split(" ")[2:])
		except Exception as e:
			self.response_statusText = ""
		##

		## Response Headers ##
		self.response_headers = jdks.loads("{}", ordered_dict=self.ordered_dict)
		try:
			for header in re.split("\r\n|\n", responseHeader)[1:]:
				if re.match("^[^:]+: .*$", header):
					kv = re.findall("^([^:]+): (.*)$", header)[0]
					JDKSObject = jdks.loads(kv[1], dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
					if JDKSObject:
						self.response_headers.set(kv[0], JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
					else:
						JDKSObject = jdks.loads(urldecode(kv[1]), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
						if JDKSObject:
							self.urlencode["ResponseHeaders"][kv[0]] = True
							self.response_headers.set(kv[0], JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
						else:
							self.response_headers.set(kv[0], kv[1], separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
		except Exception as e:
			pass
		##

		## Response Cookies ##
		self.response_cookies = jdks.loads("{}", ordered_dict=self.ordered_dict)
		for k,v in self.response_headers.filter_keys("Set-Cookie", ordered_dict=True).getObject().items():
			cookie = v.split(";")[0]
			kv = cookie.split("=", 1)
			if len(kv) == 2:
				JDKSObject = jdks.loads(kv[1].strip(), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
				if JDKSObject:
					self.response_cookies.set(kv[0].strip(), JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
				else:
					JDKSObject = jdks.loads(urldecode(kv[1].strip()), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
					if JDKSObject:
						self.urlencode["ResponseCookies"][kv[1].strip()] = True
						self.response_cookies.set(kv[0].strip(), JDKSObject.getObject(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
					else:
						self.response_cookies.set(kv[0].strip(), kv[1].strip(), separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
			else:
				self.response_cookies.set(kv[0].strip(), "", separator=self.separator, parse_index=self.parse_index, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict)
		##

		## Response Body ##
		try:
			resBody = responseBody
			if self.response_headers.get("Content-Length", case_insensitive=True)["value"] == "JSON_DUPLICATE_KEYS_ERROR": self.response_headers.set("Content-Length", len(resBody))

			if len(resBody) > 0:
				# JSON Body
				JDKSObject = jdks.loads(resBody, dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
				if JDKSObject:
					self.response_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": "json", "data": JDKSObject.getObject() })
				else:
					JDKSObject = jdks.loads(urldecode(resBody), dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, ordered_dict=self.ordered_dict, skipDuplicated=self.skipDuplicated)
					if JDKSObject:
						self.urlencode["ResponseBody"]["json"] = True
						self.response_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": "json", "data": JDKSObject.getObject() })
					else:
						self.response_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": "unknown", "data": resBody })
			else:
				# No body
				self.response_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": None, "data": None })
		except Exception as e:
			# No body
			self.response_body = jdks.JSON_DUPLICATE_KEYS({ "dataType": None, "data": None })
		##

	def bytes_to_string(self, data):
		# Try plain UTF-8
		try:
			return data.decode("utf-8")
		except UnicodeDecodeError:
			pass

		# Try gzip
		try:
			with gzip.GzipFile(fileobj=BytesIO(data)) as f:
				decompressed = f.read()
				return decompressed.decode("utf-8")
		except Exception:
			pass

		# Try raw deflate (zlib wbits=-15)
		try:
			decompressed = zlib.decompress(data, wbits=-15)
			return decompressed.decode("utf-8")
		except Exception:
			pass

		# Try zlib default (wbits=+zlib format)
		try:
			decompressed = zlib.decompress(data)
			return decompressed.decode("utf-8")
		except Exception:
			pass

		# Try latin1 as a fallback for decoding weird encodings (1:1 byte mapping)
		try:
			return data.decode("latin1")
		except Exception:
			pass

		# Final fallback: replace invalid chars
		return data.decode("utf-8", errors="replace")

	def unparse(self, update_content_length=False):
		httpVersion = statusCode = statusText = headers = body = ""

		if type(self.response_httpVersion) in [unicode, str]:
			httpVersion = self.response_httpVersion
		elif type(self.response_httpVersion) == bytes:
			httpVersion = self.bytes_to_string(self.response_httpVersion)
		else:
			httpVersion = str(self.response_httpVersion)

		if type(self.response_statusCode) in [unicode, str]:
			statusCode = self.response_statusCode
		elif type(self.response_statusCode) == bytes:
			statusCode = self.bytes_to_string(self.response_statusCode)
		else:
			statusCode = str(self.response_statusCode)

		if type(self.response_statusText) in [unicode, str]:
			statusText = self.response_statusText
		elif type(self.response_statusText) == bytes:
			statusText = self.bytes_to_string(self.response_statusText)
		else:
			statusText = str(self.response_statusText)

		try:
			if type(self.response_body) == jdks.JSON_DUPLICATE_KEYS or ("__module__" in dir(self.response_body) and self.response_body.__module__ == "json_duplicate_keys"):
				if self.response_body.get("dataType")["value"] == "json":
					if "json" in self.urlencode["ResponseBody"]:
						body = urlencode(jdks.JSON_DUPLICATE_KEYS(self.response_body.get("data")["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False))
					else:
						body = jdks.JSON_DUPLICATE_KEYS(self.response_body.get("data")["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False)
				elif self.response_body.get("dataType")["value"] == "unknown":
					body = self.response_body.get("data")["value"]
		except Exception as e:
			pass

		if update_content_length:
			self.response_headers.update("Content-Length", len(body), allow_new_key=True, case_insensitive=True)

		try:
			if type(self.response_headers) == jdks.JSON_DUPLICATE_KEYS or ("__module__" in dir(self.response_headers) and self.response_headers.__module__ == "json_duplicate_keys"):
				for k in self.response_headers.getObject():
					if type(k) in [unicode, str]:
						Jget = self.response_headers.get(k)
						if type(Jget["value"]) in [OrderedDict, dict, list]:
							if jdks.normalize_key(k) in self.urlencode["ResponseHeaders"]:
								headers += "\r\n{key}: {value}".format(key=jdks.normalize_key(k), value=urlencode(jdks.JSON_DUPLICATE_KEYS(Jget["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False)))
							else:
								headers += "\r\n{key}: {value}".format(key=jdks.normalize_key(k), value=jdks.JSON_DUPLICATE_KEYS(Jget["value"]).dumps(dupSign_start=self.dupSign_start, dupSign_end=self.dupSign_end, separators=(",",":"), ensure_ascii=False))
						elif type(Jget["value"]) in [unicode, str]:
							headers += "\r\n{key}: {value}".format(key=jdks.normalize_key(k), value=Jget["value"])
						elif type(Jget["value"]) == bytes:
							headers += "\r\n{key}: {value}".format(key=jdks.normalize_key(k), value=self.bytes_to_string(Jget["value"]))
						else:
							headers += "\r\n{key}: {value}".format(key=jdks.normalize_key(k), value=str(Jget["value"]))
		except Exception as e:
			pass

		return httpVersion+" "+statusCode+" "+statusText+headers+"\r\n\r\n"+body