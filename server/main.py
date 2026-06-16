"""
TCP Server for PC Assembly System - SQLite.
"""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import socket
import threading
import json
import traceback
from server.auth import AuthService
from server.factory import RepositoryFactory

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
                data = client_socket.recv(8192)
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

        if action == 'register':
            username = request.get('username')
            password = request.get('password')
            role = request.get('role', 'operator')
            try:
                user_id = AuthService.register_user(username, password, role)
                return {'success': True, 'user_id': user_id}
            except Exception as e:
                return {'success': False, 'error': str(e)}

        if action == 'login':
            username = request.get('username')
            password = request.get('password')
            print(f"[SERVER] Login attempt: {username}")
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

        if not session.get('authenticated'):
            return {'success': False, 'error': 'Authentication required'}

        use_orm = request.get('use_orm', True)

        # COMPONENTS
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

        # ORDERS
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

        if action == 'order_get_items':
            repo = RepositoryFactory.create_order_repository(use_orm)
            items = repo.get_order_items(request.get('order_id'))
            return {'success': True, 'data': items}

        if action == 'order_add_item':
            repo = RepositoryFactory.create_order_repository(use_orm)
            result = repo.add_order_item(
                request.get('order_id'),
                request.get('component_id'),
                request.get('quantity'),
                request.get('unit_price')
            )
            return {'success': result}

        # CLIENTS
        if action == 'client_create':
            repo = RepositoryFactory.create_client_repository(use_orm)
            client_id = repo.create(request.get('data', {}))
            return {'success': True, 'client_id': client_id}

        if action == 'client_get':
            repo = RepositoryFactory.create_client_repository(use_orm)
            client = repo.get_by_id(request.get('client_id'))
            return {'success': True, 'data': client}

        if action == 'client_list':
            repo = RepositoryFactory.create_client_repository(use_orm)
            clients = repo.get_all(request.get('filters'))
            return {'success': True, 'data': clients}

        if action == 'client_update':
            repo = RepositoryFactory.create_client_repository(use_orm)
            result = repo.update(request.get('client_id'), request.get('data', {}))
            return {'success': result}

        if action == 'client_delete':
            repo = RepositoryFactory.create_client_repository(use_orm)
            result = repo.delete(request.get('client_id'))
            return {'success': result}

        # CATALOG BUILDS
        if action == 'build_create':
            repo = RepositoryFactory.create_catalog_build_repository(use_orm)
            build_id = repo.create(request.get('data', {}))
            return {'success': True, 'build_id': build_id}

        if action == 'build_get':
            repo = RepositoryFactory.create_catalog_build_repository(use_orm)
            build = repo.get_by_id(request.get('build_id'))
            return {'success': True, 'data': build}

        if action == 'build_list':
            repo = RepositoryFactory.create_catalog_build_repository(use_orm)
            builds = repo.get_all(request.get('filters'))
            return {'success': True, 'data': builds}

        if action == 'build_add_component':
            repo = RepositoryFactory.create_catalog_build_repository(use_orm)
            result = repo.add_component(
                request.get('build_id'),
                request.get('component_id'),
                request.get('quantity')
            )
            return {'success': result}

        if action == 'build_get_components':
            repo = RepositoryFactory.create_catalog_build_repository(use_orm)
            components = repo.get_build_components(request.get('build_id'))
            return {'success': True, 'data': components}

        if action == 'build_delete':
            repo = RepositoryFactory.create_catalog_build_repository(use_orm)
            result = repo.delete(request.get('build_id'))
            return {'success': result}

        # FINANCES
        if action == 'finance_create':
            repo = RepositoryFactory.create_finance_repository(use_orm)
            record_id = repo.create(request.get('data', {}))
            return {'success': True, 'record_id': record_id}

        if action == 'finance_list':
            repo = RepositoryFactory.create_finance_repository(use_orm)
            records = repo.get_all(request.get('filters'))
            return {'success': True, 'data': records}

        if action == 'finance_summary':
            repo = RepositoryFactory.create_finance_repository(use_orm)
            summary = repo.get_summary()
            return {'success': True, 'data': summary}

        # USERS (admin only)
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
                if not request.get('confirmed'):
                    return {'success': False, 'error': 'Deletion requires confirmation'}
                repo = RepositoryFactory.create_user_repository(use_orm)
                result = repo.delete(request.get('user_id'))
                return {'success': result}

        # ACTIVE SESSIONS
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
