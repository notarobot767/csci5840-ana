#!/usr/bin/env python3

import file_object
import yaml, textwrap
from pathlib import Path

def make_dir(dir):
    """create if doesnt exist"""
    path = Path(dir)
    path.mkdir(parents=True, exist_ok=True)

def make_yaml_file(yaml_lst):
    src = "./roles/device/templates/{{ item.template }}"
    dest = "./cfgs/{{ item.dest }}/{{ item.hostname }}/{{ item.hostname }}_{{ item.device }}.txt"
    return f"""
---
- name: Generate configuration files
  ansible.builtin.template:
    src: {src}
    dest: {dest}
  with_items:
{"\n".join(yaml_lst)}
""".strip()

def init_ansible_yaml_file(role):
    src = f"./roles/{role}/templates/{{{{ item.template }}}}"
    dest = "./cfgs/{{ item.hostname }}_{{ now(fmt='%Y-%m-%d_%H-%M-%S') }}.cfg"
    return f"""
---
- name: Generate configuration files
  ansible.builtin.template:
    src: {src}
    dest: {dest}
  with_items:
""".lstrip()

def check_req_keys(dic):
    required_keys = ["hostname", "template", "role"]
    if all(key in dic for key in required_keys):
        return True
    return False

def get_roles():
    return ["router"]

def clean_cfgs_dir(directory="./cfgs"):
    """Delete all files and subdirectories inside the cfg directory."""
    cfg_path = Path(directory)
    if not cfg_path.exists():
        return

    for item in cfg_path.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            print(f"Error removing {item}: {e}")

def main():
    for role in get_roles():
        task_dir = f"./roles/{role}/tasks"
        make_dir(task_dir)
        file_object.write_file(f"{task_dir}/main.yaml", init_ansible_yaml_file(role))
        # create initial task dir if non existent
        # init main.yaml task
    
    base = "./requirements"
    path = Path(base)
    files = [str(f.resolve()) for f in path.rglob("*") if f.is_file()]
    # create list of all file reqs in this dir and sub dirs
    
    for file in files:
        #try:
        data = file_object.read_file_yaml(file)
        #except:
            #print(f"unable to open file '{file}' as yaml!")
            #continue
        if check_req_keys(data):
            #make_dir(f"./cfgs/{data["dest"]}/{data["hostname"]}")
            #make_dir(f"./cfgs/{data["dest"]}")
                # make cfg dir if needed
            yml = yaml.dump([data], default_flow_style=False, sort_keys=False)
            yml = textwrap.indent(yml, '    ')
            file_object.write_file(f"./roles/{data["role"]}/tasks/main.yaml", yml, "a")
    # iterate and open as json each file
    # format as json and append to yaml_lst

    clean_cfgs_dir("./cfgs")

if __name__ == "__main__":
    main()