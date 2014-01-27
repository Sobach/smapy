KeyChain - is a kind of storage for connectors' tokens. Besides it has some useful methods, like: generating valid token fram raw login data, or checking token's validity. KeyChain class located in the `smapy.network_connectors.addons` section.

> **Important!** 
> All tokens are stored without any encryption. So be careful, using your real and valuable network profiles and/or dumping data to distrusting places. Keep in mind, that you are using this functionality at your won risk.

Read more on how to get tokens for different networks:

* [[Facebook token]]
* [[Twitter token]]
* [[Google token]]
* [[Instagram token]]
* [[VKontakte token]]
* [[Odnoklassniki token]]

### Documentation

_class_ smapy.network_connectors.addons.**KeyChain()**

Public methods:
* **assign**(_net, token_)

    If `net` parameter is registered in network_connectors - assigns `token` value to apropriate net. Usually `net` is a two-letter social media channel identifier. But in some cases it has `raw_` prefix, which means that authorisation is needed to produce appropriate token. Raw prefixes available for Facebook and VKontakte. After assigning `autocomplete()` method is called.

* **check**(_net = None, token = None_)

    This method checks tokens validity through BaseConnector `check_token()` method. If you need to check the exact token from KeyChain - specify it using net parameter with two-letter network id. This method returns True, if token is valid, or False in other cases. If no parameters specified - all tokens are being checked. In this case method returns dict object with all avaliable networks as keys and True/False values. Also it is possible to specify both net and token. Then this exact token would be checked (regardless to KeyChain value for specified network).

* **get**(_net = None_)

    Returns token for network, specified with two-letter ID. If no network parameter specified - all avaliable tokens returned as a dictionary-object.

* **delete**(_net_)

    Removes token for specified network from KeyChain object and returns it.

* **autocomplete**()

    This method is used to update tokens in KeyChain object. Some network keys may be stored in raw form. Method produces valid token from Raw data and assigns it to KeyChain. Use it after loading KeyChain object from dump (some tokens are time limited).

* **show**()

    Prints all your KeyChain object to stdout in a pretty form.

* **dump**(*key_dir = os.path.dirname(\__file\__)*)

    This method stores KeyChain object on hard drive. It uses `pickle` module to create dump and writes it on disk. File name - is a hash-string, obtained from current date and KeyChain tokens. You can specify folder name as `key_dir` parameter. Otherwise KeyChain would be dumped to module's directory.
    
* **available_dumps**(*key_dir = os.path.dirname(\__file\__)*)

    This method checks specified directory and loads all saved KeyChain dumps from it. Method returns dictionary object with three items:
    - `hash` - name of the dump-file without extension;
    - `date` - datetime stamp of the dump (when it was created);
    - `networks` - list of two-letter (and raw_ prefixed) identifiers of avaliable networks in the dump.

    Used to review all available dumps to choose required before loading.

* **load**(*hashstr, key_dir = os.path.dirname(\__file\__)*)

    Method loads dump with provided hash into the KeyChain object. Specify key dumps folder in the parameters. If dump was loaded - return True, otherwise returns False.

* **load_last**(*key_dir = os.path.dirname(\__file\__)*)

    Combined `available_dumps()` and `load()` methods. Scans all available dumps in the folder, and then loads the newest. Returns True, if dump was loaded. Otherwise - False.


### Example

```python
>>> from smapy.network_connectors.addons import KeyChain
>>> token_collection = KeyChain()
>>> token_collection.assign('fb', 'tHiS_iS_mY_sAmPlE_tOkEn')
>>> token_collection.check('fb') # Token from this example neither real, nor valid. So:
False
>>> token_collection.dump() # Saving it on disk
>>> token_collection.assign('fb', 'ChAnGeD_vErSiOn_Of_ToKeN') # Changing Facebook-token value
>>> token_collection.get('fb')
'ChAnGeD_vErSiOn_Of_ToKeN'
>>> token_collection.load_last() # Loading token collection from last dump
True
>>> token_collection.get('fb')
'tHiS_iS_mY_sAmPlE_tOkEn'
>>> token_collection.get('ig') # We have not specified Instagram token yet
None
```