import requests
import pyotp
import json
from pprint import pprint
from typing import Optional, Dict, Any, List
from io import BytesIO


def parse_response(response: requests.Response):
    print(f"Status Code: {response.status_code}")
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        print("Response JSON:")
        try:
            pprint(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Error decoding JSON. Raw content:")
            print(response.text)
    elif "text/" in content_type:
        print("Response Text:")
        print(
            response.text[:1000] + "..." if len(response.text) > 1000 else response.text
        )
    else:
        print(f"Response Content-Type: {content_type}")
        print(f"Content-Length: {response.headers.get('Content-Length')}")
        print("Binary content (not displayed)")
    if response.status_code == 500:
        print("Error:")
        print(response.text)
        raise Exception(f"Internal Server Error: {response.text}")


class XTSystemsSDK:
    def __init__(
        self,
        base_url: str = "http://localhost:20437",
        agixt_server: str = "http://localhost:7437",
        verbose: bool = True,
    ):
        self.base_url = base_url
        self.agixt_server = agixt_server
        self.headers = {}
        self.verbose = verbose

    def handle_error(self, error) -> str:
        print(f"Error: {error}")
        raise Exception(f"Unable to retrieve data. {error}")

    def login(self, email, otp):
        response = requests.post(
            f"{self.agixt_server}/v1/login",
            json={"email": email, "token": otp},
        )
        if self.verbose:
            parse_response(response)
        response = response.json()
        if "detail" in response:
            detail = response["detail"]
            if "?token=" in detail:
                token = detail.split("token=")[1]
                self.headers = {"Authorization": token}
                print(f"Log in at {detail}")
                return token

    def register_user(self, email, first_name, last_name):
        login_response = requests.post(
            f"{self.agixt_server}/v1/user",
            json={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        if self.verbose:
            parse_response(login_response)
        response = login_response.json()
        if "otp_uri" in response:
            mfa_token = str(response["otp_uri"]).split("secret=")[1].split("&")[0]
            totp = pyotp.TOTP(mfa_token)
            self.login(email=email, otp=totp.now())
            return response["otp_uri"]
        else:
            return response

    def user_exists(self, email):
        response = requests.get(f"{self.agixt_server}/v1/user/exists?email={email}")
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_user(self, **kwargs):
        response = requests.put(
            f"{self.agixt_server}/v1/user",
            headers=self.headers,
            json={**kwargs},
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_user(self):
        response = requests.get(f"{self.agixt_server}/v1/user", headers=self.headers)
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_companies(self):
        response = requests.get(
            f"{self.agixt_server}/v1/companies", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def create_company(self, name: str, parent_company_id: Optional[str] = None):
        params = {"name": name}
        if parent_company_id:
            params["parent_company_id"] = parent_company_id
        response = requests.post(
            f"{self.agixt_server}/v1/companies",
            headers=self.headers,
            params=params,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_company(
        self, 
        company_id: str, 
        name: str = None,
        email: str = None,
        website: str = None, 
        city: str = None,
        state: str = None,
        zip_code: str = None,
        country: str = None,
        notes: str = None,
        address: str = None,
        phone_number: str = None,
    ):
        # Build params dict with only non-None values
        params = {}
        if name is not None:
            params["name"] = name
        if email is not None:
            params["email"] = email
        if website is not None:
            params["website"] = website
        if city is not None:
            params["city"] = city
        if state is not None:
            params["state"] = state
        if zip_code is not None:
            params["zip_code"] = zip_code
        if country is not None:
            params["country"] = country
        if notes is not None:
            params["notes"] = notes
        if address is not None:
            params["address"] = address
        if phone_number is not None:
            params["phone_number"] = phone_number
            
        response = requests.put(
            f"{self.agixt_server}/v1/companies/{company_id}",
            headers=self.headers,
            params=params,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_secrets(self):
        response = requests.get(f"{self.base_url}/v1/secrets", headers=self.headers)
        if self.verbose:
            parse_response(response)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    def get_secret(self, secret_id):
        response = requests.get(
            f"{self.base_url}/v1/secret/{secret_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_expired_secrets(self):
        response = requests.get(
            f"{self.base_url}/v1/secrets/expired", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_expiring_soon_secrets(self, days=30):
        response = requests.get(
            f"{self.base_url}/v1/secrets/expiring-soon",
            params={"days": days},
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def create_secret(self, name, description, items, expires_at=None, company_id=None):
        data = {
            "name": name,
            "description": description,
            "items": items,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "company_id": company_id,
        }
        response = requests.post(
            f"{self.base_url}/v1/secrets",
            headers=self.headers,
            json=data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_secret(self, secret_id, name, description, items, expires_at=None):
        data = {
            "name": name,
            "description": description,
            "items": items,
            "expires_at": expires_at.isoformat() if expires_at else None,
        }
        response = requests.put(
            f"{self.base_url}/v1/secret/{secret_id}",
            headers=self.headers,
            json=data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_secret(self, secret_id):
        response = requests.delete(
            f"{self.base_url}/v1/secret/{secret_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def create_invitation(self, email: str, company_id: str, role_id: int):
        response = requests.post(
            f"{self.agixt_server}/v1/invitations",
            headers=self.headers,
            json={"email": email, "company_id": company_id, "role_id": role_id},
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def accept_invitation(self, invitation_id: str):
        response = requests.post(
            f"{self.agixt_server}/v1/invitations/{invitation_id}/accept",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def verify_stripe_session(self, session_id):
        response = requests.post(
            f"{self.agixt_server}/v1/verify-stripe-session",
            headers=self.headers,
            params={"session_id": session_id},
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def create_checkout_session(self):
        response = requests.post(
            f"{self.agixt_server}/v1/create-checkout-session", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def create_portal_session(self):
        response = requests.post(
            f"{self.agixt_server}/v1/create-portal-session", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def create_asset_template(self, name, description, fields, company_id):
        response = requests.post(
            f"{self.base_url}/v1/asset-templates",
            headers=self.headers,
            json={
                "name": name,
                "description": description,
                "fields": fields,
                "company_id": company_id,
            },
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_asset_templates(self):
        response = requests.get(
            f"{self.base_url}/v1/asset-templates",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_asset_template(self, template_id):
        response = requests.get(
            f"{self.base_url}/v1/asset-templates/{template_id}",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_asset_template(
        self, template_id, name=None, description=None, fields=None
    ):
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if fields is not None:
            data["fields"] = fields

        response = requests.put(
            f"{self.base_url}/v1/asset-templates/{template_id}",
            headers=self.headers,
            json=data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_asset_template(self, template_id):
        response = requests.delete(
            f"{self.base_url}/v1/asset-templates/{template_id}",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    # Asset owner assignment method
    def assign_asset_owner(self, asset_id: str, contact_id: str) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}/v1/assets/{asset_id}/owner/{contact_id}",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def create_asset(
        self,
        name,
        description,
        company_id,
        items=None,
        secret_ids=None,
        files=None,
        template_id=None,
        template_data=None,
        owner_id=None,
    ):
        asset_data = {
            "name": name,
            "description": description,
            "company_id": company_id,
            "items": items if items is not None else [],
            "secret_ids": secret_ids or [],
            "template_id": template_id,
            "template_data": template_data,
            "owner_id": owner_id,
        }

        files_data = []
        if files:
            for i, file in enumerate(files):
                if isinstance(file, bytes):
                    files_data.append(
                        (
                            "files",
                            (f"file_{i}", BytesIO(file), "application/octet-stream"),
                        )
                    )
                elif isinstance(file, BytesIO):
                    files_data.append(
                        ("files", (f"file_{i}", file, "application/octet-stream"))
                    )
                else:
                    raise ValueError(f"Unsupported file type for file {i}")

        response = requests.post(
            f"{self.base_url}/v1/assets",
            headers=self.headers,
            data={"asset": json.dumps(asset_data)},
            files=files_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_assets(self):
        response = requests.get(f"{self.base_url}/v1/assets", headers=self.headers)
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_asset(self, asset_id):
        response = requests.get(
            f"{self.base_url}/v1/assets/{asset_id}",
            headers=self.headers,
        )
        if response.status_code == 404:
            if self.verbose:
                print(f"Asset with id {asset_id} not found.")
            return None
        if self.verbose:
            parse_response(response)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}")
        return response.json()

    def update_asset(
        self,
        asset_id,
        name=None,
        description=None,
        items=None,
        secret_ids=None,
        template_data=None,
        files=None,
        owner_id=None,
    ):
        # Prepare the asset data
        asset_data = {
            "name": name,
            "description": description,
            "items": items,
            "secret_ids": secret_ids,
            "template_data": template_data,
            "owner_id": owner_id,
        }
        # Remove None values
        asset_data = {k: v for k, v in asset_data.items() if v is not None}

        # Convert asset_data to JSON string
        asset_json = json.dumps(asset_data)

        files_data = []
        if files:
            for i, file in enumerate(files):
                if isinstance(file, bytes):
                    files_data.append(
                        (
                            "files",
                            (f"file_{i}", BytesIO(file), "application/octet-stream"),
                        )
                    )
                elif isinstance(file, BytesIO):
                    files_data.append(
                        ("files", (f"file_{i}", file, "application/octet-stream"))
                    )
                elif hasattr(file, "read"):  # File-like object
                    files_data.append(
                        (
                            "files",
                            (
                                getattr(file, "name", f"file_{i}"),
                                file,
                                getattr(
                                    file, "content_type", "application/octet-stream"
                                ),
                            ),
                        )
                    )
                else:
                    raise ValueError(
                        f"Unsupported file type for file {i}: {type(file)}"
                    )

        data = {"asset": asset_json}

        response = requests.put(
            f"{self.base_url}/v1/assets/{asset_id}",
            headers=self.headers,
            data=data,
            files=files_data,
        )
        if self.verbose:
            parse_response(response)
        if response.status_code != 200:
            raise Exception(f"Error updating asset: {response.text}")
        return response.json()

    def delete_asset(self, asset_id):
        response = requests.delete(
            f"{self.base_url}/v1/assets/{asset_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_asset_file(self, asset_id, file_id):
        if isinstance(file_id, dict):
            file_id = file_id["id"]
        response = requests.get(
            f"{self.base_url}/v1/assets/{asset_id}/files/{file_id}",
            headers=self.headers,
        )
        if self.verbose:
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            print(f"Content-Length: {response.headers.get('Content-Length')}")
        if response.status_code == 200:
            return response.content
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    def rotate_company_key(self, company_id: str):
        response = requests.post(
            f"{self.base_url}/v1/companies/{company_id}/rotate-key",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_user(self):
        response = requests.delete(f"{self.agixt_server}/v1/user", headers=self.headers)
        if self.verbose:
            parse_response(response)
        return response.json()

    # Ticket methods
    # Status Management
    def create_ticket_status(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/v1/ticket-statuses",
            headers=self.headers,
            json=status_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_ticket_statuses(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/v1/ticket-statuses",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_ticket_status(
        self, status_id: str, status_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}/v1/ticket-statuses/{status_id}",
            headers=self.headers,
            json=status_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_ticket_status(self, status_id: str) -> bool:
        response = requests.delete(
            f"{self.base_url}/v1/ticket-statuses/{status_id}",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    # Priority Management
    def create_ticket_priority(self, priority_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/v1/ticket-priorities",
            headers=self.headers,
            json=priority_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_ticket_priorities(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/v1/ticket-priorities",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_ticket_priority(
        self, priority_id: str, priority_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}/v1/ticket-priorities/{priority_id}",
            headers=self.headers,
            json=priority_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_ticket_priority(self, priority_id: str) -> bool:
        response = requests.delete(
            f"{self.base_url}/v1/ticket-priorities/{priority_id}",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure status_id and priority_id are provided instead of strings
        if "status" in ticket_data:
            del ticket_data["status"]
        if "priority" in ticket_data:
            del ticket_data["priority"]

        response = requests.post(
            f"{self.base_url}/v1/tickets",
            headers=self.headers,
            json=ticket_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/v1/tickets/{ticket_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_all_tickets(self) -> List[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/v1/tickets", headers=self.headers)
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_ticket(
        self, ticket_id: str, ticket_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Ensure status_id and priority_id are provided instead of strings
        if "status" in ticket_data:
            del ticket_data["status"]
        if "priority" in ticket_data:
            del ticket_data["priority"]

        response = requests.put(
            f"{self.base_url}/v1/tickets/{ticket_id}",
            headers=self.headers,
            json=ticket_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_ticket(self, ticket_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.base_url}/v1/tickets/{ticket_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    # Ticket Type methods
    def create_ticket_type(self, ticket_type_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/v1/ticket-types",
            headers=self.headers,
            json=ticket_type_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_ticket_type(self, ticket_type_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/v1/ticket-types/{ticket_type_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_all_ticket_types(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/v1/ticket-types", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_ticket_type(
        self, ticket_type_id: str, ticket_type_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}/v1/ticket-types/{ticket_type_id}",
            headers=self.headers,
            json=ticket_type_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_ticket_type(self, ticket_type_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.base_url}/v1/ticket-types/{ticket_type_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    # Ticket Template methods
    def create_ticket_template(
        self, ticket_template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/v1/ticket-templates",
            headers=self.headers,
            json=ticket_template_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_ticket_template(self, ticket_template_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/v1/ticket-templates/{ticket_template_id}",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_all_ticket_templates(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/v1/ticket-templates", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_ticket_template(
        self, ticket_template_id: str, ticket_template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}/v1/ticket-templates/{ticket_template_id}",
            headers=self.headers,
            json=ticket_template_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_ticket_template(self, ticket_template_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.base_url}/v1/ticket-templates/{ticket_template_id}",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    # Ticket Note methods
    def create_ticket_note(
        self, ticket_id: str, note_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/v1/tickets/{ticket_id}/notes",
            headers=self.headers,
            json=note_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_ticket_notes(self, ticket_id: str) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/v1/tickets/{ticket_id}/notes", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_ticket_note(
        self, ticket_id: str, note_id: str, note_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}/v1/tickets/{ticket_id}/notes/{note_id}",
            headers=self.headers,
            json=note_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_ticket_note(self, ticket_id: str, note_id: str) -> Dict[str, Any]:
        response = requests.delete(
            f"{self.base_url}/v1/tickets/{ticket_id}/notes/{note_id}",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/v1/contacts", headers=self.headers, json=contact_data
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/v1/contacts/{contact_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_all_contacts(self) -> List[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/v1/contacts", headers=self.headers)
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_contact(
        self, contact_id: str, contact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}/v1/contacts/{contact_id}",
            headers=self.headers,
            json=contact_data,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_contact(self, contact_id: str) -> bool:
        response = requests.delete(
            f"{self.base_url}/v1/contacts/{contact_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def register_machine(self, company_id: str, hostname: str, device_data: dict = {}, ip_address: str = "0.0.0.0"):
        response = requests.post(
            f"{self.base_url}/v1/machine/register",
            headers=self.headers,
            json={
                "company_id": company_id,
                "hostname": hostname,
                "device_data": device_data,
                "ip_address": ip_address,
            },
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def approve_machine(self, asset_id: str, company_id: str):
        response = requests.post(
            f"{self.base_url}/v1/machine/approve",
            headers=self.headers,
            json={"asset_id": asset_id, "company_id": company_id},
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def deny_machine(self, asset_id: str, company_id: str):
        response = requests.post(
            f"{self.base_url}/v1/machine/deny",
            headers=self.headers,
            json={"asset_id": asset_id, "company_id": company_id},
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def machine_login(self, asset_id: str, mfa_token: str):
        response = requests.post(
            f"{self.base_url}/v1/machine/login",
            json={"asset_id": asset_id, "mfa_token": pyotp.TOTP(mfa_token).now()},
        )
        self.headers = {"Authorization": response.json()["token"]}
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_machine_status(self):
        response = requests.get(
            f"{self.base_url}/v1/machine/status",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def sync_device_data(self, device_data: Dict[str, Any]):
        response = requests.post(
            f"{self.base_url}/v1/machine",
            headers=self.headers,
            json={"device_data": device_data},
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_machines_by_status(self, company_id: str, status: str = None):
        url = f"{self.base_url}/v1/companies/{company_id}/machines"
        if status:
            url += f"?status={status}"
        response = requests.get(url, headers=self.headers)
        if self.verbose:
            parse_response(response)
        return response.json()

    def add_approved_ip_range(self, company_id: str, start_ip: str, end_ip: str):
        response = requests.post(
            f"{self.base_url}/v1/companies/{company_id}/approved-ip-ranges",
            headers=self.headers,
            json={
                "start_ip": start_ip,
                "end_ip": end_ip,
            },
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_approved_ip_ranges(self, company_id: str):
        response = requests.get(
            f"{self.base_url}/v1/companies/{company_id}/approved-ip-ranges",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_integrations(self, active: bool = False) -> List[Dict[str, Any]]:
        """
        Get all integrations or only active ones.
        """
        params = {"active": str(active).lower()}
        response = requests.get(
            f"{self.base_url}/v1/integrations", headers=self.headers, params=params
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def create_integration(
        self, name: str, company_id: str, secret_id: str
    ) -> Dict[str, Any]:
        """
        Create a new integration.
        """
        data = {
            "name": name,
            "company_id": company_id,
            "secret_id": secret_id,
            "status": "Active",
        }
        response = requests.post(
            f"{self.base_url}/v1/integrations", headers=self.headers, json=data
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_integration(self, integration_id: str) -> Dict[str, Any]:
        """
        Get details of a specific integration.
        """
        response = requests.get(
            f"{self.base_url}/v1/integrations/{integration_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def update_integration(self, integration_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing integration.
        """
        response = requests.put(
            f"{self.base_url}/v1/integrations/{integration_id}",
            headers=self.headers,
            json=kwargs,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def delete_integration(self, integration_id: str) -> bool:
        """
        Delete an integration.
        """
        response = requests.delete(
            f"{self.base_url}/v1/integrations/{integration_id}", headers=self.headers
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def sync_integration(self, integration_id: str) -> Dict[str, Any]:
        """
        Trigger a sync for a specific integration.
        """
        response = requests.post(
            f"{self.base_url}/v1/integrations/{integration_id}/sync",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_integration_auth_data(self, integration_id: str) -> Dict[str, str]:
        """
        Get authentication data for a specific integration.
        """
        response = requests.get(
            f"{self.base_url}/v1/integrations/{integration_id}/auth",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_integration_companies(self, integration_id: str) -> List[Dict[str, Any]]:
        """
        Get companies for a specific integration.
        """
        response = requests.get(
            f"{self.base_url}/v1/integrations/{integration_id}/companies",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_integration_devices(self, integration_id: str) -> List[Dict[str, Any]]:
        """
        Get devices for a specific integration.
        """
        response = requests.get(
            f"{self.base_url}/v1/integrations/{integration_id}/devices",
            headers=self.headers,
        )
        if self.verbose:
            parse_response(response)
        return response.json()

    def get_conversations(self, **kwargs) -> List[str]:
        url = f"{self.agixt_server}/api/conversations"
        try:
            response = requests.get(
                headers=self.headers,
                url=url,
            )
            if self.verbose:
                parse_response(response)
            return response.json()["conversations"]
        except Exception as e:
            return self.handle_error(e)

    def get_conversation(
        self, conversation_name: str, limit: int = 100, page: int = 1, **kwargs
    ) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                headers=self.headers,
                url=f"{self.agixt_server}/api/conversation",
                json={
                    "conversation_name": conversation_name,
                    "limit": limit,
                    "page": page,
                },
            )
            if self.verbose:
                parse_response(response)
            return response.json()["conversation_history"]
        except Exception as e:
            return self.handle_error(e)

    def learn_file(
        self,
        agent_name: str,
        file_name: str,
        file_content: str,
        collection_number: str = "0",
        company_id=None,
        user=True,
    ) -> str:
        try:
            if not company_id:
                response = requests.post(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/learn/file",
                    json={
                        "file_name": file_name,
                        "file_content": file_content,
                        "collection_number": collection_number,
                        "user": user,
                    },
                )
            else:
                response = requests.post(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/learn/file",
                    json={
                        "file_name": file_name,
                        "file_content": file_content,
                        "collection_number": collection_number,
                        "company_id": company_id,
                        "user": user,
                    },
                )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    # Add this endpoint to boilerplate and add a test
    def learn_url(
        self,
        agent_name: str,
        url: str,
        collection_number: str = "0",
        company_id=None,
    ) -> str:
        try:
            if not company_id:
                response = requests.post(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/learn/url",
                    json={
                        "url": url,
                        "collection_number": collection_number,
                    },
                )
            else:
                response = requests.post(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/learn/url",
                    json={
                        "url": url,
                        "collection_number": collection_number,
                        "company_id": company_id,
                    },
                )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    def positive_feedback(
        self,
        agent_name,
        message: str,
        user_input: str,
        feedback: str,
        conversation_name: str = "",
    ) -> str:
        try:
            response = requests.post(
                headers=self.headers,
                url=f"{self.agixt_server}/api/agent/{agent_name}/feedback",
                json={
                    "user_input": user_input,
                    "message": message,
                    "feedback": feedback,
                    "positive": True,
                    "conversation_name": conversation_name,
                },
            )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    def negative_feedback(
        self,
        agent_name,
        message: str,
        user_input: str,
        feedback: str,
        conversation_name: str = "",
    ) -> str:
        try:
            response = requests.post(
                headers=self.headers,
                url=f"{self.agixt_server}/api/agent/{agent_name}/feedback",
                json={
                    "user_input": user_input,
                    "message": message,
                    "feedback": feedback,
                    "positive": False,
                    "conversation_name": conversation_name,
                },
            )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    # Add this endpoint to boilerplate and add a test
    def fork_conversation(
        self,
        conversation_name: str,
        message_id: str,
    ):
        try:
            response = requests.post(
                headers=self.headers,
                url=f"{self.agixt_server}/api/conversation/fork",
                json={"conversation_name": conversation_name, "message_id": message_id},
            )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    # Add this endpoint to boilerplate and add a test
    def new_conversation(
        self,
        agent_name: str,
        conversation_name: str,
        conversation_content: List[Dict[str, Any]] = [],
    ) -> List[Dict[str, Any]]:
        try:
            response = requests.post(
                headers=self.headers,
                url=f"{self.agixt_server}/api/conversation",
                json={
                    "conversation_name": conversation_name,
                    "agent_name": agent_name,
                    "conversation_content": conversation_content,
                },
            )
            if self.verbose:
                parse_response(response)
            return response.json()["conversation_history"]
        except Exception as e:
            return self.handle_error(e)

    # Add this endpoint to boilerplate and add a test
    def rename_conversation(
        self,
        agent_name: str,
        conversation_name: str,
        new_name: str = "-",
    ):
        try:
            response = requests.put(
                headers=self.headers,
                url=f"{self.agixt_server}/api/conversation",
                json={
                    "conversation_name": conversation_name,
                    "new_conversation_name": new_name,
                    "agent_name": agent_name,
                },
            )
            if self.verbose:
                parse_response(response)
            return response.json()["conversation_name"]
        except Exception as e:
            return self.handle_error(e)

    # Add this endpoint to boilerplate and add a test
    def delete_conversation(self, agent_name: str, conversation_name: str) -> str:
        try:
            response = requests.delete(
                headers=self.headers,
                url=f"{self.agixt_server}/api/conversation",
                json={
                    "conversation_name": conversation_name,
                    "agent_name": agent_name,
                },
            )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    # Add this endpoint to boilerplate and add a test
    def delete_conversation_message(
        self, agent_name: str, conversation_name: str, message: str
    ) -> str:
        try:
            response = requests.delete(
                headers=self.headers,
                url=f"{self.agixt_server}/api/conversation/message",
                json={
                    "message": message,
                    "agent_name": agent_name,
                    "conversation_name": conversation_name,
                },
            )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    # Add this endpoint to boilerplate and add a test
    def update_conversation_message(
        self, agent_name: str, conversation_name: str, message: str, new_message: str
    ) -> str:
        try:
            response = requests.put(
                headers=self.headers,
                url=f"{self.agixt_server}/api/conversation/message",
                json={
                    "message": message,
                    "new_message": new_message,
                    "agent_name": agent_name,
                    "conversation_name": conversation_name,
                },
            )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    # Add a test
    def get_memories_external_sources(
        self, agent_name: str, collection_number: str, company_id=None
    ):
        try:
            if not company_id:
                response = requests.get(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/memory/external_sources/{collection_number}",
                )
            else:
                response = requests.get(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/memory/external_sources/{collection_number}/{company_id}",
                )
            if self.verbose:
                parse_response(response)
            return response.json()["external_sources"]
        except Exception as e:
            return self.handle_error(e)

    # Add a test
    def delete_memory_external_source(
        self,
        agent_name: str,
        source: str,
        collection_number: str,
        company_id=None,
        user=True,
    ) -> str:
        try:
            if not company_id:
                response = requests.delete(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/memory/external_source",
                    json={
                        "external_source": source,
                        "collection_number": collection_number,
                        "user": user,
                    },
                )
            else:
                response = requests.delete(
                    headers=self.headers,
                    url=f"{self.base_url}/api/agent/{agent_name}/memory/external_source",
                    json={
                        "external_source": source,
                        "collection_number": collection_number,
                        "company_id": company_id,
                        "user": user,
                    },
                )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    # Add a test
    def get_persona(self, agent_name: str, company_id: str = None) -> str:
        try:
            if company_id:
                response = requests.get(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/persona/{company_id}",
                )
            else:
                response = requests.get(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/persona",
                )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    # Add a test
    def update_persona(self, agent_name: str, persona: str, company_id: str = None):
        try:
            if company_id:
                response = requests.put(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/persona",
                    json={"persona": persona, "company_id": company_id},
                )
            else:
                response = requests.put(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/persona",
                    json={"persona": persona},
                )
            if self.verbose:
                parse_response(response)
            return response.json()["message"]
        except Exception as e:
            return self.handle_error(e)

    def toggle_command(
        self, agent_name: str, command_name: str, enable: bool, company_id: str = None
    ):
        if not company_id:
            try:
                response = requests.patch(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/command",
                    json={"command_name": command_name, "enable": enable},
                )
                if self.verbose:
                    parse_response(response)
                return response.json()["message"]
            except Exception as e:
                return self.handle_error(e)
        else:
            try:
                response = requests.patch(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/command/{company_id}",
                    json={"command_name": command_name, "enable": enable},
                )
                if self.verbose:
                    parse_response(response)
                return response.json()["message"]
            except Exception as e:
                return self.handle_error(e)

    def get_agent_extensions(self, agent_name: str = "XT", company_id: str = None):
        if not company_id:
            try:
                response = requests.get(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/extensions",
                )
                if self.verbose:
                    parse_response(response)
                return response.json()["extensions"]
            except Exception as e:
                return self.handle_error(e)
        else:
            try:
                response = requests.get(
                    headers=self.headers,
                    url=f"{self.agixt_server}/api/agent/{agent_name}/extensions/{company_id}",
                )
                if self.verbose:
                    parse_response(response)
                    return response.json()["extensions"]
            except Exception as e:
                return self.handle_error(e)

    # Activity Log endpoints
    def get_activity_logs(
        self,
        company_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ):
        """
        Retrieve activity logs with optional filtering and pagination.
        
        Args:
            company_id: Filter by specific company
            entity_type: Filter by entity type ('ticket', 'asset', etc.)
            entity_id: Filter by specific entity ID
            user_id: Filter by user who performed action
            limit: Number of logs to return (1-1000, default: 100)
            offset: Pagination offset (default: 0)
        """
        try:
            params = {
                "limit": limit,
                "offset": offset,
            }
            if company_id:
                params["company_id"] = company_id
            if entity_type:
                params["entity_type"] = entity_type
            if entity_id:
                params["entity_id"] = entity_id
            if user_id:
                params["user_id"] = user_id
            
            response = requests.get(
                headers=self.headers,
                url=f"{self.base_url}/activity-logs",
                params=params,
            )
            if self.verbose:
                parse_response(response)
            return response.json()
        except Exception as e:
            return self.handle_error(e)

    def get_entity_activity_logs(self, entity_type: str, entity_id: str):
        """
        Get all activity logs for a specific entity.
        
        Args:
            entity_type: Type of entity ('ticket', 'asset', etc.)
            entity_id: ID of the specific entity
        """
        try:
            response = requests.get(
                headers=self.headers,
                url=f"{self.base_url}/activity-logs/{entity_type}/{entity_id}",
            )
            if self.verbose:
                parse_response(response)
            return response.json()
        except Exception as e:
            return self.handle_error(e)

    def get_ticket_activity_logs(self, ticket_id: str):
        """
        Convenient endpoint to get all logs for a specific ticket.
        
        Args:
            ticket_id: ID of the ticket
        """
        try:
            response = requests.get(
                headers=self.headers,
                url=f"{self.base_url}/tickets/{ticket_id}/activity-logs",
            )
            if self.verbose:
                parse_response(response)
            return response.json()
        except Exception as e:
            return self.handle_error(e)

    def get_asset_activity_logs(self, asset_id: str):
        """
        Convenient endpoint to get all logs for a specific asset.
        
        Args:
            asset_id: ID of the asset
        """
        try:
            response = requests.get(
                headers=self.headers,
                url=f"{self.base_url}/assets/{asset_id}/activity-logs",
            )
            if self.verbose:
                parse_response(response)
            return response.json()
        except Exception as e:
            return self.handle_error(e)