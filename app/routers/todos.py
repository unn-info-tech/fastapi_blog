# from fastapi import APIRouter, status, HTTPException
# from pydantic import BaseModel
# from typing import List
# from ..schemas import Todo

# router = APIRouter(
#     prefix="/todos",
#     tags=["Todos"]
# )


# # =====================
# # Fake DB
# # =====================
# todos_db = []
# todo_id = 1


# # =====================
# # CREATE
# # =====================
# @router.post("/", status_code=status.HTTP_201_CREATED)
# def create_todo(todo: Todo):
#     global todo_id

#     todo_dict = todo.dict()
#     todo_dict["id"] = todo_id

#     todo_id += 1
#     todos_db.append(todo_dict)

#     return {"xabar": "Todo yaratildi", "todo": todo_dict}


# # =====================
# # READ ALL
# # =====================
# @router.get("/", response_model=List[dict])
# def get_todos():
#     return todos_db


# # =====================
# # READ ONE
# # =====================
# @router.get("/{id}")
# def get_todo(id: int):
#     for t in todos_db:
#         if t["id"] == id:
#             return t
#     raise HTTPException(status_code=404, detail="Topilmadi")


# # =====================
# # UPDATE
# # =====================
# @router.put("/{id}")
# def update_todo(id: int, todo: Todo):
#     for index, t in enumerate(todos_db):
#         if t["id"] == id:
#             updated = todo.dict()
#             updated["id"] = id
#             todos_db[index] = updated
#             return {"xabar": "Yangilandi", "todo": updated}

#     raise HTTPException(status_code=404, detail="Topilmadi")


# # =====================
# # DELETE
# # =====================
# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_todo(id: int):
#     for index, t in enumerate(todos_db):
#         if t["id"] == id:
#             todos_db.pop(index)
#             return None

#     raise HTTPException(status_code=404, detail="Topilmadi")