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

class Task(BaseHandler):
    def initialize(self, db):
        self.db = db

    def post(self):
        try:       
            data = tornado.escape.json_decode(self.request.body)
            tasklist_id = self.get_query_argument("tasklist_id")
            tasklist_id = ObjectId(tasklist_id)
            title = data.get("title")
            new_task_id = ObjectId()  
            status = "pending"
            accept_header = self.request.headers.get("Accept", "application/json")
            mycol = self.db["taskList"]
            
            task = {
                "_id": new_task_id,
                "title": title,
                "status": status
            }
            try:
                result = mycol.update_one(
                    {"_id": tasklist_id},  
                    {"$addToSet": {"tasks": task}}  
                )
            except Exception as e:
                self.write(e)
                return
            print(result)
            if "text/html" in accept_header:
                self.redirect("/homepage")
            else:
                self.write({"status": "success", "message": "Task updated successfully."})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"An error occurred: {e}"})
    def put(self):
        try:
            task_id = self.get_query_argument("task_id")
            task_id = ObjectId(task_id)
            accept_header = self.request.headers.get("Accept", "application/json")
            mycol = self.db["taskList"]

            try:
                result = mycol.update_one(
                    {"tasks._id": task_id},
                    {"$set": {"tasks.$.status": "Completed"}}
                )
            except Exception as e:
                self.set_status(500)
                self.write({"status": "error", "message": f"An error occurred: {e}"})
                return
            
            if result.modified_count == 0:
                self.set_status(404)
                self.write({"status": "error", "message": "Task not found."})
                return

            if "text/html" in accept_header:
                self.redirect("/homepage")
            else:
                self.write({"status": "success", "message": "Task status updated successfully.", "task_id": str(task_id)})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"An error occurred: {e}"})

    def delete(self):
        try:
            task_id = self.get_query_argument("task_id")
            task_id = ObjectId(task_id)
            if not task_id:
                self.set_status(400)
                self.write({"status": "error", "message": "Missing task_id"})
                return 
            accept_header = self.request.headers.get("Accept", "application/json")
            mycol = self.db["taskList"]
            try:
                result = mycol.update_one(
                    {"tasks._id": task_id},
                    {"$pull": {"tasks": {"_id": task_id}}}
                )
            except Exception as e:
                self.set_status(500)
                self.write({"status": "error", "message": str(e)})
                return

            if result.modified_count > 0:
                if "text/html" in accept_header:
                    self.redirect("/homepage")
                else:
                    self.write({"status": "success", "message": "Task deleted successfully."})
            else:
                self.set_status(404)
                self.write({"status": "error", "message": "Task not found."})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"An error occurred: {str(e)}"})  
    def get(self):
        try:
            data = tornado.escape.json_decode(self.request.body)
            task_list_id = data.get("task_list_id")
            task_id = data.get("task_id")
            
            # Validate input
            if not task_list_id or not task_id:
                self.set_status(400)
                self.write({"status": "error", "message": "Missing task_list_id or task_id"})
                return
            
            task_list_id = ObjectId(task_list_id)
            task_id = ObjectId(task_id)
            
            mycol = self.db["taskList"]
            task_list = mycol.find_one({"_id": task_list_id})
            
            if task_list:
                task = next((task for task in task_list['tasks'] if task['_id'] == task_id), None)
                if task:
                    task['_id'] = str(task['_id'])
                    self.write({"status": "success", "data": task})
                else:
                    self.set_status(404)
                    self.write({"status": "error", "message": "Task not found."})
            else:
                self.set_status(404)
                self.write({"status": "error", "message": "Task list not found."})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"An error occurred: {str(e)}"})