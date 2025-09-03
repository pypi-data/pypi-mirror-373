"""
Editor Functions
"""

import sys
import os
import time
import textwrap
import subprocess
from anatools.lib.print import print_color
from anatools.anaclient._menu import _get_key, _clear_lines, print_link

def _select_session(sessions, action_name="select"):
    """
    Interactive session selector using arrow keys.
    
    Parameters
    ----------
    sessions : list
        List of session dictionaries from listRemoteDevelopment
    action_name : str
        Name of the action (e.g., "stop" or "delete") for display purposes
        
    Returns
    -------
    str or None
        Selected session ID or None if cancelled
    """
    if not sessions:
        print(f"\n❌ No sessions available to {action_name}")
        return None

    current_selection = None
    last_displayed_lines = 0

    def display_sessions():
        nonlocal last_displayed_lines
        if last_displayed_lines > 0:
            _clear_lines(last_displayed_lines)
        
        print(f"\n📝 Use arrow keys (↑/↓) to {action_name} a session, Enter to confirm, q to quit:\n")
        
        for i, session in enumerate(sessions):
            is_selected = current_selection is not None and i == current_selection
            session_line = (
                f"  {'▶' if is_selected else ' '} "
                f"🏢 {session['organization'][:15]} "
                f"🔗 {session['editorUrl']} "
                f"📦 {session['channel']} "
                f"📟 {session['instanceType']} "
                f"📊 {session['status']['state']} "
                f"🔑 {session['sshPort']}"
            )
            if is_selected:
                print(f"\033[44m{session_line}\033[0m")
            else:
                print(session_line)
        
        last_displayed_lines = len(sessions) + 3

    display_sessions()

    while True:
        key = _get_key(None)
        if key == 'up':
            if current_selection is None:
                current_selection = len(sessions) - 1
            else:
                current_selection = max(0, current_selection - 1)
            display_sessions()
        elif key == 'down':
            if current_selection is None:
                current_selection = 0
            else:
                current_selection = min(len(sessions) - 1, current_selection + 1)
            display_sessions()
        elif key == 'enter':
            if current_selection is not None:
                return sessions[current_selection]['editorSessionId']
        elif key.lower() == 'q':
            if last_displayed_lines > 0:
                _clear_lines(last_displayed_lines)
            print("\n❌ Session selection cancelled")
            return None

