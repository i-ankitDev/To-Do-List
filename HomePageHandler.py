from bson import ObjectId
import tornado.web
import json
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

class HomePageHandler(BaseHandler):
    def initialize(self, db):
        self.db = db

    def get(self):
        if not self.current_user:
            self.set_status(401)
            self.write({"status": False, "message": "Unauthorized"})
            return    
        try:
            token = self.get_secure_cookie("auth_token")
            if token:
                
                user_id = decode(token)
                # print(user_id)
                user_id = user_id['user']
                mycol_users = self.db["users"]
                user = mycol_users.find_one({"_id": ObjectId(user_id)})
                if user:
                    # print(user)
                    mycol_task_lists = self.db["taskList"]
                    user_object_id = ObjectId(user_id)
                    task_lists = list(mycol_task_lists.find({"user_id": user_object_id}))
                    for task_list in task_lists:
                        task_list['_id'] = str(task_list['_id'])
                        task_list['user_id'] = str(task_list['user_id'])
                        for task in task_list['tasks']:
                            task['_id'] = str(task['_id'])
                    self.set_header("Content-Type","text/html")
                    accept_header = self.request.headers.get("Accept", "application/json")
                    if "text/html" in accept_header:
                        # print(task_lists)
                        self.render("frontend/homepage.html", task_lists=task_lists)
                    else:
                        self.set_status(200)
                        self.write({"status": True, "task_lists": task_lists})


            else:
                self.set_status(401) 
                self.write({"status": False, "message": "Authorization token is missing."})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"An error occurred: {str(e)}"})