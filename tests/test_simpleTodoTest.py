import unittest
import simpleTodoDataAccess as todoData
import unittest.mock as mock
import pymongo


class TestTodo(unittest.TestCase):

    def test_get_all_todos_by_due_date(self):
        mongo = mock.Mock()
        sortArgs = {'sort.return_value':[{"a","1"},{"b":"2"}]}
        mongo.db.todos.find({}).configure_mock(**sortArgs)
        todoDataAccess = todoData.SimpleTodoDataAccess(mongo)
        returnData = todoDataAccess.get_all_todos_by_due_date()
        #Verify calls to mongo
        self.assertTrue(mongo.db.todos.find({}).sort.call_args == (('due_date',pymongo.ASCENDING),))
        self.assertTrue(len(returnData)==2)

    def test_get_todo(self):
        mongo = mock.Mock()
        todoDataAccess = todoData.SimpleTodoDataAccess(mongo)
        todoDataAccess.get_todo(1)
        #Verify calls to mongo
        self.assertTrue(mongo.db.todos.find_one.call_args == (({'todo_id':1},),))

    def test_create_todo_no_data(self):
        mongo = mock.Mock()
        todoDataAccess = todoData.SimpleTodoDataAccess(mongo)
        aggregateArgs = {'aggregate.return_value':[{'max_id':5}]}
        mongo.db.todos.configure_mock(**aggregateArgs)
        todoDataAccess.create_todo({})
        #Verify calls to mongo
        self.assertTrue(mongo.db.todos.insert_one.call_args == (({'todo_id':6},),))

