import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from server.auth import AuthService
print('calling authenticate')
print(AuthService.authenticate('admin','password123'))
