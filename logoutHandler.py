import tornado.ioloop
import tornado.web

from TokenGeneration import decode

class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def get_current_user(self):
        auth_cookie = self.get_secure_cookie("auth_token")
        if auth_cookie:
            try:
                token = auth_cookie.decode('utf-8')
                return decode(token)
            except Exception as e:
                print(f"Error decoding token: {e}")
                return None
        return None
    
class LogoutHandler(BaseHandler):
    def post(self):
        if not self.current_user:
            self.set_status(401)
            self.write({"status": False, "message": "Unauthorized"})
            return    
        self.clear_cookie("auth_token")
        self.render("frontend/index.html")
        # self.write({"status": True, "message": "Logged out successfully."})
