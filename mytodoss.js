const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const MyTodosModel = new Schema({
  userId: {
    type: Number,
    reqired: true,
  },
  id: {
    type: Number,
    reqired: true,
  },
  title: {
    type: String,
    reqired: true,
  },
  completed: {
    type: Boolean,
    reqired: true,
  },
});

const MyTodos = mongoose.model("MyTodos", MyTodosModel, MyTodos);
export default MyTodos;
