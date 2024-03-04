#!/usr/bin/python3
"""This is the console module"""
import cmd
import os
import readline
import json
from models.base_model import BaseModel
from models.manufacturer import Manufacturer
from models.generator import Generator
from models.part import Part
from models import storage
from models.engine.db_storage import DBStorage


def complete(text, state):
  options = ['Manufacturer', 'Generator', 'Part', 'create']
  matches = [cmd for cmd in options if cmd.startswith(text)]
  if state < len(matches):
    return matches[state]
  return None


class PartCommand(cmd.Cmd):
  """This model represents our console."""

  prompt: str = "(efod) "
  file = None
  class_name = {
    'BaseModel': BaseModel, 'Manufacturer': Manufacturer,
    'Generator': Generator, 'Part': Part
  }

  def parse_input(self, cmd):
    """Parse string pass to it."""
    arg = cmd.replace('(', ' ').replace('"', '').replace("'", "")
    arg = arg.replace('.', ' ', 1).replace(')', '')
    return arg
  
  def emptyline(self) -> None:
    """Do nothing when empty line and enter"""
    return
  
  def default(self, line: str) -> None:
    """Find the right cmd and execute it."""
    cmd = {
      'all': self.do_all,
      'count': self.count,
      'show': self.do_show,
      'destroy': self.do_destroy,
      'update': self.get_update,
      'link': self.do_link
    }
    arg = self.parse_input(line).split()

    if len(arg) < 2:
      return super().default(line)

    if arg[1] in cmd:
      func = cmd[arg[1]]
      func(line)
    else:
      return super().default(line)

  def do_clear(self, arg):
    return os.system('cls' if os.name == 'nt' else 'clear') 

  def do_quit(self, line):
    """Type quit to exit the program."""
    return True

  def do_EOF(self, line):
    """EOF or ctrl^D command to exit the program."""
    return True

  def do_create(self, line):
    """Create an available model and save it"""
    try:
      model, *line = line.split()
      args = {}
      for value in line:
        key = value[:value.find('=')]
        val = value[value.find('=') + 1:].replace(
                               '"', '').replace('_', ' ')
        args[key] = val
    except Exception:
      model = args
    if not model:
      print('** class name missing **')
    elif model not in self.class_name:
      print("** class doesn't exist **")
    if type(args) is dict:
      new_instance = self.class_name[model](**args)
    else:
      new_instance = eval(f'{self.class_name[model]}()')
    new_instance.save()
    print(new_instance.id)

  def do_show(self, line):
    """Retrieves the instance from storage engine"""
    arg = self.parse_input(line).replace('show', '').split()
    if not line:
      print('** class name missing **')
    elif not arg[0] in self.class_name:
      print("** class doesn't exist **")
    elif len(arg) != 2:
      print("** instance id missing **")
    else:
      id_ = arg[0] + '.' + arg[1]
      try:
        if os.getenv('MECH_TYPE_STORAGE') == 'db':
          db_storage = DBStorage()
          objs = db_storage.all()
          key = id_
          if key in objs:
            print(objs[key])
          else:
            print("** no instance found **")
        
        else: 
          with open('file.json', 'r', encoding='utf-8') as f:
            objs = json.loads(f.read())
          if id_ in objs:
            out = objs[id_]
            name = out['__class__']
            base = eval(f"{name}(**out)")
            print(base)
          else:
            print("** no instance found **")
      except Exception:
        print("** no instance found **")

  def do_destroy(self, line):
    """Delete an instance of a supported model from storage"""
    arg = self.parse_input(line).replace('destroy', '').split()
    if not line:
        print('** class name missing **')
    elif not arg[0] in self.class_name:
        print("** class doesn't exist **")
    elif len(arg) != 2:
        print("** instance id missing **")
    else:
        id_ = arg[0] + '.' + arg[1]
        try:
            if os.getenv('MECH_TYPE_STORAGE') == 'db':
                db_storage = DBStorage()
                objs = db_storage.all()
                key = id_
                if key in objs:
                    db_storage.delete(objs[key])
                    print("object destroyed")
                    db_storage.save()  # Commit the changes to the database
                else:
                    print("** no instance found **")
            else:
                with open('file.json', 'r', encoding='utf-8') as f:
                    objs = json.loads(f.read())
                if id_ in objs:
                    del objs[id_]
                    with open('file.json', 'w', encoding='utf-8') as f:
                        json.dump(objs, f, indent=4)
                else:
                    print("** no instance found **")
        except Exception:
            print("** no instance found **")


  def do_all(self, line):
    """Retrieve every model instances from our file storage."""
    line = self.parse_input(line).replace('all', '').replace(' ', '')
    objs_arr = []

    if os.getenv('MECH_TYPE_STORAGE') == 'db':
        db_storage = DBStorage()
        objs = db_storage.all()
    else:
        try:
            with open('file.json', 'r', encoding='utf-8') as f:
                objs = json.loads(f.read())
        except Exception as e:
            print(f"Error loading data from file: {e}")
            return

    if not line:
        for obj in objs.values():
            objs_arr.append(str(obj))
    elif line not in self.class_name:
        print("** class doesn't exist **")
    else:
        for obj in objs.values():
            if os.getenv('MECH_TYPE_STORAGE') == 'db':
              if obj.__class__.__name__ == line:
                objs_arr.append(str(obj))
            else:
              if obj.get("__class__") == line:
                inst = eval(f'{obj.__class__.__name__}(**obj)')
                objs_arr.append(str(obj))

    print(objs_arr)



  def do_update(self, line):
    """update an instance of a supported model """
    if ')' in line:
      line = line.replace(',', '', 2)
    arg = line.replace(')', '').replace('.', ' ').replace('(', '')
    arg = arg.replace('update', '').split(maxsplit=3)
    cnvt = {
      "int": int,
      "float": float,
      "Str": str,
    }
    try:
      if not line:
        print('** class name missing **')
      elif arg[0] not in self.class_name:
        print("** class doesn't exist **")
      elif len(arg) < 2:
        print("** instance id missing **")
      elif arg[0] + '.' + self.parse_input(arg[1]) not in storage.all():
        print("** no instance found **")
      elif len(arg) < 3:
        print("** attribute name missing **")
      elif len(arg) < 4:
        print("** value missing **")
      else:
        with open('file.json', 'r', encoding='utf-8') as f:
          objs = json.loads(f.read())
        inst = eval(f'{arg[0]}()')
        k, val = arg[2], arg[3].replace('"', '').replace("'", "")
        key = arg[0] + '.' + self.parse_input(arg[1])
        typ = type(getattr(inst, k, None))
        if typ:
          if typ.__name__ in cnvt:
            func = cnvt[typ.__name__]
            val = func(val)
        obj = objs[key]
        obj[k] = val
        with open('file.json', 'w', encoding='utf-8') as f:
          json.dump(objs, f, indent=4)
    except Exception as err:
      print(err)
  

  def get_update(self, line):
    """Call the rightful Update method."""
    if '{' in line and '}' in line:
      self.update_dict(line)
    else:
      self.do_update(line)

  def update_dict(self, line):
    """Update any model instance using dictionary."""
    arg = line.replace(')', '').replace('.', ' ').replace('(', '')
    arg = arg.replace('update', '').replace(',', '', 1).split(maxsplit=2)
    cnvt = {
      "int": int,
      "float": float,
      "str": str,
    }

    try: 
      if not line:
        print('** class name missing **')
      elif arg[0] not in self.class_name:
        print("** class doesn't exist **")
      elif len(arg) < 2:
        print("** instance id missing **")
      elif arg[0] + '.' + self.parse_input(arg[1]) not in storage.all():
        print("** no instance found **")
      elif len(arg) < 3:
        print("** dict missing **")
      else:
        with open('file.json', 'r', encoding='utf-8') as f:
          objs = json.loads(f.read())
        inst = eval(f'{arg[0]}()')
        obj_dict = eval(arg[2].replace("'", '"'))
        key = arg[0] + '.' + self.parse_input(arg[1])
        obj = objs[key]

        for k, val in obj_dict.items():
          typ = type(getattr(inst, k, None))
          if typ:
            if typ.__name__ in cnvt:
              func = cnvt[typ.__name__]
              val = func(val)
          obj[k] = val
        with open('file.json', 'w', encoding='utf-8') as f:
          json.dump(objs, f, indent=4)
    except Exception:
      pass


  def count(self, line):
    """
    Count total instances of supported model from fs
    """
    cnt = 0
    line = self.parse_input(line).replace('count', '').replace(' ', '')
    if line not in self.class_name:
      print("** class doesn't exist **")
      return
    try:
      with open('file.json', 'r', encoding='utf-8') as f:
        objs = json.loads(f.read())
      for obj in objs.values():
        name = obj['__class__']
        if name == line:
          cnt += 1
      print(cnt)
    except Exception:
      print(cnt)
  
  def do_link(self, line):
    """Link a Generator to a Part."""
    try:
      id_1, id_2 = line.split()
    except ValueError:
      print("Invalid syntax. Use: link Generator.[id] Part.[id]")
      return
    model_1, model_id_1 = id_1.split('.')
    model_2, model_id_2 = id_2.split('.')
    if model_1 != 'Generator' or model_2 != 'Part':
      print("Invalid models. Use: link Generator.[id] Part.[id]")
      return
    if storage.link(model_id_1, model_id_2):
      storage.save()
      print(f"Linked Generator {model_id_1} to Part {model_id_2}.")
    else:
      print("Error: Duplicate entry. Entry already exists")
  

if __name__ == '__main__':
  readline.parse_and_bind("tab: complete")
  readline.set_completer(complete)

  PartCommand().cmdloop()
