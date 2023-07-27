#!/usr/bin/env python3
from pyln.client import Plugin
import time
import requests
import re


class ExtendedPlugin(Plugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.preimage = None
        self.command = ""


    def _pay402(self, endpoint, proxy, invoice):
        assert endpoint != 'None', "You need to set the endpoint option on startup for this plugin to work"
        try:
            payed = self.rpc.pay(invoice)
            self.preimage = payed['payment_preimage']
            header={'Authorization': f"L402 {self.token}:{payed['payment_preimage']}"}
            response = requests.post(endpoint, proxies=proxy, headers=header, data={'command': self.command})
            return str(response.content, 'UTF-8')
        except Exception as e:
            return f"Error: {e}"

    def pay402(self, endpoint, tor_proxy, pay1shot):
        assert endpoint != 'None', "You need to set the endpoint option on startup for this plugin to work"
        data={'prompt': self.command}
        if tor_proxy:
            proxy={'http': '127.0.0.1:9050', 'https': '127.0.0.1:9050'}
        else:
            proxy=None
        
        if self.token and self.preimage:
            header={'Authorization': f"L402 {self.token}:{self.preimage}"}
        else:
            header=None

        response = requests.post(endpoint, proxies=proxy, headers=header, data=data)
        self.log(f"Got response: {response.text}")

        if response.status_code == 402:
            pattern_token = r"token='(.*?)'"
            self.token = re.findall(pattern_token, response.headers['WWW-Authenticate'])[0]
            pattern_invoice = r"invoice='(.*?)'"
            to_pay = re.findall(pattern_invoice, response.headers['WWW-Authenticate'])[0]
            decoded = self.rpc.decodepay(to_pay)
            if pay1shot:
                return self._payl402(endpoint, proxy, to_pay)
            else:
                return f"{str(response.content, 'UTF-8')}. Please give the command 'lightning-cli pay402 {to_pay}'"
            

        elif response.status_code == 200:
            return str(response.content, 'UTF-8')

        else:
            return f"Status code {response.status_code}"

plugin = ExtendedPlugin()


@plugin.method("aihelpme")
def aihelpme(plugin, command=""):
    """This is the documentation string for the hello-function.

    It gets reported as the description when registering the function
    as a method with `lightningd`.

    """
    tor_proxy = plugin.get_option('torproxy')
    endpoint = plugin.get_option('endpoint')
    pay1shot = plugin.get_option('pay1shot')
    plugin.command = command
    plugin.log(f"performing request with proxy={tor_proxy} on endpoint={endpoint}, pay1shot={pay1shot}")
    return plugin.pay402(endpoint, tor_proxy, pay1shot)

@plugin.method("pay402")
def pay402(plugin, invoice):
    """This is the documentation string for the hello-function.

    It gets reported as the description when registering the function
    as a method with `lightningd`.

    """
    tor_proxy = plugin.get_option('torproxy')
    endpoint = plugin.get_option('endpoint')
    return plugin._pay402(endpoint, tor_proxy, invoice)


@plugin.init()
def init(options, configuration, plugin, **kwargs):
    tor_proxy = plugin.get_option('torproxy')
    endpoint = plugin.get_option('endpoint')
    if endpoint == 'None':
        plugin.log("You need to set the endpoint option on startup for this plugin to work")
    else:
        if tor_proxy:
            proxy={'http': '127.0.0.1:9050', 'https': '127.0.0.1:9050'}
            plugin.log("torproxy not enabled.")
        else:
            proxy=None
        plugin.log(f"performing request with proxy={proxy} on endpoint={endpoint}")
        response = requests.get(endpoint, proxies=proxy)
        if response.status_code == 402:
            return f"Successfully connected to endpoint {endpoint}"

plugin.add_option(name='endpoint', default='None', opt_type='string',
                  description='Default endpoint to forward AI requests with L402 protocol.')
plugin.add_option(name='torproxy', default=False, opt_type='bool',
                  description='Use Tor proxy to connect to endpoint. Default: False')
plugin.add_option(name='pay1shot', default=False, opt_type='bool',
                  description='Pay invoice without confirmation for every request. Default: False')
plugin.run()
