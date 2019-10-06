try:
    import os
    import json
    from libs.libmalshare import MalshareAPI
    from libs.libhybridanalysis import HBAPI
except ImportError as err:
    print("[!] Error, could not import %s. Quitting!" % str(err))
    os._exit(1)

class MalQuery():
    '''
    MalQuery is a middle-ware helper class to parse user-args and leverage
    different underlying Malware download site APIs.
    '''

    def __init__(self, provider, action, hashval):
        '''
        '''
        self.provider = provider # CLI Provided API provider
        self.action = action # CLI provided action
        self.hash = hashval # Hash to search
        
        # Malshare groupings
        self.malshare_api_key = self.__get_env_var__("MALSHARE_TOKEN")
        self.has_malshare_api = None
        self.malshare_obj = None

        # Hybrid-Analysis groupings
        self.hba_api_key = self.__get_env_var__("HBA_TOKEN")
        self.has_hba_api = None
        self.hba_obj = None

        # Libquery Meta
        self.__provider_objects__ = [] # List of class objects to iterate 
                                       # through for API operations.

        self.__api_status__() # Check what API tokens are available and update 
                              # objects 

        self.parse_action(self.action) # Parse CLI action and call underlying 
                                       # API objects.

    def __api_status__(self):
        '''
        Name: __api_status__
        Purpose: Check if 
        '''
        if self.provider == "all":
            self.__load_malshare_api__()
            self.__load_hba_api__()

        elif self.provider == "hba":
            self.__load_hba_api__()

        elif self.provider == "malshare":
            self.__load_malshare_api__()

    def __load_malshare_api__(self):
        '''
        Name: __load_malshare_api__
        Purpose: load Malshare API objects
        Return: N/A
        '''
        if self.malshare_api_key is not None:
            self.has_malshare_api = True
            self.malshare_obj = MalshareAPI(self.malshare_api_key)
            self.__provider_objects__.append(self.malshare_obj)
            print("\t[+] Malshare API token identified.")
        else:
            print("\t[!] Malshare API token not found.")

    def __load_hba_api__(self):
        '''
        Name: __load_hba_api__
        Purpose: load Hybrid-Analysis API objects
        Return: N/A
        '''
        if self.hba_api_key is not None:
            self.has_hba_api = True
            self.hba_obj = HBAPI(self.hba_api_key)
            self.__provider_objects__.append(self.hba_obj)
            print("\t[+] Hybrid-Analysis API token identified.")
        else:
            print("\t[!] Malshare API token not found.")

    def __get_env_var__(self, env_name):
        '''
        Name: get_env_var
        purpose: get environment variable for malshare api key.
        return: string value.
        '''
        if os.environ.get(env_name) is None:
            print("[!] %s environment variable was not specified." % str(env_name))
        else:
            return os.environ.get(env_name)

    def parse_action(self, action):
        '''
        Name: parse_action
        Purpose: parse CLI action for downloading/searchhing/list
        Return: integer indicating success or failure.
        '''
        if action == "download":
            for provider in self.__provider_objects__:
                if provider.download_sample(self.hash) == True:
                    self.sample_download(provider, self.hash)
                    print("[+] %s found and downloaded via %s" % (self.hash, provider))
                    break # No need to download same sample from different provider.
                else:
                    print("[!] %s not found at %s" % (self.hash, provider))
            return 0

        elif action == "search":
            print("[================ Search ===================]")
            for provider in self.__provider_objects__:
                print(provider.hash_search(self.hash))
            return 0

        elif action == "info":
            print("[================ API Info ===================]")
            for provider in self.__provider_objects__:
                print(provider.get_api_info())
            return 0

        elif action == "list":
            print("[================ 24hr File List ===================]")
            for provider in self.__provider_objects__:
                provider.latest_submissions()
            return 0
