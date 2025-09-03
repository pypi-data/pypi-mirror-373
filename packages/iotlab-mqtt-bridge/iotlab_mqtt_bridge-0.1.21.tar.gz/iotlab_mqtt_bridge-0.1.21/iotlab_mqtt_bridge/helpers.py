import os, tempfile

def getScriptPath():
    return os.path.dirname(os.path.abspath(__file__))+'/iotlab_mqtt_bridge.py'
    
    
__hidden_file_list__ = []   # keep the files in memory so they are not deleted 
                            # util the end of the program.
    
    
def makeScriptConfig(host, username_bridge=None, password_bridge=None, topic='', port=1883, verbose=0, username_iotlab=None, password_iotlab=None, ca_certs=None):
    """Generate a temporary scriptconfig file which contain the appropriate 
    environment variables. This file is deleted when the program calling this function ends.
    Returns the absolute path of this file."""
    f = tempfile.NamedTemporaryFile(mode='w', 
                                    prefix="iotlab_mqtt_bridge", 
                                    delete=True
                                    )
    f.write("LI_BRIDGE_HOST={}\n".format(host))
    f.write("LI_BRIDGE_PORT={}\n".format(port))
    f.write("LI_BRIDGE_VERBOSE={}\n".format(verbose))
    if username_bridge :
        f.write("LI_BRIDGE_USER={}\n".format(username_bridge))
    if password_bridge :
        f.write("LI_BRIDGE_PWD={}\n".format(password_bridge))
    if username_iotlab :
        f.write("LI_IOTLAB_USER={}\n".format(username_iotlab))
    if password_iotlab :
        f.write("LI_IOTLAB_PWD={}\n".format(password_iotlab))
    if ca_certs :
        f.write("LI_BRIDGE_CA_CERTS={}\n".format(ca_certs))
        
    f.write("LI_BRIDGE_TOPIC={}\n".format(topic))
    f.flush()
    
    __hidden_file_list__.append(f)
        
        
    return f.name
    
    
