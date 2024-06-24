from bson import ObjectId
import tornado.web
import tornado.escape

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

class TaskList(BaseHandler):
    def initialize(self, db):
        self.db = db

    def post(self):
        try:
            if not self.request.body:
                self.set_status(400)
                self.write({"status": "error", "message": "Empty request body"})
                return
            token = self.request.headers.get('Authorization')
            token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNjY2Mjk0ZTdlZjdmOGQ2NWVlZTVjYzVkIn0.G5q-haZWo-puEMnOs0bs6sK0FeqdxxP7nKkFqG7LRck'
            if token:
                decoded_token = decode(token[7:])
                user_id = decoded_token['user']
                mycol_users = self.db["users"]
                user = mycol_users.find_one({"_id": ObjectId(user_id)})
                if user:
                    mycol_task_lists = self.db["taskList"]
                    user_object_id = ObjectId(user_id)
            
                    data = tornado.escape.json_decode(self.request.body)
                    task_list_name = data.get("taskListName")
                    accept_header = self.request.headers.get("Accept", "application/json")                                               
                    mycol = self.db["taskList"]
                    result = mycol.insert_one(
                    {"user_id": ObjectId(user_id), "taskListName": task_list_name, "tasks": []}
                    )
                if "text/html" in accept_header:
                    self.redirect("/homepage")
                else:
                    self.write({"status": "success", "message": "Task list created successfully."})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"An error occurred: {e}"})
    def put(self):
        try:
            data = tornado.escape.json_decode(self.request.body)
            tasklist_id = data.get("task_id")
            tasklist_id = ObjectId(tasklist_id) 
            new_task_list_name = data.get("newTaskListName")
            accept_header = self.request.headers.get("Accept", "application/json")

            mycol = self.db["taskList"]

            try:
                result = mycol.update_one(
                    {"_id": tasklist_id},
                    {"$set": {"taskListName": new_task_list_name}}
                )
            except Exception as e:
                self.set_status(500)
                self.write({"status": "error", "message": str(e)})
                return
            if "text/html" in accept_header:
                self.redirect("/homepage")
            else:
                    self.write({"status": "success", "message": "Task list name updated successfully."})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"An error occurred: {str(e)}"})

    def delete(self):
        try:
            tasklist_id = self.get_argument("list_id", None)
            if not tasklist_id:
                self.set_status(400)
                self.write({"status": "error", "message": "Missing task_id"})
                return
            tasklist_id = ObjectId(tasklist_id)  
            accept_header = self.request.headers.get("Accept", "application/json")
            mycol = self.db["taskList"]
            try:
                result = mycol.delete_one({"_id": tasklist_id})
            except Exception as e:
                self.set_status(500)
                self.write({"status": "error", "message": str(e)})
                return

            if result.deleted_count > 0:
                if "text/html" in accept_header:
                    self.redirect("/homepage")
                else:
                    self.write({"status": "success", "message": "Task list deleted successfully."})
            else:
                self.set_status(404)
                self.write({"status": "error", "message": "Task list not found."})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"An error occurred: {str(e)}"})
    def get(self):
        try:
            data = tornado.escape.json_decode(self.request.body)
            task_list_id = data.get("task_list_id")
            task_list_id = ObjectId(task_list_id)
            mycol = self.db["taskList"]
            task_list = mycol.find_one({"_id": task_list_id})  

            if task_list:
                try:
                    task_list["_id"] = str(task_list["_id"])  # Convert ObjectId to string
                    task_list['user_id'] = str(task_list['user_id'])
                    
                    for task in task_list.get('tasks', []):
                        task['_id'] = str(task['_id'])

                    self.write({"status": "success", "data": task_list})
                except Exception as e:
                    print(e)
            else:
                self.set_status(404)
                self.write({"status": "error", "message": "Task list not found."})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"An error occurred: {str(e)}"})
