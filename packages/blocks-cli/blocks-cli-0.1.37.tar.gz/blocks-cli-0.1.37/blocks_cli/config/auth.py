import re
import toml
from typing import Optional
from pydantic import BaseModel

class AuthConfig(BaseModel):

    uid: Optional[str] = ""
    puid: Optional[str] = ""
    wid: Optional[str] = ""
    # Corresponds to env variable BLOCKS_AUTH__API_KEY
    api_key: Optional[str] = ""
    job_session_token: Optional[str] = ""

    def save_api_key(self, api_key: str) -> None:
        """Save the API key to the config file."""
        from blocks_cli.config.config import Config

        # Allow only base64url characters (alphanumeric, '-', '_', and '=')
        # This prevents invalid characters from blowing up the config file
        if re.search(r'[^a-zA-Z0-9\-_=]', api_key):
            raise ValueError("Invalid API key supplied. Please check your API key at [white]https://app.blocksorg.com[/white]")

        config_file = Config.get_config_file()

        config = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = toml.load(f)
        try:
            config['auth']['api_key'] = api_key
        except KeyError:
            config['auth'] = {'api_key': api_key}

        with open(config_file, 'w') as f:
            toml.dump(config, f)

    def get_auth_headers(self) -> dict:
        from blocks_cli.console import console
        headers = {}
        if self.uid and self.puid and self.wid:
            console.print("⚠️ Using uid, puid and wid for auth headers. This is intended for development purposes only.", style="yellow bold")
            headers["x-blocks-uid"] = self.uid
            headers["x-blocks-puid"] = self.puid
            headers["x-blocks-wid"] = self.wid
        else:
            headers["Authorization"] = f"ApiKey {self.api_key}"

        return headers