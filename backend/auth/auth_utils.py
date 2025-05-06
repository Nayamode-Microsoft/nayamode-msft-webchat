import logging
import json
import base64

def get_authenticated_user_details(request_headers):
    user_object = {}

    logging.debug("Checking for 'X-Ms-Client-Principal-Id' in request headers...")
    
    # Check if running in dev mode or production
    if "X-Ms-Client-Principal-Id" not in request_headers:
        logging.info("'X-Ms-Client-Principal-Id' not found in headers. Assuming development mode.")
        try:
            from . import sample_user
            raw_user_object = sample_user.sample_user
            logging.debug("Loaded sample user for development mode.")
        except Exception as e:
            logging.error(f"Error loading sample user in development mode: {str(e)}")
            return {}
    else:
        logging.info("'X-Ms-Client-Principal-Id' found. Extracting user from headers.")
        raw_user_object = {k: v for k, v in request_headers.items()}
        logging.debug("Raw user object extracted from headers.")

    # Extract basic user details
    user_object['user_principal_id'] = raw_user_object.get('X-Ms-Client-Principal-Id')
    user_object['user_name'] = raw_user_object.get('X-Ms-Client-Principal-Name')
    user_object['auth_provider'] = raw_user_object.get('X-Ms-Client-Principal-Idp')
    user_object['auth_token'] = raw_user_object.get('X-Ms-Token-Aad-Id-Token')
    user_object['client_principal_b64'] = raw_user_object.get('X-Ms-Client-Principal')
    user_object['aad_id_token'] = raw_user_object.get('X-Ms-Token-Aad-Id-Token')

    logging.debug(f"Basic user details extracted: {user_object}")

    # Extract full name from the client principal
    full_name = ""
    try:
        if user_object['client_principal_b64']:
            logging.debug("Decoding base64 client principal.")
            client_principal_json = base64.b64decode(user_object['client_principal_b64']).decode('utf-8')
            client_principal = json.loads(client_principal_json)
            logging.debug("Client principal decoded and parsed.")

            # Look for the claim with "typ": "name"
            if 'claims' in client_principal:
                for claim in client_principal['claims']:
                    if claim.get('typ') == 'name':
                        full_name = claim.get('val', '')
                        logging.debug(f"Full name found in client principal: {full_name}")
                        break

            if not full_name:
                logging.warning("Could not find 'name' claim in client principal.")
        else:
            logging.warning("Client principal base64 string is missing.")
    except Exception as e:
        logging.error(f"Error decoding client principal: {str(e)}")

    user_object['full_name'] = full_name
    logging.info("User authentication details parsed successfully.")

    return user_object
