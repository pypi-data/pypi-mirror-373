import pickle 
def pkl_save(obj, filename):
    with open(filename, 'wb') as file:
        pickle.dump(obj, file)

def pkl_load(filename):
    with open(filename, 'rb') as file:  
        return pickle.load(file)
         