def _select_editor(client, action_name="select"):
    """Interactive editor selector with rich display.

    Parameters
    ----------
    sessions : list[dict]
        List containing dictionaries describing editor sessions. Must include keys:
        - editorSessionId
        - editorUrl
        - instanceType
        - status (with key 'state')
        - workspaceName (optional) or workspaceId
    action_name : str, default "select"
        The verb used in prompt (e.g. "delete", "stop").

    Returns
    -------
    str | None
        The selected `editorSessionId` or None if user cancelled.
    """
    def _get_sessions(client):
        raw_sessions = client.get_servers()
        workspaces = client.get_workspaces()
        sessions = []
        for s in raw_sessions:
            workspace = [ws for ws in workspaces if ws['workspaceId'] == s.get('workspaceId', '')][0]
            sessions.append({
                'editorSessionId': s.get('editorId'),
                'name': s.get('name', s.get('editorId')),
                'editorUrl': s.get('url', ''),
                'serverPath': s.get('serverPath', '/workspace/'),
                'organization': s.get('organizationId', ''),
                'instanceType': s.get('instanceType', ''),
                'status': s.get('status', {}),
                'workspaceId': s.get('workspaceId', ''),
                'workspaceName': workspace['name']
            })
        return sessions
    
    sessions = _get_sessions(client)
    if not sessions:
        print(f"\n❌ No sessions available to {action_name}")
        return None

    current_selection: int | None = None
    last_lines_printed = 0

    def _link(text: str, url: str) -> str:
        """Return clickable terminal hyperlink (OSC 8)."""
        ESC = "\033"
        return f"{ESC}]8;;{url}{ESC}\\{text}{ESC}]8;;{ESC}\\"


    def _render():
        nonlocal last_lines_printed
        if last_lines_printed > 0: _clear_lines(last_lines_printed)
        print(
            f"\n📝 Use arrow keys (↑/↓) to {action_name} a session, Enter to confirm.\n\n" +
            f"   |       Server      |     Status      |    Instance    |      Workspace    |                IDEs              |\n" +
            f"   |-------------------|-----------------|----------------|-------------------|----------------------------------|"
        )
        for i, s in enumerate(sessions):
            selected = current_selection is not None and i == current_selection
            name = s['name']
            eid = s["editorSessionId"]
            path= s['serverPath']
            host = s["editorUrl"].replace("https://", "")
            if s['status']['state'] == 'running':
                browser = _link("Browser", s["editorUrl"])
                windsurf = _link("Windsurf", f"windsurf://vscode-remote/ssh-remote+{eid}@{host}:443{path}")
                cursor = _link("Cursor", f"cursor://vscode-remote/ssh-remote+{eid}@{host}:443{path}")
                vscode = _link("VSCode", f"vscode://vscode-remote/ssh-remote+{eid}@{host}:443{path}")
            else: browser = windsurf = cursor = vscode = ""
            workspace_name = s.get("workspaceName") or s.get("workspaceId", "")
            line = (
                f"  {'▶' if selected else ' '} "
                f"🆔 {name:<17}  "
                f"📊 {s['status']['state']:<13}  "
                f"📟 {s['instanceType']:<12}  "
                f"🗄 {workspace_name[:15]:<15}  "
                f"{browser}{'  ' if browser else ''}{windsurf}{'  ' if windsurf else ''}{cursor}{'  ' if cursor else ''}{vscode}"
            )
            if selected: print(f"\033[44m{line}\033[0m")
            else: print(line)
        last_lines_printed = len(sessions) + 5

    # First render
    sessions = _get_sessions(client)
    _render()
    while True:
        timeout = None
        for session in sessions:
            if session['status']['state'] in ['starting', 'stopping', 'terminating']: timeout = 1
        key = _get_key(None, timeout)
        if key == 'up':
            if current_selection is None: current_selection = len(sessions) - 1
            else: current_selection = max(0, current_selection - 1)
            _render()
        elif key == 'down':
            if current_selection is None: current_selection = 0
            else: current_selection = min(len(sessions) - 1, current_selection + 1)
            _render()
        elif key == 'enter':
            if current_selection is not None:
                _clear_lines(last_lines_printed)
                return sessions[current_selection]['editorSessionId'], sessions[current_selection]['status']['state']
        elif key == None:
            sessions = _get_sessions(client)
            _render()


def _spinner_animation():
    """Generator for a simple spinner animation."""
    while True:
        for char in '|/-\\':
            yield char

def _show_operation_status(operation):
    """Show a loading spinner while an operation is in progress."""
    import threading
    import time

    stop_thread = threading.Event()
    spinner = _spinner_animation()

    def spin():
        while not stop_thread.is_set():
            sys.stdout.write(f"\r⏳ {next(spinner)} {operation}...")
            sys.stdout.flush()
            time.sleep(0.1)

        sys.stdout.write('\r\033[K')
        sys.stdout.write('\n')
        sys.stdout.flush()

    spinner_thread = threading.Thread(target=spin)
    spinner_thread.start()
    return stop_thread, spinner_thread

def _cleanup_ssh_config(environment, editorSessionId, sshPort=None):
    """Helper function to clean up SSH configuration and known hosts.
    
    Parameters
    ----------
    environment : str
        The environment (dev, prod, etc)
    editorSessionId : str
        The ID of the editor session to clean up.
    sshPort : str, optional
        The SSH port to remove from known hosts. If not provided, only the port-less entry is removed.
    """
    
    if sshPort:
        subprocess.run(["ssh-keygen", "-R", f"[{editorSessionId}.dyn-editor.{environment}.rendered.ai]:{sshPort}"], check=True)

    # Clean up SSH config
    ssh_config_path = os.path.join(os.path.expanduser("~"), ".ssh", "config")
    if os.path.exists(ssh_config_path):
        with open(ssh_config_path, "r") as f:
            ssh_config_content = f.read()
        # Delete the entire block for the old session
        start_pattern = f"Host {editorSessionId}.dyn-editor.{environment}.rendered.ai"
        end_pattern = "Host "
        start_index = ssh_config_content.find(start_pattern)
        if start_index != -1:
            end_index = ssh_config_content.find(end_pattern, start_index + len(start_pattern))
            if end_index == -1:
                end_index = len(ssh_config_content)
            ssh_config_content = ssh_config_content[:start_index] + ssh_config_content[end_index:]
        with open(ssh_config_path, "w") as f:
            f.write(ssh_config_content.strip() + "\n")

