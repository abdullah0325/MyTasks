
from fastapi import FastAPI
app = FastAPI()

data = [{"id": 1, "name": "usman", "id_card_no": "ID123456", "salary": 50000},
        {"id": 2, "name": "ali", "id_card_no": "ID789012", "salary": 55000},
        {"id": 3, "name": "ahmed", "id_card_no": "ID345678", "salary": 60000},
        {"id": 4, "name": "khan", "id_card_no": "ID901234", "salary": 52000},
        {"id": 5, "name": "naveed", "id_card_no": "ID567890", "salary": 58000}]

@app.post("/create/")
def create_employee(id:int,name:str,id_card_no:str,salary:int):
    for emp in data:
        if emp["id"]== id:
            return {"message":"Employee already exists"}
    new_employee = {"id":id,"name":name,"id_card_no":id_card_no,"salary":salary}
    data.append(new_employee)
    return "the new employee added",new_employee


@app.get("/read/")
def get_employee(id: int):
    for emp in data:
        if emp["id"] == id:
            return emp
    return {"message":"Employee not found"}


@app.put("/update/")
def update_employee(id:int,salary:int):
    for emp in data:
        if emp["id"] == id:
            emp["salary"]=salary    
            return emp    
    return {"message":"Employee not found"}
            

@app.delete("/delete/")
def delete_employee(id:int):
    for emp in data:
        if emp["id"] == id:
            data.remove(emp)
            return {"message":"Employee deleted successfully"}
    return {"message":"Employee not found"}



