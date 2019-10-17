import os
import json
import argparse
import sys
try:
    import requests
except ImportError as err:
    print("[!] error, missing %s" % (err))
    sys.exit()

class MalshareAPI():
    '''
    API wrapper for https://www.malshare.com API.
    Docs:
    '''

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = ("https://malshare.com/api.php?api_key=%s&action=" % \
                (self.api_key))
        self.hash_search_endpoint = (self.base_url + "details&hash=")
        #self.data_search_endpoint = (self.base_url + "search&query=")
        self.download_endpoint = (self.base_url + "getfile&hash=") 

    def get_api_info(self):
        '''
        Name: get_limit
        Purpose: get limit of API provider
        Parameters: N/A
        '''
        req = requests.get(self.base_url+"getlimit")
        if req.status_code == 200:
            return("\n\t[ Malshare ]\n\t\t[+] Limit: %s \n\t\t[+] Remaining: %s " 
                    %  (req.json().get("LIMIT"), req.json().get("REMAINING")) )
        else:
            return("\n\t[!] Error, Malshare API request for API limits went horribly wrong. %s" % str(req.text))

    def latest_submissions(self):
        '''
        Name: latest_submissions
        Purpose: get latest hash contents.
        Parameters: N/A
        Return: string.
        '''
        req = requests.get(self.base_url+"getlist") # Get the latest submissions
        json_data = {}
        if req.status_code == 200:
            for hashes in req.json():
                    # Get data about the latest submissions
                info_req = requests.get(self.base_url+"details&hash="+ \
                        hashes.get("md5"))
                if info_req.status_code == 200:
                    print(json.dumps(info_req.json(), indent=4))
                    # TODO: for each hash that comes back concat into a large 
                    # list and return all at once.
            return True # Avoid 'None' from being printed.
        elif req.status_code == 429:
            return "\t[!] Error, too many requests being made against Malshare API"
        else:
            return("\n\t[Malsahre] Error, trying to get latest submissions. Something went horribly wrong. %s" % str(req.text))

    def hash_search(self, hash_val):
        '''
        Name: search_hash_sample
        purpose: search for infor about a particular hash
        Parameters: [hash_val] string value to specify hash to search for.
        return: string
        '''
        req = requests.get(self.hash_search_endpoint+hash_val)
        if req.status_code == 200:
            try:
                return("[Malshare]\n" + json.dumps(req.json(),indent=4))
            except json.decoder.JSONDecodeError as err:
                # If something is searched out and doesn't return JSON or 
                # malformed, print the plain text.
                if len(req.text) == 0:
                    return "\t[!] Error, HTTP request succeeded, but no content is available."
                else:
                    return(req.text)
        elif req.status_code == 429:
            return "[!] Error, too many requests being made against Malshare." 
        else:
            return "\t[Malshare] Hash not identified."
    

    def download_sample(self, hash_value, file_name=None):
        '''
        Name: download_sample
        Purpose: Download a hash from an API provider and writes sample 
                 byte stream to a file of the hash name or user provided name.
        Param:
            [hash_value] string value indicatin hash (sha{128,256,512}/md5) to 
            search for.

            [file_name] string value specifying the file name to download on 
            the CLI. Otherwise the file name is the hash.
        Return:
            [boolean] True if file downloaded successfully. 
                      False if error occurs.
        '''
        req = requests.get(self.download_endpoint+hash_value)

        if req.status_code == 200:
            try:
                with open(hash_value, "wb+") as fout:
                    fout.write(req.content)
                return True
            except IOError as err:
                print("\t[!] Error writing to file.")
        else:
            print("\t[!] Error %s, failed to identify hash %s." % 
                    (req.status_code,hash_value ))
            return False