def _is_windows_without_wsl():
    """Check if running on Windows without WSL"""
    if sys.platform != "win32":
        return False
    # Check for WSL
    try:
        with open('/proc/version', 'r') as f:
            if 'Microsoft' in f.read():
                return False  # Running in WSL
    except FileNotFoundError:
        pass
    return True  # Regular Windows

def create_remote_development(self, channelId, organizationId=None, channelVersion=None, instanceType=None):
    """
    Creates a remote development environment.

    This method initiates a remote development session on the specified channel, optionally within a given organization.
    If no organizationId is provided, it defaults to the organization associated with the current user.

    Parameters
    ----------
    channelId : str
        The ID of the channel to use for creating the remote development session.
    channelVersion : str, optional
        The version of the channel to use. If not provided, defaults to the latest version.
    organizationId : str, optional
        The ID of the organization where the session will be created. 
        If not provided, defaults to the user's organization.
    instanceType : str, optional
        The type of instance to use for the remote development session.
        If not provided, defaults to the instance type specified in the channel.

    Returns
    -------
    str
        A message indicating that the session is being created, along with a link to access the session.

    Notes
    -----
    - This function checks if the user is logged out before proceeding.
    - Calls `ana_api.createRemoteDevelopment` to initiate the session.
    - Displays a warning message indicating that the feature is experimental.

    Example Output
    --------------
    ⚠️ Warning: This feature is very experimental. Use with caution! ⚠️
    🚀 Your environment will be available here shortly: 🔗 <editorUrl> 🌐
    """
    if self.check_logout():
        print("\n❌ Error: You are not logged in. Please log in first.\n")
        return

    try:
        session = self.ana_api.createRemoteDevelopment(
            channelId=channelId,
            channelVersion=channelVersion,
            instanceType=instanceType
        )

        print(
            "\n⚠️ Warning: This feature is very experimental. Use with caution! ⚠️\n"
            f"🚀 Your environment will be available here shortly: "
            f"🔗 {session['editorUrl']} 🌐\n"
        )
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            print("\n❌ Error: Access denied. Please check that:")
            print("  • You have the correct permissions for this channel")
            print("  • The channel ID is correct")
            print("  • You are a member of the organization that owns this channel\n")
        elif "404" in error_msg or "Not Found" in error_msg:
            print("\n❌ Error: Channel not found. Please verify the channel ID is correct.\n")
        else:
            print(f"\n❌ Error: Failed to create remote development environment: {error_msg}\n")
            print("Please make sure you are logged in, the channel ID is valid and you have permission to the channel. If the problem persists, please contact support.\n")

def delete_remote_development(self, editorSessionId=None):
    """
    Deletes a remote development session.

    This method removes a specific editor session, optionally within a given organization.
    If no editorSessionId is provided, it will show a list of active sessions and prompt for selection.

    Parameters
    ----------
    editorSessionId : str, optional
        The ID of the editor session to be deleted. If not provided, will prompt for selection.

    Returns
    -------
    dict
        A dictionary representing the result of the session deletion.

    Notes
    -----
    - This function checks if the user is logged out before proceeding.
    - Calls `ana_api.deleteRemoteDevelopment` to perform the deletion.
    - Use arrow keys (↑/↓) to select a session, Enter to confirm, q to quit
    """
    if self.check_logout():
        print("\n❌ Error: You are not logged in. Please log in first.\n")
        return

    if editorSessionId is None:
        sessions = self.ana_api.listRemoteDevelopment(organizationId=None)
        editorSessionId = _select_session(sessions, action_name="delete")
        if editorSessionId is None:
            return

    spinner_stop_event, spinner_thread = _show_operation_status(f"Deleting Development Session {editorSessionId}")
    try:
        session = self.ana_api.deleteRemoteDevelopment(editorSessionId=editorSessionId)
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            print("\n❌ Error: Access denied. Please check that:")
            print("  • You have the correct permissions for this channel")
            print("  • The channel ID is correct")
            print("  • You are a member of the organization that owns this channel\n")
        elif "404" in error_msg or "Not Found" in error_msg:
            print("\n❌ Error: Session not found. Please verify the session ID is correct.\n")
        else:
            print(f"\n❌ Error: Failed to delete development session: {error_msg}\n")
            print("If the problem persists, please contact support.\n")
    finally:
        spinner_stop_event.set()
        spinner_thread.join()
    print(f"\n🗑️  Successfully deleted Development Session {editorSessionId}\n")

    print(f"To remove SSH configuration call `remove_ssh_remote_development()`")


