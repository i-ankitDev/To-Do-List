import tornado.ioloop
import tornado.web
import pymongo

from LoginHandler import LoginHandler 
from SignupHandler import SignUpHandler
from HomePageHandler import HomePageHandler
from TaskList import TaskList
from Task import Task
from logoutHandler import LogoutHandler

def make_app(db):
    return tornado.web.Application([
        (r"/", LoginHandler, dict(db=db)),
        (r"/signup", SignUpHandler, dict(db=db)),
        (r"/homepage", HomePageHandler, dict(db=db),TaskList),
        (r"/TaskList", TaskList, dict(db=db)),
        (r"/TaskList/Task", Task, dict(db=db)),
        (r"/logout", LogoutHandler)

    ], cookie_secret="nbkZgds8bKe3SFXKhX09B7AC8NwtUmxq86NBjW6iLGvxItZt_ST5", debug=True)
 
if __name__ == "__main__":
    myclient = pymongo.MongoClient("mongodb://localhost:27017")
    mydb = myclient["mydatabase"]
    app = make_app(mydb)
    app.listen(8889)
    print("running in http://localhost:8889/")
    tornado.ioloop.IOLoop.current().start()
