from pygrabber.dshow_graph import FilterGraph

graph = FilterGraph()
device_list = graph.get_input_devices()

print("--- Connected Cameras On Windows 11 ---")
for index, name in enumerate(device_list):
    print(f"Index {index} : {name}")