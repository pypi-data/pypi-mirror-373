import json
import os
from dotenv import load_dotenv
import typer
from supabase import create_client, Client

# Load variables from .env file
load_dotenv()

app = typer.Typer()

CONFIG_DIR = os.path.expanduser("~/.agenthub")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):  # ✅ works with str path
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

@app.command()
def login(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True)
):
    """
    Login with email and password, fetch Supabase token, and save it locally.
    """
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )

        if response.user:
            user = response.user
            session = response.session
            access_token = session.access_token
            refresh_token = session.refresh_token
            email = user.email
            role = user.role
            provider = user.app_metadata['provider']
            last_sign_in_at = str(user.last_sign_in_at)

            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, "w") as f:
                json.dump(
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": {
                            "user_id": user.id,
                            "email": email,
                            "role": role,
                            "last_sign_in_at": last_sign_in_at
                        },
                        "provider":provider,
                        
                     },
                    f,
                    indent=2,
                    default=str
                )

            typer.secho("✅ Login successful! Token saved.", fg=typer.colors.GREEN)
        else:
            typer.secho("❌ Login failed: No user returned.", fg=typer.colors.RED)

    except Exception as e:
        typer.secho(f"⚠️ Error: {str(e)}", fg=typer.colors.RED)
        
@app.command()
def whoami():
    """
    Display stored user session info.
    """
    config = load_config()
    if not config:
        typer.secho("⚠️ Not logged in. Run `agenthub login`.", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.secho("👤 Current session:", fg=typer.colors.BLUE)
    typer.echo(f"   Provider: {config['provider']}")
    typer.echo(f"   Role: {config['user']['role']}")
    typer.echo(f"   Access Token: {config['access_token'][:15]}...")  # partial for safety
    typer.echo(f"   Last Sign-in: {config['user']['last_sign_in_at']}")

@app.command()
def logout():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        print("✅ Logged out successfully")
    else:
        print("⚠️ You are not logged in.")

if __name__ == "__main__":
    app()
