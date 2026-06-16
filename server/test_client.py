import socket
import json
import traceback

def send(req):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect(('localhost', 5000))
        s.send(json.dumps(req).encode('utf-8'))
        resp = s.recv(8192)
        print('RAW RESPONSE:', resp)
        try:
            print('DECODED:', json.loads(resp.decode('utf-8')))
        except Exception:
            print('Failed to decode JSON response')
    except Exception as e:
        print('ERROR:', e)
        traceback.print_exc()
    finally:
        s.close()

if __name__ == '__main__':
    send({'action': 'login', 'username': 'admin', 'password': 'password123'})