def list_remote_development(self, organizationId=None): 
    """Shows all the active development sessions in the organization.
    
    Parameters
    ----------
    organizationId : str
        The ID of the organization to list the active development sessions.
    
    Returns
    -------
    list[dict]
        If organizationId is not provided, returns all active sessions in organizations that user has access to.
        If organizationId is provided, returns active sessions in that specific organization.
    """
    if self.check_logout():
        print("\n❌ Error: You are not logged in. Please log in first.\n")
        return

    try:
        sessions = self.ana_api.listRemoteDevelopment(organizationId=organizationId)

        if not sessions:
            print("✨ No active development sessions found. Use `create_remote_development` to start a new session.")
            return sessions

        if organizationId is None:
            print("\n🚧 Active Development Sessions:\n")
        else:
            print(f"\n🚧 Active Development Sessions in Organization {organizationId}:\n")
        

        for session in sessions:
            print(
                f"🏢 {session['organization'][:15]} "
                f"🔗 {session['editorUrl']} "
                f"📦 {session['channel']} "
                f"📟 {session['instanceType']} "
                f"📊 {session['status']['state']} "
                f"🔑 {session['sshPort']}"
                f"📅 {session['updatedAt']}"
            )
            if session['status']['state'] == 'ERROR':
                print(f"\t❌ Error: {session['status']['message']}")

        print(f"\n\nTo ssh in to an instance, add your public ssh key to /home/anadev/.ssh/authorized_keys and call `prepare_ssh_remote_development()`.")
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            print("\n❌ Error: Access denied. Please check that:")
            print("  • You have the correct permissions for this channel")
            print("  • The channel ID is correct")
            print("  • You are a member of the organization that owns this channel\n")
        elif "404" in error_msg or "Not Found" in error_msg:
            print("\n❌ Error: Organization not found. Please verify the organization ID is correct.\n")
        else:
            print(f"\n❌ Error: Failed to list development sessions: {error_msg}\n")
            print("If the problem persists, please contact support.\n")


def stop_remote_development(self, editorSessionId=None):
    """
    Stops a remote development session.

    This method stops a specific editor session, optionally within a given organization.
    If no editorSessionId is provided, it will show a list of active sessions and prompt for selection.

    Parameters
    ----------
    editorSessionId : str, optional
        The ID of the editor session to be stopped. If not provided, will prompt for selection.

    Returns
    -------
    dict
        A dictionary representing the result of the session stop operation.

    Notes
    -----
    - This function checks if the user is logged out before proceeding.
    - Calls `ana_api.stopRemoteDevelopment` to stop the session.
    - Use arrow keys (↑/↓) to select a session, Enter to confirm, q to quit
    - Only shows sessions that are currently running or resuming
    """
    if self.check_logout():
        print("\n❌ Error: You are not logged in. Please log in first.\n")
        return

    if editorSessionId is None:
        sessions = self.ana_api.listRemoteDevelopment(organizationId=None)
        active_sessions = [s for s in sessions if s['status']['state'] in ('RUNNING', 'RESUMING')]
        if not active_sessions and sessions:
            print("✨ No active sessions available to stop.")
            return
        editorSessionId = _select_session(active_sessions, action_name="stop")
        if editorSessionId is None:
            return

    spinner_stop_event, spinner_thread = _show_operation_status(f"Stopping Development Session {editorSessionId}")
    try:
        session = self.ana_api.stopRemoteDevelopment(editorSessionId=editorSessionId)
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            print("\n❌ Error: Access denied. Please check that:")
            print("  • You have the correct permissions for this channel")
            print("  • The channel ID is correct")
            print("  • You are a member of the organization that owns this channel\n")
        elif "404" in error_msg or "Not Found" in error_msg:
            print("\n❌ Error: Session not found. Please verify the session ID is correct.\n")
        else:
            print(f"\n❌ Error: Failed to stop development session: {error_msg}\n")
            print("If the problem persists, please contact support.\n")
    finally:
        spinner_stop_event.set()
        spinner_thread.join()
    print(f"\n🛑 Successfully stopped Development Session {editorSessionId}\n")


