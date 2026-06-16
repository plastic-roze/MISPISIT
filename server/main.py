"""
TCP Server for PC Assembly System.
Handles multiple client connections via threading.
"""
import sys
import pathlib
# Ensure package imports work when running this file as a script
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import socket
import threading
import json
import traceback
from server.auth import AuthService
from server.factory import RepositoryFactory

# Active sessions tracking
active_sessions = {}
sessions_lock = threading.Lock()

class Server:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        print(f"[SERVER] Started on {self.host}:{self.port}")

        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"[SERVER] Connection from {address}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"[SERVER] Error accepting connection: {e}")

    def handle_client(self, client_socket, address):
        session_id = f"{address[0]}:{address[1]}"
        with sessions_lock:
            active_sessions[session_id] = {
                'address': address,
                'authenticated': False,
                'user': None
            }

        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break

                try:
                    request = json.loads(data.decode('utf-8'))
                    response = self.process_request(request, session_id)
                except json.JSONDecodeError:
                    response = {'success': False, 'error': 'Invalid JSON'}
                except Exception as e:
                    response = {'success': False, 'error': str(e)}
                    traceback.print_exc()

                client_socket.send(json.dumps(response).encode('utf-8'))
        except Exception as e:
            print(f"[SERVER] Client error: {e}")
        finally:
            with sessions_lock:
                if session_id in active_sessions:
                    del active_sessions[session_id]
            client_socket.close()
            print(f"[SERVER] Connection closed: {address}")

    def process_request(self, request, session_id):
        action = request.get('action')
        session = active_sessions.get(session_id, {})

        # Allow new user registration without authentication
        if action == 'register':
            username = request.get('username')
            password = request.get('password')
            role = request.get('role', 'operator')
            try:
                user_id = AuthService.register_user(username, password, role)
                return {'success': True, 'user_id': user_id}
            except Exception as e:
                return {'success': False, 'error': str(e)}

        # Auth actions
        if action == 'login':
            username = request.get('username')
            password = request.get('password')
            print(f"[SERVER] Login attempt for: {username}")
            user = AuthService.authenticate(username, password)
            if user:
                with sessions_lock:
                    active_sessions[session_id]['authenticated'] = True
                    active_sessions[session_id]['user'] = user
                return {'success': True, 'user': user}
            return {'success': False, 'error': 'Invalid credentials'}

        if action == 'logout':
            with sessions_lock:
                active_sessions[session_id]['authenticated'] = False
                active_sessions[session_id]['user'] = None
            return {'success': True}

        # Check authentication for protected actions
        if not session.get('authenticated'):
            return {'success': False, 'error': 'Authentication required'}

        # Get repository type (ORM or SQL)
        use_orm = request.get('use_orm', True)

        # Component operations
        if action == 'component_create':
            repo = RepositoryFactory.create_component_repository(use_orm)
            component_id = repo.create(request.get('data', {}))
            return {'success': True, 'component_id': component_id}

        if action == 'component_get':
            repo = RepositoryFactory.create_component_repository(use_orm)
            component = repo.get_by_id(request.get('component_id'))
            return {'success': True, 'data': component}

        if action == 'component_list':
            repo = RepositoryFactory.create_component_repository(use_orm)
            components = repo.get_all(request.get('filters'))
            return {'success': True, 'data': components}

        if action == 'component_update':
            repo = RepositoryFactory.create_component_repository(use_orm)
            result = repo.update(request.get('component_id'), request.get('data', {}))
            return {'success': result}

        if action == 'component_delete':
            repo = RepositoryFactory.create_component_repository(use_orm)
            result = repo.delete(request.get('component_id'))
            return {'success': result}

        # Order operations
        if action == 'order_create':
            repo = RepositoryFactory.create_order_repository(use_orm)
            order_id = repo.create(request.get('data', {}))
            return {'success': True, 'order_id': order_id}

        if action == 'order_get':
            repo = RepositoryFactory.create_order_repository(use_orm)
            order = repo.get_by_id(request.get('order_id'))
            return {'success': True, 'data': order}

        if action == 'order_list':
            repo = RepositoryFactory.create_order_repository(use_orm)
            orders = repo.get_all(request.get('filters'))
            return {'success': True, 'data': orders}

        if action == 'order_update_status':
            repo = RepositoryFactory.create_order_repository(use_orm)
            result = repo.update_status(request.get('order_id'), request.get('status'))
            return {'success': result}

        if action == 'order_delete':
            repo = RepositoryFactory.create_order_repository(use_orm)
            result = repo.delete(request.get('order_id'))
            return {'success': result}

        # User operations (admin only)
        if action in ['user_create', 'user_delete', 'user_list']:
            user = session.get('user', {})
            if user.get('role') != 'admin':
                return {'success': False, 'error': 'Admin privileges required'}

            if action == 'user_create':
                repo = RepositoryFactory.create_user_repository(use_orm)
                user_id = repo.create(request.get('data', {}))
                return {'success': True, 'user_id': user_id}

            if action == 'user_list':
                repo = RepositoryFactory.create_user_repository(use_orm)
                users = repo.get_all()
                return {'success': True, 'data': users}

            if action == 'user_delete':
                # Requires re-authentication
                if not request.get('confirmed'):
                    return {'success': False, 'error': 'Deletion requires confirmation and re-auth'}
                repo = RepositoryFactory.create_user_repository(use_orm)
                result = repo.delete(request.get('user_id'))
                return {'success': result}

        # Active sessions
        if action == 'active_sessions':
            with sessions_lock:
                sessions = [{
                    'session_id': k,
                    'address': v['address'],
                    'authenticated': v['authenticated'],
                    'username': v['user']['username'] if v['user'] else None
                } for k, v in active_sessions.items()]
            return {'success': True, 'data': sessions}

        return {'success': False, 'error': f'Unknown action: {action}'}

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()

if __name__ == '__main__':
    server = Server()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
        server.stop()
