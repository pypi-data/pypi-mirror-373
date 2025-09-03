from functools import wraps
from flask import request, current_app
import requests
from shared_kernel.auth import JWTTokenHandler
from shared_kernel.config import Config
from shared_kernel.exceptions import Unauthorized, NotFound
from shared_kernel.interfaces.databus import DataBus
from shared_kernel.messaging import DataBusFactory
from shared_kernel.registries.service_event_registry import ServiceEventRegistry


config = Config()
token_handler = JWTTokenHandler(config.get("JWT_SECRET_KEY"))
service_event_registry = ServiceEventRegistry()
databus: DataBus = DataBusFactory.create_data_bus(bus_type="HTTP", config={})


def get_workbook_share_meta(workbook_id):
    try:
        event = {
            "event_name": "GET_WORKBOOK_SHARE_META",
            "event_payload": {"workbook_id": workbook_id},
        }
        response = databus.request_event(
            getattr(service_event_registry, "GET_WORKBOOK_SHARE_META"), event
        )
        return response.get("data")

    except requests.RequestException as e:
        current_app.logger.error(f"Error fetching workbook: {e}")
        return None


def check_user_in_org(user, organization_id):
    return user["organization_id"] == organization_id


def has_workbook_share(user_id, shared_users):
    return user_id in shared_users


# Decorator to protect routes based on workbook permissions
def workbook_permission_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        workbook_id = kwargs.get("workbook_id")
        # Fetch the workbook share data from the master service
        workbook_share_data = get_workbook_share_meta(workbook_id)
        if not workbook_share_data:
            raise NotFound("Workbook not found.")

        # Public Access: No token required for public workbooks
        if workbook_share_data.get("is_public"):
            return current_app.ensure_sync(f)(None, *args, **kwargs)

        # Non-public requests need token verification
        token = None
        if not request.authorization:
            raise Unauthorized("Token is missing!")

        token = request.authorization.token
        payload = token_handler.decode_token(token)

        if "error" in payload:
            raise Unauthorized("Failed to parse token")

        # Add user information to the request context
        current_user = {
            "user_id": payload["user_id"],
            "organization_id": payload["organization_id"],
        }

        # Owner Access
        if current_user["user_id"] == workbook_share_data.get("created_by"):
            return current_app.ensure_sync(f)(current_user, *args, **kwargs)

        # Organization Access
        if workbook_share_data.get("shared_with_org") and check_user_in_org(
            current_user, workbook_share_data["organization_id"]
        ):
            return current_app.ensure_sync(f)(current_user, *args, **kwargs)

        # Specific User Access
        if has_workbook_share(
            current_user["user_id"], workbook_share_data["shared_users"]
        ):
            return current_app.ensure_sync(f)(current_user, *args, **kwargs)

        # If none of the conditions are met, deny access
        raise Unauthorized("You don't have permission to access this workbook.")

    return decorator