def start_remote_development(self, editorSessionId=None):
    """
    Starts a remote development session.

    This method starts a specific editor session, optionally within a given organization.
    If no editorSessionId is provided, it will show a list of stopped sessions and prompt for selection.

    Parameters
    ----------
    editorSessionId : str, optional
        The ID of the editor session to be started. If not provided, will prompt for selection.

    Returns
    -------
    dict
        A dictionary representing the result of the session start operation.

    Notes
    -----
    - This function checks if the user is logged out before proceeding.
    - Calls `ana_api.startRemoteDevelopment` to start the session.
    - Use arrow keys (↑/↓) to select a session, Enter to confirm, q to quit
    - Only shows sessions that are currently stopped
    """
    if self.check_logout():
        print("\n❌ Error: You are not logged in. Please log in first.\n")
        return

    if editorSessionId is None:
        sessions = self.ana_api.listRemoteDevelopment(organizationId=None)
        stopped_sessions = [s for s in sessions if s['status']['state'] == 'STOPPED']
        if not stopped_sessions and sessions:
            print("✨ No stopped sessions available to start.")
            return
        editorSessionId = _select_session(stopped_sessions, action_name="start")
        if editorSessionId is None:
            return

    spinner_stop_event, spinner_thread = _show_operation_status(f"Starting Development Session {editorSessionId}")
    try:
        session = self.ana_api.startRemoteDevelopment(editorSessionId=editorSessionId)
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            print("\n❌ Error: Access denied. Please check that:")
            print("  • You have the correct permissions for this channel")
            print("  • The channel ID is correct")
            print("  • You are a member of the organization that owns this channel\n")
        elif "404" in error_msg or "Not Found" in error_msg:
            print("\n❌ Error: Session not found. Please verify the session ID is correct.\n")
        else:
            print(f"\n❌ Error: Failed to start development session: {error_msg}\n")
            print("If the problem persists, please contact support.\n")
    finally:
        spinner_stop_event.set()
        spinner_thread.join()
    print(
        f"\n🚀 Successfully started Development Session {editorSessionId}\n"
        f"🔗 Your environment will be available here shortly: {session['editorUrl']} 🌐\n"
    )

# create a new function to prepare ssh sessions. clear old sessions from hosts file. we should list sessions like we do above and allow users to use keys to select the environment
def prepare_ssh_remote_development(self, editorSessionId=None, forceUpdate=False):
    """
    Prepares a remote development session for SSH access.

    This method prepares a specific editor session for SSH access, optionally within a given organization.
    If no editorSessionId is provided, it will show a list of active sessions and prompt for selection.

    Parameters
    ----------
    editorSessionId : str, optional
        The ID of the editor session to prepare SSH for. If not provided, will prompt user to select.
    forceUpdate : bool, optional
        If True, will remove existing SSH configuration before adding new one.

    Returns
    -------
    dict
        A dictionary representing the result of the session preparation.

    Notes
    -----
    - This function checks if the user is logged out before proceeding.
    - Use arrow keys (↑/↓) to select a session, Enter to confirm, q to quit
    - Only shows sessions that are currently running or resuming
    """
    if self.check_logout():
        print("\n❌ Error: You are not logged in. Please log in first.\n")
        return

    if _is_windows_without_wsl():
        print("\n⚠️  SSH configuration management is not supported on Windows.")
        print("Please use Windows Subsystem for Linux (WSL) for full SSH support.")
        return

    sessions = self.ana_api.listRemoteDevelopment(organizationId=None)
    active_sessions = [s for s in sessions if s['status']['state'] in ('RUNNING', 'RESUMING')]
    if not active_sessions and sessions:
        print("✨ No active sessions available to prepare.")
        return

    if editorSessionId is None:
        editorSessionId = _select_session(active_sessions, action_name="prepare")
        if editorSessionId is None:
            return
    
    # Find the selected session to get its port
    session = next((s for s in active_sessions if s['editorSessionId'] == editorSessionId), None)
    if not session:
        print(f"❌ Could not find session {editorSessionId}")
        return

    spinner_stop_event, spinner_thread = _show_operation_status(f"Preparing SSH for Development Session {editorSessionId}")
    try:
        if forceUpdate:
            _cleanup_ssh_config(self.environment, editorSessionId, session.get('sshPort'))
        
        ssh_config_path = os.path.join(os.path.expanduser("~"), ".ssh", "config")
        with open(ssh_config_path, "a+") as f:
            f.seek(0)
            if f.read().find(f"Host {editorSessionId}.dyn-editor.{self.environment}.rendered.ai") == -1:
                ssh_config_template = f'''
                    Host {editorSessionId}.dyn-editor.{self.environment}.rendered.ai
                        HostName ssh-editor.{self.environment}.rendered.ai
                        Port {session.get('sshPort')}
                        User anadev
                        StrictHostKeyChecking no
                        UserKnownHostsFile /dev/null
                '''
                f.write(textwrap.dedent(ssh_config_template))
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Error: Failed to prepare SSH for development session: {error_msg}\n")
        print("If the problem persists, please contact support.\n")
    finally:
        spinner_stop_event.set()
        spinner_thread.join()
    print(f"\n🚀 Successfully prepared SSH for Development Session {editorSessionId}\n")

    print(f"To SSH in to an instance, add your public ssh key to /home/anadev/.ssh/authorized_keys")
    print(f"then call `ssh {editorSessionId}.dyn-editor.{self.environment}.rendered.ai`")
    print(f"or use host {editorSessionId}.dyn-editor.{self.environment}.rendered.ai in your code editor\n")

    print(f"To remove SSH configuration call `remove_ssh_remote_development()`\n")

