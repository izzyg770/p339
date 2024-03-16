"""CCP REST API."""
from ccp.api.main import get_resource
from ccp.api.pets import get_pet
from ccp.views.accounts import handle_login
from ccp.api.model import get_all_pets
from ccp.api.likes import post_likes
from ccp.api.likes import delete_like
from ccp.api.comments import post_comments