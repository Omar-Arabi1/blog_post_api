from fastapi import FastAPI

from auth import auth
from auth.auth import user_dependency
from user_actions import user_actions
from databases.database import db_dependency, Base, engine
from helpers.check_logged_in import check_logged_in

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(user_actions.router)

@app.get('/')
def root(db: db_dependency, user: user_dependency):
    check_logged_in(user=user)
    
    return {'user': user}