# add a new function to remove ssh sessions from hosts file and clear old sessions from config
def remove_ssh_remote_development(self, editorSessionId=None):
    """
    Removes a remote development session from SSH access.

    This method removes a specific editor session from SSH access, optionally within a given organization.
    If no editorSessionId is provided, it will show a list of active sessions and prompt for selection.

    Parameters
    ----------
    editorSessionId : str, optional
        The ID of the editor session to be removed. If not provided, will prompt user to select.

    Returns
    -------
    dict
        A dictionary representing the result of the session removal.

    Notes
    -----
    - This function checks if the user is logged out before proceeding.
    - Use arrow keys (↑/↓) to select a session, Enter to confirm, q to quit
    - Only shows sessions that are currently running or resuming
    """
    if self.check_logout():
        print("\n❌ Error: You are not logged in. Please log in first.\n")
        return

    if _is_windows_without_wsl():
        print("\n⚠️  SSH configuration management is not supported on Windows.")
        print("Please use Windows Subsystem for Linux (WSL) for full SSH support.")
        return

    sessions = self.ana_api.listRemoteDevelopment(organizationId=None)

    if editorSessionId is None:
        editorSessionId = _select_session(sessions, action_name="remove")
        if editorSessionId is None:
            return
    
    # Find the selected session to get its port
    session = next((s for s in sessions if s['editorSessionId'] == editorSessionId), None)
    if not session:
        print(f"❌ Could not find session {editorSessionId}")
        return

    spinner_stop_event, spinner_thread = _show_operation_status(f"Removing SSH for Development Session {editorSessionId}")
    try:
        _cleanup_ssh_config(self.environment, editorSessionId, session.get('sshPort'))
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Error: Failed to remove SSH for development session: {error_msg}\n")
        print("If the problem persists, please contact support.\n")
    finally:
        spinner_stop_event.set()
        spinner_thread.join()
    print(f"\n🛑 Successfully removed SSH for Development Session {editorSessionId}\n")


def invite_remote_development(self, editorSessionId, email):
    """
    Invites a user to join a remote development session.

    Parameters
    ----------
    editorSessionId : str
        The ID of the editor session to invite the user to.
    email : str
        The email address of the user to invite.
    Returns
    -------
    bool
        A boolean status of whether the operation was successful.
    """
    self.check_logout()
    return self.ana_api.inviteRemoteDevelopment(editorSessionId, email)


