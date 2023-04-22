import Matrix_3 as mx

config = open('Config.txt', 'r')

mode = mx.nbl.find_value_by_name('Mode', config)
method = mx.nbl.find_value_by_name('Method', config)
N = mx.nbl.count_objects('obj_', config)
end_time = int(float( mx.nbl.find_value_by_name('End_time', config) ))
time_step = float( mx.nbl.find_value_by_name('Time_step', config) )
time_direction = int( mx.nbl.find_value_by_name('Time_direction', config) )
#pulse_table = bool(int( mx.nbl.find_value_by_name('Pulse_table', config) ))

objects = mx.nbl.format_objects('obj_', config)

config.close()

# system = open('System.txt', 'r')
# objects = mx.nbl.format_objects('obj_', system)
# system.close()
print(*objects, sep = "\n") #ПЕЧАТАТЬ С РАЗДЕЛИТЕЛЕМ \n
print('========= ^ Config Content ^ =========')


method = 'e'
ms = mx.gn.formatting(objects)
dir = time_direction
end = end_time
h = time_step

mx.simulation(method, ms, dir, end, h)