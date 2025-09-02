from syncmodels.model import BaseModel

# from surrealdb import Surreal


# # TODO: review SurrealORM / pydantic
# class SurrealCRUD(Surreal):
#     def __init__(
#         self,
#         url,
#         max_size=2**20,
#         user: str = "root",
#         passwd="root",
#         ns="test",
#         db="test",
#     ):
#         super().__init__(url=url, max_size=max_size)
#         self.user = user
#         self.passwd = passwd
#         self.ns = ns
#         self.db = db

#     async def connect(self):
#         await super().connect()
#         await self.signin({"user": self.user, "pass": self.passwd})
#         await self.use(self.ns, self.db)

#     async def create_(self, item: BaseModel, data=None):
#         table = item.__module__
#         table = table.replace(".", "_")
#         # table = table.split('.')[-1]

#         # TODO: analyze __pydantic_core_schema__
#         # schema.schema.fields.*
#         # for k, v in item.__dict__.items():
#         # if isinstance(v, BaseModel):
#         # pass
#         # print(f"{k}: {v}")

#         data = data or item.model_dump(mode="json")
#         assert "id" in data

#         await self.create(table, data)

#     async def read_(self):
#         pass

#     async def update_(self):
#         pass

#     async def delete_(self):
#         pass