def register_ssh_key(self, filename=None):
    """
    Registers a public SSH key for use with remote development sessions.

    Parameters
    ----------
    filename : str
        The filename of the .pub SSH key to register.
    Returns
    -------
    bool
        A boolean status of whether the operation was successful.
    """
    if self.check_logout():
        print("\n❌ Error: You are not logged in. Please log in first.\n")
        return

    if filename is None:
        # Look for SSH keys in standard locations
        ssh_dir = os.path.expanduser("~/.ssh")
        if not os.path.exists(ssh_dir):
            print("\n❌ Error: No SSH directory found at ~/.ssh\n")
            return
        
        # Find all .pub files
        pub_keys = []
        for file in os.listdir(ssh_dir):
            if file.endswith(".pub"):
                pub_keys.append(os.path.join(ssh_dir, file))
        
        if not pub_keys:
            print("\n❌ Error: No public SSH keys found in ~/.ssh\n")
            return
        
        # Present selection interface
        print("\nAvailable SSH public keys:\n")
        for i, key in enumerate(pub_keys, 1):
            print(f"{i}. {os.path.basename(key)}")
        
        while True:
            try:
                choice = input("\nSelect a key number (or 'q' to quit): ")
                if choice.lower() == 'q':
                    return
                choice = int(choice)
                if 1 <= choice <= len(pub_keys):
                    filename = pub_keys[choice - 1]
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q' to quit.")
    
    # Validate and process the selected/provided key
    if not os.path.splitext(filename)[1] == ".pub":
        raise Exception(f"Invalid filename. Please provide a public SSH key that ends with .pub.")
    
    name = os.path.splitext(os.path.basename(filename))[0]
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            publicKey = f.read().strip()
    else:
        raise Exception(f"Could not find SSH public key file {filename}.")
    
    return self.ana_api.createSSHKey(name=name, key=publicKey)


def deregister_ssh_key(self, name=None):
    """
    Removes a public SSH key for use with remote development sessions.

    Parameters
    ----------
    name : str
        The name of the SSH key to deregister.
    Returns
    -------
    bool
        A boolean status of whether the operation was successful.
    """
    if self.check_logout():
        print("\n❌ Error: You are not logged in. Please log in first.\n")
        return

    if name is None:
        # Get list of registered SSH keys
        keys = self.ana_api.getSSHKeys()
        if not keys:
            print("\n❌ No SSH keys registered\n")
            return

        # Present selection interface
        print("\nRegistered SSH keys:\n")
        for i, key in enumerate(keys, 1):
            print(f"{i}. {key['name']}")

        while True:
            try:
                choice = input("\nSelect a key number to remove (or 'q' to quit): ")
                if choice.lower() == 'q':
                    return
                choice = int(choice)
                if 1 <= choice <= len(keys):
                    name = keys[choice - 1]['name']
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q' to quit.")

    result = self.ana_api.deleteSSHKey(name=name)
    if result:
        print(f"\n✅ Successfully removed SSH key: {name}\n")
    return result


def get_ssh_keys(self):
    """
    Returns a list of SSH keys a user has registered with the platform.

    Parameters
    ----------
    Returns
    -------
    list
        A list of registered SSH keys.
    """
    if self.check_logout():
        print("\n❌ Error: You are not logged in. Please log in first.\n")
        return
    return self.ana_api.getSSHKeys()


# Service/Workspace Editors
def get_servers(self, organizationId=None, workspaceId=None, serverId=None, cursor=None, limit=None, filters=None, fields=None):
    """
    Returns a list of servers for a workspace.
    
    Parameters
    ----------
    organizationId : str
        The ID of the organization to get servers for.
    workspaceid : str
        The ID of the workspace to get servers for.
    serverId : str
        The ID of the server to get.
    Returns
    -------
    list
        A list of servers for the specified workspace.
    """
    self.check_logout()
    if limit is None: limit = 100
    editors = self.ana_api.getEditors(organizationId=organizationId, workspaceId=workspaceId, editorId=serverId, cursor=cursor, limit=limit, filters=filters, fields=fields)
    if not self.interactive or len(editors) != 1: return editors
    else:
        editorId = editors[0]['editorId']
        while True:
            editor = self.ana_api.getEditors(editorId=editorId)[0]
            print(f'Waiting for server {editorId} to start...', end='\r')
            if editor['status']['state'] == 'running': break
            time.sleep(5)
        print_color(f'✅ Server available, open with:                ', '91e600')
        serverpath = editor.get('serverPath', '/workspace/')
        print("  ", end=''); print_link("Browser", editor["url"])
        print("  ", end=''); print_link("Cursor", f"cursor://vscode-remote/ssh-remote+{editor['editorId']}@{editor['url'].replace('https://', '')}:443{serverpath}")
        print("  ", end=''); print_link("VSCode", f"vscode://vscode-remote/ssh-remote+{editor['editorId']}@{editor['url'].replace('https://', '')}:443{serverpath}")
        print("  ", end=''); print_link("Windsurf", f"windsurf://vscode-remote/ssh-remote+{editor['editorId']}@{editor['url'].replace('https://', '')}:443{serverpath}")
        return

