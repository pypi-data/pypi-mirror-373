import argparse, os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from config import Config, loadenv
    from api_client import ApiClient
except ImportError as e:
    from .config import Config, loadenv
    from .api_client import ApiClient


class CLIRunner:
    def __init__(self):
        """Initialize the CLI runner."""
        print("🚀 Agent Space Deployment Service CLI")
        print("=" * 50)
        
        self.parser = argparse.ArgumentParser(description="CLI for interacting with Agent Space and Reasoning Engines")
        self._setup_arguments()
        self._show_available_commands()
        self.last_engines_list = []  # Cache the last engine list for position-based deletion
        self.last_agents_list = []   # Cache the last agents list for position-based deletion
        self.last_auth_list = []     # Cache the last authorization list for position-based deletion

    def _setup_arguments(self):
        subparsers = self.parser.add_subparsers(dest="command")
        # List reasoning engines  
        subparsers.add_parser("list-engines", help="List all reasoning engines in the project")
        # Delete reasoning engine
        delete_engine_parser = subparsers.add_parser("delete-engine", help="Delete a reasoning engine by list position")
        delete_engine_parser.add_argument("position", help="Position number from the list (e.g., 1, 2, 3...)")
        
        # Agent space commands
        subparsers.add_parser("list-agents", help="List all agents in the agent space")
        delete_agent_parser = subparsers.add_parser("delete-agent", help="Delete an agent from agent space by list position")
        delete_agent_parser.add_argument("position", help="Position number from the list (e.g., 1, 2, 3...)")
        
        # Authorization commands
        subparsers.add_parser("list-authorizations", help="List all authorizations in the project")
        delete_auth_parser = subparsers.add_parser("delete-authorization", help="Delete an authorization by list position")
        delete_auth_parser.add_argument("position", help="Position number from the list (e.g., 1, 2, 3...)")
        # New commands
        get_auth_info_parser = subparsers.add_parser("get-authorization-info", help="Get details for a specific authorization")
        get_auth_info_parser.add_argument("auth_id", help="Authorization ID")
        update_auth_scopes_parser = subparsers.add_parser("update-authorization-scopes", help="Update scopes for a specific authorization")
        update_auth_scopes_parser.add_argument("auth_id", help="Authorization ID")
        update_auth_scopes_parser.add_argument("scopes", help="Comma-separated list of scopes")
        drop_agent_auth_parser = subparsers.add_parser("drop-agent-authorizations", help="Drop all authorizations for an agent space agent")
        drop_agent_auth_parser.add_argument("agent_id", help="Agent ID")

    def run(self):
        # Load environment variables from .env.agent file (same as GUI editor)
        env_agent_path = ".env.agent"
        if os.path.exists(env_agent_path):
            try:
                loadenv(env_agent_path)
                print(f"✅ Loaded environment from {env_agent_path}")
            except Exception as e:
                print(f"⚠️ Warning: Could not load {env_agent_path}: {e}")
        else:
            print(f"⚠️ No {env_agent_path} file found. Please create one with your environment variables.")
        
        # Try DEV first, then PROD, then fallback to legacy variables
        config_dev = Config("DEV")
        config_prod = Config("PROD")
        
        if config_dev.is_configured:
            config = config_dev
            print("✅ Using DEV environment configuration")
        elif config_prod.is_configured:
            config = config_prod
            print("✅ Using PROD environment configuration")
        else:
            # Fallback to legacy environment variables
            config = Config("DEV")  # This will use legacy fallbacks
            print("⚠️ Using legacy environment variables (consider upgrading to DEV_/PROD_ prefixed variables)")
        
        if not config.is_configured:
            print("\n❌ Error: Required configuration values are missing.")
            print("Please ensure your .env.agent file contains the required variables:")
            print("  - DEV_PROJECT_ID or PROD_PROJECT_ID")
            print("  - DEV_PROJECT_NUMBER or PROD_PROJECT_NUMBER") 
            print("  - DEV_PROJECT_LOCATION or PROD_PROJECT_LOCATION")
            print("  - DEV_AGENT_SPACE_ENGINE or PROD_AGENT_SPACE_ENGINE")
            return
        
        self.api_client = ApiClient(
            project_id=config.project_id,
            project_number=config.project_number,
            location=config.location,
            engine_name=config.engine_name,
            staging_bucket=config.staging_bucket,
            oauth_client_id=config.oauth_client_id,
            oauth_client_secret=config.oauth_client_secret,
            agent_import=config.agent_import,
            mode="live"  # or "mock" for testing
        )

        while True:
            try:
                command = input("\nEnter a command (or 'exit' to quit): ").strip()
                if command.lower() == "exit":
                    print("Exiting CLI. Goodbye!")
                    break

                args = self.parser.parse_args(command.split())

                if args.command == "list-engines":
                    self._list_engines()
                elif args.command == "delete-engine":
                    self._delete_engine(args.position)
                elif args.command == "list-agents":
                    self._list_agents()
                elif args.command == "delete-agent":
                    self._delete_agent(args.position)
                elif args.command == "list-authorizations":
                    self._list_authorizations()
                elif args.command == "delete-authorization":
                    self._delete_authorization(args.position)
                elif args.command == "get-authorization-info":
                    self._get_authorization_info(args.auth_id)
                elif args.command == "update-authorization-scopes":
                    scopes = [s.strip() for s in args.scopes.split(",") if s.strip()]
                    self._update_authorization_scopes(args.auth_id, scopes)
                elif args.command == "drop-agent-authorizations":
                    self._drop_agent_authorizations(args.agent_id)
                else:
                    self.parser.print_help()
            except SystemExit:
                # Catch argparse's SystemExit to prevent CLI from closing
                print("Invalid command. Please try again.")
            except Exception as e:
                raise
                print(f"An error occurred: {e}")
        print("\nAvailable commands:")
        print("  list-engines            List all reasoning engines in the project")
        print("  delete-engine <pos>     Delete a reasoning engine by list position")
        print("  list-agents             List all agents in the agent space")
        print("  delete-agent <pos>      Delete an agent from agent space by list position")
        print("  list-authorizations     List all authorizations in the project")
        print("  delete-authorization <pos>  Delete an authorization by list position")
        print("  exit                    Quit the CLI")

    def _show_available_commands(self):
        """Show available commands."""
        print("\nAvailable commands:")
        print("  list-engines            List all reasoning engines in the project")
        print("  delete-engine <pos>     Delete a reasoning engine by list position")
        print("  list-agents             List all agents in the agent space")
        print("  delete-agent <pos>      Delete an agent from agent space by list position")
        print("  list-authorizations     List all authorizations in the project")
        print("  delete-authorization <pos>  Delete an authorization by list position")
        print("  exit                    Quit the CLI")

    # Removed deploy/create operations

    def _list_engines(self):
        """List reasoning engines."""
        print("📋 Listing reasoning engines...")
        try:
            engines = self.api_client.list_reasoning_engines()
            self.last_engines_list = engines  # Cache for position-based deletion
            if not engines:
                print("No reasoning engines found.")
                self._show_available_commands()
                return
            for idx, engine in enumerate(engines, start=1):
                print(f"[{idx}] ID: {engine['id']}")
                print(f"    Display Name: {engine['display_name']}")
                print(f"    Resource Name: {engine['resource_name']}")
                print(f"    Create Time: {engine['create_time']}")
                print("    ---")
            self._show_available_commands()
        except Exception as e:
            error_msg = str(e)
            if "api_mode" in error_msg or "Failed to register API methods" in error_msg:
                print("⚠️ Vertex AI API registration warning suppressed.")
                print("Continuing with engine listing...")
                # Try to continue anyway - the error might not be fatal
                print("No reasoning engines found or list unavailable due to API registration.")
            else:
                print(f"❌ Error listing engines: {e}")
            self._show_available_commands()

    def _delete_engine(self, position):
        """Delete a reasoning engine by list position."""
        try:
            pos = int(position)
        except ValueError:
            print(f"❌ Invalid position: {position}. Please provide a number (e.g., 1, 2, 3...)")
            return
        
        if not self.last_engines_list:
            print("❌ No engines list available. Please run 'list-engines' first.")
            return
        
        if pos < 1 or pos > len(self.last_engines_list):
            print(f"❌ Invalid position: {pos}. Available positions: 1-{len(self.last_engines_list)}")
            return
        
        # Get the engine at the specified position (convert to 0-based index)
        selected_engine = self.last_engines_list[pos - 1]
        
        # Show confirmation prompt
        print(f"\n🗑️ About to delete engine:")
        print(f"    Position: [{pos}]")
        print(f"    ID: {selected_engine['id']}")
        print(f"    Display Name: {selected_engine['display_name']}")
        print(f"    Resource Name: {selected_engine['resource_name']}")
        
        confirmation = input(f"\nAre you sure you want to delete this engine? (yes/no): ").strip().lower()
        
        if confirmation not in ['yes', 'y']:
            print("❌ Deletion canceled.")
            return
        
        print(f"🗑️ Deleting engine at position {pos}...")
        try:
            status, message = self.api_client.delete_reasoning_engine_by_id(selected_engine['resource_name'])
            print(f"✅ Status: {status}, Message: {message}")
            
            # Remove from cached list
            self.last_engines_list.pop(pos - 1)
            print("💡 Tip: Run 'list-engines' to see the updated list.")
        except Exception as e:
            print(f"❌ Error deleting engine: {e}")

    def _list_agents(self):
        """List agent space agents."""
        print("👥 Listing agent space agents...")
        try:
            agents = self.api_client.list_agent_space_agents()
            self.last_agents_list = agents  # Cache for position-based deletion
            if not agents:
                print("No agents found in agent space.")
                self._show_available_commands()
                return
            for idx, agent in enumerate(agents, start=1):
                print(f"[{idx}] ID: {agent['id']}")
                print(f"    Display Name: {agent['display_name']}")
                print(f"    Authorization ID: {agent['authorization_id']}")
                print(f"    Engine ID: {agent['engine_id']}")
                print(f"    Full Name: {agent['full_name']}")
                print("    ---")
            self._show_available_commands()
        except Exception as e:
            print(f"❌ Error listing agents: {e}")
            self._show_available_commands()

    def _delete_agent(self, position):
        """Delete an agent from agent space by list position."""
        try:
            pos = int(position)
        except ValueError:
            print(f"❌ Invalid position: {position}. Please provide a number (e.g., 1, 2, 3...)")
            return
        
        if not self.last_agents_list:
            print("❌ No agents list available. Please run 'list-agents' first.")
            return
        
        if pos < 1 or pos > len(self.last_agents_list):
            print(f"❌ Invalid position: {pos}. Available positions: 1-{len(self.last_agents_list)}")
            return
        
        # Get the agent at the specified position (convert to 0-based index)
        selected_agent = self.last_agents_list[pos - 1]
        
        # Show confirmation prompt
        print(f"\n🗑️ About to delete agent:")
        print(f"    Position: [{pos}]")
        print(f"    ID: {selected_agent['id']}")
        print(f"    Display Name: {selected_agent['display_name']}")
        print(f"    Full Name: {selected_agent['full_name']}")
        
        confirmation = input(f"\nAre you sure you want to delete this agent? (yes/no): ").strip().lower()
        
        if confirmation not in ['yes', 'y']:
            print("❌ Deletion canceled.")
            return
        
        print(f"🗑️ Deleting agent at position {pos}...")
        try:
            status, message = self.api_client.delete_agent_from_space(selected_agent['full_name'])
            print(f"✅ Status: {status}, Message: {message}")
            
            # Remove from cached list
            self.last_agents_list.pop(pos - 1)
            print("💡 Tip: Run 'list-agents' to see the updated list.")
        except Exception as e:
            print(f"❌ Error deleting agent: {e}")

    def _list_authorizations(self):
        """List authorizations."""
        print("🔐 Listing authorizations...")
        try:
            authorizations = self.api_client.list_authorizations()
            self.last_auth_list = authorizations  # Cache for position-based deletion
            if not authorizations:
                print("No authorizations found.")
                self._show_available_commands()
                return
            for idx, auth in enumerate(authorizations, start=1):
                print(f"[{idx}] ID: {auth['id']}")
                print(f"    Name: {auth['name']}")
                print("    ---")
            self._show_available_commands()
        except Exception as e:
            print(f"❌ Error listing authorizations: {e}")
            self._show_available_commands()

    def _delete_authorization(self, position):
        """Delete an authorization by list position."""
        try:
            pos = int(position)
        except ValueError:
            print(f"❌ Invalid position: {position}. Please provide a number (e.g., 1, 2, 3...)")
            return
        
        if not self.last_auth_list:
            print("❌ No authorizations list available. Please run 'list-authorizations' first.")
            return
        
        if pos < 1 or pos > len(self.last_auth_list):
            print(f"❌ Invalid position: {pos}. Available positions: 1-{len(self.last_auth_list)}")
            return
        
        # Get the authorization at the specified position (convert to 0-based index)
        selected_auth = self.last_auth_list[pos - 1]
        
        # Show confirmation prompt
        print(f"\n🗑️ About to delete authorization:")
        print(f"    Position: [{pos}]")
        print(f"    ID: {selected_auth['id']}")
        print(f"    Name: {selected_auth['name']}")
        
        confirmation = input(f"\nAre you sure you want to delete this authorization? (yes/no): ").strip().lower()
        
        if confirmation not in ['yes', 'y']:
            print("❌ Deletion canceled.")
            return
        
        print(f"🗑️ Deleting authorization at position {pos}...")
        try:
            status, message = self.api_client.delete_authorization(selected_auth['id'])
            print(f"✅ Status: {status}, Message: {message}")
            
            # Remove from cached list
            self.last_auth_list.pop(pos - 1)
            print("💡 Tip: Run 'list-authorizations' to see the updated list.")
        except Exception as e:
            print(f"❌ Error deleting authorization: {e}")

    def _get_authorization_info(self, auth_id):
        """Get details for a specific authorization."""
        print(f"🔍 Getting info for authorization: {auth_id}")
        try:
            info = self.api_client.get_authorization_info(auth_id)
            from pprint import pprint
            pprint(info)
        except Exception as e:
            print(f"❌ Error getting authorization info: {e}")

    def _update_authorization_scopes(self, auth_id, scopes):
        """Update scopes for a specific authorization."""
        print(f"🔧 Updating scopes for authorization: {auth_id}")
        print(f"New scopcdscsdes: {scopes}")

        result = self.api_client.update_authorization_scopes(auth_id, scopes)
        from pprint import pprint
        pprint(result)

    def _drop_agent_authorizations(self, agent_id):
        """Drop all authorizations for an agent space agent."""
        print(f"🗑️ Dropping all authorizations for agent: {agent_id}")
        try:
            result = self.api_client.drop_agent_authorizations(agent_id)
            from pprint import pprint
            pprint(result)
        except Exception as e:
            raise
            print(f"❌ Error dropping agent authorizations: {e}")

if __name__ == "__main__":
    CLIRunner().run()
