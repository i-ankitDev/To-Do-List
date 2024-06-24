import tornado.ioloop
import tornado.web
from hashPassword import hashPassowrd
import logging


class SignUpHandler(tornado.web.RequestHandler):
    def initialize(self,db):
        self.db = db

    def get(self):
        self.render("frontend/signup.html")

    def post(self):
        try:
            logging.info("Headers: %s", self.request.headers)
            logging.info("Body: %s", self.request.body)
            data = tornado.escape.json_decode(self.request.body)
            name = data.get("name")
            email = data.get("email")
            password = data.get("password")
            hashed_password = hashPassowrd.hash_password(password)
            mycol = self.db["users"]
            mydict = {"name": name, "email": email, "password": hashed_password}
            x = mycol.insert_one(mydict)
            accept_header = self.request.headers.get("Accept", "application/json")
            if "text/html" in accept_header:
                self.render("frontend/login.html")
            else:
                self.write({"status": "success", "message": "User registered successfully."})
        
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"An error occurred: {e}"})