def create_server(self, organizationId=None, workspaceId=None, instance=None, name=None):
    """
    Creates a new server for a workspace.

    Parameters
    ----------
    organizationId : str
        The ID of the organization to create the server for.
    workspaceId : str
        The ID of the workspace to create the server for.
    instance : str
        The instance of the server to create.
    name : str
        A custom name to give the server.
    Returns
    -------
    str
        The ID for the newly created server.
    """
    import time
    self.check_logout()
    if organizationId is None: organizationId = self.organization
    if workspaceId is None: workspaceId = self.workspace
    editorId = self.ana_api.createEditor(organizationId=organizationId, workspaceId=workspaceId, instance=instance, name=name)
    if not self.interactive: return editorId
    else:
        starttime = time.time()
        while True:
            editor = self.ana_api.getEditors(editorId=editorId)[0]
            print(f'Waiting for server {editorId} to start...[{time.time()-starttime:.3f}s]', end='\r')
            if editor['status']['state'] == 'running':
                break
            time.sleep(2)
        print(f'Waiting for server {editorId} to start...done. [{time.time()-starttime:3f}s]')
        print_color(f'✅ Server available, open with:                ', '91e600')
        serverpath = editor.get('serverPath', '/workspace/')
        print("  ", end=''); print_link("Browser", editor["url"])
        print("  ", end=''); print_link("Cursor", f"cursor://vscode-remote/ssh-remote+{editor['editorId']}@{editor['url'].replace('https://', '')}:443{serverpath}")
        print("  ", end=''); print_link("VSCode", f"vscode://vscode-remote/ssh-remote+{editor['editorId']}@{editor['url'].replace('https://', '')}:443{serverpath}")
        print("  ", end=''); print_link("Windsurf", f"windsurf://vscode-remote/ssh-remote+{editor['editorId']}@{editor['url'].replace('https://', '')}:443{serverpath}")
        return


def delete_server(self, serverId):
    """
    Deletes an editor session.
    
    Parameters
    ----------
    serverId : str
        The ID of the server to delete.
    Returns
    -------
    bool
        If true, the editor session was successfully deleted.
    """
    self.check_logout()
    return self.ana_api.deleteEditor(editorId=serverId)

    
def edit_server(self, serverId, name):
    """
    Edit the name of a server.
    
    Parameters
    ----------
    serverId : str
        The ID of the editor session to invite the user to.
    name : str
        The name to give the server.
    Returns
    -------
    bool
        If true, the server was successfully edited.
    """
    self.check_logout()
    return self.ana_api.editEditor(editorId=serverId, name=name)


def start_server(self, serverId):
    """
    Starts a server.
    
    Parameters
    ----------
    serverId : str
        The ID of the server to start.
    Returns
    -------
    bool
        If true, the server was successfully started.
    """
    import time
    self.check_logout()
    status =  self.ana_api.startEditor(editorId=serverId)
    if not self.interactive: return status
    else:
        starttime = time.time()
        while True:
            resp = self.ana_api.getEditors(editorId=serverId)
            if not resp:
                time.sleep(5)
                continue
            editor = resp[0]
            print(f'Waiting for editor {serverId} to start...[{time.time()-starttime:.3f}s]', end='\r')
            if editor['status']['state'] == 'running':
                break
            time.sleep(2)
        print(f'Waiting for editor {serverId} to start...done. [{time.time()-starttime:3f}s]')
        print_color(f'✅ Editor available, open with:                ', '91e600')
        serverpath = editor.get('serverPath', '/workspace/')
        print("  ", end=''); print_link("Browser", editor["url"])
        print("  ", end=''); print_link("Cursor", f"cursor://vscode-remote/ssh-remote+{editor['editorId']}@{editor['url'].replace('https://', '')}:443{serverpath}")
        print("  ", end=''); print_link("VSCode", f"vscode://vscode-remote/ssh-remote+{editor['editorId']}@{editor['url'].replace('https://', '')}:443{serverpath}")
        print("  ", end=''); print_link("Windsurf", f"windsurf://vscode-remote/ssh-remote+{editor['editorId']}@{editor['url'].replace('https://', '')}:443{serverpath}")
        return
    

def stop_server(self, serverId):
    """
    Stops a server.
    
    Parameters
    ----------
    editorId : str
        The ID of the server to stop.
    Returns
    -------
    bool
        If true, the server was successfully stopped.
    """
    self.check_logout()
    return self.ana_api.stopEditor(editorId=serverId)
    