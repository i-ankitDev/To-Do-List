import tornado.ioloop
import tornado.web
import bcrypt
from TokenGeneration import encode

class LoginHandler(tornado.web.RequestHandler):
    def initialize(self,db):
        self.db = db
    
    def get(self):
        self.render("frontend/index.html")

    
    def post(self):

        try:
            data = tornado.escape.json_decode(self.request.body)
            email = data.get("email")
            password = data.get("password")
            
            if not email or not password:
                self.set_status(400)
                self.write({"status": False, "message": "Email and password are required."})
                return

            mycol = self.db["users"]
            user = mycol.find_one({"email": email})

            if user is None or not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                self.set_status(401)
                self.write({"status": False, "message": "Invalid email or password."})
            else:
                encoded_user_id = encode(str(user["_id"]))
                self.set_secure_cookie("auth_token", encoded_user_id, httponly=True, secure=True)
                # print(encoded_user_id)
                self.write({"token": encoded_user_id, "status": True, "message": "User logged in successfully."})
        except Exception as e:
            self.set_status(500)
            self.write({"status": False, "message": f"An error occurred: {str(e)}"})