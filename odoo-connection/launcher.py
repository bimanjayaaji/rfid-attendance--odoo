from lib import OdooXMLrpc, Utils

if __name__ == '__main__':
    Utils.getSettingsFromDeviceCustomization()
    Odoo = OdooXMLrpc.OdooXMLrpc()
    serverProxy = Odoo.getServerProxy("/xmlrpc/object")
    res = serverProxy.execute_kw(
                    Utils.settings["odooParameters"]["db"][0],
                    Odoo.uid,
                    Utils.settings["odooParameters"]["user_password"][0],
                    "hr.employee",
                    "attendance_scan",
                    ['041726031032']
                )
    
    print(res['action']['attendance']['display_name'])

    input("\nPress Enter to exit...")