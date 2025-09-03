#!/usr/bin/env python3
import dns.resolver
import os
import requests
import threading
import time

class TempCatcher:
	def _updateLocalData(self, path: str, data: str) -> None:
		with open(path, "w") as fp:
			fp.write(data)

	def _updateResources(self, key: str, value: str) -> None:
		# save data to same directory as this program
		path = self.executionPath + f"/{key}.txt"

		try:
			r = self.session.get(value)
		except:
			if not os.path.exists(path): # this shouldn't happen but if it does its because data files dont exist
				raise FileNotFoundError(f"Request for resource: `{key}` at url: `{value}` failed and could not locate local data")
			else:
				with open(path, "r") as fp:
					data = fp.read().splitlines()
				return data

		if not os.path.exists(path): # first run
			self._updateLocalData(path, r.text)
		else:
			with open(path, "r") as fp:
				if hash(fp.read()) != hash(r.text):
					self._updateLocalData(path, r.text)

		return r.text.splitlines()

	def _thread(self) -> None:
		try:
			while True:
				for key, value in self.resources.items():
					self.resources[key][1] = self._updateResources(key, value[0])

				time.sleep(self.update)
		except KeyboardInterrupt:
			exit()

	def validateEmail(self, email: str) -> str:
		try:
			assert email.count("@") == 1
			username, domain = email.split("@")

			assert domain.count(".") >= 1
			sld, tld = domain.split(".")

			assert tld in self.resources["tlds"][1]
		except:
			return [None, 1]

		username = username.replace(".", "") if "." in username else username
		username = username.split("+")[0] if "+" in username else username

		return [username, domain], 0

	def dnsCheck(self, domain: str) -> bool:
		try:
			if dns.resolver.resolve(domain, "MX"):
				return True
		except:
			pass
		return False

	def check(self, email: str, dns: bool = False) -> bool:
# return `0`	email found in data
# return `1`	email not found in data
# return `2`	invalid email
# return `3`	optional dns check failed
		while len(self.resources["emails"][1]) < 1 or len(self.resources["tlds"][1]) < 1:
			# wait for resources to be created / updated
			...

		formattedEmailParts, status = self.validateEmail(email.strip())

		if status == 1:
			return None, 2

		username, domain = formattedEmailParts

		if dns:
			if not self.dnsCheck(domain):
				return None, 3

		if domain == "gmail.com":
			if (email := (username + "@" + "googlemail.com")) in self.resources["emails"][1]:
				return email, 0

		elif domain == "googlemail.com":
			if (email := (username + "@" + "gmail.com")) in self.resources["emails"][1]:
				return email, 0

		if (email := (username + "@" + domain)) in self.resources["emails"][1]:
			return email, 0
		return email, 1

	def __del__(self):
		if hasattr(self, "thread"):
			self.thread.join()

	def __init__(self,
		session: requests.Session = requests.Session(), # pass headers, cookies and session
		headers: dict = {},
		cookies: dict = {},
		update: int = 3600 # 1 hour
	):
		self.session = session
		self.session.cookies.update(cookies)
		self.session.headers.update(headers)
		self.update = update

		self.executionPath = os.path.join(os.path.dirname(__file__))
		self.resources = {
			"tlds": ["https://tld-list.com/df/tld-list-basic.txt", []],
			"emails": ["https://raw.githubusercontent.com/TempCatcher/tempcatcher/refs/heads/main/emails.txt", []]
		}
		self.thread = threading.Thread(target = self._thread, daemon = True)
		self.thread.start()

if __name__ == "__main__":
	t = TempCatcher()

	email, status = t.check(input("Input email you would like to check: "), dns = False)

	match status:
		case 0:
			print(f"Email: `{email}` was found in the tempcatcher data. (spam)")
		case 1:
			print(f"Email: `{email}` was not found in the tempcatcher data. (not spam)")
		case 2:
			print(f"Email was formatted incorrectly.")
		case 3:
			print(f"Email: `{email}` Could not find DNS MX record assocciated with domain")
		case _:
			print(f"How did we get here?")
	del t # join update thread
