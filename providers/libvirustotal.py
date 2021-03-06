"""
VirusTotal API class wrapper
"""
import json
import time
import sys
import logging
try:
    import requests
except ImportError as err:
    print("[!] error, missing %s" % (err))
    sys.exit()


class VTAPI():
    '''
    API wrapper for https://www.virustotal.com API.
    Docs: https://developers.virustotal.com
    '''

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = ("https://www.virustotal.com/vtapi/v2/file/")
        self.params = {'apikey' : self.api_key}
        logging.getLogger().setLevel(logging.INFO)

    def get_api_info(self):
        '''
        Name: get_api_info
        Purpose: get info about API usage from provider
        Parameters: N/A
        '''

        logging.info("[*] VirusTotal does not support a get API info endpoint..")
        return "\t[*] Virustotal does not support an info endpoint at this time."

    def latest_submissions(self):
        '''
        Name: latest_submissions
        Purpose: get latest ioc contents.
        Parameters: N/A
        Return: string.
        '''

        print("\t[*] This is a premium feature, and requires a private API key.")
        self.params['package'] = "11:00"
        try:
            req = requests.get(self.base_url+"feed", params=self.params, stream=True,
                               allow_redirects=True)

        except requests.exceptions.RequestException as err:
            return "[!] Error could not get latest submissions with Virus Total. %s" % (err)

        if req.status_code == 200:
            logging.info("[+] VirusTotal successfully requested latest submissions.")
            fname = time.asctime().replace(' ', '-').replace(':', '-')
            try:
                with open(fname, 'wb') as file_writer:
                    for chunk in req.iter_content(chunk_size=65536):
                        file_writer.write(chunk)
            except IOError as err:
                return "[!] Error wrting file, %s" % str(err)
            return "[+] Wrote daily pull to %s" % (fname)

        elif req.status_code == 429:
            return "[!] Error, too many requests being made against Virus Total API"

        elif req.status_code == 403:
            return "\n\t[!] Error, you do not have appropriate permissions " \
                    "to make this Virus Total API request."

        return "[!] Error, Could not get latest submissions from Virus Total."

    def search(self, ioc_val):
        '''
        Name: search
        Purpose: search for information about a particular ioc
        Parameters: [ioc_val] string value to specify hash to search for.
        return: string
        '''

        try:
            req = requests.get(self.base_url+ "report", params=self.params)
        except requests.exceptions.RequestException as err:
            return "[!] Error could not search for ioc with Virus Total. %s" % (err)

        self.params['resource'] = ioc_val
        self.params['allinfo'] = False  # premium API feature
        req = requests.get(self.base_url+ "report", params=self.params)
        if req.status_code == 200:
            try:
                logging.info("Identified ioc %s", str(ioc_val))
                return "[VirusTotal]\n" + json.dumps(req.json(), indent=4)
            except json.decoder.JSONDecodeError:
                if len(req.text) == 0:
                    return "[!] Error, HTTP request succeeded, but no content" \
                            " is available."
                else:
                    return req.text
        elif req.status_code == 429:
            return "\t[!] Error, too many requests being made against VirusTotal."

        elif req.status_code == 403:
            return "\n\t[!] Error, you do not have appropriate permissions " \
                    "to make this Virus Total API request."
        else:
            return "\t[VirusTotal] ioc not found."

    def download_sample(self, ioc_value, directory):
        '''
        Name: download_sample
        Purpose: Download a ioc from an API provider and writes sample
                 byte stream to a file of the ioc name or user provided name.
        Param:
            [ioc_value] string value indicatin hash (sha{128,256,512}/md5) to
            search for.

            [file_name] string value specifying the file name to download on
            the CLI. Otherwise the file name is the ioc.
        Return:
            [boolean] True if file downloaded successfully.
                      False if error occurs.
        '''
        print("\t[*] This is a premium feature, and requires a private API key.")
        self.params['ioc'] = ioc_value
        try:
            req = requests.get(self.base_url+ "download", params=self.params)
        except requests.exceptions.RequestException as err:
            return "[!] Error could not download sample from Virus Total %s" % (err)

        if req.status_code == 200:
            logging.info("[+] VirusTotal successfully downloaded sample %s.", str(ioc_value))
            try:
                with open(directory + ioc_value, "wb+") as fout:
                    fout.write(req.content)
                return True
            except IOError as err:
                print("\t[!] Error writing to file.\n\tMsg: %s" % (err))
                return False
        elif req.status_code == 403:
            print("\n\t[!] Error, you do not have appropriate permissions " \
                    "to make this Virus Total API request.")
            return False
        else:
            print("\t[!] Failed to identify ioc %s.\n\t[ERROR] %s" \
                    % (ioc_value, req.status_code))
            return False
