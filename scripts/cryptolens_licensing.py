from licensing.models import *
from licensing.methods import Key, Helpers

license_string = ''
license_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'wizardassistant_license.skm')
license_key_is_valid = False
license_key = None
# license_type = 'Lite'

RSAPubKey = "{enter the RSA Public key here. Click here to view it.}"
auth = "{access token with permission to access the activate method. Click here to view it.}"
trial_auth = "{access token with permission to access the activate method. Click here to view it.}"


def save_license_to_file():
    try:  # saving license file to disk
        with open(license_file, 'w') as f:
            f.write(license_key.save_as_string())
            print('License Key saved to file')
    except:
        print('Not able to save license file to disk')
        pass


def load_license_from_file():
    try:
        global trial_license, lite_license, premium_license, professional_license, corporate_license, license_expiration, license_key_is_valid, license_key
        with open(license_file, 'r') as f:
            license_key = LicenseKey.load_from_string(RSAPubKey, f.read(), 30)
            # print((dir(license_key)))
            if license_key is None or not Helpers.IsOnRightMachine(license_key):
                print("NOTE: This license file does not belong to this machine.")
                license_key_is_valid = False
                lite_license = True
                license_expiration = str(license_key.expires)
            else:
                license_key_is_valid = True
                trial_license = str(license_key.f1)
                premium_license = str(license_key.f2)
                professional_license = str(license_key.f3)
                corporate_license = str(license_key.f4)
                license_expiration = str(license_key.expires)
                print('Successfully loaded license file')
                print("Trial (Feature 1): " + str(license_key.f1))
                print("Premium (Feature 2): " + str(license_key.f2))
                print("Professional (Feature 3): " + str(license_key.f3))
                print("Corporate (Feature 4): " + str(license_key.f4))
                print("License expires: " + str(license_key.expires))
                # print(trial_license)

                trial_license = strtobool(trial_license.lower())
                premium_license = strtobool(premium_license.lower())
                professional_license = strtobool(professional_license.lower())
                corporate_license = strtobool(corporate_license.lower())
                # print('trial_license: ' + str(trial_license))
    except:
        pass


def license_trial():
    global trial_license, lite_license, premium_license, professional_license, corporate_license, license_expiration, license_key_is_valid, license_key
    trial_key = Key.create_trial_key(trial_auth, 6527, Helpers.GetMachineCode())

    if trial_key[0] is None:
        print("An error occurred creating a trial key: {0}".format(trial_key[1]))

    result = Key.activate(token=trial_auth,
                          rsa_pub_key=RSAPubKey,
                          product_id=6527, key=trial_key[0],
                          machine_code=Helpers.GetMachineCode())

    if result[0] is None or not Helpers.IsOnRightMachine(result[0]):
        # an error occurred or the key is invalid or it cannot be activated
        # (eg. the limit of activated devices was achieved)
        license_key_is_valid = False
        lite_license = True
        print("An error occurred trying to activate trial license: {0}".format(result[1]))
    else:
        license_key = result[0]
        license_key_is_valid = True
        trial_license = str(license_key.f1)
        premium_license = str(license_key.f2)
        professional_license = str(license_key.f3)
        corporate_license = str(license_key.f4)
        print("Success: Trial key is now activated")
        print("Trial (Feature 1): " + str(license_key.f1))
        print("Premium (Feature 2): " + str(license_key.f2))
        print("Professional (Feature 3): " + str(license_key.f3))
        print("Corporate (Feature 4): " + str(license_key.f4))
        print("License expires: " + str(license_key.expires))
        trial_license = strtobool(trial_license.lower())
        premium_license = strtobool(premium_license.lower())
        professional_license = strtobool(professional_license.lower())
        corporate_license = strtobool(corporate_license.lower())
        # print('trial_license: ' + str(trial_license))

    if result[0] is not None:
        save_license_to_file()


def license_activate():
    global trial_license, lite_license, premium_license, professional_license, corporate_license, license_expiration, license_key_is_valid, license_key
    if license_key_is_valid is False:
        try:
            result = Key.activate(token=auth,
                                  rsa_pub_key=RSAPubKey,
                                  product_id=6527,
                                  key=str(license_string),
                                  machine_code=Helpers.GetMachineCode())

            if result[0] is None or not Helpers.IsOnRightMachine(result[0]):

                # an error occurred or the key is invalid or it cannot be activated
                # (eg. the limit of activated devices was achieved)
                license_key_is_valid = False
                lite_license = True
                print("The license does not work: {0}".format(result[1]))
            else:
                # everything went fine if we are here!
                license_key = result[0]
                license_key_is_valid = True
                trial_license = str(license_key.f1)
                premium_license = str(license_key.f2)
                professional_license = str(license_key.f3)
                corporate_license = str(license_key.f4)
                print("Success")
                print("The license is valid!")
                print("Trial (Feature 1): " + str(license_key.f1))
                print("Premium (Feature 2): " + str(license_key.f2))
                print("Professional (Feature 3): " + str(license_key.f3))
                print("Corporate (Feature 4): " + str(license_key.f4))
                print("License expires: " + str(license_key.expires))
                trial_license = strtobool(trial_license.lower())
                premium_license = strtobool(premium_license.lower())
                professional_license = strtobool(professional_license.lower())
                corporate_license = strtobool(corporate_license.lower())
                # print('trial_license: ' + str(trial_license))

            if result[0] is not None:
                save_license_to_file()
        except:
            pass


# activate if possible license

# try loading license from file
load_license_from_file()

# try activating
license_activate()

# try activating trial
if license_key_is_valid is False:
    license_trial()
