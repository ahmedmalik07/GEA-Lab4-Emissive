import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
r = re.RemoteExecution(); r.start()
for _ in range(60):
    if r.remote_nodes: break
    time.sleep(1)
if not r.remote_nodes: print("NO NODES"); sys.exit(1)
r.open_command_connection(r.remote_nodes[0]["node_id"])
arg = sys.argv[1]
if arg.endswith(".py"):
    res = r.run_command(arg, exec_mode=re.MODE_EXEC_FILE, unattended=True)
else:
    res = r.run_command(arg, exec_mode=re.MODE_EXEC_STATEMENT, unattended=True)
print(res.get("success"))
for o in res.get("output", []): print(o.get("type"), o.get("output"))
print(res.get("result"))
r.stop()
